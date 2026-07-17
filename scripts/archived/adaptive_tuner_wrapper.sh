#!/bin/bash
cd /root/hyperliquid-agent-scout
docker compose exec -T mbio-bot python /app/adaptive_tuner.py >> /var/log/adaptive_tuner.log 2>&1
