<?php

session_start();

if(!isset($_SESSION["account_id"])){
    header("Location: /website/src/sign_in_page.html");
    exit();
}