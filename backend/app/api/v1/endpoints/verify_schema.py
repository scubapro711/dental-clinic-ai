"""
Temporary endpoint to verify telegram_users table schema.
This endpoint should be removed after verification is complete.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/verify-telegram-users-schema")
async def verify_telegram_users_schema(db: Session = Depends(get_db)):
    """
    Verify the actual schema of telegram_users table in the database.
    
    Returns all column names, types, and constraints.
    """
    try:
        logger.info("🔍 Checking telegram_users table schema...")
        
        # Get all columns
        columns_sql = """
        SELECT 
            column_name, 
            data_type, 
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'telegram_users'
        ORDER BY ordinal_position;
        """
        
        result = db.execute(text(columns_sql))
        columns = [dict(row._mapping) for row in result]
        
        # Get indexes
        indexes_sql = """
        SELECT
            indexname,
            indexdef
        FROM pg_indexes
        WHERE tablename = 'telegram_users';
        """
        
        result = db.execute(text(indexes_sql))
        indexes = [dict(row._mapping) for row in result]
        
        # Get constraints
        constraints_sql = """
        SELECT
            conname as constraint_name,
            contype as constraint_type
        FROM pg_constraint
        WHERE conrelid = 'telegram_users'::regclass;
        """
        
        result = db.execute(text(constraints_sql))
        constraints = [dict(row._mapping) for row in result]
        
        logger.info(f"📊 Found {len(columns)} columns in telegram_users table")
        
        return {
            "success": True,
            "table_name": "telegram_users",
            "columns": columns,
            "indexes": indexes,
            "constraints": constraints
        }
        
    except Exception as e:
        logger.error(f"❌ Schema verification failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

