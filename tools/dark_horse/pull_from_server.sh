#!/usr/bin/env bash
# Back up the server's daily folders, status and logs into the local repo (append-only; raw captures excluded from git by .gitignore).
# Writes to data/elections/dark_horse/server_pull/ so server data never overwrites the local runs. Run weekly or before any server change.
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p data/elections/dark_horse/server_pull
scp -q -r -i ~/.ssh/hosting_com ascendan@65.181.121.38:llf-data/dark_horse/data/elections/dark_horse/daily data/elections/dark_horse/server_pull/
scp -q -i ~/.ssh/hosting_com ascendan@65.181.121.38:llf-data/dark_horse/data/elections/dark_horse/status.json data/elections/dark_horse/server_pull/status.json
scp -q -i ~/.ssh/hosting_com ascendan@65.181.121.38:llf-data/dark_horse/logs/daily.log data/elections/dark_horse/server_pull/daily.log
echo pulled
