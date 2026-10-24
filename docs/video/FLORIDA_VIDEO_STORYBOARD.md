# Storyboard: fl-2026-state-of-the-race (generated from the spec)

90 s, 9:16, 1080x1920, 30 fps. Layer-1 frames are in `release/video/fl-2026-state-of-the-race/frames/` (`segNN.png` on paper, `segNN_alpha.png` transparent).

## Segment 1 · 0-5 s · `hero_title`
- Frame: `seg01.png`
- On screen: 30 contests · Nov 3 / FLORIDA: WHAT THE NUMBERS SHOW
- Narrator: "Florida votes November third, on thirty contests. What do the numbers actually show?"
- SFX and music: brass-techno bed enters on the first beat; one percussive hit on the title
- Facts: F-01
- Plate P01 (frame around the real photo: sky and ground strip only): see `fl_video_prompts.csv`
- Animations (deterministic layer): hero photo: slow push 100%→104% at 0.0s for 5.0s (linear); chip: slam in from top at 0.4s for 0.3s (ease-out); title: fade up with a hit at 1.2s for 0.4s (ease-out)
- Transition out T01 (1.0 s): The paper horizon folds forward like a card and thirty paper tiles unfold out of it into a neat grid; locked-off camera, slow, smooth. Fallback: tiles scale in from the center with a 60 ms stagger.

## Segment 2 · 5-10 s · `board`
- Frame: `seg02.png`
- On screen: 1 governor · 1 Senate · 28 House districts
- Narrator: "One governor, one senator, twenty-eight House members. Eighty-three House candidates alone."
- SFX and music: tile ticks, soft riser
- Facts: F-01, F-02
- Plate P02 (backing grid; real tiles composite on top): see `fl_video_prompts.csv`
- Animations (deterministic layer): tiles: scale in from center, 30 tiles at 0.2s for 1.8s (ease-out); caption: fade in at 2.2s for 0.4s (ease-out)
- Transition out T02 (1.0 s): The thirty tiles slide together and merge into one pale-teal paper peninsula; locked-off camera. Fallback: tiles morph (mask) into the map outline.

## Segment 3 · 10-15 s · `map`
- Frame: `seg03.png`
- On screen: 21 of 28 redrawn
- Narrator: "First, the House. Florida redrew twenty-one of its twenty-eight districts this year."
- SFX and music: hit on the number
- Facts: F-18
- Plate P03 (texture behind the real map): see `fl_video_prompts.csv`
- Animations (deterministic layer): districts 8 to 28: fill teal, left to right at 0.4s for 1.6s (ease-in-out); chip: count 0→21 at 1.0s for 0.8s (ease-out)
- Transition out T03 (1.0 s): Camera pushes in slowly on the paper peninsula as its inner layers shift and a blade re-cuts one edge; thin paper strips curl away. Fallback: map scale-up 140% with the two districts highlighting.

## Segment 4 · 15-20 s · `map_bars`
- Frame: `seg04.png`
- On screen: FL-14 Trump 55 · Harris 44 / FL-9 Trump 58 · Harris 41 / reporters' figures, 2024 vote on new lines (WLRN) / courts declined to block the map for 2026 (WUSF)
- Narrator: "Reporters put Trump's 2024 vote at fifty-five to forty-four in Castor's new district."
- SFX and music: bars grow with a rising tone
- Facts: F-19, F-20, F-21
- Plate P04 (texture behind the bars): see `fl_video_prompts.csv`
- Animations (deterministic layer): map: zoom to FL-14 and FL-9 at 0.0s for 1.0s (ease-in-out); bars: grow from zero at 1.0s for 0.9s (ease-out); small print: fade in at 2.4s for 0.4s (ease-out)
- Transition out T04 (1.0 s): The cut paper layers settle; three mustard-yellow paper discs drop in one after another and bounce once. Fallback: three pins drop with a 3-frame bounce.

## Segment 5 · 20-25 s · `portraits_pins`
- Frame: `seg05.png`
- On screen: FL-25 · Moskowitz / FL-6 · Fine / FL-20 · Wasserman Schultz / won their August 18 primaries
- Narrator: "In August, Moskowitz, Fine and Wasserman Schultz all won primaries under the new lines."
- SFX and music: three tight hits
- Facts: F-22
- Plate P05 (backing for pins; portraits composite on top): see `fl_video_prompts.csv`
- Animations (deterministic layer): portraits: drop onto pins, 3-frame bounce at 0.4s for 0.5s (ease-out); caption: fade in at 2.2s for 0.4s (ease-out)
- Transition out T05 (1.0 s): The three discs slide apart and each splits into two, becoming a row of six small paper windows. Fallback: pins become six slots by mask.

