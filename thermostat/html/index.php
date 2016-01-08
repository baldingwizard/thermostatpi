<html>
<head>
<title>Thermostat</title>
<meta http-equiv="refresh" content="30"/>
<meta name="viewport" content="width=320; initial-scale=1.0; maximum-scale=1.0; user-scalable=0;">
<body style='margin: 0px;'>
<div style='background: #ffffff; height: 75%; location: absolute; top: 0px;'>
<div style='display: block; background: #c0c0c0; padding: 5px;'>
<?php

$ipc = file_get_contents('/home/pi/thermostat/ramdisk/thermostat.ipcfile');

$ipc_temp_desired = substr($ipc,0,10);
$ipc_boost	  = round(substr($ipc,10,10));
$ipc_boiler_state = substr($ipc,11,1);

//------------------------------------------------------------------------------

echo "Thermostat ";

echo "<select onchange='settemp(this)'>";

for ($t = 5; $t < 26; $t += 0.5)
{
	if (round($t,1) == round($ipc_temp_desired,1))
	{
		echo "<option selected='selected'>$t</option>";
	}
	else
	{
		echo "<option>$t</option>";
	}
	
}

echo "</select>";

//------------------------------------------------------------------------------

echo "<div style='float: right;'>";
echo "Boost ";

echo "<select onchange='setboost(this)'>";

$found = false;
for ($b = 0; $b <= 60; $b += 15)
{
	if (round($b,1) == round($ipc_boost,1))
	{
		echo "<option selected='selected'>$b</option>";
		$found = true;
	}
	else
	{
		echo "<option>$b</option>";
	}
	
}
if (!$found)
{
	echo "<option selected='selected'>$ipc_boost</option>";
}

echo "</select>";
echo "</div>";

//------------------------------------------------------------------------------

?>
</div>
<div style='overflow-y: auto; width: 100%;'>
<center>
<img style='display: block; height: 40%;' src='temp_minutes.php'>
<img style='display: block; height: 40%;' src='temp_hours.php'>
</center>
<div style='display: block; text-align: center'>
<input type='button' value='Presets' onclick='window.location="presets.php"'>
<select onchange='setstate(this)'>
<option selected='selected'>none</option>
<option>pacman</option>
<option>ghost</option>
<option>ufo</option>
<option>deathstar</option>
<option>asteroids</option>
</select>
</div>
</div>
</div>
</div>
<div style='background: black; width: 100%; height: 25%; padding: 10px; align: center; location: absolute; bottom: 0px; left: 0px;'>
<center>
<img style='max-width: 256px; height: 100%;' id='ui' width='100%' src=ui.png>
</center>
</div>
<script>
function settemp(element)
{
	var temp = element.value;
	xmlhttp = new XMLHttpRequest();
	//xmlhttp.open("GET","write_temp.php?temp="+temp);
	xmlhttp.open("GET","write_temp.php?temp="+temp, false);	//synchronous
	xmlhttp.send();
	setTimeout(function() { location.reload(true)} , 2000);
}

function setboost(element)
{
	var boost = element.value;
	xmlhttp = new XMLHttpRequest();
	xmlhttp.open("GET","write_boost.php?boost="+boost, false);	//synchronous
	xmlhttp.send();
	setTimeout(function() { location.reload(true)} , 2000);
}

function setstate(element)
{
	var state = element.value;
	xmlhttp = new XMLHttpRequest();
	xmlhttp.open("GET","write_state.php?state="+state, false);	//synchronous
	xmlhttp.send();
	setTimeout(function() { location.reload(true)} , 2000);
}

function updateImage()
{
	document.getElementById('ui').src = 'ui.png?x='+String(new Date().getTime()/1000);
	setTimeout(updateImage, 500);
}

updateImage();

</script>

</body>
</html>
