---
name: llf-election-render
description: Render election articles and pages with the existing LLF components (elections.py, layout report, data macros, charts, candidate cards, district maps, responsive checks). Use when turning approved copy and mockups into built pages or when a component needs changing.
---

# llf-election-render

**Version** 1.1.1 · **Owner** LLF production (Claude Code) · **Type** skill that drives `build.py` and `elections.py`.

## What exists (reuse, do not rebuild)
`elections.py`: `render_report`, `candidate_card`, `tip_button`, `delta_chart`, `spend_chart`, `dedupe_ie`, `autolink` (R1 and R2), `expand_values` (`[[v:name]]`), `expand_macros` (`[[s:n]]`, `[[el:name]]`), the hub, guide and 28 district pages, the dark-horse status page. Styles `static/css/elections.css`, script `static/js/elections.js`. CSS classes are prefixed (`btile`, `relrail`, `etabs`) to avoid site.css collisions. Issue icons `assets/icons/issue-<slug>.svg` must match the issue slug with hyphens.

## Components added 2026-10-24
`poll_unf`, `sept_polls`, `sen_cards`, `mk_sen`, `stats_sen`, `map_story` (five districts with leader-line pins), `trump_bars`, `result_bars`, `house_cards_a`, `house_cards_b`, `mk_h14`, `mk_h25`, `stats_house`, rails `sen` and `house`; values come from `data/elections/FL/story_data.json` (each value carries its source). Share images: `tools/social/render_cards.py`. A new component needs a `role=img` label, a caption with source and date, and a mobile screenshot at 390 px.

## Global shell (2026-11-04)
Pages written through `build.shell()` receive the one shared rail (the desktop sidebar and the mobile slide-in drawer) and mobile bar automatically (`shared_nav.py`, `docs/design/LLF_GLOBAL_SHELL.md`). Render work adds no navigation markup, loads no second rail and keeps section headings `id`ed for the outline. After a layout change run `python3 tools/qa/shell_check.py` as well as `tools/qa/shots.py`.

## Steps
1. Put the article in `content/learn/<slug>.html`; add data to `elections.values()` rather than typing numbers.
2. `PYTHONUTF8=1 python3 build.py --strict`, then `tools/qa/rebuild_serve.sh` and `tools/qa/shots.py` for desktop and mobile screenshots.
3. Check no horizontal scroll at 375 px, hero credit visible, portraits only where licensed (`fl_assets.csv`), alt text present.

## Input and output
Input: approved copy plus data in `data/elections/<ST>/`. Output: `dist/` pages and a release zip made with `python3 build.py --zip --keep-live-robots` (the older `release/looklearnfind-site.zip` must not be uploaded: it overwrites the live robots.txt).

## Fixtures and QA gate
Strict build (0 violations) and `tools/qa/smoke.py`. A new component needs a rendered sample in an existing report before it is used.

## Failure semantics
A macro that cannot resolve fails the build; there is no placeholder fallback. Do not publish a page whose strict build failed.

## Changelog
1.1.1 (2026-11-04) note on the global shell: pages carry no navigation markup of their own. 1.1.0 (2026-10-24) story components, share-image renderer. 1.0.0 (2026-10-23) first version, documenting the components built during Round 0.

## Politics Creative Lock (added 2026-11-05)
For any Politics image, cutout, cover, homepage or feature art, read `docs/politics/brand/01_POLITICS_BRAND_IDENTITY_CREATIVE_BRIEF.md` first. Real politicians appear only as real, rights-recorded photographs (never a generated likeness); every image gets a row in `docs/politics/brand/ASSET_MANIFEST.csv`; an image with unverified rights or identity stays `usage_status=pending` and unpublished. The lock never overrides source verification, this skill's rules or the global shell.
