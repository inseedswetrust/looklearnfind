# LOOKLEARNFIND — POLITICS HOMEPAGE

**Document ID:** `LLF-POLITICS-HOME-001`  
**Version:** 1.0 — November 5, 2026  
**Target route:** `/politics/`  
**Status:** Page copy and content specification, ready for design integration; not permission to publish unverified current-events statements  
**Visual contract:** `01_POLITICS_BRAND_IDENTITY_CREATIVE_BRIEF.md`

## 1. The editorial job of this page

The Politics homepage is **not** a general homepage, a national results dashboard or a long chronological article list. It must rapidly introduce the LLF editorial promise, surface today's reporting, send readers into the living state reports and create a clearly marked path to leadership and other accountability coverage. Preserve global cross-category search in the locked sidebar, not a Politics-only trap.

Within the first viewport, the reader must see (a) why LLF exists, (b) what's current today and (c) the leading developing story. Below that, give the reader practical entry points into election records, state reporting, campaign money, original sources and archived coverage.

**Copy convention:** Text below marked `PUBLISHABLE BASE COPY` is stable editorial framing, not a finding about the November 3 results. All `DYNAMIC` fields require source-reviewed content. Brackets are **editorial placeholders**, never literal published prose. If a feed is empty, show the specified real empty state rather than sample data.

**Exact public series names for this iteration:** The Daily Signal; The Accountability Desk; Election 2026; State Election Reports; State of the Record; Follow the Money; Election Signals; Go to the Source. The current `State of the Race` archive remains accessible under its original title and is not silently renamed.

## 2. Page title structure and search metadata

- **Browser `<title>`:** `Politics: The Daily Signal, Election Results & Accountability | LookLearnFind`
- **Meta description (draft, ~155 chars):** `Follow political decisions, 2026 election results and campaign money with daily reporting, public records and accountability coverage from LookLearnFind.`
- **Canonical:** the existing canonical for `/politics/`, confirmed by the generator.
- **H1 (only one):** `Less noise. More evidence.`
- **Hero eyebrow:** `01 / POLITICS`
- **Hero subhead:** `The daily briefing, the original records and what they reveal about power, money and what comes next.`
- **Breadcrumb:** `HOME / POLITICS`
- **Page-level `last_updated` label:** Display only if accurately derived from editorial update time; do not render an artificial “live” timestamp.

The headline is a publication promise, not a claim that LLF is more accurate than any named competitor. The visual hero uses directional duochrome geometry and a properly sourced photo or a clearly identified conceptual illustration where applicable. Avoid a second redundant tagline in the hero.

## 3. Page composition and FINAL COPY, top to bottom

### ZONE A — HERO / FIRST IMPRESSION

**Format:** Signature full-width editorial spread within the main content pane. Fixed charcoal sidebar and slim mast remain unchanged. Text occupies the calm warm-paper area; the selected photographic architecture and teal field cut across the adjacent plane. This is the *single principal graphic intervention* above the fold.

**Eyebrow:** `01 / POLITICS`  
**H1:** `Less noise. More evidence.`  
**Deck:** `The daily briefing, the original records and what they reveal about power, money and what comes next.`

**Optional discreet utility links (if needed, not required):** `Explore the 2026 election` · `Go to the source`.

**Do not add:** a yellow underline beneath the H1, a giant yellow CTA block, three competing mission statements or invented factual claims. The editorial hero is meant to have air.

### ZONE B — THE DAILY SIGNAL / TODAY'S BRIEFING

**Format:** Compact horizontal asymmetric strip. Use a title side and concise summary side, a date/time field and one plain link. Yellow may appear as a **small controlled tab or field**, not across the whole row. Dynamic copy supersedes the placeholder every edition.

**Eyebrow:** `THE DAILY SIGNAL`  
**H2:** `Today's political briefing`  
**Standfirst (stable fallback):** `The developments worth following, the evidence behind them and the questions still open.`  
**Datetime label:** `UPDATED [MONTH DAY, YEAR · TIME + ZONE]` — show the actual briefing's reviewed publication time.  
**CTA:** `Read today's briefing`  
**Supporting link:** `Past briefings`

