#!/usr/bin/python

# To do...
# 
# * Buttons - get the capacitive buttons working and then develop a user
#   interface.
#
# * Timer settings - need PHP page to show the current set times and allow them
#   to be modified, deleted, added.
#
# * Remote control - allow it to be controlled (and viewed?) from afar.
#   Obvious security implications with this.


import time
import RPi.GPIO as GPIO
import sys
import datetime
import os
import mmap

from time import gmtime, localtime, strftime

# Driver for oled display
import Adafruit_SSD1306

# Driver for temperature sensor
import Adafruit_MCP9808.MCP9808 as MCP9808

import Image
import ImageDraw
import ImageFont
import random
import math
import ImageOps

#===============================================================================

# Function to draw shadowed text to allow it to overlay a background image
def drawShadowedText(draw, x, y, text, font):
	draw.text((x, y+1), text, font=font, fill=0)
	draw.text((x+1, y), text, font=font, fill=0)
	draw.text((x+1, y+1), text, font=font, fill=0)
	draw.text((x, y-1), text, font=font, fill=0)
	draw.text((x-1, y), text, font=font, fill=0)
	draw.text((x, y), text, font=font, fill=255)

#===============================================================================

# Function to handle drawing animated characters behind the text
def drawAnimationBehind():

	global anim_state, anim_percent
	
	if anim_state == 'pacman':

		pass

	elif anim_state == 'ghost':

		global ghost_image

		ghost_x = 150 - anim_percent * 200 / 100

		image.paste(ghost_image,(ghost_x,33))

	elif anim_state == 'ufo':

		global ufo_small_image, ufo_small_image_mask

		ufo_x = 150 - anim_percent * 200 / 100
		image.paste(ufo_small_image,(ufo_x,10), ufo_small_image_mask)
		image.paste(ufo_small_image,(ufo_x+20,25), ufo_small_image_mask)
		image.paste(ufo_small_image,(ufo_x+5,45), ufo_small_image_mask)


#===============================================================================

# Function to handle drawing animated characters over the text
def drawAnimationInfront():

	global anim_state, anim_percent
	
	if anim_state == 'pacman':

		global pac_x, pac_y, pac_radius, pac_blackout, pac_angle

		draw.rectangle((pac_x, pac_y-pac_radius, pac_x-pac_blackout, pac_y+pac_radius), fill=0);
		draw.pieslice((pac_x-pac_radius-pac_blackout,pac_y-pac_radius,pac_x+pac_radius-pac_blackout,pac_y+pac_radius),90, 270, fill=0)
		draw.pieslice((pac_x-pac_radius,pac_y-pac_radius,pac_x+pac_radius,pac_y+pac_radius),0+pac_angle, 359-pac_angle, fill=255, outline=0)

	elif anim_state == 'ufo':

		global ufo_image, ufo_image_mask

		ufo_x = anim_percent * 400 / 100 - 250
		image.paste(ufo_image,(ufo_x,5), ufo_image_mask)

	elif anim_state == 'asteroids':

		global ast_bullets, ast_shrapnel, ast_oldimage, ast_ship

		if ast_oldimage != 'noimage' and anim_percent > 0:
			image.paste(ast_oldimage,(0,0))

			for bullet in ast_bullets:
				draw.point((bullet['x'], bullet['y']), fill=255)

			for shrapnel in ast_shrapnel:
				x = math.sin(math.radians(shrapnel['angle'])) * shrapnel['radius']
				y = math.cos(math.radians(shrapnel['angle'])) * shrapnel['radius']
				draw.line(( shrapnel['x']-x, shrapnel['y']-y, shrapnel['x']+x, shrapnel['y']+y), fill=255)

			#Draw ship
			front_x = math.sin(math.radians(ast_ship['angle'])) *3.0 + ast_ship['x']
			front_y = math.cos(math.radians(ast_ship['angle'])) *3.0 + ast_ship['y']

			backleft_x = math.sin(math.radians(ast_ship['angle']-145)) *3.0 + ast_ship['x']
			backleft_y = math.cos(math.radians(ast_ship['angle']-145)) *3.0 + ast_ship['y']

			backright_x = math.sin(math.radians(ast_ship['angle']+145)) *3.0 + ast_ship['x']
			backright_y = math.cos(math.radians(ast_ship['angle']+145)) *3.0 + ast_ship['y']

			draw.line(( front_x, front_y, backleft_x, backleft_y), fill=255)
			draw.line(( front_x, front_y, backright_x, backright_y), fill=255)

	elif anim_state == 'deathstar':

		global deathstar_oldimage, deathstar_stars, deathstar_image

		if anim_percent > 0:
			draw.rectangle((0,0,width,height), outline=0, fill=0)
			for star in deathstar_stars:
				draw.ellipse((star['x'], star['y'], star['x']+star['size'], star['y']+star['size']), fill=255)
			
			image.paste(deathstar_oldimage,(-anim_percent*4,0))
			image.paste(deathstar_image,(-50+(100-anim_percent)*3,16))

		if anim_percent > 65 and anim_percent < 90:
			drawShadowedText(draw, 10, 48, "That's no moon!", fontDefault);

	elif anim_state == 'birthday':
		global birthday_icon, birthday_pos, birthday_age

		dist = anim_percent * 2

		draw.rectangle((0,0,128,64), fill=0)
		image.paste(birthday_icon, (birthday_pos[0], birthday_pos[1]-dist/2),birthday_icon)
		image.paste(birthday_icon, (birthday_pos[0], birthday_pos[1]+dist/2),birthday_icon)
		image.paste(birthday_icon, (birthday_pos[0]-dist/3, birthday_pos[1]-dist/4),birthday_icon)
		image.paste(birthday_icon, (birthday_pos[0]-dist/3, birthday_pos[1]+dist/4),birthday_icon)
		image.paste(birthday_icon, (birthday_pos[0]+dist/3, birthday_pos[1]-dist/4),birthday_icon)
		image.paste(birthday_icon, (birthday_pos[0]+dist/3, birthday_pos[1]+dist/4),birthday_icon)
		drawShadowedText(draw, birthday_pos[0]-20, birthday_pos[1]-10, birthday_age, fontBig)


