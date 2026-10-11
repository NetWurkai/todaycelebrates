# Review — run of 2026-10-11 (overnight engineering)

**Item: E3 — perennial day pages. The perennial pages are done; the
`/holidays/<year>/` index pages are not.** E2's five open decisions were still
unanswered, and none of them is work an unattended run should start, so this
run went to the next unblocked item. They are restated at the bottom of this
file — the full versions are in §5 of the plan and in git history
(`git show HEAD:docs/REVIEW.md`).

The site now has a year-less page for every calendar date: `/october-8/`,
366 of them, February 29 included. That is the URL three of the four leading
competitors rank with and we had nothing at.

## Files touched

```
 M scripts/generate.py            +~310  perennial index, renderer, generation, sitemap, report
?? scripts/templates/perennial.html       new: the page template (same components as day.html)
 M scripts/templates/day.html     +1     one marker, for the dated -> perennial link
 M public/_headers                +39    cache rules, one per month
 M scripts/README.md              +64    URL model row + a section on how this works
 M docs/REVIEW.md, docs/EXECUTION_PLAN.md
```

No generated file touched. `public/**` (other than `_headers`), `sitemap.xml`
and `scripts/holidays.json` are untouched — the generator only ran into
throwaway directories outside the repo.

## What the new page says, and why that split matters

Each date's observances are split in two, and this is the whole design:

- **Fixed-date rows are the page's content** — the numbered table, the count in
  the title, the `ItemList` structured data. They are on that date every year,
  which is exactly what a year-less URL should claim.
- **Rule-dated rows are a note, not a list entry.** Memorial Day is not a
  May 26 observance; it is one that falls on May 26 in 2031. So the note names
  the years ("Columbus Day — 2027 and 2032") and those rows stay out of the
  table and out of the count.

The year-specific angle — the weekday, and where a moveable observance goes
*next* year — stays on `/day/YYYY-MM-DD/`. That is the only thing keeping the
two page types from reading as near-duplicates, which is the risk this item
carries. Both pages are self-canonical and both stay in the sitemap, per E3.

Three states, all three real on the current data:

| | Example | What it shows |
|---|---|---|
| Has fixed-date observances (340 dates) | `/october-11/` | 9 in the table, 3 more named with their years |
| Rule-dated only (18 dates) | `/february-29/`, `/may-26/` | no table; "Nothing falls on this date every year", then the note |
| Nothing at all (8 dates) | `/january-3/` | no table, no structured data, an honest empty state |

## What to check

1. **`git diff scripts/generate.py`** — the new code is four functions plus a
   generation block; the only change to existing behavior is one added
   paragraph in `render_day_page()`'s note block.
2. **The empty-state decision is one line.** `PERENNIAL_EMPTY_PAGES = True` in
   `generate.py` publishes all 366 so no date in the year 404s. `False`
   publishes 358 and the prev/next ring skips the rest — verified working
   either way. See *Needs a decision* below.
3. **Expect a large one-time regeneration**, bigger than the page count
   suggests: 366 new pages, **and all 348 dated pages change**, because the
   cross-link back to the perennial page is in their shared note block. Those
   348 then get today's `lastmod` in the sitemap, so the next Action commit
   restamps them. That is true (their content did change), it happens once, and
   it is the price of the cross-link E3 asks for. Holiday pages are untouched.
