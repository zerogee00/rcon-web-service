#!/bin/bash

# Test the improved notification format
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
SLACK_ENABLED="true"

# Test notification function with improved format
notify_slack() {
  local message="$1"
  local status="$2"
  local color="$3"
  
  # Skip if Slack is disabled or webhook URL is not set
  if [ "$SLACK_ENABLED" != "true" ] || [ -z "$SLACK_WEBHOOK_URL" ]; then
    return 0
  fi
  
  # Construct the payload with better formatting for previews
  local payload=$(cat <<PAYLOAD
{
  "text": "$message",
  "attachments": [
    {
      "color": "$color",
      "fields": [
        {
          "title": "Minecraft Backup Status",
          "value": "$message",
          "short": false
        }
      ],
      "footer": "PufferPanel Backup System",
      "ts": $(date +%s)
    }
  ]
}
PAYLOAD
)
  
  # Send the notification
  curl -X POST -H 'Content-type: application/json' \
    --data "$payload" \
    "$SLACK_WEBHOOK_URL" \
    --silent --show-error --fail > /dev/null 2>&1
  
  local curl_status=$?
  if [ $curl_status -ne 0 ]; then
    echo "⚠️  Failed to send Slack notification (curl exit code: $curl_status)"
  else
    echo "✅ Notification sent successfully"
  fi
}

# Send test notification
notify_slack "🧪 **Test Notification with Preview**

This is a test of the improved Slack notification format that should show preview content properly!" "success" "good"
