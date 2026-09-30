# The nexus: how Look, Learn, and Find connect (draft)

Status: proposal for review. Phase 1 builds the static bones (data layer, thread pages, slots). Phase 2 wires the Look Ledger into it. Until then Ledger-dependent components render as "Coming soon".

## The problem

Three kinds of object, three different levels of authority:

| Object | What it is | Authority |
| --- | --- | --- |
| **Look** (Ledger entry) | A short video someone kept, with their note | "Worth a look." Not verified. |
| **Learn** (story) | Reported deep dive with `SOURCE 01` footnotes | What was checked, with receipts |
| **Find** (entry) | A real-world person, business, guide, product, or place | A judgment with stated criteria and disclosure |

They need to connect without borrowing each other's authority (a Tartaria clip must not look endorsed by a Tartaria article, and an article must not look like it endorses the clip).

Existing structure: 4 categories > 12 topics. "Tartaria" is finer than either, so we need a third, open-ended tier.

## Core idea: the Thread

A **Thread** is a named subject: Tartaria, Midterms 2026, Retinol, Sourdough, Home energy audits. It is the only thing the three object types share. Objects never link to each other directly by default; each points at threads, and the thread page is where they meet. (This fits the existing line, "Follow a thread.")

```
Category (4)  >  Topic (12)  >  Thread (open-ended)  >  Look clips · Learn stories · Find entries
```

A thread page has fixed, separately labeled shelves:

1. **What people are saving** (Look): Ledger clips, labeled Reader-added / Editor-added.
2. **What the record shows** (Learn): stories, each with its checked/unsettled summary.
3. **Where to try it** (Find): real-world entries.
4. **Not looked into yet** empty state, honest about gaps, with "Send us a source" (feeds Contribute).

Clicking a metadata link on a clip (e.g. `Tartaria`) goes to `/threads/tartaria/`; a "Learn only" results view is one tab away (`?show=learn`).

## Options considered

### A. Free tags (hashtags)
Anyone tags anything. Like YouTube/TikTok hashtags, Tumblr tags.
- Pro: zero editorial work, scales with the Ledger.
- Con: "Tartaria" / "tartarian architecture" / "tartaria mud flood" fragment; no description, no stable page, nothing stopping a tag from implying authority. Weak for a brand built on showing receipts.

### B. Curated thread pages with aliases (recommended core)
A controlled list of threads, each with a canonical page, short editorial description, aliases, and parent topic. Contributors pick from the list (autocomplete) or propose a new one, which editors approve or merge.
- Precedents: Wikipedia articles with redirects (aliases resolve to one canonical page); Wikidata items (stable ID, many labels); New York Times and Guardian topic/tag pages (a stable hub per subject mixing formats); Are.na channels (one block can live in many channels).
- Pro: stable URLs, a real page for each subject, dedupes naturally, editors control framing.
- Con: needs light moderation. Acceptable, since Ledger public adds are already reviewed.

### C. Claim-level links (add later, selectively)
A clip makes a specific claim; a Learn story examines exactly that claim, and the clip shows "Deep dive attached" pointing at it.
- Precedents: schema.org `ClaimReview` markup used by fact-checkers such as Snopes and PolitiFact (and surfaced in search); YouTube's information panels that attach a neutral topic-context link to videos on contested subjects (closest analog to Tartaria clips); X's Community Notes.
- Pro: most honest; the Ledger proposal already has `Deep dive attached`.
- Con: labor-intensive; apply per entry by hand, not as the general mechanism.

### D. Open graph of typed links between objects
Any object can link to any other with a relation type (examines, inspired, visit-for).
- Precedents: Roam/Obsidian-style backlinks; Are.na connections.
- Con: too loose and expensive to maintain at launch. Keep as optional explicit "related" fields.

**Recommendation:** B as the backbone, C as a per-entry overlay, A never (no free tags).

## How Find hangs off Learn

