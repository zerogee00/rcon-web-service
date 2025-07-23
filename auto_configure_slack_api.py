#!/usr/bin/env python3
"""
Automated Slack API Configuration Script
This script uses the Slack API to automatically create slash commands
"""

import json
import sys
import os
import requests
from urllib.parse import urljoin

def get_slack_token():
    """Get Slack token from user or environment"""
    token = os.environ.get('SLACK_BOT_TOKEN')
    
    if not token:
        print("🔑 **Slack Token Required**")
        print("=" * 50)
        print("You need a Slack Bot Token with the following scopes:")
        print("  • commands:write")
        print("  • app_mentions:read") 
        print("  • chat:write")
        print("")
        print("Get your token from: https://api.slack.com/apps")
        print("Go to: OAuth & Permissions > Bot User OAuth Token")
        print("")
        
        while True:
            token = input("Enter your Slack Bot Token (starts with xoxb-): ").strip()
            if token.startswith('xoxb-'):
                break
            else:
                print("❌ Invalid token format. Should start with 'xoxb-'")
    
    return token

def get_base_url():
    """Get base URL for the service"""
    base_url = os.environ.get('RCON_SERVICE_URL', 'https://slackbot.doktorodd.com')
    return base_url.rstrip('/')

def test_slack_connection(token):
    """Test if the Slack token is valid"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get('https://slack.com/api/auth.test', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            print(f"✅ Connected to Slack as: {data.get('user')}")
            print(f"📱 Team: {data.get('team')}")
            return True
        else:
            print(f"❌ Slack API Error: {data.get('error')}")
            return False
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        return False

def create_slash_command(token, command_data):
    """Create a single slash command"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Slack API endpoint for creating slash commands
    url = 'https://slack.com/api/apps.commands.create'
    
    response = requests.post(url, headers=headers, json=command_data)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            return True, f"✅ Created /{command_data['command']}"
        else:
            return False, f"❌ Failed to create /{command_data['command']}: {data.get('error')}"
    else:
        return False, f"❌ HTTP Error {response.status_code} for /{command_data['command']}"

def update_slash_command(token, command_id, command_data):
    """Update an existing slash command"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Add command ID to the data
    command_data['command_id'] = command_id
    
    # Slack API endpoint for updating slash commands
    url = 'https://slack.com/api/apps.commands.update'
    
    response = requests.post(url, headers=headers, json=command_data)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            return True, f"✅ Updated /{command_data['command']}"
        else:
            return False, f"❌ Failed to update /{command_data['command']}: {data.get('error')}"
    else:
        return False, f"❌ HTTP Error {response.status_code} for /{command_data['command']}"

def list_existing_commands(token):
    """List existing slash commands"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    url = 'https://slack.com/api/apps.commands.list'
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            commands = data.get('commands', [])
            existing = {}
            for cmd in commands:
                existing[cmd['command']] = cmd['id']
            return existing
        else:
            print(f"❌ Failed to list commands: {data.get('error')}")
            return {}
    else:
        print(f"❌ HTTP Error {response.status_code} when listing commands")
        return {}

