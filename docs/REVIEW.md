# Review — 2026-10-12, engineering run (E3's year indexes)

Tree was clean at the gate. Took the one item left in E3: the
**`/holidays/<year>/` index pages**, its fourth bullet. That finishes E3.

## What I changed and why

The 351 dated pages were reachable only one day at a time — prev/next, the
week rail, the homepage calendar widget, the sitemap. Nothing on the site let a
reader, or a crawler that follows links rather than the sitemap, see a year of
the archive at once. So: **one index page per year the archive touches**, built
from `day_dates` and nothing else.

- **`/holidays/2026/`** — 85 dates, October 8 to December 31, 2026, in three
  month sections.
- **`/holidays/2027/`** — 266 dates, January 1 to October 11, 2027, ten month
  sections.

Each row is the weekday and date, linking to that `/day/` page, with its
observance count. Each page carries a month rail in the sidebar, a year switcher
at the foot, and a link out to `/dates/`.

Three things I decided and want you to look at:

1. **Both ends of the archive are partial, so each page says so in a
   sentence** rather than rendering twelve month headings with nine empty. The
   2026 page says the archive opens October 8, 2026; the 2027 page says it
   reaches about a year ahead and extends daily. The 2027 page also says
   outright that **18 dates inside its range have nothing on the calendar and
   so have no page** — that number is real, not a bug (Jan 3, Jan 6, May 18–20,
   and so on).
2. **New segment, `/holidays/`, plural.** `/holiday/<slug>/` is one observance
   and `/day/<date>/` is one date; a year index is neither, so it needed its
   own segment. Cloudflare's `/holiday/*` rule does not match it, so `_headers`
   got its own rule.
3. **No new nav item.** The tab row is already tight at 760px — that was the
   call on 2026-10-11 and it still holds. Reachability comes from every dated
   page linking its own year index, plus a link from `/dates/`. That is 87
   pages linking `/holidays/2026/` and 268 linking `/holidays/2027/`.

Breadcrumbs follow the existing hierarchy: `Today / Calendar / 2027`. Both
pages are self-canonical and in the sitemap. **No new CSS** — the page reuses
the `/dates/` hub's markup exactly.

## Files touched

```
 M scripts/generate.py              +182/-6: year_index_path(), year_index_html(),
                                    the pages wired into simple_pages, YEAR_LINK on
                                    dated pages, the year links on /dates/,
                                    year_index_pages in the report
 M scripts/templates/day.html       one line: <!--TC:YEAR_LINK--> in the note block
 M public/_headers                  +5: a /holidays/* cache rule
 M public/llms.txt                  +2: the year-index page type, and when to cite it
 M scripts/README.md                +37: URL model row + a section on the year indexes
 M docs/REVIEW.md, docs/EXECUTION_PLAN.md
```

No generated file touched. The generator only ran into throwaway directories
outside the repo. Nothing committed, nothing pushed. **The pages themselves do
not exist in `public/` yet** — they appear when you commit and the daily Action
regenerates, which is the normal path for every page type.

## What you should check

1. **The two new pages at phone width.** They reuse the hub's two-column
   `.cat-list`, but the label is longer than the hub's ("Thursday, October 8"
   against "October 8"), so the row wrap is the one visual thing I could not
   check — nothing is deployed.
2. **The wording of the coverage sentences**, which are the honest part of
   these pages and the part most worth disagreeing with.
3. **The one-paragraph addition to all 351 dated pages** — that is the whole
   reason the dated-page half of the diff is 351 files. Verification below
   shows it is only that paragraph.

## How I verified it

- **Reverse-transform against the pre-patch generator**, both run over the same
  `holidays.json`/`people.json` into seeded copies of `public/` at the same
  `--today`: removing the one added paragraph makes **all 351 dated pages
  byte-identical**; removing the added clause makes `/dates/` byte-identical.
  Every holiday page, perennial page, data file, category page, the homepage
  and `/about/` are **untouched**. Zero unexplained deltas; the sitemap gained
  exactly the two new URLs.
- Exit 0, **zero WARNING lines**, and a second run is **byte-identical** —
  idempotent.
- Both pages: no unbalanced tags, no leftover template markers, self-canonical,
  one sitemap entry each, and **every day link resolves** (85 and 266, all
  unique, none pointing at the wrong year). The day count on each page matches
  the archive on disk, and **every observance count matches that dated page's
  own `ItemList`** — 0 disagreements.
