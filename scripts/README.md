# scripts/

## `holidays.json`

The canonical, Notion-independent source of truth for every holiday on the
site: 502 entries, each with `slug`, `name`, `category`, `description`,
`recurrence` (`"Annual"` or `"Floating"`), and either a fixed `month`/`day`
(Annual) or a `floating_rule` (Floating) — plus a `display_order` used to
keep each day's holiday list in its original, deliberate order across
regenerations.

Built once, for Phase 3, from the live site's 502 pages (name, date,
category, description all extracted from the HTML that had already been
hand-reviewed) merged with the `Recurrence` classification backfilled into
Notion that same session. Going forward, this file should be regenerated
from Notion directly (pull `Holiday`, `Category`, `Description`,
`Recurrence`, `Date` for every published row) rather than re-scraped from
the site — Notion is the actual source of truth; this file is a build
artifact `generate.py` consumes.

Floating rules currently defined for 7 holidays: Labor Day (1st Monday of
September), National Grandparents Day (1st Sunday after Labor Day),
Columbus Day / Indigenous Peoples' Day / Canadian Thanksgiving Day (2nd
Monday of October), Sweetest Day (3rd Saturday of October), and Autumnal
Equinox (astronomical — a hand-confirmed lookup table by year, currently
populated through 2030; extend it before it runs out, don't guess a date).

## `generate.py`

Pure function: `holidays.json` + a site's `public/` directory + a "today"
date → regenerated `public/data/YYYY-MM.json` month files, regenerated
`public/holiday/<slug>/index.html` pages, and a regenerated `sitemap.xml`.
No Notion dependency, no network calls — safe to run repeatedly and to
call from a future scheduled job (see roadmap.md's Phase 4 plan for a
daily GitHub Actions workflow).

Each run picks every holiday's *next* occurrence on or after "today" —
this year's date if it hasn't passed yet, otherwise next year's — so a
holiday quietly rolls forward a year once its date has passed, and
everything else regenerates byte-identical. That's the whole "auto-recur"
behavior: re-run this, `git diff` shows only what actually needs review
(holidays that just rolled to a new year), and Jay pushes when it looks
right.

```
python3 scripts/generate.py \
  --holidays scripts/holidays.json \
  --site public \
  --today 2026-09-13 \
  [--dry-run] [--report report.json]
```

`--dry-run` computes and reports without writing anything — useful to see
the diff size before committing to it. The report's `occurrences` map
gives the computed date for every slug, which is worth spot-checking
after adding a new floating rule or extending the equinox lookup table.

## Refreshing from Notion

To regenerate `holidays.json` from Notion directly (rather than the
site-scrape bootstrap this file used the first time): pull every
published row's `Holiday`, `Category`, `Description`, `Recurrence`, and
`Date` fields, slugify the name the same way `public/index.html`'s
client-side `slugify()` does (lowercase, `&`→`and`, strip apostrophes,
non-alphanumerics→hyphens), and preserve each holiday's existing
`display_order` unless you have a real reason to change it.
