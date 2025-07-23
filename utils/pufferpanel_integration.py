#!/usr/bin/env python3
"""
Enhanced PufferPanel integration for RCON Web Service
Provides server control, status monitoring, and advanced features
"""

import os
import json
import subprocess
import psutil
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import sqlite3

from utils.slack_notifications import notify_server_status, notify_command

logger = logging.getLogger(__name__)

class PufferPanelManager:
    def __init__(self, server_root="/var/lib/pufferpanel/servers", db_path="/var/lib/pufferpanel/database.db", api_url="http://localhost:8080"):
        self.server_root = server_root
        self.db_path = db_path
        self.api_url = api_url
        self.token = self._get_auth_token()
    
    def _get_auth_token(self) -> str:
        """Get authentication token from PufferPanel config"""
        try:
            with open('/etc/pufferpanel/config.json', 'r') as f:
                config = json.load(f)
                return config.get('panel', {}).get('token', '')
        except Exception as e:
            logger.error(f"Error getting auth token: {e}")
            return ""
    
    def _make_api_request(self, method: str, endpoint: str, data=None) -> Optional[Dict]:
        """Make authenticated API request to PufferPanel"""
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.api_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=10)
            else:
                return None
            
            if response.status_code == 200:
                return response.json() if response.content else {}
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error making API request to {endpoint}: {e}")
            return None
    
    def get_server_info(self, server_id: str) -> Dict[str, Any]:
        """Get comprehensive server information from PufferPanel"""
        config_path = os.path.join(self.server_root, f"{server_id}.json")
        server_dir = os.path.join(self.server_root, server_id)
        
        if not os.path.exists(config_path):
            return None
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Basic info
            server_info = {
                'id': server_id,
                'name': self.get_display_name(config),
                'type': config.get('type', 'unknown'),
                'config_path': config_path,
                'server_dir': server_dir,
                'running': self.is_server_running(server_id),
                'pid': self.get_server_pid(server_id),
            }
            
            # Add server properties if available
            properties_path = os.path.join(server_dir, 'server.properties')
            if os.path.exists(properties_path):
                server_info['properties'] = self.parse_server_properties(properties_path)
            
            # Add resource usage if running
            if server_info['running'] and server_info['pid']:
                server_info['resources'] = self.get_server_resources(server_info['pid'])
            
            return server_info
            
        except Exception as e:
            logger.error(f"Error getting server info for {server_id}: {e}")
            return None
    
    def get_display_name(self, config: Dict) -> str:
        """Extract display name from PufferPanel config"""
        # Try MOTD first
        if 'data' in config and 'motd' in config['data']:
            motd = config['data']['motd'].get('value', '')
            if motd:
                # Clean up Minecraft formatting codes
                import re
                clean_motd = re.sub(r'§[0-9a-fA-F]', '', motd)
                clean_motd = clean_motd.replace('"', '').strip()
                if clean_motd:
                    return clean_motd
        
        # Fallback to display or id
        return config.get('display', config.get('id', 'Unknown'))
    
    def parse_server_properties(self, properties_path: str) -> Dict[str, str]:
        """Parse server.properties file"""
        properties = {}
        try:
            with open(properties_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        properties[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Error parsing server.properties: {e}")
        
        return properties
    
    def is_server_running(self, server_id: str) -> bool:
        """Check if server is currently running"""
        try:
            # Look for java processes in the server directory
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                try:
                    if proc.info['name'] and 'java' in proc.info['name'].lower():
                        # Check if process is running in the server directory
                        server_path = os.path.join(self.server_root, server_id)
                        if proc.info['cwd'] and server_path in proc.info['cwd']:
                            return True
                        # Also check command line arguments
                        if proc.info['cmdline'] and any(server_id in str(arg) for arg in proc.info['cmdline']):
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            logger.error(f"Error checking if server {server_id} is running: {e}")
            return False
    
    def get_server_pid(self, server_id: str) -> Optional[int]:
        """Get the PID of a running server"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                try:
                    if proc.info['name'] and 'java' in proc.info['name'].lower():
                        # Check if process is running in the server directory
                        server_path = os.path.join(self.server_root, server_id)
                        if proc.info['cwd'] and server_path in proc.info['cwd']:
                            return proc.info['pid']
                        # Also check command line arguments
                        if proc.info['cmdline'] and any(server_id in str(arg) for arg in proc.info['cmdline']):
                            return proc.info['pid']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return None
        except Exception as e:
            logger.error(f"Error getting PID for server {server_id}: {e}")
            return None
    
    def get_server_resources(self, pid: int) -> Dict[str, Any]:
        """Get resource usage for a server process"""
        try:
            proc = psutil.Process(pid)
            return {
                'cpu_percent': proc.cpu_percent(interval=1),
                'memory_mb': proc.memory_info().rss / 1024 / 1024,
                'memory_percent': proc.memory_percent(),
                'num_threads': proc.num_threads(),
                'create_time': datetime.fromtimestamp(proc.create_time()),
                'status': proc.status()
            }
        except Exception as e:
            logger.error(f"Error getting resources for PID {pid}: {e}")
            return {}
    
    def list_all_servers(self) -> List[Dict[str, Any]]:
        """Get information for all servers"""
        servers = []
        try:
            for file in os.listdir(self.server_root):
                if file.endswith('.json'):
                    server_id = file[:-5]  # Remove .json extension
                    server_info = self.get_server_info(server_id)
                    if server_info:
                        servers.append(server_info)
        except Exception as e:
            logger.error(f"Error listing servers: {e}")
        
        return sorted(servers, key=lambda x: x['name'])
    
    def control_server(self, server_id: str, action: str, user: str = None) -> bool:
        """Control server using proper PufferPanel methods"""
        if action not in ['start', 'stop', 'restart', 'kill']:
            return False
        
        server_info = self.get_server_info(server_id)
        if not server_info:
            logger.error(f"Server {server_id} not found")
            return False
        
        try:
            if action == 'kill':
                # Force kill the server process
                pid = self.get_server_pid(server_id)
                if pid:
                    os.kill(pid, 9)
                    logger.info(f"Force killed server {server_id} (PID: {pid})")
                    notify_server_status(server_info['name'], 'killed', user)
                    return True
                else:
                    logger.error(f"No running process found for server {server_id}")
                    return False
            else:
                # Use PufferPanel's internal control mechanism
                success = self._control_server_internal(server_id, action)
                
                if success:
                    logger.info(f"Server {server_id} {action} successful")
                    notify_server_status(server_info['name'], action, user)
                else:
                    logger.error(f"Server {server_id} {action} failed")
                
                return success
                
        except Exception as e:
            logger.error(f"Error controlling server {server_id} ({action}): {e}")
            return False
    
    def _control_server_internal(self, server_id: str, action: str) -> bool:
        """Internal server control using PufferPanel's process management"""
        try:
            server_dir = os.path.join(self.server_root, server_id)
            
            if action == 'start':
                # Check if already running
                if self.is_server_running(server_id):
                    logger.info(f"Server {server_id} is already running")
                    return True
                
                # Start server by running the start script or java command directly
                # PufferPanel typically uses screen sessions or direct process spawning
                start_script = os.path.join(server_dir, 'start.sh')
                if os.path.exists(start_script):
                    # Use existing start script
                    result = subprocess.Popen(
                        ['bash', start_script],
                        cwd=server_dir,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        preexec_fn=os.setsid
                    )
                    # Give it a moment to start
                    import time
                    time.sleep(2)
                    return self.is_server_running(server_id)
                else:
                    # Try to start using the jar file directly
                    jar_file = os.path.join(server_dir, 'server.jar')
                    if os.path.exists(jar_file):
                        cmd = [
                            'java', '-Xmx14848M', 
                            '-Dterminal.jline=false', 
                            '-Dterminal.ansi=true', 
                            '-Dlog4j2.formatMsgNoLookups=true',
                            '-jar', 'server.jar', 'nogui'
                        ]
                        result = subprocess.Popen(
                            cmd,
                            cwd=server_dir,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            preexec_fn=os.setsid
                        )
                        # Give it a moment to start
                        import time
                        time.sleep(2)
                        return self.is_server_running(server_id)
                    else:
                        logger.error(f"No server.jar found for {server_id}")
                        return False
            
            elif action == 'stop':
                # Send graceful stop command
                pid = self.get_server_pid(server_id)
                if pid:
                    # Try to send stop command via stdin if possible
                    # For now, use SIGTERM for graceful shutdown
                    os.kill(pid, 15)  # SIGTERM
                    
                    # Wait a bit for graceful shutdown
                    import time
                    time.sleep(5)
                    
                    # Check if it's still running
                    if self.is_server_running(server_id):
                        # Force kill if still running
                        try:
                            os.kill(pid, 9)  # SIGKILL
                        except ProcessLookupError:
                            pass  # Already dead
                    
                    return not self.is_server_running(server_id)
                else:
                    logger.info(f"Server {server_id} is not running")
                    return True
            
            elif action == 'restart':
                # Stop then start
                stop_success = self._control_server_internal(server_id, 'stop')
                if stop_success:
                    import time
                    time.sleep(2)  # Wait between stop and start
                    return self._control_server_internal(server_id, 'start')
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error in internal server control for {server_id} ({action}): {e}")
            return False
    
    def get_server_logs(self, server_id: str, lines: int = 50) -> List[str]:
        """Get recent server logs"""
        log_path = os.path.join(self.server_root, server_id, "logs", "latest.log")
        if not os.path.exists(log_path):
            return []
        
        try:
            # Use tail to get last N lines efficiently
            result = subprocess.run(
                ['tail', '-n', str(lines), log_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting logs for server {server_id}: {e}")
            return []
    
    def backup_server(self, server_id: str, backup_type: str = "incremental", user: str = None) -> bool:
        """Trigger server backup"""
        try:
            backup_script = "/root/rcon-web-service/backup.sh"
            if not os.path.exists(backup_script):
                logger.error("Backup script not found")
                return False
            
            env = os.environ.copy()
            env['BACKUP_SLACK_WEBHOOK_URL'] = os.getenv('BACKUP_SLACK_WEBHOOK_URL', '')
            
            if backup_type == "full":
                # Interactive mode for single server
                result = subprocess.run(
                    [backup_script, '--interactive'],
                    input=f"1\n",  # Assuming first server in list
                    text=True,
                    capture_output=True,
                    timeout=300,
                    env=env
                )
            else:
                # Regular incremental backup
                result = subprocess.run(
                    [backup_script],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    env=env
                )
            
            success = result.returncode == 0
            if success:
                logger.info(f"Backup triggered for server {server_id}")
                server_info = self.get_server_info(server_id)
                if server_info:
                    notify_command(user or "System", server_info['name'], f"backup {backup_type}", 
                                 "Backup completed successfully", True)
            else:
                logger.error(f"Backup failed for server {server_id}: {result.stderr}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error backing up server {server_id}: {e}")
            return False

# Global instance
pufferpanel = PufferPanelManager()

# Convenience functions
def get_server_info(server_id: str) -> Dict[str, Any]:
    return pufferpanel.get_server_info(server_id)

def list_servers() -> List[Dict[str, Any]]:
    return pufferpanel.list_all_servers()

def control_server(server_id: str, action: str, user: str = None) -> bool:
    return pufferpanel.control_server(server_id, action, user)

def get_server_logs(server_id: str, lines: int = 50) -> List[str]:
    return pufferpanel.get_server_logs(server_id, lines)

def backup_server(server_id: str, backup_type: str = "incremental", user: str = None) -> bool:
    return pufferpanel.backup_server(server_id, backup_type, user)
