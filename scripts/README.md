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

## `export_from_notion.py`

Pulls every `Published` row from the "Today Celebrates — Holidays" Notion
database and writes `holidays.json` in the exact shape `generate.py`
expects — this is the piece that replaces the Phase 3 site-scrape
bootstrap now that Notion is the actual source of truth going forward.

```
NOTION_TOKEN=secret_xxx python3 scripts/export_from_notion.py scripts/holidays.json
```

Requires a Notion **internal integration token** with access to the
database (one-time setup, see below). For each published row it reads
`Holiday`, `Date`, `Category`, `Description`, `Recurrence`, and `Order`
(used as `display_order` — falls back to sorting last if a row has no
Order set, so it's worth eyeballing that Order is actually populated
across the database if per-day ordering matters to you). Floating
holidays' actual date rules (nth-weekday-of-month, the Autumnal Equinox
lookup table, etc.) live in this script's `FLOATING_RULES` dict, not in
Notion — Notion only has an Annual/Floating switch, not "which rule."
Adding a new Floating holiday means adding its rule here by hand.

Rows missing a required field (Category, Description, a valid Recurrence,
etc.) are skipped with a warning printed to stderr rather than failing
the whole run — one bad row shouldn't take down the daily site update.
As a safety net against a Notion outage or auth failure silently
returning an empty/partial result, the script refuses to write
`holidays.json` if the resulting holiday count would be zero, or would
drop by more than 20% from the previous run's count.

## Phase 4: daily automation

`.github/workflows/daily-regenerate.yml` runs `export_from_notion.py` →
`generate.py` → commits and pushes to `main` once a day (~08:00 UTC,
early morning US Eastern), reusing the existing Cloudflare Workers Build
auto-deploy on push. Also runnable on demand from the repo's Actions tab
(`workflow_dispatch`).

**One-time setup Jay needs to do** (neither of these can be done from a
Claude session — both require signing in as the account owner):

1. **Create a Notion integration:** go to
   [notion.so/my-integrations](https://www.notion.so/my-integrations) →
   "New integration" → give it a name (e.g. "Today Celebrates site sync")
   → under the workspace this database lives in → copy the "Internal
   Integration Secret" it gives you (starts with `secret_` or `ntn_`).
2. **Share the database with it:** open the "Today Celebrates — Holidays"
   database in Notion → `...` menu (or "Connections") → Connect to →
   select the integration you just created. Without this step the
   integration can authenticate but the query will return zero rows.
3. **Add it as a GitHub secret:** in the `NetWurkai/todaycelebrates` repo
   on GitHub → Settings → Secrets and variables → Actions → "New
   repository secret" → name it exactly `NOTION_TOKEN` → paste the
   integration secret from step 1.

After that, trigger the workflow once manually (Actions tab → "Daily site
regeneration" → "Run workflow") to confirm it runs clean before trusting
the schedule — check the run's logs for the generation report and any
`WARNING:` lines from the export step.
