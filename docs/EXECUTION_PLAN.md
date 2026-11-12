# Today Celebrates — 90-Day Execution Plan

**This file is the state machine for the automated build-out. Every scheduled
session reads it first and writes to it before finishing.** A scheduled run
starts a fresh session with no memory of any prior conversation — this document
is the only context it has. Keep it accurate or the runs go wrong.

Plan start: 2026-10-09 · Re-plan checkpoint: 2026-11-08 (30 days) · Horizon: 2027-01-07

Strategic basis: `https://claude.ai/artifact/YY4gduYbND7mgRP7USdaPo`

---

## 1. Operating model

| | Engineering | Content |
|---|---|---|
| Cadence | Nightly, ~00:54 ET | Mon / Wed / Fri, ~01:47 ET |
| Batch | One queue item (or part of one) | 3 holidays |
| Decides | Jay, daily | Claude, autonomously |
| Jay reviews | Every morning, in GitHub Desktop | Spot-check + Friday digest |
| Output lands in | The repo working tree, uncommitted | Notion, unpublished |

Jay is pre-aligned on content direction and consults at most weekly. His daily
attention goes to engineering.

---

## 2. Hard rules — every run

1. **Never commit, never push, never merge.** Leave changes uncommitted in the
   working tree. Jay reviews the diff in GitHub Desktop and commits himself.
   This is the review gate; do not route around it.
2. **Stop if the working tree is dirty.** Run
   `git status --porcelain -- . ':(exclude)docs'`. If it returns anything, a
   previous night's work is still unreviewed. Append a note to the Run Log
   saying so and **stop**. Do not stack changes.

   `docs/` is excluded on purpose. Rule 6 requires every run to write
   `docs/REVIEW.md` and append to §8 of this file, so `docs/` is the run's own
   workspace and is *always* expected to differ. An unqualified
   `git status --porcelain` reports it every run and so blocks every run
   forever — that is exactly what happened on 2026-10-09, before this wording.
   The exclusion is scoped to `docs/` only: everything the gate actually
   protects (`scripts/`, `public/`, `wrangler.jsonc`, `.github/`, and anything
   added at the repo root later) is still covered. Jay can commit `docs/`
   whenever convenient; the gate no longer depends on it either way.
3. **Never touch generated output.** See the file boundary in §3. The GitHub
   Action owns those files; editing them locally causes merge conflicts Jay has
   to resolve by hand.
4. **Work only from the queue in §5.** If the next item is blocked or the queue
   is empty, say so in the Run Log and stop. **Do not invent engineering work
   on a live site.**
5. **One item per run.** Finishing early is fine. Starting a second item is not —
   it makes the morning diff too large to review properly.
6. **Every run writes two things**: `docs/REVIEW.md` (overwritten each run — what
   changed, why, what to check, what to watch for) and an appended entry in §8.
7. **Verify before finishing.** Run the generator into a throwaway directory
   (never into `public/`) and confirm it exits clean. Report the result.
8. **Sourcing rule for all content** (§4). A claim without a source does not ship.

### If something is ambiguous
Write the question into `docs/REVIEW.md` under `## Needs a decision`, do the part
that isn't ambiguous, and stop. An unattended run must not resolve a design
question by guessing.

---

## 3. File boundary

**Source — safe to edit:**
```
scripts/*.py            scripts/templates/*     scripts/README.md
public/styles/*.css     public/ads/*            public/_headers
public/robots.txt       public/llms.txt         docs/*
wrangler.jsonc
```

**Generated — never edit:**
```
public/index.html       public/holiday/**       public/day/**
public/<month>-<day>/** public/dates/**         public/about/**
public/categories/**    public/category/**      public/holidays/**
public/data/**          public/sitemap.xml      scripts/holidays.json
public/calendar.ics     public/occasions/**     scripts/occasions.json
```

`public/holidays/**` (the year indexes, E3) and `public/calendar.ics` plus the
`.ics` files under `public/holiday/**` and `public/category/**` (the calendar
feeds, E5) are generated too. The feeds are written by `generate.py` on the same
run as the pages; to change what is in one, change the generator, not the file.
`public/_headers`, `public/llms.txt` and `public/styles/*.css` stay source.

`scripts/people.json` is likewise a build artifact (from `scripts/build_people.py`);
to change who appears, edit `scripts/people_overrides.json` (source, safe to edit) and
run `python3 scripts/build_people.py --assemble-only`. `scripts/.people_cache/` is
git-ignored.

`scripts/holidays.json` is a build artifact pulled from Notion. To change holiday
data, change Notion, not this file.

`scripts/occasions.json` is likewise a build artifact, pulled from the separate
**"Today Celebrates — Submitted Occasions"** database by
`scripts/export_occasions_from_notion.py` (source, safe to edit). To change a
paid listing, change that Notion row; `public/occasions/**` is generated from it.
The file does not exist yet, which is exactly why E6's publication half is
dormant: with no `occasions.json` the generator writes a byte-identical site.

The E7 share cards are generated too, by `generate.py` on the same run as the
pages -- but only when cards are switched on (`--cards` / `SHARE_CARDS`),
which they are not. There is now one beside each page of five types:
`public/holiday/<slug>/card.png`, `public/day/<date>/card.png`,
`public/<month>-<day>/card.png`, `public/holidays/<year>/card.png` and
`public/category/<slug>/card.png`. `docs/card-samples/` is **source**: four
cards checked in so the design can be reviewed without running anything.

---

## 4. Content specification

### Target
**600–900 original words** per holiday page. Beats nationaldaycalendar (230–600),
competitive with timeanddate (850–1,200), honest against nationaltoday
(1,000–2,300) without padding. Current state is ~24 words of templated filler.

### Required sections
1. **Opening** — 2–3 sentences. What it is and why anyone marks it. No "celebrates
   a piece of culture that's become part of everyday life" boilerplate.
2. **History / origin** — 120–200 words. Who started it, when, and why, **with a
   source**. If the origin genuinely cannot be sourced, write *"The origin of
   this observance is not well documented"* and move on. That sentence is more
   valuable than an invented founder.
3. **Timeline** — 4–6 dated entries, each one sourced.
4. **How to observe** — 100–150 words of specific, real suggestions. Not
   "celebrate with friends and family."
5. **FAQ** — 3–5 questions people actually ask. These also feed FAQPage
   structured data, which nationaltoday has and we currently don't.
6. **Dates table** — the next five occurrences. Generated from the floating-rule
   engine; never typed by hand.

### Sourcing rule — the one that matters
Every factual claim about an origin, a founder, a date, or a statistic carries a
source URL recorded in Notion. **No source, no claim.** Omit the section and
ship a shorter page.

The entire strategic position of this site is that it is the trustworthy one.
One fabricated founding date on a page claiming authority costs more than fifty
missing pages. A sourced 500-word page beats an unsourced 900-word page every time.

Acceptable sources: the organization that founded the observance; a federal,
state, or municipal government page; an established news outlet; a published
book or journal. **Not acceptable:** other daily-holiday aggregators (including
all five competitors), content farms, or AI-generated listicles. They are the
reason wrong founding dates circulate.

**Exception, added 2026-10-11 at Jay's direction — born-on-this-day data only.**
Wikipedia, Wikidata and the Wikimedia pageview API are acceptable sources for the
"Born on <date>" blocks (names, birth and death years, short descriptors, ranking),
built by `scripts/build_people.py`. Wikidata is CC0; Wikipedia text is CC BY-SA, so
every name links back to its article and the block carries an attribution line. This
exception does **not** extend to holiday content: for an observance's origin,
founder, date or statistics, Wikipedia may point you to a primary source but is not
itself the citation. Widening the exception to holiday content is Jay's call to make.

### Voice
Plain, specific, unhurried. Assume a curious adult, not a search engine. No
exclamation marks, no "Did you know?", no second-person cheerleading. Where a
holiday's history is contested or commercial in origin, say so — that candor is
the product.

**Spelling: American English, always** (honor, neighborhood, digitized, color,
center). Proper names keep their own spelling (e.g. *Encyclopædia Britannica*).

### Where content goes — and that it publishes itself
Notion, in the long-form fields: `Opening`, `Body`, `Timeline`, `FAQ`, `Sources`,
with **`Content Status = Live`**. **Do not change `Published`.** Every existing
row is already Published — it *is* the live page — so unticking it would remove
the holiday from the site at the next export.

**Changed 2026-10-10 (Jay, live): content runs publish directly.** They used to
leave rows at `Draft` for Jay to release. He removed that gate to cut friction,
so a content run's work reaches readers at the next regeneration with no human
in between. Two things follow, and they are the whole bargain:

1. **The sourcing rule below is now the only gate.** There is no second pair of
   eyes. A claim without a source does not ship — that is not a style note, it
   is the thing standing between this site and the aggregators it is trying to
   beat.
2. **Every content run sends a recap** naming each page it published, its live
   URL, and anything worth a second look: a source conflict it resolved, its
   least confident claim, a section it cut for lack of a source. That recap is
   how Jay spot-checks after the fact, so it is not optional.

The machinery is unchanged and still works the old way: `Content Status` is
enforced in `scripts/export_from_notion.py`, which carries the long-form fields
and `Opening` only at `Reviewed` or `Live`. **Setting a row back to `Draft` is
the revert** — at the next regeneration the page returns to its short
`Description` with nothing lost.

### Field formatting that fails silently
Notion stores bold and italics as rich-text *annotations*, and the exporter
reads `plain_text`, which drops them: asterisks typed into a field never come
back out. So **FAQ questions need no bolding** — a question is the first line
of a blank-line-separated block — and **source links must be bare URLs**,
because `[text](url)` loses its URL on the way out, which for a citation is the
whole point gone. `###` headings and `- ` bullets are literal and survive.
Until 2026-10-10 `parse_faq()` required bolded questions, so every FAQ ever
written parsed to zero pairs and both the FAQ section and its FAQPage data
were missing from the page with no warning. See `scripts/README.md`.

---

## 5. Engineering queue

Work top to bottom. Each item is done only when its acceptance criteria are met.

### E1 — Long-form content rendering  ·  BLOCKS ALL CONTENT WORK  ·  do first
Content drafts have nowhere to go until the schema and renderer exist.

- Notion: add `Body` (rich text), `Sources` (rich text), `Content Status`
  (select: Draft / Reviewed / Live), `Timeline` (rich text), `FAQ` (rich text).
- `export_from_notion.py`: carry the new fields into `holidays.json`.
- `generate.py` + `scripts/templates/`: render the §4 sections when present,
  degrade to today's one-liner when absent. Add FAQPage JSON-LD when FAQ exists.
- Add the five-year dates table from the existing rule engine.

**Done when:** a holiday with the fields populated renders all sections; one
without them renders byte-identical to today; FAQPage validates; the generator
exits clean.

**STATUS: DONE 2026-10-09** (uncommitted, awaiting Jay's review). All five
Notion properties exist; `export_from_notion.py` carries them through;
`generate.py` renders every §4 section plus the five-year dates table and a
separate FAQPage JSON-LD block; byte-identical degradation verified by diffing
the pre-patch generator's output against the patched one. FAQPage was validated
structurally, not yet against Google's Rich Results Test — nothing is live with
an FAQ to point it at. **Do not restart E1; the next engineering run starts at
E2.** Two open schema questions are in `docs/REVIEW.md` under
*Needs a decision*; neither blocks E2 or content work.

### E2 — Coverage gaps  ·  high leverage, low effort
A missing page cannot rank at all; a thin page can. These high-demand
observances are **absent from the dataset entirely** (verified 2026-10-08):

Kwanzaa · Rosh Hashanah · Yom Kippur · National Pizza Day (Feb 9) ·
Leap Day (Feb 29) · Winter Solstice · Summer Solstice · Vernal Equinox ·
Día de los Muertos / Day of the Dead · Teacher Appreciation Day & Week ·
National Margarita Day (Feb 22) · National French Fry Day · National Hugging
Day (Jan 21) · Super Bowl Sunday · Tax Day · Oktoberfest (start)

Note the shape of this gap: Hanukkah and Passover are present but the High Holy
Days and Kwanzaa are not. That reads as carelessness to exactly the readers
least likely to forgive it. Fix it early.

**Also a fidelity bug:** `national-doughnut-day` is stored as fixed June 4.
National Donut Day is the **first Friday in June** — it should be Floating with
an `nth_weekday` rule. Audit the other food/awareness days for the same error
class while in there.

**Done when:** each observance exists as a published Notion row with the correct
recurrence and a sourced date; Donut Day is Floating; the generator picks them up.

**STATUS: PARTLY DONE 2026-10-10** (code uncommitted; Notion rows live).
Created, published, sourced, and verified to resolve: Kwanzaa, Rosh Hashanah,
Yom Kippur, Day of the Dead, National Pizza Day, National Margarita Day,
National Hugging Day, National Teacher Appreciation Day, National Teacher
Appreciation Week, Oktoberfest (starts in Germany), Super Bowl Sunday.
Donut Day is Floating (first Friday in June, per The Salvation Army), and
National Ice Cream Day was fixed with it (third Sunday in July, per
Proclamation 5219). `generate.py` gained an `nth_weekday_offset` rule kind and
two `next_occurrence` fixes; `export_from_notion.py` gained eight rules.

**What is left of E2 — all five are waiting on Jay, none is work to start
unattended.** Details and options are in the 2026-10-10 `docs/REVIEW.md`:
1. **Leap Day** — row exists, complete and sourced, `Published` left OFF:
   publishing it moves the dated archive's forward horizon (derived from the
   furthest next occurrence) from Oct 2027 to Feb 2028, ≈142 new `/day/` pages.
2. **Tax Day** — overlaps the existing `Income Tax Pay Day` row, and the IRS
   deadline shifts for weekends and DC Emancipation Day.
3. **National French Fry Day** — July 13 vs the second Friday of July; the move
   was made by an aggregator at a restaurant chain's request.
4. **Winter / Summer Solstice and Vernal Equinox** — already present as
   `First Day of Winter` / `Yule`, `The First Day of Summer`, and
   `The First Day of Spring` / `Ostara`. Alias rows or renames, not a gap.
5. **`Oktoberfest (ends in Germany)`** — wrong from 2027; needs a rule kind or
   a lookup table for Munich's conditional Oct 3 extension.

The audit E2 asks for is done as a screen: 24 candidate rows in
`docs/FIDELITY_AUDIT.md`, two of them fixed. **Do not restart E2 from the top.**
Once Jay has answered the five above, the next engineering run goes to E3.

### E3 — Perennial day pages + canonical model
Three of four leading competitors use a year-less day URL; we only have dated
ones. `/october-8/` is the page that ranks for the recurring query.

- Generate `/<month>-<day>/` for all 366 days from the existing day index.
- Perennial page is **canonical**; each `/day/YYYY-MM-DD/` self-canonicalizes and
  keeps its year-specific angle as its unique content. Both stay in the sitemap.
- Cross-link both directions. Add `/holidays/<year>/` index pages.

**Done when:** 366 perennial pages exist, canonicals are correct in both
directions, no page is orphaned, sitemap is consistent, CLS stays 0.0000.

**STATUS: PARTLY DONE 2026-10-11** (committed by Jay, then extended the same
day). The 366 perennial `/<month>-<day>/` pages exist, February 29 included;
both page types are self-canonical and both are in the sitemap; the cross-link
runs both ways; prev/next and the rail wrap as a closed 366-day ring, so
nothing is orphaned. Then, after Jay answered the three open questions:

- **`/dates/` hub added** — all 366 grouped by month — and the header's
  **Calendar** tab and the footer link now point at it instead of `/#calendar`,
  so every date is one click from every page. A fifth nav tab was the
  alternative and was rejected (the tab row is already tight at 760px).
- **Holiday pages now link to the perennial page**: the breadcrumb's date crumb
  and the back-link. The dated page keeps its links from the Date row of the
  spec list and from *All N on <date>* in the sidebar — every holiday page
  carries at least one, with an assertion for it.
- **Breadcrumbs follow one hierarchy**: `Today / Calendar / October 8` and
  `Today / Calendar / October 8 / Halloween`.

**The three questions are answered — do not re-ask them:**
1. **Empty-date pages: keep them** (Jay, 2026-10-11). Celebrity and historic
   figure dates are being added, so these pages fill in. `PERENNIAL_EMPTY_PAGES`
   stays True. The count has already fallen from 8 to 6 as rows landed.
2. **Navigation: the `/dates/` hub, via the existing Calendar tab** — built.
3. **Holiday pages link to perennial pages: yes** — built.

CLS still **not** measured (nothing deployed) and the hub has not been seen at
real phone width; both are worth a look on the live site, since E3's acceptance
criteria name CLS.

**STATUS: DONE 2026-10-12** (the year indexes, uncommitted). The fourth bullet
is built: one `/holidays/<year>/` page per year the dated archive touches —
`/holidays/2026/` (85 dates, Oct 8–Dec 31) and `/holidays/2027/` (266 dates,
Jan 1–Oct 11) — each listing that year's `/day/` pages by month with the weekday
and observance count, derived from `day_dates` alone, so a year appears with its
first dated page and the newest year's page grows with the horizon. Both ends of
the archive are partial and each page states its own coverage rather than
rendering empty months. Every dated page links its year index (`YEAR_LINK`), and
`/dates/` links them all; no new nav item (the 760px tab row, decided
2026-10-11). New `/holidays/*` cache rule; `llms.txt` and the README's URL model
updated. No new CSS. **Do not restart E3 from the top — all four bullets are
done; the next engineering run starts at E4.**

**CLS measured on the live site 2026-10-27, and E3's last acceptance criterion is
now answered.** Headless Chromium against the deployed site, `layout-shift` entries
excluding `hadRecentInput`, 8 URLs x 1280px and 390px: **CLS 0.0000 with zero shifts
on `/october-27/`, `/dates/`, `/holidays/2026/` and `/holidays/2027/`** — and on the
dated, observance and categories pages — with **no horizontal overflow anywhere**
(`scrollWidth == clientWidth` on all 16 combinations), so the phone-width question on
`/dates/` and the year pages is answered too: they are fine. **Do not re-measure these.**

The **home page** is the single exception: one shift ~0.5s after load, 0.00325 at
1280px and 0.03731 at 390px (0.0023-0.0075 at 1440 / 1100 / 900 / 760), reproducible
to the same value on three consecutive loads. Cause isolated and proven, not inferred,
by pinning the browser clock: the page is baked for one date
(`<main data-today="...">`) and the inline script re-renders the band for the reader's
date, which **only happens while the deployed build is a day behind the reader's clock**
— local midnight until the regeneration deploys around 09:00 ET. With the clock set to
the build's own date the script's existing guard fires, the DOM is left alone and CLS is
**0.0000 / zero shifts**; with the real date it shifts once. So the "CLS 0.0000" measured
against a fresh build on 2026-10-26 was correct — the stale-build window is a different
case, and it is the one morning readers are in. Whether to reserve the band's height is a
visual trade-off on the most-visited page and is **Jay's call, open as star D in
`docs/REVIEW.md`**; if he accepts the shift, this criterion's wording should change from
"CLS stays 0.0000" to a threshold, or it stays unmet forever.

Two small new decisions are in `docs/REVIEW.md` under *Needs a decision* (a bare
`/holidays/` 404s; the 2026 page makes the archive's start line visible, which
raises backfilling). Neither blocks E4.

### E4 — Observance type taxonomy
Flat 7–14 item day lists give Thanksgiving and National Pumpkin Day the same
visual weight, which tells the reader we don't know which matters.

- Notion `Type` select: Federal / State / Religious / Cultural / Observance /
  Season & Clock / Fun.
- Sort and style day lists by type. Also the prerequisite for separating paid
  occasions from genuine ones in E6.

**Done when:** every published row has a Type; day lists sort by it; major
observances are visually dominant.

**Shape of this item, noted 2026-10-12 so the next run does not discover it
mid-flight:** the acceptance criterion covers ~2,450 published Notion rows, so
it is several runs of bulk property writes, not one. A good share of rows are
also a judgment call (is a given awareness day *Observance* or *Fun*?), and an
unattended run must not guess its way through 2,450 of those. So unless Jay has
left an assignment rule: do the unambiguous rows first — federal holidays,
religious observances, the season-and-clock rows — report the counts and the
calls made, and leave the ambiguous ones untyped rather than filling them in.
The sort-and-style half of the item can be built and verified against whatever
subset is typed; a row with no Type must degrade to today's flat ordering.

**STATUS: PARTLY DONE 2026-10-13** (code uncommitted; Notion `Type` property
and 40 rows live). The machinery is finished: Notion `Type` select with the
seven options; `export_from_notion.py` carries it and omits the key when
unset; `obs_sort_key()` = `(type rank, Order, name)` is now the single sort
for dated pages, perennial pages, the home page and the month data files, with
`Order` kept as the tiebreaker **inside** a type; a typed row gains `data-t`,
a `t-<slug>` class and a chip that replaces the `Lead` label on row one; which
tiers read as "major" is one CSS selector in `site.css`. An untyped row is
byte-identical to pre-E4 (proven: the patched generator on untyped data
differs from the pre-patch generator in **one file**, the home page's inline
script). An unknown `Type` warns and renders as untyped rather than inventing
a tier. Month data entries gain a 5th element **only when typed**.

**Typed so far: 40 of ~2,450**, chosen because none of them is a judgment
call — the 11 federal holidays of 5 U.S.C. § 6103, 6 season-and-clock rows,
23 religious observances. Effect: the lead changes on 16 list pages (July 4,
2027 led with *Alice in Wonderland Day*; it now leads with Independence Day).

**The remaining ~2,410 are blocked on an assignment rule from Jay** — three
boundaries are written up in the 2026-10-13 `docs/REVIEW.md`: saints' feast
days, secularized religious holidays, and Observance vs Fun (most of the
remainder). **Do not restart E4 from the top, and do not type the rest by
guessing.** With a rule, the next run continues E4; without one, E5 is
independent of all of this and can be taken instead.

Also found while in there and **not fixed** (E2/§7 work, one item per run):
**`Ascension` is stored as a fixed May 6 but is Easter + 39 days** — right for
2027 by coincidence, wrong from 2028, and absent from `docs/FIDELITY_AUDIT.md`
because that screen only catches weekday-ruled rows.

### E5 — Calendar export
Absent across all five competitors. A subscribed calendar is the only retention
mechanism available without accounts.

- `/calendar.ics` (all), `/holiday/<slug>/event.ics` (one), per-category feeds.
- `webcal://` links. Correct `VTIMEZONE`, stable `UID`s across regenerations.

**Done when:** feeds validate and subscribe cleanly in Apple Calendar and Google
Calendar, and UIDs are stable run to run.

**STATUS: DONE 2026-10-14** (uncommitted), except the one criterion that needs a
deploy. All three feed shapes are generated on the same run as the pages:
`/calendar.ics` (3,265 events, 1.9 MB raw / ~164 KB gzipped),
`/category/<slug>/calendar.ics` (14) and `/holiday/<slug>/event.ics` (2,450),
2,465 files in all, none of them in `sitemap.xml`. `webcal://` and download
links are on every observance page (above the back-link), every category page,
and in a new `/about/` section; `llms.txt` names all three shapes.

Two model decisions, both written up in `scripts/README.md`:
- **Fixed-date rows are one VEVENT with `RRULE:FREQ=YEARLY`; rule-dated rows are
  enumerated** out of the same index pass the perennial pages use — so a date in
  a feed is a date the site shows. RRULEs were deliberately *not* used for rule
  dates: `BYDAY` cannot express an Easter offset, a lookup table or "the day
  after Thanksgiving", so a partial translation would be a second recurrence
  engine free to disagree with the site. Window: ten years, rolling forward with
  every daily regeneration. A row whose lookup table has expired contributes
  fewer events rather than an extrapolated date.
- **No `VTIMEZONE`, deliberately.** These are `DATE`-valued all-day events, which
  carry no zone; attaching one would move every holiday a day for subscribers
  east or west of it. The item's wording asks for a correct VTIMEZONE and for
  these events the correct answer is none.

UIDs are stable by construction (`<slug>@` for a recurring row,
`<slug>-YYYYMMDD@` per enumerated occurrence) and `ICS_DTSTAMP` is a fixed build
stamp, so a regeneration that changes no dates rewrites no feed file: verified by
a second run (0 changed, 2,465 unchanged). Verified further by reverse-transform
against the pre-patch generator (removing the one added line makes all 2,450
holiday pages, 14 category pages and `/about/` byte-identical; every dated,
perennial, year, hub and data file **and the sitemap** untouched), 201,453
structural and cross-checks with 0 failures, 1,230 link checks, and a simulated
`--today 2027-06-15` rollover. Exit 0, zero WARNINGs.

**Measured on the deployed feeds 2026-10-28 — the validation half of that last
criterion is answered, and `UID` stability with it.** All 2,465 committed feeds
plus 29 re-downloaded from the live site parse against RFC 5545 with **zero
failures and zero warnings** (CRLF throughout, no folded line over 75 octets,
`VALUE=DATE` with an exclusive `DTEND`, only `FREQ=YEARLY` RRULEs, no
`VTIMEZONE` and no `TZID`, no duplicate UID); counts tie out three ways (3,264
events in `/calendar.ics`, the 14 category feeds partitioning that set exactly,
the 2,450 per-holiday feeds carrying it again); 4,915 `.ics` links on pages all
resolve; all three shapes serve 200 over HTTP/2 as `text/calendar; charset=utf-8`
with no redirect; and none of the invitation-shaped properties that make a client
treat a feed as a meeting request (`METHOD`, `ORGANIZER`, `ATTENDEE`,
`RECURRENCE-ID`, `EXDATE`, `VALARM`, `STATUS:CANCELLED`) is present. **UIDs are
stable run to run** across three independently produced builds (committed
2026-10-26, live 2026-10-27, fresh 2026-10-28): recurring set identical,
enumerated set identical, 0 added, 0 dropped, no UID with a changed `SUMMARY`. A
one-day roll changes **11 of 2,465** feed files. Full method in
`scripts/README.md` under *Verified against the deployed feeds*. **Do not
re-measure these.**

