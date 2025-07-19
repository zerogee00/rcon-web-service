"""
Backup management module
"""
import os
import re
import subprocess
import logging
from flask import jsonify
from config.settings import SERVERS, BACKUP_CONFIG
from utils.server_utils import get_server_info
from utils.security import is_admin_user

logger = logging.getLogger(__name__)

def handle_backup_list():
    """List all servers available for backup"""
    try:
        server_list = "📋 **Servers Available for Backup**\n\n"
        for server_id in SERVERS.keys():
            server_info = get_server_info(server_id)
            if server_info:
                server_list += f"• **{server_info['name']}** (`{server_id}`)\n"
        
        return jsonify({
            'response_type': 'ephemeral',
            'text': server_list
        })
    except Exception as e:
        logger.error(f"Error listing servers for backup: {str(e)}")
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error listing servers: {str(e)}'
        })

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
            backup_script = os.path.join(os.path.dirname(__file__), '..', 'backup_single_server.sh')
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
            response_text = f"🚀 Starting incremental backup for **{server_name}** (`{server_id}`)...\n\nThis will run in the background. Check logs for completion status."
        else:
            # All servers incremental backup (default behavior)
            backup_script = os.path.join(os.path.dirname(__file__), '..', 'backup.sh')
            if not os.path.exists(backup_script):
                backup_script = BACKUP_CONFIG['backup_script_path']
            
            if not os.path.exists(backup_script):
                return jsonify({
                    'response_type': 'ephemeral',
                    'text': '❌ Backup script not found. Please ensure backup.sh is available.'
                })
            
            subprocess.Popen([backup_script], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
            
            response_text = "🚀 Starting incremental backup for all servers...\n\nThis will run in the background. Check logs for completion status."
        
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
            backup_script = os.path.join(os.path.dirname(__file__), '..', 'backup_single_server.sh')
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
            response_text = f"🚀 Starting full backup with cloud upload for **{server_name}** (`{server_id}`)...\n\nThis will run in the background and may take several minutes."
        else:
            # All servers full backup using interactive mode
            backup_script = os.path.join(os.path.dirname(__file__), '..', 'backup.sh')
            if not os.path.exists(backup_script):
                backup_script = BACKUP_CONFIG['backup_script_path']
            
            if not os.path.exists(backup_script):
                return jsonify({
                    'response_type': 'ephemeral',
                    'text': '❌ Backup script not found. Please ensure backup.sh is available.'
                })
            
            # Create a temporary script to simulate interactive mode selection for "all servers"
            temp_input = f"{len(SERVERS)+1}\n"  # Select "ALL" option
            process = subprocess.Popen([backup_script, '--interactive'], 
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL,
                                     start_new_session=True,
                                     text=True)
            process.stdin.write(temp_input)
            process.stdin.close()
            
            response_text = "🚀 Starting full backup with cloud upload for all servers...\n\nThis will run in the background and may take several minutes."
        
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

def handle_backup_status():
    """Show backup status and recent logs with improved filtering"""
    try:
        log_file = BACKUP_CONFIG['log_file']
        max_lines = BACKUP_CONFIG.get('max_log_lines', 30)
        
        if os.path.exists(log_file):
            # Get more lines to filter from
            result = subprocess.run(['tail', f'-{max_lines * 2}', log_file], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                raw_logs = result.stdout
                
                # Filter out process management noise
                filtered_lines = []
                for line in raw_logs.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Skip technical process messages
                    skip_patterns = [
                        r'Process \d+ dead!',
                        r'Process \d+ detected',
                        r'CPU limit.*Nice.*I/O priority',
                        r'Running CPU-limited.*rsync',
                        r'Nice.*ionice.*cpulimit'
                    ]
                    
                    skip_line = False
                    for pattern in skip_patterns:
                        if re.search(pattern, line):
                            skip_line = True
                            break
                    
                    if not skip_line:
                        filtered_lines.append(line)
                
                # Keep only the most recent entries
                filtered_lines = filtered_lines[-max_lines:] if len(filtered_lines) > max_lines else filtered_lines
                
                if filtered_lines:
                    # Format the output with summary
                    recent_activity = '\n'.join(filtered_lines)
                    
                    # Count recent operations
                    backup_count = len([l for l in filtered_lines if '✅ Incremental backup completed' in l or '✅ Full backup' in l])
                    cleanup_count = len([l for l in filtered_lines if '✅' in l and 'cleanup complete' in l])
                    
                    status_text = f"📊 **Recent Backup Activity**\n\n"
                    
                    if backup_count > 0 or cleanup_count > 0:
                        status_text += f"📈 **Summary:** {backup_count} backup operations, {cleanup_count} cleanup tasks completed\n\n"
                    
                    status_text += f"```\n{recent_activity}\n```"
                else:
                    status_text = "📊 **Recent Backup Activity:**\n\nNo recent backup activity found."
            else:
                status_text = "📊 Unable to read backup log file."
        else:
            status_text = "📊 No backup log file found. No backups have been run yet."
        
        return jsonify({
            'response_type': 'ephemeral',
            'text': status_text
        })
        
    except Exception as e:
        logger.error(f"Error getting backup status: {str(e)}")
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error getting backup status: {str(e)}'
        })
