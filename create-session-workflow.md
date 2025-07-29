---
description: Create a new Devin session
---

# Create Devin Session Workflow

This workflow helps you create a new Devin session using the devin-cli tool.

## Prerequisites

1. Make sure you have the devin-cli installed and configured
2. Set up your Devin API token using `devin-cli auth`

## Steps

1. **Check authentication status**
// turbo
```bash
devin-cli auth --test
```

2. **Create a basic session (interactive mode)**
```bash
devin-cli create
```
This will prompt you for the required prompt and optional parameters.

3. **Create a session with command-line arguments**
```bash
devin-cli create --prompt "Your detailed prompt here" --title "Session Title"
```

4. **Create an idempotent session (won't create duplicate if same prompt exists)**
```bash
devin-cli create --prompt "Your prompt" --idempotent
```

5. **Create a session with additional parameters**
```bash
devin-cli create \
  --prompt "Your detailed prompt" \
  --title "Session Title" \
  --tags "tag1,tag2,tag3" \
  --unlisted \
  --max-acu-limit 100
```

## Available Options

- `--prompt`: The main prompt for the Devin session (required)
- `--title`: Title for the session
- `--snapshot-id`: Snapshot ID to use
- `--unlisted`: Make the session unlisted (boolean flag)
- `--idempotent`: Prevent duplicate sessions with same prompt (boolean flag)
- `--max-acu-limit`: Maximum ACU limit for the session
- `--secret-ids`: Comma-separated list of secret IDs
- `--knowledge-ids`: Comma-separated list of knowledge base IDs
- `--tags`: Comma-separated list of tags
- `--output`: Output format (table or json)

## Tips

- Use the `devin-session-guide.md` file for prompt examples and best practices
- The CLI supports both interactive mode (no arguments) and command-line mode
- All sessions are created using the Devin API at https://api.devin.ai/v1/sessions
