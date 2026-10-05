---
name: setup-pstack
description: Configure which models pstack uses per role and at what budget. Detects the models your Claude Code session can spawn, plus optional external CLI reviewers, and writes a user rule that overrides the skill defaults. Use for /setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.
---

# Setup pstack

Write `~/.claude/rules/pstack-models.md`, a user rule that sets pstack's model per role. Claude Code loads every file in `~/.claude/rules/` that has no `paths` frontmatter into every session, so every pstack skill sees it. [`references/model-routing.md`](references/model-routing.md) says how skills turn each line into an Agent tool call.

## Steps

### 1. Detect available models

The Agent tool's `model` parameter lists the aliases this session can spawn. Read them from its schema, usually `opus`, `sonnet`, `fable`, and `haiku`. That is the dependable source. `inherit` is always valid. A full model ID works too, but write one only when the user names it.

Then look for external CLI reviewers. Run `command -v codex gemini cursor-agent 2>/dev/null`. For each CLI found, offer it once as an optional panel seat. Before you write one, find the non-interactive invocation in its `--help` that reads a prompt on stdin and prints the answer, and prove it works: `printf 'Reply with the single word ok.' | <command>` must print `ok` within 60 seconds. Never write a CLI command you have not run.

### 2. Load current state

The default role-to-model mapping is the `max` column in step 3. If `~/.claude/rules/pstack-models.md` already exists, read it and treat its `# budget` line, its role values, and its `cli` lines as the current choices. Otherwise start from the defaults. A line whose role is not in step 3 is from a retired role. Drop it.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** Use AskUserQuestion with these four options and these exact labels, and name the current budget when the rule records one.

- `max — opus for judgment, sonnet for code`
- `balanced — sonnet for most roles, opus for the hardest calls`
- `economy — sonnet for judgment, fable for code and bulk roles`
- `session — every role runs on the session model`

**(b) Apply it.** Build the working table from the budget's column. On a re-run, keep any role the user moved off the default, including `cli:` entries.

| Role | max | balanced | economy | session |
|---|---|---|---|---|
| `feature, refactoring` | sonnet | sonnet | fable | inherit |
| `bug-fix` | sonnet | sonnet | fable | inherit |
| `perf-issue` | sonnet | sonnet | fable | inherit |
| `hillclimb` | sonnet | sonnet | fable | inherit |
| `judgment and prose` | opus | sonnet | sonnet | inherit |
| `hardest tasks` | opus | opus | sonnet | inherit |
| `how explorer` | sonnet | sonnet | fable | inherit |
| `how explainer` | opus | sonnet | sonnet | inherit |
| `why investigators` | sonnet | sonnet | fable | inherit |
| `why synthesizer` | opus | opus | sonnet | inherit |
| `reflect tooling` | sonnet | sonnet | fable | inherit |
| `reflect judgment, divergent, synthesizer` | opus | sonnet | sonnet | inherit |
| `arena runners` | opus, sonnet, fable | opus, sonnet | sonnet, fable | inherit, inherit |
| `arena cross-judge pool` | opus, sonnet, fable | opus, sonnet | sonnet, fable | inherit |
| `swarm workers` | sonnet | sonnet | fable | inherit |
| `architect runners` | opus, sonnet, fable | opus, sonnet | sonnet, fable | inherit, inherit |
| `interrogate reviewers` | opus, sonnet, fable | opus, sonnet | sonnet, fable | inherit, inherit |

Reasoning effort is not part of the budget. Claude Code sets effort per session with `/effort`, so say that once if the user asks about reasoning depth.

**(c) Show the roles and confirm.** Show every role with its model, marking any value not in the detected set as needing a choice. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles, offering the detected models, `inherit` (this role runs on the session model), and any CLI that passed step 1 as `cli:<name>`. Use AskUserQuestion. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one subagent runs per entry, `inherit` and `cli:` entries included, so the list length sets the count. A `cli:` seat is the only way to put a non-Claude model on a panel. `arena cross-judge pool` is also a list, but Arena selects one value from it whose model differs from the session's when possible. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

### 4. Validate

Every model written must be in the detected set or be `inherit`. Every `cli:<name>` entry must have a matching `cli <name>:` line that passed the step 1 test. If a chosen value fails, stop and ask again.

### 5. Write the rule

Write `~/.claude/rules/pstack-models.md` with a `# budget` line and one line per role, using the same labels poteto-mode uses. Add one `cli <name>: <command>` line per CLI seat in use. No frontmatter, so the rule always loads. Overwrite the whole file so re-runs stay idempotent. Shape:

```
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# Values: opus, sonnet, fable, haiku, a full model ID, inherit (omit the Agent `model`, run on the session model), or cli:<name>.
# Routing rules: the pstack plugin's skills/setup-pstack/references/model-routing.md.
# budget: max
feature, refactoring: sonnet
bug-fix: sonnet
perf-issue: sonnet
hillclimb: sonnet
judgment and prose: opus
hardest tasks: opus
how explorer: sonnet
how explainer: opus
why investigators: sonnet
why synthesizer: opus
reflect tooling: sonnet
reflect judgment, divergent, synthesizer: opus
arena runners: opus, sonnet, fable
arena cross-judge pool: opus, sonnet, fable
swarm workers: sonnet
architect runners: opus, sonnet, fable
interrogate reviewers: opus, sonnet, fable
```

With a CLI seat, a panel line reads `interrogate reviewers: opus, sonnet, cli:codex` and the file adds `cli codex: <the tested command>`.

### 6. Confirm

Tell the user the rule was written and that Claude Code loads it at session start, so it applies to new sessions. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill under `.claude/skills/`, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /pstack:create-verification-skill." On yes, read and follow `../create-verification-skill/SKILL.md` next to this skill. On no, move on without pushing.
