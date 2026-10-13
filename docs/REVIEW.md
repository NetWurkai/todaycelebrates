# Review — 2026-10-13, engineering run (E4, first slice)

Tree was clean at the gate. E3 is done and committed, so this run opened
**E4 — observance type taxonomy**. E4 is a multi-run item (its acceptance
criterion covers ~2,450 Notion rows); this run built **all of the machinery**
and typed **40 rows where the type is not a judgment call**.

## What I changed and why

A flat day list gives Thanksgiving and National Pumpkin Day the same visual
weight. The clearest case in the data: **July 4, 2027 currently leads with
*Alice in Wonderland Day***, with a books hero image, and Independence Day
sits at number two. After this change it leads with Independence Day.

**Notion.** New `Type` select on *Today Celebrates — Holidays*:
`Federal · State · Religious · Cultural · Observance · Season & Clock · Fun`,
with a property description stating the sort order and the Federal rule.
Additive — no existing property or row content touched, `Published` and
`Content Status` untouched everywhere.

**Typed 40 rows, and only these:**

- **Federal (11)** — the statutory list in **5 U.S.C. § 6103** and nothing
  else: New Year's Day, Martin Luther King, Jr. Day, Presidents' Day,
  Memorial Day, Juneteenth, Independence Day, Labor Day, Columbus Day,
  Veterans Day, Thanksgiving Day, Christmas Day.
- **Season & Clock (6)** — astronomical or clock events, no judgment in them:
  The First Day of Spring, The First Day of Summer, Autumnal Equinox, First
  Day of Winter, The Start of Daylight Saving Time, Daylight Saving Time Ends.
- **Religious (23)** — Advent Sunday, All Saints' Day, All Souls' Day,
  Ascension, Ash Wednesday, Assumption of Mary, Diwali, Easter Monday, Easter
  Sunday, Eid al-Fitr, Good Friday, Islamic New Year, Maundy Thursday,
  Orthodox Christmas Day, Palm Sunday, Passover, Pentecost, Purim, Rosh
  Hashanah, The Start of Hanukkah, The Start of Ramadan, Tu BiShvat, Yom
  Kippur.

**2,410 rows are deliberately left untyped.** See *Needs a decision*.

**Code.** `obs_sort_key()` is `(type rank, Order, name)` and is now the single
sort for the dated pages, the perennial pages, the home page and the month
data files. `Order` stays the tiebreaker *inside* a type, so the curation
already in Notion still decides between two Fun days — the taxonomy only
overrules it between two rows of different kinds. A typed row gains `data-t`,
a `t-<slug>` class and a small chip after its name; on row one the chip
**replaces** the `Lead` label, because the type says more than "Lead" does.

Which tiers read as "major" is one CSS selector, not a Python constant, so you
can move the line in one edit:

```css
.obs tr.t-federal td.nm a,.obs tr.t-state td.nm a,.obs tr.t-religious td.nm a{font-size:17px}
```

**An untyped row renders byte-identically to before** — same rule as E1, same
reason. The exporter omits the `type` key when the select is empty; `obs_row()`
emits no attribute, class or chip. Month data entries stay
`[name, slug, category, yearly]` and gain a **fifth element only when typed**,
so those files change only where a row was actually typed and old cached
copies on either side keep working.

## Files touched

```
 M scripts/generate.py              +124/-11: TYPE_ORDER / TYPE_SLUG / type_rank /
                                    obs_sort_key / type_tag / type_json, obs_row
                                    markup, both sort sites, the 5th month-data
                                    element, type_counts + unknown_types in the
                                    report, and a WARNING for an unknown Type
 M scripts/export_from_notion.py    +18: carry Notion's Type, omit the key when unset
 M scripts/templates/index.html     +14/-3: TYPES var and the obsRow() mirror
 M public/styles/site.css           +21: .tg chips, the one "major" rule, a mobile
                                    wrap rule for the name cell
 M scripts/README.md                +72: a section on the taxonomy
 M docs/REVIEW.md, docs/EXECUTION_PLAN.md
```

No generated file touched. The generator only ran into throwaway directories
outside the repo. Nothing committed, nothing pushed. **The chips and the new
ordering are not in `public/` yet** — they appear when you commit and the
daily Action regenerates from Notion, which is the normal path.

## What you should check

