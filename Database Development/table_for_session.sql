CREATE TABLE geofence_v1.session (
    session_id UNIQUEIDENTIFIER PRIMARY KEY,
    account_id UNIQUEIDENTIFIER,
    issued_at DATETIME NOT NULL DEFAULT GETDATE(),
    expires_at DATETIME NOT NULL DEFAULT GETDATE(),
    revoked BIT DEFAULT 0,

    CONSTRAINT fk_account_session 
    FOREIGN KEY (account_id) REFERENCES geofence_v1.account(account_id) ON DELETE CASCADE
);