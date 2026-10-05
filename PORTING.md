# Porting pstack from Cursor to Claude Code

This file records how upstream pstack ([cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack), commit `00b52d9`, pstack 0.15.11) maps onto Claude Code, why each judgment call went the way it did, and what was verified. `.upstream/SOURCE` holds the exact upstream commit the port tracks.

## Why a separate repository

A Claude Code plugin installs from a marketplace, and a marketplace is a git repository with `.claude-plugin/marketplace.json`. This repository is both: the marketplace lists one plugin whose source is the repository root. That buys three things a folder inside another project cannot.

- **User-scope install.** `/plugin install pstack@pstack-claude` makes pstack available in every project, the way upstream is available in every Cursor workspace.
- **Team install.** A project commits `extraKnownMarketplaces` and `enabledPlugins` to `.claude/settings.json`, and every teammate gets the same version.
- **Upstream tracking.** The `upstream` branch mirrors cursor/plugins verbatim, so `scripts/sync-upstream.sh` merges new upstream work and git replays the port's edits. A copied folder loses that lineage.

## What was ported

| Upstream | Count | Port |
|---|---|---|
| Skills | 51 | All 51, plus nine from cursor-team-kit (`deslop`, `control-cli`, `control-ui`, which pstack routes to, and `fix-ci`, `fix-merge-conflicts`, `get-pr-comments`, `make-pr-easy-to-review`, `thermo-nuclear-code-quality-review`, `what-did-i-get-done`), plus `babysit`, written for this port. 61 total. |
| Playbooks under `poteto-mode` | 23 | All 23. |
| Subagents | 2 | `poteto-agent`, `comment-sicko`, the vendored `thermo-nuclear-code-quality-review`, plus a new `reader` (see below). |
| Scripts | `watch-pr`, `orch`, `check-plan.mjs`, `worktree-audit.sh`, `log.sh` | All. Only `worktree-audit.sh` changed in behavior. |
| Guide | 10 pages, 6 images | All, with install and mode sections rewritten. |
| benny automation pack | 3 operational skills, templates | All, re-targeted at Claude Code routines. |
| Custom mode (`mode: true`, `reminder`) | 1 | The `pstack:poteto` output style. |

## Mapping

