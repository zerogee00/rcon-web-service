#!/usr/bin/env python3
"""
Automated Slack Slash Commands Setup Script for RCON Web Service

This script creates all necessary slash command configurations that can be 
copy-pasted into Slack's slash command setup interface.
"""

import sys
import os
from urllib.parse import urlparse

def get_base_url():
    """Get the base URL for the service"""
    # Check for environment variable first
    base_url = os.environ.get('RCON_SERVICE_URL')
    
    if not base_url:
        # Interactive prompt
        print("🌐 **Service URL Configuration**")
        print("=" * 50)
        print("Enter your RCON Web Service base URL.")
        print("Examples:")
        print("  • https://your-domain.com")
        print("  • https://your-server.ngrok.io") 
        print("  • http://your-ip:5000")
        print()
        
        while True:
            base_url = input("Enter base URL: ").strip()
            if base_url:
                # Validate URL format
                try:
                    parsed = urlparse(base_url)
                    if parsed.scheme in ['http', 'https'] and parsed.netloc:
                        break
                    else:
                        print("❌ Invalid URL format. Please include http:// or https://")
                except:
                    print("❌ Invalid URL format.")
            else:
                print("❌ URL is required.")
    
    return base_url.rstrip('/')

def generate_slack_commands(base_url):
    """Generate Slack slash command configurations"""
    
    commands = [
        {
            'name': 'mc',
            'description': 'Execute Minecraft RCON commands on your servers',
            'usage_hint': '[server_id] <command> | servers | help | config',
            'url': f'{base_url}/slack/mc',
            'examples': [
                '/mc list',
                '/mc say Hello players!', 
                '/mc servers',
                '/mc help',
                '/mc config'
            ]
        },
        {
            'name': 'players',
            'description': 'Show online players on your default server',
            'usage_hint': '',
            'url': f'{base_url}/slack/players',
            'examples': ['/players']
        },
        {
            'name': 'servers',
            'description': 'List all available Minecraft servers',
            'usage_hint': '',
            'url': f'{base_url}/slack/servers',
            'examples': ['/servers']
        },
        {
            'name': 'backup',
            'description': 'Manage Minecraft server backups',
            'usage_hint': 'list | create [server_id] | restore [backup_id] | cleanup',
            'url': f'{base_url}/slack/backup',
            'examples': [
                '/backup list',
                '/backup create',
                '/backup create 7eaa7ab6',
                '/backup cleanup'
            ]
        },
        {
            'name': 'status',
            'description': 'Show status of all Minecraft servers and system resources',
            'usage_hint': '',
            'url': f'{base_url}/slack/status',
            'examples': ['/status']
        },
        {
            'name': 'start',
            'description': 'Start a Minecraft server',
            'usage_hint': '<server_id>',
            'url': f'{base_url}/slack/start',
            'examples': ['/start 7eaa7ab6']
        },
        {
            'name': 'stop',
            'description': 'Stop a Minecraft server',
            'usage_hint': '<server_id>',
            'url': f'{base_url}/slack/stop',
            'examples': ['/stop 7eaa7ab6']
        },
        {
            'name': 'restart',
            'description': 'Restart a Minecraft server',
            'usage_hint': '<server_id>',
            'url': f'{base_url}/slack/restart',
            'examples': ['/restart 7eaa7ab6']
        },
        {
            'name': 'logs',
            'description': 'View recent server logs',
            'usage_hint': '<server_id> [lines]',
            'url': f'{base_url}/slack/logs',
            'examples': [
                '/logs 7eaa7ab6',
                '/logs 7eaa7ab6 50'
            ]
        }
    ]
    
    return commands

