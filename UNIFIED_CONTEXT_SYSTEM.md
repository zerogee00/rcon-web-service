# Unified Context System

## Overview
The RCON Web Service now uses a single, unified context-based system that intelligently manages user preferences and temporary contexts. This replaces the previous dual system of `setdefault` commands and separate context management.

## How It Works

### 1. Smart Server Selection
- When a user runs a command without specifying a server, the system first checks for their **default server**
- If no default server is set, it prompts them to choose one
- Once they choose, that server becomes their **persistent default** for all future commands
- Users can change their default by explicitly using a different server: `/mc <server_id> <command>`

### 2. Context-Aware Interactions
- When prompting for server selection, the system sets a **temporary context**
- This context remembers what command the user wanted to run
- After server selection, it automatically executes the original command
- Contexts expire after 5 minutes of inactivity

### 3. Unified Commands

#### Core Commands
- `/mc <command>` - Run on default server (prompts to select if none set)
- `/mc <server_id> <command>` - Run on specific server (updates default)
- `/mc servers` - List all servers with current default highlighted
- `/mc config` - View current configuration
- `/mc config clear` - Clear default server
- `/mc config reset` - Reset all settings
- `/mc help` - Show help

#### Removed Commands
- `setdefault` - No longer needed! Server selection is now contextual and automatic

## User Experience Flow

### First Time User
1. User runs `/mc list`
2. System prompts: "Choose a server: 1. Server A, 2. Server B..."
3. User replies: `1`
4. System sets Server A as default and shows player list
5. Future commands automatically use Server A

### Experienced User
1. User has Server A as default
2. User runs `/mc time set day` - executes on Server A
3. User runs `/mc server_b weather clear` - executes on Server B AND sets Server B as new default
4. Future commands now use Server B by default

### Configuration Management
1. User runs `/mc config` - shows current default server and any active context
2. User runs `/mc config clear` - removes default server, will prompt on next command
3. User runs `/mc config reset` - clears everything, fresh start

## Technical Implementation

### Context Types
- `server_selection` - Temporary context during server selection process
- Default server storage - Persistent user preference

### Context Data Structure
```json
{
  "user123": {
    "default_server": "7eaa7ab6",
    "context": {
      "type": "server_selection",
      "data": {
        "command": "list",
        "servers": ["7eaa7ab6", "b46f4016"]
      },
      "created_at": "2025-07-19T22:00:00",
      "expires_at": "2025-07-19T22:05:00"
    }
  }
}
```

### Key Functions
- `get_user_default_server()` - Get persistent default
- `set_user_default_server()` - Set/clear persistent default
- `get_user_context()` / `set_user_context()` - Manage temporary contexts
- `prompt_server_selection()` - Unified server selection flow

## Benefits

### For Users
- ✅ **Simpler**: No need to remember `setdefault` command
- ✅ **Intuitive**: Natural flow from selection to execution
- ✅ **Flexible**: Easy to switch between servers
- ✅ **Persistent**: Remembers preferences across sessions
- ✅ **Contextual**: Understands what you're trying to do

### For Developers
- ✅ **Unified**: Single system instead of two separate ones
- ✅ **Maintainable**: Less code duplication
- ✅ **Extensible**: Easy to add new context types
- ✅ **Consistent**: All user interactions follow same pattern

## Migration Notes
- Existing user data is preserved
- Old `setdefault` commands removed from help and code
- Context system enhanced to handle server clearing (None values)
- All existing default servers continue to work seamlessly
