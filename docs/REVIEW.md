# Review — 2026-10-15, engineering run (E6, submitted occasions — publication half)

Tree was clean at the gate, so last night's E5 work is in. E4's remaining ~2,410
rows are still waiting on an assignment rule from you, so per §5 I took **E6 —
submitted occasions**, and did the half of it that does not need a decision from
you. Yesterday's review is in git history: `git show HEAD:docs/REVIEW.md`.

## What I changed and why

E6 is two halves. The upstream half (form → Stripe → Worker → Notion row) needs
a price and a deployment decision from you. The downstream half — what happens
to a paid listing once it is approved — needed neither, and it is the half the
non-negotiable constraints are actually about. That is what is built.

**The key decision, and the reason I made it rather than asking:** paid
occasions live in their **own Notion database**, not behind a flag in the
Holidays one. E6's acceptance criterion is that a paid occasion cannot reach
Event structured data *even if misconfigured*. In one database, "misconfigured"
is one wrong click. In two, there is no code path at all: `occasions.json` is
never merged into `holidays`, so a listing cannot reach the observance list, a
`/holiday/` URL, the month data files, `search.json`, any calendar feed or any
`Event` JSON-LD. The criterion more or less dictates the answer, so I took it —
and the database is empty, so reversing it costs nothing.

Four further guards sit on top of that:

| Guard | What it stops |
| --- | --- |
| Occasion pages render from `templates/page.html` | That template has **no JSON-LD slot**, so the page cannot carry structured data of any kind |
| The generator greps its own rendered output for `"@type": "Event"` and refuses to write the page if it finds one | A future template or code edit quietly reintroducing it |
| `validate_occasions()` re-checks everything the exporter checked | A hand-edited `occasions.json` |
| A slug already belonging to a holiday is dropped, in both the exporter and the generator | A paid listing passing itself off as a real observance by name |

The listing itself: its own page at `/occasions/<slug>/`, a directory at
`/occasions/`, and a labelled `.occ` block **appended after every other block**
on its dated page — never interleaved with the observance table, never in that
page's `ItemList`. The submitter's link carries `rel="sponsored nofollow
noopener"`, because it was paid for. `Review Status = Approved` is the only gate;
setting a row back to `Pending` is the revert.

**It is dormant.** There is no `occasions.json`, so the site the generator writes
tonight is byte-identical to the one it wrote yesterday — zero new files, zero
changed pages, zero sitemap URLs. Nothing goes live until you wire step 4 below.

## Files touched

| File | Change |
| --- | --- |
| `scripts/export_occasions_from_notion.py` | **New, 266 lines.** Approved rows only → `occasions.json`. Slug-collision and tier guards; no shrink guard, deliberately (a withdrawn listing must disappear at once, not be protected as "too big a drop") |
| `scripts/generate.py` | +353/−8. `OCCASION_*` constants and the two disclosure strings; `load_occasions`, `validate_occasions`, `occasions_block_html`, `occasion_body_html`, `occasion_page_html`, `occasions_index_body`; the occ indexes in `generate()`; pages routed through `simple_pages`; 5 report keys and 3 warning paths |
| `scripts/templates/day.html`, `templates/perennial.html` | +1 marker each, last in the content column |
| `public/styles/site.css` | +18. `.occ` — neutral outline, no pills, no hero weight, static markup |
| `public/_headers` | +7. `/occasions/*` at a 10-minute cache, shorter than the pages: a withdrawn listing should leave the edge fast |
| `public/llms.txt` | +4. a section saying these are paid listings and not to cite one as an observance |
| `scripts/README.md` | +103. "Submitted occasions (E6)" — the two-database argument, the guards, the gate, and what is not built |
| `docs/EXECUTION_PLAN.md` | §3 boundary, E6 status, Run Log |

**Notion:** one new database, **"Today Celebrates — Submitted Occasions"**
(`7c9d328c-0360-4feb-aabf-998f6402eed9`), 17 properties, each with a description,
**zero rows**. The Holidays database was not touched at all.

