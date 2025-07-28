#!/usr/bin/env python3
"""
Simple test script to verify CLI functionality
"""

import subprocess
import sys
import os

def test_cli():
    """Run basic CLI tests"""
    print("🧪 Testing Devin CLI...")
    
    # Test 1: Help command
    print("\n1. Testing help command:")
    result = subprocess.run(['devin-cli', '--help'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Help command works")
    else:
        print("❌ Help command failed")
        return False
    
    # Test 2: Version command  
    print("\n2. Testing version command:")
    result = subprocess.run(['devin-cli', '--version'], capture_output=True, text=True)
    if result.returncode == 0 and '1.0.0' in result.stdout:
        print("✅ Version command works")
    else:
        print("❌ Version command failed")
        return False
    
    # Test 3: Missing API key handling
    print("\n3. Testing missing API key:")
    env = os.environ.copy()
    env.pop('DEVIN_API_KEY', None)  # Remove API key
    result = subprocess.run(['devin-cli', '--prompt', 'test'], 
                          capture_output=True, text=True, env=env)
    if result.returncode == 1 and 'DEVIN_API_KEY' in result.stdout:
        print("✅ Missing API key handled correctly")
    else:
        print("❌ Missing API key not handled properly")
        return False
    
    # Test 4: Argument parsing (with fake API key)
    print("\n4. Testing argument parsing:")
    env = os.environ.copy()
    env['DEVIN_API_KEY'] = 'fake_test_key'
    result = subprocess.run([
        'devin-cli', 
        '--prompt', 'Test prompt',
        '--snapshot-id', 'snap-123',
        '--tags', 'test,cli',
        '--idempotent',
        '--output', 'json'
    ], capture_output=True, text=True, env=env)
    
    if 'Creating Devin session...' in result.stdout:
        print("✅ Arguments parsed correctly (reached API call)")
    else:
        print("❌ Argument parsing failed")
        return False
    
    print("\n🎉 All basic tests passed!")
    return True

if __name__ == '__main__':
    success = test_cli()
    sys.exit(0 if success else 1)