#===============================================================================

# Function to manage the animated character states
def updateAnimation():

	global anim_state, anim_percent, oldimage

	if anim_state == 'pacman':

		global pac_x, pac_y, pac_radius, pac_blackout, pac_angle
		global pac_x_change, pac_angle_change

		pac_x = pac_x + pac_x_change
		if pac_x > 128+pac_radius+pac_blackout:
			pac_x = 0-pac_radius
			pac_y = random.randint(pac_radius, 63-pac_radius)
			anim_state = 'none'

		pac_angle = pac_angle + pac_angle_change
		if pac_angle > 45:
			pac_angle = 45
			pac_angle_change = pac_angle_change * -1
		else:
			if pac_angle < 5:
				pac_angle = 5
				pac_angle_change = pac_angle_change * -1
				
	elif anim_state == 'ghost':

		anim_percent = anim_percent + 5

	elif anim_state == 'ufo':

		anim_percent = anim_percent + 2

	elif anim_state == 'deathstar':

		global deathstar_oldimage

		if anim_percent == 0:
			# Start of animation
			del deathstar_stars[:]
			for star in range(1,30):
				speed = float(random.randint(1, 3))
				deathstar_stars.append({ 'x':random.randint(0,128), 'y':random.randint(0,64), 'dx':-speed, 'dy': 0, 'size':1})
			anim_percent = 1	# Running
			deathstar_oldimage = oldimage.copy()
			#print "Done copy into deathstar_oldimage"

		else:
			# Move stars
			for star in deathstar_stars:
				star['x'] = star['x'] + star['dx']
				star['y'] = star['y'] + star['dy']

				if star['x'] > 128:
					star['x'] = star['x'] - 128
				elif star['x'] < 0:
					star['x'] = star['x'] + 128

				if star['y'] > 64:
					star['y'] = star['y'] - 64
				elif star['y'] < 0:
					star['y'] = star['y'] + 64

			anim_percent = anim_percent + 1

		if len(deathstar_stars) == 0:
			anim_percent = 101	# End animation

		#print len(deathstar_stars)

	elif anim_state == 'asteroids':

		global ast_oldimage, ast_ship

		if anim_percent == 0:
			# Start of animation
			anim_percent = 1	# Running
			#ast_oldimage = Image.new('1', (width, height))
			#ast_oldimage.paste(oldimage,(0,0))
			ast_oldimage = oldimage.copy()
			#print "Done copy into ast_oldimage"
			del ast_bullets[:]
			del ast_shrapnel[:]

			ast_ship = {'x':130.0, 'y':random.randint(10,51), 'dx':0, 'dy':0, 'angle':270}

		else:
			if random.randint(1,2) == 1:
				ast_bullets.append({ 'x': (math.sin(math.radians(ast_ship['angle'])) *3.0 + ast_ship['x']), 'y': (math.cos(math.radians(ast_ship['angle'])) *3.0 + ast_ship['y']), 'dx': (math.sin(math.radians(ast_ship['angle'])) * 1)+ast_ship['dx'], 'dy': (math.cos(math.radians(ast_ship['angle'])) * 1+ast_ship['dy'])})

			# Move bullets
			for bullet in ast_bullets:
				for loop in range(1,5):
					bullet['x'] = bullet['x'] + bullet['dx']
					bullet['y'] = bullet['y'] + bullet['dy']

					if bullet['x'] >= 128 or bullet['x'] < 0:
						ast_bullets.remove(bullet)
						break
					elif bullet['y'] >= 64 or bullet['y'] < 0:
						ast_bullets.remove(bullet)
						break
					elif ast_oldimage.getpixel((bullet['x'],bullet['y'])) != 0:
						ast_shrapnel.append({ 'x':bullet['x'], 'y':bullet['y'], 'dx':random.randint(0,10)/10.0-0.5, 'dy': random.randint(0,10)/10.0-0.5, 'angle':random.randint(0,360), 'rotation': random.randint(-30,30), 'radius': 0.0, 'percent':0})
						ast_shrapnel.append({ 'x':bullet['x'], 'y':bullet['y'], 'dx':random.randint(0,10)/10.0-0.5, 'dy': random.randint(0,10)/10.0-0.5, 'angle':random.randint(0,360), 'rotation': random.randint(-30,30), 'radius': 0.0, 'percent':0})
						ast_shrapnel.append({ 'x':bullet['x'], 'y':bullet['y'], 'dx':random.randint(0,10)/10.0-0.5, 'dy': random.randint(0,10)/10.0-0.5, 'angle':random.randint(0,360), 'rotation': random.randint(-30,30), 'radius': 0.0, 'percent':0})
						ImageDraw.Draw(ast_oldimage).ellipse((bullet['x']-3, bullet['y']-3, bullet['x']+3, bullet['y']+3), fill=0)
						ast_bullets.remove(bullet)

						break

			# Move shrapnel
			for shrapnel in ast_shrapnel:
				shrapnel['angle'] = shrapnel['angle'] + shrapnel['rotation']
				shrapnel['x'] = shrapnel['x'] + shrapnel['dx']
				shrapnel['y'] = shrapnel['y'] + shrapnel['dy']

				shrapnel['percent'] = shrapnel['percent'] + 10
				shrapnel['radius'] = (5-abs(shrapnel['percent'] - 50)/10)/1.5

				if shrapnel['percent'] > 100:
					ast_shrapnel.remove(shrapnel)

			# Move ship
			ast_ship['x'] = ast_ship['x'] + ast_ship['dx']
			ast_ship['y'] = ast_ship['y'] + ast_ship['dy']

			# Dampen movement
			ast_ship['dx'] = ast_ship['dx'] * 0.99
			#ast_ship['dy'] = ast_ship['dy'] * 0.99

			# Point ship
			ast_ship['angle'] = 270 - (ast_ship['y'] - 31)*5

			# Thrust
			if ast_ship['angle'] > 315 or ast_ship['angle'] < 225 or ast_ship['dy']<0.25:
				ast_ship['dx'] = ast_ship['dx'] + math.sin(math.radians(ast_ship['angle']))/ 50
				ast_ship['dy'] = ast_ship['dy'] + math.cos(math.radians(ast_ship['angle']))/ 50
				ast_ship['thrust'] = True
			else:
				ast_ship['thrust'] = False

			# Collision
			x = ast_ship['x']
			y = ast_ship['y']
			if x>3 and x<125 and y>3 and y<60:
				if ast_oldimage.getpixel((x,y)) != 0 or \
				   ast_oldimage.getpixel((x+1,y)) != 0 or \
				   ast_oldimage.getpixel((x+2,y)) != 0 or \
				   ast_oldimage.getpixel((x-1,y)) != 0 or \
				   ast_oldimage.getpixel((x-2,y)) != 0 or \
				   ast_oldimage.getpixel((x,y-1)) != 0 or \
				   ast_oldimage.getpixel((x,y-2)) != 0 or \
				   ast_oldimage.getpixel((x,y+1)) != 0 or \
				   ast_oldimage.getpixel((x,y+2)) != 0:
					ast_ship['x'] = -1000

					for frag in range(1,10):
						ast_shrapnel.append({ 'x':x, 'y':y, 'dx':random.randint(0,10)/10.0-0.5, 'dy': random.randint(0,10)/10.0-0.5, 'angle':random.randint(0,360), 'rotation': random.randint(-30,30), 'radius': 0.0, 'percent':0})

		if ast_ship['x'] < -10 and len(ast_bullets) == 0 and len(ast_shrapnel) == 0:
			anim_percent = 101	# End animation

	elif anim_state == 'birthday':

		anim_percent = anim_percent + 5 

	else:

		if random.randint(1,60) == 1:

			anim_percent = 0
			anim_no = random.randint(1,100)

			if anim_no <= 25:
				anim_state = 'pacman'
			elif anim_no <= 50:
				anim_state = 'ghost'
			elif anim_no <= 75:
				anim_state = 'ufo'
			elif anim_no <= 93:
				anim_state = 'deathstar'
			elif anim_no <= 100:
				anim_state = 'asteroids'
			elif anim_no <= -1:
				anim_state = 'melt'
			else:
				anim_state = 'none'

	if anim_percent > 100:
		anim_state = 'none'
		anim_percent = 0

	if anim_state == 'none':
		global birthday_icon, birthday_pos, birthday_age
		if random.randint(1,10) == 1:

			currentday = strftime("%d/%m", localtime())

			if currentday == '29/02':	# dd/mm

				anim_state = 'birthday'
				birthday_age = str(int(strftime("%Y")) - 2012)
				birthday_icon = Image.open('images/star.png').convert("1")
				birthday_pos = (random.randint(20,108), random.randint(15,34))

			#elif currentday == 'dd/mm':  repeat for each birthday
			#	anim_state = 'birthday'
			#	birthday_age = str(int(strftime("%Y")) - <year>)
			#	birthday_icon = Image.open('images/star.png').convert("1")
			#	birthday_pos = (random.randint(20,108), random.randint(15,34))

			elif currentday == '04/05': # May the fourth be with you

				anim_state = 'deathstar'

		if anim_state == "none" and ipcbuf[60:80] != ".................":
			anim_state = ipcbuf[60:80].rstrip()
			ipcbuf[60:80] = "...................."

			if anim_state == "....................":
				anim_state = "none"

