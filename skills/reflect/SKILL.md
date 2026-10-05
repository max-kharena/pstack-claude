---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.
disable-model-invocation: true
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

## When to invoke

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## Process

### 1. Locate the active transcript

The parent finds its own transcript file before fanning out. Claude Code writes it to `~/.claude/projects/<slug>/<session-id>.jsonl`, and this session's ID is `${CLAUDE_SESSION_ID}`. Listing that one file name reads no other chat:

```bash
ls ~/.claude/projects/*/${CLAUDE_SESSION_ID}.jsonl ~/.claude/projects/*/${CLAUDE_SESSION_ID}/subagents/*.jsonl 2>/dev/null
```

Two transcript layouts: the session (`<project>/<session-id>.jsonl`) and its subagents (`<project>/<session-id>/subagents/agent-<id>.jsonl`). Each line is one JSON event. `type` is `user`, `assistant`, `attachment`, or a bookkeeping type, and `message.content` is a string or a list of `text`, `tool_use` (`name`, `input`), and `tool_result` blocks.

If the session ID did not resolve, list `ls -t ~/.claude/projects/<slug>/*.jsonl | head -10`, where `<slug>` is the session's starting directory with every character other than a letter, digit, or `-` turned into `-` (`/Users/you/proj` becomes `-Users-you-proj`). For each candidate, check that its first `type: "user"` line's `message.content` contains the conversation's opening user prompt. Do not glob across `~/.claude/projects/*/` for anything else. That crosses project boundaries and reads private chats from unrelated projects. If no path resolves, write a tight digest of the session and pass that instead.

### 2. Spawn three reviewers in parallel

One message, three `Agent` calls, `subagent_type: pstack:reader`, with `model` set as below. Reviewers need MCP access for context lookups (tickets, chat threads, observability traces referenced in the transcript), and the reader keeps MCP tools while it cannot edit files.

Each reviewer and the synthesizer name a role line in the `~/.claude/rules/pstack-models.md` rule and a default. Resolve it per `${CLAUDE_SKILL_DIR}/../setup-pstack/references/model-routing.md`: the line's value, or the default if the rule or the line is missing. Omit `model` for `inherit`. If the Agent tool rejects a model, step down a tier and say so.

| Lens | Role line | Default `model` | Prompt template |
|---|---|---|---|
| Judgment | `reflect judgment, divergent, synthesizer` | `opus` | `references/judgment-reviewer.md` |
| Tooling | `reflect tooling` | `sonnet` | `references/tooling-reviewer.md` |
| Divergent | `reflect judgment, divergent, synthesizer` | `opus` | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in the `Agent` response body.

### 3. Synthesize

One `Agent` call, `subagent_type: pstack:reader`, with `model` from the `reflect judgment, divergent, synthesizer` line (default `opus`). The synthesizer's quality check includes spot-verifying citations, which can require MCP access, and the reader keeps it. Use `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. The synthesizer returns a structured Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the synthesizer's Accepted list. For any item that would be enforced more reliably by a lint rule, script, metadata flag, or runtime check, move it from Accepted to Backlog. See the **encode-lessons-in-structure** principle skill.

### 5. Apply

Before applying any Accepted edit, present the synthesizer's full Accepted/Rejected/Backlog output to the user and wait for explicit approval. The user picks which subset to apply and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

Backlog items file to whatever devex / backlog tracker your team uses automatically. Only the Accepted list waits for approval.

For each approved Accepted item, follow the Routing field exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): parent does directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): hand to the `skill-creator` skill and run its draft / test / iterate loop. Without it, follow the Authoring a skill playbook (`${CLAUDE_SKILL_DIR}/../poteto-mode/playbooks/authoring-a-skill.md`).
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): hand to `skill-creator` and run its description-optimization loop.
- `new skill via skill-creator: <kebab-name>`: hand creation to `skill-creator`. Do not invent the shape ad hoc.

Run `claude plugin validate --strict <dir>` on the directory of every touched skill before declaring done.

### 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
