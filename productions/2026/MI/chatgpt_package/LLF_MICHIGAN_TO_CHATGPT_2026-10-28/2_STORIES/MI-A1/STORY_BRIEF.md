# MI-A1: The independent who left (governor)

As of 2026-10-28 · Status: READY · Race: https://theissuesparty.org/races/2026-GOV-MI · Format: Reported Feature

## The one-sentence story
Mike Duggan ended his independent campaign for Michigan governor on May 21, 2026. The Michigan Department of State's general-election listing shows five governor candidates and no independent. Kalshi's governor event still lists a Duggan contract, which last traded at 0.3 cents when we captured it on October 28.

## The conflict and the insight
A candidate who is gone from the ballot still has a line on a prediction market. The piece is about **what a market price does and does not mean** when the thing it prices has changed, not about Duggan's motives and not about who wins. Say plainly that a price is not a forecast, that thin or stale contracts can persist, and that Kalshi has not said why this one is listed (we do not know).

## Verified facts (all in `CLAIMS.csv`)
- **May 21, 2026.** Duggan announced he was ending his independent bid (Bridge Michigan, Simon D. Schuster, opened and read). He is quoted: "If we were even in the polls and behind in fundraising, we have a path to winning ... But we're behind in both." The article does not say whether his name stays on any ballot or whether he endorsed anyone.
- **Official listing.** Michigan Department of State, Official Candidate Listing, General Election 2026-11-03 (read 2026-10-28), governor and lieutenant governor: Jocelyn Benson / Winnie Brinks (Democratic), John James / Jay DeBoyer (Republican), Anthony Hudson / Beau Parmenter (Libertarian), Donna Brandenburg / Robert Donald Cowper II (U.S. Taxpayers) and Douglas Campbell / Bobbie Clay (Green). No independent.
- **Kalshi capture, 2026-10-28 20:21:35 UTC**, event "Michigan Governor winner?" (https://kalshi.com/markets/govpartymi): contract `GOVPARTYMI-26-MD` (a person contract; rule: "If Mike Duggan is inaugurated as the governor of Michigan pursuant to the 2026 election, then the market resolves to Yes"): bid 0.0 cents, ask 0.1 cent, last 0.3 cents. Benson contract `GOVPARTYMI-26-D` (rule: a Democratic-party representative is inaugurated as governor): bid 92.3, ask 93.0, last 92.3 cents. James contract `GOVPARTYMI-26-R` (Republican-party rule): bid 7.1, ask 7.3, last 7.5 cents. Volume on the Duggan contract in the capture: 138,350.39 contracts (all-time, as returned by Kalshi's API; the unit is contracts, not dollars).
- **Marist poll** (Oct 15-18; released about Oct 20): Benson ahead of James among likely voters by 6 points and among registered voters by 11. Margin of error 4.3 points (likely) and 4.0 (registered). Exact percentages and the governor question wording are not on the page we read. Do not give percentages.

## Suggested hook and headlines
- "Mike Duggan left the governor's race in May. A prediction market still lists him."
- "What a 0.3-cent price on a withdrawn candidate does and does not tell you."
Dek idea: Duggan ended his independent bid on May 21 and the state's ballot listing shows no independent. A Kalshi contract with his name last traded at 0.3 cents on October 28.

## Structure that fits
1. The withdrawal, dated and attributed (Bridge).
2. What the official listing shows now (the five tickets).
3. What the market shows now (exact contract, side, UTC time) and what it is.
4. Note the Benson and James contracts are party contracts while Duggan's is a person contract. Why a leftover contract can exist: **say only what is established**: Kalshi's own rules page for the contract defines it; we have not found a statement from Kalshi about this contract. Do not speculate about traders.
5. Where the race stands in reporting, with Marist (margin stated), and the two nominees' TIP profiles.
6. What we do not know.

## TIP
Benson https://theissuesparty.org/candidates/GOV-MI-BENSON · James https://theissuesparty.org/candidates/H2MI10150 · Race https://theissuesparty.org/races/2026-GOV-MI · LLF state governor page https://looklearnfind.com/elections/2026/michigan/governor/ (already carries a short note on the Duggan contract). **No grades are used in this story.**

## Unknowns (write around them)
- Whether any Duggan petition filing or name remains on record anywhere: the Bridge article does not say.
- Why Kalshi still lists the contract.
- Whether he endorsed anyone after leaving.
- Marist's governor wording and exact percentages.
