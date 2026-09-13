#!/usr/bin/env python3
"""
Today Celebrates — static site generator.

Pure function: holidays.json + a "today" date -> regenerated month data
files, per-holiday static pages, and sitemap.xml.

No Notion dependency. Reusable for the one-time Phase 3 run and for the
future Phase 4 daily cron (GitHub Actions pulls fresh Notion rows, writes
holidays.json, then calls this script).

Recurrence model:
  - "Annual" holidays have a fixed (month, day). Each generation run picks
    the NEXT occurrence of that (month, day) on or after `today`, rolling
    into next year if this year's date has already passed.
  - "Floating" holidays are computed per-year via a rule -- nth-weekday-of-
    month, last-weekday-of-month, an Easter offset, a fixed almanac/calendar
    lookup table (for astronomical or lunar/lunisolar events), or an offset
    relative to another holiday's date in this same dataset (e.g. Black
    Friday = Thanksgiving + 1 day) -- then the same next-occurrence-on-or-
    after-today logic is applied. See compute_floating_date() for the full
    list of rule kinds.

This means the site always shows each holiday's next upcoming occurrence
under its one permanent URL — no year in the slug, no duplicate pages per
year. A holiday whose date has already passed this year quietly rolls
forward to next year's date the next time the generator runs; that's the
"auto-recur" behavior confirmed with Jay for Phase 3.

Usage:
  python3 generate.py --holidays holidays.json --site /path/to/public --today 2026-09-13 [--dry-run]
"""
import argparse
import calendar
import datetime
import json
import os
import re
import sys

MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

SITE_BASE_URL = "https://todaycelebrates.com"


# ---------------------------------------------------------------------------
# Date computation
# ---------------------------------------------------------------------------

def nth_weekday_of_month(year, month, weekday, n):
    """weekday: 0=Monday ... 6=Sunday (Python's convention). n: 1-based."""
    first = datetime.date(year, month, 1)
    first_weekday = first.weekday()
    offset = (weekday - first_weekday) % 7
    day = 1 + offset + (n - 1) * 7
    days_in_month = calendar.monthrange(year, month)[1]
    if day > days_in_month:
        raise ValueError(f"nth_weekday_of_month: no {n}th weekday {weekday} in {year}-{month:02d}")
    return datetime.date(year, month, day)


def labor_day(year):
    return nth_weekday_of_month(year, 9, 0, 1)  # 1st Monday of September


def last_weekday_of_month(year, month, weekday):
    """weekday: 0=Monday ... 6=Sunday. The LAST occurrence of that weekday in the month."""
    days_in_month = calendar.monthrange(year, month)[1]
    last = datetime.date(year, month, days_in_month)
    offset = (last.weekday() - weekday) % 7
    return last - datetime.timedelta(days=offset)


def nearest_weekday_to(year, month, day, weekday):
    """The occurrence of `weekday` nearest to the fixed calendar date (year, month, day).
    Searches +/- 3 days, which always finds exactly one match since weekdays cycle
    every 7 days. Used for holidays defined as e.g. "the Sunday closest to Nov 30"."""
    anchor = datetime.date(year, month, day)
    for delta in (0, 1, -1, 2, -2, 3, -3):
        candidate = anchor + datetime.timedelta(days=delta)
        if candidate.weekday() == weekday:
            return candidate
    raise RuntimeError(f"nearest_weekday_to: no match found near {anchor}")  # unreachable


def last_weekday_on_or_before(date, weekday):
    """The most recent occurrence of `weekday` on or before `date`."""
    offset = (date.weekday() - weekday) % 7
    return date - datetime.timedelta(days=offset)


def last_weekday_before(date, weekday):
    """The most recent occurrence of `weekday` strictly before `date`."""
    return last_weekday_on_or_before(date - datetime.timedelta(days=1), weekday)


def us_election_day(year):
    """US General Election Day: the Tuesday after the first Monday in November."""
    first_monday = nth_weekday_of_month(year, 11, 0, 1)
    return first_monday + datetime.timedelta(days=1)


def easter_sunday(year):
    """Western/Gregorian Easter Sunday, via the Anonymous Gregorian algorithm
    (Computus). Deterministic — no lookup table needed, valid for any Gregorian
    year. See https://en.wikipedia.org/wiki/Date_of_Easter#Anonymous_Gregorian_algorithm"""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(year, month, day)


