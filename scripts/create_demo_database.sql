-- Demo Database Schema for Dental Clinic AI
-- Converted from DentneD SQL Server schema to MySQL
-- Date: 2025-09-27

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS dental_clinic_demo;
USE dental_clinic_demo;

-- Drop tables if they exist (for clean recreation)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS treatments;
DROP TABLE IF EXISTS treatmentsprices;
DROP TABLE IF EXISTS treatmentspriceslists;
DROP TABLE IF EXISTS treatmentstypes;
DROP TABLE IF EXISTS patientstreatments;
DROP TABLE IF EXISTS patientsaddresses;
DROP TABLE IF EXISTS patientscontacts;
DROP TABLE IF EXISTS patientsattributes;
DROP TABLE IF EXISTS patientsnotes;
DROP TABLE IF EXISTS patientsattachments;
DROP TABLE IF EXISTS patientsmedicalrecords;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS invoiceslines;
DROP TABLE IF EXISTS estimates;
DROP TABLE IF EXISTS estimateslines;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS paymentstypes;
DROP TABLE IF EXISTS taxes;
DROP TABLE IF EXISTS addressestypes;
DROP TABLE IF EXISTS contactstypes;
DROP TABLE IF EXISTS medicalrecordstypes;
DROP TABLE IF EXISTS patientsattachmentstypes;
DROP TABLE IF EXISTS patientsattributestypes;
SET FOREIGN_KEY_CHECKS = 1;

-- Core Tables

