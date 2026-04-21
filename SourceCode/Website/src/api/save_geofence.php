<?php
require_once "../auth/session_check.php";
require_once "../config/db.php";

header("Content-Type: application/json");

$data = json_decode(file_get_contents("php://input"), true);

$geofence_id = $data["geofence_id"] ?? null;
$patient_id = $data["patient_id"] ?? null;
$lat = $data["lat"] ?? null;
$lng = $data["lng"] ?? null;
$radius = $data["radius"] ?? null;

if (!$patient_id || !$lat || !$lng || !$radius) {
    echo json_encode(["error" => "Missing data"]);
    exit;
}

// store as JSON (fine for now)
$payload = json_encode([
    "lat" => $lat,
    "lng" => $lng,
    "radius" => $radius
]);

if ($geofence_id) {
    // UPDATE EXISTING
    $stmt = $conn->prepare("
        UPDATE geofence 
        SET encrypted_payload=?, patient_id=? 
        WHERE geofence_id=?
    ");
    $stmt->bind_param("sss", $payload, $patient_id, $geofence_id);
    $stmt->execute();

    echo json_encode([
        "status" => "updated",
        "geofence_id" => $geofence_id
    ]);

} else {
    // CREATE NEW
    $new_id = "geo_" . uniqid();

    $stmt = $conn->prepare("
        INSERT INTO geofence 
        (geofence_id, patient_id, name, shape_type, encrypted_payload, created_by)
        VALUES (?, ?, 'Geofence', 'circle', ?, ?)
    ");
    $stmt->bind_param(
        "ssss",
        $new_id,
        $patient_id,
        $payload,
        $_SESSION["account_id"]
    );
    $stmt->execute();

    echo json_encode([
        "status" => "created",
        "geofence_id" => $new_id
    ]);
}