**Dynamic edition fields:**
- `lead_headline` — no more than 12 words, owner-approved
- `lead_summary` — 25–45 words explaining what happened and why it matters
- `briefing_updated_at` — accurate timestamp
- `top_story_links` — up to three, each pointing to a published article or sourced report
- `two_video_assignments` — internal production metadata, **not automatically visible to readers**
- `review_status` — only `approved` appears on the public page

**Empty state if no briefing has been approved:** `Our next briefing is being prepared. In the meantime, explore the reporting and original records below.` Do not claim a briefing has been issued when it has not.

### ZONE C — THE ACCOUNTABILITY DESK / LEAD FEATURE

**Format:** One dominant photo-led editorial feature; use authentic photo cutouts for named leaders when the specific feature art is sourced. Strong headline alongside or partly over a photograph, but no invented leader response counts. This is a lead reporting thread, not an endorsement panel.

**Eyebrow:** `THE ACCOUNTABILITY DESK`  
**H2:** `Who will lead the new Congress?`  
**Deck:** `Leadership decisions shape what reaches the floor, what gets negotiated and what never receives a vote. Follow the public positions, the contenders and the records behind the decisions.`  
**Primary CTA:** `Explore the leadership record`  
**Secondary CTA:** `See the underlying sources`

**Optional live module title:** `Leadership positions, documented`  
**No-data message:** `We're collecting attributable public positions and verifying the source of each one. An unanswered request is not a vote or a position.`

**When records exist, show statuses:** `Supports retaining current leadership`, `Supports alternative leadership`, `Undecided publicly`, `Declined to answer`, `No public position documented`. Do not collapse these into a binary moral score. A story about replacing Jeffries and Schumer must distinguish an advocacy campaign's position from a public record of lawmakers' choices. Do not characterize an election outcome as proof of a particular leadership mandate without supporting evidence.

**TIP relationship:** Link a clearly identified `The Issues Party Action Party` as *external advocacy* only when the route and specific campaign are available and approved. Link candidate records as `Candidate record at The Issues Party`, never imply the candidate endorses TIP.

**Art note:** Use **actual sourced photos** of Hakeem Jeffries and Chuck Schumer when pictured. Extract accurate, unchanged likenesses into paper-edge cutouts. Pair with a sourced documentary chamber or Capitol environment and restrained teal geometry. Do not stage or imply a real joint appearance. Use no generated substitute likeness.

### ZONE D — ELECTION 2026 / STATE REPORTS

**Format:** A substantive section introducing the seven existing state election hubs. Begin with an editorial heading and deck, then a state selector and a visually varied, photo-first set of *actual available* state report links. State tiles are secondary to the lead feature and should not become brightly colored tourism cards.

**Eyebrow:** `ELECTION 2026`  
**H2:** `The election is over. The record isn't.`  
**Deck:** `Explore the results, campaign money and reporting that shaped the contests. Each state report brings the vote counts together with what changed and what comes next.`  
**Section CTA:** `Explore all state reports`  
**Selector label:** `Choose a state`  
**Default ordering:** Editorially selected lead state then alphabetical; never imply popularity or national coverage based on layout position.

**Eligible existing states:** Florida, Illinois, Michigan, Minnesota, New Jersey, New York, Pennsylvania. Use only actual indexed and generated state routes; verify the destination before including a tile.

**State-card copy template:**
- Eyebrow: `[STATE] / ELECTION 2026`
- Title: `[State]: what changed and what comes next`
- Deck: `[One verified, state-specific outcome or question, 15–25 words]`
- Footer: `Results and reporting` and `Updated [accurate date]` only when true
- Link: route to existing `/elections/2026/{state}/`

**No state-specific evidence yet:** Use `Explore the races, reporting and source records for [State].` Do not invent a statewide result or a trend.

**Relationship to prior format:** Existing `State of the Race` pieces become an explicitly dated pre-election archive, linked from state reports under `Before the vote`. The current election report page should not look like an old betting-market preview.

### ZONE E — TWO REPORTING THREADS / MONEY AND EVIDENCE

**Format:** Two large editorial stories or one large lead plus one smaller linked feature. Prefer source-dense reporting and photographs or documentary details. Avoid three identical icon cards and a box titled “features.”

