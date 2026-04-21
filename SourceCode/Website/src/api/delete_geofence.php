<?php
require_once "../auth/session_check.php";
require_once "../config/db.php";

$data = json_decode(file_get_contents("php://input"), true);
$geofence_id = $data["geofence_id"];

// delete
$stmt = $conn->prepare("DELETE FROM geofence WHERE geofence_id=?");
$stmt->bind_param("s", $geofence_id);
$stmt->execute();

echo json_encode(["status"=>"deleted"]);