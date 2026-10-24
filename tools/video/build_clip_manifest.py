"""Write CLIP_MANIFEST.csv and RIGHTS_REGISTER.csv for the Florida footage-first pass from one table.

The table below is the single source: every row was checked on 2026-10-24 through page metadata, captions
(timed text, not footage) and thumbnails. Nothing is marked CLEARED without a license basis. A time marked
CAPTION: comes from caption text and has NOT been seen on screen; UNINSPECTED means no timing at all.

Usage: PYTHONUTF8=1 python tools/video/build_clip_manifest.py
"""
import csv, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/video/florida-2026"
VID = ROOT / "assets/video/florida-2026"
YT = "https://www.youtube.com/watch?v="

COLS = ["scene_id", "clip_id", "candidate", "source_url", "origin_uploader", "published_date", "footage_description", "full_duration",
        "suggested_in", "suggested_out", "suggested_seconds", "source_context", "licensing_basis", "rights_status", "selected_file",
        "sha256", "quality", "notes", "fallback_still"]

UNI = "UNINSPECTED"
NL, ER, IR, CL, RJ = "NEEDS_LICENSE", "EDITORIAL_REVIEW", "INTERNAL_REFERENCE_ONLY", "CLEARED", "REJECTED"
STD = "YouTube standard license (no Creative Commons flag in page metadata); uploader or rights holder must grant permission"

