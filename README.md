# Today Celebrates

[todaycelebrates.com](https://todaycelebrates.com) is a daily calendar of
national, international and world holidays and observances: about 2,400 of them,
each with its own page, plus a permanent page for every date.

It is a static site. There is no framework and no build step on the server: a
Python script turns a data file into plain HTML, and Cloudflare serves the
result. That is deliberate, and it is why the pages are fast (layout shift is
0.0000, and a day page is well under 200 KB).

## How it works

```
Notion database ──► scripts/export_from_notion.py ──► scripts/holidays.json
                                                            │
                                  scripts/generate.py ◄─────┤  + scripts/templates/
                                                            ▼
                                                         public/   ──► Cloudflare
```

- **Content** lives in a Notion database, "Today Celebrates — Holidays", which
  is the source of truth. Rows are reviewed and approved there.
- **`export_from_notion.py`** pulls the approved rows into `scripts/holidays.json`.
  Don't hand-edit that file; it is overwritten on every run.
- **`generate.py`** takes `holidays.json` and a date and writes everything under
  `public/`: the home page, one page per holiday, one per date, category pages,
  the monthly calendar data, the search index and `sitemap.xml`. It makes no
  network calls and is safe to run repeatedly; unchanged pages come out
  byte-identical, so the git diff only shows what really changed.
- **Cloudflare Workers** serves `public/` as static assets (`wrangler.jsonc`).
  Pushing to `main` deploys automatically.
- **A daily GitHub Action** (`.github/workflows/daily-regenerate.yml`, 08:00 UTC)
  re-exports from Notion, regenerates, and pushes if anything changed. This is
  what rolls a holiday forward to next year once its date has passed.

## Repository layout

| Path | What it is |
| --- | --- |
| `public/` | The deployed site. Mostly generated; see below for what is hand-edited |
| `public/styles/site.css` | The whole design: colour tokens, header, tables, buttons |
| `public/styles/ads.css` | Ad slot sizes and space reservations |
| `public/js/site.js` | Share, copy link, add to calendar, search, jump to date |
| `public/ads/` | House ads (`house.js` controls what runs in each slot) |
| `public/robots.txt`, `public/llms.txt` | Crawler policy and a guide for AI tools |
| `public/_headers` | Cloudflare cache rules |
| `scripts/generate.py` | The site generator |
| `scripts/export_from_notion.py` | Notion to `holidays.json`, including the rules for moving holidays |
| `scripts/templates/` | Page templates and the shared header, footer and head partials |
| `scripts/README.md` | Detailed notes on the generator, URL model and data files |
| `docs/` | Execution plan, run log and reviews for the automated build-out |

**Edit the templates and `generate.py`, never the generated pages.** Anything
under `public/holiday/`, `public/day/`, `public/category/`, `public/about/`,
`public/categories/`, `public/data/` and `public/index.html` is overwritten on
the next run.

## URL model

| URL | What it is |
| --- | --- |
| `/` | Today. Always the current date, baked into the HTML at build time |
| `/holiday/<slug>/` | One observance. Always shows its next occurrence; one URL forever |
| `/day/YYYY-MM-DD/` | One date. A permanent record, starting 2026-10-08 |
| `/category/<slug>/`, `/categories/` | Browse by theme |
| `/about/` | About the site |

`scripts/README.md` explains why these are kept separate.

## Working on it locally

Regenerate the site (use a throwaway copy when experimenting):

```
python3 scripts/generate.py \
  --holidays scripts/holidays.json \
  --site public \
  --today "$(date +%F)"
```

Add `--dry-run` to see what would change without writing anything.

Preview with the real caching and asset rules:

```
npm install
npx wrangler dev
```

or, for a quick look without Cloudflare's rules, `python3 -m http.server -d public`.

Pulling fresh data from Notion needs a `NOTION_TOKEN` (stored as a GitHub secret
for the daily run).

There is no automated test suite. Before pushing a change to the generator or
templates, regenerate into a copy of `public/`, run it twice to confirm the
second run changes nothing, and check the pages in a browser.

## Things worth knowing

- **Layout shift is protected.** The header is a fixed height, every ad slot
  reserves its exact size, and anything the home page fills in with JavaScript
  is already baked into the HTML. The home page's inline script and
  `obs_row()` / `calendar_html()` in `generate.py` must produce identical markup.
- **Shared page furniture is one edit.** The header, footer and head live in
  `scripts/templates/partials/`. They must never contain today's date, or every
  permanent `/day/` page would change daily.
- **Ads are house ads** for Jay's own products; there is no ad network.
  `public/ads/house.js` is the only file that decides what runs.
- **Analytics** is Google Analytics 4, installed from the shared head partial.
- **AI crawlers are welcome.** `robots.txt` allows them and asks for attribution
  and links back; `llms.txt` tells AI tools how to cite the site.

## The automated build-out

A 90-day plan of nightly engineering runs and Monday/Wednesday/Friday content
runs is described in `docs/EXECUTION_PLAN.md`, which is also the shared state
those runs read and write. The one rule that matters when working by hand: the
automated runs never commit or push, and they stop if the working tree has
uncommitted changes, so commit or discard your own work before leaving it
overnight.

## Roadmap

Deep, researched content for every holiday (the current descriptions are short
templates); perennial pages for each calendar date; an observance type
taxonomy; and later, paid occasion pages. See `docs/EXECUTION_PLAN.md` for the
queue.

## Owner

Built and run by Jay. Changes are committed and pushed through GitHub
Desktop.
