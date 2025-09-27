-- Demo Data Population Script for Dental Clinic AI
-- Realistic Israeli dental clinic data
-- Date: 2025-09-27

USE dental_clinic_demo;

-- Insert address types
INSERT INTO addressestypes (addressestypes_name) VALUES
('Home'),
('Work'),
('Billing'),
('Emergency');

-- Insert contact types
INSERT INTO contactstypes (contactstypes_name) VALUES
('Mobile'),
('Home'),
('Work'),
('Email'),
('WhatsApp');

-- Insert payment types
INSERT INTO paymentstypes (paymentstypes_name, paymentstypes_description) VALUES
('Cash', 'מזומן'),
('Credit Card', 'כרטיס אשראי'),
('Bank Transfer', 'העברה בנקאית'),
('Check', 'צ\'ק'),
('Insurance', 'ביטוח'),
('Installments', 'תשלומים');

-- Insert tax rates
INSERT INTO taxes (taxes_name, taxes_rate, taxes_isdefault, taxes_isactive) VALUES
('VAT 17%', 17.00, TRUE, TRUE),
('VAT 0%', 0.00, FALSE, TRUE),
('Reduced VAT', 8.50, FALSE, TRUE);

-- Insert treatment types
INSERT INTO treatmentstypes (treatmentstypes_name, treatmentstypes_description) VALUES
('Preventive', 'טיפולי מניעה'),
('Restorative', 'טיפולי שיקום'),
('Endodontic', 'טיפולי שורש'),
('Periodontic', 'טיפולי חניכיים'),
('Orthodontic', 'יישור שיניים'),
('Oral Surgery', 'כירורגיה'),
('Prosthodontic', 'שיקום פה'),
('Cosmetic', 'טיפולים אסתטיים');

-- Insert treatment price lists
INSERT INTO treatmentspriceslists (treatmentspriceslists_name, treatmentspriceslists_description, treatmentspriceslists_isdefault) VALUES
('Standard Prices', 'מחירון רגיל', TRUE),
('Insurance Prices', 'מחירי ביטוח', FALSE),
('Private Prices', 'מחירים פרטיים', FALSE),
('Student Discount', 'הנחה לסטודנטים', FALSE);

-- Insert treatments
INSERT INTO treatments (treatmentstypes_id, treatments_code, treatments_name, treatments_description) VALUES
(1, '001', 'Dental Cleaning', 'ניקוי שיניים מקצועי'),
(1, '002', 'Fluoride Treatment', 'טיפול פלואור'),
(1, '003', 'Dental Examination', 'בדיקת שיניים'),
(1, '004', 'X-Ray', 'צילום רנטגן'),
(2, '101', 'Filling - Amalgam', 'סתימה אמלגם'),
(2, '102', 'Filling - Composite', 'סתימה קומפוזיט'),
(2, '103', 'Crown - Porcelain', 'כתר חרסינה'),
(2, '104', 'Crown - Metal', 'כתר מתכת'),
(3, '201', 'Root Canal', 'טיפול שורש'),
(3, '202', 'Pulp Capping', 'כיסוי עצב'),
(4, '301', 'Scaling', 'גירוד אבנית'),
(4, '302', 'Gum Surgery', 'ניתוח חניכיים'),
(5, '401', 'Braces - Metal', 'גשר מתכת'),
(5, '402', 'Braces - Ceramic', 'גשר קרמי'),
(6, '501', 'Tooth Extraction', 'עקירת שן'),
(6, '502', 'Wisdom Tooth Extraction', 'עקירת שן בינה'),
(7, '601', 'Denture - Partial', 'תותבת חלקית'),
(7, '602', 'Denture - Complete', 'תותבת מלאה'),
(8, '701', 'Teeth Whitening', 'הלבנת שיניים'),
(8, '702', 'Veneer', 'ציפוי');

