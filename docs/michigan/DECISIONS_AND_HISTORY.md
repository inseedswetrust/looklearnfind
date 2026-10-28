# Michigan 2026: decisions and history

## 2026-10-28, stage 1: roster and TIP join
- **Official list found.** `mielections.us` did not answer and `michigan.gov/sos` returned 403 (not worked around). The Department of State "Candidate Listing Report" that TIP cites (`mi-boe.entellitrak.com`) answered a plain request, so the roster is reconciled to the official list, not just a secondary source. Capture: `data/elections/MI/captures/boe_probe.html` (text in `boe_text.txt`). Michigan pages can therefore say "official list" rather than "not official". Write-ins are not on the printed list.
- **Roster.** `tools/elections/build_mi_roster.py` writes `data/elections/MI/roster.json` (75 rows: 5 Governor, 6 Senate, 64 House; 2 write-ins from Green Papers). `tools/elections/verify_mi_official.py` compares it to the official list: party and surname agree in all 15 races. Four candidates marked DISQ on the official list are left out (Thibodeau, Wilcoxon, S. Campbell, Morton).
- **TIP export** (read-only): `node scripts/export/state-packet.mjs MI`, copied to `data/elections/MI/tip_export/`; `LLF_STATE=MI python tools/elections/join_tip.py data/elections/MI/tip_export` linked 69 of 75. The builder takes each person's TIP name from the race entry by FEC ID because the join matches on the entry name.
- **Overwritten:** `data/elections/MI/candidates.json` was Senate-only (2 people); it now holds all 75 (the old copy is in git).
- **Gaps:** see `TIP_FIX_LIST_FOR_APPROVAL.md`. Waiting on owner approval before any TIP write.
- **Open:** Green Papers lists no independent for Governor; the official list also shows only the five party candidates, so none expected.
