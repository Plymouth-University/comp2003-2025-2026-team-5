CREATE TABLE geofence_v1.carer_patient ( 
    carer_id UNIQUEIDENTIFIER, 
    patient_id UNIQUEIDENTIFIER,  
    
    CONSTRAINT pk_carer_patient PRIMARY KEY (carer_id, patient_id),
    CONSTRAINT fk_carer 
    FOREIGN KEY (carer_id) REFERENCES geofence_v1.carer(carer_id) ON DELETE CASCADE,
    CONSTRAINT fk_patient
    FOREIGN KEY (patient_id) REFERENCES geofence_v1.patient(patient_id) ON DELETE NO ACTION
);