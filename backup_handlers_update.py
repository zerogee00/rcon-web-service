def handle_incremental_backup(user_name, server_id=None):
    """Handle incremental backup request"""
    try:
        if server_id:
            # Validate server_id
            if server_id not in SERVERS:
                return jsonify({
                    'response_type': 'ephemeral',
                    'text': f'❌ Invalid server ID: `{server_id}`. Use `/backup list` to see available servers.'
                })
            
            # Single server incremental backup using wrapper script
            backup_script = os.path.join(os.path.dirname(__file__), 'backup_single_server.sh')
            if not os.path.exists(backup_script):
                return jsonify({
                    'response_type': 'ephemeral',
                    'text': '❌ Single server backup script not found.'
                })
            
            subprocess.Popen([backup_script, server_id, 'incremental'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
            
            server_info = get_server_info(server_id)
            server_name = server_info['name'] if server_info else server_id
            response_text = f"🚀 Starting incremental backup for **{server_name}** (`{server_id}`)...\\n\\nThis will run in the background. Check logs for completion status."
        else:
            # All servers incremental backup (default behavior)
            backup_script = os.path.join(os.path.dirname(__file__), 'backup.sh')
            if not os.path.exists(backup_script):
                backup_script = '/var/lib/pufferpanel/backup.sh'
            
            if not os.path.exists(backup_script):
                return jsonify({
                    'response_type': 'ephemeral',
                    'text': '❌ Backup script not found. Please ensure backup.sh is available.'
                })
            
            subprocess.Popen([backup_script], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
            
            response_text = "🚀 Starting incremental backup for all servers...\\n\\nThis will run in the background. Check logs for completion status."
        
        logger.info(f"Incremental backup started by {user_name} for server: {server_id or 'all'}")
        
        return jsonify({
            'response_type': 'in_channel',
            'text': response_text
        })
        
    except Exception as e:
        logger.error(f"Error starting incremental backup: {str(e)}")
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error starting backup: {str(e)}'
        })

def handle_full_backup(user_name, server_id=None):
    """Handle full backup request"""
    try:
        if server_id:
            # Validate server_id
            if server_id not in SERVERS:
                return jsonify({
                    'response_type': 'ephemeral',
                    'text': f'❌ Invalid server ID: `{server_id}`. Use `/backup list` to see available servers.'
                })
            
            # Single server full backup using wrapper script
            backup_script = os.path.join(os.path.dirname(__file__), 'backup_single_server.sh')
            if not os.path.exists(backup_script):
                return jsonify({
                    'response_type': 'ephemeral',
                    'text': '❌ Single server backup script not found.'
                })
            
            subprocess.Popen([backup_script, server_id, 'full'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
            
            server_info = get_server_info(server_id)
            server_name = server_info['name'] if server_info else server_id
            response_text = f"🚀 Starting full backup with cloud upload for **{server_name}** (`{server_id}`)...\\n\\nThis will run in the background and may take several minutes."
        else:
            # All servers full backup using interactive mode
            backup_script = os.path.join(os.path.dirname(__file__), 'backup.sh')
            if not os.path.exists(backup_script):
                backup_script = '/var/lib/pufferpanel/backup.sh'
            
            if not os.path.exists(backup_script):
                return jsonify({
                    'response_type': 'ephemeral',
                    'text': '❌ Backup script not found. Please ensure backup.sh is available.'
                })
            
            # Create a temporary script to simulate interactive mode selection for "all servers"
            temp_input = f"{len(SERVERS)+1}\\n"  # Select "ALL" option
            process = subprocess.Popen([backup_script, '--interactive'], 
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL,
                                     start_new_session=True,
                                     text=True)
            process.stdin.write(temp_input)
            process.stdin.close()
            
            response_text = "🚀 Starting full backup with cloud upload for all servers...\\n\\nThis will run in the background and may take several minutes."
        
        logger.info(f"Full backup started by {user_name} for server: {server_id or 'all'}")
        
        return jsonify({
            'response_type': 'in_channel',
            'text': response_text
        })
        
    except Exception as e:
        logger.error(f"Error starting full backup: {str(e)}")
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error starting backup: {str(e)}'
        })
