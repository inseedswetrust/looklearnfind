#!/usr/bin/env python3
"""Build the visual direction document and the prompt sheet for the Florida video from one data table, so the two cannot disagree.

    python3 tools/video/build_visual_direction.py

Writes docs/video/FLORIDA_VISUAL_DIRECTION_AND_PROMPTS.md and docs/video/fl_video_prompts.csv.
Two layers: LAYER 1 is deterministic (data cards, real public-domain portraits, real Capitol photo) and carries every name and number; LAYER 2 is generated plates and
transitions that carry no information. Nothing generated is evidence, and nothing generated contains a person, a face, text, a number or a logo.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STYLE = ("editorial cut-paper collage, flat matte paper texture, warm off-white paper background (#f5f2eb), deep teal (#145b5d) and ink black (#1c1d1b) shapes, "
         "small accents of mustard yellow (#dfca00), subtle risograph grain, soft even studio light, minimal, graphic, premium magazine illustration, vertical composition")
NEG = "text, letters, numbers, words, logos, flags, people, faces, hands, portraits, red, blue, political symbols, photorealism, 3D render, watermark, signature"
SUFFIX = " --ar 9:16 --style raw --stylize 100 --no " + NEG.replace(", ", ", ")

# (id, segment, layer-1 frame to render (deterministic), layer-2 plate prompt (generated, behind or around the layer-1 frame), plate role)
PLATES = [
 ("P01", 1, "Old Florida State Capitol hero photo (static/img/elections/fl-capitol.jpg), slow 4% push; chip '30 contests · Nov 3'; title card",
  "top-down cut-paper horizon: a pale paper sky and a low strip of teal paper palm fronds and sawgrass along the bottom edge, a single mustard-yellow paper sun disc, large calm empty area in the middle for a photograph", "frame around the real photo: sky and ground strip only"),
 ("P02", 2, "30-tile State Board (from candidates.json): 1 governor, 1 Senate, 28 districts, names and party letters",
  "top-down grid of thirty small blank paper rectangles in three rows of ten, softly shadowed, slightly different off-white and pale teal tones, one rectangle in mustard yellow, all perfectly blank", "backing grid; real tiles composite on top"),
 ("P03", 3, "28-district map (districts.json), 21 districts filled teal, 1 to 7 grey; chip '21 of 28 redrawn'",
  "an abstract paper-cut peninsula shape made of overlapping torn paper layers in pale teal and grey, with a faint hand-cut seam running through it, large empty margins", "texture behind the real map"),
 ("P04", 4, "map zoomed to FL-14 and FL-9 with split bars 55-44 and 58-41; small print: reporters' figures; courts declined to block",
  "close detail of overlapping paper layers being re-cut with a sharp blade edge, thin strips of teal and ink paper curling away from the cut, shallow depth of field", "texture behind the bars"),
 ("P05", 5, "three real portraits (Moskowitz 88911, Fine 90492, Wasserman Schultz 91577) dropping onto pins 25, 6, 20",
  "three small circular paper discs in mustard yellow resting on a pale teal paper map texture, long soft shadows, top-down", "backing for pins; portraits composite on top"),
 ("P06", 6, "six-slot TIP issue strip filling in, dashes in the empty slots; caption 'A dash = not graded, not zero'",
  "a row of six empty square paper windows with thin ink borders, four of them filled with flat pale grey paper, two with soft teal paper behind, top-down, symmetrical", "backing for the six slots"),
 ("P07", 7, "Donalds and Jolly portraits split screen with three empty chips (governor)",
  "a clean split of the frame into two halves: left half ink-black paper, right half pale teal paper, a thin torn-paper seam between them, three small blank paper circles floating in a row above the seam", "split backdrop"),
 ("P08", 8, "poll bars 49 and 47 with caption UNF, 1,471 likely voters, Oct 12-19, margin of error 2.81",
  "two horizontal paper strips of nearly equal length, one ink black and one teal, lying on warm off-white paper with tiny graph-paper grid lines, top-down", "backing for the bars"),
 ("P09", 9, "market chip '83¢' with 'Kalshi · Republican party contract · price, not vote share'",
  "a blank paper price tag on a thin string swinging gently against a plain off-white paper wall, mustard-yellow tag, long soft shadow", "backing for the chip"),
 ("P10", 10, "two bars '$107.6M' and '$6.4M' labeled committee money reported as of Sept 11, includes transfers",
  "two stacks of blank paper slips of very different heights standing side by side on an off-white surface, one tall in ink black and one short in teal, side light", "backing for the two bars"),
 ("P11", 11, "three chips lined up and stamped: ASKS VOTERS, SHOWS TRADERS, SHOWS FUNDING",
  "three identical blank paper stamps with round bases lined up in a row on off-white paper, each leaving a faint blank circular imprint, top-down", "backing for the three stamps"),
 ("P12", 12, "Senate card: Moody and Nixon portraits at equal size, 'U.S. SENATE · SPECIAL ELECTION'",
  "a tall cut-paper arch in teal framing a plain off-white inner space, small mustard-yellow star-free geometric dots along the top, symmetrical, ceremonial but abstract", "frame around the Senate card"),
 ("P13", 13, "Nixon portrait enlarged; Vindman name card 'primary winner over reported $14.5M raised through June (WFLX)'",
  "a single spotlight cone cut from pale yellow paper falling on an empty paper stage, deep teal paper curtains at the edges, no figure", "stage light behind the portrait"),
 ("P14", 14, "poll bars 49 and 45 with portraits at equal size; 'UNF · Oct 12-19 · margin of error 2.81'",
  "two horizontal paper strips, ink black slightly longer than teal, resting on warm off-white paper, a thin mustard-yellow ruler line across them", "backing for the bars"),
 ("P15", 15, "gap marker sliding from 8 to 4: 'July: 8 (one report, WLRN) → now: 4'",
  "a paper slider track with a mustard-yellow paper marker caught mid-slide, motion-blurred edge, plain off-white background", "backing for the marker"),
 ("P16", 16, "two equal quote cards: Moody 'declined to debate' and 'will keep engaging with voters' (News Service of Florida)",
  "two identical blank paper cards side by side with a thin gap, ink border, soft shadow, plain off-white background, perfectly symmetrical", "backing for the cards"),
 ("P17", 17, "everything clears; Nixon and Moody side by side; 'A challenger who beat the money favorite, four points back.' then 'Polls are snapshots. Ballots are not.'",
  "an empty open field of off-white paper with a low sunrise of concentric mustard-yellow and teal paper semicircles on the horizon, rays of thin paper strips, hopeful, calm, very clean", "peak-moment backdrop"),
 ("P18", 18, "end card: 'Early voting: Oct 24–31, all 67 counties', 'link in bio', credits, 'Narration is synthetic.'",
  "a calm paper-cut coastline at dawn: a pale teal sea, a sliver of off-white beach, a few stylized paper palm fronds, mustard-yellow sun just above the horizon, a large empty space for text", "end card backdrop"),
]

# transitions: (id, from segment, to segment, motion prompt for the generated plate video, deterministic fallback, seconds)
TRANS = [
 ("T01", 1, 2, "The paper horizon folds forward like a card and thirty paper tiles unfold out of it into a neat grid; locked-off camera, slow, smooth.", "tiles scale in from the center with a 60 ms stagger", 1.0),
 ("T02", 2, 3, "The thirty tiles slide together and merge into one pale-teal paper peninsula; locked-off camera.", "tiles morph (mask) into the map outline", 1.0),
 ("T03", 3, 4, "Camera pushes in slowly on the paper peninsula as its inner layers shift and a blade re-cuts one edge; thin paper strips curl away.", "map scale-up 140% with the two districts highlighting", 1.0),
 ("T04", 4, 5, "The cut paper layers settle; three mustard-yellow paper discs drop in one after another and bounce once.", "three pins drop with a 3-frame bounce", 1.0),
 ("T05", 5, 6, "The three discs slide apart and each splits into two, becoming a row of six small paper windows.", "pins become six slots by mask", 1.0),
 ("T06", 6, 7, "The six windows slide to the edges and the frame splits into an ink half and a teal half with a torn seam.", "vertical wipe with a torn-edge matte", 1.0),
 ("T07", 7, 8, "The seam holds while two horizontal paper strips slide in from the left and stop at nearly equal lengths.", "bars grow from zero over 0.6 s", 1.0),
 ("T08", 8, 9, "The strips fold away and a paper price tag drops on its string and swings once.", "cross-dissolve with the tag easing in", 1.0),
 ("T09", 9, 10, "The tag swings out of frame and two stacks of paper slips of different heights rise from the bottom edge.", "two bars rise from the baseline", 1.0),
 ("T10", 10, 11, "Both stacks slide into a row and three round paper stamps press down in turn, each leaving a faint blank imprint.", "three chips stamp in at 10-frame intervals", 1.0),
 ("T11", 11, 12, "A hard cut: a single flash of brass-colored paper sweeps across the frame left to right on the beat, revealing a tall teal paper arch.", "hard cut on the beat with a 4-frame yellow flash", 0.5),
 ("T12", 12, 13, "The arch's inner space darkens slightly and a cone of pale yellow paper light falls onto an empty stage between teal curtains.", "spotlight mask grows over 0.6 s", 1.0),
 ("T13", 13, 14, "The stage light lowers and two horizontal paper strips slide up into place, ink slightly longer than teal.", "bars grow, portraits scale to equal size", 1.0),
 ("T14", 14, 15, "The strips fall away and a paper slider track appears; its yellow marker begins to slide.", "marker animates from 8 to 4 over 1 s", 1.0),
 ("T15", 15, 16, "The slider track folds in half and becomes two identical blank paper cards side by side.", "two cards slide in from opposite sides at the same speed", 1.0),
 ("T16", 16, 17, "A broad sweep of paper strips clears everything to an empty off-white field in one smooth motion.", "wipe to off-white, then hold 6 frames", 1.0),
 ("T17", 17, 18, "Concentric yellow and teal paper semicircles rise on the horizon like a sunrise and settle; a pale sea and a sliver of beach slide in beneath.", "sunrise shapes rise over 1 s, end card fades in", 1.0),
]

def plate_prompt(desc): return f"{desc}, {STYLE}{SUFFIX}"
def motion_prompt(m): return f"{m} Cut-paper collage style, matte paper, locked-off camera, slow and smooth, no text, no people, no faces, no logos, no flags."

rows = []
for pid, seg, l1, desc, role in PLATES:
    rows.append({"id": pid, "type": "plate", "segment": seg, "layer1_deterministic": l1, "prompt": plate_prompt(desc), "role": role, "start": "", "end": "", "seconds": 5.0, "fallback": ""})
for tid, a, b, m, fb, sec in TRANS:
    rows.append({"id": tid, "type": "transition", "segment": f"{a}->{b}", "layer1_deterministic": "", "prompt": motion_prompt(m), "role": "video from the two plates", "start": f"P{a:02d}", "end": f"P{b:02d}", "seconds": sec, "fallback": fb})
out_csv = ROOT / "docs/video/fl_video_prompts.csv"
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

md = ["""# Florida video: visual direction, plate prompts and transition prompts

