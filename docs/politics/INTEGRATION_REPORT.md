# Politics 2.0 integration report (2026-11-05, local only, updated for the Edition 001 mockup)

Nothing is pushed, deployed or published. Live `/politics/` is unchanged. Policy 0.3.0, PROVISIONAL.

## What was built from the mockup and handoff
- `/politics/` re-composed to the mockup: hero with the Capitol, Daily Signal strip, Accountability feature, three tiles, Election Signals beside Current Reporting, and the Go to the Source band. Copy follows the integration contract; the shell is untouched.
- The Edition 001 long-form briefing page (`/politics/daily/2026-11-05/`): opening, five jump-linked signals, five deep sections, "what we are watching", numbered sources, update log, a rail outline named "On this briefing" (desktop and drawer), and Back to today's signals links.
- Edition 001 is imported as a **draft** (fact check pending, editor not assigned). It appears only in a local preview build, labelled and noindex.
- Real photographs: Capitol (hero), Jeffries and Schumer (cutouts). The mockup's AI portraits and plates were not used.

## Screenshots (`docs/politics/screenshots/`)
`politics-1440-viewport.png` (first viewport), `politics-1440.png` (full page), `politics-1024.png`, `politics-390.png`, `politics-320.png`; `politics-drawer-closed-390.png`, `politics-drawer-open-390.png`; the briefing at the same widths (`politics-edition-*`) with its drawer; the Daily Signal index; and `compare-mockup-vs-build.png` (mockup left, build right). All were taken from a preview build, so they show the draft strip and Five signals.

## Verification
| Check | Result |
|---|---|
| `python build.py --strict` (normal build) | 251 pages, 0 publishing violations, `GLOBAL SHELL: 0 violation(s)`, 3 gated calls to action |
| Preview build (`LLF_PREVIEW_DRAFTS=1`) | 252 pages; `--zip` is refused |
| Unit suite | all OK (1 skipped Playwright test) |
| `politics_contract_check.py` | 0 problems on a normal build; a preview build fails unless `--allow-preview` |
| `politics_visual_check.py` (preview build) | 12 page checks at 1440, 1024, 390 and 320: one H1, heading order, landmarks, control names, alt text, no horizontal scroll, 44px targets, visible focus, no failed requests |
| `drawer_check.py`, `shell_check.py` | 0 failures |

## Where the build differs from the mockup (deliberate)
Yellow underlines, the "Politics tools" rail group, the invented Jeffries/Schumer headline, the VOTE booth, banknote and bar-chart imagery, and "12 min read" were not reproduced. Type weight is lighter and the Capitol is a full-front photograph rather than the diagonal dome crop. Details: `brand/CONFLICTS_RESOLVED.md` items 16 to 24.

## Blockers that need the owner
- Independent fact check of Edition 001 (every figure, call and control claim), an assigned editor, then approval. Nothing in it was verified here.
- Rights confirmation for the AI illustrations used in tiles (`labelled_ai` rows; `s2-illinois` and `s1-florida` have no provenance record).
- A real photograph for the signals tile and a chamber photograph for the leadership composition; the mockup's lower photographs were AI-generated and cannot be used.
- Approval or creation of the gated routes (leadership tracker, `/politics/money/`, `/politics/signals/`, `/elections/2026/`), the FEC link and a validated results source.
- Whether `/politics/` replaces the old category page on deploy (the old Look, Learn and Find shelves are gone).
- Owner review of the visual build before any deploy.
