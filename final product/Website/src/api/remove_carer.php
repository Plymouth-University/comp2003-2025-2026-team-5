<?php
require_once "../auth/session_check.php";
require_once "../config/db.php";

$data = json_decode(file_get_contents("php://input"), true);

$carer_id = $data["carer_id"];
$account_id = $_SESSION["account_id"];

// get patient_id
$stmt = $conn->prepare("SELECT patient_id FROM patient WHERE account_id=?");
$stmt->bind_param("s", $account_id);
$stmt->execute();
$patient = $stmt->get_result()->fetch_assoc();

$patient_id = $patient["patient_id"];

// delete link
$stmt = $conn->prepare("
    DELETE FROM carer_patient
    WHERE carer_id=? AND patient_id=?
");
$stmt->bind_param("ss", $carer_id, $patient_id);
$stmt->execute();

echo json_encode(["status" => "removed"]);