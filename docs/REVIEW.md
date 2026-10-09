# Review — run of 2026-10-09 (overnight engineering)

**Item: E1 — long-form content rendering. Landed, complete, uncommitted.**
The renderer, the exporter passthrough, the five Notion properties and the
five-year dates table all exist. Nothing is published: no row has long-form
content yet, so every one of the 2,439 live pages still renders byte-for-byte
what it rendered before tonight. Verified by diffing the old generator's
output against the new one — see below.

## Files touched

```
 M scripts/generate.py            +339 / -6   renderer, dates table, FAQPage JSON-LD
 M scripts/export_from_notion.py   +36       carry the five new fields through
 M scripts/README.md               +85       document the fields and the Markdown subset
 M public/styles/holiday.css       +30       styles for the new sections
?? docs/                                     this file + the Run Log line
```

No generated file was touched. `scripts/holidays.json`, `public/index.html`,
`public/holiday/**`, `public/day/**`, `public/data/**` and `public/sitemap.xml`
are all untouched — the generator only ever ran into throwaway directories
outside the repo.

## Notion (changed — this is the part not in your diff)

Five properties added to **Today Celebrates — Holidays**, each with a
description written into the property so the field explains itself in the UI:

| Property | Type |
|---|---|
| `Body` | rich text |
| `Timeline` | rich text |
| `FAQ` | rich text |
| `Sources` | rich text |
| `Content Status` | select — Draft / Reviewed / Live |

Additive only. No existing property was renamed, retyped or dropped, and **no
row was edited** — every one of them is still blank. The pre-existing `Source`
(text) property was left exactly as it was: see *Needs a decision* below.

## What changed, and why it's shaped this way

**A page has two shapes now.** Without long-form content it is the short page
it has always been. With it, the page renders History, Timeline, How to
observe, FAQ, a five-year dates table and Sources, in the order §4 specifies —
the Timeline is slotted in ahead of the `How to observe` heading inside `Body`,
as `docs/CONTENT_EXEMPLAR.md` shows it.

**Byte-identical degradation was the hard requirement**, not a nicety. It is
what makes it safe to land a renderer before any content exists, and what stops
the daily Action from producing a 2,439-page diff. Every branch returns `""`
when its field is absent, and both template slots collapse to nothing.

**The Notion fields hold a tiny Markdown subset** — `###` heading, blank-line
paragraphs, `- ` bullets, `**bold**`, `*italic*`, `[text](url)` — and nothing
else. Everything is HTML-escaped *before* those six patterns are applied, so a
`<script>` tag typed into a Notion field ships as visible text, not as live
HTML. Content arrives from Notion rather than from the repo, so the renderer
treats it as data.

**FAQPage goes in a second `<script type="application/ld+json">` block**,
beside the existing Event block rather than merged into it. That is precisely
what lets a page without an FAQ keep its exact previous head markup.

**The dates table never guesses.** It reads the same rule engine the rest of
the site uses, and when a rule runs out of resolvable years — a `lookup_table`
past its last hand-confirmed year — it renders a shorter table rather than
raising or extrapolating. A fixed Feb 29 correctly skips the years it doesn't
land in.

**`Content Status` does not gate publishing.** `Published` is still the only
thing that puts a page live, which is how §4 reads it ("`Published` left OFF").
There is a test for exactly this: a row with `Content Status = Live` and
`Published` unchecked is still skipped by the exporter.

### One bug fixed on the way through

`next_friday_the_13th()` scanned forward **400 days**. The longest real gap
between two Friday the 13ths is **427** — and the next instance of it is
2027-08-13 → 2028-10-13. So every daily regeneration between 2027-08-14 and
2028-10-13 would have failed to resolve `friday-the-13th` and dropped it out of
the calendar with a WARNING for fourteen months. `friday-the-13th` is a real
published row, so this was live, just not yet due.

The new code calls that function, which is how it surfaced; the bound is now
460. This is the one change tonight that is not strictly E1 — it is two lines
and a comment in `generate.py`, easy to revert if you'd rather schedule it
separately.

## What you should check

1. **`scripts/generate.py`** is the diff that matters. Most of it is one new
   block of functions (`md_inline` … `faq_ld_json`) plus six small edits:
   two template slots, a widened `render_page` signature, one call inside it,
   two extra `.format()` arguments, and the call site in `generate()`.
