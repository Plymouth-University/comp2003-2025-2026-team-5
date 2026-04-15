let selectedPatientId = null;

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

// update when user selects
document.getElementById("patientSelect").addEventListener("change", (e) => {
    selectedPatientId = e.target.value;
});