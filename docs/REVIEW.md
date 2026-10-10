# Review — run of 2026-10-10 (overnight engineering)

**Item: E2 — coverage gaps. Partly landed.** 11 of the 16 missing observances
are in Notion and published, both fidelity bugs are fixed, five things need a
decision from you. E2 stays open in §5 with a STATUS block listing the
remainder, so the next run won't restart it.

The repo diff is small. **Most of tonight's work is in Notion, which isn't in
your diff** — see below.

## Files touched

```
 M scripts/export_from_notion.py  +55     eight new FLOATING_RULES entries, each sourced in a comment
 M scripts/generate.py            +34/-3  new nth_weekday_offset rule kind; two next_occurrence fixes
 M scripts/README.md              +43     documents all of the above
?? docs/FIDELITY_AUDIT.md                 new: the audit's worklist (this file gets overwritten nightly)
 M docs/REVIEW.md, docs/EXECUTION_PLAN.md
```

No generated file touched. `scripts/holidays.json`, `public/**` and
`sitemap.xml` are untouched — the generator only ran into throwaway directories
outside the repo.

## Notion: 11 rows created, 2 fixed, 1 held back

Created with `Published` ticked and `Content Status` empty, so each ships its
one-paragraph `Description` and nothing more (long-form drafting is §6's job):

| Row | Recurrence | Next | Date source |
|---|---|---|---|
| Kwanzaa | Annual Dec 26 | 2026-12-26 | Maulana Karenga's own site (founder) |
| Rosh Hashanah | Floating, table to 2036 | 2027-10-02 | Hebcal |
| Yom Kippur | Floating, Rosh Hashanah + 9 | 2027-10-11 | Hebcal |
| Day of the Dead | Annual Nov 2 | 2026-11-02 | Smithsonian NMAH; UNESCO |
| National Pizza Day | Annual Feb 9 | 2027-02-09 | TODAY (NBC) |
| National Margarita Day | Annual Feb 22 | 2027-02-22 | TODAY (NBC) |
| National Hugging Day | Annual Jan 21 | 2027-01-21 | nationalhuggingday.com (founder) |
| National Teacher Appreciation Day | Floating, Tue of 1st full week of May | 2027-05-04 | NEA's 1985 rule, checked against NEA's published 2026 dates |
| National Teacher Appreciation Week | Floating, Mon of that week | 2027-05-03 | same |
| Oktoberfest (starts in Germany) | Floating, 15 days before 1st Sun in Oct | 2027-09-18 | Munich city regulation 130 §2, checked against the city's 2026/2027 dates |
| Super Bowl Sunday | Floating, 2027 only | 2027-02-14 | NBC Los Angeles |

Fixed — E2's named bug plus one more of the same class:

- **National Doughnut Day**: Annual June 4 → **first Friday in June**. The
  Salvation Army created it in 1938 and states the rule itself.
- **National Ice Cream Day**: Annual July 18 → **third Sunday in July**, per
  Reagan's Proclamation 5219 (1984), via GPO.

Both keep their current next occurrence — 2027-06-04 *is* the first Friday and
2027-07-18 *is* the third Sunday, which is exactly how the bug hid — so no date
on the site changes now; the fix is about 2028 onward. Their `Description`s did
change, since both asserted the wrong fixed date in prose.

Date citations went in **`Source`** (text), not `Sources`, matching what the
code assumes. Last night's decision 1 is still open and `Source` was empty on
every row until tonight, so it's cheap to move.

## What to check

1. `git diff scripts/` — 131 added lines across three files. The only behavior
   changes are in `generate.py`; the exporter diff is new dict entries.
2. The eleven new pages after the Action regenerates: `/holiday/kwanzaa/`,
   `/rosh-hashanah/`, `/yom-kippur/`, `/day-of-the-dead/`,
   `/national-pizza-day/`, `/national-margarita-day/`, `/national-hugging-day/`,
   `/national-teacher-appreciation-day/`,
   `/national-teacher-appreciation-week/`, `/oktoberfest-starts-in-germany/`,
   `/super-bowl-sunday/`.
3. **Expect ~129 existing pages to change, not 11.** Adding an observance to a
   date rewrites the "also on this date" list on every other page for that date
   (Boxing Day, All Souls' Day, Valentine's Day…): 60 holiday pages, plus 5 new
   and 64 changed `/day/` pages. That's the whole shape of it.
4. **The new rows sit low on their days** — Kwanzaa is 5th on Dec 26, Day of
   the Dead 8th on Nov 2. I gave each the next free `Order` instead of
   reordering existing days, because per-day ranking is **E4's** job and that's
   literally the problem E4 describes. One `Order` field per row if you want
   them featured sooner. Floating rows got `Order 1`, since their neighbors
   change every year.

## One timing thing

The daily Action exports from **Notion**, not from your working tree, so
tomorrow's 08:00 UTC run picks up all eleven rows and both fixes **whether or
not this diff is committed**. Without the diff the exporter has no rules for
the five new Floating rows or for Doughnut Day and Ice Cream Day, and skips all
seven with warnings — and those last two have live pages today, so they'd drop
out of the calendar and sitemap (their HTML stays, so the URLs keep working)
until the diff lands. Committing before 08:00 UTC avoids it. If you'd rather
wait, set those two rows back to `Annual` in Notion and nothing degrades.

## How I verified it

- **Regression:** pre-patch generator (`git show HEAD:scripts/generate.py`) vs
  patched, both over the current `holidays.json` into seeded copies of
  `public/`. `diff -r` → **byte-identical across the whole site**; both exit 0,
  zero warnings. Every change is inert for the rows that exist today.
- **Forward:** built the `holidays.json` the exporter will now produce and
  generated into a third throwaway directory. Exit 0, **zero WARNING lines**,
  11 pages created / 60 changed, 5 `/day/` created / 64 changed, sitemap 2,818
  URLs, search index 2,450. A second run changed nothing — still idempotent.
- **Each computed date checked against its source**, not just against itself:
  Teacher Day 2026-05-05 and week 2026-05-04 match NEA's published May 4–8;
  Oktoberfest 2026-09-19 and 2027-09-18 match Munich's published dates; Yom
  Kippur = Rosh Hashanah + 9 in all eleven table years; Doughnut Day and Ice
  Cream Day land on the right weekday. Both JSON-LD blocks parse.

### Two engine bugs fixed on the way

1. **Annual `next_occurrence()` scanned two years.** Fine for a date that
   exists every year — but Feb 29 doesn't, so Leap Day raised in three years
   out of four, was caught as "unresolved", and **no page would ever have been
   built for it**. Now nine years (widest real leap gap is eight, across a
   non-leap century year).
2. **A `lookup_table` whose first confirmed year is *next* year resolved to
   nothing.** The Floating branch raised on this year and never tried next, so
   Super Bowl Sunday (2027 only, added in Oct 2026) was reported as having no
   date at all. Unresolvable years are now skipped; if none resolves the error
   is re-raised, so an **expired** table still fails as loudly as before.

## Needs a decision

**1. Leap Day is in Notion with `Published` unticked, on purpose.** The dated
archive's forward horizon is derived, not configured —
`day_end = max(occurrences.values())` — so publishing a row whose next
occurrence is 2028-02-29 moves the horizon from Oct 2027 to Feb 2028 and
creates **~142 new `/day/` pages in one run** (measured). They're real pages,
but how far forward the archive publishes is the same kind of content and crawl
decision the README already guards for `DAY_ARCHIVE_START`. Either tick
`Published`, or clamp `day_end` first (one line:
`min(max(occurrences.values()), today + timedelta(days=400))`) and then tick
it. The row is complete and sourced either way.

**2. `Oktoberfest (ends in Germany)` is wrong from 2027.** Stored Annual Oct 4;
Munich's regulation ends the festival on the **first Sunday in October,
extended to Oct 3** when that Sunday is Oct 1 or 2 — so 2027 ends Oct 3. The
conditional extension fits no existing rule kind: either a new kind (~6 lines)
or a short lookup table of the city's published dates. The start row I added is
unaffected; its rule is unconditional.

**3. Tax Day: not created.** Three tangled questions. `Income Tax Pay Day`
(Annual Apr 15) already covers the ground — second row or rename? The real date
is the IRS deadline, which shifts for weekends and DC's Emancipation Day (2028
is Apr 18), so "Annual April 15" is wrong about one year in three. And modeling
it properly needs either DC-holiday logic in a new rule kind or a table holding
only the years the IRS has announced.

