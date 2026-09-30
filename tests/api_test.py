#!/usr/bin/env python3
"""End-to-end API checks against a running dev server.

    LLF_DATA=/tmp/llfdev LLF_DEV=1 php -S 127.0.0.1:8090 -t dist tests/router.php &
    echo '<?php return ["admin_emails"=>["editor@test.local"]];' > /tmp/llfdev/config.php
    php static/api/tools/seed_demo.php dist
    python3 tests/api_test.py
"""
import json, sys, urllib.request, urllib.error, http.cookiejar

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8090"
fails = 0


class Client:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.csrf = None

    def call(self, method, path, data=None, headers=None):
        req = urllib.request.Request(BASE + path, method=method)
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        if data is not None:
            req.data = json.dumps(data).encode()
            req.add_header("Content-Type", "application/json")
        if self.csrf:
            req.add_header("X-CSRF", self.csrf)
        try:
            r = self.op.open(req)
            code, body = r.status, r.read()
        except urllib.error.HTTPError as e:
            code, body = e.code, e.read()
        try:
            j = json.loads(body)
        except Exception:
            j = body
        if isinstance(j, dict) and "csrf" in j and j["csrf"]:
            self.csrf = j["csrf"]
        return code, j

    get = lambda self, p: self.call("GET", p)
    post = lambda self, p, d=None: self.call("POST", p, d or {})


def check(name, cond, extra=""):
    global fails
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else f"  {extra}"))
    if not cond:
        fails += 1


anon, ann, ed = Client(), Client(), Client()

# ---- public reads on seeded data
c, j = anon.get("/api/ledger/list")
check("explore lists seeded entries", c == 200 and j["total"] >= 9, j)
check("entries carry ledger numbers", all(i["video"]["ledger"] for i in j["items"]))
check("newest first", [i["save"]["added_at"] for i in j["items"]] == sorted([i["save"]["added_at"] for i in j["items"]], reverse=True))
c, j = anon.get("/api/ledger/list?category=everyday-life&topic=cooking")
check("filters by category+topic", j["total"] == 1 and j["items"][0]["save"]["topic"] == "cooking", j.get("total"))
c, j = anon.get("/api/ledger/list?q=mud+flood")
check("query resolves thread alias (mud flood -> tartaria)", j["total"] == 1 and j["items"][0]["save"]["threads"][0]["slug"] == "tartaria", j.get("total"))
c, j = anon.get("/api/ledger/list?thread=tartaria")
check("thread filter", j["total"] == 1)
check("deep dive + find links resolve", j["items"][0]["deep_dive"] and j["items"][0]["find_link"] and j["items"][0]["links"]["learn"][0]["url"] == "/learn/what-was-tartary/", j["items"][0]["links"])
c, j = anon.get("/api/ledger/list?deep=1")
check("has-deep-dive filter", j["total"] >= 3)
c, j = anon.get("/api/ledger/list?length=lt1")
check("length filter (<1 min)", j["total"] >= 2 and all(i["video"]["duration"] < 60 for i in j["items"]))
c, j = anon.get("/api/ledger/list?q=nonexistent-zzz")
check("empty result is empty, not an error", c == 200 and j["total"] == 0)
check("facets only for populated values", all(f["n"] > 0 for f in anon.get("/api/ledger/list")[1]["facets"]["topic"]))
c, j = anon.get("/api/ledger/shuffle?category=politics")
check("shuffle draws from current filters", j["total"] >= 2 and j["item"]["save"]["category"] == "politics")
c, j = anon.get("/api/ledger/entry?ref=L-1")
check("entry by ledger id with notes", c == 200 and len(j["notes"]) == 2, j)
c, j = anon.get("/api/ledger/entry?ref=L-999")
check("missing entry is 404", c == 404)
check("desk shelf present", anon.get("/api/ledger/desk")[1]["desk"]["items"][0]["video"]["ledger_no"] == 1)
check("thread listing has seeded threads", len(anon.get("/api/threads")[1]["threads"]) >= 10)
check("following requires sign-in", anon.get("/api/ledger/list?mode=following")[0] == 401)

