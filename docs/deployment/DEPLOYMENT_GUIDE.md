# DentaFlow Deployment Guide

**Version:** 1.0
**Date:** October 8, 2025
**Status:** Production Ready

---

## Overview

This guide provides step-by-step instructions for deploying the complete DentaFlow system to a production environment on AWS.

## System Architecture

DentaFlow consists of three main components:

1. **Backend API** (Python/FastAPI) - Port 8000
2. **Onboarding Frontend** (React/Vite) - Served via Nginx or S3
3. **Main Dashboard** (React) - Served via Nginx or S3

## Prerequisites

- AWS Account with EC2, S3, and RDS access
- Domain name (e.g., `dentaflow.com`)
- SSL/TLS certificate (via AWS Certificate Manager or Let's Encrypt)
- Google Cloud Platform account (for OAuth)
- SendGrid or AWS SES account (for emails)
- Twilio account (for SMS)

---

## Part 1: Backend Deployment (EC2)

### 1.1 Launch EC2 Instance

```bash
# Instance specifications:
# - Type: t3.medium or larger
# - OS: Ubuntu 22.04 LTS
# - Storage: 30GB SSD
# - Security Group: Allow ports 22, 80, 443, 8000
```

### 1.2 Connect and Setup

```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql-client nginx git

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 1.3 Clone Repository

```bash
cd /home/ubuntu
git clone https://github.com/scubapro711/dental-clinic-ai.git
cd dental-clinic-ai
```

### 1.4 Setup Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env
```

### 1.5 Configure Environment Variables

Edit `/home/ubuntu/dental-clinic-ai/backend/.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/dentaflow

# Security
SECRET_KEY=your-super-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@dentaflow.com

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Odoo
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your-odoo-database
ODOO_USERNAME=admin
ODOO_PASSWORD=your-odoo-password

# Environment
ENVIRONMENT=production
```

### 1.6 Setup Database

```bash
# Run migrations
alembic upgrade head

# Create initial admin user (optional)
python scripts/create_admin.py
```

### 1.7 Setup Systemd Service

Create `/etc/systemd/system/dentaflow-backend.service`:

```ini
[Unit]
Description=DentaFlow Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dental-clinic-ai/backend
Environment="PATH=/home/ubuntu/dental-clinic-ai/backend/venv/bin"
ExecStart=/home/ubuntu/dental-clinic-ai/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dentaflow-backend
sudo systemctl start dentaflow-backend
sudo systemctl status dentaflow-backend
```

---

## Part 2: Database Setup (RDS)

### 2.1 Create RDS PostgreSQL Instance

1. Go to AWS RDS Console
2. Create PostgreSQL 15 instance
3. Instance class: `db.t3.micro` or larger
4. Storage: 20GB SSD
5. Enable automated backups
6. Set master password
7. Configure security group to allow access from EC2

### 2.2 Initialize Database

```bash
# From EC2 instance
psql -h your-rds-endpoint -U postgres -d postgres

CREATE DATABASE dentaflow;
CREATE USER dentaflow_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE dentaflow TO dentaflow_user;
\q
```

---

## Part 3: Frontend Deployment

### Option A: Deploy to S3 + CloudFront (Recommended)

#### 3.1 Build Onboarding Frontend

```bash
cd /home/ubuntu/dental-clinic-ai/dentaflow-onboarding

# Update .env
nano .env
```

Set production values:
```env
VITE_API_BASE_URL=https://api.dentaflow.com/api/v1
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
VITE_ENV=production
```

```bash
# Build
pnpm install
pnpm build

# Upload to S3
aws s3 sync dist/ s3://onboard.dentaflow.com --delete
```

#### 3.2 Build Main Dashboard

```bash
cd /home/ubuntu/dental-clinic-ai/frontend

# Update environment
nano .env.production
```

```env
REACT_APP_API_URL=https://api.dentaflow.com
REACT_APP_ENV=production
```

```bash
# Build
npm install
npm run build

# Upload to S3
aws s3 sync build/ s3://app.dentaflow.com --delete
```

#### 3.3 Configure CloudFront

1. Create CloudFront distribution for each S3 bucket
2. Set default root object to `index.html`
3. Configure custom error responses (404 → /index.html)
4. Add SSL certificate
5. Set CNAME records

### Option B: Deploy to EC2 with Nginx

#### 3.4 Build and Copy Files

```bash
# Build onboarding
cd /home/ubuntu/dental-clinic-ai/dentaflow-onboarding
pnpm build
sudo cp -r dist /var/www/onboard

# Build dashboard
cd /home/ubuntu/dental-clinic-ai/frontend
npm run build
sudo cp -r build /var/www/app
```

#### 3.5 Configure Nginx

Create `/etc/nginx/sites-available/dentaflow`:

```nginx
# API Backend
server {
    listen 80;
    server_name api.dentaflow.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Onboarding Frontend
server {
    listen 80;
    server_name onboard.dentaflow.com;
    root /var/www/onboard;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}

# Main Dashboard
server {
    listen 80;
    server_name app.dentaflow.com;
    root /var/www/app;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/dentaflow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Part 4: SSL/TLS Configuration

### Using Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificates
sudo certbot --nginx -d api.dentaflow.com
sudo certbot --nginx -d onboard.dentaflow.com
sudo certbot --nginx -d app.dentaflow.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## Part 5: DNS Configuration

Add these DNS records to your domain:

| Type | Name | Value |
|---|---|---|
| A | api | EC2 Elastic IP |
| A | onboard | EC2 Elastic IP or CloudFront |
| A | app | EC2 Elastic IP or CloudFront |
| CNAME | www | dentaflow.com |

---

## Part 6: Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: Web application
6. Authorized redirect URIs:
   - `https://onboard.dentaflow.com/auth/google/callback`
   - `https://app.dentaflow.com/auth/google/callback`
7. Copy Client ID and Client Secret
8. Update `.env` files with these values

---

## Part 7: Monitoring & Logging

### 7.1 Setup CloudWatch (AWS)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### 7.2 Application Logs

```bash
# View backend logs
sudo journalctl -u dentaflow-backend -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## Part 8: Backup Strategy

### 8.1 Database Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup-dentaflow-db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR

pg_dump -h your-rds-endpoint -U dentaflow_user dentaflow | gzip > $BACKUP_DIR/dentaflow_$DATE.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/dentaflow_$DATE.sql.gz s3://dentaflow-backups/

# Keep only last 30 days locally
find $BACKUP_DIR -name "dentaflow_*.sql.gz" -mtime +30 -delete
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-dentaflow-db.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup-dentaflow-db.sh
```

---

## Part 9: Security Checklist

- [ ] All secrets in environment variables (not in code)
- [ ] HTTPS enabled on all domains
- [ ] Database not publicly accessible
- [ ] SSH key-based authentication only
- [ ] Firewall rules configured (UFW or Security Groups)
- [ ] Regular security updates enabled
- [ ] Audit logging enabled
- [ ] Backup strategy in place
- [ ] Monitoring and alerts configured
- [ ] HIPAA compliance measures verified

---

## Part 10: Testing

### 10.1 Health Checks

```bash
# Backend health
curl https://api.dentaflow.com/health

# Onboarding frontend
curl https://onboard.dentaflow.com

# Main dashboard
curl https://app.dentaflow.com
```

### 10.2 End-to-End Test

1. Visit `https://onboard.dentaflow.com`
2. Complete registration flow
3. Verify email
4. Sign BAA
5. Invite team member
6. Login to dashboard at `https://app.dentaflow.com`

---

## Troubleshooting

### Backend not starting

```bash
# Check logs
sudo journalctl -u dentaflow-backend -n 50

# Check if port is in use
sudo lsof -i :8000

# Restart service
sudo systemctl restart dentaflow-backend
```

### Database connection issues

```bash
# Test connection
psql -h your-rds-endpoint -U dentaflow_user -d dentaflow

# Check security group rules
# Ensure EC2 security group can access RDS security group
```

### Frontend not loading

```bash
# Check Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

---

## Support

For deployment issues or questions:
- Email: support@dentaflow.com
- Documentation: https://docs.dentaflow.com

---

**Deployment completed successfully! 🚀**