**Thread 1 eyebrow:** `FOLLOW THE MONEY`  
**H2:** `The money behind the message.`  
**Deck:** `Campaign filings and outside spending show who tried to influence the election. Follow the disclosures, the beneficiaries and the limits of what those records can establish.`  
**CTA:** `Follow the spending`

**Thread 2 eyebrow:** `STATE OF THE RECORD`  
**H2:** `Promises made. Decisions pending.`  
**Deck:** `Campaign positions are part of the public record. Now we follow the votes, appointments and decisions that show what happens after Election Day.`  
**CTA:** `Read the record`

These are stable category landing summaries. The linked routes must be real before the CTAs are activated. Do not populate with placeholder URLs.

### ZONE F — ELECTION SIGNALS / SMALL REPORTING MODULE

**Format:** Controlled textual and visual evidence strip, not a statistics dashboard. This module should answer one specific analytical question when a verified signal is available.

**Eyebrow:** `ELECTION SIGNALS`  
**H2:** `What the numbers reveal — and what they don't.`  
**Deck:** `Margins, turnout, geography and spending can reveal important patterns. We show the comparisons, the sources and the uncertainty behind each finding.`  
**CTA:** `Explore the signals`

**Signal card fields:** `headline`, `stat_or_comparison`, `population_and_geography`, `comparison_period`, `method_note`, `source_links`, `verified_at`, `reviewer`, `status`.

**No verified signal:** Show the explanatory deck and a link to methodology or suppress the card carousel. Never show fabricated percentages, fabricated seat totals or unsupported color-coded conclusions.

### ZONE G — CURRENT REPORTING / EDITORIAL PICKS

**Format:** One large chosen story and a compact ruled list of three to five further published stories. Preserve high-quality documentary imagery, varied title length and explicit pre-/post-election context. Do not repeat the entire archive on the homepage.

**Eyebrow:** `THE REPORTING`  
**H2:** `Stories worth a closer look.`  
**Deck:** `Original reporting, verified records and questions we haven't stopped asking.`  
**CTA:** `Browse all Politics reporting`

**Story item fields:** `title`, `standfirst`, `section`, `publication_date`, `update_date`, `source_count`, `image_asset_id`, `canonical_url`, `historical_context_flag`.

If an older story is a poll or prediction-market report, display its original date and a contextual badge: `PRE-ELECTION REPORT / HISTORICAL CONTEXT`. Do not silently republish dated forecasts as if they describe the result.

### ZONE H — GO TO THE SOURCE / FOOTER AREA

**Format:** Calm evidence-oriented row with two or three direct destinations, not a loud conversion banner. It should reinforce LLF's source-first identity and reader autonomy.

**Eyebrow:** `GO TO THE SOURCE`  
**H2:** `Don't take our word for it.`  
**Deck:** `Find original election returns, campaign-finance disclosures and public records. See what we checked, what remains uncertain and how we correct the record.`

**Link labels:** `Election returns`, `Campaign finance records`, `Our reporting methods` — activate only when corresponding approved destinations exist.

**Small method line:** `Sources, timestamps and corrections are part of the story.`

### ZONE I — OPTIONAL NEWSLETTER / END OF PAGE

Only if LLF already has an approved email capture and working consent flow. Do not design or publish a nonfunctional form simply to fill space.

**Eyebrow:** `KEEP LOOKING`  
**H2:** `The next development deserves context.`  
**Deck:** `Get new reporting, useful records and the questions worth following.`  
**CTA:** `Get the briefing`

Ensure consent and privacy language are handled by the existing subscription component, not invented by this copy document.

## 4. Exact homepage reading order

Desktop, main pane only (the shared left rail and top mast are not part of this page-specific template):

1. `01 / POLITICS` + H1 “Less noise. More evidence.” + 1-sentence deck + cutout/duochrome hero.
2. The Daily Signal strip, using the latest **approved** edition or a dignified fallback.
3. One prominent Accountability Desk feature, preferably the leadership question, with documentary image and real-photo leader cutouts when available.
4. Election 2026: state reports heading, clear state-selector entry and genuine state links.
5. Follow the Money + State of the Record: two substantial editorial threads.
6. Election Signals: sourced patterns, no faux metrics.
7. Current reporting: limited curated stories with a path to the full archive.
8. Go to the Source: primary evidence and method links.
9. Optional newsletter only if connected and functional.

