#!/bin/bash
set -e

echo "🚀 Starting DentaFlow Backend..."

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
