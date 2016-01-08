<?php

header("Cache-Control: max-age=0");

$temp = $_GET["temp"]."            ";

echo "set temp to $temp"; 

$file = fopen("/home/pi/thermostat/ramdisk/thermostat.ipcfile", "r+");

fseek($file, 0);
fwrite($file, substr($temp,0,10));
fflush($file);
fclose($file);

echo "file closed";
?>
