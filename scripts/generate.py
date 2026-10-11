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

Long-form content (E1): when a holiday row carries body / timeline / faq /
sources text from Notion, the page additionally renders those sections, a
five-year dates table computed from the rule engine, and FAQPage JSON-LD.
A row without those fields renders byte-identically to the pre-E1 page.
See render_longform() for the Markdown subset those fields use.

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
from urllib.parse import quote

MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
MONTH_ABBR = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                 "Saturday", "Sunday"]

SITE_BASE_URL = "https://todaycelebrates.com"

# First date to publish a /day/YYYY-MM-DD/ page for.
#
# Day pages are permanent URLs, so this is the archive's start line. Do not move
# it backwards casually: lowering it backfills dated pages for dates the site
# never actually covered, which is a deliberate content decision (and a
# near-duplicate-content risk), not a tweak. Moving it forward would orphan
# pages that are already published and indexed.
DAY_ARCHIVE_START = datetime.date(2026, 10, 8)

# Perennial date pages (E3): /<month>-<day>/, e.g. /october-8/ -- one page per
# calendar date with no year in the URL. Three of the four leading competitors
# have this URL and we did not; it is the page that answers the recurring
# query ("what is celebrated on October 8") rather than one year's version of
# it.
#
# PERENNIAL_YEARS is how many calendar years, starting with the current one,
# are examined to work out which rule-dated ("Floating") observances can land
# on a given month-day. It only affects the "lands here in some years" note:
# the fixed-date list is year-independent. Ten years is enough for the weekday
# rules to cycle; the lookup-table rules simply contribute the years they have
# (see "FLOATING_RULES -- which ones expire" in scripts/README.md).
PERENNIAL_YEARS = 10

# Whether to publish a page for a month-day that has nothing on it at all.
# 26 month-days have no fixed-date observance and 8 have nothing in a ten-year
# window (Jan 3, Jan 6, Jan 12, May 2, Jun 3, Jun 11, Jul 10, Aug 31 as of
# 2026-10-11). True publishes all 366 so no date in the year 404s and the URL
# stays guessable; False publishes only the dates that have something, and the
# prev/next chain and the rail skip the rest. Flipping this is a content call,
# not a code change.
PERENNIAL_EMPTY_PAGES = True

# "Born on this day": two sub-blocks per date -- historic figures and living
# celebrities/public figures -- read from scripts/people.json. That file is a
# committed data file built by scripts/build_people.py (run by hand, about
# monthly); this script never touches the network for it, so the daily workflow
# is unaffected. If the file is missing the blocks simply do not render and
# every page is byte-identical to a build without the feature.
#
# The full lists live on the perennial /<month>-<day>/ pages, which is where
# they compound. The dated /day/ pages carry a short version that links to the
# full one, so a date does not repeat the same twenty names on every year's page.
DEFAULT_PEOPLE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "people.json"
)
PEOPLE_PERENNIAL_LIMIT = 10  # names per sub-block on /october-10/
PEOPLE_DAY_LIMIT = 4         # names per sub-block on /day/2026-10-10/
# The living lists age: someone on them can die, and a page that lists a dead
# person as a living celebrity is a credibility problem. main() warns once the
# file is older than this, and the fix is to re-run scripts/build_people.py.
PEOPLE_STALE_DAYS = 45

DEFAULT_TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates"
)

# Ad slots on/off, and whether to label them.
#
# These are baked into the <html> class at build time rather than set by
# JavaScript on load, and that is the whole point: a deferred script adding the
# class after first paint makes every slot appear at once and shoves the page
# down, which is a measurable layout shift (0.09 CLS when it was done that way).
# Static class, no shift.
#
# ADS_ENABLED False removes all ad space from the site. It must agree with
# public/ads/house.js: this flag reserves the space, that file fills it.
ADS_ENABLED = True
ADS_LABELLED = False  # set True once real paid creative runs, not placeholders


def html_class():
    classes = []
    if ADS_ENABLED:
        classes.append("ads-enabled")
        if ADS_LABELLED:
            classes.append("ads-labelled")
    return " ".join(classes)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

GENERATED_NOTE = (
    "<!-- Generated by scripts/generate.py from scripts/templates/index.html. "
    "Do not edit this file directly; your changes will be overwritten on the "
    "next run. -->"
)


def load_template(templates_dir, name):
    with open(os.path.join(templates_dir, name), encoding="utf-8") as f:
        return f.read()


def fill(template, values):
    """Replace every <!--TC:KEY--> marker in a template with its value.

    Marker substitution rather than str.format() on purpose: these templates are
    full of CSS and JS braces, and having to escape every one of them would be a
    reliable source of bugs (PAGE_TEMPLATE below does use .format(), which is
    exactly why its inline script needs doubled braces). Unfilled markers raise
    rather than shipping a visible HTML comment to the live site.
    """
    out = template
    for key, value in values.items():
        out = out.replace(f"<!--TC:{key}-->", value)
    # <!--TC-ONLY ... --> blocks are notes to whoever edits the template. Strip
    # them: they're maintainer context, not page content, and shipping them
    # would publish "edit this other file instead" to every visitor's view-source.
    out = re.sub(r"<!--TC-ONLY\b.*?-->\n?", "", out, flags=re.S)
    leftover = sorted(set(re.findall(r"<!--TC:([A-Z_0-9]+)-->", out)))
    if leftover:
        raise ValueError(f"template left unfilled markers: {leftover}")
    return out


# ---------------------------------------------------------------------------
# Date formatting (kept in one place so the baked homepage markup matches what
# index.html's own JS produces when it re-renders the same day)
# ---------------------------------------------------------------------------

def long_date(d):
    return f"{MONTH_NAMES[d.month]} {d.day}, {d.year}"


def month_day(d):
    return f"{MONTH_NAMES[d.month]} {d.day}"


def weekday_long_date(d):
    return f"{WEEKDAY_NAMES[d.weekday()]}, {MONTH_NAMES[d.month]} {d.day}, {d.year}"


def weekday_month_day(d):
    # Matches toLocaleDateString(undefined, {weekday:'long', month:'long', day:'numeric'})
    return f"{WEEKDAY_NAMES[d.weekday()]}, {MONTH_NAMES[d.month]} {d.day}"


def short_badge_date(d):
    # Matches toLocaleDateString(undefined, {month:'short', day:'numeric', year:'numeric'})
    return f"{MONTH_ABBR[d.month]} {d.day}, {d.year}"


def day_path(d):
    return f"/day/{d.isoformat()}/"


def perennial_path(month, day):
    """/october-8/ -- the year-less page for one calendar date.

    Unpadded day on purpose: it is the form the competing sites use and the
    form a person types.
    """
    return f"/{MONTH_NAMES[month].lower()}-{day}/"


def month_day_label(month, day):
    return f"{MONTH_NAMES[month]} {day}"


def all_month_days():
    """Every (month, day) in the calendar year, February 29 included: 366.

    Derived from a leap year so the list is the same on every run -- the
    perennial pages are permanent URLs and February 29 is a real date that
    needs one even in a non-leap year.
    """
    out = []
    for m in range(1, 13):
        for d in range(1, calendar.monthrange(2024, m)[1] + 1):
            out.append((m, d))
    return out


def next_md_occurrence(month, day, today):
    """The next date this month-day falls on, on or after `today`.

    Nine years of scan for the same reason next_occurrence() uses nine: it has
    to reach the next leap year from any starting point (February 29 can be
    eight years away across a non-leap century year). Returns None if it
    cannot, which no real date does.
    """
    for year in range(today.year, today.year + 9):
        try:
            cand = datetime.date(year, month, day)
        except ValueError:
            continue
        if cand >= today:
            return cand
    return None


def js_day_key(d):
    # index.html's own key() format: unpadded, e.g. "2026-10-9"
    return f"{d.year}-{d.month}-{d.day}"


def plural(n, singular, plural_form=None):
    return singular if n == 1 else (plural_form or singular + "s")


def join_names(names):
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f" and {names[-1]}"


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
    # The longest gap between two Friday the 13ths is 14 months -- 427 days,
    # the 1900-07-13 -> 1901-09-13 shape, which recurs (2027-08-13 ->
    # 2028-10-13 is the next one). The bound here was 400, which is shorter
    # than that: any run between 2027-08-14 and 2028-10-13 would have raised,
    # and friday-the-13th would have dropped out of the calendar with a
    # WARNING for fourteen months. 460 clears the real maximum with room to
    # spare and still fails loud rather than looping forever.
    for _ in range(460):
        if candidate.day == 13 and candidate.weekday() == 4:
            return candidate
        candidate += datetime.timedelta(days=1)
    raise RuntimeError("could not find next Friday the 13th within 460 days")


