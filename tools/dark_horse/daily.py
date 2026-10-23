#!/usr/bin/env python3
"""Daily dark-horse monitor: dated market quotes (Kalshi, Polymarket) and race polls (VoteHub) for the verified watchlist. Stdlib only.

    python3 tools/dark_horse/daily.py                       # real run against the network
    python3 tools/dark_horse/daily.py --dry-run             # builds rows from the map without calling any API
    python3 tools/dark_horse/daily.py --date 2026-10-24     # name the day folder (America/New_York date by default)

Reads  data/elections/dark_horse/watchlist.csv, contract_map.json (human-verified contract IDs only).
Writes data/elections/dark_horse/daily/<date>/{markets.json,markets.csv,polls.json,alerts.json,manifest.json,captures/*.json}, latest.json, status.json.
Rules (see daily_feed_contract.md): never invent a quote; no contract mapped means `unavailable`; party-winner contracts are labeled as such and are not
reported as a named-candidate contract; deltas compare the same venue + contract + price type only; a failed provider keeps its last good data and is marked stale;
latest.json only moves for a complete day (at least one real quote and no provider error); no poll averages, no probabilities, no rankings.
"""
import argparse, csv, datetime, hashlib, json, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "data" / "elections" / "dark_horse"
KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
VOTEHUB = "https://api.votehub.com/polls"
UA = {"User-Agent": "LLFResearchMonitor/1.0 (hello@looklearnfind.com)", "Accept": "application/json"}
CHANGE_THRESHOLD = 0.03   # placeholder, in dollars per $1 contract; to be calibrated on real daily data (owner approves any change)
STALE_HOURS = 48
STATE_NAMES = {"MI": "Michigan", "IL": "Illinois", "MN": "Minnesota", "FL": "Florida", "TX": "Texas", "CA": "California", "NY": "New York", "NJ": "New Jersey",
               "PA": "Pennsylvania", "CO": "Colorado", "CT": "Connecticut", "MA": "Massachusetts"}


class HttpError(Exception):
    def __init__(self, code, msg=""):
        super().__init__(f"HTTP {code} {msg}")
        self.code = code


def default_fetch(url):
    """One attempt, no blind retry on 429 (the contract forbids hammering a rate-limited venue)."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            raw = r.read()
            return json.loads(raw.decode("utf-8")), raw
    except urllib.error.HTTPError as e:
        raise HttpError(e.code, e.reason)
    except Exception as e:
        raise HttpError(0, str(e)[:120])


def ny_today():
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("America/New_York")).date()
    except Exception:
        return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=4)).date()   # EDT; zoneinfo/tzdata unavailable


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def load_json(p, default):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def key_of(c):
    return c.get("tip_candidate_id") or f"no_tip:{c['state']}:{c['race']}:{c['candidate_name']}"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def base_row(c, provider, m, now):
    k = provider
    return {"candidate_id": key_of(c), "candidate_name": c["candidate_name"], "race_id": c["race"], "race_key": c.get("race_key"), "provider": provider,
            "contract_id": m.get(f"{k}_ticker") or m.get(f"{k}_token_id"), "contract_url": m.get(f"{k}_url"), "outcome_label": m.get(f"{k}_outcome"),
            "contract_kind": m.get(f"{k}_contract_kind"), "resolution_rules_url": m.get(f"{k}_rules_url"), "quoted_price": None, "price_type": None, "currency": "USD per $1 contract",
            "bid": None, "ask": None, "volume": None, "liquidity": None, "open_interest": None, "market_status": None, "observed_at_utc": None, "retrieved_at_utc": now,
            "source_url": None, "fetch_status": "unavailable", "error": None, "mapping_verified_at": m.get("checked_at"), "source_capture_sha256": None}


def fetch_kalshi(row, ticker, fetch, cap_dir):
    url = f"{KALSHI}/markets/{urllib.parse.quote(ticker, safe='')}"
    data, raw = fetch(url)
    (cap_dir / f"kalshi_{ticker}.json").write_bytes(raw)
    mk = data.get("market", {})
    last = mk.get("last_price_dollars")
    row.update(quoted_price=float(last) if last not in (None, "") else None, price_type="last_trade", bid=_f(mk.get("yes_bid_dollars")), ask=_f(mk.get("yes_ask_dollars")),
               volume=_f(mk.get("volume_fp") or mk.get("volume")), open_interest=_f(mk.get("open_interest_fp")), market_status=mk.get("status"),
               observed_at_utc=mk.get("updated_time"), source_url=url, source_capture_sha256=sha(raw),
               fetch_status="ok" if last not in (None, "") else "no_quote")
    row["resolution_rules"] = (mk.get("rules_primary") or "")[:400]


def fetch_polymarket(row, token, fetch, cap_dir, now):
    gurl = f"{GAMMA}/markets?clob_token_ids={urllib.parse.quote(token)}"
    g, graw = fetch(gurl)
    last_url = f"{CLOB}/last-trade-price?token_id={urllib.parse.quote(token)}"
    book_url = f"{CLOB}/book?token_id={urllib.parse.quote(token)}"
    lt, ltraw = fetch(last_url)
    bk, bkraw = fetch(book_url)
    (cap_dir / f"polymarket_{token[:16]}.json").write_text(json.dumps({"gamma": g, "last": lt, "book": bk}), encoding="utf-8")
    bids = [float(x["price"]) for x in bk.get("bids", [])]
    asks = [float(x["price"]) for x in bk.get("asks", [])]
    m = (g[0] if isinstance(g, list) and g else {}) or {}
    price = lt.get("price")
    row.update(quoted_price=float(price) if price not in (None, "") else None, price_type="last_trade", bid=max(bids) if bids else None, ask=min(asks) if asks else None,
               volume=_f(m.get("volume")), liquidity=_f(m.get("liquidity")), market_status="closed" if m.get("closed") else "active", observed_at_utc=now, source_url=book_url,
               source_capture_sha256=sha(graw + ltraw + bkraw), fetch_status="ok" if price not in (None, "") else "no_quote")


QUOTE_STALE_HOURS = 72


def flag_stale(rows, now):
    """quote_age_hours from the venue's own timestamp. No timestamp -> stale_quote 'unknown' (never silently fresh)."""
    t_now = datetime.datetime.fromisoformat(now.replace("Z", "+00:00"))
    for r in rows:
        if r.get("fetch_status") != "ok":
            r["quote_age_hours"], r["stale_quote"] = None, None
            continue
        ts = r.get("observed_at_utc")
        try:
            age = (t_now - datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))).total_seconds() / 3600
        except Exception:
            r["quote_age_hours"], r["stale_quote"] = None, "unknown"
            continue
        r["quote_age_hours"] = round(age, 1)
        r["stale_quote"] = age > QUOTE_STALE_HOURS
    return rows


