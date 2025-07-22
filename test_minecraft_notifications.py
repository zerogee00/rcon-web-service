#!/usr/bin/env python3
"""
Test script for minecraft Slack notifications
Run this to test the minecraft webhook integration
"""

import os
import sys
sys.path.append('/root/rcon-web-service')

from utils.slack_notifications import notify_command, notify_player_action, notify_server_status

# Load environment
with open('.env', 'r') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value.strip('"')

def test_notifications():
    print("🧪 Testing Minecraft Slack Notifications...")
    
    # Test 1: Command notification
    print("📋 Testing command notification...")
    success = notify_command(
        user="TestUser", 
        server_name="Oddmine OG!", 
        command="/list", 
        result="There are 3 players online: Player1, Player2, Player3",
        success=True
    )
    print(f"   Command notification: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 2: Player action notification
    print("👤 Testing player action notification...")
    success = notify_player_action(
        user="AdminUser",
        server_name="Oddmine OG!",
        action="kick",
        player="BadPlayer",
        details="Excessive griefing"
    )
    print(f"   Player action notification: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 3: Server status notification
    print("🔄 Testing server status notification...")
    success = notify_server_status(
        server_name="Oddmine OG!",
        status="restarted", 
        user="AdminUser"
    )
    print(f"   Server status notification: {'✅ Success' if success else '❌ Failed'}")
    
    print("\n✅ Test complete! Check your Slack channels for notifications.")

if __name__ == "__main__":
    test_notifications()
