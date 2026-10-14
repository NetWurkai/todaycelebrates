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

Three layers, deliberately separated so they don't compete for the same
queries:

| URL | Owns | Lifetime |
| --- | --- | --- |
| `/` | **Today.** Always the current date, with today's real holiday names rendered into the HTML at build time, plus the interactive calendar. | Evergreen; content changes daily |
| `/day/YYYY-MM-DD/` | **One specific date.** Permanent dated record, with the weekday, the observance list, and the year-specific note about which entries moved. | Permanent once published |
| `/<month>-<day>/` | **One calendar date, any year** (`/october-8/`). The observances that fall on it *every* year, plus a note naming the years a rule-dated one lands there. The page for the recurring query. | Permanent; refreshed, not rewritten |
| `/holiday/<slug>/` | **One observance.** Always shows its *next* occurrence. | Evergreen; one URL forever |
| `/dates/` | **The hub for the 366.** Every date of the year grouped by month, with each date's fixed-date count. Linked from the header nav and the footer on every page. | Evergreen |
| `/holidays/<year>/` | **One year of the dated archive** (`/holidays/2027/`). Every date that year has a `/day/` page for, grouped by month, with each date's weekday and observance count. The index of the archive, not a page that competes for a query. | Evergreen; the current year's grows daily |
| `/category/<slug>/`, `/categories/`, `/about/` | Browse-by-theme lists and the About page. | Evergreen |

Calendar feeds (`/calendar.ics`, `/category/<slug>/calendar.ics`,
`/holiday/<slug>/event.ics`) sit alongside these but are not pages and are not
in the sitemap — see "Calendar export (E5)".

Each page self-canonicalises. `/` is not canonicalised to today's dated page or
vice versa — they're different pages with different jobs, and collapsing them
would either stop `/` ranking for "what holiday is today" or stop the dated
archive being indexed at all. The same reasoning holds for `/october-8/` and
`/day/2026-10-08/`: the perennial page is the one meant to rank for "October 8
holidays", the dated page is the record of that one October 8, both are
self-canonical, and both stay in the sitemap. Neither carries a cross-domain
`rel=canonical` to the other.

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

### Perennial date pages (`/october-8/`)

One page per calendar date with no year in the URL, 366 of them, February 29
included. Three of the four leading competitors have this URL and we did not;
it is the page that answers "what is celebrated on October 8" rather than one
year's version of that question.

**What goes on it, and what deliberately does not.** `build_perennial_index()`
splits a date's observances in two:

- **fixed-date (`Annual`) rows** are on that date every year, so they are the
  page's own content: the numbered table, the count in the title, the
  `ItemList` structured data.
- **rule-dated (`Floating`) rows** are *not* October 8 observances — they are
  observances that fall on October 8 in 2027 and 2032. They appear in a note
  that names those years, never in the table, and never in the count.

The year-specific angle — the weekday, and where a moveable observance goes
*next* year — stays on `/day/YYYY-MM-DD/`. That split is the only thing keeping
the two page types from being near-duplicates, so don't move the floating rows
into the table "for completeness": it would make the perennial page a copy of
whichever year was generated, and make it wrong the following year.

**`PERENNIAL_YEARS`** (10) is how many calendar years from the current one the
wider index pass examines, and it only affects that note. A `lookup_table` rule
that runs out of confirmed years simply contributes the years it has and lands
in the report's `perennial_index_skipped` — the three administratively-dated
rows are there today. That list is informational: unlike `unresolved_holidays`
it is not a warning, because a rule not reaching 2035 is normal.

**`PERENNIAL_EMPTY_PAGES`** (True, **decided by Jay on 2026-10-11**) decides
what happens to a date with nothing on it. 25 month-days have no fixed-date
observance and 6 have nothing at all in the window (Jan 3, Jan 6, Jan 12,
Jun 11, Jul 10, Aug 31 on 2026-10-11 — it was 8 the day before; the list
shrinks as rows land, so it is not a fixed set). True publishes all 366, so no
date in the year 404s and the URL stays guessable; False publishes only the
dates that have something, the prev/next ring skips the rest, and `/dates/`
lists them as plain text instead of links. It is a content decision, not a code
change.

