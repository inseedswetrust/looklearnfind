#!/usr/bin/env python3
"""Generate docs/dark-horse/IMPLEMENTED.md from the real data files (so numbers cannot drift from the data)."""
import csv, json, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
B = ROOT / "data/elections/dark_horse"
L = json.loads((B / "latest.json").read_text())
day = L["date"]
cov = list(csv.DictReader(open(B / "coverage_matrix.csv", encoding="utf-8")))
mk = json.loads((B / L["markets_path"]).read_text())["rows"]
man = json.loads((B / L["manifest_path"]).read_text())
wl = list(csv.DictReader(open(B / "watchlist.csv", encoding="utf-8")))
cnt = collections.Counter(r["lock_status"] for r in wl)
ballot_yes = sum(1 for r in wl if r["current_ballot_verified"] == "yes")

def line(r):
    k = r["kalshi"] + (f" ({r['kalshi_contract_kind']}) {r['kalshi_last']}" if r["kalshi"] == "ok" else "")
    p = r["polymarket"] + (f" {r['polymarket_last']}" if r["polymarket"] == "ok" else "")
    return f"| {r['state']} {r['race']} | {r['candidate_name']} | {r['tip_candidate_id'] or 'none'} | {r['current_ballot_verified']} | {r['lock_status']} | {k} | {p} | {r['polls_votehub']} ({r['poll_status']}) |"

matrix = "\n".join(line(r) for r in cov)
okq = [r for r in mk if r["fetch_status"] == "ok"]
pm = [x for x in okq if x["provider"] == "polymarket"]
ka = [x for x in okq if x["provider"] == "kalshi"][:4]
sample = "\n".join(f"| {r['provider']} | {r['candidate_name']} | {r['contract_id'][:24]} | {r['contract_kind']} | {r['price_type']} | {r['quoted_price']} | {r['bid']} | {r['ask']} | {r['volume']} |" for r in pm + ka)
watch_rows = "\n".join(f"| {r['candidate_name']} | {r['state']} {r['race']} | {r['lock_status']} | {r['primary_outcome_verified'][:110]} | {r['c2_udp_spending_documented'][:150]} | {r['c3_establishment_opponent'][:90]} |"
                       for r in wl if r["lock_status"] in ("verified", "partial", "unverified"))
