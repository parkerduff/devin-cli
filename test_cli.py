#!/usr/bin/env python3
"""
Test script to verify the CLI tool works
"""

import subprocess
import sys
import os

def test_help():
    """Test that the help command works"""
    try:
        result = subprocess.run([sys.executable, 'devin_cli.py', '--help'], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        print("Help command output:")
        print(result.stdout)
        if result.returncode == 0:
            print("✅ Help command works!")
        else:
            print("❌ Help command failed:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running help command: {e}")

def test_version():
    """Test that the version command works"""
    try:
        result = subprocess.run([sys.executable, 'devin_cli.py', '--version'], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        print("\nVersion command output:")
        print(result.stdout)
        if result.returncode == 0:
            print("✅ Version command works!")
        else:
            print("❌ Version command failed:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running version command: {e}")

if __name__ == '__main__':
    print("Testing Devin CLI tool...")
    test_help()
    test_version()
