<?php
require_once "auth/session_check.php";
require_once "auth/role_check.php";
requireRole(["carer"]);
?>
<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="./output.css" rel="stylesheet">
  <script>
    // this is code directly from the tailwind documentation: https://tailwindcss.com/docs/dark-mode
    // On page load or when changing themes, best to add inline in `head` to avoid FOUC

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

    <?php include "components/navbar.php"; ?>
    
    <main id="app">
        <p class="text-2xl">
            This will be the page where the Patient and Carer view, create, edit or delete geofence boundaries.
        </p>
    </main>
</body>
</html>