-- Insert treatment prices
INSERT INTO treatmentsprices (treatments_id, treatmentspriceslists_id, treatmentsprices_price) VALUES
-- Standard prices
(1, 1, 250.00), (2, 1, 150.00), (3, 1, 200.00), (4, 1, 120.00),
(5, 1, 300.00), (6, 1, 450.00), (7, 1, 2500.00), (8, 1, 2000.00),
(9, 1, 1800.00), (10, 1, 400.00), (11, 1, 350.00), (12, 1, 3500.00),
(13, 1, 8000.00), (14, 1, 9500.00), (15, 1, 400.00), (16, 1, 800.00),
(17, 1, 4500.00), (18, 1, 8500.00), (19, 1, 1200.00), (20, 1, 2800.00),
-- Insurance prices (20% discount)
(1, 2, 200.00), (2, 2, 120.00), (3, 2, 160.00), (4, 2, 96.00),
(5, 2, 240.00), (6, 2, 360.00), (7, 2, 2000.00), (8, 2, 1600.00),
(9, 2, 1440.00), (10, 2, 320.00), (11, 2, 280.00), (12, 2, 2800.00),
(13, 2, 6400.00), (14, 2, 7600.00), (15, 2, 320.00), (16, 2, 640.00),
(17, 2, 3600.00), (18, 2, 6800.00), (19, 2, 960.00), (20, 2, 2240.00);

-- Insert rooms
INSERT INTO rooms (rooms_name, rooms_description) VALUES
('Room 1', 'חדר טיפולים ראשי'),
('Room 2', 'חדר טיפולים משני'),
('Room 3', 'חדר כירורגיה'),
('Room 4', 'חדר יישור שיניים'),
('X-Ray Room', 'חדר רנטגן'),
('Consultation', 'חדר ייעוץ');

-- Insert doctors
INSERT INTO doctors (doctors_name, doctors_surname, doctors_doctext, doctors_username, doctors_password) VALUES
('Dr. David', 'Cohen', 'רופא שיניים בכיר, מומחה בטיפולי שורש ושיקום פה. 15 שנות ניסיון.', 'dcohen', 'pass01'),
('Dr. Sarah', 'Levy', 'רופאת שיניים מומחית ביישור שיניים וטיפולים אסתטיים. 12 שנות ניסיון.', 'slevy', 'pass02'),
('Dr. Michael', 'Goldstein', 'רופא שיניים מומחה בכירורגיה וטיפולי חניכיים. 20 שנות ניסיון.', 'mgold', 'pass03'),
('Dr. Rachel', 'Rosen', 'רופאת שיניים מומחית בטיפולי ילדים ומניעה. 8 שנות ניסיון.', 'rrosen', 'pass04');