**Navigation is a closed ring.** Prev/next and the "Nearby dates" rail wrap at
December 31, so every one of the 366 is reachable from its neighbours no matter
which one a crawler lands on — that is what keeps a date with nothing on it from
being orphaned. The cross-link to the dated pages is in the note at the foot of
the content; the other half of it is `PERENNIAL_LINK` in `render_day_page()`.

**The one value on these pages that moves.** Each table row carries the next
date this month-day comes round, because that is what the "Add to calendar"
button needs. So on the day after a date passes, that one page's rows roll to
next year's ISO date: **exactly one perennial page changes per day**, which is
the churn to expect in the daily commit. Everything else on the page is derived
from the calendar and the holiday data alone.

**Cache headers.** These pages sit at the top level, so `public/_headers` has
one rule per month (`/january-*` … `/december-*`) rather than a single splat,
which would match the whole site.

**Where they sit in the navigation** (decided 2026-10-11). The header's
**Calendar** tab and the footer's Calendar link point at **`/dates/`**, not at
`/#calendar` as they did before. Three reasons:

1. A sitewide nav link pointing at a homepage fragment is spent on something no
   crawler can follow and no second page can be reached through. Pointing it at
   a real page puts all 366 one click from every page on the site, which is what
   actually keeps them out of orphan territory — the prev/next ring alone makes
   them reachable, not discoverable.
2. `chrome_for("CALENDAR")` was already the chrome handed to `/day/` and
   perennial pages, so those pages were marking a nav tab current for a URL they
   had no fragment of. Now the tab and the pages agree.
3. The homepage calendar widget is unchanged and still reachable: `/dates/`
   carries the one link to `/#calendar`, and the homepage is the Today tab.

The breadcrumb hierarchy follows from that, on both page types:
`Today / Calendar / October 8` on a perennial page, and
`Today / Calendar / October 8 / Halloween` on a holiday page.

**Holiday pages link to the perennial page, not the dated one** (decided
2026-10-11). A holiday page lives forever at one URL, so its parent should too —
the dated page's URL changes every year, which makes it a poor breadcrumb
ancestor and a poor back-link. So the breadcrumb's date crumb and the
`&larr; See everything October 31 celebrates` back-link both point at
`/october-31/`. The specific dated page did not lose its inbound links: it is
linked from the **Date row of the spec list** (the `<time>` element is wrapped in
a link to it, which is also the more honest place for it) and from
*All N on October 31* in the "Also on" sidebar. Every holiday page carries at
least one link to its dated page — there is an assertion for that, because the
sidebar link is conditional and the spec row is not.

### Year indexes (`/holidays/2027/`)

E3's fourth bullet. One page per year the dated archive touches, built in
`year_index_html()` and derived entirely from `day_dates` — there is nothing to
configure and no list of years to maintain. A year's page appears on the run
that creates its first dated page, and the newest year's page grows as the
forward horizon moves, so on the day the horizon crosses a New Year a new year
index appears holding one date.

**Why the site needed one.** The 351 dated pages were reachable only one day at
a time: prev/next, the week rail, the homepage calendar widget, the sitemap.
Nothing let a reader — or a crawler following links rather than the sitemap —
see a year of the archive at once.

**Not to be confused with `/dates/`**, which indexes the 366 *year-less* pages.
These index one year's *dated* pages. Different question, different set of URLs,
no overlap in what they link to.

**Both ends of the archive are partial**, because it opens at
`DAY_ARCHIVE_START` and ends at the derived horizon below. So each page states
the range it covers in a sentence rather than rendering twelve month headings
with nine of them empty, and it names the count of dates inside that range that
have no page at all (a date with nothing on the calendar gets none — 18 of them
in 2027 as of 2026-10-12). Someone who came looking for March 2026 has to be
told the record does not reach back that far, not handed an empty March.

**Reachability**, which is what E3's acceptance criteria care about: every
dated page links to its own year index from the note block above the share
row (`YEAR_LINK` in `render_day_page()`, derived from the date alone, so past
pages still regenerate byte-identically), and `/dates/` links to all of them.
No new nav item: the tab row is already tight at 760px, and the Calendar tab
reaches `/dates/`, which reaches these.

