# LookLearnFind — sitemap and copy notes (draft for review)

Static-first. "Phase 1" pages are plain HTML from shared templates. "Later" pages need the backend (accounts, database, moderation) and launch as static prototypes or "coming soon" shells with sample data labeled illustrative.

## Sitemap

```
/                                 Home                                  Phase 1
/politics/                        Category: Politics                    Phase 1
/economy/                         Category: Economy                     Phase 1
/society/                         Category: Society                     Phase 1
/everyday-life/                   Category: Everyday Life               Phase 1
/topics/                          Topics index (12 icons)               Phase 1
/topics/{slug}/                   12 topic pages                        Phase 1
    politics · candidates · businesses · home-improvement ·
    self-improvement · side-projects · working-out · cooking ·
    supplements · skincare · self-care · money
/latest/                          Newest across Look, Learn, Find       Phase 1
/learn/                           Story index (all deep dives)          Phase 1
/learn/{story-slug}/              Story Reader, footnotes, Open file    Phase 1 (template + 1 sample)
/find/                            Find hub                              Phase 1
/find/ledger/                     Find Ledger (video index)             Phase 1 static prototype → Later live
/find/ledger/{L-042}/             Single Ledger entry + notes           Later
/find/people/                     People worth visiting/following       Phase 1 shell
/find/businesses/                 Businesses                            Phase 1 shell
/find/guides/                     Guides                                Phase 1 shell
/find/products/                   Products                              Phase 1 shell
/find/{type}/{slug}/              Find entry: why listed, what checked  Phase 1 (template + 1 sample)
/search/                          Search with type tabs + filters       Phase 1 (client-side over a built index)
/about/                           About: Look → Learn → Find example    Phase 1
/about/people/                    Maker, editors, ownership, funding    Phase 1 (real details required)
/about/standards/                 How we source, correct, disclose      Phase 1
/about/corrections/               Corrections and updates log           Phase 1
/contribute/                      Send a question, source, or clip      Phase 1 (form)
/ledger/add/                      Add a post flow                       Later
/account/ · /me/ · /u/{handle}/   Sign in, My Ledger, public profiles   Later
/privacy/ · /terms/ · /contact/   Legal and contact                     Phase 1
/404 · /sitemap.xml · /robots.txt                                       Phase 1
```

Notes
- Story and Find entries carry both a category and one or more topics in front matter; category and topic pages are generated lists.
- Look (short social posts) has no page of its own at launch: Look lives on social, and the Ledger is its index. A `/look/` page is an option if we want a home for our own short posts.
- `/find/ledger/` should be reachable from Find and from each social post that points at an entry.
- Cannabis is outside the current focus, so there is no topic for it.

## Nav and footer

Masthead (from mockups): Politics · Economy · Society · Everyday Life · Topics · Latest · Find (yellow when active) · About · search icon.
Footer: the same nav, plus Contribute, Standards, Corrections, Privacy, Terms, Contact.

## Copy thoughts

Principles, from the guide: lead with a specific noticing, be candid about limits, use concrete verbs, don't repeat slogans.

**Home.** Keep "where signal meets source" exactly. The homepage preview already has the right chapter voice ("Public life, up close." / "Follow the money home." / "How we live together." / "Make a life on purpose." / "Choose a thread." / "Worth a closer look." / "Find what holds up."). I'd keep those, and tighten the closing "Interesting ideas. Open receipts." band. The yellow strip ("Keep looking.") can point to the Ledger and email signup. Flag: the midterms chapter is timely copy and should be dated or swapped after the election.

**About.** Open with "Curiosity should lead somewhere." Then a single worked example, so it shows rather than tells: a short clip → the question behind it → a sourced story → a place to try or visit. Suggested section heads: *What caught our eye* / *What the record shows* / *Where to try it*. The people/ownership/funding section is required and must be real; I'll leave clearly marked placeholders rather than invent anything.

**Category pages.** One-sentence promise, then three to five "threads" (story series), then relevant topics and Finds. Sample one-liners:
- Politics: "The race, the records, the money, and the choices beneath the noise."
- Economy: "Prices, work, business, and the systems behind a receipt."
- Society: "Not a debate stage. A wider view of the norms, places, and conversations shaping daily life."
- Everyday Life: "The home, the kitchen, the body, the small project you keep thinking about."
(These paraphrase the homepage preview; I'd confirm wording against the source files.)

**Topic pages.** Template: a one-line question ("What is actually in a supplement label?"), then Stories, Finds, Ledger clips, and "Bring a question." Keep health topics (Supplements, Skincare, Self care) and Money especially plain about what was checked and what is unsettled, and never glib.

**Story Reader.** Fixed labels: *What does the record show?* · *What we checked* · *What the sources support* · *Other views* · *What remains open* · *Updated / Corrected*. Footnotes read `SOURCE 01` with title, publisher, date, and a one-line "why it matters."

**Find entries.** Fixed labels: *Why it made the list* · *What we checked* · *What to know before you go / try / buy* · *Disclosure*. "Best" only with stated criteria.

**Search.** "Follow a thread." Field label "What are you looking into?" Tabs: All · Stories · Finds · Ledger · Topics. Empty state: "Nothing on that thread yet. Try a broader question, or send us a source."

**Ledger.** Use the proposal's copy as written (Explore/Following/My Ledger, "Why was this worth keeping?", empty/duplicate/unavailable states). In the static prototype, the Save/Follow/Add actions should say *Coming soon* rather than appear to work; all sample rows are labeled illustrative.

**Contribute.** "Bring a question. Bring a source. Tell us what held up." Form types: question, source, video for the Ledger, report from trying a Find. Promise in plain terms: credit, review before elevation, corrections explained.

**Microcopy.** Buttons: Open the source, Read the record, Watch original ↗, Save +, See what changed, Try it, Visit the shop. Avoid: unlock, insights, journey, optimize, game-changing.

## Open questions for you

1. Real names/roles for maker, editors, funding and affiliations (About/people). Placeholders until then.
2. Domain and hosting (static host: cPanel like the seeds site, or Netlify/Cloudflare Pages?).
3. Do we want a dedicated `/look/` page, or keep Look on social only?
4. Any real stories or Finds to seed the templates, or sample content flagged illustrative for now?
5. Font decision: stay on system serif/sans stacks, or license a pair?

## Proposed build order

1. Repo scaffold: static builder, shared masthead/footer, design tokens (colors/type above), logo, favicon.
2. Home (from the preview + assets).
3. Find Ledger static prototype (desktop + mobile drawer, client-side filters, URL state, Shuffle).
4. Category, Topics index and topic pages, Latest.
5. Story Reader template with footnotes; Find entry template.
6. Search, About set, Contribute, legal.
7. Backend phase: accounts, saves, follows, review queue.
