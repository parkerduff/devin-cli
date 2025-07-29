#!/usr/bin/env python3
"""
Devin CLI - Enhanced version with auth subcommand
A command line tool for creating Devin sessions with built-in authentication management
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import argparse
import getpass
from pathlib import Path
from typing import Optional, List


class DevinAPIError(Exception):
    """Custom exception for Devin API errors"""
    pass


def get_config_dir() -> Path:
    """Get the configuration directory for storing auth tokens"""
    config_dir = Path.home() / '.devin-cli'
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_token_file() -> Path:
    """Get the path to the token file"""
    return get_config_dir() / 'token'


def save_token(token: str) -> None:
    """Save the API token to a secure file"""
    token_file = get_token_file()
    
    # Write token to file with restricted permissions
    with open(token_file, 'w') as f:
        f.write(token.strip())
    
    # Set file permissions to be readable only by owner (600)
    os.chmod(token_file, 0o600)
    print(f"✅ Token saved securely to {token_file}")


def load_token() -> Optional[str]:
    """Load the API token from file or environment variable"""
    # First try environment variable
    env_token = os.getenv('DEVIN_API_KEY')
    if env_token:
        return env_token.strip()
    
    # Then try saved token file
    token_file = get_token_file()
    if token_file.exists():
        try:
            with open(token_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            print(f"⚠️  Warning: Could not read saved token: {e}")
    
    return None


def get_api_key() -> str:
    """Get API key from environment variable or saved file"""
    api_key = load_token()
    if not api_key:
        print("❌ Error: No Devin API token found.")
        print("\nTo set up authentication, run:")
        print("  devin-cli auth")
        print("\nOr set the environment variable:")
        print("  export DEVIN_API_KEY=your_token_here")
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


def test_token(token: str) -> bool:
    """Test if a token is valid by making a test API request"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Make a minimal test request
    test_payload = json.dumps({'prompt': 'test'}).encode('utf-8')
    req = urllib.request.Request('https://api.devin.ai/v1/sessions', 
                                data=test_payload, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return True
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return False  # Invalid token
        # Other errors might be valid token but other issues
        return True
    except Exception:
        # Network errors, assume token format is OK
        return True


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


def cmd_auth(args):
    """Handle the auth subcommand"""
    if args.status:
        # Show authentication status
        token = load_token()
        if token:
            # Mask the token for security
            masked_token = token[:8] + '...' + token[-4:] if len(token) > 12 else '***'
            
            if os.getenv('DEVIN_API_KEY'):
                print(f"✅ Using token from environment variable: {masked_token}")
            else:
                print(f"✅ Using saved token: {masked_token}")
                print(f"   Location: {get_token_file()}")
            
            # Test the token
            print("\n🧪 Testing token...")
            if test_token(token):
                print("✅ Token is valid!")
            else:
                print("❌ Token appears to be invalid or expired")
        else:
            print("❌ No authentication token found")
            print("\nRun 'devin-cli auth' to set up authentication")
        return
    
    if args.remove:
        # Remove saved token
        token_file = get_token_file()
        if token_file.exists():
            token_file.unlink()
            print("✅ Saved token removed")
        else:
            print("ℹ️  No saved token to remove")
        return
    
    # Default: Set up authentication
    print("🔑 Devin CLI Authentication Setup")
    print("=" * 40)
    print("\n1. Go to https://app.devin.ai")
    print("2. Navigate to your API settings")
    print("3. Generate or copy your API token")
    print("4. Paste it below (input will be hidden for security)")
    print()
    
    try:
        # Use getpass for secure token input
        token = getpass.getpass("Paste your Devin API token: ").strip()
        
        if not token:
            print("❌ No token provided")
            sys.exit(1)
        
        # Basic validation
        if len(token) < 10:
            print("❌ Token seems too short. Please check and try again.")
            sys.exit(1)
        
        # Test the token
        print("\n🧪 Testing token...")
        if not test_token(token):
            print("❌ Token appears to be invalid. Please check and try again.")
            if not confirm("Save anyway?", default=False):
                sys.exit(1)
        else:
            print("✅ Token is valid!")
        
        # Save the token
        save_token(token)
        
        print("\n🎉 Authentication setup complete!")
        print("You can now use: devin-cli --prompt 'your task here'")
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")
        sys.exit(1)


def cmd_playbook(args):
    """Handle the playbook subcommand - simplified interactive mode for playbook + prompt"""
    # Always prompt for playbook_id and prompt in this mode
    if not args.playbook_id:
        args.playbook_id = prompt_user('Playbook ID', required=True)
    
    if not args.prompt:
        args.prompt = prompt_user('Task description for Devin', required=True)
    
    # Build minimal payload with just the essentials
    payload = {
        'prompt': args.prompt,
        'playbook_id': args.playbook_id
    }
    
    try:
        # Make the API request
        print(f"Creating Devin session with playbook '{args.playbook_id}'...")
        result = make_api_request(payload)
        
        # Output the result
        if args.output == 'json':
            print(json.dumps(result, indent=2))
        else:
            # Table format
            print("\n✅ Session created successfully!")
            print(f"Session ID: {result.get('session_id', 'N/A')}")
            print(f"URL: {result.get('url', 'N/A')}")
            print(f"Playbook: {args.playbook_id}")
            print(f"New Session: {result.get('is_new_session', 'N/A')}")
            
    except DevinAPIError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_create(args):
    """Handle the create session subcommand"""
    # Check if any session creation arguments were provided
    has_args = any([
        args.prompt, args.snapshot_id, args.playbook_id, args.unlisted, args.idempotent,
        args.max_acu_limit, args.secret_ids, args.knowledge_ids, 
        args.tags, args.title
    ])
    
    # Default to interactive mode if no arguments provided, unless explicitly disabled
    if not has_args and not args.non_interactive:
        args.interactive = True
    
    # Override interactive mode if --non-interactive is specified
    if args.non_interactive:
        args.interactive = False
    
    # Interactive mode or missing required prompt
    if args.interactive or not args.prompt:
        if not args.prompt:
            args.prompt = prompt_user('Task description for Devin', required=True)
        
        # Prompt for optional fields if in interactive mode
        if args.interactive:
            if not args.snapshot_id:
                snapshot_id = prompt_user('Snapshot ID (optional)')
                args.snapshot_id = snapshot_id if snapshot_id else None
            
            if not args.playbook_id:
                playbook_id = prompt_user('Playbook ID (optional)')
                args.playbook_id = playbook_id if playbook_id else None
            
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
    if args.playbook_id:
        payload['playbook_id'] = args.playbook_id
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


def main():
    parser = argparse.ArgumentParser(
        description='Devin CLI - Create and manage Devin sessions',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Auth subcommand
    auth_parser = subparsers.add_parser('auth', help='Manage authentication')
    auth_parser.add_argument('--status', action='store_true', 
                           help='Show authentication status')
    auth_parser.add_argument('--remove', action='store_true',
                           help='Remove saved authentication token')
    
    # Playbook subcommand (simplified interactive mode)
    playbook_parser = subparsers.add_parser('playbook', help='Create session with playbook (simplified)')
    playbook_parser.add_argument('--playbook-id',
                               help='ID of a playbook to use')
    playbook_parser.add_argument('--prompt', '-p',
                               help='The task description for Devin')
    playbook_parser.add_argument('--output', '-o', choices=['json', 'table'], default='table',
                               help='Output format (default: table)')
    
    # Create subcommand (default)
    create_parser = subparsers.add_parser('create', help='Create a new Devin session')
    create_parser.add_argument('--prompt', '-p', 
                             help='The task description for Devin')
    create_parser.add_argument('--snapshot-id', 
                             help='ID of a machine snapshot to use')
    create_parser.add_argument('--playbook-id',
                             help='ID of a playbook to use')
    create_parser.add_argument('--unlisted', action='store_true',
                             help='Make the session unlisted')
    create_parser.add_argument('--idempotent', action='store_true',
                             help='Enable idempotent session creation')
    create_parser.add_argument('--max-acu-limit', type=int,
                             help='Maximum ACU limit for the session')
    create_parser.add_argument('--secret-ids',
                             help='Comma-separated list of secret IDs to use')
    create_parser.add_argument('--knowledge-ids',
                             help='Comma-separated list of knowledge IDs to use')
    create_parser.add_argument('--tags',
                             help='Comma-separated list of tags to add to the session')
    create_parser.add_argument('--title',
                             help='Custom title for the session')
    create_parser.add_argument('--interactive', '-i', action='store_true',
                             help='Run in interactive mode (prompt for missing values)')
    create_parser.add_argument('--non-interactive', action='store_true',
                             help='Disable interactive mode (for scripts)')
    create_parser.add_argument('--output', '-o', choices=['json', 'table'], default='table',
                             help='Output format (default: table)')
    
    # Also add create arguments to main parser for backward compatibility
    parser.add_argument('--prompt', '-p', 
                       help='The task description for Devin')
    parser.add_argument('--snapshot-id', 
                       help='ID of a machine snapshot to use')
    parser.add_argument('--playbook-id',
                       help='ID of a playbook to use')
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
    parser.add_argument('--non-interactive', action='store_true',
                       help='Disable interactive mode (for scripts)')
    parser.add_argument('--output', '-o', choices=['json', 'table'], default='table',
                       help='Output format (default: table)')
    parser.add_argument('--version', action='version', version='1.1.0')
    
    args = parser.parse_args()
    
    # Handle subcommands
    if args.command == 'auth':
        cmd_auth(args)
    elif args.command == 'playbook':
        cmd_playbook(args)
    elif args.command == 'create':
        cmd_create(args)
    else:
        # Default behavior (backward compatibility)
        cmd_create(args)


if __name__ == '__main__':
    main()