## Segment 6 · 25-30 s · `issue_strip`
- Frame: `seg06.png`
- On screen: Six issues / A dash = not graded, not zero
- Narrator: "Each profile shows up to six issue grades. A dash means not graded."
- SFX and music: single bell tone on the dash
- Facts: F-23
- Plate P06 (backing for the six slots): see `fl_video_prompts.csv`
- Animations (deterministic layer): six slots: fill in order at 0.3s for 0.3s (ease-out); dash slot: pulse once at 2.2s for 0.5s (ease-in-out)
- Transition out T06 (1.0 s): The six windows slide to the edges and the frame splits into an ink half and a teal half with a torn seam. Fallback: vertical wipe with a torn-edge matte.

## Segment 7 · 30-35 s · `split_portraits`
- Frame: `seg07.png`
- On screen: GOVERNOR / Donalds (R) · Jolly (D) / Three numbers
- Narrator: "Governor: Donalds versus Jolly. Three numbers that do not agree."
- SFX and music: beat drops to the kick only
- Facts: F-08, F-09, F-10
- Plate P07 (split backdrop): see `fl_video_prompts.csv`
- Animations (deterministic layer): split: wipe in from the seam at 0.0s for 0.6s (ease-out); three chips: pop in empty, one by one at 1.6s for 0.3s (ease-out)
- Transition out T07 (1.0 s): The seam holds while two horizontal paper strips slide in from the left and stop at nearly equal lengths. Fallback: bars grow from zero over 0.6 s.

## Segment 8 · 35-40 s · `poll_bars`
- Frame: `seg08.png`
- On screen: UNF poll / Donalds 49 / Jolly 47 / 1,471 likely voters · Oct 12–19 · ±2.81
- Narrator: "UNF's poll says forty-nine to forty-seven. Close, not a lead."
- SFX and music: bars grow
- Facts: F-08
- Plate P08 (backing for the bars): see `fl_video_prompts.csv`
- Animations (deterministic layer): bars: grow from zero at 0.3s for 0.9s (ease-out); caption: fade in at 1.6s for 0.4s (ease-out)
- Transition out T08 (1.0 s): The strips fold away and a paper price tag drops on its string and swings once. Fallback: cross-dissolve with the tag easing in.

## Segment 9 · 40-45 s · `market_chip`
- Frame: `seg09.png`
- On screen: 83¢ / Kalshi · Republican party contract / a price, not a vote share
- Narrator: "Kalshi's Republican contract last traded at eighty-three cents. A price, not a vote share."
- SFX and music: cash-register tick, once
- Facts: F-09
- Plate P09 (backing for the chip): see `fl_video_prompts.csv`
- Animations (deterministic layer): price: count 0→83 at 0.3s for 0.8s (ease-out); label: fade in at 1.4s for 0.4s (ease-out)
- Transition out T09 (1.0 s): The tag swings out of frame and two stacks of paper slips of different heights rise from the bottom edge. Fallback: two bars rise from the baseline.

## Segment 10 · 45-50 s · `two_bars`
- Frame: `seg10.png`
- On screen: $107.6M / $6.4M / committee money reported as of Sept 11 · includes transfers · not ad spending
- Narrator: "Committee money, September eleventh: one hundred seven million versus six point four. Not ad spending."
- SFX and music: low swell
- Facts: F-10
- Plate P10 (backing for the two bars): see `fl_video_prompts.csv`
- Animations (deterministic layer): bars: rise from baseline at 0.3s for 1.0s (ease-out); caption: fade in at 1.8s for 0.4s (ease-out)
- Transition out T10 (1.0 s): Both stacks slide into a row and three round paper stamps press down in turn, each leaving a faint blank imprint. Fallback: three chips stamp in at 10-frame intervals.

## Segment 11 · 50-55 s · `three_stamps`
- Frame: `seg11.png`
- On screen: ASKS VOTERS / SHOWS TRADERS / SHOWS FUNDING
- Narrator: "A poll asks voters. A market shows traders. Money shows funding. None is a forecast."
- SFX and music: bed returns full
- Facts: F-08, F-09, F-10
- Plate P11 (backing for the three stamps): see `fl_video_prompts.csv`
- Animations (deterministic layer): stamps: press down in turn at 0.3s for 0.25s (ease-in); footer: fade in at 2.2s for 0.4s (ease-out)
- Transition out T11 (0.5 s): A hard cut: a single flash of brass-colored paper sweeps across the frame left to right on the beat, revealing a tall teal paper arch. Fallback: hard cut on the beat with a 4-frame yellow flash.

## Segment 12 · 55-60 s · `senate_card`
- Frame: `seg12.png`
- On screen: U.S. SENATE · SPECIAL ELECTION / Moody (R) · Nixon (D)
- Narrator: "Now the Senate: a special election for the last two years of Rubio's term."
- SFX and music: beat re-enters with a brass stab
- Facts: F-12
- Plate P12 (frame around the Senate card): see `fl_video_prompts.csv`
- Animations (deterministic layer): card: hard cut in on the beat at 0.0s for 0.0s (none); portraits: slide in from opposite sides at the same speed at 0.2s for 0.6s (ease-out)
- Transition out T12 (1.0 s): The arch's inner space darkens slightly and a cone of pale yellow paper light falls onto an empty stage between teal curtains. Fallback: spotlight mask grows over 0.6 s.