def compute_floating_date(rule, year, by_slug=None, memo=None, in_progress=None):
    kind = rule["rule"]
    if kind == "nth_weekday":
        return nth_weekday_of_month(year, rule["month"], rule["weekday"], rule["n"])
    if kind == "nth_weekday_offset":
        # Nth given weekday of a month, then a signed day offset. The mirror of
        # last_weekday_offset, and what "weekday of the first full week" needs:
        # the first full (Sun-Sat) week of a month begins on its first Sunday,
        # so Tuesday of that week is 1st Sunday + 2. The offset may cross a
        # month or year boundary on purpose (Oktoberfest opens 15 days before
        # the first Sunday in October, which always lands in September).
        base = nth_weekday_of_month(year, rule["month"], rule["weekday"], rule["n"])
        return base + datetime.timedelta(days=rule["offset_days"])
    if kind == "after_labor_day_sunday":
        ld = labor_day(year)
        # first Sunday after Labor Day (Labor Day is always a Monday, so +6 days)
        return ld + datetime.timedelta(days=6)
    if kind == "lookup_table":
        table = rule["table"]
        key = str(year)  # JSON round-trips int keys as strings
        if key not in table:
            raise ValueError(
                f"lookup_table has no hand-confirmed date for {year} (it covers "
                f"{min(table)}-{max(table)}) — add the year after checking an almanac "
                f"or the organizing body, don't guess or extrapolate."
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
        # Nine years, not two. Two is enough for every date that exists every
        # year, but Feb 29 exists only in leap years: scanning only this year
        # and next would raise for Leap Day in three years out of four, which
        # main() catches as "unresolved" -- so the page would simply never be
        # built. Nine covers the widest real gap between leap years (eight,
        # across a non-leap century year such as 2100).
        for year in range(today.year, today.year + 9):
            try:
                candidate = datetime.date(year, month, day)
            except ValueError:
                continue  # Feb 29 in a non-leap year: that year has none
            if candidate >= today:
                return candidate
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
        last_error = None
        for year in (today.year, today.year + 1):
            try:
                candidate = holiday_date_for_year(holiday, year, by_slug, memo)
            except (ValueError, KeyError) as e:
                # One unresolvable year must not hide a resolvable later one.
                # A lookup_table whose first hand-confirmed year is *next* year
                # -- which is what a newly added holiday looks like for the rest
                # of the current year -- raised here and the holiday was
                # reported as having no date at all, so no page was built for a
                # date we actually know. Skip that year and try the next one.
                # If no year resolves (the expired-table case) the error is
                # re-raised below, so an expired table still fails loudly.
                last_error = e
                continue
            if candidate >= today:
                return candidate
        if last_error is not None:
            raise last_error
        raise RuntimeError(f"could not find next floating occurrence for {holiday['slug']}")
    else:
        raise ValueError(f"unknown recurrence type: {holiday['recurrence']!r} for {holiday['slug']}")


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Site chrome and shared markup (the "Almanac" design)
#
# The <head> boilerplate, header, footer and script tags live as partials under
# scripts/templates/partials/. They are filled here and handed to every page
# template as ordinary markers (HEAD_COMMON, SITE_HEADER, SITE_FOOTER,
# SITE_SCRIPTS), so changing the navigation is a one-file edit.
#
# obs_row() and calendar_html() produce markup that the home page's inline
# script ALSO produces when a visitor picks another day or month. The two have
# to stay identical -- see the note at the top of templates/index.html.
# ---------------------------------------------------------------------------

# Category key -> (display title, pill colour class). The pill classes are
# defined in public/styles/site.css (lil / sun / cor / mnt). Unknown categories
# fall back to a capitalised title and the lilac pill.
CATEGORY_STYLE = {
    "celebration": ("Celebration", "lil"),
    "community": ("Community", "lil"),
    "kids": ("Kids & Family", "lil"),
    "music": ("Music", "lil"),
    "food": ("Food", "sun"),
    "coffee": ("Coffee", "sun"),
    "books": ("Books", "sun"),
    "beer": ("Beer", "cor"),
    "halloween": ("Halloween", "cor"),
    "sports": ("Sports", "cor"),
    "dog": ("Dogs", "cor"),
    "health": ("Health", "mnt"),
    "nature": ("Nature", "mnt"),
    "tech": ("Tech", "mnt"),
}

NAV_KEYS = ("TODAY", "CALENDAR", "CATEGORIES", "ABOUT")
_partial_cache = {}


def cat_title(category):
    if category in CATEGORY_STYLE:
        return CATEGORY_STYLE[category][0]
    return category.upper() if category == "lgbt" else category.capitalize()


def cat_pill_class(category):
    return CATEGORY_STYLE.get(category, ("", "lil"))[1]


def cat_pill(category, link=False):
    title = esc_attr(cat_title(category))
    cls = cat_pill_class(category)
    if link:
        return f'<a class="pill {cls}" href="/category/{category}/">{title}</a>'
    return f'<span class="pill {cls}">{title}</span>'


def category_json():
    """CATEGORY_STYLE for the home page's inline script (one source of truth)."""
    return json.dumps(
        {k: [v[0], v[1]] for k, v in CATEGORY_STYLE.items()},
        ensure_ascii=False, separators=(",", ":"),
    )


def load_partial(templates_dir, name):
    key = (templates_dir, name)
    if key not in _partial_cache:
        _partial_cache[key] = load_template(os.path.join(templates_dir, "partials"), name)
    return _partial_cache[key]


def chrome_for(templates_dir, active=None):
    """Shared page furniture as template-marker values.

    `active` names the nav tab to mark current (one of NAV_KEYS), or None for
    pages that belong to no tab (an individual holiday page, say). Nothing in
    here depends on today's date, which is what keeps the permanent /day/ pages
    byte-identical from run to run.
    """
    if active is not None and active not in NAV_KEYS:
        raise ValueError(f"unknown nav tab {active!r}")
    nav = {
        f"NAV_{k}": (' aria-current="page"' if k == active else "") for k in NAV_KEYS
    }
    header = fill(load_partial(templates_dir, "header.html"), {
        "ICONS": load_partial(templates_dir, "icons.html").rstrip("\n"),
        **nav,
    })
    return {
        "HEAD_COMMON": load_partial(templates_dir, "head.html").rstrip("\n"),
        "SITE_HEADER": header.rstrip("\n"),
        "SITE_FOOTER": load_partial(templates_dir, "footer.html").rstrip("\n"),
        "SITE_SCRIPTS": load_partial(templates_dir, "scripts.html").rstrip("\n"),
    }


def icon(name, size=17):
    return f'<svg width="{size}" height="{size}" aria-hidden="true"><use href="#i-{name}"/></svg>'


def row_button(action, label, icon_name, extra=""):
    return (
        f'<button type="button" class="ib{extra}" data-a="{action}" '
        f'aria-label="{esc_attr(label)}">{icon(icon_name)}</button>'
    )


def obs_row(h, index, iso_date):
    """One observance as a table row: number, name, category pill, actions.

    `index` is 0-based; the first row of a day is the leading celebration.
    The data-* attributes are what /js/site.js reads for Share, Copy link and
    Add to calendar, so no per-row script or URL-building is needed.
    """
    name, slug = h["name"], h["slug"]
    yearly = "1" if h["recurrence"] == "Annual" else "0"
    hot = ' class="hot"' if index == 0 else ""
    lead = '<span class="lbl">Lead</span>' if index == 0 else ""
    actions = (
        row_button("copy", f"Copy link to {name}", "link")
        + row_button("ics", f"Add {name} to calendar", "cal")
        + row_button("share", f"Share {name}", "share", " sh")
    )
    return (
        f'<tr data-u="/holiday/{slug}/" data-n="{esc_attr(name)}" data-d="{iso_date}" '
        f'data-y="{yearly}"{hot}>'
        f'<td class="n mono">{index + 1:02d}</td>'
        f'<td class="nm"><a href="/holiday/{slug}/">{esc_attr(name)}</a>{lead}</td>'
        f'<td class="cat">{cat_pill(h["category"])}</td>'
        f'<td class="act">{actions}</td></tr>'
    )


OBS_THEAD = (
    '<thead><tr><th scope="col">#</th><th scope="col">Observance</th>'
    '<th scope="col">Category</th><th scope="col"><span class="sr">Actions</span></th>'
    '</tr></thead>'
)


def share_links(path, text):
    """Plain-<a> share intents: they work with JavaScript off."""
    full = SITE_BASE_URL + path
    u = quote(full, safe="")
    t = quote(text, safe="")
    both = quote(f"{text} {full}", safe="")
    ext = 'target="_blank" rel="noopener noreferrer"'
    return (
        f'<a href="mailto:?subject={t}&amp;body={both}" aria-label="Share by email">Email</a>'
        f'<a href="sms:?&amp;body={both}" aria-label="Share by text message">Text</a>'
        f'<a href="https://www.facebook.com/sharer/sharer.php?u={u}" {ext} '
        f'aria-label="Share on Facebook (opens in a new tab)">Facebook</a>'
        f'<a href="https://twitter.com/intent/tweet?text={t}&amp;url={u}" {ext} '
        f'aria-label="Share on X (opens in a new tab)">X</a>'
        f'<a href="https://wa.me/?text={both}" {ext} '
        f'aria-label="Share on WhatsApp (opens in a new tab)">WhatsApp</a>'
    )


def day_text(date, is_today):
    sep = " " if is_today else ", "
    return f"{WEEKDAY_NAMES[date.weekday()]}{sep}{MONTH_NAMES[date.month]} {date.day}"


def calendar_html(year, month, today, selected, has_days):
    """The month grid for the home page's calendar box (Sunday-first)."""
    first = (datetime.date(year, month, 1).weekday() + 1) % 7
    ndays = calendar.monthrange(year, month)[1]
    out = "".join(f'<span class="w">{w}</span>' for w in "SMTWTFS")
    out += "<span></span>" * first
    for d in range(1, ndays + 1):
        dt = datetime.date(year, month, d)
        cls = "d" + (" has" if d in has_days else "")
        cls += " t" if dt == today else ""
        cls += " sel" if dt == selected else ""
        pressed = ' aria-pressed="true"' if dt == selected else ""
        current = ' aria-current="date"' if dt == today else ""
        out += (
            f'<button type="button" class="{cls}" data-k="{year}-{month}-{d}" '
            f'aria-label="{MONTH_NAMES[month]} {d}"{pressed}{current}>{d}</button>'
        )
    return out


def month_jump_html(current_month):
    parts = []
    for m in range(1, 13):
        cls = ' class="t"' if m == current_month else ""
        parts.append(f'<button type="button"{cls}>{MONTH_ABBR[m]}</button>')
    return "".join(parts)


def coming_up_html(today, day_index, limit=4, horizon=45):
    """The leading observance of each of the next few days that have one."""
    rows = []
    for offset in range(1, horizon + 1):
        d = today + datetime.timedelta(days=offset)
        items = day_index.get(d)
        if not items:
            continue
        h = items[0]
        when = "Tomorrow" if offset == 1 else f"In {offset} days"
        rows.append(
            f'<a href="/holiday/{h["slug"]}/"><span class="d mono">'
            f'{MONTH_ABBR[d.month]} {d.day}</span><span><b>{esc_attr(h["name"])}</b>'
            f'<small>{when}</small></span></a>'
        )
        if len(rows) == limit:
            break
    return "".join(rows)


def also_on_html(date, items, exclude_slug, day_published):
    """Sidebar of the other observances on a holiday's date."""
    others = [(i, h) for i, h in enumerate(items, 1) if h["slug"] != exclude_slug]
    if not others:
        return ""
    lis = "".join(
        f'<li><a href="/holiday/{h["slug"]}/"><span>{esc_attr(h["name"])}</span>'
        f'<span class="mono">{i:02d}</span></a></li>'
        for i, h in others[:10]
    )
    more = ""
    if day_published:
        more = (
            f'<p><a class="back-link" href="{day_path(date)}">'
            f'All {len(items)} on {esc_attr(month_day(date))} &rarr;</a></p>'
        )
    return f'<h2>Also on {esc_attr(month_day(date))}</h2><ul class="list-side">{lis}</ul>{more}'


def category_side_html(category_counts, current=None):
    lis = []
    for c, n in sorted(category_counts.items(), key=lambda kv: cat_title(kv[0])):
        here = ' aria-current="page"' if c == current else ""
        lis.append(
            f'<li><a href="/category/{c}/"{here}><span>{esc_attr(cat_title(c))}</span>'
            f'<span class="mono">{n}</span></a></li>'
        )
    return f'<h2>Categories</h2><ul class="list-side">{"".join(lis)}</ul>'


def write_if_changed(path, content, dry_run=False):
    """Write `content` to `path`; returns (changed, created)."""
    old = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = f.read()
    changed = old != content
    if changed and not dry_run:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return changed, old is None


def esc_attr(s):
    # Matches the escaping convention already baked into the live pages
    # (BeautifulSoup's default serialization), including apostrophes as
    # &#x27; — needed so unchanged holidays regenerate byte-identical.
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;")
             .replace("'", "&#x27;"))


