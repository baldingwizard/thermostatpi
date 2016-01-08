<?php
//Script to read the file and generate an image containing a graph 

//....read file and generate array of details
$filecontents = file_get_contents("/home/pi/thermostat/ramdisk/stats.ipcfile");

//create image
$img = imagecreate(280,200);

//Setup
$backgroundcolour = imagecolorallocate($img, 255, 255, 255);
$gridcolour = imagecolorallocate($img, 128, 255, 128);
$tempdesiredcolour = imagecolorallocate($img, 0, 80, 0);
$tempmeasuredcolour = imagecolorallocate($img, 192, 0, 0);
$tempmeasuredcolour5 = imagecolorallocate($img, 255, 240, 240);
$tempmeasuredcolour25 = imagecolorallocate($img, 255, 192, 192);
$tempmeasuredcolour50 = imagecolorallocate($img, 255, 128, 128);
$tempmeasuredcolour75 = imagecolorallocate($img, 255, 64, 64);
$tempmeasuredcolour100 = imagecolorallocate($img, 255, 0, 0);
$burnercolour = imagecolorallocate($img, 255, 0, 0);
$extractfancolour = imagecolorallocate($img, 128, 128, 255);

//....draw static stuff
imagesetthickness($img,2);
imagerectangle($img, 20, 20, 260, 180, $gridcolour);
imagerectangle($img, 20, 20, 220, 180, $gridcolour);
imagerectangle($img, 20, 20, 180, 180, $gridcolour);
imagerectangle($img, 20, 20, 140, 180, $gridcolour);
imagerectangle($img, 20, 20, 100, 180, $gridcolour);
imagerectangle($img, 20, 20, 60, 180, $gridcolour);

imagesetthickness($img,1);
imagerectangle($img, 20, 20, 260, 180, $gridcolour);
imagerectangle($img, 20, 20, 260, 160, $gridcolour);
imagerectangle($img, 20, 20, 260, 140, $gridcolour);
imagerectangle($img, 20, 20, 260, 120, $gridcolour);
imagerectangle($img, 20, 20, 260, 100, $gridcolour);
imagerectangle($img, 20, 20, 260, 80, $gridcolour);
imagerectangle($img, 20, 20, 260, 60, $gridcolour);
imagerectangle($img, 20, 20, 260, 40, $gridcolour);

//imagestring($img, FONT, X, Y, "10", $gridcolour);

//... axis labels


// Plot 'desired' temp
$lastx = -1;
$lasty = -1;
for ($t=0; $t<60; $t++)
{
	$temp = (float)substr($filecontents,2000 + $t*10,4);
	$heat = (float)substr($filecontents,2000 + $t*10 + 5,2);

	$x = 260 - $t * 4 -3;
	$y = 180 - $temp * 4;

	if ($y > 180) { $y = 180; }

	if ($heat >= 55)
	{
		imagefilledrectangle($img, $x, 180, $x+3, $y, $tempmeasuredcolour100);
	}
	else if ($heat >= 40)
	{
		imagefilledrectangle($img, $x, 180, $x+3, $y, $tempmeasuredcolour75);
	}
	else if ($heat >= 25)
	{
		imagefilledrectangle($img, $x, 180, $x+3, $y, $tempmeasuredcolour50);
	}
	else if ($heat >= 10)
	{
		imagefilledrectangle($img, $x, 180, $x+3, $y, $tempmeasuredcolour25);
	}
	else if ($heat > 0)
	{
		imagefilledrectangle($img, $x, 180, $x+3, $y, $tempmeasuredcolour5);
	}
	else
	{
		imagefilledrectangle($img, $x, 180, $x+3, $y, $backgroundcolour);
	}

	if (($lastx>=0)&&($lasty>=0)&&($x>=0)&&($y>=0))
	{
		imageline($img, $lastx, $lasty, $x, $y, $tempmeasuredcolour);
	}
	$lastx = $x;
	$lasty = $y;

}

//return image data
header("Content-type: image/png");
imagepng($img);

//tidy up
imagecolordeallocate($img,$backgroundcolour);
imagecolordeallocate($img,$gridcolour);
imagecolordeallocate($img,$tempdesiredcolour);
imagecolordeallocate($img,$tempmeasuredcolour);
imagecolordeallocate($img,$tempmeasuredcolour5);
imagecolordeallocate($img,$tempmeasuredcolour25);
imagecolordeallocate($img,$tempmeasuredcolour50);
imagecolordeallocate($img,$tempmeasuredcolour75);
imagecolordeallocate($img,$tempmeasuredcolour100);
imagecolordeallocate($img,$burnercolour);
imagecolordeallocate($img,$extractfancolour);

imagedestroy($img);

?>
