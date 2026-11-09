# Review — 2026-11-09 engineering run

**No engineering item was started. Twelfth consecutive night.** The stop is at
hard rule 4 (the queue), not the gate. The checkpoint you were due to hold
yesterday is the thing that would end this, and as of tonight no answer has
landed.

## What I changed

**No source file, no generated file, no Notion row.** Only the two artifacts
rule 6 requires.

### Files touched
```
docs/REVIEW.md          (this file, overwritten per rule 6)
docs/EXECUTION_PLAN.md  (§8 Run Log, one appended line)
```

**One thing in the morning diff that is *not* mine, and will look like it is:**
`find public -newermt 2026-11-09` lists **112 files** with today's timestamp.
Those are from your own `git pull` at 01:59 (reflog `HEAD@{0}`, merge
`7553c549`) checking out the daily regeneration's commits. The tree is
**clean** — they match `HEAD` exactly. I wrote only into
`$HOME/verify-2026-11-09`, outside the repo, and removed it.

### Why nothing was started

The gate (`git status --porcelain -- . ':(exclude)docs'`) was **empty**,
untracked included, before and after. E1 / E3 / E5 are done. Everything else
waits on you: E2's five leftovers, E4's ~2,410 rows (★ B), E6's upstream half
(★ A), E7's two bullets. §5's "Queue empty?" names the remaining candidates as
explicitly *not* unattended work, so nothing was invented.

I checked this rather than assumed it. A rows-mode filter for the four `Type`
options ★ B would put into use — `Fun`, `Cultural`, `Observance`, `State` —
returns **zero rows**, and the generator's own `type_counts` is unchanged at
`(untyped) 2410 · Religious 23 · Federal 11 · Season & Clock 6`. (Rows mode and
the generator, not SQL mode — per the 11-08 finding.) Your `9108719e`
("Nov 8 Update") committed the runs' own `docs/` writes and nothing else; the
clone is now **in sync with `origin/main`** at `7553c549` for the first time
since 11-03.

## What I verified

Generator on committed inputs, `--today 2026-11-09`, into two throwaway
directories under `$HOME`, outside the mount. `public/` was never a target.

- **Exit 0, stderr 0 bytes, zero WARNING lines.** Twice.
- **5,696 files**, and the two runs are **`diff -rq` byte-identical** — idempotent.
- 2,450 observance / **379 dated** / 366 perennial / 2 year-index / 19 simple.
  379, up from 378: the horizon rolled a day, to `2027-11-08`.