Nothing in `public/` is generated output in this diff — I ran the generator into
throwaway directories, never into `public/`.

## What you should check

- **The two-database call**, above. It is the one judgment in this run, and the
  database is empty, so if you want occasions as rows in the Holidays database
  instead, say so and it is a short run to redo — but read the argument first.
- **The disclosure wording**, in `OCCASIONS_LIST_NOTICE` and
  `OCCASIONS_PAGE_NOTICE` at the top of `generate.py`. It says plainly that
  these are paid listings and not official observances. That sentence is the
  thing standing between this feature and the aggregators, so it is worth your
  own words rather than mine.
- **The `.occ` block's weight.** I made it deliberately quieter than the
  observance table — neutral outline, no category pill, muted blurb. Unseen on a
  real device, like everything else since E3.
- **The Notion database's property set**, in case the form you have in mind asks
  for something I did not give it a field for (a logo, a second link, a city).

## How I verified it

**52 structural checks and 34 unit assertions, 0 failures.** The ones that matter:

- **The dormant path is byte-identical.** Ran HEAD's generator (with HEAD's
  templates) and the patched one into two fresh directories. `diff -r` over all
  **5,670 files: no differences at all** — not one page, data file, feed or
  sitemap line. Same result for a damaged `occasions.json` and for an absent one,
  both of which warn-and-disable rather than failing the build.
- **The populated path touches only what it should.** With a 9-row fixture (4
  usable, 5 rejected for every distinct reason), exactly **5 new files** (4
  listings + the directory) and **5 changed**: 3 dated pages, 1 perennial page,
  and `sitemap.xml`. No `.ics` file, no data file, no holiday page, no year page,
  no hub, no home page.
- **Reverse-transform.** Removing the `<section class="occ">` block from those 4
  changed pages makes them **byte-identical** to the no-occasions run. Zero
  unexplained deltas.
- **The structured data stays clean.** The `ItemList` JSON-LD on each affected
  dated page is byte-identical with and without occasions and names none of
  them. No occasion page contains `application/ld+json` at all, let alone an
  `Event`. No occasion name or slug appears in `search.json` or any month data
  file.
- **Every reject path fires:** wrong tier, slug colliding with `halloween`,
  malformed slug, bad date, empty blurb, missing name, duplicate slug, junk
  entries — each dropped with its own warning. A `javascript:` link is stripped
  while the row survives. Markdown in a body cannot inject HTML.
- **Sitemap:** gained exactly the 5 occasion URLs, lost none, no duplicates.
- **Idempotent:** a second run over the same directory changed 0 files.
- **Withdrawal works, and says so.** Removing a listing from the fixture drops it
  from the date pages and the sitemap on the next run, and the run **warns** that
  `public/occasions/<slug>/` is still on disk — the generator never deletes
  generated output, and for a paid listing someone asked to take down, that
  warning is the thing to act on.
- **A listing dated beyond the archive** gets its page but appears in no date
  list, and the run warns. An occasion contributes **no** date to the archive
  horizon, so a listing dated 2031 cannot backfill five years of `/day/` pages.
- **Generator run for the record** (`--today 2026-10-15`, throwaway dir, no
  occasions): **exit 0, zero WARNING lines**, 5,670 files, type counts unchanged
  (40 typed / 2,410 untyped).

**Not verified: the exporter never ran against live Notion** — there is no
`NOTION_TOKEN` in this run's shell. Its property names are exactly the ones the
database returned on creation, and its extraction logic is unit-tested against
synthetic Notion payloads (16 assertions), but the live round-trip is untested
and the integration still has to be shared with the new database.

## Needs a decision

1. **What does the Listed tier cost, and what does it include?** This is the one
   thing blocking the rest of E6: no price means no Stripe product, which means
   no Checkout and no Worker. A number and one line on what the buyer gets is
   enough to unblock a whole run.
