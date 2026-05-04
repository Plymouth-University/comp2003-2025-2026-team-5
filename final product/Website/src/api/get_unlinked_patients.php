<?php
require_once "../auth/session_check.php";
require_once "../config/db.php";

$account_id = $_SESSION["account_id"];

// get carer_id
$stmt = $conn->prepare("SELECT carer_id FROM carer WHERE account_id=?");
$stmt->bind_param("s", $account_id);
$stmt->execute();
$carer = $stmt->get_result()->fetch_assoc();

$carer_id = $carer["carer_id"];

// get patients NOT already linked
$stmt = $conn->prepare("
    SELECT patient_id, name 
    FROM patient
    WHERE patient_id NOT IN (
        SELECT patient_id FROM carer_patient WHERE carer_id=?
    )
");
$stmt->bind_param("s", $carer_id);
$stmt->execute();

$result = $stmt->get_result();
$data = [];

while ($row = $result->fetch_assoc()) {
    $data[] = $row;
}

echo json_encode($data);