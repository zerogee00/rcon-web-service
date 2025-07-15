# Slack Slash Command Configuration Details

## /mc Command

**Command:** `/mc`

**Short Description:** 
```
Execute Minecraft server commands
```

**Usage Hint:**
```
<server_id> <command>
```

**Examples:**
- `/mc 7eaa7ab6 list` - List players on Server 1
- `/mc b46f4016 say Hello everyone!` - Send message to Server 2
- `/mc e6a4f515 tps` - Check TPS on Server 3

---

## /players Command

**Command:** `/players`

**Short Description:**
```
Show player count and status for all servers
```

**Usage Hint:**
```
(no parameters needed)
```

**Examples:**
- `/players` - Display player count for all servers

---

## Server ID Reference

When using `/mc <server_id> <command>`, use these server IDs:

- **7eaa7ab6** - Server 1 (Port 25576)
- **b46f4016** - Server 2 (Port 25581)
- **e6a4f515** - Server 3 (Port 25580)

---

## Common Minecraft Commands for /mc

### Player Management
- `list` - List online players
- `kick <playername>` - Kick a player
- `ban <playername>` - Ban a player
- `pardon <playername>` - Unban a player

### Communication
- `say <message>` - Send message to all players
- `tell <playername> <message>` - Send private message

### Server Control
- `tps` - Show server performance (if supported)
- `save-all` - Save the world
- `reload` - Reload server configuration

### World Management
- `time set day` - Set time to day
- `time set night` - Set time to night
- `weather clear` - Clear weather
- `weather rain` - Start rain

### Example Usage in Slack:
```
/mc 7eaa7ab6 list
/mc b46f4016 say Server restart in 5 minutes!
/mc e6a4f515 time set day
/players
```
