# Review — 2026-11-17

**No engineering item started. Stopped at hard rule 2 for the third night
running.** The working tree is still carrying the 2026-11-14 E8b diff,
unreviewed for three days, and **not one byte of it has moved**. Nothing was
added to it. This run wrote only `docs/REVIEW.md` and §8 of
`docs/EXECUTION_PLAN.md`; `public/` was never written to, and no source file
was touched.

```
git status --porcelain -- . ':(exclude)docs'
 M public/llms.txt
 M scripts/README.md
 M scripts/generate.py
 M scripts/templates/holiday.html
```

+516 / −26. Non-`docs` diff SHA-256 **`92036aac4ae8…`** — identical to the hash
the 11-15 **and** 11-16 runs recorded, so three independent nights agree the
diff is unchanged. mtimes still `2026-11-14 06:02`–`06:10`. No untracked files
(checked with `--untracked-files=all`), nothing staged, no stashes, nothing
committed, pushed or merged.

**The written review of that diff is further down, under `# Review —
2026-11-14`.** This section was prepended, not written over — same reason the
11-15 and 11-16 runs gave: overwriting it would destroy the only description of
the diff sitting in your tree.

---

## What you should do — it is one action, and it reopens the whole queue

1. **Pull, then commit the E8b diff.** Your local `HEAD` is **`c6a6bbd6`**;
   `origin/main` is now **`97850fcf`** — you are **4 commits behind**, all four
   of them nightly Action regenerations (11-13 through 11-16, 92 generated
   files). I checked the overlap explicitly: **none of those 92 files is one of
   the four you have modified**, so the pull is clean and will not touch your
   work.
2. **Then the queue moves again.** Kwanzaa (★ A, hard date **2026-12-26**) is
   all that is left of E8b, and E8c → E8d sit behind it. **E8d is the Dec 15
   deliverable** (`/january/` and `/february/` live, in the sitemap, submitted
   for indexing) and it is two items deep in a queue that is fully serialized
   behind this one commit.

**The number worth reacting to:** 28 days to Dec 15, 39 to Dec 26. The
remaining E8 work is roughly five to eight nightly runs, so there is still
slack — but three of the nights that were supposed to absorb it have now gone
to the gate instead, and the runs cannot start themselves. Nothing here is a
design problem; it is a commit that takes a minute.

---

## I verified the pending diff against today's live data — it does exactly what
## the 11-14 run said it does

The 11-14 verification ran against a Notion export from before the seven span
rows were published, so it could not exercise the span path with real rows.
Tonight's could, without a Notion token and without touching your tree: the
nightly Action commits `scripts/holidays.json`, so **`origin/main`'s copy is a
real export made on 11-16**, with E8a's exporter and the seven rows
`Published` ON. I read it out of git into a throwaway file and ran both
generators against it.

It contains **7 span objects** and 2,457 rows. Both generators exited **0**,
**zero WARNINGs**, **stderr 0 bytes**. Diffing the two output trees:

| | files |
|---|---|
| committed generator (`SPANS_RENDER = False`) | 5,704 |
| pending generator (`SPANS_RENDER = True`) | 5,718 |

**+14 files, 5 changed, 0 removed, and nothing else moves among the other
5,704.** The 14 new files are an `index.html` and an `event.ics` for each of the
seven spans: `american-heart-month`, `black-history-month`,
`cervical-health-awareness-month`, `dry-january`, `lent`,
`national-blood-donor-month`, `national-impaired-driving-prevention-month`. The
5 changed are `calendar.ics`, `category/community/calendar.ics`,
`category/health/calendar.ics`, `data/search.json` and `sitemap.xml` — the exact
five the 11-14 run predicted.

Spot checks on the rendered output:

- `spans_total 7`, `spans_rendered true`, **`span_problems []`**, 7 pages
  created, 64 span feed events.
- Resolved dates are right: Black History Month and American Heart Month
  `2027-02-01 → 2027-02-28`; the three January spans `2027-01-01 → 2027-01-31`;
  National Impaired Driving Prevention Month `2026-12-01 → 2026-12-31`; **Lent
  `2027-02-10 → 2027-03-25`** (Ash Wednesday to Holy Thursday, per USCCB).
- Date line renders as **"All of February 2027"**.
- `Event` JSON-LD carries **both** `startDate` and `endDate`
  (`2027-02-01` / `2027-02-28`).
- The feed's exclusive end is correct: Lent ends `2027-03-25` and the VEVENT
  reads **`DTEND;VALUE=DATE:20270326`** — end + 1 day, as iCalendar requires.
- Enumerated, **no RRULE**, over the ten-year window, with
  `lent-20270210@…` / `lent-20280301@…` / `lent-20290214@…` UIDs.

**Also confirmed safe as it stands.** None of the seven span slugs has a live
page under `public/holiday/`, and the committed generator writes none for them,
so three nights of regenerating with those rows published has published nothing
and broken nothing. **Kwanzaa is correctly still unconverted** — it is the one
span-to-be with a live page, and converting it before this diff lands would
take that page stale, which is why §5 orders it after the commit.

---

## How this run was verified

- Gate run exactly as hard rule 2 words it, before and after; re-run at the end
  and still the same four files.
- `git fetch origin` (read-only; refs only, no working-tree change, no pull, no
  merge) to get a true picture of `origin/main` instead of a stale ref. The
  four incoming commits touch `public/**` and `scripts/holidays.json` only —
  **`scripts/generate.py` is untouched upstream, and `origin/main` still reads
  `SPANS_RENDER = False`**, so E8b is definitively not committed.
- `git show origin/main:scripts/export_from_notion.py | grep -c SPAN_KINDS` → **2**,
  so E8a *is* committed and the nightly export is carrying spans.
- Three generator builds into `$HOME/verify-1117/` (outside the repo, never
  `public/`): pending generator on your local `holidays.json`, and both
  generators on the 11-16 upstream export. All three exit 0, zero WARNINGs.

