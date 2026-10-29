# Michigan 2026: storyboard (section level, estimated timing)

Script: `SCRIPT.md`, locked 2026-10-29. Single host, about 833 spoken words; at 2.6 words a second that is 5.3 minutes, so about 6 with pauses. **Durations below are estimates from word count; they become exact when the narration audio exists.** Scene-level rows (`SCENES.csv`, `ASSETS.csv`) are built from the audio timings and the render path chosen (see DECISION_LOG), so they are not written yet.

Visual rules: real people only as real stills or clips; the generated art is supporting illustration only; every number, name card, date and chart is a deterministic overlay (Remotion components, not generated images). Poll field dates stay on screen for the whole poll beat. Narration and AI-art disclosures go on the end card.

| # | Section | Est. start | Est. length | Base visual | Overlays and notes |
|---|---|---|---|---|---|
| 1 | Open (host to camera) | 0:00 | ~29 s | Host; six quick topic cards (poll, rally, ad buy, mailer, ballot, township) | One card per story named in the open, held about 3 s. No candidate images beyond what the later sections show. |
| 2 | Polling | 0:29 | ~37 s | S1 WDIV graphic (REAL_STILL, uncleared) | Overlay field dates, n=600, margin 4.0, Glengariff: the graphic itself carries none. A plain "Oct 19-22 | Oct 25 rally" timeline bar for the "interviews happened before" line. Cut to El-Sayed official clip (about 4 s) and Rogers official clip (about 4 s) at equal length and equal screen size when each is named. |
| 3 | UDP line (woven) | 1:06 | ~12 s | Exact-data graphic (S8) | Five notice rows (Oct 15, 19, 21, 21, 23) adding to $398,683.44; label "FEC Schedule E, Form 24"; "super PAC" caption. No logos. |
| 4 | Attacks | 1:18 | ~37 s | S2 rally photo (uncleared) | Quote cards for the metal-detector remark and Bahbah, attributed to AP/Michigan Public. Back to host for the "My read" line. Credit line must be confirmed (see notes). |
| 5 | Governor | 1:55 | ~44 s | S3 James photo, then James official clip (about 4 s, frames without children) | "$1.8M Michigan Republican Party ad buy"; a plain flow diagram: DeVos gift Oct 19-20 ($2M) -> Michigan Victory 2026 -> state party -> ads; "$750,000 limit" vs "$1.9M reported" bar. Label "Complaint filed; unresolved". |
| 6 | House mailers | 2:40 | ~45 s | S4 mailer, full document first, then punch-in to the payer box | Chain graphic: Conservative Americans PAC -> Progressive Champions PAC -> mailers (100% per WMUK). Green Party denial as an attributed quote. McCann and Barnett have no official ad: show the mailer only; no generated likeness. |
| 7 | Proposal 2 | 3:25 | ~43 s | S6 signatures photo (advocacy-supplied, labeled) | "73.8% yes" bar with n, dates, ±4.0 and "after hearing the ballot summary"; the proposal title from the ballot text (to be read from the official ballot language before build). |
| 8 | Data centers | 4:08 | ~47 s | S7 protest photo labeled "Michigan data-center opposition" | Site card: 423 acres, 700 MW, "exploring, not approved", Oct 30 meeting. Map only if built from a sourced location; otherwise none. |
| 9 | Close + end card | 4:55 | ~27 s | Host, then end card | "Our source links are below"; the woven link-in-bio line; disclosures (synthetic narration if used; AI-generated background art if used); source list S1 to S8. |

Estimated total about 5:22 before pauses. The three official clips are inserts of 3 to 5 seconds, not full ads (see CLIP_CAPTURE.md).
