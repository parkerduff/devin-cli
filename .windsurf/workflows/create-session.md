---
description: Create a Devin session with proper context and repository information
---

# Create Devin Session Workflow

This workflow helps you create a well-structured Devin session using the CLI with proper context.

## Prerequisites
1. Ensure you have authenticated with `devin-cli auth`
2. Have the repository URL or path ready
3. Know the specific task you want Devin to accomplish

## Steps

1. **Review Prompt Structure Guide**
   I'll reference `devin-session-guide.md` for the official prompt structure and examples to ensure proper formatting.

2. **Gather Context**
   Following the guide structure, I'll collect:
   - **Overview**: The task/goal you want Devin to accomplish
   - **Repository**: Current repo will be auto-detected if applicable, or specify <owner>/<repo-name>
   - **Procedure details**: Specific files, PRs, issues, or technical constraints
   - **Specifications**: Success criteria and expected outcomes
   - **Advice**: Preferred approaches, tools, or methodologies
   - **Forbidden Actions**: What Devin should avoid

3. **Auto-detect Repository (if needed)**
   // turbo
   If working with the current repository, I'll run:
   ```bash
   git remote get-url origin
   ```
   To extract the owner/repository name automatically.

4. **Create Structured Prompt**
   Using the guide examples as reference, I'll construct a complete prompt with all sections:
   - **Overview**: Clear goal statement
   - **What's Needed From User**: "No user intervention required - complete end-to-end"
   - **Procedure**: Step-by-step instructions with repository context
   - **Specifications**: Success criteria and postconditions
   - **Advice and Pointers**: Technical guidance based on task type
   - **Forbidden Actions**: Security and quality constraints

5. **Verify Prompt**
   I'll show you the complete constructed prompt and ask for your approval before proceeding.

6. **Execute Session Creation**
   Once approved, I'll run the CLI command:
   ```bash
   devin-cli create --prompt "[CONSTRUCTED_PROMPT]" --output table
   ```
   
   With appropriate metadata like tags and title based on the task.

## Example Command
```bash
devin-cli create \
  --prompt "$(cat your-prompt.txt)" \
  --tags "repository,development" \
  --title "Repository Analysis and Enhancement" \
  --idempotent
```

## Repository Detection Process
When you indicate the session should run on the current repository, I will:
1. Check if we're in a git repository
2. Extract the remote origin URL
3. Parse the owner/repository name from the URL
4. Include this information in the session prompt as "Repository: owner/repo"

## Tips
- Devin can identify GitHub repositories using the owner/repository format
- Keep the repository reference at the beginning of your procedure
- Be specific about file paths and directory structures
- Include any environment setup requirements
- Specify the expected deliverables clearly
- Test your prompt structure with the examples in the guide first