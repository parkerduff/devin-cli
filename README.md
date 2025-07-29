# Devin CLI

A command line tool for creating Devin sessions via the Devin API with built-in authentication management.

## Installation

### Option 1: Install Directly from GitHub (Recommended)

```bash
# Install latest version directly from GitHub
pip install git+https://github.com/parkerduff/devin-cli.git

# Or install for current user only (no sudo needed)
pip install --user git+https://github.com/parkerduff/devin-cli.git
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/parkerduff/devin-cli.git
cd devin-cli

# Install globally
pip install .

# Or install for current user only (no sudo needed)
pip install --user .

# For development (editable install)
pip install -e .
```

### Verify Installation

```bash
# Check that the command is available
devin-cli --help

# Check version
devin-cli --version
```

## Authentication Setup

The CLI provides built-in authentication management. You can set up your API key in two ways:

### Option 1: Using the CLI (Recommended)

```bash
# Set up authentication interactively
devin-cli auth

# Test your current token
devin-cli auth --test
```

This securely stores your token in `~/.devin-cli/token` with restricted file permissions.

### Option 2: Environment Variable

```bash
export DEVIN_API_KEY=your_token_here
```

The CLI will automatically use the environment variable if available, or fall back to the saved token file.

## Important Note: Playbooks

**⚠️ Playbooks are not currently supported via CLI** - The `playbook_id` parameter is not functional at this time. Instead, you should create thorough, detailed prompts that include all necessary information for Devin to complete your task successfully.

### Creating Effective Prompts

Since playbooks aren't available via CLI, structure your prompts using the official Devin playbook format. **Important**: CLI sessions should be designed to run end-to-end without human intervention, so avoid any requirements for user input during execution.

#### Essential Sections for Your Prompt:

**1. Overview/Outcome**
- Clearly state what you want Devin to achieve
- Define what success looks like

**2. Procedure** 
- Write one step per line, each written imperatively with action verbs
- Cover the entire scope: setup → main task → delivery
- Make steps Mutually Exclusive and Collectively Exhaustive
- Don't be overly specific unless necessary (preserve Devin's problem-solving ability)

**3. Specifications**
- Describe postconditions - what should be true after Devin is done
- List files that should exist, tests that should pass, features that should work
- Include performance requirements or quality standards

**4. Advice and Pointers**
- Correct Devin's priors with your preferred approaches
- Include specific commands, tools, or methodologies
- Add technical details that guide toward success

**5. Forbidden Actions**
- Explicitly list actions Devin should absolutely avoid
- Include security, safety, or quality constraints

**6. What's Needed From User**
- **For CLI sessions**: State "No user intervention required - complete end-to-end"
- Include any initial context, credentials, or setup information in the prompt itself

### Example Structured Prompt

```
## Overview
Create a REST API for user management with authentication, fully deployed and documented.

## What's Needed From User
No user intervention required - complete end-to-end. All configuration and deployment should be automated.

## Procedure
1. Initialize a new Node.js project with Express and required dependencies
2. Set up project structure with routes, middleware, and models directories
3. Implement user registration endpoint with email validation and password hashing
4. Implement login endpoint with JWT token generation
5. Create authentication middleware for protected routes
6. Implement user profile endpoints (GET, PUT) with authentication
7. Add comprehensive input validation and error handling
8. Write unit tests for all endpoints
9. Create API documentation using Swagger/OpenAPI
10. Set up environment configuration for development and production
11. Deploy to a cloud platform (Heroku, Railway, or similar)
12. Provide deployment URL and API documentation

## Specifications
- All endpoints return JSON responses with consistent error format
- Passwords hashed using bcrypt with salt rounds >= 12
- JWT tokens expire after 24 hours
- All routes except registration/login require valid JWT authentication
- Input validation prevents SQL injection and XSS attacks
- API documentation accessible at /api-docs endpoint
- Application successfully deployed and accessible via HTTPS
- Environment variables used for all sensitive configuration

## Advice and Pointers
- Use Express.js with helmet for security headers
- Implement rate limiting to prevent abuse
- Use joi or express-validator for request validation
- Follow RESTful conventions: POST /auth/register, POST /auth/login, GET /users/profile
- Include CORS configuration for frontend integration
- Use dotenv for environment variable management

## Forbidden Actions
- Do not store passwords in plain text or use weak hashing
- Do not commit API keys, secrets, or database credentials to repository
- Do not skip input validation on any endpoint
- Do not use deprecated or vulnerable package versions
- Do not expose sensitive information in error messages
```

