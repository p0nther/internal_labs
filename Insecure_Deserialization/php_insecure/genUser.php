<?php

class User
{
    public $username = "p0nther";
    public $role = "user";
}

echo serialize(new User());
echo base64_encode(
    serialize(
        new User()
    )
);