**No CSS of its own.** The page reuses the hub's markup exactly — the `.plain`
wrapper, the two-column `.cat-list`, the `.list-side` rail.

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

## Born on this day (`build_people.py` -> `people.json`)

Every perennial page (`/october-10/`) and dated page (`/day/2026-10-10/`) carries
a "Born on <date>" block with two separate sub-blocks:

- **Historic figures** - deceased people, ranked by Wikipedia language-edition count
  (sitelinks). That ranking is stable, so the list rarely changes.
- **Celebrities & public figures** - living people, ranked by a blend:
  `0.5*z(log sitelinks) + 0.5*z(log median daily pageviews, last 60 days)`, z-scores
  taken across all 366 dates. Sitelinks alone surface old politicians; pageviews
  alone surface whoever was in the news last week; the blend gives recognisable names.

The perennial page shows up to 10 per list (`PEOPLE_PERENNIAL_LIMIT`), the dated
page 4 (`PEOPLE_DAY_LIMIT`) plus a link to the perennial page. 12 are kept per list
in the data.

**Pipeline** (separate from the Notion pipeline; people never go through Notion):

```
Wikipedia "on this day" births ----+
Wikidata (sitelinks, birth/death) -+--> scripts/build_people.py --> scripts/people.json --> generate.py
MediaWiki pageviews (living) ------+          ^
                                    scripts/people_overrides.json (hand-kept)
```

`people.json` is committed, so a normal `generate.py` run needs no network. The
feature is simply off if the file is missing, and `generate.py` warns (and, in
Actions, annotates) when the file is older than 45 days (`PEOPLE_STALE_DAYS`).

**Refresh (about monthly, by hand - workflow files are protected, so it is not
scheduled):**

```
python3 scripts/build_people.py            # full build, resumable; cache in scripts/.people_cache/ (git-ignored)
python3 scripts/build_people.py --assemble-only   # after editing people_overrides.json only
python3 scripts/build_people.py --dates 10-10     # one date; --refresh re-fetches it
python3 scripts/build_people.py --fix-views       # re-fetch pageviews only, for dates flagged views_ok=false
```

A full build is ~366 dates and takes a few minutes on an ordinary connection.
Shared cloud IPs get rate-limited by Wikimedia; the script honours `Retry-After`,
and `--budget SECONDS` stops cleanly so a long build can be run in slices. Writes
are atomic per date, so an interrupted run resumes where it stopped.

**Rules the build applies** (all in `build_people.py`, constants at the top):

- A person is kept only if Wikipedia and Wikidata agree on the month-day *and* the
  Wikidata date has day precision. Julian-calendar dates after 1582 are dropped as
  ambiguous; pre-1583 dates tolerate the Julian-to-Gregorian shift. Conflicts are
  logged in `.people_cache/report.json`.
- Minimum notability: 25 sitelinks (historic), 20 sitelinks and 150 median daily
  views (living).
- Anyone with a recorded criminal conviction on Wikidata (P1399) is dropped
  (`EXCLUDE_CONVICTED`). This is blunt: it also drops fraud and tax convictions.
- Occupation deny-list: serial killers (`DENY_OCCUPATIONS`, label-checked at run time).
- `people_overrides.json` -> `exclude` removes a person by Wikipedia title or QID
  (currently 11 people: Nazi leadership, Stalin, Mussolini, jihadist leaders, an
  ICTY indictee); `include` adds one the build would not.
- A person who lands on more than one date (e.g. a disputed birth date) is dropped
  from all of them rather than guessed.
- Descriptors come from Wikipedia's own one-line summary, trimmed to ~70 characters;
  for living people only the lead clause is kept, because office-holder text goes
  stale ("current president of ...").

**Deliberately not done:** no `Event`/`Person` JSON-LD (a birthday is not an event
people attend, and it would put 8,800 entities into structured data); nothing
written to Notion; the homepage does not show people; people never appear in the
sitemap or on `/holiday/` pages. Removing the `<!--TC:PEOPLE_BLOCK-->` marker or
running with `--people /nonexistent` produces output byte-identical to before the
feature.

**Attribution:** each block ends with "Birth dates from Wikidata; names link to
Wikipedia." Wikidata is CC0. Descriptor text is paraphrased from Wikipedia
(CC BY-SA); it is short and every name links back to the article.

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

