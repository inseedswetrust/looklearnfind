#!/usr/bin/env python3
"""Start a video spec for another state from the Florida one. The reusable parts (frame types, animation timelines, plate prompts, transition prompts, timing, rules) are kept;
everything state-specific (narration, on-screen text, params, facts) becomes <fill> and the validator refuses the spec until each one is filled from published, checked articles.

    python3 tools/video/init_state_spec.py <ST> [source-spec.json]       writes data/video/<st>_<year>_state_of_the_race.json
"""
import copy, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
st = sys.argv[1].upper()
src = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "data/video/fl_2026_state_of_the_race.json"
spec = json.loads(src.read_text(encoding="utf-8"))
new = copy.deepcopy(spec)
new["id"] = f"{st.lower()}-2026-state-of-the-race"
new["state"] = st
new["as_of"] = "<fill>"
new["facts"] = [{"id": "F-01", "statement": "<fill>", "numbers": [], "source": "<fill>", "status": "VERIFIED", "never_say": "<fill>", "refresh": True}]
for s in new["segments"]:
    s["on_screen"] = ["<fill>"]
    s["vo"] = "<fill>"
    s["facts"] = []
    s["params"] = {k: "<fill>" for k in s.get("params", {})}
    s.pop("structural", None)
new["credits"] = ["<fill>"]
out = ROOT / f"data/video/{st.lower()}_2026_state_of_the_race.json"
out.write_text(json.dumps(new, indent=1, ensure_ascii=False), encoding="utf-8")
print("wrote", out, "- fill every <fill>, then run: python3 tools/video/build_video_pack.py", out.relative_to(ROOT))
