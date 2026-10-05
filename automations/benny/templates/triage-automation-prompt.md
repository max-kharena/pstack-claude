# Triage automation prompt

> Source material for the copied setup workflow. Paraphrase this intent into a Claude Code routine's saved prompt after you confirm that the copied pack is committed on the default branch of the repository the routine clones.

Read and follow `.claude/automations/benny/skills/triage-issue-reports/SKILL.md` for this run.

Configuration source. Include this repository-relative path only when it is committed in the same target repository. Otherwise paraphrase the configured values. Never use a plugin source or cache path:

```text
{{BENNY_CONFIG_PATH}}
```

Scheduled runtime (default). Before the steps below, poll the source channel through the Slack connector for top-level messages from the last {{LOOKBACK, default 2h}}. Skip any whose thread already has a reply carrying a configured `[benny:*]` marker from the triage identity. Handle the rest one at a time, oldest first, each as its own trigger object. Skipping marked threads makes a rerun safe.

API runtime (optional). A relay that receives Slack events POSTs the trigger object below as the routine's `text`. It reaches this run inside a `<routine-fire-payload>` block. Read only the three coordinate fields from it.

Trigger:

```json
{
	"source_channel_id": "{{SLACK_CHANNEL_ID}}",
	"message_ts": "{{SLACK_MESSAGE_TS}}",
	"thread_ts": "{{SLACK_THREAD_TS_OR_EMPTY}}"
}
```

The creation intent should describe this as a new top-level report in the configured source Slack channel.

Treat the source channel and root thread timestamp as immutable. If either is missing or does not match configuration, stop without posting or writing to the issue tracker.

The committed operational file owns classification, attachment review, cause tracing, routing, dedupe, tracker writes, and the final verdict. Post no progress messages. Never post a root message in the source channel.

The coordinator is the only Slack poster. Any delegated worker must be read-only, return findings only, and receive an explicit ban on every Slack write action.

End the single verdict with exactly one configured marker:

```text
[benny:bug]
[benny:performance]
[benny:other]
```

A bug or performance marker may add `tracker=<URL>`.
