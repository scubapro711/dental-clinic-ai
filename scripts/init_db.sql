-- Dental Clinic Database Initialization Script
-- מסד נתונים למערכת ניהול מרפאת שיניים

USE dental_clinic;

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    date_of_birth DATE,
    address TEXT,
    emergency_contact VARCHAR(20),
    medical_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_phone (phone),
    INDEX idx_email (email)
);

-- Create providers table (dentists and staff)
CREATE TABLE IF NOT EXISTS providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    license_number VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create treatment types table
CREATE TABLE IF NOT EXISTS treatment_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    duration_minutes INT DEFAULT 30,
    price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create appointments table
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    provider_id INT NOT NULL,
    treatment_type_id INT,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration_minutes INT DEFAULT 30,
    status ENUM('scheduled', 'confirmed', 'completed', 'cancelled', 'no_show') DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE,
    FOREIGN KEY (treatment_type_id) REFERENCES treatment_types(id) ON DELETE SET NULL,
    INDEX idx_appointment_date (appointment_date),
    INDEX idx_patient_id (patient_id),
    INDEX idx_provider_id (provider_id),
    INDEX idx_status (status)
);

-- Create messages table for communication history
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    sender_type ENUM('patient', 'system', 'staff') NOT NULL,
    channel ENUM('whatsapp', 'telegram', 'sms', 'email', 'api') NOT NULL,
    message_text TEXT NOT NULL,
    response_text TEXT,
    status ENUM('sent', 'delivered', 'read', 'failed') DEFAULT 'sent',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL,
    INDEX idx_patient_id (patient_id),
    INDEX idx_channel (channel),
    INDEX idx_created_at (created_at)
);

-- Insert sample data

-- Sample providers
INSERT INTO providers (first_name, last_name, specialization, phone, email, license_number) VALUES
('Dr. Sarah', 'Cohen', 'General Dentistry', '+972-50-1234567', 'sarah.cohen@clinic.com', 'DEN001'),
('Dr. Michael', 'Levy', 'Orthodontics', '+972-50-2345678', 'michael.levy@clinic.com', 'DEN002'),
('Dr. Rachel', 'Ben-David', 'Oral Surgery', '+972-50-3456789', 'rachel.bendavid@clinic.com', 'DEN003');

-- Sample treatment types
INSERT INTO treatment_types (name, description, duration_minutes, price) VALUES
('Cleaning', 'Regular dental cleaning and checkup', 45, 250.00),
('Filling', 'Dental filling for cavities', 60, 400.00),
('Root Canal', 'Root canal treatment', 90, 1200.00),
('Crown', 'Dental crown placement', 120, 2000.00),
('Extraction', 'Tooth extraction', 30, 300.00),
('Orthodontic Consultation', 'Initial orthodontic evaluation', 60, 200.00);

-- Sample patients
INSERT INTO patients (first_name, last_name, phone, email, date_of_birth, address) VALUES
('John', 'Smith', '+972-50-1111111', 'john.smith@email.com', '1985-03-15', 'Tel Aviv, Israel'),
('Mary', 'Johnson', '+972-50-2222222', 'mary.johnson@email.com', '1990-07-22', 'Jerusalem, Israel'),
('David', 'Brown', '+972-50-3333333', 'david.brown@email.com', '1978-11-08', 'Haifa, Israel'),
('Lisa', 'Wilson', '+972-50-4444444', 'lisa.wilson@email.com', '1995-01-30', 'Netanya, Israel'),
('Robert', 'Davis', '+972-50-5555555', 'robert.davis@email.com', '1982-09-12', 'Eilat, Israel');

-- Sample appointments
INSERT INTO appointments (patient_id, provider_id, treatment_type_id, appointment_date, appointment_time, status) VALUES
(1, 1, 1, '2025-09-28', '09:00:00', 'scheduled'),
(2, 2, 6, '2025-09-28', '10:30:00', 'confirmed'),
(3, 1, 2, '2025-09-29', '14:00:00', 'scheduled'),
(4, 3, 5, '2025-09-30', '11:00:00', 'scheduled'),
(5, 1, 1, '2025-10-01', '15:30:00', 'scheduled');

-- Sample messages
INSERT INTO messages (patient_id, sender_type, channel, message_text, response_text, status) VALUES
(1, 'patient', 'whatsapp', 'I need to schedule an appointment', 'Hello! I can help you schedule an appointment. What type of treatment do you need?', 'delivered'),
(2, 'system', 'sms', 'Reminder: You have an appointment tomorrow at 10:30 AM', NULL, 'sent'),
(3, 'patient', 'telegram', 'Can I reschedule my appointment?', 'Of course! When would you prefer to reschedule?', 'read');

-- Create indexes for better performance
CREATE INDEX idx_appointments_datetime ON appointments(appointment_date, appointment_time);
CREATE INDEX idx_messages_datetime ON messages(created_at);

-- Grant permissions
GRANT ALL PRIVILEGES ON dental_clinic.* TO 'dental_user'@'%';
FLUSH PRIVILEGES;