def esc_text(s):
    """Escaping for text nodes: the three characters that must not appear raw.

    Deliberately narrower than esc_attr() -- apostrophes and quotes are legal
    in text content, and prose is full of them, so escaping them here would
    fill every long-form page's source with &#x27;. esc_attr() is still used
    for anything that lands inside an attribute.
    """
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def esc_href(url):
    """esc_text has already run on the URL, so only the quote characters that
    would break out of the attribute are left to handle."""
    return url.replace('"', "&quot;").replace("'", "&#x27;")


# ---------------------------------------------------------------------------
# Long-form content (E1)
#
# The Notion long-form fields (Body, Timeline, FAQ, Sources) hold plain text in
# a deliberately tiny Markdown subset -- NOT general Markdown, and not HTML:
#
#   ### Heading          section heading inside Body (rendered as <h2>: the
#                        page's <h1> is the holiday name in the hero)
#   blank line           paragraph break; single newlines are soft wraps
#   - item               list item
#   **bold**  *italic*   inline emphasis
#   [text](https://...)  link
#
# Everything is HTML-escaped before those five patterns are applied, so any
# other markup in a Notion field ships as literal text rather than as live
# HTML. Anything outside the subset is left alone rather than guessed at.
#
# A holiday with none of these fields populated renders exactly the page it
# rendered before E1 -- byte for byte. That is the property the regression
# check in docs/REVIEW.md verifies, and it is why every piece of this block
# returns "" when its field is absent.
# ---------------------------------------------------------------------------

MD_LINK_RE = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+)\)")
MD_BARE_URL_RE = re.compile(r'(?<![">=\w/])(https?://[^\s<"]+?)(?=[.,;:!?)]*(?:\s|<|$))')
MD_BOLD_RE = re.compile(r"\*\*([^*\n]+)\*\*")
MD_ITALIC_RE = re.compile(r"(?<![*\w])\*([^*\n]+)\*(?!\w)")


def md_inline(text):
    """Links, bold, italics. Escapes first; links before emphasis so that
    emphasis inside a link label still works and a URL's own characters
    cannot be mistaken for emphasis markers."""
    out = esc_text(text)
    out = MD_LINK_RE.sub(
        lambda m: f'<a href="{esc_href(m.group(2))}">{m.group(1)}</a>', out
    )
    # A bare URL (Notion often hands these over unwrapped) becomes a link too.
    out = MD_BARE_URL_RE.sub(lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>', out)
    out = MD_BOLD_RE.sub(r"<strong>\1</strong>", out)
    out = MD_ITALIC_RE.sub(r"<em>\1</em>", out)
    return out


def strip_md(text):
    """Same subset, flattened to plain text -- for JSON-LD values, where
    markup is noise at best and invalid at worst."""
    out = MD_LINK_RE.sub(r"\1", text)
    out = MD_BOLD_RE.sub(r"\1", out)
    out = MD_ITALIC_RE.sub(r"\1", out)
    return out.strip()


def md_blocks(text):
    """Parse the subset into a list of ('h2'|'p'|'ul', payload) blocks."""
    blocks = []
    para = []
    items = []

    def flush_para():
        if para:
            blocks.append(("p", " ".join(para)))
            para.clear()

    def flush_items():
        if items:
            blocks.append(("ul", list(items)))
            items.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush_para()
            flush_items()
            continue
        if line.startswith("###"):
            flush_para()
            flush_items()
            blocks.append(("h2", line.lstrip("#").strip()))
            continue
        if line.startswith("- "):
            flush_para()
            items.append(line[2:].strip())
            continue
        if items and raw[:1].isspace():
            # An indented line under a bullet continues that bullet.
            items[-1] += " " + line
            continue
        flush_items()
        para.append(line)
    flush_para()
    flush_items()
    return blocks


def render_md_blocks(blocks, indent="      "):
    out = []
    for kind, payload in blocks:
        if kind == "h2":
            out.append(f"{indent}<h2>{md_inline(payload)}</h2>")
        elif kind == "p":
            out.append(f"{indent}<p>{md_inline(payload)}</p>")
        elif kind == "ul":
            out.append(f"{indent}<ul>")
            for item in payload:
                out.append(f"{indent}  <li>{md_inline(item)}</li>")
            out.append(f"{indent}</ul>")
    return out


def split_body_sections(body):
    """Body into [(heading_or_None, [blocks])], split at each ### heading."""
    sections = []
    current = (None, [])
    for kind, payload in md_blocks(body):
        if kind == "h2":
            if current[1] or current[0] is not None:
                sections.append(current)
            current = (payload, [])
        else:
            current[1].append((kind, payload))
    if current[1] or current[0] is not None:
        sections.append(current)
    return sections


def parse_faq(text):
    """[(question, answer)] from Question / answer line pairs.

    A question is either a fully **bolded** line or the first line of a block
    that ends in a question mark. Everything up to the next question is its
    answer. A stray answer with no question above it is dropped rather than
    rendered headless.

    The unbolded form is not a convenience -- it is the only form that
    actually arrives. The field convention says to bold the question, but
    Notion stores that bold as a rich-text *annotation*, and
    export_from_notion.py reads `plain_text`, which drops annotations: the
    asterisks never survive the round trip. Keying on asterisks alone meant
    every FAQ written so far parsed to zero pairs, so the FAQ section and its
    FAQPage structured data silently vanished from the finished page -- on
    Halloween and Thanksgiving Day among others. Blank-line separation
    between pairs is what the field convention already requires, so a
    question is exactly the line that opens a block.
    """
    pairs = []
    question = None
    answer = []
    at_block_start = True
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            at_block_start = True
            continue
        bold_only = re.fullmatch(r"\*\*(.+)\*\*", line)
        is_question = bool(bold_only) or (at_block_start and line.endswith("?"))
        at_block_start = False
        if is_question:
            if question:
                pairs.append((question, " ".join(answer).strip()))
            question = (bold_only.group(1) if bold_only else line).strip()
            answer = []
        else:
            answer.append(line)
    if question:
        pairs.append((question, " ".join(answer).strip()))
    return [(q, a) for q, a in pairs if a]


def next_five_occurrences(holiday, occ_date, by_slug, memo, count=5):
    """This holiday's next `count` dates, starting with the one on the page.

    Never raises: a rule that runs out of resolvable years (a lookup_table
    past its last hand-confirmed year, say) just yields a shorter table. A
    short table is honest; a guessed sixth row is not.
    """
    dates = [occ_date]
    rule = (holiday.get("floating_rule") or {}).get("rule")

    if rule == "next_friday_13":
        # Not resolvable per-year: 0-3 per calendar year. Scan forward.
        cursor = occ_date
        while len(dates) < count:
            cursor = next_friday_the_13th(cursor + datetime.timedelta(days=1))
            dates.append(cursor)
        return dates

    year = occ_date.year + 1
    # Generous ceiling: Feb 29 only lands every fourth year, so five rows of
    # Leap Day need a 17-year reach.
    horizon = occ_date.year + 40
    while len(dates) < count and year <= horizon:
        if holiday["recurrence"] == "Annual":
            try:
                dates.append(datetime.date(year, holiday["month"], holiday["day"]))
            except ValueError:
                pass  # Feb 29 in a non-leap year: that year simply has none
        else:
            try:
                d = holiday_date_for_year(holiday, year, by_slug, memo)
            except (ValueError, RuntimeError, KeyError):
                break
            if d not in dates:
                dates.append(d)
        year += 1
    return dates


def render_longform(holiday, occ_date, by_slug, memo):
    """Returns (html, faq_pairs). ("", []) when the row has no long-form
    content, which is what keeps pre-E1 pages byte-identical."""
    body = (holiday.get("body") or "").strip()
    timeline = (holiday.get("timeline") or "").strip()
    faq_text = (holiday.get("faq") or "").strip()
    sources = (holiday.get("sources") or "").strip()

    if not (body or timeline or faq_text):
        return "", []

    name = holiday["name"]
    out = ['    <div class="longform">']

    # One "- " bullet per entry, but an entry may be hard-wrapped across lines:
    # any non-bullet line after a bullet continues it rather than being dropped.
    timeline_items = []
    for raw in (timeline.splitlines() if timeline else []):
        line = raw.strip()
        if line.startswith("- "):
            timeline_items.append(line[2:].strip())
        elif line and timeline_items:
            timeline_items[-1] += " " + line

    def timeline_html():
        if not timeline_items:
            return []
        rows = ['      <section class="tc-timeline">', "        <h2>Timeline</h2>",
                "        <ul>"]
        for item in timeline_items:
            rows.append(f"          <li>{md_inline(item)}</li>")
        rows += ["        </ul>", "      </section>"]
        return rows

    # Body sections in their authored order, with the Timeline slotted in
    # ahead of "How to observe" -- the order docs/EXECUTION_PLAN.md section 4
    # specifies and docs/CONTENT_EXEMPLAR.md shows. If Body has no such
    # heading the Timeline goes after the body instead.
    timeline_done = False
    for heading, blocks in split_body_sections(body):
        if (heading or "").lower().startswith("how to observe") and not timeline_done:
            out += timeline_html()
            timeline_done = True
        out.append('      <section class="tc-body">')
        if heading:
            out.append(f"        <h2>{md_inline(heading)}</h2>")
        out += render_md_blocks(blocks, indent="        ")
        out.append("      </section>")
    if not timeline_done:
        out += timeline_html()

    faq_pairs = parse_faq(faq_text) if faq_text else []
    if faq_pairs:
        out.append('      <section class="tc-faq">')
        out.append("        <h2>Frequently asked questions</h2>")
        for question, answer in faq_pairs:
            out.append('        <div class="faq-item">')
            out.append(f"          <h3>{md_inline(question)}</h3>")
            out.append(f"          <p>{md_inline(answer)}</p>")
            out.append("        </div>")
        out.append("      </section>")

    # Dates table, straight off the rule engine -- never typed by hand.
    dates = next_five_occurrences(holiday, occ_date, by_slug, memo)
    out.append('      <section class="tc-dates">')
    out.append(f"        <h2>When is {md_inline(name)}?</h2>")
    out.append('        <table class="dates">')
    out.append("          <thead><tr><th>Year</th><th>Date</th><th>Day</th></tr></thead>")
    out.append("          <tbody>")
    for n, d in enumerate(dates):
        now_cls = ' class="now"' if n == 0 else ""
        out.append(
            f"            <tr{now_cls}><td>{d.year}</td>"
            f"<td>{MONTH_NAMES[d.month]} {d.day}</td>"
            f"<td>{WEEKDAY_NAMES[d.weekday()]}</td></tr>"
        )
    out.append("          </tbody>")
    out.append("        </table>")
    out.append("      </section>")

    if sources:
        out.append('      <section class="tc-sources">')
        out.append("        <h2>Sources</h2>")
        out += render_md_blocks(md_blocks(sources), indent="        ")
        out.append("      </section>")

    out.append("    </div>")
    return "\n" + "\n".join(out), faq_pairs


def faq_ld_json(faq_pairs):
    """FAQPage structured data, as its own script block so that a page without
    an FAQ keeps the exact Event-only markup it had before E1."""
    if not faq_pairs:
        return ""
    ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": strip_md(question),
                "acceptedAnswer": {"@type": "Answer", "text": strip_md(answer)},
            }
            for question, answer in faq_pairs
        ],
    }
    payload = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    return f'\n<script type="application/ld+json">{payload}</script>'


