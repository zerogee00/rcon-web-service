#!/usr/bin/env python3
"""
RCON Web Service - Modular Version
A Flask application for managing Minecraft servers via RCON with Slack integration
"""
import os
import sys
import logging
from flask import Flask

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration
from config.settings import CONFIG

# Import route blueprints
from routes.api_routes import api_bp
from routes.slack_routes import slack_bp

# Import utilities to initialize contexts
from utils.context_manager import load_user_contexts

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configure logging
    log_level = getattr(logging, CONFIG.get('log_level', 'INFO').upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Initialize user contexts
    load_user_contexts()
    logger.info("User contexts loaded successfully.")
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(slack_bp)
    
    # Health check endpoint (also available at root)
    @app.route('/', methods=['GET'])
    def root():
        return {'status': 'RCON Web Service is running', 'version': '2.0.0'}
    
    logger.info("RCON Web Service initialized successfully")
    return app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
