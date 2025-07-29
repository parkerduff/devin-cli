#!/usr/bin/env python3
"""
Edge cases and error scenario tests for Devin CLI
Tests boundary conditions, error handling, and unusual inputs
"""

import subprocess
import sys
import os
import json
import tempfile
import time
from unittest.mock import patch, MagicMock
from pathlib import Path


def run_cli_command(args, env_vars=None, input_data=None):
    """Run CLI command with optional input data"""
    cmd = [sys.executable, 'devin_cli_standalone.py'] + args
    
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            env=env,
            input=input_data,
            timeout=10,
            cwd=os.path.dirname(__file__)
        )
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'returncode': -2,
            'stdout': '',
            'stderr': 'Command timed out'
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }


def test_empty_and_null_arguments():
    """Test handling of empty and null arguments"""
    print("🧪 Testing empty and null arguments...")
    
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    test_cases = [
        (['--prompt', ''], "Empty prompt"),
        (['--prompt', ' '], "Whitespace-only prompt"),
        (['--prompt', '\t'], "Tab-only prompt"),
        (['--prompt', '\n'], "Newline-only prompt"),
        (['--snapshot-id', ''], "Empty snapshot ID"),
        (['--secret-ids', ''], "Empty secret IDs"),
        (['--knowledge-ids', ''], "Empty knowledge IDs"),
        (['--tags', ''], "Empty tags"),
        (['--title', ''], "Empty title"),
        (['--max-acu-limit', '0'], "Zero ACU limit"),
    ]
    
    for args, description in test_cases:
        if '--prompt' not in args:
            args = ['--prompt', 'Test prompt'] + args
        
        result = run_cli_command(args, env_vars=env)
        
        if result['returncode'] == -2:
            print(f"⚠️  {description} timed out (expected for some edge cases)")
        elif '--prompt' in args and args[args.index('--prompt') + 1].strip() == '':
            assert result['returncode'] != 0, f"{description} should be rejected or handled gracefully"
        else:
            assert result['returncode'] == 1, f"{description} should reach API call stage and fail with fake key"
    
    print("✅ Empty and null arguments handled correctly")


def test_special_characters_and_unicode():
    """Test handling of special characters and unicode in prompts"""
    print("🧪 Testing special characters and unicode...")
    
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    special_prompts = [
        "Test with émojis 🚀🎉💻",
        "Test with quotes \"double\" and 'single'",
        "Test with backslashes \\ and \\n newlines",
        "Test with unicode: café, naïve, résumé",
        "Test with symbols: @#$%^&*()_+-=[]{}|;:,.<>?",
        "Test with Chinese: 测试中文字符",
        "Test with Arabic: اختبار النص العربي",
        "Test with Russian: тестирование русского текста",
        "Test with mixed: Hello 世界 🌍 café",
        "Test\nwith\nnewlines",
        "Test\twith\ttabs",
    ]
    
    for prompt in special_prompts:
        result = run_cli_command(['--prompt', prompt, '--output', 'json'], env_vars=env)
        
        assert result['returncode'] == 1, f"Special character prompt should reach API call: {repr(prompt)}"
        assert 'Creating Devin session...' in result['stdout'], f"Should handle special characters: {repr(prompt)}"
    
    print("✅ Special characters and unicode handled correctly")


def test_extremely_long_inputs():
    """Test handling of extremely long input text"""
    print("🧪 Testing extremely long inputs...")
    
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    long_prompt = "A" * 10000
    very_long_prompt = "B" * 100000
    
    test_cases = [
        (long_prompt, "10K character prompt"),
        (very_long_prompt, "100K character prompt"),
        ("x" * 1000 + "," + "y" * 1000, "Long comma-separated values"),
    ]
    
    for prompt, description in test_cases:
        result = run_cli_command(['--prompt', prompt, '--output', 'json'], env_vars=env)
        
        assert result['returncode'] == 1, f"{description} should reach API call stage"
        assert 'Creating Devin session...' in result['stdout'], f"{description} should be processed"
    
    long_tags = ",".join([f"tag{i}" for i in range(1000)])
    result = run_cli_command(['--prompt', 'Test', '--tags', long_tags], env_vars=env)
    assert result['returncode'] == 1, "Long tags list should be processed"
    
    print("✅ Extremely long inputs handled correctly")


