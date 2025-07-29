#!/usr/bin/env python3
"""
Master test runner for all Devin CLI test suites
"""

import sys
import subprocess
import os


def run_test_file(test_file):
    """Run a single test file and return success status"""
    print(f"\n{'='*60}")
    print(f"Running {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=os.path.dirname(__file__),
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run {test_file}: {e}")
        return False


def main():
    """Run all test suites"""
    print("🚀 Running comprehensive Devin CLI test suite...")
    
    test_files = [
        'test_cli.py',
        'test_comprehensive.py', 
        'test_enhanced_auth.py',
        'test_simple.py'
    ]
    
    results = {}
    
    for test_file in test_files:
        if os.path.exists(test_file):
            results[test_file] = run_test_file(test_file)
        else:
            print(f"⚠️  Test file {test_file} not found, skipping...")
            results[test_file] = None
    
    print(f"\n{'='*60}")
    print("FINAL TEST RESULTS")
    print('='*60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_file, success in results.items():
        if success is None:
            print(f"⚠️  {test_file}: SKIPPED")
            skipped += 1
        elif success:
            print(f"✅ {test_file}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_file}: FAILED")
            failed += 1
    
    print(f"\n📊 Summary: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("🎉 All available tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
