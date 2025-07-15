#!/bin/bash

API_TOKEN="e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd"
BASE_URL="http://localhost:5000"

echo "=== Testing Health Check ==="
curl -s "$BASE_URL/health" | python3 -m json.tool

echo -e "\n=== Testing Server List ==="
curl -s -H "Authorization: Bearer $API_TOKEN" "$BASE_URL/servers" | python3 -m json.tool

echo -e "\n=== Testing RCON Command (list players) ==="
curl -s -X POST -H "Authorization: Bearer $API_TOKEN" -H "Content-Type: application/json" \
  -d '{"server": "7eaa7ab6", "command": "list"}' "$BASE_URL/rcon" | python3 -m json.tool

echo -e "\n=== Testing RCON Command (server info) ==="
curl -s -X POST -H "Authorization: Bearer $API_TOKEN" -H "Content-Type: application/json" \
  -d '{"server": "b46f4016", "command": "tps"}' "$BASE_URL/rcon" | python3 -m json.tool

echo -e "\n=== Testing New /servers Endpoint ==="
echo "Note: This simulates a Slack request (normally needs proper signature)"
curl -s -X POST "http://localhost:5000/slack/servers" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "user_name=test_user" | python3 -m json.tool
