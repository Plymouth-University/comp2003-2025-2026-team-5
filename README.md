[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/xGnTrW1S)
[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=20873210)
# COMP2003-2023
Use this folder structure for your git repository. You may add additional folders as you see fit, but these basic folders provide the fundamental organization for evidences that need to be collected throughout the semester, so upload/commit them periodically.

# Running the website
To run the website, place the website folder into XAMPP HTDOCS on your computer and then turn on apache throught the xampp control panel

Turn on MySQL on the xampp control panel then go to https://localhost/phpmyadmin/index.php and run this script to create the necessary sql:

CREATE DATABASE geofence;
USE geofence;

---------------- ACCOUNT ----------------

CREATE TABLE account (
    account_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

---------------- PATIENT ----------------

CREATE TABLE patient (
    patient_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    name VARCHAR(100),

    FOREIGN KEY (account_id) REFERENCES account(account_id) ON DELETE CASCADE
);

---------------- CARER ----------------

CREATE TABLE carer (
    carer_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    name VARCHAR(100),

    FOREIGN KEY (account_id) REFERENCES account(account_id) ON DELETE CASCADE
);

---------------- CARER ↔ PATIENT ----------------

CREATE TABLE carer_patient (
    id INT AUTO_INCREMENT PRIMARY KEY,
    carer_id VARCHAR(50),
    patient_id VARCHAR(50),

    FOREIGN KEY (carer_id) REFERENCES carer(carer_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id) ON DELETE CASCADE
);

---------------- GEOFENCE ----------------

CREATE TABLE geofence (
    geofence_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    name VARCHAR(100),
    shape_type VARCHAR(20),
    encrypted_payload JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES account(account_id) ON DELETE CASCADE
);

---------------- GEOFENCE AUDIT ----------------

CREATE TABLE geofence_audit (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    geofence_id VARCHAR(50),
    action VARCHAR(20),
    performed_by VARCHAR(50),
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (geofence_id) REFERENCES geofence(geofence_id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES account(account_id) ON DELETE CASCADE
);

---------------- BROKEN GEOFENCES ----------------

CREATE TABLE broken_geofences (
    broken_geofence_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(50),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES patient(patient_id) ON DELETE CASCADE
);

# Database triggers
DELIMITER $$
CREATE TRIGGER geofence_insert
AFTER INSERT ON geofence
FOR EACH ROW
BEGIN
    INSERT INTO geofence_audit (geofence_id, action, performed_by)
    VALUES (NEW.geofence_id, 'create', NEW.created_by);
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER geofence_update
AFTER UPDATE ON geofence
FOR EACH ROW
BEGIN
    INSERT INTO geofence_audit (geofence_id, action, performed_by)
    VALUES (NEW.geofence_id, 'update', NEW.created_by);
END$$
DELIMITER ;


DELIMITER $$
CREATE TRIGGER geofence_delete
AFTER DELETE ON geofence
FOR EACH ROW
BEGIN
    INSERT INTO geofence_audit (geofence_id, action, performed_by)
    VALUES (OLD.geofence_id, 'delete', OLD.created_by);
END$$
DELIMITER ;

# frontend link (use this to get to the website once XAMPP is running)
https://localhost/website/src/geofence.php

# Redundant section, please ignore
This became out of scope after I spent hours and hours trying to make it work and decided that if I get this many bugs setting it up then it will not be feasable to ask others to do so to run this so I reverted the code back to the MySQL XAMPP Method
as we are now using MSSQL instead of MYSQL, additional steps are required to run the database
download Microsoft SQL server express, SQL server management studio and microsoft drivers for PHP for SQL Server
Edit the php.ini file in your xampp installation to include these lines : 
extension=sqlsrv
extension=pdo_sqlsrv