1. **The 16 pages whose lead changes.** This is the whole visible effect, and
   two of them are arguable:

   | date | led with | now leads with |
   |---|---|---|
   | 2026-12-04 | Bartender Appreciation Day | The Start of Hanukkah |
   | 2027-01-23 | International Sticky Toffee Pudding Day | Tu BiShvat |
   | 2027-03-09 | Barbie Day | Eid al-Fitr |
   | **2027-03-14** | **Pi Day** | **The Start of Daylight Saving Time** |
   | 2027-03-21 | Naw-Ruz | Palm Sunday |
   | 2027-03-23 | American Diabetes Association Alert Day | Purim |
   | **2027-04-22** | **Earth Day** | **Passover** |
   | 2027-05-16 | Biographers Day | Pentecost |
   | 2027-06-06 | Drive-In Movie Day | Islamic New Year |
   | 2027-06-19 | Dog Dads Day | Juneteenth |
   | 2027-06-21 | Go Skateboarding Day | The First Day of Summer |
   | 2027-07-04 | Alice in Wonderland Day | Independence Day |
   | 2027-09-23 | National Snack Stick Day | Autumnal Equinox |
   | 2027-10-02 | International Day of Non-Violence | Rosh Hashanah |
   | /july-4/ | Alice in Wonderland Day | Independence Day |
   | /june-19/ | Dog Dads Day | Juneteenth |

   **Pi Day losing to DST is temporary** — it corrects itself the moment Pi Day
   is typed, because Cultural and Observance both outrank Season & Clock.
   **Earth Day losing to Passover is permanent** under the plan's ordering:
   Religious outranks Observance whatever Earth Day gets typed as. If that is
   wrong, it is the ordering that is wrong, not the data.

   The lead also sets the hero image, the meta/OG/Twitter description and the
   `ItemList` order, so all of those move with it.

2. **The chip at phone width.** The name cell is its own grid area under
   760px, so a long name plus a chip can wrap to two lines. I let it wrap
   rather than clip. Nothing is deployed, so I could not look at it.

3. **Chip replacing `Lead` on row one.** A styling call, easily reversed —
   say the word and both can show.

## How I verified it

Three full generator runs over seeded copies of `public/`, all at
`--today 2026-10-13`, all into throwaway directories outside the repo.

- **A = pre-patch generator + today's data. B = patched generator + today's
  (untyped) data. A and B differ in exactly one file**: `index.html`, and only
  in its inline script (the new `TYPES` map and the `obsRow()` mirror). All
  2,450 holiday pages, 351 dated pages, 366 perennial pages, both year
  indexes, all 13 data files, the sitemap and `/about/` are **byte-identical**.
  That is the degradation requirement, proven rather than asserted.
- **C = patched generator + the 40 rows typed.** Against A, exactly **194
  files** differ: 131 holiday pages (their *All N on this date* sidebar
  reorders), 39 dated pages, 10 perennial pages (the 10 typed rows that are
  `Annual`; the `Floating` ones live in the moves note, which is year-ordered
  and untouched), 13 data files, and `index.html`. Nothing else.
- **6,606 automated invariant checks, 0 failures**, across every one of those
  194 files: no holiday is gained or lost on any page (multiset of
  `/holiday/<slug>/` links identical A↔C); the table rows are a *permutation*,
  not a rewrite; every chip sits on a row whose `data-t` matches; exactly one
  chip per typed row and none on an untyped one; `Lead` and a chip never
  co-occur; month-data entries are the same set with arity 4 or 5 and a valid
  type in position 5; no leftover `<!--TC:` markers; balanced `<tr>`/`<span>`;
  **sitemap byte-identical**. All 40 typed rows render a chip.
- **Exit 0 and zero WARNING lines** on every run.
- **Idempotent**: a second run over C's output reports 0 created, 0 changed,
  sitemap unchanged, and is byte-identical.
- **25 unit assertions, 0 failures** — rank order, untyped last, unknown type
  just above untyped, `Order` as the in-type tiebreaker, an all-untyped day
  keeping exactly the old `(Order, name)` order, untyped markup unchanged,
  typed markup, `Season & Clock` escaping to `Season &amp; Clock` identically
  in Python and in the inline script, `type_json()` matching `TYPE_SLUG`, and
  the exporter omitting the key for an empty or cleared select while leaving
  the other keys in their existing order.
- **Unknown-type path tested end to end**: a row typed `Bank Holiday` produces
  a `WARNING`, lands in the report's `unknown_types`, and leaves the site
  **byte-identical** — it renders as untyped rather than inventing a tier.
- **Every type slug has a `.tg-` rule** in `site.css`, checked mechanically.

**Not measured:** CLS, and real phone-width rendering — both still need a
deploy, same as after E3.

## Needs a decision

1. **The rule for the remaining 2,410 rows.** This is the real blocker and the
   reason this run stopped at 40. Three boundaries I would not guess at:
   - **Saints' feast days.** St. Patrick's Day, St. Nicholas Day, Feast of
     Saint George / Saint James / Saints Peter and Paul, St. Francis of Assisi
     Feast Day. Each is literally a saint's feast, but St. Patrick's Day in the
     US is observed secularly. Either they are all Religious or the test is
     "how it is actually observed here" — I left all six untyped rather than
     split them inconsistently. (`St. Urho's Day` is an invented joke saint and
     is not in this class.)
   - **Secularized religious holidays.** Valentine's Day, Halloween, Christmas
     Eve, Feast of the Seven Fishes, Yule, Ostara, Naw-Ruz. Christmas Day only
     escaped this because Federal settles it — which is itself a loss: the
     single-select cannot say "federal *and* religious".
   - **Observance vs Fun**, which is most of the remaining rows. National
     Pizza Day and World Mental Health Day are both "National/World ___ Day"
     and clearly belong on opposite sides, but I have no rule that separates
     them at scale. A usable one might be: *Fun* = commercial or
     invented-for-fun origin, *Observance* = a cause, a profession, or a
     government/NGO proclamation. Say the word and the next run applies it and
     reports every call.
