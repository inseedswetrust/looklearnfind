# Questions for review: UX refinement pass

Date 2026-11-04. Everything is local: nothing is committed, published or deployed. Please answer by number. Where I have a recommendation it is marked, with the reason.

## How to review
1. Open `screenshots/` (viewport PNGs at 1440, 1024, 390 and 320 px for the homepage, Pennsylvania hub, race page and article; `-full.jpg` files show the whole page at 1440 and 390; the `*-explore-sheet.png` files show the mobile menu).
2. Open `screenshots/mockups/` for the Pennsylvania Living State Hub design (`state-pa-*`) and the other mockups. Every figure in them is a placeholder marked SAMPLE.
3. Read `UX_REFINEMENT_REPORT.md` for what changed and what was tested.

## Approval
**A. Do the screenshots look right to commit?** If yes, I commit this pass locally (nothing is pushed or deployed until you say so). If not, tell me which pages and widths to change.

## Design decisions
**1. Desktop mast.** It is now a slim bar with only Search and Sign in.
- (a) Keep it. **Recommended:** it keeps both tools one click away without repeating the rail.
- (b) Remove the bar, put Search in the rail only and Sign in in the rail footer.
- (c) Keep the bar and add the page title or section name to it.

**2. About, Look and Find.** Look and Find are the rail modes and About is in the rail footer.
- (a) Leave as is. **Recommended.**
- (b) Add About to the Browse list.

**3. Pennsylvania Living State Hub: apply to the live page?** Today only the mockup follows the new direction; the live hub at `/elections/2026/pennsylvania/` is unchanged.
- (a) Not yet; wait for a results policy and a data source. **Recommended:** the live page is indexed, and the new sections imply results that do not exist.
- (b) Apply the layout now with every results module showing "data unavailable".
- Either way I need your approval of the new heading wording ("what changed and what comes next" versus the current "the State of the Race").

**4. Hero image on the hub.** The mockup uses the existing Harrisburg Capitol AI illustration, labelled as one.
- (a) Keep the labelled illustration. **Recommended** for consistency with the other state heroes.
- (b) License or commission a real photograph (needs a source and a license).

**5. Outline on pages without in-page headings.** State hubs and a few other pages have no outline in the rail.
- (a) Add section ids in the hub generator so the rail shows an outline. **Recommended.**
- (b) Leave them without one.

**6. Rail recommendations on articles** ("Along this thread" and "On our radar") are still pre-election editorial picks. Review them now, after results, or as part of the post-election plan?

**7. Wrong agency in the roster note.** 75 race pages say the roster is from Green Papers "because the State Board of Elections list could not be read". That is wrong for Minnesota (Secretary of State, behind a captcha) and Pennsylvania (Department of State, list not found).
- (a) Fix with one sentence per state. **Recommended:** it is a factual error on live pages. It needs your approval because it is editorial copy.
- (b) Leave for now.

## Carried over from the earlier design package (still open)
**8.** Link the rail to `/elections/2026/` once that landing page exists (it returns 403 today and building it is a separate approval).
**9.** The shell is on `/account/` and `/admin/` because you said every page. Keep it?
**10.** Retire the old stories-only sidebar code after you sign off? (It stays behind the rollback flag until then.)
**11.** Two sets of mast and rail behaviours at 901 to 1060 px were adjusted; please look at the 1024 px screenshots specifically.

## What I did not do
No deploy, no push, no commit; no result, winner statement or analytical conclusion anywhere; no change to any article, route, canonical URL, source or editorial content (verified: the main content HTML is identical on all 250 pages).