**A note on the file-count discrepancy the 11-16 run flagged.** Its 5,702 at
`--today 2026-11-15` and tonight's 5,704 at `--today 2026-11-17` differ by
exactly **+2** — one new day page per day of forward-window roll, which is what
should happen. So the 11-16 figure and tonight's are consistent with each other
and I do not think anything regressed. I will offer one hypothesis about the
unexplained 11-15 figure of 5,719 and flag it as a guess, not a finding: a
spans-on build of the same data comes to **5,718**, one off that number, so the
11-15 count may have been taken from a build that was writing the span pages.
Not worth a run's time to chase; worth knowing before anyone treats 5,719 as a
baseline.

**One thing I did that left a trace, reported rather than buried.** The
`git fetch` could not clean up after itself — deletes are blocked for me in
your folder — so it left `tmp_pack_oSyXUw`, `tmp_idx_Cr18y4` and a
`pack-bea9fbe6….keep` in `.git/objects/pack/`. They are inside `.git`, not the
working tree, so they do not show in the gate or in GitHub Desktop, and git
will not misbehave because of them. Four older sets from Oct 8, Oct 21 and
earlier are sitting there too, so this is a recurring side effect of these runs
rather than anything new tonight. `.git/objects/maintenance.lock` is dated
**2026-10-08** and predates tonight. Delete all of them whenever convenient;
nothing depends on them.

---

## Needs a decision

- **★ A — Kwanzaa.** Deadline **2026-12-26**. Unblocked the moment E8b is in
  `origin/main`; nothing to decide except when you commit. Unchanged from
  11-16.
- **Does the gate need an escape hatch?** This is the real question tonight, and
  it is a process question only you can answer. Hard rule 2 is doing its job —
  it has correctly refused to stack changes three nights in a row. But it has
  also converted "Jay was busy for three days" into "three engineering nights
  produced nothing", on the one item in the plan with a hard external deadline.
  Three options, and I am **not** picking one: (a) leave it exactly as is and
  accept that the queue advances only as fast as you commit; (b) let a run
  continue on a tree that is dirty **only** with a diff whose hash matches the
  one the previous run recorded, since an unchanged hash proves nothing is
  being stacked silently — the stacking risk the rule exists to prevent is a
  *changing* tree, not a frozen one; (c) keep the rule and add a notification
  so a blocked night reaches you the same morning instead of waiting for the
  Friday digest. Option (b) is a real loosening of your review gate and I would
  not take it without you saying so.
- **Still unanswered, carried from 11-14 and 11-16:** ★ B `Verified Through`
  empty on all seven published span rows · ★ C the hero tile on a span page ·
  ★ D whether `public/js/site.js` is source · ★ E the pinned `/about/` and
  `/categories/` count of 2,450 · ★ G which queue the nightly content run takes
  (Tier S or Tier 5) · ★ H the `World Diabetes Day` → `National Diabetes Month`
  `Part Of` relation. **★ F is closed** — see the 11-16 section; ignore the ★ F
  ask in the 11-15 and 11-14 sections.
- **Promoting the fidelity audit to a queue item.** Unchanged and still not
  unattended work: §7 carries two rows whose own pages contradict the site's
  date field in front of readers (`guinness-world-records-day` now,
  `national-bison-day` from 2027).

---
---

# Review — 2026-11-16

**No engineering item started. Stopped at hard rule 2: the working tree is
still dirty outside `docs/`.** The 2026-11-14 E8b diff is now **unreviewed for
two days** and is byte-for-byte unchanged. Nothing was added to it.

```
git status --porcelain -- . ':(exclude)docs'
 M public/llms.txt
 M scripts/README.md
 M scripts/generate.py
 M scripts/templates/holiday.html
```

+516 / −26. Non-`docs` diff SHA-256 `92036aac…` — **identical to the hash the
11-15 run recorded**, so not one byte has moved. mtimes still `2026-11-14
06:02`–`06:10`. No untracked files, nothing staged, no stashes. Nothing
committed, pushed, pulled, fetched or merged. `public/` was never written to.

**The review you want for that diff is further down, under
`# Review — 2026-11-14`.** It is intact: this section was prepended, not
written over, because overwriting it would destroy the only written review of
the diff sitting in your tree.

---

## What you should do

1. **Pull first, then commit the E8b diff.** `origin/main` is at **`87c9384c`**;
   your local `HEAD` is **`c6a6bbd6`**. One more nightly Action commit landed
   since the 11-15 run (which saw `df37bd0d`). Pull before you commit or
   you will conflict on the generated output.
2. **Then Kwanzaa (★ A).** It is the only thing left in E8b, it has a hard date
   of **2026-12-26**, and §5 makes it wait on this commit. Committing reopens
   the queue — the gate is now the single thing blocking all engineering.
3. **★ F needs nothing from you — it fixed itself.** Read the next section and
   then ignore the ★ F ask in the 11-15 and 11-14 sections below; it is stale.

Three nights of engineering have now been spent on the gate instead of the
Dec 15 / Dec 26 deadlines. That is the one number worth reacting to.

---

## ★ F is resolved: all 14 `Type` values are back, and the site shows them

Verified by the authoritative method (per-option `COUNT(*)` plus row
enumeration by name, never `GROUP BY`, per the 11-02 correction):

| `Type` | 11-15 | tonight | committed export |
|---|---|---|---|
| Federal | 11 | **11** | 11 |
| Religious | 12 | **24** | 23 (+ the new `Lent` span row) |
| Season & Clock | 4 | **6** | 6 |
| Cultural | 1 | 1 | — (new span row) |
| Observance | 5 | 5 | — (new span rows) |
| State / Fun | 0 | 0 | 0 |
| (untyped) | 2,428 | **2,414** | 2,410 |
| all rows | 2,461 | 2,461 | 2,450 |

Enumerated the rows rather than trusting the totals: **23 single-day Religious
rows + `Lent` = 24**, matching the committed export's 23, and **6 Season &
Clock**, matching its 6. Arithmetic closes exactly — 47 typed + 2,414 untyped =
2,461, and 2,410 original untyped + 4 new untyped span-era rows = 2,414.

