# scripts/

## `holidays.json`

The canonical, Notion-independent source of truth for every holiday on the
site — currently ~2,439 entries (2,345 Annual, 94 Floating) covering a full
rolling year. Each entry has `slug`, `name`, `category`, `description`,
`recurrence` (`"Annual"` or `"Floating"`), and either a fixed `month`/`day`
(Annual) or a `floating_rule` (Floating) — plus a `display_order` used to
keep each day's holiday list in its original, deliberate order across
regenerations.

**This file is a build artifact, not something to hand-edit.** It is
regenerated from Notion by `export_from_notion.py` on every daily run;
Notion is the source of truth. (It was bootstrapped once in Phase 3 from
the live site's then-502 hand-reviewed pages, which is why older notes
describe it as site-derived.)

## `templates/`

Hand-editable source templates for the two generated page types that aren't
built from `PAGE_TEMPLATE` inside `generate.py`:

- **`templates/index.html`** → renders to `public/index.html`. **Edit the
  template, never `public/index.html`** — the latter is overwritten on every
  run, and carries a comment saying so.
- **`templates/day.html`** → renders to `public/day/YYYY-MM-DD/index.html`.

Both use `<!--TC:KEY-->` markers, substituted by `fill()`. That's deliberate
rather than `str.format()`: these files are full of CSS and JS braces, and
escaping every one would be a reliable source of bugs (`PAGE_TEMPLATE` *does*
use `.format()`, which is exactly why its inline analytics snippet needs
doubled braces). An unfilled marker raises instead of shipping a stray HTML
comment to the live site, and `<!--TC-ONLY ... -->` blocks are maintainer notes
stripped from the output.

## URL model — what owns what

Two layers, deliberately separated so they don't compete for the same queries:

| URL | Owns | Lifetime |
| --- | --- | --- |
| `/` | **Today.** Always the current date, with today's real holiday names rendered into the HTML at build time, plus the interactive calendar. | Evergreen; content changes daily |
| `/day/YYYY-MM-DD/` | **One specific date.** Permanent dated record, with the weekday, the observance list, and the year-specific note about which entries moved. | Permanent once published |
| `/holiday/<slug>/` | **One observance.** Always shows its *next* occurrence. | Evergreen; one URL forever |

Each page self-canonicalises. `/` is not canonicalised to today's dated page or
vice versa — they're different pages with different jobs, and collapsing them
would either stop `/` ranking for "what holiday is today" or stop the dated
archive being indexed at all.

Why the homepage is built at generate time: it used to render entirely
client-side, so the HTML a crawler received had a `—` where the date belonged
and empty containers where the holidays belonged. The baked markup must match
what `index.html`'s own `renderHero`/`renderList` produce for the same day,
since that script re-renders the same elements the moment it loads — if you
change one side, change the other.

### `/day/` archive behaviour

`DAY_ARCHIVE_START` in `generate.py` is the archive's start line (currently
2026-10-08, the launch date). Every date from there through the end of the
forward window gets a page; dates with no observances get none.

Past pages are **regenerated every run and come out byte-identical**, because
`build_day_index()` derives a date's contents only from the holiday data and
the date itself — never from "today". That's what lets the archive stay in sync
with sitewide chrome changes (a new analytics tag, a footer edit) without
churning git or drifting. It also means a past page reflects the *current*
Notion data for that date, so adding an observance to a date retroactively
updates that date's historical page — correct for "the calendar for that date",
worth knowing if you'd expect a frozen snapshot instead.

Do not move `DAY_ARCHIVE_START` backwards casually: that backfills dated pages
for dates the site never covered, which is a content decision (and a
near-duplicate-content risk), not a tweak. Moving it forward orphans pages that
are already published and indexed.

## `generate.py`

Pure function: `holidays.json` + a site's `public/` directory + a "today"
date → regenerated `public/data/YYYY-MM.json` month files, regenerated
`public/holiday/<slug>/index.html` pages, `public/day/YYYY-MM-DD/index.html`
dated pages, `public/index.html`, and a regenerated `sitemap.xml`.
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
  [--templates scripts/templates] [--dry-run] [--report report.json]