def next_friday_the_13th(after_date):
    """The first Friday the 13th on or after `after_date`. A calendar year can
    have zero to three of these, so — unlike every other rule here — this
    can't be computed "for a given year" and is special-cased in
    next_occurrence() instead of going through compute_floating_date()."""
    candidate = after_date
    for _ in range(400):  # generous bound; a match is always within a few months
        if candidate.day == 13 and candidate.weekday() == 4:
            return candidate
        candidate += datetime.timedelta(days=1)
    raise RuntimeError("could not find next Friday the 13th within 400 days")


def compute_floating_date(rule, year, by_slug=None, memo=None, in_progress=None):
    kind = rule["rule"]
    if kind == "nth_weekday":
        return nth_weekday_of_month(year, rule["month"], rule["weekday"], rule["n"])
    if kind == "after_labor_day_sunday":
        ld = labor_day(year)
        # first Sunday after Labor Day (Labor Day is always a Monday, so +6 days)
        return ld + datetime.timedelta(days=6)
    if kind == "lookup_table":
        table = rule["table"]
        key = str(year)  # JSON round-trips int keys as strings
        if key not in table:
            raise ValueError(
                f"a lunar/lunisolar/astronomical holiday has no confirmed date "
                f"for {year} in its lookup table — add one after checking an almanac "
                f"or authoritative calendar source, don't guess."
            )
        mm, dd = table[key].split("-")
        return datetime.date(year, int(mm), int(dd))
    if kind == "last_weekday":
        return last_weekday_of_month(year, rule["month"], rule["weekday"])
    if kind == "last_weekday_offset":
        base = last_weekday_of_month(year, rule["month"], rule["weekday"])
        return base + datetime.timedelta(days=rule["offset_days"])
    if kind == "easter_offset":
        return easter_sunday(year) + datetime.timedelta(days=rule["days"])
    if kind == "us_election_day":
        return us_election_day(year)
    if kind == "nearest_weekday_to_date":
        return nearest_weekday_to(year, rule["month"], rule["day"], rule["weekday"])
    if kind == "last_weekday_before_date":
        anchor = datetime.date(year, rule["month"], rule["day"])
        return last_weekday_before(anchor, rule["weekday"])
    if kind == "offset_from_slug":
        if by_slug is None or memo is None:
            raise ValueError("offset_from_slug rule requires by_slug/memo context")
        ref = by_slug.get(rule["slug"])
        if ref is None:
            raise ValueError(f"offset_from_slug: unknown reference slug {rule['slug']!r}")
        ref_date = holiday_date_for_year(ref, year, by_slug, memo, in_progress)
        return ref_date + datetime.timedelta(days=rule["days"])
    if kind == "last_weekday_before_slug":
        if by_slug is None or memo is None:
            raise ValueError("last_weekday_before_slug rule requires by_slug/memo context")
        ref = by_slug.get(rule["slug"])
        if ref is None:
            raise ValueError(f"last_weekday_before_slug: unknown reference slug {rule['slug']!r}")
        ref_date = holiday_date_for_year(ref, year, by_slug, memo, in_progress)
        return last_weekday_on_or_before(ref_date, rule["weekday"])
    raise ValueError(f"unknown floating rule kind: {kind}")


def holiday_date_for_year(holiday, year, by_slug, memo, in_progress=None):
    """Resolve a holiday's date for one specific calendar year (not "next
    occurrence" — an exact year). Needed because some floating rules
    (offset_from_slug, last_weekday_before_slug) are defined relative to
    another holiday in the dataset and must recursively resolve that
    holiday's date for the same year first. Memoized on (slug, year); guards
    against a rule cycle (A defined relative to B defined relative to A)."""
    slug = holiday["slug"]
    key = (slug, year)
    if key in memo:
        return memo[key]
    if in_progress is None:
        in_progress = set()
    if key in in_progress:
        raise RuntimeError(f"circular floating-rule reference involving {slug!r} for {year}")
    in_progress.add(key)
    try:
        if holiday["recurrence"] == "Annual":
            result = datetime.date(year, holiday["month"], holiday["day"])
        elif holiday["recurrence"] == "Floating":
            rule = holiday["floating_rule"]
            result = compute_floating_date(rule, year, by_slug=by_slug, memo=memo, in_progress=in_progress)
        else:
            raise ValueError(f"unknown recurrence type: {holiday['recurrence']!r} for {slug}")
    finally:
        in_progress.discard(key)
    memo[key] = result
    return result


