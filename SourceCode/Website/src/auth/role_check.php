<?php

if(!isset($_SESSION["account_id"])){
    header("Location: /website/src/sign_in_page.html");
    exit();
}

function requireRole($allowed_roles){

    if(!isset($_SESSION["role"]) || !in_array($_SESSION["role"], $allowed_roles)){
        
        echo "Your role does not grant access to this feature";
        exit();
    }
}