def render_page(holiday, occ_date, day_link, by_slug, memo, template, chrome,
                same_day=(), day_published=False):
    """Render one /holiday/<slug>/ page.

    `same_day` is every observance on this holiday's date (for the "Also on"
    sidebar); `day_published` says whether that date has a /day/ page to link.
    """
    slug = holiday["slug"]
    name = holiday["name"]
    category = holiday["category"]
    description = holiday["description"]
    path = f"/holiday/{slug}/"
    url = f"{SITE_BASE_URL}{path}"
    image = f"{SITE_BASE_URL}/images/hero/{category}.jpg"
    iso_date = occ_date.isoformat()
    date_long = f"{MONTH_NAMES[occ_date.month]} {occ_date.day}, {occ_date.year}"
    date_short = f"{MONTH_NAMES[occ_date.month]} {occ_date.day}"
    annual = holiday["recurrence"] == "Annual"

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

    longform, faq_pairs = render_longform(
        holiday, occ_date,
        by_slug if by_slug is not None else {},
        memo if memo is not None else {},
    )

    if annual:
        if holiday.get("month") == 2 and holiday.get("day") == 29:
            recurs = "Every February 29 (leap years only)"
        else:
            recurs = f"Every year on {date_short}"
    else:
        recurs = "The date changes each year. This page always shows the next one."

    share_text = f"{name} — {date_long}"

    return fill(template, {
        "HTML_CLASS": html_class(),
        "NAME": esc_attr(name),
        "DATE_LONG": date_long,
        "DATE_SHORT": date_short,
        "DATE_WEEKDAY": weekday_long_date(occ_date),
        "ISO_DATE": iso_date,
        "YEARLY": "1" if annual else "0",
        "DESCRIPTION": esc_attr(description),
        "URL": url,
        "PATH": path,
        "IMAGE_ABS": image,
        "LD_JSON": ld_json,
        "EXTRA_LD": faq_ld_json(faq_pairs),
        "DAY_LINK": day_link,
        "LONGFORM": longform,
        "RECURS": esc_attr(recurs),
        "CATEGORY_PILL": cat_pill(category, link=True),
        "SHARE_TEXT": esc_attr(share_text),
        "SHARE_LINKS": share_links(path, share_text),
        "ALSO_ON": also_on_html(occ_date, same_day, slug, day_published),
        **chrome,
    })


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

def build_day_index(holidays, by_slug, memo, start, end):
    """Map every date in [start, end] to the holidays observed on that date.

    This is the opposite question from next_occurrence(): absolute ("what falls
    on this exact date") rather than relative ("what's next"). A dated,
    permanent page needs the absolute answer.

    Deliberately derived only from the holiday data and the date itself -- never
    from "today" -- so any given date renders byte-identically on every run.
    That's what lets the archive be regenerated every day without churning git
    or drifting out of sync with the site's chrome.

    Returns (index, skipped_slugs).
    """
    index = {}
    skipped = set()
    if end < start:
        return index, sorted(skipped)

    for h in holidays:
        rule = h.get("floating_rule") or {}
        if rule.get("rule") == "next_friday_13":
            # 0-3 per calendar year, so it has no single date per year like
            # every other rule: it belongs on every Friday the 13th in range.
            d = start
            while d <= end:
                if d.day == 13 and d.weekday() == 4:
                    index.setdefault(d, []).append(h)
                d += datetime.timedelta(days=1)
            continue

        for year in range(start.year, end.year + 1):
            try:
                occ = holiday_date_for_year(h, year, by_slug, memo)
            except (ValueError, RuntimeError, KeyError):
                # Same graceful-degradation stance as next_occurrence: one
                # unresolvable rule must not take out the whole archive. The
                # holiday is simply absent from that year's dated pages.
                skipped.add(h["slug"])
                continue
            if start <= occ <= end:
                index.setdefault(occ, []).append(h)

    for d in index:
        index[d].sort(key=lambda h: (h.get("display_order", 999), h["name"]))
    return index, sorted(skipped)


def moveable_note_html(date, items, by_slug, memo):
    """The genuinely year-specific part of a dated page.

    Which observances landed on this exact date because of a rule rather than a
    fixed calendar date, and where the same observance lands the year after.
    That difference -- plus the weekday -- is what actually distinguishes
    October 9, 2026 from October 9, 2027, so it's worth stating outright rather
    than publishing two pages that read identically.
    """
    lines = []
    f13_slugs = {
        h["slug"] for h in items
        if (h.get("floating_rule") or {}).get("rule") == "next_friday_13"
    }
    moveable = [h for h in items
                if h["recurrence"] == "Floating" and h["slug"] not in f13_slugs]

    by_next_date = {}
    for h in moveable:
        try:
            nxt = holiday_date_for_year(h, date.year + 1, by_slug, memo)
        except (ValueError, RuntimeError, KeyError):
            continue  # rule can't reach next year yet -- don't claim a date
        by_next_date.setdefault(nxt, []).append(h["name"])

    for nxt, names in sorted(by_next_date.items()):
        one = len(names) == 1
        lines.append(
            f"{esc_attr(join_names(names))} {'falls' if one else 'fall'} on this date "
            f"in {date.year} because {'it is' if one else 'they are'} set by a rule "
            f"rather than a fixed date &mdash; in {nxt.year}, "
            f"{'it lands' if one else 'they land'} on {esc_attr(month_day(nxt))}."
        )

    if f13_slugs:
        lines.append(
            f"Friday the 13th lands here because the 13th of "
            f"{MONTH_NAMES[date.month]} falls on a Friday in {date.year}."
        )

    if not lines:
        return ""
    body = "".join(f"<p>{line}</p>" for line in lines)
    return f'<div class="moveable-note">{body}</div>'


def week_list_html(date, day_index, published_days):
    """The days either side of this one that have a permanent page."""
    out = []
    for offset in range(-3, 4):
        d = date + datetime.timedelta(days=offset)
        if d != date and d not in published_days:
            continue
        label = f"{WEEKDAY_NAMES[d.weekday()][:3]} {d.day}"
        if d == date:
            out.append(
                f'<a class="t" href="{day_path(d)}" aria-current="date">'
                f'<span class="d mono">{label}</span><b>This page</b></a>'
            )
        else:
            n = len(day_index.get(d, []))
            out.append(
                f'<a href="{day_path(d)}"><span class="d mono">{label}</span>'
                f'<b>{n} {plural(n, "observance")}</b></a>'
            )
    return "".join(out)


def load_people(path):
    """scripts/people.json -> {"meta": {...}, "dates": {"MM-DD": {...}}}, or None.

    Never raises: a missing or damaged file turns the feature off for this run
    (with a warning for the damaged case) rather than failing the daily build.
    """
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data.get("dates"), dict):
            raise ValueError("no 'dates' object")
        return data
    except (OSError, ValueError, AttributeError) as e:
        print(f"WARNING: {path} could not be read ({e}); the 'born on this "
              f"day' blocks are off for this run.", file=sys.stderr)
        return None


def person_li_html(r):
    """One person: name linked to Wikipedia, years, and a short descriptor."""
    title = r.get("title") or r["name"].replace(" ", "_")
    href = "https://en.wikipedia.org/wiki/" + quote(title, safe="()_,'.:!~*-")
    if r.get("d") is None:
        years = f"b.&nbsp;{r['y']}"
    else:
        years = f"{r['y']}&ndash;{r['d']}"
    desc = r.get("w") or ""
    return (
        f'<li><a href="{esc_href(esc_text(href))}" rel="noopener">{esc_text(r["name"])}</a>'
        f'<span class="yrs mono">{years}</span>'
        + (f'<span class="desc">{esc_text(desc)}</span>' if desc else "")
        + "</li>"
    )


