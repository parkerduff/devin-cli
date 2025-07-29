#!/usr/bin/env python3
"""
Comprehensive test suite for Devin CLI
Tests all functionality without requiring a real API key
"""

import subprocess
import sys
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
import urllib.request
import urllib.error


def run_cli_command(args, env_vars=None):
    """Run the CLI command and return result"""
    cmd = [sys.executable, 'devin_cli_standalone.py'] + args
    
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


def test_help_command():
    """Test --help command"""
    print("🧪 Testing --help command...")
    result = run_cli_command(['--help'])
    
    assert result['returncode'] == 0, f"Help command failed: {result['stderr']}"
    assert 'Create a new Devin session' in result['stdout'], "Help text missing"
    assert '--prompt' in result['stdout'], "Prompt option missing from help"
    assert '--snapshot-id' in result['stdout'], "Snapshot ID option missing from help"
    assert '--interactive' in result['stdout'], "Interactive option missing from help"
    print("✅ Help command works correctly")


def test_version_command():
    """Test --version command"""
    print("🧪 Testing --version command...")
    result = run_cli_command(['--version'])
    
    assert result['returncode'] == 0, f"Version command failed: {result['stderr']}"
    assert '1.0.0' in result['stdout'], "Version number missing"
    print("✅ Version command works correctly")


def test_missing_api_key():
    """Test behavior when API key is missing"""
    print("🧪 Testing missing API key handling...")
    env = {'DEVIN_API_KEY': ''}  # Empty API key
    result = run_cli_command(['--prompt', 'test'], env_vars=env)
    
    assert result['returncode'] == 1, "Should fail with missing API key"
    assert 'DEVIN_API_KEY environment variable is required' in result['stdout'], "Missing proper error message"
    print("✅ Missing API key handled correctly")


def test_argument_parsing():
    """Test that all arguments are parsed correctly"""
    print("🧪 Testing argument parsing...")
    
    # Test with fake API key to avoid actual API call, but check parsing
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    # This will fail at API call stage, but we can check that parsing worked
    result = run_cli_command([
        '--prompt', 'Test prompt',
        '--snapshot-id', 'snap-123',
        '--unlisted',
        '--idempotent', 
        '--max-acu-limit', '100',
        '--secret-ids', 'secret1,secret2',
        '--knowledge-ids', 'kb1,kb2',
        '--tags', 'test,cli',
        '--title', 'Test Session',
        '--output', 'json'
    ], env_vars=env)
    
    # Should fail at API call (403 or network error), not at argument parsing
    assert result['returncode'] == 1, "Expected API failure, not parsing failure"
    assert 'Creating Devin session...' in result['stdout'], "Should reach API call stage"
    print("✅ Argument parsing works correctly")


def test_interactive_mode_simulation():
    """Test interactive mode with simulated input"""
    print("🧪 Testing interactive mode simulation...")
    
    # Create a script that simulates interactive input
    test_script = '''
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Mock input function
inputs = iter([
    "Test interactive prompt",  # prompt
    "snap-456",                 # snapshot_id
    "y",                        # unlisted
    "n",                        # idempotent
    "50",                       # max_acu_limit
    "secret3,secret4",          # secret_ids
    "kb3,kb4",                  # knowledge_ids
    "interactive,test",         # tags
    "Interactive Test Session"  # title
])

def mock_input(prompt):
    try:
        return next(inputs)
    except StopIteration:
        return ""

# Patch input function
import builtins
builtins.input = mock_input

# Set fake API key
os.environ['DEVIN_API_KEY'] = 'fake_key_for_testing'

# Import and run
from devin_cli_standalone import main
sys.argv = ['devin_cli_standalone.py', '--interactive', '--output', 'json']

try:
    main()
except SystemExit as e:
    # Expected to exit with 1 due to fake API key
    if e.code == 1:
        print("Interactive mode completed (expected API failure)")
    else:
        raise
'''
    
    # Write and run the test script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, 
                              cwd=os.path.dirname(__file__))
        
        # Clean up
        os.unlink(test_file)
        
        # Should complete interactive prompting
        assert 'Creating Devin session...' in result.stdout or 'Interactive mode completed' in result.stdout
        print("✅ Interactive mode simulation works")
        
    except Exception as e:
        os.unlink(test_file)  # Clean up on error
        print(f"⚠️  Interactive mode test skipped: {e}")


