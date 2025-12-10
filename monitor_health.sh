#!/bin/bash
# Health monitoring script for CRM Backend
# Checks PM2 status, Nginx, and backend health every 30 seconds

LOG_FILE="/var/log/crm-health-monitor.log"
BACKEND_URL="http://localhost:3001/api/health"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_pm2() {
    STATUS=$(pm2 jlist | jq -r '.[0].pm2_env.status' 2>/dev/null)
    if [ "$STATUS" != "online" ]; then
        log "❌ PM2 Backend status: $STATUS - RESTARTING..."
        pm2 restart crm-backend
        return 1
    fi
    return 0
}

check_backend() {
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$BACKEND_URL" 2>/dev/null)
    if [ "$HTTP_CODE" != "200" ]; then
        log "❌ Backend health check failed (HTTP $HTTP_CODE) - RESTARTING..."
        pm2 restart crm-backend
        return 1
    fi
    return 0
}

check_nginx() {
    if ! systemctl is-active --quiet nginx; then
        log "❌ Nginx is not running - STARTING..."
        sudo systemctl start nginx
        return 1
    fi
    return 0
}

check_memory() {
    PM2_MEM=$(pm2 jlist | jq -r '.[0].monit.memory' 2>/dev/null)
    PM2_MEM_MB=$((PM2_MEM / 1024 / 1024))

    if [ "$PM2_MEM_MB" -gt 450 ]; then
        log "⚠️  High memory usage: ${PM2_MEM_MB}MB - RESTARTING..."
        pm2 restart crm-backend
        return 1
    fi
    return 0
}

# Main monitoring loop
log "🚀 CRM Health Monitor started"

while true; do
    ALL_OK=true

    if ! check_pm2; then ALL_OK=false; fi
    if ! check_backend; then ALL_OK=false; fi
    if ! check_nginx; then ALL_OK=false; fi
    if ! check_memory; then ALL_OK=false; fi

    if [ "$ALL_OK" = true ]; then
        log "✅ All systems healthy"
    fi

    sleep 30
done
