# Holiday fidelity audit — candidate list

Durable companion to the audit Jay deferred to end of year
(`docs/EXECUTION_PLAN.md` §7). `docs/REVIEW.md` is overwritten every run, so
findings live here instead. Opened 2026-10-10 by the E2 run.

## The error class

A row stored as `Recurrence = Annual` with a fixed month/day, when the
observance is actually defined by a weekday rule. The site then shows the
right date for one year and the wrong date for every year after it.

`national-doughnut-day` was the known case (stored June 4; actually the first
Friday in June). Two were fixed on 2026-10-10 — see §8 of the plan.

## The detector

The dataset was bootstrapped from the live site's dates for one particular
year, so a weekday-ruled row's stored date **lands on its own named weekday in
exactly one year and drifts off in the next**. That is a cheap screen:

```
for every Annual row: does the name contain a weekday word?
                      does the stored date fall on that weekday this year?
                      ... and not next year?
```

It is a screen, not a verdict. Some of these may genuinely be fixed-date
observances whose name is historical. **Each row below still needs its own
primary-source check before anything is changed** — that is the whole point of
§4's sourcing rule.

## Candidates — named after a weekday, stored as a fixed date

Weekday shown for the stored month/day in 2026 and 2027.

| Row | Stored | 2026 | 2027 | Likely rule (unverified) |
|---|---|---|---|---|
| Fat Thursday | 2/4 | Wed | **Thu** | Thursday before Ash Wednesday → `easter_offset -52` |
| Friday Fish Fry Day | 2/12 | Thu | **Fri** | a Friday in Lent? |
| Mothering Sunday | 3/7 | Sat | **Sun** | 4th Sunday of Lent → `easter_offset -21` |
| Pretzel Sunday | 3/7 | Sat | **Sun** | same as Mothering Sunday |
| Thank You Thursday | 4/29 | Wed | **Thu** | unknown |
| National "Thank God It's Monday" Day | 6/7 | Sun | **Mon** | unknown |
| Willing-To-Lend-A-Hand Wednesday | 8/25 | Tue | **Wed** | a named day of Be Kind to Humankind Week (Aug 25–31) |
| Forgive Your Foe Friday | 8/27 | Thu | **Fri** | same week |
| Speak Kind Words Saturday | 8/28 | Fri | **Sat** | same week |
| Sacrifice Our Wants for Other's Needs Sunday | 8/29 | Sat | **Sun** | same week |
| Motorist Consideration Monday | 8/30 | Sun | **Mon** | same week |
| National Seat Check Saturday | 9/26 | **Sat** | Sun | Saturday of NHTSA's Child Passenger Safety Week — NHTSA is a federal primary source |
| Sunday School Teacher Appreciation Day | 10/18 | **Sun** | Mon | unknown |
| Frankenstein Friday | 10/30 | **Fri** | Sat | last Friday of October? |
| National Jersey Friday | 11/6 | **Fri** | Sat | a Friday in the NFL season? |

The Be Kind to Humankind Week cluster is one check, not five: either the
organizer assigns the names to fixed dates (Aug 25–31) and all five rows are
correct as Annual, or it assigns them to weekdays and all five are Floating.

## Candidates — weekday-ruled observances whose name doesn't say so

| Row | Stored | 2026 | 2027 | Likely rule (unverified) |
|---|---|---|---|---|
| Free Comic Book Day | 5/1 | Fri | **Sat** | 1st Saturday of May (freecomicbookday.com is the organizer) |
| National Bowling Day | 8/14 | Fri | **Sat** | 2nd Saturday of August (bowl.com) |
| National Garage Sale Day | 8/14 | Fri | **Sat** | 2nd Saturday of August |
| National Hunting and Fishing Day | 9/26 | **Sat** | Sun | 4th Saturday of September (established by Congress, 1972 — primary source available) |
| National Public Lands Day | 9/26 | **Sat** | Sun | last Saturday of September (NEEF / NPS) |
| Plaidurday | 10/2 | **Fri** | Sat | 1st Friday of October |
| National Ugly Christmas Sweater Day | 12/18 | **Fri** | Sat | 3rd Friday of December |
| World Sight Day | 10/8 | **Thu** | Fri | 2nd Thursday of October — already logged in §7 |
| Oktoberfest (ends in Germany) | 10/4 | **Sun** | Mon | first Sunday in October, **extended to Oct 3** when that Sunday is Oct 1 or 2 (City of Munich regulation 130 §2). Wrong from 2027. See *Needs a decision* in the 2026-10-10 review |

## Candidates added after the opening screen

The 2026-10-10 screen only looked at rows whose **name** carries a weekday word,
so it could not catch a row with a neutral name or a non-weekday rule. These were
found later, one at a time, and §7 of the plan asks for them here. Added
2026-11-07 by the engineering run; none has been changed.

