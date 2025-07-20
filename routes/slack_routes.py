"""
Slack integration routes for RCON Web Service
"""
import logging
from flask import Blueprint, request, jsonify
from config.settings import SERVERS
from modules.command_processor import execute_rcon_command, get_server_info, process_command_alias
from utils.context_manager import (
    get_user_default_server, set_user_default_server, 
    get_user_context, set_user_context, clear_user_context
)

logger = logging.getLogger(__name__)
slack_bp = Blueprint('slack', __name__)

def handle_help_command():
    """Handle help command with enhanced context information"""
    help_text = """🎮 *Minecraft RCON Commands*

*Basic Usage:*
• `/mc <command>` - Run command on your default server
• `/mc <server_id> <command>` - Run command on specific server  
• `/mc servers` - List all available servers
• `/mc help` - Show this help

*Server Selection:*
When you don't have a default server, I'll guide you through selecting one and remember it for future commands.

*Popular Commands:*
• `list` - Show online players
• `say <message>` - Broadcast message to server  
• `tp <player1> <player2>` - Teleport player1 to player2
• `gamemode <mode> <player>` - Change player's game mode
• `time set <time>` - Set server time (day, night, etc.)
• `weather <weather>` - Set weather (clear, rain, thunder)
• `seed` - Show world seed

*Examples:*
• List players: `/mc list`
• Broadcast message: `/mc say Server restart in 5 minutes!`
• Change time: `/mc time set day`

*Context-Aware Features:*
• 🧠 I remember your preferred server across commands
• ⏱️ Context expires after 5 minutes of inactivity
• 🔄 I'll prompt you to choose again when needed"""

    return jsonify({
        'response_type': 'ephemeral',
        'text': help_text
    })

def handle_servers_command(user_name):
    """Handle servers list command with context awareness"""
    server_list = "🎯 *Available Minecraft Servers:*\n\n"
    
    default_server = get_user_default_server(user_name)
    
    for server_id, config in SERVERS.items():
        server_info = get_server_info(server_id)
        status_indicator = "✅" if default_server == server_id else "⚪"
        server_list += f"{status_indicator} *{server_info['name']}* (`{server_id}`) - localhost:{config['port']}\n"
    
    if default_server:
        server_info = get_server_info(default_server)
        server_list += f"\n💡 Your current default: *{server_info['name']}* (`{default_server}`)"
    else:
        server_list += "\n💡 No default server set. Use any server ID with commands or I'll help you choose one."
    
    return jsonify({
        'response_type': 'ephemeral',
        'text': server_list
    })

def handle_config_command(user_name, text):
    """Handle configuration commands"""
    parts = text.split()
    
    if len(parts) == 1:
        # Show current config
        default_server = get_user_default_server(user_name)
        context = get_user_context(user_name)
        
        config_text = "⚙️ *Your Configuration:*\n\n"
        
        if default_server:
            server_info = get_server_info(default_server)
            config_text += f"🎯 *Default Server:* {server_info['name']} (`{default_server}`)\n"
        else:
            config_text += "🎯 *Default Server:* Not set\n"
        
        if context:
            config_text += f"🧠 *Active Context:* {context['type']} (expires in a few minutes)\n"
        else:
            config_text += "🧠 *Active Context:* None\n"
        
        config_text += "\n*Commands:*\n"
        config_text += "• `config clear` - Clear your default server\n"
        config_text += "• `config reset` - Reset all your settings\n"
        
        return jsonify({
            'response_type': 'ephemeral',
            'text': config_text
        })
    
    elif len(parts) == 2:
        action = parts[1].lower()
        
        if action == 'clear':
            set_user_default_server(user_name, None)
            clear_user_context(user_name)
            return jsonify({
                'response_type': 'ephemeral',
                'text': '✅ Default server cleared. I\'ll prompt you to choose for your next command.'
            })
        
        elif action == 'reset':
            set_user_default_server(user_name, None)
            clear_user_context(user_name)
            return jsonify({
                'response_type': 'ephemeral',
                'text': '✅ All settings reset. Starting fresh!'
            })
    
    return jsonify({
        'response_type': 'ephemeral',
        'text': '❌ Usage: `config`, `config clear`, or `config reset`'
    })

@slack_bp.route('/slack/commands', methods=['POST'])
def handle_slack_command():
    """Handle incoming Slack slash commands with unified context system"""
    try:
        user_name = request.form.get('user_name', 'unknown')
        text = request.form.get('text', '').strip()
        
        logger.info(f"Slack command from {user_name}: '{text}'")
        
        if not text:
            return handle_help_command()
        
        # Handle special commands
        if text.lower() == 'servers':
            return handle_servers_command(user_name)
        elif text.lower() == 'help':
            return handle_help_command()
        elif text.lower().startswith('config'):
            return handle_config_command(user_name, text)
        
        # Check for pending context (user was in middle of server selection)
        context = get_user_context(user_name)
        if context and context['type'] == 'server_selection':
            return handle_server_selection_response(user_name, text, context)
        
        # Parse command
        parts = text.split()
        
        # Check if first part is a server ID
        if len(parts) >= 2 and parts[0] in SERVERS:
            server_id = parts[0]
            command = ' '.join(parts[1:])
            # Update their default server for convenience
            set_user_default_server(user_name, server_id)
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
        
        # Execute command
        result = execute_rcon_command(server_id, processed_command, f"Slack User: {user_name}")
        server_info = get_server_info(server_id)
        
        # Format response
        if processed_command.lower() in ['list', 'who']:
            response_text = f"*👥 Players on {server_info['name']}:*\n```\n{result}\n```"
        else:
            response_text = f"*🎮 {server_info['name']}* - Command: `{processed_command}`\n```\n{result}\n```"
        
        return jsonify({
            'response_type': 'in_channel',
            'text': response_text
        })
        
    except Exception as e:
        logger.error(f"Error handling Slack command: {e}")
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error: {str(e)}'
        })