## Observance type (E4)

Every row can carry a `Type` — a Notion select with seven options — and the
day lists sort and style by it. The point is that a flat list gives
Thanksgiving and National Pumpkin Day the same weight, which tells the reader
the site does not know which one matters.

| Notion property | `holidays.json` key | Holds |
|---|---|---|
| `Type` (select) | `type` | One of the seven below, or absent |

**The seven, in priority order** — this is `TYPE_ORDER` in `generate.py` and
the order the lists sort in:

`Federal` · `State` · `Religious` · `Cultural` · `Observance` ·
`Season & Clock` · `Fun`

`Federal` means the eleven holidays in **5 U.S.C. § 6103** and nothing else.
It is a statutory list, so it is the one tier with no judgment in it.

### How it sorts

`obs_sort_key()` is `(type rank, Order, name)`. **`Order` is still the
tiebreaker inside a type**, so the hand-curation already in Notion decides
between two Fun days; the taxonomy only overrules it between two rows of
different kinds. One sort function feeds the dated pages, the perennial
pages, the home page and the month data files, so the four can never disagree.

A row with **no** `Type` sorts after every typed row, and an unknown `Type`
(an option added in Notion that `TYPE_ORDER` does not list) sorts just above
untyped and renders as untyped — the run prints a `WARNING` and the report
carries `unknown_types`, rather than inventing a tier.

### Why an untyped row renders byte-identically

The same rule as E1, for the same reason. `export_from_notion.py` leaves the
`type` key **out** of the entry when the select is empty, and `obs_row()`
emits no `data-t`, no `t-` class and no chip for such a row. ~2,450 rows get
typed over several runs, and this is what stops each of those runs from
producing a whole-site diff: a date with nothing typed on it regenerates
exactly as before.

The month data files follow the same principle. An entry is
`[name, slug, category, yearly]` as it always was, with a **fifth element, the
type, appended only on rows that have one**. A four-element entry is therefore
the bytes it was before E4, and old cached copies on either side keep working:
the home page's script reads `it[4]` as `undefined` and renders an untyped row.

### Styling

The chip after the name is `.tg` plus `.tg-<slug>` in `public/styles/site.css`,
filled like the category pills (colour as fill, never as text — the whole
palette fails contrast as text). The chip **replaces** the `Lead` label on row
one: the type says more than "Lead" does, and one chip per row keeps the table
quiet.

Which tiers read as "major" is **one CSS rule**, deliberately not a Python
constant:

```css
.obs tr.t-federal td.nm a,.obs tr.t-state td.nm a,.obs tr.t-religious td.nm a{font-size:17px}
```

Move the line by editing that selector. Each type also needs a `.tg-<slug>`
rule; adding a `Type` option in Notion without one is what the `WARNING`
above is for.

`obs_row()` in `generate.py` and `obsRow()` in `templates/index.html` must
produce identical markup — the home page re-renders its table in the browser
when a visitor picks another date. They were changed together; change them
together.

## Calendar export (E5)

Three kinds of iCalendar file, all written by `generate()` on the same run that
writes the pages, all static, none of them in `sitemap.xml` (a sitemap lists
indexable pages; these are downloads).

| URL | Holds |
|---|---|
| `/calendar.ics` | Every observance on the site |
| `/category/<slug>/calendar.ics` | One category, one feed each (14 today) |
| `/holiday/<slug>/event.ics` | One observance (~2,450 files) |

Each is offered two ways on the pages that link it: the `https` URL downloads
the file, and the same path under `webcal://` subscribes to it. Observance
pages carry the line above the back-link, category pages under the intro, and
`/about/` has a section. `public/llms.txt` names all three.

### The recurrence model, and why it is not symmetrical

**Fixed-date (`Annual`) rows: one VEVENT with `RRULE:FREQ=YEARLY`.** That is
exactly what the page already claims ("Every year on March 14"), it recurs
forever, and it costs one event. `DTSTART` is the row's *next* occurrence — the
same date the page shows — so a feed never carries a date that has already
passed. A February 29 row gets a leap-year `DTSTART`, and RFC 5545's yearly
rule then only produces leap years, which is correct and needs no special case.