| Row | Stored | Next occurrence | Likely rule (unverified) | Found |
|---|---|---|---|---|
| `international-stout-day` | Annual 11/5 | 2027-11-05 | 1st Thursday of November. Nov 5 **is** that Thursday in 2026 and in no nearby year (2027 → Nov 4, 2028 → Nov 2). Observed dates fit from 2017 on (2017 Nov 2, 2020 Nov 5, 2024 Nov 7) but **2012 and 2013 do not**. | 2026-11-05 content run |
| `fountain-pen-day` | Annual 11/6 | 2027-11-06 | 1st Friday of November. Nov 6 is that Friday in 2026 only (2024 Nov 1, 2025 Nov 7, 2027 Nov 5). | 2026-11-06 content run |
| `international-tongue-twister-day` | Annual 11/8 | 2027-11-08 | **2nd Sunday of November.** Nov 8 is that Sunday in 2026 only (2024 Nov 10, 2025 Nov 9, 2027 Nov 14 — verified by calculation). The aggregators that promote the day publish it on Nov 8, Nov 10 **and** Nov 12 across different years, which is the rule leaking through a fixed-date field. | 2026-11-08 content run |
| `ascension` | Annual 5/6 | 2027-05-06 | `easter_offset +39`. **Right for 2027 by coincidence** (Easter 2027 = Mar 28); Easter 2028 = Apr 16, so the true date is **2028-05-25** and the stored one is wrong from 2028 on. Typed `Religious` on 10-13. | 2026-10-13 E4 run |

**All three November rows are blocked on sourcing, not on effort.** The weekday rule is
stated only by aggregators. `fountainpenday.org` — the observance's own former site,
and the one body that could have confirmed its rule — now redirects to an unrelated
commercial site behind a bot wall. `international-tongue-twister-day` is worse off still:
the 2026-11-08 content run could find **no founding body, government page or news outlet
for the observance at all**, only aggregators, so there is not even a candidate authority
to ask. Under §4's sourcing rule there is nothing primary
to change these to, so they stay as stored and stay listed here. `ascension` is the
opposite case: the rule is not in doubt at all, only the fix is unmade, and it is the
one row on this page that could be corrected tonight if the audit were a queue item.

**Correction to the 2026-11-06 §7 note:** it records `National Jersey Friday`
(Annual 11/6) as "untouched, unqueued". It is untouched, but it is **not unqueued** —
it has been in the weekday-named table above since this file was opened on 2026-10-10.
Nothing to add; the note was simply duplicating a known row.

## Candidate outside the detector — weekday-ruled but not weekday-named

**`national-bison-day` · stored `Annual` 11/7 · found by the 2026-11-07 content run.**

This is the first candidate on this page whose rule is stated by an **acceptable** source,
and the first whose error has become visible on a published page.

- The observance is the **first Saturday of November**. Sources: the National Bison
  Association — "Since 2012, the United States Senate has annually designated the first
  Saturday in November as National Bison Day"
  (https://nationalbison.org/2026-national-bison-day-saturday-november-7/); the submitted
  Senate resolution texts for 2017 and 2023, each reading "designates November 4, ...,
  the first Saturday of November"
  (https://www.hoeven.senate.gov/wp-content/uploads/media/doc/MAZ17147.pdf and
  https://www.heinrich.senate.gov/imo/media/doc/national_bison_day.pdf); and Public Law
  114-152's findings, "committed to continuing this tradition annually on the first
  Saturday of November"
  (https://www.govinfo.gov/content/pkg/PLAW-114publ152/html/PLAW-114publ152.htm).
- First Saturdays: **2026 Nov 7 · 2027 Nov 6 · 2028 Nov 4.** The stored Annual 11/7
  matches 2026 only — the exact signature this page screens for.
- **Not changed**, because recurrence belongs to this audit rather than to a content run.
  But unlike `international-stout-day` and `fountain-pen-day`, this row is **not blocked on
  sourcing**. It is blocked only on the decision to run the audit.
- **The published page states the first-Saturday rule**, since the rule is sourced and §4
  requires accuracy. The generated Dates table will keep showing November 7. From 2027 the
  page contradicts its own date table where readers can see it. That is new: every other
  row on this page is wrong silently.

### What this row says about the detector

The screen above asks whether a row's **name** contains a weekday word. `National Bison
Day` contains none, and would never have surfaced. The error class is therefore wider than
the screen: **any** observance defined by a weekday rule can be stored as a fixed date,
whether or not its name admits it. Candidates found by reading sources during content runs
(`international-stout-day`, `fountain-pen-day`, now `national-bison-day`) have all come in
outside the screen. Widening it — or accepting that content runs are the real detector — is
a scope decision for whoever runs the audit.

## Not findings

- **"Barbershop Quartet Day" is not duplicated.** It looked like it in a first
  pass; it is one row (one slug, 4/11).
- The three stale duplicate rows already named in §7 (National Taco Day Oct 6,
  National Forgiveness Day Oct 7, International Newspaper Carrier Day Oct 10)
  are unrelated to this error class and still harmless.
