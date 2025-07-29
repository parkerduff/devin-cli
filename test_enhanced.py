#!/usr/bin/env python3
"""
Enhanced CLI implementation tests for devin_cli_enhanced.py
Tests token management, authentication, and enhanced features
"""

import subprocess
import sys
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path


def run_enhanced_cli_command(args, env_vars=None):
    """Run the enhanced CLI command and return result"""
    cmd = [sys.executable, 'devin_cli_enhanced.py'] + args
    
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            env=env,
            cwd=os.path.dirname(__file__)
        )
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }


def test_token_validation():
    """Test the test_token() function"""
    print("🧪 Testing token validation...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_enhanced import test_token
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        assert test_token('valid_token') == True, "Valid token should return True"
        
        mock_urlopen.side_effect = Exception("Network error")
        assert test_token('network_error_token') == True, "Network errors should assume token is valid"
        
        from urllib.error import HTTPError
        import io
        mock_urlopen.side_effect = HTTPError("", 403, "Forbidden", {}, io.StringIO())
        assert test_token('invalid_token') == False, "403 error should return False"
        
        mock_urlopen.side_effect = HTTPError("", 500, "Server Error", {}, io.StringIO())
        assert test_token('server_error_token') == True, "Non-403 HTTP errors should return True"
    
    print("✅ Token validation works correctly")


def test_token_storage_and_retrieval():
    """Test token storage and retrieval functionality"""
    print("🧪 Testing token storage and retrieval...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_enhanced import save_token, load_token, get_config_dir, get_token_file
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('devin_cli_enhanced.get_config_dir') as mock_config_dir:
            mock_config_dir.return_value = Path(temp_dir)
            
            test_token = "test_api_key_12345"
            save_token(test_token)
            
            token_file = Path(temp_dir) / 'token'
            assert token_file.exists(), "Token file should be created"
            
            file_perms = oct(token_file.stat().st_mode)[-3:]
            assert file_perms == '600', f"Token file should have 600 permissions, got {file_perms}"
            
            retrieved_token = load_token()
            assert retrieved_token == test_token, "Retrieved token should match saved token"
            
            env_token = "env_api_key_67890"
            with patch.dict(os.environ, {'DEVIN_API_KEY': env_token}):
                retrieved_token = load_token()
                assert retrieved_token == env_token, "Environment variable should take precedence"
    
    print("✅ Token storage and retrieval works correctly")


def test_cmd_auth_status():
    """Test cmd_auth function with status flag"""
    print("🧪 Testing cmd_auth status functionality...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_enhanced import cmd_auth
    
    class MockArgs:
        def __init__(self, status=False, remove=False):
            self.status = status
            self.remove = remove
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('devin_cli_enhanced.get_config_dir') as mock_config_dir:
            mock_config_dir.return_value = Path(temp_dir)
            
            with patch('devin_cli_enhanced.test_token') as mock_test_token:
                mock_test_token.return_value = True
                
                with patch('builtins.print') as mock_print:
                    args = MockArgs(status=True)
                    cmd_auth(args)
                    
                    print_calls = [call[0][0] for call in mock_print.call_args_list]
                    assert any("No authentication token found" in call for call in print_calls), "Should report no token found"
    
    print("✅ cmd_auth status functionality works correctly")


def test_cmd_auth_remove():
    """Test cmd_auth function with remove flag"""
    print("🧪 Testing cmd_auth remove functionality...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_enhanced import cmd_auth, save_token
    
    class MockArgs:
        def __init__(self, status=False, remove=False):
            self.status = status
            self.remove = remove
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('devin_cli_enhanced.get_config_dir') as mock_config_dir:
            mock_config_dir.return_value = Path(temp_dir)
            
            save_token("test_token")
            token_file = Path(temp_dir) / 'token'
            assert token_file.exists(), "Token file should exist before removal"
            
            with patch('builtins.print') as mock_print:
                args = MockArgs(remove=True)
                cmd_auth(args)
                
                assert not token_file.exists(), "Token file should be removed"
                print_calls = [call[0][0] for call in mock_print.call_args_list]
                assert any("Saved token removed" in call for call in print_calls), "Should confirm token removal"
    
    print("✅ cmd_auth remove functionality works correctly")


def test_cmd_auth_interactive_setup():
    """Test cmd_auth interactive token setup"""
    print("🧪 Testing cmd_auth interactive setup...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_enhanced import cmd_auth
    
    class MockArgs:
        def __init__(self, status=False, remove=False):
            self.status = status
            self.remove = remove
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('devin_cli_enhanced.get_config_dir') as mock_config_dir:
            mock_config_dir.return_value = Path(temp_dir)
            
            with patch('getpass.getpass') as mock_getpass:
                mock_getpass.return_value = "new_test_token_12345"
                
                with patch('devin_cli_enhanced.test_token') as mock_test_token:
                    mock_test_token.return_value = True
                    
                    with patch('builtins.print') as mock_print:
                        args = MockArgs()
                        cmd_auth(args)
                        
                        token_file = Path(temp_dir) / 'token'
                        assert token_file.exists(), "Token file should be created"
                        
                        with open(token_file, 'r') as f:
                            saved_token = f.read().strip()
                        assert saved_token == "new_test_token_12345", "Token should be saved correctly"
    
    print("✅ cmd_auth interactive setup works correctly")


def test_enhanced_cli_auth_command():
    """Test the enhanced CLI auth command via subprocess"""
    print("🧪 Testing enhanced CLI auth command...")
    
    result = run_enhanced_cli_command(['auth', '--status'])
    
    assert result['returncode'] == 0, f"Auth status command should succeed: {result['stderr']}"
    assert 'No authentication token found' in result['stdout'] or 'Using token' in result['stdout'], "Should show auth status"
    
    print("✅ Enhanced CLI auth command works correctly")


def test_enhanced_cli_version():
    """Test enhanced CLI version command"""
    print("🧪 Testing enhanced CLI version...")
    
    result = run_enhanced_cli_command(['--version'])
    
    assert result['returncode'] == 0, f"Version command failed: {result['stderr']}"
    assert '1.1.0' in result['stdout'], "Should show version 1.1.0"
    
    print("✅ Enhanced CLI version works correctly")


def test_enhanced_cli_create_session():
    """Test enhanced CLI create session functionality"""
    print("🧪 Testing enhanced CLI create session...")
    
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    result = run_enhanced_cli_command([
        'create',
        '--prompt', 'Test enhanced CLI',
        '--output', 'json'
    ], env_vars=env)
    
    assert result['returncode'] == 1, "Should fail with fake API key"
    assert 'Creating Devin session...' in result['stdout'], "Should reach API call stage"
    
    print("✅ Enhanced CLI create session works correctly")


def run_all_tests():
    """Run all enhanced CLI tests"""
    print("🚀 Starting enhanced CLI tests...\n")
    
    tests = [
        test_token_validation,
        test_token_storage_and_retrieval,
        test_cmd_auth_status,
        test_cmd_auth_remove,
        test_cmd_auth_interactive_setup,
        test_enhanced_cli_auth_command,
        test_enhanced_cli_version,
        test_enhanced_cli_create_session,
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
    
    print(f"📊 Enhanced CLI Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All enhanced CLI tests passed!")
    else:
        print("⚠️  Some enhanced CLI tests failed. Check the output above for details.")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
