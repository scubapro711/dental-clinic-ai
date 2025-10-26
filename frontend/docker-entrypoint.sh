#!/bin/sh
set -e

# Replace ${PORT} in nginx config template with actual PORT value
echo "Configuring nginx to listen on port ${PORT}..."
envsubst '${PORT}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Verify the configuration
echo "Nginx configuration:"
cat /etc/nginx/conf.d/default.conf | head -10

# Test nginx configuration
nginx -t

# Execute the main command (nginx)
exec "$@"

