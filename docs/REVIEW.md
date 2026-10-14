# Review — 2026-10-14, engineering run (E5, calendar export)

**Two runs wrote this file today.** My engineering review is below. Tonight's
content run (Christmas Eve, Veterans Day, Memorial Day — all published Live)
had already appended its own section before I finished, so I **kept it**, at the
bottom, rather than obeying rule 6's "overwrite" to the letter and destroying
the only record of three pages going live. The previous engineering review is in
git history: `git show HEAD:docs/REVIEW.md`.

E4's remaining ~2,410 rows are still blocked on an assignment rule from you, so
per §5 I took **E5 — calendar export** instead. It needed no Notion changes.

## What I changed and why

The site now publishes iCalendar feeds, generated on the same run as the pages:

| URL | What it holds | Count |
|---|---|---|
| `/calendar.ics` | every observance | 3,265 events, 1.9 MB (164 KB gzipped) |
| `/category/<slug>/calendar.ics` | one category | 14 feeds (largest: food, 352 KB) |
| `/holiday/<slug>/event.ics` | one observance | 2,450 files, ~1 KB each |

Two decisions inside that are worth your eye, because they are the item's
substance rather than its wording:

1. **Fixed-date rows are one event with `RRULE:FREQ=YEARLY`; rule-dated rows are
   enumerated date by date for ten years.** `BYDAY` could express "third Sunday
   in June", but nothing in RFC 5545 expresses an Easter offset, an almanac
   lookup table, "the day after Thanksgiving" or "the next Friday the 13th" — so
   translating the rules into RRULEs would cover some and not others and would
   be a *second* implementation of the recurrence engine, free to drift out of
   agreement with the site. The enumerated dates come out of `wide_index`, the
   same index pass the perennial date pages are built from, so a date in a feed
   is a date the site shows, by construction. The window rolls forward on every
   daily regeneration. 2,348 recurring events + 917 enumerated.
2. **There is no `VTIMEZONE`, and that is deliberate** — the queue item asks for
   "correct VTIMEZONE", and for these events the correct answer is none. All-day
   events are `DATE`-valued, so they carry no time and no zone; attaching one
   would shift every holiday by a day for any subscriber far enough east or west
   of whichever zone we picked. Christmas is December 25 wherever you are.

UIDs are stable by construction: `<slug>@todaycelebrates.com` for a fixed-date
row (one identity forever), `<slug>-YYYYMMDD@...` per enumerated occurrence, so
a corrected date replaces exactly that occurrence in a subscriber's calendar.
`DTSTAMP` is a fixed build stamp, not the run time — otherwise ~2,470 files
whose only daily change was a timestamp would churn the repo and the CDN every
night and tell every subscriber everything had been revised. The feeds are also
compared as **bytes**, not text, or Python's newline translation would report
every file changed on every run.

Linked, not hidden: observance pages get a line above the back-link
(download + `webcal://` subscribe), category pages one under the intro,
`/about/` a new "Subscribe to the calendar" section, and `llms.txt` names all
three URL shapes. Both affordances appear everywhere, so a device with no
calendar app registered for `webcal://` still has a working download.

## Files touched

| File | Change |
|---|---|
| `scripts/generate.py` | +323. `ICS_*` constants and the model comment; `ics_text` / `ics_fold` / `ics_date` / `ics_uid` / `ics_event` / `ics_calendar`; `write_bytes_if_changed`; `cal_links_html`, `cal_feed_links_html`; `ics_occ` in `generate()`; the feed-writing block; 8 new report keys |
| `scripts/templates/holiday.html` | +1. `<!--TC:CAL_LINKS-->` above the back-link |
| `public/styles/site.css` | +11. `.cal`, `.cal-add`, `.cal-note` (static markup, so no post-paint shift) |
| `public/_headers` | +16. `Content-Type: text/calendar` and a cache rule for the three patterns |
| `public/llms.txt` | +8. a "Calendar feeds" section |
| `scripts/README.md` | +112. "Calendar export (E5)" — the model, the stability rules, folding, sizes |
| `docs/EXECUTION_PLAN.md` | §3 boundary gains the generated `.ics` paths; E5 status; Run Log |
| `docs/REVIEW.md` | this file |

Nothing in `public/` is generated output in the diff: as always I ran the
generator into a throwaway directory, never into `public/`. **The ~2,470 `.ics`
files and the 2,465 changed pages appear in your working tree only after you run
the generator (or after the next daily Action).** Notion untouched.

## What you should check

- **The line on an observance page.** `/holiday/halloween/` — is a bordered box
  above the back-link the right weight for this, and is the wording right? It is
  the only new UI on the site.
