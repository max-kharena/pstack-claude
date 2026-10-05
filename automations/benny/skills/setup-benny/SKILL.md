---
name: setup-benny
description: Configure Benny and prepare its triage and repro automations. Use when installing Benny or changing its Slack, tracker, repository, routing, control, model, or budget settings.
disable-model-invocation: true
---

# Set up Benny

Benny ships as a dormant automation pack inside pstack. The plugin manifest exposes only pstack's normal skill root; this file and the two operational files are not slash skills.

The human enters setup by pointing Claude Code at the pack's `FOR_AGENTS.md`. The bootstrap flow copies the whole pack into the target repository, then reads this file directly at `.claude/automations/benny/skills/setup-benny/SKILL.md`.

Benny needs external configuration and two live Claude Code routines (cloud sessions on the user's claude.ai account).

Do not create or update a routine until the user explicitly asks. Never put a secret value in plugin files, prompts, or committed configuration.

## 1. Copy the pack and enable shared pstack skills

Do this before asking for Benny configuration and before creating any routine.

Ask which repository will run the automations. The source pack is the directory containing `FOR_AGENTS.md`. The destination is `<target-repository>/.claude/automations/benny/`.

Merge the entire source pack into the destination:

1. Create the destination when it is absent.
2. Copy every source file to the same relative path.
3. Preserve destination-only files. Never delete unrelated files during install or refresh.
4. Keep user-owned configuration, feature maps, and routing maps outside the destination. Never overwrite them.
5. When an existing source-managed file differs, inspect the diff and merge without discarding local edits. If ownership is ambiguous, stop and ask before replacing it.
6. Verify that the destination contains `FOR_AGENTS.md`, this setup file, both operational files, their references, and the templates.

If this file is already being read from the target destination, treat the copy as complete and run the same verification before continuing.

Add pstack to the target repository's `.claude/settings.json`. If the file or `.claude` directory does not exist, create it.

Merge this entry into the existing JSON or JSONC:

```json
{
	"extraKnownMarketplaces": {
		"pstack-claude": { "source": { "source": "github", "repo": "max-kharena/pstack-claude" } }
	},
	"enabledPlugins": { "pstack@pstack-claude": true }
}
```

Preserve every unrelated top-level setting, marketplace, and plugin entry. If `enabledPlugins` already names pstack, change only its value. Validate the file after editing it.

Start a fresh session rooted there and accept the plugin install prompt. Verify that these shared pstack skills resolve from project scope:

- `how`
- `why`
- `tdd`
- `unslop`
- `principle-separate-before-serializing-shared-state`
- `principle-minimize-reader-load`
- `principle-guard-the-context-window`
- `principle-sequence-verifiable-units`
- `principle-fix-root-causes`
- `principle-prove-it-works`

Do not count a skill loaded from the current session or a user-scoped plugin. The check must show that a fresh agent in the target repository receives pstack through project settings.

A routine runs in a cloud session that clones the repository, and Claude Code documents only that it uses skills committed to that clone. After the routine exists, prove the cloud path with **Run now** and a prompt that reads each shared skill above. If any does not resolve there, copy those pstack skill directories into the target repository's `.claude/skills/` and commit them, so the clone carries them.

If project-scoped plugin installation is unavailable or any shared dependency does not resolve, stop and explain the failure.

The Benny files are read directly from `.claude/automations/benny/`. Do not add that directory to a plugin manifest or expect its `SKILL.md` files to appear in the slash-skill list.

Tell the user that `.claude/settings.json`, `.claude/automations/benny/`, and any referenced secret-free configuration must be committed before either automation is enabled. Do not commit them unless the user asks.

Once this check passes, live automation prompts may read the committed operational files by their stable repository-relative paths. They must not embed a plugin cache path or copy the file contents.

## 2. Adapt the configuration

Open these copied examples:

- `../../templates/configuration.example.yaml`
- `../reproduce-and-fix-issues/references/feature-map.example.md`

Create user-owned copies outside `.claude/automations/benny/`. These are configuration files, not pack files. Example locations:

- Project config, such as `.claude/benny/configuration.yaml`
- Project feature map, such as `.claude/benny/feature-map.md`
- Project routing map, such as `.claude/benny/routing.md`
- User config, such as `~/.config/benny/configuration.yaml`
- User feature map, such as `~/.config/benny/feature-map.md`

Fill one feature-map section for every user-facing feature the automation may reproduce. Keep it at the user point of view. Do not freeze implementation details or current code paths in the map.

Do not edit the copied examples. Pack refreshes may update source-managed files after conflict review, but they must never touch the user-owned copies.

Prefer committed, secret-free files in the target repository when a fresh automation checkout must read them. Otherwise paraphrase the required values into the live prompt. Reference a repository file only after you confirm with `git` that the file is committed on the default branch the routine clones.

Use stable repository-relative paths for committed pack and configuration files. Never reference the plugin source directory or a plugin cache path from a live automation.

## 3. Fill the required choices

Ask for or confirm:

- Source Slack channel ID
- Optional operations or status channel ID
- Repository URL and default branch
- Triage identity or Slack user ID
- Issue tracker type, team, project, labels, and intake status
- Tracker adapter skill or MCP actions
- Optional routing map path
- Required control skill name
- Required user-facing feature-map path
- Status emoji strings
- Pull request URL format
- Polling and effort budgets
- Model slug for triage, repro, code work, and media review

The routine's own model comes from its model selector. Subagent models inside a run use Claude Code aliases (`opus`, `sonnet`, `fable`, `haiku`). Do not guess a full model ID and do not carry over a private default.

The source channel, triage identity, repository, tracker adapter, control skill, and feature map must be explicit. Fail setup if any required value stays ambiguous.

Use pstack's `unslop` skill on the final routine names and prompts before saving them.

## 4. Check integration capabilities

The triage automation needs:

- Read access to the configured source Slack channel and its threads
- Thread-reply access in that channel
- Attachment metadata and file download access when reports include media
- Search, read, create, and update access through the configured issue-tracker adapter

The repro automation needs:

- Read access to the source thread
- Thread-reply access in the source channel
- Optional post and edit access in the configured operations channel
- Repository read and history access
- A pull request action that can open a draft pull request
- The configured control-adapter skill

Prefer the routine's Slack connector for reads and posts. Include only the connectors Benny needs, because a routine uses every included connector without asking. The optional `BENNY_SLACK_BOT_TOKEN` may fill a narrow gap such as editing one operations status message or downloading an attachment. Store the value in a secret manager or environment, not in YAML.

Do not use undocumented integration endpoints.

## 5. Prepare the routing map

If the user wants reroutes or owner pings:

1. Copy `../triage-issue-reports/references/routing.example.md` outside `.claude/automations/benny/`.
2. Replace every placeholder with public or organization-local values.
3. Keep owner pings off by default.
4. Allow a ping only for a configured feature owner or a confirmed likely regression author.

If no routing map is configured, triage may classify a report but must not guess a destination or owner.

## 6. Verify the control adapter

Read `../reproduce-and-fix-issues/references/control-adapter.md` and the user's completed feature map.

Confirm that the named skill can:

- Bring up the target app
- Navigate every mapped feature through the real UI
- Exercise mapped states through declared adapter actions
- Inspect state without forcing the result
- Capture screenshots
- Start and stop a recording
- Clean up its processes and temporary data

If any capability is missing, leave the repro automation disabled. It must fail closed rather than claim a reproduction it did not perform.

## 7. Prepare the live routines

Ask whether this is first-time creation or configuration of existing routines.

Read `../../FOR_AGENTS.md` from the copied pack as the primary user-intent source for either path. Use it to understand the two triggers, tools, instructions, outcomes, and shared rules.

### Pick the runtime

Routines start on a schedule, an API call, or a GitHub event. None of these is a Slack trigger, so ask the user to pick one:

- **Scheduled poll (default).** An hourly routine (the minimum interval) polls the source channel through the Slack connector for new top-level reports and skips threads that already carry a Benny marker. No extra infrastructure. Reports wait up to an hour.
- **API trigger.** A relay the user already runs (a Slack app on the Events API, or a Slack workflow that can send an HTTP request) POSTs each new report's coordinates to the routine's `/fire` endpoint as `{"text": "<trigger JSON>"}`. Faster, but the user hosts the relay and stores the routine's bearer token in it, never in chat or the repository.

### First-time creation

Create one routine at a time.

For each routine:

1. Read the matching copied prompt template as secondary internal source material.
2. Turn `FOR_AGENTS.md`, the finished Benny configuration, the chosen runtime, and the template intent into a complete, self-contained routine prompt. A routine runs autonomously, so the prompt must say what success looks like.
3. Tell the prompt to read and follow its exact committed operational file under `.claude/automations/benny/`.
4. Use the stable repository-relative path, not a plugin source or cache path. Do not copy the operational file contents into the prompt.
5. Confirm with `git` that the copied pack and any referenced configuration files are committed on the default branch the routine clones.
6. Show the user the draft: name, prompt, repository, connectors, trigger, and model. Get approval.
7. Create it with `/schedule` for the scheduled runtime. For the API runtime, the user creates it at `https://claude.ai/code/routines`, then adds the API trigger and generates the token there, because the CLI cannot mint tokens. Keep connectors to Slack, the tracker, and what the control adapter needs.
8. Leave the routine paused until the thread-safety test in step 8 passes.

The triage routine's prompt, filled from configuration:

- Name `benny-triage`.
- Read and follow `.claude/automations/benny/skills/triage-issue-reports/SKILL.md` for every report.
- The trigger: the scheduled poll step from the template, or the `<routine-fire-payload>` coordinates.
- Read the triggering thread and reply only inside it.
- Use the configured issue-tracker connector.
- Classify, inspect evidence, trace cause, dedupe, and create only clear new bugs.
- End one thread-only verdict with the configured `[benny:bug]`, `[benny:performance]`, or `[benny:other]` marker and optional tracker URL.
- Never post a source-channel root message.

After the triage routine passes its test, the repro and fix routine's prompt:

- Name `benny-reproduce`.
- Read and follow `.claude/automations/benny/skills/reproduce-and-fix-issues/SKILL.md` for every report.
- The same trigger runtime, polling for reports whose thread already carries a trusted triage marker and no repro status yet.
- Use the configured repository and default branch. Routines push to `claude/`-prefixed branches unless the prompt names another, which suits a draft pull request.
- Read the source thread and reply only inside it.
- Include pull request creation and the configured tracker, control-adapter, and feature-map requirements. Paraphrase mapped user paths and states unless the feature map is committed in the same repository.
- Wait for a trusted triage marker before acting.
- Reproduce the exact symptom twice through the mapped real UI and capture evidence.
- Verify an existing fix without authoring over it.
- Attempt an optional bounded fix only after confirmed repro, then open a draft pull request when proof and checks pass.
- Never post a source-channel root message.

### Existing routines

Finish configuration, routing, control-adapter, and feature-map validation. Then update each routine with `/schedule update`, or give the user this checklist for its edit page at `https://claude.ai/code/routines`.

For the existing triage routine, update:

- Name
- Direct instruction to read `.claude/automations/benny/skills/triage-issue-reports/SKILL.md`
- Trigger runtime and source channel
- Slack connector and issue-tracker connector
- Paraphrased triage instructions, thread-only rule, and Benny verdict markers

For the existing repro routine, update:

- Name
- Direct instruction to read `.claude/automations/benny/skills/reproduce-and-fix-issues/SKILL.md`
- Matching trigger runtime and source channel
- Repository and default branch
- Slack, tracker, and pull request access
- Control-adapter and feature-map requirements
- Paraphrased marker wait, evidence, verification, and bounded-fix instructions

Do not create replacements or duplicates.

### Creation boundary

Never call an undocumented routines endpoint. Create and edit routines only through `/schedule` or the routines page. Never put the API token in a prompt, a committed file, or chat.

Do not enable either routine until the thread-safety test passes.

## 8. Test thread safety

Use a test channel or a harmless test report.

Before testing, confirm that the target repository's `.claude/settings.json`, `.claude/automations/benny/`, and every referenced secret-free configuration file are committed on the branch used by the automation checkout. Confirm that both live prompts point at their exact committed operational files. If any check fails, stop. Tell the user that the routine cannot be enabled yet.

Verify:

1. Triage stores the root `thread_ts` and posts exactly one verdict as a reply.
2. The verdict contains one configured marker.
3. Repro accepts the marker only from the configured triage identity.
4. Repro keeps the same immutable source coordinates.
5. No source-channel root message appears.
6. A delegated worker cannot use any Slack write action.
7. Missing coordinates, a deleted parent, or a failed preflight produces no post and no tracker issue.

Enable normal traffic only after all seven checks pass.
