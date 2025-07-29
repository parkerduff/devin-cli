---
description: Run a Devin playbook on the current repository
---

# Run Devin Playbook Workflow

This workflow runs a Devin playbook on your repository using the devin-cli tool.

## Prerequisites

1. Ensure you have authentication set up:
   ```bash
   devin-cli auth --status
   ```
   
   If not authenticated, run:
   ```bash
   devin-cli auth
   ```

## Steps

1. **Setup: Get repository info and playbook ID**
   ```bash
   # Auto-detect repository from git remote
   REPO_INFO=$(git remote get-url origin | sed 's/.*github.com[:\/]//g' | sed 's/\.git$//')
   echo "Detected repository: $REPO_INFO"
   
   # Prompt for playbook ID if not already provided
   read -p "Enter Playbook ID: " PLAYBOOK_ID
   ```

2. **Run the playbook with both parameters**
   ```bash
   # Run the playbook command with both playbook ID and repository prompt
   devin-cli playbook --playbook-id "$PLAYBOOK_ID" --prompt "run this end to end on repository $REPO_INFO"
   ```

3. **Automatically open session in Windsurf browser preview**
   - The workflow will automatically extract the session URL from the CLI output
   - The session will open in the in-IDE browser preview for monitoring
   - You can interact with Devin directly through the preview as the playbook runs

## Example Output

## Troubleshooting

- **"Playbook ID does not belong to your org"**: Make sure you're using a playbook ID from your organization
- **"Unauthorized"**: Check your authentication with `devin-cli auth --status`
- **Network errors**: Ensure you have internet connectivity

## Tips

- Keep your playbook IDs handy for frequently used playbooks
- Use descriptive task descriptions that include the repository name
- The session URL allows you to monitor and interact with the running playbook
- You can run multiple playbooks simultaneously by creating multiple sessions