- **A real subscribe, on a real device.** This is E5's acceptance criterion and
  the one thing I cannot do from here: subscribe to
  `webcal://todaycelebrates.com/calendar.ics` in Apple Calendar and add it by URL
  in Google Calendar once this is deployed. Everything structural about the files
  is verified; "it subscribes cleanly" is not.
- **`/category/food/calendar.ics`** is 530 observances. Subscribing to it is a
  lot of calendar. Worth deciding whether that is the feed you want to advertise.
- The content run's note that the tree was dirty: **that was my own work in
  progress**, not an unreviewed earlier run. Nothing is stacked.

## How I verified it

**201,453 checks, 0 failures** (`~/e5/verify.py` on my side; it is throwaway, not
in the repo). The ones that matter:

- **Reverse-transform against the pre-patch generator.** Ran HEAD's `generate.py`
  and the patched one into two fresh directories. Removing the one added `.cal`
  paragraph makes all **2,450 holiday pages byte-identical**; the same for the
  14 category pages and for `/about/` (its one button→link wording aside). Every
  `/day/` page, all 366 perennial pages, both year indexes, `/dates/`,
  `/categories/`, the home page, every data file **and `sitemap.xml` are
  byte-identical** — the feeds add no URLs and change no page content. Zero
  unexplained deltas; the only new files are the 2,465 `.ics`.
- **Structure, file by file, all 2,465.** CRLF throughout and no bare LF; no
  folded line over 75 **octets** (and fold/unfold is lossless, tested on
  multi-byte and 200-character strings); valid envelope; balanced `VEVENT`s;
  every content line matches the `NAME;PARAM=value:` grammar; every event carries
  UID / DTSTAMP / DTSTART / DTEND / SUMMARY / DESCRIPTION / URL / CATEGORIES /
  TRANSP / CLASS / SEQUENCE; `DTEND` is always `DTSTART` + 1 day; no `VTIMEZONE`
  anywhere; `SOURCE` on each file points at its own URL.
- **The dates agree with the site.** Every one of the 9,795 parsed events was
  checked against the recurrence engine: each fixed-date row's `DTSTART` is the
  exact date its page shows, each enumerated date is what the rule gives for that
  year, nothing is in the past, nothing is past the ten-year window, and every
  Friday-the-13th event really is one. Separately, every holiday the dated
  archive lists between today and 2026-12-31 (530 placements) has a matching
  event in `/calendar.ics`.
- **Composition.** 3,265 UIDs, no duplicates inside a file, none describing two
  different events; `/calendar.ics`'s UID set is exactly the union of the 2,450
  observance files, and exactly the union of the 14 category feeds.
- **Links resolve.** 1,230 `.ics` links sampled across pages (every category and
  `/about/` plus 400 observances): every `https` and `webcal://` path exists on
  disk.
- **Idempotent, properly.** A second run over the same directory: **0 files
  created, 0 changed, 2,465 unchanged**, and no page, data file or sitemap
  touched. That is what the fixed `DTSTAMP` and the byte comparison buy.
- **Rollover.** Simulated `--today 2027-06-15`: exit 0, 2,461 feed files, and the
  four rows whose lookup tables have expired (Belmont, Preakness,
  teach-your-children-to-save, Super Bowl Sunday — the known §7 issue, not caused
  by this) drop out of the feeds along with their pages, with **no page left
  linking a missing file**. A short feed is honest; an extrapolated date is not.
- **Generator run for the record** (`--today 2026-10-14`, throwaway dir):
  **exit 0, zero WARNING lines**, 5,669 files, 2,465 feeds, 3,265 events,
  type counts unchanged (40 typed / 2,410 untyped).

## Needs a decision

1. **The old in-browser button vs the new file.** `public/js/site.js` still
   builds a one-event `.ics` in the browser for the "Add to calendar" button in
   the `.tool` row. It now duplicates `/holiday/<slug>/event.ics`, which works
   without JavaScript and can be linked and subscribed to. I did **not** touch
   it: turning that `<button>` into an `<a>` changes the `.tool` row's markup on
   2,450 pages and CLS is still unmeasured, so it is your call. My
   recommendation: make it a link to the static file and delete
   `addToCalendar()`. Until then the page offers two routes to the same thing.
2. **Discovery.** The feeds are reachable from observance pages, category pages,
   `/about/` and `llms.txt` — but not from the home page or the footer, which is
   where a subscription feature earns its keep. A footer link touches every page
   on the site and is an IA decision, so I left it alone. Say the word and the
   next run adds it.
