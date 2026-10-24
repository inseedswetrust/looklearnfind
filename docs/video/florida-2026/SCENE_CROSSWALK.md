# Scene crosswalk and timing report (for correction, not changed)

The packet numbers 13 scenes (2, 3, 5, 6, 8, 10 for footage; IG-02, 04, 06, 08, 09/10, 11, 12/13 for graphics). The locked script in this repo (`docs/video/FLORIDA_VIDEO_SCRIPT_AND_PITCH.md`, spec `data/video/fl_2026_state_of_the_race.json`) has 18 segments of 5 seconds. The 13-scene schedule was not in the packet or the repo, so this is the closest mapping. The narration was not touched.

| Packet item | Closest script segment(s) | Note |
|---|---|---|
| IG-02 primary result (scene 2) | 13 "Angie Nixon beat Alex Vindman…" | Packet puts the Senate upset at scene 2; the locked script puts it at 1:00, after House and governor |
| Scene 3 Nixon organizing | none | No narration line about organizing exists |
| IG-04 county map (scene 4) | none | No line about where the win came from; adds a beat the script does not have |
| Scene 5 Moody and Nixon side by side | 12 and 14 | |
| IG-06 poll and debate (scene 6) | 14 (poll), 15 (July 8 to 4), 16 (debate) | One graphic spans three segments |
| IG-08 governor contrast (scene 8) | 7 to 11 | Script has three measures, not "two visions" |
| IG-09/10 House map to FL-14 (scenes 9 to 10) | 3 to 5 | Packet puts the House at scenes 9 to 10 (after the governor); script puts it first |
| Scene 10 Castor and Beltran | 4 to 5 | Script names Castor's district and three other winners, not Beltran |
| IG-11 six issues (scene 11) | 6 | |
| IG-12/13 ecosystem and CTA (scenes 12 to 13) | 18 | |

## Inconsistencies to correct
1. **Order.** The packet runs Senate result (2) → governor (8) → House (9 to 10). The locked script runs House (3 to 6) → governor (7 to 11) → Senate (12 to 17). Both cannot be used; the frames are order-free but the Premiere sequence must follow one.
2. **Length.** The packet itself notes scenes 12 and 13 extending to 1:40 against a 1:30 target. The 18 x 5 s script is exactly 90.0 s with 230 words. Adding the county map (IG-04) and an organizing beat would add time and words the script does not have: not fitted, not pretended to fit.
3. **Vote shares.** Fact F-15 forbids a vote share until the Division of Elections count is read. It has been read (56.06% and 43.94%); the spec needs a new fact row (and an owner decision) before narration cites it.
4. **Money hook.** "$16M vs under $1M" is true only through the primary; FEC totals on Oct 24 are $11.3M (Nixon) and $20.5M (Vindman). The script's own fact F-16 ($14.5M through June, WFLX) is a third figure.
5. **"Summit" framing.** Donalds and Jolly appeared in separate WLRN sessions on Sept 23; graphics and footage must not show them sharing a stage.
6. **Debate.** Scene 6's "refusal" rests on WUSF / News Service of Florida (Oct 1). The Aug 21 WPLG report does not show a refusal.
