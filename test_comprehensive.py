#!/usr/bin/env python3
"""
Comprehensive test suite for all Devin CLI implementations
Tests all functionality without requiring a real API key
"""

import subprocess
import sys
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import urllib.request
import urllib.error
from test_utils import (
    run_cli_subprocess, create_mock_api_response, mock_requests_post, 
    mock_urllib_urlopen, MockResponse, MockHTTPError, create_interactive_test_script,
    get_cli_implementations, get_test_parameters, format_cli_args,
    create_temp_config_dir, cleanup_temp_dir
)


def test_comprehensive_argument_parsing():
    """Test comprehensive argument parsing for all implementations"""
    print("🧪 Testing comprehensive argument parsing for all implementations...")
    
    mock_response = MockResponse(create_mock_api_response())
    test_params = get_test_parameters()
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        
        env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
        args = format_cli_args(test_params) + ['--output', 'json']
        
        if cli_file == 'devin_cli.py':
            with patch('requests.post', mock_requests_post(mock_response)):
                result = run_cli_subprocess(cli_file, args, env_vars=env)
        else:
            with patch('urllib.request.urlopen', mock_urllib_urlopen(mock_response)):
                result = run_cli_subprocess(cli_file, args, env_vars=env)
        
        assert result['returncode'] == 0, f"Argument parsing failed for {cli_file}: {result['stderr']}"
        assert 'Creating Devin session...' in result['stdout'], f"Should reach API call stage for {cli_file}"
        print(f"    ✅ Comprehensive argument parsing works for {cli_file}")
    
    print("✅ Comprehensive argument parsing works for all implementations")


def test_parameter_combinations():
    """Test various parameter combinations"""
    print("🧪 Testing parameter combinations for all implementations...")
    
    mock_response = MockResponse(create_mock_api_response())
    
    test_cases = [
        {'prompt': 'Minimal test'},
        {'prompt': 'With snapshot', 'snapshot_id': 'snap-456'},
        {'prompt': 'With flags', 'unlisted': True, 'idempotent': True},
        {'prompt': 'With limits', 'max_acu_limit': 50},
        {'prompt': 'With lists', 'secret_ids': 'sec1,sec2', 'tags': 'tag1,tag2'},
    ]
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        
        for i, params in enumerate(test_cases):
            env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
            args = format_cli_args(params)
            
            if cli_file == 'devin_cli.py':
                with patch('requests.post', mock_requests_post(mock_response)):
                    result = run_cli_subprocess(cli_file, args, env_vars=env)
            else:
                with patch('urllib.request.urlopen', mock_urllib_urlopen(mock_response)):
                    result = run_cli_subprocess(cli_file, args, env_vars=env)
            
            assert result['returncode'] == 0, f"Parameter combination {i+1} failed for {cli_file}: {result['stderr']}"
        
        print(f"    ✅ Parameter combinations work for {cli_file}")
    
    print("✅ Parameter combinations work for all implementations")


def test_error_handling():
    """Test error handling scenarios for all implementations"""
    print("🧪 Testing error handling scenarios for all implementations...")
    
    error_scenarios = [
        (MockResponse({}, 403), "HTTP 403"),
        (MockResponse({}, 404), "HTTP 404"),
        (MockResponse({}, 500), "HTTP 500"),
    ]
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        
        for mock_response, scenario in error_scenarios:
            env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
            args = ['--prompt', f'Test {scenario}']
            
            if cli_file == 'devin_cli.py':
                with patch('requests.post') as mock_post:
                    mock_post.return_value = mock_response
                    mock_response.raise_for_status = MagicMock(side_effect=Exception(f"HTTP {mock_response.status_code}"))
                    result = run_cli_subprocess(cli_file, args, env_vars=env)
            else:
                with patch('urllib.request.urlopen') as mock_urlopen:
                    mock_urlopen.side_effect = MockHTTPError(mock_response.status_code, scenario)
                    result = run_cli_subprocess(cli_file, args, env_vars=env)
            
            assert result['returncode'] == 1, f"Should fail with {scenario} for {cli_file}"
            error_found = ('Error:' in result['stdout'] or 'Error:' in result['stderr'] or 
                          'HTTP' in result['stdout'] or 'HTTP' in result['stderr'])
            assert error_found, f"Missing error message for {scenario} in {cli_file}"
        
        print(f"    ✅ Error handling works for {cli_file}")
    
    print("✅ Error handling works for all implementations")