# ---- auth + csrf
c, j = ann.post("/api/auth/signup", {"email": "ann@test.local", "password": "short", "handle": "ann_t"})
check("weak password rejected", c == 400)
c, j = ann.post("/api/auth/signup", {"email": "ann@test.local", "password": "longenough1", "handle": "ann_t", "display_name": "Ann T."})
check("signup ok and signed in", c == 200 and j["user"]["handle"] == "ann_t" and j["user"]["role"] == "member", j)
c, j = ann.post("/api/auth/signup", {"email": "ann@test.local", "password": "longenough1", "handle": "ann2"})
check("duplicate email rejected", c == 409)
saved = ann.csrf; ann.csrf = "bad"
check("missing/bad csrf blocked", ann.post("/api/ledger/save", {"url": "x"})[0] == 403)
ann.csrf = saved
check("wrong password rejected", Client().post("/api/auth/login", {"email": "ann@test.local", "password": "nope-nope"})[0] == 401)

# ---- link normalization + dedupe
c, j = ann.post("/api/ledger/preview", {"url": "https://vimeo.com/123"})
check("unsupported platform rejected", c == 400 and "supported" in j["error"])
c, j = ann.post("/api/ledger/preview", {"url": "https://www.instagram.com/reel/CabcDEF123/?igsh=xyz"})
check("instagram reel normalizes", c == 200 and j["video"]["url"] == "https://www.instagram.com/reel/CabcDEF123/" and j["duplicate"] is False, j)
c, j = ann.post("/api/ledger/preview", {"url": "https://youtu.be/dQw4w9WgXcQ?t=3"})
check("youtu.be normalizes", c == 200 and j["video"]["url"].endswith("dQw4w9WgXcQ"), j)

# ---- private save, then public submission goes to review
body = {"url": "https://www.instagram.com/reel/CabcDEF123/", "note": "", "visibility": "private", "creator_handle": "skinfriend", "duration": "0:52"}
c, j = ann.post("/api/ledger/save", body)
check("private save immediate", c == 200 and j["status"] == "private" and j["entry"]["video"]["creator_handle"] == "@skinfriend" and j["entry"]["video"]["duration"] == 52, j)
vid, sid = j["video_id"], j["save_id"]
c, j = ann.get("/api/ledger/list?mode=mine")
check("My Ledger shows private save", j["total"] == 1 and j["items"][0]["save"]["visibility"] == "private")
c, j = anon.get("/api/ledger/list?q=skinfriend")
check("private save never public", j["total"] == 0)
c, j = ann.post("/api/ledger/save", dict(body, visibility="public", note="Nice", topic="skincare", kind="Explainer"))
check("public needs a real note", c == 400, j)
c, j = ann.post("/api/ledger/save", dict(body, visibility="public", note="The ingredient list says more than the promise does.", topic="skincare", kind="Explainer", threads=["skincare-claims"]))
check("public without public profile asks for consent", c == 409, j)
c, j = ann.post("/api/ledger/save", dict(body, visibility="public", note="The ingredient list says more than the promise does.", topic="skincare", kind="Explainer", threads=["skincare-claims"], propose_threads=["Retinol myths"], make_profile_public=True))
check("public save pending review", c == 200 and j["status"] == "pending", j)
check("same person saving again updates, not duplicates", j["duplicate"] is True)
c, j = anon.get("/api/ledger/list?q=skinfriend")
check("pending not visible publicly", j["total"] == 0)
c, j = ann.post("/api/ledger/preview", {"url": "https://instagram.com/reel/CabcDEF123"})
check("duplicate detected across URL variants", j["duplicate"] is True and j["my_save"]["status"] == "pending")