def people_block_html(people, month, day, limit, full_page=False):
    """The "Born on <date>" section: Historic figures and Celebrities, side by side.

    Two sub-blocks because they answer different questions and age differently:
    the historic list is deceased people ranked by global notability and never
    changes; the living list is ranked by a notability/pageview blend and is the
    one that needs the periodic refresh. Either sub-block is omitted when it has
    no one; the whole section is omitted when neither does.

    Years only, never an age: "born 1967" stays true on a page that is
    regenerated for years, "turns 59" does not.

    This section is deliberately plain HTML with no structured data: a birthday
    is not an Event, and these names must stay out of the Event JSON-LD that is
    reserved for genuine observances (see the credibility constraints in
    docs/EXECUTION_PLAN.md, E6).
    """
    if not people:
        return ""
    entry = people["dates"].get(f"{month:02d}-{day:02d}")
    if not entry:
        return ""
    historic = entry.get("historic", [])[:limit]
    living = entry.get("living", [])[:limit]
    if not historic and not living:
        return ""

    def column(heading, rows):
        if not rows:
            return ""
        return (
            f'<div><h3>{heading}</h3><ul class="born-list">'
            + "".join(person_li_html(r) for r in rows)
            + "</ul></div>"
        )

    label = month_day_label(month, day)
    cols = (
        column("Historic figures", historic)
        + column("Celebrities &amp; public figures", living)
    )
    more = ""
    if not full_page:
        more = (
            f'<p class="born-more"><a href="{perennial_path(month, day)}#born-h">'
            f"Everyone born on {esc_text(label)} &rarr;</a></p>"
        )
    return (
        f'<section class="born" aria-labelledby="born-h">'
        f'<h2 class="eyebrow" id="born-h">Born on {esc_text(label)}</h2>'
        f'<div class="born-cols">{cols}</div>{more}'
        f'<p class="born-src">Birth dates from '
        f'<a href="https://www.wikidata.org/" rel="noopener">Wikidata</a>; '
        f"names link to Wikipedia.</p>"
        f"</section>"
    )


def render_day_page(date, items, prev_date, next_date, template, by_slug, memo,
                    chrome, day_index, published_days, people=None):
    """Render one permanent /day/YYYY-MM-DD/ page."""
    n = len(items)
    lead = items[0]
    hero_rel = f"/images/hero/{lead['category']}.jpg"
    path = day_path(date)
    url = f"{SITE_BASE_URL}{path}"
    iso = date.isoformat()

    rows = [obs_row(h, i, iso) for i, h in enumerate(items)]

    # A rectangle partway down a long list is the conventional (and
    # highest-viewability) in-content position for a list page. Split the
    # table rather than putting an ad inside a <tr>; the second table has no
    # header row of its own, only a screen-reader caption, and the numbering
    # carries on from the first.
    if len(rows) >= 8:
        split = 5
        list_block = (
            f'<table class="obs">{OBS_THEAD}<tbody>{"".join(rows[:split])}</tbody></table>'
            f'<div class="ad-slot ad-rect" data-ad-slot="incontent"></div>'
            f'<table class="obs"><caption class="sr">Observances, continued</caption>'
            f'<tbody>{"".join(rows[split:])}</tbody></table>'
        )
    else:
        list_block = f'<table class="obs">{OBS_THEAD}<tbody>{"".join(rows)}</tbody></table>'

    preview = join_names([h["name"] for h in items[:3]])
    description = (
        f"{n} national and international {plural(n, 'holiday')} and observances "
        f"fall on {weekday_long_date(date)}, including {preview}."
    )

    ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"Holidays and observances on {long_date(date)}",
        "numberOfItems": n,
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "url": url,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": h["name"],
                "url": f"{SITE_BASE_URL}/holiday/{h['slug']}/",
            }
            for i, h in enumerate(items)
        ],
    }
    ld_json = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")

    stepper = ""
    if prev_date:
        stepper += (
            f'<a class="btn" href="{day_path(prev_date)}" '
            f'aria-label="Previous day: {esc_attr(long_date(prev_date))}">&lsaquo;</a>'
        )
    if next_date:
        stepper += (
            f'<a class="btn" href="{day_path(next_date)}" '
            f'aria-label="Next day: {esc_attr(long_date(next_date))}">&rsaquo;</a>'
        )

    nav = []
    nav.append(
        f'<a href="{day_path(prev_date)}">&larr; {esc_attr(long_date(prev_date))}</a>'
        if prev_date else "<span></span>"
    )
    nav.append(
        f'<a href="{day_path(next_date)}">{esc_attr(long_date(next_date))} &rarr;</a>'
        if next_date else "<span></span>"
    )

    share_title = f"Everything {long_date(date)} celebrates"
    share_text = (
        f"{n} {plural(n, 'holiday')} and observances on {weekday_long_date(date)}"
    )

    return fill(template, {
        "TITLE": esc_attr(
            f"{weekday_long_date(date)}: {n} {plural(n, 'Holiday')} & Observances "
            f"| Today Celebrates"
        ),
        "OG_TITLE": esc_attr(share_title),
        "DESCRIPTION": esc_attr(description),
        "URL": url,
        "PATH": path,
        # og:image/twitter:image want an absolute URL -- several scrapers won't
        # resolve a site-relative one.
        "HERO_IMAGE_ABS": f"{SITE_BASE_URL}{hero_rel}",
        "WEEKDAY_LINE": esc_attr(weekday_long_date(date)).upper(),
        "HEADLINE": esc_attr(share_title),
        "INTRO": (
            f"{n} national, international, and world {plural(n, 'observance')} "
            f"{plural(n, 'is', 'are')} on the calendar for "
            f"{esc_attr(weekday_long_date(date))}."
        ),
        "LIST_BLOCK": list_block,
        "MOVEABLE_NOTE": moveable_note_html(date, items, by_slug, memo),
        "PEOPLE_BLOCK": people_block_html(
            people, date.month, date.day, PEOPLE_DAY_LIMIT
        ),
        "DAY_NAV": stepper,
        "DAY_PN": "".join(nav),
        "HTML_CLASS": html_class(),
        "DATE_PLAIN": esc_attr(long_date(date)),
        "LD_JSON": ld_json,
        "SHARE_TITLE": esc_attr(share_title),
        "SHARE_TEXT": esc_attr(share_text),
        "SHARE_LINKS": share_links(path, share_title),
        "WEEK_LIST": week_list_html(date, day_index, published_days),
        # The dated -> perennial half of E3's cross-link. Derived from the date
        # alone, so a past dated page still regenerates byte-identically.
        "PERENNIAL_LINK": (
            f'<p>For what falls on {esc_attr(month_day(date))} in any year, see '
            f'<a href="{perennial_path(date.month, date.day)}">'
            f'{esc_attr(month_day(date))} holidays and observances</a>.</p>'
        ),
        **chrome,
    })


def build_perennial_index(wide_index):
    """(month, day) -> what falls on that calendar date, year-independently.

    Built from a wide build_day_index() pass rather than from a single year,
    because that is the only way to answer the question a year-less page asks:
    *which* observances can land on October 8, and which of them land there
    every single year.

    Two buckets, and the split is the whole point of the page type:

      annual   -- fixed-date observances. They are on this date every year, so
                  they are the perennial page's own content.
      floating -- rule-dated observances, each with the years inside the
                  window in which the rule puts it on this date. "Memorial Day
                  is May 25 in 2026 and 2032" is a fact about the calendar, not
                  about a particular year, so it belongs here too -- but as a
                  note, not as a list entry, since it is not true every year.

    The year-specific angle (the weekday, and where a moveable observance goes
    *next* year) stays on /day/YYYY-MM-DD/, which is what keeps the two page
    types from being near-duplicates of each other.
    """
    buckets = {key: {"annual": {}, "floating": {}} for key in all_month_days()}
    for date, items in wide_index.items():
        bucket = buckets.get((date.month, date.day))
        if bucket is None:  # cannot happen for a real date; cheap guard
            continue
        for h in items:
            if h["recurrence"] == "Annual":
                bucket["annual"][h["slug"]] = h
            else:
                bucket["floating"].setdefault(h["slug"], [h, []])[1].append(date.year)

    index = {}
    for key, bucket in buckets.items():
        annual = sorted(
            bucket["annual"].values(),
            key=lambda h: (h.get("display_order", 999), h["name"]),
        )
        floating = sorted(
            ((h, sorted(set(years))) for h, years in bucket["floating"].values()),
            key=lambda pair: (pair[1][0], pair[0]["name"]),
        )
        index[key] = {"annual": annual, "floating": floating}
    return index


def perennial_nearby_html(key, month_days, perennial_index):
    """The rail: three dates either side of this one, as a closed 366-day ring.

    Wrapping at December 31 is deliberate -- it means every perennial page is
    reachable from its neighbours no matter which one a crawler lands on, so
    none of the 366 can be orphaned even for a date with nothing on it.
    """
    i = month_days.index(key)
    out = []
    for offset in range(-3, 4):
        k = month_days[(i + offset) % len(month_days)]
        label = f"{MONTH_ABBR[k[0]]} {k[1]}"
        if k == key:
            out.append(
                f'<a class="t" href="{perennial_path(*k)}" aria-current="page">'
                f'<span class="d mono">{label}</span><b>This page</b></a>'
            )
            continue
        n = len(perennial_index[k]["annual"])
        if n:
            note = f'{n} every year'
        elif perennial_index[k]["floating"]:
            note = "Moveable dates only"
        else:
            note = "Nothing on record"
        out.append(
            f'<a href="{perennial_path(*k)}"><span class="d mono">{label}</span>'
            f'<b>{note}</b></a>'
        )
    return "".join(out)


def perennial_moves_html(label, floating):
    """The "lands here in some years" note.

    Each entry names the years inside the window, which is the honest form: a
    rule-dated observance is not an October 8 observance, it is one that falls
    on October 8 in 2026 and 2032. Naming the years is also what keeps this
    page from claiming something the dated pages contradict.
    """
    if not floating:
        return ""
    lines = [
        f"<p>These are set by a rule rather than a fixed date, so they only land "
        f"on {esc_attr(label)} in some years.</p>"
    ]
    for h, years in floating:
        yrs = join_names([str(y) for y in years])
        lines.append(
            f'<p><a href="/holiday/{h["slug"]}/">{esc_attr(h["name"])}</a> &mdash; '
            f'{yrs}</p>'
        )
    return f'<div class="moveable-note">{"".join(lines)}</div>'


def perennial_years_html(label, dated):
    """Cross-link from the perennial page to the dated pages for the same date.

    The other direction lives in render_day_page()'s PERENNIAL_LINK. Both
    pages stay self-canonical and both stay in the sitemap: they answer
    different questions, and collapsing either into the other would lose one of
    them (see the URL model table in scripts/README.md).
    """
    parts = [
        f"<p>This page covers {esc_attr(label)} in any year."
    ]
    if dated:
        links = join_names([
            f'<a href="{day_path(d)}">{esc_attr(long_date(d))}</a>' for d in dated
        ])
        parts[0] += (
            f" For one year in particular &mdash; the weekday, and which moveable "
            f"observances landed on it &mdash; see {links}.</p>"
        )
    else:
        parts[0] += "</p>"
    parts.append(
        "<p>Today Celebrates tracks daily national, international and world "
        "observances all year.</p>"
    )
    return f'<div class="note">{"".join(parts)}</div>'


