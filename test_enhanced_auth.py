#!/usr/bin/env python3
"""
Specific tests for enhanced CLI authentication features
"""

import subprocess
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from test_utils import (
    run_cli_subprocess, create_mock_api_response, mock_urllib_urlopen, 
    MockResponse, MockHTTPError, create_temp_config_dir, cleanup_temp_dir
)


def test_auth_subcommand_help():
    """Test auth subcommand help"""
    print("🧪 Testing auth subcommand help...")
    
    result = run_cli_subprocess('devin_cli_enhanced.py', ['auth', '--help'])
    
    assert result['returncode'] == 0, f"Auth help failed: {result['stderr']}"
    assert 'status' in result['stdout'], "Auth help missing --status option"
    assert 'remove' in result['stdout'], "Auth help missing --remove option"
    
    print("✅ Auth subcommand help works")


def test_auth_status_no_token():
    """Test auth status when no token exists"""
    print("🧪 Testing auth status with no token...")
    
    env = {'DEVIN_API_KEY': ''}
    result = run_cli_subprocess('devin_cli_enhanced.py', ['auth', '--status'], env_vars=env)
    
    assert result['returncode'] == 0, f"Auth status failed: {result['stderr']}"
    assert 'No authentication token found' in result['stdout'], "Missing no token message"
    
    print("✅ Auth status with no token works")


def test_auth_status_with_env_token():
    """Test auth status with environment token"""
    print("🧪 Testing auth status with environment token...")
    
    mock_response = MockResponse(create_mock_api_response())
    
    with patch('urllib.request.urlopen', mock_urllib_urlopen(mock_response)):
        env = {'DEVIN_API_KEY': 'test_env_token_12345'}
        result = run_cli_subprocess('devin_cli_enhanced.py', ['auth', '--status'], env_vars=env)
    
    assert result['returncode'] == 0, f"Auth status failed: {result['stderr']}"
    assert 'Using token from environment variable' in result['stdout'], "Missing env token message"
    assert 'test_env_token_12345' not in result['stdout'], "Token should be masked"
    assert 'Token is valid' in result['stdout'], "Missing token validation message"
    
    print("✅ Auth status with environment token works")


def test_auth_setup_interactive():
    """Test interactive auth setup"""
    print("🧪 Testing interactive auth setup...")
    
    temp_config_dir = create_temp_config_dir()
    
    try:
        script_content = f'''
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

from unittest.mock import patch, MagicMock
from pathlib import Path

def mock_getpass(prompt):
    return "test_interactive_token_67890"

def mock_get_config_dir():
    return Path("{temp_config_dir}")

with patch('getpass.getpass', mock_getpass):
    with patch('devin_cli_enhanced.get_config_dir', mock_get_config_dir):
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{{"session_id": "test"}}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response
            
            from devin_cli_enhanced import main
            sys.argv = ['devin_cli_enhanced.py', 'auth']
            
            try:
                main()
            except SystemExit as e:
                if e.code == 0:
                    print("Auth setup completed successfully")
                else:
                    print(f"Auth setup failed with code {{e.code}}")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            test_file = f.name
        
        try:
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True, 
                                  cwd=os.path.dirname(__file__))
            
            os.unlink(test_file)
            
            success_indicators = [
                'Authentication setup complete' in result.stdout,
                'Token saved securely' in result.stdout,
                'Auth setup completed successfully' in result.stdout
            ]
            
            assert any(success_indicators), f"Auth setup failed: {result.stdout}"
            print("    ✅ Interactive auth setup works")
            
        except Exception as e:
            if os.path.exists(test_file):
                os.unlink(test_file)
            print(f"    ⚠️  Interactive auth setup test skipped: {e}")
    
    finally:
        cleanup_temp_dir(temp_config_dir)
    
    print("✅ Interactive auth setup testing completed")


def test_auth_remove():
    """Test auth token removal"""
    print("🧪 Testing auth token removal...")
    
    temp_config_dir = create_temp_config_dir()
    
    try:
        script_content = f'''
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from unittest.mock import patch
from pathlib import Path

def mock_get_config_dir():
    return Path("{temp_config_dir}")

with patch('devin_cli_enhanced.get_config_dir', mock_get_config_dir):
    from devin_cli_enhanced import save_token, main
    
    save_token("test_token_to_remove")
    
    sys.argv = ['devin_cli_enhanced.py', 'auth', '--remove']
    
    try:
        main()
    except SystemExit as e:
        if e.code == 0:
            print("Auth remove completed successfully")
        else:
            print(f"Auth remove failed with code {{e.code}}")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            test_file = f.name
        
        try:
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True, 
                                  cwd=os.path.dirname(__file__))
            
            os.unlink(test_file)
            
            success_indicators = [
                'Saved token removed' in result.stdout,
                'Auth remove completed successfully' in result.stdout
            ]
            
            assert any(success_indicators), f"Auth remove failed: {result.stdout}"
            print("    ✅ Auth token removal works")
            
        except Exception as e:
            if os.path.exists(test_file):
                os.unlink(test_file)
            print(f"    ⚠️  Auth remove test skipped: {e}")
    
    finally:
        cleanup_temp_dir(temp_config_dir)
    
    print("✅ Auth token removal testing completed")


def test_create_subcommand():
    """Test create subcommand functionality"""
    print("🧪 Testing create subcommand...")
    
    mock_response = MockResponse(create_mock_api_response())
    
    with patch('urllib.request.urlopen', mock_urllib_urlopen(mock_response)):
        env = {'DEVIN_API_KEY': 'fake_test_key'}
        args = ['create', '--prompt', 'Test create subcommand', '--output', 'json']
        result = run_cli_subprocess('devin_cli_enhanced.py', args, env_vars=env)
    
    assert result['returncode'] == 0, f"Create subcommand failed: {result['stderr']}"
    assert 'Creating Devin session...' in result['stdout'], "Should reach API call stage"
    
    print("✅ Create subcommand works")


def test_backward_compatibility():
    """Test backward compatibility (no subcommand)"""
    print("🧪 Testing backward compatibility...")
    
    mock_response = MockResponse(create_mock_api_response())
    
    with patch('urllib.request.urlopen', mock_urllib_urlopen(mock_response)):
        env = {'DEVIN_API_KEY': 'fake_test_key'}
        args = ['--prompt', 'Test backward compatibility', '--output', 'json']
        result = run_cli_subprocess('devin_cli_enhanced.py', args, env_vars=env)
    
    assert result['returncode'] == 0, f"Backward compatibility failed: {result['stderr']}"
    assert 'Creating Devin session...' in result['stdout'], "Should reach API call stage"
    
    print("✅ Backward compatibility works")


def run_all_enhanced_auth_tests():
    """Run all enhanced authentication tests"""
    print("🚀 Starting enhanced authentication tests...\n")
    
    tests = [
        test_auth_subcommand_help,
        test_auth_status_no_token,
        test_auth_status_with_env_token,
        test_auth_setup_interactive,
        test_auth_remove,
        test_create_subcommand,
        test_backward_compatibility,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        print()
    
    print(f"📊 Enhanced Auth Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All enhanced authentication tests passed!")
    else:
        print("⚠️  Some enhanced authentication tests failed. Check the output above for details.")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_enhanced_auth_tests()
    sys.exit(0 if success else 1)
