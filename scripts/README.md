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

Hand-editable source templates. Edit these, never the generated files in
`public/` — they are overwritten on every run.

| Template | Renders to |
| --- | --- |
| `index.html` | `public/index.html` (home: today's table, calendar, "coming up") |
| `holiday.html` | `public/holiday/<slug>/index.html` (was `PAGE_TEMPLATE` in `generate.py`) |
| `day.html` | `public/day/YYYY-MM-DD/index.html` |
| `page.html` | `/about/`, `/categories/`, `/category/<slug>/` |
| `partials/head.html` | shared `<head>` boilerplate: analytics, icons, stylesheets |
| `partials/header.html` | global header and navigation (`/styles/site.css` styles it) |
| `partials/footer.html` | footer and the "link copied" toast |
| `partials/icons.html` | the SVG icon sprite the buttons reference |
| `partials/scripts.html` | the script tags every page ends with |

Every page template pulls the partials in through `<!--TC:HEAD_COMMON-->`,
`SITE_HEADER`, `SITE_FOOTER` and `SITE_SCRIPTS`, so a navigation or footer
change is a one-file edit. The partials must never contain today's date: that is
what keeps the permanent `/day/` pages byte-identical from run to run.

All templates use `<!--TC:KEY-->` markers, substituted by `fill()`. That's
deliberate rather than `str.format()`: these files are full of CSS and JS
braces, and escaping every one would be a reliable source of bugs. An unfilled
marker raises instead of shipping a stray HTML comment to the live site, and
`<!--TC-ONLY ... -->` blocks are maintainer notes stripped from the output.

**Home page parity rule.** The home page ships today's list and calendar baked
into the HTML (so there is no layout shift and crawlers see real names), and its
inline script rebuilds the same markup when a visitor picks another day or
month. `obs_row()` and `calendar_html()` in `generate.py` and `obsRow()` /
`renderCalendar()` in `index.html` must stay identical; change one, change both.

## Site styling and behaviour

- `public/styles/site.css` — the whole design ("Almanac"): colour tokens in
  `:root`, header, tables, pills, buttons, layout. System fonts only. Colour is
  used as fill, never as thin text on white (contrast).
- `public/styles/ads.css` — ad slot sizes and reservations (unchanged rules,
  adapted to the new layout: the sidebar `rail` slot shows from 900px up).
- `public/js/site.js` — share (Web Share API, falling back to copy), copy link,
  add-to-calendar (an `.ics` built in the browser), search and jump-to-date.
  No dependencies; nothing in it changes layout on load.
- `public/styles/holiday.css` — no longer referenced by any page; safe to delete.
- Category pill colours and titles live in `CATEGORY_STYLE` in `generate.py`.

## Generated data

- `public/data/v2/YYYY-MM.json` — per-month calendar data, built from the same
  index as the `/day/` pages: `{ "2026-10-9": [[name, slug, category, yearly]] }`.
  The older `public/data/YYYY-MM.json` files are no longer written; they stay
  only so pages cached from before the redesign keep working and can be deleted
  a few days after launch.
- `public/data/search.json` — `[[name, slug], ...]` for the header search,
  fetched the first time the search box is focused.

## URL model — what owns what

Two layers, deliberately separated so they don't compete for the same queries:

| URL | Owns | Lifetime |
| --- | --- | --- |
| `/` | **Today.** Always the current date, with today's real holiday names rendered into the HTML at build time, plus the interactive calendar. | Evergreen; content changes daily |
| `/day/YYYY-MM-DD/` | **One specific date.** Permanent dated record, with the weekday, the observance list, and the year-specific note about which entries moved. | Permanent once published |
| `/holiday/<slug>/` | **One observance.** Always shows its *next* occurrence. | Evergreen; one URL forever |
| `/category/<slug>/`, `/categories/`, `/about/` | Browse-by-theme lists and the About page. | Evergreen |

Each page self-canonicalises. `/` is not canonicalised to today's dated page or
vice versa — they're different pages with different jobs, and collapsing them
would either stop `/` ranking for "what holiday is today" or stop the dated
archive being indexed at all.

Why the homepage is built at generate time: it used to render entirely
client-side, so the HTML a crawler received had a `—` where the date belonged
and empty containers where the holidays belonged. The baked markup must match
what `index.html`'s own `renderDay`/`renderCalendar` produce for the same day,
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
date → regenerated `public/data/v2/YYYY-MM.json` month files, regenerated
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

### Which years `next_occurrence()` looks at

For an **Annual** row it scans **nine** calendar years from today, not two.
Two is enough for any date that exists every year, but Feb 29 exists only in
leap years: with a two-year scan, Leap Day raised in three years out of four,
`main()` caught that as "unresolved", and no page was built for a date we
know perfectly well. Nine covers the widest real gap between leap years (eight,
across a non-leap century year such as 2100).

For a **Floating** row it still looks at this year and next, but a year whose
rule can't resolve is now **skipped rather than fatal**. A `lookup_table` whose
first hand-confirmed year is *next* year — which is what any newly added
administratively-dated holiday looks like for the rest of the current year —
used to raise on this year and be reported as having no date at all.
`super-bowl-sunday` was exactly that case. If *no* year resolves, the error is
re-raised, so an **expired** table still fails as loudly as before.

### The dated archive's forward horizon is derived, not configured

`day_end = max(occurrences.values())` — the `/day/` archive and the month data
files run from `DAY_ARCHIVE_START` to **the furthest next occurrence in the
whole dataset**. So one long-cycle row quietly moves the horizon for the entire
site: publishing a Feb 29 row in October 2026 pushes it from Oct 2027 to Feb
2028 and creates ~142 dated pages in one run. That is the same class of content
decision as moving `DAY_ARCHIVE_START` backwards (above), so it is worth
knowing before adding a row whose next occurrence is more than a year out.

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

### `FLOATING_RULES` — 102 entries, and which ones expire

Rule kinds (all computed in `generate.py`'s `compute_floating_date`):

| kind | means |
| --- | --- |
| `nth_weekday` | Nth given weekday of a month (Thanksgiving = 4th Thursday of Nov) |
| `last_weekday` | last given weekday of a month (Memorial Day, Earth Hour) |
| `nth_weekday_offset` | Nth given weekday of a month, then a day offset. This is how "weekday of the first full week" is expressed: the first full (Sun–Sat) week of a month begins on its first Sunday, so National Teacher Appreciation Day is 1st Sunday of May + 2. The offset may cross a month boundary on purpose — Oktoberfest opens 15 days before the first Sunday in October, which always lands in September. |
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
Ramadan, Eid al-Fitr, Islamic New Year, Naw-Rúz, Rosh Hashanah).

`yom-kippur` deliberately has **no table of its own**: it is 10 Tishrei, always
exactly nine days after the first day of Rosh Hashanah, so it is an
`offset_from_slug` off `rosh-hashanah` (checked against Hebcal for all eleven
years — identical in every one). One table to extend instead of two, and the
two can never drift apart.

Populated only through **2027**, because these have no formula at all
— the date is set administratively each year and has to be looked up:

- `national-teach-your-children-to-save-day` — the ABA sets it; **expires
  after 2027-04-27**
- `preakness-stakes` — the Maryland Jockey Club moved the 2027 race to
  May 23 and has not committed to a new permanent rule; **expires after
  2027-05-23**
- `belmont-stakes` — NYRA sets it each year, and the venue has been in flux;
  **expires after 2027-06-05**
- `super-bowl-sunday` — the NFL schedules the game each season. It has fallen
  on the second Sunday in February since 2022, but the league has not committed
  to that as a rule and has publicly discussed moving it if the season
  lengthens, so only announced dates go in the table. Holds **2027 only**
  (Feb 14, Super Bowl LXI) and **expires after 2027-02-14**. Add each later
  year from the NFL's own announcement; don't extrapolate "second Sunday"

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

## Long-form holiday content (E1)

A holiday page has two shapes. Without long-form content it is the short page
it has always been: hero, category tag, the one-paragraph `Description`, and
the back-link. With long-form content it additionally renders History, a
Timeline, How to observe, an FAQ, a five-year dates table, and Sources.

**A row with no long-form content renders byte-identically to the pre-E1
page.** That is a hard requirement, not a nicety — it is what makes it safe to
land the renderer before any content exists, and what keeps the daily
regeneration from producing a 2,439-page diff. Every piece of
`render_longform()` returns `""` when its field is absent, and the two template
slots (`{longform}`, `{extra_ld}`) collapse to nothing.

### The five Notion fields

| Notion property | `holidays.json` key | Holds |
|---|---|---|
| `Body` (rich text) | `body` | History / origin and How to observe, as `###` sections |
| `Timeline` (rich text) | `timeline` | 4–6 dated entries, one per line |
| `FAQ` (rich text) | `faq` | 3–5 question/answer pairs |
| `Sources` (rich text) | `sources` | One bullet per claim group, with URLs |
| `Content Status` (select) | `content_status` | Draft / Reviewed / Live — editorial only |

All five are optional. An absent or empty one is **left out of the JSON
entirely** rather than written as `""`, so `holidays.json` stays byte-identical
for rows that have no long-form content.

`Content Status` is editorial metadata and nothing else. The publish gate is
still the `Published` checkbox, exactly as before — a row with
`Content Status = Live` and `Published` unchecked does not reach the site. See
`docs/EXECUTION_PLAN.md` §4.

There is also a pre-existing `Source` (text) property, unrelated and still
unread by the exporter. It predates `Sources` and the two have not been
reconciled — see `docs/REVIEW.md`.

### The Markdown subset

These fields hold plain text in a deliberately tiny subset. Not general
Markdown, and **not** HTML:

```
### Heading          a section heading inside Body (rendered as <h2>, because
                     the page's <h1> is the holiday name in the hero)
blank line           paragraph break; single newlines are soft wraps
- item               list item
**bold**  *italic*   inline emphasis
[text](https://...)  link
```

Everything is HTML-escaped *before* those patterns are applied, so anything
else in a Notion field — a `<script>` tag, a stray `&` — ships as literal text
rather than as live HTML. Content comes from Notion rather than from the repo,
so the renderer treats it as data, not markup.

**Emphasis and links do not survive the round trip — don't rely on them.**
Typing `**bold**`, `*italic*` or `[text](url)` into a Notion field (by hand or
through the API) makes Notion store *rich-text annotations*, not those
characters. `export_from_notion.py` reads `plain_text`, which drops
annotations, so what reaches `holidays.json` has no markers at all. Every
long-form row written so far arrives this way. Practical consequences:

- **FAQ questions need no bolding.** `parse_faq()` takes the first line of a
  blank-line-separated block as the question (bolded or not). Before
  2026-10-10 it required `**bold**`, so every FAQ written parsed to zero
  pairs and both the FAQ section and the FAQPage structured data silently
  vanished from the page — on Halloween and Thanksgiving Day among others.
- **Write links as bare URLs**, which `md_inline()` auto-links. A
  `[text](url)` link loses its URL entirely on the way out of Notion, which
  for a `Sources` field means losing the citation.
- Bold years in `Timeline` and italic titles in `Body` are cosmetic and simply
  won't appear. Timeline entries still render: the parser keys on the `- `
  bullet, not the bold.

The markers are still honored when they *are* present, so a field edited
directly in the repo or pasted as literal text behaves as the table says.

Section order on the page follows `docs/EXECUTION_PLAN.md` §4: the Timeline is
slotted in **ahead of** the `How to observe` heading inside `Body`. If `Body`
has no such heading, the Timeline goes after the body instead.

### Dates table

`next_five_occurrences()` computes the next five dates straight off the same
rule engine the rest of the site uses — never typed by hand. It never raises:
a rule that runs out of resolvable years (a `lookup_table` past its last
hand-confirmed year) simply yields a shorter table, and a fixed Feb 29 skips
the years it doesn't land in. A four-row table is honest; a guessed fifth row
is not.

### FAQPage structured data

When `FAQ` is populated the page emits a **second** `application/ld+json`
block holding FAQPage, alongside the existing Event block rather than merged
into it. Keeping them separate is what lets a page without an FAQ keep its
exact pre-E1 head markup. Answers are flattened to plain text for the JSON-LD
and kept as HTML on the page.

### One fix that came out of this

`next_friday_the_13th()` scanned forward 400 days. The longest real gap between
two Friday the 13ths is 427 days (next instance: 2027-08-13 → 2028-10-13), so
every daily regeneration between 2027-08-14 and 2028-10-13 would have failed to
resolve `friday-the-13th`, dropping it out of the calendar with a WARNING for
fourteen months. The bound is now 460.
