#!/bin/bash

# ============================================================================
# StoreHub Production Deployment Script
# ============================================================================
# Usage: bash deploy.sh [environment]
# Example: bash deploy.sh production
# ============================================================================

set -e

ENVIRONMENT=${1:-production}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================================="
echo "StoreHub Production Deployment"
echo "Environment: $ENVIRONMENT"
echo "=================================================="

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.production to .env and configure it."
    exit 1
fi

# Load environment variables
export $(cat "$PROJECT_DIR/.env" | grep -v '#' | xargs)

echo "[1/10] Checking system requirements..."
# Check for required commands
for cmd in docker docker-compose python pip; do
    if ! command -v $cmd &> /dev/null; then
        echo "ERROR: $cmd is not installed!"
        exit 1
    fi
done

echo "[2/10] Pulling latest changes from git..."
cd "$PROJECT_DIR"
git pull origin main || true

echo "[3/10] Installing Python dependencies..."
pip install -r requirements.txt

echo "[4/10] Running security checks..."
python manage.py check --deploy

echo "[5/10] Building Docker images..."
docker-compose build

echo "[6/10] Starting services..."
docker-compose up -d

echo "[7/10] Running database migrations..."
sleep 3  # Wait for database to be ready
docker-compose exec -T web python manage.py migrate

echo "[8/10] Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo "[9/10] Creating cache tables..."
docker-compose exec -T web python manage.py createcachetable || true

echo "[10/10] Running health checks..."
# Check if web service is running
if docker-compose ps web | grep -q "Up"; then
    echo "✓ Web service is running"
else
    echo "✗ Web service failed to start"
    docker-compose logs web
    exit 1
fi

# Check if database is accessible
docker-compose exec -T web python manage.py dbshell <<EOF
SELECT 1;
EOF

echo "✓ Database connection successful"

echo ""
echo "=================================================="
echo "Deployment Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Create superuser: docker-compose exec web python manage.py createsuperuser"
echo "2. Check logs: docker-compose logs -f web"
echo "3. Access admin: https://yourdomain.com/admin"
echo "4. Configure SSL certificates with Let's Encrypt"
echo ""
echo "Service Status:"
docker-compose ps
echo ""
