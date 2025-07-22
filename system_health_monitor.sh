#!/bin/bash

# === SYSTEM HEALTH MONITOR ===
# Monitors CPU, temperature, disk space, memory, and more
# Sends Slack notifications for alerts

# === CONFIGURATION ===
SLACK_WEBHOOK_URL="${SYSTEM_SLACK_WEBHOOK_URL:-$SLACK_WEBHOOK_URL}"
SLACK_ENABLED="true"
LOG_FILE="/var/log/system-health.log"

# Check for webhook URL from command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --slack-url)
      SLACK_WEBHOOK_URL="$2"
      shift 2
      ;;
    --disable-slack)
      SLACK_ENABLED="false"
      shift
      ;;
    -s|--summary)
      SUMMARY_MODE=true
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# === LOGGING ===
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# === ENHANCED SLACK NOTIFICATION FUNCTION ===
notify_slack() {
    local message="$1"
    local status="$2"
    local color="$3"
    local preview_text="$4"
    
    # Skip if Slack is disabled or webhook URL is not set
    if [ "$SLACK_ENABLED" != "true" ] || [ -z "$SLACK_WEBHOOK_URL" ]; then
        return 0
    fi
    
    # Construct the payload with color coding and preview
    local payload=$(cat <<PAYLOAD
{
  "text": "$preview_text",
  "unfurl_links": true,
  "unfurl_media": true,
  "attachments": [
    {
      "color": "$color",
      "fields": [
        {
          "title": "System Health Alert",
          "value": "$message",
          "short": false
        }
      ],
      "footer": "System Health Monitor",
      "footer_icon": "https://cdn-icons-png.flaticon.com/512/2620/2620669.png",
      "ts": $(date +%s),
      "mrkdwn_in": ["text", "pretext", "fields"]
    }
  ]
}
PAYLOAD
)
    
    # Send the notification
    local response=$(curl -X POST -H 'Content-type: application/json' \
        --data "$payload" \
        "$SLACK_WEBHOOK_URL" \
        --silent --show-error --write-out "%{http_code}" 2>&1)
    
    local curl_status=$?
    local http_code="${response: -3}"
    
    if [ $curl_status -eq 0 ] && [ "$http_code" = "200" ]; then
        log "✅ Slack notification sent successfully"
    else
        log "⚠️  Failed to send Slack notification (curl exit code: $curl_status, HTTP: $http_code)"
        if [ -n "$response" ]; then
          log "   Response: ${response:0:-3}"
        fi
    fi
}

# === SYSTEM HEALTH CHECKS ===

check_disk_usage() {
    # Placeholder for disk usage checking logic
    notify_slack "DISK ALERT" "warning" "warning" "🚨 Disk check required"
}

check_cpu_usage() {
    # Placeholder for CPU usage checking logic
    notify_slack "CPU ALERT" "warning" "warning" "🔥 High CPU load detected"
}

check_memory_usage() {
    # Placeholder for memory usage checking logic
    notify_slack "MEMORY ALERT" "warning" "warning" "🧠 High memory usage"
}

# === HEALTH SUMMARY ===
generate_health_summary() {
    local summary="📊 *Daily System Health Summary*"
    notify_slack "$summary" "info" "good" "📊 Daily Health Summary"
    log "📊 Daily health summary sent"
}

# === MAIN SCRIPT ===
main() {
    log "🏥 Starting system health check..."
    
    # Run all health checks
    check_disk_usage
    check_cpu_usage
    check_memory_usage

    # If this is run with "summary" argument, send daily summary
    if [ "$SUMMARY_MODE" = true ]; then
        generate_health_summary
    fi
    
    log "✅ System health check completed"
}

# Create log file if it doesn't exist
touch "$LOG_FILE"

# Run the main function
main "$@"
