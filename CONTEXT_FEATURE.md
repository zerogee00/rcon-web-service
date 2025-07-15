# Context Feature - Default Server Support

## Overview
The context feature allows users to set a default server, eliminating the need to specify the server ID with every command.

## How It Works

### Setting a Default Server
```
/mc context set <server_id>
```

### Using Commands Without Server ID
Once you've set a default server, you can use commands without specifying the server ID:
```
/mc heal PlayerName
/mc fly_on PlayerName
/mc day
/mc tps
```

Instead of:
```
/mc 7eaa7ab6 heal PlayerName
/mc 7eaa7ab6 fly_on PlayerName
/mc 7eaa7ab6 day
/mc 7eaa7ab6 tps
```

## Context Commands

### Set Default Server
```
/mc context set 7eaa7ab6
```
Response: `✅ Default server set to **Server Name** (7eaa7ab6)`

### Show Current Default
```
/mc context get
```
or
```
/mc context show
```
Response: `📋 Your default server: **Server Name** (7eaa7ab6)`

### Clear Default Server
```
/mc context clear
```
Response: `✅ Default server cleared`

### List Available Servers
```
/mc context list
```
Response: Shows all available servers with their IDs and names

## Usage Examples

**First, set your default server:**
```
/mc context set 7eaa7ab6
```

**Then use commands without server ID:**
```
/mc heal PlayerName
/mc addperm PlayerName essentials.fly
/mc day
/mc list
/mc tps
```

**You can still use the traditional format:**
```
/mc b46f4016 heal PlayerName
```

## Help Command
```
/mc
```
Shows usage information including your current default server (if set)

## Configuration Options (Admin)

### Global Default Server
Admins can set a global default server for all users:
```
/mc config set global_default_server 7eaa7ab6
```

### Enable/Disable User Contexts
```
/mc config set enable_user_contexts false
```
When disabled, only the global default server is used.

## How Context Resolution Works

1. **User has default server set**: Uses user's default server
2. **User has no default, but global default exists**: Uses global default
3. **No defaults set**: Requires server ID in command

## Benefits

- **Faster commands**: No need to remember/type server IDs
- **User-specific**: Each user can have their own default server
- **Backward compatible**: Traditional format still works
- **Fallback support**: Global defaults for new users

## Error Handling

If you try to use a command without a server ID and no default is set:
```
❌ No default server set. Use `/mc context set <server_id>` to set one, or use `/mc <server_id> <command>`
```

## Admin View

Admins can see all user contexts in the config:
```
/mc config
```

Shows:
- Current configuration
- User contexts (who has what default server)