## Usage

The CLI has three main commands:

- `devin-cli auth` - Manage authentication
- `devin-cli create` - Create Devin sessions
- `devin-cli setup` - Download workflow templates and guides

### Creating Sessions

#### Interactive Mode (Default)

When you don't provide a prompt, the CLI enters interactive mode:

```bash
# Interactive session creation
devin-cli create
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

#### Command Line Mode

Provide parameters via command line flags:

```bash
# Basic usage with just a prompt
devin-cli create --prompt "Review the pull request at https://github.com/example/repo/pull/123"

# With additional options
devin-cli create --prompt "Analyze this codebase" --idempotent --unlisted --title "Code Analysis Session"

# With lists (comma-separated)
devin-cli create --prompt "Deploy to production" --tags "deployment,production" --secret-ids "secret1,secret2"
```

#### Mixed Mode

You can provide some flags and be prompted for missing required parameters:

```bash
# Will prompt for the task description since it's required
devin-cli create --idempotent --unlisted
```

### Setting Up Templates

The `setup` command downloads the latest workflow templates and session guide to your repository:

```bash
# Download templates to current directory
devin-cli setup

# Download to specific directory
devin-cli setup --target-dir /path/to/project

# Force overwrite existing files
devin-cli setup --force
```

This downloads:
- `devin-session-guide.md` - Comprehensive guide with examples and best practices
- `.windsurf/workflows/create-session.md` - Windsurf workflow for creating sessions

#### Setup Command Options

- `--target-dir, -t`: Target directory to copy files to (default: current directory)
- `--force, -f`: Overwrite existing files without prompting

## Commands and Options

### Authentication Commands

```bash
# Set up or update your API token
devin-cli auth

# Test your current token
devin-cli auth --test
```

### Session Creation Options

For the `devin-cli create` command:

- `--prompt, -p`: The task description for Devin (required, or will be prompted)
- `--snapshot-id`: ID of a machine snapshot to use
- `--unlisted`: Make the session unlisted (flag)
- `--idempotent`: Enable idempotent session creation (flag)
- `--max-acu-limit`: Maximum ACU limit for the session (integer)
- `--secret-ids`: Comma-separated list of secret IDs to use
- `--knowledge-ids`: Comma-separated list of knowledge IDs to use
- `--tags`: Comma-separated list of tags to add to the session
- `--title`: Custom title for the session
- `--output, -o`: Output format (`json` or `table`, default: `table`)

### Global Options

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
devin-cli create --prompt "Test task" --output json
```

## Examples

```bash
# Simple session creation
devin-cli create --prompt "Review PR #249"

# Production deployment with secrets and tags
devin-cli create --prompt "Deploy to production" \
      --tags "deployment,production,urgent" \
      --secret-ids "aws-prod,db-prod" \
      --title "Production Deployment - v2.1.0"

# Idempotent session (safe to retry)
devin-cli create --prompt "Run tests" --idempotent

# Interactive mode for complex sessions
devin-cli create

# JSON output for scripting
devin-cli create --prompt "Generate report" --output json | jq '.session_id'

# Setup examples
devin-cli setup                   # Download templates to current directory
devin-cli setup --force          # Overwrite existing files
devin-cli setup -t ~/my-project  # Download to specific directory

# Authentication examples
devin-cli auth                    # Set up token
devin-cli auth --test            # Test current token
```

## Error Handling

The tool will exit with appropriate error codes:
- `0`: Success
- `1`: API error or other failure

### Authentication Errors

If you encounter authentication errors:

1. **No token found**: Run `devin-cli auth` to set up your API key
2. **Invalid token**: Run `devin-cli auth --test` to verify your token, then `devin-cli auth` to update it
3. **Token file issues**: The CLI stores tokens securely in `~/.devin-cli/token` with restricted permissions

### API Errors

Common API errors and solutions:
- **401/403 errors**: Authentication issue - check your token with `devin-cli auth --test`
- **Network errors**: Check your internet connection and try again
- **Rate limiting**: Wait a moment and retry your request
