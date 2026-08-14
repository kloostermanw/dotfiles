---
name: create-commit
description: Generate a conventional commit message for staged changes following the format. Use when the user asks to "commit this", "write a commit message", "generate a commit", or is about to commit staged changes. Presents the message and asks before committing.
---

Generate a conventional commit message for the staged changes. Follow ALL steps in order.

**Force mode:** If `$ARGUMENTS` contains `f`, `F`, `force`, or `Force`, enable force mode: skip the confirmation question in step 10 and commit directly. Treat any remaining argument as the commit type.

1. Analyze the current uncommited changes
2. Generate a commit message that conforms to the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) standard
3. Use the $ARGUMENTS type for the conventional commit message type
4. If no $ARGUMENTS type is provided, use one of the following types: feat, fix, change, docs and refactor
5. DO NOT use optional scope for the conventional commit message, only the type, description and body
6. Extract the issue number from the branch name if the branch name follows the standard "issue-<issue-number>"
7. Add the issue number with a leading # character to the conventional commit message footer if it exists. Prefix it with the word "references". Do NOT put the issue number in the subject line.
8. DO NOT actually commit the changes using gh or git commands until the user confirms (or force mode is enabled)
9. Provide the commit message formatted so it's ready to use
10. ALWAYS Offer GitHub Submission (skip in force mode — commit directly instead)
   - IMPORTANT: Always ask this question after providing the commit message - do not skip this step (unless force mode is enabled)
   - Do not add any reference to Claude, Claude Code, Anthropic or Co-Authored to the commit message
   - Ask: "Would you like me to commit these changes?"
