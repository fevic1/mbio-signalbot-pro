#!/bin/bash
cd /root/hyperliquid-agent-scout
docker compose exec -T mbio-bot python /app/evaluator.py >> /var/log/evaluator.log 2>&1
