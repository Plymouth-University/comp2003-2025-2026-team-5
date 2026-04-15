<?php
require_once "../auth/session_check.php";
require_once "../config/db.php";

$data = json_decode(file_get_contents("php://input"), true);

$lat = $data["lat"];
$lng = $data["lng"];
$radius = $data["radius"];
$patient_id = $data["patient_id"];

// build payload
$payload = json_encode([
    "type" => "circle",
    "center" => [
        "lat" => $lat,
        "lng" => $lng
    ],
    "radius" => $radius
]);

// 🔐 simple encryption (for now)
$key = "your-secret-key-123"; // move to config later
$encrypted_payload = openssl_encrypt($payload, "AES-128-ECB", $key);

// generate ID
$geofence_id = uniqid("geo_", true);

// created_by from session
$created_by = $_SESSION["account_id"];

// insert
$stmt = $conn->prepare("
    INSERT INTO geofence 
    (geofence_id, patient_id, name, shape_type, encrypted_payload, created_by)
    VALUES (?, ?, ?, ?, ?, ?)
");

$name = "Geofence " . date("Y-m-d H:i:s");
$shape_type = "circle";

$stmt->bind_param(
    "ssssss",
    $geofence_id,
    $patient_id,
    $name,
    $shape_type,
    $encrypted_payload,
    $created_by
);

$stmt->execute();

echo json_encode(["status" => "success"]);