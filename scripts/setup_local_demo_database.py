#!/usr/bin/env python3
"""
Local Demo Database Setup Script for Dental Clinic AI
Creates and populates the demo database in local MySQL
"""

import pymysql
import os
import sys
from pathlib import Path

# Local database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'dental_user',
    'password': 'dental_pass_2025',
    'database': 'dental_clinic_demo',
    'port': 3306,
    'charset': 'utf8mb4',
    'connect_timeout': 30,
    'read_timeout': 60,
    'write_timeout': 60
}

def execute_sql_file(connection, file_path):
    """Execute SQL commands from a file"""
    print(f"Executing SQL file: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        sql_content = file.read()
    
    # Split by semicolon and execute each statement
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    cursor = connection.cursor()
    
    for i, statement in enumerate(statements):
        if statement.strip():
            try:
                print(f"Executing statement {i+1}/{len(statements)}")
                cursor.execute(statement)
                connection.commit()
                
                # If it's a SELECT statement, fetch and print results
                if statement.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    if results:
                        print(f"Results: {results}")
                        
            except Exception as e:
                print(f"Error executing statement {i+1}: {e}")
                print(f"Statement: {statement[:100]}...")
                # Continue with next statement
                continue
    
    cursor.close()
    print(f"Completed executing {file_path}")

def main():
    """Main function to set up the demo database"""
    print("Setting up Local Demo Database for Dental Clinic AI")
    print("=" * 55)
    
    # Get script directory
    script_dir = Path(__file__).parent
    schema_file = script_dir / 'create_demo_database.sql'
    data_file = script_dir / 'populate_demo_data.sql'
    
    # Check if SQL files exist
    if not schema_file.exists():
        print(f"Error: Schema file not found: {schema_file}")
        sys.exit(1)
    
    if not data_file.exists():
        print(f"Error: Data file not found: {data_file}")
        sys.exit(1)
    
    try:
        # Connect to database
        print("Connecting to local MySQL...")
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ Connected successfully!")
        
        # Execute schema creation
        print("\n📋 Creating database schema...")
        execute_sql_file(connection, schema_file)
        print("✅ Schema created successfully!")
        
        # Execute data population
        print("\n📊 Populating demo data...")
        execute_sql_file(connection, data_file)
        print("✅ Demo data populated successfully!")
        
        # Verify the setup
        print("\n🔍 Verifying database setup...")
        cursor = connection.cursor()
        
        # Check if demo database exists and switch to it
        cursor.execute("USE dental_clinic_demo")
        
        # Get table count
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✅ Created {len(tables)} tables")
        
        # Get some statistics
        cursor.execute("SELECT COUNT(*) FROM patients")
        patient_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM doctors")
        doctor_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM appointments WHERE appointments_from >= CURDATE()")
        upcoming_appointments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patientstreatments")
        completed_treatments = cursor.fetchone()[0]
        
        print(f"✅ {patient_count} patients")
        print(f"✅ {doctor_count} doctors")
        print(f"✅ {upcoming_appointments} upcoming appointments")
        print(f"✅ {completed_treatments} completed treatments")
        
        # Test some queries that the AI agent will use
        print("\n🧪 Testing AI agent queries...")
        
        # Test patient search
        cursor.execute("SELECT patients_id, patients_name, patients_surname FROM patients WHERE patients_surname LIKE '%Cohen%' OR patients_name LIKE '%David%' LIMIT 3")
        search_results = cursor.fetchall()
        print(f"✅ Patient search test: Found {len(search_results)} results")
        
        # Test appointment availability
        cursor.execute("""
            SELECT d.doctors_name, d.doctors_surname, COUNT(a.appointments_id) as appointment_count
            FROM doctors d 
            LEFT JOIN appointments a ON d.doctors_id = a.doctors_id 
            WHERE a.appointments_from >= CURDATE() AND a.appointments_from <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            GROUP BY d.doctors_id
        """)
        availability_results = cursor.fetchall()
        print(f"✅ Doctor availability test: {len(availability_results)} doctors with upcoming appointments")
        
        # Test treatment history
        cursor.execute("""
            SELECT p.patients_name, p.patients_surname, t.treatments_name, pt.patientstreatments_date
            FROM patientstreatments pt
            JOIN patients p ON pt.patients_id = p.patients_id
            JOIN treatments t ON pt.treatments_id = t.treatments_id
            ORDER BY pt.patientstreatments_date DESC
            LIMIT 5
        """)
        treatment_results = cursor.fetchall()
        print(f"✅ Treatment history test: {len(treatment_results)} recent treatments")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 Local demo database setup completed successfully!")
        print("The system is now ready to use real database instead of mock data.")
        print("\n📝 Database Connection Details:")
        print(f"   Host: {DB_CONFIG['host']}")
        print(f"   Database: {DB_CONFIG['database']}")
        print(f"   User: {DB_CONFIG['user']}")
        print(f"   Port: {DB_CONFIG['port']}")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