2. **The Friday-the-13th bound**, above — the only pre-existing behaviour this
   run changed.
3. **In Notion**, that the five new property names and the three Content Status
   options read the way you want them to *before* 50 drafts exist behind them.
   Renaming now is free.
4. **The two decisions below.** Neither blocks content work, but the first gets
   expensive to unwind later.

One thing that will look alarming and isn't: a regeneration against the
committed `public/` reports all 2,439 pages changed and all 346 day pages
created. That is pre-existing drift — the ads / day-link template work was
committed without regenerating the pages behind it — and it is identical with
or without tonight's diff. The next daily Action run will produce that
2,439-page commit either way.

## How it was verified

**Regression — byte-identity, the one that matters.** Ran the *pre-patch*
generator and the *patched* generator over the real `scripts/holidays.json`
into two separate throwaway copies of `public/` outside the repo, twice each,
then `diff -r` between them:

```
IDENTICAL: patched generator output matches the pre-patch generator byte for byte
```

**Rule 7 — generator into a throwaway directory, never `public/`:**

- Exit code **0** on both consecutive runs.
- **Zero WARNING / ERROR / traceback lines** — stderr empty, both runs.
- Second run: `pages_unchanged_count: 2439`, `pages_changed: []`,
  `day_pages_unchanged_count: 346`, `sitemap_changed: false`, `home_changed:
  false`, `month_diffs: {}` — i.e. **idempotent**, which is what keeps the
  08:00 UTC Action from producing noise commits.
- `unresolved_holidays: []`, `pages_skipped: []`.
- One informational item, unchanged from yesterday: `stale_month_files:
  ["2026-09"]`. A leftover month data file. Not an error.

**Populated-row render.** Injected the Halloween exemplar's four fields into a
*scratch copy* of `holidays.json` (the repo's copy was never written) and
regenerated: exactly **one** page changed — `halloween` — and 2,438 stayed
unchanged. The page renders History → Timeline → How to observe → FAQ → dates
table → Sources, both JSON-LD blocks are present, and the long-form block
parses as well-formed XML (85 elements).

**24 unit assertions, all passing.** Dates table for Annual, Floating
`nth_weekday`, Feb 29, `next_friday_13` and an exhausted `lookup_table`; the
Markdown subset including the escaping of `<script>` and `&`; FAQ parsing
including a dangling question; FAQPage JSON-LD shape; and the degradation paths.

**8 exporter assertions, all passing.** A row with the properties *absent*
produces exactly the eight keys it produced before E1; a row with them present
but *empty* produces an identical dict; a populated row carries all five; and
`Content Status = Live` does not publish an unpublished row.

Environment note, carried forward: this Mac runs Python 3.10.12 while the
GitHub Action pins 3.11. Nothing here is version-sensitive, but local
verification is not the production interpreter.

## Needs a decision

**1. `Sources` vs the existing `Source`.** Carried over from last night,
unanswered. `Sources` (rich text) now exists and the exporter reads it;
`Source` (text) still exists, is still unread, and was not touched. So nothing
is broken — but two near-identical names in one schema is how citations end up
split across both fields. Options: keep `Source` for the *date* citation and
`Sources` for body citations (what the code assumes today); fold `Source` into
`Sources` and drop it; or rename `Source` to something unmistakable like
`Date source`. Worth five minutes before drafts accumulate; genuinely
expensive after.

**2. `Content Status` vs `Published`.** I implemented `Content Status` as
editorial metadata only, with `Published` as the sole publish gate, because
that is how §4 reads. If you actually want the exporter to refuse rows that
aren't `Reviewed`/`Live`, that is a different design and a one-line change —
but it is a change to the publish gate, which isn't a thing to assume.

**3. Timeline placement — implemented, flag only, no action needed.** The
Timeline renders *before* the `How to observe` section, per §4's section order
and the exemplar. If you'd rather it sat after the whole `Body`, that's one
condition in `render_longform()`.

**4. Long-form pages keep their existing `<title>` and meta description.**
I didn't touch either, since §4 doesn't ask for it. A 700-word page arguably
wants a different meta description than a 24-word one — that's an SEO decision
for the re-plan, not for an unattended run.

---

*Next up in §5 is E2 (coverage gaps). §6's content queue is now unblocked:
E1 has landed, so the Halloween exemplar can be loaded into Notion as the
first content action.*
