-- ENTITY FOR THE DEVICE --
CREATE TABLE geofence_v1.device (
    device_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    patient_id UNIQUEIDENTIFIER NOT NULL,
    device_identifier VARCHAR (100) UNIQUE NOT NULL,
    public_key VARBINARY,
    is_active BIT DEFAULT 1,
    provisioned_at DATETIME DEFAULT GETDATE()

    CONSTRAINT fk_patient_device
    FOREIGN KEY (patient_id) REFERENCES geofence_v1.patient(patient_id) ON DELETE CASCADE
);