## Segment 13 · 60-65 s · `portrait_spotlight`
- Frame: `seg13.png`
- On screen: Nixon wins the Democratic primary / over Alex Vindman / Vindman: about $14.5M reported raised through June (WFLX)
- Narrator: "Angie Nixon beat Alex Vindman, who had reported raising fourteen and a half million."
- SFX and music: brass line rises
- Facts: F-15, F-16
- Plate P13 (stage light behind the portrait): see `fl_video_prompts.csv`
- Animations (deterministic layer): portrait: scale 80%→100% in the spotlight at 0.2s for 0.8s (ease-out); vindman card: slide in from right at 1.4s for 0.5s (ease-out)
- Transition out T13 (1.0 s): The stage light lowers and two horizontal paper strips slide up into place, ink slightly longer than teal. Fallback: bars grow, portraits scale to equal size.

## Segment 14 · 65-70 s · `poll_bars_portraits`
- Frame: `seg14.png`
- On screen: UNF poll / Moody 49 / Nixon 45 / Oct 12–19 · ±2.81
- Narrator: "The newest poll: Moody forty-nine, Nixon forty-five. Margin of error, nearly three."
- SFX and music: bars grow, held note
- Facts: F-13
- Plate P14 (backing for the bars): see `fl_video_prompts.csv`
- Animations (deterministic layer): bars: grow from zero, same speed at 0.3s for 0.9s (ease-out); caption: fade in at 1.6s for 0.4s (ease-out)
- Transition out T14 (1.0 s): The strips fall away and a paper slider track appears; its yellow marker begins to slide. Fallback: marker animates from 8 to 4 over 1 s.

## Segment 15 · 70-75 s · `gap_marker`
- Frame: `seg15.png`
- On screen: July: 8 (one report, WLRN) / Now: 4
- Narrator: "In July, one report says Moody led by eight. Now: four."
- SFX and music: the held note lifts
- Facts: F-13
- Plate P15 (backing for the marker): see `fl_video_prompts.csv`
- Animations (deterministic layer): marker: slide from 8 to 4 at 0.8s for 1.0s (ease-in-out); caption: fade in at 0.2s for 0.4s (ease-out)
- Transition out T15 (1.0 s): The slider track folds in half and becomes two identical blank paper cards side by side. Fallback: two cards slide in from opposite sides at the same speed.

## Segment 16 · 75-80 s · `quote_cards`
- Frame: `seg16.png`
- On screen: Moody declined to debate / She says she will keep engaging with voters / News Service of Florida
- Narrator: "Moody has declined to debate. She says she will keep engaging with voters."
- SFX and music: music thins to kick and bass
- Facts: F-14
- Plate P16 (backing for the cards): see `fl_video_prompts.csv`
- Animations (deterministic layer): cards: slide in from opposite sides at the same speed at 0.3s for 0.6s (ease-out)
- Transition out T16 (1.0 s): A broad sweep of paper strips clears everything to an empty off-white field in one smooth motion. Fallback: wipe to off-white, then hold 6 frames.

## Segment 17 · 80-85 s · `closing_line`
- Frame: `seg17.png`
- On screen: A challenger who beat the money favorite. / Four points back. / Polls are snapshots.
- Narrator: "A challenger who beat the money favorite, four points back. Polls are snapshots."
- SFX and music: full brass drop, the peak
- Facts: F-13, F-15, F-16
- Plate P17 (peak-moment backdrop): see `fl_video_prompts.csv`
- Animations (deterministic layer): everything else: clear at 0.0s for 0.4s (ease-in); lines: type on, one at a time at 0.6s for 0.5s (ease-out)
- Transition out T17 (1.0 s): Concentric yellow and teal paper semicircles rise on the horizon like a sunrise and settle; a pale sea and a sliver of beach slide in beneath. Fallback: sunrise shapes rise over 1 s, end card fades in.

## Segment 18 · 85-90 s · `end_card`
- Frame: `seg18.png`
- On screen: Early voting: Oct 24–31 / all 67 counties / Every contest and every grade: link in bio / Narration is synthetic. Background graphics are AI-generated illustrations.
- Narrator: "Early voting is open through October thirty-first. Every contest, every grade, linked below."
- SFX and music: final hit, clean tail
- Facts: F-25
- Plate P18 (end card backdrop): see `fl_video_prompts.csv`
- Animations (deterministic layer): end card: fade in over the sunrise at 0.0s for 0.8s (ease-out); credits: fade in at 1.8s for 0.5s (ease-out)
