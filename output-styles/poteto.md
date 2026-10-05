---
name: poteto
description: Keep pstack's poteto-mode on across turns. It applies itself when a playbook matches or a task needs rigor, and stays out of casual turns.
keep-coding-instructions: true
---

# pstack poteto mode

poteto mode is on for this session.

New task? Playbook match or rigor needed: apply poteto-mode. Read `${CLAUDE_PLUGIN_ROOT}/skills/poteto-mode/SKILL.md` in full, then follow it. If that path does not resolve, read the newest match of `~/.claude/plugins/cache/*/pstack/*/skills/poteto-mode/SKILL.md`. Mid-chat, "new task" means match a fresh playbook.

Casual turn, a question about something already settled, or the user opts out: don't apply it.
