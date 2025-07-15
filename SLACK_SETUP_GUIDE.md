# Slack App Configuration Guide

## Step 1: Create or Access Your Slack App

1. Go to https://api.slack.com/apps
2. If you already have an app, click on it. If not, click "Create New App"
3. Choose "From scratch"
4. Enter app name (e.g., "Minecraft RCON Bot")
5. Select your workspace
6. Click "Create App"

## Step 2: Configure Slash Commands

### Add /mc Command
1. In your app dashboard, go to "Slash Commands" in the left sidebar
2. Click "Create New Command"
3. Fill in the details:
   - **Command**: `/mc`
   - **Request URL**: `https://YOUR-CLOUDFLARE-TUNNEL-DOMAIN.com/slack/mc`
   - **Short Description**: `Execute Minecraft server commands`
   - **Usage Hint**: `<server_id> <command>`
   - **Escape channels, users, and links**: Leave unchecked
4. Click "Save"

### Add /players Command
1. Click "Create New Command" again
2. Fill in the details:
   - **Command**: `/players`
   - **Request URL**: `https://YOUR-CLOUDFLARE-TUNNEL-DOMAIN.com/slack/players`
   - **Short Description**: `Show player count for all servers`
   - **Usage Hint**: `` (leave empty)
   - **Escape channels, users, and links**: Leave unchecked
3. Click "Save"

## Step 3: Configure OAuth & Permissions

1. Go to "OAuth & Permissions" in the left sidebar
2. Scroll down to "Scopes"
3. Add these Bot Token Scopes:
   - `commands` (for slash commands)
   - `chat:write` (to send messages)
   - `chat:write.public` (to send messages to channels)
4. Click "Install to Workspace" at the top
5. Authorize the app

## Step 4: Get Your Signing Secret

1. Go to "Basic Information" in the left sidebar
2. Scroll down to "App Credentials"
3. Copy the "Signing Secret" - this should be: `160d4303b6e7d262e71c01ef70726dd0`

## Step 5: Test Configuration

### Test /mc Command
Try these examples in your Slack workspace:

```
/mc 7eaa7ab6 list
/mc b46f4016 tps
/mc e6a4f515 say Hello from Slack!
```

### Test /players Command
```
/players
```

## Server IDs Reference

- **7eaa7ab6**: Server 1 (Port 25576)
- **b46f4016**: Server 2 (Port 25581)
- **e6a4f515**: Server 3 (Port 25580)

## Common RCON Commands

### Player Management
- `list` - List online players
- `kick <player>` - Kick a player
- `ban <player>` - Ban a player
- `pardon <player>` - Unban a player

### Server Management
- `say <message>` - Send message to all players
- `tps` - Show server TPS (if supported)
- `save-all` - Save the world
- `stop` - Stop the server

### World Management
- `time set day` - Set time to day
- `time set night` - Set time to night
- `weather clear` - Clear weather
- `weather rain` - Start rain

## Troubleshooting

### Command Not Found
- Verify the slash command is created in your Slack app
- Check that the Request URL is correct
- Ensure your Cloudflare tunnel is running

### Permission Denied
- Verify the signing secret matches
- Check that the app has proper scopes
- Reinstall the app if permissions were changed

### Server Connection Failed
- Verify the Minecraft servers are running
- Check RCON is enabled in server.properties
- Test RCON locally first

## Security Notes

- Your signing secret is: `160d4303b6e7d262e71c01ef70726dd0`
- Keep this secret secure and don't share it
- Commands executed via Slack are logged on the server
- Users can only execute commands they have permission for in your workspace

## Example Slack Interactions

**User input:** `/mc 7eaa7ab6 list`
**Bot response:** 
```
✅ Server 1
There are 0 out of maximum 20 players online.
```

**User input:** `/players`
**Bot response:**
```
🎮 Server Status

Server 1: There are 0 out of maximum 20 players online.
Server 2: There are 2 out of maximum 20 players online.
Server 3: ❌ Connection failed
```

Your Slack app is now ready to control your Minecraft servers! 🎮
