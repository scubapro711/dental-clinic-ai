"""
Temporary migration endpoint for adding fields to telegram_users table.
This endpoint should be removed after migration is complete.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging_config import logger

router = APIRouter()


@router.post("/run-telegram-user-migration")
async def run_telegram_user_migration(db: Session = Depends(get_db)):
    """
    Run migration to add phone, status, linked_at columns to telegram_users table.
    
    **WARNING:** This is a temporary endpoint and should be removed after use.
    """
    try:
        logger.info("🔧 Starting telegram_users migration...")
        
        # Migration SQL
        migration_sql = """
        -- Add phone column
        ALTER TABLE telegram_users 
        ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
        
        -- Add status column with default value
        ALTER TABLE telegram_users 
        ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'NEW';
        
        -- Add linked_at column
        ALTER TABLE telegram_users 
        ADD COLUMN IF NOT EXISTS linked_at TIMESTAMP WITH TIME ZONE;
        
        -- Update existing records to have NEW status if null
        UPDATE telegram_users 
        SET status = 'NEW' 
        WHERE status IS NULL;
        
        -- Create index on status for faster queries
        CREATE INDEX IF NOT EXISTS idx_telegram_users_status ON telegram_users(status);
        """
        
        # Execute migration
        db.execute(text(migration_sql))
        db.commit()
        
        logger.info("✅ Migration completed successfully!")
        
        # Verify the changes
        verify_sql = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'telegram_users'
        AND column_name IN ('phone', 'status', 'linked_at')
        ORDER BY column_name;
        """
        
        result = db.execute(text(verify_sql))
        columns = [dict(row._mapping) for row in result]
        
        logger.info(f"📊 Verified columns: {columns}")
        
        return {
            "success": True,
            "message": "Migration completed successfully",
            "columns_added": columns
        }
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Migration failed: {str(e)}"
        )