2. **Is `Season & Clock` really sixth?** I took §5's list as a priority order
   verbatim. It puts the solstices and DST below every awareness day that ever
   gets typed `Observance`. Pi Day vs DST above is this question in miniature.
3. **Untyped rows sort last.** The alternative is to slot them where
   `Observance` sits, which would make the transition gentler but means the
   order keeps shifting as rows are typed. Last is predictable; it is still a
   choice.

### Not an E4 decision, but found while in there

4. **`Ascension` is stored as a fixed May 6 (Annual) and is a moveable
   feast** — Easter + 39 days. Palm Sunday, Maundy Thursday, Good Friday and
   Pentecost are all correctly `Floating`; Ascension is the odd one out. It is
   right for 2027 by coincidence (Easter 2027 is March 28) and **wrong from
   2028**. Same class as the Donut Day bug, and it is **not** in
   `docs/FIDELITY_AUDIT.md` — the screen only catches weekday-ruled rows, and
   this one is ruled off Easter. I did not fix it: it is E2/§7 work, and rule 5
   is one item per run.

### Carried over, still unanswered

These block E2 and nothing else; they did not block this run.

5. **Leap Day** sits unpublished; publishing it extends the dated archive by
   ≈142 pages (and adds a `/holidays/2028/` page), or clamp `day_end` first.
6. **`Oktoberfest (ends in Germany)`** is wrong from 2027.
7. **Tax Day** overlaps `Income Tax Pay Day`.
8. **National French Fry Day** — July 13 vs the second Friday of July.
9. **Solstices / vernal equinox** already exist under other names — a naming
   call, not a coverage gap.
10. From 2026-10-12: a bare **`/holidays/`** 404s; and the 2026 year page makes
    the archive's start line visible, which raises backfilling.
11. From the 2026-10-11 content run: the Notion **`FAQ` field description is
    stale** (still says questions must be bolded), and **`parse_faq()` is
    stricter than §4 describes** (it requires a trailing `?`).

## Where the queue stands

**E4 is partly done.** The machinery is finished and verified; 40 of ~2,450
rows are typed. The next engineering run either continues E4 with an
assignment rule from you (question 1), or — if you would rather not spend
several nights on bulk property writes — skips to **E5, calendar export**,
which is independent of all of this. Both are fine; E4's code half degrades
cleanly for as long as the rest stays untyped.

Earlier review notes are in git history: `git show HEAD:docs/REVIEW.md`.

---

## Content run 2026-10-12 — notes for the engineering run
*(Back-filled by the 2026-10-13 content run; the 2026-10-12 run lost the device
bridge before it could write this.)*

1. **The §6 tick marks are not a reliable record of what is published, and an
   unattended run that trusts them will overwrite live pages.** The 2026-10-12
   run found items 6-8 unticked in §6 but already Live in Notion, written by the
   2026-10-11 run, which lost the bridge before it could tick them. **This has
   now happened three runs in a row** — the 2026-10-13 run found items 9-11 in
   the same state and back-filled them too. Worth either (a) having the content
   task derive the queue from Notion (`Body` empty and `Content Status` empty)
   rather than from the ticks, which is what the Tier 5 rule already does, or
   (b) writing the Run Log line and ticks *before* the Notion writes.
   Option (a) is the stronger fix: it makes the ticks a convenience rather than
   the source of truth. **This is the single highest-value change to the content
   task prompt right now** — three runs have each burned part of their budget
   detecting and repairing it, and a run that happened not to check Notion first
   would have silently rewritten three live pages.
2. **The Notion `FAQ` field description is still stale.** It reads "Question on
   its own line wrapped in **bold**". Raised by the 2026-10-11 and 2026-10-12
   runs and still unchanged as of 2026-10-13. Since the 2026-10-10 fix, bolding
   is a no-op that never survives `plain_text`. It is the first thing a future
   session reads about the field. One-line fix in the Notion schema.
3. **`parse_faq()` is still stricter than §4 says** (it requires a trailing `?`,
   §4 says only "first line of a blank-line block"). Raised 2026-10-11, still
   open. Every question written since ends in `?`, so nothing is affected now.
4. **Content runs still cannot run the generator.** The exporter needs a
   `NOTION_TOKEN` that is not in the repo or available to a scheduled session,
   so content runs can only check field shapes over the Notion API, never
   rendering end to end. If end-to-end verification matters for content runs,
   the token needs to reach them, or the generator needs a mode that renders
   from a hand-built fixture.
5. E2's five open decisions and E3's two from the 2026-10-12 engineering run are
   untouched by the content runs and still open.