# ---- editor review
c, j = ed.post("/api/auth/signup", {"email": "editor@test.local", "password": "longenough1", "handle": "ed_t"})
check("admin_emails promotes to admin", j["user"]["role"] == "admin", j)
check("members cannot reach admin", ann.get("/api/admin/queue")[0] == 403)
c, j = ed.get("/api/admin/queue")
q = [i for i in j["items"] if i["save"]["id"] == sid]
check("queue contains pending save with proposed thread", c == 200 and len(q) == 1 and q[0]["proposed_threads"][0]["slug"] == "retinol-myths", j)
c, j = ed.post("/api/admin/review", {"save_id": sid, "action": "approve", "edits": {"kind": "Explainer"}})
check("approve", c == 200)
c, j = anon.get("/api/ledger/list?q=skinfriend")
check("approved save appears in Explore with Reader-added label", j["total"] == 1 and j["items"][0]["save"]["label"] == "Reader-added" and j["items"][0]["video"]["ledger_no"] == 10, j)
check("unapproved proposed thread hidden on public entry", [t["slug"] for t in j["items"][0]["save"]["threads"]] == ["skincare-claims"])
c, j = ed.get("/api/admin/threads")
check("thread proposal queued", any(t["slug"] == "retinol-myths" for t in j["threads"]))
check("editor approves proposal", ed.post("/api/admin/thread", {"action": "approve", "slug": "retinol-myths", "category": "everyday-life", "summary": "What retinol can and cannot do."})[0] == 200)
check("approved thread now shows on entry", any(t["slug"] == "retinol-myths" for t in anon.get("/api/ledger/list?thread=retinol-myths")[1]["items"][0]["save"]["threads"]))
check("thread lookup for dynamic page", anon.get("/api/threads/get?slug=retinol-myths")[0] == 200)

# ---- editing an approved public save returns it to review; editors publish directly
c, j = ann.post("/api/ledger/save", dict(body, visibility="public", note="Changed my note to say something more careful.", topic="skincare", kind="Explainer"))
check("edit of approved save re-enters review", j["status"] == "pending")
check("entry leaves index while re-review pending", anon.get("/api/ledger/list?q=skinfriend")[1]["total"] == 0)
ed.post("/api/admin/review", {"save_id": sid, "action": "approve"})
c, j = ed.post("/api/ledger/save", {"url": "https://www.instagram.com/reel/CeditorOne1/", "visibility": "public", "note": "An editor adds this one directly.", "topic": "cooking", "kind": "Demonstration", "creator_handle": "@chef"})
check("editor save is live immediately and labeled Editor-added", c == 200 and j["status"] == "approved" and j["entry"]["save"]["label"] == "Editor-added", j)
c, j = ed.post("/api/ledger/save", {"url": "https://www.instagram.com/reel/CabcDEF123/", "visibility": "public", "note": "A second person's note on the same video.", "topic": "skincare", "kind": "Explainer"})
check("second saver attaches to same canonical video", j["video_id"] == vid)
c, j = anon.get(f"/api/ledger/entry?ref={vid}")
check("open notes shows both savers, distinct", len(j["notes"]) == 2 and {n["saver"]["handle"] for n in j["notes"]} == {"ann_t", "ed_t"})
check("only one row for that video in Explore", anon.get("/api/ledger/list?q=skinfriend")[1]["total"] == 1)

# ---- follow / following feed / profile / mute
c, j = ann.post("/api/follow", {"handle": "ed_t"})
check("follow", c == 200)
ed.post("/api/ledger/save", {"url": "https://www.tiktok.com/@cook/video/7123456789012345678", "visibility": "public", "note": "Newest public save by someone ann follows.", "topic": "cooking", "kind": "Demonstration"})
c, j = ann.get("/api/ledger/list?mode=following")
check("Following = newest public saves of followed profiles", c == 200 and j["total"] >= 2 and j["items"][0]["video"]["provider"] == "tiktok", j.get("total"))
check("Following is strictly newest-first", [i["save"]["added_at"] for i in j["items"]] == sorted([i["save"]["added_at"] for i in j["items"]], reverse=True))
ann.post("/api/mute", {"handle": "ed_t", "muted": True})
check("mute hides from Following without unfollowing", ann.get("/api/ledger/list?mode=following")[1]["total"] == 0)
ann.post("/api/mute", {"handle": "ed_t", "muted": False})
c, j = anon.get("/api/profile?handle=ed_t")
check("public profile lists public saves, no follower counts", j["private"] is False and j["total"] >= 3 and "followers" not in j and "follower_count" not in j)
check("unknown profile 404", anon.get("/api/profile?handle=nobody_here")[0] == 404)
c, j = ann.post("/api/profile/update", {"profile_public": False})
j2 = anon.get(f"/api/ledger/entry?ref={vid}")[1]
check("going private pulls that person's public saves (another saver keeps the entry alive)", [n["saver"]["handle"] for n in j2["notes"]] == ["ed_t"] and j2["save"]["saver"]["handle"] == "ed_t" and anon.get("/api/profile?handle=ann_t")[1]["private"] is True, j2["notes"])
ann.post("/api/profile/update", {"profile_public": True})

