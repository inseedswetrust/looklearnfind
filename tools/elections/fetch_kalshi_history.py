#!/usr/bin/env python3
"""Fetch real candlestick history for a Kalshi contract (public API) and save it with the capture.

    python3 tools/elections/fetch_kalshi_history.py SENATEMI SENATEMI-26-D 2026-09-20 2026-10-23 data/elections/MI

Daily (1440) and hourly (60) candles. A candle is stamped with the period END; a daily candle ending 04:00Z covers the previous Eastern-time day, recorded as et_day. Values are exactly the API's price close, yes bid close and yes ask close per period.
Charts must plot these points only (no smoothing, no interpolation).
"""
import sys, json, urllib.request, urllib.parse, datetime
from pathlib import Path
series, ticker, d0, d1, outdir = sys.argv[1:6]
B = "https://api.elections.kalshi.com/trade-api/v2"
ts = lambda s: int(datetime.datetime.fromisoformat(s).replace(tzinfo=datetime.timezone.utc).timestamp())
def get(p, **q):
    with urllib.request.urlopen(urllib.request.Request(B + p + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "LLF-election-desk"}), timeout=90) as r:
        return json.loads(r.read())
out = {"ticker": ticker, "series": series, "captured_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "range": [d0, d1]}
for name, iv in (("daily", 1440), ("hourly", 60)):
    j = get(f"/series/{series}/markets/{ticker}/candlesticks", start_ts=ts(d0), end_ts=ts(d1), period_interval=iv)
    rows = []
    for c in j.get("candlesticks", []):
        p = c.get("price", {})
        end = datetime.datetime.fromtimestamp(c["end_period_ts"], datetime.timezone.utc)
        et = end - datetime.timedelta(hours=4)          # EDT (UTC-4) applies for all dates before Nov 1, 2026
        rows.append({"et_day": (et - datetime.timedelta(seconds=1)).strftime("%Y-%m-%d") if iv == 1440 else None,
                     "period_end_et": et.strftime("%Y-%m-%dT%H:%M"),
                     "end_utc": datetime.datetime.fromtimestamp(c["end_period_ts"], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                     "close": p.get("close_dollars"), "high": p.get("high_dollars"), "low": p.get("low_dollars"),
                     "bid_close": c.get("yes_bid", {}).get("close_dollars"), "ask_close": c.get("yes_ask", {}).get("close_dollars"),
                     "volume": c.get("volume_fp"), "open_interest": c.get("open_interest_fp")})
    out[name] = rows
Path(outdir, "captures").mkdir(parents=True, exist_ok=True)
Path(outdir, "captures", f"kalshi_{ticker}_{out['captured_at_utc'][:10]}.json").write_text(json.dumps(out))
Path(outdir, f"kalshi_{ticker}.json").write_text(json.dumps(out, indent=1))
print(ticker, {k: len(out[k]) for k in ("daily", "hourly")})
