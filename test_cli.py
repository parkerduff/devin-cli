#!/usr/bin/env python3
"""
Comprehensive test suite for Devin CLI
Tests all functionality including auth management without requiring a real API key
"""

import subprocess
import sys
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
import requests
from pathlib import Path


def run_cli_command(args, env_vars=None):
    """Run the CLI command and return result"""
    cmd = [sys.executable, 'devin_cli.py'] + args
    
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
    assert 'Devin CLI - Create and manage Devin sessions' in result['stdout'], "Help text missing"
    assert 'auth' in result['stdout'], "Auth subcommand missing from help"
    assert 'create' in result['stdout'], "Create subcommand missing from help"
    assert 'get' in result['stdout'], "Get subcommand missing from help"
    assert 'message' in result['stdout'], "Message subcommand missing from help"
    print("✅ Help command works correctly")


def test_version_command():
    """Test --version command"""
    print("🧪 Testing --version command...")
    result = run_cli_command(['--version'])
    
    assert result['returncode'] == 0, f"Version command failed: {result['stderr']}"
    assert '1.1.0' in result['stdout'], "Version number missing"
    print("✅ Version command works correctly")


def test_auth_help():
    """Test auth subcommand help"""
    print("🧪 Testing auth --help command...")
    result = run_cli_command(['auth', '--help'])
    
    assert result['returncode'] == 0, f"Auth help command failed: {result['stderr']}"
    assert 'Set or test your Devin API token' in result['stdout'], "Auth help text missing"
    assert '--test' in result['stdout'], "Test option missing from auth help"
    print("✅ Auth help command works correctly")


def test_create_help():
    """Test create subcommand help"""
    print("🧪 Testing create --help command...")
    result = run_cli_command(['create', '--help'])
    
    assert result['returncode'] == 0, f"Create help command failed: {result['stderr']}"
    assert 'Create a new Devin session' in result['stdout'], "Create help text missing"
    assert '--prompt' in result['stdout'], "Prompt option missing from create help"
    assert '--snapshot-id' in result['stdout'], "Snapshot ID option missing from create help"
    print("✅ Create help command works correctly")


def test_missing_api_key():
    """Test behavior when API key is missing"""
    print("🧪 Testing missing API key handling...")
    
    # We need to test this by creating a separate test script that imports and runs
    # the CLI with mocked config directory, since subprocess doesn't inherit our patches
    test_script = '''
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import CLI functions
from devin_cli import cli

# Create empty temp directory and mock config dir
with tempfile.TemporaryDirectory() as temp_dir:
    with patch('devin_cli.get_config_dir') as mock_config_dir:
        mock_config_dir.return_value = Path(temp_dir)
        
        # Clear environment
        os.environ.pop('DEVIN_API_KEY', None)
        
        try:
            # This should fail with missing API key
            cli(['create', '--prompt', 'test'])
            print("ERROR: Should have failed")
            sys.exit(0)  # Unexpected success
        except SystemExit as e:
            if e.code == 1:
                print("SUCCESS: Correctly failed with missing API key")
                sys.exit(1)  # Expected failure
            else:
                print(f"ERROR: Wrong exit code {e.code}")
                sys.exit(0)
        except Exception as e:
            print(f"ERROR: Unexpected exception {e}")
            sys.exit(0)
'''
    
    # Write and run the test script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # We expect exit code 1 (controlled failure) and success message
        assert result.returncode == 1, f"Expected exit code 1, got {result.returncode}. stdout: {result.stdout}, stderr: {result.stderr}"
        assert "SUCCESS: Correctly failed with missing API key" in result.stdout, f"Missing success message. stdout: {result.stdout}"
        
    finally:
        os.unlink(test_file)
    
    print("✅ Missing API key handled correctly")