-- Insert patients with realistic Israeli names and data
INSERT INTO patients (treatmentspriceslists_id, patients_name, patients_surname, patients_sex, patients_birthdate, patients_birthcity, patients_doctext, patients_notes, patients_username, patients_password) VALUES
(1, 'Yossi', 'Mizrahi', 'M', '1985-03-15', 'Tel Aviv', 'מטופל רגיל, ללא אלרגיות ידועות', 'מטופל שיתופי, מגיע לבדיקות באופן קבוע', 'ymizrahi', 'pat001'),
(1, 'Miriam', 'Shapiro', 'F', '1978-07-22', 'Jerusalem', 'אלרגיה לפניצילין', 'מטופלת חרדה, זקוקה להרגעה לפני טיפולים', 'mshapir', 'pat002'),
(2, 'Avi', 'Ben-David', 'M', '1992-11-08', 'Haifa', 'מטופל צעיר, בריא', 'סטודנט, מעוניין בתשלומים', 'abendav', 'pat003'),
(1, 'Tamar', 'Katz', 'F', '1965-05-30', 'Beersheba', 'סוכרת מאוזנת', 'מטופלת ותיקה, מגיעה עם בעלה', 'tkatz', 'pat004'),
(1, 'Moshe', 'Friedman', 'M', '1955-12-03', 'Bnei Brak', 'לחץ דם גבוה', 'מטופל דתי, מעדיף טיפולים בימי ראשון', 'mfriedm', 'pat005'),
(3, 'Noa', 'Golan', 'F', '1995-09-18', 'Ramat Gan', 'מטופלת בריאה', 'מעוניינת בטיפולים אסתטיים', 'ngolan', 'pat006'),
(1, 'Eli', 'Stern', 'M', '1970-01-25', 'Netanya', 'אסתמה קלה', 'מטופל עסוק, מעדיף תורים מוקדמים', 'estern', 'pat007'),
(1, 'Shira', 'Weiss', 'F', '1988-04-12', 'Herzliya', 'בהריון (חודש 6)', 'זקוקה לטיפולים עדינים בתקופת ההריון', 'sweiss', 'pat008'),
(2, 'Daniel', 'Rosenberg', 'M', '2005-08-07', 'Petah Tikva', 'מטופל צעיר', 'זקוק ליישור שיניים', 'drosenb', 'pat009'),
(1, 'Rivka', 'Goldberg', 'F', '1943-02-14', 'Tel Aviv', 'מטופלת מבוגרת', 'זקוקה לתותבת חלקית', 'rgoldb', 'pat010'),
(1, 'Yair', 'Levi', 'M', '1980-06-28', 'Ashdod', 'מטופל בריא', 'מגיע לבדיקות תקופתיות', 'ylevi', 'pat011'),
(1, 'Dina', 'Avraham', 'F', '1972-10-15', 'Eilat', 'אלרגיה לטקס', 'מטופלת רגישה, זקוקה לכפפות ללא טקס', 'davraha', 'pat012'),
(3, 'Ron', 'Peretz', 'M', '1990-03-03', 'Kfar Saba', 'מטופל ספורטאי', 'מעוניין במגן שיניים לספורט', 'rperetz', 'pat013'),
(1, 'Gila', 'Mor', 'F', '1960-11-20', 'Holon', 'מטופלת ותיקה', 'זקוקה לטיפולי חניכיים', 'gmor', 'pat014'),
(1, 'Amir', 'Segal', 'M', '1975-07-09', 'Rishon LeZion', 'מטופל עם חרדת שיניים', 'זקוק להרגעה לפני כל טיפול', 'asegal', 'pat015'),
(2, 'Maya', 'Klein', 'F', '1998-12-25', 'Raanana', 'סטודנטית', 'מעוניינת בהלבנת שיניים', 'mklein', 'pat016'),
(1, 'Boaz', 'Haim', 'M', '1963-05-17', 'Bat Yam', 'מטופל מעשן', 'זקוק לניקויים תכופים', 'bhaim', 'pat017'),
(1, 'Orly', 'Dahan', 'F', '1982-09-30', 'Kiryat Gat', 'מטופלת בריאה', 'מגיעה עם הילדים לטיפולים', 'odahan', 'pat018'),
(1, 'Gadi', 'Yosef', 'M', '1968-01-11', 'Acre', 'מטופל עם ברוקסיזם', 'זקוק למגן לילה', 'gyosef', 'pat019'),
(1, 'Hila', 'Barak', 'F', '1987-08-04', 'Modiin', 'מטופלת בריאה', 'מעוניינת בטיפולי מניעה', 'hbarak', 'pat020');

