<?php
require_once "../auth/session_check.php";
require_once "../config/db.php";

$account_id = $_SESSION["account_id"];

// get patient_id
$stmt = $conn->prepare("SELECT patient_id FROM patient WHERE account_id=?");
$stmt->bind_param("s", $account_id);
$stmt->execute();
$patient = $stmt->get_result()->fetch_assoc();

$patient_id = $patient["patient_id"];

// get carers
$stmt = $conn->prepare("
    SELECT c.carer_id, c.name
    FROM carer_patient cp
    JOIN carer c ON cp.carer_id = c.carer_id
    WHERE cp.patient_id=?
");
$stmt->bind_param("s", $patient_id);
$stmt->execute();

$result = $stmt->get_result();
$data = [];

while ($row = $result->fetch_assoc()) {
    $data[] = $row;
}

echo json_encode($data);