2. **Does a paid listing appear once, or every year?** I did not guess: the
   Notion row carries a `Recurs Yearly` checkbox, off by default, and the
   generator honours it — off puts the listing on its one dated page, on also
   puts it on the year-less `/<month>-<day>/` page forever. Which one you
   actually sell is a pricing answer, and it may want an expiry date on the row
   rather than a permanent tick.
3. **Where does the Worker live?** `wrangler.jsonc` declares **assets only** (no
   `main`). Adding a Worker to it changes how the live site deploys, which is not
   a change I will make to a live site unattended. The alternatives are a second
   Worker on its own route, or Cloudflare Pages Functions. Your call.
4. **Are paid listings in the sitemap?** I put `/occasions/` and each listing in
   it: being findable is what the buyer is paying for, and the pages are honestly
   labelled and `nofollow`ed outbound. If you would rather they were `noindex`,
   that is a one-line change — but then it is worth asking what the tier is
   selling.

Smaller, not blocking anything:

5. **The home page does not show occasions.** Dated and perennial pages do. The
   home page's list is built by an inline script from the month data files, so
   adding them there means touching that script and the data format — more risk
   than the rest of this run put together, for a feature with no rows in it yet.
   Worth doing before the first listing goes live.
6. **No `/submit/` page exists, so nothing on the site links to `/occasions/`**
   except the listings themselves. Deliberate: I did not want to advertise a
   submission route that does not work yet.

## Carried over, still unanswered

Unchanged; none of them blocked tonight.

1. **The assignment rule for E4's remaining ~2,410 rows** — still the real
   blocker. Three boundaries an unattended run must not guess: **saints' feast
   days** (St. Patrick's, St. Nicholas, Feast of Saint George / James / Peter and
   Paul, St. Francis — all literally feasts, but observed secularly here: all
   *Religious*, or is the test "how it is actually observed"?); **secularized
   religious holidays** (Valentine's Day, Halloween, Christmas Eve, Feast of the
   Seven Fishes, Yule, Ostara, Naw-Ruz — Christmas Day only escapes because
   *Federal* settles it, which the single-select cannot say alongside
   *Religious*); and **Observance vs Fun**, which is most of the remainder. A
   usable rule might be: *Fun* = commercial or invented-for-fun origin,
   *Observance* = a cause, a profession, or a government/NGO proclamation. Say
   the word and the next run applies it and reports every call.
2. **Is `Season & Clock` really sixth?** It puts the solstices and DST below
   every awareness day typed *Observance*.
3. **Untyped rows sort last** — predictable, but a choice.
4. **`Ascension` is stored as a fixed May 6 and is Easter + 39 days** — right for
   2027 by coincidence, **wrong from 2028**, and absent from
   `docs/FIDELITY_AUDIT.md` because that screen only catches weekday-ruled rows.
5. **Leap Day** sits unpublished; publishing it extends the dated archive by ≈142
   pages (and adds a `/holidays/2028/` page), or clamp `day_end` first.
6. **`Oktoberfest (ends in Germany)`** is wrong from 2027.
7. **Tax Day** overlaps `Income Tax Pay Day`.
8. **National French Fry Day** — July 13 vs the second Friday of July.
9. **Solstices / vernal equinox** already exist under other names — a naming
   call, not a coverage gap.
10. A bare **`/holidays/`** 404s; and the 2026 year page makes the archive's
    start line visible, which raises backfilling.
11. The Notion **`FAQ` field description is stale** (still says to bold the
    questions), and **`parse_faq()` is stricter than §4 describes** (it requires
    a trailing `?`).
12. From E5: the now-redundant in-browser **Add to calendar** button duplicates
    `/holiday/<slug>/event.ics`; **footer/home discovery** for the feeds; the
    **1.9 MB `/calendar.ics`** and a federal-holidays-only feed (wants E4's
    typing); and **CLS still unmeasured** on `/dates/`, the year pages, the
    `.cal` box and now the `.occ` block. All of those need a deploy.