3. **1.9 MB for `/calendar.ics`.** Fine for Apple Calendar, and ~164 KB over the
   wire once the edge compresses it, but Google's limit for a subscribed URL is
   not something I could test from here. Two cheap levers if it bites: drop
   `DESCRIPTION` from that one feed (≈60% off, per-observance and per-category
   feeds unaffected), or publish a curated "major observances" feed — which wants
   E4's typing finished first. Related: should there be a feed of *only* federal
   holidays? That is the feed most people actually want, and it is one line once
   `Type` is populated.
4. **Still unmeasured, from E3 and E4: CLS**, plus real phone-width rendering of
   `/dates/`, the year pages and now the `.cal` box. All three need a deploy.

## Where the queue stands

**E5 is done** on every criterion I can check without a deploy: the three feed
shapes exist, `webcal://` links are in place, UIDs are stable run to run, and the
files are structurally valid. The one open criterion is "subscribes cleanly in
Apple Calendar and Google Calendar", which needs this deployed.

Next engineering run: **E4 with an assignment rule from you (question 1 in the
carried-over list), otherwise E6 — submitted occasions**, which is the next
unblocked item and is large enough to want its own run. E2's five decisions and
E3's two are still open and still do not block anything.

---

## Carried over, still unanswered

Unchanged from the 2026-10-13 engineering run; none of them blocked tonight.

1. **The assignment rule for E4's remaining ~2,410 rows** — the real blocker.
   Three boundaries an unattended run must not guess: **saints' feast days**
   (St. Patrick's, St. Nicholas, Feast of Saint George / James / Peter and Paul,
   St. Francis — all literally feasts, but observed secularly here: all
   *Religious*, or is the test "how it is actually observed"?); **secularized
   religious holidays** (Valentine's Day, Halloween, Christmas Eve, Feast of the
   Seven Fishes, Yule, Ostara, Naw-Ruz — Christmas Day only escapes because
   *Federal* settles it, which the single-select cannot say alongside
   *Religious*); and **Observance vs Fun**, which is most of the remainder. A
   usable rule might be: *Fun* = commercial or invented-for-fun origin,
   *Observance* = a cause, a profession, or a government/NGO proclamation. Say
   the word and the next run applies it and reports every call.
2. **Is `Season & Clock` really sixth?** Taken from §5's list verbatim; it puts
   the solstices and DST below every awareness day typed *Observance*.
3. **Untyped rows sort last** — predictable, but a choice. The alternative is
   slotting them where *Observance* sits.
4. **`Ascension` is stored as a fixed May 6 and is Easter + 39 days** — right for
   2027 by coincidence, **wrong from 2028**, and absent from
   `docs/FIDELITY_AUDIT.md` because that screen only catches weekday-ruled rows.
   E2/§7 work, and rule 5 is one item per run.
5. **Leap Day** sits unpublished; publishing it extends the dated archive by ≈142
   pages (and adds a `/holidays/2028/` page), or clamp `day_end` first.
6. **`Oktoberfest (ends in Germany)`** is wrong from 2027.
7. **Tax Day** overlaps `Income Tax Pay Day`.
8. **National French Fry Day** — July 13 vs the second Friday of July.
9. **Solstices / vernal equinox** already exist under other names — a naming
   call, not a coverage gap.
10. A bare **`/holidays/`** 404s; and the 2026 year page makes the archive's
    start line visible, which raises backfilling.
11. The Notion **`FAQ` field description is stale** (still says to bold the
    questions), and **`parse_faq()` is stricter than §4 describes** (it requires
    a trailing `?`).

---

## 2026-10-14 · content run · Christmas Eve, Veterans Day, Memorial Day (appended)

**All three published Live in Notion.** No repo files changed except `docs/`.

| Holiday | Row | Status | Sections |
|---|---|---|---|
| Christmas Eve | Dec 24, Order 1 | Live | all five |
| Veterans Day | Nov 11, Type Federal, Order 1 | Live | all five |
| Memorial Day | Floating, Type Federal, Order 1 | Live | all five |

Ambiguous titles: the database holds 8 rows matching "Veterans Day" and 5 matching
"Memorial Day". The main row was taken in each case — the one with `Type = Federal`,
`Order = 1` and the canonical date. `Published` and `Description` were not touched
on any row.

**Verification run**

- STEP 0: `git show HEAD:scripts/export_from_notion.py | grep -c LONGFORM_RELEASED_STATUSES`
  returned 2. The committed exporter carries the long-form fields.
- All three FAQ fields were run through the **committed** `parse_faq()` logic:
  5 pairs each, no headless answers. Questions are unbolded and end in `?`, so they
  satisfy both the documented rule and the stricter implemented one (open item 3 below).