Learn stories are where Finds originate ("the ingredient list is a better starting point" becomes "here is a shop/guide/product that holds up"). Options, not mutually exclusive:

1. **Thread-level (baseline).** Story tagged with thread; the thread page's "Where to try it" shelf lists Finds. Zero extra design; always works.
2. **End-of-story module.** "Try it / Visit it / Meet them" after the final section (Wirecutter-style product picks from reviews; NYT Cooking recipes linked from food stories; Atlas Obscura stories tied to a place page).
3. **Margin markers (brand-native).** A `FIND 01` marker beside the passage it relates to, parallel to `SOURCE 01`. Sources point *back* to the record; Finds point *out* to the world. Uses the existing margin-note grammar and keeps the two kinds of reference visibly different. Needs a distinct treatment (teal arrow/outline versus the `SOURCE` mark) so they're never confused.
4. **Place-led (later).** A map or place index where Finds have locations (Atlas Obscura, Eater maps). Only for Find types where place matters.

**Recommendation:** ship 1 and 2 in phase 1 (static, editorially simple), design 3 as the signature treatment and add it to the story template once two or three real stories exist.

Every Find module carries `Why it made the list · What we checked · Disclosure`. A link from Learn to Find is never paid placement without the disclosure beside it.

## Labels that protect authority

- Look cards: `Reader-added` / `Editor-added`; "Saved by…"; never "verified."
- Thread page shelves are separate and titled differently (above). The Look shelf never sits inside the Learn shelf.
- `L / 042` for Ledger index, `SOURCE 01` for sources, `FIND 01` for real-world references. Three marks, three meanings.
- A thread with clips but no Learn story says so plainly and invites a source.

## Data model (static-friendly)

Flat files now, same shape goes into a database later.

```yaml
# data/threads.yml
- slug: tartaria
  title: Tartaria
  aliases: [tartarian architecture, tartarian empire, mud flood]
  category: society        # one of the 4
  topics: []               # any of the 12 (optional)
  summary: One or two sentences, in voice, neutral framing.
  related: [world-fairs, 19th-century-architecture]
```

```yaml
# Learn story front matter          # Find entry front matter
threads: [tartaria, world-fairs]    threads: [world-fairs]
category: society                   type: place | person | business | guide | product
topics: []                          learned_from: [story-slug]   # optional
                                    criteria, checked, disclosure...

# Look ledger entry (phase 2 data)
id: L-042
video: {provider, provider_id, canonical_url}
threads: [tartaria]     # note, kind, saver etc. per Ledger proposal
```

Build step (phase 1): generate `/threads/{slug}/` from threads.yml, gather Learn and Find items by `threads`, render shelves. The Look shelf renders a "Coming soon" shell until Ledger data exists. Also emit a JSON index for client-side Search and alias resolution.

URLs: `/threads/` (index), `/threads/{slug}/`, optional `?show=look|learn|find`.

## Phase split

**Phase 1 (static)**
- Threads data + generated thread pages and index; aliases; thread chips on stories and Finds.
- Learn story template with thread chips, end-of-story Find module slot.
- Find entry template with "Came from" link back to stories.
- Look page (`/look/`) as static prototype of the v2 table, sample rows flagged illustrative; thread chips on rows link to real thread pages; Save/Follow/Add say "Coming soon".

**Phase 2 (backend)**
- Live Ledger: submissions, dedupe, review queue, accounts, private/public saves, follows.
- Thread autocomplete and proposal/merge queue for editors.
- Claim-level `Deep dive attached` links; margin `FIND 01` markers.
- Thread following.

## Decisions needed

1. Name: "Thread" for the third tier (fits "Follow a thread"). Alternatives: Subject, Question.
2. Move the Ledger to `/look/` with **Look** in the main nav (Ledger proposal had it inside Find).
3. Approve the Learn/Find end-of-story module and the margin `FIND 01` idea.
4. Who approves new threads at launch (editors only, or contributors propose)?
