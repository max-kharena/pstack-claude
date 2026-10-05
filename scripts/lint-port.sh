#!/usr/bin/env bash
# Fail when Cursor-only constructs survive in shipped plugin files.
# Run after scripts/port.py and after every upstream sync merge.
# Usage: scripts/lint-port.sh   (exit 1 on any hit)
set -u
cd "$(dirname "$0")/.."

# pattern<TAB>why. Patterns are extended regex, matched case-sensitively.
rules=$(cat <<'EOF'
\.cursor/	Cursor path; Claude Code uses .claude/
~/\.cursor	Cursor home path; use ~/.claude
\.mdc\b	Cursor rule file; Claude Code rules are .md under ~/.claude/rules/
alwaysApply	Cursor rule frontmatter; Claude Code user rules always load
agent-transcripts	Cursor transcript layout; Claude Code uses ~/.claude/projects/<slug>/<session>.jsonl
generalPurpose	Cursor subagent type; use general-purpose or pstack:reader
readonly: (true|false)|`readonly`	Cursor Task flag; use subagent_type pstack:reader for read-only work
environment: "(cloud|local)"|cloud_base_branch	Cursor cloud-agent spawn field; use isolation: "worktree"
\bAskQuestion\b	Cursor tool; use AskUserQuestion
Task tool|`Task`	Cursor tool name; Claude Code calls it the Agent tool
grok-|gpt-5|-sol-|claude-opus-5-5-max	Cursor model slug; use opus, sonnet, fable, haiku, or inherit
inherit-parent	Cursor alias; Claude Code uses inherit
cursor-team-kit	dependency is vendored into this plugin
create-skill	Cursor built-in; Claude Code uses the skill-creator skill
Custom Mode|option\+enter|Option\+Enter|alt\+enter|Alt\+Enter	Cursor custom modes; use the pstack:poteto output style or claude --agent
/add-plugin	Cursor install command; use /plugin install
cursor\.com|cursor\.sh	Cursor URL
mcps/	Cursor MCP directory; Claude Code lists MCP tools as mcp__<server>__<tool>
Grok Bot|update_state|SendToUser	Cursor bot runtime; use Claude Code routines
EOF
)

# Files that may name Cursor on purpose: attribution, the port map, upstream mirror.
allow='^(\./)?(README\.md|PORTING\.md|LICENSE|vendor/|\.upstream/|scripts/)'

hits=0
while IFS=$'\t' read -r pattern why; do
	[ -z "$pattern" ] && continue
	out=$(git ls-files -co --exclude-standard | grep -Ev "$allow" | grep -Ev '\.(png|jpg|lock)$' \
		| xargs grep -nE -- "$pattern" 2>/dev/null)
	if [ -n "$out" ]; then
		printf '\n## %s\n   %s\n' "$why" "$pattern"
		printf '%s\n' "$out" | sed 's/^/   /' | cut -c1-220
		hits=$((hits + $(printf '%s\n' "$out" | wc -l)))
	fi
done <<<"$rules"

# Bare "Cursor" in prose is usually a missed rewrite. A line that also says
# "upstream" is deliberate attribution. The watch-pr script keeps its Cursor
# Bugbot detection on purpose (it still matches Bugbot comments).
out=$(git ls-files -co --exclude-standard | grep -Ev "$allow" | grep -Ev '\.(png|jpg|lock)$' \
	| grep -v 'scripts/watch-pr/' | xargs grep -nwE 'Cursor' 2>/dev/null | grep -v 'upstream')
if [ -n "$out" ]; then
	printf '\n## bare "Cursor" mention\n'
	printf '%s\n' "$out" | sed 's/^/   /' | cut -c1-220
	hits=$((hits + $(printf '%s\n' "$out" | wc -l)))
fi

if [ "$hits" -gt 0 ]; then
	printf '\nlint-port: %d hit(s)\n' "$hits" >&2
	exit 1
fi
echo "lint-port: clean"
