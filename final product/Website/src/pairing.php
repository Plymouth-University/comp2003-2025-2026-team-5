<?php
require_once "auth/session_check.php";
require_once "auth/role_check.php";
requireRole(["carer", "patient"]);
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
    
    <main class="max-w-xl mx-auto mt-10 p-6 bg-white dark:bg-gray-800 rounded-xl shadow">

        <h1 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
            Account Pairing
        </h1>

        <!-- CARER VIEW -->
        <div id="carerSection" class="hidden">
            <h2 class="text-lg mb-3 text-black dark:text-white">Link to a Patient</h2>

            <select id="patientSelect" class="w-full p-3 mb-4 rounded-lg bg-white text-black border border-gray-300 dark:bg-gray-700 dark:text-white dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition">
                <option value="">Loading patients...</option>
            </select>

            <button id="pairBtn"
                class="w-full bg-blue-600 hover:bg-blue-500 p-3 rounded">
                Pair with Patient
            </button>
        </div>

        <!-- PATIENT VIEW -->
        <div id="patientSection" class="hidden">
            <h2 class="text-lg mb-3 text-black dark:text-white">Your Carers</h2>

            <select id="carerSelect" class="w-full p-3 mb-4 rounded-lg bg-white text-black border border-gray-300 dark:bg-gray-700 dark:text-white dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition">
                <option value="">Loading carers...</option>
            </select>

            <button id="removeBtn"
                class="w-full bg-red-600 hover:bg-red-500 p-3 rounded">
                Remove Carer
            </button>
        </div>

    </main>
<script>
    let role = null;

    // get role from backend
    fetch("api/get_role.php")
    .then(res => res.json())
    .then(data => {
        role = data.role;

        if (role === "carer") {
            document.getElementById("carerSection").classList.remove("hidden");
            loadPatients();
        } else {
            document.getElementById("patientSection").classList.remove("hidden");
            loadCarers();
        }
    });

    // ---------------- CARER ----------------

    function loadPatients() {
        fetch("api/get_unlinked_patients.php")
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById("patientSelect");
            select.innerHTML = '<option value="">-- Select Patient --</option>';

            data.forEach(p => {
                select.innerHTML += `
                    <option value="${p.patient_id}">
                        ${p.name || p.patient_id}
                    </option>
                `;
            });
        });
    }

    document.getElementById("pairBtn")?.addEventListener("click", () => {
        const patientId = document.getElementById("patientSelect").value;

        fetch("api/pair_patient.php", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ patient_id: patientId })
        })
        .then(res => res.json())
        .then(() => {
            alert("Paired successfully");
            loadPatients(); // refresh dropdown
        });
    });

    // ---------------- PATIENT ----------------

    function loadCarers() {
        fetch("api/get_my_carers.php")
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById("carerSelect");
            select.innerHTML = '<option value="">-- Select Carer --</option>';

            data.forEach(c => {
                select.innerHTML += `
                    <option value="${c.carer_id}">
                        ${c.name || c.carer_id}
                    </option>
                `;
            });
        });
    }

    document.getElementById("removeBtn")?.addEventListener("click", () => {
        const carerId = document.getElementById("carerSelect").value;

        fetch("api/remove_carer.php", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ carer_id: carerId })
        })
        .then(res => res.json())
        .then(() => {
            alert("Carer removed");
            loadCarers();
        });
    });
</script>
</body>
</html>