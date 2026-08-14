---
name: make-issue
description: Create a new GitHub issue from a brief description with template selection, issue type assignment, and labels. Use when the user asks to "create an issue", "file an issue", "open a ticket", "make a GitHub issue", or describes a bug/feature request they want tracked. Runs issue-readiness assessment before posting.
---

You're going to create a new GitHub issue based on the $ARGUMENTS input from the user.

The user has briefly described the issue in the $ARGUMENTS.

Follow this procedure:

1. Check if there are any GitHub issue templates in the .github/ISSUE_TEMPLATE folder of the current working directory
2. Detect the current repository name:
   ```
   REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
   ```
3. Query available issue types using GraphQL:
   ```
   env -u GITHUB_TOKEN gh api graphql -f query='{ repository(owner: "kloostermanw", name: "'"$REPO_NAME"'") { issueTypes(first: 20) { nodes { id name } } } }'
   ```
4. Ask the user which template to use AND which issue type to assign (Bug, Feature, Task, etc.)
5. Write the issue concise and to the point but with enough working information and context.
   - Do NOT use conventional commit prefixes (`feat:`, `fix:`, `change:`, etc.) in the issue title
   - The title should read naturally as a description of the issue
6. Use the GitHub CLI to create the issue
7. Get the issue's node ID and set the type using GraphQL:
   ```
   REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
   env -u GITHUB_TOKEN gh api graphql -f query='{ repository(owner: "kloostermanw", name: "'"$REPO_NAME"'") { issue(number: ISSUE_NUMBER) { id } } }'
   env -u GITHUB_TOKEN gh api graphql -f query='mutation { updateIssue(input: { id: "ISSUE_NODE_ID", issueTypeId: "ISSUE_TYPE_ID" }) { issue { issueType { name } } } }'
   ```
8. Retrieve the available labels for the repository:
   ```
   env -u GITHUB_TOKEN gh label list --repo kloostermanw/$REPO_NAME --limit 100
   ```
9. You may suggest any relevant labels. Every suggested label must exist in the repo's label list from step 8 — if a listed value is missing there, pick the closest available one and say so.
10. Apply the selected labels:
    ```
    env -u GITHUB_TOKEN gh issue edit <number> --repo kloostermanw/$REPO_NAME \
      --add-label "<priority>" --add-label "<impact>" --add-label "<estimate>" [--add-label "<optional>" ...]
    ```

Finally, provide a link to the newly created issue.
