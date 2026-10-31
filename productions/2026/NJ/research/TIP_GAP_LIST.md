# New Jersey 2026: TIP gap list (for owner approval; nothing in TIP has been changed)

TIP export: docs/state-packets/NJ, 2026-10-31 (13 races, 40 race entries, 194 candidate rows). Roster: data/elections/NJ/roster.json, parsed from The Green Papers (the Division of Elections list was not read). Scope: U.S. Senate (Class 2) and 12 House districts. New Jersey has no governor election in 2026 (the 2025 election chose Mikie Sherrill), and TIP has no NJ governor race, which is correct.

## Matches
All 40 roster rows (5 Senate, 35 House) match a TIP race entry, by FEC ID or, for the four with no FEC ID, by name. Nothing on the roster is missing from TIP and nothing in TIP is missing from the roster.

## Gaps
1. **Four printed entries have no candidate profile and no FEC ID:** Seamus Patrick O'Toole (NJ-07), Aristotle "Ari" Eliopoulos and Craig Honts (NJ-08) and Winston Jordan (NJ-12). They are on the ballot per Green Papers but have no federal filing, so they have no TIP page to link. The NJ pages will list them with "No TIP record yet".
2. **One write-in has a race entry but no candidate row:** Eduardo Jose Castillo Nicasio (Senate, FEC ID S6NJ00495), status `review`.
3. **Fifteen entries are "National source only"** (all minor-party or independent): Ramon Mora Jr. (NJ-02); Ryan Michael Kelly and Steven Welzer (NJ-03); Adam Rueda (NJ-05); O'Toole (NJ-07); Da'shone Hughey, Eliopoulos and Honts (NJ-08); Terrisa Bukovinac (NJ-09); Alan Bond (NJ-11); Andres Jinete and Winston Jordan (NJ-12); Joanne Kuniansky, Veronica Fernandez and Castillo Nicasio (Senate).
4. **NJ-12 incumbent field:** TIP's race row still names Bonnie Watson Coleman. She is not on the roster (open seat; Adam Hamawy is the Democratic nominee). Confirm and clear or relabel the field.
5. **Name forms:** TIP stores some names in capitals (Rob Menendez, Analilia Mejia); the pages show title case.

## Proposed fixes if approved (all idempotent, TIP repo script)
- Create candidate profiles (status `needs_review`) for the four no-FEC printed candidates and link their race entries, as was done for the Michigan and New York minor candidates. Profile slugs would be of the form `nj-h07-2026-otoole`.
- Leave the write-in (Castillo Nicasio) at `review`.
- Do not change the national-source-only labels until the Division certification can be read.
- Clear NJ-12 `incumbent_name` only if you confirm she is not running.
