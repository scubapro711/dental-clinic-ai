# Dockerfile for Database Backup Cloud Run Job

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Google Cloud SDK
RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH $PATH:/root/google-cloud-sdk/bin

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backup script and application
COPY backup_app.py .
COPY ../scripts/backup-database-gcs.sh /app/backup-database-gcs.sh
RUN chmod +x /app/backup-database-gcs.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the backup application
CMD ["python", "backup_app.py"]

