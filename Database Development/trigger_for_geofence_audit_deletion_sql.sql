-- Trigger to automatically insert into the geofence audit table whenever there is an insert 
CREATE OR ALTER TRIGGER geofence_v1.geofence_audit_trigger_delete
ON geofence_v1.geofence
AFTER DELETE
AS 
BEGIN 
    -- Insert into the geofence automatically 
    IF NOT EXISTS (SELECT TOP 1 * FROM inserted) AND  EXISTS (SELECT TOP 1 * FROM deleted)
    INSERT INTO geofence_v1.geofence_audit (geofence_id, action, performed_by)
    SELECT geofence_id, 'DELETE', created_by FROM deleted

END;