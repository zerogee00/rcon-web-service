#!/usr/bin/env python3
"""
Test script for enhanced PufferPanel integration
"""

import os
import sys
sys.path.append('/root/rcon-web-service')

from utils.pufferpanel_integration import list_servers, get_server_info, get_server_logs

def test_integration():
    print("🎮 Testing Enhanced PufferPanel Integration...")
    print("=" * 60)
    
    # Test 1: List all servers
    print("\n📋 Listing all servers:")
    servers = list_servers()
    
    for server in servers:
        status_icon = "🟢" if server['running'] else "🔴"
        print(f"  {status_icon} {server['name']} ({server['id']})")
        print(f"      Type: {server['type']}")
        if server['running']:
            print(f"      PID: {server['pid']}")
            if 'resources' in server:
                res = server['resources']
                print(f"      CPU: {res.get('cpu_percent', 0):.1f}%")
                print(f"      Memory: {res.get('memory_mb', 0):.1f}MB")
        print()
    
    # Test 2: Detailed info for one server
    if servers:
        test_server = servers[0]
        print(f"\n🔍 Detailed info for '{test_server['name']}':")
        detailed = get_server_info(test_server['id'])
        
        if detailed:
            print(f"  Server Directory: {detailed['server_dir']}")
            print(f"  Running: {detailed['running']}")
            
            if 'properties' in detailed:
                props = detailed['properties']
                print(f"  Server Properties:")
                for key in ['server-port', 'motd', 'max-players', 'gamemode', 'difficulty']:
                    if key in props:
                        print(f"    {key}: {props[key]}")
            
            # Test 3: Get recent logs
            print(f"\n📜 Recent logs (last 5 lines):")
            logs = get_server_logs(test_server['id'], 5)
            for log_line in logs[-5:]:
                if log_line.strip():
                    print(f"    {log_line}")
    
    print("\n✅ Integration test complete!")

if __name__ == "__main__":
    test_integration()