**And it is live.** Live HTTP on the day lists, where the `Type` label actually
renders (`<span class="tg tg-…">`): `/day/2026-12-25/` → Federal,
`/day/2026-12-21/` → Season & Clock (First Day of Winter, one of the 14),
`/day/2026-11-29/` → Religious, `/day/2027-03-28/` → Religious (Easter Sunday,
the other row the 11-15 run named). All restored.

**Timing:** the Action is `cron: 0 8 * * *`. The 11-15 run read Notion de-typed
at roughly 06:30 UTC; the 08:00 UTC Action that same morning exported the
restored values and shipped them, which is also the commit that moved
`origin/main`. So the restore happened inside that ~90-minute window.

**The cause is still unknown, and that is the part worth a thought.** Fourteen
values vanished and returned with no recorded action by this session. If it
wasn't you, something else is writing to that database. Nothing is lost either
way, and no restore is needed — but it is worth knowing whether it can recur
before E8 puts more weight on `Type`.

*Correction for future runs:* the `<span class="tag">Observance</span>` in the
hero eyebrow is a **hard-coded literal on every holiday page** in the committed
template, not the `Type` label — E8b is what turns it into `<!--TC:HERO_TAG-->`.
I misread it as a site-wide regression for several minutes tonight. The `Type`
label only ever renders on day lists, as `tg tg-<slug>`.

---

## How this run was verified

Generator run read-only into `$HOME/verify-2026-11-16`, outside the repo and
outside `$HOME/mnt`. `public/` untouched.

**Working-tree generator**, `--today 2026-11-16`: **exit 0, zero WARNING lines,
stderr 0 bytes**, 5,703 files. Report: `unknown_types`,
`unresolved_holidays`, `stale_month_files`, `pages_skipped`,
`occasions_problems` and `span_problems` **all empty**;
`perennial_index_skipped` only the four known §7 rows; `spans_total` 0 and
`span_feed_events` 0 as expected, since the committed `holidays.json` is still
the pre-span export. 2,450 observance / 386 day / 366 perennial / 2 year-index
/ 19 simple pages; 2,465 `.ics` · 3,260 events.

**New tonight, and the check that matters most for the commit:** I rebuilt the
site a second time with the **committed** generator and template
(`HEAD:scripts/generate.py` at `SPANS_RENDER = False` plus
`HEAD:scripts/templates/holiday.html`), same inputs, into a second throwaway
directory — exit 0, stderr 0 bytes — and diffed the trees.

```
diff -rq  →  0 differences across all 5,703 files
```

**So the diff you are about to commit changes nothing on the day path with
today's committed export.** That is the strongest statement available without a
span-bearing export, and it is new information: the 11-14 run proved this with
fixtures, this proves it against the real committed data.

Also confirmed the span rows are parked safely: the 7 seeded rows are
`Published` ON, and `/holiday/lent/` and `/holiday/black-history-month/` both
return **404** live — correct, because the committed generator partitions spans
out. Nothing is stale or half-shipped.

I deliberately did **not** run `git fetch` or `git pull`. This shell cannot
delete files, and those commands leave `.git/*.lock` files behind that break
every later `git` command. `git ls-remote` is read-only and gave me the remote
head.

---

## One discrepancy I could not explain

The 11-15 run recorded **5,719 files** for its verification build. Re-running
tonight's (byte-identical) working-tree generator against the same unchanged
`holidays.json` at `--today 2026-11-15` gives **5,702**. Seventeen files
unaccounted for.

Tonight's numbers are internally sound — the two independent builds agree
byte-for-byte, the file-type census is `3,222 html + 2,465 ics + 15 json +
1 xml = 5,703`, and the only difference between the 11-15 and 11-16 trees is
exactly one new day page (`/day/2027-11-15/index.html`), which is precisely
what a one-day roll of the forward window should produce. So I do not think
anything regressed. I think the 11-15 figure counted a slightly different set
of files. **Flagging it rather than smoothing it over**, because that number is
the one a future run would compare against.

---

## Needs a decision

- **★ A — Kwanzaa.** Deadline **2026-12-26**, and the only item with a date on
  it. Unblocked the moment E8b is in `origin/main`. Nothing to decide except
  when you commit.
- **★ F — closed.** No decision needed; see above. The remaining open question
  is only *why* it happened, which matters for confidence, not for the site.
- **Still unanswered, carried from 11-14:** ★ B `Verified Through` empty on all
  seven published span rows · ★ C the hero tile on a span page · ★ D whether
  `public/js/site.js` is source · ★ E the pinned `/about/` and `/categories/`
  count of 2,450 · ★ G which queue the nightly content run takes (Tier S or
  Tier 5 — it has now bitten twice) · ★ H the `World Diabetes Day` → `National
  Diabetes Month` `Part Of` relation.
- **Promoting the fidelity audit to a queue item.** §7 now carries two rows
  whose pages contradict the site's own date field *in front of readers*
  (`guinness-world-records-day` today, `national-bison-day` from 2027). Not
  something an unattended run should start.

---
---

# Review — 2026-11-15

**No engineering item started. Stopped at hard rule 2: the working tree is
still dirty.** Last night's E8b diff has not been committed, so tonight's run
appended nothing to it.

```
git status --porcelain -- . ':(exclude)docs'
 M public/llms.txt
 M scripts/README.md
 M scripts/generate.py
 M scripts/templates/holiday.html
```

That is the **2026-11-14 E8b diff**, unreviewed for one day and **byte-for-byte
unchanged**: non-`docs` diff hash `92036aac`, mtimes still `2026-11-14
06:02`–`06:10`, no untracked files anywhere. Nothing committed, pushed or
merged tonight. `public/` was never written to.

**The review you want this morning is the one below this section**, under
`# Review — 2026-11-14`. It is intact — this section was prepended, not
written over, because overwriting it would have destroyed the review for the
diff you are about to read.

---

## What you should do

1. **Review and commit the E8b diff** (GitHub Desktop). It is the whole reason
   the queue is stalled — the gate stays shut and every further engineering
   night is a no-op until it lands.
2. **Pull first.** Read-only `git ls-remote` puts `origin/main` at `df37bd0d`;
   local `HEAD` is `c6a6bbd6`. The clone is behind. Nothing was fetched.
