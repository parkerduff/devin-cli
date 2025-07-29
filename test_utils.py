#!/usr/bin/env python3
"""
Shared test utilities for Devin CLI testing
"""

import os
import sys
import json
import tempfile
import subprocess
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error


class MockResponse:
    """Mock HTTP response for testing"""
    def __init__(self, json_data: Dict[str, Any], status_code: int = 200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")
    
    def read(self):
        return self.text.encode('utf-8')
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass


class MockHTTPError(Exception):
    """Mock HTTP error for urllib testing"""
    def __init__(self, code: int, msg: str = "HTTP Error"):
        self.code = code
        self.msg = msg
    
    def read(self):
        return f"HTTP {self.code}: {self.msg}".encode('utf-8')


def create_mock_api_response(session_id: str = "test-session-123", 
                           url: str = "https://app.devin.ai/sessions/test-session-123",
                           is_new_session: bool = True) -> Dict[str, Any]:
    """Create a mock API response"""
    return {
        "session_id": session_id,
        "url": url,
        "is_new_session": is_new_session
    }


def run_cli_subprocess(cli_file: str, args: List[str], env_vars: Optional[Dict[str, str]] = None, 
                       mock_api_response: Optional[MockResponse] = None) -> Dict[str, Any]:
    """Run CLI command via subprocess and return result"""
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    
    if mock_api_response and '--prompt' in args:
        return run_cli_with_mock(cli_file, args, env, mock_api_response)
    
    cmd = [sys.executable, cli_file] + args
    
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


def run_cli_with_mock(cli_file: str, args: List[str], env: Dict[str, str], 
                     mock_response: MockResponse) -> Dict[str, Any]:
    """Run CLI with mocked API response"""
    cli_dir = os.path.dirname(__file__)
    script_content = f'''
import sys
import os
sys.path.insert(0, "{cli_dir}")

from unittest.mock import patch, MagicMock

# Set up environment
for key, value in {env!r}.items():
    os.environ[key] = value

mock_response = MagicMock()
mock_response.json.return_value = {mock_response.json_data!r}
mock_response.status_code = {mock_response.status_code}
mock_response.text = {mock_response.text!r}

if "{cli_file}" == "devin_cli.py":
    with patch('requests.post', return_value=mock_response):
        from devin_cli import create_session
        import click.testing
        runner = click.testing.CliRunner()
        result = runner.invoke(create_session, {args!r})
        print(result.output, end='')
        sys.exit(result.exit_code)
else:
    mock_urlopen_response = MagicMock()
    mock_urlopen_response.read.return_value = {mock_response.text!r}.encode('utf-8')
    mock_urlopen_response.__enter__.return_value = mock_urlopen_response
    
    with patch('urllib.request.urlopen', return_value=mock_urlopen_response):
        if "{cli_file}" == "devin_cli_standalone.py":
            from devin_cli_standalone import main
        elif "{cli_file}" == "devin_cli_enhanced.py":
            from devin_cli_enhanced import main
        
        sys.argv = ["{cli_file}"] + {args!r}
        try:
            main()
        except SystemExit as e:
            sys.exit(e.code)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        test_file = f.name
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, 
                              cwd=os.path.dirname(__file__))
        os.unlink(test_file)
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        if os.path.exists(test_file):
            os.unlink(test_file)
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }


def create_interactive_test_script(cli_file: str, inputs: List[str], args: Optional[List[str]] = None) -> str:
    """Create a temporary script for testing interactive mode"""
    if args is None:
        args = ['--interactive']
    
    cli_dir = os.path.dirname(__file__)
    script_content = f'''
import sys
import os
sys.path.insert(0, "{cli_dir}")

inputs = iter({inputs!r})

def mock_input(prompt):
    try:
        return next(inputs)
    except StopIteration:
        return ""

import builtins
builtins.input = mock_input

os.environ['DEVIN_API_KEY'] = 'fake_key_for_testing'

if "{cli_file}" == "devin_cli.py":
    from devin_cli import create_session
    import click.testing
    runner = click.testing.CliRunner()
    result = runner.invoke(create_session, {args!r})
    print(result.output)
    sys.exit(result.exit_code)
elif "{cli_file}" == "devin_cli_standalone.py":
    from devin_cli_standalone import main
    sys.argv = ['devin_cli_standalone.py'] + {args!r}
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code)
elif "{cli_file}" == "devin_cli_enhanced.py":
    from devin_cli_enhanced import main
    sys.argv = ['devin_cli_enhanced.py'] + {args!r}
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code)
'''
    return script_content


def mock_requests_post(mock_response: MockResponse):
    """Create a mock for requests.post"""
    def _mock_post(*args, **kwargs):
        if mock_response.status_code >= 400:
            mock_response.raise_for_status = lambda: None
            import requests
            error = requests.HTTPError(f"HTTP {mock_response.status_code}")
            error.response = mock_response
            raise error
        return mock_response
    return _mock_post


def mock_urllib_urlopen(mock_response: MockResponse):
    """Create a mock for urllib.request.urlopen"""
    def _mock_urlopen(*args, **kwargs):
        if mock_response.status_code >= 400:
            raise MockHTTPError(mock_response.status_code, "Test error")
        return mock_response
    return _mock_urlopen


def assert_api_payload_structure(payload: Dict[str, Any], expected_prompt: str):
    """Assert that API payload has correct structure"""
    assert 'prompt' in payload, "Payload missing required 'prompt' field"
    assert payload['prompt'] == expected_prompt, f"Expected prompt '{expected_prompt}', got '{payload['prompt']}'"
    
    optional_fields = ['snapshot_id', 'unlisted', 'idempotent', 'max_acu_limit', 
                      'secret_ids', 'knowledge_ids', 'tags', 'title']
    
    for field in payload:
        if field not in ['prompt'] + optional_fields:
            raise AssertionError(f"Unexpected field in payload: {field}")


def create_temp_config_dir() -> str:
    """Create a temporary config directory for testing enhanced CLI"""
    temp_dir = tempfile.mkdtemp()
    return temp_dir


def cleanup_temp_dir(temp_dir: str):
    """Clean up temporary directory"""
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def get_cli_implementations() -> List[str]:
    """Get list of CLI implementation files to test"""
    return ['devin_cli.py', 'devin_cli_standalone.py', 'devin_cli_enhanced.py']


def get_test_parameters() -> Dict[str, Any]:
    """Get standard test parameters for session creation"""
    return {
        'prompt': 'Test session creation',
        'snapshot_id': 'snap-test-123',
        'unlisted': True,
        'idempotent': True,
        'max_acu_limit': 100,
        'secret_ids': 'secret1,secret2',
        'knowledge_ids': 'kb1,kb2',
        'tags': 'test,cli,automation',
        'title': 'Test Session Title'
    }


def format_cli_args(params: Dict[str, Any]) -> List[str]:
    """Format parameters as CLI arguments"""
    args = []
    for key, value in params.items():
        if key == 'prompt':
            args.extend(['--prompt', str(value)])
        elif key == 'snapshot_id':
            args.extend(['--snapshot-id', str(value)])
        elif key == 'unlisted' and value:
            args.append('--unlisted')
        elif key == 'idempotent' and value:
            args.append('--idempotent')
        elif key == 'max_acu_limit':
            args.extend(['--max-acu-limit', str(value)])
        elif key == 'secret_ids':
            args.extend(['--secret-ids', str(value)])
        elif key == 'knowledge_ids':
            args.extend(['--knowledge-ids', str(value)])
        elif key == 'tags':
            args.extend(['--tags', str(value)])
        elif key == 'title':
            args.extend(['--title', str(value)])
    return args