def _f(v):
    try:
        return float(v) if v not in (None, "") else None
    except Exception:
        return None


def collect_markets(candidates, cmap, fetch, now, cap_dir, dry):
    rows, errors, ok = [], [], {"kalshi": 0, "polymarket": 0}
    tried = {"kalshi": 0, "polymarket": 0}
    failed = {"kalshi": None, "polymarket": None}
    for c in candidates:
        m = cmap.get(key_of(c), {})
        for provider, field in (("kalshi", "kalshi_ticker"), ("polymarket", "polymarket_token_id")):
            row = base_row(c, provider, m, now)
            idv = m.get(field)
            if not idv:
                rows.append(row)                      # unavailable: no verified contract for this candidate on this venue
                continue
            if dry:
                row["fetch_status"] = "dry_run"
                rows.append(row)
                continue
            tried[provider] += 1
            try:
                if provider == "kalshi":
                    fetch_kalshi(row, idv, fetch, cap_dir)
                else:
                    fetch_polymarket(row, idv, fetch, cap_dir, now)
                if row["fetch_status"] == "ok":
                    ok[provider] += 1
            except HttpError as e:
                if e.code == 404:                       # the venue no longer lists this contract: record it, do not count it as an outage
                    row["fetch_status"] = "market_not_found"
                    row["error"] = str(e)[:200]
                    time.sleep(0.15)
                    rows.append(row)
                    continue
                row["fetch_status"] = "error"
                row["error"] = str(e)[:200]
                failed[provider] = str(e)[:200]
                errors.append({"provider": provider, "candidate_id": row["candidate_id"], "contract_id": idv, "error": row["error"]})
            time.sleep(0.15)
            rows.append(row)
    return rows, errors, ok, tried, failed