3. **Then ★ F below** — it is live on the site right now and does not wait for
   the commit.

---

## ★ F is now live, and it is the one thing that got worse overnight

Re-verified tonight, read-only. **All 14 rows still have `Type` empty in
Notion, and the loss has now reached readers.**

Method, per the 2026-11-02 correction in §8: **per-option `COUNT(*)` plus a row
enumeration, never a `GROUP BY`** (a `GROUP BY` over `Type` mis-buckets typed
rows and invents a fake regression).

| `Type` | Committed export | Notion tonight |
| --- | --- | --- |
| Federal | 11 | 11 |
| Religious | 23 | 12 — *but 1 of those is `Lent`, a new span row, so 11 of the original 23 survive* |
| Season & Clock | 6 | 4 |
| Cultural | 0 | 1 — new span row |
| Observance | 0 | 5 — new span rows |
| untyped | 2,410 | 2,428 |
| **all rows** | **2,450** | **2,461** |

The arithmetic closes exactly: `2,410 + 14 de-typed + 4 new untyped = 2,428`,
and the 7 span rows account for every new typed value. Row enumeration by name
confirms all 14 are `Type = null` and all 14 are still `Published = __YES__`:

> Easter Sunday · Palm Sunday · Pentecost · Ascension · Advent Sunday · Easter
> Monday · Eid al-Fitr · Islamic New Year · Orthodox Christmas Day · Purim ·
> Tu BiShvat · Assumption of Mary *(Religious)* · First Day of Winter · The
> First Day of Summer *(Season & Clock)*

**Two things are new tonight, and they point opposite ways:**

- **Good: it is not spreading.** 11 original Religious rows survive tonight,
  the same 11 as last night. Nothing was de-typed in the last 24 hours. This
  looks like one event between the 11-13 and 11-14 exports, not an ongoing
  process.
- **Bad: the 08:00 UTC Action has already shipped it.** Live HTTP checks:
  `/holiday/easter-sunday/` and `/holiday/first-day-of-winter/` return **200
  with no type label in the page**, while `/holiday/christmas-day/` and
  `/holiday/thanksgiving-day/` still render **Federal**. So the 14 have lost
  their type label on the live site and now sort after every typed row on day
  lists. This happened independently of the uncommitted diff and will persist
  through every regeneration until the Notion values come back.

**Still not restored, deliberately.** Rule 2 stopped this run, restoring is not
a §5 queue item, and — the real reason — *something* cleared 14 values in a
live database and nobody knows what. Writing them back without knowing the
cause risks papering over a job or automation that will simply do it again,
and tells you nothing. The values are recoverable from the committed
`scripts/holidays.json`, which still holds all 14 (verified tonight), so
nothing is lost. **This is your call: say the word and a run restores all 14
from that file in one pass.**

---

## How this run was verified

The generator was run anyway — read-only, into a throwaway directory outside
the repo (`$HOME/verify-2026-11-15`), with the **working tree's** generator
(the uncommitted E8b one), `--today 2026-11-15`:

- **exit 0, zero `WARNING` lines, stderr 0 bytes**
- 5,719 files · 2,450 observance pages · 366 perennial · 385 day · 2 year-index
  · 2,465 `.ics` files · 3,260 events
- `unknown_types`, `unresolved_holidays`, `stale_month_files`, `pages_skipped`,
  `occasions_problems`, `span_problems` **all empty**
- `perennial_index_skipped` only the four known §7 rows (`belmont-stakes`,
  `national-teach-your-children-to-save-day`, `preakness-stakes`,
  `super-bowl-sunday`)
- `spans_total: 0`, `span_feed_events: 0` — expected: `scripts/holidays.json`
  is the committed pre-span export, so the span path correctly produces nothing
  and the build is byte-identical to the pre-E8b site. This is the same result
  that made publishing E8b safe.
- `public/` never written; the directory was removed afterwards.

So the uncommitted diff still builds clean one day on. Nothing blocks the
commit.

---

## Needs a decision

**Nothing new tonight.** No engineering work was done, so no new questions were
created. Everything open is below, unchanged, in the 2026-11-14 section:

- **★ A — Kwanzaa**, deadline **2026-12-26**. Still the one with a date on it,
  and it cannot start until the E8b diff is committed.
- **★ F — the 14 de-typed rows.** Restated above because it is now live.
- ★ B `Verified Through` · ★ C the span hero tile · ★ D is
  `public/js/site.js` source · ★ E the pinned `/about/` count · ★ G the
  content queue · ★ H the `Part Of` relation — all unanswered.

---
---

# Review — 2026-11-14

**Item: E8b — span pages, feeds, structured data.** The gate was clean
(`git status --porcelain -- . ':(exclude)docs'` empty; whole tree clean,
untracked included). `HEAD` = `c6a6bbd6` ("Fri 11-13-26") and the
`origin/main` ref points at the same commit, so **E8a is committed** —
`git show origin/main:scripts/export_from_notion.py | grep -c SPAN_KINDS`
returns 2 — which is exactly the condition §5 names for starting E8b. The
first unblocked engineering item in sixteen nights.

Nothing committed, pushed or merged. `public/` was never written to: every
build went into throwaway directories outside the repo.

---

## What changed, and why

A resolved span now gets a real page, a real feed and a real index entry.
E8a had worked out every span's next occurrence and then thrown it away;
this run spends it.

| | |
| --- | --- |
| A page | `/holiday/<slug>/`, from the existing `holiday.html` |
| A feed | `/holiday/<slug>/event.ics`, and its events in `/calendar.ics` and its category's feed |
| An index entry | `sitemap.xml` and `data/search.json` |

**`render_span_page()` is a sibling of `render_page()`, not a branch inside
it.** That is the one structural decision worth knowing: a day page is
byte-identical to the pre-E8b build *by construction*, because no line of the
day path was touched. `holiday.html` gained three markers — `HERO_TAG`,
`CAL_BUTTON`, `ASIDE_LABEL` — and each is filled with precisely the literal
that used to sit there hard-coded, so day pages do not move a byte either.