def generate_command_configs(base_url):
    """Generate command configurations"""
    
    commands = [
        {
            'command': 'mc',
            'url': f'{base_url}/slack/mc',
            'description': 'Execute Minecraft RCON commands on your servers',
            'usage_hint': '[server_id] <command> | servers | help | config',
            'should_escape': True
        },
        {
            'command': 'players',
            'url': f'{base_url}/slack/players',
            'description': 'Show online players on your default server',
            'usage_hint': '',
            'should_escape': True
        },
        {
            'command': 'servers',
            'url': f'{base_url}/slack/servers',
            'description': 'List all available Minecraft servers',
            'usage_hint': '',
            'should_escape': True
        },
        {
            'command': 'backup',
            'url': f'{base_url}/slack/backup',
            'description': 'Manage Minecraft server backups',
            'usage_hint': 'list | create [server_id] | restore [backup_id] | cleanup',
            'should_escape': True
        },
        {
            'command': 'status',
            'url': f'{base_url}/slack/status',
            'description': 'Show status of all Minecraft servers and system resources',
            'usage_hint': '',
            'should_escape': True
        },
        {
            'command': 'start',
            'url': f'{base_url}/slack/start',
            'description': 'Start a Minecraft server',
            'usage_hint': '<server_id>',
            'should_escape': True
        },
        {
            'command': 'stop',
            'url': f'{base_url}/slack/stop',
            'description': 'Stop a Minecraft server',
            'usage_hint': '<server_id>',
            'should_escape': True
        },
        {
            'command': 'restart',
            'url': f'{base_url}/slack/restart',
            'description': 'Restart a Minecraft server',
            'usage_hint': '<server_id>',
            'should_escape': True
        },
        {
            'command': 'logs',
            'url': f'{base_url}/slack/logs',
            'description': 'View recent server logs',
            'usage_hint': '<server_id> [lines]',
            'should_escape': True
        }
    ]
    
    return commands

def main():
    """Main execution function"""
    
    print("🤖 **AUTOMATED SLACK API CONFIGURATION**")
    print("=" * 80)
    print("This script will automatically configure your slash commands")
    print("using the Slack API instead of manual web interface setup.")
    print()
    
    try:
        # Get Slack token
        token = get_slack_token()
        
        # Get base URL
        base_url = get_base_url()
        print(f"🌐 Using base URL: {base_url}")
        print()
        
        # Test connection
        print("🔗 Testing Slack connection...")
        if not test_slack_connection(token):
            print("❌ Failed to connect to Slack API")
            sys.exit(1)
        print()
        
        # List existing commands
        print("📋 Checking existing commands...")
        existing_commands = list_existing_commands(token)
        if existing_commands:
            print(f"Found {len(existing_commands)} existing commands:")
            for cmd_name in existing_commands.keys():
                print(f"  • /{cmd_name}")
        else:
            print("No existing commands found.")
        print()
        
        # Generate command configurations
        command_configs = generate_command_configs(base_url)
        
        # Create or update commands
        print("⚙️  Configuring slash commands...")
        success_count = 0
        error_count = 0
        
        for cmd_config in command_configs:
            cmd_name = cmd_config['command']
            
            # Prepare API payload
            payload = {
                'command': cmd_name,
                'url': cmd_config['url'],
                'description': cmd_config['description'],
                'usage_hint': cmd_config['usage_hint'],
                'should_escape': cmd_config['should_escape']
            }
            
            if cmd_name in existing_commands:
                # Update existing command
                success, message = update_slash_command(token, existing_commands[cmd_name], payload)
            else:
                # Create new command
                success, message = create_slash_command(token, payload)
            
            print(message)
            
            if success:
                success_count += 1
            else:
                error_count += 1
        
        print()
        print("📊 **CONFIGURATION SUMMARY**")
        print("=" * 50)
        print(f"✅ Successfully configured: {success_count} commands")
        if error_count > 0:
            print(f"❌ Failed to configure: {error_count} commands")
        
        if success_count > 0:
            print()
            print("🎉 **NEXT STEPS**")
            print("=" * 50)
            print("1. Your slash commands are now configured!")
            print("2. Try them in your Slack workspace:")
            print("   • /mc servers")
            print("   • /players")
            print("   • /status")
            print("3. If commands don't appear, reinstall your app to the workspace")
        
        if error_count > 0:
            print()
            print("⚠️  **TROUBLESHOOTING**")
            print("=" * 50)
            print("Some commands failed to configure. Common issues:")
            print("• Token doesn't have 'commands:write' scope")
            print("• App is not installed to workspace")
            print("• Command name conflicts")
            print("• Rate limiting")
        
    except KeyboardInterrupt:
        print("\n❌ Configuration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