def collect_polls(candidates, fetch, now, cap_dir, dry):
    """VoteHub race-level polls (us-senator, us-representative). Original poll URL and sponsor facts are kept; no averaging."""
    polls_by_type, errs = {}, {}
    if not dry:
        for t in ("us-senator", "us-representative"):
            try:
                data, raw = fetch(f"{VOTEHUB}?poll_type={t}&limit=3000")
                (cap_dir / f"votehub_{t}.json").write_bytes(raw)
                polls_by_type[t] = data
            except HttpError as e:
                errs[t] = str(e)
    out, coverage = [], {}
    for c in candidates:
        rid = key_of(c)
        t = "us-senator" if c["race"] == "SEN" else "us-representative"
        if dry:
            coverage[rid] = {"status": "dry_run", "polls": 0}
            continue
        if t not in polls_by_type:
            coverage[rid] = {"status": "source_error", "polls": 0, "error": errs.get(t)}
            continue
        last = c["candidate_name"].split()[-1].lower()
        subj = f"2026 {STATE_NAMES.get(c['state'], c['state'])}"
        seat = None if c["race"] == "SEN" else c["race"].replace("HOUSE-", f"{c['state']}-")
        found = []
        for p in polls_by_type[t]:
            if seat:      # House polls carry the district in seat_name and in subject ("2026 CA-11")
                if p.get("seat_name") != seat and p.get("subject") != f"2026 {seat}":
                    continue
            elif p.get("subject") != subj:
                continue
            if not any(last in (a.get("choice") or "").lower() for a in p.get("answers", [])):
                continue
            found.append({"race_id": c["race"], "candidate_ids": [rid], "pollster": p.get("pollster"), "sponsor": p.get("sponsors") or [], "partisan_sponsor": p.get("partisan"),
                          "internal": p.get("internal"), "mode": None, "sample_size": p.get("sample_size"), "population": p.get("population"), "field_start": p.get("start_date"),
                          "field_end": p.get("end_date"), "publication_date": None, "aggregator_import_date": p.get("created_at"), "margin_of_error": None, "question_text": None,
                          "candidate_results": p.get("answers"), "original_poll_url": p.get("url"), "aggregator_url": f"{VOTEHUB}?poll_type={t}", "aggregator_poll_id": p.get("id"),
                          "licensing": "VoteHub API (beta); terms not verified; facts stored with attribution", "verification_status": "aggregator_listing_original_not_reviewed",
                          "imported_at_utc": now})
        out += found
        coverage[rid] = {"status": "ok" if found else "no_poll_found", "polls": len(found), "source_checked": "votehub:" + t,
                         "latest_field_end": max((x["field_end"] for x in found if x["field_end"]), default=None)}
    return out, coverage, errs


def deltas(today_rows, prev_rows):
    prev = {(r["provider"], r["contract_id"], r["price_type"]): r for r in prev_rows if r.get("fetch_status") == "ok"}
    out = []
    for r in today_rows:
        if r.get("fetch_status") != "ok":
            continue
        p = prev.get((r["provider"], r["contract_id"], r["price_type"]))
        if not p or p["quoted_price"] is None or r["quoted_price"] is None:
            continue
        d = round(r["quoted_price"] - p["quoted_price"], 4)
        if abs(d) >= CHANGE_THRESHOLD:
            out.append({"candidate_id": r["candidate_id"], "provider": r["provider"], "contract_id": r["contract_id"], "price_type": r["price_type"], "contract_kind": r["contract_kind"],
                        "previous_price": p["quoted_price"], "previous_observed": p.get("retrieved_at_utc"), "price": r["quoted_price"], "observed": r.get("retrieved_at_utc"),
                        "change": d, "bid": r["bid"], "ask": r["ask"], "volume": r["volume"], "possible_events": [],
                        "note": "Same venue, contract and quote type. No cause is asserted; possible_events is filled only by a reviewed editorial pass."})
    return out


