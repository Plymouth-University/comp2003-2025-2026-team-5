CREATE TABLE geofence_v1.carer(
    carer_id INT IDENTITY(1,1) PRIMARY KEY,
    account_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    CONSTRAINT fk_account 
    FOREIGN KEY(account_id)
    REFERENCES geofence_v1.account(account_id)
);