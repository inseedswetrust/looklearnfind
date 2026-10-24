"""Deterministic Florida infographic masters and start/end frames (1080 x 1920).

Every graphic is built from one scene definition: frame B is the SAME assets as frame A moved, scaled,
cropped or revealed by transform. No generated imagery, no regenerated faces. Facts come from FACTS below
and from the files written by tools/video/fetch_florida_infographic_data.py.

Usage: PYTHONUTF8=1 python tools/video/build_florida_infographics.py [--no-render]
Output: assets/video/florida-2026/infographics/<IG-id>/  (layered SVG masters, start/end PNG, build notes)
"""
import base64, csv, io, json, math, random, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "assets/video/florida-2026/infographics"
DATA = BASE / "data"
PORT = ROOT / "static/img/elections/portraits"
CAP = BASE / "captures"
W, H = 1080, 1920
PAPER, INK, BODY, TEAL, AMBER = "#FEF9F3", "#001D33", "#152225", "#01616F", "#B58E62"
GRAY, LGRAY, CARD = "#6B747A", "#C9CCCC", "#FFFFFF"
SERIF = "Newsreader, Georgia, 'Times New Roman', serif"
SANS = "Arial, Helvetica, sans-serif"
FONT_FILE = ROOT / "static/fonts/newsreader-latin-opsz-normal.woff2"
GEORGIA = "C:/Windows/Fonts/georgia.ttf"
GEORGIAB = "C:/Windows/Fonts/georgiab.ttf"
ARIAL = "C:/Windows/Fonts/arial.ttf"
ARIALB = "C:/Windows/Fonts/arialbd.ttf"

# Photos: (file, credit, license, eye_fraction_of_height)
PHOTOS = {
    "nixon": (PORT / "90009.jpg", "Florida House of Representatives", "Public domain", 0.33),
    "vindman": (DATA.parent / "src/vindman_2019.jpg", "Mykola Lazarenko / Presidential Administration of Ukraine, 2019", "CC BY 4.0", 0.30),
    "moody": (PORT / "89119.jpg", "U.S. Senate Photography Service", "Public domain", 0.33),
    "donalds": (PORT / "89042.jpg", "U.S. Congress", "Public domain", 0.31),
    "jolly": (PORT / "89243.jpg", "Wikimedia Commons (official)", "Public domain", 0.30),
    "castor": (PORT / "88870.jpg", "U.S. Government", "Public domain", 0.30),
    "beltran": (PORT / "91313.jpg", "Florida House of Representatives", "Public domain", 0.31),
}

# ---------------------------------------------------------------- measuring and svg helpers
_fc = {}


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


def tw(text, size, face="serif", bold=False):
    p = (GEORGIAB if bold else GEORGIA) if face == "serif" else (ARIALB if bold else ARIAL)
    return font(p, size).getlength(text)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, size, maxw, face="serif", bold=False):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if tw(t, size, face, bold) <= maxw or not cur:
            cur = t
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def T(x, y, s, size, fill=BODY, weight=400, face="serif", anchor="start", ls=0, op=1, style=""):
    fam = SERIF if face == "serif" else SANS
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}" opacity="{op}" {style}>{esc(s)}</text>')


def TL(x, y, text, size, maxw, lh, fill=BODY, weight=400, face="serif", anchor="start", ls=0):
    """wrapped lines; returns (svg, next_y)"""
    out = []
    for i, ln in enumerate(wrap(text, size, maxw, face, weight >= 600)):
        out.append(T(x, y + i * lh, ln, size, fill, weight, face, anchor, ls))
    return "\n".join(out), y + len(out) * lh


def R(x, y, w, h, fill="none", stroke="none", sw=1, rx=0, op=1, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}" {extra}/>'


def G(id_, inner, transform="", extra=""):
    t = f' transform="{transform}"' if transform else ""
    return f'<g id="{id_}"{t} {extra}>\n{inner}\n</g>'


_img_cache = {}


def photo(key, w, h, scale_up=2):
    """Center-crop (eyes at 38% of height), resize without upscaling beyond 2x display size; returns data URI + crop box."""
    path, _, _, eye = PHOTOS[key]
    ck = (key, w, h)
    if ck in _img_cache:
        return _img_cache[ck]
    im = Image.open(path).convert("RGB")
    sw, sh = im.size
    s = max(w / sw, h / sh)  # cover scale
    cw, ch = min(sw, round(w / s)), min(sh, round(h / s))
    cx0 = (sw - cw) // 2
    ey = eye * sh
    cy0 = int(max(0, min(sh - ch, ey - 0.38 * ch)))
    im = im.crop((cx0, cy0, cx0 + cw, cy0 + ch))
    tw_, th_ = min(cw, w * scale_up), min(ch, h * scale_up)
    if (tw_, th_) != (cw, ch):
        im = im.resize((round(tw_), round(th_)), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=92)
    uri = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    _img_cache[ck] = uri
    return uri


def img(uri, x, y, w, h, id_="", extra=""):
    return f'<image id="{id_}" href="{uri}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" {extra}/>'


def file_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def font_css():
    f = base64.b64encode(FONT_FILE.read_bytes()).decode()
    return ("@font-face{font-family:Newsreader;font-weight:200 800;font-style:normal;"
            f"src:url(data:font/woff2;base64,{f}) format('woff2');}}")


