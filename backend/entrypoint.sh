#!/bin/bash
set -e

echo "🚀 Starting DentaFlow Backend..."

# Optional database connection check (non-blocking)
echo "⏳ Checking database connection..."
python3 -c "
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

try:
    engine = create_engine(str(settings.DATABASE_URL))
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('✅ Database connection successful')
except Exception as e:
    print(f'⚠️  Database connection check failed: {e}')
    print('⚠️  Server will start anyway. Database operations may fail until connection is established.')
" || true

echo "🌟 Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
