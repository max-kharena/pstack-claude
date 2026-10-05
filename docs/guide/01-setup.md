# Set up pstack

In this page you install the plugin, pick which models pstack uses, and run your first task. Setup is one command plus a short conversation.

## Install the plugin

In Claude Code, add the marketplace and install the plugin:

```text
/plugin marketplace add max-kharena/pstack-claude
/plugin install pstack@pstack-claude
```

Claude Code confirms the plugin is installed. Restart the session so its skills load. Every pstack skill answers to `/pstack:<name>`, and to its bare name, such as `/poteto-mode`, when no other plugin uses that name.

To turn pstack on for everyone working in a repo, commit this to the repo's `.claude/settings.json`. Teammates get a prompt to install it when they trust the folder:

```json
{
  "extraKnownMarketplaces": {
    "pstack-claude": { "source": { "source": "github", "repo": "max-kharena/pstack-claude" } }
  },
  "enabledPlugins": { "pstack@pstack-claude": true }
}
```

The `watch-pr` and `orch` scripts that some playbooks run need [Bun](https://bun.sh). Everything else needs only `git` and `gh`.

## Pick your models

Run:

```text
/setup-pstack
```

[`/setup-pstack`](../../skills/setup-pstack/SKILL.md) detects the models you have access to, asks for a reasoning budget, shows you each role (code delegates, judgment, the review panels), and asks what you want. Answer the questions. It writes `~/.claude/rules/pstack-models.md`, a small user rule that Claude Code loads into every session, so every pstack skill reads it.

You only override what you care about. A role with no line in the rule keeps the skill's default. To restore a default, delete that role's line. A rerun of `/setup-pstack` keeps any role whose model differs from the default.

You might be wondering how to keep every subagent on the model you picked for the session. Set a role to `inherit` and pstack omits the subagent `model` field, so the subagent runs on your session's model. The `session` budget does that for every role.

Upstream pstack mixes Claude, GPT, and Grok on its review panels. In Claude Code every subagent is a Claude model, so the panels default to Opus, Sonnet, and Fable. If you have another vendor's CLI, such as `codex`, setup can add it as a `cli:` panel seat after it proves the CLI answers. For a panel role the value is a list, and one subagent runs per entry, so the list length sets the panel size. Setup also configures `swarm workers`, the default model for every `/swarm` worker unless a race names a model for each arm.

## Accept the verification offer, or don't

At the end of setup, `/setup-pstack` looks for a way to prove app behavior in your project, either a `verify-*` skill or an existing harness. If it finds neither, it offers once to generate one with [`/create-verification-skill`](../../skills/create-verification-skill/SKILL.md).

Say yes and it writes `.claude/skills/verify-<app>/`, a project-local skill that teaches agents to drive your app the way a user does. It proves the skill works once before handing it over. Say no and setup moves on. You can run `/create-verification-skill` yourself any time. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) covers it in depth.

If you're new to pstack, say yes. An agent that can check its own work keeps going until the check passes. An agent that can't hands every result back to you to check by hand. Of everything in this guide, the verification skill pays off the most.

After setup, start a new session. Claude Code loads the model rule at session start.

## Keep the cost in check

pstack spends extra tokens on subagents and review panels. That's the price of the rigor. To spend fewer:

- Rerun `/setup-pstack` and pick a smaller budget or cheaper models. A strong model in the main session with cheaper, faster models in the code roles is a good split.
- Set a role to `inherit` so it runs on the session's own model.
- Shorten a panel list. Each entry runs one subagent.
- Save `/poteto-mode` for work that needs rigor. A small, obvious edit doesn't.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
/poteto-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `/poteto-mode` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. To keep `/poteto-mode` on for the whole session, run `/output-style pstack:poteto`. The [output style](https://code.claude.com/docs/en/output-styles) stays in context on every turn, applies poteto-mode when a playbook matches or a task needs rigor, and stays out of casual turns. `/output-style default` turns it off. To run a whole session as the poteto agent instead, start it with `claude --agent pstack:poteto-agent`. A plain `/poteto-mode` attaches the skill to one task, and it fades as the session moves on.

Next: [Route work through `/poteto-mode`](./02-poteto-mode.md).