def next_occurrence(holiday, today, by_slug=None, memo=None):
    """Return the date.date of this holiday's next occurrence on/after `today`."""
    if holiday["recurrence"] == "Annual":
        month, day = holiday["month"], holiday["day"]
        for year in (today.year, today.year + 1):
            try:
                candidate = datetime.date(year, month, day)
            except ValueError:
                continue  # e.g. Feb 29 in a non-leap year, not expected in this dataset
            if candidate >= today:
                return candidate
        # Shouldn't happen (year+1 always covers it), but fail loud rather than silent.
        raise RuntimeError(f"could not find next occurrence for {holiday['slug']}")
    elif holiday["recurrence"] == "Floating":
        rule = holiday["floating_rule"]
        if rule["rule"] == "next_friday_13":
            # Can produce 0-3 hits per calendar year, so it can't be resolved
            # "for a given year" like every other rule — scan forward directly.
            return next_friday_the_13th(today)
        if by_slug is None:
            by_slug = {}
        if memo is None:
            memo = {}
        for year in (today.year, today.year + 1):
            candidate = holiday_date_for_year(holiday, year, by_slug, memo)
            if candidate >= today:
                return candidate
        raise RuntimeError(f"could not find next floating occurrence for {holiday['slug']}")
    else:
        raise ValueError(f"unknown recurrence type: {holiday['recurrence']!r} for {holiday['slug']}")


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — {date_long} | Today Celebrates</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#ff6b45" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#ff8a63" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="article">
<meta property="og:title" content="{name} — {date_long}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{image}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Today Celebrates">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{name} — {date_long}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{image}">
<link rel="stylesheet" href="/styles/holiday.css">
<script type="application/ld+json">{ld_json}</script>
</head>
<body>
  <div class="topbar"><a href="/">Today Celebrates</a></div>
  <div class="hero" style="background-image:url('{image}')">
    <div class="hero-inner">
      <div class="hero-date">{date_long}</div>
      <h1>{name}</h1>
    </div>
  </div>
  <main>
    <span class="category-tag">{category_title}</span>
    <p class="desc">{description}</p>
    <a class="back-link" href="/">&larr; See everything else {date_short} celebrates</a>
    <div class="also">Know a holiday we're missing, or think this date has more going on? Today Celebrates tracks daily national, international, and world observances all year.</div>
  </main>
  <footer>Today Celebrates — a daily calendar of national &amp; international holidays.</footer>
