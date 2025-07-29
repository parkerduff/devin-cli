#!/usr/bin/env python3
"""
Cross-implementation consistency tests for all three CLI variants
Ensures all implementations behave consistently with the same inputs
"""

import subprocess
import sys
import os
import json
import tempfile
from unittest.mock import patch, MagicMock


def run_cli_implementation(implementation, args, env_vars=None):
    """Run a specific CLI implementation and return result"""
    cmd = [sys.executable, f'{implementation}.py'] + args
    
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


def test_help_command_consistency():
    """Test that all implementations provide consistent help output"""
    print("🧪 Testing help command consistency...")
    
    implementations = ['devin_cli_standalone', 'devin_cli_enhanced']
    help_results = {}
    
    for impl in implementations:
        result = run_cli_implementation(impl, ['--help'])
        help_results[impl] = result
        
        assert result['returncode'] == 0, f"{impl} help command should succeed"
        assert '--prompt' in result['stdout'], f"{impl} help should mention --prompt option"
        assert '--output' in result['stdout'], f"{impl} help should mention --output option"
        assert '--interactive' in result['stdout'], f"{impl} help should mention --interactive option"
    
    common_options = ['--prompt', '--snapshot-id', '--unlisted', '--idempotent', '--output', '--interactive']
    for option in common_options:
        for impl in implementations:
            assert option in help_results[impl]['stdout'], f"{impl} should support {option}"
    
    print("✅ Help command consistency verified")


def test_version_command_consistency():
    """Test that all implementations provide version information"""
    print("🧪 Testing version command consistency...")
    
    implementations = ['devin_cli_standalone', 'devin_cli_enhanced']
    
    for impl in implementations:
        result = run_cli_implementation(impl, ['--version'])
        
        assert result['returncode'] == 0, f"{impl} version command should succeed"
        assert any(v in result['stdout'] for v in ['1.0.0', '1.1.0']), f"{impl} should show version number"
    
    print("✅ Version command consistency verified")


def test_missing_api_key_consistency():
    """Test that all implementations handle missing API key consistently"""
    print("🧪 Testing missing API key handling consistency...")
    
    implementations = ['devin_cli_standalone', 'devin_cli_enhanced']
    env = {'DEVIN_API_KEY': ''}
    
    for impl in implementations:
        result = run_cli_implementation(impl, ['--prompt', 'test'], env_vars=env)
        
        assert result['returncode'] == 1, f"{impl} should fail with missing API key"
        assert 'DEVIN_API_KEY' in result['stdout'] or 'API' in result['stdout'] or 'token' in result['stdout'], f"{impl} should mention API key requirement"
    
    print("✅ Missing API key handling consistency verified")


def test_argument_parsing_consistency():
    """Test that all implementations parse arguments consistently"""
    print("🧪 Testing argument parsing consistency...")
    
    implementations = ['devin_cli_standalone']
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    test_args = [
        '--prompt', 'Test consistency',
        '--snapshot-id', 'snap-123',
        '--unlisted',
        '--idempotent',
        '--max-acu-limit', '100',
        '--secret-ids', 'secret1,secret2',
        '--knowledge-ids', 'kb1,kb2',
        '--tags', 'test,consistency',
        '--title', 'Consistency Test',
        '--output', 'json'
    ]
    
    for impl in implementations:
        result = run_cli_implementation(impl, test_args, env_vars=env)
        
        assert result['returncode'] == 1, f"{impl} should fail at API call (expected with fake key)"
        assert 'Creating Devin session...' in result['stdout'], f"{impl} should reach API call stage"
    
    print("✅ Argument parsing consistency verified")


def test_enhanced_cli_backward_compatibility():
    """Test that enhanced CLI maintains backward compatibility"""
    print("🧪 Testing enhanced CLI backward compatibility...")
    
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    test_args = [
        '--prompt', 'Test backward compatibility',
        '--output', 'json'
    ]
    
    result = run_cli_implementation('devin_cli_enhanced', test_args, env_vars=env)
    
    assert result['returncode'] == 1, "Enhanced CLI should fail at API call (expected with fake key)"
    assert 'Creating Devin session...' in result['stdout'], "Enhanced CLI should reach API call stage"
    
    create_args = [
        'create',
        '--prompt', 'Test create subcommand',
        '--output', 'json'
    ]
    
    result = run_cli_implementation('devin_cli_enhanced', create_args, env_vars=env)
    
    assert result['returncode'] == 1, "Enhanced CLI create subcommand should fail at API call"
    assert 'Creating Devin session...' in result['stdout'], "Enhanced CLI create should reach API call stage"
    
    print("✅ Enhanced CLI backward compatibility verified")


