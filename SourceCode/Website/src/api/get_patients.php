<?php
require_once "../auth/session_check.php";
require_once "../config/db.php";

header("Content-Type: application/json");

$account_id = $_SESSION["account_id"];

// get carer_id
$stmt = $conn->prepare("SELECT carer_id FROM carer WHERE account_id=?");
$stmt->bind_param("s", $account_id);
$stmt->execute();
$result = $stmt->get_result();
$carer = $result->fetch_assoc();

if (!$carer) {
    echo json_encode([]);
    exit;
}

$carer_id = $carer["carer_id"];

// get linked patients
$stmt = $conn->prepare("
    SELECT p.patient_id, p.name
    FROM carer_patient cp
    JOIN patient p ON cp.patient_id = p.patient_id
    WHERE cp.carer_id = ?
");
$stmt->bind_param("s", $carer_id);
$stmt->execute();
$result = $stmt->get_result();

$patients = [];

while ($row = $result->fetch_assoc()) {
    $patients[] = $row;
}

echo json_encode($patients);

error_reporting(E_ALL);
ini_set('display_errors', 1);