-- Doctors table
CREATE TABLE doctors (
    doctors_id INT AUTO_INCREMENT PRIMARY KEY,
    doctors_name VARCHAR(128) NOT NULL,
    doctors_surname VARCHAR(128) NOT NULL,
    doctors_doctext VARCHAR(512) NOT NULL,
    doctors_username VARCHAR(8) NOT NULL,
    doctors_password VARCHAR(6) NOT NULL,
    doctors_token VARCHAR(64) NULL,
    doctors_lastlogin DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Rooms table
CREATE TABLE rooms (
    rooms_id INT AUTO_INCREMENT PRIMARY KEY,
    rooms_name VARCHAR(64) NOT NULL,
    rooms_description VARCHAR(256) NULL,
    rooms_isactive BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Treatment types
CREATE TABLE treatmentstypes (
    treatmentstypes_id INT AUTO_INCREMENT PRIMARY KEY,
    treatmentstypes_name VARCHAR(64) NOT NULL,
    treatmentstypes_description VARCHAR(256) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Treatment price lists
CREATE TABLE treatmentspriceslists (
    treatmentspriceslists_id INT AUTO_INCREMENT PRIMARY KEY,
    treatmentspriceslists_name VARCHAR(64) NOT NULL,
    treatmentspriceslists_description VARCHAR(256) NULL,
    treatmentspriceslists_isdefault BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Treatments
CREATE TABLE treatments (
    treatments_id INT AUTO_INCREMENT PRIMARY KEY,
    treatmentstypes_id INT,
    treatments_code CHAR(3) NOT NULL,
    treatments_name VARCHAR(128) NOT NULL,
    treatments_description VARCHAR(512) NULL,
    treatments_isactive BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (treatmentstypes_id) REFERENCES treatmentstypes(treatmentstypes_id)
);

-- Treatment prices
CREATE TABLE treatmentsprices (
    treatmentsprices_id INT AUTO_INCREMENT PRIMARY KEY,
    treatments_id INT NOT NULL,
    treatmentspriceslists_id INT NOT NULL,
    treatmentsprices_price DECIMAL(10, 2) NOT NULL,
    treatmentsprices_isactive BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (treatments_id) REFERENCES treatments(treatments_id),
    FOREIGN KEY (treatmentspriceslists_id) REFERENCES treatmentspriceslists(treatmentspriceslists_id)
);

-- Patients table
CREATE TABLE patients (
    patients_id INT AUTO_INCREMENT PRIMARY KEY,
    treatmentspriceslists_id INT NULL,
    patients_name VARCHAR(128) NOT NULL,
    patients_surname VARCHAR(128) NOT NULL,
    patients_sex CHAR(1) NOT NULL,
    patients_birthdate DATE NOT NULL,
    patients_birthcity VARCHAR(64) NOT NULL,
    patients_doctext VARCHAR(512) NOT NULL,
    patients_notes TEXT NULL,
    patients_isarchived BOOLEAN DEFAULT FALSE,
    patients_username VARCHAR(8) NOT NULL,
    patients_password VARCHAR(6) NOT NULL,
    patients_token VARCHAR(64) NULL,
    patients_lastlogin DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (treatmentspriceslists_id) REFERENCES treatmentspriceslists(treatmentspriceslists_id)
);

-- Appointments table
CREATE TABLE appointments (
    appointments_id INT AUTO_INCREMENT PRIMARY KEY,
    doctors_id INT NOT NULL,
    patients_id INT NOT NULL,
    rooms_id INT NOT NULL,
    appointments_from DATETIME NOT NULL,
    appointments_to DATETIME NOT NULL,
    appointments_title VARCHAR(128) NOT NULL,
    appointments_notes TEXT NULL,
    appointments_color CHAR(7) NULL,
    appointments_status ENUM('scheduled', 'confirmed', 'completed', 'cancelled', 'no_show') DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (doctors_id) REFERENCES doctors(doctors_id),
    FOREIGN KEY (patients_id) REFERENCES patients(patients_id),
    FOREIGN KEY (rooms_id) REFERENCES rooms(rooms_id)
);

-- Patient treatments (completed treatments)
CREATE TABLE patientstreatments (
    patientstreatments_id INT AUTO_INCREMENT PRIMARY KEY,
    patients_id INT NOT NULL,
    doctors_id INT NOT NULL,
    treatments_id INT NOT NULL,
    appointments_id INT NULL,
    patientstreatments_date DATE NOT NULL,
    patientstreatments_notes TEXT NULL,
    patientstreatments_price DECIMAL(10, 2) NOT NULL,
    patientstreatments_status ENUM('planned', 'in_progress', 'completed', 'cancelled') DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patients_id) REFERENCES patients(patients_id),
    FOREIGN KEY (doctors_id) REFERENCES doctors(doctors_id),
    FOREIGN KEY (treatments_id) REFERENCES treatments(treatments_id),
    FOREIGN KEY (appointments_id) REFERENCES appointments(appointments_id)
);

-- Address types
CREATE TABLE addressestypes (
    addressestypes_id INT AUTO_INCREMENT PRIMARY KEY,
    addressestypes_name VARCHAR(16) NOT NULL
);

-- Patient addresses
CREATE TABLE patientsaddresses (
    patientsaddresses_id INT AUTO_INCREMENT PRIMARY KEY,
    patients_id INT NOT NULL,
    addressestypes_id INT NOT NULL,
    patientsaddresses_address VARCHAR(256) NOT NULL,
    patientsaddresses_city VARCHAR(64) NOT NULL,
    patientsaddresses_zipcode VARCHAR(16) NOT NULL,
    patientsaddresses_country VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patients_id) REFERENCES patients(patients_id),
    FOREIGN KEY (addressestypes_id) REFERENCES addressestypes(addressestypes_id)
);

-- Contact types
CREATE TABLE contactstypes (
    contactstypes_id INT AUTO_INCREMENT PRIMARY KEY,
    contactstypes_name VARCHAR(16) NOT NULL
);

-- Patient contacts
CREATE TABLE patientscontacts (
    patientscontacts_id INT AUTO_INCREMENT PRIMARY KEY,
    patients_id INT NOT NULL,
    contactstypes_id INT NOT NULL,
    patientscontacts_contact VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patients_id) REFERENCES patients(patients_id),
    FOREIGN KEY (contactstypes_id) REFERENCES contactstypes(contactstypes_id)
);

-- Payment types
CREATE TABLE paymentstypes (
    paymentstypes_id INT AUTO_INCREMENT PRIMARY KEY,
    paymentstypes_name VARCHAR(32) NOT NULL,
    paymentstypes_description VARCHAR(128) NULL
);

-- Payments
CREATE TABLE payments (
    payments_id INT AUTO_INCREMENT PRIMARY KEY,
    patients_id INT NOT NULL,
    paymentstypes_id INT NOT NULL,
    payments_amount DECIMAL(10, 2) NOT NULL,
    payments_date DATE NOT NULL,
    payments_notes TEXT NULL,
    payments_reference VARCHAR(64) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patients_id) REFERENCES patients(patients_id),
    FOREIGN KEY (paymentstypes_id) REFERENCES paymentstypes(paymentstypes_id)
);

-- Taxes
CREATE TABLE taxes (
    taxes_id INT AUTO_INCREMENT PRIMARY KEY,
    taxes_name VARCHAR(32) NOT NULL,
    taxes_rate DECIMAL(5, 2) NOT NULL,
    taxes_isdefault BOOLEAN DEFAULT FALSE,
    taxes_isactive BOOLEAN DEFAULT TRUE
);

-- Invoices
CREATE TABLE invoices (
    invoices_id INT AUTO_INCREMENT PRIMARY KEY,
    doctors_id INT NULL,
    patients_id INT NULL,
    invoices_number VARCHAR(32) NOT NULL UNIQUE,
    invoices_date DATE NOT NULL,
    invoices_doctor VARCHAR(512) NOT NULL,
    invoices_patient VARCHAR(512) NOT NULL,
    invoices_payment VARCHAR(512) NOT NULL,
    invoices_footer VARCHAR(512) NULL,
    invoices_totalnet DECIMAL(10, 2) NOT NULL,
    invoices_totalgross DECIMAL(10, 2) NOT NULL,
    invoices_totaldue DECIMAL(10, 2) NOT NULL,
    invoices_deductiontaxrate DECIMAL(10, 2) NOT NULL,
    invoices_status ENUM('draft', 'sent', 'paid', 'overdue', 'cancelled') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (doctors_id) REFERENCES doctors(doctors_id),
    FOREIGN KEY (patients_id) REFERENCES patients(patients_id)
);