- **Rollover tested** by generating at a simulated `--today 2027-06-15`: three
  year pages appear, 2027 fills out to a complete year and drops its partial-year
  sentence, 2028 opens partial. (That run prints four WARNINGs — the
  lookup tables that expire in 2027, §7 — which are pre-existing and expected at
  a 2027 date, not caused by this change.) The single-date case the horizon
  produces whenever it crosses a New Year is unit-tested separately and reads
  "The record for 2028 is one date so far, January 1, 2028."
- **Not measured:** CLS, which E3's acceptance criteria name, and real
  phone-width rendering. Both need a deploy.

## Needs a decision

New, both small:

1. **Should a bare `/holidays/` exist?** Today it 404s — someone who trims
   `/holidays/2027/` back lands on nothing. Options: leave it, redirect it to
   `/dates/`, or make it a small hub listing the years. I did not guess.
2. **The 2026 page makes the archive's start line visible** ("earlier dates in
   2026 have no dated page"). That is the honest statement of where
   `DAY_ARCHIVE_START` is, but it does invite the question of backfilling
   January–early October 2026. The README already flags backfilling as a
   content decision, not a tweak (near-duplicate-content risk, ~280 pages). No
   action taken.

Carried over from 2026-10-10, still unanswered — these are what block E2 and
nothing else:

3. **Leap Day** sits unpublished; publishing it extends the dated archive by
   ≈142 pages (and would add a `/holidays/2028/` page), or clamp `day_end` first.
4. **`Oktoberfest (ends in Germany)`** is wrong from 2027; needs a new rule kind
   or a lookup table for Munich's conditional October 3 extension.
5. **Tax Day** overlaps `Income Tax Pay Day`, and the IRS date shifts for
   weekends and DC Emancipation Day.
6. **National French Fry Day** — July 13 vs the second Friday of July; the move
   was an aggregator's, at a restaurant chain's request.
7. **Solstices / vernal equinox** already exist under other names: a naming
   call, not a coverage gap.

## Where the queue stands

**E3 is done.** All four bullets are built. The next engineering run goes to
**E4 — observance type taxonomy**, and it is worth knowing what that item
actually is before it starts: its acceptance criterion is *every published row
has a Type*, which is ~2,450 Notion rows. That is several runs of bulk property
writes, and the Federal / State / Religious / Cultural / Observance / Season &
Clock / Fun assignment is a judgment call on a good number of rows. If you want
a particular assignment rule — or want the first run to do a sample of a few
hundred and show you the calls it made before going wide — say so and the next
run will follow it; otherwise it will start with the rows where the type is
unambiguous (federal holidays, religious observances) and report what it left
alone.

Earlier review notes are in git history: `git show HEAD:docs/REVIEW.md`.

---

## Content run 2026-10-11 — notes for the engineering run

*(Back-filled by the 2026-10-12 content run; text is the 2026-10-11 run's own, from
`claude/content-run-2026-10-11-tier1-6to8.md` in the project. That run finished its
Notion writes but lost the device bridge before it could write these.)*

1. **The Notion `FAQ` field description is stale and now contradicts the code.**
   It still reads: "Question on its own line wrapped in **bold**". Since the
   2026-10-10 fix, bolding is a no-op that never survives `plain_text`, and §4
   of the plan says questions need no bolding. The field description is the
   thing a future session reads first. One-line fix in the Notion schema.
2. **The committed `parse_faq()` is stricter than §4 describes.** §4 (and the
   content task prompt) say a question is "the first line of a blank-line
   block". The code requires `at_block_start and line.endswith("?")`. A
   block-opening question without a trailing question mark is silently
   demoted to a headless answer and dropped. All 15 questions written today
   end in "?", so nothing is affected now. Either loosen the code or tighten
   the wording — the current mismatch is the same silent-failure shape that
   cost every FAQ before 2026-10-10.
3. **This run could not finish its repo writes.** The device bridge dropped
   after the Notion writes. The §6 queue ticks for items 6-8 may or may not
   have landed (the script asserts on an already-ticked line, so re-running
   it is harmless); the §8 Run Log line and this note were not written by the
   run itself. Section A and B of
   `claude/content-run-2026-10-11-tier1-6to8.md` in the project hold the exact
   text. Worth considering whether content runs should write the Run Log line
   *before* the Notion writes, so a dropped connection loses a draft rather
   than the record of one.
4. E2's five open decisions and E3's three from the 2026-10-11 engineering run
   are untouched by this run and still open.