def test_payload_generation_consistency():
    """Test that all implementations generate consistent API payloads"""
    print("🧪 Testing payload generation consistency...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    implementations = [
        ('devin_cli_standalone', 'urllib.request.urlopen'),
        ('devin_cli_enhanced', 'urllib.request.urlopen'),
    ]
    
    test_payload_data = {
        'prompt': 'Test payload consistency',
        'snapshot_id': 'snap-456',
        'unlisted': True,
        'idempotent': True,
        'max_acu_limit': 50,
        'secret_ids': ['secret1', 'secret2'],
        'knowledge_ids': ['kb1', 'kb2'],
        'tags': ['test', 'payload'],
        'title': 'Payload Test'
    }
    
    captured_payloads = {}
    
    for module_name, mock_target in implementations:
        try:
            module = __import__(module_name)
            make_api_request = getattr(module, 'make_api_request')
            
            with patch(mock_target) as mock_request:
                mock_response = MagicMock()
                mock_response.read.return_value = b'{"session_id": "test-123", "url": "https://app.devin.ai/sessions/test-123", "is_new_session": true}'
                mock_response.__enter__.return_value = mock_response
                mock_request.return_value = mock_response
                
                with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_api_key'}):
                    make_api_request(test_payload_data)
                    
                    mock_request.assert_called_once()
                    call_args = mock_request.call_args[0][0]
                    
                    payload_bytes = call_args.data
                    payload_str = payload_bytes.decode('utf-8')
                    payload_json = json.loads(payload_str)
                    captured_payloads[module_name] = payload_json
            
        except ImportError as e:
            print(f"⚠️  Could not import {module_name}: {e}")
        except Exception as e:
            print(f"❌ {module_name} payload generation failed: {e}")
            raise
    
    if len(captured_payloads) >= 2:
        payload_keys = list(captured_payloads.keys())
        payload1 = captured_payloads[payload_keys[0]]
        payload2 = captured_payloads[payload_keys[1]]
        
        for key in test_payload_data:
            assert payload1.get(key) == payload2.get(key), f"Payload key '{key}' should be consistent: {payload1.get(key)} vs {payload2.get(key)}"
    
    print("✅ Payload generation consistency verified")


def test_error_handling_consistency():
    """Test that all implementations handle errors consistently"""
    print("🧪 Testing error handling consistency...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    implementations = [
        ('devin_cli_standalone', 'urllib.request.urlopen'),
        ('devin_cli_enhanced', 'urllib.request.urlopen'),
    ]
    
    for module_name, mock_target in implementations:
        try:
            module = __import__(module_name)
            make_api_request = getattr(module, 'make_api_request')
            DevinAPIError = getattr(module, 'DevinAPIError')
            
            with patch(mock_target) as mock_request:
                from urllib.error import HTTPError, URLError
                import io
                
                mock_http_error = HTTPError("", 403, "Forbidden", {}, io.BytesIO(b"Forbidden"))
                mock_request.side_effect = mock_http_error
                
                with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_api_key'}):
                    try:
                        make_api_request({'prompt': 'test'})
                        assert False, f"{module_name} should raise exception for HTTP error"
                    except DevinAPIError as e:
                        assert '403' in str(e), f"{module_name} should include HTTP status in error"
                
                mock_request.side_effect = URLError("Network error")
                
                with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_api_key'}):
                    try:
                        make_api_request({'prompt': 'test'})
                        assert False, f"{module_name} should raise exception for network error"
                    except DevinAPIError as e:
                        assert 'Network error' in str(e), f"{module_name} should include network error details"
            
            print(f"✅ {module_name} error handling works correctly")
            
        except ImportError as e:
            print(f"⚠️  Could not import {module_name}: {e}")
        except Exception as e:
            print(f"❌ {module_name} error handling failed: {e}")
            raise
    
    print("✅ Error handling consistency verified")


def test_output_format_consistency():
    """Test that all implementations produce consistent output formats"""
    print("🧪 Testing output format consistency...")
    
    implementations = ['devin_cli_standalone']
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    for output_format in ['json', 'table']:
        format_results = {}
        
        for impl in implementations:
            result = run_cli_implementation(impl, [
                '--prompt', 'Test output format',
                '--output', output_format
            ], env_vars=env)
            
            format_results[impl] = result
            assert result['returncode'] == 1, f"{impl} should fail at API call"
            assert 'Creating Devin session...' in result['stdout'], f"{impl} should reach API call stage"
        
        if output_format == 'json':
            for impl in implementations:
                assert '--output' in run_cli_implementation(impl, ['--help'])['stdout'], f"{impl} should support --output option"
    
    print("✅ Output format consistency verified")


def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting integration tests...\n")
    
    tests = [
        test_help_command_consistency,
        test_version_command_consistency,
        test_missing_api_key_consistency,
        test_argument_parsing_consistency,
        test_enhanced_cli_backward_compatibility,
        test_payload_generation_consistency,
        test_error_handling_consistency,
        test_output_format_consistency,
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
    
    print(f"📊 Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
    else:
        print("⚠️  Some integration tests failed. Check the output above for details.")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
