# Illinois: data access limitation (recorded 2026-10-28, after the Production Lock install)

This note was added after the discovery handoff; the returned discovery files are unchanged.

**Limitation.** The Illinois State Board of Elections site (`elections.il.gov`) returned **HTTP 403** to automated requests during the discovery pass. The official certified candidate list was therefore **not read**.

**Consequences.**
- `data/elections/IL/roster.json` (54 rows) is transcribed from The Green Papers and cross-checked against OpenFEC and TIP; it is **not** an official or complete list. Its header already says this.
- Every row's `isbe_verified` in `il_candidate_tip_mapping.csv` is `PENDING`.
- State-office candidates and write-ins are supported by the secondary source alone; federal candidates by that source plus OpenFEC IDs and TIP entries.
- The Senate and House primary vote shares in the briefs are unofficial (reporters' figures), because the Board's results pages were not read either.

**What clears it.** A person opens the Board's list and results in a browser, confirms the 54 rows and the six primary results, and records the date and initials in the mapping CSV. The discovery work is not repeated.

See `docs/production/DATA_ACCESS_LIMITATIONS.md` for the shared register.