def handle_backup_cleanup(user_name):
    """Handle backup cleanup request"""
    try:
        backup_script = os.path.join(os.path.dirname(__file__), '..', 'backup.sh')
        if not os.path.exists(backup_script):
            backup_script = BACKUP_CONFIG['backup_script_path']
        
        if not os.path.exists(backup_script):
            return jsonify({
                'response_type': 'ephemeral',
                'text': '❌ Backup script not found. Please ensure backup.sh is available.'
            })
        
        # Execute cleanup
        subprocess.Popen([backup_script, '--cleanup-remote'], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL,
                       start_new_session=True)
        
        logger.info(f"Backup cleanup started by {user_name}")
        
        return jsonify({
            'response_type': 'in_channel',
            'text': "🧹 Starting cleanup of old remote backups...\n\nThis will run in the background."
        })
        
    except Exception as e:
        logger.error(f"Error starting backup cleanup: {str(e)}")
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Error starting cleanup: {str(e)}'
        })

def process_backup_command(user_name, command_text):
    """Process backup command and route to appropriate handler"""
    if not is_admin_user(user_name):
        return jsonify({
            'response_type': 'ephemeral',
            'text': '❌ Access denied. Backup operations require admin privileges.'
        })
    
    args = command_text.split() if command_text else []
    
    if not args:
        help_text = """🛠️ **Minecraft Backup System - Complete Guide**

**📋 Available Commands:**
• `/backup list` - List all servers available for backup
• `/backup status` - Show recent backup activity and logs
• `/backup cleanup` - Clean up old remote backups

**📦 Backup Types:**

**⚡ Incremental Backup** (Fast, Local Only):
• `/backup incremental` - Backup all servers (quick sync)
• `/backup incremental <server_id>` - Backup specific server
• Perfect for daily automated backups
• Uses rsync for speed, stores locally only

**☁️ Full Backup** (Complete + Cloud Upload):
• `/backup full` - Full backup of all servers with cloud upload
• `/backup full <server_id>` - Full backup of specific server  
• Creates zip files and uploads to Google Drive
• Best for weekly/monthly archival backups

**📊 Management:**
• `/backup status` - View recent backup logs and activity
• `/backup cleanup` - Remove old backups (keeps 5 most recent)

**📖 Examples:**
• `/backup incremental 7eaa7ab6` - Quick backup of Cactus Truck server
• `/backup full b46f4016` - Full backup of CactusTruckLanWorld
• `/backup status` - Check if backups are running
• `/backup list` - See all your servers

**🎯 Backup Strategy:**
• **Daily**: Use incremental for speed
• **Weekly**: Use full for complete archives
• **Monthly**: Run cleanup to manage storage

**💾 Storage Locations:**
• **Local**: `/var/lib/pufferpanel/servers/backup/`
• **Cloud**: Google Drive (mc-backups folder)
• **Retention**: 3 days local, 5 backups per server in cloud

**⏱️ Performance:**
• Incremental: Usually 30 seconds - 2 minutes
• Full backup: 2-10 minutes depending on world size
• All backups run in background (non-blocking)"""
        
        return jsonify({
            'response_type': 'ephemeral',
            'text': help_text
        })
    
    command = args[0].lower()
    
    if command == 'list':
        return handle_backup_list()
    elif command == 'incremental':
        server_id = args[1] if len(args) > 1 else None
        return handle_incremental_backup(user_name, server_id)
    elif command == 'full':
        server_id = args[1] if len(args) > 1 else None
        return handle_full_backup(user_name, server_id)
    elif command == 'status':
        return handle_backup_status()
    elif command == 'cleanup':
        return handle_backup_cleanup(user_name)
    else:
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'❌ Unknown backup command: `{command}`. Use `/backup` for help.'
        })
