# Review — 2026-11-08 engineering run

**Today is the 30-day re-plan checkpoint.** This file is the agenda for it.

## What I changed

**No source file, no generated file, no Notion row.** Only the two artifacts hard
rule 6 requires: this file and the Run Log entry in §8 of `docs/EXECUTION_PLAN.md`.

**Why nothing was started — eleventh consecutive night.** The dirty-tree gate
(`git status --porcelain -- . ':(exclude)docs'`) was **empty**, including untracked, before
and after. So the stop was at **rule 4, the queue**, not the gate: E1/E3/E5 are done, and
every remaining item is waiting on an answer from you — E2's five, E4's ~2,410 rows (★ B),
E6's upstream half (★ A), E7's two bullets. I checked, rather than assumed, that no answer
had landed: `HEAD` is still `3a27ff95` with a clean tree, and in Notion **no row carries
`Fun`, `Cultural`, `Observance` or `State`** — the four options ★ B would put into use — so
the typing has not moved. §5's "Queue empty?" note names the remaining candidates as
explicitly *not* unattended work, so nothing was invented.

### Files touched
```
docs/REVIEW.md          (this file, overwritten per rule 6)
docs/EXECUTION_PLAN.md  (§8 Run Log, one appended line)
```
Nothing else. If the morning diff shows anything under `scripts/`, `public/`,
`wrangler.jsonc` or `.github/`, I did not put it there.

---

## One new finding, and it is a measurement trap

**The Notion MCP connector's SQL mode silently drops `select` property values for some
rows.** Counting `Type` by group in SQL mode returned `(untyped) 2425 · Federal 11 ·
Religious 10 · Season & Clock 4` — which reads as **15 published rows having lost their
`Type` since the last export**, including Easter Sunday. It is wrong. Fetching Easter
Sunday in **rows** mode returns `Type: "Religious"`, and a server-side
`Type is_empty` filter against all fifteen names returns **zero rows**: every one is still
typed. The generator's own `type_counts` on the committed export agrees —
`(untyped) 2410 · Religious 23 · Federal 11 · Season & Clock 6`, unchanged — and the live
site still renders `data-t="religious"` on `/day/2027-03-28/`, `data-t="season-clock"` on
`/day/2026-12-21/`. Three sources against one; SQL mode is the outlier.

I am flagging it because **this run came within one tool call of reporting a phantom
live-data regression to you at 1am**, and because the Friday digest and the content runs
query this same database to report coverage counts. Any count either of them took from SQL
mode may be understated. The safe pattern, for whoever writes the next one: count with a
server-side `is_empty` / `is_not_empty` filter in **rows** mode, or read `type_counts`
out of the generator's own report. Not SQL.

No code and no data needed fixing, so nothing was changed. This belongs in §7 as a
standing note rather than buried in a log line — which is itself the open question at the
bottom of this agenda.

---

## What I verified

Generator on committed inputs, `--today 2026-11-08`, into throwaway directories under
`$HOME` (outside `$HOME/mnt`, since the mount cannot delete), both removed afterwards.
`public/` was never a target and carries no file modified today.

- **Exit 0**, **stderr 0 bytes**, **zero WARNING lines** in stdout or stderr. Twice.
- **5,695 files**, and a second same-date run is **`diff -rq` byte-identical** — idempotent.
- 2,450 observance / 378 dated / 366 perennial / 2 year-index / 19 simple pages.
- **2,465 `.ics`, 3,262 events**, `/calendar.ics` **1,991,688 bytes** — unchanged five
  nights running, so **★ G has not moved**.
- Cards off (`cards_created: 0`), `occasions_total: 0` — E6 still dormant, as intended.
- `type_counts` `(untyped) 2410 · Religious 23 · Federal 11 · Season & Clock 6`.
- Every problem array empty **except** the four known expiring lookup rows
  (`perennial_index_skipped`: `belmont-stakes`, `national-teach-your-children-to-save-day`,
  `preakness-stakes`, `super-bowl-sunday`; `day_index_skipped`: `super-bowl-sunday`).
  Those are §7's D2, not new.

## What you should check

1. **Nothing in the diff.** It is two docs files. That is the whole change.
2. **The checkpoint agenda below** — that is what tonight was actually for.

---

## Needs a decision

This is the checkpoint agenda. The queue has produced no engineering work for **eleven
nights**; every line below is a reason why, and the first two would end it.

- **★ B — the E4 `Type` assignment rule** for the remaining 2,410 rows (**26 days**).
  Still the only open answer that returns an unblocked item to the queue. The ordering
  question comes first because it decides whether a cheap partial batch is allowed at all:
  `UNTYPED_RANK` sits *below* `Fun`, so typing the 661 easy food/beer/coffee/dog rows as
  `Fun` would **promote** them above every row still waiting for a tier — 2,752 files
  changed, lead observance changed on 471 of 744 list pages. Smallest useful answer, one
  sentence: *"move `UNTYPED_RANK` above `Fun`, then type food/beer/coffee/dog as `Fun`"* —
  one line of code and 661 rows.
