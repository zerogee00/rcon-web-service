#!/usr/bin/env python3
"""
Example script showing how to use the Bearer Token for direct API access
"""

import requests
import json
import sys

# Your bearer token
BEARER_TOKEN = "e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd"
BASE_URL = "http://localhost:5000"  # Change to your tunnel URL for external access

def make_api_request(endpoint, method="GET", data=None):
    """Make an authenticated API request"""
    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    if method == "GET":
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    elif method == "POST":
        response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
    
    return response.json()

def get_servers():
    """Get list of available servers"""
    return make_api_request("/servers")

def execute_rcon(server_id, command):
    """Execute RCON command on a server"""
    data = {
        "server": server_id,
        "command": command
    }
    return make_api_request("/rcon", method="POST", data=data)

def main():
    print("=== RCON API Example ===\n")
    
    # Get server list
    print("1. Getting server list...")
    servers = get_servers()
    print(json.dumps(servers, indent=2))
    
    # Execute commands on each server
    print("\n2. Checking players on all servers...")
    for server in servers['servers']:
        server_id = server['id']
        server_name = server['name']
        
        print(f"\n--- {server_name} ({server_id}) ---")
        result = execute_rcon(server_id, "list")
        
        if result.get('success'):
            print(f"✅ {result['output']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    # Example of sending a message
    print("\n3. Example: Sending a message to Server 1...")
    result = execute_rcon("7eaa7ab6", "say Hello from Python script!")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