What a span page says differently: the hero pill reads **Month / Week /
Season** instead of "Observance" (a `Range` shows as "Season" — nobody calls
Lent a range); the date line is *All of February 2027*, *May 6–12, 2027* or
*Feb 10 – Mar 25, 2027*, with both years when the span crosses New Year; the
spec list's Date row carries `<time datetime="2027-02">` for a whole month and
two `<time>` elements otherwise; the dates table lists ranges and lengths; and
the aside becomes **"Days inside this month / week / season"**, built from the
Notion `Part Of` relation.

**`Event` JSON-LD carries `startDate` *and* `endDate`.** `startDate` alone
would tell Google that Black History Month happens on February 1 and is over.

**Feeds are enumerated, never an RRULE.** Black History Month ends Feb 28 in
2027 and Feb 29 in 2028, and a floating span has no `BYDAY` form, so a
recurrence rule would be a second date engine free to disagree with the site —
the same reasoning E5 already applies to rule-dated days. One all-day `VEVENT`
per occurrence over the same ten-year window the perennial pass uses, `DTEND` =
last day + 1 (iCalendar's exclusive end), existing `<slug>-YYYYMMDD@` UIDs.

**Notion: the seven seeded span rows are now `Published`.** S-1 through S-7
(National Impaired Driving Prevention Month, Dry January, Cervical Health
Awareness Month, National Blood Donor Month, Black History Month, American
Heart Month, Lent). This is safe before you commit, and I checked it rather
than assumed it: the **committed** generator produces output that is
byte-for-byte identical whether span rows are present or absent, so tonight's
and tomorrow's regenerations publish nothing new. The seven pages appear at the
first regeneration **after** this diff lands.

---

## Files touched

```
scripts/generate.py              +448 / -24   source
scripts/templates/holiday.html   +3 / -3      source (three markers)
scripts/README.md                +86 / -8     source (new "E8b" section)
public/llms.txt                  +1           source (§3 lists it as source)
docs/REVIEW.md                   this file
docs/EXECUTION_PLAN.md           §5 E8b status + §8 run log
```

Nothing generated was edited. No `public/` page, feed, sitemap or data file is
in the diff.

---

## What to check

1. **The seven pages, after you commit and the Action deploys.**
   `https://todaycelebrates.com/holiday/black-history-month/` is the one to
   look at first: hero pill, the "All of February 2027" line, the dates table,
   and the aside (which will be empty until `Part Of` relations are set).
   `/holiday/lent/` is the floating, two-month, "Season" case.
2. **One feed, in a real calendar.** `/holiday/black-history-month/event.ics`
   should drop in as a single all-day block covering February, not a 28-day
   stack. This is also the two-minute check E5 has been waiting on.
3. **The diff in `scripts/generate.py`** is large but it is almost all new
   code in one block. The edits to *existing* functions are four and small:
   `ics_event` gained a `last_day=None` keyword, `render_longform` gained a
   `span_occ=None` keyword, `render_page` fills two new marker keys, and the
   search-index block now appends spans.
4. **Then Kwanzaa** — see ★ A below. It is the one piece of E8b I deliberately
   did not do, and it has a December 26 deadline.

---

## How it was verified

Generator run into throwaway directories at `--today 2026-11-14`, `public/`
never written, with `public/styles`, `ads`, `js` and `images` seeded first (so
the `?v=` asset hashes match — the 2026-10-27 lesson).

- **No span rows: 0 differences across all 5,733 files** against the committed
  generator and the committed templates. The byte-identity half of E8b's
  acceptance criterion, measured rather than asserted.
- **Committed generator, span rows present vs absent: 0 differences.** This is
  what makes publishing the seven Notion rows tonight safe.
- **With the seven real rows: exit 0, zero WARNINGs, stderr 0 bytes.** Exactly
  five existing files change — `calendar.ics`, the community and health
  category feeds, `data/search.json`, `sitemap.xml` — and seven page-and-feed
  pairs are added. Every other file is byte-identical.
- **With ten rows** (the seven plus three fixtures for shapes the real seven
  don't cover: a fixed week inside one month, a year-crossing Kwanzaa-shaped
  range, a floating seven-day week off a weekday rule): **136,182 structural
  checks, 0 failures**. RFC 5545 shape (CRLF, no folded line over 75 octets),
  `DTEND` exclusive and after `DTSTART`, no `RRULE` / `VTIMEZONE` / `TZID` /
  `METHOD` / `ORGANIZER` / `VALARM`, UIDs unique, every span event present
  exactly once in both the whole-site and its category feed, both JSON-LD dates
  present and distinct, every internal link on every span page resolving to a
  file the build wrote, no unfilled template marker, sitemap free of duplicates
  and of feed URLs, `search.json` sorted and unique.
- **Determinism:** two runs from the same inputs into fresh directories are
  byte-identical, so UIDs are stable run to run. A **one-day roll** changes no
  span feed file at all — the feature adds no nightly churn.
- **Rollover:** at `--today 2027-03-26`, the day after Lent 2027 ends, Lent
  rolls to 2028-03-01 – 2028-04-13 (Easter 2028 is April 16) and Black History
  Month to a **29-day** February. The leap year is the whole argument against
  an RRULE, and it behaves.
- **The warning paths fire.** A fixture with `Verified Through` 2026 and a 2027
  occurrence produced the "confirm with the sponsor" warning; a fixture day row
  mis-marked `Part Of` a week it falls outside produced the new "check the
  Part Of relation" warning. Both carry GitHub annotations.

---

## Judgment calls I made rather than asked about

- **A per-span `event.ics` is written**, though E8b's wording names only
  `calendar.ics` and the category feeds. The span page offers that download
  (the markup is shared with day pages), so not writing it would ship a 404.
- **The in-browser "Add to calendar" button is removed from span pages.**
  `/js/site.js` builds a one-day event out of `data-d`; on a month that is
  simply wrong. Extending the script would change shared chrome and move every
  page's bytes, so the button is gone from span pages and the correct `.ics`
  download stays. See ★ D.
- **Breadcrumbs are `Today / Calendar / <Name>`** and the back-link points at
  the start month's block on `/dates/`. A span has no single date, so a
  perennial page is the wrong parent; E8d's month hub is the right one and
  replaces both.
- **A `Part Of` member whose own date falls outside the span is reported, not
  hidden.** Silently filtering it would make a mis-set relation invisible.
- **A span whose slug collides with a day row's is refused** and the day keeps
  the URL, with a span problem reported.

---

## Needs a decision

**★ A — Kwanzaa, and the order it has to happen in. This one has a date on it.**
E8b's sub-item list includes converting the Kwanzaa row to `Span` = Range
(2026-12-26 → 2027-01-01). I did **not** do it, deliberately, because doing it
tonight would break the live page. With the committed generator at
`SPANS_RENDER = False`, a Kwanzaa row carrying a `span` object is partitioned
out of the day pipeline and nothing is rendered for it: the existing
`/holiday/kwanzaa/` page would go stale and drop out of the sitemap,
`search.json` and every calendar feed at the next regeneration, with its
long-form content sitting in Notion, invisible. The conversion is only safe
*after* this diff is committed. **Kwanzaa 2026 starts December 26**, and §5
requires it to render as a span before then — so the sequence is: commit this,
then the conversion (either you, in Notion, once it is pushed, or the next
engineering run). Please say which, because an unattended run will otherwise
treat E8c as next.

**★ B — `Verified Through` is empty on all seven published span rows.** The
generator's "dates are verified only through *N*" warning therefore cannot ever
fire for them: it is the one guard against a span's dates quietly going stale,
and it is switched off by an empty field. Filling it means confirming each
span's dates on the sponsor's own page, which is sourcing work, not a value I
should guess. Tier S lists `Verified Through` as a required field; should a
content run backfill it for S-1…S-7?

**★ C — the hero tile on a span page.** It shows the start date (a large ghost
"1" and a FEB/1/Monday tile on Black History Month). It is decorative and
`aria-hidden`, so nothing is wrong, but "1" is an odd thing to shout on a page
whose subject is a whole month. A span-specific treatment is a CSS and design
change on a template shared with 2,450 pages, which is your call, not an
unattended one.

**★ D — is `public/js/site.js` source or not?** §3's file boundary lists it on
**neither** side. It is clearly not generated (the generator hashes it for
cache-busting), but it is also not on the safe-to-edit list, and editing it
moves every page's `?v=` and therefore every page's bytes. I left it alone.
Worth one line in §3 either way, and the answer decides whether a span-aware
in-browser calendar button is ever buildable.

**★ E — `/about/` and `/categories/` still say 2,450.** I pinned both to the
single-day count, because that is what their per-category lists add up to,
while `search.json` now carries 2,457 entries. E8c adds spans to the category
pages, and all three numbers should move together there. Flagging it so it
isn't read as an oversight.

---

**★ F — unrelated to E8b, and it needs you: 14 rows have lost their `Type`
in Notion since yesterday's export.** I checked the E4 typing count tonight
rather than copying last night's figure, and it had moved in the wrong
direction. The committed `scripts/holidays.json` (exported 2026-11-13) carries
`Religious 23 · Season & Clock 6 · Federal 11 · (untyped) 2,410`. Notion right
now, excluding the seven span rows I published, carries `Religious 11 ·
Season & Clock 4 · Federal 11 · (untyped) 2,424`. The fourteen rows that were
typed on Wednesday and are untyped now:

> **Religious** — Advent Sunday, Ascension, Assumption of Mary, Easter Monday,
> **Easter Sunday**, Eid al-Fitr, Islamic New Year, Orthodox Christmas Day,
> Palm Sunday, Pentecost, Purim, Tu BiShvat
> **Season & Clock** — First Day of Winter, The First Day of Summer

**This takes effect at the next regeneration, whether or not you commit
tonight's diff.** A row with no `Type` loses its chip and sorts after every
typed row, so Easter Sunday stops leading Easter Sunday's day page, and the
same for the other thirteen. That is E4's whole visible effect being undone on
fourteen of the forty rows it covered.

I have **not** restored them. The committed export proves what the values were,
so restoring is not guesswork — but whether they *should* be restored is: you
may have cleared them deliberately while the `Span` and `Part Of` properties
went in on Wednesday, and re-typing rows is E4 work, which is blocked on your
assignment rule and is not this run's item. Say the word and the next
engineering run restores all fourteen from the committed export in one pass.

Worth noting there is no detector for this: nothing compares last night's types
to tonight's, and the only record of the old values is the committed
`holidays.json`. If you want one, it is a small addition to the generator's
report.

---

### Carried forward, unanswered

- **★ 2026-10-13 — E4's assignment rule.** Still unanswered, 32 days, and now
  going backwards — see ★ F above. E4's remaining rows stay blocked.
- **★ 2026-10-15/16 — the Listed and Featured tier price.** E6's and E7's
  upstream halves are both waiting on it.
- **★ 2026-10-27 — the home page's one layout shift** (0.00325 at 1280px,
  0.03731 at 390px, only while the deployed build is a day stale). Accepting it
  means rewording E3's "CLS stays 0.0000" to a threshold.
