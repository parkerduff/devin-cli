#!/usr/bin/env python3
"""
Devin CLI - A standalone command line tool for creating Devin sessions
Uses only Python standard library to avoid dependency issues
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import argparse
from typing import Optional, List


class DevinAPIError(Exception):
    """Custom exception for Devin API errors"""
    pass


def get_api_key() -> str:
    """Get API key from environment variable"""
    api_key = os.getenv('DEVIN_API_KEY')
    if not api_key:
        print("❌ Error: DEVIN_API_KEY environment variable is required.")
        print("Set it with: export DEVIN_API_KEY=your_token_here")
        sys.exit(1)
    return api_key


def make_api_request(payload: dict) -> dict:
    """Make API request to create Devin session using urllib"""
    api_key = get_api_key()
    
    # Prepare the request
    url = 'https://api.devin.ai/v1/sessions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Convert payload to JSON bytes
    data = json.dumps(payload).encode('utf-8')
    
    # Create the request
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8') if e.fp else str(e)
        raise DevinAPIError(f"HTTP {e.code}: {error_msg}")
    except urllib.error.URLError as e:
        raise DevinAPIError(f"Network error: {e}")
    except json.JSONDecodeError as e:
        raise DevinAPIError(f"Invalid JSON response: {e}")


def parse_list_input(value: str) -> List[str]:
    """Parse comma-separated string into list"""
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


def prompt_user(message: str, default: str = None, required: bool = False) -> str:
    """Prompt user for input with optional default"""
    if default:
        prompt = f"{message} [{default}]: "
    else:
        prompt = f"{message}: "
    
    while True:
        try:
            value = input(prompt).strip()
            if not value and default:
                return default
            if not value and required:
                print("This field is required. Please enter a value.")
                continue
            return value
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            sys.exit(1)


def confirm(message: str, default: bool = False) -> bool:
    """Ask user for yes/no confirmation"""
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        try:
            response = input(f"{message}{suffix}: ").strip().lower()
            if not response:
                return default
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'")
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Create a new Devin session via the API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --prompt "Review PR #123"
  %(prog)s --interactive
  %(prog)s --prompt "Deploy to prod" --tags "deployment,urgent" --idempotent
        """
    )
    
    parser.add_argument('--prompt', '-p', 
                       help='The task description for Devin')
    parser.add_argument('--snapshot-id', 
                       help='ID of a machine snapshot to use')
    parser.add_argument('--unlisted', action='store_true',
                       help='Make the session unlisted')
    parser.add_argument('--idempotent', action='store_true',
                       help='Enable idempotent session creation')
    parser.add_argument('--max-acu-limit', type=int,
                       help='Maximum ACU limit for the session')
    parser.add_argument('--secret-ids',
                       help='Comma-separated list of secret IDs to use')
    parser.add_argument('--knowledge-ids',
                       help='Comma-separated list of knowledge IDs to use')
    parser.add_argument('--tags',
                       help='Comma-separated list of tags to add to the session')
    parser.add_argument('--title',
                       help='Custom title for the session')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode (prompt for missing values)')
    parser.add_argument('--output', '-o', choices=['json', 'table'], default='table',
                       help='Output format (default: table)')
    parser.add_argument('--version', action='version', version='1.0.0')
    
    args = parser.parse_args()
    
    # Interactive mode or missing required prompt
    if args.interactive or not args.prompt:
        if not args.prompt:
            args.prompt = prompt_user('Task description for Devin', required=True)
        
        # Only prompt for optional fields if in interactive mode
        if args.interactive:
            if not args.snapshot_id:
                snapshot_id = prompt_user('Snapshot ID (optional)')
                args.snapshot_id = snapshot_id if snapshot_id else None
            
            if not args.unlisted:
                args.unlisted = confirm('Make session unlisted?', default=False)
            
            if not args.idempotent:
                args.idempotent = confirm('Enable idempotent session creation?', default=False)
            
            if args.max_acu_limit is None:
                max_acu_input = prompt_user('Maximum ACU limit (optional)')
                args.max_acu_limit = int(max_acu_input) if max_acu_input else None
            
            if not args.secret_ids:
                args.secret_ids = prompt_user('Secret IDs (comma-separated, optional)')
            
            if not args.knowledge_ids:
                args.knowledge_ids = prompt_user('Knowledge IDs (comma-separated, optional)')
            
            if not args.tags:
                args.tags = prompt_user('Tags (comma-separated, optional)')
            
            if not args.title:
                title = prompt_user('Custom title (optional)')
                args.title = title if title else None

    # Build the request payload
    payload = {'prompt': args.prompt}
    
    # Add optional parameters if provided
    if args.snapshot_id:
        payload['snapshot_id'] = args.snapshot_id
    if args.unlisted:
        payload['unlisted'] = args.unlisted
    if args.idempotent:
        payload['idempotent'] = args.idempotent
    if args.max_acu_limit is not None:
        payload['max_acu_limit'] = args.max_acu_limit
    if args.secret_ids:
        payload['secret_ids'] = parse_list_input(args.secret_ids)
    if args.knowledge_ids:
        payload['knowledge_ids'] = parse_list_input(args.knowledge_ids)
    if args.tags:
        payload['tags'] = parse_list_input(args.tags)
    if args.title:
        payload['title'] = args.title

    try:
        # Make the API request
        print("Creating Devin session...")
        result = make_api_request(payload)
        
        # Output the result
        if args.output == 'json':
            print(json.dumps(result, indent=2))
        else:
            # Table format
            print("\n✅ Session created successfully!")
            print(f"Session ID: {result.get('session_id', 'N/A')}")
            print(f"URL: {result.get('url', 'N/A')}")
            print(f"New Session: {result.get('is_new_session', 'N/A')}")
            
    except DevinAPIError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
