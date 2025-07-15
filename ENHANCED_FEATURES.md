# Enhanced RCON Web Service Features

## New Features Added

### 1. Command Aliases
Simplified commands that expand to full plugin commands:

**Player Management:**
- `heal <player>` → `essentials:heal <player>`
- `feed <player>` → `essentials:feed <player>`
- `fly <player>` → `essentials:fly <player>`
- `tp <player1> <player2>` → `essentials:tp <player1> <player2>`
- `spawn <player>` → `essentials:spawn <player>`
- `gm <mode> <player>` → `essentials:gamemode <mode> <player>`

**LuckPerms Shortcuts:**
- `addperm <player> <permission>` → `lp user <player> permission set <permission> true`
- `removeperm <player> <permission>` → `lp user <player> permission unset <permission>`
- `addgroup <player> <group>` → `lp user <player> parent add <group>`
- `userinfo <player>` → `lp user <player> info`
- `fly_on <player>` → `lp user <player> permission set essentials.fly true`
- `fly_off <player>` → `lp user <player> permission unset essentials.fly`

**Economy Commands:**
- `bal <player>` → `essentials:balance <player>`
- `pay <player> <amount>` → `essentials:pay <player> <amount>`
- `baltop` → `essentials:baltop`

**Quick World Commands:**
- `day` → `time set day`
- `night` → `time set night`
- `sun` → `weather clear`
- `rain` → `weather rain`
- `save` → `save-all`

### 2. Configuration System
Admin users can modify bot settings directly from Slack:

**Configuration Commands:**
- `/mc <server_id> config` - Show current configuration
- `/mc <server_id> config set <key> <value>` - Set configuration value
- `/mc <server_id> config reset` - Reset to defaults

**Available Settings:**
- `enable_aliases` - Enable/disable command aliases
- `enable_luckperms_shortcuts` - Enable/disable LuckPerms shortcuts
- `enable_essentials_shortcuts` - Enable/disable Essentials shortcuts
- `default_group` - Default group for group operations
- `admin_users` - List of admin users (comma-separated)
- `enable_dangerous_commands` - Enable/disable dangerous commands
- `auto_essentials_prefix` - Auto-prefix essentials commands

### 3. Safety Features
- **Admin Protection**: Only admin users can modify configuration
- **Dangerous Command Protection**: Commands like `stop`, `ban`, `op` are disabled by default
- **Command Transformation Tracking**: Shows how commands are transformed

### 4. Enhanced Help System
- `/mc <server_id> help` - Shows comprehensive help with all aliases and shortcuts

## Usage Examples

**Basic Commands:**
```
/mc 7eaa7ab6 heal PlayerName
/mc 7eaa7ab6 fly_on PlayerName
/mc 7eaa7ab6 addperm PlayerName essentials.fly
/mc 7eaa7ab6 day
/mc 7eaa7ab6 bal PlayerName
```

**Configuration (Admin only):**
```
/mc 7eaa7ab6 config
/mc 7eaa7ab6 config set enable_dangerous_commands true
/mc 7eaa7ab6 config set admin_users doktorodd,admin2
```

**Help:**
```
/mc 7eaa7ab6 help
```

## Command Transformation
The bot now shows how commands are transformed:
- **Alias**: Shows if a command alias was used
- **Converted**: Shows if vanilla commands were converted to Essentials

Example output:
```
✅ **Server Name** (7eaa7ab6)
Alias: `heal PlayerName` → `essentials:heal PlayerName`
```

## Admin Users
Currently configured admin users: `doktorodd`

Admin users can:
- Modify configuration settings
- Enable dangerous commands
- Reset configuration to defaults
