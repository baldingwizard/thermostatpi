<?php

header("Cache-Control: max-age=0");

$state = $_GET["state"]."                      ";

echo "set state to $state"; 

$file = fopen("/home/pi/thermostat/ramdisk/thermostat.ipcfile", "r+");

fseek($file, 60);
fwrite($file, substr($state."                    ",0,20));

fflush($file);
fclose($file);

echo "file closed";
?>
