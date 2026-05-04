<?php

require_once "../config/db.php";
session_start();

$account_id = $_SESSION["account_id"];

// Step 1: get carer_id
$stmt = $conn->prepare("SELECT carer_id FROM carer WHERE account_id=?");
$stmt->bind_param("s", $account_id);
$stmt->execute();
$result = $stmt->get_result();
$carer = $result->fetch_assoc();

$carer_id = $carer["carer_id"];

// Step 2: get alerts ONLY for linked patients
$stmt = $conn->prepare("
SELECT 
    bg.broken_geofence_id,
    bg.latitude,
    bg.longitude,
    bg.created_at,
    p.patient_id,
    p.name
FROM broken_geofences bg
JOIN patient p ON bg.patient_id = p.patient_id
JOIN carer_patient cp ON p.patient_id = cp.patient_id
WHERE cp.carer_id = ?
ORDER BY bg.created_at DESC
");

$stmt->bind_param("s", $carer_id);
$stmt->execute();

$result = $stmt->get_result();

$alerts = [];

while($row = $result->fetch_assoc()){
    $alerts[] = $row;
}

echo json_encode($alerts);