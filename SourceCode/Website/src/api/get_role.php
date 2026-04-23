<?php
require_once "../auth/session_check.php";

echo json_encode([
    "role" => $_SESSION["role"]
]);