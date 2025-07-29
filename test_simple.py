#!/usr/bin/env python3
"""
Simple integration tests for the Devin CLI tool using raw Python files
"""

import subprocess
import sys
import os


def test_cli():
    """Test basic CLI functionality using raw Python files"""
    print("🧪 Testing Devin CLI implementations...")
    
    cli_files = ['devin_cli.py', 'devin_cli_standalone.py', 'devin_cli_enhanced.py']
    
    for cli_file in cli_files:
        print(f"\n📁 Testing {cli_file}:")
        
        # Test help command
        print("  1. Testing help command:")
        result = subprocess.run([sys.executable, cli_file, '--help'], 
                              capture_output=True, text=True, 
                              cwd=os.path.dirname(__file__))
        
        if result.returncode != 0:
            print(f"    ❌ Help command failed: {result.stderr}")
            return False
        
        expected_texts = ['prompt', 'session', 'Create']
        if not any(text in result.stdout for text in expected_texts):
            print(f"    ❌ Help output doesn't contain expected content")
            return False
        
        print("    ✅ Help command works")
        
        # Test version command
        print("  2. Testing version command:")
        result = subprocess.run([sys.executable, cli_file, '--version'], 
                              capture_output=True, text=True,
                              cwd=os.path.dirname(__file__))
        
        if result.returncode != 0:
            print(f"    ❌ Version command failed: {result.stderr}")
            return False
        
        print("    ✅ Version command works")
        
        print("  3. Testing missing API key:")
        env = os.environ.copy()
        env.pop('DEVIN_API_KEY', None)  # Remove API key if present
        
        result = subprocess.run([sys.executable, cli_file, '--prompt', 'test'], 
                              capture_output=True, text=True, env=env,
                              cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("    ❌ Should fail without API key")
            return False
        
        error_indicators = ['API key', 'DEVIN_API_KEY', 'authentication', 'token']
        if not any(indicator in result.stderr or indicator in result.stdout 
                  for indicator in error_indicators):
            print(f"    ❌ Error message doesn't mention API key: {result.stderr}")
            return False
        
        print("    ✅ Missing API key handled correctly")
        
        if cli_file != 'devin_cli_enhanced.py':
            print("  4. Testing invalid arguments:")
            result = subprocess.run([sys.executable, cli_file, '--invalid-flag'], 
                                  capture_output=True, text=True,
                                  cwd=os.path.dirname(__file__))
            
            if result.returncode == 0:
                print("    ❌ Should fail with invalid arguments")
                return False
            
            print("    ✅ Invalid arguments handled correctly")
        else:
            print("  4. Skipping invalid arguments test for enhanced version (has subcommands)")
    
    print("\n🎉 All simple integration tests passed!")
    return True


if __name__ == '__main__':
    success = test_cli()
    sys.exit(0 if success else 1)