- **★ 2026-10-28 — Cloudflare is not compressing `text/calendar`.**
  `/calendar.ics` costs 1.98 MB per daily refresh where gzip would make it
  177 KB. A zone setting, not a code change — and this run just made that file
  bigger.
- **The `FAQ` property description in Notion still instructs bolding**, which
  `parse_faq()` has not required since 2026-10-10. Six nights flagged. It is a
  one-line edit in the Notion schema whenever you are in there.

---

## Appended by the 2026-11-14 content run (not the engineering run)

Three Tier 5 pages published to Notion as `Content Status = Live`: **World Diabetes
Day**, **National Pickle Day**, **National American Teddy Bear Day** (all Nov 14,
Orders 1/2/3). No source file touched, no row's `Published` checkbox changed, nothing
committed. Reverting any one of them is `Content Status = Draft` on that row.

**★ G — which queue does the nightly content run take, Tier S or Tier 5?**
§6 gained Tier S yesterday and says, in its own words, that it "takes priority over
Tier 5 until it is done" and that "a run does **six** of them, not three." The content
task's standing prompt, written before Tier S existed, says to take **three** holidays
to publication depth and describes only the long-form field set — which Tier S rows
explicitly do not get (`Content Status` left empty; "the deep content comes later").
The two cannot both be followed.

