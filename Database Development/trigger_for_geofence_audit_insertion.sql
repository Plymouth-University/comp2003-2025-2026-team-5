-- Trigger to automatically insert into the geofence audit table whenever there is an insert 
CREATE OR ALTER TRIGGER geofence_v1.geofence_audit_trigger
ON geofence_v1.geofence
AFTER INSERT
AS 
BEGIN 
    -- Insert into the geofence automatically 
    IF EXISTS (SELECT TOP 1 * FROM inserted) AND NOT EXISTS (SELECT TOP 1 * FROM deleted)
    INSERT INTO geofence_v1.geofence_audit (geofence_id, action, performed_by)
    SELECT geofence_id, 'INSERT', created_by FROM inserted

END;