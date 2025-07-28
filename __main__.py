#!/usr/bin/env python3
"""
Allow running devin-cli as a module: python -m devin-cli
"""

from devin_cli import create_session

if __name__ == '__main__':
    create_session()
