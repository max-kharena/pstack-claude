#!/usr/bin/env bash
# Pull new cursor/plugins work into the port.
#
# 1. Refresh the `upstream` branch with a verbatim copy of cursor/plugins' pstack
#    (plus the three cursor-team-kit skills pstack depends on), in a temporary
#    worktree so this checkout never switches branches under the running script.
# 2. Merge `upstream` into the current branch, so git replays the port's edits.
# 3. Re-run the mechanical port and the three checks.
#
# Usage: scripts/sync-upstream.sh [ref]   (default ref: main of cursor/plugins)
set -euo pipefail
cd "$(dirname "$0")/.."
ref="${1:-main}"

[ -z "$(git status --porcelain)" ] || { echo "working tree is dirty; commit or stash first" >&2; exit 1; }
old_sha=$(sed -n 's/^sha=//p' .upstream/SOURCE 2>/dev/null || git show upstream:.upstream/SOURCE | sed -n 's/^sha=//p')

tmp=$(mktemp -d)
trap 'git worktree remove --force "$tmp/wt" 2>/dev/null || true; rm -rf "$tmp"' EXIT

git clone --quiet --depth 1 --branch "$ref" https://github.com/cursor/plugins.git "$tmp/src"
new_sha=$(git -C "$tmp/src" rev-parse HEAD)
if [ "$new_sha" = "$old_sha" ]; then echo "already at cursor/plugins@${new_sha:0:7}"; exit 0; fi

git worktree add --quiet "$tmp/wt" upstream
rsync -a --delete --exclude .git --exclude .upstream --exclude vendor --exclude .cursor-plugin \
	"$tmp/src/pstack/" "$tmp/wt/"
mkdir -p "$tmp/wt/vendor/cursor-team-kit/skills" "$tmp/wt/.upstream"
for s in deslop control-ui control-cli; do
	rsync -a --delete "$tmp/src/cursor-team-kit/skills/$s/" "$tmp/wt/vendor/cursor-team-kit/skills/$s/"
done
cp "$tmp/src/cursor-team-kit/LICENSE" "$tmp/wt/vendor/cursor-team-kit/LICENSE"
cp "$tmp/src/pstack/.cursor-plugin/plugin.json" "$tmp/wt/.upstream/cursor-plugin.json"
printf 'repo=https://github.com/cursor/plugins\nsha=%s\npaths=pstack cursor-team-kit/skills/{deslop,control-ui,control-cli}\n' "$new_sha" \
	> "$tmp/wt/.upstream/SOURCE"
git -C "$tmp/wt" add -A
git -C "$tmp/wt" commit --quiet -m "upstream: cursor/plugins@${new_sha:0:7}"

echo "upstream ${old_sha:0:7} -> ${new_sha:0:7}. Files the port owns by hand changed upstream; port these by reading the diff:"
git diff --stat "upstream~1" upstream -- README.md .upstream/cursor-plugin.json skills/setup-pstack skills/poteto-help \
	skills/make-bot-ui agents automations/benny/FOR_AGENTS.md | cat

if ! git merge --no-edit upstream; then
	echo "merge stopped on conflicts. Resolve them, commit, then rerun: scripts/port.py && scripts/lint-port.sh && scripts/check-refs.py" >&2
	exit 1
fi

python3 scripts/port.py
status=0
scripts/lint-port.sh || status=1
python3 scripts/check-refs.py || status=1
claude plugin validate --strict . || status=1
git status --short
[ "$status" -eq 0 ] && echo "sync clean. Review the diff, bump .claude-plugin/plugin.json version, then commit." \
	|| echo "sync needs hand edits: fix what the checks printed, then commit." >&2
exit "$status"
