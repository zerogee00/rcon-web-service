"""
User context management utilities
"""
import json
import os
import logging
from datetime import datetime, timedelta
from config.settings import USER_CONTEXTS_FILE, CONFIG

logger = logging.getLogger(__name__)

# Global user contexts storage
USER_CONTEXTS = {}

def load_user_contexts():
    """Load user contexts from file"""
    global USER_CONTEXTS
    if os.path.exists(USER_CONTEXTS_FILE):
        try:
            with open(USER_CONTEXTS_FILE, 'r') as f:
                data = json.load(f)
            
            # Handle legacy format where values might be strings
            USER_CONTEXTS = {}
            for user_name, user_data in data.items():
                if isinstance(user_data, str):
                    # Legacy format: user -> server_id string
                    USER_CONTEXTS[user_name] = {
                        'default_server': user_data
                    }
                elif isinstance(user_data, dict):
                    # New format: user -> dict with default_server and context
                    USER_CONTEXTS[user_name] = user_data
                else:
                    # Skip invalid entries
                    logger.warning(f"Skipping invalid user data for {user_name}: {user_data}")
                    
            logger.info("User contexts loaded successfully.")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading user contexts: {e}")
            USER_CONTEXTS = {}
    else:
        USER_CONTEXTS = {}
        save_user_contexts()

def save_user_contexts():
    """Save user contexts to file"""
    try:
        with open(USER_CONTEXTS_FILE, 'w') as f:
            json.dump(USER_CONTEXTS, f, indent=2)
    except IOError as e:
        logger.error(f"Error saving user contexts: {e}")

def get_user_default_server(user_name):
    """Get user's default server"""
    user_data = USER_CONTEXTS.get(user_name, {})
    if isinstance(user_data, dict):
        return user_data.get('default_server')
    return None

def set_user_default_server(user_name, server_id):
    """Set user's default server"""
    if user_name not in USER_CONTEXTS:
        USER_CONTEXTS[user_name] = {}
    elif not isinstance(USER_CONTEXTS[user_name], dict):
        # Convert legacy format
        USER_CONTEXTS[user_name] = {}
    
    USER_CONTEXTS[user_name]['default_server'] = server_id
    save_user_contexts()

def get_user_context(user_name):
    """Get user's current context"""
    user_data = USER_CONTEXTS.get(user_name, {})
    
    # Ensure user_data is a dict
    if not isinstance(user_data, dict):
        # Legacy format or invalid data
        return None
    
    context = user_data.get('context')
    
    if context:
        # Check if context has expired
        try:
            expires_at = datetime.fromisoformat(context['expires_at'])
            if datetime.now() > expires_at:
                clear_user_context(user_name)
                return None
        except (KeyError, ValueError) as e:
            # Invalid context format, clear it
            logger.warning(f"Invalid context format for {user_name}: {e}")
            clear_user_context(user_name)
            return None
    
    return context

def set_user_context(user_name, context_type, data, timeout_minutes=None):
    """Set user's context with optional timeout"""
    if timeout_minutes is None:
        timeout_minutes = CONFIG.get('default_context_timeout', 300) // 60  # Convert seconds to minutes
    
    if user_name not in USER_CONTEXTS:
        USER_CONTEXTS[user_name] = {}
    elif not isinstance(USER_CONTEXTS[user_name], dict):
        # Convert legacy format, preserving default_server if it was a string
        old_server = USER_CONTEXTS[user_name] if isinstance(USER_CONTEXTS[user_name], str) else None
        USER_CONTEXTS[user_name] = {}
        if old_server:
            USER_CONTEXTS[user_name]['default_server'] = old_server
    
    expires_at = datetime.now() + timedelta(minutes=timeout_minutes)
    
    USER_CONTEXTS[user_name]['context'] = {
        'type': context_type,
        'data': data,
        'created_at': datetime.now().isoformat(),
        'expires_at': expires_at.isoformat()
    }
    save_user_contexts()

def clear_user_context(user_name):
    """Clear user's current context"""
    if user_name in USER_CONTEXTS and isinstance(USER_CONTEXTS[user_name], dict):
        if 'context' in USER_CONTEXTS[user_name]:
            del USER_CONTEXTS[user_name]['context']
            save_user_contexts()

def cleanup_expired_contexts():
    """Clean up expired contexts (call periodically)"""
    now = datetime.now()
    expired_users = []
    
    for user_name, user_data in USER_CONTEXTS.items():
        if not isinstance(user_data, dict):
            continue
            
        context = user_data.get('context')
        if context:
            try:
                expires_at = datetime.fromisoformat(context['expires_at'])
                if now > expires_at:
                    expired_users.append(user_name)
            except (KeyError, ValueError):
                # Invalid context, mark for cleanup
                expired_users.append(user_name)
    
    for user_name in expired_users:
        clear_user_context(user_name)
    
    if expired_users:
        logger.info(f"Cleaned up {len(expired_users)} expired contexts")

# Initialize contexts on import
load_user_contexts()
