# LookLearnFind — The Find Ledger

**Template route:** `/find/ledger`  
**Page role:** a searchable, human-curated index of short-form video links, with personal saves and a chronological feed of public saves from followed profiles.  
**Working line:** **A feed you can steer.**

## The thesis

The Ledger preserves the moment when a short video makes someone stop scrolling. A visitor can find it again by subject, kind of post, the person who saved it, or the path it opens. The experience is finite and navigable: choose filters, choose an order, open the original, and decide what to follow next.

This sits inside **Find** as the index of short-form discoveries. A Ledger item can lead to a **Learn** deep dive and, when there is a meaningful connection, to a real-world **Find**. The original video, a reader's note, a reported story, and a curated real-world recommendation are distinct objects with distinct labels. Saving a link does not verify its claims or make it a LookLearnFind endorsement.

The signature behavior is **Shuffle this shelf**. It picks one random entry from the visitor's current filters and says exactly what set it drew from. It offers serendipity without silently changing the order of the whole page.

## Page anatomy

| Area | What appears | Behavior |
| --- | --- | --- |
| Masthead | Approved `01` logo and site navigation; Find is active | Ledger is reachable from Find and from short social posts that point to an entry. |
| Intro | Title, one-sentence promise, `Add a post` action | Sets expectations: human saves, visitor-chosen filters, original-platform links. |
| Modes | **Explore / Following / My Ledger** | Explore is public; Following is the newest public saves by profiles followed; My Ledger holds personal saves and collections. Signed-out visitors can explore and open originals. |
| Search and filters | Query, category, topic, post kind, duration, platform, language, contributor, date added, and optional location | Query and filters are reflected in the URL. Only show facets populated by the current result set. Applied filters are removable chips. |
| Sort and discovery | **Recently added** default; **Original post date** when known; **Shuffle this shelf** | No opaque personalized sort. A visitor may deliberately choose other views. A finite page ends with `More entries`. |
| Editorial shelf | A small, clearly labeled **From the desk** collection | A deliberate selection with a named curator and a sentence explaining its theme. It never replaces the filterable public index. |
| Results | Contact-sheet grid or readable list toggle | Each card shows a video still or text fallback, original creator, platform, duration if known, post kind, topic, saver, human note, and actions. No autoplay. |
| Profile peek | Featured public collection or person whose saves are worth following | Shows what they tend to save and a direct route to their full public ledger. No follower leaderboard. |

On mobile, put the search field and mode tabs first. Use a full-screen filter drawer with a visible count of applied filters, one card per row, and a persistent Save action. Keep the content and notes readable before asking the visitor to open the original platform.

## The entry card

**Top:** `L / 042` index, topic, post kind, and duration if available.  
**Visual:** provider thumbnail or a typographic fallback; never a fabricated frame presented as the video.  
**Attribution:** `Originally posted by @creator on [platform]` and `Added by [Ledger profile]`. These are different people and must never be conflated.  
**Human context:** one short answer to **“Why was this worth keeping?”**  
**Status:** `Reader-added` or `Editor-added`; if a reported piece exists, `Deep dive attached`. An entry with no deep dive carries no implied fact-check.  
**Actions:** `Watch original ↗` · `Save` · `Open notes`; conditional `Read the deep dive →` and `Find it in the world →`.

Open notes can show additional public savers' notes without turning the card into a comment thread. The original creator's caption is attributed to the platform, while the contributor's note is attributed to the saver. Date added is always available; original publication date and duration display only when reliably obtained.

## Browse controls

**Subject** uses the four main categories: Politics, Economy, Society, Everyday Life. **Topic** uses the site's established subjects, including Candidates, Businesses, Home improvement, Side projects, Cooking, Supplements, Skincare, and Self care.

**Kind of post** is a separate, controlled facet: `Explainer`, `Demonstration`, `Interview`, `Firsthand account`, `Debate / response`, `Visit / tour`, `Idea in progress`. A contributor chooses one primary kind; editors can correct it without changing the original post.

