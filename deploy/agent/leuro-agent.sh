#!/usr/bin/env bash
# Pull-based deploy agent. Runs from a systemd timer as root.
# Fetches the repository; when deploy/<target>/ changed since the last applied commit
# (or the last run failed), runs deploy/<target>/apply.sh and publishes a status file.
set -uo pipefail
SRC="${LEURO_SRC:-/opt/l-euro-src}"
BRANCH="${LEURO_BRANCH:-main}"
TARGET="${LEURO_TARGET:-pilot}"
STATE=/var/lib/leuro-agent; LOG=/var/log/leuro-agent.log
STATUS_DIR=/srv/l-euro/site
mkdir -p "$STATE" "$STATUS_DIR"
exec 9>"$STATE/lock"; flock -n 9 || exit 0
log(){ echo "$(date -Is) $*" >> "$LOG"; }
cd "$SRC" || { log "missing $SRC"; exit 1; }
git fetch -q origin "$BRANCH" || { log "fetch failed"; exit 1; }
NEW=$(git rev-parse "origin/$BRANCH")
OLD=$(cat "$STATE/applied" 2>/dev/null || true)
LAST=$(cat "$STATE/result" 2>/dev/null || echo none)
if [ "$NEW" = "$OLD" ] && [ "$LAST" = ok ]; then exit 0; fi
if [ -n "$OLD" ] && [ "$LAST" = ok ] && git diff --quiet "$OLD" "$NEW" -- "deploy/$TARGET" deploy/agent; then
  echo "$NEW" > "$STATE/applied"; exit 0
fi
git reset -q --hard "$NEW"
install -m 755 deploy/agent/leuro-agent.sh /usr/local/sbin/leuro-agent
log "apply $TARGET at $NEW"
OUT=$(mktemp)
if bash "deploy/$TARGET/apply.sh" > "$OUT" 2>&1; then RES=ok; else RES=failed; fi
cat "$OUT" >> "$LOG"
echo "$RES" > "$STATE/result"; echo "$NEW" > "$STATE/applied"
log "result $RES"
python3 - "$NEW" "$RES" "$OUT" "$TARGET" > "$STATUS_DIR/status.json" <<'P'
import json, sys, datetime
commit, res, out, target = sys.argv[1:5]
tail = open(out, errors="replace").read().splitlines()[-40:]
print(json.dumps({"target": target, "commit": commit, "result": res,
  "time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
  "log_tail": tail}, ensure_ascii=False, indent=2))
P
rm -f "$OUT"
