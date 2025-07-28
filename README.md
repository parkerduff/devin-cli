# Devin CLI

A command line tool for creating Devin sessions via the Devin API.

## Installation

### Option 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/parkerduff/devin-cli.git
cd devin-cli

# Install using pip (standalone version, no dependencies)
pip install .

# Or install in development mode
pip install -e .
```

### Option 2: Direct Download and Install

```bash
# Download and run the installation script
curl -sSL https://raw.githubusercontent.com/parkerduff/devin-cli/main/manual_install.sh | bash
```

### Option 3: Manual Installation (No pip required)

```bash
# Download the standalone script
curl -O https://raw.githubusercontent.com/parkerduff/devin-cli/main/devin_cli_standalone.py
chmod +x devin_cli_standalone.py

# Use directly
./devin_cli_standalone.py --help

# Or create an alias
echo 'alias devin-cli="python3 /path/to/devin_cli_standalone.py"' >> ~/.zshrc
source ~/.zshrc
```

## Setup

Set your Devin API key as an environment variable:

```bash
export DEVIN_API_KEY=your_token_here
```

## Usage

### Command Line Flags Mode

Provide all parameters via command line flags:

```bash
# Basic usage with just a prompt
devin --prompt "Review the pull request at https://github.com/example/repo/pull/123"

# With additional options
devin --prompt "Analyze this codebase" --idempotent --unlisted --title "Code Analysis Session"

# With lists (comma-separated)
devin --prompt "Deploy to production" --tags "deployment,production" --secret-ids "secret1,secret2"
```

### Interactive Mode

Use the `-i` or `--interactive` flag to be prompted for each parameter:

```bash
devin -i
```

This will prompt you for:
- Task description (required)
- Snapshot ID (optional)
- Whether to make session unlisted
- Whether to enable idempotent creation
- Maximum ACU limit
- Secret IDs
- Knowledge IDs
- Tags
- Custom title

### Mixed Mode

You can combine flags with interactive mode. Any missing required parameters will be prompted:

```bash
# Will prompt for the task description since it's required
devin --idempotent --unlisted
```

## Options

- `--prompt, -p`: The task description for Devin (required)
- `--snapshot-id`: ID of a machine snapshot to use
- `--unlisted`: Make the session unlisted (flag)
- `--idempotent`: Enable idempotent session creation (flag)
- `--max-acu-limit`: Maximum ACU limit for the session (integer)
- `--secret-ids`: Comma-separated list of secret IDs to use
- `--knowledge-ids`: Comma-separated list of knowledge IDs to use
- `--tags`: Comma-separated list of tags to add to the session
- `--title`: Custom title for the session
- `--interactive, -i`: Run in interactive mode
- `--output, -o`: Output format (`json` or `table`, default: `table`)
- `--version`: Show version information
- `--help`: Show help message

## Output

By default, the tool outputs a formatted table with session information:

```
✅ Session created successfully!
Session ID: devin-xxx
URL: https://app.devin.ai/sessions/xxx
New Session: true
```

Use `--output json` for JSON output:

```bash
devin --prompt "Test task" --output json
```

## Examples

```bash
# Simple session creation
devin --prompt "Review PR #249"

# Production deployment with secrets and tags
devin --prompt "Deploy to production" \
      --tags "deployment,production,urgent" \
      --secret-ids "aws-prod,db-prod" \
      --title "Production Deployment - v2.1.0"

# Idempotent session (safe to retry)
devin --prompt "Run tests" --idempotent

# Interactive mode for complex sessions
devin -i

# JSON output for scripting
devin --prompt "Generate report" --output json | jq '.session_id'
```

## Error Handling

The tool will exit with appropriate error codes:
- `0`: Success
- `1`: API error or other failure

Make sure your `DEVIN_API_KEY` environment variable is set correctly.