def fibers(seed=7):
    rnd = random.Random(seed)
    out = []
    for _ in range(170):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        l, a = rnd.uniform(18, 70), rnd.uniform(0, math.pi)
        x2, y2 = x + l * math.cos(a), y + l * math.sin(a)
        cx, cy = (x + x2) / 2 + rnd.uniform(-8, 8), (y + y2) / 2 + rnd.uniform(-8, 8)
        out.append(f'<path d="M{x:.0f},{y:.0f}Q{cx:.0f},{cy:.0f} {x2:.0f},{y2:.0f}" stroke="#8a7a62" stroke-width="0.8" fill="none" opacity="{rnd.uniform(.05, .13):.2f}"/>')
    return "\n".join(out)


def chrome(section, source_lines, microlabel=True):
    """Background, fibers, folio, hairline, section title, source block (inside safe zone), bottom microtext."""
    s = [G("paper", R(0, 0, W, H, PAPER) + G("fibers", fibers()))]
    s.append(G("folio",
               T(90, 205, "LOOKLEARNFIND / STATE OF THE RACE", 24, TEAL, 700, "sans", ls=3.2) +
               R(90, 240, 900, 2, INK, op=0.85)))
    if section:
        s.append(G("section", T(90, 300, section, 28, TEAL, 700, "sans", ls=3)))
    lines = [sub for ln in source_lines for sub in wrap(ln, 19, 900, "sans")]
    y0 = 1596 - (len(lines) - 1) * 25  # block bottom-aligned inside the safe zone (ends above y=1610)
    assert y0 >= 1462, f"source block too tall ({len(lines)} lines)"
    src = [T(90, y0 + i * 25, sub, 19, GRAY, 400, "sans") for i, sub in enumerate(lines)]
    s.append(G("source", "\n".join(src)))
    s.append(G("microtext", T(90, 1856, "Sources and candidate records \u2192 LookLearnFind / The Issues Party", 20, GRAY, 400, "sans", ls=0.6)))
    return s


def svg_doc(layers, extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'<defs><style>{font_css()}</style>{extra_defs}</defs>\n' + "\n".join(layers) + "\n</svg>")


# ---------------------------------------------------------------- facts (each with its source)
SRC_DOE = "Florida Division of Elections, official results page for the Aug 18, 2026 Democratic primary (floridaelectionwatch.gov), retrieved Oct 24, 2026."
STATE = json.loads((DATA / "senate_dem_primary_state_2026-08-18.json").read_text(encoding="utf8"))
NIX, VIN, TOT = STATE["nixon"], STATE["vindman"], STATE["total"]
NIX_P, VIN_P = 100 * NIX / TOT, 100 * VIN / TOT
MARGIN = NIX_P - VIN_P  # 12.1


def credit_line(*keys):
    seen, parts = set(), []
    for k in keys:
        _, c, lic, _e = PHOTOS[k]
        t = f"{c} ({lic})"
        if t not in seen:
            seen.add(t)
            parts.append(t)
    return "Photos: " + "; ".join(parts) + "."


# ---------------------------------------------------------------- IG-02 primary result
def ig02(state):
    """state 'A' matchup, 'B' result reveal. The same card assets; B moves, scales and crops them."""
    L = chrome("FLORIDA \u00b7 AUGUST 18 PRIMARY", [SRC_DOE, credit_line("nixon", "vindman") + " Vindman photo is from 2019."])
    nix_card, vin_card = (115, 350, 360, 680), (605, 350, 360, 680)
    ph = 480
    nix_uri = photo("nixon", 360, ph)
    vin_uri = photo("vindman", 360, ph)
    nix_uri_b = photo("nixon", 530, 640)
    vin_uri_b = photo("vindman", 260, 347)

    def card(id_, x, y, w, h, uri, name, role):
        return G(id_, R(x, y, w, h, CARD, LGRAY, 1.5) + img(uri, x, y, w, ph, id_ + "-photo") +
                 G(id_ + "-caption", T(x + 24, y + ph + 62, name, 40, INK, 700) + T(x + 24, y + ph + 104, role, 22, GRAY, 400, "sans") +
                   T(x + 24, y + ph + 136, "Democratic primary", 20, TEAL, 700, "sans", ls=1.5)))

    if state == "A":
        L.append(G("cards", card("card-nixon", *nix_card[:2], 360, 680, nix_uri, "Angie Nixon", "Florida House member") +
                   card("card-vindman", *vin_card[:2], 360, 680, vin_uri, "Alex Vindman", "Retired U.S. Army officer")))
        plaque = (R(115, 1100, 850, 350, "none", INK, 1.6) + R(125, 1110, 830, 330, "none", LGRAY, 1) +
                  "".join(R(x, y, 26, 2, TEAL) + R(x, y, 2, 26, TEAL) for x, y in [(115, 1100)]) +
                  T(540, 1285, "\u2014", 60, LGRAY, 400, "serif", "middle"))
        L.append(G("result-plaque-empty", plaque))
    else:
        # teal accent appears only after the reveal, behind the advanced Nixon card
        L.append(G("accent-nixon", R(115, 312, 590, 760, TEAL)))
        L.append(G("cards",
                   G("card-nixon", R(135, 330, 530, 720, CARD, LGRAY, 1.5) + img(nix_uri_b, 135, 330, 530, 640, "card-nixon-photo") +
                     T(159, 1012, "Angie Nixon", 40, INK, 700) + T(159, 1040, "Florida House member \u00b7 Democratic primary", 19, GRAY, 400, "sans")) +
                   G("card-vindman", R(735, 330, 240, 420, CARD, LGRAY, 1.5) + img(vin_uri_b, 735, 330, 240, 320, "card-vindman-photo") +
                     T(751, 695, "Alex Vindman", 26, INK, 700) + T(751, 724, "Democratic primary", 17, GRAY, 400, "sans"))))
        res = []
        res.append(R(115, 1100, 850, 350, CARD, INK, 1.6))
        res.append(T(145, 1190, "NIXON WINS", 84, INK, 700, "serif", ls=1))
        res.append(T(145, 1240, f"~{round(MARGIN)}-POINT MARGIN", 34, TEAL, 700, "sans", ls=3))
        for i, (nm, v, p, col) in enumerate([("Angie Nixon", NIX, NIX_P, TEAL), ("Alex Vindman", VIN, VIN_P, GRAY)]):
            y = 1290 + i * 70
            res.append(T(145, y + 30, nm, 30, INK, 700))
            bw = 380 * p / 100 / 0.6
            res.append(R(400, y + 6, bw * 0.6 * 1.0, 34, col))
            res.append(T(400 + bw * 0.6 + 14, y + 33, f"{v:,}  \u00b7  {p:.1f}%", 28, BODY, 700, "sans"))
        res.append(T(145, 1432, f"Margin: {NIX - VIN:,} votes ({MARGIN:.1f} points). Statewide total {TOT:,}.", 20, GRAY, 400, "sans"))
        L.append(G("result-plaque", "\n".join(res)))
    return svg_doc(L)


