#!/usr/bin/env python3
"""Reset user password in the database."""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash
from app.core.database import engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User


def reset_password(email: str, new_password: str):
    """Reset password for a user."""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ User {email} not found")
            return False
        
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        print(f"✅ Password reset for {email}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <email> <new_password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    success = reset_password(email, password)
    sys.exit(0 if success else 1)
