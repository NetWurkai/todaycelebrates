# Review — 2026-10-11, second pass (interactive: Jay's three answers)

Jay answered the three questions the overnight E3 run left open. All three are
now implemented, and the answers are recorded in the plan (§5 E3) and in
`scripts/README.md` so no future run re-asks them.

| His answer | What was done |
|---|---|
| Keep the empty-date pages — celebrity/historic-figure dates are coming | `PERENNIAL_EMPTY_PAGES` stays True, with the reasoning written into the constant. The count has **already fallen from 8 to 6** (May 2 and June 3 picked up observances), which is the argument in miniature. |
| Perennial pages in the nav: recommend and add per best practice | New hub at **`/dates/`**, and the header's **Calendar** tab plus the footer link now point at it instead of `/#calendar`. |
| Should holiday pages link to them too — yes | Holiday breadcrumb and back-link now point at the perennial page; the dated page keeps its links from the Date row and the sidebar. |

## The navigation recommendation, and why

**Repoint the existing Calendar tab at a real hub page rather than add a fifth
nav item.** `/dates/` lists all 366 dates grouped by month, each with its
fixed-date count.

1. A sitewide nav link aimed at a homepage fragment (`/#calendar`) is spent on
   something no crawler can follow and no second page can be reached through.
   Aimed at a real page, it puts all 366 **one click from every page on the
   site** — the prev/next ring made them *reachable*, this makes them
   *discoverable*, which is the thing that was actually missing.
2. `chrome_for("CALENDAR")` was already the chrome handed to `/day/` and
   perennial pages, so those pages were marking a nav tab current for a URL they
   had no fragment of. Tab and pages now agree.
3. A fifth tab was the alternative and I rejected it: tabs only show above
   760px and the row already carries brand, search and Jump-to-date, so a fifth
   item squeezes the search box at the narrow end of that range for no gain.

The homepage calendar widget is untouched and still reachable — `/dates/` carries
the one remaining link to `/#calendar`, and the homepage is the Today tab.

Breadcrumbs now follow one hierarchy: `Today / Calendar / October 8` on a
perennial page, `Today / Calendar / October 8 / Halloween` on a holiday page.

## Holiday pages: which date page they point at

The breadcrumb's date crumb and the `← See everything October 31 celebrates`
back-link now point at `/october-31/`. The reasoning: a holiday page lives
forever at one URL, so its parent should too — the dated page's URL changes
every year, which makes it a poor breadcrumb ancestor.

The dated page did **not** lose its inbound links. It is linked from the **Date
row of the spec list** (the `<time>` element is now wrapped in a link to it,
which is also the more honest place for it) and from *All N on October 31* in
the "Also on" sidebar. The sidebar link is conditional — it needs other
observances that day — so the spec row is what guarantees it, and there is an
assertion that every one of the 2,450 holiday pages carries at least one.

## Files touched

```
 M scripts/generate.py                 dates_hub_html(); /dates/ wired in; holiday-page
                                       crumbs, Date-row link and back-link; the
                                       PERENNIAL_EMPTY_PAGES decision in its comment
 M scripts/templates/holiday.html      hand-written crumbs -> CRUMBS; DATE_SPEC; back-link href
 M scripts/templates/partials/header.html   Calendar tab -> /dates/ (tabs + mobile menu)
 M scripts/templates/partials/footer.html   Calendar link -> /dates/
 M public/styles/site.css              one rule: .cat-list .cat-list-off
 M public/_headers                     /dates/* cache rule
 M public/llms.txt                     the date-page type, the hub, and which to cite
 M scripts/README.md                   URL model row + the navigation section
 M docs/REVIEW.md, docs/EXECUTION_PLAN.md
```

No generated file touched. The generator only ran into throwaway directories
outside the repo.

## What to check

1. **The nav change is the big one.** Every page on the site now differs from
   the committed version, because the header and footer are in every page's
   chrome. That is 2,450 holiday + 351 dated + 366 perennial + 17 browse pages.
   Nothing in that is content: see the verification below.
2. **`/dates/`** — 42 kB, 366 links, 12 month sections with an in-page month rail.
   Worth a look at phone width; it reuses the About page's prose wrapper and the
   category pages' two-column list, so it should need no new layout.
3. **One new CSS rule**, `.cat-list .cat-list-off`, which only renders if you
   ever set `PERENNIAL_EMPTY_PAGES = False` (it styles an unlinked row on the hub
   so the eight—now six—blank dates still appear, without linking to pages that
   were never written). Nothing uses it today.
4. **`public/llms.txt`** now describes the date pages and says which URL to cite
   for which question. It is hand-maintained and was in neither list in §3, so I
   have added it to the source list in the plan.

## How I verified it

- **Reverse-transform against the committed HEAD**, both generators run over the
  current `holidays.json` and `people.json` into seeded copies of `public/`:
  undoing the nav substitution makes all 351 dated pages, the homepage, About,
  Categories and all 14 category pages **byte-identical** to HEAD; undoing it
  plus the one added breadcrumb level does the same for all 366 perennial pages;
  undoing it plus the crumbs, the Date-row link and the back-link does the same
  for all **2,450 holiday pages**. Every one of the 3,184 changed files is
  accounted for, with **zero** unexplained deltas. The sitemap gained exactly
  one URL: `/dates/`.
- Exit 0, **zero WARNING lines**, sitemap 3,185 URLs, and a second run changes
  nothing — idempotent.
- The hub parses with no unbalanced tags, no leftover markers, 366 unique links
  that all resolve, 12 month headings, self-canonical, present in the sitemap
  once.
- **40 assertions**, including: no page anywhere still links `/#calendar` except
  the hub itself; the hub is linked from the nav and footer of every page type;
  every holiday page keeps a link to its dated page; every perennial link on
  every holiday page resolves; and with `PERENNIAL_EMPTY_PAGES = False` the hub
  drops to 360 links, renders the 6 blank dates unlinked, and no holiday
  breadcrumb points at a page that was not written.
- **Not measured:** CLS, and the hub at real phone width — nothing is deployed.

## Needs a decision

Only the five carried over from 2026-10-10, still unanswered. Full text in §5
of the plan under E2; in one line each:

1. **Leap Day** sits unpublished — publishing it extends the dated archive by
   ≈142 pages, or clamp `day_end` first.
2. **`Oktoberfest (ends in Germany)`** is wrong from 2027; needs a new rule kind
   or a lookup table for Munich's conditional October 3 extension.
3. **Tax Day** overlaps `Income Tax Pay Day`, and the IRS date shifts for
   weekends and DC Emancipation Day.
4. **National French Fry Day** — July 13 vs the second Friday of July; the move
   was an aggregator's, at a restaurant chain's request.
5. **Solstices / vernal equinox** already exist under other names: a naming
   call, not a coverage gap.

## What is left of E3

The **`/holidays/<year>/` index pages**, E3's fourth bullet — still not started,
and still the next engineering run's item. Note that `/dates/` is *not* that
page: the hub indexes the 366 year-less pages, a year index would list one
year's dated pages. Everything else in E3 is done.

Earlier notes from today (the overnight E3 run and the born-on-this-day
addendum, whose decisions Jay answered) are in git history:
`git show HEAD:docs/REVIEW.md`.
