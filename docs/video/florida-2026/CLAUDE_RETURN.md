# Florida footage-first and infographic pass: return (2026-10-24)

Nothing was assembled, rendered, deployed or posted. The locked narration was not changed.

## 1. Footage: what exists
- 28 candidate clips across scenes 02, 03, 05, 06, 08 and 10 (`CLIP_MANIFEST.csv`). Rights: **24 NEEDS_LICENSE, 2 EDITORIAL_REVIEW, 1 CLEARED (a 2012 Castor clip, not acquired), 1 INTERNAL_REFERENCE_ONLY**. Scene 03 organizing has no source (NEEDS_ASSET).
- **Downloaded: one file**, Moody at a Senate hearing (168 MB, from Wikimedia Commons), plus a 4-second select (0:00 to 0:04, inspected). I took it before seeing that it is her office's branded edit, so it is held as EDITORIAL_REVIEW in `_review_hold/`, not cleared. Everything else is link, caption timing and thumbnail only; no restricted video was taken.
- Timecodes: only the held select is visually inspected. Others are CAPTION (from timed text) or UNINSPECTED. Per scene detail with links: `CLIP_REVIEW.md`. Who to ask: `PERMISSION_REQUESTS.md` (drafts, not sent).
- Local media library: no Florida video existed before this pass; portraits reused from `static/img/elections/portraits/`.

## 2. Infographics: what was built
Seven graphics, 17 frames, each a layered SVG master (editable in Illustrator, Inkscape or Figma; text stays live, named layers) and a 1080 x 1920 PNG, in `assets/video/florida-2026/infographics/`:

| Graphic | Start | End | Notes |
|---|---|---|---|
| IG-02 | A: matchup, empty plaque | B: Nixon card pushed in, "NIXON WINS", ~12-point margin, official counts | B uses the same photos moved and re-cropped |
| IG-04 | A: 67-county map, Nixon share | B: reduced map plus Duval, Gadsden, Sumter; B1 to B3 push-ins on each | all 67 counties from official data |
| IG-06 | A: 49 and 45 bars | B: poll held smaller, debate card in | headshot bytes identical in A and B (tested) |
| IG-08 | A: two cards, topic chips | B: cards 90%, UNF poll line, summit badge | official portraits, not footage |
| IG-09-10 | A: 28-district map, "21 of 28" callout | B: zoom to FL-14 with Castor and Beltran | district paths from the EDR plan |
| IG-11 | A: six folders with TIP issue names | B: two real TIP records (Moody and Nixon) | screenshots unedited |
| IG-12-13 | A: "Read the race." and "Inspect the record." | B: pulled-back two-panel spread and CTA | real captures of both sites |

No AI plates were made (the packet's background prompts remain optional; the SVG paper layer stands in). No generated faces, maps or text. Evidence for every figure: `INFOGRAPHIC_SOURCES.md`.

## 3. Premiere sequence recommendation (from the packet's timings)
1. IG-02: hold A 0.8 s → reveal B over 1.3 s (cross-dissolve of the result plaque; the card move is a keyframed scale and position of the same two photos) → 1.5 s push toward Nixon → hard cut to Nixon crowd footage (S02-N2 after a license; otherwise the Nixon still).
2. IG-04: A hold, then B1, B2, B3 each with a 1.2 s move between them; end on B.
3. IG-06: bars fill to 49 and 45 and hold; slide to B; then Moody and Nixon speech clips if licensed.
4. IG-08: two 1 to 2 s real clips (matched WLRN sessions) if licensed; otherwise A; then B.
5. IG-09-10: A, then a pan and scale to B; the same SVG paths in both.
6. IG-11: A then B (dissolve through the paper layer).
7. IG-12-13: A, slow pullback to B, hold the CTA at least 3 s.
Keep each graphic's folio and microtext layers for the franchise look; hide them on footage frames.

## 4. Knowledge center changes
Skills: `llf-footage-scout` 1.0.0 (new), `llf-video-storyboard` 1.1.0 (footage-first order, no AI likeness, end frames from start frames). Updated: `CLAUDE.md`, `docs/election-build/AGENT_RUNBOOK.md` and `INDEX.md`, `data/elections/source_registry.json` (six sources), `.gitignore` (video binaries), `WORKFLOW_LOG.md`. Asset manifest: `VIDEO_ASSET_MANIFEST.csv` (44 rows with hashes) from `tools/video/make_video_manifest.py`. The article and publishing skills were not touched.

## 5. Tests
`python -m unittest tests/test_footage_pack.py tests/test_video_pack.py` and the full suite plus `python build.py --strict`: results in the final message of the session (see commit). `tests/test_footage_pack.py` has 16 tests: manifest columns, rights enum, no restricted file downloaded, hashes, timecode format, safe zones, official counts in IG-02, county sums, issue names, identical photo bytes between start and end frames.

## 6. Factual gaps and rights limits
See `INFOGRAPHIC_SOURCES.md` (gaps) and `SCENE_CROSSWALK.md` (timing and order conflicts). In short: no clip is cleared for use; vote shares and the $16M versus under $1M line need an owner decision and a spec fact row; Vindman and Beltran photos are low resolution; the UNF releases were not opened; the Ballotpedia ad index, Reuters Connect and the packet's WESH video could not be read.
