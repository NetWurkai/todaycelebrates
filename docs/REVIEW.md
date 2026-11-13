# Review — 2026-11-13 engineering run

**No engineering item was started. Sixteenth consecutive night.** The stop is at
hard rule 4 (the queue), not the gate. Every §5 item is done or waiting on you.
The 11-08 re-plan checkpoint is five days past.

**One thing is new tonight, and it is not good news:** the Guinness World Records
date contradiction is now **live on the deployed site**, verified rather than
predicted. Details below under *What I verified*. It is the strongest argument yet
for the second of the three ways out.

## What I changed

**No source file, no generated file, no Notion row, no `.git` change.** Only the
two artifacts rule 6 requires.

```
docs/REVIEW.md          (this file, overwritten per rule 6)
docs/EXECUTION_PLAN.md  (§8 Run Log, one appended line)
```

## Why nothing was started

The gate (`git status --porcelain -- . ':(exclude)docs'`) was **empty**, untracked
included, before and after — eleventh clean night running. The whole tree was clean:
you committed the 11-12 `docs/` files as `41c766aa` and merged `origin/main`, so
**`HEAD` == `origin/main` == `bfbf70b8`**. Nothing to pull.

E1 / E3 / E5 are done. E2's five leftovers, E4's ~2,410 rows (★ B), E6's upstream
half (★ A) and E7's two bullets all wait on you. §5's "Queue empty?" names the
remaining candidates as explicitly *not* unattended work, so nothing was invented.

**Checked rather than assumed that no answer had landed.** A live `Type` count over
the Notion database returns **(untyped) 2414 · Religious 23 · Federal 11 · Season &
Clock 6** — identical to 11-11 and 11-12, with **zero** rows in `Fun`, `Cultural`,
`Observance` or `State`. ★ B has not moved. I also read `41c766aa` hunk by hunk:
every line is the two runs' own writes (three content-queue ticks, the §7 GWR
candidate, two Run Log entries). No answer arrived in the plan either.

**No `git fetch` again tonight** — `ls-remote` showed no new commit, so there was no
reason to risk it. 11-11's **`.git/stale-fetch-tmp/` is still there (97 files,
1.4 MB)**; nothing references it, delete it whenever you like.

## What I verified

Committed generator on committed inputs, `--today 2026-11-13`, into two throwaway
directories under `$HOME`, outside the mount. `public/` was never a target; both
directories were removed afterwards and the gate re-checked clean.

- **Exit 0, stderr 0 bytes, zero WARNING lines.** Twice.
- **5,700 files**, and the two runs are **`diff -rq` byte-identical** — idempotent.
- 2,450 observance / **383 dated** (horizon rolled one day to `2027-11-12`, so one
  new dated page and nothing rewritten) / 366 perennial / 2 year-index / 14 category
  / 19 simple.
- 2,465 `.ics`, 3,261 events, main feed **1,999,149 bytes** (+897 on last night —
  the ten-year window stepping, not a trend). Cards off, `occasions_total` 0.
