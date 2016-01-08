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
$burnercolour = imagecolorallocate($img, 255, 224, 224);
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


//... axis labels


// Plot 'desired' temp
$lastx = -1;
$lasty = -1;
for ($t=0; $t<60; $t++)
{
	$temp = (float)substr($filecontents,80 + $t*5,4);
	$heat = substr($filecontents,80 + $t*5+4,1);

	$x = 260 - $t * 4 -3;
	$y = 180 - $temp * 4;

	if ($y > 180) { $y = 180; }

	if ($heat == 'H')
	{
		imagefilledrectangle($img, $x, 180, $x+3, $y, $burnercolour);
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
imagecolordeallocate($img,$burnercolour);
imagecolordeallocate($img,$extractfancolour);

imagedestroy($img);

?>
