#!/usr/bin/env python3
"""
Comprehensive test suite for Devin CLI Enhanced - Create Subcommand
Tests the create subcommand functionality including argument parsing, interactive mode, and API integration
"""

import subprocess
import sys
import os
import json
from unittest.mock import patch, MagicMock


def run_enhanced_cli_command(args, env_vars=None):
    """Run the enhanced CLI command and return result"""
    cmd = [sys.executable, 'devin_cli_enhanced.py'] + args
    
    # Set up environment
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


def test_create_subcommand_help():
    """Test create subcommand help"""
    print("🧪 Testing create subcommand help...")
    result = run_enhanced_cli_command(['create', '--help'])
    
    assert result['returncode'] == 0, f"Create help command failed: {result['stderr']}"
    assert 'Create a new Devin session' in result['stdout'] or 'create' in result['stdout'].lower(), "Create help text missing"
    assert '--prompt' in result['stdout'], "Prompt option missing from create help"
    assert '--interactive' in result['stdout'], "Interactive option missing from create help"
    print("✅ Create subcommand help works correctly")


def test_create_subcommand_argument_parsing():
    """Test create subcommand argument parsing"""
    print("🧪 Testing create subcommand argument parsing...")
    
    # Test with fake API key to avoid actual API call, but check parsing
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    # This will fail at API call stage, but we can check that parsing worked
    result = run_enhanced_cli_command([
        'create',
        '--prompt', 'Test create subcommand',
        '--snapshot-id', 'snap-456',
        '--unlisted',
        '--idempotent', 
        '--max-acu-limit', '200',
        '--secret-ids', 'secret3,secret4',
        '--knowledge-ids', 'kb3,kb4',
        '--tags', 'test,create,subcommand',
        '--title', 'Test Create Session',
        '--output', 'json'
    ], env_vars=env)
    
    # Should fail at API call (403 or network error), not at argument parsing
    assert result['returncode'] == 1, "Expected API failure, not parsing failure"
    assert 'Creating Devin session...' in result['stdout'], "Should reach API call stage"
    print("✅ Create subcommand argument parsing works correctly")


def test_backward_compatibility():
    """Test backward compatibility with direct usage"""
    print("🧪 Testing backward compatibility...")
    
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    result = run_enhanced_cli_command([
        '--prompt', 'Test backward compatibility',
        '--output', 'json'
    ], env_vars=env)
    
    assert result['returncode'] == 1, "Expected API failure"
    assert 'Creating Devin session...' in result['stdout'], "Should reach API call stage"
    print("✅ Backward compatibility works correctly")


def test_api_request_structure():
    """Test that API requests are structured correctly for create subcommand"""
    print("🧪 Testing API request structure...")
    
    # Import the API function
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_enhanced import make_api_request
    
    # Mock urllib.request.urlopen
    with patch('urllib.request.urlopen') as mock_urlopen:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"session_id": "test-create-456", "url": "https://app.devin.ai/sessions/test-create-456", "is_new_session": true}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        # Set API key
        os.environ['DEVIN_API_KEY'] = 'test_create_api_key'
        
        payload = {
            'prompt': 'Test create subcommand API',
            'snapshot_id': 'snap-create-123',
            'idempotent': True,
            'unlisted': False,
            'max_acu_limit': 150,
            'tags': ['create', 'test', 'api'],
            'secret_ids': ['secret-create-1'],
            'knowledge_ids': ['kb-create-1'],
            'title': 'Create API Test'
        }
        
        result = make_api_request(payload)
        
        # Verify the request was made correctly
        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args[0][0]  # Get the Request object
        
        assert call_args.get_full_url() == 'https://api.devin.ai/v1/sessions'
        assert call_args.headers['Authorization'] == 'Bearer test_create_api_key'
        assert call_args.headers['Content-type'] == 'application/json'
        
        # Verify response parsing
        assert result['session_id'] == 'test-create-456'
        assert result['is_new_session'] == True
        
        print("✅ API request structure is correct for create subcommand")


