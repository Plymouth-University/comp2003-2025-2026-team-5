CREATE TABLE geofence_v1.patient(
    patient_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    account_id UNIQUEIDENTIFIER NOT NULL,
    name VARCHAR(100) NOT NULL,

    CONSTRAINT fk_patient_account 
    FOREIGN KEY (account_id) 
    REFERENCES geofence_v1.account(account_id) ON DELETE CASCADE
);