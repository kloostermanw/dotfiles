#!/usr/bin/env python3
import json
import sys
import os
import re
import time
import hashlib
import subprocess
from datetime import datetime

# --- PR lookup cache -------------------------------------------------------
# gh pr view needs the network (~0.7s), far too slow to run on every status
# line refresh. So we cache the result per (repo, branch) and refresh it in a
# detached background process, always rendering from the cache instantly.
PR_CACHE = os.path.expanduser('~/.claude/.statusline-pr-cache.json')
PR_TTL = 300       # a cached lookup stays "fresh" this many seconds
PR_LOCK_TTL = 30   # min seconds between background refreshes for one branch


def _pr_key(root, branch):
    return f"{root}\n{branch}"


def _pr_lock_path(root, branch):
    h = hashlib.sha1(_pr_key(root, branch).encode()).hexdigest()[:16]
    return os.path.expanduser(f'~/.claude/.statusline-pr-lock-{h}')


def _read_pr_cache():
    try:
        with open(PR_CACHE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}

# Git branch name — resolved against the workspace dir, not the process CWD,
# and handling worktrees where .git is a file pointing elsewhere.
def read_git_branch(root):
    if not root:
        return ""
    git_path = os.path.join(root, '.git')
    head_file = ""
    if os.path.isdir(git_path):
        head_file = os.path.join(git_path, 'HEAD')
    elif os.path.isfile(git_path):
        try:
            with open(git_path, 'r') as f:
                line = f.read().strip()
        except OSError:
            return ""
        if line.startswith('gitdir:'):
            head_file = os.path.join(line[len('gitdir:'):].strip(), 'HEAD')
    if not head_file:
        return ""
    try:
        with open(head_file, 'r') as f:
            ref = f.read().strip()
    except OSError:
        return ""
    if ref.startswith('ref: refs/heads/'):
        return ref[len('ref: refs/heads/'):]
    if ref:
        return ref[:7]  # detached HEAD → short SHA
    return ""


def run_git(root, args):
    """Run a git command in `root`; return stdout on success, None otherwise."""
    try:
        r = subprocess.run(
            ['git'] + args,
            cwd=root, capture_output=True, text=True, timeout=1.0,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def refresh_pr(root, branch):
    """Background worker: ask gh for the PR of `branch` and update the cache."""
    number = None
    url = None
    # Match the project convention of running gh without an inherited token.
    env = {k: v for k, v in os.environ.items() if k != 'GITHUB_TOKEN'}
    try:
        r = subprocess.run(
            ['gh', 'pr', 'view', '--json', 'number,url'],
            cwd=root, capture_output=True, text=True, timeout=8, env=env,
        )
        if r.returncode == 0:
            d = json.loads(r.stdout)
            number = d.get('number')
            url = d.get('url')
    except (OSError, subprocess.SubprocessError, ValueError):
        pass

    cache = _read_pr_cache()
    cache[_pr_key(root, branch)] = {'number': number, 'url': url, 'ts': time.time()}
    try:
        tmp = f"{PR_CACHE}.{os.getpid()}.tmp"
        with open(tmp, 'w') as f:
            json.dump(cache, f)
        os.replace(tmp, PR_CACHE)
    except OSError:
        pass


def _spawn_pr_refresh(root, branch):
    """Kick off a detached refresh, throttled so we don't spam gh."""
    lock = _pr_lock_path(root, branch)
    try:
        if time.time() - os.path.getmtime(lock) < PR_LOCK_TTL:
            return  # a refresh ran (or is running) very recently
    except OSError:
        pass
    try:
        with open(lock, 'w'):
            pass
    except OSError:
        pass
    try:
        subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), '--refresh-pr', root, branch],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL, start_new_session=True,
        )
    except OSError:
        pass


def get_pr(root, branch):
    """Return (number, url) for the branch's PR from cache; refresh if stale.

    Returns (None, None) when no PR exists or it isn't known yet."""
    if not root or not branch:
        return None, None
    entry = _read_pr_cache().get(_pr_key(root, branch))
    if entry is None or (time.time() - entry.get('ts', 0)) >= PR_TTL:
        _spawn_pr_refresh(root, branch)
    if entry is None:
        return None, None
    return entry.get('number'), entry.get('url')


def repo_web_url(root):
    """https URL for origin, normalising ssh/.git forms. '' if unknown."""
    out = run_git(root, ['remote', 'get-url', 'origin'])
    if not out:
        return ""
    u = out.strip()
    if u.endswith('.git'):
        u = u[:-4]
    if u.startswith('git@'):  # git@github.com:owner/repo
        host, _, path = u[len('git@'):].partition(':')
        return f"https://{host}/{path}" if path else ""
    return u


def hyperlink(url, text):
    """Wrap text in an OSC 8 terminal hyperlink (plain text if no url)."""
    if not url:
        return text
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


