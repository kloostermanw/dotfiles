---
name: pr-standards
description: Pull request creation and review standards. Use whenever writing a PR title or body, reviewing a pull request, discussing PR quality, or preparing changes for review in a project. Also triggers when the user asks to "open a PR", "review this PR", or when evaluating whether code is ready to merge.
---

# PR Standards

Standards for creating and reviewing pull requests in projects.

## Creating a PR

### Title

- Natural language — describe what the PR does
- Do **not** use conventional commit prefixes (`feat:`, `fix:`, etc.)
- Keep under 72 characters
- Good: "Add pagination to employee list endpoint"
- Bad: "feat: add pagination to employee list endpoint"

### Body

- Use the repo's `.github/pull_request_template.md` if it exists
- If no template, use sections: Summary, Motivation and Context, How Has This Been Tested, Types of Changes, Checklist
- Include `closes #<issue-number>` in the Motivation and Context section (this is how GitHub auto-closes the issue on merge)
- Do **not** add any Claude, Claude Code, Anthropic, or Co-Authored attribution

### GitHub CLI

Always use the `env -u GITHUB_TOKEN gh` pattern:

```bash
env -u GITHUB_TOKEN gh pr create --title "Title here" --body "Body here"
```

## Reviewing a PR

Evaluate the diff against these 7 dimensions. Skip a dimension only if it genuinely does not apply.

### 1. Correctness & Issue Alignment

- Does the code solve the linked issue?
- Are there edge cases the implementation misses?
- Could any change introduce a regression?

### 2. Code Quality

- Single responsibility, no unnecessary complexity
- Clear naming for methods, variables, and classes
- Readable without the PR description
- No dead code, commented-out blocks, or debugging artifacts

### 3. Error Handling

- Failure paths handled explicitly (not swallowed silently)
- User-facing error messages are clear and actionable
- Exceptions caught at the right level of abstraction

### 4. Security

- Input validation and sanitization on user-facing input
- No hardcoded credentials, tokens, or secrets
- Authorization checks on new/modified endpoints
- No SQL injection, XSS, or CSRF exposure

### 5. Performance

- Database queries are indexed, scoped, and efficient
- No N+1 query risks in loops
- No unbounded operations (loading all records without pagination)
- Resource cleanup (connections, file handles, streams)

### 6. Testing (Critical — Blocking)

This is the most important dimension. Missing or inadequate tests is a **blocking** finding.

**Coverage:**
- New/updated tests for every behavioral change
- Bug fixes must have a regression test
- New features need success path AND failure path tests
- Refactors must maintain existing test coverage

**Quality:**
- Assert on behavior/outcomes, not implementation details
- Descriptive test names that serve as documentation
- Edge cases: empty inputs, null values, boundaries, permissions, concurrency

**Missing tests = blocking finding.** Clearly state what tests must be added before the PR can be approved.

### 7. Documentation

- New public methods/classes documented
- User-facing changes have documentation updates
- Complex algorithms or non-obvious decisions explained

## Review Verdict

Choose one:

| Verdict | When to use |
|---------|-------------|
| **Approve** | No blocking issues, ready to merge |
| **Approve with minor revisions** | Only minor/suggestion findings, safe to merge after small fixes |
| **Request changes** | Blocking issues must be resolved before merge |

## Review Output Format

Structure the review as:

1. **Summary** — What the PR does, which issue it addresses, whether implementation matches requirements (2–3 sentences)
2. **Testing assessment** — Test coverage status, gaps, specific tests to add
3. **Summary table** — All findings: `Severity | File:Line | Finding`
4. **Verdict** — One of the three options above
