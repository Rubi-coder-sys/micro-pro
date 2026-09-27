"""
Seed script — Initializes the database with schema and dummy data.

Run this script to:
1. Create all tables (if they don't exist).
2. Insert dummy users with properly hashed passwords.
3. Insert sample components, requests, issues, and complaints.

Usage:
    python seed_data.py
"""

import os
import sys

# Add parent directory to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from werkzeug.security import generate_password_hash
from config import Config


SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")

DEFAULT_PASSWORD = "password123"

USERS = [
    ("Alice Johnson", "ENR001", "REG001", "Computer Science", "alice@college.edu", "student"),
    ("Bob Smith", "ENR002", "REG002", "Electronics", "bob@college.edu", "student"),
    ("Charlie Brown", "ENR003", "REG003", "Information Technology", "charlie@college.edu", "student"),
    ("Dr. Sarah Williams", None, None, "Computer Science", "sarah.faculty@college.edu", "faculty"),
    ("Prof. James Davis", None, None, "Electronics", "james.faculty@college.edu", "faculty"),
]

COMPONENTS = [
    ("ARD-UNO-001", "Arduino Uno R3", "Microcontroller", 20, 18, "Arduino Uno R3 development board", "active"),
    ("ARD-MEGA-001", "Arduino Mega 2560", "Microcontroller", 10, 8, "Arduino Mega 2560 with 54 digital I/O pins", "active"),
    ("RPI-4B-001", "Raspberry Pi 4 Model B", "Single Board Computer", 15, 12, "Raspberry Pi 4B with 4GB RAM", "active"),
    ("SENS-DHT11-001", "DHT11 Temperature Sensor", "Sensor", 50, 45, "Digital temperature and humidity sensor", "active"),
    ("SENS-ULTRA-001", "HC-SR04 Ultrasonic Sensor", "Sensor", 40, 35, "Ultrasonic distance sensor module", "active"),
    ("LED-KIT-001", "LED Assortment Kit", "Passive Component", 30, 28, "Assorted LEDs", "active"),
    ("RES-KIT-001", "Resistor Kit 1/4W", "Passive Component", 25, 25, "500pcs resistor assortment kit", "active"),
    ("BREAD-001", "Breadboard 830 Points", "Prototyping", 35, 30, "Full-size solderless breadboard", "active"),
    ("WIRE-JMP-001", "Jumper Wire Kit", "Prototyping", 40, 38, "Jumper wires assortment", "active"),
    ("MOT-SERVO-001", "SG90 Servo Motor", "Actuator", 20, 15, "Micro servo motor", "active"),
    ("OLD-COMP-001", "Legacy Serial Port Card", "Legacy", 5, 5, "Old RS232 serial port card", "inactive"),
]


def create_database_if_needed():
    """Create the lab_components_db database if it doesn't exist."""
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname="postgres",
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (Config.DB_NAME,))
        if not cur.fetchone():
            cur.execute(f'CREATE DATABASE "{Config.DB_NAME}"')
            print(f"[OK] Database '{Config.DB_NAME}' created.")
        else:
            print(f"[OK] Database '{Config.DB_NAME}' already exists.")
        cur.close()
        conn.close()
    except psycopg2.OperationalError as e:
        print(f"[FAIL] Cannot connect to PostgreSQL: {e}")
        print("  Make sure PostgreSQL is running and credentials are correct in .env")
        sys.exit(1)


def run_schema():
    """Execute the schema.sql file to create tables."""
    schema_path = os.path.normpath(SCHEMA_PATH)
    if not os.path.exists(schema_path):
        print(f"[FAIL] Schema file not found: {schema_path}")
        sys.exit(1)

    conn = psycopg2.connect(Config.get_db_dsn())
    try:
        cur = conn.cursor()
        with open(schema_path, "r") as f:
            sql = f.read()
        cur.execute(sql)
        conn.commit()
        print("[OK] Schema applied successfully.")
        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"[FAIL] Error applying schema: {e}")
        sys.exit(1)
    finally:
        conn.close()


def seed_users():
    """Insert dummy users with hashed passwords."""
    conn = psycopg2.connect(Config.get_db_dsn())
    try:
        cur = conn.cursor()
        password_hash = generate_password_hash(DEFAULT_PASSWORD)
        for name, enr, reg, dept, email, role in USERS:
            cur.execute(
                """INSERT INTO users (name, enrollment_number, register_number, department, email, password_hash, role)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (email) DO NOTHING""",
                (name, enr, reg, dept, email, password_hash, role),
            )
        conn.commit()
        print(f"[OK] {len(USERS)} users seeded (password: {DEFAULT_PASSWORD}).")
        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"[FAIL] Error seeding users: {e}")
    finally:
        conn.close()


def seed_components():
    """Insert sample components."""
    conn = psycopg2.connect(Config.get_db_dsn())
    try:
        cur = conn.cursor()
        for code, name, cat, total, avail, desc, status in COMPONENTS:
            cur.execute(
                """INSERT INTO components
                   (component_code, name, category, total_quantity, available_quantity, description, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (component_code) DO NOTHING""",
                (code, name, cat, total, avail, desc, status),
            )
        conn.commit()
        print(f"[OK] {len(COMPONENTS)} components seeded.")
        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"[FAIL] Error seeding components: {e}")
    finally:
        conn.close()


def main():
    print("=" * 50)
    print("Lab Components Management — Database Seeder")
    print("=" * 50)
    print()

    create_database_if_needed()
    run_schema()
    seed_users()
    seed_components()

    print()
    print("[OK] Database setup complete!")
    print(f"  Database: {Config.DB_NAME}")
    print(f"  Host: {Config.DB_HOST}:{Config.DB_PORT}")
    print(f"  Default login: alice@college.edu / {DEFAULT_PASSWORD}")
    print(f"  Faculty login: sarah.faculty@college.edu / {DEFAULT_PASSWORD}")


if __name__ == "__main__":
    main()