This run followed the prompt and wrote three Tier 5 pages, on the reasoning that
(a) the prompt is the instruction this session actually runs under, (b) seeding six
new published span rows is the less reversible of the two readings, and (c) S-1–S-7
were seeded interactively and published by the engineering run, so Tier S has so far
moved without the content run. **S-8 (Glaucoma Awareness Month), S-9 (National
Mentoring Month) and S-10 (Veganuary) are therefore still unticked, and they are
January spans** — which matters against E8's `/january/` deadline of 2026-12-15.

Answer needed: either update the content task's prompt to say "six Tier S rows until
S-47 is ticked, then three Tier 5 pages", or strike the priority line from Tier S and
let the engineering run keep seeding spans. Until then every content run will face the
same fork and make the same guess.

**★ H — `World Diabetes Day` wants a `Part Of` relation.** It is the cleanest example
in the database of a day inside a span (National Diabetes Month, Tier S S-41, not yet
seeded). Worth setting the moment that row exists; the page is already written in a way
that assumes nothing about it.

**Sourcing notes worth a glance, not decisions.** Four source conflicts were stated
rather than averaged, per §4: the UN's observance page dates resolution 61/225 to 2007
while the resolution itself is dated 20 December 2006 (resolution preferred, as the more
primary source); IDF and WHO describe WHO's role in founding the day differently (the
resolution's "co-sponsorship" preferred); IDF's 589M and WHO's 830M prevalence totals are
printed side by side and left unreconciled; and NPS and the Theodore Roosevelt Center
place the 1902 Roosevelt bear hunt in two different Mississippi towns (both named). Five
pages could not be retrieved at all this run — IDF's blue-circle pages, the Smithsonian
NMAH object record for the Michtom bear, eCFR 21 CFR 114 (robots-disallowed), Britannica,
and the Chronicling America JSON search — and each omission is stated on the page it
affects rather than papered over.
---

# Content run — 2026-11-15 (appended, nothing above overwritten)

Three Tier 5 pages published Live: **America Recycles Day**, **National Bundt
Day**, **I Love to Write Day** (Nov 15, Orders 1/2/3). `Published` untouched on
all three. Full detail is in the §8 Run Log; three things want your eye.

**1. ★ G is still open and it bit again tonight.** §6's Tier S says it takes
priority over Tier 5 and that a run does **six** span rows; this task's standing
prompt says **three long-form holidays**, with a field set Tier S rows do not
get. This run followed the prompt, for the second night running. S-8 Glaucoma
Awareness Month, S-9 National Mentoring Month and S-10 Veganuary are all
January spans and all still unticked, against E8's `/january/` deadline of
**2026-12-15 — 30 days out**. Either update the content task's prompt to do six
span rows while Tier S lasts, or strike the priority line from Tier S. One line
either way; it is the only thing standing between the nightly content run and
the January deadline.

**2. America Recycles Day ships with a founding year the EPA contradicts.** The
fullest published history (U.S. Chamber of Commerce Foundation) dates the first
national observance to **November 15, 1997**; the EPA's own releases call 2015
the 18th and 2017 the 20th, which counts back to **1998**. Both are on the page,
unreconciled, per §4. If you would rather the page picked one, say which.

**3. I Love to Write Day leans on the founder for its numbers.** Riddle's
11,000-school first-year figure, the nine governors' proclamations and the 2008
Congressional Record entry are attributed to him on the page and corroborated by
nothing. The Congressional Record one is checkable if you ever want it settled;
govinfo refuses automated requests from here.

**Revert for any of the three:** set that row's `Content Status` back to `Draft`
in Notion. At the next regeneration the long-form text goes and the short
`Description` page returns.

---

# Content run — 2026-11-16 (appended, nothing above overwritten)

Three Tier 5 pages published Live: **International Day for Tolerance**, **National
Fast Food Day**, **National Button Day** (Nov 16, Orders 1/2/3). `Published`
untouched on all three, `Description` untouched. Full detail is in the §8 Run Log;
four things want your eye.

**1. ★ G is open for a third content run.** §6's Tier S says it takes priority over
Tier 5 and that a run does **six** span rows; this task's standing prompt says
**three long-form holidays**, with a field set Tier S rows explicitly do not get.
This run followed the prompt, as the 11-14 and 11-15 runs did. S-8 Glaucoma
Awareness Month, S-9 National Mentoring Month and S-10 Veganuary are all January
spans and all still unticked, against E8's `/january/` deadline of **2026-12-15 —
29 days out**. One line either way settles it: update this task's prompt to do six
span rows while Tier S lasts, or strike the priority line from Tier S.

**2. The Timeline bold markers never survive the write, on any row.** The Notion
MCP property write turns `**1921**` into a rich-text annotation, and
`export_from_notion.py` reads `plain_text`, so the asterisks are gone before the
exporter ever sees them — 24 characters per Timeline, on all three rows tonight and
on every long-form row written before (verified against `World Kindness Day`).
Nothing breaks: `md_inline()` renders the entries fine and the dates simply show
unbolded. It is recorded here only so nobody later "repairs" a Timeline by typing
the asterisks back, or reads a length mismatch as data loss. If you want bold
Timeline dates, that is a renderer change (wrap the leading date span), not a
content fix.

**3. Two founding bodies, and the page says which did what.** International Day
for Tolerance is the best-sourced Tier 5 origin so far, but the two sources do not
say the same thing: **UNESCO proclaimed** the day in Article 6 of its Declaration
of Principles on Tolerance (Paris, 16 November 1995), and **the General Assembly
invited** member states to observe it in resolution 51/95 the following year. The
page keeps that distinction rather than flattening it into "the UN created it."
What is **missing on purpose**: the adoption date of resolution 51/95, because the
UN Digital Library record returned a client error and documents.un.org refuses
automated requests — and the number of the 1993 resolution that proclaimed the UN
Year for Tolerance, for the same reason. Both omissions are stated in `Sources`.

