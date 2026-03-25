<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="./output.css" rel="stylesheet">
  <!-- Dark mode -->
  <script>
    if (
        localStorage.theme === "dark" ||
        (!("theme" in localStorage) &&
        window.matchMedia("(prefers-color-scheme: dark)").matches)
    ) {
        document.documentElement.classList.add("dark");
    } else {
        document.documentElement.classList.remove("dark");
    }
  </script>

</head>

<body class="bg-gray-100 dark:bg-gray-900 text-white font-sans">

<?php

if(!isset($_SESSION["account_id"])){
    header("Location: /website/src/sign_in_page.php");
    exit();
}

function requireRole($allowed_roles){

    if(!isset($_SESSION["role"]) || !in_array($_SESSION["role"], $allowed_roles)){

        include "components/navbar.php";
        echo '<p class="text-2xl">Your role does not grant access to this feature</p>';
        exit();
    }
}
?>
</body>
</html>