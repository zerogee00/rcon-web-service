#!/bin/bash

# Script to configure Slack webhook URL for backup and health monitoring scripts

CONFIG_FILE="/root/rcon-web-service/.env"
SLACK_URL="$1"

if [ -z "$SLACK_URL" ]; then
    echo "Usage: $0 <slack_webhook_url>"
    echo ""
    echo "Example:"
    echo "  $0 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'"
    echo ""
    echo "This will create/update the .env file with:"
    echo "  SLACK_WEBHOOK_URL=your_webhook_url"
    echo ""
    echo "Current configuration:"
    if [ -f "$CONFIG_FILE" ]; then
        grep "SLACK_WEBHOOK_URL" "$CONFIG_FILE" 2>/dev/null || echo "  No Slack URL configured"
    else
        echo "  No configuration file exists"
    fi
    exit 1
fi

# Create or update .env file
if [ -f "$CONFIG_FILE" ]; then
    # Update existing file
    if grep -q "SLACK_WEBHOOK_URL" "$CONFIG_FILE"; then
        sed -i "s|^SLACK_WEBHOOK_URL=.*|SLACK_WEBHOOK_URL=\"$SLACK_URL\"|" "$CONFIG_FILE"
        echo "✅ Updated existing Slack webhook URL in $CONFIG_FILE"
    else
        echo "SLACK_WEBHOOK_URL=\"$SLACK_URL\"" >> "$CONFIG_FILE"
        echo "✅ Added Slack webhook URL to existing $CONFIG_FILE"
    fi
else
    # Create new file
    echo "SLACK_WEBHOOK_URL=\"$SLACK_URL\"" > "$CONFIG_FILE"
    echo "✅ Created $CONFIG_FILE with Slack webhook URL"
fi

# Test the webhook URL
echo ""
echo "🧪 Testing webhook URL..."
response=$(curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"🧪 Test notification from backup system configuration"}' \
    "$SLACK_URL" \
    --silent --show-error --write-out "%{http_code}" 2>&1)

curl_status=$?
http_code="${response: -3}"

if [ $curl_status -eq 0 ] && [ "$http_code" = "200" ]; then
    echo "✅ Test notification sent successfully!"
    echo "   Check your Slack channel to confirm receipt"
else
    echo "❌ Test notification failed (curl exit code: $curl_status, HTTP: $http_code)"
    if [ -n "$response" ]; then
        echo "   Response: ${response:0:-3}"
    fi
fi

echo ""
echo "📋 Next steps:"
echo "  1. Update your crontab to use environment variables:"
echo "     */15 * * * * cd /root/rcon-web-service && source .env && ./system_health_monitor.sh >> /var/log/system-health.log 2>&1"
echo "     0 */4 * * * cd /root/rcon-web-service && source .env && ./backup.sh >> /var/log/minecraft-backup.log 2>&1"
echo ""
echo "  2. Or pass the URL directly:"
echo "     ./backup.sh --slack-url \"$SLACK_URL\""
echo "     ./system_health_monitor.sh --slack-url \"$SLACK_URL\""