</body>
</html>
"""


def esc_attr(s):
    # Matches the escaping convention already baked into the live pages
    # (BeautifulSoup's default serialization), including apostrophes as
    # &#x27; — needed so unchanged holidays regenerate byte-identical.
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;")
             .replace("'", "&#x27;"))


def render_page(holiday, occ_date):
    slug = holiday["slug"]
    name = holiday["name"]
    category = holiday["category"]
    description = holiday["description"]
    url = f"{SITE_BASE_URL}/holiday/{slug}/"
    image = f"/images/hero/{category}.jpg"
    iso_date = occ_date.isoformat()
    date_long = f"{MONTH_NAMES[occ_date.month]} {occ_date.day}, {occ_date.year}"
    date_short = f"{MONTH_NAMES[occ_date.month]} {occ_date.day}"

    ld = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": name,
        "description": description,
        "startDate": iso_date,
        "endDate": iso_date,
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
        "location": {"@type": "VirtualLocation", "url": url},
        "organizer": {"@type": "Organization", "name": "Today Celebrates", "url": f"{SITE_BASE_URL}/"},
        "image": [image],
        "url": url,
    }
    ld_json = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")

    return PAGE_TEMPLATE.format(
        name=esc_attr(name),
        date_long=date_long,
        date_short=date_short,
        description=esc_attr(description),
        url=url,
        image=image,
        category_title=category.capitalize() if category != "lgbt" else category.upper(),
        ld_json=ld_json,
    )


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

def generate(holidays, today, site_dir, dry_run=False):
    """Returns a report dict describing what changed."""
    by_slug = {h["slug"]: h for h in holidays}
    memo = {}  # (slug, year) -> date.date, shared across all holidays this run
    occurrences = {}  # slug -> date.date
    for h in holidays:
        occurrences[h["slug"]] = next_occurrence(h, today, by_slug, memo)

    # ---- month data files: only for months that actually have content ----
    by_month = {}  # "YYYY-MM" -> { "YYYY-M-D": [(order, name), ...] }
    for h in holidays:
        occ = occurrences[h["slug"]]
        mk = f"{occ.year:04d}-{occ.month:02d}"
        dk = f"{occ.year}-{occ.month}-{occ.day}"
        # Preserve each holiday's original display position within its day
        # (captured from the live site at Phase 3 build time) rather than
        # re-sorting alphabetically, so unaffected days stay byte-identical
        # and the deliberate Notion ordering survives regeneration.
        by_month.setdefault(mk, {}).setdefault(dk, []).append(
            (h.get("display_order", 999), h["name"])
        )

    for mk, days in by_month.items():
        for dk in days:
            days[dk].sort(key=lambda pair: pair[0])
            days[dk] = [name for _, name in days[dk]]

    data_dir = os.path.join(site_dir, "data")
    existing_month_files = set()
    if os.path.isdir(data_dir):
        existing_month_files = {f[:-5] for f in os.listdir(data_dir) if f.endswith(".json")}

    month_diffs = {}
    for mk, days in sorted(by_month.items()):
        path = os.path.join(data_dir, f"{mk}.json")
        new_content = json.dumps(days, ensure_ascii=False, separators=(",", ":"))
        old_content = None
        if os.path.exists(path):
            old_content = open(path, encoding="utf-8").read()
        if old_content != new_content:
            month_diffs[mk] = {"old_days": len(json.loads(old_content)) if old_content else 0,
                                "new_days": len(days)}
        if not dry_run:
            os.makedirs(data_dir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

    stale_month_files = existing_month_files - set(by_month.keys())

    # ---- per-holiday pages ----
    page_diffs = {"changed": [], "unchanged": [], "created": []}
    for h in holidays:
        slug = h["slug"]
        occ = occurrences[slug]
        new_html = render_page(h, occ)
        page_dir = os.path.join(site_dir, "holiday", slug)
        page_path = os.path.join(page_dir, "index.html")
        old_html = None
        if os.path.exists(page_path):
            old_html = open(page_path, encoding="utf-8").read()
        if old_html is None:
            page_diffs["created"].append(slug)
        elif old_html != new_html:
            page_diffs["changed"].append(slug)
        else:
            page_diffs["unchanged"].append(slug)
        if not dry_run:
            os.makedirs(page_dir, exist_ok=True)
            with open(page_path, "w", encoding="utf-8") as f:
                f.write(new_html)

    # ---- sitemap.xml ----
    today_iso = today.isoformat()
    urls = [f'  <url><loc>{SITE_BASE_URL}/</loc><lastmod>{today_iso}</lastmod></url>']
    for h in sorted(holidays, key=lambda h: h["slug"]):
        urls.append(
            f'  <url><loc>{SITE_BASE_URL}/holiday/{h["slug"]}/</loc><lastmod>{today_iso}</lastmod></url>'
        )
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(urls) + "\n</urlset>\n")
    sitemap_path = os.path.join(site_dir, "sitemap.xml")
    old_sitemap = open(sitemap_path, encoding="utf-8").read() if os.path.exists(sitemap_path) else None
    sitemap_changed = old_sitemap != sitemap
    if not dry_run:
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(sitemap)

    return {
        "today": today_iso,
        "months_covered": sorted(by_month.keys()),
        "month_diffs": month_diffs,
        "stale_month_files": sorted(stale_month_files),
        "pages_created": sorted(page_diffs["created"]),
        "pages_changed": sorted(page_diffs["changed"]),
        "pages_unchanged_count": len(page_diffs["unchanged"]),
        "sitemap_changed": sitemap_changed,
        "occurrences": {slug: d.isoformat() for slug, d in occurrences.items()},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--holidays", required=True, help="path to holidays.json")
    ap.add_argument("--site", required=True, help="path to the site's public/ directory")
    ap.add_argument("--today", required=True, help="YYYY-MM-DD, the generation run's 'today'")
    ap.add_argument("--dry-run", action="store_true", help="compute + report only, write nothing")
    ap.add_argument("--report", help="optional path to write the JSON report to")
    args = ap.parse_args()

    holidays = json.load(open(args.holidays, encoding="utf-8"))
    today = datetime.date.fromisoformat(args.today)

    report = generate(holidays, today, args.site, dry_run=args.dry_run)

    print(json.dumps(
        {k: v for k, v in report.items() if k != "occurrences"},
        indent=2, ensure_ascii=False
    ))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