2026-10-24 · for the 90-second script in `FLORIDA_VIDEO_SCRIPT_AND_PITCH.md` · machine-readable: `fl_video_prompts.csv` (generated from the same table as this file by `tools/video/build_visual_direction.py`).

## Yes: the direction exists, and here is how it is applied
The approved brief (schema 07, section 6) says: render true numbers, names, rankings and ballot facts **deterministically in the edit, never inside generated imagery**, and use generated imagery only for **non-evidentiary visual transitions** with start and end frames and motion instructions; disclose it; never present AI visuals as footage of real events; use real, licensed portraits, not AI caricatures. This sheet gives you that: 18 plate prompts (one backdrop per segment), 17 transition prompts (the motion from one plate to the next), and the deterministic frames each plate sits behind.

## Two layers
| Layer | What it carries | How it is made | Rule |
|---|---|---|---|
| **1 Deterministic** | every name, number, label, chart, map, portrait and credit | HTML cards rendered by `tools/social/render_cards.py` (extend to 1080 x 1920), the real Old Capitol photo, public-domain portraits | the only layer a viewer reads for information |
| **2 Generated** | backdrops and the motion between segments | Midjourney (or any image and image-to-video tool) from the prompts below | abstract paper shapes only: no person, face, text, number, logo, flag or party color; never evidence |

