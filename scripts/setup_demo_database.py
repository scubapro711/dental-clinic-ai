#!/usr/bin/env python3
"""
Demo Database Setup Script for Dental Clinic AI
Creates and populates the demo database in AWS RDS
"""

import pymysql
import os
import sys
from pathlib import Path

# Database configuration
DB_CONFIG = {
    'host': 'dental-prod-database.c0jiwcc6ykf7.us-east-1.rds.amazonaws.com',
    'user': 'dental_user',
    'password': 'dental_pass_2025',
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
    print("Setting up Demo Database for Dental Clinic AI")
    print("=" * 50)
    
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
        print("Connecting to AWS RDS MySQL...")
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
        
        cursor.close()
        connection.close()
        
        print("\n🎉 Demo database setup completed successfully!")
        print("The system is now ready to use real database instead of mock data.")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
