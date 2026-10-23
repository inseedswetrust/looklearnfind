#!/usr/bin/env python3
"""Propose Kalshi and Polymarket contracts for each watchlist race. Output is a REVIEW file, not a mapping: a human (or Claude with the
rules text in hand) promotes an entry into contract_map.json only after reading the contract's resolution rules.

    python3 tools/dark_horse/discover_contracts.py data/elections/dark_horse/watchlist.csv > data/elections/dark_horse/contract_candidates.json
"""
import csv, json, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (LLF research monitor)", "Accept": "application/json"}
def get(u):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            if a == 2: return {"_error": f"HTTP {e.code}"}
            time.sleep(2)
        except Exception as e:
            if a == 2: return {"_error": str(e)[:100]}
            time.sleep(2)
KAL = "https://api.elections.kalshi.com/trade-api/v2"
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
out = []
for r in rows:
    last = r["candidate_name"].split()[-1].lower()
    race = r["race"]; st = r["state"]
    tickers = [f"SENATE{st}-26", f"SENATE{st}S-26"] if race == "SEN" else [f"KXHOUSERACE-{st}{race.split('-')[1]}-26"]
    k = []
    for t in tickers:
        j = get(f"{KAL}/events/{t}?with_nested_markets=true")
        if not j or "_error" in j or "event" not in j: continue
        mk = j.get("markets") or j["event"].get("markets") or []
        for m in mk:
            if last in (m.get("yes_sub_title") or "").lower() or last in (m.get("title") or "").lower():
                k.append({"event_ticker": t, "ticker": m["ticker"], "title": j["event"]["title"], "yes_label": m.get("yes_sub_title"), "status": m.get("status"),
                          "last": m.get("last_price_dollars"), "bid": m.get("yes_bid_dollars"), "ask": m.get("yes_ask_dollars"), "rules": (m.get("rules_primary") or "")[:300]})
    time.sleep(0.15)
    q = urllib.parse.quote(f"{r['candidate_name']} {st}")
    pm = get(f"https://gamma-api.polymarket.com/public-search?q={q}&limit_per_type=5&events_status=active")
    p = []
    for ev in (pm or {}).get("events", []) if pm and "_error" not in pm else []:
        for m in ev.get("markets", []):
            if last in (m.get("question") or "").lower() and "2026" in json.dumps(ev):
                p.append({"event_slug": ev.get("slug"), "event_title": ev.get("title"), "question": m.get("question"), "outcomes": m.get("outcomes"), "prices": m.get("outcomePrices"),
                          "token_ids": m.get("clobTokenIds"), "end": m.get("endDate"), "closed": m.get("closed"), "rules": (m.get("description") or "")[:300]})
    time.sleep(0.15)
    out.append({"candidate_name": r["candidate_name"], "state": st, "race": race, "kalshi_candidates": k, "polymarket_candidates": p,
                "polymarket_error": (pm or {}).get("_error") if isinstance(pm, dict) else None})
    print(r["candidate_name"], "| kalshi", len(k), "| polymarket", len(p), file=sys.stderr)
print(json.dumps(out, indent=1))
