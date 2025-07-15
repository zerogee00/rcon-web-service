# Bearer Token Usage Guide

## What is the Bearer Token?

The Bearer Token we generated is: `e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd`

## Purpose of the Bearer Token

The Bearer Token is used for **direct API access** to your RCON web service, separate from Slack integration.

## Two Different Authentication Methods

### 1. Slack Integration (Uses Signing Secret)
- **Method**: Slack signature verification
- **Token**: Slack Signing Secret (`160d4303b6e7d262e71c01ef70726dd0`)
- **Usage**: Automatic when users type `/mc` or `/players` in Slack
- **Endpoints**: `/slack/mc` and `/slack/players`

### 2. Direct API Access (Uses Bearer Token)
- **Method**: Bearer token authentication
- **Token**: API Bearer Token (`e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd`)
- **Usage**: Manual API calls, scripts, other applications
- **Endpoints**: `/mc` and `/servers`

## When to Use the Bearer Token

### 1. Testing the API
```bash
# Test server list
curl -H "Authorization: Bearer e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd" \
  http://localhost:5000/servers

# Test RCON command
curl -X POST -H "Authorization: Bearer e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd" \
  -H "Content-Type: application/json" \
  -d '{"server": "7eaa7ab6", "command": "list"}' \
  http://localhost:5000/mc
```

### 2. Automated Scripts
Create scripts that can execute RCON commands automatically:
```python
import requests

headers = {
    'Authorization': 'Bearer e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd',
    'Content-Type': 'application/json'
}

# Get server list
response = requests.get('http://localhost:5000/servers', headers=headers)
print(response.json())

# Execute RCON command
data = {'server': '7eaa7ab6', 'command': 'list'}
response = requests.post('http://localhost:5000/mc', headers=headers, json=data)
print(response.json())
```

### 3. Other Applications
- Web dashboards
- Monitoring tools
- Custom integrations
- Mobile apps

### 4. External Services (via Cloudflare Tunnel)
```bash
# Once your tunnel is set up, external services can use:
curl -H "Authorization: Bearer e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd" \
  https://your-tunnel-domain.com/servers
```

## Security Considerations

### Keep the Bearer Token Secure
- **DON'T** share it publicly
- **DON'T** commit it to version control
- **DO** treat it like a password
- **DO** rotate it periodically if needed

### Token Rotation (if needed)
To change the bearer token:
1. Generate new token: `openssl rand -hex 32`
2. Update `/etc/systemd/system/mc-web.service`
3. Restart service: `systemctl restart rcon-web.service`
4. Update any scripts using the old token

## Current Token Location

The bearer token is currently configured in:
- **File**: `/etc/systemd/system/mc-web.service`
- **Environment Variable**: `API_TOKEN=e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd`

## For Your Slack Bot

**Important**: Your Slack bot does NOT need the bearer token! 

- Slack uses the signing secret for authentication
- The bearer token is for direct API access only
- Your Slack slash commands will work without ever touching the bearer token

## Summary

- **Slack Integration**: Uses signing secret automatically ✅
- **Direct API Access**: Uses bearer token manually 🔧
- **Both work simultaneously**: Different authentication for different use cases 🎯

The bearer token gives you flexibility to build other tools and integrations beyond just Slack!
