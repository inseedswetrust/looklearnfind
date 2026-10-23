#!/usr/bin/env python3
"""Capture Kalshi market quotes for Florida governor, Senate and House events, exactly as returned (public API, no auth).

    python3 tools/elections/fetch_kalshi.py

Writes data/elections/FL/markets.json and captures/kalshi_fl_<UTC timestamp>.json (one file per capture, never overwritten) (raw).
Rules: quotes are market-implied prices for a contract, not forecasts. We keep bid, ask, last, volume, open interest, rules text,
contract title and the capture timestamp. Nothing is smoothed or interpolated.
"""
import json, urllib.request, urllib.parse, datetime, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data/elections/FL"
B = "https://api.elections.kalshi.com/trade-api/v2"

def get(p, **q):
    u = B + p + ("?" + urllib.parse.urlencode(q) if q else "")
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "LLF-election-desk"}), timeout=60) as r:
                return json.loads(r.read())
        except Exception:
            if a == 2:
                raise
            time.sleep(2)

events = {"governor": "GOVPARTYFL-26", "senate": "SENATEFLS-26"}
for n in range(1, 29):
    events[f"house-{n:02d}"] = f"KXHOUSERACE-FL{n:02d}-26"
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
raw, out = {}, {}
for race, et in events.items():
    try:
        j = get(f"/events/{et}", with_nested_markets="true")
    except Exception as ex:
        out[race] = {"event_ticker": et, "error": str(getattr(ex, "code", ex))}
        continue
    raw[et] = j
    ev = j["event"]
    mk = j.get("markets") or ev.get("markets") or []
    out[race] = {"event_ticker": et, "title": ev["title"], "url": f"https://kalshi.com/markets/{ev.get('series_ticker', '').lower()}",
                 "mutually_exclusive": ev.get("mutually_exclusive"), "contracts": [
        {"ticker": m["ticker"], "title": m.get("title"), "yes_label": m.get("yes_sub_title"), "no_label": m.get("no_sub_title"),
         "status": m.get("status"), "yes_bid": m.get("yes_bid_dollars"), "yes_ask": m.get("yes_ask_dollars"), "last": m.get("last_price_dollars"),
         "previous": m.get("previous_price_dollars"), "volume": m.get("volume_fp") or m.get("volume"), "volume_24h": m.get("volume_24h_fp"),
         "open_interest": m.get("open_interest_fp"), "rules": m.get("rules_primary"), "close_time": m.get("close_time")} for m in mk]}
    time.sleep(0.2)
(D / "captures" / ("kalshi_fl_" + now.replace(":", "").replace("-", "") + ".json")).write_text(json.dumps(raw))
(D / "markets.json").write_text(json.dumps({"captured_at_utc": now, "source": "Kalshi public API v2 (api.elections.kalshi.com)", "races": out}, indent=1))
print({k: (len(v.get("contracts", [])) if "contracts" in v else v.get("error")) for k, v in out.items()})
