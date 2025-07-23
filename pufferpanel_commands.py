#!/usr/bin/env python3
"""
PufferPanel command integration for Slack slash commands
"""

import sys
sys.path.append('/root/rcon-web-service')

from flask import jsonify
import logging
import sys; sys.path.append("/root/rcon-web-service"); from utils.pufferpanel_integration import list_servers, get_server_info, control_server, get_server_logs, backup_server
from utils.context_manager import get_user_default_server, set_user_default_server

logger = logging.getLogger(__name__)

def prompt_server_selection_for_control(user_name, command, original_action):
    """Prompt user to select a server for control commands and set context"""
    from utils.context_manager import set_user_context
    
    # Get available servers from PufferPanel
    servers = list_servers()
    if not servers:
        return jsonify({
            'response_type': 'ephemeral',
            'text': '❌ No servers found'
        })
    
    server_list = f"🎯 *Choose a server to {original_action}:*\n\n"
    
    for i, server in enumerate(servers, 1):
        status_icon = "🟢" if server['running'] else "🔴"
        server_list += f"{i}. {status_icon} *{server['name']}* (`{server['id']}`)\n"
    
    server_list += f"\n💡 *Next:* Reply with the *number* of your choice (e.g., `1`, `2`, etc.)"
    server_list += f"\n🧠 I'll remember your choice for future commands!"
    
    # Set context for this selection
    set_user_context(user_name, 'server_selection', {
        'command': command,
        'servers': [s['id'] for s in servers],
        'action': original_action
    }, timeout_minutes=5)
    
    return jsonify({
        'response_type': 'ephemeral',
        'text': server_list
    })

def handle_status_command(user_name):
    """Handle server status command"""
    try:
        servers = list_servers()
        if not servers:
            return jsonify({
                'response_type': 'ephemeral',
                'text': '❌ No servers found'
            })
        
        status_text = "🎮 *Server Status Overview:*\n\n"
        running_count = 0
        
        for server in servers:
            status_icon = "🟢" if server['running'] else "🔴"
            status_text += f"{status_icon} *{server['name']}* (`{server['id']}`)\n"
            
            if server['running']:
                running_count += 1
                if server.get('pid'):
                    status_text += f"   └── PID: {server['pid']}"
                if 'resources' in server:
                    res = server['resources']
                    status_text += f", CPU: {res.get('cpu_percent', 0):.1f}%, RAM: {res.get('memory_mb', 0):.0f}MB"
                status_text += "\n"
            status_text += "\n"
        
        status_text += f"\n📊 *Summary:* {running_count}/{len(servers)} servers running"
        
        return jsonify({
            'response_type': 'in_channel',
            'text': status_text
        })
        
    except Exception as e:
        logger.error(f"Error in status command: {e}")
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error getting server status: {str(e)}'
        })

def handle_server_control_command(user_name, text):
    """Handle server control commands (start/stop/restart) with default server support"""
    try:
        parts = text.split()
        if len(parts) < 1:
            return jsonify({
                'response_type': 'ephemeral',
                'text': '❌ Usage: `start [server_id]`, `stop [server_id]`, or `restart [server_id]`'
            })
        
        action = parts[0].lower()
        
        if action not in ['start', 'stop', 'restart', 'kill']:
            return jsonify({
                'response_type': 'ephemeral',
                'text': '❌ Invalid action. Use: start, stop, restart, or kill'
            })
        
        # Check if server_id is provided
        if len(parts) >= 2:
            server_id = parts[1]
            # Update their default server for convenience
            set_user_default_server(user_name, server_id)
        else:
            # Use default server
            server_id = get_user_default_server(user_name)
            
            if not server_id:
                # No default server set, need to choose
                return prompt_server_selection_for_control(user_name, text, action)
        
        # Check if server exists
        server_info = get_server_info(server_id)
        if not server_info:
            return jsonify({
                'response_type': 'ephemeral',
                'text': f'❌ Server `{server_id}` not found'
            })
        
        # Perform the action
        success = control_server(server_id, action, user_name)
        
        if success:
            action_icons = {
                'start': '🟢',
                'stop': '🔴', 
                'restart': '🔄',
                'kill': '💀'
            }
            
            icon = action_icons.get(action, '⚡')
            return jsonify({
                'response_type': 'in_channel',
                'text': f'{icon} Server *{server_info["name"]}* {action}ed successfully by {user_name}'
            })
        else:
            return jsonify({
                'response_type': 'ephemeral',
                'text': f'❌ Failed to {action} server *{server_info["name"]}*'
            })
            
    except Exception as e:
        logger.error(f"Error in server control command: {e}")
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error controlling server: {str(e)}'
        })

def handle_logs_command(user_name, text):
    """Handle server logs command with default server support"""
    try:
        parts = text.split()
        server_id = None
        lines = 10  # default
        
        if len(parts) >= 2:
            # Check if first argument is a server_id or number of lines
            first_arg = parts[1]
            if first_arg.isdigit():
                # It's number of lines, use default server
                server_id = get_user_default_server(user_name)
                lines = int(first_arg)
            else:
                # It's a server_id
                server_id = first_arg
                # Update their default server for convenience
                set_user_default_server(user_name, server_id)
                # Check for lines parameter
                if len(parts) >= 3 and parts[2].isdigit():
                    lines = int(parts[2])
        elif len(parts) == 1:
            # No arguments, use default server
            server_id = get_user_default_server(user_name)
        
        if not server_id:
            # No default server set, need to choose
            return prompt_server_selection_for_control(user_name, text, 'view logs for')
        
        lines = min(lines, 50)  # Limit to 50 lines max
        
        # Check if server exists
        server_info = get_server_info(server_id)
        if not server_info:
            return jsonify({
                'response_type': 'ephemeral',
                'text': f'❌ Server `{server_id}` not found'
            })
        
        # Get logs
        logs = get_server_logs(server_id, lines)
        if not logs:
            return jsonify({
                'response_type': 'ephemeral',
                'text': f'📜 No recent logs found for *{server_info["name"]}*'
            })
        
        # Format logs for Slack
        log_text = f"📜 *Recent logs for {server_info['name']}* (last {len(logs)} lines):\n\n```\n"
        for log_line in logs:
            if log_line.strip():
                log_text += log_line + "\n"
        log_text += "```"
        
        return jsonify({
            'response_type': 'ephemeral',
            'text': log_text
        })
        
    except Exception as e:
        logger.error(f"Error in logs command: {e}")
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error getting logs: {str(e)}'
        })

# Test the functions
if __name__ == "__main__":
    print("Testing PufferPanel command handlers...")
    
    # Test status
    try:
        result = handle_status_command("TestUser")
        print("✅ Status command working")
    except Exception as e:
        print(f"❌ Status command error: {e}")
    
    print("✅ PufferPanel commands loaded successfully!")