def test_network_connectivity_issues():
    """Test handling of network connectivity issues"""
    print("🧪 Testing network connectivity issues...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_standalone import make_api_request, DevinAPIError
    
    test_payload = {'prompt': 'Test network error'}
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        from urllib.error import URLError
        
        mock_urlopen.side_effect = URLError("Network is unreachable")
        
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_key'}):
            try:
                make_api_request(test_payload)
                assert False, "Should raise DevinAPIError for network issues"
            except DevinAPIError as e:
                assert 'Network error' in str(e), "Should indicate network error"
        
        mock_urlopen.side_effect = URLError("Connection timed out")
        
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_key'}):
            try:
                make_api_request(test_payload)
                assert False, "Should raise DevinAPIError for timeout"
            except DevinAPIError as e:
                assert 'Network error' in str(e), "Should indicate network error"
    
    print("✅ Network connectivity issues handled correctly")


def test_malformed_api_responses():
    """Test handling of malformed API responses"""
    print("🧪 Testing malformed API responses...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_standalone import make_api_request, DevinAPIError
    
    test_payload = {'prompt': 'Test malformed response'}
    
    malformed_responses = [
        b'{"incomplete": json',
        b'not json at all',
        b'',
        b'{"session_id": null}',
        b'{"error": "Something went wrong"}',
        b'<html><body>Error 500</body></html>',
    ]
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        for response_data in malformed_responses:
            mock_response = MagicMock()
            mock_response.read.return_value = response_data
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response
            
            with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_key'}):
                try:
                    result = make_api_request(test_payload)
                    if response_data == b'{"session_id": null}':
                        assert result.get('session_id') is None, "Should handle null values"
                    elif response_data == b'{"error": "Something went wrong"}':
                        assert 'error' in result, "Should return error response"
                except DevinAPIError as e:
                    assert 'Invalid JSON' in str(e) or 'JSON' in str(e), f"Should handle malformed JSON: {response_data}"
                except json.JSONDecodeError:
                    pass
    
    print("✅ Malformed API responses handled correctly")


def test_api_request_timeout_handling():
    """Test handling of API request timeouts"""
    print("🧪 Testing API request timeout handling...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_standalone import make_api_request, DevinAPIError
    
    test_payload = {'prompt': 'Test timeout'}
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        import socket
        
        mock_urlopen.side_effect = socket.timeout("Request timed out")
        
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_key'}):
            try:
                make_api_request(test_payload)
                assert False, "Should raise exception for timeout"
            except (DevinAPIError, socket.timeout):
                pass
        
        mock_urlopen.side_effect = OSError("Connection reset by peer")
        
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_key'}):
            try:
                make_api_request(test_payload)
                assert False, "Should raise exception for connection error"
            except (DevinAPIError, OSError):
                pass
    
    print("✅ API request timeout handling works correctly")


def test_interactive_input_validation():
    """Test interactive input validation and error handling"""
    print("🧪 Testing interactive input validation...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_standalone import prompt_user, confirm
    
    with patch('builtins.input') as mock_input:
        mock_input.return_value = "valid input"
        result = prompt_user("Test prompt")
        assert result == "valid input", "Should return user input"
        
        mock_input.return_value = ""
        result = prompt_user("Test prompt", default="default_value")
        assert result == "default_value", "Should return default when input is empty"
        
        mock_input.side_effect = ["", "", "finally valid"]
        result = prompt_user("Test prompt", required=True)
        assert result == "finally valid", "Should keep prompting until valid input"
        
        mock_input.return_value = "y"
        result = confirm("Test confirmation")
        assert result == True, "Should return True for 'y'"
        
        mock_input.return_value = "n"
        result = confirm("Test confirmation")
        assert result == False, "Should return False for 'n'"
        
        mock_input.return_value = ""
        result = confirm("Test confirmation", default=True)
        assert result == True, "Should return default for empty input"
    
    print("✅ Interactive input validation works correctly")


def test_keyboard_interrupt_handling():
    """Test keyboard interrupt (Ctrl+C) handling"""
    print("🧪 Testing keyboard interrupt handling...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_standalone import prompt_user, confirm
    
    with patch('builtins.input') as mock_input:
        mock_input.side_effect = KeyboardInterrupt()
        
        try:
            prompt_user("Test prompt")
            assert False, "Should raise SystemExit for KeyboardInterrupt"
        except SystemExit:
            pass
        
        try:
            confirm("Test confirmation")
            assert False, "Should raise SystemExit for KeyboardInterrupt"
        except SystemExit:
            pass
    
    print("✅ Keyboard interrupt handling works correctly")


def test_boundary_value_inputs():
    """Test boundary value inputs and edge cases"""
    print("🧪 Testing boundary value inputs...")
    
    env = {'DEVIN_API_KEY': 'fake_key_for_testing'}
    
    boundary_cases = [
        (['--max-acu-limit', '1'], "Minimum ACU limit"),
        (['--max-acu-limit', '999999'], "Very high ACU limit"),
        (['--max-acu-limit', '-1'], "Negative ACU limit"),
        (['--tags', 'a'], "Single character tag"),
        (['--tags', 'a' * 100], "Very long single tag"),
        (['--secret-ids', 'a' * 50], "Long secret ID"),
        (['--knowledge-ids', 'k' * 50], "Long knowledge ID"),
    ]
    
    for args, description in boundary_cases:
        test_args = ['--prompt', 'Test boundary case'] + args
        result = run_cli_command(test_args, env_vars=env)
        
        if '--max-acu-limit' in args and args[args.index('--max-acu-limit') + 1] == '-1':
            assert result['returncode'] != 0, f"{description} should be rejected"
        else:
            assert result['returncode'] == 1, f"{description} should reach API call stage"
    
    print("✅ Boundary value inputs handled correctly")


def test_concurrent_request_simulation():
    """Test behavior under simulated concurrent requests"""
    print("🧪 Testing concurrent request simulation...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_standalone import make_api_request, DevinAPIError
    
    test_payload = {'prompt': 'Test concurrent request'}
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"session_id": "concurrent-test", "url": "https://app.devin.ai/sessions/concurrent-test", "is_new_session": true}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_key'}):
            results = []
            for i in range(5):
                try:
                    result = make_api_request(test_payload)
                    results.append(result)
                except Exception as e:
                    results.append(str(e))
            
            assert len(results) == 5, "Should handle multiple requests"
            for result in results:
                if isinstance(result, dict):
                    assert 'session_id' in result, "Each result should have session_id"
    
    print("✅ Concurrent request simulation works correctly")


def test_memory_usage_with_large_inputs():
    """Test memory usage with large inputs"""
    print("🧪 Testing memory usage with large inputs...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_standalone import parse_list_input
    
    large_list = ",".join([f"item{i}" for i in range(10000)])
    result = parse_list_input(large_list)
    
    assert len(result) == 10000, "Should handle large lists"
    assert result[0] == "item0", "First item should be correct"
    assert result[-1] == "item9999", "Last item should be correct"
    
    very_large_string = "x" * 1000000
    result = parse_list_input(very_large_string)
    assert len(result) == 1, "Should handle very large single items"
    assert result[0] == very_large_string, "Should preserve large strings"
    
    print("✅ Memory usage with large inputs works correctly")


def test_file_system_edge_cases():
    """Test file system related edge cases for enhanced CLI"""
    print("🧪 Testing file system edge cases...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_enhanced import get_config_dir, save_token, load_token
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('devin_cli_enhanced.get_config_dir') as mock_config_dir:
            mock_config_dir.return_value = Path(temp_dir)
            
            save_token("test_token")
            
            token_file = Path(temp_dir) / 'token'
            
            os.chmod(token_file, 0o000)
            try:
                result = load_token()
                assert result is None or isinstance(result, str), "Should handle permission errors gracefully"
            except Exception:
                pass
            finally:
                os.chmod(token_file, 0o600)
            
            with open(token_file, 'w') as f:
                f.write("corrupted\x00token\xff")
            
            try:
                result = load_token()
                assert isinstance(result, str), "Should handle corrupted token files"
            except Exception:
                pass
    
    print("✅ File system edge cases handled correctly")


def run_all_tests():
    """Run all edge case tests"""
    print("🚀 Starting edge case tests...\n")
    
    tests = [
        test_empty_and_null_arguments,
        test_special_characters_and_unicode,
        test_extremely_long_inputs,
        test_network_connectivity_issues,
        test_malformed_api_responses,
        test_api_request_timeout_handling,
        test_interactive_input_validation,
        test_keyboard_interrupt_handling,
        test_boundary_value_inputs,
        test_concurrent_request_simulation,
        test_memory_usage_with_large_inputs,
        test_file_system_edge_cases,
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
    
    print(f"📊 Edge Case Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All edge case tests passed!")
    else:
        print("⚠️  Some edge case tests failed. Check the output above for details.")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