13. From the 2026-10-14 content run: three Tier-1/2 pages run **over §4's
    600–900 word target** (≈915 / ≈1,040 / ≈1,170), every claim sourced —
    whether to enforce the cap on dense-history holidays is yours; and the
    **2026-10-13 content run's three rows were found empty** the next night,
    which is either writes that never reached Notion or rows cleared since. That
    one is still unexplained.

---

## Content run — 2026-10-15 (appended; engineering run owns the rest of this file)

Queue items 15–17 taken to publication depth and set **Content Status = Live**:
Labor Day (`/holiday/labor-day/`), Martin Luther King, Jr. Day
(`/holiday/martin-luther-king-jr-day/`), Presidents' Day
(`/holiday/presidents-day/`). `Published` was not touched on any row; `Description`
was left in place and `Opening` written separately, as §4 requires.

**What to spot-check**

- **Presidents' Day leans on the name gap.** The page says flatly that the federal
  holiday is "Washington's Birthday" and that "Presidents' Day" was never adopted,
  sourced to the National Archives and OPM. That is correct but it is a stronger
  claim than most sites make, and it is the page's whole angle. Worth a read.
- **Labor Day's FAQ declines to answer a question.** "Why September rather than
  May 1?" is answered with *we could not find a primary source for that decision*.
  That is §4's candor rule applied literally; if you would rather the page just
  dropped the question, say so and it comes out.
- **Mount Vernon free admission** (Presidents' Day, How to observe) is documented
  for the 2026 observance only. The page tells readers to check the year's schedule.
  This is the run's least confident claim.
- **REVIEW item 13, first half, is now enforced, not escalated.** All three pages
  were trimmed from a ~1,000–1,050-word first pass down to ~854 / ~898 / ~860 so
  they sit inside §4's 600–900. The underlying question you raised on 2026-10-14 —
  whether dense-history holidays should be allowed over the cap — is still yours to
  settle; this run just assumed the answer is no.
- **REVIEW item 13, second half, shows no symptom now.** All fourteen previously
  written rows (Halloween through Memorial Day) still hold their long-form content
  and are all `Live`, Body 2.6–3.7 KB each. Nothing is empty. Note that Christmas
  Day, Valentine's Day and New Year's Day are `Live` in Notion although §6 still
  annotates them "Draft" — released at some point after they were written. Not
  changed by this run.

**Omitted for lack of a source** — the September-vs-May-1 rationale for Labor Day;
the 1983 House and Senate vote counts on the King holiday bill; and the common
claim that South Carolina was the *last* state to adopt it (the 2000 act is cited
for what it does say, not for the ranking).

**Conflicts resolved toward the more primary source** — the Obama White House
archive page gives both November 2 and November 20, 1983 for Reagan's signature;
the page follows the Statutes at Large (97 Stat. 917), November 2. The Library of
Congress says the 1894 Labor Day act was "approved" where the Department of Labor
says Cleveland signed it; the page follows Labor. Both choices are stated in the
pages' own Sources notes, not just here.

**Stale field description in Notion.** The `FAQ` property's description in the
Holidays database still says questions must be wrapped in `**bold**`. That has been
wrong since the 2026-10-10 renderer change and is exactly the instruction that made
every earlier FAQ parse to zero pairs. This run ignored it and wrote unbolded
questions; all three parse to 5 pairs against `generate.py`'s `parse_faq()`.
Updating that one property description would remove a live trap for future runs.

**Verification** — generator run into a throwaway directory on the committed
`holidays.json`: exit 0, zero WARNINGs, `occasions_problems` empty. The exporter
could **not** be run against live Notion (no `NOTION_TOKEN` in this run's shell),
so the end-to-end round trip of these three rows is unverified until the next
scheduled deploy. Nothing committed; no generated output touched.
