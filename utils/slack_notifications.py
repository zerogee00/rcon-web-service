#!/usr/bin/env python3
"""
Slack notification utilities for RCON Web Service
Handles sending notifications to different Slack channels for different types of events
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SlackNotifier:
    def __init__(self):
        self.backup_webhook = os.getenv('BACKUP_SLACK_WEBHOOK_URL')
        self.system_webhook = os.getenv('SYSTEM_SLACK_WEBHOOK_URL') 
        self.minecraft_webhook = os.getenv('MINECRAFT_SLACK_WEBHOOK_URL')
    
    def _send_notification(self, webhook_url: str, payload: Dict[Any, Any]) -> bool:
        """Send notification to Slack webhook"""
        if not webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send Slack notification: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False
    
    def notify_minecraft_command(self, user: str, server_name: str, command: str, result: str, success: bool = True) -> bool:
        """Send notification for minecraft server commands"""
        color = "good" if success else "danger"
        status_emoji = "✅" if success else "❌"
        
        payload = {
            "text": f"{status_emoji} Minecraft Command: {command}",
            "unfurl_links": True,
            "unfurl_media": True,
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Minecraft Server Command",
                            "value": f"**User:** {user}\\n**Server:** {server_name}\\n**Command:** `{command}`\\n**Result:** {result}",
                            "short": False
                        }
                    ],
                    "footer": "RCON Web Service",
                    "footer_icon": "https://cdn-icons-png.flaticon.com/512/2620/2620669.png",
                    "ts": int(datetime.now().timestamp()),
                    "mrkdwn_in": ["text", "pretext", "fields"]
                }
            ]
        }
        
        return self._send_notification(self.minecraft_webhook, payload)
    
    def notify_minecraft_player_action(self, user: str, server_name: str, action: str, player: str = None, details: str = None) -> bool:
        """Send notification for minecraft player actions (kick, ban, etc.)"""
        action_emojis = {
            'kick': '👢',
            'ban': '🚫', 
            'whitelist': '✅',
            'op': '👑',
            'deop': '👥',
            'pardon': '🔓'
        }
        
        emoji = action_emojis.get(action.lower(), '🎮')
        preview_text = f"{emoji} Player Action: {action}"
        if player:
            preview_text += f" - {player}"
        
        value_text = f"**User:** {user}\\n**Server:** {server_name}\\n**Action:** {action}"
        if player:
            value_text += f"\\n**Player:** {player}"
        if details:
            value_text += f"\\n**Details:** {details}"
        
        payload = {
            "text": preview_text,
            "unfurl_links": True,
            "unfurl_media": True,
            "attachments": [
                {
                    "color": "warning",
                    "fields": [
                        {
                            "title": "Minecraft Player Action",
                            "value": value_text,
                            "short": False
                        }
                    ],
                    "footer": "RCON Web Service",
                    "footer_icon": "https://cdn-icons-png.flaticon.com/512/2620/2620669.png",
                    "ts": int(datetime.now().timestamp()),
                    "mrkdwn_in": ["text", "pretext", "fields"]
                }
            ]
        }
        
        return self._send_notification(self.minecraft_webhook, payload)
    
    def notify_minecraft_server_status(self, server_name: str, status: str, user: str = None) -> bool:
        """Send notification for minecraft server status changes"""
        status_colors = {
            'started': 'good',
            'stopped': 'danger', 
            'restarted': 'warning'
        }
        
        status_emojis = {
            'started': '🟢',
            'stopped': '🔴',
            'restarted': '🔄'
        }
        
        color = status_colors.get(status.lower(), 'warning')
        emoji = status_emojis.get(status.lower(), '⚡')
        
        value_text = f"**Server:** {server_name}\\n**Status:** {status.upper()}"
        if user:
            value_text += f"\\n**Initiated by:** {user}"
        
        payload = {
            "text": f"{emoji} Server {status}: {server_name}",
            "unfurl_links": True,
            "unfurl_media": True,
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Minecraft Server Status Change",
                            "value": value_text,
                            "short": False
                        }
                    ],
                    "footer": "RCON Web Service",
                    "footer_icon": "https://cdn-icons-png.flaticon.com/512/2620/2620669.png",
                    "ts": int(datetime.now().timestamp()),
                    "mrkdwn_in": ["text", "pretext", "fields"]
                }
            ]
        }
        
        return self._send_notification(self.minecraft_webhook, payload)

# Global instance
slack_notifier = SlackNotifier()

# Convenience functions
def notify_command(user: str, server_name: str, command: str, result: str, success: bool = True) -> bool:
    return slack_notifier.notify_minecraft_command(user, server_name, command, result, success)

def notify_player_action(user: str, server_name: str, action: str, player: str = None, details: str = None) -> bool:
    return slack_notifier.notify_minecraft_player_action(user, server_name, action, player, details)

def notify_server_status(server_name: str, status: str, user: str = None) -> bool:
    return slack_notifier.notify_minecraft_server_status(server_name, status, user)