def render_perennial_page(key, bucket, prev_key, next_key, template, chrome,
                          month_days, perennial_index, dated, today, people=None):
    """Render one permanent /<month>-<day>/ page."""
    month, day = key
    label = month_day_label(month, day)
    path = perennial_path(month, day)
    url = f"{SITE_BASE_URL}{path}"
    annual = bucket["annual"]
    floating = bucket["floating"]
    n = len(annual)
    nf = len(floating)

    # The ICS button on each row needs a concrete date, so rows carry the next
    # time this month-day comes round. That is the one value on this page that
    # moves: on the day after this date passes, these pages' rows roll to next
    # year's ISO date, so exactly one perennial page changes per day. Everything
    # else here is derived from the calendar and the holiday data alone.
    occ = next_md_occurrence(month, day, today)
    iso_date = occ.isoformat() if occ else ""

    hero_rel = f"/images/hero/{annual[0]['category'] if annual else 'celebration'}.jpg"

    if annual:
        rows = [obs_row(h, i, iso_date) for i, h in enumerate(annual)]
        # Same split as the dated pages: a rectangle partway down a long list,
        # between two tables rather than inside a row.
        if len(rows) >= 8:
            split = 5
            list_block = (
                f'<table class="obs">{OBS_THEAD}<tbody>{"".join(rows[:split])}</tbody></table>'
                f'<div class="ad-slot ad-rect" data-ad-slot="incontent"></div>'
                f'<table class="obs"><caption class="sr">Observances, continued</caption>'
                f'<tbody>{"".join(rows[split:])}</tbody></table>'
            )
        else:
            list_block = f'<table class="obs">{OBS_THEAD}<tbody>{"".join(rows)}</tbody></table>'
    else:
        list_block = (
            f'<p class="empty-note">No observance falls on {esc_attr(label)} '
            f'every year.</p>'
        )

    if n:
        preview = join_names([h["name"] for h in annual[:3]])
        description = (
            f"{n} national and international {plural(n, 'holiday')} and observances "
            f"fall on {label} every year, including {preview}."
        )
        intro = (
            f"{n} national, international, and world {plural(n, 'observance')} "
            f"{plural(n, 'is', 'are')} on the calendar for {esc_attr(label)} "
            f"every year"
        )
        intro += (
            f", and {nf} more {plural(nf, 'lands', 'land')} on it in some years."
            if nf else "."
        )
        title = (
            f"{label}: {n} {plural(n, 'Holiday')} & Observances "
            f"| Today Celebrates"
        )
    elif nf:
        names = join_names([h["name"] for h, _ in floating[:3]])
        description = (
            f"No observance falls on {label} every year, but {names} can land on "
            f"it depending on the year."
        )
        intro = (
            f"Nothing falls on {esc_attr(label)} every year. "
            f"{nf} rule-dated {plural(nf, 'observance')} "
            f"{plural(nf, 'lands', 'land')} on it in some years."
        )
        title = f"{label}: Holidays and Observances | Today Celebrates"
    else:
        description = (
            f"No national or international observance is on record for {label}. "
            f"Today Celebrates keeps a page for every date of the year."
        )
        intro = (
            f"No observance is on record for {esc_attr(label)}, in any year. "
            f"The site keeps a page for every date of the calendar, so this one "
            f"is here for when that changes."
        )
        title = f"{label}: No Observances on Record | Today Celebrates"

    share_title = (
        f"Everything {label} celebrates" if (n or nf)
        else f"{label} on the calendar"
    )
    share_text = (
        f"{n} {plural(n, 'holiday')} and observances on {label}, every year"
        if n else f"What {label} celebrates"
    )

    ld_block = ""
    if annual:
        ld = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"Holidays and observances on {label}",
            "numberOfItems": n,
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "url": url,
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": h["name"],
                    "url": f"{SITE_BASE_URL}/holiday/{h['slug']}/",
                }
                for i, h in enumerate(annual)
            ],
        }
        ld_json = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
        ld_block = (
            f'\n<script type="application/ld+json">{ld_json}</script>'
        )

    prev_label = month_day_label(*prev_key)
    next_label = month_day_label(*next_key)
    stepper = (
        f'<a class="btn" href="{perennial_path(*prev_key)}" '
        f'aria-label="Previous date: {esc_attr(prev_label)}">&lsaquo;</a>'
        f'<a class="btn" href="{perennial_path(*next_key)}" '
        f'aria-label="Next date: {esc_attr(next_label)}">&rsaquo;</a>'
    )
    pn = (
        f'<a href="{perennial_path(*prev_key)}">&larr; {esc_attr(prev_label)}</a>'
        f'<a href="{perennial_path(*next_key)}">{esc_attr(next_label)} &rarr;</a>'
    )

    return fill(template, {
        "TITLE": esc_attr(title),
        "OG_TITLE": esc_attr(share_title),
        "DESCRIPTION": esc_attr(description),
        "URL": url,
        "PATH": path,
        "HERO_IMAGE_ABS": f"{SITE_BASE_URL}{hero_rel}",
        "CRUMBS": crumbs_html((label, None)),
        "EYEBROW": esc_attr(f"EVERY {label}").upper(),
        "HEADLINE": esc_attr(share_title),
        "INTRO": intro,
        "LIST_BLOCK": list_block,
        "MOVES_NOTE": perennial_moves_html(label, floating),
        "PEOPLE_BLOCK": people_block_html(
            people, month, day, PEOPLE_PERENNIAL_LIMIT, full_page=True
        ),
        "YEARS_NOTE": perennial_years_html(label, dated),
        "DATE_NAV": stepper,
        "DATE_PN": pn,
        "HTML_CLASS": html_class(),
        "LD_BLOCK": ld_block,
        "SHARE_TITLE": esc_attr(share_title),
        "SHARE_TEXT": esc_attr(share_text),
        "SHARE_LINKS": share_links(path, share_title),
        "NEARBY": perennial_nearby_html(key, month_days, perennial_index),
        **chrome,
    })


def render_home(date, items, template, chrome, has_day_page, month_days,
                coming_up, day_from, day_to):
    """Render public/index.html with the generator's "today" baked in.

    The baked markup must match what index.html's own inline script produces
    for the same day (obs_row, calendar_html and the headings above), because
    that script takes over as soon as the visitor picks another day. Matching
    means no flash of changing content; the point of baking it is that a
    crawler (or a visitor with JS blocked) sees the real holiday names instead
    of empty placeholders.
    """
    n = len(items)
    iso = date.isoformat()
    day_link = (
        f'<a href="{day_path(date)}">Permanent page for {esc_attr(long_date(date))} &rarr;</a>'
        if has_day_page else ""
    )
    base = day_text(date, True)

    if items:
        lead = items[0]
        title = f"What Holiday Is Today? — {long_date(date)} | Today Celebrates"
        preview = join_names([h["name"] for h in items[:3]])
        description = (
            f"{n} {plural(n, 'holiday')} and observances today, "
            f"{weekday_long_date(date)}: {preview}. A daily calendar of national, "
            f"international, and world holidays."
        )
        image = f"/images/hero/{lead['category']}.jpg"
    else:
        lead = None
        # Literal em dash, not &mdash; -- esc_attr() would turn the entity's &
        # into &amp; and print it verbatim.
        title = f"Today Celebrates — {long_date(date)}"
        description = (
            "A daily calendar of national, international, and world holidays "
            "and observances."
        )
        image = "/images/hero/celebration.jpg"

    return fill(template, {
        "HTML_CLASS": html_class(),
        "GENERATED_NOTE": GENERATED_NOTE,
        "TITLE": esc_attr(title),
        "DESCRIPTION": esc_attr(description),
        "IMAGE_ABS": f"{SITE_BASE_URL}{image}",
        "TODAY_KEY": js_day_key(date),
        "DAY_FROM": day_from,
        "DAY_TO": day_to,
        "H1_TEXT": esc_attr(f"Today, {base}"),
        "COUNT_TEXT": f"{n} {plural(n, 'observance')}" if n else "",
        "LEAD_HIDDEN": "" if lead else " hidden",
        "LEAD_NAME": esc_attr(lead["name"]) if lead else "",
        "LEAD_HREF": f"/holiday/{lead['slug']}/" if lead else "/",
        "LEAD_SHARE_URL": "/",
        "LEAD_SHARE_TITLE": esc_attr(f"What holiday is today? {base}"),
        "LEAD_SHARE_LABEL": "Share today",
        "TABLE_HIDDEN": "" if lead else " hidden",
        "EMPTY_HIDDEN": " hidden" if lead else "",
        "ROWS": "".join(obs_row(h, i, iso) for i, h in enumerate(items)),
        "DAY_LINK": day_link,
        "CAL_LABEL": f"{MONTH_ABBR[date.month]} {date.year}",
        "CAL_GRID": calendar_html(date.year, date.month, date, date, month_days),
        "MONTH_JUMP": month_jump_html(date.month),
        "COMING_UP": coming_up,
        "CAT_JSON": category_json(),
        **chrome,
    })


def render_simple_page(template, chrome, *, title, description, path, headline,
                       body, side="", crumbs=""):
    """/about/, /categories/ and /category/<slug>/."""
    return fill(template, {
        "HTML_CLASS": html_class(),
        "TITLE": esc_attr(title),
        "DESCRIPTION": esc_attr(description),
        "URL": f"{SITE_BASE_URL}{path}",
        "IMAGE_ABS": f"{SITE_BASE_URL}/images/hero/celebration.jpg",
        "HEADLINE": esc_attr(headline),
        "BODY": body,
        "SIDE": side,
        "CRUMBS": crumbs,
        **chrome,
    })


def crumbs_html(*trail):
    """trail: (label, href_or_None) pairs after the leading Today link."""
    parts = ['<a href="/">Today</a>']
    for label, href in trail:
        parts.append('<span aria-hidden="true">/</span>')
        parts.append(
            f'<a href="{href}">{esc_attr(label)}</a>' if href
            else f'<span aria-current="page">{esc_attr(label)}</span>'
        )
    return f'<nav class="crumbs" aria-label="Breadcrumb">{"".join(parts)}</nav>'