```

`--dry-run` computes and reports without writing anything — useful to see
the diff size before committing to it. The report's `occurrences` map
gives the computed date for every slug, which is worth spot-checking
after adding a new floating rule or extending a lookup table.

### If a holiday's date can't be resolved

A floating rule can stop producing a date — most commonly a `lookup_table`
that has run out of hand-confirmed years. When that happens the generator
**skips that one holiday and finishes the run** rather than aborting:

- its existing `public/holiday/<slug>/index.html` is left exactly as it is
  (a stale date on one page beats deleting it or publishing a dateless one),
- it drops out of the `public/data/YYYY-MM.json` calendar listings until the
  rule is fixed,
- its sitemap entry is kept, with its previous `lastmod`,
- the slug appears in the report's `unresolved_holidays` and `pages_skipped`,
  and `main()` prints a `WARNING:` line per holiday to stderr.

This matters because the generator runs unattended: if one expired lookup
table raised, the daily workflow would fail and the **whole site** would
silently stop rolling holidays forward. Degrading to one frozen holiday,
loudly, is the intended tradeoff. When `GITHUB_ACTIONS=true`, the generator
also emits a `::warning::` workflow command, so a skipped holiday shows up as
a visible annotation on the Actions run summary rather than only in the log —
no workflow YAML changes needed to pick that up.

### `sitemap.xml` and `lastmod`

`lastmod` reflects when a page's content actually changed, not when the
generator last ran. Each URL's `lastmod` is carried forward from the
sitemap already on disk, and only pages this run created or changed get
today's date (the homepage counts as changed whenever any month data file
did). A URL with no previous entry gets today.

Don't "simplify" this back to stamping every URL with today — that was the
original behavior, and it both rewrote all ~2,400 URLs in every daily
commit (a 4,880-line diff a day) and told crawlers the entire site changed
daily when roughly ten pages had.

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
holidays' actual date rules live in this script's `FLOATING_RULES` dict,
not in Notion — Notion only has an Annual/Floating switch, not "which
rule." Adding a new Floating holiday means adding its rule here by hand,
or `export_from_notion.py` skips the row with a warning.

### `FLOATING_RULES` — 94 entries, and which ones expire

Rule kinds (all computed in `generate.py`'s `compute_floating_date`):

| kind | means |
| --- | --- |
| `nth_weekday` | Nth given weekday of a month (Thanksgiving = 4th Thursday of Nov) |
| `last_weekday` | last given weekday of a month (Memorial Day, Earth Hour) |
| `last_weekday_offset` | last given weekday, then a day offset (Administrative Professionals Day) |
| `last_weekday_before_date` | last given weekday strictly before a fixed date (Super Saturday) |
| `nearest_weekday_to_date` | given weekday nearest a fixed date (Advent Sunday ≈ Nov 30) |
| `after_labor_day_sunday` | the Sunday after Labor Day (National Grandparents Day) |
| `us_election_day` | Tuesday after the first Monday in November |
| `easter_offset` | signed day offset from Western Easter, computed via the Computus algorithm — no table needed, valid for any year |
| `offset_from_slug` | signed day offset from **another holiday in the dataset** (Black Friday = `thanksgiving-day` + 1), resolved recursively with memoization and cycle detection |
| `last_weekday_before_slug` | last given weekday on/before another holiday's date (World Sleep Day ≈ Friday before the spring equinox) |
| `next_friday_13` | special-cased in `next_occurrence` — a year can hold 0–3 Friday-the-13ths, so it scans forward from today rather than resolving "for a year" |
| `lookup_table` | hand-confirmed `{year: "MM-DD"}` — **the only kind that expires** |

**`lookup_table` holidays need periodic extension. Don't guess a date —
check an almanac or the organizing body, then add the year.**

Populated through **2036** (astronomical and lunar/lunisolar — equinoxes,
solstices, Chinese New Year, Diwali, Hanukkah, Tu BiShvat, Purim, Passover,
Ramadan, Eid al-Fitr, Islamic New Year, Naw-Rúz).

Populated only through **2027**, because these three have no formula at all
— the date is set administratively each year and has to be looked up:

- `national-teach-your-children-to-save-day` — the ABA sets it; **expires
  after 2027-04-27**
- `preakness-stakes` — the Maryland Jockey Club moved the 2027 race to
  May 23 and has not committed to a new permanent rule; **expires after
  2027-05-23**
- `belmont-stakes` — NYRA sets it each year, and the venue has been in flux;
  **expires after 2027-06-05**

Once one of those dates passes, that holiday is skipped with a loud warning
on every daily run (see `generate.py` above) until its table gains the next
year. The site keeps updating in the meantime.

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

**Status: live since 2026-09-14** — the one-time setup below is done and the
workflow has been committing a regeneration every day. Occasionally GitHub
drops a scheduled cron run (it happened 2026-10-02); the next day's run
catches up automatically, so no intervention is needed.

**One-time setup, for reference / if the token ever needs rotating** (neither
of these can be done from a Claude session — both require signing in as the
account owner):

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


## Display ad slots

Self-served house ads — no ad network. Standard IAB units in conventional
positions, currently running placeholder creatives.

| Slot | Unit | Homepage | `/holiday/` | `/day/` | Loading |
| --- | --- | --- | --- | --- | --- |
| `leaderboard` | 728x90 desktop / 320x50 mobile | yes | yes | yes | eager |
| `incontent` | 300x250 | — | yes | yes (lists of 8+, after item 5) | lazy |
| `footer` | 300x250 | yes | yes | yes | lazy |
| `rail` | 300x600 | — | yes | yes | lazy |

The leaderboard sits *below* the hero, not above it: the hero image is the
likely Largest Contentful Paint element on these pages, and pushing it down to
make room for an ad would directly damage that metric.

The `rail` only appears at 1200px and wider, where there's genuinely room beside
the 760px reading column. Below that `.page-grid` stays `display:block`, so the
content column is pixel-identical to what it was before ads existed — verified
in Chromium at 1000px, ads on and off.

### What's running now

PodIQ house banners, HTML5 creative, one folder per size under
`public/ads/podiq/`:

| Slot | Creative |
| --- | --- |
| `leaderboard` | `/ads/podiq/728x90/`, with `/ads/podiq/320x50/` below 768px |
| `incontent` | `/ads/podiq/300x250/` |
| `footer` | `/ads/podiq/300x250/` |
| `rail` | `/ads/podiq/300x600/` |

The supplied set also includes 160x600 and 970x250, which no slot currently
uses. The original per-size zips are the master copies — keep them, they're
what an ad server or DSP wants.

**Shared assets.** Each size shipped self-contained, which meant four copies of
the same fonts and logo — 73% of the asset weight was duplicates, and a desktop
page showing three different sizes would download the same 24KB font three
times over. The repo copies are rewritten to point at `/ads/podiq/shared/`
instead, so one download serves every slot on the page. If you re-export the
banners, redo that rewrite (it's just `fonts/` → `../shared/fonts/` and the two
PNG paths in each `index.html`).

**Click-through** lives in each banner's own `index.html`, in the `clickTag`
variable near the top. It is not set in `house.js`.

### Changing what runs

**Edit `public/ads/house.js`. That is the only file involved.** It takes two
kinds of creative:

- **HTML5 banner** — `type: "html"` plus `src` pointing at the folder. Served
  in an iframe; it does its own click handling via its clickTag, so it never
  gets wrapped in a link.
- **Image** — `img` plus an optional `href`. Wrapped in a link with
  `rel="sponsored noopener"` when `href` is set, which is what search engines
  expect on a paid placement.

Either way `width` and `height` must be the creative's real pixel size — those
are what stop the page jumping as it loads. Drop a new banner folder into
`public/ads/<campaign>/<size>/` (or an image into `public/images/ads/`), point
the entry at it, commit. No template edits, no regeneration of ~2,800 pages.

- More than one creative in a slot and one is picked at random per page view.
- A slot set to `[]` collapses to nothing.
- `mobile` supplies a small variant served below 768px, so what's delivered
  matches the height the stylesheet reserved.

Set `SHOW_LABEL = true` here **and** `ADS_LABELLED = True` in `generate.py`
when third-party paid creative runs. It's off for house ads.

### Why HTML5 creative is sandboxed

The iframes carry `sandbox="allow-scripts allow-popups
allow-popups-to-escape-sandbox"`. The creative can run its own animation and
open its click-through, but cannot reach this page's DOM, cookies or storage —
worth having even for first-party creative, and essential if third-party
creative ever runs here.

