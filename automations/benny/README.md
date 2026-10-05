# benny

benny gives you two claude code routines for slack issue reports. one triages each report. the other reproduces confirmed bugs and may prepare a small draft fix.

the files in this directory are dormant setup and automation sources. they do not appear as slash skills.

## set it up

1. point claude code at [`FOR_AGENTS.md`](./FOR_AGENTS.md) and name the target repository.
2. let setup merge this whole directory into the target at `.claude/automations/benny/`. it must preserve destination-only files and review conflicts instead of overwriting local edits.
3. let setup enable pstack in the target repository's `.claude/settings.json` for shared dependencies:

```json
{
	"extraKnownMarketplaces": {
		"pstack-claude": { "source": { "source": "github", "repo": "max-kharena/pstack-claude" } }
	},
	"enabledPlugins": { "pstack@pstack-claude": true }
}
```

4. keep user-owned configuration outside the copied pack, for example in `.claude/benny/`. adapt [`configuration.example.yaml`](./templates/configuration.example.yaml) and [`feature-map.example.md`](./skills/reproduce-and-fix-issues/references/feature-map.example.md).
5. commit `.claude/settings.json`, `.claude/automations/benny/`, and any secret-free configuration before enabling either routine.
6. review each routine draft, create it with `/schedule` (or at claude.ai/code/routines for an api trigger), and keep it paused. then send a harmless test report, use **run now**, and verify every source-channel post stays in the original thread.

routines have no slack trigger. the default runtime polls the channel hourly. a relay you host can fire the routine's api trigger instead for faster pickup. routines are a research preview, so re-check [the routines docs](https://code.claude.com/docs/en/routines) before relying on a detail.