| Cursor construct | Claude Code construct | Where |
|---|---|---|
| `.cursor-plugin/plugin.json` | `.claude-plugin/plugin.json` plus `.claude-plugin/marketplace.json` | repository root |
| `/add-plugin pstack` | `/plugin marketplace add max-kharena/pstack-claude`, then `/plugin install pstack@pstack-claude` | README, guide, poteto-help |
| `.cursor/settings.json` `plugins.pstack.enabled` | `.claude/settings.json` `extraKnownMarketplaces` + `enabledPlugins` | README, guide, benny |
| `Task` tool | `Agent` tool | everywhere (`scripts/port.py`) |
| `subagent_type: generalPurpose` | `general-purpose` for work that edits | everywhere |
| `readonly: true`, and `readonly: false` kept only for MCP access | `subagent_type: pstack:reader`, which cannot edit files but keeps MCP tools | how, why, interrogate, arena, reflect, recall, show-me-your-work |
| `subagent_type: "poteto-agent"` | `"pstack:poteto-agent"` | poteto-mode, playbooks, README |
| `subagent_type: "Comment Sicko"` | `"pstack:comment-sicko"` (agent names must be kebab-case) | no-comments |
| `is_background: true` | `background: true` | poteto-agent |
| `environment: "cloud"` / `"local"` | `isolation: "remote"` where the Agent tool offers it, else `isolation: "worktree"` | swarm, orchestrate, autopilot, shipping, multi-phase plan |
| `cloud_base_branch` | the worker's brief says to fetch and check out the branch | swarm |
| resume / message a subagent | `SendMessage` | poteto-mode, orchestrate |
| `AskQuestion` (4-6 options, `allow_multiple`) | `AskUserQuestion` (up to 4 options, `multiSelect`) | setup-pstack, automate-me, poteto-mode |
| todolist | the task list (TaskCreate / TaskUpdate, or TodoWrite where task tools are off) | poteto-mode, arena, swarm, architect |
| `~/.cursor/rules/pstack-models.mdc` (`alwaysApply: true`) | `~/.claude/rules/pstack-models.md` (a user rule with no `paths` loads in every session) | setup-pstack and every routed skill |
| model slugs `claude-opus-5-5-max`, `gpt-5.6-sol-max`, `grok-4.7-xhigh-fast` | `opus`, `sonnet`, `fable` (see Models) | setup-pstack, model-routing, routed skills, playbooks |
| `inherit-parent` / `auto` | `inherit` (omit the Agent `model`) | same |
| reasoning budget (effort ladder per slug) | budget picks model tiers. Claude Code sets effort per session (`/effort`), not per Agent call | setup-pstack |
| transcripts `~/.cursor/projects/<slug>/agent-transcripts/<id>/<id>.jsonl` | `~/.claude/projects/<slug>/<session-id>.jsonl`, subagents in `<session-id>/subagents/`. The slug turns every character other than a letter, digit, or `-` into `-` | reflect, recall, automate-me, show-me-your-work, session pickup, eval, worktree-audit.sh |
| "the system prompt names the transcript directory" | `${CLAUDE_SESSION_ID}` names the exact file | reflect, show-me-your-work, recall, eval |
| `message.content[0].text` first-line check | `type: "user"` lines, `message.content` string or blocks; skill use shows as `Skill` tool calls and `<command-name>` tags | reflect and its reviewers |
| `mcps/` directory, available-tools map | MCP tools named `mcp__<server>__<tool>`, including deferred ones, loaded with ToolSearch | why |
| Custom Mode (Option+Enter) with `reminder` | `/output-style pstack:poteto`, or `claude --agent pstack:poteto-agent` | output-styles/poteto.md, README, guide, poteto-help |
| Cursor `/loop` | Claude Code `/loop` | unchanged |
| Cursor `create-skill` | Anthropic's `skill-creator` skill, else the Authoring a skill playbook plus `claude plugin validate --strict` | reflect, automate-me, authoring-a-skill, poteto-mode |
| Cursor built-in `/babysit` | `/pstack:babysit`, a thin skill that runs the Babysit playbook outside poteto-mode | skills/babysit, poteto-mode, poteto-help |
| cursor-team-kit skills and agent | vendored into `skills/` and `agents/`, listed in `scripts/vendor.list` | poteto-mode, playbooks, babysit |
| thermo-nuclear agent's `shell` and `explore` subagents | the parent gathers the diff with Bash and the files with Read | agents/thermo-nuclear-code-quality-review.md |
| Cursor agent store (path in the system prompt) | `~/.claude/pstack/orchestrate/<slug>/` exported as `ORCH_STORE` | orchestrate |
| Cursor dashboard for cloud agents | `claude.ai/code` sessions | orchestrate |
| Grok Bot routine, `update_state`, `SendToUser` secret card, `api2.cursor.sh` webhook | Claude Code routine API trigger (`/fire`, bearer token, `<routine-fire-payload>`), token written by the user with `read -s` | make-bot-ui |
| Cursor Automations with Slack triggers, `/automate`, Automations editor | Claude Code routines: hourly poll by default, API trigger via a relay, `/schedule` or claude.ai/code/routines | benny |
| `.cursor/skills/`, `~/.cursor/skills/`, `.cursor/worktrees/` | `.claude/skills/`, `~/.claude/skills/`, `.claude/worktrees/` | everywhere |
| skill name `Poteto Mode`, `Make Bot UI` | `poteto-mode`, `make-bot-ui` | frontmatter |
| frontmatter `mode`, `icon`, `color`, `reminder` | dropped (no Claude Code skill equivalent) | poteto-mode |

## Judgment calls

