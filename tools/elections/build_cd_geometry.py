#!/usr/bin/env python3
"""Build SVG geometry for a state's congressional districts from the U.S. Census cartographic boundary file (public domain).

    python3 tools/elections/build_cd_geometry.py IL <path-to-cb_2024_us_cd119_500k.shp> [<path-to-cb_2024_us_county_500k.shp>]

Source: https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_cd119_500k.zip (119th Congress districts; Illinois's plan is unchanged for 2026).
Writes data/elections/<ST>/districts.json in the same shape as build_fl_geometry.py. Counties are optional context and are left empty without the county file.
Requires geopandas + shapely.
"""
import json, sys, math, hashlib
from pathlib import Path
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[2]
FIPS = {"IL": "17", "MI": "26", "NY": "36", "NJ": "34", "MN": "27", "PA": "42"}
st, shp = sys.argv[1], sys.argv[2]
cty = sys.argv[3] if len(sys.argv) > 3 else None
g = gpd.read_file(shp)
g = g[g["STATEFP"] == FIPS[st]].to_crs(4326)
g["n"] = g["CD119FP"].astype(int)
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

zp = ROOT / f"data/elections/{st}/captures/cb_2024_us_cd119_500k.zip"
out = {"source": {"plan": "119th Congress districts (in use for the 2026 election)", "publisher": "U.S. Census Bureau cartographic boundary file cb_2024_us_cd119_500k",
                  "url": "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_cd119_500k.zip",
                  "zip_sha256": hashlib.sha256(zp.read_bytes()).hexdigest() if zp.exists() else "", "counties_source": ""},
       "viewbox": [0, 0, int(W), round(H)], "districts": {}}
simp = g.copy()
simp["geometry"] = g.geometry.simplify(0.004, preserve_topology=True)
for _, r in simp.iterrows():
    n = int(r["n"])
    cx, cy = px(*r.geometry.representative_point().coords[0])
    out["districts"][str(n)] = {"path": path_for(r.geometry), "label_xy": [cx, cy], "counties": [], "population": None}
out["state_outline"] = path_for(simp.union_all().simplify(0.004)) if hasattr(simp, "union_all") else path_for(simp.unary_union.simplify(0.004))
(ROOT / f"data/elections/{st}/districts.json").write_text(json.dumps(out, separators=(",", ":")))
print({"districts": len(out["districts"]), "viewbox": out["viewbox"], "bytes": len(json.dumps(out))})