Additional filters: `Length` (under 1 minute, 1–3, 3–10, longer, unknown), `Platform`, `Language`, `Added by`, `Added date`, `Has a deep dive`, `Has a real-world Find`, and `Place` only when location matters. Avoid asking contributors to fill every facet. Imported metadata may be incomplete, and the interface should say `Length unknown` rather than guess.

Explore defaults to **Recently added**, with the choice stated beside the sort control. Following is strictly **newest public save first**. The Ledger does not rank by view count, likes, follower count, or a hidden engagement score. The visitor can share a URL that reproduces their query, filters, sort, and view.

## Save, profile, and follow

1. A person can **Save privately in one click** after signing in. They may add a private note or place the video in a collection.
2. To make a save discoverable, they deliberately choose **Add to public Ledger** or place it in a public collection. Private saves never appear on a profile or in Following.
3. A profile has a display name/handle, brief description, topics of interest, public saves, named collections, and an optional note about what they tend to look for. A profile may also keep everything private.
4. Following a profile subscribes to **that profile's newest public saves**, in time order. A resave can appear with the new saver's note while pointing to the same canonical video. A visitor can unfollow or mute a profile without changing the global Ledger.
5. Public collections have a title, short premise, curator, and ordered entries. The founder can seed collections such as `Midterms worth checking` or `Things to try in the kitchen`; members can make their own. Collection following can be a later extension if profile following launches first.

Counts and social proof stay quiet. The page can say `Saved by people you follow`, but it does not turn profiles into a popularity contest. Offer a simple export of a member's saves so their archive is theirs to keep.

## Add a post: the low-friction flow

**Step 1:** Paste a public short-video URL from a supported platform. Normalize it to a canonical post ID and look for an existing Ledger entry. A duplicate offers `Save it and add your note` instead of creating another video record.

**Step 2:** Show available original creator, title/caption, thumbnail, date, and duration. The contributor can correct or supply missing descriptive metadata, with imported and human-entered fields tracked separately.

**Step 3:** Choose one topic and one kind of post. Answer **“Why was this worth keeping?”** in a sentence or two. Optional: a second topic, place, language, public collection, or a suggested connection to a Learn story/real-world Find.

**Step 4:** Choose **Private save** or **Submit to public Ledger**. A private save is immediate. Public additions pass the stated review process and retain the contributor's attribution. The result gives a link back to the canonical entry.

For launch, the founder and invited contributors can seed the public index, while public member submissions enter a review queue. Report actions cover broken links, wrong attribution, spam, and material that needs context. Moderators can correct tags, merge duplicates, add context, or remove an entry with an audit trail. No open comment thread is needed at launch.

## Trust and source semantics

Use an **`L / 042` Ledger index** for saved links. Reserve the brand's numbered `SOURCE 01` treatment for the footnoted Learn stories that actually examine material. This prevents a popular video from borrowing the authority of a checked source.

The card's `Reader-added` and `Editor-added` labels tell visitors who selected the video. They do not imply truth. `Deep dive attached` is only shown when an actual sourced article is linked. When a creator deletes a post or an embed fails, retain the ledger record with `Original unavailable` and the last checked date, then remove it from active results unless its context still has archival value.