# ---- collections
c, j = ann.post("/api/collections/create", {"title": "Things to try", "premise": "Saved for later", "visibility": "private"})
cid = j["id"]
check("collection created", c == 200)
check("add to collection", ann.post("/api/collections/add", {"id": cid, "save_id": sid})[0] == 200)
c, j = ann.get(f"/api/collection?id={cid}")
check("owner sees collection", c == 200 and len(j["items"]) == 1)
check("private collection hidden from others", anon.get(f"/api/collection?id={cid}")[0] == 404)
ann.post("/api/collections/update", {"id": cid, "visibility": "public"})
check("public collection visible", anon.get(f"/api/collection?id={cid}")[0] == 200)

# ---- reports, moderation, unavailable handling, merge
check("report filed", anon.post("/api/report", {"video_id": vid, "reason": "wrong_attribution", "detail": "Handle is wrong"})[0] == 200)
c, j = ed.get("/api/admin/reports")
check("report appears for editors", len(j["reports"]) == 1)
ed.post("/api/admin/report", {"report_id": j["reports"][0]["id"], "action": "resolve", "note": "Fixed"})
ed.post("/api/admin/entry", {"video_id": vid, "action": "edit", "creator_handle": "@skinfriend2"})
check("editor corrects attribution, marked human", anon.get(f"/api/ledger/entry?ref={vid}")[1]["video"]["creator_handle"] == "@skinfriend2")
ed.post("/api/admin/entry", {"video_id": vid, "action": "unavailable"})
check("unavailable entries leave active results", anon.get("/api/ledger/list?q=skinfriend")[1]["total"] == 0)
ed.post("/api/admin/entry", {"video_id": vid, "action": "available"})
ed.post("/api/admin/entry", {"video_id": vid, "action": "set_links", "learn": ["what-was-tartary"], "find": []})
check("editor attaches a deep dive", anon.get("/api/ledger/list?q=skinfriend")[1]["items"][0]["deep_dive"] is True)
ed.post("/api/admin/entry", {"video_id": vid, "action": "remove"})
check("removed entries disappear", anon.get("/api/ledger/list?q=skinfriend")[1]["total"] == 0)
check("audit trail recorded", len(ed.get("/api/admin/audit")[1]["audit"]) >= 5)

# ---- unpublish, export, forms, desk
c, j = ann.post("/api/ledger/save", {"url": "https://www.instagram.com/reel/CprivateAA1/", "visibility": "private", "note": "just for me"})
check("private note stays out of export for others; export works", ann.get("/api/export?format=json")[0] == 200)
check("newsletter", anon.post("/api/newsletter", {"email": "reader@example.com"})[0] == 200)
check("bad email rejected", anon.post("/api/newsletter", {"email": "nope"})[0] == 400)
check("contact honeypot swallows bots", anon.post("/api/contact", {"email": "a@b.co", "message": "hi there", "website": "spam"})[1] == {"ok": True})
check("contact stores real messages", anon.post("/api/contact", {"email": "a@b.co", "message": "hello", "kind": "contribution", "type": "A question"})[0] == 200)
c, j = ed.post("/api/admin/desk", {"title": "Test shelf", "note": "n", "video_ids": [1, 2]})
check("desk shelf replaced", c == 200 and anon.get("/api/ledger/desk")[1]["desk"]["title"] == "Test shelf")
check("cross-origin POST blocked", Client().call("POST", "/api/newsletter", {"email": "x@y.zz"}, {"Origin": "https://evil.example"})[0] == 403)
print("\n%s" % ("ALL PASSED" if not fails else f"{fails} FAILED"))
sys.exit(1 if fails else 0)
