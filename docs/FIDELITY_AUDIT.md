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

## Not findings

- **"Barbershop Quartet Day" is not duplicated.** It looked like it in a first
  pass; it is one row (one slug, 4/11).
- The three stale duplicate rows already named in §7 (National Taco Day Oct 6,
  National Forgiveness Day Oct 7, International Newspaper Carrier Day Oct 10)
  are unrelated to this error class and still harmless.
