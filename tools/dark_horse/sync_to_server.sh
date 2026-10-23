#!/usr/bin/env bash
# Push the collector code, watchlist and contract map to the server's private folder (~/llf-data/dark_horse). Run after any mapping change.
set -euo pipefail
cd "$(dirname "$0")/../.."
tar czf dh_bundle.tgz tools/dark_horse/daily.py tools/dark_horse/alert_if_stale.py tools/dark_horse/coverage.py data/elections/dark_horse/watchlist.csv data/elections/dark_horse/contract_map.json
scp -q -i ~/.ssh/hosting_com dh_bundle.tgz ascendan@65.181.121.38:/tmp/dh_bundle.tgz && rm -f dh_bundle.tgz
ssh -i ~/.ssh/hosting_com ascendan@65.181.121.38 'cd ~/llf-data/dark_horse && tar xzf /tmp/dh_bundle.tgz && rm /tmp/dh_bundle.tgz && echo synced'