**4. National French Fry Day: not created, the date is contested.** July 13 is
traditional, but National Day Calendar moved it to the second Friday of July in
2022 at a restaurant chain's request and the big chains have since split across
both (Axios covered the mess). Under §4 I can't assert either date on an
aggregator's say-so. My suggestion: take July 13 and make the disputed date
part of the page — it's better content than the date itself.

**5. Winter Solstice / Summer Solstice / Vernal Equinox are already on the
site under other names.** `First Day of Winter` + `Yule` (Dec 21),
`The First Day of Summer` (Jun 21) and `The First Day of Spring` + `Ostara`
(Mar 20) all exist with correct tables through 2036. Adding "Winter Solstice"
would put a third near-identical entry on Dec 21. The real question is whether
the solstice wording earns its own page for the search term (alias rows, which
E3's canonical work would need to know about) or belongs in the existing
titles. A naming decision, not a gap.

## The audit, and where it went

E2 also asks for an audit of the other food and awareness days. The signature
is findable: the dataset was bootstrapped from one year's dates, so a
weekday-ruled row's stored date lands on its own named weekday in exactly one
year and drifts off the next. **24 candidates** came out — six days of Be Kind
to Humankind Week, Free Comic Book Day, National Public Lands Day, National
Hunting and Fishing Day, Frankenstein Friday, Fat Thursday and more.

I fixed only the two I could tie to a primary document tonight and wrote the
rest up in **`docs/FIDELITY_AUDIT.md`** with each row's stored date, its
weekday drift and the likely rule — so the audit you deferred to year-end has a
worklist. Candidates, not verdicts: some may be legitimately fixed-date. §7
points at the file.

---

# Appendix — content run of 2026-10-10 (appended, not overwritten)

This section was **appended** by the Mon/Wed/Fri content run. The engineering
review above, including its five unanswered decisions, is left intact on
purpose: overwriting it per hard rule 6 would have destroyed questions you have
not answered yet. Rule 6 probably wants narrowing to "the engineering run
overwrites this file; content runs append."

## Drafted, awaiting your review

Christmas Day, Valentine's Day, New Year's Day — queue items 3–5 of §6, taken
top-first. Each has `Opening`, `Body`, `Timeline`, `FAQ`, `Sources` populated and
`Content Status = Draft`. `Published` and `Description` were not touched on any
row. Nothing reaches the site until you move a row to Reviewed or Live.

## Needs a decision — the FAQ fields on Halloween and Thanksgiving Day do not render

Not caused by this run. `parse_faq()` in `generate.py` recognizes a question
only when the whole line is wrapped in `**bold**`:

```python
bold_only = re.fullmatch(r"\*\*(.+)\*\*", line)
```

The FAQ fields on both finished rows use plain-text questions
(`Is Halloween always October 31?`), so both parse to **zero pairs**. The
consequence is that both pages ship with no FAQ section and no FAQPage
structured data — the one competitive feature E1 was built to add. Verified:

```
parse_faq("Is Halloween always October 31?\nYes. The date is fixed.")  -> []
parse_faq("**Is Halloween always October 31?**\nYes. The date is fixed.") -> [(...)]
```

Both rows are at Content Status **Live**, so this is live-site behavior.

Separately, **both rows have an empty `Opening`**, so both keep the templated
`Description` ("Halloween, observed on October 31, celebrates…") on the site
rather than the drafted opening — the exact boilerplate §4 exists to replace.

Two ways to fix it, your call:

1. **Edit the two Notion rows** — wrap each FAQ question in `**…**`, and fill
   `Opening` from the drafted opening paragraphs. No code change; nothing else
   is affected. The exemplar already shows the bolded form, so the spec is right
   and the two rows drifted from it.
2. **Loosen `parse_faq`** — also treat an unbolded line that ends in `?` and is
   followed by a non-question line as a question. More forgiving for future
   runs, but it is a parser change on a rule that currently fails loudly-ish
   (silently, in fact) rather than wrongly, and it would need its own
   byte-identity check.

Today's three drafts use the bolded form and were verified to parse into five
pairs each with FAQPage JSON-LD emitted, so they are unaffected either way.

## How I verified this run

- 23 assertions, all passing: `extract_holiday()` drops `body` / `timeline` /
  `faq` / `sources` and ignores `Opening` at `Draft`, and carries all five at
  `Live`; `render_longform()` on exactly today's field shapes produces the FAQ
  section, the timeline ahead of "How to observe", bolded years as `<strong>`,
  bare source URLs as links, italic titles as `<em>`; `faq_ld_json()` emits
  `"@type": "FAQPage"` with the answer text.
- Generator run into a throwaway directory (never `public/`): exit 0, zero
  WARNINGs, 2,803 pages.
- The three drafted pages render in that throwaway build with **no** long-form
  block and **no** FAQPage — the review gate confirmed end to end on real data.

## Sourcing notes worth a spot-check

- **Christmas tree, source conflict resolved.** The usual "Prince Albert
  introduced the Christmas tree to Britain" line is contradicted by the Royal
  Collection Trust, which credits Queen Charlotte in the late eighteenth century
  with a yew. The draft follows RCT as the more primary source — the royal
  household's own collection — and says Albert popularized rather than
  introduced it, per §4's instruction to prefer the more primary source and say
  so rather than average the two.
- **1659 Massachusetts ban, repeal omitted.** mass.gov gives the statute, the
  heading "Penalty for Keeping Christmas" and the five-shilling fine, but not a
  repeal date. The draft states only what is sourced; the commonly cited 1681
  repeal is left out.
- **New Year's resolutions, no origin claimed.** The Babylonian/Roman vow story
  could not be traced to a primary source, so the FAQ says that outright instead
  of repeating it. This is the §4 "not well documented" sentence, used
  deliberately.
- **NRF $29.1bn (2026).** A retail trade association's survey of stated spending
  intent, not a government measurement. Cited as the originating organization for
  its own survey and labeled as such in the draft body rather than presented as
  a statistic. Flagging it because it is the only non-government, non-archival
  source across the three pages.
- No aggregator was consulted or cited on any of the three.