# (scene, id, candidate, url, uploader, date, description, duration, in, out, secs, context, basis, status, selected, quality, notes, fallback)
ROWS = [
    ("02", "S02-N1", "Angie Nixon", YT + "TxMQbKAhCqY", "Angie Nixon For Florida | Change Can't Wait (@AngieForFL)", "2026-07-27",
     "Nixon speaking to camera; thumbnail shows lower-third 'VOTE BY AUGUST 18' and 'Paid for by Angie for Florida'", "0:30", "CAPTION:00:00:00", "CAPTION:00:00:04", "4",
     "Campaign digital ad (six-figure statewide buy announced Jul 27); official announcement https://angienixon.com/u-s-senate-candidate-angie-nixon-launches-six-figure-statewide-digital-ad-buy-highlighting-working-class-roots-bold-vision/",
     "Campaign-produced; no reuse terms published on the campaign page; " + STD, NL, "", "up to 2160p per page metadata", "Speech text at 0:00 'I'm Angie Nixon. I didn't grow up with a lot of money' (caption). The 'VOTE BY AUGUST 18' graphic is stale for a post-primary film: crop or ask for the clean master. Not downloaded.", "static/img/elections/portraits/90009.jpg (Florida House, public domain)"),
    ("02", "S02-N2", "Angie Nixon", YT + "VSJ2vu6JCS8", "News4JAX The Local Station", "2026-08-19",
     "Full victory speech; thumbnail shows Nixon at a microphone in front of a standing crowd", "20:14", UNI, UNI, "2-4",
     "Primary-night speech after the Aug 18 win", "Broadcaster copyright; " + STD, NL, "", "1080p per page metadata", "Best match for the 'authentic Nixon crowd footage' hard cut after the result reveal. Timecodes need a person to scrub it after a license is granted.", "IG-02 portrait"),
    ("02", "S02-N3", "Angie Nixon", YT + "nEOB3JIzpGw", "CBS Miami", "2026-08-23",
     "1-on-1 interview after the primary win", "12:33", UNI, UNI, "2-4", "Post-primary interview", "Broadcaster copyright; " + STD, NL, "", "1080p per page metadata", "Alternate; interview framing, not crowd footage.", "IG-02 portrait"),
    ("02", "S02-V1", "Alex Vindman", YT + "EJfAHrw4_vs", "WPLG Local 10", "2026-02-10",
     "First campaign event (Sunrise, FL); thumbnail shows a man with a microphone at a lectern, Local 10 bug (identity not confirmed on screen)", "2:56", UNI, UNI, "2-4",
     "Campaign launch event coverage", "Broadcaster copyright; " + STD, NL, "", "720p per page metadata", "Needs a person to confirm the speaker is Vindman before use.", "IG-02 Vindman photo (CC BY 4.0, 2019)"),
    ("02", "S02-V2", "Alex Vindman", YT + "Joc0DBTdhiM", "Gulf Coast News", "2026-08-12", "Vindman discusses Senate race, war and voter concerns (title)", "2:32", UNI, UNI, "2-4",
     "Southwest Florida coverage, six days before the primary", "Broadcaster copyright; " + STD, NL, "", "720p per page metadata", "Alternate.", "IG-02 Vindman photo"),
    ("02", "S02-V3", "Alex Vindman", YT + "YPclIZyt7y8", "WPTV News", "unknown (not read)", "'Vindman's money advantage meets Nixon's Florida roots in Democratic Senate primary' (title)", "1:30", UNI, UNI, "2-4",
     "Primary preview", "Broadcaster copyright; " + STD, NL, "", "not read", "Alternate; metadata not read.", "IG-02 Vindman photo"),
    ("03", "S03-N1", "Angie Nixon", YT + "TxMQbKAhCqY", "Angie Nixon For Florida | Change Can't Wait (@AngieForFL)", "2026-07-27",
     "Same July ad; caption window where she says she is running for Senate and lists lower health care costs and affordable homes", "0:30", "CAPTION:00:00:17", "CAPTION:00:00:29", "4",
     "Campaign ad", STD, NL, "", "up to 2160p", "This is a talking-head ad. It does NOT show organizing or voter contact, so it cannot stand in for those actions. Organizing footage: NEEDS_ASSET.", "WUSF rally photos (copyright WUSF; license needed)"),
    ("03", "S03-N2", "Angie Nixon", "https://www.wusf.org/politics-issues/2026-10-05/angie-nixon-brings-pep-rally-style-campaign-stop-to-usf-tampa", "WUSF Public Media", "2026-10-05",
     "Article with four photographs of the Oct 4 USF Oval Theater rally (Steve Newborn, Meghan Bowman); no video on the page", "n/a", "n/a", "n/a", "n/a",
     "Rally of several hundred, Sunday night Oct 4 (date inferred from 'Sunday night' and the Oct 5 posting)", "Footer: (c) 2026 WUSF, all rights reserved; no license terms on the page", NL, "", "photos only", "No footage exists on this source. Request the photographers' stills or ask USF/campaign for event video.", "WUSF photo 3 (Nixon at microphone) after license"),
    ("03", "S03-N3", "Angie Nixon", "https://www.reutersconnect.com/item/florida-democrat-angie-nixon-launches-senate-bid-against-republican-ashley-moody/dGFnOnJldXRlcnMuY29tLDIwMjY6bmV3c21sX09XRUZWQzU1MDIxNzY0MjQxMDAx", "Reuters (item id includes WESH feed)", "unknown (not read)",
     "Licensed news video item: 'Florida Democrat Angie Nixon launches Senate bid against Republican Ashley Moody'", "unknown", UNI, UNI, "2-4",
     "Senate bid launch (Jan 2026 per other coverage)", "Reuters Connect is a paid licensing platform; page not readable without an account", NL, "", "unknown", "Purchase path. Fetch was blocked, so duration, date and shots are unknown.", ""),
    ("05", "S05-M1", "Ashley Moody", YT + "g1LOk0ohVvw", "WPLG Local 10", "2026-08-21",
     "Moody remarks outside a Miami-Dade Republican event in Doral; she did not take questions", "2:11", "CAPTION:00:00:42", "CAPTION:00:00:54", "4",
     "Local 10 report on Moody's South Florida stop; same report carries a separate Nixon sit-down segment", "Broadcaster copyright; " + STD, NL, "", "720p per page metadata", "Caption window is Moody speaking about Nixon and DSA; check she is on screen. This clip is a characterization of her opponent, so pair it with an equal-length Nixon answer.", "static/img/elections/portraits/89119.jpg"),
    ("05", "S05-N1", "Angie Nixon", YT + "g1LOk0ohVvw", "WPLG Local 10", "2026-08-21",
     "Nixon sit-down interview segment inside the same report (a different event from Moody's Doral stop)", "2:11", "CAPTION:00:01:43", "CAPTION:00:01:56", "4",
     "Wednesday sit-down with Local 10", "Broadcaster copyright; " + STD, NL, "", "720p per page metadata", "Same source as S05-M1, so scale and quality match by construction. Visually uninspected.", "static/img/elections/portraits/90009.jpg"),
    ("05", "S05-M2", "Ashley Moody", YT + "RU55Ejn5KBQ", "AshleyMoodyFL (candidate channel)", "2025-03-18",
     "Moody at a podium between U.S. and Florida flags (thumbnail); 'Ashley Moody for U.S. Senate'", "0:41", UNI, UNI, "2-4",
     "Campaign video posted Mar 2025", "Candidate-produced; " + STD, NL, "", "1080p per page metadata", "18 months old; check it is not framed as current. Alternate for Moody.", "static/img/elections/portraits/89119.jpg"),
    ("05", "S05-X1", "Moody and Nixon", "https://www.wesh.com/article/florida-us-senate-race-moody-nixon-clash/74197567", "WESH 2 News (Greg Fox)", "2026-10-20",
     "Article: Moody at a Palm Coast restaurant and Nixon in Orlando, both on Tuesday Oct 20 (separate events, same day)", "n/a", "n/a", "n/a", "n/a",
     "Text read in full; no video file or embed was found in the page source", "Broadcaster copyright; terms of use apply", NL, "", "n/a", "Best editorial match for 'separate events' but the video, if any, was not reachable. Ask WESH for the two stand-ups.", ""),
    ("06", "S06-M1", "Ashley Moody", YT + "g1LOk0ohVvw", "WPLG Local 10", "2026-08-21", "Moody public remarks (see S05-M1)", "2:11", "CAPTION:00:00:42", "CAPTION:00:00:54", "4",
     "Same report", "Broadcaster copyright; " + STD, NL, "", "720p per page metadata", "Debate refusal is NOT in this report: Local 10 says her team has not yet accepted its invitation and Moody said the teams will meet. The refusal source is WUSF / News Service of Florida, Oct 1 (text). Never pair this clip with a 'declined' caption.", "static/img/elections/portraits/89119.jpg"),
    ("06", "S06-M2", "Ashley Moody", "https://commons.wikimedia.org/wiki/File:Senator_Ashley_Moody_Questions_Anthony_Fauci_At_U.S._Senate_HSGAC_Hearing.webm", "Senator Ashley Moody (office YouTube channel), mirrored on Wikimedia Commons", "2026-07-29",
     "Moody questioning at a Senate HSGAC hearing; medium shot, her own lower-right brand bug 'ASHLEYMOODY'", "14:38", "00:00:00", "00:00:04", "4",
     "July 29 Senate Homeland Security Committee hearing with Anthony Fauci; original YouTube https://www.youtube.com/watch?v=EbhiR1nPZfY",
     "Commons tags it public domain (U.S. Senate) but the file is her office's branded edit, not the raw committee feed; basis not independently confirmed", ER,
     "assets/video/florida-2026/selects/_review_hold/S06-01_moody_hsgac_0000-0004.mp4", "1920x1080 50 fps VP9 source; select H.264 CRF 14",
     "ACQUIRED BEFORE THE PACKET'S RIGHTS RULE WAS APPLIED: held for review, not cleared. Visually inspected 0:00-0:04 (Moody speaking, steady framing, brand bug bottom right). Topic (Fauci hearing) is unrelated to the race. Do not publish until the Commons PD basis is confirmed against the Senate's own feed.", "static/img/elections/portraits/89119.jpg"),
    ("06", "S06-N1", "Angie Nixon", YT + "VSJ2vu6JCS8", "News4JAX The Local Station", "2026-08-19", "Victory speech (see S02-N2)", "20:14", UNI, UNI, "2-4", "Primary night", "Broadcaster copyright; " + STD, NL, "", "1080p per page metadata", "Equal-length counterpart to any Moody clip.", "static/img/elections/portraits/90009.jpg"),
    ("08", "S08-J1", "David Jolly", YT + "4nEIiR4yZsg", "WLRN News", "unknown (not read)", "Jolly on affordability, insurance costs and Amendment 3 at the WLRN Sunshine Economy Summit (title)", "30:16", UNI, UNI, "2-4",
     "Full WLRN session; WLRN hosted the summit", "WLRN copyright; " + STD, NL, "", "not read", "Best pair for matching: the same producer filmed both candidates in separate sessions.", "static/img/elections/portraits/89243.jpg"),
    ("08", "S08-D1", "Byron Donalds", YT + "ct26bOviu0A", "WLRN News", "unknown (not read)", "Donalds on affordability, Amendment 3 and the Trump agenda at the same summit (title)", "30:55", UNI, UNI, "2-4",
     "Full WLRN session", "WLRN copyright; " + STD, NL, "", "not read", "Pairs with S08-J1 (30:16 and 30:55, same producer).", "static/img/elections/portraits/89042.jpg"),
    ("08", "S08-B1", "Byron Donalds and David Jolly", YT + "AjRj_vWPXEs", "CBS Miami", "2026-09-23",
     "Reporter package: split-screen of both candidates in the opening; separate sessions at the WLRN summit", "2:34", UNI, UNI, "2-4",
     "'They were never in the same room together' (reporter). Caption times: hurricane-tax denial 0:24-0:31; Amendment 3 answers 0:52-0:57. Speaker attribution cannot be read from captions.", "Broadcaster copyright; (c) 2026 CBS Broadcasting; " + STD, NL, "", "1080p per page metadata",
     "This is the source named in the packet. Do not use a side-by-side as if they shared a stage. Also contains Jolly saying there will be no formal debates (0:02:04): outside the film's script.", "static/img/elections/portraits/89042.jpg and 89243.jpg"),
    ("08", "S08-B2", "Byron Donalds and David Jolly", YT + "JZH-HTTvcXk", "WPTV News", "2026-09-23", "'Jolly, Donalds clash on property taxes, insurance during gubernatorial...' (title)", "2:15", UNI, UNI, "2-4",
     "Same summit, second outlet", "Broadcaster copyright; " + STD, NL, "", "720p per page metadata", "Alternate. Its caption download was rate-limited, so no caption times.", ""),
    ("08", "S08-J2", "David Jolly", YT + "ZR7TF4oeyDQ", "David Jolly (candidate channel)", "2026-09-10", "'Change is here...be a part of it!'; thumbnail shows Jolly among supporters at an outdoor tent event", "1:45", UNI, UNI, "2-4",
     "Campaign video", "Candidate-produced; " + STD, NL, "", "1080p per page metadata", "Shows an organizing-style event. No equal Donalds campaign video was found, so use only if one exists.", "static/img/elections/portraits/89243.jpg"),
    ("10", "S10-C1", "Kathy Castor", YT + "Z6F_T_GpQfs", "RepKathyCastor (official House office channel)", "2026-09-14", "Castor to camera with on-screen text 'CUT HEALTH CARE FOR THOUSANDS OF' (thumbnail); 'Corruption Costing You: Hope Florida'", "3:15", UNI, UNI, "2-4",
     "Official office video on a Florida state matter", "Official congressional office content may be a government work, but this piece is political in subject and the office has not stated reuse terms", ER, "", "2160p per page metadata", "Needs review of House franking and reuse rules before any use; also not a campaign video.", "static/img/elections/portraits/88870.jpg"),
    ("10", "S10-C2", "Kathy Castor", YT + "qVj4UZKVeNk", "Spectrum News", "unknown (not read)", "'Kathy Castor campaigning for another term in Congress' (title)", "11:47", UNI, UNI, "2-4", "Political Connections segment", "Broadcaster copyright; " + STD, NL, "", "not read", "Alternate.", "static/img/elections/portraits/88870.jpg"),
    ("10", "S10-C3", "Kathy Castor", "https://commons.wikimedia.org/wiki/File:U.S._Rep._Kathy_Castor_offers_foreclosure_avoidance-_WMNF_News.webm", "wmnfnews (WMNF), mirrored on Wikimedia Commons", "2012-02-22",
     "Castor at a Tampa foreclosure expo", "unknown", "n/a", "n/a", "n/a", "2012 news clip", "CC BY 3.0 per Commons file page (attribution to wmnfnews)", CL, "", "1280x720", "Cleared but not acquired: 14 years old, wrong district, and the district has since been redrawn. Fallback only with a visible 2012 date.", "static/img/elections/portraits/88870.jpg"),
    ("10", "S10-B1", "Mike Beltran", YT + "TMDXoUEsiGQ", "Spectrum News", "2026-10-07", "'Mike Beltran looks to unseat Congresswoman Kathy Castor in November'", "12:08", UNI, UNI, "2-4", "Spectrum interview", "Broadcaster copyright; " + STD, NL, "", "1080p per page metadata", "Best Beltran source by quality and recency.", "static/img/elections/portraits/91313.jpg (150x200)"),
    ("10", "S10-B2", "Mike Beltran", YT + "xd7tJZfV1E8", "Inform Your Vote", "2026-09-26", "Candidate answer, 'Cost of Living? FL District 14 2026'", "1:23", UNI, UNI, "2-4", "Voter-guide question series (Castor's answer is WWCsx8h1GJI, 33 s)", "Publisher copyright; " + STD, NL, "", "480p per page metadata", "Low resolution; the paired Castor answer is a good equal-length match. Not suitable for full-frame 1080x1920.", "static/img/elections/portraits/91313.jpg"),
    ("10", "S10-B3", "Mike Beltran", YT + "qc9t74u6F_k", "WFLA News Channel 8", "unknown (not read)", "'Mike Beltran to face Kathy Castor in November'", "2:04", UNI, UNI, "2-4", "Post-primary report", "Broadcaster copyright; " + STD, NL, "", "not read", "Alternate. The 10 Tampa Bay report PrxKRHiMpQ4 (2026-08-19, 2:35) is another; its thumbnail did not load.", "static/img/elections/portraits/91313.jpg"),
    ("10", "S10-X1", "Castor and Beltran", "https://ballotpedia.org/Florida%27s_14th_Congressional_District_election%2C_2026", "Ballotpedia", "n/a", "Campaign ad index requested by the packet", "n/a", "n/a", "n/a", "n/a",
     "The page returned HTTP 202 with an empty body to both a fetch tool and curl (bot challenge); no ad list could be read", "n/a", IR, "", "n/a", "NEEDS_ASSET: a person must open the page in a browser and copy the ad links.", ""),
]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in ROWS:
        (scene, cid, cand, url, up, date, desc, dur, i, o, secs, ctx, basis, status, sel, qual, notes, fb) = r
        digest = ""
        if sel:
            p = ROOT / sel
            if not p.exists():
                raise SystemExit(f"selected file missing: {sel}")
            digest = sha(p)
        rows.append([scene, cid, cand, url, up, date, desc, dur, i, o, secs, ctx, basis, status, sel, digest, qual, notes, fb])
    with open(OUT / "CLIP_MANIFEST.csv", "w", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        w.writerows(rows)
    reg = [["clip_id", "source_url", "rights_holder", "rights_status", "basis", "acquired", "local_file", "next_action", "restrictions"]]
    for r in rows:
        acquired = "yes (held, not cleared)" if r[14] and r[13] != CL else ("yes" if r[14] else "no")
        action = {NL: "Request written permission from the rights holder (uploader or outlet); keep the reply in docs/video/florida-2026/permissions/",
                  ER: "Editorial and legal review before any use", CL: "Attach credit line; acquire only if the scene needs it", IR: "Look up in a browser; do not use",
                  RJ: "Do not use"}[r[13]]
        restr = "No download without written permission" if r[13] == NL else ("Internal review only; no publication" if r[13] in (ER, IR) else "Credit required")
        reg.append([r[1], r[3], r[4], r[13], r[12], acquired, r[14], action, restr])
    with open(OUT / "RIGHTS_REGISTER.csv", "w", newline="", encoding="utf8") as f:
        csv.writer(f).writerows(reg)
    from collections import Counter
    print(Counter(r[13] for r in rows), len(rows), "rows")


if __name__ == "__main__":
    main()
