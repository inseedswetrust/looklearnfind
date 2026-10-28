# MI-A2: Senate: a two-point poll and a 69-cent contract, side by side

As of 2026-10-28 · Status: READY · Race: https://theissuesparty.org/races/2026-S-MI · Format: Delta Report (poll beside market)

> **OVERLAP WARNING (read first).** The live piece "Michigan Senate market: most of the slide came before the debate" already reports the Marist 50 to 48 likely-voter result, the registered-voter lead (El-Sayed +7, margin 4.0) and the "69 cents is not a 69% vote share" point. MI-A2 adds only: (a) the October 28 quotes, (b) the contract definition (it is a party contract, see below) and (c) a side-by-side explainer. If the owner prefers, treat MI-A2 as a short companion explainer (400 to 600 words) or skip it. Claude Code has asked the owner; draft nothing until the assignment says which.

## The one-sentence story
Marist's October 15-18 poll has Abdul El-Sayed at 50 and Mike Rogers at 48 among likely voters (margin of error 4.3 points); Kalshi's El-Sayed Senate contract last traded at 69 cents on October 28.

## The conflict and the insight
A two-point gap inside a stated margin of error and a 69-cent price look like different sizes of "lead." They are different kinds of numbers: a poll is a sample of voters' stated preference during a field period; a price is what traders paid for a contract that pays $1 if the stated event resolves yes. Neither is a forecast and neither is a vote share. The piece shows both with their definitions and **explains the difference without predicting**. It must not say which is "right."

## Verified facts (all in `CLAIMS.csv`)
- **Marist** (field dates Oct 15-18, 2026; released about Oct 20; https://maristpoll.marist.edu/polls/midterm-elections-in-michigan-october-2026/): 1,185 registered voters, multi-mode; margin of error 4.3 points among likely voters and 4.0 among registered. Senate wording: "In November's election for Senate, are you supporting:". Likely voters: El-Sayed 50, Rogers 48. Among registered voters El-Sayed leads by 7 points (margin 4.0), as reported in the live piece from the same release. The page does not state the likely-voter sample size and we do not have registered-voter percentages: do not give either.
- **Kalshi capture, 2026-10-28 20:21:35 UTC**, event "Michigan Senate winner?" (https://kalshi.com/markets/senatemi): the contract labeled for El-Sayed, `SENATEMI-26-D`, bid 67, ask 69, last 69 cents. **It is a party contract:** its rules say it resolves yes if "a representative of the Democratic party is sworn in as a Senator of Michigan for the term beginning in 2027." Kalshi shows the nominee's name on it; the rule text names the party. Say "the contract for the Democratic seat, shown under El-Sayed's name" or similar, not "a contract on El-Sayed winning." Rogers's counterpart, `SENATEMI-26-R`: bid 31, ask 33, last 32 cents (Republican party rule). Volume (all-time, contracts): El-Sayed 4,443,722.55; Rogers 6,036,761.45.
- **Already live on LLF (link, do not restate):** the Kalshi El-Sayed delta, "Michigan Senate market: most of the slide came before the debate" (https://looklearnfind.com/learn/michigan-senate-delta-october-2026/), and the AIPAC/UDP money delta (https://looklearnfind.com/learn/aipac-udp-money-delta-october-2026/).
- Other October polls reported by Political Wire (YouGov, Quantus, CBS Detroit/Mitchell) have El-Sayed ahead, mostly within their margins. **Political Wire's summary page was not opened by LLF and the original releases were not opened.** Treat as a lead only: you may say "other October polls have been reported" only if you cite the Political Wire page as the source of that sentence, and Claude Code will check it. Do not give their numbers.

## Suggested hook and headlines
- "Michigan Senate: a 2-point poll and a 69-cent contract."
- "Two numbers about the same race. Here is what each one measures."
Dek idea: Marist has El-Sayed at 50 and Rogers at 48 among likely voters, inside a 4.3-point margin. Kalshi's El-Sayed contract last traded at 69 cents. They measure different things.

## Structure that fits
1. The two numbers, side by side, each with its source, date and definition.
2. What a poll measures (who was asked, how, the margin, what "likely voter" means in general terms).
3. What a Kalshi price measures (contract rules URL, bid/ask/last, that it moves with trading and can be thin or wide).
4. Why they can look different and why that is not a contradiction. **No claim that either predicts the result.**
5. Related reporting on LLF (the two live pieces) and TIP profiles for El-Sayed and Rogers.
6. What we do not know.

## TIP
El-Sayed https://theissuesparty.org/candidates/S6MI00418 · Rogers https://theissuesparty.org/candidates/S4MI00595 · Race https://theissuesparty.org/races/2026-S-MI · LLF Senate page https://looklearnfind.com/elections/2026/michigan/senate/. **No grades are used in this story.**

## Unknowns
Original YouGov, Quantus and Mitchell releases; Marist likely-voter sample size; Marist registered-voter percentages (only the 7-point gap is known); whether Marist weights by anything we have not read.
