# Data request (ChatGPT to Claude Code)

Keep drafting around the gap. Send requests in this form, one block per request, in `MI-A1_NOTES.md` or a file named `DATA_REQUEST_<date>.md`. Claude Code reads it from the disk and answers with a file or a claims row.

```
ID: DR-1
Story: MI-A1
Need: <the exact fact, number, document or file>
Why: <the sentence it would support, or the decision it unblocks>
Where it might be: <URL, outlet, FEC committee ID, TIP slug, or "unknown">
Blocking: yes / no   (no = you drafted around it)
```

Types Claude Code can do: open and read a source and add a claims row; FEC pulls (committee totals, independent expenditures, candidate filings); TIP lookups (profiles, race entries, grades, issue definitions); Kalshi captures with exact timestamps; roster checks against the official list; licensed-portrait searches; chart data and SVG graphics; file conversions.

Types Claude Code cannot do: read pages that block automated access (the Illinois State Board of Elections and Michigan Advance returned 403; Claude does not work around bot checks, so those need a human to paste the text); interview anyone; contact campaigns; decide that something is true because it is plausible.
