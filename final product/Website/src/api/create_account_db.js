// import the database connection pool
const pool = require('./db.js')
const haversine = require('./server.js');


// function to create account in MYSQL database
async function createAccount(account_id, email, role) {

    // define the queries
    const insert_account_query = 'INSERT INTO `account` (account_id, email, role) VALUES (?, ?, ?)';
    const query_values = [account_id, email, role];
    const check_account_query = 'SELECT * FROM `account` WHERE `account_id` = ?'; 

    try{
        // check if account already exists
        const [account_rows] = await pool.query(check_account_query, [account_id]);
        if (account_rows.length) {
            console.error("Account already exists");
            return;
        }

        // insert values into the account entity in the database
        await pool.query(insert_account_query, query_values);
        console.log("Account created successfully");
    } catch (err) {
        console.error("Database error:", err);
    }

}

// function to create patient in MYSQL database
async function createPatient (account_id, patient_id, name) {
    // define the queries
    const insert_patient_query = 'INSERT INTO `patient` (account_id, patient_id, name) VALUES (?, ?, ?)';
    const query_values = [account_id, patient_id, name];
    const check_patient_query = 'SELECT * FROM `patient` WHERE `patient_id` = ?';
    try {
        // check if patient already exists
        const [patient_rows] = await pool.query(check_patient_query, [patient_id]);
        if (patient_rows.length) {
            console.error("Patient already exists");
            return;
        }
        // insert values into the patient entity in the database
        await pool.query(insert_patient_query, query_values);
        console.log("Patient created successfully");
    } catch (err) {
        console.error("Database error:", err);
    }
}

// function to assign device to patient
async function assignDeviceToPatient(patient_id, device_id) {
    // define the queries
    const assign_device_query = 'INSERT INTO `device` (patient_id, device_id) VALUES (?, ?)';
    const query_values = [patient_id, device_id];
    const check_device_query = 'SELECT * FROM `device` WHERE `device_id` = ?';
    try {
        // check if device already exists
        const [device_rows] = await pool.query(check_device_query, [device_id]);
        if (device_rows.length) {
            console.error("Device already exists");
            return;
        }
        // insert values into the device entity in the database
        await pool.query(assign_device_query, query_values);
        console.log("Device assigned to patient successfully");
    } catch (err) {
        console.error("Database error:", err);
    }
}

// function to create geofence within database
async function createGeofence(patient_id, latitude, longitude, radius, shape_type) {

    // define the queries
    const insert_geofence_query = 'INSERT INTO `geofence` (patient_id, latitude, longitude, radius, shape_type) VALUES (?, ?, ?, ?, ?)';
    const query_values = [patient_id, latitude, longitude, radius, shape_type];
    const check_geofence_query = 'SELECT * FROM `geofence` WHERE `patient_id` = ?';
    try {
        // check if geofence already exists for patient
        const [geofence_rows] = await pool.query(check_geofence_query, [patient_id]);
        if (geofence_rows.length) {
            console.error("Geofence already exists for patient");
            return;
        }

        // insert values into the geofence entity in the database
        await pool.query(insert_geofence_query, query_values);
        console.log("Geofence created successfully");
    } catch (err) {
        console.error("Database error:", err);
    }
}

// dummy data for geofence
latitude = 52.480759
longitude = -1.902691
radius = haversine(latitude, longitude, 52.481000, -1.902000) // calculate radius using haversine distance between two points
shape_type = 'circle'

createAccount(1, 'user@example.com', 'patient');
createPatient(1, 1, 'John Doe');
assignDeviceToPatient(1, 1);
createGeofence(1, latitude, longitude, radius, shape_type);