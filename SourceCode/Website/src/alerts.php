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

  <!-- Leaflet -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css">
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

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

<?php include "components/navbar.php"; ?>

<main id="app"></main>

<script>

const app = document.getElementById("app");

// Get query param
const params = new URLSearchParams(window.location.search);
const id = params.get("id");

// LIST VIEW
if (!id){

  app.innerHTML = `
    <div class="container mx-auto text-center p-8">
      <div id="alertsGrid"
        class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
      </div>
    </div>
  `;

  fetch("/website/src/api/get_alerts.php")
  .then(res => res.json())
  .then(alerts => {

    const grid = document.getElementById("alertsGrid");

    alerts.forEach(alert => {

      grid.innerHTML += `
        <div class="bg-gray-400 dark:bg-gray-800 rounded-lg overflow-hidden shadow-md">

          <div id="map-${alert.broken_geofence_id}" class="w-full h-48"></div>

          <div class="p-4">
            <h3 class="text-xl font-semibold mb-2">
              ${alert.name} left safe zone
            </h3>
            <p class="text-gray-800 dark:text-gray-300">
              ${alert.created_at}
            </p>

            <a href="alerts.php?id=${alert.broken_geofence_id}"
              class="block mt-4 bg-sky-800 hover:bg-sky-700 text-white px-4 py-2 rounded-full">
              Learn More
            </a>
          </div>
        </div>
      `;

      // Create map after render
      setTimeout(() => createMap(alert), 0);

    });

  });

}

// DETAIL VIEW
else {

  app.innerHTML = `
    <div class="container mx-auto text-center px-4 py-4">
      <div id="alertDetail"></div>
    </div>
  `;

  fetch("/website/src/api/get_alerts.php")
  .then(res => res.json())
  .then(alerts => {

    const thisAlert = alerts.find(a => a.broken_geofence_id === id);

    if (!thisAlert){
      document.getElementById("alertDetail").innerHTML = "Alert not found";
      return;
    }

    const detail = document.getElementById("alertDetail");

    detail.innerHTML = `
      <div class="bg-gray-400 dark:bg-gray-800 rounded-lg overflow-hidden shadow-md">

        <div id="mapDetail" class="w-full h-96"></div>

        <div class="p-4">
          <h3 class="text-xl font-semibold mb-2">
            ${thisAlert.name} left safe zone
          </h3>

          <p class="text-gray-300">
            ${thisAlert.created_at}
          </p>

          <button
            class="mt-4 bg-sky-800 hover:bg-sky-700 text-white px-4 py-2 rounded-full">
            Dismiss alert
          </button>
        </div>
      </div>
    `;

    setTimeout(() => createDetailMap(thisAlert), 0);

  });

}

// MAP FUNCTIONS
function createMap(alert){

  const map = L.map(`map-${alert.broken_geofence_id}`).setView(
    [alert.latitude, alert.longitude],
    15
  );

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
    .addTo(map);

  L.marker([alert.latitude, alert.longitude]).addTo(map);
}


function createDetailMap(alert){

  const map = L.map("mapDetail").setView(
    [alert.latitude, alert.longitude],
    15
  );

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
    .addTo(map);

  L.marker([alert.latitude, alert.longitude]).addTo(map);
}

</script>

</body>
</html>