- **★ A — the Listed tier price and what it includes** (**24 days**). Unblocks E6's
  upstream half (form, Stripe Checkout, Worker) and E7's Featured tier.
- **The fidelity audit as queue item E8** — go/no-go only; it is already specified. It is
  also now the only *latent* problem that has become *visible*: `national-bison-day`'s
  published page states the first-Saturday rule while the generated Dates table will say
  Nov 7 from 2027, so the page contradicts itself in front of readers. `ascension` is a row
  an unattended run could fix correctly on night one (Easter +39; stored fixed May 6, right
  for 2027 by coincidence, true date 2028-05-25).
- **D1 — the three Notion property descriptions still contradict the code**
  (**twentieth flag**; re-confirmed in the live schema tonight). `FAQ` still instructs
  `**bold**` questions — the exact trap that silently emptied every FAQ before 2026-10-10,
  and still the advice a human writing a row today would follow. `Body` still lists
  `[text](url)`; `Timeline` still asks for `- **1927** —`. Three description edits, no code,
  no risk. Not applied because rule 4 confines me to §5 and this writes to Notion. Twenty
  flags is the argument for standing permission or two minutes of your time.
- **★ G — feeds still served uncompressed.** `/calendar.ics` ~1.99 MB per daily refresh
  where gzip would make it ~177 KB. Cloudflare zone setting, not code.
- **Bare `/holidays/` still 404s** (`/holidays/2026/` 200s) — the 10-12 small decision.
- **Carried forward unchanged:** ★ D (the home page's one layout shift in the stale-build
  window, and whether E3's "CLS stays 0.0000" should become a threshold), ★ E (hero poster
  band as a queue item?), ★ F (should a fixed-date feed event keep its history?), D2 (the
  four lookup tables expiring in 2027; `super-bowl-sunday` expires 2027-02-14), D3 (the
  attached folder: connected again tonight, as on every engineering run since 11-03).
- **Where method findings live** — now with a concrete cost. Tonight's SQL-mode trap is
  exactly the kind of finding that, recorded as a log line, every future run re-derives from
  scratch; the 11-07 run already lost two nights to a §7 instruction filed in a note about
  something else. Worth deciding at the checkpoint whether method findings become standing
  notes in §7.

### The structural question the checkpoint should actually answer

Eleven nights of a nightly engineering cadence have produced eleven "no item started"
entries. The machinery is working exactly as designed — gate clean, generator clean,
nothing invented — and that is the problem: **the queue is drained of anything an
unattended run is allowed to do.** Three options, none of which I should pick for you:
promote the fidelity audit to E8 and let the runs work it (one go/no-go, and it has ~24
rows of real work); answer ★ B's one-sentence ordering question and let E4 run for weeks;
or stand the nightly engineering run down to weekly until there is an item for it, and stop
spending a run a night on a clean no-op.


---

## Content run — 2026-11-08 (appended; the engineering run above owns the rest of this file)

**Published Live, three rows, Tier 5 T5-22 to T5-24.** All three are Nov 8, selected by the
Tier 5 rule (published rows with empty `Body` and empty `Content Status`, ordered by next
occurrence, tie broken by `Order`). Nov 8 `Order` 1 is Diwali, already Live, correctly skipped.

| Page | Words | Timeline | FAQ pairs |
|---|---|---|---|
| https://todaycelebrates.com/holiday/national-cappuccino-day/ | 871 | 6 | 5 |
| https://todaycelebrates.com/holiday/cook-something-bold-day/ | 665 | **omitted** | 5 |
| https://todaycelebrates.com/holiday/international-tongue-twister-day/ | 897 | 4 | 5 |

### What to spot-check

1. **`international-tongue-twister-day` is a new §7 fidelity candidate** and it is now in
   `docs/FIDELITY_AUDIT.md`. The row is `Annual` Nov 8; Nov 8 is the **second Sunday of November
   in 2026 and in no nearby year** (2024-11-10, 2025-11-09, 2026-11-08, 2027-11-14). The
   aggregators publish the day on Nov 8, Nov 10 *and* Nov 12 in different years — that is the
   weekday rule leaking through a fixed-date field. **Nothing was changed.** No acceptable source
   states the rule; this observance has no founding body, government page or news coverage at all,
   so unlike `national-bison-day` there is not even an authority to ask. The page states the
   conflict in both the History section and the FAQ rather than picking a side.
