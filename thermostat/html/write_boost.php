<?php

header("Cache-Control: max-age=0");

$boost = $_GET["boost"]."            ";

echo "set boost to $boost"; 

$file = fopen("/home/pi/thermostat/ramdisk/thermostat.ipcfile", "r+");

if ($boost == undefined)
{
	//Read the current 'boost' minutes
	fseek($file, 10);
	$boost_mins = (int)(fread($file,10));

	echo "prev=".$boost_mins; 

	if ($boost_mins >= 59)
	{
		$boost_mins = 0;
	}
	else if ($boost_mins >= 44)
	{
		$boost_mins = 60;
	}
	else if ($boost_mins >= 29)
	{
		$boost_mins = 45;
	}
	else if ($boost_mins >= 14)
	{
		$boost_mins = 30;
	}
	else 
	{
		$boost_mins = 15;
	}
}
else
{
	$boost_mins = $boost;
}

fseek($file, 10);
fwrite($file, substr($boost_mins."          ",0,10));

echo "aft=".$boost_mins; 

fflush($file);
fclose($file);

echo "file closed";
?>
