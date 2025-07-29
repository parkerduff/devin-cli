#!/usr/bin/env python3
"""
Basic functionality tests for all three Devin CLI implementations
"""

import subprocess
import sys
import os
import json
from unittest.mock import patch, MagicMock
from test_utils import (
    run_cli_subprocess, create_mock_api_response, mock_requests_post, 
    mock_urllib_urlopen, MockResponse, get_cli_implementations
)


def test_help_command():
    """Test --help command for all implementations"""
    print("🧪 Testing --help command for all implementations...")
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        result = run_cli_subprocess(cli_file, ['--help'])
        
        assert result['returncode'] == 0, f"Help command failed for {cli_file}: {result['stderr']}"
        assert 'prompt' in result['stdout'], f"Help text missing prompt option for {cli_file}"
        assert 'interactive' in result['stdout'], f"Help text missing interactive option for {cli_file}"
        print(f"    ✅ Help command works for {cli_file}")
    
    print("✅ Help command works for all implementations")


def test_version_command():
    """Test --version command for all implementations"""
    print("🧪 Testing --version command for all implementations...")
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        result = run_cli_subprocess(cli_file, ['--version'])
        
        assert result['returncode'] == 0, f"Version command failed for {cli_file}: {result['stderr']}"
        version_found = '1.0.0' in result['stdout'] or '1.1.0' in result['stdout']
        assert version_found, f"Version number missing for {cli_file}"
        print(f"    ✅ Version command works for {cli_file}")
    
    print("✅ Version command works for all implementations")


def test_missing_api_key():
    """Test behavior when API key is missing for all implementations"""
    print("🧪 Testing missing API key handling for all implementations...")
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        env = {'DEVIN_API_KEY': ''}
        result = run_cli_subprocess(cli_file, ['--prompt', 'test'], env_vars=env)
        
        assert result['returncode'] == 1, f"Should fail with missing API key for {cli_file}"
        error_msg_found = ('DEVIN_API_KEY' in result['stdout'] or 
                          'DEVIN_API_KEY' in result['stderr'] or
                          'No Devin API token found' in result['stdout'])
        assert error_msg_found, f"Missing proper error message for {cli_file}"
        print(f"    ✅ Missing API key handled correctly for {cli_file}")
    
    print("✅ Missing API key handled correctly for all implementations")


def test_basic_argument_parsing():
    """Test basic argument parsing for all implementations"""
    print("🧪 Testing basic argument parsing for all implementations...")
    
    mock_response = MockResponse(create_mock_api_response())
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        
        env = {'DEVIN_API_KEY': 'fake_test_key'}
        args = [
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
        ]
        
        result = run_cli_subprocess(cli_file, args, env_vars=env, mock_api_response=mock_response)
        
        assert result['returncode'] == 0, f"Argument parsing failed for {cli_file}: {result['stderr']}"
        assert 'Creating Devin session...' in result['stdout'], f"Should reach API call stage for {cli_file}"
        
        try:
            output_lines = result['stdout'].strip().split('\n')
            json_line = None
            for line in output_lines:
                if line.strip().startswith('{'):
                    json_line = line.strip()
                    break
            
            if json_line:
                json_output = json.loads(json_line)
                assert 'session_id' in json_output, f"JSON output missing session_id for {cli_file}"
        except json.JSONDecodeError:
            pass
        
        print(f"    ✅ Argument parsing works for {cli_file}")
    
    print("✅ Argument parsing works for all implementations")


def test_output_formats():
    """Test JSON and table output formats for all implementations"""
    print("🧪 Testing output formats for all implementations...")
    
    mock_response = MockResponse(create_mock_api_response())
    
    for cli_file in get_cli_implementations():
        print(f"\n  Testing {cli_file}:")
        
        env = {'DEVIN_API_KEY': 'fake_test_key'}
        
        for output_format in ['json', 'table']:
            args = ['--prompt', 'Test output format', '--output', output_format]
            
            result = run_cli_subprocess(cli_file, args, env_vars=env, mock_api_response=mock_response)
            
            assert result['returncode'] == 0, f"Output format {output_format} failed for {cli_file}"
            
            if output_format == 'json':
                try:
                    output_lines = result['stdout'].strip().split('\n')
                    json_line = None
                    for line in output_lines:
                        if line.strip().startswith('{'):
                            json_line = line.strip()
                            break
                    
                    if json_line:
                        json_output = json.loads(json_line)
                        assert 'session_id' in json_output, f"JSON output missing session_id for {cli_file}"
                except json.JSONDecodeError:
                    pass
            else:
                assert 'Session created successfully' in result['stdout'], f"Table output missing success message for {cli_file}"
                assert 'Session ID:' in result['stdout'], f"Table output missing session ID for {cli_file}"
        
        print(f"    ✅ Output formats work for {cli_file}")
    
    print("✅ Output formats work for all implementations")


def run_all_tests():
    """Run all basic functionality tests"""
    print("🚀 Starting basic CLI functionality tests...\n")
    
    tests = [
        test_help_command,
        test_version_command,
        test_missing_api_key,
        test_basic_argument_parsing,
        test_output_formats,
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
    
    print(f"📊 Basic Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All basic tests passed!")
    else:
        print("⚠️  Some basic tests failed. Check the output above for details.")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
