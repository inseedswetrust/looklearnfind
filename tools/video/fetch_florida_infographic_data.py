"""Fetch the evidence the Florida infographics draw on, and store it with provenance.

Writes under assets/video/florida-2026/infographics/data/:
  senate_dem_primary_county_2026-08-18.csv   county votes, Florida Division of Elections (floridaelectionwatch.gov)
  senate_dem_primary_state_2026-08-18.json   statewide totals from the same page
  fl_counties_cb2024_500k.geojson            Florida counties, U.S. Census cb_2024_us_county_500k (public domain)
  sources.json                               URL, retrieval time and sha256 for each file

Usage: PYTHONUTF8=1 python tools/video/fetch_florida_infographic_data.py
Network required. Nothing here writes outside the data folder.
"""
import csv, hashlib, html as htmllib, io, json, re, sys, zipfile, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets/video/florida-2026/infographics/data"
UA = {"User-Agent": "Mozilla/5.0 (LLF research; jmarlow989@gmail.com)"}
DOE = "https://floridaelectionwatch.gov"
CENSUS = "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip"


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
        return r.read()


def text(html):
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S))))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    prov = {}

    state = get(f"{DOE}/FederalOffices/USSenator").decode("utf8", "ignore")
    t = text(state)
    m = re.search(r"Angie Nixon DEM ([\d,]+) ([\d.]+)% Alex Vindman DEM ([\d,]+) ([\d.]+)% Total\s+([\d,]+)", t)
    if not m:
        sys.exit("statewide Democratic Senate block not found; page layout changed")
    n, np_, v, vp, tot = m.groups()
    n, v, tot = (int(x.replace(",", "")) for x in (n, v, tot))
    assert n + v == tot, "statewide totals do not add up"
    sj = {"contest": "United States Senator, Democratic primary, Aug 18 2026", "nixon": n, "vindman": v, "total": tot,
          "nixon_pct_doe": float(np_), "vindman_pct_doe": float(vp), "source": f"{DOE}/FederalOffices/USSenator", "retrieved_utc": now}
    (OUT / "senate_dem_primary_state_2026-08-18.json").write_text(json.dumps(sj, indent=1), encoding="utf8")
    prov["state"] = {"url": sj["source"], "retrieved_utc": now, "sha256": hashlib.sha256(state.encode()).hexdigest()}

    page = get(f"{DOE}/ContestResultsByCounty/120002").decode("utf8", "ignore")
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", page, flags=re.S)
    out = []
    for r in rows[1:]:
        cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, flags=re.S)]
        cells = [c for c in cells if c]
        if len(cells) >= 3 and not cells[0].lower().startswith("total"):
            out.append((cells[0], int(cells[1].replace(",", "")), int(cells[2].replace(",", ""))))
    if len(out) != 67:
        sys.exit(f"expected 67 counties, found {len(out)}")
    assert sum(r[1] for r in out) == n and sum(r[2] for r in out) == v, "county rows do not sum to the statewide totals"
    with open(OUT / "senate_dem_primary_county_2026-08-18.csv", "w", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        w.writerow(["county", "nixon", "vindman"])
        w.writerows(out)
    prov["counties"] = {"url": f"{DOE}/ContestResultsByCounty/120002", "retrieved_utc": now, "sha256": hashlib.sha256(page.encode()).hexdigest()}

    import geopandas as gpd
    z = get(CENSUS)
    tmp = OUT / "_cb.zip"
    tmp.write_bytes(z)
    g = gpd.read_file(f"zip://{tmp}")
    g = g[g["STATEFP"] == "12"][["NAME", "geometry"]].to_crs(4326)
    assert len(g) == 67
    g.to_file(OUT / "fl_counties_cb2024_500k.geojson", driver="GeoJSON")
    prov["geometry"] = {"url": CENSUS, "retrieved_utc": now, "sha256": hashlib.sha256(z).hexdigest()}
    tmp.unlink()
    (OUT / "sources.json").write_text(json.dumps(prov, indent=1), encoding="utf8")
    print("ok: 67 counties, Nixon", n, "Vindman", v)


if __name__ == "__main__":
    main()