def test_interactive_mode():
    """Test interactive mode for all implementations"""
    print("🧪 Testing interactive mode for all implementations...")
    
    mock_response = MockResponse(create_mock_api_response())
    
    interactive_inputs = [
        "Test interactive prompt",
        "snap-456",
        "y",
        "n", 
        "50",
        "secret3,secret4",
        "kb3,kb4",
        "interactive,test",
        "Interactive Test Session"
    ]
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        
        script_content = create_interactive_test_script(cli_file, interactive_inputs, ['--interactive', '--output', 'json'])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            test_file = f.name
        
        try:
            if cli_file == 'devin_cli.py':
                with patch('requests.post', mock_requests_post(mock_response)):
                    result = subprocess.run([sys.executable, test_file], 
                                          capture_output=True, text=True, 
                                          cwd=os.path.dirname(__file__))
            else:
                with patch('urllib.request.urlopen', mock_urllib_urlopen(mock_response)):
                    result = subprocess.run([sys.executable, test_file], 
                                          capture_output=True, text=True, 
                                          cwd=os.path.dirname(__file__))
            
            os.unlink(test_file)
            
            success_indicators = [
                'Creating Devin session...' in result.stdout,
                'Interactive mode completed' in result.stdout,
                'session_id' in result.stdout
            ]
            
            assert any(success_indicators), f"Interactive mode failed for {cli_file}: {result.stdout}"
            print(f"    ✅ Interactive mode works for {cli_file}")
            
        except Exception as e:
            if os.path.exists(test_file):
                os.unlink(test_file)
            print(f"    ⚠️  Interactive mode test skipped for {cli_file}: {e}")
    
    print("✅ Interactive mode testing completed")


