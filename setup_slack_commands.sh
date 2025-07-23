#!/bin/bash

# Automated Slack Slash Commands Setup Script for RCON Web Service
# This script generates all necessary slash command configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BLUE}🤖 AUTOMATED SLACK SLASH COMMANDS SETUP${NC}"
    echo -e "${BLUE}======================================================================${NC}"
    echo "This script will generate all the configuration needed for"
    echo "your Slack slash commands to work with the RCON Web Service."
    echo ""
}

get_base_url() {
    # Check for environment variable first
    if [ -n "$RCON_SERVICE_URL" ]; then
        BASE_URL="$RCON_SERVICE_URL"
        echo -e "${GREEN}✅ Using URL from environment: $BASE_URL${NC}"
    else
        echo -e "${YELLOW}🌐 Service URL Configuration${NC}"
        echo "=================================================="
        echo "Enter your RCON Web Service base URL."
        echo "Examples:"
        echo "  • https://your-domain.com"
        echo "  • https://your-server.ngrok.io" 
        echo "  • http://your-ip:5000"
        echo ""
        
        while true; do
            read -p "Enter base URL: " BASE_URL
            if [ -n "$BASE_URL" ]; then
                # Basic URL validation
                if [[ "$BASE_URL" =~ ^https?:// ]]; then
                    break
                else
                    echo -e "${RED}❌ Invalid URL format. Please include http:// or https://${NC}"
                fi
            else
                echo -e "${RED}❌ URL is required.${NC}"
            fi
        done
    fi
    
    # Remove trailing slash
    BASE_URL="${BASE_URL%/}"
}

generate_setup_guide() {
    local base_url="$1"
    
    echo ""
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BLUE}🚀 SLACK SLASH COMMANDS SETUP GUIDE${NC}"
    echo -e "${BLUE}======================================================================${NC}"
    
    echo ""
    echo -e "${YELLOW}📋 Setup Instructions:${NC}"
    echo "1. Go to https://api.slack.com/apps"
    echo "2. Select your Slack app (or create one)"
    echo "3. Navigate to 'Slash Commands' in the left sidebar"
    echo "4. For each command below, click 'Create New Command'"
    echo "5. Copy and paste the configuration details"
    echo "6. Click 'Save' for each command"
    echo "7. Don't forget to reinstall your app to the workspace!"
    
    # Define commands
    declare -a commands=(
        "mc|Execute Minecraft RCON commands on your servers|[server_id] <command> | servers | help | config|/mc list,/mc say Hello players!,/mc servers,/mc help"
        "players|Show online players on your default server||/players"
        "servers|List all available Minecraft servers||/servers"
        "backup|Manage Minecraft server backups|list | create [server_id] | restore [backup_id] | cleanup|/backup list,/backup create,/backup cleanup"
        "status|Show status of all servers and system resources||/status"
        "start|Start a Minecraft server|<server_id>|/start 7eaa7ab6"
        "stop|Stop a Minecraft server|<server_id>|/stop 7eaa7ab6"
        "restart|Restart a Minecraft server|<server_id>|/restart 7eaa7ab6"
        "logs|View recent server logs|<server_id> [lines]|/logs 7eaa7ab6,/logs 7eaa7ab6 50"
    )
    
    local counter=1
    for cmd_info in "${commands[@]}"; do
        IFS='|' read -r name description usage_hint examples <<< "$cmd_info"
        
        echo ""
        echo "=============================================================="
        echo -e "${GREEN}📝 COMMAND $counter: /$name${NC}"
        echo "=============================================================="
        echo "Command: /$name"
        echo "Request URL: $base_url/slack/$name"
        echo "Short Description: $description"
        if [ -n "$usage_hint" ]; then
            echo "Usage Hint: $usage_hint"
        else
            echo "Usage Hint: (leave empty)"
        fi
        echo "Escape channels, users, and links sent to your app: ✅ (checked)"
        
        echo ""
        echo "Examples:"
        IFS=',' read -ra example_array <<< "$examples"
        for example in "${example_array[@]}"; do
            echo "  • $example"
        done
        
        ((counter++))
    done
    
    # Quick reference table
    echo ""
    echo "=============================================================="
    echo -e "${GREEN}🎯 QUICK COPY-PASTE SUMMARY${NC}"
    echo "=============================================================="
    printf "| %-10s | %-35s |\n" "Command" "URL"
    printf "| %-10s | %-35s |\n" "----------" "-----------------------------------"
    
    for cmd_info in "${commands[@]}"; do
        IFS='|' read -r name description usage_hint examples <<< "$cmd_info"
        printf "| /%-9s | %-35s |\n" "$name" "$base_url/slack/$name"
    done
}

generate_test_commands() {
    local base_url="$1"
    
    echo ""
    echo "=============================================================="
    echo -e "${YELLOW}🧪 TEST COMMANDS (Optional)${NC}"
    echo "=============================================================="
    echo "You can test these endpoints manually with curl:"
    echo ""
    
    echo "# Test /mc"
    echo "curl -X POST $base_url/slack/mc \\"
    echo "  -d 'user_name=testuser&text=servers'"
    echo ""
    
    echo "# Test /players"
    echo "curl -X POST $base_url/slack/players \\"
    echo "  -d 'user_name=testuser'"
    echo ""
    
    echo "# Test /servers"  
    echo "curl -X POST $base_url/slack/servers \\"
    echo "  -d 'user_name=testuser'"
    echo ""
    
    echo "# Test /status"
    echo "curl -X POST $base_url/slack/status \\"
    echo "  -d 'user_name=testuser'"
    echo ""
    
    echo "# Test /backup"
    echo "curl -X POST $base_url/slack/backup \\"
    echo "  -d 'user_name=testuser&text=list'"
    echo ""
}

save_config_file() {
    local base_url="$1"
    local config_file="slack_commands_config.txt"
    
    cat > "$config_file" << EOCONFIG
# Slack Slash Commands Configuration
# Generated on: $(date -Iseconds)
# Base URL: $base_url

# Command configurations for Slack App setup:

## /mc  
Command: /mc
Request URL: $base_url/slack/mc
Short Description: Execute Minecraft RCON commands on your servers
Usage Hint: [server_id] <command> | servers | help | config

## /players
Command: /players
Request URL: $base_url/slack/players
Short Description: Show online players on your default server
Usage Hint: 

## /servers
Command: /servers
Request URL: $base_url/slack/servers
Short Description: List all available Minecraft servers
Usage Hint: 

## /backup
Command: /backup
Request URL: $base_url/slack/backup
Short Description: Manage Minecraft server backups
Usage Hint: list | create [server_id] | restore [backup_id] | cleanup

## /status
Command: /status
Request URL: $base_url/slack/status
Short Description: Show status of all servers and system resources
Usage Hint: 

## /start
Command: /start
Request URL: $base_url/slack/start
Short Description: Start a Minecraft server
Usage Hint: <server_id>

## /stop
Command: /stop
Request URL: $base_url/slack/stop
Short Description: Stop a Minecraft server
Usage Hint: <server_id>

## /restart
Command: /restart
Request URL: $base_url/slack/restart
Short Description: Restart a Minecraft server
Usage Hint: <server_id>

## /logs
Command: /logs
Request URL: $base_url/slack/logs
Short Description: View recent server logs
Usage Hint: <server_id> [lines]
EOCONFIG

    echo ""
    echo -e "${GREEN}📄 Configuration saved to: $config_file${NC}"
    echo "$config_file"
}

main() {
    print_header
    
    # Get base URL
    get_base_url
    
    # Generate setup guide
    generate_setup_guide "$BASE_URL"
    
    # Generate test commands
    generate_test_commands "$BASE_URL"
    
    # Save config file
    config_file=$(save_config_file "$BASE_URL")
    
    echo ""
    echo -e "${GREEN}✅ SETUP COMPLETE!${NC}"
    echo "📋 Total commands to configure: 9"
    echo "📄 Configuration saved to: $config_file"
    echo "🌐 Service URL: $BASE_URL"
    echo ""
    echo "Next steps:"
    echo "1. Copy the command configurations above into your Slack app"
    echo "2. Test the commands in your Slack workspace"
    echo "3. Run the curl test commands if needed"
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${RED}❌ Setup cancelled by user${NC}"; exit 1' INT

# Run main function
main "$@"