# ---------------------------------------------------------------- IG-04 county map
def load_counties():
    import geopandas as gpd
    from shapely.geometry import mapping
    g = gpd.read_file(DATA / "fl_counties_cb2024_500k.geojson").to_crs(3086)
    res = {r["county"].lower(): (int(r["nixon"]), int(r["vindman"])) for r in csv.DictReader(open(DATA / "senate_dem_primary_county_2026-08-18.csv", encoding="utf8"))}
    minx, miny, maxx, maxy = g.total_bounds
    return g, res, (minx, miny, maxx, maxy)


def ig04(state, focus=None):
    g, res, (minx, miny, maxx, maxy) = load_counties()
    mx0, mw = 90, 900
    sc = mw / (maxx - minx)
    mh = (maxy - miny) * sc
    my0 = 400

    def proj(x, y):
        return mx0 + (x - minx) * sc, my0 + (maxy - y) * sc

    def path(geom):
        polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
        d = []
        for p in polys:
            for ring in [p.exterior] + list(p.interiors):
                pts = [proj(*c) for c in ring.coords]
                d.append("M" + "L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + "Z")
        return "".join(d)

    shares = {n: res[n.lower()][0] / sum(res[n.lower()]) * 100 for n in g["NAME"]}
    lo, hi = 30.0, 80.0

    def colour(v):
        t = max(0, min(1, (v - lo) / (hi - lo)))
        a, b = (0xE6, 0xEF, 0xEF), (0x01, 0x4A, 0x55)
        return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

    centroids = {}
    cells = []
    for _, r in g.iterrows():
        n = r["NAME"]
        cells.append(f'<path id="county-{re.sub(r"[^a-z]", "", n.lower())}" d="{path(r.geometry)}" fill="{colour(shares[n])}" stroke="{INK}" stroke-width="0.9" stroke-linejoin="round"/>')
        c = r.geometry.representative_point()
        centroids[n] = proj(c.x, c.y)
    spot = ["Duval", "Gadsden", "Sumter"]
    mapg = G("county-map", "\n".join(cells))
    legend_x, legend_y = 110, 1030
    steps = 50
    leg = [R(legend_x - 14, legend_y - 56, 560, 200, PAPER, LGRAY, 1.2, op=0.96),
           T(legend_x, legend_y - 22, "NIXON SHARE OF COUNTY VOTE", 18, INK, 700, "sans", ls=1.8)]
    for i in range(steps):
        leg.append(R(legend_x + i * 8, legend_y, 8.2, 26, colour(lo + (hi - lo) * i / (steps - 1))))
    for v in range(30, 81, 10):
        x = legend_x + (v - lo) / (hi - lo) * 400
        leg.append(R(x - 0.5, legend_y + 26, 1, 8, INK))
        leg.append(T(x, legend_y + 56, f"{v}%", 18, BODY, 400, "sans", "middle"))
    xm = legend_x + (50 - lo) / (hi - lo) * 400
    leg.append(T(xm, legend_y + 80, "50% = even split with Vindman", 16, GRAY, 400, "sans", "middle"))
    leg.append(T(legend_x, legend_y + 118, "Method: Nixon votes \u00f7 (Nixon + Vindman votes) in each county.", 16, GRAY, 400, "sans"))
    leg.append(T(legend_x, legend_y + 138, "Boundaries: U.S. Census cb_2024 county file. Votes: official county results.", 16, GRAY, 400, "sans"))
    src = [SRC_DOE + " County boundaries: U.S. Census Bureau cartographic boundary file cb_2024_us_county_500k."]
    L = chrome(None, src)
    L.append(G("title", T(90, 312, "WHERE DID THE UPSET COME FROM?", 44, INK, 700, "serif", ls=0.5) +
               T(90, 352, "County results, Aug 18 Democratic primary", 26, TEAL, 700, "sans", ls=1.2)))
    ring = []
    for n in spot:
        row = g[g["NAME"] == n].iloc[0]
        ring.append(f'<path d="{path(row.geometry)}" fill="none" stroke="{AMBER}" stroke-width="5" stroke-linejoin="round"/>')
    spotlight = G("spotlight-rings", "\n".join(ring))

    def stat(n):
        a, b = res[n.lower()]
        return shares[n], a, b

    if state == "A":
        L += [mapg, G("legend", "\n".join(leg))]
        return svg_doc(L)
    if state == "B":
        k = 0.64
        tx, ty = 90 - 90 * k + 20, 392 - 400 * k + 0
        L.append(G("county-map", "\n".join(cells), f"translate({tx:.1f},{ty:.1f}) scale({k})") + G("spotlight-rings", "\n".join(ring), f"translate({tx:.1f},{ty:.1f}) scale({k})"))
        rows = []
        y0 = 1010
        for i, n in enumerate(spot):
            p, a, b = stat(n)
            y = y0 + i * 104
            rows.append(R(90, y, 900, 92, CARD, LGRAY, 1.2))
            rows.append(R(90, y, 8, 92, AMBER))
            rows.append(T(120, y + 40, f"{n} County", 32, INK, 700))
            rows.append(T(120, y + 72, f"Nixon {a:,} \u00b7 Vindman {b:,}", 21, BODY, 400, "sans"))
            rows.append(T(960, y + 62, f"{p:.1f}%", 50, TEAL if p > 50 else GRAY, 700, "serif", "end"))
            rows.append(T(960, y + 22, "NIXON SHARE", 14, GRAY, 700, "sans", "end", 1.2))
        L.append(G("county-labels", "\n".join(rows)))
        note_y = 1340
        side = [R(90, note_y, 900, 168, "none", TEAL, 1.6),
                T(114, note_y + 36, "WHAT REPORTING FOUND", 17, TEAL, 700, "sans", ls=2)]
        s1, ny = TL(114, note_y + 70, "Strong support in lower-income, less-college-educated and heavily Black counties, according to a Washington Post analysis (read via a DNYUZ repost, Aug 19).", 22, 850, 28, BODY, 400, "serif")
        s2, _ = TL(114, ny + 4, "County totals do not show how individual voters chose or why.", 20, 850, 26, GRAY, 400, "sans")
        L.append(G("sidebar", "\n".join(side) + s1 + s2))
        return svg_doc(L)
    # push-in crop on one county, same assets
    cx, cy = centroids[focus]
    k = 2.2 if focus != "Duval" else 2.6
    # window: map clipped region x 90..990, y 400..1180; place county centre at window centre
    wx, wy, ww, wh = 90, 400, 900, 760
    tx, ty = wx + ww / 2 - cx * k, wy + wh / 2 - cy * k
    L.append(f'<clipPath id="win"><rect x="{wx}" y="{wy}" width="{ww}" height="{wh}"/></clipPath>')
    L.append(G("camera-window", G("county-map", "\n".join(cells), f"translate({tx:.1f},{ty:.1f}) scale({k})") +
               G("spotlight-rings", "\n".join(ring), f"translate({tx:.1f},{ty:.1f}) scale({k})"), "", 'clip-path="url(#win)"'))
    L.append(R(wx, wy, ww, wh, "none", INK, 1.5))
    p, a, b = stat(focus)
    lab = [R(90, 1190, 900, 150, CARD, LGRAY, 1.2), R(90, 1190, 8, 150, AMBER),
           T(120, 1244, f"{focus} County", 44, INK, 700), T(120, 1290, f"Nixon {a:,} \u00b7 Vindman {b:,}", 26, BODY, 400, "sans"),
           T(120, 1324, "Source: Florida Division of Elections, official county results", 18, GRAY, 400, "sans"),
           T(960, 1290, f"{p:.1f}%", 72, TEAL if p > 50 else GRAY, 700, "serif", "end"), T(960, 1226, "NIXON SHARE", 15, GRAY, 700, "sans", "end", 1.4)]
    L.append(G("county-label", "\n".join(lab)))
    return svg_doc(L)


# ---------------------------------------------------------------- IG-06 poll and debate
POLL_SRC = ("Poll: University of North Florida survey, Oct 12\u201319, 2026; Moody 49%, Nixon 45%, 5% undecided, margin of error \u00b12.81 points, "
            "as reported by WLRN and Action News Jax on Oct 21. Debate: News Service of Florida via WUSF, Oct 1, 2026.")


def ig06(state):
    L = chrome(None, [POLL_SRC, credit_line("moody", "nixon")])
    poll = []
    poll.append(T(90, 330, "THE NEW TEST", 60, INK, 700, "serif", ls=1))
    poll.append(T(90, 376, "Florida U.S. Senate \u00b7 UNF poll, Oct 12\u201319", 28, TEAL, 700, "sans", ls=0.8))
    ax0, axw = 330, 600  # bars share one zero line, axis 0-100
    for i, (key, nm, val, role) in enumerate([("moody", "Ashley Moody", 49, "Republican \u00b7 incumbent"), ("nixon", "Angie Nixon", 45, "Democratic nominee")]):
        y = 440 + i * 250
        poll.append(R(90, y, 840 + 60, 215, CARD, LGRAY, 1.2))
        poll.append(img(photo(key, 130, 170), 108, y + 22, 130, 170, f"headshot-{key}"))
        poll.append(T(ax0, y + 52, nm, 34, INK, 700))
        poll.append(T(ax0, y + 82, role, 20, GRAY, 400, "sans"))
        poll.append(R(ax0, y + 104, axw, 44, "#E9E6E0"))
        poll.append(R(ax0, y + 104, axw * val / 100, 44, TEAL if key == "nixon" else INK, extra=f'id="bar-{key}"'))
        poll.append(T(ax0 + axw * val / 100 + 12, y + 138, f"{val}%", 38, INK, 700, "sans"))
    ay = 440 + 2 * 250 - 20
    poll.append(R(ax0, ay - 4, axw, 1.5, INK))
    for v in (0, 25, 50, 75, 100):
        x = ax0 + axw * v / 100
        poll.append(R(x - 0.5, ay - 4, 1.5, 9, INK))
        poll.append(T(x, ay + 26, str(v), 17, GRAY, 400, "sans", "middle"))
    poll.append(T(ax0 + axw / 2, ay + 52, "Share of respondents, %. Both bars start at zero.", 17, GRAY, 400, "sans", "middle"))
    poll.append(T(90, ay + 96, "5% undecided \u00b7 margin of error \u00b12.81 points", 22, BODY, 400, "sans"))
    foot, _ = TL(90, ay + 132, "One survey. An earlier poll reported by WLRN showed a wider Moody lead (8 points, July). Poll results are not election outcomes.", 22, 880, 29, BODY, 400, "serif")
    poll.append(foot)
    if state == "A":
        L.append(G("poll", "\n".join(poll)))
    else:
        k = 0.66
        L.append(G("poll", "\n".join(poll), f"translate({90 - 90 * k + 0:.1f},{105:.1f}) scale({k})"))
        d = [R(90, 900, 900, 520, CARD, INK, 1.6), R(90, 900, 900, 10, AMBER),
             T(120, 970, "THE DEBATE THAT DIDN'T HAPPEN", 38, INK, 700, "serif")]
        s1, y1 = TL(120, 1030, "According to contemporaneous reporting, Moody declined to debate Nixon.", 34, 840, 44, INK, 400)
        s2, y2 = TL(120, y1 + 18, "Moody told the News Service of Florida she will keep engaging with voters.", 28, 840, 38, BODY, 400)
        d += [s1, s2, T(120, 1385, "News Service of Florida via WUSF \u00b7 Oct 1, 2026 \u00b7 reported statements, not a transcript", 19, GRAY, 400, "sans")]
        L.append(G("debate-card", "\n".join(d)))
    return svg_doc(L)


# ---------------------------------------------------------------- IG-08 governor contrast
def ig08(state):
    L = chrome(None, ["Poll: University of North Florida survey, Oct 12\u201319, 2026; Donalds 49%, Jolly 47%, 4% undecided, 1,471 likely voters, margin of error \u00b12.81, as reported by Action News Jax on Oct 21. "
                      "Summit: CBS Miami video, Sept 23, 2026 (candidates appeared in separate sessions at WLRN's Sunshine Economy Summit).", credit_line("donalds", "jolly") + " Official portraits, not summit footage."])
    L.append(G("title", T(90, 330, "ONE STATE. TWO VISIONS.", 62, INK, 700, "serif", ls=0.5)))

    def card(key, nm, party, x, y, w, ph, h):
        return G("card-" + key, R(x, y, w, h, CARD, LGRAY, 1.5) + img(photo(key, int(w), int(ph)), x, y, w, ph, f"card-{key}-photo") +
                 T(x + 20, y + ph + 50, nm, 34, INK, 700) + T(x + 20, y + ph + 82, party, 19, TEAL, 700, "sans", ls=1.4))
    chips = lambda y: G("chips", "".join(R(x, y, wd, 52, "none", TEAL, 1.6, 26) + T(x + wd / 2, y + 34, tx, 19, TEAL, 700, "sans", "middle", 1.6)
                                         for x, wd, tx in [(90, 200, "INSURANCE"), (305, 300, "PROPERTY TAXES"), (620, 270, "AFFORDABILITY")]))
    if state == "A":
        L.append(G("cards", card("donalds", "Byron Donalds", "REPUBLICAN NOMINEE", 90, 400, 420, 560, 700) + card("jolly", "David Jolly", "DEMOCRATIC NOMINEE", 570, 400, 420, 560, 700)))
        L.append(chips(1170))
        s, _ = TL(90, 1280, "Topics both candidates addressed at the Sept 23 summit, according to CBS Miami.", 26, 880, 34, BODY)
        L.append(G("topic-note", s))
    else:
        k = 0.9
        # each card scales to 90% about its own centre (cards stay equal)
        def tf(cx, cy):
            return f"translate({cx * (1 - k):.1f},{cy * (1 - k):.1f}) scale({k})"
        L.append(G("cards", G("c1", card("donalds", "Byron Donalds", "REPUBLICAN NOMINEE", 90, 400, 420, 560, 700), tf(300, 750)) +
                   G("c2", card("jolly", "David Jolly", "DEMOCRATIC NOMINEE", 570, 400, 420, 560, 700), tf(780, 750))))
        p = [R(90, 1100, 900, 340, CARD, INK, 1.6), R(90, 1100, 900, 8, AMBER),
             T(120, 1155, "UNF POLL \u00b7 OCT 12\u201319 \u00b7 LIKELY VOTERS", 20, TEAL, 700, "sans", ls=2)]
        for i, (nm, v, col) in enumerate([("Donalds", 49, INK), ("Jolly", 47, TEAL)]):
            y = 1195 + i * 78
            p += [T(120, y + 36, nm, 32, INK, 700), R(330, y + 6, 4.8 * v, 42, col), T(330 + 4.8 * v + 14, y + 40, f"{v}%", 34, INK, 700, "sans")]
        p.append(T(120, 1388, "4% undecided \u00b7 margin of error \u00b12.81 points \u00b7 a snapshot, not a forecast", 21, BODY, 400, "sans"))
        L.append(G("poll-line", "\n".join(p)))
        L.append(G("source-badge", R(90, 1074, 420, 38, AMBER) + T(110, 1100, "CBS MIAMI \u2022 SEPT 23 SUMMIT", 19, "#FFFFFF", 700, "sans", ls=1.8)))
    return svg_doc(L)


# ---------------------------------------------------------------- IG-09/10 House map to FL-14
def ig0910(state):
    d = json.loads((ROOT / "data/elections/FL/districts.json").read_text(encoding="utf8"))
    vb = d["viewbox"]
    districts = d["districts"]
    pts = [tuple(map(float, m)) for m in re.findall(r"(-?\d+\.?\d*),(-?\d+\.?\d*)", districts["14"]["path"])]
    bx0, bx1 = min(p[0] for p in pts), max(p[0] for p in pts)
    by0, by1 = min(p[1] for p in pts), max(p[1] for p in pts)
    k0 = 0.9
    ox, oy = 90, 400
    mapsvg = G("outline", f'<path d="{d["state_outline"]}" fill="#EFE9DE" stroke="none"/>') + G("districts", "".join(
        f'<path id="fl-{n.zfill(2)}" d="{v["path"]}" fill="#E4DED0" stroke="{INK}" stroke-width="1.1" stroke-linejoin="round"/>' for n, v in districts.items()))
    hi = f'<path id="fl-14-contour" d="{districts["14"]["path"]}" fill="{TEAL}" fill-opacity="0.28" stroke="{TEAL}" stroke-width="{4 if state == "A" else 1.6}" stroke-linejoin="round"/>'
    src = ["Districts: Florida Legislature EDR plan EOGPCRP2026 (HB 1-D). 21 of 28: WLRN, May 5, 2026, and WUSF, June 15, 2026. FL-14: WLRN, May 5, 2026.",
           credit_line("castor", "beltran") + " Beltran source file is 150 x 200 px."]
    L = chrome(None, src)
    if state == "A":
        L.append(G("title", T(90, 312, "2026 HOUSE MAP", 44, INK, 700, "serif", ls=1) + T(90, 352, "Florida's 28 congressional districts, plan enacted May 2026", 24, TEAL, 700, "sans", ls=0.8)))
        L.append(G("map", mapsvg, f"translate({ox},{oy}) scale({k0})"))
        L.append(G("callout", R(90, 1300, 900, 150, CARD, INK, 1.6) + R(90, 1300, 8, 150, AMBER) +
                   T(122, 1362, "Reporting: 21 of 28 districts reworked", 40, INK, 700) +
                   T(122, 1404, "Count as reported by WLRN and WUSF, not recomputed by LookLearnFind.", 19, GRAY, 400, "sans")))
    else:
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        k = 3.3
        wx, wy, ww, wh = 90, 380, 900, 640
        tx, ty = wx + ww / 2 - (ox + cx * k0) * 0 - cx * k, wy + wh / 2 - cy * k
        L.append(f'<clipPath id="win"><rect x="{wx}" y="{wy}" width="{ww}" height="{wh}"/></clipPath>')
        L.append(G("camera-window", G("map", mapsvg + hi, f"translate({tx:.1f},{ty:.1f}) scale({k})"), "", 'clip-path="url(#win)"'))
        L.append(R(wx, wy, ww, wh, "none", INK, 1.5))
        L.append(G("title", T(90, 322, "FL-14", 44, INK, 700, "serif", ls=1) + T(90 + tw("FL-14", 44, "serif", True) + 40, 322, "|  Castor vs Beltran", 38, INK, 400)))
        L.append(G("panel", R(90, 1050, 900, 400, CARD, LGRAY, 1.4) + R(90, 1050, 900, 8, TEAL) +
                   img(photo("castor", 200, 267), 120, 1082, 200, 267, "portrait-castor") + img(photo("beltran", 200, 267), 380, 1082, 200, 267, "portrait-beltran") +
                   T(120, 1384, "Kathy Castor", 28, INK, 700) + T(120, 1412, "Democrat \u00b7 incumbent", 18, GRAY, 400, "sans") +
                   T(380, 1384, "Mike Beltran", 28, INK, 700) + T(380, 1412, "Republican nominee", 18, GRAY, 400, "sans") +
                   T(640, 1110, "DISTRICT", 16, TEAL, 700, "sans", ls=2) + T(640, 1160, "FL-14", 52, INK, 700) +
                   T(640, 1215, "District boundaries changed", 26, BODY, 700) +
                   TL(640, 1252, "Castor said she would run in the new FL-14 (WLRN, May 5, 2026).", 20, 320, 26, GRAY, 400, "sans")[0]))
    return svg_doc(L)


# ---------------------------------------------------------------- IG-11 six issues
ISSUES = [("data_bill_of_rights", "Data Bill of Rights", ""), ("war_crime_accountability", "War-Crime Accountability", ""),
          ("congressional_stock_trading_ban", "Congressional Stock Trading Ban", ""), ("citizens_united_reform", "Citizens United Reform", ""),
          ("universal_healthcare", "Universal Healthcare", ""), ("us-israel-military-merger", "US-Israel Military Merger", "Section 224 / FY27 NDAA")]


def ig11(state):
    defs = json.loads((ROOT / "data/elections/FL/tip_export/issue_definitions.json").read_text(encoding="utf8"))
    stored = {x["slug"]: x for x in defs}
    for slug, name, _ in ISSUES:
        assert stored[slug]["display_name"] == name, (slug, stored[slug]["display_name"])
    L = chrome(None, ["Issue names as stored in the TIP issue definitions export (captured Oct 23, 2026). Candidate records: The Issues Party, theissuesparty.org, captured Oct 24, 2026."])
    L.append(G("title", T(90, 312, "THE ISSUES PARTY", 26, TEAL, 700, "sans", ls=4) + T(90, 372, "THE RECORD, NOT THE NOISE", 54, INK, 700, "serif")))
    tiles = []
    cw, chh, gx, gy = 430, 250, 40, 34
    pos = {}
    for i, (slug, name, sub) in enumerate(ISSUES):
        col, row = i % 2, i // 2
        x, y = 90 + col * (cw + gx), 430 + row * (chh + gy)
        pos[slug] = (x, y)
        icon = (ROOT / f"assets/icons/issue-{slug.replace('_', '-')}.svg").read_text(encoding="utf8").replace("currentColor", TEAL)
        iconuri = "data:image/svg+xml;base64," + base64.b64encode(icon.encode()).decode()
        t = R(x, y + 26, cw, chh - 26, "#F4EEE2", INK, 1.4) + R(x + 24, y, 190, 40, TEAL, rx=6)
        t += T(x + 38, y + 27, f"ISSUE {i + 1} OF 6", 15, "#FFFFFF", 700, "sans", ls=1.6)
        t += f'<image href="{iconuri}" x="{x + 24}" y="{y + 66}" width="64" height="64"/>'
        t += TL(x + 24, y + 164, name, 30, cw - 48, 36, INK, 700)[0]
        if sub:
            t += T(x + 24, y + 164 + 36 * len(wrap(name, 30, cw - 48, "serif", True)) + 4, sub, 18, GRAY, 700, "sans", ls=0.6)
        tiles.append(G("folder-" + slug, t))
    grid = G("six-folders", "\n".join(tiles))
    if state == "A":
        L.append(grid)
        s, _ = TL(90, 1370, "Each candidate profile shows up to six issue grades. A dash means not graded, and not graded is not zero.", 26, 900, 34, BODY)
        L.append(G("explainer", s))
    else:
        k = 1.0
        L.append(grid)
        m = file_uri(CAP / "tip_moody_where_they_stand.png", "image/png")
        n = file_uri(CAP / "tip_nixon_where_they_stand.png", "image/png")
        L.append(G("scrim", R(0, 400, W, 1060, PAPER)))
        ph = 640
        pw = int(ph * 263 / 475)
        L.append(G("tip-record-moody", R(90 - 6, 420 - 6, pw + 12, ph + 12, INK) + f'<image href="{m}" x="90" y="420" width="{pw}" height="{ph}"/>'))
        L.append(G("tip-record-nixon", R(90 + pw + 56 - 6, 420 - 6, pw + 12, ph + 12, INK) + f'<image href="{n}" x="{90 + pw + 56}" y="420" width="{pw}" height="{ph}"/>'))
        L.append(G("record-labels", T(90, 1120, "ASHLEY MOODY", 22, INK, 700, "sans", ls=1.6) + T(90 + pw + 56, 1120, "ANGIE NIXON", 22, INK, 700, "sans", ls=1.6)))
        L.append(G("note", R(90, 1160, 900, 120, "none", TEAL, 1.8) + T(120, 1230, "NOT GRADED \u2260 NEGATIVE GRADE", 40, TEAL, 700, "sans", ls=1) +
                   T(120, 1262, "A dash means no recorded congressional acts on that issue yet.", 20, GRAY, 400, "sans")))
        L.append(G("capture-label", T(90, 1330, "TIP candidate record, captured Oct 24, 2026", 24, INK, 700, "sans") +
                   T(90, 1364, "theissuesparty.org/candidates/S6FL00640 and /S6FL00830", 20, GRAY, 400, "sans") +
                   TL(90, 1410, "Both records shown at equal size. Grades appear only on the profile that holds them. Screenshots are unedited.", 22, 900, 30, BODY, 400, "serif")[0]))
    return svg_doc(L)


# ---------------------------------------------------------------- IG-12/13 ecosystem and CTA
def ig1213(state):
    llf = file_uri(CAP / "llf_florida_hero.png", "image/png")
    tip = file_uri(CAP / "tip_moody_where_they_stand.png", "image/png")
    logo_llf = file_uri(ROOT / "static/img/logo-ink.png", "image/png")
    L = chrome(None, ["Screenshots: looklearnfind.com/elections/2026/florida/ (hero, captured Oct 24, 2026) and theissuesparty.org/candidates/S6FL00640 (record panel, captured Oct 24, 2026). Unedited."])
    L.append(G("brand-rail", f'<image href="{logo_llf}" x="90" y="262" width="104" height="70"/>' + T(214, 306, "LookLearnFind", 24, INK, 700, "sans", ls=0.6) +
               T(610, 306, "THE ISSUES PARTY", 24, TEAL, 700, "sans", ls=3)))
    # the same two screenshot assets in both states; B pulls them back into a two-panel spread
    if state == "A":
        L.append(G("read-the-race", T(90, 408, "Read the race.", 56, INK, 700) + R(90, 430, 900, 486, "none", INK, 2) +
                   f'<image href="{llf}" x="91" y="431" width="898" height="484"/>'))
        L.append(G("inspect-the-record", T(90, 1010, "Inspect the record.", 56, INK, 700) + R(90, 1034, 255, 460, "none", INK, 2) +
                   f'<image href="{tip}" x="91" y="1035" width="253" height="458"/>'))
        L.append(G("record-caption", TL(390, 1090, "The same six issues for every candidate. Grades appear only on the profile that holds them.", 30, 590, 40, BODY)[0] +
                   T(390, 1300, "theissuesparty.org", 28, TEAL, 700, "sans")))
    else:
        L.append(G("panel-llf", R(90, 380, 440, 640, CARD, LGRAY, 1.4) + T(114, 424, "READ THE RACE", 18, TEAL, 700, "sans", ls=2.4) +
                   R(106, 450, 408, 1, LGRAY) + R(106, 470, 408, 220, "none", INK, 1.5) + f'<image href="{llf}" x="107" y="471" width="406" height="218"/>' +
                   TL(114, 740, "All 30 contests and 96 candidates, with the money, the market quotes and the record behind them.", 24, 390, 32, BODY)[0]))
        L.append(G("panel-tip", R(550, 380, 440, 640, CARD, LGRAY, 1.4) + T(574, 424, "INSPECT THE RECORD", 18, TEAL, 700, "sans", ls=2.4) +
                   R(566, 450, 408, 1, LGRAY) + R(609, 470, 322, 2 + 581, "none", INK, 1.5) + f'<image href="{tip}" x="610" y="471" width="320" height="580"/>'))
        L.append(G("title-block", TL(90, 1110, "THE RACE IS ONE STORY. THE RECORD IS ANOTHER.", 58, 900, 70, INK, 700)[0]))
        L.append(G("urls", R(90, 1360, 900, 2, TEAL) + T(90, 1418, "looklearnfind.com/elections/2026/florida", 32, TEAL, 700, "sans") + T(90, 1458, "theissuesparty.org", 26, GRAY, 700, "sans")))
    return svg_doc(L)


# ---------------------------------------------------------------- render
def render(jobs):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge")
        except Exception:
            b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        for svg_path, png_path in jobs:
            pg.goto(Path(svg_path).resolve().as_uri())
            pg.wait_for_timeout(250)
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=str(png_path), clip={"x": 0, "y": 0, "width": W, "height": H})
        b.close()


