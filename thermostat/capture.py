
from subprocess import call
import time

image=100000

while True:
	call(["cp", "ramdisk/ui.png", "ramdisk/ui_"+str(image)+".png"])
	time.sleep(0.2)
	image = image + 1
