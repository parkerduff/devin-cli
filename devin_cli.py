#!/usr/bin/env python3
"""
Devin CLI - A command line tool for creating Devin sessions
"""

import os
import sys
import json
import requests
import click
from typing import Optional, List


class DevinAPIError(Exception):
    """Custom exception for Devin API errors"""
    pass


def get_api_key() -> str:
    """Get API key from environment variable"""
    api_key = os.getenv('DEVIN_API_KEY')
    if not api_key:
        raise click.ClickException(
            "DEVIN_API_KEY environment variable is required. "
            "Set it with: export DEVIN_API_KEY=your_token_here"
        )
    return api_key


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


@click.command()
@click.option('--prompt', '-p', 
              help='The task description for Devin')
@click.option('--snapshot-id', 
              help='ID of a machine snapshot to use')
@click.option('--unlisted', is_flag=True, default=None,
              help='Make the session unlisted')
@click.option('--idempotent', is_flag=True, default=None,
              help='Enable idempotent session creation')
@click.option('--max-acu-limit', type=int,
              help='Maximum ACU limit for the session')
@click.option('--secret-ids',
              help='Comma-separated list of secret IDs to use')
@click.option('--knowledge-ids',
              help='Comma-separated list of knowledge IDs to use')
@click.option('--tags',
              help='Comma-separated list of tags to add to the session')
@click.option('--title',
              help='Custom title for the session')
@click.option('--interactive', '-i', is_flag=True,
              help='Run in interactive mode (prompt for missing values)')
@click.option('--output', '-o', type=click.Choice(['json', 'table']), default='table',
              help='Output format')
@click.version_option(version='1.0.0')
def create_session(prompt, snapshot_id, unlisted, idempotent, max_acu_limit, 
                  secret_ids, knowledge_ids, tags, title, interactive, output):
    """Create a new Devin session via the API"""
    
    # If interactive mode or prompt is missing, prompt for required fields
    if interactive or not prompt:
        if not prompt:
            prompt = click.prompt('Task description for Devin', type=str)
        
        # Only prompt for optional fields if in interactive mode
        if interactive:
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
    create_session()
