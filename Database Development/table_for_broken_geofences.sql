CREATE TABLE geofence_v1.broken_geofences (
    broken_geofence_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    patient_id UNIQUEIDENTIFIER NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),

    CONSTRAINT broken_geofence_patient
    FOREIGN KEY (patient_id) REFERENCES geofence_v1.patient(patient_id) ON DELETE CASCADE
)