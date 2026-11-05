# Edition 001 handoff (Daily Signal, 2026-11-05)

Installed byte for byte from `LLF_DAILY_SIGNAL_001_CLAUDE_HANDOFF.zip` and `DAILY_SIGNAL_2026-11-05_EDITORIAL_DRAFT.md`. Authority order: the Creative Lock (`../01`, `../02`), then `HOMEPAGE_INTEGRATION_AND_ASSET_CONTRACT.md` and the mockup in `preview/`, then this edition.

- `preview/` and the reference plates in `assets/` are AI-generated layout references (`usage_status=reference_only` in `../ASSET_MANIFEST.csv`). They are never shipped and never a source for a likeness. The production art is built from real public-domain photographs by `tools/politics/build_politics_art.py`.
- `assets/teal_directional_geometry_1600x900.png` and `assets/paper_cut_edge_1600x900.png` are the two production-ready overlays; copies are in `static/img/politics/` and are used by the hero and the Go to the Source band.

## The edition record
`data/politics_daily/2026-11-05-edition-001.json` was imported from the draft by `tools/politics/import_daily_draft.py` without rewriting any text. It is **status draft, fact check pending, editor not assigned**.

- A normal build (and any release) does not render it: `/politics/` shows the approved fallback and no dated page exists.
- Local review: `LLF_PREVIEW_DRAFTS=1 python build.py --strict` renders `/politics/daily/2026-11-05/` (noindex, labelled draft, not in the sitemap or search, refused by `--zip`) and shows the live-edition strip, the Five signals today links and the Accountability CTA on `/politics/`. `python tools/qa/politics_contract_check.py` fails a preview build unless `--allow-preview` is passed.
- To publish: an independent reviewer passes every figure, call and control claim; set `fact_check.state` to `passed` with the reviewer's name, set a real `editor` (not the author), set `status` to `approved`, then rebuild normally. The contract check enforces those fields.
