# Model routing

Every pstack spawn names a role and a default model. This file is the one place that says how a role becomes an Agent tool call in Claude Code. Skills point here instead of restating it.

## Resolve the role

1. Find the role's line in `~/.claude/rules/pstack-models.md`. Claude Code loads that user rule into every session, so it is usually already in context. If you can't see it, Read the file. No file or no line means the skill's default.
2. Map the value to the Agent tool call.
   - `opus`, `sonnet`, `fable`, `haiku`, or a full model ID: pass it as `model`.
   - `inherit`: omit `model`. The subagent runs on the session's model.
   - `cli:<name>`: an external CLI seat. See below.
3. A panel role (arena runners, arena cross-judge pool, architect runners, interrogate reviewers) is a comma-separated list. Spawn one subagent per entry. `inherit` and `cli:` entries count toward the list length, so the list length sets the panel size.

## When a model is rejected

If the Agent tool rejects a value, run that seat one tier down on `opus` > `sonnet` > `fable` > `haiku` and say so in the reply. If it rejects every tier, omit `model`. Never block the work on a model choice, and never treat `inherit` or a `cli:` entry as a rejected model.

## Model diversity

Upstream pstack mixes model families (Claude, GPT, Grok) in its panels. Inside Claude Code every Agent seat is a Claude model, so diversity comes from tiers: Opus for judgment, Sonnet for code and balanced review, Fable for a fast, differently-tuned third opinion. When a skill asks for "a different model family from the parent's", pick a seat whose model differs from the session's. A `cli:` seat is the only way to get a different vendor.

## External CLI seats

A `cli:<name>` entry runs a non-Claude model through a CLI that reads a prompt on stdin and prints the answer on stdout. The rule's `cli <name>:` line holds the exact command, which `/setup-pstack` tested before it wrote it.

To run a CLI seat:

1. Write the seat's filled prompt to a temp file, for example `/tmp/pstack-<skill>-<seat>.md`.
2. Spawn a `pstack:reader` subagent with `model: haiku`. Its brief: run `<command> < <prompt file>` from the repository root with a 15-minute timeout, then return stdout verbatim. Do not summarize, edit, or add to it.
3. Label the seat by the CLI name (`cli:codex`), not by a Claude model, everywhere the skill reports which model raised a finding.

A CLI seat that fails or times out drops out like any other seat. Proceed with N-1 and note the dropout.

## Reasoning effort

Claude Code sets reasoning effort per session (`/effort`) or per agent definition, not per Agent call. pstack's budget therefore picks model tiers, not effort levels.
