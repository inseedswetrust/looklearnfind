# MI-A1 fact-check (Claude, 2026-10-28)

Article: `content/learn/mike-duggan-withdrawn-candidate-kalshi-michigan.html`. Checked against saved primary captures, not against ChatGPT's own claims file. **Owner signed off in chat on 2026-10-28. Deploy not yet approved.**

## Result

Every figure and rule quote in the draft matches the saved Kalshi response. All five governor tickets match the official listing. Three statements needed fixing and one sentence was added. Nothing else was cut.

| Claim | Checked against | Result |
|---|---|---|
| Duggan contract: bid 0.0¢, ask 0.1¢, last 0.3¢, active, rule names him | `data/elections/MI/captures/kalshi_mi_20261028T202135Z.json` (GOVPARTYMI-26-MD: 0.0000 / 0.0010 / 0.0030) | Verified |
| Benson contract 92.3 / 93.0 / 92.3 and party rule | same file (-D: 0.9230 / 0.9300 / 0.9230) | Verified |
| James contract 7.1 / 7.3 / 7.5 and party rule | same file (-R: 0.0710 / 0.0730 / 0.0750) | Verified |
| Event title "Michigan Governor winner?"; capture 20:21:35 UTC | file name and event.title | Verified |
| Volume 138,350.39 contracts | `volume_fp` | Verified as Kalshi's cumulative volume field |
| Five tickets with running mates and parties; no independent | `boe_text.txt` (Department of State listing, read Oct 28) | Verified |
| Bridge report dated May 21, 2026 by Simon D. Schuster | Bridge Michigan page, re-read Oct 28 | Verified (page also shows a May 22 update) |
| Duggan quote | Bridge page | **Fixed**, see below |

## Fixes made

1. **Quote.** The draft joined two separate quoted sentences with an ellipsis and dropped the sentence between them. Bridge prints: "If we were even in the polls and behind in fundraising, we have a path to winning," then, as a second quotation, "If we were behind in the polls and even in fundraising, we have a path. But we're behind in both." The article now quotes both in full. Bridge's page leaves the second quotation unclosed; the attribution is "Duggan said in his statement".
2. **May 21.** The Bridge page says the campaign announced "Thursday" and is dated May 21; it does not itself say "May 21". The lede now reads "Bridge Michigan reported on May 21, 2026 that ..." instead of stating May 21 as the date he ended the campaign.
3. **"Duggan does not appear on that listing."** The Department of State listing does contain a different Duggan: Brian M. Duggan, a Republican candidate for the 16th District state House seat in Wayne County. The sentence now says Mike Duggan does not appear among the governor tickets.

## Added

- One sentence on 24-hour volume: the capture reports 317.81 contracts traded in the preceding 24 hours (`volume_24h_fp`), so the contract was not untouched that day. The draft did not have this field. The article still does not say the market is thin or stale, or when the last trade happened. The capture's `updated_time` (Oct 15, 2026) is a market-update stamp, not a trade time, and is not used.

## Wording changed for publication

The open-file box and source notes carried drafting-process language ("supplied reporting", "the package", "this draft", a file path). Rewritten in publication voice. Front-matter title and dek had quote marks that the site printed literally; removed. Date set to 2026-10-28 (the owner sets the real date at deploy).

## Not verified

- `https://kalshi.com/markets/govpartymi` is the URL ChatGPT cited for the Kalshi capture; the data came from Kalshi's public API, and the page URL was not opened.
- The TIP links (`/races/2026-GOV-MI`, `/candidates/GOV-MI-BENSON`, `/candidates/H2MI10150`) were not requested live. The build's publishing rules pass (0 violations).
- Three governor candidates (Hudson, Brandenburg and Campbell) are mentioned without links because their TIP profiles are `needs_review` and their TIP entries are not yet active. This is the open DR-4 / C5 item, not a waiver.
- `MI-A1_CLAIMS.csv` is ChatGPT's list with `checked_date` filled for VERIFIED and ATTRIBUTED rows only. It describes the draft as returned, so the wording changes above are not reflected in it.
- DR-1 (Marist method), DR-2 (a Kalshi explanation) and DR-3 (a trade timestamp) stay open. None blocks the article.
