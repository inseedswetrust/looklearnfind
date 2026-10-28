# Michigan: TIP-side fixes, for owner approval

Prepared 2026-10-28. **Nothing has been written to TIP.** Basis: `data/elections/MI/roster.json` (reconciled to the Michigan Department of State Official Candidate Listing, General Election 2026-11-03, read 2026-10-28), the TIP export in `data/elections/MI/tip_export/` and `data/elections/MI/candidates.json` (the join; every linked page returned HTTP 200).

Result of the join: 75 roster rows, 69 linked to a TIP page, 6 not linked. TIP holds no entry that is missing from the roster.

## A. Governor race has no race entries (decision)
TIP has the race `2026-GOV-MI` but **zero race entries** for it. Benson and James have profiles (Benson `GOV-MI-BENSON`, needs_review; James `GOV-MI-JAMES`, a merged alias of `H2MI10150`), so LLF links them, but the race page lists nobody.

TIP's Michigan governor profiles also include people not on the November ballot (Mike Cox, Chris Swanson, Perry Johnson, Gretchen Whitmer). They stay out of the entries.

| # | Name | Party | Ballot status (official list) | TIP today |
|---|---|---|---|---|
| 1 | Jocelyn Benson (running mate Winnie Brinks) | Democratic | Petitions, filed 2026-04-16 | profile yes, no entry |
| 2 | John James (running mate Jay DeBoyer) | Republican | Petitions, filed 2026-04-20 | profile yes, no entry |
| 3 | Anthony Hudson (running mate Beau Parmenter) | Libertarian | Convention, 2026-06-29 | no profile |
| 4 | Donna Brandenburg (running mate Robert Donald Cowper II) | U.S. Taxpayers | Convention, 2026-07-20 | no profile |
| 5 | Douglas "Doug" Campbell (running mate Bobbie Clay) | Green | Convention, 2026-08-03 | no profile |

**Proposed:** create 5 `race_entries` (ballot_type printed, source official list, status review until you promote) and 3 new profiles (`verification_status = needs_review`), as for Illinois.

## B. Two race entries with no profile
Both are printed-ballot entries (status active, "Official candidate record checked") with no candidate row, so their TIP page cannot open.

| Name | Race | Party |
|---|---|---|
| Kwabena "Cubby" Nkromo | MI-10 | Green |
| Simone R. Coleman | MI-13 | Working Class |

**Proposed:** create the two profiles and link the existing entries. Neither has an FEC ID in our data; none is graded, and not graded is not zero.

## C. Left alone, listed for the record
- **Bree Taylor** (MI-06, write-in): from Green Papers only, not on the official printed list, no TIP entry. LLF shows "No TIP record yet". Proposed: do nothing.
- **Jasen D. Cartwright** (MI-09, write-in): TIP entry at `review` ("National source only"). Not on the official printed list. Proposed: leave at review.
- **Disqualified on the official list (excluded from LLF; check TIP did not carry them):** Felix Thibodeau (MI-07 Working Class), D. Etta Wilcoxon (MI-13 Green), Shelby Campbell and Maurice Morton (MI-13 No Party Affiliation). TIP's export has no entry for any of them.
- **Thomas "Tom" Smith** (MI-08 Republican) suspended his campaign on 2026-07-16 per Green Papers and remains on the ballot. LLF shows him as listed.

## Decision for you
Approve A (5 entries and 3 profiles) and B (2 profiles) together, or say which to skip. On approval the SQL goes into `the-issues-party/docs/state-packets/MI/` as `NN_missing_profiles.sql` and is applied through the same route as Illinois.
