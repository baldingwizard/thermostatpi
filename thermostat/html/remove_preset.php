<?php

header("Cache-Control: max-age=0");

$days = $_GET["days"];
$time = $_GET["time"];
$temp = $_GET["temp"];
$incdec = $_GET["incdec"];

//echo "Trying to remove '$days', '$time', '$temp', '$incdec'.";

$file = fopen("/home/pi/thermostat/ramdisk/thermostat.ipcfile", "r+");

for ($p=0; $p<20; $p++)
{
	//echo "Process ".$p;
	fseek($file, 160+$p*80);
	$_days   = fread($file, 8);
	$_time   = fread($file, 6);
	$_temp   = fread($file, 5);
	$_incdec = fread($file, 1);

	//echo "$days == $_days";
	//echo "$time == $_time";
	//echo "'$temp' == '$_temp'";
	//echo "$incdec == $_incdec";

	if (
		(rtrim($days) == rtrim($_days)) &&
	   	(rtrim($time) == rtrim($_time)) &&
	   	(number_format(rtrim($temp),1) == number_format(rtrim($_temp),1)) &&
           (rtrim($incdec) == rtrim($_incdec)))
	{
		// Found a match so delete it
		fseek($file, 160+$p*80);
		fwrite($file, '........................................');
		fflush($file);
		echo "Record deleted.";
		break;
	}
}

fclose($file);

?>
