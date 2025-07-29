#!/usr/bin/env python3
"""
Devin CLI - Enhanced version with auth management
A command line tool for creating Devin sessions with built-in authentication management
"""

import os
import sys
import json
import requests
import click
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
    click.echo(f"✅ Token saved securely to {token_file}")


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
            click.echo(f"⚠️  Warning: Could not read saved token: {e}", err=True)
    
    return None


def get_api_key() -> str:
    """Get API key from environment variable or saved file"""
    api_key = load_token()
    if not api_key:
        raise click.ClickException(
            "No Devin API token found.\n\n"
            "To set up authentication, run:\n"
            "  devin-cli auth\n\n"
            "Or set the environment variable:\n"
            "  export DEVIN_API_KEY=your_token_here"
        )
    return api_key


def test_token(token: str) -> bool:
    """Test if a token is valid by making a test API request"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Make a minimal test request
    try:
        response = requests.post(
            'https://api.devin.ai/v1/sessions',
            headers=headers,
            json={'prompt': 'test'},
            timeout=10
        )
        # Check for authentication errors
        if response.status_code in [401, 403]:
            return False  # Invalid token
        # If we get any other response (including errors), assume token is valid
        return True
    except Exception:
        # Network errors, assume token format is OK
        return True


def make_api_request(payload: dict) -> dict:
    """Make API request to create Devin session"""
    api_key = get_api_key()
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            'https://api.devin.ai/v1/sessions',
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise DevinAPIError(f"API request failed: {e}")


def parse_list_input(value: str) -> List[str]:
    """Parse comma-separated string into list"""
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version='1.1.0')
def cli(ctx):
    """Devin CLI - Create and manage Devin sessions"""
    if ctx.invoked_subcommand is None:
        # Default behavior - show help
        click.echo(ctx.get_help())


@cli.command()
@click.option('--test', is_flag=True, help='Test the current token')
def auth(test):
    """Set or test your Devin API token"""
    if test:
        token = load_token()
        if token:
            click.echo("Testing token...")
            if test_token(token):
                source = "environment variable" if os.getenv('DEVIN_API_KEY') else "saved file"
                click.echo(f"✅ Token is valid (from {source})")
            else:
                click.echo("❌ Token is invalid")
        else:
            click.echo("❌ No token found")
        return
    
    # Set token
    click.echo("Enter your Devin API token (get it from: https://api.devin.ai)")
    token = click.prompt('Token', hide_input=True, type=str)
    
    click.echo("Testing token...")
    if test_token(token):
        save_token(token)
        click.echo("✅ Token saved and verified!")
    else:
        click.echo("❌ Token is invalid. Please check and try again.")
        sys.exit(1)


@cli.command()
@click.option('--prompt', '-p', help='The task description for Devin')
@click.option('--snapshot-id', help='ID of a machine snapshot to use')
@click.option('--unlisted', is_flag=True, default=None, help='Make the session unlisted')
@click.option('--idempotent', is_flag=True, default=None, help='Enable idempotent session creation')
@click.option('--max-acu-limit', type=int, help='Maximum ACU limit for the session')
@click.option('--secret-ids', help='Comma-separated list of secret IDs to use')
@click.option('--knowledge-ids', help='Comma-separated list of knowledge IDs to use')
@click.option('--tags', help='Comma-separated list of tags to add to the session')
@click.option('--title', help='Custom title for the session')
@click.option('--output', '-o', type=click.Choice(['json', 'table']), default='table', help='Output format')
def create(prompt, snapshot_id, unlisted, idempotent, max_acu_limit, 
          secret_ids, knowledge_ids, tags, title, output):
    """Create a new Devin session (interactive by default)"""
    
    # If no prompt provided, go into full interactive mode
    if not prompt:
        prompt = click.prompt('Task description for Devin', type=str)
        
        # Prompt for all optional fields in interactive mode
        if snapshot_id is None:
            snapshot_id = click.prompt('Snapshot ID (optional)', default='', show_default=False)
            snapshot_id = snapshot_id if snapshot_id else None
        
        if unlisted is None:
            unlisted = click.confirm('Make session unlisted?', default=False)
        
        if idempotent is None:
            idempotent = click.confirm('Enable idempotent session creation?', default=False)
        
        if max_acu_limit is None:
            max_acu_limit_input = click.prompt('Maximum ACU limit (optional)', default='', show_default=False)
            max_acu_limit = int(max_acu_limit_input) if max_acu_limit_input else None
        
        if secret_ids is None:
            secret_ids = click.prompt('Secret IDs (comma-separated, optional)', default='', show_default=False)
        
        if knowledge_ids is None:
            knowledge_ids = click.prompt('Knowledge IDs (comma-separated, optional)', default='', show_default=False)
        
        if tags is None:
            tags = click.prompt('Tags (comma-separated, optional)', default='', show_default=False)
        
        if title is None:
            title = click.prompt('Custom title (optional)', default='', show_default=False)
            title = title if title else None

    # Build the request payload
    payload = {'prompt': prompt}
    
    # Add optional parameters if provided
    if snapshot_id:
        payload['snapshot_id'] = snapshot_id
    if unlisted is not None:
        payload['unlisted'] = unlisted
    if idempotent is not None:
        payload['idempotent'] = idempotent
    if max_acu_limit is not None:
        payload['max_acu_limit'] = max_acu_limit
    if secret_ids:
        payload['secret_ids'] = parse_list_input(secret_ids)
    if knowledge_ids:
        payload['knowledge_ids'] = parse_list_input(knowledge_ids)
    if tags:
        payload['tags'] = parse_list_input(tags)
    if title:
        payload['title'] = title

    try:
        # Make the API request
        click.echo("Creating Devin session...")
        result = make_api_request(payload)
        
        # Output the result
        if output == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            # Table format
            click.echo("\n✅ Session created successfully!")
            click.echo(f"Session ID: {result.get('session_id', 'N/A')}")
            click.echo(f"URL: {result.get('url', 'N/A')}")
            click.echo(f"New Session: {result.get('is_new_session', 'N/A')}")
            
    except DevinAPIError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)





if __name__ == '__main__':
    cli()