-- Insert patient addresses
INSERT INTO patientsaddresses (patients_id, addressestypes_id, patientsaddresses_address, patientsaddresses_city, patientsaddresses_zipcode, patientsaddresses_country) VALUES
(1, 1, 'Dizengoff 123', 'Tel Aviv', '6473912', 'Israel'),
(2, 1, 'King George 45', 'Jerusalem', '9426218', 'Israel'),
(3, 1, 'Herzl 78', 'Haifa', '3310151', 'Israel'),
(4, 1, 'Ben Gurion 12', 'Beersheba', '8414101', 'Israel'),
(5, 1, 'Rabbi Akiva 56', 'Bnei Brak', '5120235', 'Israel'),
(6, 1, 'Weizmann 89', 'Ramat Gan', '5252141', 'Israel'),
(7, 1, 'Herzl 34', 'Netanya', '4250734', 'Israel'),
(8, 1, 'Ben Gurion 67', 'Herzliya', '4685067', 'Israel'),
(9, 1, 'Rothschild 23', 'Petah Tikva', '4951023', 'Israel'),
(10, 1, 'Allenby 156', 'Tel Aviv', '6581156', 'Israel'),
(11, 1, 'HaAtzmaut 45', 'Ashdod', '7743045', 'Israel'),
(12, 1, 'Eilat 12', 'Eilat', '8810012', 'Israel'),
(13, 1, 'Sokolov 78', 'Kfar Saba', '4441078', 'Israel'),
(14, 1, 'Sokolov 34', 'Holon', '5845034', 'Israel'),
(15, 1, 'Jabotinsky 89', 'Rishon LeZion', '7546089', 'Israel'),
(16, 1, 'Ahuza 23', 'Raanana', '4350023', 'Israel'),
(17, 1, 'Ben Yehuda 67', 'Bat Yam', '5930067', 'Israel'),
(18, 1, 'HaNasi 12', 'Kiryat Gat', '8210012', 'Israel'),
(19, 1, 'Weizmann 45', 'Acre', '2413045', 'Israel'),
(20, 1, 'Emek Dotan 78', 'Modiin', '7177078', 'Israel');

-- Insert patient contacts
INSERT INTO patientscontacts (patients_id, contactstypes_id, patientscontacts_contact) VALUES
-- Mobile phones
(1, 1, '050-1234567'), (2, 1, '052-2345678'), (3, 1, '054-3456789'), (4, 1, '050-4567890'),
(5, 1, '052-5678901'), (6, 1, '054-6789012'), (7, 1, '050-7890123'), (8, 1, '052-8901234'),
(9, 1, '054-9012345'), (10, 1, '050-0123456'), (11, 1, '052-1234567'), (12, 1, '054-2345678'),
(13, 1, '050-3456789'), (14, 1, '052-4567890'), (15, 1, '054-5678901'), (16, 1, '050-6789012'),
(17, 1, '052-7890123'), (18, 1, '054-8901234'), (19, 1, '050-9012345'), (20, 1, '052-0123456'),
-- Emails
(1, 4, 'yossi.mizrahi@gmail.com'), (2, 4, 'miriam.shapiro@walla.co.il'), (3, 4, 'avi.bendavid@student.technion.ac.il'),
(4, 4, 'tamar.katz@hotmail.com'), (5, 4, 'moshe.friedman@gmail.com'), (6, 4, 'noa.golan@outlook.com'),
(7, 4, 'eli.stern@company.co.il'), (8, 4, 'shira.weiss@gmail.com'), (9, 4, 'daniel.rosenberg@student.edu'),
(10, 4, 'rivka.goldberg@gmail.com'), (11, 4, 'yair.levi@yahoo.com'), (12, 4, 'dina.avraham@walla.co.il'),
(13, 4, 'ron.peretz@sport.co.il'), (14, 4, 'gila.mor@gmail.com'), (15, 4, 'amir.segal@company.co.il'),
(16, 4, 'maya.klein@student.ac.il'), (17, 4, 'boaz.haim@hotmail.com'), (18, 4, 'orly.dahan@gmail.com'),
(19, 4, 'gadi.yosef@walla.co.il'), (20, 4, 'hila.barak@outlook.com');

-- Insert appointments for the next two weeks
INSERT INTO appointments (doctors_id, patients_id, rooms_id, appointments_from, appointments_to, appointments_title, appointments_notes, appointments_color, appointments_status) VALUES
-- Today's appointments
('1', '1', '1', '2025-09-27 09:00:00', '2025-09-27 09:30:00', 'Dental Cleaning', 'ניקוי שיניים תקופתי', '#4CAF50', 'confirmed'),
('2', '6', '4', '2025-09-27 10:00:00', '2025-09-27 11:00:00', 'Orthodontic Consultation', 'ייעוץ יישור שיניים', '#2196F3', 'confirmed'),
('3', '15', '3', '2025-09-27 11:30:00', '2025-09-27 12:00:00', 'Tooth Extraction', 'עקירת שן בינה', '#FF5722', 'confirmed'),
('4', '9', '2', '2025-09-27 14:00:00', '2025-09-27 14:30:00', 'Dental Examination', 'בדיקת שיניים לילד', '#9C27B0', 'scheduled'),
('1', '4', '1', '2025-09-27 15:00:00', '2025-09-27 15:45:00', 'Root Canal', 'טיפול שורש שן 36', '#FF9800', 'scheduled'),