#===============================================================================

GPIO.setmode(GPIO.BCM)
GPIO.setup(22,GPIO.OUT)

disp = Adafruit_SSD1306.SSD1306_128_64(rst=27)
sensor = MCP9808.MCP9808()

anim_state = 'none'
anim_percent = 0

# Variables for animation
pac_x = 0
pac_x_change = 5
pac_y = 32
pac_radius = 10
pac_angle = 0
pac_angle_change = 30
pac_blackout = 50

ghost_image = Image.open('images/ghost_left.png').convert("1")

ufo_image = Image.open('images/ufo.png').convert("1")
ufo_image_mask = Image.open('images/ufo_mask.png').convert("1")
ufo_small_image = Image.open('images/ufo_small.png').convert("1")
ufo_small_image_mask = Image.open('images/ufo_small_mask.png').convert("1")

ast_bullets = []
ast_shrapnel = []
ast_oldimage = 'noimage'
ast_ship = 'none'

deathstar_stars = []
deathstar_oldimage = 'noimage'

deathstar_image = Image.open('images/deathstar.png').convert("1")

disp.begin()
sensor.begin()

# Clear display.
disp.clear()
disp.dim(True)
disp.set_contrast(0)
disp.display()

#-------------------------------------------------------------------------------

# Create mmap file for inter-thread communication
#ipcfile = os.open("/home/pi/thermostat/ramdisk/thermostat.ipcfile", os.O_CREAT |os.O_TRUNC|os.O_RDWR,0666)
ipcfile = os.open("/home/pi/thermostat/ramdisk/thermostat.ipcfile", os.O_RDWR,0666)
#assert os.write(ipcfile, '.' * mmap.PAGESIZE) == mmap.PAGESIZE
ipcbuf = mmap.mmap(ipcfile, mmap.PAGESIZE, mmap.MAP_SHARED);