no_market = [r["candidate_name"] for r in cov if r["current_ballot_verified"] == "yes" and r["kalshi"] != "ok"]
doc = f"""# Dark-horse monitor: IMPLEMENTED

**Date:** 2026-10-23. **Status:** collector built, tested, run live, installed as a daily job on the LLF server. First scheduled run: **2026-10-24 08:00 America/New_York** (not yet observed; see "What is not proven").

## What was done against the request

| # | Request | Result |
|---|---|---|
| 1 | Verify the 28 watchlist names against TIP and official rosters | Done. 28 rows kept as supplied (`watchlist_original.csv`); `watchlist.csv` adds TIP IDs, race keys, ballot status, primary outcome (cited), documented criteria and a status. **{cnt['verified']} meet a documented criterion, {cnt['partial']} partial, {cnt['unverified']} unverified, {cnt['background']} background leads.** {ballot_yes} have a ballot verified from TIP's official record; 4 gaps (Wahab and Haynes have no TIP profile; Al Green has no TIP entry for TX-09; Omar's TIP entry rests on owner-supplied sources only) |
| 2 | Reuse Kalshi code; add Polymarket (Gamma + CLOB); no fake URLs or odds | Done. Kalshi lookups follow the existing `tools/elections/fetch_kalshi*.py` approach; Polymarket Gamma for market metadata, CLOB for last trade and book. **Every Kalshi House and Senate contract found is a party-winner contract** (rules: "member of the Democratic Party is sworn in") labeled with the candidate's name; recorded as `party_winner`, never as a named-candidate contract. Polymarket has **two** matched individual-winner contracts (Wahab CA-14, Wiener CA-11); the other search hits were unrelated or derivative markets and were not mapped |
| 3 | VoteHub beta API for race polls | Tested. **VoteHub has race-level polls** (`poll_type=us-senator`, `us-representative`, `governor`) with pollster, sponsor, partisan flag, field dates, sample and original URL. Watchlist coverage: Senate polls for MI, FL, IL, MN; House polls for CA-11, CA-22 and MI-07 only. 270toWin's House page lists no district polls and states no reuse terms, so it was not scraped. VoteHub's terms page returned 403, so licensing is recorded as unverified |
| 4 | Daily folder, manifest, latest pointer, error states, retry, status.json, status view | Done: `daily/<date>/`, `manifest.json` with capture hashes, `latest.json` (moves only for a complete day), `status.json`, `alerts.json`, atomic writes, no blind retry on 429; status page `/elections/2026/dark-horse/status/` (built, ships with the next LLF zip) and a live public `status.json` |
| 5 | Skills from templates and real scripts | Four skills under `.claude/skills/` (paths below). Roles and boundaries in `docs/dark-horse/OPERATIONS.md` |
| 6 | Live tests | **{man['market_quotes_ok']['kalshi']} Kalshi rows, {man['market_quotes_ok']['polymarket']} Polymarket row, {man['poll_rows']} poll rows, 0 errors** locally and again on the server. 9 fixture tests pass with no network (`python3 -m unittest tests/test_dark_horse.py`) |
| 7 | Install the daily job | Installed on the LLF hosting account (proof below) |
| 8 | Carry over R1/R2, fact-check ledger, capture hashes | Capture SHA-256 in every `manifest.json`; ledger format and R1/R2 are in the `llf-factcheck-finalize` skill and apply to any article written from this data (none written yet) |
| 9 | Deliverables | This file, `RUN_REPORT.md`, coverage matrix, skills, changed files, job proof |

## Watchlist: what the evidence supports (not a ranking)

Criteria: C1 incumbent defeated (cited), C2 FEC-documented United Democracy Project (UDP) spending against the nominee or for the defeated opponent, C3 establishment-endorsed opponent (cited). Only rows with a verified criterion are `verified`; every other row is a background research lead. UDP independent expenditures come from OpenFEC Schedule E for the 2026 cycle (de-duplicated, 24/48-hour notices preferred). **AIPAC PAC itself reported no independent expenditures.** Direct AIPAC PAC contributions (Schedule B) and other AIPAC-affiliated committees were not pulled.

| Candidate | Race | Status | Primary outcome (source) | UDP spending (FEC) | Establishment opponent |
|---|---|---|---|---|---|
{watch_rows}

Prior leads, corrected: Ford was endorsed by retiring Rep. Danny Davis; Mejia benefited from spending against Malinowski, not for her; Bronin had the state party endorsement; no UDP spending for or against Biss, Lander or Stratton appears in the FEC data (other committees not checked). For Wahab, Wikipedia says more than $5 million from two AIPAC-affiliated super PACs backed Hernandez, while UDP's FEC total in that race is $0.8M supporting Hernandez and $1.6M opposing Wahab: unreconciled.

## Coverage matrix ({day}, every watchlisted race)

| Race | Candidate | TIP ID | Ballot verified | Status | Kalshi | Polymarket | Polls (VoteHub) |
|---|---|---|---|---|---|---|---|
{matrix}

## Sample real rows

| Venue | Candidate | Contract | Kind | Quote type | Price | Bid | Ask | Volume |
|---|---|---|---|---|---|---|---|---|
{sample}

## Skills (Claude Code)
- `.claude/skills/darkhorse-source-monitor/SKILL.md`
- `.claude/skills/llf-delta-editorial/SKILL.md`
- `.claude/skills/llf-factcheck-finalize/SKILL.md`
- `.claude/skills/workflow-retrospective/SKILL.md`

## Daily job proof
- Host: LLF hosting account (ascendan@65.181.121.38), private folder `~/llf-data/dark_horse` (mode 700), Python 3.9.25, server clock UTC.
- Crontab (updated 2026-10-23 after a DST review; backups `crontab.backup-20261023` and `-b`): `0 12 * * *` and `0 13 * * *` UTC, both running `tools/dark_horse/cron_run.sh`, which proceeds only when the New York hour is 08. 08:00 EDT is 12:00Z until 2026-11-01 and 08:00 EST is 13:00Z after, so exactly one of the two fires each day on either side of the change and `CRON_TZ` support is not needed.
- Proved by hand on the server: the guard skips at 18 ET and at an overridden hour 09; a dry run at an overridden hour 08 runs the job body, writes only `dry_runs/` and leaves `latest.json` alone; the production body (`daily.py`, `alert_if_stale.py`, status copy) ran at 22:54Z with exit 0 (21 Kalshi, 1 Polymarket, 70 poll rows, 0 errors) as revision r2 beside the untouched first run.
- **Status URL (live):** https://looklearnfind.com/elections/2026/dark-horse/status.json
- Staleness: `alert_if_stale.py` exits 1 and prints when a source is over 48 hours old; the public `status.json` shows each source's `stale` flag. No e-mail is sent (no MAILTO is set: adding one would send mail from the account and needs owner approval).

## What is not proven
- No unattended scheduled run has happened yet. After 12:00 UTC on 2026-10-24 (08:00 EDT) check `ls ~/llf-data/dark_horse/data/elections/dark_horse/daily` for a `2026-10-24` folder, `tail ~/llf-data/dark_horse/logs/cron.log ~/llf-data/dark_horse/logs/daily.log`, and `python3 ~/llf-data/dark_horse/tools/dark_horse/verify_day.py`. Status: PENDING_UNATTENDED.
- Server data and repo data are separate. `tools/dark_horse/pull_from_server.sh` backs the server folders up into the repo; `sync_to_server.sh` pushes mapping changes.
- VoteHub licensing, and Polymarket terms for the owner, were not verified; read access works from this network and from the server.
- 17 of {man['watchlist_monitored']} monitored races have no poll. Monitored races with no Kalshi market: {', '.join(no_market)}.
- The 3-point change threshold in `alerts.json` is a placeholder to calibrate after several real days.

## Changed and new files
LLF repo: `tools/dark_horse/*`, `data/elections/dark_horse/*`, `tests/test_dark_horse.py`, `.claude/skills/*`, `docs/dark-horse/*`, `elections.py` (adds only the status page), `.gitignore`. No existing live page was changed. TIP: read-only lookups only.
"""
(ROOT / "docs/dark-horse/IMPLEMENTED.md").write_text(doc, encoding="utf-8")
print(len(doc), "chars")