def print_setup_instructions(commands):
    """Print setup instructions for Slack"""
    
    print("\n" + "="*80)
    print("🚀 **SLACK SLASH COMMANDS SETUP GUIDE**")
    print("="*80)
    
    print(f"\n📋 **Setup Instructions:**")
    print("1. Go to https://api.slack.com/apps")
    print("2. Select your Slack app (or create one)")
    print("3. Navigate to 'Slash Commands' in the left sidebar")
    print("4. For each command below, click 'Create New Command'")
    print("5. Copy and paste the configuration details")
    print("6. Click 'Save' for each command")
    print("7. Don't forget to reinstall your app to the workspace!")
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n{'='*60}")
        print(f"📝 **COMMAND {i}: /{cmd['name']}**")
        print('='*60)
        print(f"**Command:** /{cmd['name']}")
        print(f"**Request URL:** {cmd['url']}")  
        print(f"**Short Description:** {cmd['description']}")
        if cmd['usage_hint']:
            print(f"**Usage Hint:** {cmd['usage_hint']}")
        else:
            print(f"**Usage Hint:** (leave empty)")
        print(f"**Escape channels, users, and links sent to your app:** ✅ (checked)")
        
        print(f"\n**Examples:**")
        for example in cmd['examples']:
            print(f"  • {example}")
    
    print(f"\n{'='*60}")
    print("🎯 **QUICK COPY-PASTE SUMMARY**")
    print('='*60)
    print("| Command   | URL                           |")
    print("| --------- | ----------------------------- |")
    for cmd in commands:
        print(f"| /{cmd['name']:<9} | {cmd['url']:<30} |")

def generate_curl_tests(commands, base_url):
    """Generate curl test commands"""
    
    print(f"\n{'='*60}")
    print("🧪 **TEST COMMANDS (Optional)**")
    print('='*60)
    print("You can test these endpoints manually with curl:")
    print()
    
    test_commands = [
        ('mc', 'text=servers'),
        ('players', ''),
        ('servers', ''),
        ('status', ''),
        ('backup', 'text=list'),
    ]
    
    for cmd_name, params in test_commands:
        if params:
            print(f"# Test /{cmd_name}")
            print(f"curl -X POST {base_url}/slack/{cmd_name} \\")
            print(f"  -d 'user_name=testuser&{params}'")
        else:
            print(f"# Test /{cmd_name}")
            print(f"curl -X POST {base_url}/slack/{cmd_name} \\")
            print(f"  -d 'user_name=testuser'")
        print()

def save_config_file(base_url, commands):
    """Save configuration to a file for reference"""
    
    config_content = f"""# Slack Slash Commands Configuration
# Generated on: {__import__('datetime').datetime.now().isoformat()}
# Base URL: {base_url}

# Command configurations for Slack App setup:
"""
    
    for cmd in commands:
        config_content += f"""
## /{cmd['name']}
Command: /{cmd['name']}
Request URL: {cmd['url']}
Short Description: {cmd['description']}
Usage Hint: {cmd['usage_hint']}
"""
    
    config_file = 'slack_commands_config.txt'
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"\n📄 **Configuration saved to:** {config_file}")
    return config_file

def main():
    """Main execution function"""
    
    print("🤖 **AUTOMATED SLACK SLASH COMMANDS SETUP**")
    print("=" * 80)
    print("This script will generate all the configuration needed for")
    print("your Slack slash commands to work with the RCON Web Service.")
    print()
    
    try:
        # Get base URL
        base_url = get_base_url()
        
        # Generate command configurations
        commands = generate_slack_commands(base_url)
        
        # Print setup instructions
        print_setup_instructions(commands)
        
        # Generate test commands
        generate_curl_tests(commands, base_url)
        
        # Save config file
        config_file = save_config_file(base_url, commands)
        
        print(f"\n✅ **SETUP COMPLETE!**")
        print(f"📋 Total commands to configure: {len(commands)}")
        print(f"📄 Configuration saved to: {config_file}")
        print(f"🌐 Service URL: {base_url}")
        print()
        print("Next steps:")
        print("1. Copy the command configurations above into your Slack app")
        print("2. Test the commands in your Slack workspace")
        print("3. Run the curl test commands if needed")
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
