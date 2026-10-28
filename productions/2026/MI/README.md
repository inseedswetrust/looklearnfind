# Michigan 2026: production folder

Lane: `production:mi-2026`. Scope: Governor, U.S. Senate, U.S. House.

## Pieces
1. **Money delta piece: AIPAC's announcement and UDP's reported spending** (Michigan U.S. Senate: Abdul El-Sayed and Mike Rogers). Working headline: "AIPAC said it was changing how it funds elections. Its super PAC kept spending." Status: draft written 2026-10-28, not fact-checked, not approved, not published.
   - Draft: `articles/aipac-udp-money-delta-october-2026.html`
   - Claims: `research/CLAIMS.csv`
   - Brief: `research/UDP_SPENDING_BRIEF.md`
   - FEC pull: `research/udp_schedule_e_raw.json` and `research/udp_delta_summary.json`, rebuilt by `tools/dark_horse/udp_delta.py`

The FEC key lives in the git-ignored `.env.local` at the repo root (`FEC_API_KEY`). Never commit or print it.

No video, no render, nothing published without the owner's approval.
