#!/usr/bin/env python3
"""Build SVG geometry for Florida's 2026 congressional districts.

Source (official): Florida Legislature, Office of Economic & Demographic Research, plan EOGPCRP2026 (HB 1-D, enacted May 2026)
  https://www.edr.state.fl.us/Content/redistricting/2026redistricting/EOGPCRP2026.zip
County names (context only): U.S. Census cartographic boundary file cb_2024_us_county_500k.

    python3 tools/elections/build_fl_geometry.py <path-to-EOGPCRP2026.shp> <path-to-cb_2024_us_county_500k.shp>

Writes data/elections/FL/districts.json. Requires geopandas + shapely.
"""
import json, sys, math, hashlib
from pathlib import Path
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[2]
shp, cty = sys.argv[1], sys.argv[2]
g = gpd.read_file(shp).to_crs(4326)
g["n"] = g["DISTRICT"].astype(int)
counties = gpd.read_file(cty)
counties = counties[counties["STATEFP"] == "12"].to_crs(5070)
g5070 = g.to_crs(5070)

minx, miny, maxx, maxy = g.total_bounds
k = math.cos(math.radians((miny + maxy) / 2))
W = 1000.0
scale = W / ((maxx - minx) * k)
H = (maxy - miny) * scale

def px(lon, lat):
    return round((lon - minx) * k * scale, 1), round((maxy - lat) * scale, 1)

def path_for(geom):
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    d = []
    for p in polys:
        if p.area < 1e-5:
            continue
        for ring in [p.exterior] + list(p.interiors):
            pts = [px(*c) for c in ring.coords]
            dedup = [pts[0]] + [q for a, q in zip(pts, pts[1:]) if q != a]
            if len(dedup) >= 4:
                d.append("M" + "L".join(f"{x},{y}" for x, y in dedup) + "Z")
    return "".join(d)

out = {"source": {"plan": "EOGPCRP2026", "bill": "HB 1-D (2026 special session)", "publisher": "Florida Legislature EDR",
                  "url": "https://www.edr.state.fl.us/Content/redistricting/2026redistricting/EOGPCRP2026.zip",
                  "zip_sha256": hashlib.sha256((ROOT / "data/elections/FL/captures/EOGPCRP2026.zip").read_bytes()).hexdigest(),
                  "counties_source": "U.S. Census cb_2024_us_county_500k"},
       "viewbox": [0, 0, int(W), round(H)], "districts": {}}
simp = g.copy()
simp["geometry"] = g.geometry.simplify(0.004, preserve_topology=True)
for _, r in simp.iterrows():
    n = int(r["n"])
    full = g5070[g5070["n"] == n].geometry.iloc[0]
    ov = []
    for _, c in counties.iterrows():
        a = full.intersection(c.geometry).area
        if a > 0:
            ov.append((a, c["NAME"]))
    ov.sort(reverse=True)
    tot = sum(a for a, _ in ov)
    principal = [(nm, round(100 * a / tot)) for a, nm in ov if a / tot >= 0.08][:4]
    cx, cy = px(*r.geometry.representative_point().coords[0])
    out["districts"][str(n)] = {"path": path_for(r.geometry), "label_xy": [cx, cy], "counties": principal,
                                "population": int(r["TOTAL"]) if str(r["TOTAL"]).isdigit() else r["TOTAL"]}
out["state_outline"] = path_for(simp.union_all().simplify(0.004)) if hasattr(simp, "union_all") else path_for(simp.unary_union.simplify(0.004))
(ROOT / "data/elections/FL/districts.json").write_text(json.dumps(out, separators=(",", ":")))
print({"districts": len(out["districts"]), "viewbox": out["viewbox"], "bytes": len(json.dumps(out))})
for n in ("1", "14", "20", "25"):
    print(n, out["districts"][n]["counties"])
