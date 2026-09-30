# Deploying LookLearnFind (cPanel, same pattern as the seeds site)

The site is static HTML plus a small PHP + SQLite backend for the Ledger. No database server to set up.

## Build
    python3 build.py --zip          # writes release/looklearnfind-site.zip (files at the zip root, hidden files included)

## Install
1. In cPanel, open the add-on domain's folder (not shared `public_html`) and upload/extract the zip so `index.html`, `.htaccess`, `api/` sit at its root.
2. **PHP**: 7.4 or newer (MultiPHP Manager). In "Select PHP Version" make sure `pdo_sqlite`, `curl`, `mbstring` are ticked.
3. **Data folder**: create `llf-data/` *next to* the website folder (one level above it) and make it writable (0700). The database (`ledger.sqlite`) and `config.php` live there, outside the web. If you cannot, the site falls back to `api/_data/` (blocked from the web by `.htaccess`).
4. **Config**: copy `docs/config.example.php` to `llf-data/config.php` and set `admin_emails` to yours.
5. **SSL**: turn on AutoSSL, then uncomment the two HTTPS redirect lines in `.htaccess`.
6. Visit `/account/?mode=signup` and create a profile with your admin email. You are now an admin; `/admin/` (or the "Editors" link in the menu) opens the review desk.
7. Optional: `/admin/` > Sample data > "Load sample entries" to see the Ledger populated with clearly marked **illustrative** rows. Clear them before launch.

## Smoke test after upload
- `/api/me` returns `{"user":null,"csrf":null}`
- `/look/` loads; signing up and saving a link works; the entry appears in `/admin/` > Queue when submitted publicly.
- Submit a test on `/contact/`; it lands in the `messages` table.

## Day to day
- **Content** (stories, Finds, threads) is edited in the repo (`content/`, `data/threads.json`), then rebuilt and re-uploaded. The database is never touched by a redeploy, but **do not delete `llf-data/`**.
- **Back up** `llf-data/ledger.sqlite` (download via cPanel File Manager). Members can export their own saves from `/account/`.
- **Newsletter / contact / contribution** submissions are stored in the same database (tables `newsletter`, `messages`).
- **Link checks**: editors can recheck a link or mark it unavailable from `/admin/` > Entries. Unavailable entries leave active results and show "Original unavailable" with the last-checked date.
- Provider metadata: YouTube and TikTok expose title, creator and a thumbnail without credentials. Instagram exposes nothing without an app token, so contributors supply the creator handle and the entry falls back to URL + note. Durations and dates for YouTube need `youtube_api_key`.

## Tests (development)
    LLF_DATA=/tmp/llfdev LLF_DEV=1 php -S 127.0.0.1:8090 -t dist tests/router.php &
    echo '<?php return ["admin_emails"=>["editor@test.local"]];' > /tmp/llfdev/config.php
    php static/api/tools/seed_demo.php dist      # with LLF_DATA set as above
    python3 tests/api_test.py && python3 tests/links_test.py
