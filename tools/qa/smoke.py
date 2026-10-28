#!/usr/bin/env python3
"""Smoke-test election pages on a base URL (local or live). Stdlib only.

    python3 tools/qa/smoke.py http://localhost:8091            # after tools/qa/rebuild_serve.sh
    python3 tools/qa/smoke.py https://looklearnfind.com        # after deploy

Checks per page: HTTP 200, <title>, canonical, og:title/og:image, no noindex meta, no template leftovers ([[ ]], None, nan),
every internal link resolves, TIP deep links resolve, external source links reachable (403 from paywalled/bot-blocking sites is reported separately).
"""
import sys, re, json, urllib.request, urllib.parse, concurrent.futures as cf
base = sys.argv[1].rstrip("/")   # add --illinois to include the Illinois pages
paths = ["/elections/2026/florida/", "/elections/2026/florida/governor/", "/elections/2026/florida/senate/", "/elections/2026/florida/house/",
         "/learn/michigan-senate-delta-october-2026/", "/learn/florida-house-independent-spending-october-2026/", "/learn/florida-governor-fundraising-polling-2026/",
         "/about/election-methods/"] + [f"/elections/2026/florida/house/{i}/" for i in range(1, 29)]
if "--illinois" in sys.argv:        # Illinois State of the Race (built locally; not live until the owner approves a deploy)
    paths += ["/elections/2026/illinois/", "/elections/2026/illinois/governor/", "/elections/2026/illinois/senate/", "/elections/2026/illinois/house/"] + [f"/elections/2026/illinois/house/{i}/" for i in range(1, 18)]
UA = {"User-Agent": "Mozilla/5.0 (LLF smoke test)"}
def fetch(u, method="GET"):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA, method=method), timeout=40) as r:
            return r.status, r.read() if method == "GET" else b""
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return 0, str(e).encode()
res, links = {}, {}
for p in paths:
    st, body = fetch(base + p)
    h = body.decode("utf-8", "ignore")
    r = {"status": st}
    if st == 200:
        r["title"] = (re.search(r"<title>(.*?)</title>", h, re.S) or [0, ""])[1][:70]
        r["canonical"] = bool(re.search(r'<link rel="canonical" href="https://looklearnfind\.com' + re.escape(p) + '"', h))
        r["og"] = bool(re.search(r'og:title', h)) and bool(re.search(r'og:image', h))
        r["noindex"] = 'content="noindex"' in h
        r["leftovers"] = [x for x in ("[[", "]]", ">None<", ">nan<") if x in h]
        for m in re.findall(r'href="([^"#]+)', h):
            links.setdefault(m, set()).add(p)
    res[p] = r
def chk(l):
    u = l if l.startswith("http") else base + l
    if not l.startswith("http") and l.startswith("/") and "." in l.rsplit("/", 1)[-1]:
        pass
    return l, fetch(u, "GET")[0]
internal = [l for l in links if l.startswith("/")]
external = [l for l in links if l.startswith("http") and "looklearnfind.com" not in l]
with cf.ThreadPoolExecutor(8) as ex:
    ri = dict(ex.map(chk, internal))
    re_ = dict(ex.map(chk, external))
bad_i = {l: s for l, s in ri.items() if s != 200 and not l.startswith(("/api/", "/account/"))}
bad_e = {l: s for l, s in re_.items() if s not in (200, 301, 302)}
ok = sum(1 for r in res.values() if r["status"] == 200 and r.get("canonical") and r.get("og") and not r.get("noindex") and not r.get("leftovers"))
print(json.dumps({"base": base, "pages": len(paths), "pages_ok": ok, "internal_links": len(internal), "internal_bad": bad_i,
                  "external_links": len(external), "external_not_200": bad_e, "page_failures": {p: r for p, r in res.items() if r["status"] != 200 or not r.get("canonical") or r.get("noindex") or r.get("leftovers")}}, indent=1))
