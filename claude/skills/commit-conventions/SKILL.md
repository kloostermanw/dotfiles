---
name: commit-conventions
description: Conventional commit message format and rules. Use whenever writing, suggesting, or reviewing a commit message in a project. Also triggers when the user asks to commit changes, discusses commit history, or when you are about to run `git commit`. Applies to all repositories in the kloostermanw org.
---

# Commit Conventions

All projects use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) with these specific rules.

## Format

```
type: description

Optional body explaining why, not what.

references #N
```

## Rules

### Type (required)

Use one of these types only:

| Type | When to use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `change` | Non-breaking change to existing behavior |
| `docs` | Documentation only |
| `refactor` | Code restructuring with no behavior change |

### Scope

Do **not** use scopes. Write `feat: description`, not `feat(scope): description`.

### Subject Line

- Lowercase after the type prefix
- Imperative mood ("add pagination", not "added pagination")
- Do **not** put issue numbers in the subject line

### Body

- Provide context on **why** the change was made, not what changed (the diff shows that)
- Separate from the subject with a blank line

### Footer — Issue Reference

- Extract the issue number from the branch name pattern `issue-<number>` (e.g., `feature/issue-42` → `42`)
- Add as a footer: `references #42`
- Use `references` — not `closes`, `fixes`, or `resolves` (PR closing keywords go in the PR body, not commits)
- Omit the footer if there is no issue number

### Attribution

Do **not** add any Claude, Claude Code, Anthropic, or Co-Authored-By attribution to commit messages.

## Examples

**Minimal:**
```
fix: correct overtime calculation for part-time employees
```

**With body and issue reference:**
```
feat: add bulk import for employee records

The previous one-at-a-time flow was blocking onboarding for clients
with 500+ employees. This adds a CSV upload path that processes
records in batches of 50.

references #128
```
