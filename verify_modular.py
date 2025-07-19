#!/usr/bin/env python3
"""
Verification script for modular RCON Web Service
Tests all major components to ensure functionality is preserved
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_configuration():
    """Test configuration loading"""
    try:
        from config.settings import SERVERS, CONFIG, ALIASES
        assert len(SERVERS) > 0, "No servers configured"
        assert 'admin_users' in CONFIG, "Admin users not configured"
        assert len(ALIASES) > 0, "No aliases configured"
        print("✅ Configuration module working")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_security():
    """Test security utilities"""
    try:
        from utils.security import is_admin_user
        from config.settings import CONFIG
        admin_users = CONFIG.get('admin_users', [])
        if admin_users:
            result = is_admin_user(admin_users[0])
            assert result == True, "Admin user check failed"
        print("✅ Security module working")
        return True
    except Exception as e:
        print(f"❌ Security error: {e}")
        return False

def test_server_utils():
    """Test server utilities"""
    try:
        from utils.server_utils import get_server_info, clean_output_text
        from config.settings import SERVERS
        server_id = list(SERVERS.keys())[0]
        info = get_server_info(server_id)
        assert info is not None, "Server info retrieval failed"
        assert 'name' in info, "Server info missing name"
        
        # Test text cleaning
        cleaned = clean_output_text("§aTest§r\\n\\nText")
        assert '§' not in cleaned, "Color codes not removed"
        print("✅ Server utilities working")
        return True
    except Exception as e:
        print(f"❌ Server utilities error: {e}")
        return False

def test_context_manager():
    """Test context management"""
    try:
        from utils.context_manager import set_user_context, get_user_context, clear_user_context
        test_user = "test_user_verification"
        
        # Test setting context
        set_user_context(test_user, 'test', {'data': 'test'})
        context = get_user_context(test_user)
        assert context is not None, "Context not saved"
        assert context['type'] == 'test', "Context type incorrect"
        
        # Test clearing context
        clear_user_context(test_user)
        context = get_user_context(test_user)
        assert context is None, "Context not cleared"
        print("✅ Context manager working")
        return True
    except Exception as e:
        print(f"❌ Context manager error: {e}")
        return False

def test_command_processor():
    """Test command processing"""
    try:
        from modules.command_processor import process_command_alias, format_command_template
        
        # Test alias processing
        result, error = process_command_alias('list', 'test_user')
        assert error is None, f"Alias processing error: {error}"
        
        # Test template formatting
        formatted, error = format_command_template('gamemode {mode} {player}', ['creative', 'TestPlayer'])
        assert error is None, f"Template formatting error: {error}"
        assert 'creative' in formatted and 'TestPlayer' in formatted, "Template not formatted correctly"
        print("✅ Command processor working")
        return True
    except Exception as e:
        print(f"❌ Command processor error: {e}")
        return False

def test_backup_manager():
    """Test backup management"""
    try:
        from modules.backup_manager import handle_backup_list
        # Just test that the function exists and is callable
        assert callable(handle_backup_list), "Backup list handler not callable"
        print("✅ Backup manager working")
        return True
    except Exception as e:
        print(f"❌ Backup manager error: {e}")
        return False

def test_routes():
    """Test route blueprints"""
    try:
        from routes.api_routes import api_bp
        from routes.slack_routes import slack_bp
        assert api_bp.name == 'api', "API blueprint not configured correctly"
        assert slack_bp.name == 'slack', "Slack blueprint not configured correctly"
        print("✅ Route blueprints working")
        return True
    except Exception as e:
        print(f"❌ Route blueprints error: {e}")
        return False

def test_flask_app():
    """Test Flask application creation"""
    try:
        from app import create_app
        app = create_app()
        assert app is not None, "Flask app not created"
        assert len(app.blueprints) >= 2, "Blueprints not registered"
        print("✅ Flask application working")
        return True
    except Exception as e:
        print(f"❌ Flask application error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Verifying modular RCON Web Service...")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Security", test_security),
        ("Server Utils", test_server_utils),
        ("Context Manager", test_context_manager),
        ("Command Processor", test_command_processor),
        ("Backup Manager", test_backup_manager),
        ("Route Blueprints", test_routes),
        ("Flask Application", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\\nTesting {name}...")
        if test_func():
            passed += 1
    
    print("\\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Modular architecture is working correctly.")
        return 0
    else:
        print(f"❌ {total - passed} tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
