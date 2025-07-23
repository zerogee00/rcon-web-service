#!/bin/bash

# Automated Slack API Configuration Script using curl
# This script uses curl to automatically create slash commands via Slack API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BLUE}🤖 AUTOMATED SLACK API CONFIGURATION (CURL VERSION)${NC}"
    echo -e "${BLUE}======================================================================${NC}"
    echo "This script will automatically configure your slash commands"
    echo "using the Slack API via curl commands."
    echo ""
}

get_slack_token() {
    # Check for environment variable first
    if [ -n "$SLACK_BOT_TOKEN" ]; then
        SLACK_TOKEN="$SLACK_BOT_TOKEN"
        echo -e "${GREEN}✅ Using token from environment${NC}"
    else
        echo -e "${YELLOW}🔑 Slack Token Required${NC}"
        echo "=================================================="
        echo "You need a Slack Bot Token with the following scopes:"
        echo "  • commands:write"
        echo "  • app_mentions:read" 
        echo "  • chat:write"
        echo ""
        echo "Get your token from: https://api.slack.com/apps"
        echo "Go to: OAuth & Permissions > Bot User OAuth Token"
        echo ""
        
        while true; do
            read -p "Enter your Slack Bot Token (starts with xoxb-): " SLACK_TOKEN
            if [[ "$SLACK_TOKEN" =~ ^xoxb- ]]; then
                break
            else
                echo -e "${RED}❌ Invalid token format. Should start with 'xoxb-'${NC}"
            fi
        done
    fi
}

get_base_url() {
    BASE_URL="${RCON_SERVICE_URL:-https://slackbot.doktorodd.com}"
    BASE_URL="${BASE_URL%/}"  # Remove trailing slash
    echo -e "${GREEN}🌐 Using base URL: $BASE_URL${NC}"
}

test_slack_connection() {
    local token="$1"
    
    echo "🔗 Testing Slack connection..."
    
    response=$(curl -s -X GET "https://slack.com/api/auth.test" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    # Check if response contains "ok":true
    if echo "$response" | grep -q '"ok":true'; then
        user=$(echo "$response" | grep -o '"user":"[^"]*"' | cut -d'"' -f4)
        team=$(echo "$response" | grep -o '"team":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}✅ Connected to Slack as: $user${NC}"
        echo -e "${GREEN}📱 Team: $team${NC}"
        return 0
    else
        error=$(echo "$response" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
        echo -e "${RED}❌ Slack API Error: $error${NC}"
        return 1
    fi
}

create_slash_command() {
    local token="$1"
    local command="$2"
    local url="$3"  
    local description="$4"
    local usage_hint="$5"
    
    local payload=$(cat << EOL
{
    "command": "$command",
    "url": "$url",
    "description": "$description",
    "usage_hint": "$usage_hint",
    "should_escape": true
}
EOL
)
    
    response=$(curl -s -X POST "https://slack.com/api/apps.commands.create" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    if echo "$response" | grep -q '"ok":true'; then
        echo -e "${GREEN}✅ Created /$command${NC}"
        return 0
    else
        error=$(echo "$response" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
        echo -e "${RED}❌ Failed to create /$command: $error${NC}"
        return 1
    fi
}

list_existing_commands() {
    local token="$1"
    
    echo "📋 Checking existing commands..."
    
    response=$(curl -s -X GET "https://slack.com/api/apps.commands.list" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    if echo "$response" | grep -q '"ok":true'; then
        # Extract command names (basic parsing)
        existing_commands=$(echo "$response" | grep -o '"command":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$existing_commands" ]; then
            echo "Found existing commands:"
            echo "$existing_commands" | while read cmd; do
                echo "  • /$cmd"
            done
            echo ""
            echo -e "${YELLOW}⚠️  Note: This script will try to create new commands.${NC}"
            echo -e "${YELLOW}   You may get 'command already exists' errors, which is normal.${NC}"
        else
            echo "No existing commands found."
        fi
    else
        echo -e "${YELLOW}⚠️  Could not list existing commands, proceeding anyway...${NC}"
    fi
    echo ""
}

configure_commands() {
    local token="$1"
    local base_url="$2"
    
    echo "⚙️  Configuring slash commands..."
    
    local success_count=0
    local error_count=0
    
    # Define commands array
    declare -a commands=(
        "mc|$base_url/slack/mc|Execute Minecraft RCON commands on your servers|[server_id] <command> | servers | help | config"
        "players|$base_url/slack/players|Show online players on your default server|"
        "servers|$base_url/slack/servers|List all available Minecraft servers|"
        "backup|$base_url/slack/backup|Manage Minecraft server backups|list | create [server_id] | restore [backup_id] | cleanup"
        "status|$base_url/slack/status|Show status of all Minecraft servers and system resources|"
        "start|$base_url/slack/start|Start a Minecraft server|<server_id>"
        "stop|$base_url/slack/stop|Stop a Minecraft server|<server_id>"
        "restart|$base_url/slack/restart|Restart a Minecraft server|<server_id>"
        "logs|$base_url/slack/logs|View recent server logs|<server_id> [lines]"
    )
    
    for cmd_info in "${commands[@]}"; do
        IFS='|' read -r name url description usage_hint <<< "$cmd_info"
        
        if create_slash_command "$token" "$name" "$url" "$description" "$usage_hint"; then
            ((success_count++))
        else
            ((error_count++))
        fi
    done
    
    echo ""
    echo -e "${BLUE}📊 CONFIGURATION SUMMARY${NC}"
    echo "=================================================="
    echo -e "${GREEN}✅ Successfully configured: $success_count commands${NC}"
    if [ $error_count -gt 0 ]; then
        echo -e "${RED}❌ Failed to configure: $error_count commands${NC}"
    fi
    
    if [ $success_count -gt 0 ]; then
        echo ""
        echo -e "${GREEN}🎉 NEXT STEPS${NC}"
        echo "=================================================="
        echo "1. Your slash commands are now configured!"
        echo "2. Try them in your Slack workspace:"
        echo "   • /mc servers"
        echo "   • /players"
        echo "   • /status"
        echo "3. If commands don't appear, reinstall your app to the workspace"
    fi
    
    if [ $error_count -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  TROUBLESHOOTING${NC}"
        echo "=================================================="
        echo "Some commands failed to configure. Common issues:"
        echo "• Token doesn't have 'commands:write' scope"
        echo "• App is not installed to workspace"
        echo "• Command name conflicts (commands may already exist)"
        echo "• Rate limiting"
    fi
}

main() {
    print_header
    
    # Get Slack token
    get_slack_token
    
    # Get base URL
    get_base_url
    echo ""
    
    # Test connection
    if ! test_slack_connection "$SLACK_TOKEN"; then
        echo -e "${RED}❌ Failed to connect to Slack API${NC}"
        exit 1
    fi
    echo ""
    
    # List existing commands
    list_existing_commands "$SLACK_TOKEN"
    
    # Configure commands
    configure_commands "$SLACK_TOKEN" "$BASE_URL"
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${RED}❌ Configuration cancelled by user${NC}"; exit 1' INT

# Run main function
main "$@"
