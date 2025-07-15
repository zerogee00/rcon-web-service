# New /servers Slash Command

## Command Added ✅

A new `/servers` slash command has been added to help users identify server IDs and names.

## Slack Configuration

### Add /servers Command to Your Slack App:

1. Go to your Slack app dashboard (https://api.slack.com/apps)
2. Navigate to "Slash Commands"
3. Click "Create New Command"
4. Configure as follows:

```
Command: /servers
Request URL: https://YOUR-CLOUDFLARE-TUNNEL-DOMAIN.com/slack/servers
Short Description: List all available servers with their IDs and names
Usage Hint: (leave empty)
```

## Command Output

When users type `/servers` in Slack, they'll see:

```
👾 **Available Servers**

**Server 1**
ID: `7eaa7ab6`
Port: 25576

**Server 2**
ID: `b46f4016`
Port: 25581

**Server 3**
ID: `e6a4f515`
Port: 25580
```

## Usage Flow

1. User types `/servers` to see available servers
2. User copies the server ID they want
3. User uses `/mc <server_id> <command>` with the correct ID

## Example Workflow

```
User: /servers
Bot: Shows server list with IDs

User: /mc 7eaa7ab6 list
Bot: Shows player list for Server 1
```

## Updated Command Summary

Your Slack app now supports these commands:

### /servers
- **Purpose**: List all servers with IDs and names
- **Usage**: `/servers`
- **Response**: Ephemeral (only visible to user)

### /mc  
- **Purpose**: Execute RCON commands
- **Usage**: `/mc <server_id> <command>`
- **Response**: In-channel (visible to all)

### /players
- **Purpose**: Show player count for all servers
- **Usage**: `/players`
- **Response**: In-channel (visible to all)

## Configuration Summary

Add this third slash command to your Slack app:

| Command | Request URL | Description |
|---------|-------------|-------------|
| `/servers` | `https://YOUR-TUNNEL-DOMAIN.com/slack/servers` | List all servers with IDs |
| `/mc` | `https://YOUR-TUNNEL-DOMAIN.com/slack/mc` | Execute RCON commands |
| `/players` | `https://YOUR-TUNNEL-DOMAIN.com/slack/players` | Show player counts |

All commands use the same OAuth permissions you already configured!

## Implementation Details

- **Response Type**: Ephemeral (private to user)
- **Authentication**: Uses existing Slack signing secret
- **Logging**: User requests are logged for audit
- **Format**: Markdown formatting for better readability

The `/servers` command makes it much easier for users to identify which server ID to use with `/mc`! 🎯