- Source links are bare URLs throughout. No `[text](url)` anywhere in `Sources`.
- Generator smoke-run into a throwaway dir (`--site $HOME/gencheck`, never `public/`):
  exit 0, 5,669 files. This used the **modified working-tree** `generate.py` and the
  pre-export `holidays.json`, so it does not render the new content — see open item 4,
  still unresolved.

**Flagged for Jay**

1. **The working tree was already dirty outside `docs/` when this run started:**
   `public/_headers`, `public/llms.txt`, `public/styles/site.css`, `scripts/generate.py`
   (+321 lines), `scripts/templates/holiday.html`. That is unreviewed engineering work
   from an earlier run. This content run did not touch any of it and did not stack on it,
   but **the next engineering run will hit hard rule 2 and stop** until it is reviewed
   and committed.
2. **The repo folder was not attached when the task fired.** The run re-requested access
   to `/Users/digitashealth/Documents/GitHub/todaycelebrates` and it was granted, so no
   work was lost — but if the folder attachment keeps dropping, a future run may fire
   with nobody there to approve the prompt. Worth checking the task's folder config.
3. **All three pages run over §4's 600–900 word target** (≈915, ≈1,040, ≈1,170 words).
   Every claim carries a source and none of it is padding, so only one soft paragraph
   was cut. Whether to enforce the cap on dense-history holidays like these is a
   decision for Jay, not for an unattended run.
4. **Notion's `FAQ` property description is still wrong** — it still tells a future
   session to bold the question. Unchanged since 2026-10-11. Open item 2 below.

**Least confident claim across the three:** that Veterans Day was observed in October
"from 1971 through 1977". The Army Center of Military History page gives the 1971
effective date and the 1978 return but never states the span; the FAQ infers it.

**Omitted rather than guessed:** the liturgical origin of the Christmas Eve vigil and
Midnight Mass; public law numbers for the 1938, 1954 and 1975 Veterans Day acts; the
Sears advertisement in the NORAD story (NORAD says only "a promotion in a local
newspaper").

**Revert for any of the three:** set that row's `Content Status` back to `Draft` in
Notion. At the next regeneration the page returns to its short `Description` with
nothing lost.

### Addendum — the 2026-10-13 content run's work is not in Notion

Found after this run's Notion writes, while checking the project docs.

`claude/content-run-2026-10-13-tier1-12to14.md` states that the 2026-10-13
content run published **these same three rows** — Christmas Eve, Veterans Day,
Memorial Day — to `Content Status = Live`, with exact word counts (916 / 780 /
850) it says it computed in SQL *after* writing. It names the same three Notion
page ids this run used.

**Those fields were empty when this run started.** The opening query at
2026-10-14 10:20 UTC returned `Content Status = NULL` and `Body = NULL` on all
three. The three live pages were therefore still serving their short
`Description`, which is also why §6 items 12–14 were still unticked.

This is not the familiar missing-ticks failure. The 2026-10-12 run's three pages
(St. Patrick's Day, Independence Day, New Year's Eve) are still fully populated
and Live — Independence Day was read in full this run as the house-format
reference. So content written on 2026-10-12 survived and content the 2026-10-13
doc says was written on 2026-10-13 did not. Either those writes never reached
Notion despite what the doc records, or something cleared those three rows
between 2026-10-13 and today.

**Worth Jay's time, because the two possibilities need different fixes.** If the
writes never landed, a run can report success it did not have, and every project
doc of this kind becomes unreliable as a record. If the rows were cleared, three
pages of sourced work can disappear from Notion without anything noticing.

This run did not lose anything: it wrote to empty fields. The three pages are
Live now with content written today from sources gathered today.

**Sections A and B of that doc were deliberately NOT back-filled.** Its Run Log
line and REVIEW note describe content that is not in Notion and has now been
superseded by this run's drafts, so applying them verbatim would put a false
record in the plan. Its genuinely open recommendations are carried forward here
instead:

- **Derive the content queue from Notion, not from the §6 ticks** (published rows
  with `Body` empty and `Content Status` empty, ordered by next occurrence — what
  the Tier 5 rule already says). Raised by the 2026-10-11, -12 and -13 runs. Today
  the ticks happened to be right, but only because the Notion content was gone too.
- **Scope §2 rule 2 to engineering runs**, or say explicitly that a content run may
  proceed on a tree that is dirty outside `docs/`. Raised 2026-10-13; this run made
  the same judgment call again, for the same reasons.
- **Write the repo bookkeeping before the Notion writes.** Raised 2026-10-13 as a
  standing order; worth adopting.
- **`Type` is empty on Christmas Eve** (as on St. Patrick's Day and New Year's Eve)
  while Veterans Day and Memorial Day are `Federal`. Noticed, not acted on — that
  assignment is E4's blocked decision.
