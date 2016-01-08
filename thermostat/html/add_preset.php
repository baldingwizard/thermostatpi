<?php

header("Cache-Control: max-age=0");

$days = $_GET["days"];
$time = $_GET["time"];
$temp = $_GET["temp"];
$incdec = $_GET["incdec"];

$file = fopen("/home/pi/thermostat/ramdisk/thermostat.ipcfile", "r+");

for ($p=0; $p<20; $p++)
{
	//echo "Process ".$p;
	fseek($file, 160+$p*80);

	$_days   = fread($file, 8);
	$_time   = fread($file, 6);
	$_temp   = fread($file, 5);
	$_incdec = fread($file, 1);

	//echo $_days.":".$_time.":".$_temp.":".$_incdec;

	if (($_days == '........') &&
	   ($_time == '......') &&
	   ($_temp == '.....') &&
           ($_incdec == '.'))
	{
		// Found a blank record so update it
		fseek($file, 160+$p*80);
		fwrite($file, $days."          ", 8);
		fwrite($file, $time."          ", 6);
		fwrite($file, $temp."          ", 5);
		fwrite($file, $incdec."          ", 1);
		fflush($file);
		echo "Record inserted.";
		break;
	}
}

fclose($file);

?>
