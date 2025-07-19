"""
Configuration settings for RCON Web Service
"""
import os

# PufferPanel configuration
USER_CONTEXTS_FILE = 'user_contexts.json'
PUFFERPANEL_SERVER_ROOT = "/var/lib/pufferpanel/servers"

# Server configurations
SERVERS = {
    "7eaa7ab6": {
        "port": 25576,
        "password": "randompass123"
    },
    "b46f4016": {
        "port": 25581,
        "password": "mQV8H0eNyjTh8Kn0"
    },
    "e6a4f515": {
        "port": 25580,
        "password": "BZXltsTJB56tB1Gg"
    }
}

# Security configuration
SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET')
API_TOKEN = os.environ.get('API_TOKEN', 'your-secure-api-token')

# Configuration system - can be modified from Slack
CONFIG = {
    'enable_aliases': True,
    'enable_luckperms_shortcuts': True,
    'enable_essentials_shortcuts': True,
    'default_group': 'default',
    'admin_users': ['doktorodd'],  # Add your Slack username here
    'enable_dangerous_commands': False,
    'max_command_length': 500,
    'rate_limit_per_user': 30,  # commands per minute
    'enable_context_commands': True,
    'default_context_timeout': 300,  # 5 minutes
    'enable_auto_suggest': True,
    'log_level': 'INFO'
}

# Backup configuration
BACKUP_CONFIG = {
    'backup_script_path': '/var/lib/pufferpanel/backup.sh',
    'log_file': '/var/log/minecraft-backup.log',
    'max_log_lines': 20
}

# Command aliases and shortcuts
ALIASES = {
    'list': 'list',
    'online': 'list',
    'who': 'list',
    'players': 'list',
    'pl': 'plugins',
    'plugins': 'plugins',
    'reload': 'reload',
    'rl': 'reload',
    'restart': 'restart',
    'stop': 'stop',
    'start': 'start',
    'save': 'save-all',
    'saveall': 'save-all',
    'whitelist': 'whitelist list',
    'wl': 'whitelist list',
    'ban': 'ban {player}',
    'unban': 'pardon {player}',
    'kick': 'kick {player}',
    'op': 'op {player}',
    'deop': 'deop {player}',
    'weather': 'weather {type}',
    'time': 'time set {time}',
    'tp': 'tp {player1} {player2}',
    'tpa': 'minecraft:tp {player1} {player2}',
    'gamemode': 'gamemode {mode} {player}',
    'gm': 'gamemode {mode} {player}',
    'gms': 'gamemode survival {player}',
    'gmc': 'gamemode creative {player}',
    'gma': 'gamemode adventure {player}',
    'gmsp': 'gamemode spectator {player}',
    'heal': 'effect give {player} minecraft:instant_health 1 255',
    'feed': 'effect give {player} minecraft:saturation 1 255',
    'fly': 'effect give {player} minecraft:levitation 0 0',
    'clear': 'clear {player}',
    'give': 'give {player} {item} {amount}',
    'enchant': 'enchant {player} {enchantment} {level}',
    'xp': 'experience add {player} {amount}',
    'level': 'experience add {player} {amount} levels'
}

# LuckPerms shortcuts
LUCKPERMS_SHORTCUTS = {
    'addgroup': 'lp user {player} parent add {group}',
    'removegroup': 'lp user {player} parent remove {group}', 
    'setgroup': 'lp user {player} parent set {group}',
    'userinfo': 'lp user {player} info',
    'groupperm': 'lp group {group} permission set {permission} true',
    'userperm': 'lp user {player} permission set {permission} true',
    'removeperm': 'lp user {player} permission unset {permission}',
    'listgroups': 'lp listgroups',
    'groupinfo': 'lp group {group} info',
    'promote': 'lp user {player} promote',
    'demote': 'lp user {player} demote'
}

# Essentials shortcuts
ESSENTIALS_SHORTCUTS = {
    'home': 'home',
    'sethome': 'sethome {name}',
    'spawn': 'spawn',
    'setspawn': 'setspawn',
    'warp': 'warp {name}',
    'setwarp': 'setwarp {name}',
    'delwarp': 'delwarp {name}',
    'tpaccept': 'tpaccept',
    'tpdeny': 'tpdeny',
    'tphere': 'tphere {player}',
    'back': 'back',
    'msg': 'msg {player} {message}',
    'r': 'r {message}',
    'broadcast': 'broadcast {message}',
    'bc': 'broadcast {message}'
}

# Command descriptions for help system
COMMAND_DESCRIPTIONS = {
    'list': 'Shows all online players',
    'plugins': 'Lists all server plugins',
    'whitelist': 'Shows whitelisted players',
    'ban': 'Bans a player from the server',
    'kick': 'Kicks a player from the server',
    'op': 'Gives operator permissions to a player',
    'deop': 'Removes operator permissions from a player',
    'gamemode': 'Changes a player\'s gamemode',
    'tp': 'Teleports one player to another',
    'give': 'Gives items to a player',
    'weather': 'Changes the weather (clear, rain, thunder)',
    'time': 'Changes the time of day',
    'save-all': 'Saves the world',
    'reload': 'Reloads server configuration',
    'restart': 'Restarts the server',
    'stop': 'Stops the server'
}