**Priority constraint:** The lead hero + Daily Signal + start of Accountability must occupy the initial editorial experience without feeling squeezed. If the viewport cannot support all three gracefully, show the hero and Daily Signal first rather than reducing headline size and photographic quality to force more content above the fold.

**Mobile order:** Same semantic order. The slide-in drawer is the only global mobile navigation. The hero's cutout image stacks after the H1/deck, content remains readable and the briefing and accountability CTA remain prominent.

## 5. Visual writing and art instructions per zone

| Zone | Typographic treatment | Image requirement | Accent rule |
|---|---|---|---|
| Hero | Signature large serif H1, short deck | One sourced monochrome architectural photo, subject mask and offset teal geometry | No automatic yellow underline |
| Daily Signal | Forceful medium serif title + small sans date | Optional atmospheric documentary crop, not necessary if horizontal strip works | One small yellow field maximum |
| Accountability | Large serif story title with quiet source intro | Real documentary Congress/chamber photo, or actual politician photo-cutouts in a sourced composite | Small teal label only |
| State reports | Section heading and photo-led story titles | Existing sourced or labelled state illustrations; real documentary photos when rights allow | No color-coded party inference |
| Money / Record | Dramatic photographic detail, brief copy | Document details, public buildings or real relevant people | Mostly monochrome/teal |
| Signals | Clear comparative typography and source date | Source-driven chart or restrained illustration, only when evidence exists | Use teal to link data elements, not to proclaim a winner |
| Reporting | One large feature and compact list | Existing verified asset manifests and meaningful crops | Minimal section rules |
| Source | Low-key text/links with high legibility | No required image | Quiet and precise |

**Photo manifest required:** asset identifier, story association, real photo origin, photographer/agency, license/reuse basis, original date, manipulation description, caption, credit and public link if available. If a politician appears, photo must be real and match that named person. The site must not use AI-created politician likenesses to stand in for retrieved photos.

## 6. Homepage functionality and information architecture

### Cross-links

- `/politics/` — the new landing, not a duplicate of `/elections/2026/`.
- `/elections/2026/` — national cycle page **only after generator returns a valid live page** (previously 403).
- `/elections/2026/{state}/` — preserve existing seven state hub routes and canonicals.
- `/learn/{slug}/` — original dated articles, unchanged canonical.
- Daily archive route, suggested `/politics/daily/` and dated `/politics/daily/YYYY-MM-DD/` — **proposed**, implement only after route and generator decision.
- Accountability, election signals and money index routes — **proposed**, do not create dead links.
- TIP candidate profile URLs — explicit external source identity when relevant; the tracker must store exact verified links, not invent them.
- TIP Action Party links — separately identified advocacy destinations when approved and active.

### Data and editorial gates

**Never infer a claim from a UI state.** A cached number does not imply official verification. A race call is not certification. No reply is not opposition. No information is not zero. A campaign statement is not a governing action.

**Module publication states:** `draft`, `awaiting_sources`, `under_fact_check`, `awaiting_owner_approval`, `approved`, `published`, `corrected`, `archived`. Only approved/published items may populate the public homepage. Article copy can remain static while verified results JSON is updated separately, but that update must not change human analysis without review.

**Daily editorial flow:** Daily Signal research in ChatGPT → owner selection/approval → Claude article/video brief → evidence review → owner recording (ElevenLabs) and production with Claude/Remotion → publication → user supplies URLs → social copy for X and Bluesky based on actual published links. Internal drafts and videos awaiting production are not visible as finished homepage content.

### Dynamic content slots — minimum schema

`site_section`, `slot_id`, `content_type`, `canonical_url`, `title`, `summary`, `eyebrow`, `published_at`, `updated_at`, `source_set_id`, `review_state`, `image_asset_id`, `alt_text`, `rights_status`, `geography`, `cycle`, `editorial_thread_id`, `historical_context_flag`.

The homepage should be compiled from these typed slots instead of manually pasting new articles into a static theme section. Existing article-to-thread associations should be mapped once using the current content inventory and corrected at metadata level where possible.

## 7. Copy variants — preapproved alternatives

