<?php
require_once "../auth/session_check.php";
require_once "../config/db.php";

$data = json_decode(file_get_contents("php://input"), true);

$patient_id = $data["patient_id"];
$account_id = $_SESSION["account_id"];

// get carer_id
$stmt = $conn->prepare("SELECT carer_id FROM carer WHERE account_id=?");
$stmt->bind_param("s", $account_id);
$stmt->execute();
$carer = $stmt->get_result()->fetch_assoc();

$carer_id = $carer["carer_id"];

// insert link
$stmt = $conn->prepare("
    INSERT INTO carer_patient (carer_id, patient_id)
    VALUES (?, ?)
");
$stmt->bind_param("ss", $carer_id, $patient_id);
$stmt->execute();

echo json_encode(["status" => "paired"]);