Composite order, back to front: plate (generated) → layer-1 frame (deterministic, with transparent margins) → captions. A transition is a short generated video that plays between the end of one layer-1 frame and the start of the next; the layer-1 frames fade over the first and last 6 frames of it. Because the AI never sees or renders a number, a morph can never garble a fact.

## Style bible (applies to every prompt)
- Look: editorial cut-paper collage, flat matte paper, soft even light, subtle risograph grain, premium magazine illustration.
- Palette: paper #f5f2eb, ink #1c1d1b, teal #145b5d, annotation yellow #dfca00. No red, no blue, no party colors.
- Camera: locked-off or a slow push; one motion per transition; nothing handheld.
- Never generate: people, faces, hands, portraits, flags, logos, political symbols, text, letters, numbers, real buildings (the Capitol is the real photo), ballots with names, "documentary" footage, news-style screenshots.
- Reference consistency: pick the best plate (usually P03) and reuse it as a style reference (`--sref <image URL>` in Midjourney) for the others so the set looks like one piece.
- Every prompt below is already ready to paste; it ends with `--ar 9:16 --style raw --stylize 100 --no ...`. Set the model version flag to the current one in your account.

## Plate prompts (18)
"""]
md.append("| ID | Seg | Layer-1 frame it sits behind | Prompt (paste as is) |\n|---|---|---|---|")
for pid, seg, l1, desc, role in PLATES:
    md.append(f"| {pid} | {seg} | {l1} | `{plate_prompt(desc)}` |")
md.append("""
## Transition prompts (17)
For each: generate the start plate and the end plate, then run image-to-video with the start frame, the end frame (if your tool supports one) and the motion prompt. In Midjourney: Animate, manual, add the end frame, low motion. If a tool cannot take an end frame, generate from the start plate and cut to the next plate on the last frame. Use the deterministic fallback whenever a generated clip shows any text, face or object that is not in the prompt.

