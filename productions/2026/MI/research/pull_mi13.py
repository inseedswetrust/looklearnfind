"""MI-13 FEC pull for MI-A3: Schedule E for McKinney and Thanedar (Thanedar is not on the November ballot, so he is not in the roster), committee metadata
for every committee that spent, and candidate totals. Run from the repository root with FEC_API_KEY set:

    python productions/2026/MI/research/pull_mi13.py

Writes fec_ie_MI13.json (same shape as fetch_fec_ie.py output), fec_committees_MI13.json and fec_totals_MI13.json beside this file.
Then: python tools/elections/reconcile_ie.py productions/2026/MI/research/fec_ie_MI13.json productions/2026/MI/research/fec_committees_MI13.json productions/2026/MI/research/mi13_reconciled.json H6MI13254 H2MI13204
"""
import json, os, shutil, subprocess, sys, time, urllib.parse, urllib.request, datetime
from pathlib import Path

R = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
KEY = os.environ["FEC_API_KEY"]
IDS = {"H6MI13254": "Donavan McKinney", "H2MI13204": "Shri Thanedar"}

tmp = R / "data/elections/_MI13"
tmp.mkdir(exist_ok=True)
(tmp / "candidates.json").write_text(json.dumps({"as_of_utc": "", "issues": [], "candidates": [
    {"id": k, "name": v, "race": "house-13", "fec_candidate_id": k} for k, v in IDS.items()]}), encoding="utf-8")
try:
    subprocess.run([sys.executable, str(R / "tools/elections/fetch_fec_ie.py"), "_MI13", str(HERE / "fec_ie_MI13.json"), "house-13"], check=True, cwd=R)
finally:
    shutil.rmtree(tmp, ignore_errors=True)


def get(path, **q):
    q["api_key"] = KEY
    u = "https://api.open.fec.gov/v1" + path + "?" + urllib.parse.urlencode(q, doseq=True)
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "LLF-election-desk"}), timeout=90) as r:
                return json.loads(r.read())
        except Exception:
            if a == 3:
                raise
            time.sleep(2 + 3 * a)


pull = json.loads((HERE / "fec_ie_MI13.json").read_text(encoding="utf-8"))
cids = sorted({r["committee_id"] for c in pull["candidates"].values() for r in c["transactions"]})
old = json.loads((HERE / "fec_committees_MI10.json").read_text(encoding="utf-8"))["committees"]
comm = {}
for cid in cids:
    if cid in old:
        comm[cid] = old[cid]
        continue
    j = get(f"/committee/{cid}/")["results"][0]
    comm[cid] = {k: j.get(k) for k in ("name", "committee_type", "committee_type_full", "designation", "designation_full", "organization_type_full", "party_full", "state", "connected_organization_name", "treasurer_name", "filing_frequency")}
(HERE / "fec_committees_MI13.json").write_text(json.dumps({"fetched": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "committees": comm}, indent=1), encoding="utf-8")
tot = {}
for fid in IDS:
    j = get(f"/candidate/{fid}/totals/", cycle=2026)["results"]
    tot[fid] = j
(HERE / "fec_totals_MI13.json").write_text(json.dumps({"fetched": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "totals": tot}, indent=1), encoding="utf-8")
print("committees", len(comm), "totals", {k: len(v) for k, v in tot.items()})
