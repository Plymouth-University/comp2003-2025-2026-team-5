<?php

require_once "../config/db.php";

session_start();
session_regenerate_id(true);

$data = json_decode(file_get_contents("php://input"), true);
$token = $data["token"];

$google_url = "https://oauth2.googleapis.com/tokeninfo?id_token=" . $token;

$response = file_get_contents($google_url);
$payload = json_decode($response, true);

$email = $payload["email"];

$stmt = $conn->prepare("SELECT account_id, role FROM account WHERE email=?");
$stmt->bind_param("s", $email);
$stmt->execute();

$result = $stmt->get_result();

if($result->num_rows > 0){

    $row = $result->fetch_assoc();

    $_SESSION["account_id"] = $row["account_id"];
    $_SESSION["role"] = $row["role"];

    echo json_encode([
        "status" => "existing_user"
    ]);

}else{

    $_SESSION["email"] = $email;

    echo json_encode([
        "status" => "new_user"
    ]);

}