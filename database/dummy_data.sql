-- ============================================
-- LAB COMPONENTS MANAGEMENT SYSTEM
-- Dummy / Seed Data
-- ============================================

-- NOTE: Passwords are hashed using Werkzeug's generate_password_hash
-- All dummy passwords are: password123

-- ============================================
-- USERS
-- ============================================
-- Password hash for 'password123' generated with werkzeug
-- You can regenerate these using: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('password123'))"

INSERT INTO users (name, enrollment_number, register_number, department, email, password_hash, role, is_active)
VALUES
    ('Alice Johnson', 'ENR001', 'REG001', 'Computer Science', 'alice@college.edu', 'scrypt:32768:8:1$placeholder$placeholder', 'student', TRUE),
    ('Bob Smith', 'ENR002', 'REG002', 'Electronics', 'bob@college.edu', 'scrypt:32768:8:1$placeholder$placeholder', 'student', TRUE),
    ('Charlie Brown', 'ENR003', 'REG003', 'Information Technology', 'charlie@college.edu', 'scrypt:32768:8:1$placeholder$placeholder', 'student', TRUE),
    ('Dr. Sarah Williams', NULL, NULL, 'Computer Science', 'sarah.faculty@college.edu', 'scrypt:32768:8:1$placeholder$placeholder', 'faculty', TRUE),
    ('Prof. James Davis', NULL, NULL, 'Electronics', 'james.faculty@college.edu', 'scrypt:32768:8:1$placeholder$placeholder', 'faculty', TRUE)
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- COMPONENTS
-- ============================================
INSERT INTO components (component_code, name, category, total_quantity, available_quantity, description, status)
VALUES
    ('ARD-UNO-001', 'Arduino Uno R3', 'Microcontroller', 20, 18, 'Arduino Uno R3 development board with ATmega328P microcontroller', 'active'),
    ('ARD-MEGA-001', 'Arduino Mega 2560', 'Microcontroller', 10, 8, 'Arduino Mega 2560 with 54 digital I/O pins', 'active'),
    ('RPI-4B-001', 'Raspberry Pi 4 Model B', 'Single Board Computer', 15, 12, 'Raspberry Pi 4 Model B with 4GB RAM', 'active'),
    ('SENS-DHT11-001', 'DHT11 Temperature Sensor', 'Sensor', 50, 45, 'Digital temperature and humidity sensor module', 'active'),
    ('SENS-ULTRA-001', 'HC-SR04 Ultrasonic Sensor', 'Sensor', 40, 35, 'Ultrasonic distance sensor module', 'active'),
    ('LED-KIT-001', 'LED Assortment Kit', 'Passive Component', 30, 28, 'Assorted LEDs - Red, Green, Blue, Yellow, White', 'active'),
    ('RES-KIT-001', 'Resistor Kit 1/4W', 'Passive Component', 25, 25, '500pcs resistor assortment kit with various values', 'active'),
    ('BREAD-001', 'Breadboard 830 Points', 'Prototyping', 35, 30, 'Full-size solderless breadboard with 830 tie points', 'active'),
    ('WIRE-JMP-001', 'Jumper Wire Kit', 'Prototyping', 40, 38, 'Male-to-male, male-to-female, female-to-female jumper wires', 'active'),
    ('MOT-SERVO-001', 'SG90 Servo Motor', 'Actuator', 20, 15, 'Micro servo motor 180 degree rotation', 'active'),
    ('MOT-DC-001', 'DC Motor 5V', 'Actuator', 15, 12, '5V DC motor for robotics projects', 'active'),
    ('DISP-LCD-001', 'LCD 16x2 Display', 'Display', 20, 18, '16x2 character LCD display module with I2C', 'active'),
    ('DISP-OLED-001', 'OLED 0.96 inch Display', 'Display', 12, 10, '0.96 inch OLED display module 128x64 I2C', 'active'),
    ('MOD-RELAY-001', 'Relay Module 4-Channel', 'Module', 10, 8, '4-channel relay module 5V with optocoupler', 'active'),
    ('MOD-WIFI-001', 'ESP8266 WiFi Module', 'Communication', 25, 20, 'ESP8266 NodeMCU WiFi development board', 'active'),
    ('OLD-COMP-001', 'Legacy Serial Port Card', 'Legacy', 5, 5, 'Old RS232 serial port expansion card', 'inactive')
ON CONFLICT (component_code) DO NOTHING;

-- ============================================
-- COMPONENT REQUESTS (sample)
-- ============================================
INSERT INTO component_requests (component_id, student_id, request_date, queue_position, status)
VALUES
    (1, 1, CURRENT_TIMESTAMP - INTERVAL '3 days', NULL, 'approved'),
    (3, 2, CURRENT_TIMESTAMP - INTERVAL '2 days', NULL, 'pending'),
    (5, 3, CURRENT_TIMESTAMP - INTERVAL '1 day', NULL, 'pending');

-- ============================================
-- ISSUE RECORDS (sample)
-- ============================================
INSERT INTO issue_records (component_id, student_id, request_id, issue_date, due_date, status)
VALUES
    (1, 1, 1, CURRENT_TIMESTAMP - INTERVAL '3 days', CURRENT_TIMESTAMP + INTERVAL '11 days', 'issued');

-- ============================================
-- COMPLAINTS (sample)
-- ============================================
INSERT INTO complaints (student_id, component_id, description, status)
VALUES
    (2, 4, 'DHT11 sensor gives incorrect temperature readings', 'open');

-- NOTE: The password hashes above are placeholders.
-- Run the seed_data.py script in the backend to insert proper hashed passwords.
