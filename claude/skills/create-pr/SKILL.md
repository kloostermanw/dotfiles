---
name: create-pr
description: Generate a pull request title and body from branch changes. Use when the user asks to "open a PR", "create a pull request", "draft the PR", or "make a PR for this branch". Reads the repo's PR template if present and offers to create the PR on GitHub.
---

Generate a pull request title and body from the current branch changes. Follow ALL steps in order.

**Force mode:** If `$ARGUMENTS` contains `f`, `F`, `force`, or `Force`, enable force mode: skip the confirmation question in step 8 and create the PR directly. Treat any remaining argument as the issue number.

1. **Detect Base Branch**
- Determine the repository's default branch:
  ```
  BASE_BRANCH=$(env -u GITHUB_TOKEN gh repo view --json defaultBranchRef -q '.defaultBranchRef.name')
  ```

2. **Analyze Changes**
- Get the commit log since the base branch:
  ```
  git log "$BASE_BRANCH"...HEAD --oneline
  ```
- Get the full diff:
  ```
  git diff "$BASE_BRANCH"...HEAD
  ```

3. **Detect Issue Number**
- If `$ARGUMENTS` is provided, use it as the issue number
- Otherwise, extract the issue number from the current branch name using the pattern `issue-<number>` (e.g. `feature/issue-123` → `123`)
- If neither works, ask the user for the issue number

4. **Read PR Template**
- Read `.github/pull_request_template.md` from the repository root
- If the file does not exist, use a simple structure with sections: Summary, Motivation and Context, How Has This Been Tested, Types of Changes, Checklist

5. **Generate PR Title**
- Write a concise title summarizing the changes (under 72 characters)
- Do NOT use conventional commit prefixes (`feat:`, `fix:`, `change:`, etc.)
- The title should read naturally as a description of what the PR does

6. **Generate PR Body**
- Fill in the PR template sections using context from the diff and commit log
- For "Motivation and Context" (or equivalent section), include `closes #<issue-number>`
- Be concise but informative — focus on what changed and why
- Do NOT add any reference to Claude, Claude Code, Anthropic, or Co-Authored

7. **Present Output**
- Display the generated title and body formatted as ready-to-use markdown
- Use a clear visual separation between title and body

8. **ALWAYS Offer GitHub Submission** (skip in force mode — create the PR directly instead)
- IMPORTANT: Always ask this question after providing the PR text — do not skip this step (unless force mode is enabled)
- Ask: "Would you like me to create this PR on GitHub and assign it to you?"

9. **Create PR on GitHub (if confirmed or force is given)**
- Use `env -u GITHUB_TOKEN gh pr create` with the generated title and body
- Target the base branch detected in step 1
- Assign the PR to the current user (`env -u GITHUB_TOKEN gh pr edit <number> --add-assignee @me`)
