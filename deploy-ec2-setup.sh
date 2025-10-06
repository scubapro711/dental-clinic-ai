#!/bin/bash
# EC2 Setup Script for Odoo 19

set -e

echo "🚀 Starting Odoo 19 deployment setup..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "✅ Docker installed successfully"
docker --version
docker-compose --version

echo "✅ Setup complete! Ready for Odoo deployment."
