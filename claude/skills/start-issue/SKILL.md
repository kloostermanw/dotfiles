---
name: start-issue
description: Start working on a GitHub issue — fetch details, download embedded assets, create a git-flow branch, explore relevant code and tests, build an implementation plan, and ask before coding.
---

Work on GitHub issue $ARGUMENTS. Follow ALL steps in order.

1. **Fetch Issue Details**
   - Run `env -u GITHUB_TOKEN gh issue view $ARGUMENTS` to get the full issue details
   - Extract key information: title, description, labels, type (bug/feature/task)

2. **Download and View Embedded Content**
   - IMPORTANT: If the issue contains any images, screenshots, or attached files, IMMEDIATELY download them
   - Run `mkdir -p .claude/local/assets` first
   - **User-uploaded images** (`private-user-images.githubusercontent.com/...`): Use `env -u GITHUB_TOKEN gh-asset download <ASSET_ID> .claude/local/assets`
   - **Assets-branch images** (`github.com/kloostermanw/<repo>/raw/assets/.github/issue-assets/...`): Extract path after `/raw/assets/`, then `git fetch origin assets` + `git show origin/assets:<path> > .claude/local/assets/<filename>`
   - **User-attached files** (`github.com/user-attachments/files/<id>/<filename>`): Use `env -u GITHUB_TOKEN gh api '<full-url>' > .claude/local/assets/<filename>`
   - View all downloaded images using the Read tool
   - Images often contain critical context (UI mockups, error screenshots, expected behavior)
   - Non-image attachments (Excel, PDF, Word) cannot be viewed directly but note their presence as context

3. **Create Working Branch (Git-Flow)**
   - Check current branch status with `git status`
   - Determine the branch prefix based on issue type from step 1:
     - Most issues (features, bugs, tasks): `feature/issue-$ARGUMENTS`
     - Urgent production fixes only: `hotfix/issue-$ARGUMENTS`
   - If not already on the issue branch, create and switch to it:
     - `git checkout -b <prefix>/issue-$ARGUMENTS` (or checkout if it exists)
   - Confirm branch creation to the user

4. **Analyze Issue Requirements**
   - Identify the type of issue (bug fix, feature, refactor, etc.)
   - Extract acceptance criteria if present
   - Note any mentioned files, components, or areas of the codebase

5. **Explore Relevant Code**
   - Search the codebase for files related to the issue
   - Use keywords from the issue title and description
   - Read relevant files to understand current implementation
   - Identify files that will likely need modification

6. **Explore Existing Tests**
   - Search the codebase for test directories and test files related to the identified code
   - Read existing test files to understand the project's testing patterns and conventions
   - Note which functionality already has test coverage
   - Identify gaps in test coverage that need to be addressed

7. **Create Implementation Plan**
   - Summarize what needs to be done
   - List specific files to modify with brief descriptions of changes
   - Identify potential risks or considerations
   - Note any dependencies or prerequisites
   - Break down the work into **bite-sized tasks** (each task should be independently testable):
     - Each task: what to test first (RED), what to implement (GREEN), how to verify
     - Order tasks by dependency (independent tasks first)
   - **Test Plan (REQUIRED)**:
     - List existing test files that may need updates
     - List new test files to create
     - Describe test scenarios (happy path and edge cases)
     - Follow the project's existing test patterns and conventions

8. **Present Summary**
   - Display a structured summary:
     - Issue: #<number> - <title>
     - Type: <bug/feature/task>
     - Branch: feature/issue-<number> (or hotfix/issue-<number>)
     - Files to modify: <list>
     - Tests to create/update: <list>
     - Implementation approach: <brief description>

9. **ALWAYS Ask to Continue**
   - IMPORTANT: Always ask this question - do not skip this step
   - Ask: "Would you like me to start implementing this issue?"

10. **Begin Implementation (after user confirms)**
    - Follow `superpowers:test-driven-development` for each task (RED-GREEN-REFACTOR cycle)
    - If the plan has multiple independent tasks, use `superpowers:subagent-driven-development` to parallelize
    - Before claiming completion, use `superpowers:verification-before-completion` (run full test suite, verify all acceptance criteria)
    - When done, use `superpowers:finishing-a-development-branch` to decide on merge/PR/keep
