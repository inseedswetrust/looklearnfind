# Conflicts between the Creative Lock and earlier rules, and how each was resolved (2026-11-05)

| # | Conflict | Resolution |
|---|---|---|
| 1 | Earlier Politics policy status LOCKED vs owner instruction | Set to **PROVISIONAL** (policy 0.2.0) until final visual acceptance. The manifest check accepts PROVISIONAL or LOCKED. |
| 2 | Earlier build: Politics pages lit no mode word. Owner: default mode LEARN | `/politics/` and `/politics/daily/**` map to LEARN in `shared_nav.MODE_ROUTES`. Category pages (`/economy/`, `/society/`, `/everyday-life/`, `/topics/**`, `/latest/`) stay neutral. Matrix, tests and `LLF_GLOBAL_SHELL.md` updated. |
| 3 | Earlier landing copy (eyebrow "POLITICS / THE PUBLIC RECORD", H1 "Power changes hands") vs copy deck | The copy deck (doc 02) governs: eyebrow `01 / POLITICS`, H1 "Less noise. More evidence." `../LANDING_COPY.md` is retained as history only. |
| 4 | Earlier module set (Daily Signal, Follow the story, Explore a state, The Record, threads, radar, verify) vs nine modules | The nine modules in doc 02 replace it. The Politics threads and topic chips move to the Current Reporting zone as links. |
| 5 | Earlier "intentional empty state" blocks vs "no large empty-state block" | A compact strip with the approved fallback sentence plus the latest clearly dated feature. No pipeline wording on the page. |
| 6 | Yellow: shell rule "mode, status and focus only" vs one yellow tab on the Daily Signal | Allowed as a status marker: one small tab, never text on paper, never a party color. |
| 7 | Teal reference `#16A79B` vs production token `--llf-blue #28636c` | Both kept: `--llf-blue` for annotation and rules, new token `--llf-teal-field` for duochrome planes only. |
| 8 | Copy deck CTAs name pages that do not exist (leadership record, money, signals, national hub, election returns) | A CTA is rendered only when its route exists (`data/politics_home.json` `route` is checked against the built site). Gated CTAs are listed in the placement map and are not shown. No dead links. |
| 9 | Copy deck zone I (newsletter) vs the shell footer, which already carries the approved sign-up | Not duplicated. |
| 10 | Brief names `docs/brand/politics/`; owner named `docs/politics/brand/` | Owner path used. |
| 11 | Real photographs required for named politicians vs the cutout needing a mask | Real official portraits (public domain) with the background removed only; the face is untouched. See `ASSET_MANIFEST.csv`. |
| 12 | AI imagery | State illustrations stay labelled "AI illustration". No AI likeness of any real person. |
| 13 | Freshness rule failed historical builds | Stale daily items are now warnings. Future dates, missing sources and duplicate story IDs remain errors. |
| 14 | One record per date vs several stories per briefing | A briefing is all approved records sharing a date; the dated page lists each story ID. |
| 15 | "Election returns" and "Campaign finance records" links | Not shown until the owner approves the destinations (no results source is validated). |

## Added 2026-11-05 (Edition 001 handoff and mockup)
| # | Conflict | Resolution |
|---|---|---|
| 16 | Mockup rail shows a "Politics tools" group and Look/Learn/Find as plain links | Not built. The global rail is permanent and identical on every page (shell invariant). The contextual outline and state picker stay as the shell defines them. |
| 17 | Mockup Accountability headline "Jeffries challenges Schumer's grip on Senate power" and its deck | Not used: it is AI-invented and states a contested claim. The integration contract's copy is used ("A new majority. The same leaders?"), which replaces the copy deck's "Who will lead the new Congress?" |
| 18 | Mockup yellow underlines under the H1, the CTAs and "Go to the source" | Not built. The Creative Lock allows one yellow attention marker per viewport and no ornamental underlines. |
| 19 | Mockup shows an invented bar chart, a VOTE booth and a banknote portrait | Not built: no invented figures, and the lower images follow the contract (real colour photographs where rights exist, labelled AI illustrations otherwise, one duochrome image). |
| 20 | Mockup "12 MIN READ" | Read time is computed from the edition text (8 minutes). |
| 21 | Contract: Five signals links and the briefing CTA only when the edition is approved | Enforced: they appear only for an approved record, or in a local preview build with a DRAFT PREVIEW label. |
| 22 | Contract: Follow the Money tile to "the existing outside-money thread" | No such thread route exists (threads are `/threads/public-money/` and others). The tile links to the lead outside-money report until `/politics/money/` is built. |
| 23 | Edition draft: figures and control claims (both chambers, $12 billion, state flips) | Unverified. The record stays a draft until an independent reviewer passes it. The importer copies the text unchanged and no number is restated elsewhere. |
| 24 | Edition draft asks for a rail outline named ON THIS BRIEFING | A page may name its outline (`data-outline-label`); the shell renders it in the desktop rail and the mobile drawer from one source. Other pages keep "On this page". |

