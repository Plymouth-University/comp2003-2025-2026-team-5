<?php

$host = "localhost";
$db = "geofence";
$user = "root";
$password = "";

$conn = new mysqli($host, $user, $password, $db);

if ($conn->connect_error) {
    die("Database connection failed");
}

?>