Link to the original platform first. Provider thumbnails and embeds are enhancements, not prerequisites: the card must work with a URL, attribution, and a contributor note. YouTube's data resources expose video metadata such as thumbnails, while TikTok documents an embed method; provider access and fields differ, so Claude should verify each integration before relying on it. Do not rehost original videos as Ledger assets.  
Official references: [YouTube video resource](https://developers.google.com/youtube/v3/docs/videos) · [TikTok embed documentation](https://developers.tiktok.com/docs/en/embed-videos).

## Visual thesis

**An editorial contact sheet that remembers who put each frame there.** Use the approved charcoal masthead, warm paper, deep teal, ink rules, and restrained yellow notation. The videos supply lively color inside disciplined frames. The page should feel like a well-kept collection you can actually use, with room for the human note beneath each still.

- Three columns of portrait media on a wide desktop; list mode gives notes more space. On a phone, one card per row. Use 9:16 media windows without forcing a missing or landscape preview into a fake vertical crop.
- Numbered labels, source lines, and small annotation dots carry the existing identity. The custom topic icons appear on filters and profile collections, not as oversized badges on every card.
- The `Save` control is a small yellow bookmark/ledger-tab motif. State change is immediate and unmistakable. Motion is limited to a subtle card focus and drawer transitions; no autoplay, infinite scroll, or slot-machine Shuffle animation.
- Differentiate original creator, Ledger saver, and LookLearnFind editor typographically. Do not make third-party creators appear to be members of this community.
- A curated shelf can have a more expressive cover and short curator's note; the core grid remains orderly, filterable, and calm.

## Proposed on-page copy

**Eyebrow:** FIND / THE LEDGER

# A feed you can steer.

Short videos that made someone stop scrolling, kept in a place you can actually search. Choose the subjects and kinds of posts you want to see. Follow people whose eye you trust. Save the good ones for later, and open the original whenever you are ready.

**Primary action:** `Explore the Ledger`  
**Secondary action:** `Add a post`

**Search label:** `What are you looking into?`  
**Search example:** `Try “candidate forum,” “kitchen project,” or “skincare claim.”`

**Mode tabs:** `Explore` · `Following` · `My Ledger`  
**Filter labels:** `Subject` · `Topic` · `Kind of post` · `Length` · `Platform` · `Added by` · `More filters`  
**Sort label:** `Order by: Recently added`  
**Serendipity action:** `Shuffle this shelf`  
**Shuffle helper:** `One random entry from your current filters.`

**Editorial shelf heading:** `From the desk`  
**Editorial shelf explanation:** `A handful of links we have been looking at, with a note on why each one stayed with us.`

**Card note prompt:** `Why was this worth keeping?`  
**Card actions:** `Watch original ↗` · `Save` · `Open notes` · `Read the deep dive →` · `Find it in the world →`

**Submission heading:** `Put one in the Ledger.`  
**Submission instruction:** `Paste the link. Tell us what made you stop. One sentence is enough.`  
**Duplicate state:** `This video is already here. Save it to your Ledger and add your own note.`  
**Visibility labels:** `Keep private` · `Submit to public Ledger`  
**Review confirmation:** `Submitted. Your link will appear publicly after review; it is already saved for you.`

**Signed-out save prompt:** `Keep this one? Create a profile to save it and follow other people's finds.`  
**Empty Following state:** `Your Following shelf is quiet. Find someone whose eye you trust, then their public saves will appear here in time order.`  
**No results:** `Nothing in this slice yet. Remove a filter, try a broader question, or add a link we missed.`  
**Unavailable post:** `The original post is unavailable. This entry was last checked on {date}.`

**Profile heading pattern:** `{Name}'s Ledger`  
**Profile subline:** `{N} public saves · Interested in {topics}`  
**Follow action:** `Follow public saves`  
**Private note:** `Your private saves are visible only to you.`

## Launch contract for Claude

**Build first:** canonical URL and deduplication; public Explore; reliable filters and shareable URL state; link-first cards; private saves; public opt-in saves and profile pages; follow profiles with chronological public-save feed; collections; founder/admin curation; review/report flow; explicit status and broken-link handling. Attach Learn and real-world Find links where they exist.

**Add after the core works:** collection following, browser/mobile share-sheet capture, public RSS or export formats, collaborative collections, and richer provider embeds. Shuffle can ship early if it is truly random within the visible result set and never masquerades as an algorithmic recommendation.

**Data contract:** keep a canonical **external video** record separate from a person's **save/note**. Store provider and ID, canonical URL, creator attribution, available provider metadata with provenance, last checked and availability status; record topic/post kind tags, contributor, note, visibility, collection membership, public moderation status, links to Learn/Find content, and follow relationships separately. This distinction supports deduplication, private saves, multiple human interpretations of one video, and corrections without losing the original creator.
