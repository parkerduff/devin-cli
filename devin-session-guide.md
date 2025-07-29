# Devin Session Creation Guide

This guide provides examples and reference information for creating effective Devin sessions via CLI.

## Official Prompt Structure

Based on the [official Devin playbook documentation](https://docs.devin.ai/product-guides/creating-playbooks), structure your prompts with these sections:

### 1. Overview
- Clear statement of what you want Devin to achieve
- Define what success looks like

### 2. What's Needed From User
- **For CLI sessions**: Always state "No user intervention required - complete end-to-end"
- Include any initial context, credentials, or setup information in the prompt itself

### 3. Procedure
- Write one step per line, each written imperatively with action verbs
- Cover the entire scope: setup → main task → delivery
- Make steps Mutually Exclusive and Collectively Exhaustive
- Don't be overly specific unless necessary (preserve Devin's problem-solving ability)

### 4. Specifications
- Describe postconditions - what should be true after Devin is done
- List files that should exist, tests that should pass, features that should work
- Include performance requirements or quality standards

### 5. Advice and Pointers
- Correct Devin's priors with your preferred approaches
- Include specific commands, tools, or methodologies
- Add technical details that guide toward success

### 6. Forbidden Actions
- Explicitly list actions Devin should absolutely avoid
- Include security, safety, or quality constraints

## Repository-Focused Example

```
## Overview
Analyze and enhance the devin-cli repository with improved error handling, documentation, and test coverage.

## What's Needed From User
No user intervention required - complete end-to-end. Repository: https://github.com/parkerduff/devin-cli

## Procedure
1. Clone the repository https://github.com/parkerduff/devin-cli to local environment
2. Analyze the current codebase structure and identify main components
3. Review existing error handling patterns in devin_cli.py
4. Implement comprehensive error handling for API failures and network issues
5. Add input validation for all CLI parameters
6. Review and enhance existing unit tests in test_cli.py
7. Add integration tests for the complete CLI workflow
8. Update README.md with any new features or improvements
9. Run all tests to ensure functionality is preserved
10. Create a summary report of changes made and test results

## Specifications
- All API calls have proper error handling with user-friendly messages
- Input validation prevents invalid parameters from reaching the API
- Test coverage is above 90% for all new code
- All existing tests continue to pass
- README.md accurately reflects current functionality
- Code follows existing style and conventions
- No breaking changes to the CLI interface

## Advice and Pointers
- Use the existing Click framework patterns for consistency
- Follow the current project structure with devin_cli.py as main module
- Preserve the authentication token management system
- Use pytest for new tests following existing test patterns
- Include both positive and negative test cases
- Use requests library error handling best practices

## Forbidden Actions
- Do not modify the core API endpoint or authentication mechanism
- Do not change the CLI command structure or break backward compatibility
- Do not remove or modify existing functionality without preserving it
- Do not commit any API keys or sensitive information
- Do not change the project's dependency requirements without good reason
```

## Code Review Example

```
## Overview
Review pull request #42 in the devin-cli repository and provide comprehensive feedback with suggested improvements.

## What's Needed From User
No user intervention required - complete end-to-end. Repository: https://github.com/parkerduff/devin-cli, PR: #42

## Procedure
1. Clone the repository https://github.com/parkerduff/devin-cli
2. Fetch and checkout the PR branch for review
3. Analyze the changes made in the pull request
4. Review code quality, style, and adherence to project conventions
5. Check for potential security issues or vulnerabilities
6. Verify that existing tests still pass
7. Identify areas where additional tests might be needed
8. Review documentation updates for accuracy and completeness
9. Create a detailed review report with specific line-by-line feedback
10. Provide overall assessment and recommendations for approval or changes needed

## Specifications
- Review covers all modified files in the PR
- Feedback includes specific line numbers and file references
- Security review identifies any potential vulnerabilities
- Test coverage analysis shows impact on overall coverage
- Documentation review ensures accuracy and completeness
- Final recommendation is clear (approve, request changes, or needs discussion)

## Advice and Pointers
- Focus on maintainability and code clarity
- Check for proper error handling in new code
- Ensure new features follow existing CLI patterns
- Verify that any new dependencies are justified
- Look for opportunities to improve existing code while reviewing

## Forbidden Actions
- Do not make changes to the code, only provide review feedback
- Do not approve or merge the PR, only provide assessment
- Do not access or modify any credentials or sensitive data
- Do not run any destructive commands or modify repository settings
```

## Bug Fix Example

```
## Overview
Fix the authentication token validation issue reported in GitHub issue #15 where expired tokens cause unclear error messages.

## What's Needed From User
No user intervention required - complete end-to-end. Repository: https://github.com/parkerduff/devin-cli, Issue: #15

## Procedure
1. Clone the repository https://github.com/parkerduff/devin-cli
2. Reproduce the issue by testing with an expired token
3. Analyze the current token validation logic in devin_cli.py
4. Identify where the unclear error message is generated
5. Implement improved error handling for expired tokens
6. Add specific error messages for different authentication failure scenarios
7. Update the test_token() function to handle edge cases
8. Add unit tests for the new error handling scenarios
9. Test the fix with various token states (valid, expired, invalid, missing)
10. Update documentation if needed and create a summary of the fix

## Specifications
- Expired tokens show clear message: "Authentication token has expired. Run 'devin-cli auth' to update."
- Invalid tokens show: "Authentication token is invalid. Run 'devin-cli auth' to set up authentication."
- Missing tokens show: "No authentication token found. Run 'devin-cli auth' to set up authentication."
- All error messages include actionable next steps
- Existing functionality is preserved
- New tests cover all authentication error scenarios

## Advice and Pointers
- Use the existing Click error handling patterns
- Preserve the current token storage mechanism in ~/.devin-cli/token
- Follow the existing code style and error message format
- Add tests to test_cli.py following existing patterns
- Use appropriate HTTP status code checking for different error types

## Forbidden Actions
- Do not change the token storage location or format
- Do not modify the API endpoint or authentication mechanism
- Do not break existing error handling for other scenarios
- Do not expose sensitive token information in error messages
```

## Best Practices for Repository Context

### Always Include:
- Full repository URL
- Specific branch if not main/master
- Relevant issue or PR numbers
- File paths for focused work

### Repository Setup Pattern:
```
1. Clone the repository [URL] to local environment
2. Switch to branch [branch-name] if specified
3. Install dependencies using [package manager and command]
4. [Any additional setup steps specific to the repository]
```

### Common Repository Tasks:
- **Analysis**: "Analyze the codebase structure and identify..."
- **Enhancement**: "Improve the existing [component] by adding..."
- **Bug Fix**: "Reproduce and fix the issue described in..."
- **Feature Addition**: "Implement new feature [name] that..."
- **Documentation**: "Update documentation to reflect..."
- **Testing**: "Add comprehensive tests for..."

### Delivery Specifications:
- Always specify what files should be created/modified
- Include test requirements
- Specify documentation updates needed
- Define success criteria clearly
