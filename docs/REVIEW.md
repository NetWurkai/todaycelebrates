# Review — 2026-11-11 engineering run

**No engineering item was started. Fourteenth consecutive night.** The stop is at
hard rule 4 (the queue), not the gate. Every §5 item is done or waiting on you,
and the 11-08 re-plan checkpoint is now three days past.

## What I changed

**No source file, no generated file, no Notion row.** Only the two artifacts rule 6
requires — plus one `.git` housekeeping move described under *Method* below.

### Files touched
```
docs/REVIEW.md          (this file, overwritten per rule 6)
docs/EXECUTION_PLAN.md  (§8 Run Log, one appended line)
.git/stale-fetch-tmp/   (97 temp files git itself left behind; see Method)
```

### Why nothing was started

The gate (`git status --porcelain -- . ':(exclude)docs'`) was **empty**, untracked
included, before and after.

E1 / E3 / E5 are done. E2's five leftovers, E4's ~2,410 rows (★ B), E6's upstream
half (★ A) and E7's two bullets all wait on you. §5's "Queue empty?" names the
remaining candidates as explicitly *not* unattended work, so nothing was invented.

Checked rather than assumed that no answer had landed. A `Type` count over the live
Notion database returns **(untyped) 2414 · Religious 23 · Federal 11 · Season &
Clock 6** — zero rows in `Fun`, `Cultural`, `Observance` or `State`, so **★ B has not
moved**, and the generator's own `type_counts` agrees (2410 of them published).

## One thing that is new tonight: the clone is behind

`origin/main` moved for the first time in three nights, from `fbc9e807` to
**`023090d6` "Daily regeneration: 2026-11-10"**. It is the GitHub Action's own
commit — 55 files, all generated (`public/**` plus `scripts/holidays.json`) — and it
carries the 11-09 and 11-10 content runs' pages onto the live site. Nothing of yours
is in it and nothing of mine is.

**So `main` is one commit behind and your working tree is not.** Pull before or after
you commit the two `docs/` files; either order is fine, there is no overlap.

Note this also means tonight's verification ran against the **committed** `holidays.json`
at `fbc9e807`, one regeneration behind the live data. That is the right input to check
— it is the state of your clone — but it is why the file counts below are a day's worth
smaller than what is deployed.

## What I verified

Committed generator on committed inputs, `--today 2026-11-11`, into two throwaway
directories under `$HOME`, outside the mount. `public/` was never a target; both
directories were removed afterwards and the gate re-checked clean.

- **Exit 0, stderr 0 bytes, zero WARNING lines.** Twice.
- **5,698 files**, and the two runs are **`diff -rq` byte-identical** — idempotent.
- 2,450 observance / **381 dated** (horizon rolled a day, to `2027-11-10`) /
  366 perennial / 2 year-index / 19 simple.
- 2,465 `.ics`, 3,261 events, main feed 1,995,454 bytes (flat, as corrected last
  night). Cards off, `occasions_total` 0 — E6 dormant, as intended.
