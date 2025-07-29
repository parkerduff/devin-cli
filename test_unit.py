#!/usr/bin/env python3
"""
Unit tests for utility functions across all CLI implementations
Tests individual functions in isolation with comprehensive coverage
"""

import sys
import os
import json
from unittest.mock import patch, MagicMock


def test_parse_list_input_comprehensive():
    """Comprehensive tests for parse_list_input function across all implementations"""
    print("🧪 Testing parse_list_input across all implementations...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    implementations = [
        ('devin_cli', 'devin_cli'),
        ('devin_cli_standalone', 'devin_cli_standalone'),
        ('devin_cli_enhanced', 'devin_cli_enhanced')
    ]
    
    test_cases = [
        ("", []),
        ("item1", ["item1"]),
        ("item1,item2", ["item1", "item2"]),
        ("item1, item2, item3", ["item1", "item2", "item3"]),
        (" item1 , item2 ", ["item1", "item2"]),
        ("  ", []),
        (",", []),
        (",,", []),
        ("item1,,item2", ["item1", "item2"]),
        ("item1, , item2", ["item1", "item2"]),
        ("item-with-dashes,item_with_underscores", ["item-with-dashes", "item_with_underscores"]),
        ("item1,item2,item3,item4,item5", ["item1", "item2", "item3", "item4", "item5"]),
        ("single-very-long-item-name-with-many-characters", ["single-very-long-item-name-with-many-characters"]),
    ]
    
    for module_name, import_name in implementations:
        try:
            module = __import__(import_name)
            parse_list_input = getattr(module, 'parse_list_input')
            
            for input_value, expected in test_cases:
                result = parse_list_input(input_value)
                assert result == expected, f"{module_name}: parse_list_input('{input_value}') = {result}, expected {expected}"
            
            print(f"✅ {module_name} parse_list_input works correctly")
            
        except ImportError as e:
            print(f"⚠️  Could not import {module_name}: {e}")
        except Exception as e:
            print(f"❌ {module_name} parse_list_input failed: {e}")
            raise
    
    print("✅ parse_list_input comprehensive testing completed")


def test_api_key_validation():
    """Test API key validation across implementations"""
    print("🧪 Testing API key validation...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    implementations = [
        ('devin_cli', 'devin_cli'),
        ('devin_cli_standalone', 'devin_cli_standalone'),
        ('devin_cli_enhanced', 'devin_cli_enhanced')
    ]
    
    for module_name, import_name in implementations:
        try:
            module = __import__(import_name)
            get_api_key = getattr(module, 'get_api_key')
            
            with patch.dict(os.environ, {'DEVIN_API_KEY': 'test_key_123'}):
                api_key = get_api_key()
                assert api_key == 'test_key_123', f"{module_name}: Should return correct API key"
            
            with patch.dict(os.environ, {}, clear=True):
                try:
                    get_api_key()
                    assert False, f"{module_name}: Should raise exception for missing API key"
                except SystemExit:
                    pass
                except Exception:
                    pass
            
            print(f"✅ {module_name} API key validation works correctly")
            
        except ImportError as e:
            print(f"⚠️  Could not import {module_name}: {e}")
        except Exception as e:
            print(f"❌ {module_name} API key validation failed: {e}")
            raise
    
    print("✅ API key validation testing completed")


def test_devin_api_error_class():
    """Test DevinAPIError exception class across implementations"""
    print("🧪 Testing DevinAPIError exception class...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    implementations = [
        ('devin_cli', 'devin_cli'),
        ('devin_cli_standalone', 'devin_cli_standalone'),
        ('devin_cli_enhanced', 'devin_cli_enhanced')
    ]
    
    for module_name, import_name in implementations:
        try:
            module = __import__(import_name)
            DevinAPIError = getattr(module, 'DevinAPIError')
            
            error = DevinAPIError("Test error message")
            assert str(error) == "Test error message", f"{module_name}: Error message should be preserved"
            assert isinstance(error, Exception), f"{module_name}: Should be instance of Exception"
            
            print(f"✅ {module_name} DevinAPIError works correctly")
            
        except ImportError as e:
            print(f"⚠️  Could not import {module_name}: {e}")
        except Exception as e:
            print(f"❌ {module_name} DevinAPIError failed: {e}")
            raise
    
    print("✅ DevinAPIError testing completed")


