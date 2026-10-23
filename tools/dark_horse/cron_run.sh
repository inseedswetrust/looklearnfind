#!/bin/bash
# Daily dark-horse job. Cron fires this at 12:00 and 13:00 UTC; it only runs when the New York hour is 08, so the same crontab is correct before
# and after the daylight-saving change (08:00 EDT = 12:00Z until 2026-11-01, 08:00 EST = 13:00Z after) and does not depend on CRON_TZ support.
# LLF_TEST_NY_HOUR overrides the clock for tests; LLF_DAILY_ARGS passes extra arguments (for example --dry-run).
HOUR="${LLF_TEST_NY_HOUR:-$(TZ=America/New_York date +%H)}"
if [ "$HOUR" != "08" ]; then echo "skip: New York hour is $HOUR"; exit 0; fi
cd "$(dirname "$0")/../.." || exit 1
mkdir -p logs
python3 tools/dark_horse/daily.py ${LLF_DAILY_ARGS:-} >> logs/daily.log 2>&1
rc=$?
python3 tools/dark_horse/alert_if_stale.py || true
if [ -z "${LLF_DAILY_ARGS:-}" ]; then
  mkdir -p "$HOME/looklearnfind.com/elections/2026/dark-horse" && cp data/elections/dark_horse/status.json "$HOME/looklearnfind.com/elections/2026/dark-horse/status.json"
fi
echo "ran: exit $rc"
exit $rc
