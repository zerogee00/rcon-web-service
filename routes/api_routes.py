"""
API routes for direct API access
"""
import logging
from flask import Blueprint, request, jsonify
from utils.security import verify_api_token
from utils.server_utils import get_server_info
from modules.command_processor import (execute_rcon_command, process_command_alias, 
                                     validate_command_safety)
from config.settings import SERVERS

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': __import__('time').time()})

@api_bp.route('/servers', methods=['GET'])
@verify_api_token
def list_servers():
    """List all configured servers"""
    servers_info = []
    for server_id in SERVERS.keys():
        server_info = get_server_info(server_id)
        if server_info:
            # Don't include password in API response
            safe_info = {k: v for k, v in server_info.items() if k != 'password'}
            servers_info.append(safe_info)
    
    return jsonify({'servers': servers_info})

@api_bp.route('/mc', methods=['POST'])
@verify_api_token
def execute_rcon():
    """Execute RCON command via API"""
    data = request.get_json()
    
    if not data or 'command' not in data:
        return jsonify({'error': 'Missing command parameter'}), 400
    
    server_id = data.get('server_id')
    command = data.get('command')
    source = data.get('source', 'API')
    
    if not server_id:
        return jsonify({'error': 'Missing server_id parameter'}), 400
    
    if server_id not in SERVERS:
        return jsonify({'error': f'Invalid server_id: {server_id}'}), 400
    
    # Process command aliases
    processed_command, error = process_command_alias(command, "api_user")
    if error:
        return jsonify({'error': error}), 400
    
    # Validate command safety
    is_safe, safety_error = validate_command_safety(processed_command, "api_user")
    if not is_safe:
        return jsonify({'error': safety_error}), 403
    
    # Execute command
    result = execute_rcon_command(server_id, processed_command, f"API: {source}")
    
    return jsonify({
        'server_id': server_id,
        'original_command': command,
        'processed_command': processed_command,
        'result': result
    })