def git_status_line(root, branch):
    """Second status line: branch, PR, uncommitted count, and divergence vs develop."""
    if not branch:
        return ""

    web = repo_web_url(root)

    # Make the issue number inside the branch name link to the GitHub issue.
    branch_label = branch
    m = re.search(r'issue[-_/]?(\d+)', branch, re.IGNORECASE) or re.search(r'(\d+)', branch)
    if m and web:
        num = m.group(1)
        linked = hyperlink(f"{web}/issues/{num}", num)
        branch_label = branch[:m.start(1)] + linked + branch[m.end(1):]
    parts = [f"🌿 {branch_label}"]

    # PR segment (only when a PR exists); #number links to the PR.
    pr_number, pr_url = get_pr(root, branch)
    if pr_number:
        pr_url = pr_url or (f"{web}/pull/{pr_number}" if web else "")
        parts.append(f"PR {hyperlink(pr_url, f'#{pr_number}')}")

    porcelain = run_git(root, ['status', '--porcelain'])
    if porcelain is not None:
        n = sum(1 for line in porcelain.splitlines() if line.strip())
        parts.append(f"📝 {n}")

    def divergence(ref):
        """(ahead, behind) of HEAD relative to ref, or None if unavailable."""
        counts = run_git(root, ['rev-list', '--left-right', '--count', f'{ref}...HEAD'])
        if counts and len(counts.split()) == 2:
            behind, ahead = counts.split()
            return ahead, behind
        return None

    base = next(
        (c for c in ('origin/develop', 'develop')
         if run_git(root, ['rev-parse', '--verify', '--quiet', c]) is not None),
        None,
    )
    if base:
        d = divergence(base)
        if d:
            parts.append(f"🔀 {base} ↑{d[0]} ↓{d[1]}")

    # Divergence vs the branch's tracked upstream (absent if HEAD has none).
    upstream = run_git(root, ['rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{upstream}'])
    if upstream:
        up = upstream.strip()
        d = divergence(up)
        if d:
            parts.append(f"🔀 {up} ↑{d[0]} ↓{d[1]}")

    return " | ".join(parts)


# Background subcommand: refresh the PR cache for one branch, then exit.
if len(sys.argv) >= 4 and sys.argv[1] == '--refresh-pr':
    refresh_pr(sys.argv[2], sys.argv[3])
    sys.exit(0)


try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    # Empty or malformed stdin (can happen during startup/transient refreshes).
    # Show a minimal line from the process CWD instead of a traceback / blank.
    cwd = os.getcwd()
    branch = read_git_branch(cwd)
    print(f"[?] 📁 {os.path.basename(cwd)}")
    if branch:
        print(f"🌿 {branch}")
    sys.exit(0)

model = data.get('model', {}).get('display_name', '?')
current_dir_full = data.get('workspace', {}).get('current_dir', '') or os.getcwd()
# Show the last two path components (e.g. "repos/celery-web-app", "celery-web-app/src").
_dir_parts = [p for p in current_dir_full.split(os.sep) if p]
current_dir = "/".join(_dir_parts[-2:]) if _dir_parts else current_dir_full

# Context usage
ctx = data.get('context_window', {})
used = ctx.get('used', 0)
total = ctx.get('total', 0)
pct = ctx.get('used_percentage', 0)

if total:
    context_str = f" | 🧠 {used:,}/{total:,} ({pct:.1f}%)"
else:
    context_str = f" | 🧠 {pct:.1f}%"

# Prefer git itself (walks up to the repo root, handles subdirs & worktrees);
# fall back to the file-based reader if git isn't available.
branch = ""
rev = run_git(current_dir_full, ['rev-parse', '--abbrev-ref', 'HEAD'])
if rev is not None:
    branch = rev.strip()
    if branch == 'HEAD':  # detached
        sha = run_git(current_dir_full, ['rev-parse', '--short', 'HEAD'])
        branch = sha.strip() if sha else ""
if not branch:
    branch = read_git_branch(current_dir_full)


def parse_reset(reset_at):
    """Parse resets_at — accepts unix timestamp (int/str) or ISO 8601 string."""
    if reset_at is None or reset_at == "":
        return None
    try:
        ts = float(reset_at)
        return datetime.fromtimestamp(ts)
    except (TypeError, ValueError):
        pass
    try:
        s = str(reset_at).replace('Z', '+00:00')
        return datetime.fromisoformat(s).astimezone()
    except (TypeError, ValueError):
        return None


def relative_day(target, now):
    """'Today' / 'Tomorrow' / 'in N days' / 'Yesterday' / 'N days ago'."""
    days = (target.date() - now.date()).days
    if days == 0:
        return "Today"
    if days == 1:
        return "Tomorrow"
    if days == -1:
        return "Yesterday"
    if days > 1:
        return f"in {days} days"
    return f"{abs(days)} days ago"


def format_rl(label, info, relative=False):
    if not info:
        return ""
    pct = info.get('used_percentage')
    if pct is None:
        return ""
    pct_i = int(round(float(pct)))
    reset_dt = parse_reset(info.get('resets_at'))
    if reset_dt is None:
        reset_phrase = "resets at ?"
    elif relative:
        reset_phrase = f"resets {relative_day(reset_dt, datetime.now())} at {reset_dt.strftime('%H:%M')}"
    else:
        reset_phrase = f"resets at {reset_dt.strftime('%H:%M')}"
    return f" | {label} {pct_i}% ({reset_phrase})"


rate_limits = data.get('rate_limits', {}) or {}
rl_5h = format_rl("5h", rate_limits.get('five_hour'))
rl_7d = format_rl("7d", rate_limits.get('seven_day'), relative=True)

print(f"[{model}] 📁 {current_dir}{context_str}{rl_5h}{rl_7d}")

status_line = git_status_line(current_dir_full, branch)
if status_line:
    print(status_line)