- Every problem array empty — `pages_changed`, `pages_skipped`, `unresolved_holidays`,
  `unknown_types`, `stale_month_files`, `occasions_problems`, `perennial_pages_skipped`
  — **except** the four known expiring lookup rows in `perennial_index_skipped` and
  `super-bowl-sunday` in `day_index_skipped` (§7's D2). Not new.
- `git fsck --connectivity-only` clean afterwards.

## Method — I ran a read-only `git fetch` tonight, which previous runs did not

Previous runs used `ls-remote` only. Tonight `ls-remote` showed a commit I had never
seen, and a SHA alone cannot tell me whether it is the nightly workflow or **your
answer to ★ B** — which is the difference between stopping and working. So I fetched.
No local branch moved, nothing was merged, the working tree was untouched, and the
answer was "it's the workflow".

One side effect worth knowing about: this session cannot delete files in your folder,
so the fetch could not clean up after itself and left **97 `tmp_obj_*` files** scattered
through `.git/objects/`. Git would have removed them itself. I moved all 97 into
**`.git/stale-fetch-tmp/` (1.4 MB)** so they sit in one place instead of 97 — **delete
that folder whenever you like**; nothing references it. `.git/objects/maintenance.lock`
was already there (dated 2026-10-08) and I left it alone.

Whether a nightly run may fetch is a small new question for you, below.

## What you should check

1. **The diff is two docs files.** Nothing else. If anything under `scripts/`,
   `public/`, `wrangler.jsonc` or `.github/` appears, I did not put it there.
2. **Pull** — you are one commit behind `origin/main` (generated output only).
3. Nothing else. There is no behavior change tonight to spot-check.

---

## Needs a decision

Only the last one is new. The rest are unchanged, in priority order, with the exact
change already written out for the two cheapest so a yes costs a sentence.

- **★ B — the E4 `Type` ordering question** (**29 days**). The one that refills the
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

- **The fidelity audit as E8 — go/no-go only.** Already specified, ~24 rows of real
  work, the only item needing no design judgment from you, and the only one with a
  *visible* defect behind it: `national-bison-day`'s published page states the
  first-Saturday rule while the generated Dates table will say Nov 7 from 2027, so page
  and table will contradict each other in front of readers. `ascension` (Easter + 39,
  stored fixed May 6, true 2028-05-25) is a row a run could fix correctly on night one.

- **★ A — the Listed tier price and what it includes** (**27 days**). Unblocks E6's
  form / Checkout / Worker and E7's Featured tier.

- **D1 — three Notion property descriptions still contradict the code**
  (**twenty-fourth flag**, re-read in the live schema tonight: `FAQ` still says the
  question goes in `**bold**`, `Body` still lists `[text](url)`, `Timeline` still asks
  for `- **1927** —`). Unapplied only because rule 4 confines me to §5. The whole fix:

  - `FAQ` → *FAQ: 3-5 pairs. Question on its own line as plain text — no bold; bold
    does not survive the export. Answer on the line(s) below, blank line between pairs.
    Feeds FAQPage structured data.*
  - `Body` → same text as now, with `[text](url)` removed from the allowed subset: a
    markdown link loses its URL on export, so body links must be bare URLs.
  - `Timeline` → *Timeline: 4-6 dated entries, one per line, as `- 1927 — what
    happened` (plain text, no bold). Every entry sourced in Sources.*

  Twenty-four flags on a three-field edit is the argument for standing permission to
  fix documentation that contradicts shipped code.

- **New, small: may a nightly run `git fetch`?** Read-only, no branch moved, no merge —
  but it is the only way to tell your commit from the workflow's, and tonight it cost
  97 stray temp files because deletion is blocked in your folder. Three answers are
  reasonable: *yes, fetch* (and ignore the litter); *yes, and grant this session delete
  permission in the repo* so it cleans up after itself; or *no, ls-remote only* — in
  which case a run can see that origin moved but never what moved, and I will stop
  reporting it as anything more than a SHA.

- **Carried forward unchanged:** bare `/holidays/` 404s; ★ D (home-page shift in the
  stale-build window, and whether E3's "CLS stays 0.0000" should become a threshold);
  ★ E (hero poster band); ★ F (fixed-date feed history); ★ G (Cloudflare not
  compressing `text/calendar` — 1.99 MB per refresh where gzip is 177 KB; a zone
  setting, no deadline); D2 (four lookup tables expiring in 2027, `super-bowl-sunday`
  first, 2027-02-14); whether method findings become standing §7 notes.

### The one structural choice

Fourteen nights, fourteen clean no-ops. The machinery is working exactly as designed —
gate clean, generator clean, nothing invented — and that is the problem: **the queue is
drained of anything an unattended run is permitted to do.** The three ways out are
unchanged: promote the fidelity audit to E8, answer ★ B's ordering question, or stand
the nightly engineering run down to weekly until there is an item for it. I will not
pick for you, but the cheapest is still: **★ B is one sentence and refills the queue;
the audit is one word and fixes a defect readers will see.** Doing none of the three
means night fifteen reads exactly like this one.

---

## Content run — 2026-11-11 · Tier 5 T5-31 to T5-33 (appended; engineering owns this file)

Published **Live**: National Sundae Day (Nov 11, Order 2), World Origami Day
(Order 3), Pocky Day (Order 4). `Published` untouched, `Description` untouched.
901 / 870 / 892 words. Render check: generator exit 0 on a patched throwaway
`holidays.json` into a throwaway dir outside the mount — 5 FAQ pairs and a
5-item `FAQPage` block on each page, no literal `**`, no `](http`.

### What to spot-check

1. **Sundae — the two-city fight is the page.** Two Rivers (1881) vs. Ithaca
   (April 3, 1892). The page states that Ithaca's own museum dates its one piece
   of documentary evidence **two different ways** (April 5, 1892 in text;
   October 5, 1892 in its own image caption), and that the universally repeated
   **"July 8, 1881" appears in no acceptable source**. If either reads as too
   blunt, that is the line to soften — but both are accurate.
2. **Origami — a sourced origin, with a founder conflict left open.** NOA's own
   site gives the 1980 designation and both reasons (four 1s; the 1918
   armistice). OrigamiUSA calls Lillian Oppenheimer a co-founder in one article
   while its own history page credits Michael Shall and others; a Japanese
   government page says she founded an Origami Center in 1958 and that
   OrigamiUSA postdates her death. Page follows OrigamiUSA's history page for
   the organization's own dates and flags 1958 as single-sourced.
3. **Pocky — Glico contradicts itself.** Corporate history: "Japan Anniversary
   Association." US marketing page: "Japan Holiday Association." Resolved toward
   the corporate history because the Japan Anniversary Association's registry
   does list the day. The registry's own detail page would not load, so 1999 is
   labeled Glico's claim.

### Needs a decision (content side, not blocking)

- **Chronicling America is unreachable from these runs.** Both the legacy API
  and the loc.gov collection endpoint failed today. That matters beyond this
  page: the Halloween exemplar recommends Chronicling America to readers, and
  it is the obvious primary route for any nineteenth-century food or custom
  claim. Worth knowing whether it is blocked for us permanently.
- **No new §7 fidelity candidate this run.** All three rows are `Annual` Nov 11
  with no weekday word and no weekday signature.
