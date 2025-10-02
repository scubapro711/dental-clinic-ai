-- Initialize DentalAI databases
-- This script runs on first PostgreSQL container startup

-- Create Odoo database
SELECT 'CREATE DATABASE dentalai_odoo'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dentalai_odoo')\gexec