- Every problem array empty — `pages_changed`, `pages_skipped`, `unresolved_holidays`,
  `unknown_types`, `stale_month_files`, `occasions_problems`, `perennial_pages_skipped`
  — **except** the four known expiring lookup rows in `perennial_index_skipped` and
  `super-bowl-sunday` in `day_index_skipped` (§7's D2). Not new.

**And one check that was not part of the routine.** Last night's content run warned
that `guinness-world-records-day` would contradict itself in front of readers. I
fetched the deployed page to see whether it actually does. It does:
`https://todaycelebrates.com/holiday/guinness-world-records-day/` returns 200 and the
**same page carries both "19 November 2026" (what Guinness publishes) and
"November 12" (the site's own date field)**. This is the first §7 fidelity defect
confirmed visible in production rather than inferred — `national-bison-day` is the
same error class but does not surface until 2027.

## What you should check

1. **The diff is two docs files.** Nothing else. If anything under `scripts/`,
   `public/`, `wrangler.jsonc` or `.github/` appears, I did not put it there.
2. **The live GWR page**, if you want to see the contradiction yourself — it is one
   page load, and it is the concrete version of the abstract argument below.

---

## Needs a decision

Unchanged in substance from last night; reordered, because the evidence moved.

- **The fidelity audit as E8 — go/no-go only.** Promoted to the top tonight. It is
  already specified (~24 rows in `docs/FIDELITY_AUDIT.md`), needs no design judgment
  from you, and is now the only open item with a defect **a reader can see today**
  rather than from 2027. `ascension` (Easter + 39, stored fixed May 6, true
  2028-05-25) is a row a run could fix correctly on night one. One word unblocks it.

  Note what E8 would *not* settle: `guinness-world-records-day` needs a model choice
  (a `Floating` lookup of announced dates, like `super-bowl-sunday`, versus an annual
  refresh), and `international-stout-day`, `fountain-pen-day` and
  `international-tongue-twister-day` have no acceptable source for their rules at all.
  E8 fixes the sourceable rows and leaves the rest flagged — which is still a dozen-odd
  real corrections.

- **★ B — the E4 `Type` ordering question** (**31 days**). The one that refills the
  queue for weeks. The blocker is not the typing: `UNTYPED_RANK` currently sorts
  *below* `Fun`, so typing the 661 easy food/beer/coffee/dog rows as `Fun` today would
  **promote** them over every row still untyped — 2,752 files, lead observance changed
  on 471 of 744 list pages. One line in `scripts/generate.py`, **not** applied:

  ```python
  # line 821, currently:
  UNTYPED_RANK = len(TYPE_ORDER) + 1       # no Type at all -- sorts last
  # would become:
  UNTYPED_RANK = TYPE_RANK["Fun"] - 0.5    # untyped sorts above Fun, below the rest
  ```

  Reply *"yes, untyped above Fun"* and the next run lands that line plus the 661
  unambiguous `Fun` rows, with the before/after lead list in the morning diff.

- **★ A — the Listed tier price and what it includes** (**29 days**). Unblocks E6's
  form / Checkout / Worker and E7's Featured tier.

- **D1 — three Notion property descriptions still contradict the code**
  (**twenty-seventh flag**, re-read in the live schema tonight: `FAQ` still says the
  question goes in `**bold**`, `Body` still lists `[text](url)`, `Timeline` still asks
  for `- **1927** —`). Unapplied only because rule 4 confines me to §5. The whole fix:

  - `FAQ` → *FAQ: 3-5 pairs. Question on its own line as plain text — no bold; bold
    does not survive the export. Answer on the line(s) below, blank line between
    pairs. Feeds FAQPage structured data.*
  - `Body` → same text as now, with `[text](url)` removed from the allowed subset: a
    markdown link loses its URL on export, so body links must be bare URLs.
  - `Timeline` → *Timeline: 4-6 dated entries, one per line, as `- 1927 — what
    happened` (plain text, no bold). Every entry sourced in Sources.*

  Twenty-seven flags on a three-field edit is the argument for standing permission to
  fix documentation that contradicts shipped code.

- **May a nightly run `git fetch`?** Read-only, no branch moved, no merge — but it is
  the only way to tell your commit from the workflow's, and on 11-11 it cost 97 stray
  temp files because deletion is blocked in your folder. Three reasonable answers:
  *yes, fetch* (and ignore the litter); *yes, and grant this session delete permission
  in the repo*; or *no, `ls-remote` only* — I defaulted to the third again.

- **May a content run correct a row's `Date`/`Recurrence` when the founding body
  itself publishes the right answer?** Raised by the 11-12 content run and now
  sharpened by the live GWR contradiction. A yes in §4 would have fixed that page
  last night without waiting for E8.

- **Carried forward unchanged:** bare `/holidays/` 404s; ★ D (home-page shift in the
  stale-build window, and whether E3's "CLS stays 0.0000" should become a threshold);
  ★ E (hero poster band); ★ F (fixed-date feed history); ★ G (Cloudflare not
  compressing `text/calendar`); D2 (four lookup tables expiring in 2027,
  `super-bowl-sunday` first, 2027-02-14); whether content-run method findings become
  standing §7 notes; whether Chronicling America is permanently unreachable from
  these runs.

### The one structural choice

Sixteen nights, sixteen clean no-ops. The machinery is working exactly as designed —
gate clean, generator clean, nothing invented — and that is the problem: **the queue
is drained of anything an unattended run is permitted to do.** Three ways out,
unchanged:

1. **Promote the fidelity audit to E8** — one word, and tonight's live-site check
   turned its justification from "a reader will see this in 2027" into "a reader can
   see this now."
2. **Answer ★ B** — one sentence, refills the queue for weeks.
3. **Stand the nightly engineering run down to weekly** until there is an item for
   it — costs nothing and stops producing a review note you have to read.

I will not pick for you. But night seventeen reads exactly like this one if none of
the three happens, and the nightly run is now costing you more attention than it is
returning.

---

## 2026-11-13 · content run · Tier 5 T5-37 to T5-39

**What changed.** Three Notion rows took long-form content and went to `Content Status = Live`,
so they publish at the next regeneration:

- World Kindness Day — https://todaycelebrates.com/holiday/world-kindness-day/ — 778 words
- National Bread Pudding Day — https://todaycelebrates.com/holiday/national-bread-pudding-day/ — 856 words
- Sadie Hawkins Day — https://todaycelebrates.com/holiday/sadie-hawkins-day/ — 794 words

In this repo only `docs/EXECUTION_PLAN.md` changed (three queue ticks in §6, one Run Log line in §8)
and this file. Nothing in `scripts/`, `public/` or at the root. Nothing committed, pushed or merged.
`Published` was not touched on any row; `Description` was not touched on any row.

**What to check.**

1. **Sadie Hawkins Day's date is not sourceable.** The Library of Congress holds a Capp original
   published 25 Sept 1943 whose catalog title reads "Sadie Hawkins Day comes on Nov. 6th". Nothing
   in an acceptable source explains how Nov 13 became the conventional date, and nothing confirms
   the universally repeated 15 Nov 1937 first-run date. The page says both of those things out loud.
   This is a §7 fidelity candidate: our stored date may simply be the aggregator consensus.
2. **Bread pudding's famous origin story is rejected on the page.** The 11th-century "poor man's
   pudding" line is everywhere, and its citation trail runs to a personal blog and a user-generated
   site. The page states that instead of repeating it. If Jay would rather the page stay silent than
   argue with the internet, that paragraph is the one to cut.
3. **Three of the bread-pudding citations are contents/index entries, not recipe bodies.** The
   Glasse 1796, Randolph 1836 and Beeton 1861 scans would not yield their recipe text; only their
   tables of contents and index were readable. `Sources` says so explicitly. The Simmons 1796 recipe
   text WAS retrieved and is quoted.
4. **World Kindness Day rests on one self-published source.** The World Kindness Movement's own site
   is the only account of the 1997 Tokyo conference and the 13 Nov 1998 launch; no corroborating
   government, UN or news source could be found. Its two pages word the Tokyo founding slightly
   differently (one gives the year, one the full date) — consistent, but worth knowing. No founder
   is named anywhere, and the page says that rather than inventing one.

**What to watch for.** The device bridge dropped mid-run, after the three Notion writes landed and
before any `docs/` edit, and reconnected roughly seven minutes later. If a future content run's Notion
rows are Live but its Run Log line is missing, that is the failure mode — the content shipped and the
bookkeeping did not.

**Verification run.** `scripts/generate.py` into a throwaway directory (never `public/`): exit 0,
2450 holiday pages, all three slugs present. `parse_faq()` from the committed `scripts/generate.py`
run against the exact submitted FAQ text: 5 / 5 / 5 pairs. Step 0 gate passed
(`LONGFORM_RELEASED_STATUSES` present in the committed exporter).

**Revert.** Set a row's `Content Status` back to `Draft` in Notion. At the next regeneration that page
returns to its short `Description` with nothing lost.