The cost is that the iframe gets an opaque origin, which makes its own font
files cross-origin. `public/_headers` therefore sends
`Access-Control-Allow-Origin: *` for `/ads/*/shared/fonts/*`. **This is load
bearing** — verified by serving the same pages without it, where every custom
face fails with a CORS error and the banners drop to system fonts. Remove the
header and the creative silently degrades.

### Why the slots bleed into the column padding

Creatives are wider than the reading column's inner width: 728px against
712px on desktop, and on a 320px phone a 300px rectangle against 272px. Each
in-flow slot therefore reclaims its container's horizontal padding, and has its
`max-width` lifted (otherwise that caps the box straight back and clips the
banner). Verified from 1440px down to 320px: every creative renders at full
size with no horizontal page overflow.

### Why the on/off switch lives in generate.py

`ADS_ENABLED` and `ADS_LABELLED` in `generate.py` bake `class="ads-enabled"`
onto `<html>` at build time, and `public/styles/ads.css` keys every dimension
off that class.

This was originally done in JavaScript, and it was wrong: `slots.js` is
deferred, so the class landed *after* first paint, every slot appeared at once
and shoved the page down — a measured 0.09 CLS. A static class costs nothing and
measures 0.0000. If you ever move this back into script, that regression comes
back with it.

`ADS_ENABLED` has to agree with `house.js`: the flag reserves the space, that
file fills it. Setting it `False` removes all ad space from the site.

### How the slot machinery works

`public/ads/slots.js` finds every `[data-ad-slot]`, decides when it loads, and
hands it to whatever provider is defined on `window.TC_ADS` (that's `house.js`).
Lazy slots load via IntersectionObserver with a 300px margin, so they're ready
before they scroll into view but cost nothing to a visitor who never gets there.
A slot whose provider calls `setFilled(false)` collapses instead of leaving a
hole. An exception inside a provider is caught — an ad failure never takes the
page down.

Keeping the provider separate from the machinery means switching to a network
later (Google Ad Manager, AdSense, anything else) is a matter of replacing
`house.js` with a file that defines `window.TC_ADS.fill(mount, slot)` the same
way. `slot` carries the position name and its standard IAB sizes. Nothing in
the templates or the generator changes.

Note: the site sends no Content-Security-Policy, so third-party ad scripts are
not blocked today. If a CSP is ever added, any ad host needs allowing there.
