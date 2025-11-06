#!/bin/bash
set -e

echo "🚀 Starting DentaFlow Backend..."

# Wait for database to be ready with retry logic
echo "⏳ Waiting for database connection..."
MAX_RETRIES=30
RETRY_COUNT=0
RETRY_DELAY=2

wait_for_db() {
    python3 -c "
import sys
import time
from sqlalchemy import create_engine, text
from app.core.config import settings

max_retries = $MAX_RETRIES
retry_count = 0

while retry_count < max_retries:
    try:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('✅ Database connection successful')
        sys.exit(0)
    except Exception as e:
        retry_count += 1
        if retry_count >= max_retries:
            print(f'❌ Database connection failed after {max_retries} attempts: {e}')
            sys.exit(1)
        print(f'⏳ Database not ready yet (attempt {retry_count}/{max_retries}), waiting ${RETRY_DELAY}s...')
        time.sleep($RETRY_DELAY)
"
}

# Wait for database
if wait_for_db; then
    echo "✅ Database is ready"
else
    echo "❌ Failed to connect to database"
    exit 1
fi

# Run database migrations
echo "📦 Running database migrations..."
alembic upgrade head

# Check if migrations succeeded
if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migrations failed!"
    exit 1
fi

# Start the application
echo "🌟 Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