**Rule-dated (`Floating`) rows: one VEVENT per date, enumerated.** They are
*not* translated into RRULEs. `BYDAY` could express "third Sunday in June", but
nothing in RFC 5545 expresses an Easter offset, an almanac lookup table, "the
day after Thanksgiving" or "the next Friday the 13th" — so an RRULE translation
would cover some rules and not others, and would be a second implementation of
the recurrence engine, free to drift out of agreement with the site. Instead
the dates come straight out of `wide_index`, the same index pass the perennial
date pages are built from: **a date in a feed is a date the site shows, by
construction.** The window is therefore `PERENNIAL_YEARS` wide (ten years) and
rolls forward on every daily regeneration, so a subscriber is never near its
end.

A row whose `lookup_table` has run out of hand-confirmed years simply
contributes fewer events (today: Belmont, Preakness,
teach-your-children-to-save and Super Bowl Sunday, which is why those four
appear in `perennial_index_skipped`). A short feed is honest; an extrapolated
date is not. See "FLOATING_RULES — which ones expire".

### Why there is no VTIMEZONE

All-day events are `DATE`-valued, so they carry no time and no timezone, and
the file needs no `VTIMEZONE` block. This is the correct reading of the item in
the plan, not a shortcut: attaching a timezone to these would shift every
holiday by a day for any subscriber far enough east or west of whichever zone
was picked. Christmas is December 25 wherever you are. `DTEND` is the following
day, because `DATE` ends are exclusive.

### Stability — UIDs and DTSTAMP

`UID` is `<slug>@todaycelebrates.com` for a fixed-date row (one event, one
identity, forever) and `<slug>-YYYYMMDD@todaycelebrates.com` for an enumerated
occurrence, so if a date is corrected or a lookup table gains a year, exactly
that occurrence is replaced in a subscriber's calendar and nothing else moves.

`ICS_DTSTAMP` is a **fixed build stamp**, not the time of the run, for the same
reason the sitemap carries each URL's `lastmod` forward: ~2,470 files whose only
daily change was a timestamp would churn the repo and the CDN every night and
tell every subscriber everything had been revised when nothing had. Bump
`ICS_DTSTAMP` (and `ICS_SEQUENCE` with it) when the output's shape changes in a
way clients should notice. With it fixed, a regeneration that changes no dates
rewrites no feed files at all — verified by running the generator twice.

The feeds are compared and written as **bytes** (`write_bytes_if_changed`),
not text. Read back in text mode, Python translates their CRLFs to LF, every
comparison reports a change, and all ~2,470 files get rewritten every run.

### Line folding and escaping

`ics_fold()` folds to RFC 5545's **75 octets** — the limit is octets, not
characters, and the fold must never land inside a multi-byte UTF-8 sequence, so
it measures bytes and breaks only between characters. Continuation lines begin
with one space, which itself counts toward the 75.

`ics_text()` escapes backslash, semicolon, comma and newline, and nothing else.
Colons and quotes are legal in a TEXT value; over-escaping them shows up as
literal backslashes in the event title, which is how you can spot a hand-rolled
feed.

### Content types

`public/_headers` states `Content-Type: text/calendar; charset=utf-8` for all
three patterns rather than leaving it to be inferred. A feed served as
`text/plain` opens in a text editor instead of a calendar app and the subscribe
flow fails with no error.

### Size

On the 2026-10-14 dataset: `/calendar.ics` is 3,265 events, 1.9 MB raw and
~164 KB gzipped (the edge compresses `text/*`); the largest category feed
(food, 530 rows) is 352 KB; an observance file is ~1 KB. Nearly all of the
bulk is the per-event `DESCRIPTION`. If the all-observances feed ever needs to
be smaller, dropping `DESCRIPTION` from that one feed takes roughly 60% off it
and leaves the per-observance and per-category feeds untouched.

### The in-browser button is still there

`public/js/site.js`'s `addToCalendar()` still builds a one-event file in the
browser for the "Add to calendar" button in the `.tool` row, independently of
these files. It is now redundant with `/holiday/<slug>/event.ics`, which works
without JavaScript and can be linked and subscribed to. Collapsing the two is
a design call, not a bug — see `docs/REVIEW.md` for 2026-10-14.

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