-- Invoice lines
CREATE TABLE invoiceslines (
    invoiceslines_id INT AUTO_INCREMENT PRIMARY KEY,
    invoices_id INT NOT NULL,
    patientstreatments_id INT NULL,
    invoiceslines_code CHAR(3) NOT NULL,
    invoiceslines_description VARCHAR(512) NOT NULL,
    invoiceslines_quantity INT NOT NULL,
    invoiceslines_unitprice DECIMAL(10, 2) NOT NULL,
    invoiceslines_taxrate DECIMAL(10, 2) NOT NULL,
    invoiceslines_istaxesdeductionsable BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoices_id) REFERENCES invoices(invoices_id),
    FOREIGN KEY (patientstreatments_id) REFERENCES patientstreatments(patientstreatments_id)
);

-- Estimates
CREATE TABLE estimates (
    estimates_id INT AUTO_INCREMENT PRIMARY KEY,
    doctors_id INT NULL,
    patients_id INT NULL,
    invoices_id INT NULL,
    estimates_number VARCHAR(32) NOT NULL UNIQUE,
    estimates_date DATE NOT NULL,
    estimates_doctor VARCHAR(512) NOT NULL,
    estimates_patient VARCHAR(512) NOT NULL,
    estimates_payment VARCHAR(512) NOT NULL,
    estimates_footer VARCHAR(512) NULL,
    estimates_totalnet DECIMAL(10, 2) NOT NULL,
    estimates_totalgross DECIMAL(10, 2) NOT NULL,
    estimates_totaldue DECIMAL(10, 2) NOT NULL,
    estimates_deductiontaxrate DECIMAL(10, 2) NOT NULL,
    estimates_status ENUM('draft', 'sent', 'accepted', 'rejected', 'expired') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (doctors_id) REFERENCES doctors(doctors_id),
    FOREIGN KEY (patients_id) REFERENCES patients(patients_id),
    FOREIGN KEY (invoices_id) REFERENCES invoices(invoices_id)
);

-- Estimate lines
CREATE TABLE estimateslines (
    estimateslines_id INT AUTO_INCREMENT PRIMARY KEY,
    estimates_id INT NOT NULL,
    patientstreatments_id INT NULL,
    estimateslines_code CHAR(3) NOT NULL,
    estimateslines_description VARCHAR(512) NOT NULL,
    estimateslines_quantity INT NOT NULL,
    estimateslines_unitprice DECIMAL(10, 2) NOT NULL,
    estimateslines_taxrate DECIMAL(10, 2) NOT NULL,
    estimateslines_istaxesdeductionsable BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estimates_id) REFERENCES estimates(estimates_id),
    FOREIGN KEY (patientstreatments_id) REFERENCES patientstreatments(patientstreatments_id)
);

-- Create indexes for better performance
CREATE INDEX idx_appointments_datetime ON appointments(appointments_from, appointments_to);
CREATE INDEX idx_appointments_doctor ON appointments(doctors_id);
CREATE INDEX idx_appointments_patient ON appointments(patients_id);
CREATE INDEX idx_patients_name ON patients(patients_surname, patients_name);
CREATE INDEX idx_patients_birthdate ON patients(patients_birthdate);
CREATE INDEX idx_patientstreatments_date ON patientstreatments(patientstreatments_date);
CREATE INDEX idx_invoices_date ON invoices(invoices_date);
CREATE INDEX idx_invoices_number ON invoices(invoices_number);
CREATE INDEX idx_payments_date ON payments(payments_date);

-- Create views for common queries
CREATE VIEW patient_summary AS
SELECT 
    p.patients_id,
    p.patients_name,
    p.patients_surname,
    p.patients_sex,
    p.patients_birthdate,
    YEAR(CURDATE()) - YEAR(p.patients_birthdate) AS age,
    COUNT(DISTINCT a.appointments_id) AS total_appointments,
    COUNT(DISTINCT pt.patientstreatments_id) AS total_treatments,
    COALESCE(SUM(pay.payments_amount), 0) AS total_payments
FROM patients p
LEFT JOIN appointments a ON p.patients_id = a.patients_id
LEFT JOIN patientstreatments pt ON p.patients_id = pt.patients_id
LEFT JOIN payments pay ON p.patients_id = pay.patients_id
WHERE p.patients_isarchived = FALSE
GROUP BY p.patients_id;

CREATE VIEW doctor_schedule AS
SELECT 
    d.doctors_id,
    d.doctors_name,
    d.doctors_surname,
    a.appointments_id,
    a.appointments_from,
    a.appointments_to,
    a.appointments_title,
    p.patients_name,
    p.patients_surname,
    r.rooms_name,
    a.appointments_status
FROM doctors d
JOIN appointments a ON d.doctors_id = a.doctors_id
JOIN patients p ON a.patients_id = p.patients_id
JOIN rooms r ON a.rooms_id = r.rooms_id
WHERE a.appointments_from >= CURDATE()
ORDER BY a.appointments_from;

-- Success message
SELECT 'Demo database schema created successfully!' AS status;
