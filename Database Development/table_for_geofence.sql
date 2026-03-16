CREATE TABLE geofence_v1.geofence (
    geofence_id UNIQUEIDENTIFIER PRIMARY KEY,
    patient_id UNIQUEIDENTIFIER NOT NULL,
    name VARCHAR(100),
    shape_type VARCHAR(20),
    encrypted_payload VARBINARY NOT NULL,
    is_active BIT DEFAULT 1,
    created_at TIMESTAMP NOT NULL,
    created_by UNIQUEIDENTIFIER NOT NULL,

    CONSTRAINT fk_geofence_patient 
    FOREIGN KEY (patient_id) REFERENCES geofence_v1.patient(patient_id) ON DELETE NO ACTION,
    CONSTRAINT fk_geofence_creator
    FOREIGN KEY (created_by) REFERENCES geofence_v1.account(account_id) ON DELETE CASCADE
);