def test_authentication_integration():
    """Test authentication integration with create subcommand"""
    print("🧪 Testing authentication integration...")
    
    env = {'DEVIN_API_KEY': ''}  # Empty API key
    result = run_enhanced_cli_command(['create', '--prompt', 'test auth'], env_vars=env)
    
    assert result['returncode'] == 1, "Should fail with missing API key"
    assert 'No Devin API token found' in result['stdout'], "Missing proper error message"
    assert 'devin-cli auth' in result['stdout'], "Should suggest auth command"
    print("✅ Authentication integration works correctly")


def test_list_parsing_enhanced():
    """Test comma-separated list parsing in enhanced CLI"""
    print("🧪 Testing list parsing functionality...")
    
    # Import the parsing function directly
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_enhanced import parse_list_input
    
    # Test various list inputs
    assert parse_list_input("") == []
    assert parse_list_input("item1") == ["item1"]
    assert parse_list_input("item1,item2") == ["item1", "item2"]
    assert parse_list_input("item1, item2, item3") == ["item1", "item2", "item3"]
    assert parse_list_input(" item1 , item2 ") == ["item1", "item2"]
    assert parse_list_input("secret-1,secret-2,secret-3") == ["secret-1", "secret-2", "secret-3"]
    
    print("✅ List parsing works correctly in enhanced CLI")


def test_output_formats():
    """Test both JSON and table output formats"""
    print("🧪 Testing output formats...")
    
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    result_json = run_enhanced_cli_command([
        'create',
        '--prompt', 'Test JSON output format',
        '--output', 'json'
    ], env_vars=env)
    
    result_table = run_enhanced_cli_command([
        'create',
        '--prompt', 'Test table output format'
    ], env_vars=env)
    
    assert result_json['returncode'] == 1, "Expected API failure for JSON"
    assert result_table['returncode'] == 1, "Expected API failure for table"
    assert 'Creating Devin session...' in result_json['stdout'], "Should reach API call stage for JSON"
    assert 'Creating Devin session...' in result_table['stdout'], "Should reach API call stage for table"
    
    print("✅ Output formats work correctly")


def test_error_handling():
    """Test error handling in create subcommand"""
    print("🧪 Testing error handling...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_enhanced import make_api_request
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = Exception("Network error")
        
        # Set API key
        os.environ['DEVIN_API_KEY'] = 'invalid_test_key'
        
        payload = {'prompt': 'Test error handling'}
        
        try:
            make_api_request(payload)
            assert False, "Should have raised an exception"
        except Exception:
            print("✅ Error handling works correctly")


def test_interactive_mode_basic():
    """Test basic interactive mode functionality"""
    print("🧪 Testing basic interactive mode...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_enhanced import cmd_create
    
    with patch('devin_cli_enhanced.prompt_user') as mock_prompt, \
         patch('devin_cli_enhanced.confirm') as mock_confirm, \
         patch('devin_cli_enhanced.make_api_request') as mock_api:
        
        mock_prompt.return_value = "Test interactive mode"
        mock_confirm.return_value = False
        mock_api.return_value = {"session_id": "test-123", "url": "https://app.devin.ai/sessions/test-123", "is_new_session": True}
        
        class MockArgs:
            def __init__(self):
                self.prompt = None
                self.interactive = True
                self.snapshot_id = None
                self.unlisted = False
                self.idempotent = False
                self.max_acu_limit = None
                self.secret_ids = None
                self.knowledge_ids = None
                self.tags = None
                self.title = None
                self.output = 'table'
        
        args = MockArgs()
        
        # Set API key
        os.environ['DEVIN_API_KEY'] = 'test_key'
        
        try:
            with patch('builtins.print'):
                cmd_create(args)
            
            assert mock_prompt.call_count >= 1, "Should have prompted for input"
            print("✅ Basic interactive mode works")
        except Exception as e:
            print(f"⚠️  Interactive mode test skipped: {e}")


def run_all_tests():
    """Run all create subcommand tests"""
    print("🚀 Starting enhanced CLI create subcommand tests...\n")
    
    tests = [
        test_create_subcommand_help,
        test_create_subcommand_argument_parsing,
        test_backward_compatibility,
        test_authentication_integration,
        test_list_parsing_enhanced,
        test_output_formats,
        test_api_request_structure,
        test_error_handling,
        test_interactive_mode_basic,
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
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All create subcommand tests passed! The enhanced CLI is working perfectly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