def run(day, dry=False, fetch=default_fetch, base=BASE, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(base / "watchlist.csv", encoding="utf-8-sig") as _f:
        watch = [r for r in csv.DictReader(_f) if r.get("monitor") == "yes"]
    cmap = load_json(base / "contract_map.json", {})
    folder, rel = Path(base) / "daily" / day, f"daily/{day}"
    rev = 1
    if dry:                                          # a dry run never touches the day's real folder or its revision numbering
        folder = rel_dir = Path(base) / "dry_runs" / f"{day}T{now[11:19].replace(':', '')}"
        rel = f"dry_runs/{folder.name}"
    while not dry and (folder / "manifest.json").exists():       # a finished day is immutable: a rerun becomes a new revision beside it
        rev += 1
        folder, rel = Path(base) / "daily" / day / "revisions" / f"r{rev}", f"daily/{day}/revisions/r{rev}"
    cap = folder / "captures"
    cap.mkdir(parents=True, exist_ok=True)
    cands = [c for c in watch if c.get("current_ballot_verified") == "yes"]
    skipped = [c["candidate_name"] for c in watch if c.get("current_ballot_verified") != "yes"]
    rows, errors, ok, tried, failed = collect_markets(cands, cmap, fetch, now, cap, dry)
    flag_stale(rows, now)
    polls, pcov, perrs = collect_polls(cands, fetch, now, cap, dry)
    # previous day for same-contract comparison
    # compare with the previous day's original (never a revision)
    days = sorted(d.name for d in (Path(base) / "daily").iterdir() if d.is_dir() and d.name < day) if (Path(base) / "daily").exists() else []
    prev_rows = load_json(Path(base) / "daily" / days[-1] / "markets.json", {}).get("rows", []) if days else []
    alerts = deltas(rows, prev_rows)
    atomic_write(folder / "markets.json", json.dumps({"date": day, "dry_run": dry, "rows": rows, "errors": errors,
        "note": "Quote types differ by venue. Party-winner contracts are not named-candidate contracts. Never infer win probability."}, indent=1))
    cols = list(rows[0].keys()) if rows else []
    if cols:
        tmp = folder / "markets.csv.tmp"
        with tmp.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        tmp.replace(folder / "markets.csv")
    atomic_write(folder / "polls.json", json.dumps({"date": day, "polls": polls, "coverage": pcov, "source_errors": perrs}, indent=1))
    atomic_write(folder / "alerts.json", json.dumps({"date": day, "threshold": CHANGE_THRESHOLD, "alerts": alerts}, indent=1))
    manifest = {"date": day, "revision": rev, "run_at_utc": now, "dry_run": dry, "watchlist_monitored": len(cands), "skipped_not_verified": skipped,
                "market_rows": len(rows), "market_quotes_ok": ok, "market_errors": len(errors), "poll_rows": len(polls),
                "captures": {p.name: sha(p.read_bytes()) for p in sorted(cap.glob("*")) if p.is_file()}}
    atomic_write(folder / "manifest.json", json.dumps(manifest, indent=1))
    # status: per-source freshness, kept across runs
    old = load_json(Path(base) / "status.json", {"sources": {}})
    src = old.get("sources", {})
    def upd(name, attempted, success, err):
        s = src.setdefault(name, {"last_success_at": None, "last_error": None, "last_error_at": None})
        if success:
            s["last_success_at"] = now
        if err:
            s["last_error"], s["last_error_at"] = err, now
        s["stale"] = (s["last_success_at"] is None) or (datetime.datetime.fromisoformat(now.replace("Z", "+00:00")) - datetime.datetime.fromisoformat(s["last_success_at"].replace("Z", "+00:00"))
                                                         > datetime.timedelta(hours=STALE_HOURS))
    if not dry:
        upd("kalshi", tried["kalshi"], ok["kalshi"] > 0, failed["kalshi"])
        upd("polymarket", tried["polymarket"], ok["polymarket"] > 0, failed["polymarket"])
        upd("votehub", len(pcov), bool(polls_ok(pcov)), "; ".join(f"{k}: {v}" for k, v in perrs.items()) or None)
    status = {"updated_at_utc": now, "last_run_date": day, "dry_run": dry, "sources": src,
              "coverage": {"watchlist_monitored": len(cands), "with_kalshi_mapping": sum(1 for c in cands if cmap.get(key_of(c), {}).get("kalshi_ticker")),
                           "with_polymarket_mapping": sum(1 for c in cands if cmap.get(key_of(c), {}).get("polymarket_token_id")),
                           "with_polls": sum(1 for v in pcov.values() if v.get("polls")), "no_poll_found": sum(1 for v in pcov.values() if v.get("status") == "no_poll_found")},
              "latest_pointer_updated": False}
    complete = (ok["kalshi"] + ok["polymarket"]) > 0 and not errors and not perrs     # a provider failure keeps the prior complete day as latest
    cur = load_json(Path(base) / "latest.json", {})
    not_older = (not cur) or (day, rev) >= (cur.get("date", ""), cur.get("revision", 1))      # the pointer never moves backward
    if complete and not dry and not_older:
        atomic_write(Path(base) / "latest.json", json.dumps({"date": day, "revision": rev, "run_at_utc": now, "markets_path": f"{rel}/markets.json", "polls_path": f"{rel}/polls.json",
                                                              "manifest_path": f"{rel}/manifest.json"}, indent=1))
        status["latest_pointer_updated"] = True
    atomic_write(Path(base) / "status.json", json.dumps(status, indent=1))
    return status, manifest


def polls_ok(pcov):
    return any(v.get("status") in ("ok", "no_poll_found") for v in pcov.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date")
    a = ap.parse_args()
    status, manifest = run(a.date or ny_today().isoformat(), dry=a.dry_run)
    print(json.dumps({"status": status["coverage"], "latest_pointer_updated": status["latest_pointer_updated"], "market_quotes_ok": manifest["market_quotes_ok"],
                      "market_errors": manifest["market_errors"], "poll_rows": manifest["poll_rows"], "sources": {k: {"stale": v["stale"], "last_success_at": v["last_success_at"], "last_error": v["last_error"]} for k, v in status["sources"].items()}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
