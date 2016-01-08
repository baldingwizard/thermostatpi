<html>
<head>
<meta name="viewport" content="width=320; initial-scale=1.0; maximum-scale=1.0; user-scalable=0;">
</head>
<body style='margin: 0px;'>
<div style='display: block; background: #c0c0c0; padding: 5px;'>
<input type='button' value='Back' onclick='window.location="index.php"'>
<div style='background: #ffc0c0'>
<center>
<b>NOTE : This page isn't finished yet so some features are incomplete!!!</b>
</center>
</div>
</div>
<div>
<?php
//Script to display presets

//....read file
$filecontents = file_get_contents("/home/pi/thermostat/ramdisk/thermostat.ipcfile");

echo "<div style='border: 1px solid black;'>";
echo "<table border=0>";
echo "<tr>";
echo "<th>Days</th>";
echo "<th>Time</th>";
echo "<th>Temp</th>";
echo "<th>Inc/Dec</th>";
echo "<th></th>";
echo "</tr>";

for ($p=0; $p<20; $p++)
{
	$daysOfWeek = substr($filecontents,160 + $p*80,7);
	$time       = substr($filecontents,160 + $p*80+8,5);
	$temp       = substr($filecontents,160 + $p*80+8+6,4);
	$incdec     = substr($filecontents,160 + $p*80+8+6+5,1);

	if ($incdec == '-')	{ $incdec = 'Decrease'; }
	else if ($incdec == '+')	{ $incdec = 'Increase'; }
	else				{ $incdec = ' '; }

	if (substr($daysOfWeek,0,1) == '.')
	{
		continue;
	}

	echo "<tr>";
	echo "<td>".$daysOfWeek."</td>";
	echo "<td>".$time."</td>";
	echo "<td align='right'>".number_format($temp,1)."</td>";
	echo "<td>&nbsp;".$incdec."</td>";
	echo "<td><input type='button' value='Remove' onclick='removePreset(\"$daysOfWeek\",\"$time\",\"$temp\",\"$incdec\");'></td>";
	echo "</tr>";
}

echo "</table>";

?>
<div style='border: 1px solid black;'>
<form>
<table>
<tr>
<td>Days</td>
<td>
	<select id='fld_days'>
		<option selected=selected>All</option>
	<!--	<option>Mon-Fri</option> -->
	<!--	<option>Sat/Sun</option> -->
	<!--	<option>Mon</option> -->
	<!--	<option>Tue</option> -->
	<!--	<option>Wed</option> -->
	<!--	<option>Thu</option> -->
	<!--	<option>Fri</option> -->
	<!--	<option>Sat</option> -->
	<!--	<option>Sun</option> -->
	</select>
</td>
</tr><tr>
<td>Time</td>
<td>
	<select id='fld_time_hour'>
		<option>00</option>
		<option>01</option>
		<option>02</option>
		<option>03</option>
		<option>04</option>
		<option>05</option>
		<option>06</option>
		<option>07</option>
		<option>08</option>
		<option>09</option>
		<option>10</option>
		<option>11</option>
		<option>12</option>
		<option>13</option>
		<option>14</option>
		<option>15</option>
		<option>16</option>
		<option>17</option>
		<option>18</option>
		<option>19</option>
		<option>20</option>
		<option>21</option>
		<option>22</option>
		<option>23</option>
	</select>
:
	<select id='fld_time_minute'>
		<option>00</option>
		<option>05</option>
		<option>10</option>
		<option>15</option>
		<option>20</option>
		<option>25</option>
		<option>30</option>
		<option>35</option>
		<option>40</option>
		<option>45</option>
		<option>50</option>
		<option>55</option>
	</select>
</td>
</tr><tr>
<td>Temp</td>
<td>
	<select id='fld_temp'>
		<option>5.0</option>
		<option>5.5</option>
		<option>6.0</option>
		<option>6.5</option>
		<option>7.0</option>
		<option>7.5</option>
		<option>8.0</option>
		<option>8.5</option>
		<option>9.0</option>
		<option>9.5</option>
		<option>10.0</option>
		<option>10.5</option>
		<option>11.0</option>
		<option>11.5</option>
		<option>12.0</option>
		<option>12.5</option>
		<option>13.0</option>
		<option>13.5</option>
		<option>14.0</option>
		<option>14.5</option>
		<option>15.0</option>
		<option>15.5</option>
		<option>16.0</option>
		<option>16.5</option>
		<option>17.0</option>
		<option>17.5</option>
		<option>18.0</option>
		<option>18.5</option>
		<option>19.0</option>
		<option>19.5</option>
		<option>20.0</option>
		<option>20.5</option>
		<option>21.0</option>
		<option>21.5</option>
		<option>22.0</option>
		<option>22.5</option>
		<option>23.0</option>
		<option>23.5</option>
		<option>24.0</option>
	</select>
</td>
</tr><tr>
<td>Inc/Dec</td>
<td>
	<select id='fld_incdec'>
		<option>Always</option>
	<!--	<option>Increase</option> -->
	<!--	<option>Decrease</option> -->
	</select>
</td>
</tr>
</table>
<input type='button' value='Add' onclick='addPreset();'>
</form>
</div>
</div>

<script>
function removePreset(days, time, temp, incdec)
{

	if (incdec == 'Decrease')	{ incdec = '-'; }
	else if (incdec == 'Increase')	{ incdec = '+'; }
	else				{ incdec = ' '; }

        xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET","remove_preset.php?days="+encodeURI(days)+"&time="+encodeURI(time)+"&temp="+encodeURI(temp)+"&incdec="+encodeURI(incdec), false);      //synchronous
        xmlhttp.send();
	//alert(xmlhttp.responseText);

	location.reload();
}

function addPreset()
{
	var days = document.getElementById('fld_days').value;
	var time = document.getElementById('fld_time_hour').value +
			":"+
			document.getElementById('fld_time_minute').value;
	var temp = document.getElementById('fld_temp').value;
	var incdec = document.getElementById('fld_incdec').value;

	if (incdec == 'Decrease')	{ incdec = '-'; }
	else if (incdec == 'Increase')	{ incdec = '+'; }
	else				{ incdec = ' '; }

        xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET","add_preset.php?days="+encodeURI(days)+"&time="+encodeURI(time)+"&temp="+encodeURI(temp)+"&incdec="+encodeURI(incdec), false);      //synchronous
        xmlhttp.send();
	//alert(xmlhttp.responseText);

	location.reload();
}
</script>

</body>
</html>
