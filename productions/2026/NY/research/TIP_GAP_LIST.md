# New York 2026: TIP gap list (for owner approval; nothing in TIP has been changed)

TIP export: docs/state-packets/NY, 2026-10-30 (32 races, 60 race entries, 321 candidate rows). Roster: data/elections/NY/roster.json (Green Papers; State Board certification not read, HTTP 403).

## Matches
- House: all 60 roster rows (26 districts) match a TIP race entry by FEC ID. No roster candidate is missing from TIP and no TIP entry is missing from the roster.

## Gaps
1. **Governor has zero race entries.** Race 2026-GOV-NY exists (incumbent Hochul) but no candidates. Roster: Kathy Hochul (D, WFP; running mate Adrienne Adams), Bruce Blakeman (R, Conservative, Vote Affordable; running mate Todd Hood). Write-ins listed by Green Papers: Paul Mailhot (Socialist Workers), Jonathan Makeley (Prohibition). TIP governor IDs use the `GOV-NY-` form, so this needs the gubernatorial profile path, not FEC IDs.
2. **Stray races that should not exist for 2026:** `2026-S-NY` (New York has no Senate election in 2026; Gillibrand 2030, Schumer 2028), `2026-H-NY-00`, and districts 27, 28 and 29 (New York has 26). Recommend marking them inactive rather than deleting. The Green Papers Senate names are early filers for later cycles.
3. **One race entry without a candidate row:** H4NY15154 (Gonzalo Duran, Conservative, NY-15).
4. **Eight entries verified only as "National source only":** Blay Tarnoff (NY-04), Priscilla Ghaznavi (NY-07), Sahir Ahsan (NY-08, status review), Karen Ortiz and Wilneida Negron (NY-12), Andre Clement Easton, Gonzalo Duran and Jose David Vega (NY-15). All are minor-line candidates; confirm against the State Board certification when it can be read.
5. **Name oddity:** NY-12 Karen Ortiz has the party label "Karen Ortiz" (an independent line named for the candidate) rather than a party.
6. **Incumbency flags to check:** NY-10 (Goldman lost) and NY-13 (Espaillat lost) are open seats; confirm `incumbent_name` in the race rows is cleared or relabeled.