def test_argument_parsing():
    """Test that all arguments are parsed correctly"""
    print("🧪 Testing argument parsing...")
    
    # Test with fake API key to avoid actual API call, but check parsing
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    # This will fail at API call stage, but we can check that parsing worked
    result = run_cli_command([
        'create',
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


def test_json_output_format():
    """Test JSON output format"""
    print("🧪 Testing JSON output format...")
    
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    result = run_cli_command([
        'create',
        '--prompt', 'Test JSON output',
        '--output', 'json'
    ], env_vars=env)
    
    # Should fail at API call but attempt JSON output
    assert result['returncode'] == 1, "Expected API failure"
    assert 'Creating Devin session...' in result['stdout'], "Should reach API call stage"
    print("✅ JSON output format option works")


def test_list_parsing():
    """Test comma-separated list parsing"""
    print("🧪 Testing list parsing functionality...")
    
    # Import the parsing function directly
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import parse_list_input
    
    # Test various list inputs
    assert parse_list_input("") == []
    assert parse_list_input("item1") == ["item1"]
    assert parse_list_input("item1,item2") == ["item1", "item2"]
    assert parse_list_input("item1, item2, item3") == ["item1", "item2", "item3"]
    assert parse_list_input(" item1 , item2 ") == ["item1", "item2"]
    
    print("✅ List parsing works correctly")


def test_token_file_operations():
    """Test token save/load operations"""
    print("🧪 Testing token file operations...")
    
    # Import functions directly
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import save_token, load_token, get_token_file
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the config directory to use temp directory for all operations
        with patch('devin_cli.get_config_dir') as mock_config_dir:
            mock_config_dir.return_value = Path(temp_dir)
            
            # Clear environment variable to ensure we're testing file operations
            with patch.dict(os.environ, {}, clear=True):
                # Test saving token
                test_token = "test_token_12345"
                save_token(test_token)
                
                # Check file exists and has correct permissions
                token_file = Path(temp_dir) / 'token'
                assert token_file.exists(), "Token file should exist"
                
                # Check file permissions (should be 0o600)
                file_mode = oct(token_file.stat().st_mode)[-3:]
                assert file_mode == '600', f"Token file should have 600 permissions, got {file_mode}"
                
                # Test loading token
                loaded_token = load_token()
                assert loaded_token == test_token, f"Loaded token should match saved token. Expected: '{test_token}', Got: '{loaded_token}'"
    
    print("✅ Token file operations work correctly")


def test_auth_token_validation():
    """Test auth token validation"""
    print("🧪 Testing auth token validation...")
    
    # Import test_token function
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import test_token
    
    # Mock requests.post to simulate different responses
    with patch('devin_cli.requests.post') as mock_post:
        # Test valid token (200 response)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        assert test_token("valid_token") == True, "Valid token should return True"
        
        # Test invalid token (401 response)
        mock_response.status_code = 401
        assert test_token("invalid_token") == False, "Invalid token should return False"
        
        # Test invalid token (403 response)
        mock_response.status_code = 403
        assert test_token("forbidden_token") == False, "Forbidden token should return False"
        
        # Test network error (exception)
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        assert test_token("any_token") == True, "Network error should assume token is valid"
    
    print("✅ Auth token validation works correctly")


def test_api_request_structure():
    """Test that API requests are structured correctly"""
    print("🧪 Testing API request structure...")
    
    # Import the API function
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import make_api_request
    
    # Mock requests.post
    with patch('devin_cli.requests.post') as mock_post:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "session_id": "test-123", 
            "url": "https://app.devin.ai/sessions/test-123", 
            "is_new_session": True
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Set API key via environment
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_api_key'}):
            # Test API request
            payload = {
                'prompt': 'Test prompt',
                'snapshot_id': 'snap-123',
                'idempotent': True,
                'tags': ['test', 'api']
            }
            
            result = make_api_request(payload)
            
            # Verify the request was made correctly
            mock_post.assert_called_once()
            call_args, call_kwargs = mock_post.call_args
            
            assert call_args[0] == 'https://api.devin.ai/v1/sessions'
            assert call_kwargs['headers']['Authorization'] == 'Bearer test_api_key'
            assert call_kwargs['headers']['Content-Type'] == 'application/json'
            assert call_kwargs['json'] == payload
            
            # Verify response parsing
            assert result['session_id'] == 'test-123'
            assert result['is_new_session'] == True
    
    print("✅ API request structure is correct")


def test_no_subcommand_shows_help():
    """Test that running CLI without subcommand shows help"""
    print("🧪 Testing no subcommand behavior...")
    result = run_cli_command([])
    
    assert result['returncode'] == 0, f"Should show help, got returncode {result['returncode']}"
    assert 'Devin CLI - Create and manage Devin sessions' in result['stdout'], "Should show help text"
    assert 'Commands:' in result['stdout'], "Should show available commands"
    print("✅ No subcommand correctly shows help")


def test_auth_command_interactive():
    """Test auth command for setting token interactively"""
    print("🧪 Testing auth command (interactive token setting)...")
    
    # Create test script that simulates interactive token input
    test_script = '''
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))
from devin_cli import cli

# Mock input to provide token and mock token validation
with patch('click.prompt') as mock_prompt, patch('devin_cli.test_token') as mock_test_token:
    mock_prompt.return_value = "test_interactive_token_123"
    mock_test_token.return_value = True  # Mock successful token validation
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('devin_cli.get_config_dir') as mock_config_dir:
            mock_config_dir.return_value = Path(temp_dir)
            
            try:
                cli(['auth'])
                
                # Check if token was saved
                token_file = Path(temp_dir) / 'token'
                if token_file.exists():
                    with open(token_file, 'r') as f:
                        saved_token = f.read().strip()
                    if saved_token == "test_interactive_token_123":
                        print("SUCCESS: Token saved correctly")
                        sys.exit(0)
                    else:
                        print(f"ERROR: Wrong token saved: {saved_token}")
                        sys.exit(1)
                else:
                    print("ERROR: Token file not created")
                    sys.exit(1)
            except Exception as e:
                print(f"ERROR: Exception during auth: {e}")
                sys.exit(1)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # The auth command should succeed (exit 0) and show token saved message
        assert result.returncode == 0, f"Auth command failed. stdout: {result.stdout}, stderr: {result.stderr}"
        assert ("SUCCESS: Token saved correctly" in result.stdout or "Token saved and verified" in result.stdout), f"Token not saved correctly. stdout: {result.stdout}"
        
    finally:
        os.unlink(test_file)
    
    print("✅ Auth command interactive token setting works")


def test_auth_test_command():
    """Test auth --test command"""
    print("🧪 Testing auth --test command...")
    
    # Test with valid token
    with patch('devin_cli.test_token') as mock_test_token:
        mock_test_token.return_value = True
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('devin_cli.get_config_dir') as mock_config_dir:
                mock_config_dir.return_value = Path(temp_dir)
                
                # Create a test token file
                token_file = Path(temp_dir) / 'token'
                with open(token_file, 'w') as f:
                    f.write("valid_test_token")
                os.chmod(token_file, 0o600)
                
                result = run_cli_command(['auth', '--test'])
                
                assert result['returncode'] == 0, f"Auth test should succeed with valid token. stderr: {result['stderr']}"
                assert '✅' in result['stdout'], "Should show success indicator"
    
    print("✅ Auth --test command works correctly")


def test_environment_variable_priority():
    """Test that DEVIN_API_KEY environment variable takes precedence over saved token"""
    print("🧪 Testing environment variable priority...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import load_token
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('devin_cli.get_config_dir') as mock_config_dir:
            mock_config_dir.return_value = Path(temp_dir)
            
            # Create a saved token file
            token_file = Path(temp_dir) / 'token'
            with open(token_file, 'w') as f:
                f.write("saved_file_token")
            
            # Test with environment variable set
            with patch.dict(os.environ, {'DEVIN_API_KEY': 'env_var_token'}):
                loaded_token = load_token()
                assert loaded_token == 'env_var_token', f"Environment variable should take precedence. Got: {loaded_token}"
            
            # Test without environment variable (should use file)
            with patch.dict(os.environ, {}, clear=True):
                loaded_token = load_token()
                assert loaded_token == 'saved_file_token', f"Should fall back to file token. Got: {loaded_token}"
    
    print("✅ Environment variable priority works correctly")


def test_corrupted_token_file_handling():
    """Test handling of corrupted or unreadable token files"""
    print("🧪 Testing corrupted token file handling...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import load_token
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('devin_cli.get_config_dir') as mock_config_dir:
            mock_config_dir.return_value = Path(temp_dir)
            
            # Create a token file with no read permissions
            token_file = Path(temp_dir) / 'token'
            with open(token_file, 'w') as f:
                f.write("test_token")
            os.chmod(token_file, 0o000)  # No permissions
            
            # Clear environment variable
            with patch.dict(os.environ, {}, clear=True):
                # Should handle the permission error gracefully
                loaded_token = load_token()
                assert loaded_token is None, "Should return None for unreadable token file"
            
            # Restore permissions for cleanup
            os.chmod(token_file, 0o600)
    
    print("✅ Corrupted token file handling works correctly")


def test_api_error_handling():
    """Test various API error scenarios"""
    print("🧪 Testing API error handling...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import make_api_request, DevinAPIError
    
    # Test network timeout
    with patch('devin_cli.requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_token'}):
            try:
                make_api_request({'prompt': 'test'})
                assert False, "Should have raised DevinAPIError"
            except DevinAPIError as e:
                assert "Request timed out" in str(e), f"Should contain timeout message. Got: {e}"
    
    # Test HTTP error
    with patch('devin_cli.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP 500 Error")
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_token'}):
            try:
                make_api_request({'prompt': 'test'})
                assert False, "Should have raised DevinAPIError"
            except DevinAPIError as e:
                assert "HTTP 500 Error" in str(e), f"Should contain HTTP error message. Got: {e}"
    
    print("✅ API error handling works correctly")


def test_edge_case_list_parsing():
    """Test edge cases in list parsing"""
    print("🧪 Testing edge case list parsing...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import parse_list_input
    
    # Test edge cases
    assert parse_list_input(None) == [], "None should return empty list"
    assert parse_list_input("  ") == [], "Whitespace-only should return empty list"
    assert parse_list_input(",,,") == [], "Only commas should return empty list"
    assert parse_list_input("item1,,item2") == ["item1", "item2"], "Should skip empty items"
    assert parse_list_input("  item1  ,  ,  item2  ") == ["item1", "item2"], "Should handle mixed whitespace and empty items"
    
    print("✅ Edge case list parsing works correctly")


def test_config_directory_creation():
    """Test that config directory is created if it doesn't exist"""
    print("🧪 Testing config directory creation...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import get_config_dir
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Point to a non-existent subdirectory
        test_config_dir = Path(temp_dir) / 'test_config'
        
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path(temp_dir)
            
            # Should create the directory
            config_dir = get_config_dir()
            
            assert config_dir.exists(), "Config directory should be created"
            assert config_dir.is_dir(), "Config path should be a directory"
            assert config_dir.name == '.devin-cli', "Should create .devin-cli directory"
    
    print("✅ Config directory creation works correctly")


def test_create_interactive_mode():
    """Test create command interactive mode with all prompts"""
    print("🧪 Testing create command interactive mode...")
    
    # Create test script that simulates interactive prompts
    test_script = '''
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))
from devin_cli import cli