2. **The cappuccino page states a date tension instead of smoothing it.** Britannica puts the
   first attestation in eighteenth-century Vienna; Merriam-Webster dates the English word to 1893;
   Britannica puts the Italian espresso-based drink in the early twentieth century. The page
   reconciles these by saying the 1893 English use most likely described the Viennese ancestor —
   **flagged as an inference, not asserted as fact.** If you would rather the page simply reported
   the three dates without that reading, say so and it is a one-line change.
3. **`cook-something-bold-day` ships with no Timeline, on purpose.** Only one dated event
   (Scoville's 1912 paper) could be sourced, against §4's four-entry minimum, so the section was
   cut rather than padded. This is the third Tier 5 page to do that (after National Author's Day
   and the bittersweet-chocolate page).
4. **The tongue-twister page actively debunks a popular claim.** "She sells seashells" is widely
   said to be about the fossil collector Mary Anning; the **Natural History Museum's own biography
   of Anning never mentions the rhyme**, and no museum or scholarly source for the connection could
   be found. The page says it may be true and is not sourced. That is the exemplar's discipline
   applied to a claim readers will arrive believing — worth a look to confirm you want that tone.

### Least confident claims, named

- **The 1813 John Harris edition of *Peter Piper's Practical Principles*** rests on a *single
  secondhand line* in a Christie's catalog describing the later 1836 Philadelphia printing.
  Bonhams, HathiTrust, catalog.loc.gov, WorldCat and Open Library all refused automated access, so
  **no library record confirms it as a first edition.** Both the body and the Timeline say so
  explicitly. This is the weakest keystone date in tonight's three pages.
- **The 2013 MIT tongue-twister research is cited to Fox News**, an established outlet, because
  the Acoustical Society of America's press room for the 166th meeting and MIT News both returned
  nothing reachable. The abstract title, session number and the names of Shattuck-Hufnagel's
  co-researchers are therefore not stated anywhere on the page.
- **Scoville's 1912 paper**: the Wiley page could not be read. Author, title, journal and year come
  from the publisher's own listing; the **volume, issue and page numbers come from the
  Alimentarium's reference list for the same paper**, which `Sources` discloses.

### Claims cut for lack of a source

- *All three*: no founder, founding year or first observance. Nothing beyond aggregators addresses
  any of them, and all three pages say so in the body and in the first FAQ pair. For
  National Cappuccino Day the aggregators do not even agree on the **month** — one gives October.
- *Cappuccino*: **no inventor, patent year or company for the espresso machine.** Britannica names
  none, and the Bezzera / Pavoni / Gaggia dates that circulate everywhere appear only on
  coffee-retailer blogs. Jonathan Morris's 1948–1962 window is used instead because it is a
  published academic book chapter.
- *Cappuccino*: **no technical cappuccino standard** (millilitres, foam depth, milk temperature).
  The Istituto Nazionale Espresso Italiano is the body that sets one and **espressoitaliano.org
  returned a client error on all four URLs tried**, so nothing was cited from it.
- *Cook Something Bold*: **no current hottest-pepper record holder or Scoville figure.** Guinness
  publishes the category definition on a readable page but not the holder, so only the definition
  is cited. PubChem's body is JavaScript-gated, so only the molecular formula (from page metadata)
  comes from it; the capsaicin–pungency link is attributed to the Alimentarium, which does state it.

### Verification actually performed

- STEP 0 passed: committed exporter's `LONGFORM_RELEASED_STATUSES` count = **2**.
- `Published` re-read as still checked on all three rows; `Description` unchanged (141 / 192 / 133
  characters). **No `Published` checkbox was touched.**
- **FAQ verified by executing the real `parse_faq()`** from `scripts/generate.py` in the working
  tree against the exact stored text: **5 / 5 / 5** pairs, every question matched, every answer
  non-empty. Word counts by `wc -w` over the exact stored `Opening`+`Body`+`Timeline`+`FAQ`.
- Live slugs confirmed against the existing `public/holiday/` directories.
- Gate `git status --porcelain -- . ':(exclude)docs'` **clean before and after**. Nothing committed,
  nothing pushed, no source file and no generated output touched — `docs/` only, plus the three
  Notion rows.
- The exporter itself could not be run: still **no `NOTION_TOKEN` and no `.env`** in this clone.

### Unchanged, flagged for the twentieth run

The Notion property descriptions still contradict §4: `FAQ` instructs bolding the question (wrong
since 2026-10-10), `Body` still lists `[text](url)`, `Timeline` still asks for `- **1927** —`.
A new writer following the field descriptions instead of this plan would still produce a silently
broken FAQ. One-line fix in Notion, never made.

### Also noted, not acted on

A separate published row, **`International Tongue Twister Contest Day`**, exists with its own live
page. It is not a duplicate of `international-tongue-twister-day` and was left untouched.

**The revert, for any of the three:** set that row's `Content Status` back to `Draft` in Notion.
At the next regeneration the long-form text comes off and the page returns to its short
`Description`. Nothing is lost.
