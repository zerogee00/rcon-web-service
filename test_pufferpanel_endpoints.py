#!/usr/bin/env python3
"""
Test script for PufferPanel Slack endpoints
"""
import requests
import json
import sys

def test_endpoint(endpoint, data=None):
    """Test a Slack endpoint"""
    url = f"http://localhost:5000/slack/{endpoint}"
    
    # Default Slack form data
    payload = {
        'user_name': 'test_user',
        'text': data if data else '',
        'team_id': 'TEST123',
        'channel_id': 'C123',
        'user_id': 'U123',
        'command': f'/{endpoint}',
        'token': 'test_token'
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        print(f"✅ {endpoint}: Status {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"   Response: {result.get('text', '')[:100]}...")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ {endpoint}: Error - {e}")
        return False

def main():
    print("🧪 Testing PufferPanel Slack endpoints...")
    print("=" * 50)
    
    endpoints = [
        ('status', ''),
        ('start', '7eaa7ab6'),  # Using first server from our test
        ('logs', '7eaa7ab6 10'),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint, test_data in endpoints:
        if test_endpoint(endpoint, test_data):
            success_count += 1
        print()
    
    print(f"📊 Results: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 All PufferPanel endpoints are working!")
        return 0
    else:
        print("⚠️  Some endpoints may need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