**4. National Button Day's usual founder does not claim it.** The attribution
everywhere is "founded in 1938 by the National Button Society." The American Sewing
Guild states it in those words with no source; NBS's own home, about-us and history
pages never mention the day at all, and the single NBS use of the name anywhere is a
members' notice reading "Celebrate National Button Day, November 16th" with no
origin. 1938 is the Society's own founding year. The page says all of that plainly.
If you would rather it simply repeated the 1938 claim, say so — but it would be the
first unsourced founding date on the site.

Smaller notes: **White Castle's own history page returned a client error**, so every
White Castle claim on the Fast Food page rests on the Kansas Historical Society's
Kansapedia entry instead of the company. The two NCHS fast-food figures (32.0% for
Aug 2021–Aug 2023, 36.6% for 2013–2016) are printed with their survey periods and
**not reconciled**. Smithsonian Libraries' record for the 1982 Cooper Hewitt button
catalog shows a CC0 notice beside an "In Copyright" metadata field, so the Button
page claims only that it is readable free.

**Revert for any of the three:** set that row's `Content Status` back to `Draft` in
Notion. At the next regeneration the long-form text goes and the short `Description`
page returns.

---

## Content run — 2026-11-17 — Tier 5, T5-49 to T5-51 (appended; nothing above was changed)

**Published Live to Notion:** World Peace Day, National Homemade Bread Day,
National Entrepreneurs' Day — all Nov 17, Orders 1/2/3. `Published` untouched on
all three (re-read as still checked), `Description` untouched, all five long-form
fields written. Nothing outside `docs/` was touched by this run.

**The one thing worth your attention: `national-entrepreneurs-day` is a new §7
fidelity candidate, and a sourceable one.** The row is `Annual` Nov 17. Nov 17 is
the **third Tuesday of November in 2026** and in no other nearby year (2025 Nov 18,
2027 Nov 16, 2028 Nov 21). The third-Tuesday rule is not an aggregator claim here:
it is in the titles and closing whereas clauses of H.Res. 401, S.Res. 582 and
S.Res. 314, and **Proclamation 10850 of 31 October 2024** calls on Americans "to
celebrate November 19, 2024, as National Entrepreneurs' Day" — that year's third
Tuesday. I did not change the recurrence, because recurrence belongs to the
deferred fidelity audit. But the published page now **states** the rule, so from
2027 it will contradict the generated Dates table directly below it. That is the
same trap `national-bison-day` set on 2026-11-07, and `guinness-world-records-day`
is already wrong this year. Three rows now, all found by content runs rather than
by the detector in `docs/FIDELITY_AUDIT.md`, which only screens names containing a
weekday word and would have caught none of them.

**Origin conflict, stated and not resolved (Entrepreneurs' Day).** Two congressional
offices disagree. Sen. Moran's releases (2014, 2015) say the day "was established in
2010 by David Hauser and Siamak Taghaddos, co-founders of Grasshopper" with Amir
Tehrani of The Legacy Foundation, who petitioned President Obama. Rep. Peters'
release (19 Nov 2013) says he launched it through H.Res. 401, prompted by the death
of San Diego innovator Duane Roth, and names neither 2010 nor those people. Neither
office is more primary than the other for the other's claim, so the page prints both.
Worth knowing: **Proclamation 8747 of 1 November 2011 — the document Moran's office
links for the Obama petition — designates November as National Entrepreneurship
Month and never uses the phrase "National Entrepreneurs' Day."** The page says that
too. The page also says the thing that is easy to get wrong: Congress never
designated this day. All three resolutions were titled "expressing support for
designation," and only S.Res. 314 was ever agreed to, in the Senate alone, on
19 November 2015.

**Sections cut for want of a source.** None of the three lost a required section, but
two claims were dropped rather than sourced loosely: the Chillicothe, Missouri 1928
first-sale story on the bread page (named on the page as uncited), and a line on the
2020 home-baking surge, for which the only candidates were trade press and content
farms. On World Peace Day, neither UN resolution's adoption date is stated, because
the UN's own pages give only the years.

**A source conflict resolved.** The UN's current observances page and its 2012
background page differ: only the older one says resolution 55/282 fixed 21 September.
Preferred the older, more specific page and said so here rather than averaging them.

**Least confident claim across the three:** that no acceptable source anywhere
documents a November 17 World Peace Day. The search was wide and turned up only
aggregators and florist blogs, but a printed calendar of record (Chase's) was not
reachable from this session. If you know of one, that page is the one to revisit.

**Could not verify:** whether a 2025 or 2026 proclamation also names National
Entrepreneurs' Day. federalregister.gov is robots-disallowed to this session and no
govinfo copy surfaced, so the page cites the 2024 proclamation without claiming it is
the most recent.

**Operational note for whoever runs next.** The session reminder listed the repo as a
connected folder, but `connectedFolders` came back empty and nothing existed under
`$HOME/mnt`. One `device_request_folder_access` call for the repo root was granted and
the run proceeded normally. If a future run finds the mount missing, that is the fix.

**★ G, still open — fourth content run under it.** §6 says Tier S "takes priority
over Tier 5 until it is done" and that a run does six span rows, not three. This
task's standing prompt says three holidays taken to publication depth, with
`Opening`/`Body`/`Timeline`/`FAQ`/`Sources` and `Content Status = Live` — fields §6
explicitly tells Tier S rows to leave empty ("the deep content comes later, through
Tier 5 rules"). The two readings cannot both be followed, so this run followed the
prompt, as the 11-14, 11-15 and 11-16 runs did. **S-8 through S-10 are January spans
and are still unticked, against E8's `/january/` deadline of 2026-12-15 — 28 days
out.** Either the prompt or §6 needs to change; a content run should not keep
deciding this on its own.

**Revert for any of the three:** set that row's `Content Status` back to `Draft` in
Notion. At the next regeneration the long-form text goes and the short `Description`
page returns.
