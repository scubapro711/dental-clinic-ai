-- Demo Database Initialization Script for Docker Container
-- This script will be executed when the MySQL container starts

-- Create the demo database
CREATE DATABASE IF NOT EXISTS dental_clinic_demo;
USE dental_clinic_demo;

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

-- Insert basic data for immediate functionality

-- Insert treatment price lists
INSERT INTO treatmentspriceslists (treatmentspriceslists_name, treatmentspriceslists_description, treatmentspriceslists_isdefault) VALUES
('Standard Prices', 'מחירון רגיל', TRUE),
('Insurance Prices', 'מחירי ביטוח', FALSE);

-- Insert treatment types
INSERT INTO treatmentstypes (treatmentstypes_name, treatmentstypes_description) VALUES
('Preventive', 'טיפולי מניעה'),
('Restorative', 'טיפולי שיקום'),
('Endodontic', 'טיפולי שורש');

-- Insert treatments
INSERT INTO treatments (treatmentstypes_id, treatments_code, treatments_name, treatments_description) VALUES
(1, '001', 'Dental Cleaning', 'ניקוי שיניים מקצועי'),
(1, '003', 'Dental Examination', 'בדיקת שיניים'),
(2, '102', 'Filling - Composite', 'סתימה קומפוזיט'),
(3, '201', 'Root Canal', 'טיפול שורש');

-- Insert rooms
INSERT INTO rooms (rooms_name, rooms_description) VALUES
('Room 1', 'חדר טיפולים ראשי'),
('Room 2', 'חדר טיפולים משני');

-- Insert doctors
INSERT INTO doctors (doctors_name, doctors_surname, doctors_doctext, doctors_username, doctors_password) VALUES
('Dr. David', 'Cohen', 'רופא שיניים בכיר, מומחה בטיפולי שורש ושיקום פה. 15 שנות ניסיון.', 'dcohen', 'pass01'),
('Dr. Sarah', 'Levy', 'רופאת שיניים מומחית ביישור שיניים וטיפולים אסתטיים. 12 שנות ניסיון.', 'slevy', 'pass02');

-- Insert sample patients
INSERT INTO patients (treatmentspriceslists_id, patients_name, patients_surname, patients_sex, patients_birthdate, patients_birthcity, patients_doctext, patients_notes, patients_username, patients_password) VALUES
(1, 'Yossi', 'Mizrahi', 'M', '1985-03-15', 'Tel Aviv', 'מטופל רגיל, ללא אלרגיות ידועות', 'מטופל שיתופי, מגיע לבדיקות באופן קבוע', 'ymizrahi', 'pat001'),
(1, 'Miriam', 'Shapiro', 'F', '1978-07-22', 'Jerusalem', 'אלרגיה לפניצילין', 'מטופלת חרדה, זקוקה להרגעה לפני טיפולים', 'mshapir', 'pat002');

-- Insert sample appointments for today and tomorrow
INSERT INTO appointments (doctors_id, patients_id, rooms_id, appointments_from, appointments_to, appointments_title, appointments_color, appointments_status) VALUES
(1, 1, 1, DATE_ADD(NOW(), INTERVAL 1 HOUR), DATE_ADD(NOW(), INTERVAL 1.5 HOUR), 'Dental Cleaning', '#4CAF50', 'scheduled'),
(2, 2, 2, DATE_ADD(NOW(), INTERVAL 1 DAY), DATE_ADD(NOW(), INTERVAL 25 HOUR), 'Dental Examination', '#2196F3', 'scheduled');

-- Create indexes for better performance
CREATE INDEX idx_appointments_datetime ON appointments(appointments_from, appointments_to);
CREATE INDEX idx_appointments_doctor ON appointments(doctors_id);
CREATE INDEX idx_appointments_patient ON appointments(patients_id);
CREATE INDEX idx_patients_name ON patients(patients_surname, patients_name);

-- Grant permissions to the dental_user
GRANT ALL PRIVILEGES ON dental_clinic_demo.* TO 'dental_user'@'%';
FLUSH PRIVILEGES;

SELECT 'Demo database initialized successfully!' AS status;