#Setup mmap fields
ipcbuf[0:10] = str("10.5").ljust(10)        # Desired Temperature (thermostat)

#-------------------------------------------------------------------------------

# Create mmap file for transient statistics, etc
statsfile = os.open("/home/pi/thermostat/ramdisk/stats.ipcfile", os.O_CREAT |os.O_TRUNC|os.O_RDWR,0666)
#assert os.write(statsfile, '.' * mmap.PAGESIZE) == mmap.PAGESIZE
#statsbuf = mmap.mmap(statsfile, mmap.PAGESIZE, mmap.MAP_SHARED);
assert os.write(statsfile, '.' * 10240) == 10240
statsbuf = mmap.mmap(statsfile, 10240, mmap.MAP_SHARED);

#Setup mmap fields
statsbuf[0:10] = str("-1:-1").ljust(10)        # Time

#-------------------------------------------------------------------------------

boiler_state = False
ipcbuf[10:20] = str(0).ljust(10)		# Boiler Boost Minutes
flameImageNo = 1

while True:

	#-----------------------------------------------------------------------

	desiredtemp = float(ipcbuf[0:10])
	try:
		boiler_boost_mins = int(ipcbuf[10:20])
	except ValueError as ve:
		print "ValueError(boiler_boost_mins)"
		boiler_boost_mins = 0
	
	if anim_state == 'none':
		try:
			temp = sensor.readTempC()
		except IOError as e:
			print "IOError(readTempC) ({0}): {1}".format(e.errno, e.strerror)
	#-----------------------------------------------------------------------

	# Control heating
	if temp >= (desiredtemp+0.1):
		#..heating off
		boiler_state = False

	if temp < (desiredtemp-0.2):
		#..heating on
		boiler_state = True

	if boiler_boost_mins > 0:
		boiler_state = True

	#-----------------------------------------------------------------------
	# Stats #
	#-------#

	# get current time
	#currenttime = strftime("%H:%M", gmtime())
	currenttime = strftime("%H:%M", localtime())


	# compare hours with that in stats file
	if currenttime[0:2] != statsbuf[0:2]:
		#statsbuf[405:1000] = statsbuf[400:995]	# Shuffle hour stats
		#statsbuf[400:405] = str(round(temp,1)).ljust(5)    # Store hour stat
		statsbuf[2010:4000] = statsbuf[2000:3990]	# Shuffle hour stats
		statsbuf[2000:2005] = str(round(temp,1)).ljust(5)    # Store hour stat
		statsbuf[2000:2005] = str(round(temp,1)).ljust(5)    # Store hour stat
		statsbuf[2005:2007] = "00".ljust(2)    		# Burner count


	# compare hours & minutes with that in stats file
	if currenttime != statsbuf[0:5]:

		if boiler_boost_mins > 0:
			boiler_boost_mins = boiler_boost_mins - 1	
			#--------------------#
			# Store 'boost' time #
			#--------------------#
			ipcbuf[10:20] = str(boiler_boost_mins).ljust(10)


		statsbuf[85:380] = statsbuf[80:375]	# Shuffle minute stats
		statsbuf[80:84] = str(round(temp,1)).ljust(4)    # Store minute stat
		if (boiler_state):
			statsbuf[84] = "H"
		else:
			statsbuf[84] = " "

		hourly_H_count = int(statsbuf[2005:2007])
		if (boiler_state and (hourly_H_count < 99)):
			statsbuf[2005:2007] = str(hourly_H_count+1).ljust(2) 

		statsbuf[0:5] = currenttime.ljust(5)

		# Check rules
		for x in range(1, 20):
			line = ipcbuf[160+80*(x-1):160+80*(x-1)+20]
			
			setdays = line[0:7]
			settime = line[8:13]
			settemp = line[14:18]

			if settime == currenttime:
				ipcbuf[0:10] = str(settemp).ljust(10)


	#-----------------------------------------------------------------------
	# Control boiler #
	#----------------#

	GPIO.output(22,not(boiler_state))


	#-----------------------------------------------------------------------
	# Draw display #
	#--------------#

	# Create blank image for drawing.
	# Make sure to create image with mode '1' for 1-bit color.
	width = disp.width
	height = disp.height
	image = Image.new('1', (width, height))
	
	# Get drawing object to draw on image.
	draw = ImageDraw.Draw(image)
	
	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,width,height), outline=0, fill=0)

	updateAnimation()

	drawAnimationBehind()

	if (boiler_state):
		flameImageNo = flameImageNo + 1
		if flameImageNo > 4:
			flameImageNo = 1
		flameImage = Image.open('images/flame'+str(flameImageNo)+'.png').convert("1")
		image.paste(flameImage,(0,0))
	
	# Load default font.
	fontDefault = ImageFont.load_default()
	fontBig = ImageFont.truetype(filename='/usr/share/fonts/truetype/freefont/FreeSans.ttf', size=40)
	fontSmall = ImageFont.truetype(filename='/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', size=8)
	
	# Draw text
	drawShadowedText(draw, 5, 8, str(round(temp,1)),  fontBig)
	drawShadowedText(draw, 40, 48, '['+str(round(desiredtemp,1))+']', fontDefault)

	# Get time and draw it
	#draw.text((0, 32), strftime("%d/%m/%Y %H:%M:%S", gmtime()), font=fontdefault, fill=255);
	drawShadowedText(draw, 1, 0, strftime("%d/%m/%Y %H:%M:%S", localtime()), fontDefault);
	
	if (boiler_state):

		#drawShadowedText(draw, 100, 48, "On", fontDefault);

		if (boiler_boost_mins > 0):
			drawShadowedText(draw, 90, 32, "Boost", fontDefault);
			drawShadowedText(draw, 100, 40, str(boiler_boost_mins), fontDefault);
	
	else:
		drawShadowedText(draw, 100, 48, "Off", fontDefault);
		
		#drawShadowedText(draw, 100, 24, "T", fontSmall);
		#drawShadowedText(draw, 100+1, 32, ipcbuf[41], fontSmall);
		#	
		#drawShadowedText(draw, 116, 24, "O", fontSmall);
		#drawShadowedText(draw, 116+1, 32, ipcbuf[51], fontSmall);


	drawAnimationInfront()
		
	#drawShadowedText(draw, 5, 56, (anim_state+" (%i)") % anim_percent, fontSmall);
	#drawShadowedText(draw, 5, 56, (anim_state+" (%s)") % time.time(), fontSmall);

	#-----------------------------------------------------------------------
	# Display image #
	#---------------#

	#image = ImageOps.invert(image)
	#image = ~image

	disp.image(image)

	oldimage = Image.new('1', (width, height))
	#oldimage = image.copy()
	oldimage.paste(image,(0,0))

	try:
		disp.display()
	except IOError as e:
		print "IOError(display) ({0}): {1}".format(e.errno, e.strerror)


	#-----------------------------------------------------------------------
	# Store image for web interface #
	#-------------------------------#

	image.save("/home/pi/thermostat/ramdisk/ui.png")


	#-----------------------------------------------------------------------

	# If not animating then no need to update more than once per second
	if anim_state == 'none':
		time.sleep(1.0)


