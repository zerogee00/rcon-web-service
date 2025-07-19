"""
Server management utilities
"""
import os
import json
import logging
from config.settings import SERVERS, PUFFERPANEL_SERVER_ROOT

logger = logging.getLogger(__name__)

def clean_output_text(text):
    """Clean RCON output text from Minecraft formatting codes and control characters"""
    if not text:
        return ""
    
    import re
    # Remove ANSI escape sequences
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    # Remove Minecraft color codes (§ followed by a character)
    text = re.sub(r'§[0-9a-fk-or]', '', text)
    # Remove other control characters but keep newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()
    
    return text

def get_server_display_name(server_id):
    """Get server display name from PufferPanel configuration or server.properties"""
    display_name = ""
    
    # Try to get MOTD from PufferPanel JSON first (more specific)
    pufferpanel_config = os.path.join(PUFFERPANEL_SERVER_ROOT, f"{server_id}.json")
    if os.path.exists(pufferpanel_config):
        try:
            with open(pufferpanel_config, 'r') as f:
                config = json.load(f)
                display_name = config.get('data', {}).get('motd', {}).get('value', '')
                # Clean up Minecraft formatting codes, quotes, and spaces
                if display_name:
                    import re
                    display_name = re.sub(r'§[0-9a-fA-F]', '', display_name)
                    display_name = display_name.strip().strip('"\'')[:40]
        except (json.JSONDecodeError, KeyError, IOError) as e:
            logger.debug(f"Could not read PufferPanel config for {server_id}: {e}")
    
    # If no MOTD found, try to get display name from PufferPanel JSON
    if not display_name and os.path.exists(pufferpanel_config):
        try:
            with open(pufferpanel_config, 'r') as f:
                config = json.load(f)
                display_name = config.get('display', '').strip()
        except (json.JSONDecodeError, KeyError, IOError) as e:
            logger.debug(f"Could not read display name for {server_id}: {e}")
    
    # If still no name, try to get MOTD from server.properties
    if not display_name:
        server_properties = os.path.join(PUFFERPANEL_SERVER_ROOT, server_id, "server.properties")
        if os.path.exists(server_properties):
            try:
                with open(server_properties, 'r') as f:
                    for line in f:
                        if line.startswith('motd='):
                            motd = line.split('=', 1)[1].strip()
                            import re
                            display_name = re.sub(r'§[0-9a-fA-F]', '', motd)
                            display_name = display_name.strip()[:40]
                            break
            except IOError as e:
                logger.debug(f"Could not read server.properties for {server_id}: {e}")
    
    # If still no name, use server ID
    if not display_name:
        display_name = server_id
    
    return display_name

def get_server_info(server_id):
    """Get comprehensive server information"""
    if server_id not in SERVERS:
        return None
    
    server_config = SERVERS[server_id]
    display_name = get_server_display_name(server_id)
    
    return {
        'id': server_id,
        'name': display_name,
        'port': server_config['port'],
        'password': server_config['password']
    }

def validate_server_id(server_id):
    """Validate that server ID exists in configuration"""
    return server_id in SERVERS

def get_server_directory(server_id):
    """Get the full path to a server's directory"""
    return os.path.join(PUFFERPANEL_SERVER_ROOT, server_id)

def server_exists(server_id):
    """Check if server directory actually exists"""
    server_dir = get_server_directory(server_id)
    return os.path.isdir(server_dir)