4. **`/about/`** has a reworded sentence ("every date of the year has a page of
   its own" rather than "of the coming year"), since the old wording described
   only the dated archive.
5. **CLS** — not measured in a browser; nothing was deployed. The structural
   argument is that `perennial.html` uses the same components as `day.html`
   (pagehead, obs table, note, tool, pn, wk rail), the same three ad slots in
   the same order, and **no new CSS at all** — it is worth confirming on the
   live page after you push, since E3's acceptance criteria name it.

## How I verified it

- **Regression, pre-patch vs patched**, both over the current `holidays.json`
  into seeded copies of `public/` outside the repo: the *only* differences are
  366 new directories, the one added paragraph on 348 dated pages, the `/about/`
  sentence, and 366 added sitemap URLs. Every holiday page, every data file and
  the homepage come out **byte-identical**. Both runs exit 0 with zero WARNINGs.
- **The patched run:** exit 0, **zero WARNING lines**, 366 perennial pages
  created, 348 dated pages written, sitemap 3,170 URLs (2,804 + 366). A second
  run changed nothing — still idempotent, dated pages included.
- **All 366 pages parsed:** zero unbalanced tags, zero unfilled template
  markers, zero leaked maintainer comments, and all 340 `ItemList` blocks are
  valid JSON with `numberOfItems` matching the list length.
- **14,314 internal links** across the new pages resolve to a file that exists;
  **no perennial page has zero inbound links** (minimum 10); every canonical on
  both page types points at itself.
- **40 assertions**, including: the annual/floating split never misfiles a row;
  Memorial Day appears on no date before May 25 and in no every-year list;
  February 29 resolves to 2028 for the calendar button and sits between
  February 28 and March 1 in the ring; the ring wraps at the year boundary;
  the `PERENNIAL_EMPTY_PAGES = False` branch publishes 358, writes no page for
  January 3, keeps it out of the sitemap, and leaves the dated cross-links
  pointing at pages that exist.

## Needs a decision

**1. Eight pages with nothing on them.** Jan 3, Jan 6, Jan 12, May 2, Jun 3,
Jun 11, Jul 10 and Aug 31 have no observance at all, in any year, in the
current dataset. E3 says "366 perennial pages exist", so I published all 366
with an honest empty state rather than silently leaving eight dates to 404 —
but eight thin pages on a site whose whole argument is trustworthiness is your
call, not mine. `PERENNIAL_EMPTY_PAGES = False` is the switch, and it is tested.
Worth knowing: some of these dates stop being empty as content lands — Jan 21
was on this list until Hugging Day was created on 10-10.

**2. Where the perennial page belongs in the navigation.** Right now it is
reachable from its dated pages, from its neighbours, and from the sitemap —
not from the header, the footer, or the home calendar. The `/holidays/<year>/`
index pages E3 also asks for are the natural hub for it, which is why I stopped
before them (below). If you want these pages in the nav before that, say where.

**3. Should holiday pages link to the perennial page too?** A holiday page's
breadcrumb and back-link currently point at the dated page. Pointing them at
`/october-8/` instead (or adding a second link) would be the stronger internal
signal, but it rewrites all 2,439 holiday pages, and which of the two a holiday
page should favour is a judgment about what you want ranking. Left alone.

**4. Still open from 2026-10-10, unanswered, restated so overwriting this file
loses nothing** — full text in §5 of the plan under E2:
Leap Day sits unpublished (publishing it adds ≈142 dated pages); `Oktoberfest
(ends in Germany)` is wrong from 2027 and needs a new rule kind or a lookup
table; Tax Day overlaps `Income Tax Pay Day` and its real date shifts for
weekends and DC Emancipation Day; National French Fry Day's date is contested
(July 13 vs the second Friday, moved by an aggregator at a chain's request);
and the solstices/equinox already exist under other names, so that is a naming
call, not a gap.

## What is left of E3

Not started, and the next engineering run should pick it up here:

- **`/holidays/<year>/` index pages** — E3's fourth bullet. A year index is a
  different page type again (it lists months and the dated pages under them),
  and it is the obvious home for a link to all 366 perennial pages, so it is
  worth doing as its own reviewable change rather than bolted onto this one.
- Decisions 2 and 3 above feed into it.

Everything else in E3 is done: the 366 pages exist, canonicals are correct in
both directions, nothing is orphaned, and the sitemap is consistent.

---

# Addendum 2026-10-11 — Born on this day (interactive session, not an overnight run)

Requested by Jay: birthdays of historic and celebrity figures, as **two separate
sub-blocks per date**. Built, verified, **not committed or pushed**.

## What changed

- `scripts/build_people.py` (new), `scripts/people.json` (new, ~1 MB, 366 dates,
  8,779 people), `scripts/people_overrides.json` (new), `scripts/templates/perennial.html`
  and `day.html` (one marker each), `scripts/generate.py` (loader + block renderer +
  `--people`), `public/styles/site.css` (+13 lines), `.gitignore` (+ `scripts/.people_cache/`),
  `scripts/README.md` (new section "Born on this day").
- Perennial pages show 10 per list, dated pages 4. Every date has 12 historic;
  living averages 12.0 (minimum 9).

## How it was verified

- Generated into throwaway copies of `public/`, with and without `people.json`; exit 0.
- Exactly 714 files differ: the 366 perennial and 348 dated pages. Every holiday page,
  data file, the homepage and `sitemap.xml` are byte-identical.
- On those 714 pages, deleting the new `<section class="born">` gives back the baseline
  page byte for byte. JSON-LD unchanged, no `Person`/`Event` entities added.
- Rendered `/october-10/` and `/day/2026-10-10/` at 1280px and 390px: columns side by
  side on desktop, stacked on phone, no horizontal scroll.
- Not measured: CLS and page weight on a real deploy (+1.9–4.6 KB per page).

## Needs a decision

1. **Borderline figures left in** (the automatic filters cannot judge them). Add to
   `people_overrides.json` -> `exclude` if you want them gone: Mao Zedong, Kim Il Sung,
   Kim Jong Il, Francisco Franco, Salazar, Hafez al-Assad, Robert Mugabe, Erich Honecker,
   Suharto, Saparmurat Niyazov, Islam Karimov, Ivan the Terrible, Leopold II, Mobutu,
   Enver Hoxha, Ben Ali, Jaruzelski, Batista, Mohammad Reza Pahlavi. Already excluded
   (11): Himmler, Goebbels, Eva Braun, Stalin, Mussolini, bin Laden, al-Baghdadi,
   al-Zawahiri, Nasrallah, Soleimani, Milošević.
2. **The conviction filter is blunt.** It drops anyone with a Wikidata conviction,
   including fraud and tax cases (Steinbrenner, Milken, Ja Rule). Set
   `EXCLUDE_CONVICTED = False` to keep them, and rely on the overrides instead.
3. **"Historic figures" includes people who died recently** (Dolly Parton, Charlie Kirk,
   Diane Keaton). Rename the sub-block ("Remembered", "Notable people, died") or split
   by a cutoff year? One string in `people_block_html`.
4. **Dated archive pages now change when people data is refreshed.** The plan says
   `/day/YYYY-MM-DD/` should regenerate byte-identically. With a fixed `people.json` it
   does, but a monthly refresh will alter old archive pages. Options: keep it (the block
   is small), or drop people from dated pages and show them only on `/<month>-<day>/`
   (set `PEOPLE_DAY_LIMIT` handling to render nothing; one line).
5. **Source policy.** Wikipedia and Wikidata are not on the plan's list of acceptable
   sources. They are the only practical source for this data; please confirm, because
   the rule exists for a reason.

## Known limits

- Stale-prone descriptors cannot be fully detected (e.g. an office held "until" a date
  that has since passed). Living-person descriptors are trimmed to the lead clause to
  reduce this. A handful of descriptors have punctuation glitches inherited from
  Wikipedia's wording ("... poet Nobel Prize laureate": 11 found, 16 have no
  descriptor and render name and years only).
- The homepage does not show people.
- Refresh is manual (monthly): workflow files are protected. `generate.py` warns when
  `people.json` is more than 45 days old.
- Nothing is committed, so the tree is dirty and **Rule 2 still blocks the overnight
  engineering runs until you commit** (E3's work is in the same tree).