def prep_assets():
    """Create the Vindman card source and the cropped real screenshots used by IG-11 and IG-12/13."""
    src = DATA.parent / "src"
    src.mkdir(exist_ok=True)
    v = src / "vindman_2019.jpg"
    if not v.exists():
        raise SystemExit("missing src/vindman_2019.jpg (Wikimedia Commons 'Alexander Vindman on May 20, 2019.jpg', CC BY 4.0)")


def main():
    prep_assets()
    out = {
        "IG-02": [("A_start", lambda: ig02("A")), ("B_end", lambda: ig02("B"))],
        "IG-04": [("A_start", lambda: ig04("A")), ("B_end", lambda: ig04("B")),
                  ("B1_duval", lambda: ig04("C", "Duval")), ("B2_gadsden", lambda: ig04("C", "Gadsden")), ("B3_sumter", lambda: ig04("C", "Sumter"))],
        "IG-06": [("A_start", lambda: ig06("A")), ("B_end", lambda: ig06("B"))],
        "IG-08": [("A_start", lambda: ig08("A")), ("B_end", lambda: ig08("B"))],
        "IG-09-10": [("A_start", lambda: ig0910("A")), ("B_end", lambda: ig0910("B"))],
        "IG-11": [("A_start", lambda: ig11("A")), ("B_end", lambda: ig11("B"))],
        "IG-12-13": [("A_start", lambda: ig1213("A")), ("B_end", lambda: ig1213("B"))],
    }
    jobs = []
    for ig, frames in out.items():
        d = BASE / ig
        d.mkdir(parents=True, exist_ok=True)
        for tag, fn in frames:
            sp = d / f"{ig}_{tag}.svg"
            doc = fn()
            ET.fromstring(doc)  # well-formed check before anything is written or rendered
            sp.write_text(doc, encoding="utf8")
            jobs.append((sp, d / f"{ig}_{tag}_1080x1920.png"))
            print("wrote", sp.relative_to(ROOT))
    if "--no-render" not in sys.argv:
        render(jobs)
        print("rendered", len(jobs), "PNGs")


if __name__ == "__main__":
    main()
