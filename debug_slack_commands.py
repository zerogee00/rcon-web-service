#!/usr/bin/env python3
"""
Debug script to test Slack endpoints manually
"""
import sys
sys.path.insert(0, '.')

from app import create_app

def list_endpoints():
    """List all registered endpoints"""
    app = create_app()
    print("🔍 **Registered Slack Endpoints:**")
    print("=" * 50)
    
    for rule in app.url_map.iter_rules():
        if 'slack' in rule.rule:
            methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"📍 {rule.rule:<30} [{methods}]")
    
    print("\n🎯 **Expected Slack Commands:**")
    print("=" * 50)
    print("• /mc <command>     → /slack/mc")
    print("• /players          → /slack/players") 
    print("• /servers          → /slack/servers")
    print("• /backup <args>    → /slack/backup")
    
    print("\n🧪 **Test Commands to Try in Slack:**")
    print("=" * 50)
    print("1. /mc servers      # This should work if /mc is configured")
    print("2. /servers         # This needs to be configured as separate command")
    print("3. /players         # This needs to be configured as separate command")
    print("4. /backup list     # This should work if /backup is configured")

if __name__ == "__main__":
    list_endpoints()