def render_about_body(total, category_count):
    return (
        '<div class="plain">'
        f"<p>Today Celebrates is a daily calendar of national, international and "
        f"world holidays and observances: {total:,} of them across {category_count} "
        f"categories, each with a page of its own.</p>"
        "<h2>How the site is organised</h2>"
        '<p><a href="/">Today</a> shows what is being celebrated right now. Every '
        "date of the year has a page of its own listing everything that falls "
        "on it, and every observance has one page that always shows its next "
        "date. "
        '<a href="/categories/">Categories</a> lets you browse by theme, and the '
        "search box finds any observance by name.</p>"
        "<h2>Fixed and moving dates</h2>"
        "<p>Most observances fall on the same date every year. Some are set by a "
        "rule instead, such as the second Monday of a month or a number of days "
        "after Easter, so their date moves. Those pages show the next upcoming "
        "date, worked out from the rule rather than typed in by hand.</p>"
        "<h2>Share and save</h2>"
        "<p>Every page has Share and Copy link buttons, plus links to send it by "
        "email, text, Facebook, X or WhatsApp. Each observance page also has an Add "
        "to calendar button: it downloads a calendar file you can open in Apple "
        "Calendar, Google Calendar or Outlook, and observances with a fixed date "
        "repeat every year.</p>"
        "</div>"
    )


def read_sitemap_lastmods(path):
    """Parse an existing sitemap.xml into {loc: lastmod}.

    Returns {} when the file is missing or unparseable -- an absent or broken
    sitemap should degrade to "stamp everything with today", never a crash.
    This is deliberately a regex rather than an XML parse: the only sitemap
    this ever reads is the one render below writes, one <url> per line.
    """
    try:
        with open(path, encoding="utf-8") as f:
            xml = f.read()
    except OSError:
        return {}
    pairs = re.findall(
        r"<loc>\s*([^<]+?)\s*</loc>\s*<lastmod>\s*([^<]+?)\s*</lastmod>", xml
    )
    return dict(pairs)


