<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <link href="./output.css" rel="stylesheet">

  <!-- Google Sign-In -->
  <script src="https://accounts.google.com/gsi/client" async defer></script>

  <!-- Dark mode (same as alerts.php) -->
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

  <script>
  function handleCredentialResponse(response) {

      fetch("/website/src/auth/google_login.php", {
          method: "POST",
          headers: {
              "Content-Type": "application/json"
          },
          body: JSON.stringify({
              token: response.credential
          })
      })
      .then(res => res.json())
      .then(data => {

          if(data.status === "new_user"){
              window.location.href = "/website/src/choose_role.html"
          }
          else{
              window.location.href = "/website/src/alerts.php"
          }

      });
  }
  </script>

</head>

<body class="bg-gray-100 dark:bg-gray-900 text-white font-sans">

<?php include "components/navbar.php"; ?>

<!-- Centered Content -->
<main class="flex items-center justify-center min-h-[80vh]">

  <div class="bg-gray-300 dark:bg-gray-800 p-10 rounded-xl shadow-lg text-center w-full max-w-md">

    <h1 class="text-3xl font-bold mb-6 text-black dark:text-white">
      Welcome Back
    </h1>

    <p class="mb-8 text-gray-700 dark:text-gray-300">
      Sign in securely using your Google account
    </p>

    <!-- Google Sign-In Setup -->
    <div id="g_id_onload"
         data-client_id="905184472532-eova2mmbpkv4dm75t4q1uom59b8v9h82.apps.googleusercontent.com"
         data-callback="handleCredentialResponse">
    </div>

    <!-- Larger Button -->
    <div class="flex justify-center">
      <div class="g_id_signin"
           data-type="standard"
           data-theme="outline"
           data-size="large"
           data-shape="pill"
           data-width="300">
      </div>
    </div>

  </div>

</main>

</body>
</html>