# Slack Notification Integration Guide

This guide shows how to integrate the enhanced Slack notifications for minecraft server control into your RCON web service.

## 📋 Summary

✅ **Configured webhooks:**
- Backup notifications: `BACKUP_SLACK_WEBHOOK_URL`
- System health notifications: `SYSTEM_SLACK_WEBHOOK_URL`  
- Minecraft server control: `MINECRAFT_SLACK_WEBHOOK_URL` *(NEW)*

✅ **Notification types available:**
- RCON command execution and results
- Player actions (kick, ban, whitelist, op, etc.)
- Server status changes (start, stop, restart)

## 🔧 Integration Steps

### 1. Import the notification functions

In your `routes/slack_routes.py`, add this import:

```python
from utils.slack_notifications import notify_command, notify_player_action, notify_server_status
```

### 2. Add notifications after RCON command execution

Find where `execute_rcon_command()` is called and add notifications:

```python
# Execute command
result = execute_rcon_command(server_id, processed_command, f"Slack User: {user_name}")

# Send Slack notification
try:
    server_info = get_server_info(server_id)
    notify_command(user_name, server_info['name'], processed_command, result, success=True)
except Exception as e:
    logger.error(f"Failed to send Slack notification: {e}")
```

### 3. Add player action notifications

For player management commands, add specific notifications:

```python
# Detect player management commands
if any(cmd in processed_command.lower() for cmd in ['kick', 'ban', 'whitelist', 'op', 'pardon']):
    # Extract action and player name from command
    parts = processed_command.split()
    if len(parts) >= 2:
        action = parts[0]
        player = parts[1] if len(parts) > 1 else None
        notify_player_action(user_name, server_info['name'], action, player, result)
```

### 4. Environment Variables

Ensure your application loads the environment variables:

```python
import os
from dotenv import load_dotenv
load_dotenv()  # This loads .env file
```

## 🧪 Testing

Run the test script to verify webhooks are working:

```bash
cd /root/rcon-web-service
python3 test_minecraft_notifications.py
```

## 📁 File Structure

```
/root/rcon-web-service/
├── .env                          # Webhook URLs (not in version control)
├── utils/slack_notifications.py  # Notification system
├── test_minecraft_notifications.py  # Test script
└── routes/slack_routes.py        # Where to integrate notifications
```

## 🔒 Security

- Webhook URLs are stored in `.env` file (excluded from git)
- Environment variables are loaded at runtime
- No sensitive data in version control

## 📱 Notification Examples

The system will send notifications like:

**Command Execution:**
```
✅ Minecraft Command: /list
User: AdminUser
Server: Oddmine OG!
Command: /list
Result: There are 3 players online: Player1, Player2, Player3
```

**Player Actions:**
```
👢 Player Action: kick - BadPlayer
User: AdminUser  
Server: Oddmine OG!
Action: kick
Player: BadPlayer
Details: Excessive griefing
```

**Server Status:**
```
🔄 Server restarted: Oddmine OG!
Server: Oddmine OG!
Status: RESTARTED
Initiated by: AdminUser
```

All notifications include rich formatting, emojis, and preview text for enhanced Slack integration.
