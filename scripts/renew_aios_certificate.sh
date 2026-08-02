#!/bin/sh
set -eu

PROJECT_DIR="/root/hyperliquid-agent-scout"
LOCK_FILE="/tmp/aios-certbot-renewal.lock"

cd "$PROJECT_DIR"

flock -n "$LOCK_FILE" docker run --rm \
  -v "$PROJECT_DIR/certbot/conf:/etc/letsencrypt" \
  -v "$PROJECT_DIR/certbot/www:/var/www/certbot" \
  certbot/certbot renew \
  --webroot \
  --webroot-path /var/www/certbot \
  --quiet

docker compose exec -T nginx nginx -s reload
