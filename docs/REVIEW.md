# Review — 2026-11-12 engineering run

**No engineering item was started. Fifteenth consecutive night.** The stop is at
hard rule 4 (the queue), not the gate. Every §5 item is done or waiting on you.
The 11-08 re-plan checkpoint is now four days past.

If you read one thing tonight, read **The one structural choice** at the bottom.
It is the same choice as the last four nights and it is the only thing that
changes night sixteen.

## What I changed

**No source file, no generated file, no Notion row, no `.git` change.** Only the
two artifacts rule 6 requires.

```
docs/REVIEW.md          (this file, overwritten per rule 6)
docs/EXECUTION_PLAN.md  (§8 Run Log, one appended line)
```

## Why nothing was started

The gate (`git status --porcelain -- . ':(exclude)docs'`) was **empty**, untracked
included, before and after. In fact the whole tree was clean — you committed the
11-11 `docs/` files as `bfb45696` and merged `origin/main` as `6936c3f8`, so
**`HEAD` == `origin/main` == `6936c3f8`**. Nothing to pull tonight.

E1 / E3 / E5 are done. E2's five leftovers, E4's ~2,410 rows (★ B), E6's upstream
half (★ A) and E7's two bullets all wait on you. §5's "Queue empty?" names the
remaining candidates as explicitly *not* unattended work, so nothing was invented.

**Checked rather than assumed that no answer had landed.** A live `Type` count over
the Notion database returns **(untyped) 2414 · Religious 23 · Federal 11 · Season &
Clock 6** — byte-for-byte last night's figures, **zero** rows in `Fun`, `Cultural`,
`Observance` or `State`. ★ B has not moved. I also re-read your commit `bfb45696`:
both hunks are the two runs' own writes (the content-queue ticks and the Run Log),
so no answer arrived in the plan either.

**I did not `git fetch` tonight.** That question is still open below, and
`ls-remote` was enough because it showed no new commit. So no stray temp files this
time. Last night's **`.git/stale-fetch-tmp/` (97 files, 1.4 MB) is still there** —
delete it whenever you like, nothing references it.

## What I verified

Committed generator on committed inputs, `--today 2026-11-12`, into two throwaway
directories under `$HOME`, outside the mount. `public/` was never a target; both
directories were removed afterwards and the gate re-checked clean.

- **Exit 0, stderr 0 bytes, zero WARNING lines.** Twice.
- **5,699 files**, and the two runs are **`diff -rq` byte-identical** — idempotent.
- 2,450 observance / **382 dated** (horizon rolled to `2027-11-11`) / 366 perennial /
  2 year-index / 14 category / 19 simple.
- 2,465 `.ics`, 3,261 events, main feed **1,998,252 bytes**. Cards off,
  `occasions_total` 0 — E6 dormant, as intended.
