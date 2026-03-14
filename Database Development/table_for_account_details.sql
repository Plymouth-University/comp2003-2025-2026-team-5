-- Table for account details --
CREATE TABLE geofence_v1.account(
    account_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BIT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL
);