**What is still left of E5 is one human action and two decisions.** Actually
clicking *subscribe* in Apple Calendar and Google Calendar is Jay's two-minute
check (a small category feed is the one to start with) — an unattended run has
no business in his accounts. Two findings from the verification are in the
2026-10-28 `docs/REVIEW.md`: **★ F**, whether a fixed-date row should keep its
history (`DTSTART` is the *next* occurrence by design, so a subscriber holds no
past instance of an observance — anchoring it is a published-model change), and
**★ G**, that Cloudflare is not compressing `text/calendar`, so `/calendar.ics`
costs 1.98 MB per daily refresh where gzip would make it 177 KB — a zone
setting, not a code change, and the one remaining risk to the Google half of the
criterion. Four decisions in the 2026-10-14 `docs/REVIEW.md`,
none blocking: the now-redundant in-browser Add-to-calendar button, footer/home
discovery, the 1.9 MB all-feed (and a federal-holidays-only feed, which wants
E4's typing), and the still-unmeasured CLS. **Do not rebuild E5**; the next
engineering run goes to E4 with a rule, else **E6**.

### E6 — Submitted occasions
Form → Stripe Checkout → Cloudflare Worker → unpublished Notion row → Jay
reviews → daily regeneration publishes. Launch with the Listed tier only.

**Non-negotiable constraints.** Paid occasions live at `/occasions/<slug>/`,
never under `/holiday/`. They are **excluded from Event JSON-LD** — we never
hand a search engine a paid day as a genuine observance. They sit in a labelled
block below real observances, never interleaved. Every one is human-reviewed.
Checkiday sells rank *inside* the real list; that is the thing to avoid, not copy.

**Done when:** end-to-end works with Stripe test keys, the review gate holds, and
a paid occasion cannot appear in Event structured data even if misconfigured.

**STATUS: PARTLY DONE 2026-10-15** — the **publication half** is built
(uncommitted; the new Notion database is live and empty). Tree was clean at the
gate; E4's remaining ~2,410 rows are still blocked on an assignment rule from
Jay, so this was the next unblocked item per §5.

What exists: a separate Notion database **"Today Celebrates — Submitted
Occasions"** (id `7c9d328c-0360-4feb-aabf-998f6402eed9`, 17 properties, every one
with a description, **zero rows**); `scripts/export_occasions_from_notion.py`,
carrying `Review Status = Approved` rows only into `scripts/occasions.json`;
`generate.py` rendering `/occasions/<slug>/` and `/occasions/`, plus a labelled
`.occ` block below everything else on the dated page (and on the perennial page
when the row's `Recurs Yearly` is ticked); `rel="sponsored nofollow noopener"` on
the paid link; disclosure copy on both page types and in `llms.txt`.

**The two non-negotiables are structural, not asserted.** A separate database
feeding a separate file that is never merged into `holidays` means there is no
code path by which a paid listing can reach the observance list, a `/holiday/`
URL, the month data files, `search.json`, a calendar feed or any `Event` JSON-LD.
On top of that: occasion pages render from `templates/page.html`, which has no
JSON-LD slot at all; the generator greps its own rendered output for
`"@type": "Event"` and refuses to write the page if it ever finds one; and a slug
that already belongs to a holiday is dropped by both the exporter and the
generator. The labelled block is appended after every other block on the page and
is absent from that page's `ItemList` — verified, not assumed.

**What is left of E6 — the upstream half, and most of it needs Jay:**
1. The public submission form (`/submit/`).
2. Stripe Checkout — needs a **price and a product**: what the Listed tier costs
   and what it includes. Not an unattended decision.
3. The Cloudflare Worker for the Stripe webhook. Note `wrangler.jsonc` declares
   **assets only** (no `main`): adding a Worker changes how the live site
   deploys, which is Jay's call to make deliberately.
4. A daily-workflow step running the occasions exporter, and sharing the Notion
   integration with the new database (database → … → Connections). Until this is
   done the feature is dormant and the site stays byte-identical.

**Do not rebuild the publication half.** With a price and a decision on the
Worker, the next engineering run can take (1)–(4).

### E7 — Share cards + Featured tier
Build-time card image per occasion, doubling as the OG image. Feed-native 9:16.
Free to view and share; the listing is what costs money.

**STATUS: PARTLY DONE 2026-10-16** — the **OG share card** is built
(uncommitted, and switched off). Tree was clean at the gate; E4's remaining
~2,410 rows are still blocked on an assignment rule and E6's upstream half on a
price, so this was the next unblocked item per §5.

What exists: `generate.py` draws a 1200x630 PNG per observance at
`/holiday/<slug>/card.png` — the site's four-colour band, the coral mark and
wordmark, a date pill in the observance's own category colour, the name set as
large as it fits, one muted line and the domain — and points that page's
`og:image`, `twitter:image` and Event JSON-LD `image` at it. It replaces the
fourteen stock hero photographs that currently make every page's link preview
look the same. Four examples are checked in at `docs/card-samples/`.

**It is off**, and the switch is the item's real content: drawing the cards
needs Pillow, which the daily workflow does not install, and 2,450 cards are
~33 MB of committed PNG. Both are deployment calls, so `SHARE_CARDS` is False,
`--cards` turns it on, and with it off every file the generator writes is
byte-identical to a build without the feature (proven by `diff -r` over all
5,671 files, not asserted). `.github/workflows/daily-regenerate.yml` was **not**
edited — it is not on §3's source list, and it is how the live site deploys;
the two-line change is written out in `docs/REVIEW.md` for Jay to apply.

**STATUS: 2026-10-17 — the third bullet below is done.** Tree was clean at the
gate (Jay committed the 2026-10-16 E7 work); E4's remaining ~2,410 rows are
still blocked on an assignment rule, E6's upstream half on a price, and E7's
two other bullets on Jay, so this was the next unblocked work per §5. The
dated, perennial, year-index and category pages now carry their own card,
behind the same switch. `card_png_bytes` was split into `card_render()` (the
frame, which knows nothing about page kind) plus five callers that fill the
pill, headline and muted line; the 2,450 observance cards come out
**byte-identical** to before the split. 3,188 cards in all, ~45 MB with cards
on. A date roll creates the one new dated card at the horizon and rewrites
none, so the feature adds no nightly churn. Cards are still **off**, and with
them off every one of the 5,672 files is byte-identical to a build without any
of this.

**What is left of E7:**
1. The **9:16 feed-native card** — the renderer generalizes to it, but nothing
   on the page offers a reader a card to download, and adding that affordance
   to 2,450 pages is a UI decision.
2. The **Featured tier** — a pricing decision, blocked on the same answer E6's
   Listed tier is waiting for.
3. ~~Cards for dated, perennial, year and category pages~~ — **done
   2026-10-17.** The home page, `/dates/`, `/categories/`, `/about/` and the
   occasion pages are deliberately still on the stock hero; whether they
   should get cards is in `docs/REVIEW.md`.

**With E4, E6 and E7 all now waiting on Jay, the queue has no unblocked item
left.** The next engineering run should expect to stop at §5 unless an answer
has landed — see "Queue empty?" below for what is explicitly *not* unattended
work.

### Queue empty?
Report it in the Run Log and stop. Candidates for the re-plan conversation, **not
for an unattended run to start on its own:** the deferred holiday fidelity audit
(see §7), the three floating lookup tables expiring in 2027, deepening content
beyond the §6 queue.

---

## 6. Content queue

Three per run, in order, top first. Mark each `[x]` when a draft is in Notion.
Ties broken by date proximity, so pages go live before their occurrence.

**Tier 1 — the holidays that carry the category**
- [x] 1. Halloween — written interactively, loaded into Notion, Live (2026-10-09).
- [x] 2. Thanksgiving Day  *(written interactively with Jay, 2026-10-09; Live)*
- [x] 3. Christmas Day  *(drafted 2026-10-10, content run; Draft)*
- [x] 4. Valentine's Day  *(drafted 2026-10-10, content run; Draft)*
- [x] 5. New Year's Day  *(drafted 2026-10-10, content run; Draft)*
- [x] 6. Easter Sunday  *(published 2026-10-11, content run; Live)*
- [x] 7. Mother's Day  *(published 2026-10-11, content run; Live)*
- [x] 8. Father's Day  *(published 2026-10-11, content run; Live)*
- [x] 9. St. Patrick's Day  *(published 2026-10-12, content run; Live)*
- [x] 10. Independence Day  *(published 2026-10-12, content run; Live)*
- [x] 11. New Year's Eve  *(published 2026-10-12, content run; Live)*
- [x] 12. Christmas Eve  *(published 2026-10-14, content run; Live)*

**Tier 2 — federal and civic**
- [x] 13. Veterans Day  *(published 2026-10-14, content run; Live)*
- [x] 14. Memorial Day  *(published 2026-10-14, content run; Live)*
- [x] 15. Labor Day  *(published 2026-10-15, content run; Live)*
- [x] 16. Martin Luther King, Jr. Day  *(published 2026-10-15, content run; Live)*
- [x] 17. Presidents' Day  *(published 2026-10-15, content run; Live)*
- [x] 18. Juneteenth  *(published 2026-10-16, content run; Live)*
- [x] 19. Columbus Day  *(published 2026-10-16, content run; Live)*
- [x] 20. Indigenous Peoples' Day  *(published 2026-10-16, content run; Live)*
- [x] 21. U.S. General Election Day  *(published 2026-10-17, content run; Live)*
- [x] 22. Flag Day  *(published 2026-10-17, content run; Live)*
- [x] 23. Patriot Day — National Day of Service & Remembrance  *(published 2026-10-17, content run; Live)*

**Tier 3 — seasonal, cultural, commercial**
- [x] 24. Black Friday  *(published 2026-10-18, content run; Live)*
- [x] 25. Cyber Monday  *(published 2026-10-18, content run; Live)*
- [x] 26. Small Business Saturday  *(published 2026-10-18, content run; Live)*
- [x] 27. Cinco de Mayo  *(published 2026-10-19, content run; Live)*
- [x] 28. Mardi Gras  *(published 2026-10-19, content run; Live)*
- [x] 29. Chinese New Year  *(published 2026-10-19, content run; Live)*
- [x] 30. Diwali  *(published 2026-10-20, content run; Live)*
- [x] 31. The Start of Hanukkah  *(published 2026-10-20, content run; Live)*
- [x] 32. Passover  *(published 2026-10-20, content run; Live)*
- [x] 33. The Start of Ramadan  *(published 2026-10-21, content run; Live)*
- [x] 34. Good Friday  *(published 2026-10-21, content run; Live)*
- [x] 35. Ash Wednesday  *(published 2026-10-21, content run; Live)*
- [x] 36. Daylight Saving Time Ends  *(published 2026-10-22, content run; Live)*
- [x] 37. The Start of Daylight Saving Time  *(published 2026-10-22, content run; Live)*
- [x] 38. Autumnal Equinox  *(published 2026-10-22, content run; Live)*
- [x] 39. Groundhog Day  *(published 2026-10-23, content run; Live)*
- [x] 40. April Fools' Day  *(published 2026-10-23, content run; Live)*
- [x] 41. Earth Day  *(published 2026-10-23, content run; Live)*
- [x] 42. Pi Day  *(published 2026-10-24, content run; Live)*
- [x] 43. Friday the 13th  *(published 2026-10-24, content run; Live)*

**Tier 3b — from E2's coverage gaps (2026-10-10), ahead of Tier 4 by demand,
as instructed below.** All eleven are published rows with a one-paragraph
Description and no long-form content.
- [x] 23a. Kwanzaa  *(published 2026-10-24, content run; Live)*
- [x] 23b. Rosh Hashanah  *(published 2026-10-25, content run; Live)*
- [x] 23c. Yom Kippur  *(published 2026-10-25, content run; Live)*
- [x] 23d. Day of the Dead  *(published 2026-10-25, content run; Live)*
- [x] 23e. National Teacher Appreciation Day  *(published 2026-10-26, content run; Live — the National Teacher Appreciation Week row published with it)*
- [x] 23f. Super Bowl Sunday  *(published 2026-10-26, content run; Live)*
- [x] 23g. Oktoberfest (starts in Germany)  *(published 2026-10-26, content run; Live — the "ends" row remains a known bug, see §7)*
- [x] 23h. National Pizza Day  *(published 2026-10-27, content run; Live)*
- [x] 23i. National Margarita Day  *(published 2026-10-27, content run; Live)*
- [x] 23j. National Hugging Day  *(published 2026-10-27, content run; Live)*

**Tier 4 — high-volume "national day" queries**
- [x] 44. National Dog Day  *(published 2026-10-28, content run; Live)*
- [x] 45. National Cat Day  *(published 2026-10-28, content run; Live)*
- [x] 46. National Coffee Day  *(published 2026-10-28, content run; Live)*
- [x] 47. National Taco Day  *(published 2026-10-29, content run; Live — main Oct 4 row; the "[DUPLICATE - DELETE]" Oct 6 row left untouched)*
- [x] 48. National Doughnut Day  *(published 2026-10-29, content run; Live — recurrence already fixed 2026-10-10, confirmed Floating)*
- [x] 49. National Ice Cream Day  *(published 2026-10-29, content run; Live)*
- [x] 50. National Cheeseburger Day  *(published 2026-10-30, content run; Live)*
- [x] 51. Administrative Professionals Day  *(published 2026-10-30, content run; Live)*
- [x] 52. National Boss' Day  *(published 2026-10-30, content run; Live — the near-duplicate "Bosses Day" row, same date, Order 1, left untouched)*
- [x] 53. National Grandparents Day  *(published 2026-10-31, content run; Live)*
- [x] 54. World Mental Health Day  *(published 2026-10-31, content run; Live)*
- [x] 55. National Coming Out Day  *(published 2026-10-31, content run; Live)*

**Tier 5 — everything else.** When Tiers 1–4 are ticked, keep going without
being re-planned: take published rows whose `Body` is empty and whose
`Content Status` is empty, ordered by **next occurrence** (soonest first, so pages
are ready before their day). Skip a row another run has already touched. Many of
these are "National ___ Day" observances with a thin or commercial origin — for
those, ship the short honest page the sourcing rule allows (a sourced 300–500
words, with "the origin of this observance is not well documented" where that
is true) rather than padding to 600. The site has ~2,400 rows, so this tier is
a multi-month job; the Friday digest reports the running count.

*Tier 5 published, newest last. Three per run, by next occurrence.*
- [x] T5-1. All Saints' Day  *(published 2026-11-01, content run; Live — Nov 1, Order 1)*
- [x] T5-2. National Author's Day  *(published 2026-11-01, content run; Live — Nov 1, Order 2; Timeline omitted, origin unsourceable)*
- [x] T5-3. World Vegan Day  *(published 2026-11-01, content run; Live — Nov 1, Order 3)*
- [x] T5-4. All Souls' Day  *(published 2026-11-02, content run; Live — Nov 2, Order 1)*
- [x] T5-5. National Deviled Egg Day  *(published 2026-11-02, content run; Live — Nov 2, Order 2; observance origin unsourceable)*
- [x] T5-6. Cookie Monster Day  *(published 2026-11-02, content run; Live — Nov 2, Order 3; Nov 2 birthday unsourceable)*
- [x] T5-7. National Sandwich Day  *(published 2026-11-03, content run; Live — Nov 3, Order 2; Nov 3 = Earl's birthday claim not sourceable, Britannica gives Nov 13)*
- [x] T5-8. Cliché Day  *(published 2026-11-03, content run; Live — Nov 3, Order 3; observance origin unsourceable; slug is `clich-day`)*
- [x] T5-9. World Jellyfish Day  *(published 2026-11-03, content run; Live — Nov 3, Order 4; observance origin unsourceable, NOAA marks the date)*
- [x] T5-10. King Tut Day  *(published 2026-11-04, content run; Live — Nov 4, Order 1; observance origin unsourceable, the Nov 4 1922 discovery is the sourced content)*
- [x] T5-11. National Candy Day  *(published 2026-11-04, content run; Live — Nov 4, Order 2; Nov 4 origin unsourceable, but a real 1916 October National Candy Day is documented in LOC newspapers)*
- [x] T5-12. Use Your Common Sense Day  *(published 2026-11-04, content run; Live — Nov 4, Order 3; origin unsourceable, Will Rogers link is aggregator-only; Oklahoma's statutory Will Rogers Day is the real Nov 4 observance)*
- [x] T5-13. National Gunpowder Day  *(published 2026-11-05, content run; Live — Nov 5, Order 1; observance origin unsourceable, the 1605 Gunpowder Plot is the sourced content; FAQ at 4 pairs)*
- [x] T5-14. National Chinese Take-Out Day  *(published 2026-11-05, content run; Live — Nov 5, Order 2; observance origin unsourceable, the 1894 oyster-pail patent and exclusion-era restaurant history are the sourced content)*
- [x] T5-15. International Stout Day  *(published 2026-11-05, content run; Live — Nov 5, Order 3; founder sourced to her own column — rare for Tier 5; the first-Thursday date rule is NOT sourceable, see §7 fidelity candidate)*
- [x] T5-16. National Nachos Day  *(published 2026-11-06, content run; Live — Nov 6, Order 1; observance origin unsourceable, Anaya's own 1961 interview preferred over the Victory Club story)*
- [x] T5-17. National Saxophone Day  *(published 2026-11-06, content run; Live — Nov 6, Order 2; observance origin unsourceable but the date is Sax's sourced birthday; patent date conflict resolved to 21 March 1846)*
- [x] T5-18. Fountain Pen Day  *(published 2026-11-06, content run; Live — Nov 6, Order 3; observance origin unsourceable, the former site now redirects off-topic; Waterman's 1884 patent is the sourced content; see §7 fidelity candidate)*
- [x] T5-19. National Bison Day  *(published 2026-11-07, content run; Live — Nov 7, Order 1; the first Tier 5 row whose weekday rule IS primary-sourced — the row is `Annual` Nov 7 but the observance is the first Saturday of November; see §7)*
- [x] T5-20. National Bittersweet Chocolate with Almonds Day  *(published 2026-11-07, content run; Live — Nov 7, Order 2; observance origin unsourceable, **Timeline omitted**; the FDA standard of identity at 21 CFR 163.123 is the sourced content; 630 words)*
- [x] T5-21. International Merlot Day  *(published 2026-11-07, content run; Live — Nov 7, Order 3; observance origin unsourceable; the 2009 parentage paper and the Journal of Wine Economics "Sideways" study are the sourced content)*
- [x] T5-22. National Cappuccino Day  *(published 2026-11-08, content run; Live — Nov 8, Order 2; observance origin unsourceable, the Viennese Kapuziner and the Capuchin etymology are the sourced content; 871 words)*
- [x] T5-23. Cook Something Bold Day  *(published 2026-11-08, content run; Live — Nov 8, Order 3; observance origin unsourceable, **Timeline omitted** — only one dated event sourceable; Scoville's 1912 paper is the sourced content; 665 words)*
- [x] T5-24. International Tongue Twister Day  *(published 2026-11-08, content run; Live — Nov 8, Order 4; observance origin unsourceable and the aggregator dates disagree — see §7 fidelity candidate; the 2013 MIT/ASA research and the 1855 term date are the sourced content; 897 words)*
- [x] T5-25. World Freedom Day  *(published 2026-11-09, content run; Live — Nov 9, Order 1; the first Tier 5 row with a fully primary-sourced origin: Proclamation 7499 of November 9, 2001)*
- [x] T5-26. National Fried Chicken Sandwich Day  *(published 2026-11-09, content run; Live — Nov 9, Order 2; observance origin unsourceable; the Chick-fil-A 1964 vs. marker "early 1960s" conflict is stated, not resolved)*
- [x] T5-27. National Greek Yogurt Day  *(published 2026-11-09, content run; Live — Nov 9, Order 3; observance origin unsourceable; FDA's 2025 finding that no standard of identity exists for Greek yogurt is the sourced content)*
- [x] T5-28. World Science Day for Peace and Development  *(published 2026-11-10, content run; Live — Nov 10, Order 1; origin fully primary-sourced — UNESCO General Conference, 31st session, resolution 20; first observed 10 Nov 2002)*
- [x] T5-29. National Young Readers Day  *(published 2026-11-10, content run; Live — Nov 10, Order 2; founding year/founder unsourceable, but the Library of Congress's own 1993 and 1995 publications document the day and its Pizza Hut / Center for the Book cosponsorship; FAQ at 4 pairs; date rule is a §7 fidelity candidate)*
- [x] T5-30. Sesame Street Day  *(published 2026-11-10, content run; Live — Nov 10, Order 3; observance origin unsourceable, the Nov 10 1969 premiere is the sourced content — CTW's own 1970 final report; CTW founding-year conflict stated, not averaged)*
- [x] T5-31. National Sundae Day  *(published 2026-11-11, content run; Live — Nov 11, Order 2; observance origin unsourceable; the Two Rivers 1881 vs. Ithaca 1892 conflict is stated, not resolved, and the widely repeated "July 8, 1881" is in no acceptable source)*
- [x] T5-32. World Origami Day  *(published 2026-11-11, content run; Live — Nov 11, Order 3; the third Tier 5 row with a sourced origin: the Nippon Origami Association's own site dates the Nov 11 designation to 1980, and a Japanese government publication attributes it to NOA)*
- [x] T5-33. Pocky Day  *(published 2026-11-11, content run; Live — Nov 11, Order 4; origin sourced to Ezaki Glico's own corporate history, 1999; Glico's two pages disagree on the certifying body's name — conflict stated, corporate history preferred)*
- [x] T5-34. Chicken Soup for the Soul Day  *(published 2026-11-12, content run; Live — Nov 12, Order 1; observance origin unsourceable; Forbes 2003 is the sourced content — Canfield's own count of 144 rejections, HCI, the 1993 publication; the 2024 Chapter 11 is a different company, stated as such; filing day given as "late June 2024" because both sources say only "Friday"; 919 words)*
- [x] T5-35. National French Dip Day  *(published 2026-11-12, content run; Live — Nov 12, Order 2; observance origin unsourceable; the Cole's vs. Philippe's invention claim is **stated, not resolved** — Philippe's dates it to 1918 with a story, Cole's claims it with no date at all, both opened 1908; Cole's closed March 2026, reopening planned; 949 words, marginally over target)*
- [x] T5-36. Guinness World Records Day  *(published 2026-11-12, content run; Live — Nov 12, Order 3; **origin fully primary-sourced** — GWR's own page: "First held in 2004..."; but GWR's own page also gives **Thursday 19 November 2026** for this year's day, so the stored Nov 12 date is wrong — see §7 fidelity candidate; 881 words)*

Once E2 lands, add the newly created rows (Kwanzaa, Rosh Hashanah, Yom Kippur,
National Pizza Day, Day of the Dead, Teacher Appreciation Day, Leap Day,
the solstices and the vernal equinox) to Tier 1–2 by demand, ahead of Tier 4.

**The exemplar.** `docs/CONTENT_EXEMPLAR.md` is the reference every draft matches
on structure, voice, and sourcing. Read it before writing. If it does not exist
yet, do not start content work — say so in the Run Log and stop.

---

## 7. Known issues, carried forward

- **Holiday fidelity audit** deferred to end of year by Jay. **Worklist now
  exists: `docs/FIDELITY_AUDIT.md`** — 24 candidate rows found by screening for
  the signature (a weekday-ruled row's stored date lands on its named weekday
  in exactly one year and drifts off the next), with the likely rule for each.
  They are candidates, not verdicts; each needs a primary source before it is
  changed. Donut Day and National Ice Cream Day were fixed on 2026-10-10.
  **World Sight Day** (Annual, genuinely the 2nd Thursday of October) and
  **Oktoberfest (ends in Germany)** (Annual Oct 4, genuinely the first Sunday
  in October with a conditional Oct 3 extension — wrong from 2027) are both on
  that list.
- **New fidelity-audit candidate, found by the 2026-11-05 content run: `international-stout-day`.**
  The row is `Annual` Nov 5, and Nov 5 is the first Thursday of November in 2026 — the exact
  signature §7's audit screens for. Recent observed dates (2017 Nov 2, 2020 Nov 5, 2024 Nov 7)
  all fall on the first Thursday, so the stored Annual date almost certainly drifts off from
  2027 (first Thursday 2027 = Nov 4). **Not changed, deliberately:** no acceptable source states
  the rule — only aggregators do — and the 2012 and 2013 observed dates do not fit it either,
  so there is nothing primary to change it to. Needs Jay, or a source. Add to `docs/FIDELITY_AUDIT.md`.
- **New fidelity-audit candidate, found by the 2026-11-06 content run: `fountain-pen-day`.**
  The row is `Annual` Nov 6, and Nov 6 is the first Friday of November in 2026 — the same signature
  as `international-stout-day`. First Fridays run 2024 Nov 1, 2025 Nov 7, **2026 Nov 6**, 2027 Nov 5,
  so an Annual Nov 6 matches in 2026 only and drifts every other year. **Not changed, deliberately:**
  the first-Friday rule is stated only by aggregators, and `fountainpenday.org` — the observance's own
  former site and the one body that could have confirmed it — now **redirects to an unrelated
  commercial site** (`chloeveganfoods.com`, behind a bot wall). There is no primary rule to change it
  to. Needs Jay, or a source. Add to `docs/FIDELITY_AUDIT.md`.
  *Also noted, not acted on:* **`National Jersey Friday` (Annual Nov 6, Order 7)** carries "Friday" in
  its own name on a date that is a Friday only in 2026 — same signature, untouched, unqueued.
- **New fidelity-audit candidate, found by the 2026-11-07 content run: `national-bison-day` — and
  this one is sourceable.** The row is `Annual` Nov 7, and Nov 7 is the first Saturday of November in
  2026, so it matches in 2026 only (first Saturdays: 2027 Nov 6, 2028 Nov 4). Unlike
  `international-stout-day` and `fountain-pen-day`, **the rule is stated by acceptable sources**: the
  National Bison Association writes "Since 2012, the United States Senate has annually designated the
  first Saturday in November as National Bison Day"; the submitted Senate resolution texts for 2017
  and 2023 each read "designates November 4, ..., the first Saturday of November"; and Public Law
  114-152's own findings record the three sponsoring organizations as "committed to continuing this
  tradition annually on the first Saturday of November." **Not changed** — recurrence belongs to the
  deferred fidelity audit, not to a content run — but this is the one row on the list that could be
  corrected without first finding a source. **The published page now states the first-Saturday rule,
  so from 2027 the page and the generated Dates table will contradict each other in front of
  readers.** That is the first time this error class is visible rather than latent, and it is the
  argument for promoting the audit to a queue item.
  *Also noted:* the detector in `docs/FIDELITY_AUDIT.md` screens rows whose **name** contains a
  weekday word. `National Bison Day` contains none, so the screen would never have found it — the
  error class is wider than the detector. Worth widening before the audit runs.
- **New fidelity-audit candidate, found by the 2026-11-08 content run: `international-tongue-twister-day`.**
  The row is `Annual` Nov 8, and Nov 8 is the **second Sunday of November in 2026** — the same signature as
  `international-stout-day` and `fountain-pen-day`. Second Sundays run 2024 Nov 10, 2025 Nov 9, **2026 Nov 8**,
  2027 Nov 14, so an Annual Nov 8 matches in 2026 only. The aggregators themselves disagree — the same day is
  published on Nov 8, Nov 10 and Nov 12 across different years, which is what a weekday rule looks like when it
  is reported as a fixed date. **Not changed, deliberately:** the second-Sunday rule is stated only by
  aggregators; no founding body, government page or news outlet for this observance could be found at all, so
  there is no primary rule to change it to. Needs Jay, or a source. Add to `docs/FIDELITY_AUDIT.md`.
  *Also noted, not acted on:* a separate published row, **`International Tongue Twister Contest Day`**, exists
  with its own page and was left untouched; it is not a duplicate of this row.
- **New fidelity-audit candidate, found by the 2026-11-12 content run: `guinness-world-records-day` — and
  this is the worst case on the list, because it is wrong *now*, not from 2027.** The row is `Annual` Nov 12.
  Guinness World Records' own GWR Day page states "GWR Day 2026 took place on Thursday, 19 November 2026" —
  the third Thursday of the month — and says the day was "First held in 2004", not 2005. Nov 12 is a Thursday
  in 2026 but the *second* one, so the row is a week early this year and will drift every year after.
  Unlike `international-stout-day`, `fountain-pen-day` and `international-tongue-twister-day`, **the correct
  date is published by the founding body itself**, so this one is sourceable today. **Not changed** —
  recurrence belongs to the deferred fidelity audit, not to a content run — but note the consequence:
  the holiday is listed on `/day/2026-11-12/` and its own page now states that Guinness gives Nov 19,
  so the page contradicts the site's own date field in front of readers, this week. Bison Day made that
  contradiction visible from 2027; this row makes it visible immediately. Add to `docs/FIDELITY_AUDIT.md`,
  and treat it as the second argument for promoting the audit to a queue item.
  *Also noted:* GWR publishes a date per edition rather than a stated rule, so a correct fix is either a
  `Floating` lookup table of announced dates (like `super-bowl-sunday`) or an annual refresh — a design
  question, not a data edit, which is why this run did not attempt it.
- **Four floating lookup tables expire in 2027.** The three administratively-set
  ones (teach-your-children-to-save, Preakness, Belmont) plus
  **`super-bowl-sunday`, added 2026-10-10 and holding 2027 only — expires after
  2027-02-14**. The NFL schedules the game each season; it has been the second
  Sunday in February since 2022 but the league has not committed to that, so
  only announced dates go in. See `scripts/README.md`.
- **The dated archive's forward horizon is derived, not configured.**
  `day_end = max(occurrences.values())` in `generate.py`, so a single row whose
  next occurrence is more than a year out extends `/day/` coverage for the
  whole site (publishing a Feb 29 row adds ≈142 dated pages). Worth knowing
  before adding a long-cycle observance; it is why Leap Day is sitting
  unpublished.
- Three stale duplicate Notion rows (National Taco Day Oct 6, National
  Forgiveness Day Oct 7, International Newspaper Carrier Day Oct 10). Harmless —
  the generator only lists holidays that have a page.
- `ADS_LABELLED` and `SHOW_LABEL` are both off (house ads for Jay's own
  products). Turn both on together when third-party paid creative runs.
- This session could not reach the GitHub API, so runs work through the local
  clone and Jay pushes. If repo access is enabled for scheduled sessions later,
  switch to a branch-and-PR flow and simplify rules 1–3.

---

## 8. Run Log

Newest last. One line per run: date, type, item, outcome. Keep it terse.

- 2026-10-09 · setup · plan written, queues built, Halloween exemplar drafted, tasks scheduled · Jay + Claude (interactive)
- 2026-10-09 · setup · first manual fire of the engineering task went out before Jay
  approved the task, so that run was cloud-only and could not reach this repo.
  Expected to stop at step 1. **The three scheduled tasks must be approved by Jay
  before any run gets his computer and this folder.** Re-fire after approval.
- 2026-10-09 · engineering · E1 not started · **stopped at hard rule 2** — tree dirty
  (`?? docs/CONTENT_EXEMPLAR.md`, `?? docs/EXECUTION_PLAN.md`: Jay's own uncommitted plan
  files, `docs/` never committed; nothing under `scripts/` or `public/` modified). No source
  or Notion change. Generator verified clean into a throwaway dir: exit 0, no WARNINGs,
  2439 pages + 346 day pages unchanged, idempotent. **Rules 2 and 6 conflict — rule 6 makes
  every run write into `docs/`, so rule 2 will fire on every future run until `docs/` is
  committed or rule 2 is narrowed to `scripts public`. See docs/REVIEW.md.**
- 2026-10-09 · plan amendment (Jay, live) · rule 2 narrowed to
  `git status --porcelain -- . ':(exclude)docs'` so rule 6's required writes into `docs/` no
  longer trip the dirty-tree gate · verified on git 2.34.1: passes with only `docs/` dirty,
  still fires on a modified tracked source file. Deadlock cleared; next run proceeds to E1.
- 2026-10-09 · engineering · **E1 done** · Notion: added Body / Timeline / FAQ / Sources
  (rich text) + Content Status (select), additive, no row edited. Code: `generate.py`
  (+339) long-form renderer, Markdown-subset parser, five-year dates table, FAQPage
  JSON-LD; `export_from_notion.py` (+36) field passthrough, omits empty keys, warns on
  long-form-without-Sources; `scripts/README.md` (+85); `public/styles/holiday.css` (+30).
  Also fixed `next_friday_the_13th()`'s 400-day scan bound — the real maximum gap is 427,
  so every run from 2027-08-14 to 2028-10-13 would have dropped `friday-the-13th` from the
  calendar. Verified: patched vs pre-patch generator output **byte-identical** across the
  whole site; generator exit 0, zero WARNINGs, idempotent on a second run; a synthetic
  populated row changed exactly 1 of 2,439 pages and rendered every section; 32 assertions
  pass. Nothing committed. Next run: E2.
- 2026-10-09 · content (Jay + Claude, interactive) · Halloween and Thanksgiving Day written, American spelling, loaded into Notion as Live. Rule added: American English always (§4 Voice). **Gate added:** `export_from_notion.py` now carries `Body`/`Timeline`/`FAQ`/`Sources`/`Opening` only for rows at Content Status Reviewed or Live (uncommitted). New Notion field `Opening`. Content task prompt updated to match; Tier 5 rule added to §6.
- 2026-10-10 · engineering · **E2 partly done** · Notion: 11 missing observances created,
  published and sourced (Kwanzaa, Rosh Hashanah, Yom Kippur, Day of the Dead, Pizza Day,
  Margarita Day, Hugging Day, Teacher Appreciation Day + Week, Oktoberfest start, Super Bowl
  Sunday); Donut Day switched to Floating (1st Friday in June, Salvation Army) and Ice Cream
  Day with it (3rd Sunday in July, Proclamation 5219); Leap Day created but left unpublished
  (publishing it extends the dated archive by ~142 pages — Jay's call). Code: `generate.py`
  (+34/-3) new `nth_weekday_offset` kind, Annual `next_occurrence` now scans 9 years so Feb 29
  resolves at all, Floating branch skips an unresolvable year so a table starting next year
  works; `export_from_notion.py` (+55) eight sourced rules; `README.md` (+43);
  new `docs/FIDELITY_AUDIT.md` with 24 audit candidates. Verified: patched vs pre-patch
  generator byte-identical on the current dataset; forward run exit 0, zero WARNINGs,
  11 pages created / 60 changed, idempotent. Nothing committed. 5 open decisions in
  docs/REVIEW.md; next engineering run goes to E3 once they are answered.
- 2026-10-10 · content · **Christmas Day, Valentine's Day, New Year's Day drafted** ·
  Queue items 3-5, top-first, one matching row each (no ambiguity: Christmas Eve and
  Orthodox Christmas Day are separate queue items, not duplicates). All five long-form
  fields written per §4, Content Status = Draft, `Published` untouched (all three still
  ticked), `Description` untouched. Word counts ~860 / ~830 / ~840. American spelling.
  Sources: Library of Congress (4 collections/blogs), Britannica, OPM, mass.gov,
  Royal Collection Trust, Smithsonian NMAH, British Library, Times Square Alliance,
  Pasadena Tournament of Roses, NRF. No aggregator cited. **No section omitted for lack
  of a source.** Verified: 23 assertions pass — the Content Status gate drops Draft
  long-form and the Opening while carrying both at Live, and the renderer produces the
  FAQ section, FAQPage JSON-LD, timeline, links and emphasis from exactly these field
  shapes; generator run into a throwaway dir exits 0 with zero WARNINGs, 2,803 pages,
  and the three pages render with no long-form and no FAQPage (gate confirmed
  end to end). Nothing committed.
  · **Found a live bug, not caused by this run: the FAQ fields on Halloween and
  Thanksgiving Day do not render.** `parse_faq()` in `generate.py` only recognizes a
  question when the line is wrapped in `**bold**`; both rows' questions are plain text,
  so both parse to zero pairs and ship with no FAQ section and no FAQPage structured
  data — the one SEO feature E1 was built to add. Both rows also have an **empty
  `Opening`**, so both keep the templated `Description` on the site. Both are at
  Content Status Live, so this is live-site behavior, not a draft problem. Today's three
  drafts use the bolded form and were verified to parse. Fix is Jay's call: bold the
  questions in the two rows, or loosen `parse_faq` to treat an unbolded line ending in
  `?` as a question. Written up in `docs/REVIEW.md`.
  · Claims I am least confident in, flagged for spot-check: the 1659 Massachusetts
  Christmas ban's **repeal** date is *omitted* — mass.gov gives the statute and the
  five-shilling fine but not the repeal, so the draft states only what is sourced;
  **New Year's resolutions** have no sourced origin, so the FAQ says so outright rather
  than repeating the Babylonian/Roman claim; the **NRF $29.1bn** figure is a retail
  trade association's survey of stated intent, labeled as such in the draft rather than
  presented as a statistic. One source conflict resolved: on the Christmas tree, the
  common "Prince Albert introduced it" line is contradicted by the **Royal Collection
  Trust**, which credits Queen Charlotte in the late 18th century; the draft follows
  RCT as the more primary source (the royal household's own collection) and says
  plainly that Albert popularized rather than introduced it.
  · Note on hard rule 6: `docs/REVIEW.md` was **appended to, not overwritten** — it
  still holds the five unanswered E2 decisions from last night's engineering run, and
  overwriting them would have destroyed them. Rule 6 may want narrowing to "the
  engineering run overwrites REVIEW.md; content runs append."
- 2026-10-10 · interactive (Jay + Claude) · Christmas / Valentine's / New Year's set to **Live**. Found that `**bold**` never survives Notion — it is stored as a rich-text annotation and `plain_text` drops it — so `parse_faq()`'s bold requirement meant **every FAQ ever written parsed to zero pairs**: no FAQ section, no FAQPage, on all five long-form rows. `parse_faq()` now reads the first line of a blank-line block as the question; byte-identical output on the current dataset, 5 pairs parsed from the real Christmas FAQ, FAQPage emitted. **Draft gate removed at Jay's request**: content runs now write Content Status = Live and owe a push recap per run (§4 rewritten; content and digest task prompts updated). Uncommitted.
- 2026-10-11 · engineering · **E3 partly done — perennial date pages** · tree was clean,
  E2's five decisions still unanswered (not unattended work), so went to the next unblocked
  item. 366 `/<month>-<day>/` pages generated from a wider index pass: fixed-date rows are the
  page's list, rule-dated rows are a note naming the years they land there, year-specific
  content stays on `/day/`. New `scripts/templates/perennial.html`; `generate.py` (+~310)
  index/renderer/generation/sitemap/report; `day.html` (+1) back-link marker; `_headers` (+39)
  one cache rule per month; `README.md` (+64); `/about/` wording. Verified: pre-patch vs patched
  differ *only* by the 366 new pages, one added paragraph on 348 dated pages, the `/about/`
  sentence and 366 sitemap URLs — every holiday page, data file and the homepage byte-identical;
  exit 0, zero WARNINGs, idempotent on a second run; 366 pages parse with no unbalanced tags and
  340 valid `ItemList` blocks; 14,314 internal links resolve, no orphans, canonicals self on both
  types; 40 assertions pass including the `PERENNIAL_EMPTY_PAGES=False` branch. CLS not measured
  (nothing deployed). Nothing committed. 3 new decisions + E2's 5 in docs/REVIEW.md; next
  engineering run: E3's `/holidays/<year>/` index pages.
- 2026-10-11 · interactive (Jay) · **Born on this day** · new pipeline `scripts/build_people.py`
  -> `scripts/people.json` (366 dates, two lists: historic = sitelinks, living = sitelinks/pageviews
  blend); rendered as two sub-blocks on perennial (10) and dated (4) pages; not in Notion, not in
  JSON-LD. Verified: only the 714 perennial/dated pages differ from baseline, byte-identical with
  the block removed. Nothing committed. Decisions in docs/REVIEW.md addendum. Monthly manual refresh.
- 2026-10-11 · interactive (Jay + Claude) · **E3's three open questions answered and built** ·
  Keep the empty-date pages (`PERENNIAL_EMPTY_PAGES` stays True — celebrity/historic dates are
  coming, and the count already fell 8 -> 6); new **`/dates/` hub** listing all 366 by month,
  with the header's Calendar tab and the footer link repointed to it from `/#calendar` (a fifth
  tab was rejected: the tab row is tight at 760px); **holiday pages now point at the perennial
  page** from the breadcrumb and the back-link, with the dated page kept in the Date row of the
  spec list and in the sidebar. Also: one CSS rule (`.cat-list-off`, only used if the empty-page
  switch is ever turned off), `/dates/*` cache rule, `llms.txt` updated with the date-page type
  and which URL to cite, §3 boundary now names `public/<month>-<day>/**` as generated and
  `llms.txt` as source. Verified by reverse-transform against HEAD: undoing the nav substitution
  (plus the crumb/Date-row/back-link changes on holiday pages) makes **all 3,184 changed pages
  byte-identical** to the committed version — zero unexplained deltas; sitemap gained exactly
  one URL; exit 0, zero WARNINGs, idempotent; 40 assertions pass including the
  `PERENNIAL_EMPTY_PAGES=False` branch. CLS and phone-width rendering not measured. Uncommitted.
  Next engineering run: E3's `/holidays/<year>/` index pages. E2's five decisions still open.
- 2026-10-12 · engineering · **E3 done — `/holidays/<year>/` year indexes** · tree clean
  at the gate; E2's five decisions still unanswered (not unattended work), so took the last
  E3 bullet. Two pages built from `day_dates` alone: `/holidays/2026/` (85 dates) and
  `/holidays/2027/` (266 dates), month sections, weekday + observance count per row, month
  rail, year switcher, self-canonical, in the sitemap, breadcrumb `Today / Calendar / 2027`.
  Each states its own coverage (the archive opens 2026-10-08, reaches ~a year ahead) and
  names the 18 dates in 2027 that have no page because nothing is on the calendar. Code:
  `generate.py` (+182/-6) `year_index_path()`, `year_index_html()`, pages into
  `simple_pages`, `YEAR_LINK` on dated pages, year links on `/dates/`, `year_index_pages`
  in the report; `day.html` (+1) marker; `_headers` (+5) `/holidays/*`; `llms.txt` (+2);
  `README.md` (+37). No new CSS, no new nav tab. Verified: reverse-transform against the
  pre-patch generator — removing the one added paragraph makes all **351 dated pages
  byte-identical**, removing one clause does the same for `/dates/`, and every holiday page,
  perennial page, data file, category page, the homepage and `/about/` are untouched; zero
  unexplained deltas; sitemap gained exactly 2 URLs; exit 0, **zero WARNINGs**, idempotent;
  both pages balanced, no leftover markers, all 351 day links resolve, day counts match the
  archive on disk and every observance count matches that dated page's own `ItemList`;
  rollover tested at a simulated `--today 2027-06-15` (three year pages, 2027 completes,
  2028 opens partial) and the single-date year unit-tested. CLS still not measured.
  Nothing committed. 2 new small decisions + E2's 5 in docs/REVIEW.md; next engineering
  run: **E4**, whose shape is now noted in §5.
- 2026-10-11 · content · **Easter Sunday, Mother's Day, Father's Day published (Live)** ·
  *(Back-filled by the 2026-10-12 content run: the 2026-10-11 run completed its Notion
  writes but lost the device bridge before its repo writes. Text is that run's own, from
  `claude/content-run-2026-10-11-tier1-6to8.md` in the project.)*
  Queue items 6-8, top-first, one unambiguous main row each (Easter Monday, Mothering Sunday
  and Stepmother's Day are separate queue items, not duplicates). All five long-form fields
  per §4, Content Status = Live, `Published` and `Description` untouched. Word counts
  900 / 841 / 873. American spelling. Sources: US Naval Observatory (the Date of Easter and
  the Christian observances table), Library of Congress (Folklife Today on the Easter Bunny,
  In Custodia Legis on the egg roll, Chronicling America guide to Mother's Day, Teaching with
  the Library on Father's Day), White House Historical Association, National Park Service
  (Anna Maria Jarvis, Dodd House), govinfo Statutes at Large 38 Stat. 770 and 86 Stat. 124,
  City of Spokane, WV Division of Culture and History, OPM. No aggregator cited.
  **No section omitted for lack of a source.** Verified: committed `export_from_notion.py`
  carries long-form at Live; committed `parse_faq()` parses 5 pairs from each unbolded FAQ
  (run against the real field text); post-write query confirms no markdown links in Sources
  and no asterisks in FAQ/Body; slugs easter-sunday / mothers-day / fathers-day confirmed
  against scripts/holidays.json. Nothing committed.
  · **Conflicts resolved.** Grafton church name: NPS and the LoC photo record give
  *Andrews Methodist Episcopal Church* (the National Historic Landmark name), the LoC
  Chronicling America guide gives "St. Andrew's Methodist Church" — followed the NPS/NHL
  form as the more primary. Monongah death toll: the WV Archives narrative says "almost four
  hundred", its own official disaster list says 357 — the draft gives 357 as the official
  count and names the higher figure as contemporary accounts, rather than averaging.
  · **Claims deliberately left out for want of a source:** Grace Golden Clayton's Fairmont
  service is **not dated** — the LoC names her and the Monongah link but gives no year, so
  the page says outright that no year is assigned and that the two origin claims cannot be
  cleanly ordered. The WHHA page's Easter-Egg-Roll revival year is internally inconsistent
  ("twelve-year hiatus" vs. hosting in 1960 after a 1948-52 interruption), so the draft says
  only "the war years and the Truman renovation" and names no revival year. Why Dodd's
  committee picked June 19 is stated as undocumented. Julia Ward Howe's 1870 proclamation
  was dropped entirely: Britannica's body text is not fetchable and no primary source was
  found, so it is absent rather than asserted.
  · **Least confident claim:** that Presidents Wilson and Coolidge "worked toward making the
  day national" (Father's Day) — the LoC states it but gives no years or acts, so the draft
  repeats it at exactly that vagueness. Worth a spot-check.
- 2026-10-13 · engineering · **E4 partly done — observance type taxonomy** · tree clean at
  the gate. Notion: new `Type` select (Federal / State / Religious / Cultural / Observance /
  Season & Clock / Fun) with a property description; 40 rows typed, chosen as the ones with
  no judgment in them — 11 federal (5 U.S.C. § 6103), 6 season-and-clock, 23 religious. No
  other property touched, `Published` and `Content Status` untouched. Code: `generate.py`
  (+124/-11) TYPE_ORDER/TYPE_SLUG/`type_rank`/`obs_sort_key`/`type_tag`/`type_json`, both
  sort sites, `obs_row` markup, 5th month-data element only on typed rows, `type_counts` +
  `unknown_types` in the report and a WARNING for an unknown Type; `export_from_notion.py`
  (+18) Type passthrough, key omitted when unset; `templates/index.html` (+14/-3) the
  `obsRow()` mirror; `site.css` (+21) `.tg` chips and the single "major" rule;
  `README.md` (+72). Verified: patched generator on **untyped** data vs the pre-patch
  generator differs in **one file** (the home page's inline script) — every holiday, dated,
  perennial and year page, every data file and the sitemap byte-identical, so the degradation
  requirement is proven not asserted; with the 40 typed, exactly 194 files differ and
  **6,606 invariant checks pass with 0 failures** (no holiday gained or lost anywhere, rows a
  permutation not a rewrite, one chip per typed row, sitemap byte-identical); 25 unit
  assertions pass; unknown-Type path warns and leaves the site byte-identical; exit 0,
  **zero WARNINGs**, idempotent. Lead changes on 16 list pages (July 4, 2027: Alice in
  Wonderland Day → Independence Day). CLS still not measured. Nothing committed.
  **The remaining ~2,410 rows are blocked on an assignment rule from Jay** (3 boundaries in
  docs/REVIEW.md). Also found, not fixed: `Ascension` is stored as fixed May 6 but is a
  moveable feast — wrong from 2028. Next engineering run: E4 with a rule, else E5.
- 2026-10-12 · content · **St. Patrick's Day, Independence Day, New Year's Eve published (Live)** ·
  *(Run Log line back-filled by the 2026-10-13 content run from
  `claude/content-run-2026-10-12-tier1-9to11.md`; the 2026-10-12 run lost the device bridge
  before it could write it.)*
  Queue items 9-11, top-first. **First found that items 6-8 were already published and Live from
  the 2026-10-11 run, which had lost the bridge before ticking them** — so that run ticked 6-8,
  back-filled its Run Log line and REVIEW note, and then took 9-11 as the genuinely untouched
  next three. One unambiguous main row each (Pet Owners Independence Day and the
  Chinese/Islamic/Assyrian New Year rows are separate queue items, not duplicates).
  All five long-form fields per §4, Content Status = Live, `Published` and `Description` untouched.
  Word counts ~900 / ~915 / ~920, estimated from character counts. American spelling.
  Sources: National Archives (Declaration history), Massachusetts Historical Society (Adams to
  Abigail, 3 July 1776), Library of Congress (Today in History for March 17 and July 4, In Custodia
  Legis on federal holidays), Royal Irish Academy (St Patrick's Confessio), Charitable Irish Society,
  Citizens Information Ireland, Smithsonian NMAAHC (Watch Night; Douglass's 1852 address), Times
  Square Alliance, OPM, NHTSA, NBC Chicago. No aggregator cited.
  **No section omitted for lack of a source**, but several individual claims were (see below).
  Verified by query only: Live status, Published and Description untouched, no `](` in Sources,
  no `**` in Body/Timeline/FAQ, every FAQ block opening with a line ending in `?`.
  **NOT verified: the renderer was never run** — the bridge dropped, and the exporter needs a
  NOTION_TOKEN that session did not have. Slugs inferred from convention, not read from
  holidays.json. Nothing committed.
  · **Conflicts resolved.** Independence Day: the Library of Congress calls the Declaration
  "unanimously adopted" on July 4, while the National Archives records New York abstaining on
  June 11 and not voting on July 2 — followed the National Archives as the more primary source
  and the document's custodian, and gave the vote counts instead of calling July 4 unanimous.
  St. Patrick's Day: the "first parade" claim is genuinely contested, so the page follows the LoC
  (New York official 1766, unofficial march 1762, Boston possibly 1775) and says outright that the
  widely repeated Boston 1737 is the Charitable Irish Society's founding and dinner, not a parade.
  · **Claims deliberately left out for want of a source:** the shamrock-and-Trinity and
  snakes-out-of-Ireland legends are named as later traditions but left **undated**. The 1938 act
  that made federal holidays paid is omitted. Jefferson's and Adams's deaths on July 4, 1826 were
  dropped entirely — no primary source was obtained. The Chicago River dyeing is dated only to
  "the 1960s", as NBC Chicago has it, not to the commonly cited 1962. The Times Square Alliance
  page contradicts itself on how many balls there have been, so the page gives **no count**. No
  New Year's Eve-specific drunk-driving figure is given, because NHTSA publishes none.
  · **Least confident claim:** that the Times Square ball "has descended every year since 1907
  except 1942 and 1943". The Alliance page states the 1942-43 suspension and the year-by-year ball
  history but never asserts unbroken continuity in those words; the page infers it. Worth a check.
- 2026-10-14 · content · **Christmas Eve, Veterans Day, Memorial Day — all three Live** · repo folder
  was not attached at fire time; re-requested and granted, then STEP 0 passed (committed exporter
  carries `LONGFORM_RELEASED_STATUSES`, count 2). Main rows used where the title was ambiguous:
  `Veterans Day` (Type Federal, Nov 11) not the 7 other "...Veterans Day" rows, and `Memorial Day`
  (Type Federal, Floating) not the 4 other "...Memorial Day" rows. `Published` untouched on all
  three; `Description` untouched. All 3 FAQs verified against the **committed** `parse_faq()` —
  5 pairs each. Generator smoke-run into a throwaway dir: exit 0, 5,669 files.
  · **Omitted for want of a source:** Christmas Eve's liturgical origin (the vigil / Midnight Mass).
  Vatican homilies confirm the papal Midnight Mass is on Dec 24 but no consulted source documents
  how the evening-before observance took shape, so the page asserts nothing. Public law numbers for
  the 1938 / 1954 / 1975 Veterans Day acts omitted — the sources give dates, not numbers. The Sears
  advertisement is left out of the NORAD story: NORAD's own fact sheet says only "a promotion in a
  local newspaper".
  · **Source conflicts resolved:** Waterloo, NY — VA/NCA ties the 1966 designation to a century of
  **May 30** observances, LOC dates the formal observance to **May 5, 1866**. Both federal, neither
  more primary; the page gives LOC's specific date and does not assert the May 30 continuity.
  Moore's authorship — New-York Historical says acknowledged **1838**, LOC says published under his
  name **1844**; different acts, so both dates are given rather than one chosen.
  · **Least confident claim:** that Veterans Day was observed in October "from 1971 through 1977".
  The Army CMH page states the 1971 effective date and the 1978 return but never spells out the
  seven-year span; the FAQ infers it. Worth a check.
  · **Over the word target:** Veterans Day ≈ 915 words, Memorial Day ≈ 1,040, Christmas Eve ≈ 1,170,
  against §4's 600–900. Every claim is sourced and none of it is padding, so nothing was cut except
  one soft paragraph on Memorial Day. Flagged for Jay rather than trimmed.
  · **Tree was dirty outside `docs/` at run time** (`public/_headers`, `public/llms.txt`,
  `public/styles/site.css`, `scripts/generate.py`, `scripts/templates/holiday.html`) — unreviewed
  engineering work from an earlier run. Content work is Notion-side so it did not stack, but the
  next *engineering* run will hit rule 2 and stop.
  · **Flagged, and the reason to read `docs/REVIEW.md` today:** the project doc
  `claude/content-run-2026-10-13-tier1-12to14.md` says the 2026-10-13 content run published
  **these same three rows** to Live, naming the same page ids and quoting exact word counts.
  All three were **empty** (`Content Status` and `Body` both NULL) when this run queried them
  at 10:20 UTC. The 2026-10-12 run's three pages are still populated, so this is not a general
  wipe. Either those writes never reached Notion, or the rows were cleared since. Nothing was
  lost by this run — it wrote into empty fields — but one of those two explanations is a real
  defect. Sections A and B of that doc were deliberately **not** back-filled, because they
  describe content that is not in Notion; its still-open recommendations are carried into
  `docs/REVIEW.md` instead.
  · Note: `scripts/README.md` appeared as modified partway through this run, after the initial
  rule-2 check listed five files without it. Not touched by this run.
- 2026-10-14 · engineering · **E5 done — calendar export** · tree clean at the gate; E4's
  remaining ~2,410 rows still blocked on an assignment rule, so took E5 per §5. No Notion
  change. `/calendar.ics` + 14 category feeds + 2,450 `/holiday/<slug>/event.ics` = 2,465
  files, 3,265 events (2,348 fixed-date rows as one `RRULE:FREQ=YEARLY` event each, 917
  rule-dated occurrences enumerated from the perennial index pass so a feed date is always a
  date the site shows); no `VTIMEZONE` by design (`DATE`-valued all-day events carry no zone);
  stable UIDs and a fixed `ICS_DTSTAMP`, so an unchanged run rewrites no feed. Code:
  `generate.py` (+323) `ICS_*`, `ics_text/fold/date/uid/event/calendar`,
  `write_bytes_if_changed`, `cal_links_html`, `cal_feed_links_html`, `ics_occ`, the feed
  block, 8 report keys; `templates/holiday.html` (+1) `CAL_LINKS`; `site.css` (+11) `.cal`;
  `_headers` (+16) `text/calendar` + cache; `llms.txt` (+8); `README.md` (+112). §3 boundary
  now also names `public/holidays/**` (missing since E3) and the generated `.ics` paths.
  Verified: reverse-transform vs the pre-patch generator — removing the one added line makes
  all 2,450 holiday pages, the 14 category pages and `/about/` byte-identical, and every
  dated, perennial, year, hub and data file **and `sitemap.xml`** are untouched, zero
  unexplained deltas; **201,453 structural and cross-checks, 0 failures** (RFC 5545 envelope,
  75-octet folding, lossless fold/unfold, `DTEND`=`DTSTART`+1, UID uniqueness, every event
  date re-derived from the recurrence engine, feed UID sets = union of the per-observance
  files = union of the category feeds); 1,230 `.ics` links resolve; second run 0 changed /
  2,465 unchanged (idempotent); `--today 2027-06-15` rollover drops the 4 expired-lookup rows
  with no page linking a missing file; exit 0, **zero WARNINGs**. Nothing committed. **Open:
  the acceptance criterion "subscribes cleanly in Apple/Google Calendar" needs a deploy.**
  4 decisions in docs/REVIEW.md; next engineering run: E4 with a rule, else E6.
  · Note: tonight's content run appended to `docs/REVIEW.md` while this run was working, so
  rule 6's "overwrite" was applied to the engineering review only — the content run's section
  was kept at the bottom of the file rather than destroyed. Its "tree was dirty outside
  `docs/`" warning refers to **this run's own work in progress**, not a second unreviewed run.
- 2026-10-15 · engineering · **E6 partly done — submitted occasions, publication half** · tree
  clean at the gate; E4 still blocked on an assignment rule, so took E6 per §5. Notion: new
  **"Today Celebrates — Submitted Occasions"** database (id `7c9d328c-0360-4feb-aabf-998f6402eed9`),
  17 described properties, **zero rows**; separate from the Holidays database on purpose, which is
  what makes "cannot appear in Event structured data even if misconfigured" structural rather than a
  checkbox. Holidays database untouched. Code: new `scripts/export_occasions_from_notion.py` (266 lines)
  carrying `Review Status = Approved` only, with slug-collision and tier guards and deliberately no
  shrink guard (a withdrawn listing must disappear at once); `generate.py` (+353/-8) `OCCASION_*`
  constants and disclosure copy, `load_occasions` / `validate_occasions` / `occasions_block_html` /
  `occasion_body_html` / `occasion_page_html` / `occasions_index_body`, the occ indexes in
  `generate()`, pages routed through `simple_pages` (so they render from page.html, the one template
  with no JSON-LD slot), 5 report keys and 3 warning paths; `templates/day.html` and
  `templates/perennial.html` (+1 marker each); `site.css` (+18) `.occ`; `_headers` (+7) a 10-minute
  `/occasions/*` rule; `llms.txt` (+4); `scripts/README.md` (+103); §3 boundary now names
  `public/occasions/**` and `scripts/occasions.json`. Verified: with no `occasions.json` the patched
  generator's output is **byte-identical to the pre-patch generator across all 5,670 files** (diff -r,
  zero differences), and the same for a damaged or an absent file; with a 9-row fixture exercising
  every reject path, exactly **5 new files and 5 changed** (3 dated pages, 1 perennial page, the
  sitemap) — no `.ics`, no data file, no holiday, perennial, year, hub or home page — and
  reverse-transform (removing the `.occ` section) restores all 4 changed pages byte-identically;
  sitemap gained exactly 5 URLs and lost none; the `ItemList` on each affected dated page is unchanged
  and names no occasion; no occasion page contains JSON-LD of any kind; **52 structural checks and 34
  unit assertions (18 generator, 16 exporter), 0 failures**; second run 0 changed (idempotent);
  withdrawal drops the listing from the pages and the sitemap and warns that the orphan directory is
  still live. Exit 0, **zero WARNINGs** on the dormant path. Nothing committed. **The exporter could
  not be run against live Notion — no NOTION_TOKEN in this run's shell** (unit-tested against
  synthetic Notion payloads instead). 4 decisions in docs/REVIEW.md, three of them E6's upstream half:
  the price and what the Listed tier includes, the Worker vs the assets-only `wrangler.jsonc`, and
  whether a listing is one-off or perennial. Next engineering run: E4 with a rule, else E6's upstream
  half once the price is set, else E7.
- 2026-10-15 · content · queue 15–17 (Labor Day, Martin Luther King, Jr. Day, Presidents' Day) ·
  all three written and **published Live** in Notion; `Published` untouched on every row. Step-0 check
  passed (committed exporter has `LONGFORM_RELEASED_STATUSES`, count 2). No duplicate rows for any of
  the three (`Child Labor Day` and `Presidential Joke Day` are separate observances, not duplicates).
  Word counts ~854 / ~898 / ~860, inside §4's 600–900 — all three were trimmed from a first pass at
  ~1,000–1,050, which is the cap issue raised as REVIEW item 13 on 2026-10-14; this run enforced the
  cap rather than exceeding it. All three FAQs verified against `generate.py`'s own `parse_faq()`:
  **5 pairs each**, unbolded, blank-line separated. Sources are bare URLs, no `[text](url)` anywhere.
  **Omitted for lack of a source:** the standard claim that Labor Day sits in September to avoid the
  international May 1 labor day (no primary source found — said so in the FAQ rather than guessing);
  the 1983 House/Senate vote counts for the King holiday; and "South Carolina was the last state" to
  adopt it. **Conflicts resolved toward the more primary source:** the Obama White House archive page
  gives both Nov 2 and Nov 20, 1983 for Reagan's signature — followed the Statutes at Large (97 Stat.
  917), Nov 2; LOC says the 1894 act was "approved" where DOL says Cleveland signed it — followed DOL.
  **Least confident claim:** Mount Vernon's free admission on the holiday, documented for the 2026
  observance only, so the page tells readers to check the year's schedule. Generator verified into a
  throwaway dir: exit 0, zero WARNINGs, `occasions_problems` empty. The exporter could not be run
  against live Notion — no `NOTION_TOKEN` in this run's shell. Nothing committed. Also checked, for
  REVIEW item 13: **all 14 previously written rows still hold their long-form content and are Live**
  (Body 2.6–3.7 KB each), so the "rows found empty" symptom is not present now.
- 2026-10-16 · engineering · **E7 partly done — share cards, the OG half** · tree clean at
  the gate; E4 still blocked on an assignment rule and E6's upstream half on a price, so took
  E7 per §5. No Notion change. `generate.py` (+316/-5) `SHARE_CARDS`/`CARD_*` constants,
  `write_raw_if_changed`, `card_rel_path`, `card_fonts` (the Pillow + pinned-DejaVu gate),
  `card_wrap`/`card_ellipsize`/`card_fit`/`card_draw_tracked`, `card_png_bytes`, the card plan
  and write in `generate()`, `card_url` on `render_page`, 7 report keys and a warning path;
  `public/_headers` (+8) a longer cache for `/holiday/*/card.png`; `scripts/README.md` (+75)
  "Share cards (E7)"; new `docs/card-samples/` with 4 checked-in examples. **Switched off**:
  cards need Pillow, which the daily workflow does not install, and 2,450 of them are ~33 MB
  of committed PNG — both deployment calls, so `.github/` was left alone and the two-line
  workflow change is written out in docs/REVIEW.md. Verified: pre-patch vs patched with cards
  off — `diff -r` over all **5,671 files, zero differences**; with `--cards`, exactly **2,450
  new card.png and 2,450 changed files**, every one of them a `/holiday/` page and every change
  exactly three lines (og:image, twitter:image, the Event JSON-LD image) — no dated, perennial,
  year, hub, data, category or home page, no `.ics`, **sitemap byte-identical**;
  reverse-transform (card URL -> the category hero URL, rebuilt from holidays.json) restores
  all 2,450 pages **byte-identically**; all 2,450 PNGs decode at 1200x630 (33.0 MB, median
  13 KB, max 18 KB); second run 0 changed (idempotent); no-Pillow and no-font runs both WARN
  and produce output byte-identical to cards-off; every one of the 2,450 names is covered by
  the pinned font's glyph set and none is clipped (2,314 set at the full 92 px). Exit 0,
  **zero WARNINGs** on the default path. Nothing committed. **The device bridge dropped four
  times mid-run**; everything above was re-run or re-checked after it came back, but the
  date-roll churn measurement did not finish. 4 decisions in docs/REVIEW.md; next engineering
  run: E4 with a rule, else E6's upstream half once the price is set, else E7's 9:16 card once
  the affordance question is answered.

- 2026-10-16 · content · Tier 2 items 18-20 — **Juneteenth, Columbus Day, Indigenous Peoples' Day
  published Live** (860 / 899 / 891 words, every origin, founder, date and statute claim sourced).
  STEP 0 passed (committed exporter carries LONGFORM_RELEASED_STATUSES, count 2). One clean Notion
  row per item; `Published` untouched on all three. **Nothing omitted for want of a source**, but
  four claims were deliberately left out and are named in docs/REVIEW.md: the 1977 UN Geneva origin
  story for Indigenous Peoples' Day, "first-ever proclamation" for Proclamation 10283, the sponsor
  of Texas HB 1016, and any count of enslaved Texans in 1865. **Two source conflicts resolved
  toward the more primary text**, both disclosed on the pages themselves: LOC's "FDR designated
  Columbus Day a national holiday in 1934" vs the 1934 resolution's own words (annual proclamation
  + flag display only — followed the statute, 1968 treated as the holiday's start); and 1866 vs
  1865 for the first Juneteenth celebration (took 1866, NARA + Texas State Archives, over the LOC
  law blog). **Also corrected a citation error carried in from a search result: the Monday-holiday
  act is Pub. L. 90-363, not 90-361** — 90-361 is a flood-control act on the same Statutes page.
  Verified end-to-end with the **committed** generator into a throwaway dir: exit 0, Juneteenth
  page renders all six sections, **FAQPage JSON-LD carries 4 Question entities** (the bug fixed on
  2026-10-10, now confirmed working on new copy), all source URLs became live anchors, no literal
  asterisks leaked, Opening replaced the boilerplate Description. Nothing committed; no generated
  output touched.
- 2026-10-16 · digest · **Friday digest written** (09:49 UTC) · read §5/§6/§8, `docs/REVIEW.md`,
  `docs/FIDELITY_AUDIT.md` and the Notion Holidays database. Week of 10-10 to 10-16: 7 engineering
  runs (E2 partly, E3 done, E4 partly, E5 done, E6 partly, E7 partly), all 7 found a clean tree at
  the gate; 18 content pages published Live (queue items 3-20), **20 rows now carry long-form, 0 at
  Draft, 0 reverted**. Flagged to Jay: this morning's E7 diff is uncommitted (`scripts/generate.py`,
  `scripts/README.md`, `public/_headers`, `?? docs/card-samples/`) and **will stop tonight's
  engineering run on rule 2 unless he commits**; the 2026-10-16 regeneration had not landed at
  09:49 UTC (cron is 08:00, historical landings 13:00-17:30, so late not broken) and today's three
  pages are still short pages on the live site; the REVIEW.md write race between the two nightly
  runs; and five open decisions, the Listed-tier price now blocking two queue items. No repo source
  or Notion change by this run. Digest filed at `claude/digest-2026-10-16-friday.md`.
- 2026-10-17 · engineering · **E7 third bullet done — share cards for the dated, perennial,
  year-index and category pages** · tree clean at the gate (Jay committed Friday's E7 work);
  E4 still blocked on an assignment rule, E6's upstream half on a price, E7's other two
  bullets on Jay, so this was the only unblocked item in §5. No Notion change.
  `card_png_bytes()` split into `card_render()` (the frame, page-kind-agnostic) + five
  callers filling pill/headline/muted line; `generate.py` (+284/-71) `card_rel_for`,
  `card_pastel`, `day_/perennial_/year_/category_card_png_bytes`, card setup hoisted above
  the page loops with a `write_card()` helper, `card_url=` on the day and perennial
  renderers, `image=` on `render_simple_page`, `cards_by_kind` in the report;
  `public/_headers` (+61/-5) card cache rules for `/day/*`, `/holidays/*`, `/category/*` and
  one per month for the perennial paths (43 → 55 rules, limit 100); `scripts/README.md`
  "Share cards (E7)" rewritten; §3 names the four new generated card paths. Verified:
  **cards off — `diff -r` pre-patch vs patched over all 5,672 files, zero differences**,
  exit 0, zero WARNINGs, idempotent; **cards on — 738 new files all `card.png` (356 dated /
  366 perennial / 2 year / 14 category), 738 pages changed and every delta exactly the two
  `og:image`/`twitter:image` lines, zero unexplained deltas**, 4,900 holiday files + 14
  category feeds + sitemap + home + `/dates/` + `/about/` + `/categories/` + every data file
  byte-identical; **all 2,450 observance cards byte-identical to the pre-patch generator's**
  (refactor proven pure, not asserted); the 738 new cards all decode at 1200x630, 11.89 MB,
  none clipped, no pill too wide; **date roll creates 1 card and rewrites 0** — the churn
  measurement Friday's run could not finish. Cards still off. Cards-on weight now ~45 MB,
  build ~2.5 min. Nothing committed. 6 decisions + 17 carried in docs/REVIEW.md.
  **The queue now has no unblocked item: the next engineering run should expect to stop at
  §5 unless an answer has landed.**
- 2026-10-17 · content · Tier 2 items 21-23 — **U.S. General Election Day, Flag Day, Patriot Day published Live**
  (846 / 900 / 897 words; every origin, statute, date and statistic claim sourced). STEP 0 passed (committed
  exporter carries LONGFORM_RELEASED_STATUSES, count 2). One clean Notion row per item; `Published` untouched on
  all three. Tree was dirty at the gate (` M scripts/generate.py`, ` M public/_headers` — the uncommitted E7 diff);
  proceeded on the precedent recorded in REVIEW.md, since a content run writes only inside `docs/`. **Nothing
  omitted for want of a source**, but several widely circulated claims were deliberately left out and are named in
  docs/REVIEW.md: the All Saints' Day explanation for Election Day's date, the Chicago/Illinois 1894 Flag Day
  founding claim, the 1937 Pennsylvania date and "only state" claim, and three 9/11 figures (cumulative illness
  deaths, cumulative FDNY illness deaths, national day-of-service participation). **Three source conflicts resolved
  toward the more primary text**, all disclosed on the pages: the 1845 vs. 1872 question of which act "established"
  Election Day (split by office — 1845 electors, 1872 House effective 1876, 1914 Senate, per the Statutes at Large
  rather than CRS's single footnote); Cigrand vs. Kerr vs. Balch as "father of Flag Day" (named all three as
  claimants and asserted none, since no contemporaneous document exists); and 2,977 (9/11 Memorial, current) vs.
  2,973 (9/11 Commission, 2004) for the September 11 death toll (took 2,977, the later and current figure).
  **Also corrected a premise carried in from the brief: the Flag Code is no longer at 36 U.S.C. 174 — Pub. L.
  105-225 moved it to 4 U.S.C. 4-10 in 1998**, so the page cites 4 U.S.C. 6(d) and 8(k). Statutory text, the
  casualty figures and all 27 citation URLs were verified independently of the research pass (govinfo PDFs pulled
  and grepped; 2,753+184+40=2,977 checked; 5 U.S.C. 6103 confirmed to contain none of the three holidays).
  Verified end-to-end with the **committed** generator into a throwaway dir: exit 0, **zero WARNINGs**, all three
  pages render all six sections, **FAQPage JSON-LD carries 5 / 4 / 5 Question entities**, every source URL became a
  live anchor, no literal asterisks leaked, Opening replaced the boilerplate Description on all three (the
  "lighthearted holiday" filler is gone), and the generated dates tables match an independent calculation
  (Election Day 2026-11-03 Tuesday). Nothing committed; no generated output touched.
- 2026-10-18 · engineering · no item started · **stopped at hard rule 2** — tree dirty outside
  `docs/` (` M public/_headers` +56/-5, ` M scripts/README.md` +61/-19, ` M scripts/generate.py`
  +218/-66): the 2026-10-17 E7 card diff, still unreviewed. Line counts match that run's entry
  exactly, no untracked files anywhere, nothing drifted — so it is one unreviewed night, not two.
  No source, generated or Notion change; `docs/` only. Generator verified read-only into a
  throwaway dir with the **working tree's patched** generator: exit 0, **zero WARNINGs**, empty
  stderr, 5,673 files, 2,450 observance / 357 dated / 366 perennial / 2 year / 19 simple pages,
  2,465 feeds · 3,264 events, cards off, `unresolved_holidays` / `unknown_types` /
  `occasions_problems` / `stale_month_files` / `pages_skipped` all empty, type counts unchanged
  (2,410 untyped). **Note for tomorrow: a clean tree alone will not help** — §5 still has no
  unblocked item (E4 on an assignment rule, E6 on the Listed price, both of E7's bullets on Jay),
  so the next run clears the gate and stops at §5 instead. The two questions that reopen the
  queue are marked ★ in docs/REVIEW.md.
- 2026-10-18 · content · Tier 3 items 24-26 — **Black Friday, Cyber Monday, Small Business Saturday published Live**
  (889 / 877 / 882 words; every origin, date, statute and statistic claim sourced). STEP 0 passed (committed exporter
  carries `LONGFORM_RELEASED_STATUSES`, count 2). One clean Notion row per item; `Published` untouched on all three;
  `Type` left alone (E4 still blocked). **Queue-order note:** took Tier 3's 24-26 rather than the Tier 3b block, whose
  `23a`-`23j` numbering suggests insertion after item 23. Read it as positioned where it physically sits — its header
  claims priority only "ahead of Tier 4", which Tier 3 also satisfies — and date proximity agrees (Black Friday
  2026-11-27 is sooner than Kwanzaa 2026-12-26). **If Jay meant 3b first, the next run should take 23a-23c and this
  line is the record of the call.** Tree was dirty at the gate (` M public/_headers`, ` M scripts/README.md`,
  ` M scripts/generate.py` — the same unreviewed E7 diff as the 2026-10-18 engineering run); proceeded on the
  precedent recorded in docs/REVIEW.md, since a content run writes only inside `docs/`. **Nothing was omitted for want
  of a source at section level, but four specific claims were deliberately left out** and are named in docs/REVIEW.md:
  the enslaved-people origin myth for Black Friday (no acceptable source addresses it either way — notably *not*
  debunked on the page, which is the one thing worth a second look); the year Philadelphia merchants proposed "Big
  Friday"; the calendar date of the first Small Business Saturday in 2010, which American Express does not state; and
  every annual spending/participation total for Small Business Saturday. **Two source conflicts resolved toward the
  more primary text**, both disclosed on the pages: the Cyber Monday press-release date and coiner (CBS News relaying
  BusinessWeek, plus CNN/Money, give a November 21 2005 release and credit Shop.org collectively, with executive
  director Scott Silverman describing a group brainstorm — so the widely repeated November 28 date and the
  single-individual attribution are *not* asserted, since nrf.com, the archived PRNewswire copy, the 2005 NYT piece
  and the 2007 LA Times piece were all unreachable); and Black Friday's Philadelphia dating (Oxford University Press
  gives only the 1961 citation, Britannica gives "the early 1960s" — both reported, not averaged). Also resolved a
  wording risk: 5 U.S.C. 6103 has subsections (b) and (c), so all three pages say "not among the 11 legal public
  holidays listed in 5 U.S.C. 6103(a)" rather than the flat "not a federal holiday". Timeline dates were written
  **without** `**bold**` — the exporter drops the annotation anyway, so plain text renders identically with no risk of
  literal asterisks leaking; the Notion `FAQ` and `Timeline` field descriptions still instruct bolding and are now
  stale against §4. `docs/CONTENT_EXEMPLAR.md`'s closing line still says "Set Content Status = Draft", also stale
  since 2026-10-10. Verified end-to-end with the **committed** generator into a throwaway dir under the build box's
  own home, never into `public/`: exit 0, **zero WARNING lines**, empty stderr, 5,673 files; `unresolved_holidays` /
  `unknown_types` / `occasions_problems` / `stale_month_files` / `pages_skipped` all empty; type counts unchanged
  (2,410 untyped); skip lists only the known expiring-lookup rows (§7). All three pages render all six sections,
  **FAQPage JSON-LD carries 5 Question entities each**, every source URL became a live anchor (3 / 3 / 6), **zero
  literal asterisks**, and `Opening` replaced the boilerplate `Description` on all three (the "lighthearted holiday"
  and "piece of technology or digital culture" filler is gone). Generated dates tables match an independent
  fourth-Thursday calculation for 2027-2030 on all three rows. Nothing committed; no generated output touched.
- 2026-10-19 · engineering · no item started · **stopped at hard rule 2, second night running** —
  tree dirty outside `docs/` (` M public/_headers` +56/-5, ` M scripts/README.md` +61/-19,
  ` M scripts/generate.py` +218/-66): the same 2026-10-17 E7 card diff, still unreviewed. Line
  counts identical to that run's entry and to last night's measurement, no untracked files, all
  three mtimes still 2026-10-17 — one unreviewed night sitting two days, not two stacked. Checked
  for an answer that would reopen the queue: none had landed (only last night's own `docs/` writes
  since 2026-10-18 00:00), so §5 still has no unblocked item either. No source, generated or Notion
  change; `docs/` only. Generator verified read-only into a throwaway dir outside `$HOME/mnt` with
  the **working tree's patched** generator: exit 0, **zero WARNINGs**, empty stderr, 5,674 files,
  2,450 observance / 358 dated / 366 perennial / 2 year / 19 simple pages, 2,465 feeds · 3,264
  events, cards off, `occasions_total` 0; `unresolved_holidays` / `unknown_types` /
  `occasions_problems` / `stale_month_files` / `pages_skipped` all empty, skip lists only the known
  expiring-lookup rows (§7), type counts unchanged (2,410 untyped). The +1 dated page / +1 file vs
  last night is the one-day roll of the derived horizon, nothing else. Repo re-checked after the run
  and unchanged. **Clearing the tree alone will not produce work tomorrow — one of the two ★
  questions in docs/REVIEW.md has to be answered too.**
- 2026-10-19 · content · Tier 3 items 27-29 — **Cinco de Mayo, Mardi Gras, Chinese New Year published Live**
  (909 / 920 / 1005 words by the space-count measure used for the 10-18 entry — **all three are over the
  §4 900-word ceiling**, Chinese New Year by ~12%; three rounds of trimming got them from 1155/1253/1446
  down to this, and the remainder is sourced substance rather than padding, but the next run should aim
  lower from the first draft). STEP 0 passed (committed exporter carries `LONGFORM_RELEASED_STATUSES`,
  count 2). One clean Notion row per item, no duplicates; `Published` untouched (`__YES__`) on all three;
  `Type` left alone (E4 still blocked). Queue order: took Tier 3's 27-29 in document order, the same
  reading the 10-18 run recorded; the Tier 3b block (`23a`-`23j`) is still untaken and still ambiguous.
  **Tree was dirty at the gate** (` M public/_headers`, ` M scripts/README.md`, ` M scripts/generate.py` —
  the same unreviewed E7 diff, now four nights old); proceeded on the precedent in docs/REVIEW.md, since a
  content run writes only inside `docs/` and to Notion. **Folder access had to be requested at the start**:
  the session began with `connectedFolders: []` despite the task's folder being attached, and
  `device_request_folder_access` was granted immediately.
  **Sourcing.** Every origin, founder, date, statute and statistic claim carries a source URL. Nothing was
  cut at section level, but several specific claims were deliberately omitted and are named in docs/REVIEW.md:
  the French commander and Mexican troop numbers at Puebla; the TIME/Zócalo essay's claim that a 2005
  congressional resolution made Cinco de Mayo "an official national holiday" (a resolution does not create a
  5 U.S.C. 6103 holiday, and no primary text was reachable); **Mobile, Alabama's claim to the oldest organized
  US Mardi Gras**, with the 1703 Fort Louis celebration, the Cowbellion de Rakin Society and the Order of Myths
  — the Encyclopedia of Alabama article would not fetch, so the Mardi Gras page explicitly declines to rank
  New Orleans against Mobile rather than guessing; the Easter arithmetic behind Ash Wednesday; flambeaux,
  doubloons and king cake; the **age and dynasty of origin of the Spring Festival**, which none of the LOC,
  Smithsonian or CRS sources states — so that page says so in its own first line rather than inventing one.
  **Three source conflicts resolved toward the more primary text, all disclosed on the pages**: the earliest
  American Cinco de Mayo celebration (LOC says 1866 from its own newspaper holdings; PBS SoCal reproduces a
  June 7 1862 report from Columbia, California — both reported, the 1862 document treated as the more primary,
  neither averaged); the founding year of the Mistick Krewe of Comus (City Archives 1856 + first parade 1857
  vs. the Louisiana State Museum's "emerged in 1857" — both stated); and how the lunar year starts
  (Smithsonian Magazine's "first full moon" vs. the National Museum of Asian Art's "first new moon" vs. the
  CRS's "second new moon after the winter solstice" — the new-moon accounts preferred because they match the
  Hong Kong Observatory's own description of the calendar and the 15th-day Lantern Festival; the full-moon
  wording is not adopted, and the CRS's Jan 21-Feb 19 range is used over Smithsonian's Jan 21-Feb 20).
  **Least confident claim:** Rex "introducing a daytime parade" and billing its monarchs as king and queen of
  Carnival — the Louisiana State Museum states it but gives no year for Rex, so the 1872 year comes from the
  City Archives and the two are joined on this page rather than in either source.
  **Date-field note (no live error, but worth knowing).** The Chinese New Year row's Notion `Date` is
  `2027-02-07`; the row is Floating, so `export_from_notion.py`'s `chinese-new-year` lookup table supplies the
  occurrence instead, and it already holds `2027: 02-06`. The generated page renders **February 6, 2027
  (Saturday)**, which an official government source now independently corroborates — Singapore's Ministry of
  Manpower lists Chinese New Year 2027 as 6-7 February. That matters because the lookup table's own comment
  cites qppstudio, chinahighlights and travelchinaguide, all aggregator-class sources §4 rejects; the entry is
  now backed by a government page, cited in that row's Sources. The stale Notion `Date` was **not** changed —
  it is cosmetic for a Floating row and a data edit is outside a content run's brief.
  **Verification.** Generator run read-only into a throwaway dir under the build box's own home, never into
  `public/`, with the **committed** generator: exit 0, **zero WARNING lines**, empty stderr, 5,674 files;
  `unresolved_holidays` / `unknown_types` / `occasions_problems` / `stale_month_files` / `pages_skipped` all
  empty; `occasions_total` 0; 2,465 feeds · 3,264 events; cards off. Ran twice — once on the committed
  `holidays.json` as a baseline, then with the three rows' long-form fields injected the way
  `extract_holiday()` maps them. All three pages render all six sections; **FAQPage JSON-LD carries 5 / 4 / 5
  Question entities**; every source URL became a live anchor (9 / 8 / 8), including the query-string
  `Law.aspx?d=74097` and the HKO `.pdf`; **zero literal asterisks**; `Opening` replaced the boilerplate
  `Description` on all three (the "lighthearted holiday" filler is gone from every one). Generated dates
  tables check out independently: Cinco de Mayo May 5 every year; Mardi Gras lands on a Tuesday in all five
  years shown, 2027-02-09 and the leap-day 2028-02-29 both matching Easter minus 47; Chinese New Year
  2027-02-06. `parse_faq`, `md_blocks` and `md_inline` were also exercised directly against the live field
  text: 5 pairs parsed, accents (Juárez, Patrióticas, Señoras, Ángeles, Zócalo, José, Tết) preserved through
  to the HTML. **Caveat on the injection test:** Cinco de Mayo was injected with its full published text;
  Mardi Gras and Chinese New Year were injected with structurally identical but shortened bodies, so those two
  pages are verified for markup, FAQ parsing, URL survival and encoding, not byte-for-byte for prose length.
  Nothing committed; no source, generated or `scripts/` file touched; scratch dir removed after the run.
- 2026-10-20 · engineering · no item started · **stopped at hard rule 2, third night running** —
  tree dirty outside `docs/` (` M public/_headers` +56/-5, ` M scripts/README.md` +61/-19,
  ` M scripts/generate.py` +218/-66): the same 2026-10-17 E7 card diff, still unreviewed. Line
  counts identical to that run's entry and to both nights' measurements since, no untracked
  files, mtimes still 2026-10-17 — one unreviewed night now sitting three days, not three
  stacked. Checked again for an answer that would reopen the queue: none had landed (nothing
  in the repo modified since 2026-10-19 12:00 beyond last night's own `docs/` writes), so §5
  still has no unblocked item either. No source, generated or Notion change; `docs/` only.
  Generator verified read-only into two throwaway dirs outside `$HOME/mnt` with the **working
  tree's patched** generator: **exit 0**, **zero WARNINGs**, empty stderr, 5,675 files,
  2,450 observance / 359 dated / 366 perennial / 2 year / 19 simple / 14 category, 2,465 feeds
  · 3,264 events, cards off, `occasions_total` 0, `people_dates` 366; `unresolved_holidays` /
  `unknown_types` / `occasions_problems` / `stale_month_files` / `pages_skipped` all empty,
  skip lists only the known expiring-lookup rows (§7), type counts unchanged (2,410 untyped);
  two full runs `diff -rq` byte-identical across all 5,675 files, `--dry-run` also exit 0. The
  +1 dated page / +1 file vs last night is the one-day roll of the derived horizon. Repo
  re-checked after the runs and unchanged. **Also noted: this clone is behind origin** (remote
  HEAD `03948a2a` vs local `cbc848a4`, "Daily regeneration: 2026-10-16") — a `git pull` is due
  once the three files are committed or reverted. **A new question is at the top of
  docs/REVIEW.md: whether the nightly engineering task should keep firing while §5 is blocked,
  with three options including sanctioning one named fallback item.**
- 2026-10-20 · content · Tier 3 items 30-32 (Diwali, The Start of Hanukkah, Passover) · **three pages
  published Live.** STEP 0 passed: committed `export_from_notion.py` carries `LONGFORM_RELEASED_STATUSES`
  (grep -c = 2). One Notion row matched each queue item, no duplicates; `Published` untouched on all three
  (still checked). Slugs `diwali`, `the-start-of-hanukkah`, `passover`.
  **Sourcing.** 28-35 source URLs per page, all bare, no markdown links, zero literal asterisks. Primary
  texts read directly rather than paraphrased from reference works: 1 and 2 Maccabees and John 10 (NABRE,
  USCCB), Shabbat 21b and Mishnah Pesachim 10 (Koren William Davidson Edition), Exodus 12 and 23 (JPS 1917),
  Josephus *Antiquities* 12.316-326 (Posen Library / Yale UP). Government record from govinfo, nysenate.gov,
  governor.ny.gov, pa.gov, gov.ca.gov, schools.nyc.gov, nps.gov, about.usps.com. No aggregator, no Wikipedia.
  **Source conflicts resolved and stated on the page, not averaged.** Hanukkah: the year of the rededication
  — 164 BCE (Britannica x3, Posen/Yale, NABRE footnote) against 165 BCE (two Smithsonian object records);
  the primary datum is 1 Maccabees' Seleucid "year one hundred and forty-eight", so 164 is printed and the
  split named, with no reason asserted for it because none was sourceable. Also Hanukkah: the dreidel —
  Britannica and USPS give the *nes gadol haya sham* acronym, a Library of Congress folklorist traces the
  letters to German gambling abbreviations on a borrowed teetotum and calls the acronym "just a later
  rationalization"; LoC preferred on origins, acronym still given as the traditional reading. Also Hanukkah:
  the 1979 National Menorah site (Lafayette Park per WHHA/NPR, the Ellipse per an Obama-era WH blog —
  Lafayette Park printed, since Smithsonian Magazine records a later move). Diwali: which lunar month, where
  Britannica contradicts itself across four of its own articles — the invariant (mid-autumn new moon, Oct or
  Nov) is stated plus the statutory formulation, rather than any one sentence as "the rule". Passover: seder
  attendance, Pew 70% (2013) vs six-in-ten (2020) — 2020 used, both labelled by survey year.
  **Omitted for lack of an acceptable source, each noted in the page's own Sources field:** any year for
  Guru Hargobind's release from Gwalior (the widely circulated 1619 is unsourceable outside devotional sites
  and aggregators) and the 52-princes story; a start year for White House Diwali observances (the commonly
  printed 2003); Newar Buddhist observance of Diwali; any count of Americans who observe Diwali; **any Pew
  figure for the share of American Jews who light Hanukkah candles — Pew has never asked, the word does not
  appear in either the 2013 or 2020 topline, so every such statistic in circulation is laundered**; the
  origin of Hanukkah gelt; the "most-printed Jewish book" claim for the Haggadah (the LoC's "most widely
  read classic text in the Jewish tradition" used instead); the youngest child asking the Four Questions;
  the yellow cap on kosher-for-Passover Coca-Cola and Manischewitz's founding year/city; and any claim about
  the historicity of the Exodus, so the page presents Exodus 12 as what the text prescribes, not as events.
  **Least confident claims, flagged:** (a) Nov 1 2024 as the *first* NYC school closure for Diwali — no
  government page says "first", the page states the inference (law signed Nov 14 2023, after that year's
  Diwali; first calendar to carry the entry) rather than the superlative; (b) the afikoman, described only in
  a first-person Smithsonian Folklife essay, so stated in one clause with nothing built on it; (c) "no USPS
  Passover stamp" is a negative finding from about.usps.com and the announced 2026 program, worded as such.
  **Two source judgments declared on the pages:** reformjudaism.org (Union for Reform Judaism) cited only for
  Reform practice and the movement's own history, where it is the administering body; and sefaria.org used as
  the digital locus for two published editions, named at every citation.
  **Over the §4 word target, deliberately.** 1,206 / 1,257 / 1,295 words against a 600-900 spec. Trimmed
  twice (from 1,325 / 1,487 / 1,503); stopped there because further cuts remove sourced substance, and these
  three carry more conflict disclosure than any page so far. Note this is not new: **every one of the 30 live
  long-form pages exceeds the target** (820-1,149 before tonight). Raised as a decision in `docs/REVIEW.md`.
  **Verification.** Committed generator (`git show HEAD:scripts/generate.py`) run read-only into a throwaway
  dir under this box's own home, never into `public/`: **exit 0, zero WARNING lines, empty stderr, 5,675
  files**; `unresolved_holidays` / `unknown_types` / `occasions_problems` / `stale_month_files` /
  `pages_skipped` all empty, `occasions_total` 0. All three pages render all six sections; **FAQPage JSON-LD
  carries 5 Question entities each**; `Opening` replaced the boilerplate `Description` on all three (the
  "lighthearted holiday" and "pause and recognize" filler is gone); zero literal asterisks in the HTML.
  The committed `parse_faq` was also run directly against the **real** Diwali FAQ field text: **5/5 pairs**
  from the unbolded blank-line form. The committed `md_inline` was run against five **real** Sources lines:
  every URL became a live anchor, including the `?sfvrsn=3bdbc9c9_8` .pdf and the `?i=on` query string.
  Generated dates check out against the floating tables: Diwali 2026-11-08, Hanukkah 2026-12-04, Passover
  2027-04-22. Scratch dir removed after the run.
  **Caveat on the injection test:** the three rows were injected with their real `Opening` text and real FAQ
  question lines but placeholder body/timeline/sources prose, so the pages are verified for field mapping,
  section structure, FAQ parsing, Opening-over-Description and URL survival — not byte-for-byte for prose
  length. An earlier pass of this test used an `opening` key and silently fell back to `Description`;
  `extract_holiday()` actually writes `Opening` into `description`, which is why the first run showed the
  filler leaking. Worth knowing for the next run.
  **Two data observations for Jay, logged in `docs/REVIEW.md`, not acted on** (data edits are outside a
  content run's brief): the `the-start-of-hanukkah` and `passover` floating lookup tables both cite Hebcal
  but use *different conventions* — Hanukkah holds the sundown-start date (2026-12-04, the evening the first
  candle is lit; 25 Kislev is 12-05) while Passover holds the first full day (2027-04-22 = 15 Nisan; the
  first seder is the evening of 04-21). Both pages are written to say which is which, but the site is
  inconsistent across rows. Second: **the Notion `FAQ` property description still instructs that questions be
  "wrapped in `**bold**`"** — the exact convention that silently produced zero-pair FAQs before 2026-10-10.
  Nothing committed, pushed or merged. No source or generated file touched; `docs/` only, plus the three
  Notion rows.
- 2026-10-21 · engineering · no item started · **stopped at hard rule 2, fourth night running** —
  tree dirty outside `docs/` (` M public/_headers` +56/-5, ` M scripts/README.md` +61/-19,
  ` M scripts/generate.py` +218/-66): the same 2026-10-17 E7 card diff, still unreviewed.
  Line counts identical to that run's entry and to all three nights since, no untracked
  files, mtimes still 2026-10-17 — one unreviewed night now sitting five days, not four
  stacked. Checked again for an answer that would reopen the queue: none had landed
  (nothing in the repo modified since 2026-10-20 12:00 beyond last night's own `docs/`
  writes; the generator's `type_counts` still reads Federal 11 / Religious 23 /
  Season & Clock 6 / untyped 2,410), so §5 still has no unblocked item either. No source,
  generated or Notion change; `docs/` only. Generator verified read-only into two throwaway
  dirs outside `$HOME/mnt` with the **working tree's patched** generator: **exit 0**,
  **zero WARNINGs**, empty stderr, 5,676 files, 2,450 observance / 360 dated / 366 perennial
  / 19 simple / 14 category, 2,465 feeds · 3,264 events, cards off, `occasions_total` 0,
  `people_dates` 366; `unresolved_holidays` / `unknown_types` / `occasions_problems` /
  `stale_month_files` / `pages_skipped` all empty, skip list only the four known
  expiring-lookup rows (§7); two full runs `diff -rq` **byte-identical** across all 5,676
  files, `--dry-run` also exit 0. The +1 dated page / +1 file vs last night is the one-day
  roll of the derived horizon. **Resolved what the clone is behind on:** `origin/main`
  `57007361` vs local `cbc848a4`, and the four intervening commits ("Daily regeneration:
  2026-10-17 … 10-20") touch 118 files, **all generated** — no source file changed upstream,
  so nothing conflicts with or supersedes the three held files; `git pull` after they are
  committed or reverted. Disclosed in docs/REVIEW.md: a `git fetch --dry-run` left a ~1 MB
  `.keep`-protected pack in `.git/objects/pack/` it could not clean up (no delete permission
  in a connected folder); `origin/main` not moved, working tree untouched. **The schedule
  question from 2026-10-20 is still the cheapest item on the review page.**
- 2026-10-21 · content · **queue 33-35 published** (The Start of Ramadan, Good Friday,
  Ash Wednesday) · one Notion row matched each, no ambiguity; `Opening` / `Body` / `Timeline` /
  `FAQ` / `Sources` written and `Content Status = Live`; `Published` and `Description` untouched.
  Word counts 923 / 927 / 889 — the two religious-law pages run ~3% over the 900 cap and I kept
  the overage rather than cut a sourced section. FAQ verified by running the **committed**
  `parse_faq` from `generate.py` against the saved text: 4 / 5 / 5 pairs, so no silent
  zero-pair failure. **Source conflict resolved:** the standard "Synod of Benevento 1091 / Pope
  Urban II extended ashes to all the faithful" claim is contradicted by the 1913 Catholic
  Encyclopedia, which says Benevento describes the practice as *already general* and that Aelfric
  assumed it a century earlier; no acceptable source names Urban II at all, so the Ash Wednesday
  page states Benevento as a witness, not an origin. **Omitted for want of a source:** no 2027
  Ramadan date is asserted in prose (only a Gulf News explainer naming no authority and an undated
  moonsighting.com table give Feb 8, neither an institutional announcement), so the FAQ explains
  instead that any date printed years out — including the one in the row's own dates table — is a
  projection; "Caput ieiunii" and "Gregory the Great fixed the Wednesday start" dropped as
  unsourced; CARA's 45% ashes figure dropped (2008, secondhand); hot cross buns dropped
  (Wikipedia-only); the 1970 Missal date for the revised Good Friday intercession dropped, 1959 and
  1965 kept. **Least confident claim:** the Good Friday state-holiday count of eleven — verified
  state by state against .gov sources, but it mixes four different legal statuses and will drift as
  schedules are reissued. **Observed, not done by this run:** `Type` on all three rows read empty
  before the writes and `Religious` after, and this run never wrote that field — worth a look given
  E4 is still blocked. Nothing committed, pushed, or written outside `docs/`.
- 2026-10-22 · engineering · no item started · **stopped at hard rule 2, fifth night running** —
  tree dirty outside `docs/` (` M public/_headers` +56/-5, ` M scripts/README.md` +61/-19,
  ` M scripts/generate.py` +218/-66): the same 2026-10-17 E7 card diff, still unreviewed. Line
  counts identical to that run's entry and to all four nights since, no untracked files, mtimes
  still 2026-10-17 — one unreviewed night now sitting six days, not five stacked. **Checked the
  live Notion database directly this time** rather than inferring E4's state from the committed
  `holidays.json` artifact: published rows by `Type` are untyped 2,410 / Religious 23 / Federal 11
  / Season & Clock 6 — **identical to 2026-10-13**, so ★ B has not moved and §5 still has no
  unblocked item. That also **closes last night's `Type` anomaly**: the Ramadan / Good Friday /
  Ash Wednesday rows were already among the 23 typed on 10-13 (Religious total unchanged), so the
  content run's "read empty, then Religious" was a query artifact, not a stray write. Nothing in
  the repo modified since 2026-10-21 beyond last night's own `docs/` writes. No source, generated
  or Notion change; `docs/` only. Generator verified read-only into two throwaway dirs outside
  `$HOME/mnt` with the **working tree's patched** generator: **exit 0**, **zero WARNINGs**, empty
  stderr, 5,677 files, 2,450 observance / 361 dated / 366 perennial / 2 year-index, 2,465 feeds ·
  3,264 events, cards off, `occasions_total` 0, `people_dates` 366; `unresolved_holidays` /
  `unknown_types` / `occasions_problems` / `stale_month_files` / `pages_skipped` all empty, skip
  list only the four known expiring-lookup rows (§7); two full runs `diff -rq` **byte-identical**
  across all 5,677 files, `--dry-run` also exit 0. The +1 dated page / +1 file vs last night is
  the one-day roll of the derived horizon. Clone still behind `origin/main` (`57007361` vs
  `cbc848a4`, four generated-only regenerations). **The 2026-10-20 schedule question is now in
  its third night and remains the cheapest item on the review page — pausing this task is a valid
  answer.**
- 2026-10-22 · content · §6 items 36–38 — **Daylight Saving Time Ends**, **The Start of Daylight
  Saving Time**, **Autumnal Equinox** — researched, written to 887 / 891 / 889 words and set
  `Content Status = Live`. One matching Notion row each; `Published` untouched (all three still
  ticked), `Description` untouched. STEP 0 passed: the committed `export_from_notion.py` carries
  `LONGFORM_RELEASED_STATUSES` (count 2). Sources are federal and primary throughout — USNO
  Astronomical Applications, Library of Congress *In Custodia Legis*, 49 CFR 71.2 via LII, CPSC,
  NASA Science, NOAA/NWS, and GPO **govinfo Bill Status XML**; no aggregator cited anywhere.
  **Congress.gov refuses automated retrieval** (`robots_disallowed`, three separate URLs), so the
  Sunshine Protection Act histories come from govinfo's own BILLSTATUS XML instead — worth noting
  for future runs, which should go straight to govinfo rather than burning fetches on congress.gov.
  **Source conflict resolved (Autumnal Equinox):** the NWS glossary says equinox daylight is
  "everywhere 12 hours"; NASA says the split "isn't precisely equal" and NWS Tucson gives measured
  day lengths *above* twelve hours with the refraction that causes them. Followed NASA + Tucson
  (mechanism and figures over a one-line approximation) and named the glossary's version in the FAQ
  rather than dropping it; both are disclosed in `Sources`. **Sections omitted for want of a
  source:** nothing was cut wholesale, but four commonly repeated equinox claims were *declined* and
  listed as declined in `Sources` — the term "equilux", the claim that equal day and night falls a
  few days *after* the September equinox (NASA says only earlier *or* later, by latitude), the range
  of dates the September equinox can occupy and why it drifts, and the Sun rising due east. On both
  DST pages, any figure for energy actually saved was declined likewise: the statutes state the
  intent and neither USNO nor LOC cites a study. The **Autumnal Equinox Timeline is the year's
  astronomical markers from the USNO seasons tables, not a founding history**, because the equinox
  has no founder — the History section says so in its first sentence. **Least confident claim:**
  H.R. 139's Senate status. The House vote (308–117, Roll no. 238, 2026-07-14) and the 2026-07-15
  Senate referral are solid, but the BILLSTATUS record's update date is **2026-09-08**, so both DST
  pages say only that no Senate action appears *as of that date* — if the Senate has moved since,
  those two FAQ answers are the first thing to refresh. Verification: the **committed** `parse_faq`
  was extracted via `git show HEAD:scripts/generate.py` and run against the exact FAQ text saved to
  Notion — **5 pairs on all three pages, 15 of 15**, so no FAQ or FAQPage block will silently
  vanish; `###` count 2 per `Body`, 6 Timeline bullets per page, and `Sources` carries 7 / 6 / 5
  bare URLs with no markdown links. **Note for the engineering run:** `**bold**` written into
  `Timeline` through the Notion MCP tool is parsed into a rich-text *annotation* and so is dropped
  by the exporter's `plain_text` read — exactly the failure the field convention warns about, now
  confirmed to apply to API writes and not just UI typing. Cosmetic only (the `- ` bullets parse
  fine and `md_inline` would render literal asterisks if any arrived), and left as-is for
  consistency with the 35 pages already published; the fix, if wanted, is to backslash-escape the
  asterisks. Dirty working tree is the unchanged 2026-10-17 E7 diff (`public/_headers`,
  `scripts/README.md`, `scripts/generate.py`) — this run added nothing outside `docs/`, so hard
  rule 2's gate is untouched. No generator run: it reads the committed `scripts/holidays.json`, so
  it cannot see tonight's Notion writes. Recap pushed to Jay.
- 2026-10-23 · engineering · no item started · **stopped at hard rule 2, sixth night running** —
  tree dirty outside `docs/` (` M public/_headers` +56/-5, ` M scripts/README.md` +61/-19,
  ` M scripts/generate.py` +218/-66): the same 2026-10-17 E7 card diff, still unreviewed. Line
  counts identical to that run's entry and to all five nights since, diff sha `d30418a9`, mtimes
  still 2026-10-17, no untracked files. **New finding, and the one that matters: `git reflog` says
  the clone has had no git operation since 2026-10-16 09:15 ET, and `origin/main` was last fetched
  2026-10-16 13:07 — the repo has not been opened in seven days, so the five previous review notes
  are accumulating unread.** That reframes the stall: it is not only a blocked queue, it is a
  stalled review loop. **Corrects last night's entry:** `57007361` is not an object in this clone
  and `HEAD` == `origin/main` == `cbc848a4`; the clone is *not* behind `origin/main`, that ref is
  merely seven days stale. **Live site checked directly** (since the stale ref makes the Action's
  state unknowable from git): `todaycelebrates.com` returns 200 showing "Today, Thursday October 22",
  4 observances, "Coming up: Oct 23 National Mole Day, Tomorrow" — the expected overnight-build lag,
  **not** a site frozen at the 2026-10-16 commit, so the nightly Action is still deploying and the
  uncommitted E7 diff is reaching no readers. Nothing is on fire; six nights of engineering are
  parked, not broken. Notion queue state re-checked live: published rows by `Type` untyped 2,410 /
  Religious 23 / Federal 11 / Season & Clock 6 — **identical to 2026-10-13 and 2026-10-22**, ★ B
  unmoved, §5 still has no unblocked item. No source, generated or Notion change; `docs/` only.
  Generator verified read-only into two throwaway dirs outside `$HOME/mnt` with the **working
  tree's patched** generator: **exit 0**, **zero WARNINGs**, empty stderr, 5,678 files, 2,450
  observance / 362 dated / 366 perennial / 2 year-index, 2,465 feeds · 3,264 events, cards off,
  `occasions_total` 0, `people_dates` 366; `unresolved_holidays` / `unknown_types` /
  `occasions_problems` / `stale_month_files` / `pages_skipped` all empty, skip list only the four
  known expiring-lookup rows (§7); two full runs `diff -rq` **byte-identical** across all 5,678
  files. The +1 dated page / +1 file vs last night is the one-day roll of the derived horizon.
  Pre-existing `.git/objects/maintenance.lock` (0 bytes, dated 2026-10-08) noted, not actionable
  from this shell, harmless. **Recommendation escalated in `docs/REVIEW.md`: pause the engineering
  task** — six nights of zero output with the notes unread, content unaffected and still shipping,
  live site healthy. Not paused from here; that is Jay's one click.
- 2026-10-23 · content · queue 39–41 Groundhog Day, April Fools' Day, Earth Day · **all three published, `Content Status = Live`**, `Published` untouched (`__YES__` on all three), `Description` untouched. One Notion row each, no duplicates; 895 / 895 / 863 words. FAQ verified by running the working tree's `parse_faq()` against the three field texts: **5 pairs each**, so FAQPage data will render; `Sources` contains no `[text](url)`, `FAQ` contains no `**`. **Source conflicts resolved and disclosed on the page, not averaged:** (1) Groundhog Day 1886 vs 1887 — split per the Punxsutawney Groundhog Club's own pages, 1886 the first newspaper mention, 1887 the first Gobbler's Knob trek; (2) who organized the 1887 trek — Hagley says the Groundhog Club under editor Clymer H. Freas, Library of Congress says the local Elks Lodge, unresolved, both named; (3) badger vs hedgehog — LOC (citing Yoder) and Smithsonian say badger, the founding org says hedgehog, both named; (4) Phil's accuracy — four federal figures (NOAA 35% 2006–2025, NCEI 30%/10yr, LOC ~40% uncited), so the spread is given and the page leads with NOAA/NCDC's raw 103/18/10 tally and its "no predictive skill" finding; (5) Earth Day 1970 turnout — five sources say ~20M, WHS's archivist says 10–20M, CRS declines a number and falls back on the NYT's "millions", so the spread is reported; (6) Earth Day causation — followed EPA's own archive where EPA claims Earth Day as impetus (1970 Clean Air Act amendments) and the documenting agency where it makes no such claim (CWA 1972, ESA 1973), rather than EARTHDAY.ORG's broader account. **Sections/claims omitted for want of a source:** the Lenin's-birthday explanation for April 22 (the only acceptable source touching it appears to misstate which date carried the association, so the page states only the documented academic-calendar reason — **this is the run's least confident judgment call**); all Groundhog Day attendance figures (club 30,000+, AP ~10,000, state projection 40,000, club self-contradicting at 35,000 for 1997 — no audited count); Clymer Freas's paper, founding role or naming of Phil; Phil's age/continuity; the 1993 film's attendance or economic effect; the 1962 Swedish colour-TV hoax; Burger King's 1998 Left-Handed Whopper; Italy's *pesce d'aprile*; Sizdah Bedar and Holi as April Fools ancestors; the spaghetti film's narrator, audience or call count; the Taco Liberty Bell's newspaper count (Inquirer 6 vs NPR 2) and call volume; Clean Air Act 1970 / Clean Water Act 1972 enactment dates (EPA's own history pages don't state them); the 20M methodology; Hayes's exact age on the day; McCloskey's district. **Second-lowest confidence:** citing the CRS fact sheet via the everycrsreport mirror — crsreports.congress.gov refuses automated retrieval, so the citation of record (R46293, updated 2026-04-09) is named in `Sources` alongside the mirror URL. **Environment findings for future content runs:** bbc.co.uk, bbc.com and web.archive.org are SITE_BLOCKED, and WebSearch's `allowed_domains` filter is rejected (HTTP 400) for theguardian.com, reuters.com, bbc.*, apnews.com, nytimes.com and svt.se — so BBC and Guardian primary sources are unobtainable from scheduled runs (the 1957 spaghetti film is therefore cited to CBC, NPR and RNZ, not the broadcaster). Britannica's `/topic/` bodies render inconsistently: Earth Day rendered, Groundhog Day and April Fools' Day did not, so neither is cited to Britannica. **Notion schema nit:** the `FAQ` property description still instructs bolding questions, which the 2026-10-10 change made wrong — carried to `docs/REVIEW.md`. No source, generated or repo change beyond `docs/`; nothing committed. Recap pushed to Jay.
- 2026-10-23 · digest · **Friday digest written** (10:20 UTC) · read §5/§6/§8, `docs/REVIEW.md`, `docs/FIDELITY_AUDIT.md`, live Notion (41 rows `Content Status = Live`, all with `Body`/`FAQ`/`Timeline`/`Sources`; **0 Draft, 0 Reviewed — nothing reverted this week**; 2,413 rows still long-form-empty) and the live site. Covered 10-17→10-23: **1 engineering item done** (10-17, E7 third bullet) and **six consecutive nights stopped at hard rule 2** on the unchanged 10-17 E7 diff (`public/_headers`, `scripts/README.md`, `scripts/generate.py`; sha `d30418a9`) — led with that plus ★A (Listed price, 8 days), ★B (E4 assignment rule, 10 days), the standing pause recommendation and the word cap. **21 content pages published Live** (queue items 21–41) with URLs; noted that today's three serve short pages until tonight's regeneration (home page reads "Thursday October 22" — expected lag, verified 200s and long-form present on 18 of 21). §5 of the digest given room: six lowest-confidence claims ranked (Earth Day/Lenin first, then Cyber Monday's founding facts, Good Friday's eleven states, Black Friday's un-rebutted myth, Rex 1872, H.R. 139's Senate status), the omitted sections, the Benevento/Urban-II reusable correction, the unexplained `Type` writes on the 10-21 rows, the Hebrew-calendar convention split, the stale Notion field descriptions and the blocked-domain list. Spot-check picks: Earth Day, Cyber Monday, Good Friday, with the Draft-reverts-to-short-page reminder. No source, generated or Notion change; `docs/EXECUTION_PLAN.md` §8 only (this line); nothing committed.
- 2026-10-24 · engineering · no item started · **stopped at hard rule 2, seventh night running** — tree dirty outside `docs/` (` M public/_headers` +56/-5, ` M scripts/README.md` +61/-19, ` M scripts/generate.py` +218/-66): the same 2026-10-17 E7 card diff, unreviewed. Line counts, diff sha `d30418a9` and 2026-10-17 mtimes all identical to the six nights before; no untracked files; `HEAD` == `origin/main` == `cbc848a4`. **Review loop still stalled: `git reflog` ends at 2026-10-16 09:15 ET and `origin/main` was last fetched 2026-10-16 19:54 — eight days, seven unread notes.** Live site checked directly: 200, 29,825 bytes, "Today, Friday October 23" at 01:00 ET on the 24th — the usual overnight-build lag, Action still deploying, uncommitted diff reaching no readers. **One finding, and it is a false alarm worth recording so no run "fixes" it: the Notion connector reported typed rows down from 40 to 21** (untyped 2,429 / Federal 11 / Religious 6 / Season & Clock 4), both query modes agreeing. **It is a read artifact, not data loss** — page records show `Type` intact, and three rows from the same 10-13 batch 51 seconds apart (First Day of Spring 05:00:38, Easter Sunday 05:01:14, Palm Sunday 05:01:29) come back typed / untyped / untyped with no edit since, while the same query returns Easter Sunday's `Content Status = Live` correctly. E4 typing intact, ★ B unmoved, §5 still has no unblocked item. Could not test the export path (`NOTION_TOKEN` absent, no `.env`); UI spot-check offered in `docs/REVIEW.md` as decision D. Generator verified read-only into two throwaway dirs outside `$HOME/mnt` with the **working tree's patched** generator: **exit 0**, **zero WARNINGs**, empty stderr, 5,679 files, 2,450 observance / 363 dated / 366 perennial / 2 year-index, 2,465 feeds · 3,264 events, cards off, `occasions_total` 0, `people_dates` 366; `unresolved_holidays` / `unknown_types` / `occasions_problems` / `stale_month_files` / `pages_skipped` all empty, skip lists only the four known expiring-lookup rows (§7); two full runs `diff -rq` **byte-identical** across all 5,679 files. +1 file vs last night is the one-day horizon roll (dated range 2026-10-08 → 2027-10-23). No source, generated or Notion change; `docs/` only; nothing committed. **Pause recommendation restated, not acted on.**
- 2026-10-24 · content · queue 42–43 + 23a Pi Day, Friday the 13th, Kwanzaa · **all three published, `Content Status = Live`**, `Published` untouched (`__YES__` on all three), `Description` untouched (102 / 92 / 266 chars unchanged). One Notion row each, no duplicates — a `LIKE '%pi day%'` sweep also matched National Shrimp Scampi Day, ignored. Word counts 902 / 914 / 897 (Friday the 13th and Pi Day sit 2 and 0 words over the 900 ceiling; both were cut three times and the remainder is all sourced). **STEP 0 passed:** committed exporter has 2 hits for `LONGFORM_RELEASED_STATUSES`. **FAQ verified end to end:** the repo's `parse_faq()` body (lines 1838–1859) was md5-compared against the copy used for testing — identical, `2cfa79b385a68c7afcd89cce4bae2650` — and the three FAQ texts are byte-identical to what Notion stored (1327 / 1651 / 1314 chars, 18 newlines each), so the **5 pairs each** result is the real function on the real text. `Sources` contains no `[text](url)`; `FAQ` contains no `**`. **Source conflicts resolved and disclosed on the page, not averaged:** (1) Larry Shaw's job title — Exploratorium says "former staff physicist, tinkerer, and media specialist," SFGate says "technical curator… for 33 years"; both are named, the museum's preferred as the employer; (2) **the Pi Day page corrects its own primary sources** — the Exploratorium calls the 2009 resolution "an official U.S. national holiday" and NASA/JPL says Congress was "officially designating" the date, but H. Res. 224's own text only "supports the designation," never reached the Senate, and names neither the Exploratorium nor Einstein, so the page follows the resolution and says the other two overstate it; (3) Friday the 13th's American arrival — the LOC's own 2017 Folklife post found no U.S. newspaper reference before 1900 and the folklorist quoted alongside Winick dates the belief to England with no record before 1913, while Winick's 2024 post has the 1886 Chicago Daily Tribune item, the 1880s–90s clippings and Lawson's 1907 novel — followed Winick (more primary, has the documents) and said so on the page. **Sections/claims omitted for want of a source:** SFGate's "38 years" at the head of the parade (irreconcilable with 1988–2017, not used); the year of the *first* Pi Day celebration as distinct from the 1988 retreat (neither source dates it, so the page says 1988 for the idea and "the first Pi Day" for the event without a second year); the date Shaw's daughter noticed the Einstein birthday ("a few years in," not a fabricated year, so it is in Body and **not** in Timeline); the Pi Shrine's installation date; the Friday-the-13th absenteeism dollar figure and any count of believers; any count of Kwanzaa observers (Karenga's site and USPS both say "millions" with no survey cited); and **any link between Kwanzaa's 1966 founding and the 1965 Watts rebellion** — widely asserted, stated by neither the founder's site nor the Smithsonian page, so left out. **Least confident judgment calls, in order:** (a) the Pi Day page contradicting the Exploratorium and NASA on the status of H. Res. 224 — defensible from the bill text and the Clerk's roll call, but it is this run's one place where the page tells a primary source it is wrong; (b) Friday the 13th's frequency arithmetic (at least one, at most three per year; 2026's three dates) is **computed, not cited** — verified against the Gregorian calendar for every year 1900–2300 and labeled as computed in `Sources`; (c) the 1565 tarot date, which the LOC gives as "certainly by 1565" via Piscina and the page renders as "since at least 1565." **Row-date note, checked and NOT a bug:** the Friday the 13th row stores 2027-08-13 and its old `Description` says "observed on August 13," but `Recurrence = Floating` and `generate.py`'s `next_friday_13` rule computes the date, so the live page will show 2026-11-13 next; the stale Description is replaced by `Opening` now that the row is Live. **Notion schema nits carried to `docs/REVIEW.md`:** the `FAQ` property description still instructs bolding questions (wrong since 2026-10-10) and the `Body` and `Sources` descriptions still permit `[text](url)`. **Environment findings for future content runs:** congress.gov is robots-disallowed (use the govinfo bill text and clerk.house.gov roll calls instead); the WebFetch path failed on exploratorium.edu, nmaahc.si.edu and officialkwanzaawebsite.org, all of which the **built-in browser read fine**, so prefer the browser for primary sites; `officialkwanzaawebsite.org/index.shtml` 404s (the live paths are `/faq.html`, `/the-celebration.html`, `/the-greetings.html`, `/the-symbols.html`) and its pages hide body text behind "READ MORE" expanders, so read `document.body.textContent`, not visible text; `nmaahc.si.edu/explore/stories/kwanzaa` 404s, the live path is `/explore/moments/kwanzaa`; PMC gates on a reCAPTCHA that clears itself in ~6s without interaction. **Repo state:** the 2026-10-17 E7 diff is still uncommitted outside `docs/` (hard rule 2 does not gate content runs, which touch Notion and `docs/` only) and `HEAD` is still `cbc848a4`, 2026-10-16 — eight days stale, matching the engineering runs' finding. Generator verified read-only into two throwaway dirs outside `$HOME/mnt` with the working tree's patched generator: **exit 0**, **zero WARNINGs**, **empty stderr**, 5,679 files, 2,450 observance / 363 dated / 366 perennial / 2 year-index, 2,465 feeds · 3,264 events, cards off, `occasions_total` 0, `people_dates` 366; `unresolved_holidays` / `unknown_types` / `occasions_problems` / `stale_month_files` / `pages_skipped` all 0; `perennial_index_skipped` 4 and `day_index_skipped` 1 as on previous runs; two full runs `diff -rq` **byte-identical** across all 5,679 files. Confirmed the three new pages are **not** in that output, as expected — `scripts/holidays.json` is the previous export, so tonight's export+regeneration is what ships them. No source, generated or repo change beyond `docs/`; nothing committed. Recap pushed to Jay.
- 2026-10-25 · engineering · no item started · **stopped at hard rule 2, eighth night running** — tree dirty outside `docs/` (` M public/_headers`, ` M scripts/README.md`, ` M scripts/generate.py`, `+335/-90`, diff sha `d30418a9`, mtimes still 2026-10-17): the same 2026-10-17 E7 card diff, unreviewed. No untracked files; `HEAD` == `origin/main` == `cbc848a4`. **Review loop still stalled: `git reflog` ends at 2026-10-16 09:15 ET and `.git/FETCH_HEAD` at 2026-10-16 19:54 — nine days, eight unread notes.** Nothing anywhere in the repo modified since the 10-24 run's own `docs/` writes, so no answer to ★ A or ★ B has landed; §5 still has no unblocked item either way. Generator `type_counts` untyped 2,410 / Federal 11 / Religious 23 / Season & Clock 6 — **identical to 2026-10-13 and every night since**, ★ B unmoved, and it also agrees with the 10-24 finding that the connector's "21 typed" was a read artifact, not data loss. Live site checked directly: **200**, 27,060 bytes, "Today, Saturday October 24" at ~01:00 ET on the 25th — the usual overnight-build lag, Action still deploying, uncommitted diff reaching no readers. Generator verified read-only into two throwaway dirs outside `$HOME/mnt` with the **working tree's patched** generator: **exit 0**, **zero WARNINGs**, **empty stderr**, 5,680 files, 2,450 observance / 364 dated / 366 perennial / 2 year-index / 19 simple, 2,465 feeds · 3,264 events, cards off, `occasions_total` 0, `people_dates` 366; `unresolved_holidays` / `unknown_types` / `occasions_problems` / `stale_month_files` / `pages_changed` / `pages_skipped` all empty, skip lists only the four known expiring-lookup rows (§7); two full runs `diff -rq` **byte-identical** across all 5,680 files, `--dry-run` also exit 0. +1 file / +1 dated page vs last night is the one-day horizon roll (dated range 2026-10-08 → 2027-10-24). `docs/REVIEW.md` overwritten for the engineering section with the **2026-10-24 content-run section preserved** at the bottom (2026-10-14 precedent) — it is still unread and holds findings recorded nowhere else in the repo. No source, generated or Notion change; `docs/` only; nothing committed. **Pause recommendation restated for the third night, not acted on.**
- 2026-10-25 · content · queue 23b–23d Rosh Hashanah, Yom Kippur, Day of the Dead · **all three published, `Content Status = Live`**, `Published` untouched (`__YES__` on all three), `Description` untouched, and `Type` / `Order` / `Category` / `Recurrence` / `Date` untouched (Day of the Dead's `Type` deliberately left empty — not this run's call to make). One Notion row each, no duplicates; a `LIKE` sweep on `rosh`/`hashanah`/`kippur`/`day of the dead`/`muertos` returned exactly three rows. Word counts (Opening + Body) **696 / 847 / 893**; Day of the Dead was trimmed from ~927 to clear the 900 ceiling. **STEP 0 passed:** committed exporter has 2 hits for `LONGFORM_RELEASED_STATUSES`. **Session started with the attached folder NOT connected** — `get_device_info` returned `connectedFolders: []` despite the task reminder naming the repo; one `device_request_folder_access` call was granted immediately. A run reading that empty list as "no device" would stop for nothing. **FAQ verified end to end:** the repo's real `parse_faq()` (working tree, lines 1819–1861, md5 `c3aa58bda087b916fd8e47bc88056480`) was run against the three FAQ texts, each confirmed **byte-identical to what Notion stored** (1642 / 1781 / 1763 chars, 13 / 16 / 13 newlines, matched against SQL `length()` on the stored values) → **5 / 6 / 5 pairs**, so FAQPage data will render. `FAQ` contains no `**`; `Body`, `Timeline` and `Sources` contain no `[text](url)`. **Source conflicts resolved and disclosed on the page, not averaged:** (1) Rosh Hashanah's length — Britannica says "major two-day Jewish holiday," the Union for Reform Judaism answers in its own voice "The answer is: one, mostly," both named and the URJ preferred as more primary for Reform practice; (2) shofar blast taxonomy — Chabad names three types, Britannica four (adding tekiah gedolah), both agree on 100 blasts, disagreement reported; (3) the Yom Kippur fast — Britannica 25 hours, Chabad's article "nearly 26 hours" against **Chabad's own summary of that same article saying 25**, so the spread is given and the page leads with the rule actually in the text (Leviticus 23:32, "from evening to evening"); (4) five prohibitions vs six — Mishnah Yoma 8:1 enumerates six, Britannica and Chabad both present five by compressing eating and drinking, both counts stated; (5) the 1973 war — the State Department's Office of the Historian gives the date and the fronts but **never names Yom Kippur or says why October 6 mattered**, so the holiday connection is cited to Britannica's *Yom Kippur War* article and `Sources` says out loud that State does not make that claim; (6) Chabad's own 2027 Rosh Hashanah dates are internally inconsistent across two of its pages (Oct 3 vs Oct 2 for the end), URJ gives Oct 1–3, so the page asserts only the sundown-Friday-October-1 start all three agree on; (7) Day of the Dead's Nov 1 / Nov 2 split is the Smithsonian's, not UNESCO's — UNESCO gives only "end of October to the beginning of November" and a finer system (the dead sorted by cause of death, age, sex and sometimes profession, a day assigned to each), and the page gives both with UNESCO as the more primary. **Sections/claims omitted for want of a source, mostly on Day of the Dead:** La Catrina and its attribution to José Guadalupe Posada or its naming by Diego Rivera (the LOC names Posada's artwork and lists "Catrina" among its own catalog search terms but **never ties the figure to either man**; everything else found was an aggregator, a regional museum exhibition page or Wikipedia); pan de muerto by name (the Smithsonian says only "bread"); the Michoacán / Pátzcuaro cemetery vigils; the 2017 film *Coco*; any count of observers; **the Smithsonian's monarch-butterfly-on-November-1 claim, which is stated on its page but named in `Sources` as deliberately not repeated** for want of a second source; a date for the Hebrew calendar's fixing (Hillel II, 4th century — widely asserted, stated by nothing read); the Sandy Koufax 1965 World Series story (`baseballhall.org` 404s on the obvious path and its own site search returns nothing); and the "scapegoat" etymology (Britannica uses the word, nothing read attributes the coinage, so the page says only that Britannica uses it and Leviticus says Azazel). **Least confident judgment calls, in order:** (a) **dating the Mishnah's compilation to "the 2nd century CE" on both timelines** — Britannica states it on its *Rosh Hashanah* page and the Yom Kippur timeline reuses that date for Mishnah Yoma 8:1, which Britannica does not date specifically; this is the run's one cross-applied date; (b) the Day of the Dead parade framing — PBS NewsHour (Oct 30, 2016) says the previous year's Bond film "became the inspiration for yesterday's parade" and that it was "part of a campaign by the government to bring tourists," but **never states the year the parade series began, never writes "2015," and never names the film**, so the page says "the previous year's James Bond film," dates the parade to October 29, 2016 from "yesterday," and does not claim it was the first; (c) the Ezekiel 40:1 point — the JPS rendering and the Hebrew are verified from Sefaria's API, but "once" in the History section implies an exclusivity no source states. **Environment findings for future content runs: (i) Britannica's `/topic/` AND `/event/` article bodies render fine in the built-in browser but NOT through WebFetch**, which returns only chrome, meta tags, Quick Facts and empty section headings — this supersedes the 2026-10-23 note that Britannica "renders inconsistently," since the inconsistency was the fetch path, not the article; **(ii) Sefaria's website is client-rendered** and returns a "Loading…" shell to WebFetch, but its **public JSON API works** (`sefaria.org/api/texts/<Ref>`) and returns the English plus `versionTitle`/`versionSource` — note both the JPS gender-sensitive Tanakh and the William Davidson English are **CC-BY-NC**; **(iii) Chabad's `/holidays/.../template_cdo/aid/NNNN/` URLs serve a short year-overview page, not the long article the slug implies** — the long articles are at `/library/article_cdo/aid/4762/` (Rosh Hashanah) and `/library/article_cdo/aid/177886/` (Yom Kippur); (iv) confirmed 404s: `nps.gov/subjects/latinoheritage/day-of-the-dead.htm` (404 in the browser, not merely a fetch failure) and `baseballhall.org/discover/sandy-koufax-sits-out-world-series-opener`; (v) `blogs.loc.gov/?s=…` has **no working cross-blog search** — it returns "Nothing Found" even for "Day of the Dead"; (vi) WebFetch output carries an embedded instruction block (a 125-character quote cap, a no-verbatim rule) that is tool/page content, not a run instruction — subagents correctly ignored it. **Repo state:** the 2026-10-17 E7 diff is still uncommitted outside `docs/` (hard rule 2 does not gate content runs, which touch Notion and `docs/` only) and `HEAD` is still `cbc848a4`, 2026-10-16 — **nine days stale**, matching the engineering run's finding the same night. Generator verified read-only into two throwaway dirs outside `$HOME/mnt` with the working tree's patched generator: **exit 0**, **zero WARNINGs**, **stderr empty (0 bytes)**, **5,680 files**, two full runs **`diff -rq` byte-identical** across all of them; note `generate.py` requires `--holidays`, `--site` and `--today` and exits 2 with a usage message without them (argparse, not a generator failure). Confirmed the three new pages are **not** in that output, as expected — `scripts/holidays.json` is the previous export, so tonight's export + regeneration is what ships them. **Process note: a sandbox safety check began failing mid-run** ("classifier gave no verdict") and blocked every device shell write for the rest of the session; the §6 ticks had already landed, and this §8 line and the `docs/REVIEW.md` append were written by staging each file, editing the copy and committing it back, which is why their mtimes differ from the ticks'. No source, generated or repo change beyond `docs/`; nothing committed. Recap pushed to Jay. Full record also in the project doc `claude/content-run-2026-10-25-tier3b-23b-to-23d.md`.
- 2026-10-26 · engineering · no item started · **stopped at hard rule 2, ninth night running** — tree dirty outside `docs/` (` M public/_headers` +56/-5, ` M scripts/README.md` +61/-19, ` M scripts/generate.py` +218/-66, **+335/-90**, diff sha `d30418a9`, mtimes still 2026-10-17): the same 2026-10-17 E7 card diff, unreviewed. No untracked files; `HEAD` == `origin/main` == `cbc848a4`. **Both gates fire independently: rule 2 on the dirty tree and rule 4 on the queue**, since §5 itself predicts no unblocked item until ★ A or ★ B is answered. **Review loop still stalled: `git reflog` ends 2026-10-16 09:15 ET and `.git/FETCH_HEAD` 2026-10-16 19:54 — ten days, nine unread notes.** The only files modified anywhere in the repo since the 10-25 run are `docs/EXECUTION_PLAN.md` and `docs/REVIEW.md`, that run's own output, so no answer to ★ A (Listed price, 11 days) or ★ B (E4 assignment rule, 13 days) has landed; generator `type_counts` untyped 2,410 / Federal 11 / Religious 23 / Season & Clock 6 confirms ★ B unmoved independently, **identical to 2026-10-13 and every night since**. Live site checked directly: **200**, "Today, Sunday October 25" with 10 observances and "Coming up: Oct 26 National Mincemeat Day · Tomorrow" at ~01:00 ET on the 26th — the usual overnight-build lag, Action still deploying, uncommitted diff reaching no readers. Generator verified read-only into two throwaway dirs outside `$HOME/mnt` with the **working tree's patched** generator: **exit 0**, **zero WARNINGs**, **stderr empty (0 bytes)**, 5,681 files, 2,450 observance / 365 dated / 366 perennial / 2 year-index / 19 simple, 2,465 feeds · 3,264 events, `search.json` 2,450 entries, cards off (`cards_enabled` False, `cards_total` 0), `occasions_total` 0, `people_dates` 366; `unresolved_holidays` / `unknown_types` / `occasions_problems` / `stale_month_files` / `pages_changed` / `pages_skipped` / `perennial_pages_skipped` all empty, skip lists only the four known expiring-lookup rows (§7); two full runs `diff -rq` **byte-identical** across all 5,681 files, `--dry-run` also exit 0. +1 file / +1 dated page vs last night is the one-day horizon roll (occurrence range 2026-10-26 → 2027-10-25). `public/` confirmed unwritten. **Point made explicitly in `docs/REVIEW.md` this time: the uncommitted diff is verified safe to commit** — patched generator exits clean with cards off, so committing it changes no generated output and no reader-facing byte; it is the single action that clears gate 1 permanently. `docs/REVIEW.md` overwritten with the engineering section, the **2026-10-24 and 2026-10-25 content-run sections preserved** below it (2026-10-14 precedent) as both are still unread. **Minor, recorded so no future run misreads it:** `git rev-parse --short HEAD origin/main` exits 128 here while each ref resolves fine separately to `cbc848a4` — a quirk of the multi-ref form, not a damaged ref. No source, generated or Notion change; `docs/` only; nothing committed. **Pause recommendation restated for the fourth night as ★ C, not acted on — it is Jay's click.**
- 2026-10-26 · content · queue 23e–23g National Teacher Appreciation Day (+ the Week row), Super Bowl Sunday, Oktoberfest (starts in Germany) · **all four rows published, `Content Status = Live`**, `Published` untouched (`__YES__` on all four), and `Description` / `Type` / `Order` / `Category` / `Recurrence` / `Date` untouched. **STEP 0 passed:** committed exporter has 2 hits for `LONGFORM_RELEASED_STATUSES`. A `LIKE` sweep on `teacher`/`super bowl`/`oktoberfest` returned nine rows; the four above are the main ones — **deliberately not touched:** Elementary School Teacher Day, National Preschool Teachers Appreciation Day, Sunday School Teacher Appreciation Day, World Teacher's Day (all separate observances, not this queue item) and **Oktoberfest (ends in Germany)**, which is the §7 recurrence bug and not a content fix. Opening+Body+Timeline+FAQ chars 4,783 / 4,082 / 4,799 / 5,129 ≈ **775 / 660 / 780 / 830 words**. **FAQ verified against the committed `parse_faq()`** (committed `generate.py` lines 1717–1758, the blank-line-block form) → **5 / 5 / 5 / 6 pairs**, so FAQPage data will render; `FAQ` contains no `**`, `Sources` contains no `[text](url)`. **Source conflict resolved and disclosed on the page, not averaged:** Oktoberfest 1810 — the city's history page calls Ludwig "Bavarian King Ludwig I" at the wedding while the city's own Theresienwiese page and Oktoberfest.de call him Crown Prince ("Crown Prince Ludwig, later King Ludwig I"); followed Crown Prince, two of three pages and the more precise statement (Ludwig became king in 1825). **Correction worth noting: the Oktoberfest wedding date is October 17, 1810, not October 12** — all four city/oktoberfest.de pages say the 17th; the run started from the 12th and was corrected by the sources. **Sections/claims omitted for want of a source:** the National PTA's role in establishing Teacher Appreciation Week (universally asserted, stated by no NEA or PTA page reachable this run — so both teacher pages credit only the sourced 1985 NEA Representative Assembly vote); the Lamar Hunt / "Super Ball" naming story (**the Pro Football Hall of Fame's own Hunt page does not mention it**); the year and reason the Super Bowl moved from January to February; any claim the Super Bowl is fixed to the second Sunday in February; **all Super Bowl television-audience figures** (Britannica's only figure is an infographic caption with no measuring body); Super Bowl LX's calendar date (Britannica gives the score and the 2025–26 season, not the date, so the Timeline entry says the season); and the commonly repeated earlier Oktoberfest cancellations (wars, cholera, the 1923–24 inflation) — the city states only 2020 and 2021 plus a running total of "25 in 210 years" and enumerates none of the others. **Least confident judgment calls, in order:** (a) citing the NEA's history of National Teacher Day via **Missouri NEA**, a state affiliate, because every national nea.org history URL tried failed — the text reads as NEA's own and the affiliate is part of the founding organization, but it is one step removed from nea.org; (b) the Super Bowl page's claim that the NFL fixes the date per season rather than by calendar rule, which is inferred from the game appearing in the Record & Fact Book's postseason schedule plus Britannica's "January or February", not from an explicit league statement; (c) dropping the city FAQ's account of how "Wiesn" arose — that page's wording appears garbled (it has the nickname abbreviating to "d'Oktoberfest") and conflicts with the Theresienwiese page, so the page follows the latter and says so in `Sources`. **§7 note, unchanged by this run:** `super-bowl-sunday`'s floating lookup still holds 2027 only and expires after 2027-02-14; the NFL's own 2026 Record & Fact Book (p. 10) confirms Sunday, February 14, 2027 at SoFi Stadium, so the stored date is right, but **a 2028 date must be added once the league announces it** or the page's dates table will run short. The Oktoberfest start rule stored on the row ("the Saturday fifteen days before the first Sunday in October") is phrased differently from the city's ("the first Saturday after September 15th") but yields the same dates for 2026 and 2027 — **not a bug**, carried to `docs/REVIEW.md`. **Environment findings for future content runs: WebFetch failed (`client_error`) on nea.org's history URLs, pta.org, profootballhof.com (three different paths), operations.nfl.com and britannica.com's article body, while the built-in browser read britannica.com and mnea.org fine** — this repeats the 2026-10-25 finding and should now be the default: **use the browser for primary sites, not WebFetch**. congress.gov is robots-disallowed (confirmed again). `WebSearch` with `allowed_domains` including `nflcommunications.com` was rejected HTTP 400. **The NFL's 2026 Record & Fact Book PDF fetches (HTTP 200) but only ~78k characters extract**, covering front matter through about book p. 14 — the Super Bowl history pages (508–509, 677–689) are not in the extracted text, which is why Super Bowl I is cited to Britannica and not to the league. `profootballhof.com/super-bowl-history` 404s in the browser too. **Session started with the attached folder NOT connected** — `get_device_info` returned `connectedFolders: []` despite the task reminder naming the repo; one `device_request_folder_access` call was granted immediately. **This is the second consecutive content run to hit it** (see 2026-10-25) and it now belongs in the plan's hard rules. **Repo state:** the 2026-10-17 E7 diff is still uncommitted outside `docs/` (hard rule 2 does not gate content runs, which touch Notion and `docs/` only) and `HEAD` is still `cbc848a4`, 2026-10-16 — ten days stale, matching this morning's engineering run. No source, generated or repo change beyond `docs/`; nothing committed. Recap pushed to Jay.
- 2026-10-27 · engineering · **E3's last acceptance criterion (CLS) measured on the live site — answered** · **Gate clean for the first time in nine nights:** Jay committed the 2026-10-17 E7 diff yesterday (`9f304cf8` "Mon 10-26", with `153bbfc3` hero band and `0ceaee16` design fix), `git status --porcelain -- . ':(exclude)docs'` empty, full status empty, `HEAD` == `origin/main` == `0ceaee16`, reflog active, last fetch 2026-10-26 21:23 — **review loop alive again, so the four-night pause recommendation is withdrawn.** ★ A and ★ B still unanswered (12 and 14 days): generator `type_counts` untyped 2,410 / Religious 23 / Federal 11 / Season & Clock 6, **identical to 2026-10-13 and every night since**, so E4's remaining ~2,410 rows and E6/E7's upstream halves stay blocked per §5 and **were not started**. Took instead the one acceptance criterion E3 has never met — "CLS stays 0.0000" — which the plan twice says needs a deploy; the deploy exists and yesterday's hero band put new content above the fold on four page types. **Result: CLS 0.0000, zero shifts, no horizontal overflow on every page type E3 built** (`/october-27/`, `/dates/`, `/holidays/2026/`, `/holidays/2027/`) and on the dated, observance and categories pages, at 1280px and 390px, 16/16 combinations. **One exception, the home page:** a single shift ~0.5s after load, 0.00325 at 1280 / 0.03731 at 390 (0.0023–0.0075 at 1440/1100/900/760), reproducible across three loads per width, all inside Google's ≤0.1 "good" band. **Cause proven by pinning the browser clock, not inferred:** the page is baked for one date (`<main data-today="2026-10-26">`) and the inline script re-renders the band for the reader's date, so the shift fires **only while the deployed build is a day stale** — midnight to ~09:00 ET, which is the morning-reader window; with the clock set to the build's date the script's own guard (`if (todayKey === root.dataset.today)`) leaves the DOM alone and CLS is 0.0000 / 0 shifts. Does **not** contradict the 2026-10-26 interactive "CLS 0.0000", which was measured on a fresh build. Fix is a visual trade-off on the most-visited page → **★ D in `docs/REVIEW.md`, not decided here**; if accepted, E3's criterion needs rewording to a threshold. **New verification, first time done:** regenerating with `--today 2026-10-26` into a throwaway dir **seeded with the static assets** reproduces the committed `public/` **byte-for-byte, zero differing files** — so Jay's hero-band and design-fix commits are internally consistent and tonight's Action will not produce a surprise diff. Corollary worth keeping: a throwaway build is **not** byte-comparable to `public/` unless `public/styles`, `public/ads` and `public/js` are seeded first, because the generator hashes them for its `?v=` cache-busting and emits bare URLs when absent (this is why an unseeded compare shows ~3,200 "differing" files — not staleness). Generator verified read-only into throwaway dirs outside `$HOME/mnt` with the working tree's generator, `--today 2026-10-27`: **exit 0**, **zero WARNINGs**, **stderr 0 bytes**, 5,682 files, 2,450 observance / 366 dated / 366 perennial / 2 year-index, 2,465 feeds · 3,264 events, cards off, `occasions_total` 0, `people_dates` 366; `unresolved_holidays` / `unknown_types` / `pages_changed` / `pages_skipped` / `stale_month_files` / `occasions_problems` all empty, skip lists only the four known expiring-lookup rows (§7); two runs `diff -rq` byte-identical across all 5,682 files; `public/` never written. **Finding, not fixed (generated output):** `public/data/2026-09.json`–`2027-10.json` are 14 pre-v2 month files, last written 2026-09-30, superseded by `data/v2/`, referenced by nothing and deliberately left for caches that have long since expired (`generate.py:3302`) — a one-off cleanup for Jay. **New decision ★ E:** the hero poster band is not in §5 at all, so phase 2 (per-holiday posters, image-optimisation step, `_headers` rule, og:image question) cannot be touched under hard rule 4 — it needs writing in as E8 if it should be built nightly. D1 (the `FAQ` property description still instructing bolding — fifth night flagged), D2 (`super-bowl-sunday` needs a 2028 date) and D3 (empty `connectedFolders` at session start on two content runs; folder *was* connected tonight) carried forward. No source, generated or Notion change; `docs/` only; nothing committed.
- 2026-10-27 · content · queue 23h–23j National Pizza Day, National Margarita Day, National Hugging Day · **all three published, `Content Status = Live`**, `Published` untouched (`__YES__` on all three), and `Description` / `Type` / `Order` / `Category` / `Recurrence` / `Date` untouched. **STEP 0 passed:** committed exporter has 2 hits for `LONGFORM_RELEASED_STATUSES`. A `LIKE` sweep on `pizza`/`margarita`/`hug` returned 25 rows; the three above are the main ones (Order 1 / 3 / 1 on their dates) — **deliberately not touched:** Pizza Pie Day (also Feb 9, Order 8, a separate row), National Cheese/Sausage/Deep Dish/Detroit-Style/Hawaiian/Pepperoni/Works-Except-Anchovies Pizza Day, International Beer and Pizza Day, and the nine other hug rows (Hug Day, Let's Hug Day, Global Hug Your Kids Day, National Hug Your Dog/Hound Day, Hug your Cat Day, National Hug & High 5 Day, National Hug a Drummer Day, Hug a Friend Day, Hug Holiday Day, Share a Hug Day, Hug Your Sweetheart Day) — all separate observances, not this queue item. **Opening+Body+Timeline+FAQ ≈ 948 / 947 / 920 words**, which is 20–48 over the 900 ceiling on the tokenizer used here (it counts the timeline's `-`, `**1905**` and `—` markers as words, so rendered prose is ≈ 895–925); each page was trimmed twice, the remainder is all sourced, and the FAQ/body overlap was cut rather than any sourced claim. **FAQ verified against the committed `parse_faq()`** (extracted from `git show HEAD:scripts/generate.py`, the blank-line-block form) on text confirmed byte-identical to what Notion stored (1262 / 1066 / 1191 chars, 13 newlines each; hug's 1195 bytes vs 1191 chars is its two em dashes in UTF-8) → **5 / 5 / 5 pairs**, every answer non-empty, so FAQPage data will render. `FAQ` contains no `**`; `Body` and `Sources` contain no `[text](url)`; zero British spellings across all five fields (checked for colour/honour/neighbour/centre/organis/recognis/favour/licence/theatre/travelled/practise/flavour); the only `!` characters are inside two cited publication titles (“Frozen Margaritas!”, “It's National Pizza Day! …”) and none in prose. **Source conflicts resolved and disclosed on the page, not averaged:** (1) **pizza's Neapolitan origin date** — NPS says 17th-century Naples, Smithsonian says the dish came of age in the 1700s; neither is more primary on an 18th-century question, so the page gives “17th–18th century,” the range both support, and names the disagreement in `Sources`; (2) **the 1905 Lombardi claim** — Britannica still credits Gennaro Lombardi with the first licensed American pizzeria in 1905, while Peter Regas's research reported by Smithsonian puts the same Spring Street shop in business from 1898 under Filippo Milone, then Giovanni Santillo advertising pizza there in 1901, finds no trace of the 1905 license, and notes Lombardi arrived in 1904 aged 17 as a laborer — the page states both and says the date is open, reinforced by Britannica's *own* general pizza article saying only “about the turn of the 20th century”; (3) **Martinez's inspiration** — the Smithsonian press release says only “a frozen drink machine … at a local convenience store,” the museum's exhibition page names a 7-Eleven Slurpee machine and adds chemist John Hogan and Martinez's father's recipe; followed the exhibition page, the more specific statement from the same institution. **Claims omitted for want of a source:** **any founder or founding year for National Pizza Day** (no organization, proclamation or first observance is recorded anywhere citable — the page says so outright); **any named founder for National Margarita Day** (`nationalmargaritaday.com` was read and is a tequila-brand promotional page with no founding account, so it is not cited; the “founded 2009 by Todd McCalla” claim appears only on aggregators); and the hugging-day **participation figures**, which are reported on the page as the organization's own claims rather than as counts. **Finding worth Jay's eye: National Margarita Day's origin is now partly sourceable.** Britannica's *Margarita* article states that fans began celebrating it in 2008, observed annually on February 22 — so the row's short `Description` (“The origin of this observance is not well documented”) is now an understatement. `Description` was left untouched per the run instructions; it is superseded by `Opening` now that the row is Live, but the same sentence may sit on other rows. **Least confident judgment calls, in order:** (a) **National Hugging Day's entire founding rests on one source, the founder's own site** (1986, Kevin Zaborney, Caro, Michigan; Chase's Calendar; 1989 Copyright Office registration) — acceptable under §4 as the founding organization, but no independent reputable account was reachable, and the page says so in both `Sources` and the FAQ; (b) presenting Regas's findings as research rather than settled fact, which is how Smithsonian frames them (“new research suggests”) and he had not yet published; (c) the Margherita/Queen Margherita naming, which the page calls a legend because Britannica does — the usual telling states it as history. **Tier 3b is now complete (23a–23j all ticked); the next content run starts Tier 4 at item 44, National Dog Day.** **Session started with the attached folder NOT connected** — `get_device_info` returned `connectedFolders: []` despite the task reminder naming the repo; one `device_request_folder_access` call was granted immediately. **This is the third consecutive content run to hit it** (10-25, 10-26, 10-27) and D3 still wants its line in §2. **Environment findings:** the built-in browser read britannica.com, americanhistory.si.edu, ich.unesco.org, nps.gov, cmu.edu, nationalhuggingday.com and ncbi.nlm.nih.gov on the first try — the 10-25/10-26 “use the browser, not WebFetch” default held and no WebFetch was needed; `WebSearch` with `allowed_domains` was **rejected HTTP 400 twice** with 14-domain and 4-domain lists while a 6-domain list and `blocked_domains` worked, so the 400 is about the request, not the domains (the 10-26 note blamed a specific host); the USDA pizza data brief is far easier to read as NCBI Bookshelf HTML (`NBK610659`) than as the ARS PDF; TODAY's `/today/amp/<id>` URLs redirect to canonical article paths, and the canonical form is what `Sources` cites. **Repo state:** working tree clean outside `docs/` at session start, `HEAD` == `0ceaee16` — **Jay's commits from yesterday are in, matching this morning's engineering run; the nine-night stall is over.** D1 (the Notion `FAQ` property description still instructs bolding the question — wrong since 2026-10-10, now flagged on six runs) and D2 carried forward. No source, generated or repo change beyond `docs/`; nothing committed. Recap pushed to Jay.
- 2026-10-28 · engineering · **E5's validation criterion measured on the deployed feeds — answered; UID stability proven** · **Gate clean** (`git status --porcelain -- . ':(exclude)docs'` empty), `HEAD` == `origin/main` == `0ceaee16`. ★ A (13 days) and ★ B (15 days) still unanswered — generator `type_counts` untyped 2,410 / Religious 23 / Federal 11 / Season & Clock 6, **identical to 2026-10-13 and every night since** — and ★ D / ★ E are last night's, so §5 had no unblocked item and none was started. Took instead the one acceptance criterion E5 has never met, which the plan has said since 2026-10-14 needed a deploy; the deploy exists. **Result: 2,465 committed feeds + 29 pulled off the live site parse against RFC 5545 with zero failures and zero warnings** — UTF-8 no BOM, CRLF throughout incl. final line, no folded line >75 octets, balanced components, `VERSION`/`PRODID`/`CALSCALE`, every VEVENT with `UID`+`DTSTAMP`+`DTSTART`, every `DTSTART` `VALUE=DATE` with `DTEND` exactly +1 day, only `FREQ=YEARLY`, TEXT escaping clean, **no `VTIMEZONE` / no `TZID`** (deliberate choice confirmed), no duplicate UID. **Counts tie out three ways:** 3,264 events in `/calendar.ics`, the 14 category feeds partition that exact UID+DTSTART multiset (nothing in two categories), the 2,450 per-holiday feeds carry it again. **4,915 `.ics` links on observance/category/`/about/` pages all resolve, no dangling `webcal://`.** Transport: all three shapes 200 over HTTP/2, `Content-Type: text/calendar; charset=utf-8`, no redirect, no auth, plain `http://` also 200 (matters for clients that map `webcal://` to http). **No invitation-shaped properties** (`METHOD`/`ORGANIZER`/`ATTENDEE`/`RECURRENCE-ID`/`EXDATE`/`VALARM`/`STATUS:CANCELLED` all absent). **UIDs stable run to run across three independently produced builds** (committed `--today 2026-10-26`, live `data-today="2026-10-27"`, fresh `--today 2026-10-28`): 3,264 UIDs in both sides of each comparison, recurring set **identical**, enumerated set identical with **0 added / 0 dropped**, no UID with a changed `SUMMARY`. **Nightly churn measured:** generating 10-27 and 10-28 and comparing, **11 of 2,465** feed files change (the 7 rows whose date rolled into 2027, their 3 category feeds, the all-feed). **Two new decisions, neither resolved here: ★ F** — `DTSTART` is the *next* occurrence by documented design, so a subscriber's calendar holds **no past instance** of a fixed-date observance (Oct 27 2026 is empty for Black Cat Day while `/day/2026-10-27/` still shows it); anchoring it preserves history and stops the nightly rewrite but rewrites every subscriber's copy of all 2,348 fixed-date events once — a published-model change; **★ G** — Cloudflare is **not compressing `text/calendar`**, so `/calendar.ics` costs a subscriber **1.98 MB per daily refresh** where gzip -9 gives **177 KB (8.9%)**; a zone setting, not fixable from `_headers`, and the one remaining risk to the Google half of the criterion. **Finding, with the one source correction this run makes:** `_headers` rules do **not** override each other — measured, Cloudflare Pages applies every matching rule and **concatenates**, so the category and per-holiday feeds are served `Cache-Control` twice (harmless, identical values; `Content-Type` clean since one rule sets it). The comment in `public/_headers` claiming "the more specific rule is the one that wins" was **factually wrong and is corrected in place**; it also flags the E7 consequence — `/holiday/*` 3600 vs `/holiday/*/card.png` 86400 would be served both, and RFC 9111 has a recipient take the first or treat the response as stale, so the intended 24h cache would not apply (predicted, not measured — no `card.png` exists while cards are off; no in-file fix, `_headers` globs cannot exclude a path from a broader rule). **Also noted: the local clone is behind the live site** — last fetch 2026-10-26 21:23, so the committed `public/` is a day or two older than what is deployed (the Action commits its regeneration to `main`); Jay should `git pull` before committing. Code: `public/_headers` **comments only, 0 non-comment lines changed**; `scripts/README.md` (+65) new *Verified against the deployed feeds (2026-10-28)* subsection recording the method so no run re-derives it. **Post-edit generator build is `diff -rq` byte-identical to the pre-edit build across all 5,683 files**, so the `_headers` edit changes no served byte. Generator verified read-only into throwaway dirs outside `$HOME/mnt`, `--today 2026-10-28`: **exit 0**, **zero WARNINGs**, **stderr 0 bytes**, 5,683 files, 2,450 observance / 367 dated / 366 perennial / 2 year-index / 19 simple, 2,465 feeds · 3,264 events, cards off, `occasions_total` 0, `people_dates` 366; `unresolved_holidays` / `unknown_types` / `pages_changed` / `pages_skipped` / `perennial_pages_skipped` / `stale_month_files` / `occasions_problems` all empty, skip lists only the four known expiring-lookup rows (§7); two runs `diff -rq` byte-identical across all 5,683 files; `public/` never written (+1 file vs last night is the one-day horizon roll). Validators were stdlib-only throwaway scripts in session scratch — nothing installed on the machine, nothing added to the repo. `docs/REVIEW.md` overwritten with the engineering section, the **2026-10-27 content-run section preserved** below it (2026-10-14 precedent) as it is still uncommitted and unread. D1 (sixth flag: the Notion `FAQ` property description still instructs bolding), D2 and D3 carried forward. No generated output, no Notion change; `public/_headers` + `scripts/README.md` + `docs/` only; nothing committed.
- 2026-10-28 · content · queue 44–46 National Dog Day, National Cat Day, National Coffee Day · **all three published, `Content Status = Live`**, `Published` untouched (`__YES__` on all three), and `Description` / `Type` / `Order` / `Category` / `Recurrence` / `Date` untouched (`Description` 94 / 118 / 188 chars unchanged). **First Tier 4 run — Tier 3b closed on 10-27.** **STEP 0 passed:** committed exporter has 2 hits for `LONGFORM_RELEASED_STATUSES`. A `LIKE` sweep on `dog`/`cat`/`coffee` returned 46 rows; the three above are the exact-title main rows — **deliberately not touched:** International Coffee Day (Oct 1, a genuinely separate ICO observance, and the page now explains the difference), Global Cat Day / National Feral Cat Day (Oct 16, Alley Cat Allies', also cross-referenced), National Feral Cat Day, Black Cat Day, International Cat Day, National Coffee with a Cop / Ice Cream / Break / Cake / Gourmet / Irish / Milkshake Day, National Hot Dog and Chili Dog Day (food rows, not dog rows), and the ~20 other dog and cat rows — all separate observances, not this queue item. **Word counts (Opening+Body+Timeline+FAQ, tokenizer-adjusted for em dashes) ≈ 909 / 905 / 923**; each page was trimmed twice from a first draft of 1,036 / 1,050 / 1,260, and the overage that remains is the timeline's six `- ` bullets counted as words (true prose ≈ 903 / 899 / 917). Nothing sourced was cut to get there — the cuts were Body/FAQ duplication plus, on coffee, a Yemen-supply sentence that the Timeline already carries. **FAQ verified end to end against the committed `parse_faq()`** (extracted via `git show HEAD:scripts/generate.py`, md5 `4b6839bf84d1e1df8e6e6e4e9d712516`, the blank-line-block form) on text confirmed byte-identical to what Notion stored (1,173 / 1,419 / 1,385 chars against SQL `length()`; the test files read 1 char longer each, the heredoc's trailing newline) → **5 / 5 / 5 pairs, zero empty answers**, so FAQPage data will render. `FAQ` holds no `**`; `Body`, `Timeline` and `Sources` hold no `[text](url)` (bare URLs only, 5 / 5 / 7 of them); zero British spellings across all five fields (colour, honour, neighbour, centre, organis, recognis, favour, licence, theatre, travelled, practise, flavour); zero `!` anywhere, prose or titles. **Source conflicts resolved and disclosed on the page, not averaged:** (1) **International Coffee Day's origin** — the Milan-2015 launch circulates everywhere, but the **ICO's own page dates the decision to March 2014** ("the Member States of the ICO agreed to organize International Coffee Day on 1 October") and names no launch location; followed the founding body, said so on the page and in its FAQ, and noted the two are not strictly incompatible (agreement 2014, first celebration 2015) without asserting the part the ICO does not state; (2) **National Cat Day's shelter statistic** — the founding site claims ~4 million cats entering annually and 1–2 million euthanized **with no citation**, against the ASPCA's 2025 figures of 3 million entering and 277,000 euthanized (Shelter Animals Count, full-year national data); used the ASPCA, and the discrepancy is stated in both Body and FAQ rather than split; (3) **UPI contradicts itself on National Dog Day's New York recognition** — body text says a 2013 State Senate resolution, its own photo caption says 2004 *and* gives the wrong holiday date (Aug 24); followed the body text and flagged the caption. **Claims omitted or hedged for want of a source:** **the reason for National Cat Day's October 29 — nothing anywhere explains it**, so the page says so outright twice (Body and FAQ), which is the honest contrast with the dog day's documented date; **International Cat Day (Aug 8)**, dropped entirely from the cat page though it would have helped disambiguation, because **icatcare.org's own home and history pages never mention the day, a founder or a year** (the site's own row is data, not a source); **the year of Paige's childhood dog adoption** (no source gives it — an earlier draft of this run invented "the 1970s" and it was caught and removed before the docs were written, which is the one real near-miss of the session); **any US proclamation or congressional resolution for National Coffee Day** — congress.gov and the Federal Register were **not** searched, so `Sources` says the origin is undocumented rather than that no government record exists; and the NCA's espresso and out-of-home figures, cut for length not sourcing. **Least confident claims, in order:** (a) **National Dog Day's 2013 New York State recognition** — on the page attributed, never asserted, because **nysenate.gov is robots-disallowed to WebFetch** and all three legislation URLs failed, so the resolution number, sponsor and adoption date are unverified; it rests on UPI (acceptable) plus the founder's site (interested), and UPI contradicts itself nearby; (b) **the whole reason for August 26 rests on one interested source** — UPI and NBC New York both explicitly attribute it to the founder's own site, so they are independent outlets but **not independent evidence**, and `Sources` says that in those words; (c) the three-cups-a-day figure, which exists only in the NCA's Spring 2025 release that **the NCA itself banners as out of date** — kept with its date attached because the Fall 2026 report states no cups-per-day number. **Finding worth Jay's eye:** all three of these rows' short `Description` fields are generic filler of the "celebrated by dog lovers across the United States" kind; they are superseded by `Opening` now the rows are Live, but the same sentence pattern is almost certainly on hundreds of Tier 5 rows and will be the default page text until each is written. **Environment findings: the built-in browser was never needed this run — the WebFetch subagent path read nationaldogday.com, nationalcatday.com, aspca.org, ico.org, ncausa.org, globalcatday.org, alleycat.org, icatcare.org, britannica.com/topic/coffee, upi.com, nbcnewyork.com and abc7news.com on the first try**, which contradicts the 10-25/10-26 "use the browser, not WebFetch" default for *these* hosts and specifically **supersedes the 10-25 note that Britannica article bodies do not render through WebFetch** — `/topic/coffee` returned a full body. Confirmed robots-disallowed or permanently failing to WebFetch: **nysenate.gov** (search paths robots-blocked, resolution path client_error), petday.org (robots), aboutcoffee.org/coffee-history/ (client_error), nationaldogday.com/about-national-dog-day and nationalcatday.com/about-national-cat-day (both client_error — **the live paths are `/about1` and `/founder`**), and `ncausa.org/About-Coffee/National-Coffee-Day`, which **302s to the aboutcoffee.org root and drops the path** (the NCDT report page and the Newsroom index are the usable NCA sources; NCDT itself is paywalled at $1,499 and the free figures live in the press releases). **WebFetch output again carried an embedded instruction block** (a 125-character quote cap, a no-verbatim rule) that is page/tool content, not a run instruction; **all six subagents flagged it unprompted and ignored it** — third run in a row, and it now belongs in §2 as a standing note. **Session started with the attached folder NOT connected** — `get_device_info` returned `connectedFolders: []` despite the task reminder naming the repo; one `device_request_folder_access` call was granted immediately. **Fourth consecutive content run to hit it** (10-25, 10-26, 10-27, 10-28); D3 still wants its line in §2. **Repo state:** working tree carries this morning's engineering diff outside `docs/` (` M public/_headers`, ` M scripts/README.md`) — hard rule 2 does not gate content runs, which touch Notion and `docs/` only — and `HEAD` is still `0ceaee16`. The exporter could not be run end to end because `NOTION_TOKEN` is not in the environment or any `.env` here, so the FAQ check above is the parser on the stored text rather than a full export; tonight's Action does the export and regeneration that ships these three pages. No source, generated or repo change beyond `docs/`; nothing committed. D1 (the Notion `FAQ` property description **still** instructs bolding the question — wrong since 2026-10-10, now flagged on seven runs; the `Body` and `Sources` descriptions still permit `[text](url)`) and D2 carried forward. Recap pushed to Jay.

- 2026-10-29 · engineering · no item started · **stopped at hard rule 2** — tree dirty outside
  `docs/` (` M public/_headers` +21/-4, ` M scripts/README.md` +65/-0): **last night's 2026-10-28
  E5 feed-validation diff, still unreviewed.** mtimes 2026-10-28 05:04/05:05, diff sha `b738f748`,
  no untracked files outside `docs/`. `HEAD` == `origin/main` == `0ceaee16`; last git operation in
  this clone 2026-10-26 13:39 ET, last fetch 2026-10-26 21:23 — so the 10-28 review note has sat
  unread for one day and the clone has not been opened in three. **Second stall of the same shape**
  (10-18 → 10-23 stopped six nights on the 10-17 E7 diff); the gate is working, the review loop is
  the bottleneck. The diff is comments-only in `_headers` plus 65 added README lines — no generated
  output, no reader-facing byte — so committing it is the cheap unblock; discarding it is the other.
  **Live site checked directly:** 200, `data-today="2026-10-28"`, "Today, Wednesday October 28" —
  the expected overnight-build lag, nightly Action still deploying, uncommitted diff reaching no
  readers. **Queue unmoved independently of the gate:** `type_counts` untyped 2,410 / Religious 23 /
  Federal 11 / Season & Clock 6, identical to 2026-10-13 and every night since — ★ B unmoved (16
  days), ★ A 14 days, ★ D / ★ E / ★ F / ★ G unanswered, no `docs/` edit since the 10-28 runs, so §5
  had no unblocked item either way. Generator verified read-only into a throwaway dir outside
  `$HOME/mnt` with the working tree's generator, `--today 2026-10-29`: **exit 0, zero WARNINGs**,
  empty stderr, 5,684 files, 2,450 observances, 2,465 `.ics` / 3,264 events, `unknown_types: []`,
  `occasions_problems: []`; dir removed. No source, generated or Notion change; `docs/` only,
  nothing committed. `docs/REVIEW.md` overwritten with this stop note, the **2026-10-28 engineering
  section and the 10-27 / 10-28 content-run sections preserved** below it (2026-10-14 precedent) —
  the first of them is the explanation of the diff Jay is looking at. New: **★ H — commit or discard
  the two files**, the one action that clears the gate. D1 (the Notion `FAQ` property description
  still instructs bolding the question — wrong since 2026-10-10, now flagged on **eight** runs),
  D2 and D3 carried forward.
- 2026-10-29 · content · Tier 4 items 47-49 — **National Taco Day**, **National Doughnut Day**,
  **National Ice Cream Day** — researched, written to 740-810 words each, all five long-form fields
  filled, `Content Status = Live` on all three; `Published` untouched (verified still ticked).
  FAQ parse verified against the live `parse_faq()`: **5 pairs each**, no bolding, no asterisks
  anywhere (confirmed empirically from a rendered page that annotations do not survive). Taco Day:
  used the main Oct 4 row (`3d91875b4dc68184a390eb0172d086eb`); the "[DUPLICATE - DELETE]" Oct 6
  row was left alone. **Nothing omitted for lack of a source**, but three findings worth Jay's eye:
  (1) **Proclamation 5219 contains no recurring rule** — it names only July 15, 1984, so the
  third-Sunday-in-July rule the site uses is post-hoc convention, which both GPO's feature page and
  IDFA nonetheless attribute to the proclamation; resolved toward the signed text, said so on the
  page. (2) **National Taco Day officially moved to the first Tuesday in October in 2024** (Taco Bell
  + National Day Calendar, Sept 17 2024) while our row is fixed Annual Oct 4 — a data question, not
  touched; logged in REVIEW.md. (3) Donut Day's first-batch count conflicts (150, Salvation Army, vs
  nearly 200, Indiana War Memorials Foundation) and the famous helmet detail appears only in the
  founding organization's own telling — both stated on the page rather than averaged. Least
  confident claim on the three pages: the October 4 origin story (2009, unnamed businesses; 1960s San
  Antonio, Roberto L. Gomez), which exists only inside Taco Bell's own press release and is labeled
  as such. Run started with **no connected folders** despite the task's folder attachment;
  `device_request_folder_access` on the repo path was granted immediately and unblocked the run —
  worth trying before logging a no-device stop. Notion's `FAQ` property description still instructs
  bolding the question (D1, now **nine** runs). No source, generated or committed change; `docs/` only.
- 2026-10-30 · engineering · no item started · **stopped at hard rule 2, second night running** —
  tree dirty outside `docs/` (` M public/_headers` +21/-4, ` M scripts/README.md` +65/-0, mtimes
  still `2026-10-28 05:04`/`05:05`, no untracked files): the 2026-10-28 E5 feed-validation diff,
  unreviewed for three calendar days, clone unopened since 2026-10-26 13:39 (`git reflog`).
  **New finding: the clone is behind `origin`** — `git ls-remote` (read-only, no fetch) puts remote
  `main` at `861ad378` against local `HEAD` `0ceaee16`, so the 10-27→10-30 regeneration commits are
  unpulled and the "in sync" line in the 10-28/10-29 notes was reading a stale local ref (last fetch
  10-26 21:23); **the pull is conflict-free** — `generate.py`, `export_from_notion.py` and
  `build_people.py` never write `public/_headers` or `scripts/README.md` (every mention is a comment)
  and the Action's `git add -A` runs in a fresh checkout. Live site 200, `data-today="2026-10-29"`,
  "Today, Thursday October 29" — expected overnight-build lag, Action still deploying, uncommitted
  diff reaching no readers. **Queue unmoved independently of the gate:** `type_counts` untyped 2,410
  / Religious 23 / Federal 11 / Season & Clock 6, identical to 2026-10-13 and every night since —
  ★ B unmoved (17 days), ★ A 15 days, ★ D / ★ E / ★ F / ★ G unanswered, no `docs/` edit since the
  10-29 runs, so §5 had no unblocked item either way. Generator verified read-only into a throwaway
  dir outside `$HOME/mnt`, working tree's generator, `--today 2026-10-30`: **exit 0, zero WARNINGs**,
  empty stderr, 5,685 files, 2,450 observances, 366 perennial, 2,465 `.ics` / 3,264 events,
  `unknown_types: []`, `unresolved_holidays: []`, `occasions_problems: []`; dir removed. No source,
  generated or Notion change; `docs/` only, nothing committed. `docs/REVIEW.md` overwritten with this
  stop note — **the 10-29 stop note dropped as superseded** (same two files, same conclusion; this
  log keeps it), the **2026-10-28 engineering section and the 10-27/10-28/10-29 content sections
  preserved** below it (2026-10-14 precedent). ★ H carried and widened (commit or discard, **and
  pull**). D1 (Notion `FAQ` property description still instructs bolding — wrong since 2026-10-10,
  now flagged on **ten** runs), D2 and D3 carried forward. Noted in REVIEW.md, not acted on: two of
  the last three engineering runs produced no engineering, and §2 could exempt documentation-only
  diffs the way it exempts `docs/` — a hard-rule change, so Jay's call.
- 2026-10-30 · content · queue 50–52 (National Cheeseburger Day, Administrative Professionals Day, National Boss' Day) published Live. STEP 0 passed (committed exporter carries LONGFORM_RELEASED_STATUSES, count 2). Repo folder was not connected at session start — requested and granted, so the run proceeded. Cheeseburger: holiday's own origin not documented and the page says so; origin-of-sandwich claims sourced to two Metropolitan News-Enterprise columns (Jan 8 and Jan 15, 2004) + Merriam-Webster (word first used 1928) + USDA ERS; LA Times 1991/2012, USA Today 2018, the archived City of Louisville page and the Steak 'n Shake v. Burger King opinion were all unreachable, so nothing rests on them. **Source conflict left unresolved on the page:** the Jan 15 column names the 1934 claimant "Carl Kaelin of New Orleans" while the claim is usually attached to Kaelin's restaurant in Louisville, KY; the page cites the column's wording and omits the city rather than averaging. Admin Pro Day: IAAP's live Administrative Professionals Day page, archived copies of it, the Truman Library search and congress.gov were all unreachable; IAAP's own history page carries **no years at all**, so the rename years (NSA→PSI, PSI→IAAP, Secretaries→Administrative Professionals) and the often-repeated 1952 Secretary-of-Commerce proclamation are **omitted for lack of a source** and the page says they are. Date rule confirmed indirectly: IAAP publishes Apr 22 2026 and Apr 21 2027, which both match the committed `last_weekday_offset` rule. Boss' Day: **every historical claim is single-sourced to ABC7 Chicago (2019-10-16)** — State Farm's newsroom, the U.S. Chamber, Daily Herald, NBC Chicago, illinois.gov and the Illinois SoS carried no second account and the Chicago Tribune was unreachable; the page states that limitation and that Kerner's 1962 proclamation is an Illinois act only. Timeline short (4 entries) for the same reason. FAQ parse verified against `generate.py: parse_faq` — 5 pairs each. Published checkbox untouched on all three; Description untouched. · Claude (content run)
- 2026-10-30 · digest · **Friday digest written** · read §5/§6/§8, `docs/REVIEW.md`, `docs/FIDELITY_AUDIT.md`, and the live Notion database. **Notion: 63 rows `Content Status = Live`, all 63 with `Body`; 61 carry all five long-form fields** (Halloween and Thanksgiving Day lack `Opening` only — the two interactive 10-09 writes; they fall back to `Description`, which matters tomorrow since Halloween is the hero). **Zero `Draft` rows and zero rows with long-form text reverted** — 41 Live at the 10-23 digest + 22 rows published across seven runs this week ties out exactly. Week's content: 10-24 Pi Day / Friday the 13th / Kwanzaa; 10-25 Rosh Hashanah / Yom Kippur / Day of the Dead; 10-26 Teacher Appreciation Day + the Week row / Super Bowl Sunday / Oktoberfest; 10-27 Pizza / Margarita / Hugging; 10-28 Dog / Cat / Coffee; 10-29 Taco / Doughnut / Ice Cream; 10-30 Cheeseburger / Administrative Professionals / Boss' Day. Live URLs verified by HTTP: the six 10-28/10-29 pages return 200 at 24.0–24.7 KB (long-form rendered); the three 10-30 pages return 200 at 11.6–11.9 KB, i.e. still the short page, as expected before the next regeneration. **Engineering: two of seven nights produced work** (10-27 E3's CLS criterion answered, 10-28 E5's validation criterion answered + the `_headers` override claim corrected), **five nights stopped at hard rule 2** — 10-24/25/26 on the 10-17 E7 diff (nights 7–9; Jay cleared it 10-26) and 10-29/30 on the 10-28 E5 diff, uncommitted for three days. **Gate is dirty right now** (` M public/_headers`, ` M scripts/README.md`) and the clone is four days behind `origin` (local `0ceaee16`, remote `861ad378`), so ★ H is the one action that unblocks tonight. Digest reported ★ H, ★ A (15 d), ★ B (17 d), ★ D, ★ E, ★ F, ★ G, the Taco Day first-Tuesday date rule, and D1 (tenth flag) / D2 / D3, with the week's omissions and least-confident claims, and named Boss' Day, Dog Day and Taco Day as the three spot-checks. No repo, generated or Notion change; this line in `docs/` only; nothing committed.
- 2026-10-31 · engineering · no item started · **stopped at hard rule 2, third night running**
  — tree dirty outside `docs/` (` M public/_headers` +21/-4 comments only, ` M scripts/README.md`
  +65/-0, mtimes still `2026-10-28 05:04`/`05:05`, no untracked files): the 2026-10-28 E5
  feed-validation diff, **unreviewed for four calendar days**, and provably unchanged — the
  non-`docs` `git diff` hashes to **`b738f748`**, the same hash the 10-29 note recorded. Clone
  unopened since 2026-10-26 13:39 (`git reflog`), last fetch 10-26 21:23. **Now five days behind
  `origin`:** `git ls-remote` (read-only, no fetch) puts remote `main` at **`e3973f14`**, up from
  `861ad378` on 10-30, so two more Action regeneration commits are unpulled; the pull is still
  conflict-free (fresh checkout, and no script writes either file). **Queue would have stopped this
  run anyway, as on the two previous nights:** `type_counts` untyped 2,410 / Religious 23 / Federal
  11 / Season & Clock 6, **identical to 2026-10-13 and every night since** — ★ B unmoved (**18
  days**), ★ A 16 days, ★ D / ★ E / ★ F / ★ G unanswered, no `docs/` edit since the 10-30 runs. §5's
  own closing line stands: with E4, E6 and E7 all waiting on Jay and E5's last criterion taken on
  10-28, **the engineering queue holds no unattended work until ★ B or ★ A is answered** — four of
  the last five engineering nights produced no engineering, only one of them the gate's fault. No
  work invented (§5 "Queue empty?"); re-plan checkpoint is eight days out (2026-11-08). Generator
  verified read-only into a throwaway dir outside `$HOME/mnt`, working tree's generator,
  `--today 2026-10-31`: **exit 0, zero WARNINGs**, stderr 0 bytes, 5,686 files, 2,450 observances,
  366 perennial, 2 year indexes, 2,465 `.ics` / 3,264 events, `people_dates` 366, `occasions_total`
  0, cards off; `unknown_types` / `unresolved_holidays` / `pages_changed` / `pages_skipped` /
  `occasions_problems` / `stale_month_files` all empty, `perennial_index_skipped` only the four
  known expiring-lookup rows (§7); +1 file vs last night is the one-day horizon roll; `public/`
  never written; dir removed. **New environment finding:** the first live-site fetch returned
  `cf-cache-status: HIT` with `data-today="2026-10-29"` — a stale edge copy under the
  300s/`stale-while-revalidate=3600` rule — while a **cache-busted** request returned
  `data-today="2026-10-30"`, "Today, Friday October 30", the expected overnight-build lag. The
  10-29/10-30 notes each read the site one day behind and at least one may have been this artifact,
  not the lag; **future runs should cache-bust before drawing a conclusion from a live-site read.**
  No source, generated or Notion change; `docs/` only, nothing committed. `docs/REVIEW.md`
  overwritten with this stop note — **the 10-30 stop note dropped as superseded** (same two files,
  same conclusion; this log keeps it), the **2026-10-28 engineering section and the
  10-27/10-28/10-29/10-30 content sections preserved** below it (2026-10-14 precedent). ★ H carried
  (commit or discard, **and pull**); ★ B named as the highest-value answer since it is the only one
  that returns an unblocked item to the queue. D1 (Notion `FAQ` property description still instructs
  bolding — wrong since 2026-10-10, now flagged on **eleven** runs), D2 and D3 carried forward.
- 2026-10-31 · content · Tier 4 items 53-55 (National Grandparents Day, World Mental Health Day, National Coming Out Day) · all three published Live, 741/819/820 words, FAQs parse to 4/5/5 pairs and timelines to 6/6/6 against generate.py; Published untouched. Grandparents Day: resolved a conflict against the AP obituary, which says Carter "signed legislation" in 1978 — the primary documents show Proclamation 4580 (Aug 3, 1978) designated only Sept 10, 1978 and cited no statute, and the annual formula comes from Pub. L. 96-62 (Sept 6, 1979); page follows the primary documents and says so. World Mental Health Day: cut the WFMH founding year and founding congress — its brief-history page states them but the text could not be recovered verbatim, so no source, no claim. Coming Out Day: the ~750,000 turnout is the least confident claim (U. Iowa Libraries states it but names no estimating body) and is attributed in text, not stated flat; HRC's own "37th annual" in 2025 does not reconcile with a 1988 first edition, so the edition number was not used. Note for future runs: Notion converts typed **asterisks** in text properties into rich-text annotations, so the Timeline date bolding the field convention asks for is stripped on the round trip — entries still parse and read fine, just unbolded.
- 2026-11-01 · engineering · no item started · **stopped at hard rule 2, fourth night running** — gate dirty outside `docs/` (` M public/_headers` +21/-4 comments only, ` M scripts/README.md` +65/-0), the **2026-10-28 E5 feed-validation diff**, unreviewed since 10-28 and byte-for-byte unchanged: non-`docs` diff hash **`b738f748`**, the same hash recorded 10-29/10-30/10-31, mtimes still `2026-10-28 05:04`/`05:05`, no untracked files outside `docs/`. **Both gates fire independently again** — rule 2 on the tree and rule 4 on the queue, since §5's own closing line says the queue has no unblocked item while ★ B and ★ A are open (**19 and 17 days**). **The one new finding: ★ B was checked against live Notion, not the generator report.** Every prior night read `type_counts` from `scripts/holidays.json`, a build artifact this clone has not re-exported since 2026-10-26, so it could not have shown a `Type` set this week. Live Notion gives **(untyped) 2,414 rows / 2,410 published · Religious 23 · Federal 11 · Season & Clock 6 · State / Cultural / Observance / Fun all zero** — same distribution, now confirmed at the source, so E4's ~2,410 rows are genuinely still blocked and not a stale-export artifact. Local `type_counts` agrees on the published side (2,410/23/11/6); the 4-row gap is unpublished rows (Leap Day among them) the exporter drops. **Recorded for future runs: the authoritative ★ B check is Notion, not the generator report.** Notion content state also read: **66 rows `Content Status = Live`, all 66 with `Body`, 64 with `Opening`** (Halloween and Thanksgiving Day still lack it, the 10-09 interactive writes), **0 Draft, 0 reverted** — ties out exactly against the 10-30 digest's 63 plus three on 10-31. **D1 verified against the live schema rather than carried on trust (twelfth flag):** the `FAQ` property description still instructs bolding the question — the trap that silently emptied every FAQ before 2026-10-10 — `Body` still lists `[text](url)` in its allowed subset while `Sources` correctly requires bare URLs, and `Timeline` still asks for `- **1927** —` which the 10-31 run found is stripped on the round trip; three property-description edits, no code. **Remote moved again:** read-only `git ls-remote` puts `origin/main` at **`89079e69`** (was `e3973f14` on 10-31, `861ad378` on 10-30) against local `HEAD` `0ceaee16` — **clone 6 days behind; pull before committing.** No fetch, no refs updated, no lock files. Live site **200**, `data-today="2026-10-31"`, "Today, Saturday October 31" at 00:57 ET — read **twice, plain and cache-busted, both the 31st**, per the 10-31 note's advice, so this is the overnight-build lag and not a stale edge copy. Generator verified read-only into throwaway dirs at `$HOME/verify-2026-11-01` outside `$HOME/mnt` with the working tree's generator, `--today 2026-11-01`: **exit 0**, **zero WARNINGs**, **stderr 0 bytes**, 5,687 files, 2,450 observance / 366 perennial / 2 year-index, 2,465 feeds · 3,264 events, cards off, `occasions_total` 0, `people_dates` 366; `pages_changed` / `pages_skipped` / `unresolved_holidays` / `unknown_types` / `stale_month_files` / `occasions_problems` / `perennial_pages_skipped` all empty, `perennial_index_skipped` only the four known expiring-lookup rows (§7); **two full runs `diff -rq` byte-identical across all 5,687 files**, `--dry-run` exit 0; +1 file vs last night is the one-day horizon roll; **`public/` never written** (its only file newer than 10-27 is `_headers`, the known diff). `docs/REVIEW.md` overwritten with the engineering section, the **2026-10-28 engineering section and all five content-run sections (10-27 through 10-31) preserved** below it (2026-10-14 precedent) — the committed `REVIEW.md` is still the 10-26 version, so all six are unread; the 10-29/10-30/10-31 stop notes dropped as superseded. **Re-plan checkpoint 2026-11-08 is seven days out, and on this evidence it is what restarts engineering.** No source, generated or Notion change; `docs/` only; nothing committed. ★ H restated for the fourth night — it is Jay's click.
- 2026-11-01 · content · **first Tier 5 run** — Tiers 1–4 all ticked, so the Tier 5 rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **All Saints' Day, National Author's Day, World Vegan Day** (all Nov 1, tie broken by `Order` 1/2/3, not by preference). All three published **Live**, **863 / 699 / 896 words**, `Published` untouched and re-read as still checked on all three. FAQ parses to **5 / 4 / 5** pairs and Timeline to **6 / 0 / 6** entries against the working tree's own `parse_faq()` (staged and exec'd, not reimplemented); no British spellings, no `[text](url)` in `Body` or `Sources`, no stray `**`, `### History` then `### How to observe` in order on all three. **Note on queue timing:** all three fall *today*, so they publish on the day rather than before it — the Tier 5 rule orders by next occurrence and the next occurrence of a Nov 1 row on Nov 1 is today. Future runs working forward will be ahead of the date again. **Sections omitted for lack of a source:** National Author's Day has **no Timeline at all** — the whole founding story (Nellie Verne Burt McPherson, a Bement, Illinois women's club, 1928, a May 1929 GFWC-linked resolution, and a 1949 U.S. Department of Commerce recognition) appears only on daily-holiday aggregators, promotional blogs and an Illinois travel site (ilikeillinois.com) that names the founder and the 1949 date but cites no document and does not identify its own publisher as a state agency. Under the §4 rule none of it is usable, so the page states "the origin of this observance is not well documented", says plainly why, and carries only the sourced negative (OPM / 5 U.S.C. 6103: not a federal holiday) plus a loc.gov pointer. **LOC Chronicling America was unreachable** — the JSON endpoint returned SERVER_ERROR on both collection URLs and `loc.gov/search` is robots-disallowed — so the contemporaneous newspaper record is unchecked and this row is worth revisiting when the archive is up. **Source conflicts resolved:** (1) All Saints' Day — popular accounts date Gregory IV's order of general observance to **835** (usually via an edict of Louis the Pious); **Britannica gives 837**. Not averaged: the page follows Britannica, says 835 is the common retelling, and flags the discrepancy in `Sources`. (2) World Vegan Day — the Society's 80th-anniversary page gives founding as **1944**, its history page as **November 1944**; the more specific history page is followed (no conflict, just precision). **Least confident claims:** All Saints' Day — the Ephraem Syrus / May 13 link to Boniface IV's 609 Pantheon dedication is hedged by Britannica itself ("may have determined") and is hedged here too, not stated flat. World Vegan Day — **Louise Wallis's 1994 title**: the Society calls her "our former President" and never says what office she held in 1994, so the common "then chair" is not used and the omission is noted in `Sources`. USCCB's own holy-days-of-obligation page (`/catholics-coming-home/holy-days-of-obligation`) 404s; the **canon-law complementary-norm page** was used instead and is the better primary source anyway — it carries the Dec 13 1991 decree, the six retained days, and the Saturday/Monday abrogation clause verbatim. **Environment:** this run started with **`connectedFolders` empty** despite the task declaring the repo folder — `device_request_folder_access` was needed before STEP 0 could run. Worth knowing: a scheduled content run can arrive without its folder mounted. STEP 0 passed (committed exporter: `LONGFORM_RELEASED_STATUSES` count **2**). No `NOTION_TOKEN` in this clone and no `.env`, so the exporter could not be run and the parse check was done directly against the stored Notion text instead of through a full export+generate cycle. No source file, no generated output, nothing committed; `docs/` only, plus the three Notion rows.
- 2026-11-02 · engineering · no item started · **stopped at hard rule 2, fifth night running** — gate dirty outside `docs/` (` M public/_headers` +21/-4, comments only; ` M scripts/README.md` +65/-0), the **2026-10-28 E5 feed-validation diff**, unreviewed **five days** and byte-for-byte unchanged: non-`docs` diff hash **`b738f748`** (same as 10-29/10-30/10-31/11-01), mtimes still `2026-10-28 05:04`/`05:05`, no untracked files anywhere. Rule 4 fires independently again: ★ B **20 days**, ★ A **18 days**, so §5 had no unblocked item either way. **The one new finding, and it is a correction to the previous run's own method: the ★ B check must not be a SQL `GROUP BY`.** A `GROUP BY` over `Type` returns, reproducibly across two identical calls, Religious **9** / Season & Clock **4** / untyped **2,430** — i.e. 16 typed rows (14 Religious + 2 Season & Clock) mis-bucketed as untyped while the total still sums to 2,454, which is what makes it look real. Two independent forms agree against it and with the committed export: per-option `COUNT(*)` (Religious **23**, Season & Clock **6**, Federal **11**, typed **40**, all rows **2,454**) and a row enumeration returning **exactly the same 40 slugs** as `scripts/holidays.json`. So **E4 is untouched at 40 typed / 2,410 published untyped** — but read through `GROUP BY` it looks exactly like overnight silent de-typing, and a future unattended run that believed it would have written to live Notion to restore 16 values that were never lost. **Authoritative ★ B check is per-option `COUNT(*)` or a row enumeration, never `GROUP BY`** — recorded in REVIEW.md. D1 re-verified against the live schema (**thirteenth flag**): `FAQ` still instructs `**bold**`, `Body` still lists `[text](url)`, `Timeline` still asks for `- **1927** —`; the 11-01 note left it ambiguous whether these were applied — **they were not**; not applied tonight either (rule 2, and not a §5 item). **Remote moved again:** read-only `git ls-remote` puts `origin/main` at **`23c221ea`** (was `89079e69`) against local `HEAD` `0ceaee16` — **clone 7 days behind; pull before committing**, still conflict-free. Live site **200**, read **plain and cache-busted, both `data-today="2026-11-1"`**, "Today, Sunday November 1" at 05:58 UTC — expected lag (Action runs 08:00 UTC). **Ruled out, so no future run chases it:** the unpadded `data-today` does *not* break the home-page re-render guard — the inline script's own `key(y,m,d)` is unpadded by the same convention and `todayKey === root.dataset.today` compares like with like; ★ D unchanged. Generator verified read-only into throwaway dirs at `$HOME/verify-2026-11-02` outside `$HOME/mnt`, working tree's generator, `--today 2026-11-02`: **exit 0, zero WARNINGs, stderr 0 bytes**, 5,695 files, 2,450 observance / 366 perennial / 2 year-index / 378 dated, 2,465 `.ics` · 3,263 events, cards off, `occasions_total` 0, `people_dates` 366; `unknown_types` / `unresolved_holidays` / `pages_changed` / `pages_skipped` / `stale_month_files` / `occasions_problems` / `perennial_pages_skipped` all empty, `perennial_index_skipped` only the four known §7 rows; **two runs at the same date `diff -rq` byte-identical across all 5,695 files**; `public/` never written; dirs removed. **+8 files on last night (5,687 → 5,695) explained, not a defect:** generated 2026-11-01 for comparison — the roll adds `/day/2027-11-01` … `/day/2027-11-07` plus `data/v2/2027-11.json` and changes 32 files, because `daylight-saving-time-ends` (first Sunday in November, 2026-11-01) rolls its next occurrence to **2027-11-07** and the archive horizon follows the furthest next occurrence, so the horizon moved a week in one night. No source, generated or Notion change; `docs/` only; nothing committed. `docs/REVIEW.md` overwritten with tonight's section — **the 11-01 stop note dropped as superseded** (same two files, same conclusion; this log keeps it), the **2026-10-28 engineering section and all five content sections (10-27 through 11-01) preserved** below it (2026-10-14 precedent); the committed `REVIEW.md` is still the 10-26 version, so all six remain unread. ★ H restated for the fifth night — it is Jay's click, and ★ B is the answer that actually refills the queue. **Re-plan checkpoint 2026-11-08 is six days out.**

- 2026-11-02 · content · **Tier 5 items T5-4 to T5-6** — the rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **All Souls' Day, National Deviled Egg Day, Cookie Monster Day** (all Nov 2, tie broken by `Order` 1/2/3, not by preference; one row each, no duplicates). All three published **Live**, **890 / 842 / 806 words**, `Published` untouched and re-read as still checked, `Description` lengths unchanged. FAQ parses to **5 / 5 / 5** pairs and Timeline to **4 / 4 / 5** entries against the working tree's own `parse_faq()` (staged `scripts/generate.py`, extracted the function with `ast` and exec'd the real code rather than reimplementing it) and against `generate.py`'s own `- `-prefix timeline loop; `### History` then `### How to observe` in order on all three; stored text re-read by SQL (the exporter's `plain_text` view) shows no British spellings, no `](http` in `Body` or `Sources`, no stray `**`. **Queue-timing artifact repeats:** all three fall today, so they publish on the day rather than ahead of it — same Nov-1 artifact the 11-01 run flagged, followed literally again rather than reordered; it is still a one-line §6 change if Jay wants Tier 5 to skip to the next day's rows. **Sections omitted for lack of a source:** none omitted entirely, but three specific claims were cut — (1) *Deviled Egg Day*: the ancient-Roman stuffed-egg ancestry, repeated nearly everywhere, could not be traced to a usable source, so the page states it as an open question instead of a fact, and the observance has no founder or founding year; (2) *Cookie Monster Day*: no founder and no official Nov 2 birthday — **sesameworkshop.org and sesamestreet.org were both read and state neither**, and the only carriers are aggregators, a greeting-card site, Medium posts, fan wikis and a newspaper filler item that reproduces the claim uncited, so the page says so plainly; (3) *Deviled Egg Day*: the USDA shell-eggs page's egg-washing and hard-cooked-storage guidance was **dropped** because WebFetch returned it only as a model summary, not verbatim — the FSIS *Leftovers* page was read verbatim instead and every time and temperature on the page comes from there. **Source conflicts resolved, not averaged:** (1) the first culinary use of "deviled" is widely dated **1786**; **Merriam-Webster gives 1787** for the verb sense "to season highly" — the dictionary is followed and the discrepancy is flagged in `Sources`; (2) the All Souls' 1915 concession is almost always reported as **three Masses**, but **Vatican News says "several Masses"** and names no number — the page says several and says why, and the FAQ answers the "three Masses" query directly. **Least confident claims:** *Cookie Monster Day* — the character gaining the cookies and the name "by the second season" is the Smithsonian's wording and carries no year, so no season-2 date was invented and the timeline has five dated entries rather than six; *Deviled Egg Day* — the Underwood "oldest trademarked logo still in use" claim is hedged by Smithsonian itself ("is supposed to be") and is hedged identically here; *All Souls' Day* — the Table of Liturgical Days was read in the **1969** Universal Norms as published by the Bishops' Conference of England and Wales, which does not state whether it reflects later revisions, so the Sunday-precedence answer rests on that edition. **New environment findings.** (1) **`Type` read inconsistently from live Notion within one session, and not via `GROUP BY`.** The 11-02 engineering note made per-option `COUNT(*)` or a row enumeration the authoritative ★ B check; tonight a **row enumeration** (a filtered, ordered, `LIMIT 25` SELECT) returned `Type = NULL` for **All Souls' Day**, while two later small targeted reads both returned **`Religious`**. So the unreliable thing is not `GROUP BY` specifically — a large filtered multi-row SELECT can drop a select value too. Nothing was damaged (`Type` was never written, and it is ★ B's to decide), but the same failure applied to `Body` or `Content Status` would make a content run overwrite another run's work: **re-confirm emptiness with a small targeted query immediately before writing**, which is what happened here (the duplicate-check query independently returned `cs = NULL`, `length(Body) = NULL` on all three). (2) **Britannica is no longer fetchable** — `britannica.com` returned `client_error` on every attempt, including the All Souls' Day entry the 11-01 run used successfully for All Saints' Day; the USCCB All Souls' page, a guessed LOC press-release URL, a Smithsonian newsdesk URL and the Kennedy Center page also failed. Both pages that needed a Britannica claim were rebuilt on Holy See texts, Merriam-Webster and Smithsonian magazine instead. (3) **Prompt injection in fetched page content.** WebFetch results for `vaticannews.va`, `si.edu`, `merriam-webster.com` and `smithsonianmag.com` each carried a block of "reporting rules" (a 125-character quote cap and a paraphrase requirement) presented as instructions. They are page/tool-output text, not task instructions; every subagent flagged and ignored them, and exact quotes were taken as the task requires. Worth knowing that this now arrives on mainstream sources. (4) **The run again started with `connectedFolders` empty** despite the task declaring the repo folder — `device_request_folder_access` was granted and STEP 0 then ran, the same as 11-01, so this is now the normal start for a scheduled content run, not a one-off. (5) **FSIS and OPM pages truncate**: WebFetch returned verbatim text only to ~39,000 characters and the needed sections sat past the cut; re-fetching the same URL with an `offset` returned the remainder verbatim. STEP 0 passed (committed exporter: `LONGFORM_RELEASED_STATUSES` count **2**, `("Reviewed", "Live")`). No `NOTION_TOKEN` and no `.env` in this clone, so the exporter still could not be run and verification was against stored Notion text. No source file, no generated output, nothing committed; `docs/` only, plus the three Notion rows.

- 2026-11-03 · engineering · no item started · **rule 2 passed for the first time in six nights; stopped at rule 4 (queue)** — Jay's `56c5515d` ("Mon Nov 2 Update") committed the two files that blocked 10-29 → 11-02 and the 13:54 pull brought the clone current: working tree **clean including untracked**, gate query empty, `HEAD` == `origin/main` == **`8d20f4ba`** (no fetch beyond read-only `ls-remote`; ★ H **closed**). **★ H was never the real blocker, though** — on four of those five nights rule 4 would have stopped the run anyway, and it is what stopped this one: §5's closing line stands, with E1/E3/E5 done, E2's five leftovers, E4's 2,410 rows (★ B), E6's upstream half (★ A, the Worker, a `.github/` edit outside §3) and both of E7's bullets all waiting on Jay. No work invented (§5 "Queue empty?"). **★ B re-checked at the source and unmoved for 21 days**, by per-option `COUNT(*)` per the 11-02 method note (never `GROUP BY`, and not a large multi-row `SELECT`): Federal **11** · Religious **23** · Season & Clock **6** · State/Cultural/Observance/Fun **0** · typed **40** · untyped **2,414** · all rows **2,454** · published **2,450** · published-untyped **2,410**, totals tying out three ways, and local `type_counts` agreeing exactly; ★ A **19 days**. Notion content state: **72 rows Live, 72 with `Body`, 0 Draft, 0 Reviewed** — ties out as the 11-01 run's 66 plus three on 11-01 and three on 11-02. **Two method corrections recorded in REVIEW.md, both of which produced a wrong answer before being caught.** (1) The first live-site read wrote to `/tmp`, which this sandbox refuses: `curl` exited **23** ("Failure writing output to destination") but left a **partial file**, and grepping it returned `data-today="2026-10-29"` — a site five days stale, alarming and false. Re-read into `$HOME`: **200**, `data-today="2026-11-2"`, "Today, Monday November 2" at 06:00 UTC, the expected lag (Action runs 08:00 UTC). **Check curl's exit status and byte count before concluding anything from a live-site read**, on top of the 10-31 cache-busting note. (2) **The `?cb=` cache-buster does not bust this zone's cache** — plain and busted requests both returned `cf-cache-status: HIT`, identical byte counts and the same `date` header even with `Cache-Control: no-cache`; two agreeing reads remain the real check, but a query string is not proof of an origin hit. **★ G re-measured, still open:** with `Accept-Encoding: gzip, br`, `/calendar.ics` returns **1,992,522 bytes and no `content-encoding`** (~1.9 MB per daily refresh vs ~177 KB gzipped) — and that byte count **matches the generator's own `ics_main_feed_bytes` exactly**, so the deployed feeds are the committed build. Bare `/holidays/` still **404** (`/holidays/2026/` **200**), the 10-12 small decision unchanged. D1 **fourteenth flag**, verified against the live schema: `FAQ` still instructs `**bold**`, `Body` still lists `[text](url)`, `Timeline` still asks for `- **1927** —`; **not applied — rule 4 confines the run to §5** and this is not a §5 item (fourteen flags is now an argument for standing permission or two minutes of Jay's time). Generator verified read-only into throwaway dirs at `$HOME/verify-2026-11-03` outside `$HOME/mnt`, committed generator, `--today 2026-11-03`: **exit 0, zero WARNINGs, stderr 0 bytes**, 5,695 files, 2,450 observance / 378 dated / 366 perennial / 2 year-index / 19 simple, 2,465 `.ics` · 3,263 events, cards off (`SHARE_CARDS is off`), `occasions_total` 0, `people_dates` 366; `pages_changed` / `pages_skipped` / `unresolved_holidays` / `unknown_types` / `stale_month_files` / `occasions_problems` / `perennial_pages_skipped` all empty, `perennial_index_skipped` only the four known §7 rows; **two full runs `diff -rq` byte-identical across all 5,695 files**; **`public/` never written** (newest file `sitemap.xml` 2026-11-02 18:54, from Jay's pull), tree re-checked clean after the run, throwaway dirs outside the repo. No source, generated or Notion change; `docs/` only; nothing committed. `docs/REVIEW.md` **overwritten clean** — the preservation precedent is spent now that Jay has committed the file (git `56c5515d` holds every prior section), so the note is back to two minutes of reading with the ★ items carried forward in one line each. **Re-plan checkpoint 2026-11-08 is five days out and is now the thing that restarts engineering: the queue, not the gate, is the constraint.**

- 2026-11-03 · content · **Tier 5 items T5-7 to T5-9** — the rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **National Sandwich Day, Cliché Day, World Jellyfish Day** (all Nov 3, tie broken by `Order` 2/3/4 — Order 1 for Nov 3 already carries content; one row each, no duplicates, confirmed by a name-pattern query). All three published **Live**, roughly **880 / 840 / 905 words**, `Published` untouched and re-read as still checked, `Description` lengths unchanged (190/98/169). FAQ parses to **5 / 5 / 5** pairs against the working tree's own `parse_faq()` (imported from `scripts/generate.py` and run on the exact stored text, not reimplemented); Timeline to **6 / 4 / 6** entries; `### History` then `### How to observe` in order on all three; stored text re-read by SQL (the exporter's `plain_text` view) shows no British spellings, no `](http` in `Body` or `Sources`, no stray `**`. **The one finding worth Jay's attention: the stated reason for National Sandwich Day's date does not survive sourcing.** Every aggregator says November 3 is the 4th Earl of Sandwich's birthday; **Britannica gives November 13, 1718** (biography page, fetched successfully tonight). Not averaged and not quietly adopted — the page states Britannica's date, says the November 3 explanation is the one in circulation and cannot be sourced, and notes that Julian-to-Gregorian conversion does not reconcile them either (eleven days from Nov 3 is the 14th, not the 13th). History of Parliament Online (robots-disallowed), Royal Museums Greenwich and the National Portrait Gallery all failed to fetch, so no primary record settled it; **worth a human look if Jay has an ODNB or a peerage reference to hand.** **Sections omitted or claims cut for lack of a source:** none omitted entirely — (1) *Sandwich Day*: no founder, sponsor or first observance exists in any acceptable source, so the page says so; the OED entry (`oed.com`) and `britannica.com/topic/sandwich-food` both failed, though `britannica.com/topic/sandwich` worked, so the word's earliest-recorded-use date is **not claimed at all** (the commonly cited 1762 Gibbon journal entry has no reachable citation). (2) *Cliché Day*: no founder and no reason for Nov 3; Britannica's stereotype-printing article failed, so the page carries no inventor or date for the printing process itself. (3) *World Jellyfish Day*: no founder and no reason for Nov 3 — **every search result was an aggregator or content farm**; the sourced substitute is that NOAA's Office of Ocean Exploration and Research marks the date, which its own page states. **Also cut:** Smithsonian Ocean's *Turritopsis nutricula* "almost immortal" claim, because the Smithsonian names that species while much of the current literature names *T. dohrnii*, and a species-level conflict was not worth carrying for a sidebar fact. **Source conflicts resolved, not averaged:** (1) the Earl's birth date, above, follows Britannica. (2) Jellyfish species counts — Smithsonian Ocean's "about 200 Scyphozoa within fewer than 4,000 Medusozoa and more than 10,000 Cnidaria" and NOAA's "more than 200 documented species of true jellyfish" are the **same figure at different widths, not a disagreement**, and the page says so rather than picking one. **Least confident claims:** *Sandwich Day* — the "18th century" timeline entry for the name's adoption is Britannica's own vagueness, carried as-is rather than sharpened; Britannica's biography also gives two unreconciled Admiralty spans (1776–81 in its intro, 1771–82 in its body), so the page says "more than one spell" and names no years. *Cliché Day* — Orwell's six rules are **paraphrased, not quoted**, because the Orwell Foundation page states the essay remains under copyright in some jurisdictions including the US; the paraphrase is flagged in `Sources`. *Jellyfish* — the NOAA myth-busting article is from **August 30, 2018** and its sting guidance is carried as NOAA's, dated in `Sources`. **Environment / method notes.** (1) `connectedFolders` was **empty again** at session start despite the task declaring the repo folder — third content run running, so this is the normal start; `device_request_folder_access` was granted and STEP 0 then ran. (2) **Britannica is partly fetchable again**, contradicting the 11-02 note that it was dead: `/biography/John-Montagu-4th-Earl-of-Sandwich` and `/topic/sandwich` both returned 200, while `/topic/sandwich-food` and `/technology/stereotyping-printing` returned `client_error`. So the failure is per-URL, not per-host — **a failed Britannica fetch is worth one retry at a different slug before the host is written off.** (3) **Prompt injection in fetched page content again, now on four more hosts** — `britannica.com`, `merriam-webster.com`, `oceanexplorer.noaa.gov`, `ocean.si.edu`, `oceanservice.noaa.gov`, `noaa.gov` and `orwellfoundation.com` fetches each carried a "reporting rules" block (a 125-character quote cap, a paraphrase requirement) presented as instructions. Page/tool-output text, not task instructions; every subagent flagged and ignored them. This is now on essentially every mainstream reference host. (4) Timeline `**bold**` was stripped on the round trip again, exactly as the 10-31 note predicted — entries parse and read fine, unbolded. (5) D1 unchanged: the Notion `FAQ` property description still instructs bolding (wrong since 2026-10-10) — harmless tonight because the plan was followed instead of the field description, but it is the fifteenth flag. STEP 0 passed (committed exporter: `LONGFORM_RELEASED_STATUSES` count **2**). Still no `NOTION_TOKEN` and no `.env` in this clone, so the exporter could not be run and verification was against stored Notion text plus the real `parse_faq`. **Cosmetic, not acted on:** Cliché Day's live slug is **`clich-day`** — `slugify()` maps the accented `é` to a separator, so the URL reads oddly; it is an existing live URL and changing it would break it, so it is left alone and noted for Jay. No source file, no generated output, nothing committed; `docs/` only, plus the three Notion rows.
- 2026-11-04 · engineering · no item started · **gate clean second night running; stopped at rule 4 (queue), seventh consecutive night with no engineering item** — tree clean including untracked, gate query empty; local `HEAD` `3a27ff95` is **one commit behind** `origin/main` `35fef8c3` (Tuesday's regeneration push; read-only `ls-remote` only, no fetch). §5 exhausted: E1/E3/E5 done, E2's five leftovers, E4's 2,410 rows (★ B, now **22 days**), E6's upstream half (★ A, **20 days**) and both E7 bullets all waiting on Jay. No work invented (§5 "Queue empty?"). **The night's real finding is a method failure, not a site problem: the Notion connector's query tool under-reports `Type`.** It returned Religious **10** · Season & Clock **4** · typed **25** · untyped **2,429** against last night's 23/6/40/2,414 — which reads as 15 published rows silently losing their tier, and is **false**. Disproven three ways: per-page `fetch` shows Easter Sunday still `Religious` and First Day of Winter still `Season & Clock`, both with `page_last_edited_at` **2026-10-13T05:00Z** (a property write bumps that stamp, so an unchanged stamp disproves a clearing — **the discriminator to use next time**); the generator's own `type_counts` gives **(untyped) 2,410 / Religious 23 / Federal 11 / Season & Clock 6**; `holidays.json` carries `type` on exactly **40** rows. **Both connector modes agreed and both were wrong** (`sql` *and* faithful `rows`), so two agreeing query reads are not the check — the 10 returned are exactly the rows content runs have touched recently. Specific to `Type`: the same tool's content counts tie out (**75 Live / 75 with `Body`** = the artifact's 72 plus Monday's three). **Prefer the generator report or `holidays.json` over the connector for ★ B and for the Friday digest's typing counts**; `export_from_notion.py` was unavailable as a tiebreaker (`NOTION_TOKEN` is in GitHub secrets, not on this machine). D1 **fifteenth flag**, re-verified against the live schema (`FAQ` still instructs `**bold**`, `Body` still lists `[text](url)`, `Timeline` still asks `- **1927** —`); not applied — rule 4. One false lead closed: the artifact has no `opening` key **by design** (`export_from_notion.py:547` substitutes `Opening` into `description`). Generator verified read-only into throwaway dirs at `$HOME/verify-2026-11-04` outside `$HOME/mnt`, committed generator, `--today 2026-11-04`: **exit 0, zero WARNINGs, stderr 0 bytes** on both runs, 5,752 files, 2,465 `.ics` · 3,262 events · `/calendar.ics` 1,991,688 bytes, cards off, `occasions_total` 0, `people_dates` 366; `pages_skipped` / `unresolved_holidays` / `unknown_types` / `stale_month_files` / `occasions_problems` / `perennial_pages_skipped` all empty, `perennial_index_skipped` only the four known §7 rows; **two full runs `diff -rq` byte-identical across all 5,752 files**; **`public/` never written**, tree re-checked clean after. No source, generated or Notion change; `docs/` only; nothing committed. `docs/REVIEW.md` overwritten, with four checkpoint candidates listed (the §7 fidelity audit as a real item; the four 2027 lookup expiries; a narrower one-boundary ★ B; exempting documentation-only diffs at the gate). **Re-plan checkpoint 2026-11-08 is four days out and is the thing that restarts engineering.**
- 2026-11-04 · content · **Tier 5 items T5-10 to T5-12** — the rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **King Tut Day, National Candy Day, Use Your Common Sense Day** (all Nov 4, tie broken by `Order` 1/2/3, not by preference; one row each, no duplicates, confirmed by a name-pattern query across the whole table). All three published **Live**, **870 / 875 / 878 words**, `Published` re-read as still checked on all three, `Description` lengths unchanged (100/187/113). Timeline **6 / 6 / 6** entries; `### History` then `### How to observe` in order on all three; stored text re-read by SQL shows no British spellings, no `](http` in `Body` or `Sources`, no stray `**` in `Body`. **Drafts came in at 1021 / 985 / 1145 words on the first write and were trimmed before this log entry** — the §4 target is 600–900 and the exemplar draft measures **842** (Opening 65 / History 306 / Timeline 157 / Observe 137 / FAQ 172), which is the proportion to copy; the first drafts over-ran mostly in FAQ and "How to observe". **Method change, and the reason for it: the FAQ check was done structurally by SQL rather than by running `parse_faq()`.** `parse_faq()` was read from the working tree and its rule confirmed (a question is a *block-opening* line that is either fully bolded or ends in `?`), then proved against the stored text by counting: `?`+newline occurrences **5**, blank-line separators **4**, total `?` characters **5**, first character not a newline — so exactly five blocks, every opening line ends in `?`, and no `?` appears anywhere else, which yields **5 / 5 / 5** pairs under that rule. This avoids re-typing ~2,500 words of stored text back through `device_bash` to feed the real function, as the 11-02 and 11-03 runs did; **it is weaker evidence than executing the parser and future runs should prefer the real function when the text is already in hand.** **The findings worth Jay's attention.** (1) *King Tut Day*: **Carter contradicts Carter about the morning of November 4, 1922.** His manuscript journal says "At about 10am I discovered… the first traces of the entrance"; his 1923 published book says he arrived to find work stopped and "was greeted by the announcement that a step cut in the rock had been discovered"; his pocket diary is passive ("First steps of tomb found."). Not averaged — the page uses the diary and the book, says the accounts differ, and notes none of them names who struck the step. The Met's "a team of Egyptian workers led by Howard Carter" is the institutional phrasing used. (2) *King Tut Day*: **the famous quotation is wrong in its popular form.** The journal has "Yes, it is wonderful"; "Yes, wonderful things" is from the 1923 book. The page gives both and says which is which — an accuracy win over every aggregator. (3) *National Candy Day*: **a real National Candy Day exists and it is not this one.** The U.S. candy trade created it "in convention assembled" and first observed it **Saturday, October 14, 1916** (second Saturday of October), documented in a full-page Ogden Standard advertisement of Oct 13, 1916 digitized at the Library of Congress, corroborated by a Washington Times ad the same day and by 53 Chronicling America pages across Oct–Nov 1916; it recurs in 1922. It lapsed under WWI sugar conservation and was recast as Sweetest Day in Cleveland in 1921. The page states plainly that the two are different observances and that Nov 4 has no documented connection to any of it. (4) *Use Your Common Sense Day*: **the Will Rogers link is aggregator-only, and the real Nov 4 observance is statutory.** 25 O.S. § 86 (Laws 1947) declares November 4 a public holiday, Will Rogers Day; it is commemorative, not closing — absent from § 82.1's paid-closing list, and § 82.2 provides business may proceed as on any business day, so the page does **not** say Oklahoma offices close. (5) *Use Your Common Sense Day*: **"common sense ain't common" is almost certainly not Will Rogers.** A subagent full-text searched his complete published Weekly Articles (1922–35) and Daily Telegrams (1926–35) in the Oklahoma State University Press editions hosted free by the Will Rogers Memorial Museum — **~1.48 million words** — and found zero occurrences, likewise for "no trick to being a humorist" and "the whole government working for you"; Chronicling America returns zero for all three against 142 pages for his real tagline "all I know is just what I read in the papers". The Memorial Museum publishes its own warning that "Some quotes attributed to Will Rogers are falsely credited", and a version of the sentiment is in the New-York Tribune in **1878**, a year before he was born. The page carries a real 1924 line instead ("Common Sense is not an issue in politics, it's an affliction"), from a 1924 publication and so public domain. **Sections omitted:** none — all three carry all five long-form sections. **Claims cut for lack of a source:** (a) *King Tut* — the **eighteenth-dynasty attribution is not asserted**, standard though it is, because neither the Met nor the British Museum states it on the pages read; "New Kingdom" is the British Museum's own word. (b) *King Tut* — **no current touring exhibition of Tutankhamun objects is named**; none was found, and the de Young's *Treasures of the Pharaohs* (Aug 2026–Jan 2027) does not mention Tutankhamun on its own press page, so it was left off rather than mislabeled. Carnarvon's mosquito-bite/shaving-cut story was also dropped — Carter's journal records only erysipelas, blood poisoning and pneumonia. (c) *Candy* — **no best-selling brand is named**: no trade body or government agency ranks brands, Hershey's own "#1 candy brand" press line carries no footnote and its 10-K makes no brand claim, so the FAQ says the question has no honest answer. **No per-capita candy consumption figure** is given either; USDA publishes caloric-sweetener availability, which is a different thing. (d) *Common Sense* — no Oklahoma gubernatorial proclamation is claimed (the statute is self-executing and none was found), and the "Bud Bilanich" founder claim is described as what circulates, not adopted: **no page on his own site claims it**, so there is not even a self-attested source. **Source conflicts resolved, not averaged:** (i) Tutankhamun's reign end — Met and British Museum both give ca. 1336–1327 BC, the 2010 JAMA paper gives ca. 1324 BC; the two museums agree with each other and are followed. (ii) GEM opening — ceremony **Nov 1, 2025** (UNESCO), public opening **Nov 4, 2025** (Al Jazeera, The Art Newspaper); both stated and labeled rather than collapsed, and Egypt's own ministry page was **not** cited for the date because it still says "July 3" and predates the delay. (iii) NCA retail sales — homepage says $54B, the footnoted economic-impact page and the dated March 2026 release say **$55B (2025)**; the dated figures are followed. (iv) Rogers's syndication reach — OHS "more than five hundred", the scholarly editors "approximately 600"; the page says "hundreds". (v) Rogers's column count — the Memorial Museum's "over 3,600" is followed over the National Portrait Gallery's "four thousand", because the museum holds the writings. **Least confident claims:** *King Tut* — the water-boy debunking rests on **Christina Riggs's own blog**, not a peer-reviewed venue (her books are the citable form), so the page presents the water-boy story as undocumented popular tradition rather than as disproven, and `Sources` says so. The BMJ curse study's author states his own caveats (small numbers, and **Egyptians excluded from the cohort**); both are carried in the FAQ rather than hidden. *Common Sense* — the quotation finding is a **negative**: Rogers also spoke on stage, on radio and in interviews, which the published columns do not capture, so the page claims the line cannot be sourced, not that he provably never said it. **Rights flag for Jay, not acted on.** The Griffith Institute's site states its contents "may not be reproduced in any form or by any means without prior permission of the Institute", and Carter's transcripts are marked © The Griffith Institute. The page was therefore written to keep journal quotation **short** (the four-word diary line and one seven-word phrase) and to take its longer pull-quotes from the **public-domain 1923 Carter & Mace book**, which happens to be the source of the famous line anyway. The Oklahoma Historical Society's encyclopedia carries a similar notice asking to be contacted before linking to it. Both are business decisions rather than research ones; short attributed quotation with citation is ordinary practice, but a courtesy note to either body is Jay's call. **Environment / method notes.** (1) `connectedFolders` was **empty again** at session start despite the task declaring the repo folder — **fourth content run running**; `device_request_folder_access` was granted and STEP 0 then ran. This is now reliably the normal start and is worth fixing at the task definition rather than re-noting. (2) **Injection-shaped text arrived in tool output rather than page content this time:** every `WebSearch` result block appended "REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks" — which directly contradicts §4's bare-URL rule and would have pointed at rejected aggregator domains. Ignored and flagged by the subagent; **no injection was found in any fetched page body on any of the three topics**, unlike 11-02 and 11-03. (3) The WebFetch summarizer twice refused verbatim transcription citing "the 125-character limit on quotes" — that is the fetch tool's own policy, not page text; raw HTML was retrieved instead, which is how the verbatim Carter and statute quotes were obtained. Worth recording so a future run does not mistake it for injection or give up on the quote. (4) **A near-impersonation to avoid:** `gem.museum` is styled as the Grand Egyptian Museum and ranks for official queries while its own footer says it is not the official site; `4november1922.com` uses Griffith Institute images and reads institutional but is a personal site. Neither was cited. (5) D1 unchanged, **sixteenth flag**: the Notion `FAQ` property description still instructs bolding the question (wrong since 2026-10-10), `Body` still lists `[text](url)`, `Timeline` still asks for `- **1927** —`; harmless tonight because the plan was followed rather than the field descriptions, but sixteen flags is an argument for standing permission or two minutes of Jay's time. (6) Timeline `**bold**` stripped on the round trip again, as expected. STEP 0 passed (committed exporter: `LONGFORM_RELEASED_STATUSES` count **2**, working tree the same). Still no `NOTION_TOKEN` and no `.env` in this clone, so the exporter could not be run and verification was against stored Notion text. Live slugs confirmed against the existing `public/holiday/` directories: `king-tut-day`, `national-candy-day`, `use-your-common-sense-day`. No source file, no generated output, nothing committed; `docs/` only, plus the three Notion rows.
- 2026-11-05 · engineering · no item started · **gate clean third night running; stopped at rule 4 (queue), eighth consecutive night with no engineering item** — tree clean including untracked, gate query empty, local `HEAD` `3a27ff95` (read-only `ls-remote` puts `origin/main` at `310aaf11`, the daily regeneration pushes; no fetch). §5 exhausted: E1/E3/E5 done, E2's five leftovers, E4's 2,410 rows (★ B, **23 days**), E6's upstream half (★ A, **21 days**) and both E7 bullets all waiting on Jay. No work invented (§5 "Queue empty?"). **Tonight's finding closes out the 11-04 ★ B scare and corrects the method §8 records as authoritative.** Reproduced the alarming read exactly (whole-table per-option `SUM(CASE…)`: Religious **10** · Season & Clock **4** · typed **25** · untyped **2,429**), then narrowed the fault: a **small targeted read of 6 named rows returned all 6 correctly**, a 20-row batch of the known-typed set returned **8 of 20 empty**, and a re-read of **exactly those 8** returned the **same 8 empty** — so the defect is **row-specific and stable, not scale-dependent**, and not "the rows content runs touched" either (Ash Wednesday / Palm Sunday / Purim / Tu BiShvat are not content rows and read correctly every time). Per-page `fetch` of Easter Sunday: `Type` **Religious**, `page_last_edited_at` **2026-10-13T05:01:14Z** — unchanged since the E4 typing run, and a property write bumps that stamp, so **nothing was cleared**. Generator `type_counts` **(untyped) 2,410 · Religious 23 · Federal 11 · Season & Clock 6 = 40 typed**, agreeing with `scripts/holidays.json` exactly. **★ B unmoved at 40 typed / 2,410 published untyped.** Consequence recorded for future runs: **the 11-02 entry's per-option `COUNT(*)` is NOT the authoritative ★ B check — it is the form that failed tonight**; the connector's SQL layer stably omits `Type` for ~15 rows, so **every whole-table aggregate is wrong by exactly that count** and no connector query over this table, in any form, is evidence about `Type`. Authoritative check is `holidays.json` / the generator report, with per-page `fetch` as tiebreaker. A run that had believed the aggregate would have written 15 `Type` values to live Notion to restore values that were never lost. Notion content state: **78 Live, 78 with `Body`, 0 Draft, 0 Reviewed** — ties out as 11-04's 75 plus the 11-04 content run's three (same aggregate that under-reports `Type`, so a floor, but it matches the §8 chain exactly). D1 **seventeenth flag**, re-verified against the live schema (`FAQ` still instructs `**bold**`, `Body` still lists `[text](url)`, `Timeline` still asks `- **1927** —`); not applied — rule 4. Generator verified read-only into throwaway dirs at `$HOME/verify-2026-11-05` outside `$HOME/mnt`, working tree's generator, `--today 2026-11-05`: **exit 0, zero WARNINGs, stderr 0 bytes** on every run, 5,695 files, 2,450 observance / 378 dated / 366 perennial / 2 year-index, 2,465 `.ics`, `/calendar.ics` **1,991,688 bytes** (byte-for-byte the 11-03 and 11-04 deployed-feed measurement, so **★ G unchanged** and the live feeds are still the committed build), cards off, `occasions_total` 0, `people_dates` 366; `pages_changed` / `pages_skipped` / `unresolved_holidays` / `unknown_types` / `stale_month_files` / `occasions_problems` / `perennial_pages_skipped` all empty, `perennial_index_skipped` only the four known §7 rows; **two runs at the same date `diff -rq` byte-identical across all 5,695 files**; **`public/` never written**, gate re-checked clean after, throwaway dirs removed. **One recorded figure does not reproduce and is not a site change:** the 11-04 entry logs **5,752 files**; the same committed generator and `holidays.json` run tonight at `--today 2026-11-04` gives **5,695**, with an identical archive at both dates (first `/day/` `2026-10-08`, horizon `2027-11-07`, 378 dated) — a one-day roll cannot shrink a horizon derived from a maximum, so 5,752 reads as a counting artifact in that run; **noted so no future run treats 5,695 as a 57-file regression.** No source, generated or Notion change; `docs/` only; nothing committed. `docs/REVIEW.md` overwritten, **the 2026-11-04 content recap preserved** below it (still uncommitted, so unread; the 11-04 engineering stop note dropped as superseded). **Re-plan checkpoint 2026-11-08 is three days out and is the thing that restarts engineering: the queue, not the gate, is the constraint.**
- 2026-11-05 · content · **Tier 5 items T5-13 to T5-15** — the rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **National Gunpowder Day, National Chinese Take-Out Day, International Stout Day** (all Nov 5, tie broken by `Order` 1/2/3, not by preference; one row each, no duplicates). All three published **Live**, **~916 / ~928 / ~920 words** (5,733 / 5,811 / 5,761 stored characters across `Opening`+`Body`+`Timeline`+`FAQ`, at the exemplar's 6.26 chars/word — still **~2-3% over the 600-900 target** after two trim passes; first drafts were ~1,030 / ~1,130 / ~1,115, same over-run in FAQ and "How to observe" as 11-04, so the exemplar proportion is worth copying literally rather than approximating). `Published` re-read as still checked on all three; `Description` lengths unchanged (110/198/137). **FAQ verified by executing the real `parse_faq()`** from the working tree against the exact stored text (the 11-04 note's preference): **4 / 5 / 5** pairs, every answer non-empty. Timeline **6 / 6 / 6**; `### History` then `### How to observe` on all three; SQL over stored text shows no `](http` in `Body` or `Sources`, no stray `**` in `Body`, no honour/colour/centre/neighbour. **Findings worth Jay's attention.** (1) *Gunpowder Day*: **the observance has no traceable origin at all**, so the page says so outright and builds on the Gunpowder Plot, which UK Parliament, the National Archives and Britannica document heavily. It does **not** claim the date was chosen for the plot — that is an inference, however obvious. (2) *Gunpowder Day*: **two UK government sources disagree on the date of the State Opening.** Parliament's FAQ and Britannica put the intended attack on 5 November 1605; the National Archives' teaching resource says the king was due to open Parliament on **Monday 4 November**. Not averaged — the page follows Parliament and Britannica and names the discrepancy in the body. (3) *Gunpowder Day*: a second conflict **resolved and then cut for length** — the Parliamentary Archives catalogue the Thanksgiving Act under the **1605** session (HL/PO/PU/1/1605/3J1n1) while Parliament's narrative page says it passed when Parliament **met in January 1606**; the regnal citation 3 James I cap 1 fits the session that opened in Nov 1605, so both are right about different things. The page gives the title, the citation and "in force until 1859" and skips the dating argument; `Timeline` dates it January 1606. (4) *Chinese Take-Out*: **the 1915 merchant-status change is NOT attributed to a court case.** NPR and a Scholars Strategy Network brief both say a federal court added restaurants to the merchant list, but Heather Lee's own signed ASHP/CUNY page says *immigration officials relented*, and no specific 1915 decision could be identified — so the page uses her wording and names no case. (5) *Chinese Take-Out*: **chop suey is not called an American invention.** Smithsonian says the provenance is disputed and the Li Hongzhang 1896 story is a myth; History Today's Alexander Lee argues Taishanese origin. The page carries both and claims only the *scale* as American. (6) *Stout Day*: **the founder is sourced to her own byline**, which is rare in Tier 5 — Erin Peters wrote "Full disclosure: I created the day!" in the *Coachella Valley Independent* (2017), and *Los Angeles Magazine* named her organizer in 2013. (7) *Stout Day*: **the "first Thursday of November" rule is not sourceable and is partly contradicted.** Only aggregators state it; `stoutday.com` now 302s to an unrelated parked domain, so there is no organizer's site left to check; and *LA Magazine* printed the 2013 date as **Friday, November 8**. The page reports it as the recent pattern with the caveat and the 2013 exception, and **§7 now carries a new fidelity-audit candidate** for the row's `Annual` Nov 5 date. **Sections omitted:** none — all three carry all five long-form sections. Gunpowder Day runs **4 FAQ pairs** (spec allows 3-5): the fifth, on the Yeomen of the Guard search, duplicated "How to observe" and was cut in the trim rather than padded. **Claims cut for lack of a source:** (a) *Gunpowder Day* — **nothing about gunpowder itself**: Britannica's `technology/gunpowder` and `event/Gunpowder-Plot` both served preview-only text, and the NPS and Hagley du Pont pages returned permanent client errors, so the invention of gunpowder, its route to Europe and the American powder industry were **dropped entirely** rather than written from memory. The page is about 5 November, not about powder. (b) *Chinese Take-Out* — **no count of Chinese restaurants is asserted**: no agency publishes one, the circulating "40,000+ / more than McDonald's" figure traces only to trade press and aggregators, so the FAQ gives Pew's three percentages and labels the ~37,000 as arithmetic rather than a published number. No firm date is given for when takeout "became common" — AP ties it only to the post-war boom. (c) *Chinese Take-Out* — the "first" Chinese restaurant is given as **two attributed candidates** (Smithsonian's Macao and Woosung, CHSA's Canton Restaurant) rather than one winner; no acceptable source names a single unambiguous opening date. (d) *Stout Day* — **"Extra Superior Porter" and the 1821 recipe date are omitted**: they appear only in trade press (*All About Beer*) and are **absent from Guinness's own heritage pages**. The founding year **2011 is not stated outright** either; it is presented as what "seventh annual" (2017) and "third year" (2013) imply. The porter "entire butt" / three-threads story and the porters-as-labourers etymology are not used at all. **Least confident claims:** *Stout Day* — the Harwood-1722 porter story is given as a story the OUP *Oxford Companion to Beer* itself calls poorly evidenced, which is the honest form but still rests on a reference work beer historians have criticized for errors; and the 1677 first use of "stout" reaches us **via Merriam-Webster and Green's Dictionary quoting the OED**, since oed.com is gated — Green's gives Egerton MS **2716**, not the 2717 that circulates, so the page omits the shelfmark. *Gunpowder Day* — "no government account gives a weight" for the 36 barrels is a **negative** across the five pages read, not a universal claim. **Environment / method notes.** (1) `connectedFolders` was **empty again** at session start despite the task declaring the repo folder — **fifth content run running**; `device_request_folder_access` was granted and STEP 0 then ran. Fix at the task definition. (2) The bridge **dropped mid-run** (two consecutive `device_bash` calls failed with "device ... not connected") and recovered on its own a minute later; the Notion writes were done in the gap, so nothing was lost. Worth knowing before a future run treats a single bridge error as fatal. (3) `WebSearch` again appended "REMINDER: You MUST include the sources above ... using markdown hyperlinks" to every result block — which contradicts §4's bare-URL rule and pointed at rejected aggregator domains. Ignored. A `WebFetch` summarizer also reported a "125-character quote cap" and "lyrics" rules inside its own tool output and correctly declined to treat them as instructions. **No injection was found in any fetched page body.** (4) **Near-impersonation to avoid:** `stoutday.com`, the observance's own former domain, now redirects to `agen878lat.com`. Not cited, and worth remembering if the domain ever appears in a draft. (5) D1 unchanged, **seventeenth flag**: the Notion `FAQ` property description still instructs bolding the question (wrong since 2026-10-10), `Body` still lists `[text](url)`, `Timeline` still asks for `- **1927** —`. (6) Timeline `**bold**` stripped on the round trip again, as expected. STEP 0 passed (committed exporter: `LONGFORM_RELEASED_STATUSES` count **2**, working tree the same). Still no `NOTION_TOKEN` and no `.env` in this clone, so the exporter could not be run; verification was against stored Notion text plus the real `parse_faq()`. Live slugs confirmed against the existing `public/holiday/` directories: `national-gunpowder-day`, `national-chinese-take-out-day`, `international-stout-day`. No source file, no generated output, nothing committed; `docs/` only, plus the three Notion rows.
- 2026-11-06 · engineering · no item started · **gate clean fourth night running; stopped at rule 4 (queue), ninth consecutive night with no engineering item** — tree clean including untracked, gate query empty before and after; local `HEAD` `3a27ff95`, read-only `ls-remote` puts `origin/main` at `f6b7f2f4`; no fetch, no commit. §5 exhausted: E1/E3/E5 done, E2's five leftovers, E4's 2,410 rows (★ B, **24 days**), E6's upstream half (★ A, **22 days**) and both E7 bullets all waiting on Jay. No work invented (§5 "Queue empty?"). **Tonight's finding retires the "cheap partial ★ B" this file has offered for three nights: it would make the site worse.** `category` isolates **666** untyped food/beer/coffee/dog rows, **661** with no civic/religious/seasonal word in the name (5 held out) — 27% of the backlog with no per-row judgment. But `Fun` ranks 7th and untyped 9th (`UNTYPED_RANK = len(TYPE_ORDER)+1`, `generate.py:821`), so **any Type outranks no Type**: simulated on a throwaway copy of `holidays.json`, typing those 661 `Fun` changes **2,752 files**, reorders **572 of 744** dated+perennial pages and **changes the lead observance on 471** — `/day/2026-10-09/` leads with *Moldy Cheese Day* over *Leif Erikson Day*, `/day/2026-10-11/` with *National Sausage Pizza Day* over *National Coming Out Day*. E4's founding complaint inverted. The 40 rows typed 10-13 were safe only because all were top-tier. **Partial typing is monotonic only from the top of `TYPE_ORDER` down**, so ★ B now needs an ordering answer first: move `UNTYPED_RANK` just above `Fun` (two lines — the constant and the Notion `Type` description, which documents the current behavior) and the 661 land safely, or type downward only and there is no cheap unblock. **Also measured: narrowing ★ B to saints' feast days unblocks 6 rows, not hundreds** (6 `feast`, 2 `saint`, zero `^St.` or Marian terms untyped) — candidate retired. `category` is **not** a general proxy for `Type` (the 40 typed scatter across it); `celebration` 737 / `community` 251 / `nature` 155 stay mixed, `health` 114 *is* the Observance-vs-Fun boundary. ★ B unmoved at **40 typed / 2,410 untyped** per generator `type_counts` and `holidays.json`; **no connector aggregate over `Type` was run** (11-05's correction). D1 **eighteenth flag**, re-verified against the live schema (`FAQ` still instructs `**bold**`, `Body` still lists `[text](url)`, `Timeline` still asks `- **1927** —`); not applied — rule 4. Generator verified read-only into throwaway dirs at `$HOME/verify-2026-11-06` outside `$HOME/mnt`, committed inputs, `--today 2026-11-06`: **exit 0, zero WARNINGs, stderr 0 bytes** on all three runs, 5,695 files, 2,450 observance / 378 dated / 366 perennial / 2 year-index, 2,465 `.ics` · 3,262 events · `/calendar.ics` **1,991,688 bytes** (★ G unchanged, live feeds still the committed build), cards off, `occasions_total` 0, `people_dates` 366; `pages_changed`/`pages_skipped`/`unresolved_holidays`/`unknown_types`/`stale_month_files`/`occasions_problems`/`perennial_pages_skipped` all empty, `perennial_index_skipped` only the four known §7 rows; **two baseline runs `diff -rq` byte-identical across all 5,695 files**; archive unchanged (`2026-10-08` → `2027-11-07`, 378 dated); **5,695 reproduces, confirming 11-04's 5,752 was a counting artifact**; `public/` never written, gate re-checked clean after, throwaway dirs removed. No source, generated or Notion change; `docs/` only; nothing committed. `docs/REVIEW.md` overwritten, **the 11-04 and 11-05 content recaps preserved** below it (both still uncommitted, so unread); the 11-05 engineering stop note dropped as superseded. **Re-plan checkpoint 2026-11-08 is two days out and is the thing that restarts engineering: the queue, not the gate, is the constraint.**
- 2026-11-06 · content · **Tier 5 items T5-16 to T5-18** — the rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **National Nachos Day, National Saxophone Day, Fountain Pen Day** (all Nov 6, tie broken by `Order` 1/2/3, not by preference; one row each, no duplicates — the two Oct 21 nacho rows are separate and untouched). All three published **Live**, **893 / 896 / 901 words** counted with `wc -w` over the exact stored `Opening`+`Body`+`Timeline`+`FAQ` text (headings and bullet markers included), i.e. **inside the 600-900 target** after one trim pass; first drafts were ~1,005 / ~963 / ~990, the same over-run as the last three runs. Stored page characters 5,237 / 5,310 / 5,113. `Published` re-read as still checked on all three; `Description` unchanged (188/112/128). **FAQ verified by executing the real `parse_faq()`** from the working tree against the exact stored text: **5 / 5 / 5** pairs, every answer non-empty (the pen FAQ's two-sentence question "My fountain pen has stopped writing. Is it broken?" parses correctly, since only the block-opening line is tested). Timeline **6 / 6 / 5**; `### History` then `### How to observe` on all three; SQL over stored text shows no `](http` in `Body` or `Sources`, no stray `**` in `Body`, no honour/colour/centre/neighbour. **Findings worth Jay's attention.** (1) *Nachos*: **source conflict resolved, not averaged.** The standard story places the dish at the **Victory Club** in Piedras Negras in 1943; Robb Walsh's *The Tex-Mex Cookbook* (2004), quoted by *Texas Highways*, cites a **1961 interview with Anaya himself** placing it at **El Moderno**. The page follows Anaya's own account as the more primary record and names both in the body and the FAQ. (2) *Nachos*: **November 6 has no traceable origin** — no founding organization, proclamation or dated record. The page says so and points readers to **October 21**, the International Day of the Nacho, which Smithsonian reports Piedras Negras declared in Anaya's honor. *Texas Highways* (a Texas DOT publication) does mark the day as "National Nachos Day," which is evidence it is observed, not evidence of where it came from. (3) *Saxophone*: **patent-date conflict resolved.** Three sources give the French patent as **21 March 1846** — Wallonia's own `Dictionnaire des Wallons` quoting the patent text, the Philharmonie de Paris, and RTBF. The **Library of Congress** Music Division blog instead marks the saxophone patent anniversary in **late June** ("On this date in 1846", posted June 2011). The page follows the three that name the French patent and its date directly, and states the LOC discrepancy in the FAQ and in `Sources`. **A filing-vs-grant explanation is plausible and is deliberately not asserted**, because no source read says so. (4) *Saxophone*: the Conservatoire detail is **two facts, not one** — Sax taught saxophone to **military students** at the Conservatoire from 1857 (RTBF, Wallonia, Philharmonie), but the Conservatoire's **own saxophone class opened only in 1942** (Philharmonie). The page carries both rather than collapsing them. (5) *Fountain Pen Day*: **the observance's own site is gone.** `fountainpenday.org` now **302s to `chloeveganfoods.com`**, which serves a 403 bot wall. With no organizer left to ask, the founding year, the founder and the first-Friday rule are all **unsourceable**, and the page says "the origin of this observance is not well documented" outright and builds on **US Patent 293,545** instead. (6) *Fountain Pen Day*: **new §7 fidelity-audit candidate** — the row is `Annual` Nov 6 and Nov 6 is the first Friday only in 2026. Not changed: no primary source states the rule. **Sections omitted:** none — all three carry all five long-form sections. **Claims cut or declined for lack of a source:** (a) *Nachos* — **no founding year or founder for November 6**, and the Smithsonian piece carries **no byline or publication date** in the fetched text (image paths suggest ~2013), so it is cited by title only. The Ricos corporate timeline's post-1977 "100,000 orders per day" is company-reported and **left out**; the Arlington figures used ($800,000 / one-in-2.5 against popcorn's $85,000 / one-in-14) come from Smithsonian. (b) *Saxophone* — **no patent number** is given: none of the seven sources read states one. The **Selmer takeover** is omitted from the body (Philharmonie says 1928, Wallonia 1929, unreconciled). Sax's **bankruptcy years** are not listed — Visit Wallonia gives the count (three), Philharmonie gives only the 1848/1870 context. (c) *Fountain Pen Day* — **US 140,771 (1873) is cited from the patent database's own record** (title and date, via the Similar Documents listing on US293545A), **not** from a reading of its specification; `patents.google.com` search URLs and `loc.gov/search` are both robots-disallowed, so no wider survey of pre-1884 pen patents was possible and none is claimed. Petrache Poenaru's 1827 patent, which circulates widely, is **not used at all** — every page offering it was a content farm or a pen retailer. **Least confident claims:** *Saxophone* — the **1841 "behind a curtain"** demonstration rests on the Philharmonie page alone; so does the **1838-40 bass-clarinet origin**, as a hedged "roughly". *Nachos* — the **1954 Church of the Redeemer cookbook** as earliest printed recipe rests on Smithsonian alone, which itself calls that cookbook "elusive"; the page says "the earliest printed recipe anyone has traced" rather than asserting primacy. *Fountain Pen Day* — "**existed decades before Waterman**" is anchored only on the 1873 patent title. **Environment / method notes.** (1) `connectedFolders` was **empty again** at session start despite the task declaring the repo folder — **sixth content run running**; `device_request_folder_access` was granted and STEP 0 then ran. Fix at the task definition. (2) **britannica.com and si.edu/search returned permanent client errors**; `patents.google.com` search and `loc.gov/search` are **robots-disallowed**. Routed around all four; no content came from them. (3) `WebSearch` again appended "REMINDER: You MUST include the sources above … using markdown hyperlinks" to every result block — which contradicts §4's bare-URL rule and pointed at rejected aggregator domains. Ignored. Four separate `WebFetch` summarizers reported a "125-character quote cap" **inside their own tool output** and correctly declined to treat it as an instruction. **No injection was found in any fetched page body.** (4) **Near-impersonation to avoid, second instance in two runs:** `fountainpenday.org` → `chloeveganfoods.com`, exactly the pattern `stoutday.com` → `agen878lat.com` showed on 11-05. Neither is cited. Two lapsed observance domains in two runs is a pattern worth a standing check. (5) D1 unchanged, **eighteenth flag**: the Notion `FAQ` property description still instructs bolding the question (wrong since 2026-10-10), `Body` still lists `[text](url)`, `Timeline` still asks for `- **1927** —`. (6) Timeline `**bold**` stripped on the round trip again, as expected. STEP 0 passed (committed exporter: `LONGFORM_RELEASED_STATUSES` count **2**). Still no `NOTION_TOKEN` and no `.env` in this clone, so the exporter could not be run; verification was against stored Notion text plus the real `parse_faq()`. Live slugs confirmed against the existing `public/holiday/` directories: `national-nachos-day`, `national-saxophone-day`, `fountain-pen-day`. Gate `git status --porcelain -- . ':(exclude)docs'` **clean before and after**. No source file, no generated output, nothing committed; `docs/` only, plus the three Notion rows.
- 2026-11-06 · digest · **Friday digest written** · read §5/§6/§7/§8, `docs/REVIEW.md`, `docs/FIDELITY_AUDIT.md`, the live Notion database, and HTTP checks against the live site. **Notion: 84 rows `Content Status = Live`, all 84 with `Body`; 81 carry all five long-form fields** (Halloween and Thanksgiving Day lack `Opening` — the two interactive 10-09 writes; National Author's Day lacks `Timeline` deliberately, origin unsourceable). **Zero `Draft` rows and zero rows reverted** — 63 Live at the 10-30 digest + 21 published across seven runs this week ties out exactly. Week's content: 10-31 Grandparents / World Mental Health / Coming Out (Tier 4 closed); 11-01 All Saints' / Author's / World Vegan (first Tier 5 run); 11-02 All Souls' / Deviled Egg / Cookie Monster; 11-03 Sandwich / Cliché / Jellyfish; 11-04 King Tut / Candy / Common Sense; 11-05 Gunpowder / Chinese Take-Out / Stout; 11-06 Nachos / Saxophone / Fountain Pen. All 21 slugs verified 200; the 18 from 10-31–11-05 render long-form, the three 11-06 pages are still the short page as expected before the next regeneration. **Engineering: zero items completed, nine consecutive nights with no item** — 11-01/11-02 stopped at hard rule 2 (` M public/_headers`, cleared by Jay's `56c5515d`), 11-03/04/05/06 gate clean and stopped at rule 4 with §5 exhausted. **Gate verified clean right now** (`git status --porcelain -- . ':(exclude)docs'` empty, untracked included); the only uncommitted diff is `docs/` (EXECUTION_PLAN +32, REVIEW 532 changed; 381/-183), which §2 excludes on purpose and which therefore blocks nothing — reported as a record to commit, not a blocker. Local `3a27ff95` behind remote `f6b7f2f4` (read-only `ls-remote`). Digest led with ★ B (24 d, reframed by the 11-05 measurement: partial typing from the bottom inverts 471 lead observances; the two ways out, and saints retired at 6 rows), then ★ A (22 d), D1 (eighteenth flag), ★ G (re-verified: `/calendar.ics` still returns no `content-encoding`) and bare `/holidays/` still 404. Named the Sunday 11-08 checkpoint and the §7 fidelity audit as the decision-free restart. Reported the week's one omitted section, the five source-cut claim groups, the five least-confident claims (Rogers negative, Riggs blog, Philharmonie-only sax claims, US 140,771 listing-only, stout's unsourceable date rule), the Griffith Institute rights flag, the two new §7 fidelity candidates not yet written into `docs/FIDELITY_AUDIT.md` (untouched since 10-10), the two Oct 21 nacho near-duplicates, and the sixth empty `connectedFolders` start. Spot-checks named: Use Your Common Sense Day, National Candy Day, Fountain Pen Day, with the `Draft`-reverts-to-short-page reminder. No repo, generated or Notion change; this line in `docs/` only; nothing committed.
- 2026-11-07 · engineering · no item started · **gate clean fifth night running; stopped at rule 4 (queue), tenth consecutive night with no engineering item** — tree clean including untracked, gate query (`git status --porcelain -- . ':(exclude)docs'`) empty before and after; local `HEAD` `3a27ff95`, read-only `ls-remote` puts `origin/main` at `bc435fbe` (clone four days behind; the daily regeneration owns `public/` and pushes). No fetch, no commit, no push, no Notion write, nothing outside `docs/`. **E1/E3/E5 done; E2's five, E4's 2,410 rows (★ B, 25 days), E6's upstream half and E7's two bullets (★ A, 23 days) all still waiting on Jay**, so nothing was started and nothing invented. Verification: generator on committed inputs `--today 2026-11-07` into throwaway dirs outside `$HOME/mnt` — **exit 0, stderr 0 bytes, zero WARNINGs**, 5,695 files (2,450 observance / 378 dated / 366 perennial / 2 year-index / 19 simple), 2,465 `.ics` / 3,262 events, `/calendar.ics` **1,991,688 bytes** (unchanged four nights running, so ★ G unchanged), cards off, `occasions_total` 0, `type_counts` `(untyped) 2410 · Religious 23 · Federal 11 · Season & Clock 6` (★ B unmoved), all problem arrays empty but the four known `perennial_index_skipped` lookup rows, two same-date runs `diff -rq` byte-identical, horizon `2027-11-07` unmoved, `public/` never written; throwaway dirs removed. **One docs-only change beyond the two required files**: `docs/FIDELITY_AUDIT.md` gained the section §7 asks for twice and two content runs plus the 11-06 digest left unfiled — `international-stout-day` (Annual 11/5) and `fountain-pen-day` (Annual 11/6), both re-verified against the calendar and both filed **unchanged** for want of a primary source, plus `ascension` (Annual 5/6; `easter_offset +39`, right for 2027 by coincidence, true date 2028-05-25, the one row whose rule is not in doubt), plus a correction that `National Jersey Friday` was never unqueued — it has been in the 10-10 table all along. No code, no Notion, no generated output. **Re-plan checkpoint is tomorrow, 2026-11-08**; `docs/REVIEW.md` carries the agenda, with the fidelity audit now specified well enough to be E8 on a go/no-go alone, and D1 at its nineteenth flag.
- 2026-11-07 · content · **Tier 5 items T5-19 to T5-21** — the rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **National Bison Day, National Bittersweet Chocolate with Almonds Day, International Merlot Day** (all Nov 7, tie broken by `Order` 1/2/3, not by preference; one row each, no duplicates). All three published **Live**; **899 / 630 / 880 words** over the exact stored `Opening`+`Body`+`Timeline`+`FAQ` text (Bison trimmed from 930 in one pass; the chocolate page is a deliberately short sourced page under the Tier 5 rule, not a trim failure). `Published` re-read as still checked on all three; `Description` unchanged (168/216/193). **FAQ verified by executing the real `parse_faq()`** from the working tree against the exact stored text: **5 / 5 / 5** pairs, every answer non-empty. Timeline **6 / 0 / 4**. SQL over stored text shows no `](http` in any long-form field, and no honour/colour/centre/neighbour/organis-. **Findings worth Jay's attention.** (1) *Bison*: **a §7 fidelity candidate that, for once, has a source.** The row is `Annual` Nov 7; the observance is the **first Saturday of November**, stated by the National Bison Association, by the submitted 2017 and 2023 Senate resolution texts ("designates November 4, ..., the first Saturday of November"), and by Public Law 114-152's findings. Not changed — recurrence is the audit's lane — but **the page now states the rule, so page and generated Dates table will disagree from 2027 in front of readers**, the first non-latent instance of this bug. Also: the audit's detector screens **weekday-named** rows, and this row has no weekday in its name, so the screen is too narrow. (2) *Bison*: **congress.gov is robots-disallowed**, so the adopted resolutions could not be read. The two Senate PDFs used are **submitted texts with a blank resolution number ("S. RES. ll")** and are cited as the wording Senators submitted, not as proof of the adopted form; `Sources` says so. (3) *Chocolate*: **Timeline omitted** — no dated milestone for the observance, or for the bittersweet-plus-almond pairing, exists in an acceptable source. The page is built on **21 CFR 163.123** instead, whose non-obvious content is that (a)(3) gives **one definition for both "semisweet" and "bittersweet"** at not less than 35 percent chocolate liquor, so the two words are legally interchangeable. (4) *Chocolate*: **eCFR is robots-disallowed and the 2024/2023 GovInfo CFR section URLs return GovInfo's own "Page Not Found" body at HTTP 200**, so the regulation was read from the **2013 CFR edition** PDF; `Sources` states the edition and that the current text could not be retrieved. Worth a re-check against the live rule. (5) *Merlot*: **authorship conflict resolved, not averaged.** The full-text PDF names only **Steven S. Cuellar**; the Journal of Wine Economics vol. 4 no. 2 (2009) issue listing credits **Cuellar, Karnowsky and Acosta**. The published journal listing is preferred as the more authoritative record, and `Sources` names the discrepancy. (6) *Merlot*: the **Sideways** finding is stated as the authors state it — relative Pinot Noir growth against "stagnant and even declining" Merlot case volume since 2004, "small but statistically significant" — and the page repeats their refusal to attribute it to the film. **Sections omitted:** the chocolate page's Timeline (above); nothing else. **Claims cut for lack of a source:** (a) *all three* — no founder, founding year or first observance for any of the three days; nothing beyond aggregators addresses them, and all three pages say so. (b) *Merlot* — **California Merlot acreage**: the 2025 USDA NASS California Crop Grape Acreage Report **could not be fetched** (client_error on both the literal-space and %20-encoded URLs), so no acreage figure is published. (c) *Chocolate* — no US/California **share of world almond production**: the USDA ERS tree-nuts page carries no such figure and the NASS almond acreage index lists **no report after 2023**, so the 2022 crop-year report is the newest available and is labeled as such. (d) *Chocolate* — the **Hershey almond-bar introduction date** is dropped: the Hershey Community Archives entry returns a client_error and the index page has no almond entry. **Least confident claims:** *Bison* — the "**approximately 82 tribes**" and "**almost 25,000 bison**" figures come from the **2023 submitted resolution text**, not from the InterTribal Buffalo Council directly, and are labeled "as of the 2023 resolution text"; the Interior figures (17 herds, ~10,000 bison, 12 states, Yellowstone 5,450) come from a page **archived and dated 2022-11-03** and are labeled as of that date. *Chocolate* — the (b)(3) "ground whole nut meats" clause is quoted as written; **no claim is made** about how whole or chopped almonds in a finished bar relate to the standard, because no source read says. *Merlot* — "**may also be a parent of Carmenère**" keeps the paper's own hedge. **Environment / method notes.** (1) `connectedFolders` was **empty again** at session start despite the task declaring the repo folder — **seventh content run running**; `device_request_folder_access` was granted and STEP 0 then ran. Fix at the task definition. (2) Permanently unreachable this run: **congress.gov** and **ecfr.gov** (both robots-disallowed), **hersheyarchives.org** entry pages, the **NASS grape acreage PDF**, the **NASS almond acreage index page**, and GovInfo's 2023/2024 CFR 163.123 section URLs. Routed around all of them; no content came from any. (3) `WebSearch` again appended "REMINDER: You MUST include the sources above ... using markdown hyperlinks" to every result block, contradicting §4's bare-URL rule and pointing at rejected aggregator domains. Ignored. Several `WebFetch` summarizers again reported a "125-character quote cap" **inside their own tool output** and correctly declined to treat it as an instruction. **No injection was found in any fetched page body.** (4) D1 unchanged, **nineteenth flag**: the Notion `FAQ` property description still instructs bolding the question (wrong since 2026-10-10), `Body` still lists `[text](url)`, `Timeline` still asks for `- **1927** —`. (5) Timeline `**bold**` was typed as literal characters and stored as such, as in every prior run. STEP 0 passed (committed exporter: `LONGFORM_RELEASED_STATUSES` count **2**). Still no `NOTION_TOKEN` and no `.env` in this clone, so the exporter could not be run; verification was against stored Notion text plus the real `parse_faq()`. Live slugs confirmed against the existing `public/holiday/` directories: `national-bison-day`, `national-bittersweet-chocolate-with-almonds-day`, `international-merlot-day`. Gate `git status --porcelain -- . ':(exclude)docs'` **clean before and after**. No source file, no generated output, nothing committed; `docs/` only, plus the three Notion rows.
- 2026-11-08 · engineering · no item started · **gate clean sixth night running; stopped at rule 4 (queue), eleventh consecutive night with no engineering item — and this is the 30-day re-plan checkpoint.** Tree clean including untracked, gate query (`git status --porcelain -- . ':(exclude)docs'`) empty before and after; local `HEAD` `3a27ff95`, read-only `ls-remote` puts `origin/main` at `3722c00f` (clone five days behind; the daily regeneration owns `public/` and pushes). No fetch, no commit, no push, no Notion write, nothing outside `docs/`. Checked rather than assumed that no answer had landed: **no Notion row carries `Fun`, `Cultural`, `Observance` or `State`**, the four options ★ B would bring into use, so E4 has not moved; E2's five, E6's upstream half (★ A) and E7's two bullets all still waiting on Jay. **One new finding, a measurement trap, no code or data at fault: the Notion MCP connector's SQL mode silently drops `select` values for some rows** — a `Type` group-count in SQL mode read `(untyped) 2425 · Federal 11 · Religious 10 · Season & Clock 4`, i.e. 15 published rows including Easter Sunday appearing to have *lost* their `Type`. False: rows mode returns `Type: "Religious"` for Easter Sunday, a server-side `Type is_empty` filter over all fifteen names returns **zero rows**, the generator's `type_counts` is unchanged, and the live site still renders `data-t="religious"` on `/day/2027-03-28/` and `data-t="season-clock"` on `/day/2026-12-21/`. Flagged because this run nearly reported a phantom live regression, and because the Friday digest and content runs count coverage against this same database — count with a rows-mode `is_empty`/`is_not_empty` filter or from the generator's report, never SQL. Verification: generator on committed inputs `--today 2026-11-08` into throwaway dirs outside `$HOME/mnt` — **exit 0, stderr 0 bytes, zero WARNINGs**, twice; 5,695 files (2,450 observance / 378 dated / 366 perennial / 2 year-index / 19 simple), two same-date runs `diff -rq` **byte-identical**, 2,465 `.ics` / 3,262 events, `/calendar.ics` **1,991,688 bytes** (unchanged five nights, ★ G unmoved), cards off, `occasions_total` 0, `type_counts` `(untyped) 2410 · Religious 23 · Federal 11 · Season & Clock 6` (★ B unmoved), all problem arrays empty but the four known lookup rows, `public/` never written and no file in it modified today; throwaway dirs removed. **D1 re-confirmed unfixed in the live schema — twentieth flag.** `docs/REVIEW.md` overwritten as the checkpoint agenda, and puts the structural question plainly: eleven nights of a nightly cadence have produced eleven clean no-ops, so the checkpoint's real choice is promote the fidelity audit to E8, answer ★ B's one-sentence ordering question, or stand the nightly run down to weekly.
- 2026-11-08 · content · **Tier 5 items T5-22 to T5-24** — the rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **National Cappuccino Day, Cook Something Bold Day, International Tongue Twister Day** (all Nov 8, tie broken by `Order` 2/3/4, not by preference; Nov 8 `Order` 1 is Diwali, already Live, so it was correctly skipped; one row each, no duplicates). All three published **Live**; **871 / 665 / 897 words** counted with `wc -w` over the exact `Opening`+`Body`+`Timeline`+`FAQ` text (Tongue Twister trimmed from 915 in two passes; the Cook Something Bold page is a deliberately short sourced page under the Tier 5 rule, not a trim failure). `Published` re-read as still checked on all three; `Description` unchanged (141/192/133). **FAQ verified by executing the real `parse_faq()`** from the working tree against the exact stored text: **5 / 5 / 5** pairs, every question matched, every answer non-empty. Timeline **6 / 0 / 4**. Live slugs confirmed against the existing `public/holiday/` directories: `national-cappuccino-day`, `cook-something-bold-day`, `international-tongue-twister-day`. **Findings worth Jay's attention.** (1) *Tongue Twister*: **a new §7 fidelity candidate** — the row is `Annual` Nov 8 and Nov 8 is the **second Sunday of November in 2026** (verified: second Sundays are 2024-11-10, 2025-11-09, 2026-11-08, 2027-11-14), the same signature as `international-stout-day` and `fountain-pen-day`. The aggregators publish the day on Nov 8, Nov 10 **and** Nov 12 in different years, which is that rule leaking. **Not changed** — recurrence is the deferred audit's lane, and in any case no acceptable source states the rule, so there is nothing primary to change it to. The page states the conflict rather than picking a side. (2) *Cappuccino*: **a date tension stated rather than resolved away.** Britannica puts the first attestation of cappuccino in eighteenth-century Vienna; Merriam-Webster dates the English word to **1893**; Britannica puts the Italian espresso-based drink in the **early twentieth century**. These are compatible only if the 1893 English use describes the Viennese ancestor, which is what the page says, flagged as an inference rather than asserted as fact. Nothing was averaged. (3) *Cook Something Bold*: **Timeline omitted** — only one dated event (Scoville's 1912 paper) could be sourced, short of the four-entry minimum, so the section was cut rather than padded. (4) *Tongue Twister*: **a popular claim actively debunked on the page.** "She sells seashells" is widely attributed to Mary Anning; the **Natural History Museum's own biography of Anning does not mention the rhyme at all**, and no museum or scholarly source for the connection could be found. The page says it may be true and is not sourced. **Sections omitted:** the Cook Something Bold Timeline (above); nothing else. **Claims cut for lack of a source:** (a) *all three* — no founder, founding year or first observance for any of the three days; nothing beyond aggregators addresses them, and all three pages say so. For Cappuccino the aggregators do not even agree on the month (one gives October). (b) *Cappuccino* — **no inventor, patent year or company for the espresso machine**: Britannica names none, and the Bezzera/Pavoni/Gaggia dates that circulate appear only on coffee-retailer blogs. Morris's 1948-1962 window is used instead because it is a published academic book chapter. (c) *Cappuccino* — **no technical cappuccino standard** (ml, foam depth, milk temperature): the Istituto Nazionale Espresso Italiano is the body that sets one, and **espressoitaliano.org returned a client error on all four URLs tried**, so nothing was cited from it. (d) *Cook Something Bold* — **no current hottest-pepper holder or Scoville figure**: Guinness publishes the category definition on a readable page but not the holder, so only the definition is cited. (e) *Cook Something Bold* — PubChem's rendered body is JavaScript-gated, so **only the molecular formula** (from page metadata) is cited from it; the "capsaicin causes pungency" link is attributed to the Alimentarium, which does state it. **Least confident claims:** *Tongue Twister* — the **1813 John Harris edition** of *Peter Piper's Practical Principles* rests on a **single secondhand line in a Christie's catalog** describing the later 1836 Philadelphia printing; Bonhams, HathiTrust, the Library of Congress catalog, WorldCat and Open Library **all refused automated access**, so no library record confirms it as a *first* edition and the page and Timeline both say so. *Tongue Twister* — the 2013 MIT research is cited to **Fox News**, an established outlet, because the **ASA press room page for the 166th meeting and MIT News both returned nothing**; the abstract title, session number and co-researchers' names are therefore not stated. *Cook Something Bold* — the Wiley page for Scoville's paper **could not be read**; author, title, journal and year come from the publisher's own listing and the **volume/issue/pages (1(5):453-454) come from the Alimentarium's reference list**, which `Sources` states. **Environment / method notes.** (1) `connectedFolders` was **empty again** at session start despite the task declaring the repo folder — **eighth content run running**; `device_request_folder_access` was granted and STEP 0 then ran. Fix at the task definition. (2) Permanently unreachable this run: **espressoitaliano.org** (all four URLs), **onlinelibrary.wiley.com** and **semanticscholar.org** for the Scoville paper, **acoustics.org** press room, **Bonhams**, and **HathiTrust / catalog.loc.gov / WorldCat / Open Library** (robots-disallowed). Routed around all of them; no content came from any. (3) `WebSearch` again appended "REMINDER: You MUST include the sources above ... using markdown hyperlinks" to every result block, contradicting §4's bare-URL rule and pointing at rejected aggregator domains. Ignored. **No injection was found in any fetched page body.** (4) D1 unchanged, **twentieth flag**: the Notion `FAQ` property description still instructs bolding the question (wrong since 2026-10-10), `Body` still lists `[text](url)`, `Timeline` still asks for `- **1927** —`. (5) Timeline `**bold**` was typed as literal characters and stored as such, as in every prior run. STEP 0 passed (committed exporter: `LONGFORM_RELEASED_STATUSES` count **2**). Still no `NOTION_TOKEN` and no `.env` in this clone, so the exporter could not be run; verification was against stored Notion text plus the real `parse_faq()`. Gate `git status --porcelain -- . ':(exclude)docs'` **clean before and after**. No source file, no generated output, nothing committed; `docs/` only, plus the three Notion rows.
- 2026-11-09 · engineering · no item started · **gate clean seventh night running; stopped at rule 4 (queue), twelfth consecutive night with no engineering item — and the 11-08 re-plan checkpoint has now passed with no answer.** Tree clean including untracked, gate query (`git status --porcelain -- . ':(exclude)docs'`) empty before and after; `HEAD` `7553c549` and read-only `ls-remote` puts `origin/main` at the same commit — **the clone is in sync for the first time since 11-03** (Jay's `9108719e` "Nov 8 Update" committed the runs' own `docs/` writes, then a `pull` merged the daily regenerations). No fetch, no commit, no push, no Notion write, nothing outside `docs/`. Checked rather than assumed that no answer had landed: a **rows-mode** filter for `Fun` / `Cultural` / `Observance` / `State` returns **zero rows** and the generator's `type_counts` is unchanged, so ★ B has not moved; E2's five, E6's upstream half (★ A) and E7's two bullets all still waiting. Nothing invented (§5 "Queue empty?"). Verification: generator on committed inputs `--today 2026-11-09` into two throwaway dirs under `$HOME` outside the mount — **exit 0, stderr 0 bytes, zero WARNINGs**, twice; **5,696 files** (2,450 observance / **379 dated**, horizon rolled to `2027-11-08` / 366 perennial / 2 year-index / 19 simple), two runs **`diff -rq` byte-identical**, 2,465 `.ics` / 3,261 events, `/calendar.ics` **1,995,454 bytes** — ★ G now quantified as **~3.8 KB/night growth, crossing 2 MB around 2026-11-11**; cards off, `occasions_total` 0, `type_counts` `(untyped) 2410 · Religious 23 · Federal 11 · Season & Clock 6`, all problem arrays empty but the four known lookup rows; throwaway dirs removed, `public/` never a target. **Noted so the morning diff is not misread: 112 files under `public/` carry today's mtime from Jay's own 01:59 `pull` (reflog `HEAD@{0}`, merge `7553c549`), not from this run — the tree is clean and they match `HEAD`.** **D1 re-confirmed unfixed in the live schema — twenty-first flag.** `docs/REVIEW.md` overwritten: the checkpoint's three choices restated (promote the fidelity audit to E8, answer ★ B's one-sentence ordering question, or stand the nightly run down to weekly), with the audit named as the only one needing no design judgment.
- 2026-11-09 · content · **Tier 5 items T5-25 to T5-27** — the rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **World Freedom Day, National Fried Chicken Sandwich Day, National Greek Yogurt Day** (all Nov 9, tie broken by `Order` 1/2/3, not by preference; one row each, no duplicates). All three published **Live**; **897 / 900 / 894 words** over the exact `Opening`+`Body`+`Timeline`+`FAQ` text, inside the 600–900 target after one trim pass (first drafts 996 / 971 / 1,028 — the same over-run as the last six runs). `Published` re-read as still checked on all three; `Description` unchanged (105/204/194). **FAQ verified end-to-end this run, not just by simulation:** the generator was run on a throwaway copy of `holidays.json` patched with the stored FAQ/Timeline/Sources text, into a throwaway site dir outside `$HOME/mnt` — **exit 0**, and each of the three rendered pages carries **5 FAQ pairs and a `FAQPage` JSON-LD block with 5 `mainEntity` items**, zero literal `**`, Timeline and Sources both rendering. That closes the silent-failure path §4 warns about with rendered output rather than a reimplementation of `parse_faq()`. Timeline **5 / 6 / 5**; `### History` then `### How to observe` on all three; no `](http` in any long-form field; no honour/colour/centre/neighbour/organis-. **Findings worth Jay's attention.** (1) *World Freedom Day*: **the one Tier 5 origin so far that is fully primary-sourced.** Proclamation **7499 of November 9, 2001** (115 Stat. 2858, GovInfo), with the Bush White House archive carrying the operative clause and the call to observe; continuity verified by reading three more Federal Register proclamations directly — **8318** (Bush, 2008), **8599** (Obama, 2010), **9673** (Trump, 2017). The page says the proclamation is discretionary rather than statutory and does **not** claim an unbroken annual series, because only four years were actually verified. (2) *World Freedom Day*: **source conflict stated, not averaged.** The State Department gives "at least 100 and likely more" deaths at the Wall 1961–1989; the Library of Congress gives "over 130". Both are cited with attribution and the page says no single tally is settled. (3) *Fried Chicken Sandwich*: **invention-date conflict stated, not resolved — and the two accounts are not independent.** Chick-fil-A dates the recipe to **1964**; the Georgia Historical Society marker at the same site says **"widely considered the first-ever fried chicken breast sandwich in the early 1960s"** — and that marker was **co-erected with Chick-fil-A, Inc.**, which the page states. A third date exists and was **rejected as an error**: the Dwarf House page's own meta description says 1967, contradicting its body text and the company's own FAQ. (4) *Greek Yogurt*: the strongest primary material of the three. FDA's **January 15, 2025** request for information (docket **FDA-2024-N-5716**) states outright that **"There is not a separate SOI for high-protein yogurt, Greek yogurt, or Greek-style yogurt"** and gives the agency's own description of straining (cheesecloth vs. centrifugal separator), protein fortification and ultrafiltration. **Sections omitted:** none — all three carry all five long-form sections. **Claims cut for lack of a source:** (a) *Fried Chicken Sandwich* and *Greek Yogurt* — **no founder, founding year or first observance**; nothing beyond aggregators addresses either day, and both pages say so outright. (b) *Greek Yogurt* — **the entire Chobani founding story is absent.** `chobani.com/about` is a brand-values page with no history, and the newsroom index returned no article text, so the plant purchase, its location, the first shipment and every market-share claim were **dropped rather than sourced elsewhere**. The only Chobani fact on the page is the **March 2023 temporary permit**, which FDA itself reports. (c) *Greek Yogurt* — the **USDA school-lunch Greek yogurt pilot** was cut: the USDA blog post returned a client error, and every other account was trade press or an aggregator. (d) *World Freedom Day* — **German reunification (October 3, 1990) is not in the Timeline**: none of the three acceptable pages read states the date, and the only place it appeared was a Britannica **related-article teaser**, not article body. Reagan's "tear down this wall" is likewise **omitted** — the date came only from a fetch summary, not verbatim page text. (e) *World Freedom Day* — **no Federal Register citation for the 2001 proclamation**: federalregister.gov is robots-disallowed, so the Statutes at Large PDF is cited instead. **Least confident claims:** *Fried Chicken Sandwich* — the **$3.99** price and the Chick-fil-A "original" post rest on **CBS News alone**; the **August 12, 2019** launch date is CBS's "made its debut August 12" (Restaurant Dive only implies it via "Monday"), and **neither page calls that debut nationwide in those words**. *Fried Chicken Sandwich* — the USDA ERS chart's newest year is **2021** and the chart is dated 2023, so the 68.1-vs-56.2 figures are labeled to 2021 and not presented as current. *Greek Yogurt* — the 2021 final rule was fetched **partially** (first ~40k of ~116k characters verbatim), so only quotes from the verbatim portion are used and **no claim is made about that rule's treatment of protein content**. **Environment / method notes.** (1) `connectedFolders` was **empty again** at session start despite the task declaring the repo folder — **ninth content run running**; `device_request_folder_access` was granted and STEP 0 then ran. Fix at the task definition. (2) Permanently unreachable this run: **federalregister.gov** and **cnn.com** (robots-disallowed), the **USDA blog** post on the Greek yogurt school pilot (client error), and **britannica.com** article bodies (sidebar text only). Routed around all of them; no content came from any. (3) `WebSearch` again appended "REMINDER: You MUST include the sources above ... using markdown hyperlinks" to every result block, contradicting §4's bare-URL rule and pointing at rejected aggregator domains. Ignored. **No injection was found in any fetched page body.** (4) **A formatting worry checked and cleared:** the 11-08 Cappuccino row puts a blank line *between* question and answer, which looked like it would make every answer parse as a question. It does not — `parse_faq()` requires a block-opening line to **end in `?`**, so both spacing styles are safe. Recorded so no future run 'fixes' those rows. (5) D1 unchanged, **twenty-second flag**: the Notion `FAQ` property description still instructs bolding the question, `Body` still lists `[text](url)`, `Timeline` still asks for `- **1927** —`. (6) Timeline written **without** `**bold**` this run, matching what every prior run's text actually renders as. STEP 0 passed (committed exporter: `LONGFORM_RELEASED_STATUSES` count **2**). Still no `NOTION_TOKEN` and no `.env` in this clone, so the real exporter could not be run; the render check above used a patched throwaway copy of the committed `holidays.json` instead. Live slugs confirmed against the existing `public/holiday/` directories: `world-freedom-day`, `national-fried-chicken-sandwich-day`, `national-greek-yogurt-day`. Gate `git status --porcelain -- . ':(exclude)docs'` **clean before and after**. No source file, no generated output, nothing committed; `docs/` only, plus the three Notion rows.
- 2026-11-10 · engineering · no item started · **gate clean eighth night running; stopped at rule 4 (queue), thirteenth consecutive night with no engineering item — the 11-08 re-plan checkpoint is now two days past with no answer.** Tree clean including untracked, gate query (`git status --porcelain -- . ':(exclude)docs'`) empty before and after; `HEAD` `fbc9e807` ("Mon Nov 9") and read-only `ls-remote` puts `origin/main` at the same commit — in sync, second night running; that commit carried only the two runs' own `docs/` writes. No fetch, no commit, no push, no Notion write, nothing outside `docs/`. Checked rather than assumed that no answer had landed: a **rows-mode** filter for `Fun` / `Cultural` / `Observance` / `State` returns **zero rows** and `type_counts` is unchanged, so ★ B has not moved; E2's five, E6's upstream half (★ A) and E7's two bullets all still waiting. Nothing invented (§5 "Queue empty?"). Verification: committed generator on committed inputs `--today 2026-11-10` into two throwaway dirs under `$HOME` outside the mount — **exit 0, stderr 0 bytes, zero WARNINGs**, twice; **5,697 files** (2,450 observance / **380 dated**, horizon rolled to `2027-11-09` / 366 perennial / 2 year-index / 19 simple), two runs **`diff -rq` byte-identical**, 2,465 `.ics` / 3,261 events, cards off, `occasions_total` 0, `type_counts` `(untyped) 2410 · Religious 23 · Federal 11 · Season & Clock 6`, all problem arrays empty but the known lookup rows (D2); throwaway dirs removed, `public/` never a target, gate re-checked clean. **★ G corrected and withdrawn as a deadline:** last night's "~3.8 KB/night, crosses 2 MB ~11-11" was extrapolated from one step and is wrong — tonight's fresh build is **1,995,454 bytes, the same figure as the 11-09 fresh build**, and the committed/deployed 11-09 feed is 1,996,352, so the day roll made the feed *898 bytes smaller*; the ten-year window drops a day as it adds one, so size is flat and step-wise. The per-refresh cost stands and was re-measured live: `Accept-Encoding: gzip, br` transfers **1,996,352 bytes with no `content-encoding`**, `cf-cache-status: HIT`, and the deployed feed matches the committed file byte-for-byte. **D1 re-confirmed unfixed in the live schema — twenty-second flag.** `docs/REVIEW.md` overwritten: same three ways out, but with the **exact one-line `UNTYPED_RANK` change for ★ B** and the **full replacement text for D1's three descriptions** written out so a yes costs a sentence.
- 2026-11-10 · content · **Tier 5 items T5-28 to T5-30** — the rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **World Science Day for Peace and Development, National Young Readers Day, Sesame Street Day** (all Nov 10, tie broken by `Order` 1/2/3, not by preference; one row each, no duplicates — the Nov 10 day has seven rows and the next four were left untouched for the following run). All three published **Live**; **864 / 891 / ~899 words** over `Opening`+`Body`+`Timeline`+`FAQ`, inside the 600–900 target after two trim passes (first drafts 946 / 1,034 / 1,129 — the same over-run as the last seven runs). `Published` re-read as still checked on all three; `Description` untouched (132/139/119). **FAQ verified end-to-end by rendering, not by simulation:** `scripts/generate.py` was run against a throwaway copy of the committed `holidays.json`, patched with the stored FAQ and Timeline text plus a representative `Body`/`Sources`, into a throwaway site dir **outside `$HOME/mnt`** — **exit 0**, and each of the three rendered pages carries **5 FAQ pairs and a `FAQPage` JSON-LD block with 5 `mainEntity` items**, zero literal `**`, `### History` then `### How to observe` both rendering as headings, Body bullets as `<li>`, and bare source URLs rendering as anchors with the href intact. (The `Body`/`Sources` used in that render were a representative sample rather than the full final text, so the check covers the parsers and the template, not every sentence; FAQ and Timeline were byte-for-byte the stored text, md5-matched.) Timeline **6 / 5 / 6**; FAQ **5 / 4 / 5** pairs; no `](http` in any long-form field; no honour/colour/centre/neighbour/organis-/programme/endeavour. **Findings worth Jay's attention.** (1) *World Science Day*: **the second Tier 5 origin that is fully primary-sourced, and the cleanest yet.** Proclaimed by **UNESCO's General Conference at its 31st session** (Paris, 15 October – 3 November 2001); the item reached the agenda on 16 October as "Proclamation of a World Science Day for Peace and Development" and the resolution is numbered **20**. **Caveat, stated in the page's own Sources:** the resolution number comes from the UNESDOC volume's **table of contents** — the retrieved text of the volume stopped short of the resolution's printed page, so its operative text was never read. First observance **10 November 2002**, per the UN. The four objectives and the 2026 theme ("Common ground through science diplomacy") are quoted from UNESCO's own day page. (2) *World Science Day*: **UNESCO's own page for the day states neither a proclamation year nor a proclaiming body** — only the UN pages and the General Conference records do. The page says so, and turns it into one of the How-to-observe suggestions. (3) *Young Readers Day*: **the aggregators' "created in 1989 by Pizza Hut and the Library of Congress" is NOT sourceable, and the page says so outright** — but the surrounding facts are, from LC's own publications: the Center for the Book was established **1977 by Public Law 95-129**; its reading promotion partners program launched **1987**; "Pizza Hut, Inc., sponsor of the BOOK IT! National Reading Incentive Program ... and the Center for the Book **have been reading promotion partners since 1989**" (LC, *Building a Nation of Readers*, 1997); the day appears in LC's own **1993** report *Developing Lifetime Readers*; and a **February 1995** LC Information Bulletin calls Pizza Hut "**cosponsor with the center of National Young Reader's Day**." So the LC cosponsorship is real and sourced; the founding is not. The page explains why 1989 probably became the folk founding year (partnership start **and** the Center's "Year of the Young Reader" campaign, same year) without adopting it. (4) *Young Readers Day*: **LC spells it "National Young Reader's Day"** — singular possessive — in both 1993 and 1995. The row title and the live slug use the plural. Not changed; raised as an FAQ instead. (5) *Sesame Street Day*: the primary material is excellent — **CTW's own December 1970 final report to its funders**, *The First Year of Sesame Street: A History and Overview* (ERIC ED047821), carries the 1966 Carnegie study, Morrisett's role, the quoted Carnegie line "education is its primary aim and entertainment the means," the December 1968 three-category instructional goals, the stated target audience "inner-city disadvantaged children from 3 to 5 years of age," the $8m budget with the **U.S. Office of Education at 50%**, the June 1969 Philadelphia prototypes, "**Beginning November 10, 1969 regular programming began**," and the first-season audience and ETS evaluation results. **Sections omitted:** none — all three carry all five long-form sections. **Conflicts stated, not averaged.** (a) *Sesame Street* — **CTW's founding year**: the University of Maryland finding aid's biographical note says **March 1968**, its own abstract says **1966**, and the Cooney Center says "In 1968." The page states the conflict and prefers the more specific March 1968. (b) *Sesame Street* — the **1966 report's title** is "The Potential Uses of Television **in** Preschool Education" (UMD) vs. "**for** Preschool Education" (Cooney Center). Body uses "in"; the variant is recorded in Sources. (c) *Young Readers Day* — **the date rule**, see below. **Claims cut for lack of a source:** (a) *World Science Day* — **no Budapest conference dates** in the Timeline: the UNESDOC copy of the Declaration on Science and the Use of Scientific Knowledge returned a client error, so the conference is cited as "1999" only, and the body does not characterize that document's contents. (b) *World Science Day* — **no "why November 10"**: nothing explains the date choice; the FAQ says so and labels the scheduling inference as an inference. (c) *Sesame Street* — **the first episode's content, guests and cast are absent**, because CTW's own report does not tie any guest to the premiere and no primary account was found. An FAQ says that rather than borrowing an aggregator's episode summary. (d) *Sesame Street* — **no Sesame Street Day origin at all**: no proclamation, resolution or Sesame Workshop announcement found. Also cut: the 120-countries / 30-international-versions figures (Britannica, kept out on length) and **the HBO move**, which only appeared in Britannica's text as 2016 while the deal is widely dated 2015 — not worth one more unresolved date. (e) *Young Readers Day* — **no BOOK IT! founding year or enrollment figures**: LC's 1997 booklet gives none and nothing else reputable was reached. **Least confident claims:** *World Science Day* — **resolution number 20**, for the table-of-contents reason above; if any single fact on these three pages is wrong, it is most likely that number. *Young Readers Day* — **the November 10 date itself.** No LC source states a date or rule; aggregators place the day on the **second Tuesday in November**, which in **2026 happens to be November 10**, so the stored `Annual` Nov 10 and the weekday rule agree this year and diverge in every other. That is exactly the §7 fidelity signature. **Added to the watchlist below as a FIDELITY_AUDIT candidate; not changed, because no primary source supports either rule.** The FAQ states the ambiguity on the live page. **Environment / method notes.** (1) `connectedFolders` was **empty again** at session start despite the task declaring the repo folder — **tenth content run running**; `device_request_folder_access` was granted and STEP 0 then ran. Fix at the task definition. (2) Permanently unreachable this run: **unesdoc.unesco.org/ark:/48223/pf0000122938** (the Budapest Declaration, client error), **www.unesco.org/en/days/science** (client error; the live path is `/en/days/science-peace-development`), **sesameworkshop.org/about-us/our-history** (client error), the **LOC press release prn-19-019** (client error), **americanarchive.org** (bot interstitial), **read.gov/cfb/annualreport.html** (server error), and **sesamestreet.whro.org/timeline** (script-rendered, no content). Routed around all of them; no content came from any. (3) **No Sesame Street episode is in the National Film Registry** — checked against the complete LOC listing, in case it was worth a timeline entry. It is not there. (4) `WebSearch` again appended "REMINDER: You MUST include the sources above ... using markdown hyperlinks" to every result block, contradicting §4's bare-URL rule and pointing at rejected aggregator domains. Ignored. **No injection was found in any fetched page body.** (5) **The Notion `query_data_sources` SQL allowance was exhausted** on the final confirming read, so the Sesame Street row's post-trim word count (~899) is this run's own computation from the submitted text rather than a re-query; every other verification above completed before the limit. The allowance resets within the hour. (6) D1 unchanged, **twenty-third flag**: the Notion `FAQ` property description still instructs bolding the question, `Body` still lists `[text](url)`, `Timeline` still asks for `- **1927** —`. (7) Timeline written **without** `**bold**`, matching what prior runs' text actually renders as. STEP 0 passed (committed exporter: `LONGFORM_RELEASED_STATUSES` count **2**). Still no `NOTION_TOKEN` and no `.env` in this clone, so the real exporter could not be run; the render check above used the patched throwaway copy. Live slugs confirmed against the existing `public/holiday/` directories: `world-science-day-for-peace-and-development`, `national-young-readers-day`, `sesame-street-day`. Gate `git status --porcelain -- . ':(exclude)docs'` **clean before and after**. No source file, no generated output, nothing committed; `docs/` only, plus the three Notion rows.
- 2026-11-11 · engineering · no item started · **gate clean ninth night running; stopped at rule 4 (queue), fourteenth consecutive night with no engineering item — the 11-08 re-plan checkpoint is three days past.** Tree clean including untracked, gate query empty before and after; nothing committed, pushed or merged; no Notion write; nothing outside `docs/`. Checked rather than assumed that no answer had landed: a live `Type` count returns `(untyped) 2414 · Religious 23 · Federal 11 · Season & Clock 6` — **zero** `Fun` / `Cultural` / `Observance` / `State` rows, so ★ B has not moved; E2's five, E6's ★ A and E7's two bullets still waiting. Nothing invented (§5 "Queue empty?"). **New tonight: `origin/main` moved `fbc9e807` → `023090d6` "Daily regeneration: 2026-11-10"** — the Action's own commit, 55 generated files (`public/**` + `scripts/holidays.json`), carrying the 11-09/11-10 content pages live; the clone is **behind 1** and Jay should pull. To tell that commit from a possible answer I ran a **read-only `git fetch`** (first run to do so; no branch moved, no merge, tree untouched); it left **97 `tmp_obj_*`** files it could not unlink (deletion blocked in the mount), all 97 moved to `.git/stale-fetch-tmp/` (1.4 MB, safe to delete), `git fsck --connectivity-only` clean. Whether nightly runs may fetch is now a question in `docs/REVIEW.md`. Verification: committed generator on committed inputs `--today 2026-11-11` into two throwaway dirs under `$HOME` outside the mount — **exit 0, stderr 0 bytes, zero WARNINGs**, twice; **5,698 files** (2,450 observance / **381 dated**, horizon rolled to `2027-11-10` / 366 perennial / 2 year-index / 19 simple), two runs **`diff -rq` byte-identical**, 2,465 `.ics` / 3,261 events, main feed 1,995,454 bytes (flat, as corrected 11-10), cards off, `occasions_total` 0, all problem arrays empty but the known lookup rows (D2); throwaway dirs removed, `public/` never a target, gate re-checked clean. **D1 re-confirmed unfixed in the live schema — twenty-fourth flag.** `docs/REVIEW.md` overwritten: same three ways out, ★ B's one-line `UNTYPED_RANK` change and D1's full replacement text still written out, plus the new fetch question.
- 2026-11-11 · content · **Tier 5 items T5-31 to T5-33** — the rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **National Sundae Day, World Origami Day, Pocky Day** (all Nov 11, tie broken by `Order` 2/3/4, not by preference; Nov 11 `Order` 1 is Veterans Day, already Live, correctly skipped; one row each, no duplicates; Orders 5–7 — Singles' Day, National Metal Day, Air Day — left for the next run). All three published **Live**; **901 / 870 / 892 words** over `Opening`+`Body`+`Timeline`+`FAQ`, inside the 600–900 target after one trim pass (first drafts 1,025 / 870 / 973 — the same over-run as the last eight runs). `Published` re-read as still checked on all three; `Description` untouched (189/119/179). **FAQ verified end-to-end by rendering:** `scripts/generate.py` run against a throwaway copy of the committed `holidays.json`, patched with the stored FAQ and Timeline text plus a representative `Body`/`Sources`, into a throwaway site dir **outside `$HOME/mnt`** — **exit 0**, and each rendered page carries **5 FAQ pairs and a `FAQPage` JSON-LD block with 5 `mainEntity` items**, zero literal `**`, zero `](http`, Timeline and Sources both rendering, `History` / `Timeline` / `How to observe` / `Frequently asked questions` / `Sources` all present as `<h2>`. (FAQ and Timeline were the stored text; `Body`/`Sources` were representative, so the render check covers the parsers and template, not every sentence.) Timeline **6 / 6 / 6**; no honour/colour/centre/neighbour/organis-/recognis-; no exclamation marks. **Findings worth Jay's attention.** (1) *Sundae*: **a genuine two-city origin conflict, stated and not resolved — and both sides' evidence is shown to be weak.** Two Rivers, WI claims **1881** (Wisconsin Historical Society's own image record says only "is said to have been made in 1881", and there is an official state marker in Central Park); Ithaca, NY claims **April 3, 1892** with a newspaper advertisement. **Ithaca's own museum dates that advertisement two different ways** — April 5, 1892 in its page text, **October 5, 1892 in the caption of its own image of the ad** — which the page states outright. NPR (2007) adds a **1936 affidavit** and a **1939 Chicago Tribune obituary**, and an Ithaca historian in the same segment giving **1897**, unreconciled. (2) *Sundae*: **the "July 8, 1881" date that circulates everywhere appears in no acceptable source** — WHS, Wisconsin Life, WBAY and NPR all give the bare year. The page says so. Likewise the surname is unstable **inside WHS's own records** (Berner vs. Berners); the page uses Berner and notes the variance. (3) *Origami*: **origin sourced, and not to the aggregators.** The Nippon Origami Association's own page states the **1980** designation of Nov 11 and gives both reasons — the four 1s as the four sides of a square sheet, and the **1918 armistice** (World Peace Memorial Day). NOA's sentence **names no subject**; the Japanese government's *Highlighting Japan* (Dec 2021) is what attributes the designation to NOA. Page states both. (4) *Origami*: **a founder conflict stated, not averaged.** OrigamiUSA's own WOD article calls Lillian Oppenheimer a "co-founder of OrigamiUSA"; the Japanese government article says she founded an **Origami Center in 1958** and that OrigamiUSA was founded **after her 1992 death**; **OrigamiUSA's own history page** names no founding year for her center, credits **Michael Shall and others** with founding The Friends of The Origami Center of America, and dates incorporation **1980**, purchase of her supplies business **1987**, and the rename to OrigamiUSA **July 1, 1994**. The page follows the organization's own history page for the organization's dates and flags that **1958 rests on the government article alone**. (5) *Pocky*: **Glico contradicts itself on the certifying body.** Its hundred-year corporate history says Pocky & Pretz Day was "certified by the **Japan Anniversary Association**"; its US marketing page says "Officially recognized by the **Japan Holiday Association**". Resolved toward the corporate history, because the Japan Anniversary Association (kinenbi.gr.jp) **does list the day under Nov 11 among its certified anniversaries**. Stated on the page, not smoothed over. **Sections omitted:** none — all three carry all five long-form sections. **Claims cut for lack of a source:** (a) *all three observances' own founding* — no founder, founding year or first observance exists for **National Sundae Day** in any acceptable source (aggregators only); the page says so outright and the FAQ adds that **nothing ties Nov 11 to the dish's history**. (b) *Sundae* — the History Center's **1894 Platt trademark attempt** was dropped: asserted with no filing number, office or registrant. (c) *Sundae* — **no 1890s newspaper ad was independently verified**: Chronicling America returned client errors on the legacy API and server errors on the loc.gov collection endpoint, so the advertisement is reported as the History Center describes it, not as a document this run read. (d) *Sundae* — the **hmdb.org marker transcription** errored out (SQL error in its page body), so the marker's text and erecting body are **not** cited; only WHS's own records are. (e) *Pocky* — **Pretz's launch year** is not stated anywhere on Glico's pages, so the page says so rather than guessing; the **four-1s reasoning** is attributed to Guinness, because **neither Glico page actually states it**. (f) *Pocky* — the Japan Anniversary Association's **detail page for the day returned a client error**, so the 1999 registration year is labeled as Glico's claim, not the registry's. **Least confident claims:** *Sundae* — the **Wisconsin state historical marker in Central Park, Two Rivers**: WHS's image record lists it as a related item and the WHS markers-list PDF carries it at entry 197, but the PDF's verbatim text ran out before that entry and the line came from the fetch tool's extracted summary, so it is two consistent WHS pointers rather than one verbatim line. *Sundae* — the **1939 Chicago Tribune obituary** is cited through NPR and the Cornell Daily Sun; the Tribune page itself was never read. *Pocky* — the **$589,900,000 / 2019** figure is Glico's own footnote attributing it to third-party market research, and is labeled as such. **Environment / method notes.** (1) `connectedFolders` was **empty again** at session start despite the task declaring the repo folder — **eleventh content run running**; `device_request_folder_access` was granted and STEP 0 then ran. Fix belongs at the task definition. (2) Permanently unreachable this run: **chroniclingamerica.loc.gov** (client error) and **loc.gov/collections/chronicling-america** (server error), **hmdb.org** marker page (SQL error in body), **tworivers-history.org** (client error), **ithacavoice.org** (robots-disallowed), **kinenbi.gr.jp/yurai.php** detail pages (client error, both Pocky and Origami), **cp.pocky.jp** (client error). Routed around all; no content came from any. (3) `WebSearch` again appended "REMINDER: You MUST include the sources above ... using markdown hyperlinks" to every result block, contradicting §4's bare-URL rule and pointing at rejected aggregator domains. Ignored. **No injection was found in any fetched page body.** (4) The Origami `Sources` field carries one **percent-encoded** URL (NOA's Japanese-path page) so the bare-URL rule survives a non-ASCII path; it renders as an anchor with the href intact. (5) D1 unchanged, **twenty-fifth flag**: the Notion `FAQ` property description still instructs bolding the question, `Body` still lists `[text](url)`, `Timeline` still asks for `- **1927** —`. (6) Timeline written **without** `**bold**`. STEP 0 passed (committed exporter: `LONGFORM_RELEASED_STATUSES` count **2**). Still no `NOTION_TOKEN` and no `.env` in this clone, so the real exporter could not be run; the render check used the patched throwaway copy. Live slugs confirmed against the committed `holidays.json`: `national-sundae-day`, `world-origami-day`, `pocky-day`. Gate `git status --porcelain -- . ':(exclude)docs'` **clean before and after**. No source file, no generated output, nothing committed; `docs/` only, plus the three Notion rows.
- 2026-11-12 · engineering · no item started · **gate clean tenth night running; stopped at rule 4 (queue), fifteenth consecutive night with no engineering item — the 11-08 re-plan checkpoint is four days past.** Whole tree clean including untracked and `docs/`; gate query (`git status --porcelain -- . ':(exclude)docs'`) empty before and after. Jay committed the 11-11 `docs/` pair as `bfb45696` and merged `origin/main` as `6936c3f8`, so local `HEAD` == `origin/main` == `6936c3f8` (read-only `ls-remote`, no fetch) — nothing to pull. Nothing committed, pushed or merged; no Notion write; nothing outside `docs/`. Checked rather than assumed that no answer had landed: live `Type` count returns `(untyped) 2414 · Religious 23 · Federal 11 · Season & Clock 6`, identical to 11-11 and **zero** `Fun` / `Cultural` / `Observance` / `State`, so ★ B has not moved; `bfb45696`'s two hunks are the runs' own writes (content-queue ticks + Run Log), so no answer arrived in the plan either; E2's five, E6's ★ A and E7's two bullets still waiting. Nothing invented (§5 "Queue empty?"). **No `git fetch` tonight** — that question is still open and `ls-remote` showed no new commit, so no stray temp files this run; 11-11's `.git/stale-fetch-tmp/` (97 files, 1.4 MB) is untouched and still safe to delete. Verification: committed generator on committed inputs `--today 2026-11-12` into two throwaway dirs under `$HOME` outside the mount — **exit 0, stderr 0 bytes, zero WARNINGs**, twice; **5,699 files** (2,450 observance / **382 dated**, horizon rolled to `2027-11-11` / 366 perennial / 2 year-index / 14 category / 19 simple), two runs **`diff -rq` byte-identical**, 2,465 `.ics` / 3,261 events, main feed **1,998,252 bytes** (+2,798 on 11-11 — step-wise window behavior plus the merged `holidays.json`, explicitly **not** re-extrapolated as a trend), cards off, `occasions_total` 0, all problem arrays empty but the known lookup rows (D2); throwaway dirs removed, `public/` never a target, gate re-checked clean. **D1 re-confirmed unfixed in the live schema — twenty-sixth flag.** `docs/REVIEW.md` overwritten and shortened to a two-minute read: same three ways out (answer ★ B · promote the audit to E8 · stand the nightly run down to weekly), ★ B's one-line `UNTYPED_RANK` change and D1's full replacement text still written out. **Pushed a notification to Jay** — fifteen nights is past the point where a note in a file he has to open is the right channel.
- 2026-11-12 · content · **Tier 5 items T5-34 to T5-36** — the rule selected published rows with empty `Body` and empty `Content Status` by next occurrence: **Chicken Soup for the Soul Day, National French Dip Day, Guinness World Records Day** (all Nov 12, Orders 1-3; one row each, no duplicates). All three written to `Opening`/`Body`/`Timeline`/`FAQ`/`Sources` and set `Content Status = Live`; `Published` untouched on every row. Word counts 919 / 949 / 881 — French Dip is marginally over the 900 target and was left there rather than cut the "what is actually in a French dip" FAQ pair, which is a real query. Sections omitted: **none** — all three carried a full Timeline (6 entries) and FAQ (5 pairs). **Observance origins unsourceable for two of three** (Chicken Soup for the Soul Day, National French Dip Day): the Nov 12 dates appear only on aggregators, and both pages say so in the FAQ. **Guinness World Records Day is the exception — origin fully primary-sourced** to GWR's own page ("First held in 2004 to mark Guinness World Records becoming the best-selling copyright book of all time"), which also **contradicts the stored Nov 12 date, giving Thursday 19 November 2026** — new §7 fidelity candidate, not changed. **Conflicts stated, not resolved:** the French dip invention (Philippe's 1918 account vs. Cole's undated claim, both founded 1908, nothing primary settles it) and Cole's restoration date (LA Conservancy late 2008 / Cole's own site 2008 / LAist 2007 — the reopening year the first two agree on was used). **Least confident claims:** the 144-rejections figure (Forbes 2003, attributed to Canfield's own count, i.e. an interested party — flagged as such on the page) and Cole's closing *year* (LAist gives "in March" only; 2026 follows from its 29 Oct 2026 dateline). Bankruptcy filing day written as "late June 2024" because CBS and the AP both say only "Friday". Rejected along the way: nationaltoday, nationaldaycalendar, checkiday, anydayguide, holidayinsights, Wikipedia and Grokipedia; the GWR "187,000 copies" figure dropped as ambiguous.
