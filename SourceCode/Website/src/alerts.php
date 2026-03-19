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
    

  <main id="app"></main>


  <script>
    const app = document.getElementById("app");
      // there MUST be security for this section so that a carer can only see alerts for the patients that they care for
      const alerts = [
    {
      id: 1,
      patientName: "[patient name]",
      time: "12/12/25 14:35",
      message: "deviated from their routine route",
      lat: 50,
      lng: 5,
      mapImage: "images/placeholder-map.jpg"
    },
    {
      id: 2,
      patientName: "[patient name]",
      time: "10/10/25 16:57",
      message: "added a new route to their routine",
      lat: 51,
      lng: 6,
      mapImage: "images/placeholder-map.jpg"
    }
    ];

    // this query parsing is the code block I developed using AI to produce a plan as to how I can achieve this.
    const queryString = window.location.search;
    const params = new URLSearchParams(queryString);
    const id = params.get("id");
    if (!id){
      app.innerHTML += `
        <!-- This is the format block that can hold and stack a multitude of alerts -->
        <div class="container mx-auto text-center p-18">
          <div id="alertsGrid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
          </div>
        </div>
        `;
    

      const grid = document.getElementById("alertsGrid");

      alerts.forEach(alert => {
        grid.innerHTML += `
          <div class="bg-gray-400 dark:bg-gray-800 rounded-lg overflow-hidden shadow-md">
            <img src="${alert.mapImage}" class="w-full h-60 sm:h-44 object-cover">
            <div class="p-4">
              <h3 class="text-xl font-semibold mb-2">
                ${alert.patientName} ${alert.message}
              </h3>
              <p class="text-gray-800 dark:text-gray-300">${alert.time}</p>
              <a href="alerts.php?id=${alert.id}"
                class="block mt-4 bg-sky-800 hover:bg-sky-700 dark:bg-amber-600 dark:hover:bg-amber-500 text-black dark:text-white px-4 py-2 rounded-full text-lg font-semibold">
                Learn More
              </a>
            </div>
          </div>
        `;
      }); 
    } else{
    app.innerHTML += `
    <div class="container mx-auto text-center sm:px-18 px-4 py-2">
      <div id="alertsDetail"></div>
    </div>
    `;
      const alertId = Number(id);
      const thisAlert = alerts.find(a => a.id === alertId);
      const detail = document.getElementById("alertsDetail");
        detail.innerHTML = `
          <div class="bg-gray-400 dark:bg-gray-800 rounded-lg overflow-hidden shadow-md">
            <div> <!-- blank div for the image to center itself inside of -->
              <img src="${thisAlert.mapImage}" class="w-full max-h-140 max-w-300 object-cover mx-auto">
            </div>
            <div class="p-4">
              <h3 class="text-black text-xl font-semibold mb-2">
                ${thisAlert.patientName} ${thisAlert.message} 
              </h3>
              <p class="text-gray-300">${thisAlert.time}</p>
              
              <!-- this should be expanded on later in development, it should label the alert as archived, NOT deleting it but instead just marking it to be shown elsewhere -->
              <a href=""class="block mt-4 dark:bg-amber-600 dark:hover:bg-amber-500 bg-sky-800 hover:bg-sky-700 text-white px-4 py-2 rounded-full text-lg font-semibold w-36">
                Dismiss alert
              </a>
            </div>
          </div>
        `; 
    }
    </script>
</body>
</html>