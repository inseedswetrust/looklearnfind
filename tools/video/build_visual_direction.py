#!/usr/bin/env python3
"""Visual direction, prompts and animation sheets for a video, generated from the spec (the single source of truth).

    python3 tools/video/build_visual_direction.py [spec.json]       (also called by build_video_pack.py)

Writes docs/video/FLORIDA_VISUAL_DIRECTION_AND_PROMPTS.md, docs/video/fl_video_prompts.csv (plates, transitions, extras) and docs/video/fl_video_animations.csv.
Two layers: LAYER 1 is deterministic (data cards, real public-domain portraits, real Capitol photo) and carries every name and number; LAYER 2 is generated plates and
transitions that carry no information. Nothing generated is evidence, and nothing generated contains a person, a face, text, a number or a logo.
"""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STYLE = ("editorial cut-paper collage, flat matte paper texture, warm off-white paper background (#f5f2eb), deep teal (#145b5d) and ink black (#1c1d1b) shapes, "
         "small accents of mustard yellow (#dfca00), subtle risograph grain, soft even studio light, minimal, graphic, premium magazine illustration, vertical composition")
NEG = "text, letters, numbers, words, logos, flags, people, faces, hands, portraits, red, blue, political symbols, photorealism, 3D render, watermark, signature"
SUFFIX = " --ar 9:16 --style raw --stylize 100 --no " + NEG


def plate_prompt(desc):
    return f"{desc}, {STYLE}{SUFFIX}"


def motion_prompt(m):
    return f"{m} Cut-paper collage style, matte paper, locked-off camera, slow and smooth, no text, no people, no faces, no logos, no flags."