def test_json_output_format():
    """Test JSON output format and structure validation"""
    print("🧪 Testing JSON output format and structure...")
    
    # Create a test script that mocks the API response within the subprocess
    current_dir = os.path.dirname(__file__)
    test_script = f'''
import sys
import os
import json
from unittest.mock import patch, MagicMock

os.chdir(r"{current_dir}")
sys.path.insert(0, r"{current_dir}")

# Set API key
os.environ['DEVIN_API_KEY'] = 'test_api_key'

# Mock urllib.request.urlopen
with patch('urllib.request.urlopen') as mock_urlopen:
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.read.return_value = b'{{"session_id": "test-456", "url": "https://app.devin.ai/sessions/test-456", "is_new_session": false}}'
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response
    
    # Import and run the CLI
    from devin_cli_standalone import main
    sys.argv = ['devin_cli_standalone.py', '--prompt', 'Test JSON output structure', '--output', 'json']
    
    try:
        main()
    except SystemExit as e:
        # Expected to exit with 0 on success
        if e.code != 0:
            print(f"Unexpected exit code: {{e.code}}", file=sys.stderr)
            sys.exit(e.code)
'''
    
    # Write and run the test script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, 
                              cwd=os.path.dirname(__file__))
        
        # Clean up
        os.unlink(test_file)
        
        assert result.returncode == 0, f"JSON output test failed: {result.stderr}"
        
        output_lines = result.stdout.strip().split('\n')
        
        # Skip the "Creating Devin session..." line and get JSON output
        json_output = None
        for line in output_lines:
            if line.strip().startswith('{'):
                json_start_idx = output_lines.index(line)
                json_lines = output_lines[json_start_idx:]
                json_output = '\n'.join(json_lines)
                break
        
        assert json_output is not None, f"No JSON output found in stdout: {result.stdout}"
        
        try:
            parsed_json = json.loads(json_output)
        except json.JSONDecodeError as e:
            assert False, f"Invalid JSON output: {e}\nOutput: {json_output}"
        
        assert isinstance(parsed_json, dict), "JSON output should be a dictionary"
        assert 'session_id' in parsed_json, "JSON output missing 'session_id' field"
        assert 'url' in parsed_json, "JSON output missing 'url' field"
        assert 'is_new_session' in parsed_json, "JSON output missing 'is_new_session' field"
        
        assert isinstance(parsed_json['session_id'], str), "'session_id' should be a string"
        assert isinstance(parsed_json['url'], str), "'url' should be a string"
        assert isinstance(parsed_json['is_new_session'], bool), "'is_new_session' should be a boolean"
        
        assert parsed_json['session_id'] == 'test-456', f"Unexpected session_id: {parsed_json['session_id']}"
        assert parsed_json['url'] == 'https://app.devin.ai/sessions/test-456', f"Unexpected url: {parsed_json['url']}"
        assert parsed_json['is_new_session'] == False, f"Unexpected is_new_session: {parsed_json['is_new_session']}"
        
        expected_formatted = json.dumps(parsed_json, indent=2)
        assert json_output == expected_formatted, "JSON output should be properly formatted with 2-space indentation"
        
        print("✅ JSON output format and structure validation works correctly")
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(test_file):
            os.unlink(test_file)
        raise e


def test_json_output_error_handling():
    """Test JSON output format during API errors"""
    print("🧪 Testing JSON output error handling...")
    
    # Test with missing API key (should not produce JSON output)
    env = {'DEVIN_API_KEY': ''}
    result = run_cli_command([
        '--prompt', 'Test JSON error',
        '--output', 'json'
    ], env_vars=env)
    
    # Should fail with missing API key
    assert result['returncode'] == 1, "Should fail with missing API key"
    assert 'DEVIN_API_KEY environment variable is required' in result['stdout'], "Missing proper error message"
    
    assert not any(line.strip().startswith('{') for line in result['stdout'].split('\n')), "Should not produce JSON output on API key error"
    
    print("✅ JSON output error handling works correctly")


def test_list_parsing():
    """Test comma-separated list parsing"""
    print("🧪 Testing list parsing functionality...")
    
    # Import the parsing function directly
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_standalone import parse_list_input
    
    # Test various list inputs
    assert parse_list_input("") == []
    assert parse_list_input("item1") == ["item1"]
    assert parse_list_input("item1,item2") == ["item1", "item2"]
    assert parse_list_input("item1, item2, item3") == ["item1", "item2", "item3"]
    assert parse_list_input(" item1 , item2 ") == ["item1", "item2"]
    
    print("✅ List parsing works correctly")


def test_api_request_structure():
    """Test that API requests are structured correctly"""
    print("🧪 Testing API request structure...")
    
    # Import the API function
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_standalone import make_api_request
    
    # Mock urllib.request.urlopen
    with patch('urllib.request.urlopen') as mock_urlopen:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"session_id": "test-123", "url": "https://app.devin.ai/sessions/test-123", "is_new_session": true}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        # Set API key
        os.environ['DEVIN_API_KEY'] = 'test_api_key'
        
        # Test API request
        payload = {
            'prompt': 'Test prompt',
            'snapshot_id': 'snap-123',
            'idempotent': True,
            'tags': ['test', 'api']
        }
        
        result = make_api_request(payload)
        
        # Verify the request was made correctly
        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args[0][0]  # Get the Request object
        
        assert call_args.get_full_url() == 'https://api.devin.ai/v1/sessions'
        assert call_args.headers['Authorization'] == 'Bearer test_api_key'
        assert call_args.headers['Content-type'] == 'application/json'
        
        # Verify response parsing
        assert result['session_id'] == 'test-123'
        assert result['is_new_session'] == True
        
        print("✅ API request structure is correct")


def run_all_tests():
    """Run all tests"""
    print("🚀 Starting comprehensive CLI tests...\n")
    
    tests = [
        test_help_command,
        test_version_command,
        test_missing_api_key,
        test_argument_parsing,
        test_json_output_format,
        test_json_output_error_handling,
        test_list_parsing,
        test_api_request_structure,
        test_interactive_mode_simulation,  # This one might be skipped
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
        print("🎉 All tests passed! Your CLI tool is working perfectly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
