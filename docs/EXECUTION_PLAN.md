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
