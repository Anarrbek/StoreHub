#!/bin/bash

# ============================================================================
# SSL/HTTPS Certificate Setup with Let's Encrypt
# ============================================================================
# This script configures automatic SSL certificates using Let's Encrypt
# ============================================================================

set -e

DOMAIN=${1:-yourdomain.com}
EMAIL=${2:-admin@yourdomain.com}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$DOMAIN" = "yourdomain.com" ]; then
    echo "ERROR: Please provide your domain name"
    echo "Usage: bash setup-ssl.sh yourdomain.com admin@yourdomain.com"
    exit 1
fi

echo "=================================================="
echo "Setting up SSL Certificate with Let's Encrypt"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo "=================================================="

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

echo "[1/5] Stopping Nginx temporarily..."
docker-compose stop nginx || systemctl stop nginx || true

echo "[2/5] Requesting SSL certificate..."
certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo "[3/5] Creating certificate bundle..."
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
cat "$CERT_DIR/fullchain.pem" "$CERT_DIR/privkey.pem" > "$CERT_DIR/cert-bundle.pem"

echo "[4/5] Updating Nginx configuration..."
# Create new Nginx config with SSL
cat > "$PROJECT_DIR/nginx-ssl.conf" << 'EOF'
upstream django {
    server web:8000;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json;
    gzip_min_length 1000;

    # Client max body size
    client_max_body_size 100M;

    # Static files caching
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files caching
    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Proxy to Django
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Deny access to backup files
    location ~ \.(bak|backup|old|tmp)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

# Replace domain placeholder
sed -i "s/yourdomain.com/$DOMAIN/g" "$PROJECT_DIR/nginx-ssl.conf"

echo "[5/5] Starting services with SSL..."
docker-compose up -d

echo ""
echo "=================================================="
echo "SSL Certificate Setup Complete!"
echo "=================================================="
echo ""
echo "Certificate Details:"
certbot certificates

echo ""
echo "IMPORTANT: The SSL certificate will auto-renew."
echo "Test renewal with: certbot renew --dry-run"
echo ""
echo "Access your site at: https://$DOMAIN"
echo ""

# Run security test
echo "Running SSL test..."
if command -v ssllabs-cli &> /dev/null; then
    ssllabs-cli --quiet https://$DOMAIN
else
    echo "Visit https://www.ssllabs.com/ssltest/ to test your SSL configuration"
fi
