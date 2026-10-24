---
name: llf-story-scout
description: Find and vet timely, verifiable election stories from recent reporting and primary records, then return a short STORY_BRIEF (2 to 3 angles per article) with sources, TIP links, grades and unknowns. Use before drafting any LLF election article, instead of assembling a finance dataset.
---

# llf-story-scout

**Version** 1.0.0 · **Owner** LLF editorial (Research agent) · **Type** skill plus the deterministic checker `tools/story/story_brief_check.py`. Added 2026-10-24 under the lean editorial reset: story first, proof enough.

## Steps (about 10 to 15 minutes per article)
1. Search recent coverage (normally the last 7 days, up to 30 for context) from the proposed outlet registry `data/elections/news_source_registry.json` and regional journalism. Registry entries are `proposed`; none is owner-approved. Grow it by adding `proposed` entries only (`registry_add`); never edit or approve existing ones.
2. Collect 8 to 12 headlines only when useful. Look for a specific verified development: an unusual result, a documented controversy with a response, a striking poll change, a campaign-ad twist, a credible contradiction, a market move. Do not manufacture a hook, and do not pick by who should win.
3. Open the best original story in full. A search snippet is never the lead. Get a second independent source or a primary record for the central claim when feasible, and say when two outlets share one underlying report. A damaging claim needs the original material or court record and a response effort.
4. Pull TIP grades from the export and show them only with the profile that holds them. Unverifiable grade: show NOT GRADED.
5. Write `STORY_BRIEF.md` (and optionally `story_brief.json`) with, per angle: working title and the one-sentence fact; state, office, race and candidate IDs; event date and publication date; 1 to 3 source URLs marked opened or discovered; verified facts; response or competing explanation; what could be shown (quote card, map, market card, photo, chart); TIP deep links and grades; at most a handful of unknowns; a synopsis of about 120 words; `ready_to_write` only if the core claim is supported.
6. Run `python3 tools/story/story_brief_check.py story_brief.json --as-of <date>`. NOT_READY angles stay in the brief with the reason; they are not dropped silently.

## Not required
FEC transactions, Schedule E or B, donor tracing, ad-spend reconciliation, full candidate finances, filing deadlines, OpenFEC keys. A reported figure ("the group spent $X, according to Y") is cited and attributed, never presented as audited by LLF, and carries a source and period. Markets and polls appear only when the story uses them; a missing one never blocks an angle.

## Input and output
Input: scope (state, office, race), `as_of`, the registry, TIP race and candidate links, the published-story log. Output: `STORY_BRIEF.md`, optional `story_brief.json`, and the checker's JSON.

## Fixtures and QA gate
`tests/test_story_scout.py` (9): missing URL or date; snippet-only lead; damaging allegation without original and response; recycled coverage labeled as new; unverifiable grade hidden as NOT GRADED; financial claim without attributed source and period; no finance data is never a blocker; registry growth preserves the original and approves nothing. Worked example: `docs/story-briefs/` (Florida Senate and House, 2026-10-24).

## Failure semantics
An angle that fails a test is `NOT_READY` with the reason. The skill never fabricates excitement, conflict, predictions or footage, and treats allegations carefully; attributed political critique is allowed.

## Changelog
1.0.0 (2026-10-24) first version, from `LLF_LEAN_EDITORIAL_RESET_CLAUDE.zip`.