def generate(holidays, today, site_dir, dry_run=False, templates_dir=None,
             people=None):
    """Returns a report dict describing what changed.

    `people` is the parsed scripts/people.json (see load_people), or None to
    render the date pages without the "born on this day" blocks."""
    templates_dir = templates_dir or DEFAULT_TEMPLATES_DIR
    by_slug = {h["slug"]: h for h in holidays}
    memo = {}  # (slug, year) -> date.date, shared across all holidays this run
    occurrences = {}  # slug -> date.date
    unresolved = []   # holidays whose rule could not produce a date this run
    for h in holidays:
        try:
            occurrences[h["slug"]] = next_occurrence(h, today, by_slug, memo)
        except (ValueError, RuntimeError, KeyError) as e:
            # One unresolvable holiday must never take the whole run down with
            # it. The overwhelmingly likely cause is a lookup_table in
            # export_from_notion.py that has run out of hand-confirmed years
            # (see scripts/README.md) -- and if that aborted generation, the
            # daily workflow would start failing and the entire site would
            # silently stop rolling holidays forward. So skip just this one:
            # its existing page and sitemap entry are left untouched, it drops
            # out of the calendar's month data until its rule is extended, and
            # everything else regenerates normally. main() warns loudly.
            unresolved.append({"slug": h["slug"], "name": h["name"], "error": str(e)})

    # ---- the day index: every date -> the holidays observed on it ----
    # The index runs from min(archive start, today) so "today" is always in it
    # even when generating for a date before the archive opened, but only dates
    # from DAY_ARCHIVE_START onward get published as pages. Month data files,
    # /day/ pages, "also on this date" lists and the home page all read from
    # this one structure, so the calendar and the archive can never disagree.
    day_end = max(occurrences.values()) if occurrences else today
    day_index, day_index_skipped = build_day_index(
        holidays, by_slug, memo, min(DAY_ARCHIVE_START, today), day_end
    )
    day_dates = [d for d in sorted(day_index) if d >= DAY_ARCHIVE_START]
    published_days = set(day_dates)

    chromes = {k: chrome_for(templates_dir, k) for k in (None,) + NAV_KEYS}

    # ---- month data files (v2): [name, slug, category, yearly] per day ----
    # Written to data/v2/ rather than over the old data/YYYY-MM.json: pages the
    # previous design left in browser and CDN caches still read the old files,
    # and a changed shape under the same URL would break them until they expire.
    by_month = {}  # "YYYY-MM" -> { "YYYY-M-D": [[name, slug, category, yearly], ...] }
    for d in sorted(day_index):
        mk = f"{d.year:04d}-{d.month:02d}"
        by_month.setdefault(mk, {})[f"{d.year}-{d.month}-{d.day}"] = [
            [h["name"], h["slug"], h["category"], 1 if h["recurrence"] == "Annual" else 0]
            for h in day_index[d]
        ]

    data_dir = os.path.join(site_dir, "data", "v2")
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

    # ---- search index: [name, slug] for every page that exists ----
    def has_page(h):
        return h["slug"] in occurrences or os.path.exists(
            os.path.join(site_dir, "holiday", h["slug"], "index.html")
        )

    search_index = [[h["name"], h["slug"]]
                    for h in sorted(holidays, key=lambda h: h["slug"]) if has_page(h)]
    search_changed, _ = write_if_changed(
        os.path.join(site_dir, "data", "search.json"),
        json.dumps(search_index, ensure_ascii=False, separators=(",", ":")),
        dry_run,
    )

    # ---- /day/YYYY-MM-DD/ permanent dated pages ----
    day_template = load_template(templates_dir, "day.html")
    day_diffs = {"created": [], "changed": [], "unchanged": 0}
    for i, d in enumerate(day_dates):
        prev_d = day_dates[i - 1] if i > 0 else None
        next_d = day_dates[i + 1] if i + 1 < len(day_dates) else None
        new_html = render_day_page(
            d, day_index[d], prev_d, next_d, day_template, by_slug, memo,
            chromes["CALENDAR"], day_index, published_days, people=people,
        )
        page_dir = os.path.join(site_dir, "day", d.isoformat())
        page_path = os.path.join(page_dir, "index.html")
        old_html = open(page_path, encoding="utf-8").read() if os.path.exists(page_path) else None
        if old_html is None:
            day_diffs["created"].append(d.isoformat())
        elif old_html != new_html:
            day_diffs["changed"].append(d.isoformat())
        else:
            day_diffs["unchanged"] += 1
        if not dry_run:
            os.makedirs(page_dir, exist_ok=True)
            with open(page_path, "w", encoding="utf-8") as f:
                f.write(new_html)

    # ---- perennial /<month>-<day>/ pages (E3) ----
    # A second, wider index pass: the year-less page has to know which
    # rule-dated observances can land on a date across several years, which the
    # archive's one-year window cannot answer. `memo` is shared with the pass
    # above, so every date either pass already computed is free.
    perennial_start = min(datetime.date(today.year, 1, 1), today)
    perennial_end = datetime.date(today.year + PERENNIAL_YEARS - 1, 12, 31)
    wide_index, perennial_skipped = build_day_index(
        holidays, by_slug, memo, perennial_start, perennial_end
    )
    perennial_index = build_perennial_index(wide_index)
    perennial_mds = all_month_days()
    dated_by_md = {}
    for d in day_dates:
        dated_by_md.setdefault((d.month, d.day), []).append(d)

    perennial_template = load_template(templates_dir, "perennial.html")
    perennial_diffs = {"created": [], "changed": [], "unchanged": 0, "skipped": []}
    for i, key in enumerate(perennial_mds):
        bucket = perennial_index[key]
        path = perennial_path(*key)
        if not bucket["annual"] and not bucket["floating"] and not PERENNIAL_EMPTY_PAGES:
            perennial_diffs["skipped"].append(path)
            continue
        prev_key = perennial_mds[(i - 1) % len(perennial_mds)]
        next_key = perennial_mds[(i + 1) % len(perennial_mds)]
        html = render_perennial_page(
            key, bucket, prev_key, next_key, perennial_template, chromes["CALENDAR"],
            perennial_mds, perennial_index, dated_by_md.get(key, []), today,
            people=people,
        )
        changed, created = write_if_changed(
            os.path.join(site_dir, path.strip("/"), "index.html"), html, dry_run
        )
        if created:
            perennial_diffs["created"].append(path)
        elif changed:
            perennial_diffs["changed"].append(path)
        else:
            perennial_diffs["unchanged"] += 1
    perennial_paths = [
        perennial_path(*k) for k in perennial_mds
        if perennial_path(*k) not in set(perennial_diffs["skipped"])
    ]

    # ---- per-holiday pages ----
    holiday_template = load_template(templates_dir, "holiday.html")
    page_diffs = {"changed": [], "unchanged": [], "created": [], "skipped": []}
    for h in holidays:
        slug = h["slug"]
        if slug not in occurrences:
            # Unresolvable date: leave whatever page already exists exactly as
            # it is. A stale date on one page beats deleting it or writing a
            # dateless one.
            page_diffs["skipped"].append(slug)
            continue
        occ = occurrences[slug]
        # Point the back-link at the dated page for this holiday's occurrence
        # rather than the homepage -- that's the page that actually answers
        # "what else is on this date". Falls back to / if that day isn't
        # published (a date before the archive opened).
        day_link = day_path(occ) if occ in published_days else "/"
        new_html = render_page(
            h, occ, day_link, by_slug, memo, holiday_template, chromes[None],
            same_day=day_index.get(occ, []), day_published=occ in published_days,
        )
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

    # ---- homepage: today's content baked into the HTML ----
    home_items = day_index.get(today, [])
    month_days = {d.day for d in day_index if (d.year, d.month) == (today.year, today.month)}
    home_html = render_home(
        today,
        home_items,
        load_template(templates_dir, "index.html"),
        chromes["TODAY"],
        has_day_page=today in published_days,
        month_days=month_days,
        coming_up=coming_up_html(today, day_index),
        day_from=day_dates[0].isoformat() if day_dates else "",
        day_to=day_dates[-1].isoformat() if day_dates else "",
    )
    home_path = os.path.join(site_dir, "index.html")
    old_home = open(home_path, encoding="utf-8").read() if os.path.exists(home_path) else None
    home_changed = old_home != home_html
    if not dry_run:
        with open(home_path, "w", encoding="utf-8") as f:
            f.write(home_html)

    # ---- /about/, /categories/ and /category/<slug>/ ----
    page_template = load_template(templates_dir, "page.html")
    by_category = {}
    for h in holidays:
        if has_page(h):
            by_category.setdefault(h["category"], []).append(h)
    category_counts = {c: len(v) for c, v in by_category.items()}
    simple_pages = {}  # site path -> html

    simple_pages["/about/"] = render_simple_page(
        page_template, chromes["ABOUT"],
        title="About Today Celebrates | Today Celebrates",
        description=(
            "Today Celebrates is a daily calendar of national, international and "
            "world holidays and observances, with a page for every one."
        ),
        path="/about/", headline="About Today Celebrates",
        body=render_about_body(len(search_index), len(category_counts)),
        side=category_side_html(category_counts),
        crumbs=crumbs_html(("About", None)),
    )

    cat_cards = "".join(
        f'<li><a href="/category/{c}/"><span>{esc_attr(cat_title(c))}</span>'
        f'<span class="mono">{n}</span></a></li>'
        for c, n in sorted(category_counts.items(), key=lambda kv: cat_title(kv[0]))
    )
    simple_pages["/categories/"] = render_simple_page(
        page_template, chromes["CATEGORIES"],
        title="Holiday Categories | Today Celebrates",
        description=(
            f"Browse {len(search_index):,} holidays and observances by category: "
            f"food, community, nature, health, music and more."
        ),
        path="/categories/", headline="Browse by category",
        body=(
            '<p class="intro">Every observance on the calendar, grouped by theme.</p>'
            f'<ul class="cats">{cat_cards}</ul>'
        ),
        side="",
        crumbs=crumbs_html(("Categories", None)),
    )

    for c, members in by_category.items():
        lis = []
        for h in sorted(members, key=lambda h: h["name"].lower()):
            occ = occurrences.get(h["slug"])
            when = (f'<span class="mono">{MONTH_ABBR[occ.month]} {occ.day}</span>'
                    if occ else "")
            lis.append(
                f'<li><a href="/holiday/{h["slug"]}/"><span>{esc_attr(h["name"])}</span>'
                f"{when}</a></li>"
            )
        title = cat_title(c)
        simple_pages[f"/category/{c}/"] = render_simple_page(
            page_template, chromes["CATEGORIES"],
            title=f"{title} Holidays and Observances | Today Celebrates",
            description=(
                f"{len(members)} {title.lower()} holidays and observances, with the "
                f"date each one next falls on."
            ),
            path=f"/category/{c}/", headline=f"{title} holidays and observances",
            body=(
                f'<p class="intro">{len(members)} observances in this category, A to Z, '
                f"with the date each one next falls on.</p>"
                f'<ul class="cat-list">{"".join(lis)}</ul>'
            ),
            side=category_side_html(category_counts, current=c),
            crumbs=crumbs_html(("Categories", "/categories/"), (title, None)),
        )

    simple_changed = set()
    for path, html in simple_pages.items():
        changed, _created = write_if_changed(
            os.path.join(site_dir, path.strip("/"), "index.html"), html, dry_run
        )
        if changed:
            simple_changed.add(path)

    # ---- sitemap.xml ----
    # lastmod must say when a page's content actually changed, not when the
    # generator last ran. Stamping every URL with today's date on every run
    # told crawlers all ~2,400 pages changed daily when ~10 did -- a
    # misleading crawl signal, and a 4,880-line diff in every daily commit.
    # So: carry each URL's lastmod forward from the sitemap already on disk,
    # and only stamp today on pages this run actually created or changed. A
    # URL with no previous entry (first run, brand-new holiday) gets today.
    today_iso = today.isoformat()
    previous_lastmod = read_sitemap_lastmods(os.path.join(site_dir, "sitemap.xml"))
    touched = set(page_diffs["created"]) | set(page_diffs["changed"])

    def lastmod_for(loc, changed_this_run):
        if changed_this_run:
            return today_iso
        return previous_lastmod.get(loc, today_iso)

    home_loc = f"{SITE_BASE_URL}/"
    urls = [
        f'  <url><loc>{home_loc}</loc>'
        f'<lastmod>{lastmod_for(home_loc, home_changed)}</lastmod></url>'
    ]

    # Perennial date pages. Both these and the dated pages stay in the sitemap:
    # they are self-canonical and answer different questions (see the URL model
    # table in scripts/README.md).
    touched_perennial = set(perennial_diffs["created"]) | set(perennial_diffs["changed"])
    for path in perennial_paths:
        loc = f"{SITE_BASE_URL}{path}"
        urls.append(
            f'  <url><loc>{loc}</loc>'
            f'<lastmod>{lastmod_for(loc, path in touched_perennial)}</lastmod></url>'
        )

    # Dated pages. Past ones are regenerated byte-identically, so they keep the
    # lastmod they were first published with -- which is the truth about them.
    touched_days = set(day_diffs["created"]) | set(day_diffs["changed"])
    for d in day_dates:
        loc = f"{SITE_BASE_URL}{day_path(d)}"
        urls.append(
            f'  <url><loc>{loc}</loc>'
            f'<lastmod>{lastmod_for(loc, d.isoformat() in touched_days)}</lastmod></url>'
        )

    for h in sorted(holidays, key=lambda h: h["slug"]):
        slug = h["slug"]
        if slug not in occurrences and not os.path.exists(
            os.path.join(site_dir, "holiday", slug, "index.html")
        ):
            # Unresolvable date AND no page was ever generated -- don't
            # advertise a URL that would 404.
            continue
        loc = f"{SITE_BASE_URL}/holiday/{slug}/"
        urls.append(
            f'  <url><loc>{loc}</loc>'
            f'<lastmod>{lastmod_for(loc, slug in touched)}</lastmod></url>'
        )
    for path in sorted(simple_pages):
        loc = f"{SITE_BASE_URL}{path}"
        urls.append(
            f'  <url><loc>{loc}</loc>'
            f'<lastmod>{lastmod_for(loc, path in simple_changed)}</lastmod></url>'
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
        "pages_skipped": sorted(page_diffs["skipped"]),
        "unresolved_holidays": sorted(unresolved, key=lambda u: u["slug"]),
        "home_changed": home_changed,
        "search_index_entries": len(search_index),
        "search_index_changed": search_changed,
        "simple_pages_total": len(simple_pages),
        "simple_pages_changed": sorted(simple_changed),
        "day_pages_total": len(day_dates),
        "day_pages_created": day_diffs["created"],
        "day_pages_changed": day_diffs["changed"],
        "day_pages_unchanged_count": day_diffs["unchanged"],
        "day_index_skipped": day_index_skipped,
        "perennial_pages_total": len(perennial_paths),
        "perennial_pages_created": perennial_diffs["created"],
        "perennial_pages_changed": perennial_diffs["changed"],
        "perennial_pages_unchanged_count": perennial_diffs["unchanged"],
        "perennial_pages_skipped": perennial_diffs["skipped"],
        "perennial_index_skipped": perennial_skipped,
        "people_dates": len(people["dates"]) if people else 0,
        "people_generated": (people.get("meta") or {}).get("generated") if people else None,
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
    ap.add_argument("--templates", default=DEFAULT_TEMPLATES_DIR,
                    help="directory holding index.html and day.html templates "
                         "(default: scripts/templates/ next to this script)")
    ap.add_argument("--people", default=DEFAULT_PEOPLE_PATH,
                    help="path to people.json, the born-on-this-day data built by "
                         "build_people.py (default: scripts/people.json; the "
                         "feature is simply off if the file is absent)")
    args = ap.parse_args()

    holidays = json.load(open(args.holidays, encoding="utf-8"))
    today = datetime.date.fromisoformat(args.today)
    people = load_people(args.people)

    report = generate(holidays, today, args.site, dry_run=args.dry_run,
                      templates_dir=args.templates, people=people)

    # people.json ages: the living lists go stale as people die. Surface it the
    # same way unresolved holidays are surfaced -- stderr always, and a workflow
    # annotation under Actions -- without failing the run.
    if people:
        generated = (people.get("meta") or {}).get("generated")
        try:
            age = (today - datetime.date.fromisoformat(generated)).days
        except (TypeError, ValueError):
            age = None
        if age is None or age > PEOPLE_STALE_DAYS:
            note = (f"scripts/people.json was generated {generated or 'on an unknown date'}"
                    + (f" ({age} days ago)" if age is not None else "")
                    + "; the living-people lists may be out of date. Re-run "
                      "python3 scripts/build_people.py and commit the result.")
            print(f"WARNING: {note}", file=sys.stderr)
            if os.environ.get("GITHUB_ACTIONS") == "true":
                print(f"::warning title=People data is stale::{note}")

    print(json.dumps(
        {k: v for k, v in report.items() if k != "occurrences"},
        indent=2, ensure_ascii=False
    ))

    # Loud warning for the one failure mode that would otherwise rot quietly:
    # a floating rule that can no longer produce a date. The run still
    # succeeds -- the rest of the site regenerates and commits -- but these
    # holidays are frozen out of the calendar until their rule is extended.
    unresolved = report["unresolved_holidays"]
    for u in unresolved:
        print(
            f"WARNING: {u['name']!r} ({u['slug']}) has no resolvable date and was "
            f"skipped -- it is missing from the calendar until this is fixed. "
            f"Cause: {u['error']}",
            file=sys.stderr,
        )
    if unresolved:
        print(
            f"WARNING: {len(unresolved)} holiday(s) skipped this run. This is "
            f"almost always a lookup_table in scripts/export_from_notion.py that "
            f"has run out of hand-confirmed years -- see scripts/README.md.",
            file=sys.stderr,
        )
        # When running in GitHub Actions, also emit a workflow command so this
        # surfaces as a visible warning annotation on the run summary instead
        # of being buried in the log. Guarded on GITHUB_ACTIONS so the "::"
        # syntax stays out of the way when run by hand. Keeping this here
        # rather than in the workflow YAML means the daily automation needs no
        # changes to pick it up.
        if os.environ.get("GITHUB_ACTIONS") == "true":
            slugs = ", ".join(u["slug"] for u in unresolved)
            print(
                f"::warning title=Holiday dates need attention::{len(unresolved)} "
                f"holiday(s) skipped this run and are missing from the calendar: "
                f"{slugs}. Most likely an expired lookup_table year in "
                f"scripts/export_from_notion.py -- see scripts/README.md."
            )

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
