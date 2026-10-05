#!/usr/bin/env python3
"""Mechanical Cursor -> Claude Code port for pstack.

Idempotent: running it twice changes nothing the second time. It owns only
mechanical rewrites (paths, tool names, frontmatter keys, vendored skill
placement). Semantic rewrites live as ordinary commits on `main`, so an
upstream merge replays them through git instead of through this script.

Usage: scripts/port.py [--check]
  --check  exit 1 if any file would change (CI guard after a sync merge)
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".upstream", "scripts", "node_modules", "vendor"}
SKIP_FILES = {"PORTING.md", "LICENSE", "README.md"}  # hand-owned
TEXT_SUFFIXES = {".md", ".sh", ".yaml", ".tsv"}

# (pattern, replacement). Order matters: specific before general.
RULES = [
    # config rule: Cursor always-applied .mdc rule -> Claude Code user rule
    (r"~/\.cursor/rules/pstack-models\.mdc", "~/.claude/rules/pstack-models.md"),
    (r"pstack-models\.mdc", "pstack-models.md"),
    # paths
    (r"~/\.cursor/projects/\*/", "~/.claude/projects/*/"),
    (r"~/\.cursor/skills/", "~/.claude/skills/"),
    (r"~/\.cursor/plugins/", "~/.claude/plugins/"),
    (r"(?<![\w~])\.cursor/(skills|worktrees|automations|benny)/", r".claude/\1/"),
    (r"(?<![\w~])\.cursor/automations/benny\b", ".claude/automations/benny"),
    # subagent types
    (r'subagent_type: "poteto-agent"', 'subagent_type: "pstack:poteto-agent"'),
    (r'subagent_type: "Comment Sicko"', 'subagent_type: "pstack:comment-sicko"'),
    (r"\bgeneralPurpose\b", "general-purpose"),
    # tools
    (r"`Task`", "`Agent`"),
    (r"\bTask (tool|calls?|subagents?|schema)\b", r"Agent \1"),
    (r"\bAskQuestion\b", "AskUserQuestion"),
    (r"`allow_multiple: true`", "`multiSelect: true`"),
    (r"\btodolist\b", "todo list"),
    # built-ins that exist in both products
    (r"Cursor's `/loop` command", "Claude Code's `/loop` command"),
    (r"\bCursor restart\b", "Claude Code restart"),
]

# Skill/agent frontmatter keys Cursor reads and Claude Code does not.
DROP_SKILL_KEYS = {"mode", "icon", "color", "reminder"}
RENAME_NAMES = {"Poteto Mode": "poteto-mode", "Make Bot UI": "make-bot-ui", "Comment Sicko": "comment-sicko"}

VENDORED = ["deslop", "control-ui", "control-cli"]


def iter_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS or (len(rel.parts) == 1 and rel.name in SKIP_FILES):
            continue
        yield path


def fix_frontmatter(text, is_agent):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return text
    lines, out = m.group(1).split("\n"), []
    for line in lines:
        key = line.split(":", 1)[0].strip() if re.match(r"^[A-Za-z_-]+:", line) else None
        if key == "name":
            value = line.split(":", 1)[1].strip()
            line = f"name: {RENAME_NAMES.get(value, value)}"
        elif key == "is_background":
            line = line.replace("is_background", "background", 1)
        elif key in DROP_SKILL_KEYS and not is_agent:
            continue
        out.append(line)
    return "---\n" + "\n".join(out) + "\n---\n" + text[m.end():]


def place_vendored(check):
    """Move cursor-team-kit skills pstack depends on into skills/.

    A move, not a copy: git rename detection then carries later upstream
    edits to vendor/... into skills/... during a sync merge.
    """
    changed = []
    for name in VENDORED:
        src = ROOT / "vendor/cursor-team-kit/skills" / name
        dst = ROOT / "skills" / name
        if not src.exists():
            continue
        if dst.exists():
            sys.exit(f"both {src.relative_to(ROOT)} and skills/{name} exist; merge by hand, then delete the vendor copy")
        changed.append(f"skills/{name} (moved from vendor)")
        if not check:
            shutil.move(str(src), str(dst))
    return changed


def main():
    check = "--check" in sys.argv
    changed = place_vendored(check)
    for path in iter_files():
        before = path.read_text()
        after = before
        for pattern, repl in RULES:
            after = re.sub(pattern, repl, after)
        if path.name == "SKILL.md" or path.parent.name == "agents":
            after = fix_frontmatter(after, is_agent=path.parent.name == "agents")
        if after != before:
            changed.append(str(path.relative_to(ROOT)))
            if not check:
                path.write_text(after)
    for c in changed:
        print(("would change " if check else "changed ") + c)
    sys.exit(1 if check and changed else 0)


if __name__ == "__main__":
    main()