-- Tomorrow's appointments
('2', '16', '2', '2025-09-28 08:30:00', '2025-09-28 09:30:00', 'Teeth Whitening', 'הלבנת שיניים', '#E91E63', 'scheduled'),
('1', '7', '1', '2025-09-28 10:00:00', '2025-09-28 10:30:00', 'Dental Cleaning', 'ניקוי שיניים', '#4CAF50', 'scheduled'),
('3', '14', '3', '2025-09-28 11:00:00', '2025-09-28 12:00:00', 'Gum Surgery', 'ניתוח חניכיים', '#795548', 'scheduled'),
('4', '18', '2', '2025-09-28 13:30:00', '2025-09-28 14:00:00', 'Dental Examination', 'בדיקת שיניים', '#9C27B0', 'scheduled'),
('2', '13', '4', '2025-09-28 15:00:00', '2025-09-28 15:30:00', 'Sports Mouthguard', 'מגן שיניים לספורט', '#607D8B', 'scheduled'),

-- Next week appointments
('1', '2', '1', '2025-09-29 09:00:00', '2025-09-29 09:30:00', 'Filling', 'סתימה קומפוזיט', '#4CAF50', 'scheduled'),
('2', '19', '2', '2025-09-29 10:30:00', '2025-09-29 11:00:00', 'Night Guard Fitting', 'התאמת מגן לילה', '#3F51B5', 'scheduled'),
('3', '5', '3', '2025-09-29 14:00:00', '2025-09-29 14:30:00', 'Dental Examination', 'בדיקת שיניים', '#9C27B0', 'scheduled'),
('4', '20', '2', '2025-09-29 15:30:00', '2025-09-29 16:00:00', 'Fluoride Treatment', 'טיפול פלואור', '#00BCD4', 'scheduled'),

('1', '8', '1', '2025-09-30 09:30:00', '2025-09-30 10:00:00', 'Prenatal Dental Care', 'טיפול שיניים בהריון', '#E91E63', 'scheduled'),
('2', '11', '4', '2025-09-30 11:00:00', '2025-09-30 11:30:00', 'Dental Cleaning', 'ניקוי שיניים', '#4CAF50', 'scheduled'),
('3', '12', '3', '2025-09-30 13:00:00', '2025-09-30 13:30:00', 'Latex-Free Treatment', 'טיפול ללא טקס', '#FF5722', 'scheduled'),
('4', '17', '2', '2025-09-30 14:30:00', '2025-09-30 15:00:00', 'Smoker Cleaning', 'ניקוי למעשן', '#795548', 'scheduled'),

('1', '3', '1', '2025-10-01 08:00:00', '2025-10-01 08:30:00', 'Student Checkup', 'בדיקה לסטודנט', '#9C27B0', 'scheduled'),
('2', '10', '2', '2025-10-01 10:00:00', '2025-10-01 11:30:00', 'Partial Denture', 'התאמת תותבת חלקית', '#607D8B', 'scheduled'),
('3', '1', '3', '2025-10-01 13:30:00', '2025-10-01 14:00:00', 'Follow-up', 'מעקב אחר טיפול', '#4CAF50', 'scheduled'),