**Models.** Upstream panels mix three vendors. Every Claude Code Agent seat is a Claude model, so the defaults map by role: judgment and prose to Opus (upstream Opus), code delegates and bulk reading to Sonnet (upstream's fast Grok), and the third panel seat to Fable, Claude's fast tier, which plays the part upstream's fast Grok seat plays. Panels lose vendor diversity. The `cli:<name>` seat in [`model-routing.md`](skills/setup-pstack/references/model-routing.md) restores it for anyone with another vendor's CLI. `/pstack:setup-pstack` only writes a CLI command it has run.

**One routing contract.** Upstream repeats the model-resolution paragraph in seven skills. The port keeps a one-line pointer in each and puts the rules in one file, so a change lands once.

**`pstack:reader`.** Cursor's `readonly` flag strips MCP tools, so upstream sets `readonly: false` on why investigators and reflect reviewers only to keep MCP access. A plugin agent with `disallowedTools: Edit, Write, NotebookEdit, Agent` is read-only and keeps MCP, which is what upstream wanted in both places.

**poteto-mode is model-invocable.** Upstream marks every skill `disable-model-invocation`. Claude Code blocks such a skill from the Skill tool, and output styles do not substitute `${CLAUDE_PLUGIN_ROOT}`. So the `pstack:poteto` style could reach poteto-mode only through a file search that triggers permission prompts. Letting the model load poteto-mode fixes that. Its description triggers only on poteto's name or style, and the output style plays the role of Cursor's per-turn mode reminder. Every other skill keeps upstream's flag.

**Reaching hidden skills.** With `disable-model-invocation`, the Skill tool cannot load a pstack skill, and upstream already reads skills as files. The port makes the path explicit: `${CLAUDE_SKILL_DIR}/../<name>/SKILL.md` inside skills, and `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md` inside agents. Both are substituted at load time. Playbooks and references are read as plain files, so poteto-mode tells the agent what the literal `${CLAUDE_SKILL_DIR}` means there.

**benny.** Routines have no Slack trigger. An hourly poll that skips threads already carrying a Benny marker needs no infrastructure and is safe to rerun. The API trigger is documented for teams that already run a Slack relay. Routines document only skills committed to the cloned repository, so setup proves the plugin loads in the cloud with **Run now** and falls back to committing the shared skills.

**`/babysit`.** Cursor has a built-in `/babysit` that poteto-mode tells agents not to use. Claude Code has none, so a user outside poteto-mode had no entry point for PR babysitting. The port adds a thin `babysit` skill that runs the upstream Babysit playbook, so upstream edits to the playbook reach it on the next sync. It is model-invocable like Cursor's built-in, falls back to `gh` when Bun is missing, and points at the vendored `fix-ci` and `get-pr-comments` helpers. It keeps the playbook's rule that a conflict is reported, not resolved.

**Kept as upstream.** Origin support (it is gated on `command -v origin`), the watch-pr script's Cursor Bugbot detection (other review bots are treated as human reviewers, which is the conservative side), and the poteto voice in every skill.

**Fixed while porting.** `worktree-audit.sh` now finds Claude Code transcripts, including the separate project folder each worktree session gets, and falls back to `grep` when `rg` is only a shell function (in that case upstream silently reported no chats). The multi-phase plan's `check-plan.mjs` path was relative to the cursor/plugins repository root and broke once installed. It now resolves from the skill folder.

## Not ported

- **dyl-stack**, upstream's layer over pstack. It can be ported as its own plugin that declares `"dependencies": ["pstack@pstack-claude"]`.
- The rest of cursor-team-kit (`check-compiler-errors`, `loop-on-ci`, `new-branch-and-pr`, `pr-review-canvas`, `review-and-ship`, `run-smoke-tests`, `verify-this`, `weekly-review`, `workflow-from-chats`, and the `ci-watcher` agent). Add a path to `scripts/vendor.list` and run `scripts/sync-upstream.sh --force <pinned sha>` to vendor one.

## Verification

Run on Claude Code 2.1.267, macOS.

| Check | Result |
|---|---|
| `claude plugin validate --strict .` (marketplace, 54 skills, 3 agents) | pass |
| `scripts/port.py --check` (mechanical port is idempotent) | pass |
| `scripts/lint-port.sh` (no Cursor-only construct left in shipped files) | pass |
| `scripts/check-refs.py` (every link, skill name, and `subagent_type` resolves; 188 skill-to-skill edges) | pass |
| Install from the marketplace at local scope, then `claude plugin details` | 54 skills, 3 agents |
| Model context in a fresh session | 5 pstack skills listed (control-cli, control-ui, deslop, poteto-mode, setup-pstack). The rest stay slash-only as upstream. 3 agents spawnable |
| Probe plugin | `${CLAUDE_SKILL_DIR}`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_PLUGIN_ROOT}` substitute in skills; `${CLAUDE_PLUGIN_ROOT}` substitutes in agents; output styles need the `plugin:style` name and get no substitution |
| `pstack:poteto-agent` spawn | read `skills/poteto-mode/SKILL.md` through `${CLAUDE_PLUGIN_ROOT}` |
| `pstack:reader` spawn | no Edit, Write, NotebookEdit, or Agent; Bash and MCP present |
| `pstack:poteto` output style | casual turn untouched; a bug report loaded `pstack:poteto-mode` through the Skill tool and copied the Bug fix steps |
| `claude --agent pstack:poteto-agent` | read poteto-mode first |
| `/pstack:how` end to end | read `model-routing.md` and the user rule, spawned `pstack:reader` with `model: opus`, correct answer, $0.70 |
| `worktree-audit.sh` on a real repository | found the worktree's last chat in Claude Code transcripts |

Not exercised: the Bun scripts (`watch-pr`, `orch`), which are byte-identical to upstream and need Bun; a `cli:` seat (no external CLI on the test machine); routines for `make-bot-ui` and benny (research preview, needs a claude.ai account action); the `/output-style pstack:poteto` command form (needs Claude Code 2.1.269+, the settings form was tested); the model-rejection fallback.

The details command projects about 4.7K always-on tokens because it counts every skill description. Only the model-invocable skills and the agents reach context, roughly 0.7K tokens.

## Syncing with upstream

```bash
scripts/sync-upstream.sh
```

The script refreshes the `upstream` branch in a temporary worktree, prints the upstream diff for the files this port owns by hand (README, setup-pstack, poteto-help, make-bot-ui, agents, benny's `FOR_AGENTS.md`), merges, re-runs `scripts/port.py`, and runs the three checks. A residue the linter flags is a new Cursor-ism. Map it with the table above, and add a rule to `scripts/port.py` when the rewrite is mechanical.