- Every problem array empty — `pages_changed`, `pages_skipped`, `unresolved_holidays`,
  `unknown_types`, `stale_month_files`, `occasions_problems`, `perennial_pages_skipped`
  — **except** the four known expiring lookup rows in `perennial_index_skipped` and
  `super-bowl-sunday` in `day_index_skipped` (§7's D2). Not new.

One number moved: the main feed is **+2,798 bytes** on last night's 1,995,454. That
is the ten-year window's step-wise behavior corrected on 11-10, plus tonight running
against the *merged* `holidays.json` rather than one a regeneration behind. **Not a
trend and not a deadline** — I am not re-extrapolating the 11-09 mistake.

## What you should check

1. **The diff is two docs files.** Nothing else. If anything under `scripts/`,
   `public/`, `wrangler.jsonc` or `.github/` appears, I did not put it there.
2. Nothing else. There is no behavior change tonight to spot-check, and nothing to
   pull.

---

## Needs a decision

Unchanged from last night, in priority order, with the exact change already written
out for the two cheapest so a yes costs a sentence.

- **★ B — the E4 `Type` ordering question** (**30 days**). The one that refills the
  queue for weeks. The blocker is not the typing: `UNTYPED_RANK` currently sorts
  *below* `Fun`, so typing the 661 easy food/beer/coffee/dog rows as `Fun` today
  would **promote** them over every row still untyped — 2,752 files, lead observance
  changed on 471 of 744 list pages. One line in `scripts/generate.py`, **not**
  applied:

  ```python
  # line 821, currently:
  UNTYPED_RANK = len(TYPE_ORDER) + 1       # no Type at all -- sorts last
  # would become:
  UNTYPED_RANK = TYPE_RANK["Fun"] - 0.5    # untyped sorts above Fun, below the rest
  ```

  Reply *"yes, untyped above Fun"* and the next run lands that line plus the 661
  unambiguous `Fun` rows, with the before/after lead list in the morning diff.

- **The fidelity audit as E8 — go/no-go only.** Already specified, ~24 rows of real
  work, the only item needing no design judgment from you, and the only one with a
  *visible* defect behind it: `national-bison-day`'s published page states the
  first-Saturday rule while the generated Dates table will say Nov 7 from 2027, so
  page and table will contradict each other in front of readers. `ascension`
  (Easter + 39, stored fixed May 6, true 2028-05-25) is a row a run could fix
  correctly on night one.

- **★ A — the Listed tier price and what it includes** (**28 days**). Unblocks E6's
  form / Checkout / Worker and E7's Featured tier.

- **D1 — three Notion property descriptions still contradict the code**
  (**twenty-sixth flag**, re-read in the live schema tonight: `FAQ` still says the
  question goes in `**bold**`, `Body` still lists `[text](url)`, `Timeline` still
  asks for `- **1927** —`). Unapplied only because rule 4 confines me to §5. The
  whole fix:

  - `FAQ` → *FAQ: 3-5 pairs. Question on its own line as plain text — no bold; bold
    does not survive the export. Answer on the line(s) below, blank line between
    pairs. Feeds FAQPage structured data.*
  - `Body` → same text as now, with `[text](url)` removed from the allowed subset: a
    markdown link loses its URL on export, so body links must be bare URLs.
  - `Timeline` → *Timeline: 4-6 dated entries, one per line, as `- 1927 — what
    happened` (plain text, no bold). Every entry sourced in Sources.*

  Twenty-six flags on a three-field edit is the argument for standing permission to
  fix documentation that contradicts shipped code.

- **May a nightly run `git fetch`?** Read-only, no branch moved, no merge — but it is
  the only way to tell your commit from the workflow's, and on 11-11 it cost 97 stray
  temp files because deletion is blocked in your folder. Three answers are reasonable:
  *yes, fetch* (and ignore the litter); *yes, and grant this session delete permission
  in the repo* so it cleans up after itself; or *no, ls-remote only* — tonight I
  defaulted to that third answer.

- **Carried forward unchanged:** bare `/holidays/` 404s; ★ D (home-page shift in the
  stale-build window, and whether E3's "CLS stays 0.0000" should become a threshold);
  ★ E (hero poster band); ★ F (fixed-date feed history); ★ G (Cloudflare not
  compressing `text/calendar` — ~2 MB per refresh where gzip is ~177 KB; a zone
  setting, no deadline); D2 (four lookup tables expiring in 2027,
  `super-bowl-sunday` first, 2027-02-14); whether content-run method findings become
  standing §7 notes; and from the 11-11 content run, whether Chronicling America is
  permanently unreachable from these runs.

### The one structural choice

Fifteen nights, fifteen clean no-ops. The machinery is working exactly as designed —
gate clean, generator clean, nothing invented — and that is the problem: **the queue
is drained of anything an unattended run is permitted to do.** The three ways out are
unchanged:

1. **Answer ★ B** — one sentence, refills the queue for weeks.
2. **Promote the fidelity audit to E8** — one word, and it fixes a defect readers
   will see from 2027.
3. **Stand the nightly engineering run down to weekly** until there is an item for
   it — which costs nothing and stops producing a review note you have to read.

I will not pick for you. But doing none of the three means night sixteen reads
exactly like this one, and the nightly run is now costing you more attention than it
is returning.

---

# Appended — 2026-11-12 content run (Tier 5, T5-34 to T5-36)

The engineering review above is untouched; its open decisions still stand. This
section is the content run's note and owns nothing in `scripts/` or `public/`.

## What I published

Three Nov 12 rows, selected by the Tier 5 rule (published, `Body` empty,
`Content Status` empty, ordered by next occurrence). All written to Notion's
long-form fields and set `Content Status = Live`. **`Published` untouched on
every row.** They go live at the next regeneration.

- `/holiday/chicken-soup-for-the-soul-day/` — 919 words
- `/holiday/national-french-dip-day/` — 949 words
- `/holiday/guinness-world-records-day/` — 881 words

No section was omitted for lack of a source: all three carry a 6-entry Timeline
and a 5-pair FAQ. That is the first run in a while where nothing had to be cut.

## What you should check

1. **`guinness-world-records-day` is on the wrong date, and the page now says
   so.** Guinness World Records' own GWR Day page gives **Thursday, 19 November
   2026** and dates the observance's founding to **2004**. The Notion row is
   `Annual` Nov 12 — the second Thursday, not the third. I did not change the
   date: recurrence belongs to the deferred fidelity audit, and the right fix is
   a design choice (a `Floating` lookup of announced dates, like
   `super-bowl-sunday`, versus an annual refresh), not a data edit an unattended
   run should make. Logged in §7 and added to `docs/FIDELITY_AUDIT.md`.
   **The consequence is live this week:** the holiday appears on
   `/day/2026-11-12/` while its own page tells the reader Guinness says Nov 19.
   Bison Day made this error class visible from 2027; this row makes it visible
   today. That is now two rows arguing for promoting the audit to a queue item.
2. **The French dip invention is stated, not resolved.** Philippe the Original
   dates it to 1918 and tells a story; Cole's calls itself the originator and
   publishes no date and no account. Both opened in 1908. The LA Conservancy
   calls Cole's the "self-proclaimed inventor." Nothing acceptable settles it, so
   the page does not, and says why.
3. **The 144-rejections figure** on the Chicken Soup page is Forbes (2003)
   reporting Jack Canfield's own count. The page flags it as a claim by an
   interested party rather than a publisher's record. It is the least confident
   claim of the three pages.
4. **Cole's closing year is derived.** LAist says "it finally shut its doors in
   March" in an article dated 29 October 2026, after a closure announced in July
   2025 and postponed several times, so the page says March 2026. If that
   reading is wrong, it is wrong on the French dip page and in its Timeline.
5. **The bankruptcy filing day** is written as "late June 2024" because CBS News
   and the AP both report only that the filing was made "Friday." Neither names
   a date, so the page does not either.

## Needs a decision (content side)

Nothing blocking. One standing question, unchanged from previous runs: whether a
content run may correct a row's `Date`/`Recurrence` when the founding body itself
publishes the right answer. Today was the clearest case yet — Guinness publishes
its own date — and the run still left it alone. If the answer is yes, say so in
§4 and the next run can fix these as it finds them.