-- Weekend appointments (Sunday)
('1', '6', '1', '2025-10-05 09:00:00', '2025-10-05 10:00:00', 'Veneer Consultation', 'ייעוץ ציפויים', '#E91E63', 'scheduled'),
('4', '9', '2', '2025-10-05 10:30:00', '2025-10-05 11:00:00', 'Orthodontic Follow-up', 'מעקב יישור שיניים', '#2196F3', 'scheduled'),
('2', '15', '4', '2025-10-05 11:30:00', '2025-10-05 12:00:00', 'Post-Surgery Check', 'בדיקה אחרי ניתוח', '#FF5722', 'scheduled');

-- Insert some completed treatments
INSERT INTO patientstreatments (patients_id, doctors_id, treatments_id, appointments_id, patientstreatments_date, patientstreatments_notes, patientstreatments_price, patientstreatments_status) VALUES
(1, 1, 1, 1, '2025-09-27', 'ניקוי שיניים מקצועי הושלם בהצלחה', 250.00, 'completed'),
(2, 1, 3, NULL, '2025-09-20', 'בדיקת שיניים תקופתית', 200.00, 'completed'),
(3, 4, 3, NULL, '2025-09-15', 'בדיקת שיניים ראשונה', 160.00, 'completed'),
(4, 1, 9, NULL, '2025-09-10', 'טיפול שורש שן 24', 1800.00, 'completed'),
(5, 3, 11, NULL, '2025-09-05', 'גירוד אבנית', 350.00, 'completed'),
(6, 2, 19, NULL, '2025-08-30', 'הלבנת שיניים', 1200.00, 'completed'),
(7, 1, 1, NULL, '2025-08-25', 'ניקוי שיניים', 250.00, 'completed'),
(8, 4, 2, NULL, '2025-08-20', 'טיפול פלואור בהריון', 150.00, 'completed'),
(9, 2, 3, NULL, '2025-08-15', 'בדיקת שיניים לילד', 160.00, 'completed'),
(10, 1, 6, NULL, '2025-08-10', 'סתימה קומפוזיט', 450.00, 'completed');

-- Insert payments
INSERT INTO payments (patients_id, paymentstypes_id, payments_amount, payments_date, payments_notes, payments_reference) VALUES
(1, 1, 250.00, '2025-09-27', 'תשלום עבור ניקוי שיניים', 'CASH001'),
(2, 2, 200.00, '2025-09-20', 'תשלום בכרטיס אשראי', 'CC002'),
(3, 6, 80.00, '2025-09-15', 'תשלום ראשון מתוך 2', 'INST003'),
(3, 6, 80.00, '2025-09-22', 'תשלום שני מתוך 2', 'INST004'),
(4, 5, 1440.00, '2025-09-10', 'תשלום ביטוח עבור טיפול שורש', 'INS005'),
(4, 1, 360.00, '2025-09-10', 'השתתפות עצמית', 'CASH006'),
(5, 2, 350.00, '2025-09-05', 'תשלום בכרטיס אשראי', 'CC007'),
(6, 3, 1200.00, '2025-08-30', 'העברה בנקאית', 'BANK008'),
(7, 1, 250.00, '2025-08-25', 'תשלום מזומן', 'CASH009'),
(8, 5, 120.00, '2025-08-20', 'תשלום ביטוח', 'INS010'),
(8, 1, 30.00, '2025-08-20', 'השתתפות עצמית', 'CASH011'),
(9, 6, 53.33, '2025-08-15', 'תשלום ראשון מתוך 3', 'INST012'),
(9, 6, 53.33, '2025-08-29', 'תשלום שני מתוך 3', 'INST013'),
(10, 2, 450.00, '2025-08-10', 'תשלום בכרטיס אשראי', 'CC014');