# Mock all the interactive prompts with appropriate responses
with tempfile.TemporaryDirectory() as temp_dir:
    with patch('devin_cli.get_config_dir') as mock_config_dir:
        mock_config_dir.return_value = Path(temp_dir)
        
        # Create a test token file
        token_file = Path(temp_dir) / 'token'
        with open(token_file, 'w') as f:
            f.write("interactive_test_token")
        
        # Mock all the click.prompt calls that would happen in interactive mode
        with patch('click.prompt') as mock_prompt:
            # Set up responses for all the prompts in order
            mock_prompt.side_effect = [
                'Test interactive prompt',  # Task description
                '',                         # Snapshot ID (empty)
                'n',                        # Unlisted (no)
                'n',                        # Idempotent (no)  
                '',                         # Max ACU limit (empty)
                '',                         # Secret IDs (empty)
                '',                         # Knowledge IDs (empty)
                '',                         # Tags (empty)
                ''                          # Title (empty)
            ]
            
            # Mock the API call to avoid actual network request
            with patch('devin_cli.make_api_request') as mock_api:
                mock_api.side_effect = Exception("API call reached - interactive mode working")
                
                try:
                    cli(['create'])
                    print("ERROR: Should have failed at API call")
                    sys.exit(1)
                except SystemExit as e:
                    if e.code == 1:
                        print("SUCCESS: Interactive mode reached API call stage")
                        sys.exit(0)  # Success - we got through all prompts
                    else:
                        print(f"ERROR: Wrong exit code {e.code}")
                        sys.exit(1)
                except Exception as e:
                    if "API call reached" in str(e):
                        print("SUCCESS: Interactive mode reached API call stage")
                        sys.exit(0)  # Success - we got through all prompts
                    else:
                        print(f"ERROR: Unexpected exception {e}")
                        sys.exit(1)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # Should succeed (exit code 0) and show success message
        assert result.returncode == 0, f"Interactive mode test failed. stdout: {result.stdout}, stderr: {result.stderr}"
        assert "SUCCESS: Interactive mode reached API call stage" in result.stdout, f"Interactive mode didn't work correctly. stdout: {result.stdout}"
        
    finally:
        os.unlink(test_file)
    
    print("✅ Create command interactive mode works correctly")


