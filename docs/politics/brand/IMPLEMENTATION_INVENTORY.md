# Politics homepage and Daily Signal: implementation inventory (2026-11-05, local, not deployed)

Authority: `01_POLITICS_BRAND_IDENTITY_CREATIVE_BRIEF.md`, `02_POLITICS_HOMEPAGE_COPY_AND_CONTENT_SPEC.md`, `edition-001/HOMEPAGE_INTEGRATION_AND_ASSET_CONTRACT.md` and the mockup in `edition-001/preview/`. Conflicts: `CONFLICTS_RESOLVED.md`. Provenance: `ASSET_MANIFEST.csv`.

## 1. Component and CSS change inventory
| Component (`politics.py`) | CSS (`static/css/politics.css`) | Used for |
|---|---|---|
| `hero_duochrome` | `.pol-hero`, `.pol-duo` (`__plane`, `__img`) | Hero. Real Capitol photograph, sky removed, black and white, over the supplied teal parallelogram |
| `daily_strip`, `five_signals` | `.pol-daily`, `.pol-tab` (the one yellow field), `.pol-five` | Daily Signal strip and the Five signals today links (only for an approved edition or a labelled local preview) |
| `accountability_feature` | `.pol-acc`, `.pol-cut` (`__plane`, `__ghost`, `__a`, `__b`), `.pol-nodata`, `.pol-status` | Newspaper-cutout composition (DUAL) of two real official portraits, headline right |
| `tile`, `election_tile`, `money_tile`, `record_tile` | `.pol-tiles`, `.pol-tile` (diagonal photo edge), `.pol-round` | Election 2026, Follow the Money, State of the Record |
| `state_bar` | `.pol-statebar`, `.pol-select` | Seven state hub links and the selector under the tiles |
| `signals_tile` | `.pol-signals` (`__pic`, `__plane`), `.pol-duo-row` | Election Signals: type only, one duochrome photograph, no figures |
| `reporting_list` | `.pol-reporting`, `.pol-ruled`, `.pol-badge`, `.pol-threadlinks` | Current Reporting: three dated stories with the pre-election badge; thread and topic links kept |
| `evidence_band` | `.pol-evidence` (torn-paper edge), `.pol-paper`, `.pol-ev` | Go to the Source |
| `render_edition`, `render_daily_briefing` | `.pol-ed`, `.pol-sig`, `.pol-glance`, `.pol-draftbar`, `.pol-page`, `.pol-story` | `/politics/daily/` index and dated briefing pages |
| Image treatments | `.pol-img--color`, `.pol-img--mono`, `.pol-img--duochrome` | Mixed on purpose: 6 colour, 6 monochrome, 1 duochrome plus the hero and cutouts |

Other changes: `shared_nav.py` (Politics routes map to LEARN; a page may name its rail outline, so the edition reads "On this briefing" in the desktop rail and the mobile drawer; outline labels are unescaped), `build.py` (Politics pages written last; `LLF_PREVIEW_DRAFTS` / `--preview-drafts`; `--zip` refuses a preview build; hubs in search), `site.css` (tokens `--llf-teal-field`, `--llf-paper-edge`), `static/js/politics.js`, `tools/politics/build_politics_art.py`, `tools/politics/import_daily_draft.py`, `data/politics_home.json`, `data/politics_daily/2026-11-05-edition-001.json` (draft).

Yellow: one field (the Daily Signal tab). Teal: hero plane, leadership plane, one signals image. No underline ornaments.

## 2. Editorial content placement map
| Zone | Source | Now on the page |
|---|---|---|
| Hero | copy deck zone A | Eyebrow, H1 and deck verbatim |
| Daily Signal | approved records in `data/politics_daily/` | Normal build: the approved fallback sentence and the latest dated feature. Preview build: Edition 001 headline, "NOV 5, 2026 / EDITION 001 / 8 MIN READ", DRAFT PREVIEW label, link to the briefing, Five signals today |
| Accountability Desk | integration contract | "A new majority. The same leaders?" with the contract's deck, position labels, no-data statement, real-photo cutouts. CTA to the leadership record is gated until the tracker exists (preview: to the edition's Leadership section) |
| Election 2026 | copy deck zone D | Tile (Florida capitol photograph) and a state bar linking the seven live hubs, with the selector |
| Follow the Money | copy deck zone E | Tile; CTA to the lead outside-money report until `/politics/money/` exists |
| State of the Record | copy deck zone E | Tile; CTA to `/threads/following-a-promise/` |
| Election Signals | copy deck zone F | Heading and deck, "No finding has passed our review yet", methods link (preview: Explore the signals to the edition's geography section) |
| Current Reporting | contract | Three real dated reports, each labelled PRE-ELECTION REPORT / HISTORICAL CONTEXT, plus thread and topic links |
| Go to the Source | copy deck zone H | Methods and Corrections; election returns and FEC links hidden until approved |

All 21 political articles, canonical URLs and dates are unchanged.

## 3. Gated calls to action (not shown, no dead link)
Leadership record route; Action Party; the national hub `/elections/2026/` (tile uses the state bar instead); `/politics/money/` (tile links to the lead report); `/politics/signals/`; election returns; the FEC link. Each is a one-line change in `data/politics_home.json`.

## 4. Edition 001 handling
Imported unchanged into a draft record with a pending fact check and no assigned editor. Public only after an independent reviewer passes it and the owner approves (see `edition-001/README.md`). The contract check blocks a release that contains a draft page, a draft strip, or an edition whose teasers, anchors or rail outline do not match.