-- Insert some invoices
INSERT INTO invoices (doctors_id, patients_id, invoices_number, invoices_date, invoices_doctor, invoices_patient, invoices_payment, invoices_footer, invoices_totalnet, invoices_totalgross, invoices_totaldue, invoices_deductiontaxrate, invoices_status) VALUES
(1, 1, 'INV-2025-001', '2025-09-27', 'Dr. David Cohen', 'Yossi Mizrahi', 'Cash', 'תודה על הביקור', 213.68, 250.00, 0.00, 17.00, 'paid'),
(1, 2, 'INV-2025-002', '2025-09-20', 'Dr. David Cohen', 'Miriam Shapiro', 'Credit Card', 'תודה על הביקור', 170.94, 200.00, 0.00, 17.00, 'paid'),
(4, 3, 'INV-2025-003', '2025-09-15', 'Dr. Rachel Rosen', 'Avi Ben-David', 'Installments', 'הנחה לסטודנט', 136.75, 160.00, 80.00, 17.00, 'partial'),
(1, 4, 'INV-2025-004', '2025-09-10', 'Dr. David Cohen', 'Tamar Katz', 'Insurance + Cash', 'טיפול שורש', 1538.46, 1800.00, 0.00, 17.00, 'paid'),
(3, 5, 'INV-2025-005', '2025-09-05', 'Dr. Michael Goldstein', 'Moshe Friedman', 'Credit Card', 'גירוד אבנית', 299.15, 350.00, 0.00, 17.00, 'paid');

-- Insert invoice lines
INSERT INTO invoiceslines (invoices_id, patientstreatments_id, invoiceslines_code, invoiceslines_description, invoiceslines_quantity, invoiceslines_unitprice, invoiceslines_taxrate, invoiceslines_istaxesdeductionsable) VALUES
(1, 1, '001', 'ניקוי שיניים מקצועי', 1, 250.00, 17.00, TRUE),
(2, 2, '003', 'בדיקת שיניים תקופתית', 1, 200.00, 17.00, TRUE),
(3, 3, '003', 'בדיקת שיניים ראשונה - הנחת סטודנט', 1, 160.00, 17.00, TRUE),
(4, 4, '201', 'טיפול שורש שן 24', 1, 1800.00, 17.00, TRUE),
(5, 5, '301', 'גירוד אבנית', 1, 350.00, 17.00, TRUE);

-- Insert some estimates for future treatments
INSERT INTO estimates (doctors_id, patients_id, estimates_number, estimates_date, estimates_doctor, estimates_patient, estimates_payment, estimates_footer, estimates_totalnet, estimates_totalgross, estimates_totaldue, estimates_deductiontaxrate, estimates_status) VALUES
(2, 9, 'EST-2025-001', '2025-09-27', 'Dr. Sarah Levy', 'Daniel Rosenberg', 'Installments', 'הצעת מחיר ליישור שיניים', 6837.61, 8000.00, 8000.00, 17.00, 'sent'),
(1, 10, 'EST-2025-002', '2025-09-27', 'Dr. David Cohen', 'Rivka Goldberg', 'Insurance', 'הצעת מחיר לתותבת חלקית', 3846.15, 4500.00, 4500.00, 17.00, 'draft'),
(2, 16, 'EST-2025-003', '2025-09-27', 'Dr. Sarah Levy', 'Maya Klein', 'Cash', 'הצעת מחיר להלבנת שיניים', 1025.64, 1200.00, 1200.00, 17.00, 'sent');

-- Insert estimate lines
INSERT INTO estimateslines (estimates_id, estimateslines_code, estimateslines_description, estimateslines_quantity, estimateslines_unitprice, estimateslines_taxrate, estimateslines_istaxesdeductionsable) VALUES
(1, '401', 'גשר מתכת - טיפול מלא', 1, 8000.00, 17.00, TRUE),
(2, '601', 'תותבת חלקית עליונה', 1, 4500.00, 17.00, TRUE),
(3, '701', 'הלבנת שיניים מקצועית', 1, 1200.00, 17.00, TRUE);

-- Success message
SELECT 'Demo data populated successfully!' AS status,
       (SELECT COUNT(*) FROM patients) AS total_patients,
       (SELECT COUNT(*) FROM doctors) AS total_doctors,
       (SELECT COUNT(*) FROM appointments WHERE appointments_from >= CURDATE()) AS upcoming_appointments,
       (SELECT COUNT(*) FROM patientstreatments) AS completed_treatments;
