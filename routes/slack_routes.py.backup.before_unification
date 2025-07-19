"""
Slack integration routes
"""
import logging
from flask import Blueprint, request, jsonify
from utils.security import verify_slack_signature, is_admin_user
from utils.server_utils import get_server_info
from utils.context_manager import (get_user_context, set_user_context, clear_user_context,
                                 get_user_default_server, set_user_default_server)
from modules.command_processor import (execute_rcon_command, process_command_alias, 
                                     execute_context_command, execute_config_command,
                                     validate_command_safety)
from modules.backup_manager import process_backup_command
from config.settings import SERVERS

logger = logging.getLogger(__name__)
slack_bp = Blueprint('slack', __name__)

@slack_bp.route('/slack/mc', methods=['POST'])
@verify_slack_signature
def slack_mc():
    """Handle Minecraft commands from Slack"""
    user_name = request.form.get('user_name', 'unknown')
    text = request.form.get('text', '').strip()
    
    logger.info(f"Slack command from {user_name}: {text}")
    
    # Check if user has an active context
    context = get_user_context(user_name)
    if context:
        return execute_context_command(text, user_name)
    
    if not text:
        help_text = """🎮 **Minecraft RCON Commands - Quick Start**

**🚀 Getting Started:**
• `/mc help` - Complete command guide with examples
• `/mc servers` - List all available servers  
• `/mc list` - Show online players on your default server

**⚡ Quick Commands:**
• `/mc <command>` - Execute on your default server
• `/mc <server_id> <command>` - Execute on specific server

**🎯 Popular Commands:**
• `/mc gamemode creative PlayerName` - Change gamemode
• `/mc give PlayerName diamond 64` - Give items
• `/mc tp Player1 Player2` - Teleport players
• `/mc weather clear` - Clear weather

**🔧 Setup:**
• `/mc setdefault <server_id>` - Set your preferred server
• `/mc servers` - See server IDs and names

**💡 Pro Tip:** Use `/mc help` for the complete command reference with examples!"""
        
        return jsonify({
            'response_type': 'ephemeral',
            'text': help_text
        })
    
    # Handle special commands
    if text.lower() == 'servers':
        return handle_servers_command(user_name)
    elif text.lower() == 'help':
        return handle_help_command()
    elif text.lower().startswith('setdefault '):
        return handle_set_default_command(user_name, text)
    elif text.lower().startswith('config'):
        return handle_config_command(user_name, text)
    
    # Parse command
    parts = text.split()
    
    # Check if first part is a server ID
    if len(parts) >= 2 and parts[0] in SERVERS:
        server_id = parts[0]
        command = ' '.join(parts[1:])
    else:
        # Use default server
        server_id = get_user_default_server(user_name)
        command = text
        
        if not server_id:
            # No default server set, need to choose
            return prompt_server_selection(user_name, command)
    
    # Validate server
    if server_id not in SERVERS:
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Invalid server ID: `{server_id}`. Use `/mc servers` to see available servers.'
        })
    
    # Process command
    processed_command, error = process_command_alias(command, user_name)
    if error:
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ {error}'
        })
    
    # Validate command safety
    is_safe, safety_error = validate_command_safety(processed_command, user_name)
    if not is_safe:
        return jsonify({
            'response_type': 'ephemeral',
            'text': safety_error
        })
    
    # Execute command
    result = execute_rcon_command(server_id, processed_command, f"Slack User: {user_name}")
    server_info = get_server_info(server_id)
    
    return jsonify({
        'response_type': 'in_channel',
        'text': f"**Server: {server_info['name']}**\n```\n{result}\n```"
    })

def handle_servers_command(user_name):
    """Handle servers list command"""
    server_list = "👾 **Available Servers**\n\n"
    default_server = get_user_default_server(user_name)
    
    for server_id in SERVERS.keys():
        server_info = get_server_info(server_id)
        if server_info:
            default_indicator = " ⭐ (default)" if server_id == default_server else ""
            server_list += f"**{server_info['name']}**{default_indicator}\nID: `{server_id}`\nPort: {server_info['port']}\n\n"
    
    return jsonify({
        'response_type': 'ephemeral',
        'text': server_list
    })

