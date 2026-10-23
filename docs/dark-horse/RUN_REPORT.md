# Run report: first live run, 2026-10-23

| Run | Where | Time (UTC) | Kalshi | Polymarket | Polls | Errors | Exit |
|---|---|---|---|---|---|---|---|
| 1 | local (Windows) | 18:41 | 21 ok | 1 ok | 65 rows (before House-poll matching fix) | 0 | 0 |
| 2 | local, after fix | ~18:43 | 21 ok | 1 ok | 70 rows over 7 races | 0 | 0 |
| 3 | server, first run | 18:45 | 21 ok | 1 ok | 70 rows | 0 | 0 |
| 4 | server, the exact cron command | 18:45 | 21 ok | 1 ok | 70 rows | 0 | 0 (status file copied to the public folder) |

## Failures and fixes found while running
1. **House polls were missed.** VoteHub tags district polls with `subject = "2026 CA-11"`, not the state, so my first matcher found 4 races with polls instead of 7. Fixed in `collect_polls`, fixture test added (`test_house_polls_match_on_district_seat`).
2. **`latest.json` advanced on a partial day.** The feed contract says the pointer must not move when a provider failed; the first version moved whenever one quote succeeded. Fixed (moves only for a complete day) and the test corrected.
3. **Wrong candidate matches in discovery** (an NHL player, an NFL quarterback) from name search on Polymarket: only individual-winner markets whose question names the race were mapped (Wahab CA-14, Wiener CA-11).
4. **Shell and path issues** (Windows `tar` treating `C:` as a host; heredoc quoting) fixed in the scripts; no data effect.

## Data observations (facts, not interpretation)
- Kalshi House and Senate contracts are party-winner contracts labeled with the candidate's name. Prices for several heavily favored races sit near the top of the range with wide bid-ask gaps and small volume (for example IL-07: last 0.956, bid 0.966, ask 0.993, 34 contracts), so the last trade can fall outside the bid-ask. The collector stores all three and never substitutes one for another.
- Polymarket CA-11 (Wiener): last 0.75, bid 0.77, ask 0.79. Last trade, not a mid or an ask.
- VoteHub returned polls for MI (39 for the Senate race), FL (16), MN (8), IL (2) Senate; CA-11 (2), CA-22 (1) and MI-07 (2) House. The rest of the watchlist returned no match: logged `no_poll_found` with source `votehub:us-representative`.
- FEC: UDP reported $56.2M of 2026-cycle independent expenditures across all races in the de-duplicated Schedule E data; AIPAC PAC reported none.

## Open items
1. Observe the first unattended run (2026-10-24 08:00 ET) and confirm the time zone.
2. Decide whether to upload the next LLF zip (status page) and whether to run `pull_from_server.sh` weekly.
3. Verify VoteHub and Polymarket terms; verify the ballot status of Wahab, Al Green, Haynes and Omar from official sources.