def prompt_server_selection(user_name, command):
    """Prompt user to select a server and set context"""
    available_servers = list(SERVERS.keys())
    server_list = "🎯 *Choose a server:*\n\n"
    
    for i, server_id in enumerate(available_servers, 1):
        server_info = get_server_info(server_id)
        server_list += f"{i}. *{server_info['name']}* (`{server_id}`)\n"
    
    server_list += "\n💡 *Next:* Reply with the *number* of your choice (e.g., `1`, `2`, etc.)"
    server_list += "\n🧠 I'll remember your choice for future commands!"
    
    # Set context for this selection
    set_user_context(user_name, 'server_selection', {
        'command': command,
        'servers': available_servers
    }, timeout_minutes=5)
    
    return jsonify({
        'response_type': 'ephemeral',
        'text': server_list
    })

def handle_server_selection_response(user_name, text, context):
    """Handle user's response to server selection"""
    try:
        choice = int(text.strip())
        available_servers = context['data']['servers']
        original_command = context['data']['command']
        
        if 1 <= choice <= len(available_servers):
            selected_server_id = available_servers[choice - 1]
            
            # Set as their default server
            set_user_default_server(user_name, selected_server_id)
            
            # Clear the selection context
            clear_user_context(user_name)
            
            # Execute the original command
            processed_command, error = process_command_alias(original_command, user_name)
            if error:
                return jsonify({
                    'response_type': 'ephemeral',
                    'text': f'❌ {error}'
                })
            
            result = execute_rcon_command(selected_server_id, processed_command, f"Slack User: {user_name}")
            server_info = get_server_info(selected_server_id)
            
            # Format response with confirmation
            response_text = f"✅ *Server set to {server_info['name']}* (I'll remember this!)\n\n"
            
            if processed_command.lower() in ['list', 'who']:
                response_text += f"*👥 Players on {server_info['name']}:*\n```\n{result}\n```"
            else:
                response_text += f"*🎮 {server_info['name']}* - Command: `{processed_command}`\n```\n{result}\n```"
            
            return jsonify({
                'response_type': 'in_channel',
                'text': response_text
            })
        else:
            return jsonify({
                'response_type': 'ephemeral',
                'text': f'❌ Invalid choice. Please enter a number between 1 and {len(available_servers)}.'
            })
            
    except ValueError:
        if text.lower() in ['cancel', 'abort', 'exit']:
            clear_user_context(user_name)
            return jsonify({
                'response_type': 'ephemeral',
                'text': '❌ Server selection cancelled.'
            })
        
        return jsonify({
            'response_type': 'ephemeral',
            'text': '❌ Please enter a number, or "cancel" to abort.'
        })

@slack_bp.route('/slack/players', methods=['POST'])
def handle_players_command():
    """Handle players list command"""
    try:
        user_name = request.form.get('user_name', 'unknown')
        
        # Get user's default server or prompt for selection
        server_id = get_user_default_server(user_name)
        if not server_id:
            return prompt_server_selection(user_name, 'list')
        
        result = execute_rcon_command(server_id, 'list', f"Slack User: {user_name}")
        server_info = get_server_info(server_id)
        
        return jsonify({
            'response_type': 'in_channel',
            'text': f"*👥 Players on {server_info['name']}:*\n```\n{result}\n```"
        })
        
    except Exception as e:
        logger.error(f"Error in players command: {e}")
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error: {str(e)}'
        })

@slack_bp.route('/slack/servers', methods=['POST'])
def handle_servers_endpoint():
    """Handle servers list endpoint"""
    try:
        user_name = request.form.get('user_name', 'unknown')
        return handle_servers_command(user_name)
    except Exception as e:
        logger.error(f"Error in servers endpoint: {e}")
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error: {str(e)}'
        })

@slack_bp.route('/slack/mc', methods=['POST'])
def handle_mc_command():
    """Handle /mc slash command - redirect to main handler"""
    return handle_slack_command()

@slack_bp.route('/slack/backup', methods=['POST'])
def handle_backup_command():
    """Handle /backup slash command - redirect to backup processor"""
    from modules.backup_manager import process_backup_command
    user_name = request.form.get('user_name', 'unknown')
    text = request.form.get('text', '').strip()
    
    logger.info(f"Backup command from {user_name}: '{text}'")
    return process_backup_command(user_name, text)