- 2,465 `.ics`, 3,261 events. Cards off, `occasions_total` 0 (E6 dormant, as intended).
- Every problem array empty — `pages_changed`, `pages_skipped`,
  `unresolved_holidays`, `unknown_types`, `stale_month_files`,
  `occasions_problems`, `perennial_pages_skipped` — **except** the four known
  expiring lookup rows in `perennial_index_skipped` (§7's D2), which is not new.
- Throwaway directories removed. Gate re-checked clean after.

## What you should check

1. **The diff is two docs files.** Nothing else. If anything under `scripts/`,
   `public/`, `wrangler.jsonc` or `.github/` appears, I did not put it there.
2. **The 112 public/ timestamps are your pull, not a write.** Explained above.

---

## Needs a decision

Nothing here is new; the point is that it is the twelfth night and the
checkpoint has now passed. In priority order:

- **★ B — the E4 `Type` ordering question** (**27 days**). One sentence returns
  a working item to the queue and keeps it fed for weeks. Because `UNTYPED_RANK`
  sits *below* `Fun`, typing the 661 easy food/beer/coffee/dog rows as `Fun`
  today would **promote** them over every row still untyped — 2,752 files, lead
  observance changed on 471 of 744 list pages. So the answer needed first is the
  ordering, not the typing: *"move `UNTYPED_RANK` above `Fun`, then type
  food/beer/coffee/dog as `Fun`"* is one line of code and 661 rows.
- **The fidelity audit as E8 — go/no-go only.** It is already specified and has
  ~24 rows of real work, and it is the one option that needs no design judgment
  from you. It is also the only item with a *visible* defect behind it:
  `national-bison-day`'s page now states the first-Saturday rule while the
  generated Dates table will say Nov 7 from 2027. `ascension` (Easter +39,
  stored fixed May 6, true date 2028-05-25) is a row a run could fix correctly
  on night one.
- **★ A — the Listed tier price and what it includes** (**25 days**). Unblocks
  E6's form / Checkout / Worker and E7's Featured tier.
- **D1 — three Notion property descriptions still contradict the code**
  (**twenty-first flag**, re-read in the live schema tonight: `FAQ` still says
  the question goes in `**bold**`, `Body` still lists `[text](url)`, `Timeline`
  still asks for `- **1927** —`). Three description edits, no code, no risk.
  Unapplied only because rule 4 confines me to §5. Twenty-one flags is the
  argument for standing permission to fix it.
- **★ G, now with a date on it.** `/calendar.ics` is **1,995,454 bytes**
  uncompressed and grows ~3.8 KB a night as the horizon rolls, so it **crosses
  2 MB in about two days** — roughly 2026-11-11 — at 177 KB gzipped. Cloudflare
  zone setting, not code.
- **Carried forward unchanged:** bare `/holidays/` 404s; ★ D (home-page shift in
  the stale-build window, and whether E3's "CLS stays 0.0000" should become a
  threshold); ★ E (hero poster band); ★ F (fixed-date feed history); D2 (four
  lookup tables expiring in 2027, `super-bowl-sunday` first, 2027-02-14);
  whether method findings become standing §7 notes rather than log lines.

### The one structural choice

Twelve nights, twelve clean no-ops. The machinery is working exactly as
designed — gate clean, generator clean, nothing invented — and that is the
problem: **the queue is drained of anything an unattended run is permitted to
do.** Three ways out, and I should not pick for you: promote the fidelity audit
to E8; answer ★ B's ordering question; or stand the nightly engineering run down
to weekly until there is an item for it. Doing none of the three means night
thirteen reads exactly like this one.

---

## Content run — 2026-11-09 (appended; the engineering run owns this file)

**Published Live, Tier 5 T5-25 to T5-27** (Nov 9, `Order` 1/2/3):

- World Freedom Day — https://todaycelebrates.com/holiday/world-freedom-day/
- National Fried Chicken Sandwich Day — https://todaycelebrates.com/holiday/national-fried-chicken-sandwich-day/
- National Greek Yogurt Day — https://todaycelebrates.com/holiday/national-greek-yogurt-day/

897 / 900 / 894 words, five long-form sections each, 5 FAQ pairs each.
`Published` untouched; `Description` unchanged on all three.

**Verification went further than usual this run.** Rather than reimplementing
`parse_faq()`, the generator itself was run on a throwaway copy of
`holidays.json` patched with the stored FAQ / Timeline / Sources text, into a
throwaway site dir outside `$HOME/mnt`: **exit 0**, and all three rendered pages
carry 5 FAQ pairs plus a `FAQPage` JSON-LD block with 5 `mainEntity` items, no
literal `**`, and Timeline and Sources both rendering. The silent-failure path
§4 warns about is now closed against rendered output, not against a model of it.

### Worth a look

- **World Freedom Day is the first Tier 5 page with a fully primary-sourced
  origin** — Proclamation **7499 of November 9, 2001** (115 Stat. 2858), plus
  **8318 / 8599 / 9673** (2008 / 2010 / 2017) read directly. The page does *not*
  claim an unbroken annual series; only those four years were verified.
- **Two conflicts stated rather than resolved.** Wall deaths: State Department
  "at least 100 and likely more" vs. Library of Congress "over 130" — both cited,
  neither averaged. Chicken sandwich: Chick-fil-A's **1964** vs. the Georgia
  Historical Society marker's **"early 1960s"** — and the page says the marker was
  **co-erected with Chick-fil-A, Inc.**, so the two accounts are not independent.
  A third date (1967, in the Dwarf House page's own meta description) was rejected
  as an error against that page's own body text.
- **Least confident:** the fried-chicken-sandwich page's **$3.99** price and
  **August 12, 2019** launch rest on CBS News alone, and neither CBS nor Restaurant
  Dive calls that debut "nationwide" in those words.
- **Cut for want of a source:** the whole **Chobani founding story**
  (`chobani.com/about` carries no history at all) and the **USDA school-lunch Greek
  yogurt pilot** (USDA's own blog post returns a client error). German reunification
  and Reagan's "tear down this wall" were both left out of the World Freedom Day
  timeline for the same reason.

### Needs a decision

- **D1, twenty-second flag, now with a near-miss attached.** The `FAQ` property
  description still tells writers to bold the question. This run almost "fixed"
  the 2026-11-08 Cappuccino row, which puts a blank line between question and
  answer — it looked like that would make every answer parse as a question. It
  does not: `parse_faq()` requires a block-opening line to **end in `?`**, so both
  spacing styles are safe. No row was touched. But a description that contradicts
  the code is now actively generating false positives in review, not just
  confusion at write time.
- **`connectedFolders` was empty again at session start** despite the task
  declaring the repo folder — **ninth content run running**. Granted on request,
  so nothing was lost, but it is a per-run approval prompt that should not exist.
  Fix belongs at the task definition.
