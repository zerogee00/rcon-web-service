# Slack Configuration Checklist

## Pre-Requirements ✅
- [x] RCON Web Service running on port 5000
- [x] Slack signing secret: `160d4303b6e7d262e71c01ef70726dd0`
- [ ] Cloudflare tunnel configured (pointing to localhost:5000)
- [ ] Tunnel domain URL ready

## Step-by-Step Setup

### 1. Access Slack App Dashboard
- [ ] Go to https://api.slack.com/apps
- [ ] Select your existing app OR create new app
- [ ] Note your app name: ________________

### 2. Configure Slash Commands
- [ ] Navigate to "Slash Commands" in left sidebar
- [ ] Click "Create New Command"

#### /mc Command Setup
- [ ] Command: `/mc`
- [ ] Request URL: `https://YOUR-TUNNEL-DOMAIN.com/slack/mc`
- [ ] Short Description: `Execute Minecraft server commands`
- [ ] Usage Hint: `<server_id> <command>`
- [ ] Click "Save"

#### /players Command Setup
- [ ] Click "Create New Command" again
- [ ] Command: `/players`
- [ ] Request URL: `https://YOUR-TUNNEL-DOMAIN.com/slack/players`
- [ ] Short Description: `Show player count for all servers`
- [ ] Usage Hint: (leave empty)
- [ ] Click "Save"

### 3. Set Permissions
- [ ] Go to "OAuth & Permissions"
- [ ] Add Bot Token Scopes:
  - [ ] `commands`
  - [ ] `chat:write`
  - [ ] `chat:write.public`
- [ ] Click "Install to Workspace"
- [ ] Authorize the app

### 4. Verify Configuration
- [ ] Go to "Basic Information"
- [ ] Confirm Signing Secret matches: `160d4303b6e7d262e71c01ef70726dd0`
- [ ] App is installed in workspace

### 5. Test Commands
- [ ] Try: `/mc 7eaa7ab6 list`
- [ ] Try: `/players`
- [ ] Verify responses appear in Slack

## Quick Reference

### Your Server IDs
- `7eaa7ab6` = Server 1 (Port 25576)
- `b46f4016` = Server 2 (Port 25581)
- `e6a4f515` = Server 3 (Port 25580)

### Test Commands
```
/mc 7eaa7ab6 list
/mc b46f4016 tps
/mc e6a4f515 say Hello from Slack!
/players
```

### Troubleshooting
- [ ] Cloudflare tunnel is running
- [ ] Web service is responding (test with curl)
- [ ] Slack app has correct permissions
- [ ] Request URLs match your tunnel domain

## Final Check
- [ ] All slash commands work in Slack
- [ ] Bot responds with server information
- [ ] No error messages in Slack
- [ ] Server logs show RCON commands being executed

🎉 Setup complete when all boxes are checked!