def handle_help_command():
    """Handle help command with comprehensive documentation"""
    from utils.security import is_admin_user
    from flask import request
    
    user_name = request.form.get('user_name', 'unknown')
    is_admin = is_admin_user(user_name)
    
    # Build comprehensive help text
    help_text = """🎮 **Minecraft RCON Commands - Complete Guide**

**📋 Basic Usage:**
• `/mc <command>` - Execute on your default server
• `/mc <server_id> <command>` - Execute on specific server
• `/mc servers` - List all available servers
• `/mc help` - Show this help menu

**🎯 Quick Commands:**
• `/mc list` - Show online players
• `/mc plugins` - List server plugins
• `/mc save-all` - Save the world
• `/mc weather clear` - Clear weather
• `/mc time set day` - Set time to day

**👤 Player Management:**
• `/mc gamemode creative PlayerName` - Change gamemode
• `/mc tp Player1 Player2` - Teleport players
• `/mc give PlayerName diamond 64` - Give items
• `/mc heal PlayerName` - Heal player
• `/mc op PlayerName` - Give operator status

**🏠 World & Locations (Essentials):**
• `/mc home` - Go to home
• `/mc sethome MyHome` - Set a home location
• `/mc spawn` - Go to spawn
• `/mc warp MyWarp` - Warp to location
• `/mc back` - Return to previous location

**🔐 Permissions (LuckPerms):**
• `/mc lp user PlayerName info` - Show player permissions
• `/mc lp user PlayerName parent add GroupName` - Add to group
• `/mc addgroup PlayerName vip` - Quick add to group
• `/mc promote PlayerName` - Promote in ladder

**🛡️ Moderation:**
• `/mc ban PlayerName` - Ban player
• `/mc kick PlayerName reason` - Kick player
• `/mc whitelist add PlayerName` - Add to whitelist

**⚡ Command Shortcuts:**
• `list`, `online`, `who` → list players
• `pl` → plugins
• `gm <mode> <player>` → gamemode
• `tp <from> <to>` → teleport  
• `give <player> <item> <amount>` → give items
• `ban <player>`, `kick <player>` → moderation"""

    if is_admin:
        help_text += """

**👑 Admin Commands:**
• `/mc config` - Server configuration
• `/mc setdefault <server_id>` - Set default server
• `/backup list` - List servers for backup
• `/backup full <server_id>` - Full backup with cloud upload
• `/backup status` - Show backup activity"""

    help_text += """

**📖 Examples:**
• `/mc gm creative` - Set your gamemode to creative
• `/mc 7eaa7ab6 list` - List players on specific server
• `/mc give Steve diamond_sword 1` - Give Steve a diamond sword
• `/mc sethome base` - Set home called "base"
• `/mc addgroup Alice vip` - Add Alice to VIP group

**💡 Tips:**
• Set a default server: `/mc setdefault 7eaa7ab6`
• Use server names or IDs for targeting
• Most commands work without the `/` prefix
• Use `help` anytime for this guide"""
    
    return jsonify({
        'response_type': 'ephemeral',
        'text': help_text
    })

def handle_set_default_command(user_name, text):
    """Handle set default server command"""
    parts = text.split()
    if len(parts) != 2:
        return jsonify({
            'response_type': 'ephemeral',
            'text': '❌ Usage: `/mc setdefault <server_id>`'
        })
    
    server_id = parts[1]
    if server_id not in SERVERS:
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Invalid server ID: `{server_id}`. Use `/mc servers` to see available servers.'
        })
    
    set_user_default_server(user_name, server_id)
    server_info = get_server_info(server_id)
    
    return jsonify({
        'response_type': 'ephemeral',
        'text': f'✅ Default server set to **{server_info["name"]}** (`{server_id}`)'
    })

def handle_config_command(user_name, text):
    """Handle configuration commands"""
    if not is_admin_user(user_name):
        return jsonify({
            'response_type': 'ephemeral',
            'text': '❌ Configuration commands require admin privileges.'
        })
    
    result = execute_config_command(text, user_name)
    return jsonify({
        'response_type': 'ephemeral',
        'text': result
    })

def prompt_server_selection(user_name, command):
    """Prompt user to select a server"""
    available_servers = list(SERVERS.keys())
    server_list = "🎯 **Choose a server:**\n\n"
    
    for i, server_id in enumerate(available_servers, 1):
        server_info = get_server_info(server_id)
        server_list += f"{i}. **{server_info['name']}** (`{server_id}`)\n"
    
    server_list += "\nEnter the number of your choice, or 'cancel' to abort."
    
    # Set context for server selection
    set_user_context(user_name, 'server_selection', {
        'command': command,
        'servers': available_servers
    })
    
    return jsonify({
        'response_type': 'ephemeral',
        'text': server_list
    })

@slack_bp.route('/slack/players', methods=['POST'])
@verify_slack_signature
def slack_players():
    """Quick player list command"""
    user_name = request.form.get('user_name', 'unknown')
    
    # Get user's default server or prompt for selection
    server_id = get_user_default_server(user_name)
    if not server_id:
        return prompt_server_selection(user_name, 'list')
    
    result = execute_rcon_command(server_id, 'list', f"Slack User: {user_name}")
    server_info = get_server_info(server_id)
    
    return jsonify({
        'response_type': 'in_channel',
        'text': f"**👥 Players on {server_info['name']}:**\n```\n{result}\n```"
    })

@slack_bp.route('/slack/servers', methods=['POST'])
@verify_slack_signature
def slack_servers():
    """List servers command"""
    user_name = request.form.get('user_name', 'unknown')
    return handle_servers_command(user_name)

@slack_bp.route('/slack/backup', methods=['POST'])
@verify_slack_signature
def slack_backup():
    """Handle backup commands from Slack"""
    user_name = request.form.get('user_name', 'unknown')
    text = request.form.get('text', '').strip()
    
    logger.info(f"Backup command from {user_name}: {text}")
    return process_backup_command(user_name, text)
