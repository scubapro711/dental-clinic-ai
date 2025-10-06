#!/bin/bash

###############################################################################
# Dental Clinic SaaS - SSL/TLS Setup Script
# This script sets up Nginx with Let's Encrypt SSL/TLS for Odoo
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Dental Clinic SaaS - SSL/TLS Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Get domain name from user
echo -e "${YELLOW}Enter your domain name (e.g., dental.example.com):${NC}"
read -p "Domain: " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}Domain name is required!${NC}"
    exit 1
fi

echo -e "${YELLOW}Enter your email for Let's Encrypt notifications:${NC}"
read -p "Email: " EMAIL

if [ -z "$EMAIL" ]; then
    echo -e "${RED}Email is required!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Configuration:${NC}"
echo -e "  Domain: ${YELLOW}$DOMAIN${NC}"
echo -e "  Email: ${YELLOW}$EMAIL${NC}"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Update system
echo -e "${GREEN}[1/7] Updating system packages...${NC}"
apt-get update -qq

# Install Nginx
echo -e "${GREEN}[2/7] Installing Nginx...${NC}"
apt-get install -y nginx

# Install Certbot
echo -e "${GREEN}[3/7] Installing Certbot...${NC}"
apt-get install -y certbot python3-certbot-nginx

# Stop Odoo temporarily
echo -e "${GREEN}[4/7] Stopping Odoo temporarily...${NC}"
systemctl stop odoo || true

# Configure Nginx
echo -e "${GREEN}[5/7] Configuring Nginx...${NC}"

cat > /etc/nginx/sites-available/odoo << EOF
# Dental Clinic Odoo - Nginx Configuration

# Upstream Odoo
upstream odoo {
    server 127.0.0.1:8069;
}

# Upstream Odoo Longpolling
upstream odoochat {
    server 127.0.0.1:8072;
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name $DOMAIN;
    
    # Allow Certbot validation
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL certificates (will be configured by Certbot)
    # ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy settings
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    proxy_set_header X-Forwarded-Host \$host;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_set_header X-Real-IP \$remote_addr;

    # Log files
    access_log /var/log/nginx/odoo-access.log;
    error_log /var/log/nginx/odoo-error.log;

    # Increase proxy buffer size
    proxy_buffers 16 64k;
    proxy_buffer_size 128k;

    # Force timeouts if the backend dies
    proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;

    # Enable data compression
    gzip on;
    gzip_min_length 1100;
    gzip_buffers 4 32k;
    gzip_types text/css text/less text/plain text/xml application/xml application/json application/javascript application/pdf image/svg+xml;
    gzip_vary on;

    # Odoo web client
    location / {
        proxy_pass http://odoo;
        proxy_redirect off;
    }

    # Odoo longpolling
    location /longpolling {
        proxy_pass http://odoochat;
    }

    # Cache static files
    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }

    # Common static files
    location ~* /web/content/ {
        proxy_pass http://odoo;
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/odoo
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo -e "${GREEN}[6/7] Testing Nginx configuration...${NC}"
nginx -t

# Restart Nginx
systemctl restart nginx

# Get SSL certificate
echo -e "${GREEN}[7/7] Obtaining SSL certificate from Let's Encrypt...${NC}"
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect

# Start Odoo
echo -e "${GREEN}Starting Odoo...${NC}"
systemctl start odoo

# Enable services to start on boot
systemctl enable nginx
systemctl enable odoo

# Setup auto-renewal
echo -e "${GREEN}Setting up SSL certificate auto-renewal...${NC}"
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ SSL/TLS Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Your Odoo instance is now accessible at:${NC}"
echo -e "  ${YELLOW}https://$DOMAIN${NC}"
echo ""
echo -e "${GREEN}SSL Certificate:${NC}"
echo -e "  Issuer: Let's Encrypt"
echo -e "  Auto-renewal: Enabled"
echo -e "  Renewal check: Twice daily"
echo ""
echo -e "${GREEN}Security Features Enabled:${NC}"
echo -e "  ✅ TLS 1.2/1.3"
echo -e "  ✅ HTTP -> HTTPS redirect"
echo -e "  ✅ HSTS enabled"
echo -e "  ✅ Security headers"
echo -e "  ✅ Gzip compression"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Update DNS: Point $DOMAIN to $(curl -s ifconfig.me)"
echo -e "  2. Test: https://$DOMAIN"
echo -e "  3. Configure Odoo web.base.url"
echo ""