def build(spec):
    segs, trans, extras = spec["segments"], spec["transitions"], spec.get("extras", [])
    plates = {s["plate"]["id"]: s["plate"] for s in segs}
    rows = []
    for s in segs:
        pl = s["plate"]
        rows.append({"id": pl["id"], "type": "plate", "segment": s["n"], "layer1_deterministic": f"{s['frame']}: " + " / ".join(s["on_screen"]), "prompt": plate_prompt(pl["desc"]), "role": pl["role"],
                     "start": "", "end": "", "seconds": s.get("seconds", spec.get("segment_seconds", 5)), "fallback": ""})
    for t in trans:
        rows.append({"id": t["id"], "type": "transition", "segment": f"{t['from']}->{t['to']}", "layer1_deterministic": "", "prompt": motion_prompt(t["motion"]), "role": "video from the two plates",
                     "start": segs[t["from"] - 1]["plate"]["id"], "end": segs[t["to"] - 1]["plate"]["id"], "seconds": t["seconds"], "fallback": t["fallback"]})
    for x in extras:
        rows.append({"id": x["id"], "type": "extra", "segment": "", "layer1_deterministic": f"{x['kind']}: {x['layer1']}", "prompt": plate_prompt(plates[x["plate_id"]]["desc"]) if x["plate_id"] in plates else "",
                     "role": f"reuse plate {x['plate_id']}", "start": "", "end": "", "seconds": "", "fallback": ""})
    with open(ROOT / "docs/video/fl_video_prompts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(ROOT / "docs/video/fl_video_animations.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["segment", "frame", "element", "action", "start_s", "duration_s", "easing", "stagger_ms"])
        for s in segs:
            for a in s["animations"]:
                w.writerow([s["n"], s["frame"], a["element"], a["action"], a["start"], a["duration"], a["easing"], a.get("stagger_ms", "")])

    md = [f"""# Visual direction, plate prompts and transition prompts ({spec['id']})

Generated from `data/video/{spec['id'].replace('-', '_')}.json` by `tools/video/build_visual_direction.py`; do not edit by hand. Machine-readable: `fl_video_prompts.csv` (plates, transitions, extras) and `fl_video_animations.csv` (in-frame animation timelines).

## The rule behind every choice
The approved brief (schema 07, section 6): render true numbers, names, rankings and ballot facts **deterministically in the edit, never inside generated imagery**; use generated imagery only for **non-evidentiary visual transitions** with start and end frames and motion instructions; disclose it; never present AI visuals as footage of real events; use real, licensed portraits, not AI caricatures.

## Two layers
| Layer | What it carries | How it is made | Rule |
|---|---|---|---|
| **1 Deterministic** | every name, number, label, chart, map, portrait and credit | HTML frames rendered by `tools/video/build_video_pack.py` (1080 x 1920, on paper and transparent), the real Old Capitol photo, public-domain portraits | the only layer a viewer reads for information |
| **2 Generated** | backdrops and the motion between segments | Midjourney (or any image and image-to-video tool) from the prompts below | abstract paper shapes only: no person, face, text, number, logo, flag or party color; never evidence |

Composite order, back to front: plate (generated) → layer-1 frame (`segNN_alpha.png`) → captions. A transition is a short generated clip between two plates; the layer-1 frames fade over the first and last 6 frames of it. The AI never sees or renders a number, so a morph can never garble a fact.

## Style bible (every prompt)
- Look: editorial cut-paper collage, flat matte paper, soft even light, subtle risograph grain, premium magazine illustration.
- Palette: paper #f5f2eb, ink #1c1d1b, teal #145b5d, annotation yellow #dfca00. No red, no blue, no party colors.
- Camera: locked-off or one slow push; one motion per transition; nothing handheld.
- Never generate: people, faces, hands, portraits, flags, logos, political symbols, text, letters, numbers, real buildings (the Capitol is the real photo), ballots with names, documentary or news-style footage.
- Consistency: pick the best plate (usually P03) and reuse it as a style reference (`--sref <image URL>` in Midjourney) for the rest.
- Each prompt already ends with `--ar 9:16 --style raw --stylize 100 --no ...`; set the model version flag to the current one in your account.

## Plate prompts
"""]
    md.append("| ID | Seg | Layer-1 frame it sits behind | Prompt (paste as is) |\n|---|---|---|---|")
    for r in rows:
        if r["type"] == "plate":
            md.append(f"| {r['id']} | {r['segment']} | {r['layer1_deterministic']} | `{r['prompt']}` |")
    md.append("""
## Transition prompts
Generate the start plate and the end plate, then image-to-video with the start frame, the end frame (if the tool supports one) and the motion prompt. In Midjourney: Animate, manual, add the end frame, low motion. If a tool cannot take an end frame, generate from the start plate and cut to the next plate on the last frame. Use the deterministic fallback whenever a clip shows text, a face or an object not in the prompt.

| ID | From → to | Start plate → end plate | Motion prompt | Length | Deterministic fallback |
|---|---|---|---|---|---|""")
    for r in rows:
        if r["type"] == "transition":
            md.append(f"| {r['id']} | {r['segment'].replace('->', ' → ')} | {r['start']} → {r['end']} | `{r['prompt']}` | {r['seconds']} s | {r['fallback']} |")
    md.append("""
## Extras (cover, Story opener, loop)
| ID | What | Layer-1 content | Plate |
|---|---|---|---|""")
    for x in extras:
        md.append(f"| {x['id']} | {x['kind']} | {x['layer1']} | {x['plate_id']} |")
    md.append("""
## In-frame animations (deterministic layer)
These are not generated. They are keyframe timelines for the editor or a scripted renderer: each row says which element moves, how, when and for how long. The full table is `fl_video_animations.csv`.

| Seg | Element | Action | Start | Duration | Easing |
|---|---|---|---|---|---|""")
    for s in segs:
        for a in s["animations"]:
            md.append(f"| {s['n']} | {a['element']} | {a['action']} | {a['start']} s | {a['duration']} s | {a['easing']} |")
    md.append("""
## What the generated layer must never do
- Imply a candidate, party, flag or event. The sunrise plates are abstract shapes, not a symbol of any campaign.
- Contain text. Any letter-like marks mean regenerate or take the fallback; type is always layer 1.
- Be described as footage. Caption line: "Background graphics are AI-generated illustrations. Narration is synthetic."

## Workflow and checks
1. Run `python3 tools/video/build_video_pack.py <spec>`: it validates the spec, renders the layer-1 frames and rewrites this file.
2. Generate four options per plate; choose the one with the calmest center, cleanest edges and no stray marks. Log each pick in `docs/video/generated_assets.csv` (template: `generated_assets_template.csv`).
3. Generate the transition clips; trim to the length in the table; check frame by frame for text, faces or distortions.
4. Assemble: plate, layer-1 frame, captions, transition, music (ducked under narration), narration.
5. QA with the fact sheet: a silent playthrough with captions only, a phone-size check, and a last read of the end-card credits and disclosures.
6. Rights: confirm the image tool's plan allows commercial use of outputs and the music license covers this use before publishing.
""")
    (ROOT / "docs/video/FLORIDA_VISUAL_DIRECTION_AND_PROMPTS.md").write_text("\n".join(md), encoding="utf-8")
    (ROOT / "docs/video/generated_assets_template.csv").write_text("id,tool_and_version,date,prompt,job_or_seed_id,plan_and_commercial_terms_checked,file_path,chosen_by,notes\n", encoding="utf-8")
    return len([r for r in rows if r["type"] == "plate"]), len([r for r in rows if r["type"] == "transition"])


if __name__ == "__main__":
    sp = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/video/fl_2026_state_of_the_race.json"
    print(build(json.loads(sp.read_text(encoding="utf-8"))))
