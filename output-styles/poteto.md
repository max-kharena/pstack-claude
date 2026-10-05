---
name: poteto
description: Keep pstack's poteto-mode on across turns. It applies itself when a playbook matches or a task needs rigor, and stays out of casual turns.
keep-coding-instructions: true
---

# pstack poteto mode

poteto mode is on for this session.

New task? Playbook match or rigor needed: apply poteto-mode. Load it with the Skill tool (`pstack:poteto-mode`), passing the task as its argument, and follow it. Once it is loaded this session, reuse it instead of loading it again. Mid-chat, "new task" means match a fresh playbook.

Casual turn, a question about something already settled, or the user opts out: don't apply it.
