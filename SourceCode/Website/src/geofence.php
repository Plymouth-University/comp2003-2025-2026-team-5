<?php
require_once "auth/session_check.php";
require_once "auth/role_check.php";
requireRole(["carer"]); // carers create geofences
?>

<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="./output.css" rel="stylesheet">

  <!-- Leaflet -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css">
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

  <!-- Leaflet Draw -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet-draw/dist/leaflet.draw.css">
  <script src="https://unpkg.com/leaflet-draw/dist/leaflet.draw.js"></script>

  <style>
    #map { height: 500px; }
  </style>
</head>

<body class="bg-gray-100 dark:bg-gray-900 text-white">

<?php include "components/navbar.php"; ?>

<div class="mb-4">
  <label class="block mb-2 text-lg">Select Patient:</label>
  <select id="patientSelect" class="text-black p-2 rounded w-full">
    <option value="">Loading...</option>
  </select>
</div>


<div class="container mx-auto p-6">
  <h1 class="text-2xl mb-4">Create Geofence</h1>
  <div id="map" class="rounded-lg"></div>
</div>

<script>
let selectedPatientId = null;

// load patients
fetch("api/get_patients.php")
.then(res => res.json())
.then(patients => {
    const select = document.getElementById("patientSelect");
    select.innerHTML = "";

    if (patients.length === 0) {
        select.innerHTML = "<option>No patients linked</option>";
        return;
    }

    patients.forEach(p => {
        const option = document.createElement("option");
        option.value = p.patient_id;
        option.textContent = p.name || p.patient_id;
        select.appendChild(option);
    });

    selectedPatientId = patients[0].patient_id;
});

// update selection
document.getElementById("patientSelect").addEventListener("change", (e) => {
    selectedPatientId = e.target.value;
});

// ---------------- MAP ----------------

const map = L.map('map').setView([51.5, -0.1], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// optional location
navigator.geolocation.getCurrentPosition(pos => {
    map.setView([pos.coords.latitude, pos.coords.longitude], 15);
});

const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

const drawControl = new L.Control.Draw({
    draw: {
        polygon: false,
        rectangle: false,
        polyline: false,
        marker: false,
        circlemarker: false,
        circle: true
    },
    edit: {
        featureGroup: drawnItems
    }
});
map.addControl(drawControl);

// ---------------- SAVE ----------------

function saveGeofence(layer) {

    if (!selectedPatientId) {
        alert("Please select a patient first");
        return;
    }

    const center = layer.getLatLng();
    const radius = layer.getRadius();

    fetch("api/save_geofence.php", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            lat: center.lat,
            lng: center.lng,
            radius: radius,
            patient_id: selectedPatientId
        })
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);
        alert("Geofence saved!");
    });
}

// only 1 circle
map.on(L.Draw.Event.CREATED, function (e) {
    drawnItems.clearLayers();
    drawnItems.addLayer(e.layer);
    saveGeofence(e.layer);
});

map.on(L.Draw.Event.EDITED, function (e) {
    e.layers.eachLayer(layer => saveGeofence(layer));
});
</script>

</body>
</html>