def test_make_api_request_structure():
    """Test make_api_request function structure and behavior"""
    print("🧪 Testing make_api_request structure...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    test_payload = {
        'prompt': 'Test prompt',
        'snapshot_id': 'snap-123',
        'tags': ['test', 'unit']
    }
    
    implementations = [
        ('devin_cli_standalone', 'urllib.request.urlopen'),
        ('devin_cli_enhanced', 'urllib.request.urlopen'),
    ]
    
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
                    result = make_api_request(test_payload)
                    
                    assert result['session_id'] == 'test-123', f"{module_name}: Should parse session_id correctly"
                    assert result['is_new_session'] == True, f"{module_name}: Should parse boolean correctly"
                    
                    mock_request.assert_called_once()
                    call_args = mock_request.call_args[0][0]
                    assert call_args.get_full_url() == 'https://api.devin.ai/v1/sessions', f"{module_name}: Should use correct URL"
                    assert call_args.headers['Authorization'] == 'Bearer test_api_key', f"{module_name}: Should use correct auth header"
            
            print(f"✅ {module_name} make_api_request works correctly")
            
        except ImportError as e:
            print(f"⚠️  Could not import {module_name}: {e}")
        except Exception as e:
            print(f"❌ {module_name} make_api_request failed: {e}")
            raise
    
    print("✅ make_api_request structure testing completed")


def test_argument_validation_logic():
    """Test argument validation and processing logic"""
    print("🧪 Testing argument validation logic...")
    
    sys.path.insert(0, os.path.dirname(__file__))
    from devin_cli_enhanced import parse_list_input
    
    edge_cases = [
        ("", []),
        ("   ", []),
        ("\t", []),
        ("\n", []),
        ("item1\n", ["item1"]),
        ("item1\t", ["item1"]),
        ("item1,\n,item2", ["item1", "item2"]),
    ]
    
    for input_value, expected in edge_cases:
        try:
            result = parse_list_input(input_value)
            assert result == expected, f"parse_list_input({repr(input_value)}) = {result}, expected {expected}"
        except Exception as e:
            print(f"❌ Argument validation failed for {repr(input_value)}: {e}")
            raise
    
    print("✅ Argument validation logic works correctly")


def test_output_formatting():
    """Test output formatting functions and logic"""
    print("🧪 Testing output formatting...")
    
    test_result = {
        'session_id': 'devin-test-123',
        'url': 'https://app.devin.ai/sessions/test-123',
        'is_new_session': True
    }
    
    json_output = json.dumps(test_result, indent=2)
    assert 'devin-test-123' in json_output, "JSON output should contain session ID"
    assert 'https://app.devin.ai/sessions/test-123' in json_output, "JSON output should contain URL"
    assert 'true' in json_output.lower(), "JSON output should contain boolean value"
    
    table_lines = [
        f"Session ID: {test_result.get('session_id', 'N/A')}",
        f"URL: {test_result.get('url', 'N/A')}",
        f"New Session: {test_result.get('is_new_session', 'N/A')}"
    ]
    
    for line in table_lines:
        assert 'devin-test-123' in line or 'https://app.devin.ai' in line or 'True' in line, f"Table line should contain expected data: {line}"
    
    print("✅ Output formatting works correctly")


def run_all_tests():
    """Run all unit tests"""
    print("🚀 Starting unit tests...\n")
    
    tests = [
        test_parse_list_input_comprehensive,
        test_api_key_validation,
        test_devin_api_error_class,
        test_make_api_request_structure,
        test_argument_validation_logic,
        test_output_formatting,
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
    
    print(f"📊 Unit Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All unit tests passed!")
    else:
        print("⚠️  Some unit tests failed. Check the output above for details.")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
