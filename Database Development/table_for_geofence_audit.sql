CREATE TABLE geofence_v1.geofence_audit (
    audit_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NewID(),
    geofence_id UNIQUEIDENTIFIER,
    action VARCHAR(20),
    performed_by UNIQUEIDENTIFIER,
    performed_at TIMESTAMP NOT NULL,
    reason TEXT

    CONSTRAINT fk_geofence_geoaudit 
    FOREIGN KEY (geofence_id) REFERENCES geofence_v1.geofence(geofence_id) ON DELETE NO ACTION,
    CONSTRAINT fk_account_audit
    FOREIGN KEY (performed_by) REFERENCES geofence_v1.account(account_id) ON DELETE CASCADE,
);