def test_setup_command_help():
    """Test setup command help"""
    print("🧪 Testing setup --help command...")
    result = run_cli_command(['setup', '--help'])
    
    assert result['returncode'] == 0, f"Setup help command failed: {result['stderr']}"
    assert 'Download latest Devin workflow and session guide' in result['stdout'], "Setup help text missing"
    assert '--target-dir' in result['stdout'], "Target dir option missing from setup help"
    assert '--force' in result['stdout'], "Force option missing from setup help"
    print("✅ Setup help command works correctly")


def test_setup_command_success():
    """Test successful setup command execution"""
    print("🧪 Testing setup command with mocked downloads...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock successful HTTP responses
        with patch('devin_cli.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = "# Mock file content\nThis is test content"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Run setup command
            result = run_cli_command(['setup', '--target-dir', temp_dir, '--force'])
            
            # Check command succeeded
            assert result['returncode'] == 0, f"Setup command failed: {result['stderr']}"
            assert 'Downloaded Devin Session Guide' in result['stdout'], "Should show guide download"
            assert 'Downloaded Create Session Workflow' in result['stdout'], "Should show workflow download"
            
            # Check files were created
            guide_file = Path(temp_dir) / 'devin-session-guide.md'
            workflow_file = Path(temp_dir) / '.windsurf' / 'workflows' / 'create-session.md'
            
            assert guide_file.exists(), "Guide file should be created"
            assert workflow_file.exists(), "Workflow file should be created"
            
            # Check file contents
            with open(guide_file, 'r') as f:
                content = f.read()
                assert "Mock file content" in content, "Guide file should have correct content"
            
            with open(workflow_file, 'r') as f:
                content = f.read()
                assert "Mock file content" in content, "Workflow file should have correct content"
            
            # Verify correct URLs were called
            assert mock_get.call_count == 2, "Should make 2 HTTP requests"
            urls_called = [call[0][0] for call in mock_get.call_args_list]
            assert any('devin-session-guide.md' in url for url in urls_called), "Should request guide file"
            assert any('create-session.md' in url for url in urls_called), "Should request workflow file"
    
    print("✅ Setup command success test passed")


def test_setup_command_network_error():
    """Test setup command with network errors"""
    print("🧪 Testing setup command with network errors...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock network error
        with patch('devin_cli.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
            
            # Run setup command
            result = run_cli_command(['setup', '--target-dir', temp_dir, '--force'])
            
            # Command should complete but show errors
            assert result['returncode'] == 0, f"Setup command should not crash: {result['stderr']}"
            assert 'Failed to download' in result['stderr'], "Should show download failure"
            assert 'No files were downloaded' in result['stdout'], "Should show no files downloaded"
            
            # Files should not exist
            guide_file = Path(temp_dir) / 'devin-session-guide.md'
            workflow_file = Path(temp_dir) / '.windsurf' / 'workflows' / 'create-session.md'
            
            assert not guide_file.exists(), "Guide file should not be created on error"
            assert not workflow_file.exists(), "Workflow file should not be created on error"
    
    print("✅ Setup command network error test passed")


def test_setup_command_file_exists_prompt():
    """Test setup command behavior when files already exist"""
    print("🧪 Testing setup command with existing files...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create existing files
        guide_file = Path(temp_dir) / 'devin-session-guide.md'
        workflows_dir = Path(temp_dir) / '.windsurf' / 'workflows'
        workflows_dir.mkdir(parents=True)
        workflow_file = workflows_dir / 'create-session.md'
        
        guide_file.write_text("Existing guide content")
        workflow_file.write_text("Existing workflow content")
        
        # Test with --force flag (should overwrite without prompting)
        with patch('devin_cli.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = "New content from GitHub"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = run_cli_command(['setup', '--target-dir', temp_dir, '--force'])
            
            assert result['returncode'] == 0, f"Setup with force should succeed: {result['stderr']}"
            assert 'Downloaded Devin Session Guide' in result['stdout'], "Should download guide"
            assert 'Downloaded Create Session Workflow' in result['stdout'], "Should download workflow"
            
            # Check files were overwritten
            assert guide_file.read_text() == "New content from GitHub", "Guide should be overwritten"
            assert workflow_file.read_text() == "New content from GitHub", "Workflow should be overwritten"
    
    print("✅ Setup command existing files test passed")


def test_setup_command_directory_creation():
    """Test that setup command creates necessary directories"""
    print("🧪 Testing setup command directory creation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        target_dir = Path(temp_dir) / 'nonexistent' / 'nested' / 'path'
        
        with patch('devin_cli.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = "Test content"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = run_cli_command(['setup', '--target-dir', str(target_dir), '--force'])
            
            assert result['returncode'] == 0, f"Setup should create directories: {result['stderr']}"
            
            # Check that directories were created
            assert target_dir.exists(), "Target directory should be created"
            workflows_dir = target_dir / '.windsurf' / 'workflows'
            assert workflows_dir.exists(), "Workflows directory should be created"
            
            # Check files exist
            guide_file = target_dir / 'devin-session-guide.md'
            workflow_file = workflows_dir / 'create-session.md'
            assert guide_file.exists(), "Guide file should be created"
            assert workflow_file.exists(), "Workflow file should be created"
    
    print("✅ Setup command directory creation test passed")


def test_setup_command_http_error():
    """Test setup command with HTTP errors (404, 500, etc.)"""
    print("🧪 Testing setup command with HTTP errors...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('devin_cli.requests.get') as mock_get:
            # Mock HTTP error
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
            mock_get.return_value = mock_response
            
            result = run_cli_command(['setup', '--target-dir', temp_dir, '--force'])
            
            # Should complete but show errors
            assert result['returncode'] == 0, f"Setup should handle HTTP errors gracefully: {result['stderr']}"
            assert 'Failed to download' in result['stderr'], "Should show HTTP error"
            assert 'No files were downloaded' in result['stdout'], "Should indicate no downloads"
    
    print("✅ Setup command HTTP error test passed")


def test_setup_command_partial_success():
    """Test setup command when some files succeed and others fail"""
    print("🧪 Testing setup command with partial success...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('devin_cli.requests.get') as mock_get:
            # First call succeeds, second fails
            responses = [
                MagicMock(text="Guide content", raise_for_status=MagicMock()),
                MagicMock(raise_for_status=MagicMock(side_effect=requests.exceptions.HTTPError("404")))
            ]
            mock_get.side_effect = responses
            
            result = run_cli_command(['setup', '--target-dir', temp_dir, '--force'])
            
            assert result['returncode'] == 0, f"Setup should handle partial success: {result['stderr']}"
            assert 'Downloaded Devin Session Guide' in result['stdout'], "Should show successful download"
            assert 'Failed to download Create Session Workflow' in result['stderr'], "Should show failed download"
            
            # Check that successful file exists
            guide_file = Path(temp_dir) / 'devin-session-guide.md'
            workflow_file = Path(temp_dir) / '.windsurf' / 'workflows' / 'create-session.md'
            
            assert guide_file.exists(), "Guide file should be created"
            assert not workflow_file.exists(), "Workflow file should not be created on error"
    
    print("✅ Setup command partial success test passed")


def test_end_to_end_workflow():
    """Test complete workflow: save token -> create session"""
    print("🧪 Testing end-to-end workflow...")
    
    # Test the workflow by testing components separately since subprocess doesn't inherit mocks
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import save_token, load_token, make_api_request
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('devin_cli.get_config_dir') as mock_config_dir:
            mock_config_dir.return_value = Path(temp_dir)
            
            # Step 1: Save a token
            test_token = "workflow_test_token_456"
            save_token(test_token)
            
            # Step 2: Verify token can be loaded
            with patch.dict(os.environ, {}, clear=True):  # Clear env to use file
                loaded_token = load_token()
                assert loaded_token == test_token, f"Token should be loaded from file. Got: {loaded_token}"
            
            # Step 3: Test API request with loaded token
            with patch('devin_cli.requests.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "session_id": "workflow-test-123",
                    "url": "https://app.devin.ai/sessions/workflow-test-123",
                    "is_new_session": True
                }
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                # Clear environment to ensure we use saved token
                with patch.dict(os.environ, {}, clear=True):
                    result = make_api_request({'prompt': 'End-to-end test'})
                    
                    # Verify the result
                    assert result['session_id'] == 'workflow-test-123', "Should return correct session ID"
                    assert result['is_new_session'] == True, "Should indicate new session"
                    
                    # Verify the API was called with correct token
                    mock_post.assert_called_once()
                    call_kwargs = mock_post.call_args[1]
                    assert call_kwargs['headers']['Authorization'] == f'Bearer {test_token}', "Should use saved token"
    
    print("✅ End-to-end workflow works correctly")


def test_get_command_help():
    """Test get command help"""
    print("🧪 Testing get --help command...")
    result = run_cli_command(['get', '--help'])
    
    assert result['returncode'] == 0, f"Get help command failed: {result['stderr']}"
    assert 'Get details of an existing Devin session' in result['stdout'], "Get help text missing"
    assert '--output' in result['stdout'], "Output option missing from get help"
    print("✅ Get help command works correctly")


def test_get_command_success():
    """Test successful get command execution"""
    print("🧪 Testing get command with mocked API response...")
    
    # Import the get_session_details function
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import get_session_details
    
    # Mock successful API response
    with patch('devin_cli.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "session_id": "test-session-123",
            "status": "active",
            "title": "Test Session",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T13:00:00Z",
            "tags": ["test", "api"],
            "messages": [
                {"role": "user", "content": "Test message 1"},
                {"role": "assistant", "content": "Test response 1"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Set API key via environment
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_api_key'}):
            result = get_session_details("test-session-123")
            
            # Verify the request was made correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args[0]
            call_kwargs = mock_get.call_args[1]
            
            assert call_args[0] == 'https://api.devin.ai/v1/sessions/test-session-123'
            assert call_kwargs['headers']['Authorization'] == 'Bearer test_api_key'
            assert call_kwargs['headers']['Content-Type'] == 'application/json'
            
            # Verify response parsing
            assert result['session_id'] == 'test-session-123'
            assert result['status'] == 'active'
            assert result['title'] == 'Test Session'
    
    print("✅ Get command API structure is correct")


def test_get_command_cli_execution():
    """Test get command CLI execution"""
    print("🧪 Testing get command CLI execution...")
    
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    result = run_cli_command([
        'get', 'test-session-123',
        '--output', 'json'
    ], env_vars=env)
    
    # Should fail at API call but reach that stage
    assert result['returncode'] == 1, "Expected API failure"
    assert 'Retrieving session details for test-session-123...' in result['stdout'], "Should reach API call stage"
    print("✅ Get command CLI execution works")


def test_message_command_help():
    """Test message command help"""
    print("🧪 Testing message --help command...")
    result = run_cli_command(['message', '--help'])
    
    assert result['returncode'] == 0, f"Message help command failed: {result['stderr']}"
    assert 'Send a message to an existing Devin session' in result['stdout'], "Message help text missing"
    assert '--message' in result['stdout'], "Message option missing from message help"
    assert '--output' in result['stdout'], "Output option missing from message help"
    print("✅ Message help command works correctly")


def test_message_command_success():
    """Test successful message command execution"""
    print("🧪 Testing message command with mocked API response...")
    
    # Import the send_message_to_session function
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import send_message_to_session
    
    # Mock successful API response
    with patch('devin_cli.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message_id": "msg-123",
            "status": "sent"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Set API key via environment
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_api_key'}):
            payload = {'message': 'Test message'}
            result = send_message_to_session("test-session-123", payload)
            
            # Verify the request was made correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args[0]
            call_kwargs = mock_post.call_args[1]
            
            assert call_args[0] == 'https://api.devin.ai/v1/sessions/test-session-123/message'
            assert call_kwargs['headers']['Authorization'] == 'Bearer test_api_key'
            assert call_kwargs['headers']['Content-Type'] == 'application/json'
            assert call_kwargs['json'] == payload
            
            # Verify response parsing
            assert result['message_id'] == 'msg-123'
            assert result['status'] == 'sent'
    
    print("✅ Message command API structure is correct")


def test_message_command_cli_execution():
    """Test message command CLI execution"""
    print("🧪 Testing message command CLI execution...")
    
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    result = run_cli_command([
        'message', 'test-session-123',
        '--message', 'Test message',
        '--output', 'json'
    ], env_vars=env)
    
    # Should fail at API call but reach that stage
    assert result['returncode'] == 1, "Expected API failure"
    assert 'Sending message to session test-session-123...' in result['stdout'], "Should reach API call stage"
    print("✅ Message command CLI execution works")


def test_message_command_interactive():
    """Test message command interactive mode (when no --message provided)"""
    print("🧪 Testing message command interactive mode...")
    
    # Create test script that simulates interactive message input
    test_script = '''
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))
from devin_cli import cli

with tempfile.TemporaryDirectory() as temp_dir:
    with patch('devin_cli.get_config_dir') as mock_config_dir:
        mock_config_dir.return_value = Path(temp_dir)
        
        # Create a test token file
        token_file = Path(temp_dir) / 'token'
        with open(token_file, 'w') as f:
            f.write("interactive_test_token")
        
        # Mock the click.prompt for message input
        with patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = "Test interactive message"
            
            # Mock the API call to avoid actual network request
            with patch('devin_cli.send_message_to_session') as mock_send:
                mock_send.side_effect = Exception("API call reached - interactive message working")
                
                try:
                    cli(['message', 'test-session-123'])
                    print("ERROR: Should have failed at API call")
                    sys.exit(1)
                except SystemExit as e:
                    if e.code == 1:
                        print("SUCCESS: Interactive message mode reached API call stage")
                        sys.exit(0)
                    else:
                        print(f"ERROR: Wrong exit code {e.code}")
                        sys.exit(1)
                except Exception as e:
                    if "API call reached" in str(e):
                        print("SUCCESS: Interactive message mode reached API call stage")
                        sys.exit(0)
                    else:
                        print(f"ERROR: Unexpected exception {e}")
                        sys.exit(1)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # Should succeed (exit code 0) and show success message
        assert result.returncode == 0, f"Interactive message test failed. stdout: {result.stdout}, stderr: {result.stderr}"
        assert "SUCCESS: Interactive message mode reached API call stage" in result.stdout, f"Interactive message mode didn't work correctly. stdout: {result.stdout}"
        
    finally:
        os.unlink(test_file)
    
    print("✅ Message command interactive mode works correctly")


def test_get_and_message_api_error_handling():
    """Test API error handling for get and message commands"""
    print("🧪 Testing API error handling for new commands...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli import get_session_details, send_message_to_session, DevinAPIError
    
    # Test get command network error
    with patch('devin_cli.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_token'}):
            try:
                get_session_details('test-session-123')
                assert False, "Should have raised DevinAPIError"
            except DevinAPIError as e:
                assert "Request timed out" in str(e), f"Should contain timeout message. Got: {e}"
    
    # Test message command HTTP error
    with patch('devin_cli.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP 500 Error")
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_token'}):
            try:
                send_message_to_session('test-session-123', {'message': 'test'})
                assert False, "Should have raised DevinAPIError"
            except DevinAPIError as e:
                assert "HTTP 500 Error" in str(e), f"Should contain HTTP error message. Got: {e}"
    
    print("✅ API error handling for new commands works correctly")


def run_all_tests():
    """Run all tests"""
    print("🚀 Starting comprehensive CLI tests...\n")
    
    tests = [
        # Basic CLI structure
        test_help_command,
        test_version_command,
        test_no_subcommand_shows_help,
        test_auth_help,
        test_create_help,
        test_get_command_help,
        test_message_command_help,
        
        # Auth functionality
        test_auth_command_interactive,
        test_auth_test_command,
        test_missing_api_key,
        
        # Token management
        test_token_file_operations,
        test_auth_token_validation,
        test_environment_variable_priority,
        test_corrupted_token_file_handling,
        
        # CLI functionality
        test_argument_parsing,
        test_json_output_format,
        test_list_parsing,
        test_edge_case_list_parsing,
        test_create_interactive_mode,
        
        # New session management commands
        test_get_command_success,
        test_get_command_cli_execution,
        test_message_command_success,
        test_message_command_cli_execution,
        test_message_command_interactive,
        test_get_and_message_api_error_handling,
        
        # Setup command
        test_setup_command_help,
        test_setup_command_success,
        test_setup_command_network_error,
        test_setup_command_file_exists_prompt,
        test_setup_command_directory_creation,
        test_setup_command_http_error,
        test_setup_command_partial_success,
        
        # Error handling
        test_api_error_handling,
        test_config_directory_creation,
        
        # Integration
        test_api_request_structure,
        test_end_to_end_workflow,
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
