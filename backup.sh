#!/bin/bash

# ============================================================================
# StoreHub Database & Media Backup Script
# ============================================================================
# This script creates backups of database and media files
# Usage: bash backup.sh
# For cron job: 0 2 * * * cd /path/to/project && bash backup.sh
# ============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "=================================================="
echo "Starting Backup Process"
echo "Timestamp: $TIMESTAMP"
echo "=================================================="

# Load environment
export $(cat "$PROJECT_DIR/.env" | grep -v '#' | xargs) 2>/dev/null || true

# ============================================================================
# Database Backup
# ============================================================================

echo "[1/3] Backing up PostgreSQL database..."

if [ "$USE_POSTGRESQL" = "True" ]; then
    BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
    
    # Using Docker
    docker-compose exec -T postgres pg_dump \
        -U "$DB_USER" \
        -h localhost \
        "$DB_NAME" > "$BACKUP_FILE"
    
    # Compress backup
    gzip "$BACKUP_FILE"
    BACKUP_FILE="$BACKUP_FILE.gz"
    
    echo "✓ Database backed up: $BACKUP_FILE"
else
    # SQLite backup
    BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3"
    cp "$PROJECT_DIR/db.sqlite3" "$BACKUP_FILE"
    gzip "$BACKUP_FILE"
    BACKUP_FILE="$BACKUP_FILE.gz"
    
    echo "✓ SQLite database backed up: $BACKUP_FILE"
fi

# ============================================================================
# Media Files Backup
# ============================================================================

echo "[2/3] Backing up media files..."

if [ -d "$PROJECT_DIR/media" ] && [ "$(ls -A $PROJECT_DIR/media)" ]; then
    MEDIA_BACKUP="$BACKUP_DIR/media_$TIMESTAMP.tar.gz"
    tar -czf "$MEDIA_BACKUP" -C "$PROJECT_DIR" media/
    echo "✓ Media files backed up: $MEDIA_BACKUP"
else
    echo "✓ No media files to backup"
fi

# ============================================================================
# Static Files Backup (optional, usually regenerated)
# ============================================================================

echo "[3/3] Backing up static files..."

if [ -d "$PROJECT_DIR/staticfiles" ]; then
    STATIC_BACKUP="$BACKUP_DIR/static_$TIMESTAMP.tar.gz"
    tar -czf "$STATIC_BACKUP" -C "$PROJECT_DIR" staticfiles/
    echo "✓ Static files backed up: $STATIC_BACKUP"
fi

# ============================================================================
# Cleanup Old Backups
# ============================================================================

echo "Cleaning up old backups (keeping last 30 days)..."

find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "✓ Old backups cleaned up"

# ============================================================================
# Backup Summary
# ============================================================================

echo ""
echo "=================================================="
echo "Backup Summary"
echo "=================================================="
ls -lh "$BACKUP_DIR"/*.gz | tail -5
echo ""
echo "Total backup size:"
du -sh "$BACKUP_DIR"
echo ""
echo "Oldest backup (will be deleted if > 30 days):"
ls -lhtr "$BACKUP_DIR"/*.gz | head -1

# ============================================================================
# Optional: Upload to S3
# ============================================================================

if command -v aws &> /dev/null && [ ! -z "$AWS_S3_BUCKET" ]; then
    echo "Uploading backups to S3..."
    aws s3 sync "$BACKUP_DIR" "s3://$AWS_S3_BUCKET/backups/" \
        --exclude "*" \
        --include "*.gz" \
        --delete
    echo "✓ Backups uploaded to S3"
fi

echo ""
echo "Backup completed at $(date)"
echo ""
