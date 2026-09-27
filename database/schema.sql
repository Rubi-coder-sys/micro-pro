-- ============================================
-- LAB COMPONENTS MANAGEMENT SYSTEM
-- Database Schema
-- ============================================

-- Create database (run this separately as superuser)
-- CREATE DATABASE lab_components_db;

-- Connect to lab_components_db before running below

-- ============================================
-- 1. USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    enrollment_number VARCHAR(50) UNIQUE,
    register_number VARCHAR(50) UNIQUE,
    department VARCHAR(100),
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'faculty')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- ============================================
-- 2. COMPONENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS components (
    id SERIAL PRIMARY KEY,
    component_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    total_quantity INTEGER NOT NULL DEFAULT 0 CHECK (total_quantity >= 0),
    available_quantity INTEGER NOT NULL DEFAULT 0 CHECK (available_quantity >= 0),
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_quantity CHECK (available_quantity <= total_quantity)
);

-- ============================================
-- 3. COMPONENT_REQUESTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS component_requests (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES components(id),
    student_id INTEGER NOT NULL REFERENCES users(id),
    request_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    queue_position INTEGER,
    available_from TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP
);

-- ============================================
-- 4. ISSUE_RECORDS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS issue_records (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES components(id),
    student_id INTEGER NOT NULL REFERENCES users(id),
    request_id INTEGER REFERENCES component_requests(id),
    issue_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    return_date TIMESTAMP,
    fine_amount NUMERIC(10, 2) DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'issued' CHECK (status IN ('issued', 'returned'))
);

-- ============================================
-- 5. DAMAGE_RECORDS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS damage_records (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES components(id),
    student_id INTEGER NOT NULL REFERENCES users(id),
    issue_id INTEGER REFERENCES issue_records(id),
    damage_description TEXT NOT NULL,
    damage_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    quantity_damaged INTEGER NOT NULL DEFAULT 1 CHECK (quantity_damaged > 0)
);

-- ============================================
-- 6. COMPLAINTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS complaints (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id),
    component_id INTEGER REFERENCES components(id),
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved'))
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_components_code ON components(component_code);
CREATE INDEX IF NOT EXISTS idx_components_category ON components(category);
CREATE INDEX IF NOT EXISTS idx_components_status ON components(status);
CREATE INDEX IF NOT EXISTS idx_requests_component ON component_requests(component_id);
CREATE INDEX IF NOT EXISTS idx_requests_student ON component_requests(student_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON component_requests(status);
CREATE INDEX IF NOT EXISTS idx_issues_component ON issue_records(component_id);
CREATE INDEX IF NOT EXISTS idx_issues_student ON issue_records(student_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issue_records(status);
CREATE INDEX IF NOT EXISTS idx_damages_component ON damage_records(component_id);
CREATE INDEX IF NOT EXISTS idx_complaints_student ON complaints(student_id);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
