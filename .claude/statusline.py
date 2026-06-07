#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime

data = json.load(sys.stdin)

model = data['model']['display_name']
current_dir = os.path.basename(data['workspace']['current_dir'])

# Context usage
ctx = data.get('context_window', {})
used = ctx.get('used', 0)
total = ctx.get('total', 0)
pct = ctx.get('used_percentage', 0)

if total:
    context_str = f" | 🧠 {used:,}/{total:,} ({pct:.1f}%)"
else:
    context_str = f" | 🧠 {pct:.1f}%"

# Git branch
git_branch = ""
if os.path.exists('.git'):
    try:
        with open('.git/HEAD', 'r') as f:
            ref = f.read().strip()
            if ref.startswith('ref: refs/heads/'):
                git_branch = f" | 🌿 {ref.replace('ref: refs/heads/', '')}"
    except:
        pass


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


def format_rl(label, info, show_weekday=False):
    if not info:
        return ""
    pct = info.get('used_percentage')
    if pct is None:
        return ""
    pct_i = int(round(float(pct)))
    reset_dt = parse_reset(info.get('resets_at'))
    fmt = "%a %-I:%M %p" if show_weekday else "%-I:%M %p"
    reset_str = reset_dt.strftime(fmt) if reset_dt else "?"
    return f" | {label} {pct_i}% (resets at {reset_str})"


rate_limits = data.get('rate_limits', {}) or {}
rl_5h = format_rl("5h", rate_limits.get('five_hour'))
rl_7d = format_rl("7d", rate_limits.get('seven_day'), show_weekday=True)

print(f"[{model}] 📁 {current_dir}{git_branch}{context_str}{rl_5h}{rl_7d}")
