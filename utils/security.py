"""
Security utilities for RCON Web Service
"""
import hashlib
import hmac
import time
import logging
from functools import wraps
from flask import request, jsonify
from config.settings import SLACK_SIGNING_SECRET, API_TOKEN, CONFIG

logger = logging.getLogger(__name__)

def verify_slack_signature(f):
    """Verify Slack request signature"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not SLACK_SIGNING_SECRET:
            logger.warning("Slack signing secret not configured")
            return jsonify({'error': 'Slack integration not properly configured'}), 500
        
        timestamp = request.headers.get('X-Slack-Request-Timestamp')
        slack_signature = request.headers.get('X-Slack-Signature')
        
        if not timestamp or not slack_signature:
            logger.warning("Missing Slack signature headers")
            return jsonify({'error': 'Missing required headers'}), 400
        
        # Check if request is too old (replay attack protection)
        if abs(time.time() - int(timestamp)) > 300:
            logger.warning("Slack request too old")
            return jsonify({'error': 'Request too old'}), 400
        
        # Verify signature
        sig_basestring = f"v0:{timestamp}:{request.get_data(as_text=True)}"
        computed_signature = f"v0={hmac.new(SLACK_SIGNING_SECRET.encode(), sig_basestring.encode(), hashlib.sha256).hexdigest()}"
        
        if not hmac.compare_digest(computed_signature, slack_signature):
            logger.warning("Invalid Slack signature")
            return jsonify({'error': 'Invalid signature'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def verify_api_token(f):
    """Verify API token for direct API access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token != API_TOKEN:
            logger.warning(f"Invalid API token attempt from {request.remote_addr}")
            return jsonify({'error': 'Invalid API token'}), 401
        return f(*args, **kwargs)
    return decorated_function

def is_admin_user(user_name):
    """Check if user has admin privileges"""
    return user_name in CONFIG.get('admin_users', [])

def rate_limit_check(user_name):
    """Check if user is within rate limits (placeholder for future implementation)"""
    # TODO: Implement actual rate limiting with Redis or in-memory cache
    return True
