<?php

require_once "../config/db.php";

session_start();
session_regenerate_id(true);

$data = json_decode(file_get_contents("php://input"), true);

$role = $data["role"];
$email = $_SESSION["email"];

$account_id = bin2hex(random_bytes(16));

$stmt = $conn->prepare("
INSERT INTO account (account_id, email, role, is_active, created_at)
VALUES (?, ?, ?, 1, NOW())
");

$stmt->bind_param("sss", $account_id, $email, $role);
$stmt->execute();

if($role === "carer"){

    $carer_id = bin2hex(random_bytes(16));

    $stmt = $conn->prepare("
    INSERT INTO carer (carer_id, account_id)
    VALUES (?, ?)
    ");

    $stmt->bind_param("ss", $carer_id, $account_id);
    $stmt->execute();
}

if($role === "patient"){

    $patient_id = bin2hex(random_bytes(16));

    $stmt = $conn->prepare("
    INSERT INTO patient (patient_id, account_id)
    VALUES (?, ?)
    ");

    $stmt->bind_param("ss", $patient_id, $account_id);
    $stmt->execute();
}

$_SESSION["account_id"] = $account_id;
$_SESSION["role"] = $role;

echo json_encode([
    "status" => "created"
]);