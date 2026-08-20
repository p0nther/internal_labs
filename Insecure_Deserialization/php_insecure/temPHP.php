<?php

class Temp
{
	public $username;
	public $password;
	private $hint;
}

$instance = new Temp();
$instance->username="p0nther";
$instance->password="idk";
// $instance->hint= "displine, plan,won't surender, avoid distruction";

$serial=base64_encode(serialize($instance));
echo "\n\nserialized without encode: " . base64_decode($serial);
echo "\n\nserialized output with encode: " . $serial;
echo "\n__________________________________________________";

echo "\n\n Deserialize it reconstruct obj: \n";
var_dump(unserialize(base64_decode($serial)));


echo "\n\n";
$json_serial=json_encode($instance);
$deserial_json=json_decode($json_serial,true);
echo "save serial with json: \n" . $json_serial;
echo "\nsave Deserial with json: \n" ;
var_dump($deserial_json);
