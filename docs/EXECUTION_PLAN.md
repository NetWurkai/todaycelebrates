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
public/robots.txt       docs/*                  wrangler.jsonc
```

**Generated — never edit:**
```
public/index.html       public/holiday/**       public/day/**
public/data/**          public/sitemap.xml      scripts/holidays.json
```

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

### E4 — Observance type taxonomy
Flat 7–14 item day lists give Thanksgiving and National Pumpkin Day the same
visual weight, which tells the reader we don't know which matters.

- Notion `Type` select: Federal / State / Religious / Cultural / Observance /
  Season & Clock / Fun.
- Sort and style day lists by type. Also the prerequisite for separating paid
  occasions from genuine ones in E6.

**Done when:** every published row has a Type; day lists sort by it; major
observances are visually dominant.

### E5 — Calendar export
Absent across all five competitors. A subscribed calendar is the only retention
mechanism available without accounts.

- `/calendar.ics` (all), `/holiday/<slug>/event.ics` (one), per-category feeds.
- `webcal://` links. Correct `VTIMEZONE`, stable `UID`s across regenerations.

**Done when:** feeds validate and subscribe cleanly in Apple Calendar and Google
Calendar, and UIDs are stable run to run.

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
- [ ] 6. Easter Sunday
- [ ] 7. Mother's Day
- [ ] 8. Father's Day
- [ ] 9. St. Patrick's Day
- [ ] 10. Independence Day
- [ ] 11. New Year's Eve
- [ ] 12. Christmas Eve

**Tier 2 — federal and civic**
- [ ] 13. Veterans Day
- [ ] 14. Memorial Day
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
