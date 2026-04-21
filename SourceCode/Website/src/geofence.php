<?php
require_once "auth/session_check.php";
require_once "auth/role_check.php";
requireRole(["carer"]);
?>

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="./output.css" rel="stylesheet">

<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css">
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<link rel="stylesheet" href="https://unpkg.com/leaflet-draw/dist/leaflet.draw.css">
<script src="https://unpkg.com/leaflet-draw/dist/leaflet.draw.js"></script>

<style>
#map { height: 500px; }
</style>
</head>

<body class="bg-gray-100 dark:bg-gray-900 text-white">

<?php include "components/navbar.php"; ?>

<div class="px-6 mt-6">
  <div class="bg-gray-200 dark:bg-gray-800 p-4 rounded-xl shadow-md">
    
    <label class="block text-lg font-semibold mb-3 text-gray-800 dark:text-white">
      Select Patient
    </label>

    <div class="relative">
      <select id="patientSelect" class="w-full p-3 pr-10 rounded-lg text-black dark:text-white bg-white dark:bg-gray-700 border border-gray-400 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition">
        <option value="">-- Select Patient --</option>
      </select>
    </div>

  </div>
</div>

<div class="container mx-auto p-6">
  <div id="map" class="rounded-lg"></div>
</div>

<script>
let currentGeofenceId = null;

const map = L.map('map').setView([51.5, -0.1], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

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
    edit: { featureGroup: drawnItems }
});
map.addControl(drawControl);

// ---------------- LOAD PATIENTS ----------------

fetch("api/get_patients.php")
.then(res => res.json())
.then(patients => {
    const select = document.getElementById("patientSelect");

    select.innerHTML = '<option value="">-- Select Patient --</option>';

    if (!patients || patients.length === 0) {
        select.innerHTML += '<option disabled>No patients found</option>';
        return;
    }

    patients.forEach(p => {
        const option = document.createElement("option");
        option.value = p.patient_id;
        option.textContent = p.name || p.patient_id;
        select.appendChild(option);
    });
})
.catch(err => {
    console.error("Patient load error:", err);
});

// ---------------- LOAD GEOFENCES ----------------

document.getElementById("patientSelect").addEventListener("change", function () {
    const patientId = this.value;

    if (!patientId) return;

    fetch(`/website/src/api/get_geofences.php?patient_id=${patientId}`)
    .then(res => res.json())
    .then(data => {

        drawnItems.clearLayers();

        data.forEach(g => {
            const payload = JSON.parse(g.encrypted_payload);

            const circle = L.circle([payload.lat, payload.lng], {
                radius: payload.radius,
                color: "blue"
            });

            // attach DB id
            circle.options.geofenceId = g.geofence_id;

            // click to select
            circle.on("click", () => {
                currentGeofenceId = g.geofence_id;
                console.log("Selected:", currentGeofenceId);
            });

            drawnItems.addLayer(circle);
        });
    });
});

// ---------------- SAVE ----------------

function saveGeofence(layer) {

    if (layer.isSaving) return; // prevent duplicate calls
    layer.isSaving = true;

    const selectedPatientId = document.getElementById("patientSelect").value;

    if (!selectedPatientId) {
        alert("Select a patient first");
        layer.isSaving = false;
        return;
    }

    const center = layer.getLatLng();
    const radius = layer.getRadius();

    fetch("api/save_geofence.php", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            geofence_id: layer.options.geofenceId || null,
            patient_id: selectedPatientId,
            lat: center.lat,
            lng: center.lng,
            radius: radius
        })
    })
    .then(res => res.json())
    .then(data => {

        if (data.geofence_id) {
            layer.options.geofenceId = data.geofence_id;
        }

    })
    .finally(() => {
        layer.isSaving = false;
    });
}

// create
map.on(L.Draw.Event.CREATED, function (e) {
    const layer = e.layer;
    drawnItems.addLayer(layer);
    layer.options.geofenceId = null;
    layer.isSaving = false;
    saveGeofence(layer);
});

// edit
map.on(L.Draw.Event.EDITED, function (e) {
    console.log("EDIT EVENT TRIGGERED");
    e.layers.eachLayer(layer => {
        if (!layer.options.geofenceId) {
            console.warn("Missing ID → skipping update");
            return;
        }
        saveGeofence(layer);
    });
});

// delete
map.on(L.Draw.Event.DELETED, function (e) {
    e.layers.eachLayer(layer => {

        console.log("Deleting layer:", layer);

        if (!layer.options.geofenceId) {
            console.warn("Delete skipped (no ID)");
            return;
        }

        fetch("api/delete_geofence.php", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                geofence_id: layer.options.geofenceId
            })
        })
        .then(res => res.json())
        .then(data => {
            console.log("Deleted:", layer.options.geofenceId);
        });
    });
});
</script>

</body>
</html>