Only use alternatives if the main choice fails at a viewport or actual route title. Do not rotate slogans automatically.

| Location | Primary | Allowed fallback |
|---|---|---|
| Hero | Less noise. More evidence. | The story behind the decision. |
| Daily Signal | Today's political briefing | The Daily Signal |
| Accountability | Who will lead the new Congress? | Leadership is a decision. Follow the record. |
| Election 2026 | The election is over. The record isn't. | What changed. What comes next. |
| Money | The money behind the message. | Follow the money. |
| Record | Promises made. Decisions pending. | From campaign promises to public decisions. |
| Signals | What the numbers reveal — and what they don't. | Read the signals. Check the sources. |
| Source | Don't take our word for it. | Go to the source. |

The copy is purposely concise. Homepage primary sections should not carry long article-length introductions. Detailed reporting belongs at the linked destination.

## 8. SEO and accessibility

- One descriptive H1. Each actual section has a semantic H2. Story headlines under each are H3 or anchors with proper text.
- Titles and summaries must be real HTML text, not embedded solely inside images. Masked art and text-over-photo covers must have equivalent accessible headline text.
- Cross-link to the seven indexed state pages with descriptive labels; do not present national fifty-state completeness.
- Maintain existing canonicals and article dates. Use `lastmod` only for substantive changes.
- Search index must include state hubs and the Politics landing; the audit identified this as a gap.
- Avoid duplicate SEO targets between a living state hub, an article on that state and TIP's candidate record.
- Provide meaningful alt text distinguishing the *subject of the photo* from an interpretation or unverified claim.
- Respect reduced motion, keyboard focus and text contrast. Color alone must not encode party, approval status or an editorial judgment.

## 9. Content migration and population

Preserve all existing political articles. The launch task is **curation and relationships** before writing dozens of new articles. Classify content as `pre-election historical`, `results analysis`, `spending`, `issues`, `election signal`, `accountability` or `source explainer`. Assign appropriate state, district and thread identifiers. Keep original headlines and canonicals unless normal editorial review approves a correction.

For each of the seven state reports, add a reviewed postmortem, verified result links and selected articles. State pages must present dated pre-election forecasts as historical context, not the current state of play. Follow TIP candidate/race profiles through exact verified cross-links and do not replace LLF-owned election-results provenance with TIP profile fields.

## 10. Explicit launch acceptance criteria

- [ ] Politics hero uses the locked mast and charcoal rail with no duplicated site navigation.
- [ ] One prominent actual-photo **directional duochrome geometry** composition appears on the Politics homepage or the designated flagship feature.
- [ ] Main editorial titles use the approved hierarchy; rare yellow interventions and no repeated ornamental underlines.
- [ ] Named politician cutout compositions use authentic, attributable source photos with clearly preserved faces and recorded rights status.
- [ ] Daily Signal opens an approved edition; if there is none it displays the honest fallback.
- [ ] Leadership feature has no invented position totals or unsupported assertions about a mandate.
- [ ] State selectors and links lead to existing valid URLs; the national route is gated until working.
- [ ] Existing Politics articles have appropriate archive/current context and are discoverable without rewriting them.
- [ ] Source-first mechanisms, evidence links and corrections remain visible.
- [ ] Layout passes 1440, 1024, 768, 390 and 320px checks.
- [ ] Mobile drawer retains same global destinations as desktop rail.
- [ ] Strict build, route/canonical/source regressions and relevant accessibility checks pass.
- [ ] No unapproved deployment, publication or production content mutation.

## 11. Implementation handoff to Claude

Read `01_POLITICS_BRAND_IDENTITY_CREATIVE_BRIEF.md` before coding. Inventory shared shell, Politics generator, content/thread registry, image manifest and style tokens. Do not alter shell. Implement the Politics main pane with this exact hierarchy and stable copy. Source actual dynamic content only from approved records. Return staged screenshots at specified viewports, a route/asset audit, sample data schema, failed/gated slots and a concise list of any source or editorial blockers. Do not ask the owner to re-approve already locked navigation or aesthetic decisions. Do not deploy without approval.

---

**Copy approval:** This document approves the *language architecture and stable text*. It does not approve unsourced current political findings, hypothetical election returns, candidate positions or fictional public statements.
