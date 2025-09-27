#!/bin/bash
#
# AI Dental Clinic - Development Environment Setup Script
#
# This script automates the setup of the local development environment.

set -e

echo "🚀 Starting AI Dental Clinic Development Environment Setup..."

# Check for Docker and Docker Compose
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker and/or Docker Compose are not installed. Please install them to continue."
    exit 1
fi

# 1. Setup .env file
if [ -f ".env" ]; then
    echo "✅ .env file already exists. Skipping creation."
else
    echo "📋 .env file not found. Creating from .env.example..."
    cp .env.example .env
fi

# 2. Get OpenAI API Key
if grep -q "your_openai_api_key_here" .env; then
    read -p "🔑 Please enter your OpenAI API Key: " openai_api_key
    if [ -z "$openai_api_key" ]; then
        echo "❌ Error: OpenAI API Key cannot be empty."
        exit 1
    fi
    sed -i "s/your_openai_api_key_here/$openai_api_key/g" .env
    echo "🔑 OpenAI API Key has been set."
else
    echo "🔑 OpenAI API Key already set in .env file."
fi

# 3. Build and run Docker containers
echo "🐳 Building and starting Docker containers... (This may take a few minutes)"
docker-compose up --build -d

echo "
✅ System is up and running!"

# 4. Verify system status
echo "
🔎 Verifying system status..."
docker-compose ps

# 5. Final instructions
echo "
🎉 Setup complete! Here's how to get started:

1.  **Check Gateway Health**: Run the following command in your terminal:
    curl http://localhost:8000/health

2.  **Access API Docs**: Open your browser and navigate to:
    http://localhost:8000/docs

3.  **View Logs**: To see the logs from all services, run:
    docker-compose logs -f

4.  **Stop the System**: To stop all services, run:
    docker-compose down
"
