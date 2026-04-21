CREATE TABLE geofence_v1.carer(
    carer_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    account_id UNIQUEIDENTIFIER NOT NULL,
    name VARCHAR(100) NULL,
    
    CONSTRAINT fk_account_carer 
    FOREIGN KEY(account_id)
    REFERENCES geofence_v1.account(account_id) ON DELETE CASCADE
);