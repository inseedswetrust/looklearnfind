---
name: llf-footage-scout
description: Find, inspect and rights-triage authentic campaign and news footage for an LLF state video, acquire only cleared clips, and return a clip manifest and rights register with honest timecodes. Use after the script and shot list exist and before any infographic or AI plate is made, whenever a candidate appears on screen.
---

# llf-footage-scout

**Version** 1.0.0 · **Owner** LLF production · **Type** skill plus `tools/video/build_clip_manifest.py` and `tools/video/make_video_manifest.py`. Added 2026-10-24 from the Florida footage-first pass. Tests: `tests/test_footage_pack.py`.

## The order (durable rule)
Script → shot selection → real footage search and capture → genuine candidate stills → evidence-based infographics → AI background and transition assets → Premiere handoff. Real footage is the primary picture whenever a candidate appears. AI is for empty environments, blank design plates and transitions only. No AI candidate likeness, ever. An end frame meant as a camera move is derived from the start frame's own assets, never regenerated.

## Procedure
1. Read the scene list and mark every scene that shows a candidate. Check `assets/video/<state>-2026/` and `docs/video/<state>-2026/CLIP_MANIFEST.csv` first; reuse before searching.
2. For each scene find 2 to 4 sources, ranked: (a) the candidate's own channel or official release, (b) a public-domain or Creative Commons file with a license on its page, (c) a news outlet's report (license needed), (d) a licensed platform item (purchase). Record the original uploader, URL, event, date, resolution and length from the page itself: `python -m yt_dlp --skip-download --print "%(id)s|%(title)s|%(channel)s|%(upload_date)s|%(duration)s|%(license)s"`. Confirm every YouTube id with `https://www.youtube.com/oembed?url=...` (a wrong id looks plausible).
3. Inspect what you can without taking the video: captions (`--write-auto-subs`) give timed speech, the thumbnail shows framing. Mark times from captions `CAPTION:hh:mm:ss`; mark anything not seen or heard `UNINSPECTED`. Never invent a timestamp. Caption text does not say who is speaking: do not attribute a quote from captions alone.
4. Rights, per clip, one value: `CLEARED` (license or public-domain basis written in `licensing_basis`), `NEEDS_LICENSE`, `EDITORIAL_REVIEW`, `INTERNAL_REFERENCE_ONLY`, `REJECTED`. Public is not permitted; a short clip is not fair use by default; a campaign upload is not public domain. YouTube pages without a Creative Commons flag are `NEEDS_LICENSE`. A file whose own license tag you cannot trace to the original producer is `EDITORIAL_REVIEW`, not cleared.
5. Acquire only `CLEARED`: `yt-dlp` or a direct file URL, then FFmpeg selects of 1 to 4 seconds, original audio kept, clean framing. Full masters go in `assets/video/<state>-2026/source/`, selects in `selects/`. Anything held for review goes in `_review_hold/` and is listed as held. Never get around a login, paywall, DRM or a platform block. Restricted footage: store the URL, thumbnail for internal reference, and proposed in and out, nothing else.
6. Write `docs/video/<state>-2026/CLIP_MANIFEST.csv` (columns fixed: scene_id, clip_id, candidate, source_url, origin_uploader, published_date, footage_description, full_duration, suggested_in, suggested_out, suggested_seconds, source_context, licensing_basis, rights_status, selected_file, sha256, quality, notes, fallback_still) and `RIGHTS_REGISTER.csv` by editing the table in `build_clip_manifest.py` and running it. Add a `fallback_still` (a genuine licensed portrait) to every row.
7. Beware what footage can imply: separate sessions are not a shared stage; a report that someone has not yet accepted an invitation is not a refusal; a candidate-ad graphic (for example "vote by August 18") can be out of date; organizing needs organizing footage, not a talking-head ad.
8. Hand `VIDEO_ASSET_MANIFEST.csv` (`make_video_manifest.py`) and `CLAUDE_RETURN.md` to the owner. The owner or counsel sends permission requests; save replies in `docs/video/<state>-2026/permissions/` and only then change a status to `CLEARED`.

## Do not
Download `NEEDS_LICENSE` material; call a status cleared on assumption; reuse a broadcast; put a generated face anywhere; render the finished video.

## Failure semantics
A clip you cannot trace stays `UNINSPECTED` or `INTERNAL_REFERENCE_ONLY`. A scene with no usable footage keeps its genuine still and the manifest says `NEEDS_ASSET`. Fix the table, not the test.

## Changelog
1.0.0 (2026-10-24) first version, from the Florida footage-first pass (28 rows, 1 cleared, 24 need a license).
