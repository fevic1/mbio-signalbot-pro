#!/bin/bash
# Secure authentication test - reads credentials from environment

# Load credentials from .env or prompt user
if [ -f .env ]; then
    source .env
    EMAIL="${MBIO_ADMIN_EMAIL:-}"
    PASSWORD="${MBIO_ADMIN_PASSWORD:-}"
else
    echo "Enter admin email:"
    read -s EMAIL
    echo "Enter admin password:"
    read -s PASSWORD
fi

if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ]; then
    echo "❌ Credentials not set. Please configure .env or provide manually."
    exit 1
fi

echo "Testing authentication..."
curl -s -c /tmp/cookies.txt -X POST http://localhost/api/dashboard/auth/login \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" | python3 -m json.tool

echo ""
echo "✅ Authentication test complete (credentials not exposed in logs)"
