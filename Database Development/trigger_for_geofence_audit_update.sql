-- Trigger to automatically insert into the geofence audit table whenever there is an update to the geofence table 
CREATE OR ALTER TRIGGER geofence_v1.geofence_audit_trigger_update
ON geofence_v1.geofence
AFTER UPDATE
AS 
BEGIN 
    -- Update the the geofence automatically 
    IF EXISTS (SELECT TOP 1 * FROM inserted) AND EXISTS (SELECT TOP 1 * FROM deleted)
    INSERT INTO geofence_v1.geofence_audit (geofence_id, action, performed_by)
    SELECT geofence_id, 'UPDATE', created_by FROM inserted

END;