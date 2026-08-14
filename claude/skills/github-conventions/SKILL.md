---
name: github-conventions
description: Conventions for GitHub CLI usage and GitHub content. Use whenever running `gh` commands, creating GitHub issues, commenting on PRs, or interacting with the GitHub API in a project. Also triggers when detecting `gh` in shell commands, discussing GitHub workflows, or writing content destined for GitHub (issue bodies, PR comments, release notes).
---

# GitHub Conventions

These conventions apply to **all** GitHub interactions in projects (`kloostermanw` org).

## GitHub CLI Authentication

Always unset `GITHUB_TOKEN` so the `gh` CLI uses the user's native authentication instead of any ambient token (e.g., Claude Code's token):

```bash
env -u GITHUB_TOKEN gh <command>
```

This applies to every `gh` invocation — API calls, issue commands, PR commands, GraphQL queries, extensions, etc.

## Repository Detection

Never hardcode the repository name. Always detect it dynamically:

```bash
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
```

The **org is intentionally hardcoded** as `kloostermanw` — this is a private org marketplace. So full repo references look like:

```bash
env -u GITHUB_TOKEN gh issue list -R "kloostermanw/$REPO_NAME"
```

## Issue Titles

- Use natural language — describe the problem or feature clearly
- Do **not** use conventional commit prefixes (`feat:`, `fix:`, `change:`, etc.)
- Good: "Add pagination to employee list endpoint"
- Bad: "feat: add pagination to employee list endpoint"

## Issue Types

Issue types are set via the GitHub GraphQL API after creation, not via labels or title prefixes:

```bash
# Query available types
env -u GITHUB_TOKEN gh api graphql -f query='{ repository(owner: "kloostermanw", name: "'"$REPO_NAME"'") { issueTypes(first: 20) { nodes { id name } } } }'

# Set type on an issue
env -u GITHUB_TOKEN gh api graphql -f query='mutation { updateIssue(input: { id: "ISSUE_NODE_ID", issueTypeId: "ISSUE_TYPE_ID" }) { issue { issueType { name } } } }'
```

## Attribution

Do **not** add any Claude, Claude Code, Anthropic, or Co-Authored attribution to GitHub content — issues, PRs, comments, commit messages, or release notes.

## Content Downloads

GitHub issues and PRs embed content via three different URL types. Always run `mkdir -p .claude/local/assets` before downloading. View downloaded images with the Read tool — they often contain critical context (UI mockups, error screenshots, data samples).

### Type 1: User-uploaded images (`gh-asset`)

URLs matching `private-user-images.githubusercontent.com/...`

```bash
env -u GITHUB_TOKEN gh-asset download <ASSET_ID> .claude/local/assets
```

This is an optional dependency — check availability before using.

### Type 2: Assets-branch images (`git show`)

URLs matching `github.com/kloostermanw/<repo>/raw/assets/.github/issue-assets/...`

Extract the path after `/raw/assets/` and use `git show`:

```bash
# Example URL: https://github.com/kloostermanw/genotool/raw/assets/.github/issue-assets/4350/6230320386.png
# Extracted path: .github/issue-assets/4350/6230320386.png
git fetch origin assets
git show origin/assets:.github/issue-assets/4350/6230320386.png > .claude/local/assets/6230320386.png
```

### Type 3: User-attached files (`gh api`)

URLs matching `github.com/user-attachments/files/<id>/<filename>`

Download using `gh api` with the full URL:

```bash
env -u GITHUB_TOKEN gh api 'https://github.com/user-attachments/files/25766326/filename.docx' \
  > .claude/local/assets/filename.docx
```

Non-image attachments (Excel, PDF, Word) cannot be viewed directly but should still be downloaded — note their presence as context for the issue.
