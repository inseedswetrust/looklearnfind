# LookLearnFind

looklearnfind.com: a static editorial site (Look · Learn · Find) with a live Ledger backend (PHP + SQLite).

    python3 build.py            # builds ./dist  (stdlib only)
    python3 build.py --zip      # also writes release/looklearnfind-site.zip

- `content/` pages; `content/learn/` stories; `content/find/` Finds. `data/threads.json` curated threads. `data/site.json` nav, categories, topics.
- `static/` copied as-is: CSS, JS, images, and `api/` (the PHP backend).
- `docs/DEPLOY.md` install on cPanel · `docs/BRAND.md` brand and voice · `docs/SITEMAP_AND_COPY.md` sitemap · `docs/NEXUS.md` how Look, Learn and Find connect · `docs/FIND_LEDGER_PROPOSAL.md` Ledger mechanics.
- `reference/` approved mockups and assets. Clip titles, handles, dates and photos in them are illustrative.
- `tests/` API and link checks.

All sample stories, Finds and Ledger rows are marked **illustrative**; sources on sample stories are labelled placeholders.