| ID | From → to | Start plate → end plate | Motion prompt | Length | Deterministic fallback |
|---|---|---|---|---|---|""")
for tid, a, b, m, fb, sec in TRANS:
    md.append(f"| {tid} | {a} → {b} | P{a:02d} → P{b:02d} | `{motion_prompt(m)}` | {sec:g} s | {fb} |")
md.append("""
Transition 11 (the Senate cut) is deliberately a hard cut on the beat: the viewer's brain should feel a new chapter start, and the music brass stab lands on it.

## What the generated layer must never do
- Imply a candidate, party, flag or event. The sunrise in P17 and P18 is an abstract shape, not a symbol of any campaign.
- Contain text. Any letter-like marks in a plate means regenerate or take the fallback; type is always layer 1.
- Be described as footage. Caption line: "Background graphics are AI-generated illustrations. Narration is synthetic."

## Workflow and checks
1. Render the 18 layer-1 frames at 1080 x 1920 with transparent margins (next step; the data and portraits already exist). Keep text out of the top 250 and bottom 340 px.
2. Generate four options per plate; choose the one with the calmest center (the layer-1 content sits there), the cleanest edges and no stray marks. Log each pick in `docs/video/generated_assets.csv`: id, tool and version, date, prompt, job or seed ID, plan and commercial-use terms checked, file path.
3. Generate the 17 transition clips; trim each to the length in the table; check frame by frame for text, faces or distortions.
4. Assemble in the editor: plate, layer-1 frame, captions, transition, music (Artlist brass-techno bed ducked under narration), narration.
5. QA: the same fact check as the script (`FLORIDA_VIDEO_CONCEPT.md` callout sheet), a silent playthrough with captions only, a phone-size check, and a last read of the end-card credits and disclosures.
6. Rights: confirm the image tool's plan allows commercial use of outputs before publishing; confirm the Artlist license covers this use.

## What I can build now
All 18 layer-1 frames from existing data and portraits (one renderer run), the composite order sheet, and the asset log template. The generated plates and clips need your image tool, so they are the only part I cannot produce here.
""")
(ROOT / "docs/video/FLORIDA_VISUAL_DIRECTION_AND_PROMPTS.md").write_text("\n".join(md), encoding="utf-8")
print(len(PLATES), "plates", len(TRANS), "transitions")
