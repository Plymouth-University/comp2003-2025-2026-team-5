<?php
require_once "../auth/session_check.php";
require_once "../config/db.php";

header("Content-Type: application/json");

$patient_id = $_GET["patient_id"] ?? null;

if (!$patient_id) {
    echo json_encode([]);
    exit;
}

$stmt = $conn->prepare("
    SELECT geofence_id, encrypted_payload 
    FROM geofence 
    WHERE patient_id=? AND is_active=1
");

$stmt->bind_param("s", $patient_id);
$stmt->execute();
$result = $stmt->get_result();

$geofences = [];

while ($row = $result->fetch_assoc()) {
    $geofences[] = $row;
}

echo json_encode($geofences);

error_reporting(E_ALL);
ini_set('display_errors', 1);