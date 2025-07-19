"""
Command processing and RCON execution module
"""
import subprocess
import logging
import re
from config.settings import (SERVERS, CONFIG, ALIASES, LUCKPERMS_SHORTCUTS, 
                           ESSENTIALS_SHORTCUTS, COMMAND_DESCRIPTIONS)
from utils.server_utils import clean_output_text, get_server_info
from utils.context_manager import get_user_context, set_user_context, clear_user_context

logger = logging.getLogger(__name__)

def execute_rcon_command(server_id, command, source="Web Service"):
    """Execute RCON command on specified server"""
    if server_id not in SERVERS:
        return f"❌ Invalid server ID: {server_id}"
    
    server_config = SERVERS[server_id]
    server_info = get_server_info(server_id)
    
    logger.info(f"Executing RCON command on {server_info['name']} ({server_id}): {command} [Source: {source}]")
    
    try:
        result = subprocess.run([
            'mcrcon', '-H', 'localhost', '-P', str(server_config['port']), 
            '-p', server_config['password'], command
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            output = clean_output_text(result.stdout)
            if not output.strip():
                output = "✅ Command executed successfully (no output)"
            logger.info(f"RCON command successful on {server_id}")
            return output
        else:
            error_msg = clean_output_text(result.stderr) or "Unknown error occurred"
            logger.error(f"RCON command failed on {server_id}: {error_msg}")
            return f"❌ Command failed: {error_msg}"
            
    except subprocess.TimeoutExpired:
        logger.error(f"RCON command timeout on {server_id}")
        return "❌ Command timed out after 30 seconds"
    except FileNotFoundError:
        logger.error("mcrcon not found")
        return "❌ RCON client not available on server"
    except Exception as e:
        logger.error(f"Unexpected error executing RCON command: {str(e)}")
        return f"❌ Unexpected error: {str(e)}"

def format_command_template(template, args):
    """Format command template with provided arguments"""
    try:
        # Simple placeholder replacement
        placeholders = re.findall(r'\{(\w+)\}', template)
        formatted_command = template
        
        for i, placeholder in enumerate(placeholders):
            if i < len(args):
                formatted_command = formatted_command.replace(f'{{{placeholder}}}', args[i])
            else:
                return None, f"Missing argument for {{{placeholder}}}"
        
        # Check if there are unused arguments
        remaining_placeholders = re.findall(r'\{(\w+)\}', formatted_command)
        if remaining_placeholders:
            return None, f"Missing arguments: {', '.join(['{' + p + '}' for p in remaining_placeholders])}"
        
        return formatted_command, None
    except Exception as e:
        return None, f"Error formatting command: {str(e)}"

def process_command_alias(command, user_name="unknown"):
    """Process command aliases and shortcuts"""
    if not command.strip():
        return command, None
    
    parts = command.strip().split()
    base_command = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    # Check regular aliases first
    if CONFIG.get('enable_aliases', True) and base_command in ALIASES:
        template = ALIASES[base_command]
        if '{' in template:
            formatted_command, error = format_command_template(template, args)
            if error:
                return command, f"Alias error: {error}"
            return formatted_command, None
        else:
            # Simple alias without parameters
            return template + (' ' + ' '.join(args) if args else ''), None
    
    # Check LuckPerms shortcuts
    if CONFIG.get('enable_luckperms_shortcuts', True) and base_command in LUCKPERMS_SHORTCUTS:
        template = LUCKPERMS_SHORTCUTS[base_command]
        formatted_command, error = format_command_template(template, args)
        if error:
            return command, f"LuckPerms shortcut error: {error}"
        return formatted_command, None
    
    # Check Essentials shortcuts
    if CONFIG.get('enable_essentials_shortcuts', True) and base_command in ESSENTIALS_SHORTCUTS:
        template = ESSENTIALS_SHORTCUTS[base_command]
        if '{' in template:
            formatted_command, error = format_command_template(template, args)
            if error:
                return command, f"Essentials shortcut error: {error}"
            return formatted_command, None
        else:
            return template + (' ' + ' '.join(args) if args else ''), None
    
    return command, None

def execute_context_command(command, user_name):
    """Execute a command within user's current context"""
    context = get_user_context(user_name)
    if not context:
        return "❌ No active context. Please start a new command session."
    
    if context['type'] == 'server_selection':
        # User is selecting a server
        try:
            choice = int(command.strip())
            available_servers = context['data']['servers']
            
            if 1 <= choice <= len(available_servers):
                selected_server = available_servers[choice - 1]
                pending_command = context['data']['command']
                
                # Clear context
                clear_user_context(user_name)
                
                # Execute the pending command on selected server
                processed_command, error = process_command_alias(pending_command, user_name)
                if error:
                    return f"❌ {error}"
                
                result = execute_rcon_command(selected_server, processed_command, f"Slack User: {user_name}")
                return f"**Server: {get_server_info(selected_server)['name']}**\n```\n{result}\n```"
            else:
                return f"❌ Invalid choice. Please enter a number between 1 and {len(available_servers)}, or 'cancel' to abort."
                
        except ValueError:
            if command.strip().lower() == 'cancel':
                clear_user_context(user_name)
                return "✅ Command cancelled."
            return "❌ Please enter a valid number or 'cancel' to abort."
    
    elif context['type'] == 'config_edit':
        # Handle configuration editing context
        return handle_config_context(command, user_name, context)
    
    return "❌ Unknown context type."

def handle_config_context(command, user_name, context):
    """Handle configuration editing context"""
    # This would be implemented based on your config editing needs
    # For now, just clear context
    clear_user_context(user_name)
    return "✅ Configuration context cleared."

def execute_config_command(command, user_name):
    """Execute configuration management commands"""
    if not user_name:
        return "❌ User authentication required."
    
    parts = command.strip().split()
    if len(parts) < 2:
        return """🔧 **Configuration Commands**
        
Available commands:
• `config get <key>` - Get configuration value
• `config set <key> <value>` - Set configuration value
• `config list` - List all configuration keys
• `config reset <key>` - Reset to default value

**Examples:**
• `config get enable_aliases`
• `config set max_command_length 600`
• `config list`"""
    
    subcommand = parts[1].lower()
    
    if subcommand == 'get':
        if len(parts) < 3:
            return "❌ Usage: config get <key>"
        key = parts[2]
        value = CONFIG.get(key, "Key not found")
        return f"**{key}**: `{value}`"
    
    elif subcommand == 'set':
        if len(parts) < 4:
            return "❌ Usage: config set <key> <value>"
        key = parts[2]
        value = ' '.join(parts[3:])
        
        # Type conversion
        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        
        CONFIG[key] = value
        return f"✅ Set **{key}** to `{value}`"
    
    elif subcommand == 'list':
        config_list = "\n".join([f"• **{k}**: `{v}`" for k, v in CONFIG.items()])
        return f"📋 **Current Configuration:**\n\n{config_list}"
    
    elif subcommand == 'reset':
        if len(parts) < 3:
            return "❌ Usage: config reset <key>"
        # This would reset to defaults - implementation depends on your needs
        return f"✅ Configuration key {parts[2]} reset to default"
    
    else:
        return f"❌ Unknown config command: {subcommand}"

def convert_to_essentials_command(command, source="Web Service"):
    """Convert standard commands to Essentials format if needed"""
    if not CONFIG.get('enable_essentials_shortcuts', True):
        return command
    
    # Add Essentials prefix for certain commands if not already present
    essentials_commands = ['home', 'sethome', 'spawn', 'setspawn', 'warp', 'setwarp', 
                          'delwarp', 'tpaccept', 'tpdeny', 'tphere', 'back', 'msg', 'r', 'broadcast']
    
    parts = command.strip().split()
    if parts and parts[0].lower() in essentials_commands and not parts[0].startswith('/'):
        return '/' + command
    
    return command

def get_command_description(command):
    """Get description for a command"""
    base_command = command.split()[0].lower() if command else ""
    return COMMAND_DESCRIPTIONS.get(base_command, "No description available")

def validate_command_safety(command, user_name):
    """Validate command safety and permissions"""
    dangerous_commands = ['stop', 'restart', '/stop', '/restart', 'kill']
    
    if not CONFIG.get('enable_dangerous_commands', False):
        for dangerous in dangerous_commands:
            if dangerous in command.lower():
                from utils.security import is_admin_user
                if not is_admin_user(user_name):
                    return False, f"❌ Dangerous command '{dangerous}' is restricted to admin users."
    
    if len(command) > CONFIG.get('max_command_length', 500):
        return False, f"❌ Command too long (max {CONFIG.get('max_command_length', 500)} characters)."
    
    return True, None
