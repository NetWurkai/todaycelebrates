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
public/calendar.ics
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

Still unmeasured, and the one acceptance criterion not confirmed: **CLS**, plus
real phone-width rendering of `/dates/` and the year pages. Both need a deploy.

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

**The one criterion left: "subscribe cleanly in Apple Calendar and Google
Calendar" needs this deployed** — an unattended run cannot subscribe to a feed
that is not published yet. Four decisions in the 2026-10-14 `docs/REVIEW.md`,
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

### E7 — Share cards + Featured tier
Build-time card image per occasion, doubling as the OG image. Feed-native 9:16.
Free to view and share; the listing is what costs money.

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
- [ ] 15. Labor Day
- [ ] 16. Martin Luther King, Jr. Day
- [ ] 17. Presidents' Day
- [ ] 18. Juneteenth
- [ ] 19. Columbus Day
- [ ] 20. Indigenous Peoples' Day
- [ ] 21. U.S. General Election Day
- [ ] 22. Flag Day
- [ ] 23. Patriot Day — National Day of Service & Remembrance

**Tier 3 — seasonal, cultural, commercial**
- [ ] 24. Black Friday
- [ ] 25. Cyber Monday
- [ ] 26. Small Business Saturday
- [ ] 27. Cinco de Mayo
- [ ] 28. Mardi Gras
- [ ] 29. Chinese New Year
- [ ] 30. Diwali
- [ ] 31. The Start of Hanukkah
- [ ] 32. Passover
- [ ] 33. The Start of Ramadan
- [ ] 34. Good Friday
- [ ] 35. Ash Wednesday
- [ ] 36. Daylight Saving Time Ends
- [ ] 37. The Start of Daylight Saving Time
- [ ] 38. Autumnal Equinox
- [ ] 39. Groundhog Day
- [ ] 40. April Fools' Day
- [ ] 41. Earth Day
- [ ] 42. Pi Day
- [ ] 43. Friday the 13th

**Tier 3b — from E2's coverage gaps (2026-10-10), ahead of Tier 4 by demand,
as instructed below.** All eleven are published rows with a one-paragraph
Description and no long-form content.
- [ ] 23a. Kwanzaa
- [ ] 23b. Rosh Hashanah
- [ ] 23c. Yom Kippur
- [ ] 23d. Day of the Dead
- [ ] 23e. National Teacher Appreciation Day  *(and the Week row with it)*
- [ ] 23f. Super Bowl Sunday
- [ ] 23g. Oktoberfest (starts in Germany)  *(the "ends" row is a known bug — see §7)*
- [ ] 23h. National Pizza Day
- [ ] 23i. National Margarita Day
- [ ] 23j. National Hugging Day

**Tier 4 — high-volume "national day" queries**
- [ ] 44. National Dog Day
- [ ] 45. National Cat Day
- [ ] 46. National Coffee Day
- [ ] 47. National Taco Day
- [ ] 48. National Doughnut Day  *(fix recurrence first — see E2)*
- [ ] 49. National Ice Cream Day
- [ ] 50. National Cheeseburger Day
- [ ] 51. Administrative Professionals Day
- [ ] 52. National Boss' Day
- [ ] 53. National Grandparents Day
- [ ] 54. World Mental Health Day
- [ ] 55. National Coming Out Day

**Tier 5 — everything else.** When Tiers 1–4 are ticked, keep going without
being re-planned: take published rows whose `Body` is empty and whose
`Content Status` is empty, ordered by **next occurrence** (soonest first, so pages
are ready before their day). Skip a row another run has already touched. Many of
these are "National ___ Day" observances with a thin or commercial origin — for
those, ship the short honest page the sourcing rule allows (a sourced 300–500
words, with "the origin of this observance is not well documented" where that
is true) rather than padding to 600. The site has ~2,400 rows, so this tier is
a multi-month job; the Friday digest reports the running count.

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