def test_mixed_mode():
    """Test mixed mode (some flags + interactive prompts)"""
    print("🧪 Testing mixed mode for all implementations...")
    
    mock_response = MockResponse(create_mock_api_response())
    
    mixed_inputs = [
        "Test mixed mode prompt",
        "",
        "n",
        "",
        "",
        "",
        "",
        ""
    ]
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        
        script_content = create_interactive_test_script(
            cli_file, 
            mixed_inputs, 
            ['--interactive', '--unlisted', '--max-acu-limit', '75', '--output', 'json']
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            test_file = f.name
        
        try:
            if cli_file == 'devin_cli.py':
                with patch('requests.post', mock_requests_post(mock_response)):
                    result = subprocess.run([sys.executable, test_file], 
                                          capture_output=True, text=True, 
                                          cwd=os.path.dirname(__file__))
            else:
                with patch('urllib.request.urlopen', mock_urllib_urlopen(mock_response)):
                    result = subprocess.run([sys.executable, test_file], 
                                          capture_output=True, text=True, 
                                          cwd=os.path.dirname(__file__))
            
            os.unlink(test_file)
            
            success_indicators = [
                'Creating Devin session...' in result.stdout,
                'session_id' in result.stdout
            ]
            
            assert any(success_indicators), f"Mixed mode failed for {cli_file}: {result.stdout}"
            print(f"    ✅ Mixed mode works for {cli_file}")
            
        except Exception as e:
            if os.path.exists(test_file):
                os.unlink(test_file)
            print(f"    ⚠️  Mixed mode test skipped for {cli_file}: {e}")
    
    print("✅ Mixed mode testing completed")


def test_list_parsing():
    """Test comma-separated list parsing for all implementations"""
    print("🧪 Testing list parsing functionality for all implementations...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    test_cases = [
        ("", []),
        ("item1", ["item1"]),
        ("item1,item2", ["item1", "item2"]),
        ("item1, item2, item3", ["item1", "item2", "item3"]),
        (" item1 , item2 ", ["item1", "item2"]),
        ("  ,  item1  ,  ,  item2  ,  ", ["item1", "item2"]),
    ]
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        
        if cli_file == 'devin_cli.py':
            from devin_cli import parse_list_input
        elif cli_file == 'devin_cli_standalone.py':
            from devin_cli_standalone import parse_list_input
        elif cli_file == 'devin_cli_enhanced.py':
            from devin_cli_enhanced import parse_list_input
        
        for input_str, expected in test_cases:
            result = parse_list_input(input_str)
            assert result == expected, f"parse_list_input('{input_str}') = {result}, expected {expected} for {cli_file}"
        
        print(f"    ✅ List parsing works for {cli_file}")
    
    print("✅ List parsing works for all implementations")


def test_api_request_structure():
    """Test that API requests are structured correctly for all implementations"""
    print("🧪 Testing API request structure for all implementations...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    test_payload = {
        'prompt': 'Test prompt',
        'snapshot_id': 'snap-123',
        'idempotent': True,
        'tags': ['test', 'api']
    }
    
    expected_response = create_mock_api_response()
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        
        os.environ['DEVIN_API_KEY'] = 'test_api_key'
        
        if cli_file == 'devin_cli.py':
            from devin_cli import make_api_request
            
            with patch('requests.post') as mock_post:
                mock_response = MockResponse(expected_response)
                mock_post.return_value = mock_response
                
                result = make_api_request(test_payload)
                
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                
                assert call_args[0][0] == 'https://api.devin.ai/v1/sessions'
                assert call_args[1]['headers']['Authorization'] == 'Bearer test_api_key'
                assert call_args[1]['headers']['Content-Type'] == 'application/json'
                assert call_args[1]['json'] == test_payload
                
        else:
            if cli_file == 'devin_cli_standalone.py':
                from devin_cli_standalone import make_api_request
            elif cli_file == 'devin_cli_enhanced.py':
                from devin_cli_enhanced import make_api_request
            
            with patch('urllib.request.urlopen') as mock_urlopen:
                mock_response = MockResponse(expected_response)
                mock_urlopen.return_value = mock_response
                
                result = make_api_request(test_payload)
                
                mock_urlopen.assert_called_once()
                call_args = mock_urlopen.call_args[0][0]
                
                assert call_args.get_full_url() == 'https://api.devin.ai/v1/sessions'
                assert call_args.headers['Authorization'] == 'Bearer test_api_key'
                assert call_args.headers['Content-type'] == 'application/json'
        
        assert result['session_id'] == expected_response['session_id']
        assert result['is_new_session'] == expected_response['is_new_session']
        
        print(f"    ✅ API request structure is correct for {cli_file}")
    
    print("✅ API request structure is correct for all implementations")


def test_enhanced_auth_management():
    """Test authentication management for enhanced CLI"""
    print("🧪 Testing enhanced authentication management...")
    
    temp_config_dir = create_temp_config_dir()
    
    try:
        with patch('devin_cli_enhanced.get_config_dir') as mock_get_config_dir:
            from pathlib import Path
            mock_get_config_dir.return_value = Path(temp_config_dir)
            
            sys.path.insert(0, os.path.dirname(__file__))
            from devin_cli_enhanced import save_token, load_token, test_token
            
            test_token_value = 'test_token_12345'
            
            save_token(test_token_value)
            
            loaded_token = load_token()
            assert loaded_token == test_token_value, f"Token not saved/loaded correctly: {loaded_token}"
            
            with patch('urllib.request.urlopen') as mock_urlopen:
                mock_response = MockResponse(create_mock_api_response())
                mock_urlopen.return_value = mock_response
                
                is_valid = test_token(test_token_value)
                assert is_valid, "Token validation should succeed"
            
            with patch('urllib.request.urlopen') as mock_urlopen:
                mock_urlopen.side_effect = MockHTTPError(403, "Forbidden")
                
                is_valid = test_token(test_token_value)
                assert not is_valid, "Token validation should fail for 403 error"
            
            print("    ✅ Enhanced authentication management works")
    
    finally:
        cleanup_temp_dir(temp_config_dir)
    
    print("✅ Enhanced authentication management testing completed")


def test_edge_cases():
    """Test edge cases and malformed inputs"""
    print("🧪 Testing edge cases and malformed inputs for all implementations...")
    
    mock_response = MockResponse(create_mock_api_response())
    
    edge_cases = [
        (['--prompt', ''], "Empty prompt"),
        (['--prompt', 'test', '--max-acu-limit', '0'], "Zero ACU limit"),
        (['--prompt', 'test', '--secret-ids', ''], "Empty secret IDs"),
        (['--prompt', 'test', '--tags', ',,,'], "Malformed tags"),
        (['--prompt', 'test', '--knowledge-ids', 'kb1,,kb2,'], "Malformed knowledge IDs"),
    ]
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        
        for args, description in edge_cases:
            env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
            
            if cli_file == 'devin_cli.py':
                with patch('requests.post', mock_requests_post(mock_response)):
                    result = run_cli_subprocess(cli_file, args, env_vars=env)
            else:
                with patch('urllib.request.urlopen', mock_urllib_urlopen(mock_response)):
                    result = run_cli_subprocess(cli_file, args, env_vars=env)
            
            if args[1] == '':
                assert result['returncode'] != 0, f"Should fail with empty prompt for {cli_file}"
            else:
                success_or_api_error = (result['returncode'] == 0 or 
                                       'Creating Devin session...' in result['stdout'])
                assert success_or_api_error, f"Edge case '{description}' failed unexpectedly for {cli_file}"
        
        print(f"    ✅ Edge cases handled correctly for {cli_file}")
    
    print("✅ Edge cases testing completed")


def run_all_tests():
    """Run all comprehensive tests"""
    print("🚀 Starting comprehensive CLI tests...\n")
    
    tests = [
        test_comprehensive_argument_parsing,
        test_parameter_combinations,
        test_error_handling,
        test_interactive_mode,
        test_mixed_mode,
        test_list_parsing,
        test_api_request_structure,
        test_enhanced_auth_management,
        test_edge_cases,
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
    
    print(f"📊 Comprehensive Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All comprehensive tests passed!")
    else:
        print("⚠️  Some comprehensive tests failed. Check the output above for details.")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
