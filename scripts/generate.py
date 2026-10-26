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
import io
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
# A handful do: 25 month-days have no fixed-date observance, and 6 have nothing
# at all in a ten-year window (Jan 3, Jan 6, Jan 12, Jun 11, Jul 10, Aug 31 on
# 2026-10-11 -- it was 8 the day before, and the list keeps shrinking as rows
# land, so don't treat it as fixed).
#
# True, decided by Jay 2026-10-11: publish all 366 so no date in the year 404s
# and the URL stays guessable, and because the born-on-this-day blocks and the
# coming celebrity/historic-figure dates fill these pages anyway. False
# publishes only the dates that have something; the prev/next ring and the rail
# skip the rest, and /dates/ lists them without a link. A content call either
# way, not a code change.
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

# ---- submitted occasions (E6) ----
#
# Paid listings people submit and buy a place for. They are NOT observances
# and the whole design is about keeping that true:
#
#   - they come from their own Notion database, exported by
#     scripts/export_occasions_from_notion.py to scripts/occasions.json, and
#     are never merged into `holidays`;
#   - they live at /occasions/<slug>/, never under /holiday/;
#   - they are rendered from templates/page.html, which has no JSON-LD slot at
#     all, so an occasion page cannot carry Event structured data even if a
#     later edit tried to give it some. occasion_page_html() checks the
#     rendered bytes for one anyway and refuses to write the page if it finds
#     it -- E6 asks for "cannot appear in Event structured data even if
#     misconfigured", and one belt plus one pair of braces is what that means;
#   - on a date page they sit in their own labelled block BELOW the real
#     observances, never interleaved with them, and never in that page's
#     ItemList JSON-LD (which is built from `items`, i.e. from holidays only);
#   - they are in no calendar feed, for the same reason: the feeds are built
#     from `holidays`.
#
# Absent occasions.json -> the feature is simply off and every page is
# byte-identical to what it was before E6, exactly like people.json.
DEFAULT_OCCASIONS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "occasions.json"
)
# Launch tier only (E6). A row carrying anything else is dropped with a
# warning rather than rendered by guesswork.
OCCASION_TIERS = ("Listed",)
OCCASION_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# The two disclosure lines. Saying this plainly is not a legal formality: the
# site's whole position is that it is the trustworthy one, and an unlabelled
# paid listing sitting next to Thanksgiving would cost more than the listing
# is worth. Checkiday sells rank inside the real list; this is the opposite.
OCCASIONS_LIST_NOTICE = (
    "Paid listings submitted by readers and businesses, each reviewed before "
    "publication. They are not national, international or official "
    "observances and are not part of the calendar above."
)
OCCASIONS_PAGE_NOTICE = (
    "This is a submitted occasion: a paid listing, reviewed before "
    "publication. It is not a national, international or official "
    "observance, and it is not part of the Today Celebrates calendar."
)

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


# ---- calendar export (E5) ----
#
# Three kinds of iCalendar file, all generated here, all static:
#   /calendar.ics                   every observance on the site
#   /category/<slug>/calendar.ics   one category
#   /holiday/<slug>/event.ics       one observance
#
# Fixed-date ("Annual") observances are one all-day VEVENT with
# RRULE:FREQ=YEARLY -- exactly what the page already claims ("Every year on
# March 14"), recurring forever at the cost of one event.
#
# Rule-dated ("Floating") observances are *not* translated into RRULEs. BYDAY
# can express "third Sunday in June", but nothing in RFC 5545 can express an
# Easter offset, an almanac lookup table, "the day after Thanksgiving" or
# "the next Friday the 13th" -- and a feed that re-expressed the rules it
# could in a second language would be a second implementation of the
# recurrence engine, free to disagree with the site. So they are enumerated
# date by date out of the same index pass the perennial date pages use: a date
# in a feed is a date the site shows, by construction. The window is therefore
# PERENNIAL_YEARS wide (ten years) and rolls forward with every daily
# regeneration, so a subscriber is never near its end.
#
# All-day events are DATE-valued, so they carry no time and no timezone, and
# the files need no VTIMEZONE: Christmas is December 25 wherever the subscriber
# is. Attaching a timezone to these would be actively wrong -- it would shift
# every holiday by a day for anyone far enough east or west of whichever zone
# we picked.

# DTSTAMP is a fixed build stamp rather than "now", for the same reason the
# sitemap carries each URL's lastmod forward: ~2,450 event files whose only
# daily change was a timestamp would churn the repo and the CDN every night and
# tell every subscriber that everything had been revised when nothing had.
# Bump it (and SEQUENCE with it) when the output's shape changes in a way
# clients should notice.
ICS_DTSTAMP = "20261014T000000Z"
ICS_SEQUENCE = 0
ICS_PRODID = "-//Today Celebrates//Site Generator//EN"

# Asked of subscribing clients: re-fetch daily, which is how often the site is
# rebuilt. REFRESH-INTERVAL is RFC 7986; X-PUBLISHED-TTL is what Outlook reads.
ICS_REFRESH = "P1D"


# ---- share cards (E7) ----
#
# One 1200x630 PNG per page, drawn at build time in the site's own palette,
# written beside its page as card.png and used as that page's og:image,
# twitter:image and (on an observance page) Event JSON-LD image.
#
# Why: every page today shares one of 14 stock hero photographs, so a link to
# National Pizza Day and a link to Thanksgiving look identical in a feed. The
# card carries the page's own subject and the wordmark, which is the part that
# actually travels.
#
# Five page types carry one: the observance pages (/holiday/<slug>/), the
# dated and perennial date pages, the year indexes and the category pages.
# All five are the same card grammar -- band, wordmark, pill, headline, one
# muted line, rule, domain -- with different slot contents, drawn by
# card_render() and filled by the five *_card_png_bytes() callers. The pages
# that are still on the stock hero are the home page, /dates/, /categories/,
# /about/ and the occasion pages.
#
# OFF by default, and that gate is deliberate rather than unfinished: turning
# it on adds a Pillow dependency to the daily GitHub Action and ~3,200 binary
# files to the repo, and both of those are deployment decisions (see
# "Share cards (E7)" in scripts/README.md). With cards off -- or with Pillow
# or the pinned font absent -- every file this generator writes is
# byte-identical to a build without the feature and the pages keep their stock
# hero image.
SHARE_CARDS = False
CARD_W, CARD_H = 1200, 630          # the og:image aspect every platform crops to
CARD_STRIPE_H = 16                  # the header's four-colour band, .site-head::before

# Pinned faces, not "whatever sans this box has". A PNG's bytes depend on the
# exact font file, so a second machine with a different face would rewrite all
# 2,450 cards and churn the repo. If none of the candidates exists the feature
# disables itself with a warning rather than substituting a face.
CARD_FONT_FILES = {
    "bold": (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    ),
    "regular": (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ),
}

# site.css's :root, as RGB. Colour is fill, never thin text: the headline and
# the wordmark are --ink on white, exactly as on the page.
CARD_PAPER = (255, 255, 255)
CARD_INK = (35, 25, 66)        # --ink    #231942
CARD_MUTED = (91, 85, 117)     # --muted  #5b5575
CARD_CORAL = (255, 138, 99)    # --coral  #ff8a63
CARD_SUN = (255, 209, 102)     # --sun    #ffd166
CARD_MINT = (143, 227, 207)    # --mint   #8fe3cf
CARD_LILAC = (205, 180, 255)   # --lilac  #cdb4ff
CARD_STRIPE = (CARD_CORAL, CARD_SUN, CARD_MINT, CARD_LILAC)
# CATEGORY_STYLE's pill class -> the same fill the pill uses on the page, so a
# card and its page agree about what colour a category is.
CARD_PASTEL = {"cor": CARD_CORAL, "sun": CARD_SUN, "mnt": CARD_MINT, "lil": CARD_LILAC}

# Flat art in a handful of colours: a palette PNG is a third the size of an
# RGB one and visually identical. 64 keeps the antialiasing on the headline
# smooth.
CARD_PNG_COLORS = 64

CARD_MARGIN = 64
CARD_NAME_SIZES = (92, 82, 74, 66, 58, 52, 46)
# The headline sits in the band between the date pill and the muted line,
# vertically centred in it, so a one-word name and a three-line one both look
# placed rather than top-aligned against a pool of white.
CARD_NAME_TOP = 248
CARD_NAME_MAX_H = 248


def ics_host():
    """The site host, for webcal:// links (same host, different scheme)."""
    return SITE_BASE_URL.split("://", 1)[1]


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


def year_index_path(year):
    """/holidays/2027/ -- the index of one year of the dated archive.

    Plural, and deliberately not under /day/: /holiday/<slug>/ is one
    observance and /day/<date>/ is one date, so a year index needed a segment
    of its own rather than a path that reads like either of them.
    """
    return f"/holidays/{year}/"


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

# ---- observance type (E4) ----
#
# Notion's "Type" select, in priority order. The rank is what day lists sort
# by, so Thanksgiving leads its date over National Pumpkin Day whatever Order
# says. This order is the one listed in section 5 of docs/EXECUTION_PLAN.md,
# read as a priority order.
#
# A row with NO type sorts after every typed row and renders exactly as it did
# before this taxonomy existed: no data-t, no class, no chip. That is what lets
# the ~2,450 rows be typed over several runs -- a date with nothing typed on it
# regenerates byte-identical. Order is still the tiebreaker inside a type, so
# the curation already in Notion decides between two Fun days; the taxonomy
# only overrules it between two rows of different kinds.
#
# The slug is the CSS hook (tr.t-federal, span.tg-federal) and the value the
# home page's inline script reads. Which tiers read as "major" is decided in
# public/styles/site.css, in one rule, not here.
TYPE_ORDER = (
    "Federal", "State", "Religious", "Cultural", "Observance",
    "Season & Clock", "Fun",
)
TYPE_SLUG = {
    "Federal": "federal",
    "State": "state",
    "Religious": "religious",
    "Cultural": "cultural",
    "Observance": "observance",
    "Season & Clock": "season-clock",
    "Fun": "fun",
}
TYPE_RANK = {name: i for i, name in enumerate(TYPE_ORDER)}
UNKNOWN_TYPE_RANK = len(TYPE_ORDER)      # a Type option added in Notion, not here
UNTYPED_RANK = len(TYPE_ORDER) + 1       # no Type at all -- sorts last


def type_slug(holiday):
    """'' for an untyped row, and for a Type this file does not know about.

    An unknown option is rendered as untyped rather than guessed at, and
    generate() reports it so the run says so out loud instead of silently
    dropping a tier someone added in Notion."""
    return TYPE_SLUG.get(holiday.get("type") or "", "")


def type_rank(holiday):
    t = holiday.get("type")
    if not t:
        return UNTYPED_RANK
    return TYPE_RANK.get(t, UNKNOWN_TYPE_RANK)


def obs_sort_key(holiday):
    """How every day list is ordered: type, then the hand-set Order, then name."""
    return (type_rank(holiday), holiday.get("display_order", 999), holiday["name"])


def type_tag(holiday):
    """The small uppercase chip after the name. '' for an untyped row."""
    slug = type_slug(holiday)
    if not slug:
        return ""
    return f'<span class="tg tg-{slug}">{esc_text(holiday["type"])}</span>'


def type_json():
    """TYPE_SLUG for the home page's inline script (one source of truth)."""
    return json.dumps(TYPE_SLUG, ensure_ascii=False, separators=(",", ":"))


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

    A typed row (E4) also carries data-t and a t-<slug> class, and shows its
    type chip where the "Lead" label would go: on row one the type says more
    than "Lead" does, and one chip per row keeps the table quiet. An untyped
    row emits byte-for-byte what it emitted before the taxonomy existed.
    """
    name, slug = h["name"], h["slug"]
    yearly = "1" if h["recurrence"] == "Annual" else "0"
    tslug = type_slug(h)
    tattr = f' data-t="{tslug}"' if tslug else ""
    classes = (["hot"] if index == 0 else []) + ([f"t-{tslug}"] if tslug else [])
    cls = f' class="{" ".join(classes)}"' if classes else ""
    tag = type_tag(h)
    lead = '<span class="lbl">Lead</span>' if index == 0 and not tag else ""
    actions = (
        row_button("copy", f"Copy link to {name}", "link")
        + row_button("ics", f"Add {name} to calendar", "cal")
        + row_button("share", f"Share {name}", "share", " sh")
    )
    return (
        f'<tr data-u="/holiday/{slug}/" data-n="{esc_attr(name)}" data-d="{iso_date}" '
        f'data-y="{yearly}"{tattr}{cls}>'
        f'<td class="n mono">{index + 1:02d}</td>'
        f'<td class="nm"><a href="/holiday/{slug}/">{esc_attr(name)}</a>{tag}{lead}</td>'
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
# iCalendar output (E5) -- see the ICS_* constants at the top of this file for
# the recurrence model and why there is no VTIMEZONE.
# ---------------------------------------------------------------------------

def ics_text(s):
    """RFC 5545 TEXT escaping: backslash, semicolon, comma, newline.

    Colons are *not* escaped (they are legal in a TEXT value) and neither are
    quotes. Over-escaping shows up as literal backslashes in the event title in
    Apple Calendar, which is how you can tell a feed was built by hand.
    """
    return (str(s).replace("\\", "\\\\")
                  .replace(";", "\\;")
                  .replace(",", "\\,")
                  .replace("\r\n", "\\n")
                  .replace("\n", "\\n")
                  .replace("\r", "\\n"))


def ics_fold(line):
    """Fold one content line to RFC 5545's 75-octet limit.

    The limit is octets, not characters, and a fold must never land inside a
    multi-byte UTF-8 sequence -- so this measures bytes and only breaks between
    characters. Continuation lines start with one space, which itself counts
    toward the 75, hence the 74 after the first break.
    """
    if len(line.encode("utf-8")) <= 75:
        return line
    pieces, chunk, size, limit = [], [], 0, 75
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > limit:
            pieces.append("".join(chunk))
            chunk, size, limit = [], 0, 74
        chunk.append(ch)
        size += n
    pieces.append("".join(chunk))
    return "\r\n ".join(pieces)


def ics_date(d):
    return f"{d.year:04d}{d.month:02d}{d.day:02d}"


def ics_uid(slug, date=None):
    """A UID that survives regeneration.

    One UID per fixed-date observance -- its RRULE covers every year, so the
    event is the same event forever. One UID per enumerated occurrence for a
    rule-dated observance, so if a date is corrected or a lookup table gains a
    year, exactly that occurrence is replaced in the subscriber's calendar and
    nothing else moves.
    """
    stem = f"{slug}-{ics_date(date)}" if date else slug
    return f"{stem}@{ics_host()}"


def ics_event(holiday, start, yearly=False):
    """One all-day VEVENT as a list of unfolded content lines."""
    slug = holiday["slug"]
    url = f"{SITE_BASE_URL}/holiday/{slug}/"
    # DTEND is exclusive for DATE values: a one-day event ends the next day.
    end = start + datetime.timedelta(days=1)
    lines = [
        "BEGIN:VEVENT",
        f"UID:{ics_uid(slug, None if yearly else start)}",
        f"DTSTAMP:{ICS_DTSTAMP}",
        f"DTSTART;VALUE=DATE:{ics_date(start)}",
        f"DTEND;VALUE=DATE:{ics_date(end)}",
        f"SUMMARY:{ics_text(holiday['name'])}",
    ]
    if yearly:
        lines.append("RRULE:FREQ=YEARLY")
    lines += [
        f"DESCRIPTION:{ics_text(holiday['description'])}\\n\\n{url}",
        f"URL;VALUE=URI:{url}",
        f"CATEGORIES:{ics_text(cat_title(holiday['category']))}",
        # A holiday does not make the subscriber busy.
        "TRANSP:TRANSPARENT",
        "CLASS:PUBLIC",
        f"SEQUENCE:{ICS_SEQUENCE}",
        "END:VEVENT",
    ]
    return lines


def ics_calendar(name, description, path, events):
    """Wrap VEVENT line-lists into one iCalendar object, CRLF-terminated.

    NAME / DESCRIPTION / REFRESH-INTERVAL / SOURCE are RFC 7986; the X-WR-*
    twins are the older spellings Google Calendar and Outlook actually read, so
    both go in. SOURCE is the https URL the feed can be re-fetched from.
    """
    out = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{ICS_PRODID}",
        "CALSCALE:GREGORIAN",
        f"NAME:{ics_text(name)}",
        f"X-WR-CALNAME:{ics_text(name)}",
        f"DESCRIPTION:{ics_text(description)}",
        f"X-WR-CALDESC:{ics_text(description)}",
        f"URL;VALUE=URI:{SITE_BASE_URL}{path}",
        f"SOURCE;VALUE=URI:{SITE_BASE_URL}{path}",
        f"REFRESH-INTERVAL;VALUE=DURATION:{ICS_REFRESH}",
        f"X-PUBLISHED-TTL:{ICS_REFRESH}",
    ]
    for ev in events:
        out.extend(ev)
    out.append("END:VCALENDAR")
    return "".join(ics_fold(line) + "\r\n" for line in out)


def write_bytes_if_changed(path, content, dry_run=False):
    """write_if_changed's twin for CRLF text.

    The .ics files must be compared and written as bytes: read back in text
    mode, Python would translate their CRLFs to LF, every comparison would
    report a change, and all ~2,470 feed files would be rewritten on every run.
    """
    data = content.encode("utf-8")
    old = None
    if os.path.exists(path):
        with open(path, "rb") as f:
            old = f.read()
    changed = old != data
    if changed and not dry_run:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    return changed, old is None


def write_raw_if_changed(path, data, dry_run=False):
    """write_bytes_if_changed's twin for data that is already bytes.

    Used for the PNG share cards: there is nothing to encode, and a card whose
    date has not rolled must not be rewritten (2,450 rewritten images a night
    would churn the repo and tell every CDN that everything had changed).
    """
    old = None
    if os.path.exists(path):
        with open(path, "rb") as f:
            old = f.read()
    changed = old != data
    if changed and not dry_run:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    return changed, old is None


def card_rel_path(slug):
    """The card sits inside the page's own directory, like its event.ics."""
    return f"/holiday/{slug}/card.png"


def card_rel_for(page_path):
    """The same convention for every other page type that has a card.

    The image lives beside the page it belongs to, exactly as `event.ics`
    does, so `/day/2026-10-08/` gets `/day/2026-10-08/card.png`. Used by the
    dated, perennial, year-index and category pages; every one of those paths
    already ends in a slash.
    """
    return f"{page_path}card.png"


def card_pastel(category):
    """The fill this category's pill uses on the page, as RGB."""
    return CARD_PASTEL.get(cat_pill_class(category), CARD_LILAC)


_CARD_STATE = None


def card_fonts():
    """(loader, None) or (None, reason).

    `loader(face, size)` returns a cached PIL font. The answer cannot change
    inside one run, so it is worked out once: either both pinned faces and
    Pillow are present, or cards are off and the reason says why.
    """
    global _CARD_STATE
    if _CARD_STATE is not None:
        return _CARD_STATE
    try:
        from PIL import ImageFont
    except ImportError:
        _CARD_STATE = (None, "Pillow is not installed in this environment "
                             "(python3 -m pip install Pillow)")
        return _CARD_STATE
    chosen = {}
    for face, candidates in CARD_FONT_FILES.items():
        for path in candidates:
            if os.path.exists(path):
                chosen[face] = path
                break
        else:
            _CARD_STATE = (None, f"no pinned {face} font file found; looked for "
                                 + ", ".join(candidates))
            return _CARD_STATE
    cache = {}

    def loader(face, size):
        key = (face, size)
        if key not in cache:
            cache[key] = ImageFont.truetype(chosen[face], size)
        return cache[key]

    _CARD_STATE = (loader, None)
    return _CARD_STATE


def card_wrap(draw, text, font, max_w):
    """Greedy word wrap at pixel width. A single word wider than the box gets
    its own line and is ellipsized later rather than silently overflowing."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and draw.textlength(trial, font=font) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [""]


def card_ellipsize(draw, text, font, max_w):
    if draw.textlength(text, font=font) <= max_w:
        return text
    cut = text
    while cut and draw.textlength(cut + "…", font=font) > max_w:
        cut = cut[:-1]
    return (cut.rstrip() + "…") if cut else ""


def card_fit(draw, text, loader, face, sizes, max_w, max_lines, max_h):
    """Largest size from `sizes` whose wrap fits the box in both axes."""
    for size in sizes:
        font = loader(face, size)
        lines = card_wrap(draw, text, font, max_w)
        if (len(lines) <= max_lines
                and len(lines) * round(size * 1.12) <= max_h
                and all(draw.textlength(ln, font=font) <= max_w for ln in lines)):
            return font, lines
    # Nothing fits: smallest size, clipped to the line budget, last line
    # ellipsized. A name long enough to reach here is a data problem, and a
    # clipped card is still a card.
    font = loader(face, sizes[-1])
    lines = card_wrap(draw, text, font, max_w)[:max_lines]
    lines = [card_ellipsize(draw, ln, font, max_w) for ln in lines]
    return font, lines


def card_draw_tracked(draw, xy, text, font, fill, track=0.0):
    """Letter-spaced text, for the wordmark only."""
    x, y = xy
    if not track:
        draw.text((x, y), text, font=font, fill=fill)
        return
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track


def card_render(loader, pill_text, pill_colour, headline, subline):
    """One share card, as PNG bytes: the band, the wordmark, a pill, the
    headline, one muted line, the rule and the domain.

    Every card type is that same grammar with different slot contents, which
    is what keeps a date's card and an observance's card recognizably the same
    object. The callers below fill the slots; nothing here knows what kind of
    page it is drawing for.

    Deterministic: the same arguments render the same bytes, which is what
    lets write_raw_if_changed leave an unchanged card alone.
    """
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (CARD_W, CARD_H), CARD_PAPER)
    d = ImageDraw.Draw(img)
    M = CARD_MARGIN
    inner_w = CARD_W - 2 * M

    # The header's four-colour band.
    band = CARD_W / len(CARD_STRIPE)
    for i, colour in enumerate(CARD_STRIPE):
        d.rectangle([round(i * band), 0, round((i + 1) * band) - 1,
                     CARD_STRIPE_H - 1], fill=colour)

    # Wordmark: the coral .mark square with its offset shadow, then the name.
    mark, my = 34, 72
    d.rectangle([M + 5, my + 5, M + mark + 5, my + mark + 5], fill=CARD_INK)
    d.rectangle([M, my, M + mark, my + mark], fill=CARD_CORAL,
                outline=CARD_INK, width=3)
    f_brand = loader("bold", 26)
    card_draw_tracked(d, (M + mark + 20, my + 3), "TODAY CELEBRATES",
                      f_brand, CARD_INK, track=2.5)

    # The pill: a date on an observance's or a date page's card, the scope on
    # the others, filled in whatever colour that page uses for its subject.
    f_date = loader("bold", 27)
    pill_y = 168
    pill_w = min(d.textlength(pill_text, font=f_date) + 44, inner_w)
    d.rounded_rectangle([M, pill_y, M + pill_w, pill_y + 56], radius=8,
                        fill=pill_colour, outline=CARD_INK, width=3)
    d.text((M + 22, pill_y + 13), pill_text, font=f_date, fill=CARD_INK)

    # Headline.
    f_name, lines = card_fit(d, headline, loader, "bold",
                             CARD_NAME_SIZES, inner_w, 3, CARD_NAME_MAX_H)
    line_h = round(f_name.size * 1.12)
    y = CARD_NAME_TOP + max(0, (CARD_NAME_MAX_H - len(lines) * line_h) // 2)
    for line in lines:
        d.text((M, y), line, font=f_name, fill=CARD_INK)
        y += line_h

    # One muted line: this card's secondary fact, whatever its subject is.
    f_sub = loader("regular", 26)
    sub = card_ellipsize(d, subline, f_sub, inner_w)
    d.text((M, 512), sub, font=f_sub, fill=CARD_MUTED)

    # Footer rule and the domain, in the page's own hard-rule idiom.
    d.rectangle([M, 562, CARD_W - M, 564], fill=CARD_INK)
    f_foot = loader("bold", 27)
    d.text((M, 582), "todaycelebrates.com", font=f_foot, fill=CARD_INK)

    out = img.convert("P", palette=Image.ADAPTIVE, colors=CARD_PNG_COLORS)
    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def card_png_bytes(holiday, occ_date, loader):
    """The card for one /holiday/<slug>/ page: the observance's own name."""
    cat = holiday.get("category") or "celebration"
    pill = (f"{WEEKDAY_NAMES[occ_date.weekday()]}, "
            f"{MONTH_NAMES[occ_date.month]} {occ_date.day}, "
            f"{occ_date.year}").upper()
    if holiday.get("recurrence") == "Annual":
        if holiday.get("month") == 2 and holiday.get("day") == 29:
            recurs = "Every February 29, in leap years"
        else:
            recurs = (f"Every year on {MONTH_NAMES[occ_date.month]} "
                      f"{occ_date.day}")
    else:
        recurs = "The date changes each year"
    return card_render(loader, pill, card_pastel(cat), holiday["name"],
                       f"{cat_title(cat)} · {recurs}")


def day_card_png_bytes(date, items, loader):
    """The card for a /day/YYYY-MM-DD/ page.

    The headline is the count in the words the page's own <title> uses, not
    the lead observance's name -- a dated page whose card said "Halloween"
    would be indistinguishable from Halloween's own card, and would promise a
    reader the wrong page. The names go on the muted line instead.
    """
    n = len(items)
    pill = (f"{WEEKDAY_NAMES[date.weekday()]}, {MONTH_NAMES[date.month]} "
            f"{date.day}, {date.year}").upper()
    cat = (items[0].get("category") or "celebration") if items else "celebration"
    return card_render(
        loader, pill, card_pastel(cat),
        f"{n} {plural(n, 'Holiday')} & Observances",
        join_names([h["name"] for h in items[:3]]) if items else "",
    )


def perennial_card_png_bytes(month, day, annual, floating, loader):
    """The card for a /<month>-<day>/ page.

    The pill carries the month-day with no year, which is the whole
    difference between this page and the dated one -- so it is the difference
    between their two cards too.
    """
    label = month_day_label(month, day)
    n, nf = len(annual), len(floating)
    cat = (annual[0].get("category") or "celebration") if annual else "celebration"
    if n:
        headline = f"{n} {plural(n, 'Holiday')} & Observances"
        sub = join_names([h["name"] for h in annual[:3]])
    elif nf:
        headline = "Nothing Every Year"
        sub = (f"{nf} rule-dated {plural(nf, 'observance')} "
               f"{plural(nf, 'lands', 'land')} on {label} in some years")
    else:
        headline = "No Observances on Record"
        sub = "The site keeps a page for every date of the calendar"
    return card_render(loader, f"EVERY {label}".upper(), card_pastel(cat),
                       headline, sub)


def year_card_png_bytes(year, loader):
    """The card for a /holidays/<year>/ page.

    Carries no count and no coverage range on purpose. Both move every time
    the archive's forward horizon rolls, which is most nights, and a card that
    is rewritten nightly is a repo diff and a CDN invalidation for nothing.
    The page itself states its own coverage.
    """
    return card_render(loader, f"THE {year} CALENDAR", CARD_LILAC,
                       f"Holidays and observances in {year}",
                       "A date-by-date index of every day with something "
                       "on the calendar")


def category_card_png_bytes(category, count, loader):
    """The card for a /category/<slug>/ page, in that category's own colour."""
    title = cat_title(category)
    return card_render(loader, title.upper(), card_pastel(category),
                       f"{title} holidays and observances",
                       f"{count} {plural(count, 'observance')} in this "
                       f"category, A to Z")


def cal_links_html(holiday, occurrence_count):
    """The "Add to your calendar" line on a /holiday/<slug>/ page."""
    ics = f"/holiday/{holiday['slug']}/event.ics"
    webcal = f"webcal://{ics_host()}{ics}"
    if holiday["recurrence"] == "Annual":
        note = "The event repeats every year."
    elif occurrence_count:
        note = (f"This date moves, so the file carries the next "
                f"{occurrence_count} {plural(occurrence_count, 'date')}.")
    else:
        note = ""
    return (
        f'<p class="cal"><a class="cal-add" href="{ics}">Add to your calendar</a>'
        f'<span class="cal-note">A calendar file for Apple Calendar, Google '
        f'Calendar or Outlook. {note} You can also '
        f'<a href="{webcal}">subscribe to this observance</a> or to '
        f'<a href="/calendar.ics">the whole calendar</a>.</span></p>'
    )


def cal_feed_links_html(label, path, count):
    """The subscribe line on a /category/<slug>/ page."""
    webcal = f"webcal://{ics_host()}{path}"
    return (
        f'<p class="cal"><a class="cal-add" href="{webcal}">Subscribe to '
        f'{esc_text(label)}</a>'
        f'<span class="cal-note">{count:,} observances, kept up to date in '
        f'Apple Calendar, Google Calendar or Outlook. Or '
        f'<a href="{path}">download the calendar file</a>.</span></p>'
    )


# ---------------------------------------------------------------------------
# Submitted occasions (E6) -- see the OCCASION_* constants at the top of this
# file for the constraints every one of these functions exists to hold.
# ---------------------------------------------------------------------------

def occasion_path(slug):
    return f"/occasions/{slug}/"


def load_occasions(path):
    """scripts/occasions.json -> a list of occasion dicts, or [].

    Never raises: a missing or damaged file turns the feature off for this run
    (with a warning for the damaged case) rather than failing the daily build,
    same as load_people().
    """
    if not path or not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("not a JSON list")
        return data
    except (OSError, ValueError, AttributeError) as e:
        print(f"WARNING: {path} could not be read ({e}); submitted occasions "
              f"are off for this run.", file=sys.stderr)
        return []


def validate_occasions(occasions, holiday_slugs):
    """Returns (usable, problems).

    The exporter checks all of this too. It is checked again here because
    occasions.json is a file on disk that a person can edit, and because the
    one thing that must never happen -- a paid listing passing itself off as
    an observance -- is cheap to re-check and expensive to get wrong.
    """
    usable, problems, seen = [], [], set()
    for o in occasions:
        name = (o.get("name") or "").strip() if isinstance(o, dict) else ""
        if not isinstance(o, dict) or not name:
            problems.append("an occasion entry has no name -- dropped")
            continue
        slug = (o.get("slug") or "").strip()
        if not OCCASION_SLUG_RE.match(slug):
            problems.append(f"{name!r}: slug {slug!r} is not a usable URL slug -- dropped")
            continue
        if slug in holiday_slugs:
            problems.append(
                f"{name!r}: slug {slug!r} is also a holiday slug -- dropped. A paid "
                f"listing must not share a name with a real observance."
            )
            continue
        if slug in seen:
            problems.append(f"{name!r}: duplicate slug {slug!r} -- dropped")
            continue
        if o.get("tier") not in OCCASION_TIERS:
            problems.append(
                f"{name!r}: tier {o.get('tier')!r} is not one of "
                f"{', '.join(OCCASION_TIERS)} -- dropped"
            )
            continue
        try:
            datetime.date.fromisoformat(o.get("date", ""))
        except (TypeError, ValueError):
            problems.append(f"{name!r}: date {o.get('date')!r} is not a date -- dropped")
            continue
        if not (o.get("blurb") or "").strip():
            problems.append(f"{name!r}: no blurb -- dropped")
            continue
        link = o.get("link")
        if link and not str(link).startswith(("http://", "https://")):
            problems.append(f"{name!r}: link {link!r} is not an http(s) URL -- link dropped")
            o = {k: v for k, v in o.items() if k != "link"}
        seen.add(slug)
        usable.append(o)
    usable.sort(key=lambda o: (o["date"], o["name"].lower(), o["slug"]))
    return usable, problems


def occasions_block_html(occasions):
    """The labelled block of paid listings, below a date page's observances."""
    if not occasions:
        return ""
    lis = "".join(
        f'<li><a href="{occasion_path(o["slug"])}">{esc_text(o["name"])}</a>'
        f'<span class="occ-blurb">{esc_text(o["blurb"])}</span></li>'
        for o in sorted(occasions, key=lambda o: (o["name"].lower(), o["slug"]))
    )
    return (
        '<section class="occ" aria-labelledby="occ-h">'
        '<h2 class="eyebrow" id="occ-h">Submitted occasions</h2>'
        f'<p class="occ-notice">{OCCASIONS_LIST_NOTICE}</p>'
        f'<ul class="occ-list">{lis}</ul>'
        "</section>"
    )


def occasion_body_html(o, published_days):
    """The body of one /occasions/<slug>/ page."""
    d = datetime.date.fromisoformat(o["date"])
    when = esc_text(long_date(d))
    if o.get("recurs"):
        when += f" &middot; and every {esc_text(month_day(d))} after it"
    parts = [
        '<div class="plain">',
        f'<p class="occ-notice">{OCCASIONS_PAGE_NOTICE}</p>',
        f'<p class="occ-when"><strong>{when}</strong></p>',
        f"<p>{esc_text(o['blurb'])}</p>",
    ]
    if o.get("body"):
        parts.extend(render_md_blocks(md_blocks(o["body"]), indent=""))
    if o.get("link"):
        href = esc_href(esc_text(o["link"]))
        # rel="sponsored nofollow": this link was paid for. Declaring that is
        # Google's documented requirement for paid links, and passing ranking
        # signals to whoever bought a listing is precisely the business this
        # site is not in.
        parts.append(
            f'<p><a href="{href}" rel="sponsored nofollow noopener">'
            f"{esc_text(o['link'])}</a></p>"
        )
    links = [
        f'<a href="{perennial_path(d.month, d.day)}">What else falls on '
        f"{esc_text(month_day(d))}</a>"
    ]
    if d in published_days:
        links.append(f'<a href="{day_path(d)}">{esc_text(long_date(d))} in full</a>')
    parts.append("<p>" + " &middot; ".join(links) + "</p>")
    parts.append("</div>")
    return "".join(parts)


def occasion_page_html(o, page_template, chrome, published_days):
    """Returns (html, problem_or_None).

    The Event check is the fail-safe for E6's "cannot appear in Event
    structured data even if misconfigured": page.html has no JSON-LD slot, so
    this can only fire if someone changes the template or this function, and
    when it fires the page is not written at all.
    """
    name = o["name"]
    d = datetime.date.fromisoformat(o["date"])
    html_out = render_simple_page(
        page_template, chrome,
        title=f"{name}: a submitted occasion | Today Celebrates",
        description=(
            f"{name} — a submitted, paid listing for {long_date(d)}. "
            f"Not a national or official observance."
        ),
        path=occasion_path(o["slug"]),
        headline=name,
        body=occasion_body_html(o, published_days),
        side="",
        crumbs=crumbs_html(("Submitted occasions", "/occasions/"), (name, None)),
    )
    if re.search(r'"@type"\s*:\s*"Event"', html_out):
        return None, (
            f"{name!r}: the rendered occasion page contains Event structured "
            f"data, which a paid listing must never carry. Page NOT written. "
            f"This is a code or template bug -- see E6 in docs/EXECUTION_PLAN.md."
        )
    return html_out, None


def occasions_index_body(occasions, today):
    """The body of /occasions/, the directory of every live paid listing."""
    rows = []
    for o in occasions:
        d = datetime.date.fromisoformat(o["date"])
        rows.append(
            f'<li><a href="{occasion_path(o["slug"])}">'
            f"<span>{esc_text(o['name'])}</span>"
            f'<span class="mono">{MONTH_ABBR[d.month]} {d.day}</span></a></li>'
        )
    return (
        f'<p class="intro">{OCCASIONS_LIST_NOTICE}</p>'
        f'<p class="occ-notice">Every listing here was read by a person before '
        f"it went up. Nothing on this page is part of the "
        f'<a href="/dates/">calendar of observances</a>, and none of it appears '
        f"in the calendar feeds.</p>"
        f'<ul class="cat-list">{"".join(rows)}</ul>'
    )


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
                same_day=(), day_published=False, ics_dates=(), card_url=None):
    """Render one /holiday/<slug>/ page.

    `same_day` is every observance on this holiday's date (for the "Also on"
    sidebar); `day_published` says whether that date has a /day/ page to link.
    `ics_dates` is this observance's occurrences inside the calendar-feed
    window (E5), used only to say how many dates its .ics file carries.
    `card_url` is this observance's share card (E7) when cards are being
    generated this run; absent, the page keeps the stock category hero as its
    og:image exactly as before.
    """
    slug = holiday["slug"]
    name = holiday["name"]
    category = holiday["category"]
    description = holiday["description"]
    path = f"/holiday/{slug}/"
    url = f"{SITE_BASE_URL}{path}"
    image = card_url or f"{SITE_BASE_URL}/images/hero/{category}.jpg"
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
        # E3 cross-links. The perennial page is the holiday's stable parent --
        # the dated page's URL changes every year, which makes it a poor
        # breadcrumb ancestor and a poor back-link for a page that lives
        # forever at one URL. The specific dated page is still linked twice:
        # from the Date row of the spec list, and from "All N on <date>" in the
        # "Also on" sidebar.
        "CRUMBS": crumbs_html(
            ("Calendar", "/dates/"),
            (date_short, perennial_path(occ_date.month, occ_date.day)),
            (name, None),
        ),
        "DATE_SPEC": (
            f'<a href="{day_link}"><time datetime="{iso_date}">'
            f'{weekday_long_date(occ_date)}</time></a>'
            if day_published else
            f'<time datetime="{iso_date}">{weekday_long_date(occ_date)}</time>'
        ),
        "PERENNIAL_HREF": perennial_path(occ_date.month, occ_date.day),
        "LONGFORM": longform,
        "CAL_LINKS": cal_links_html(holiday, len(ics_dates)),
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
        index[d].sort(key=obs_sort_key)
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
                    chrome, day_index, published_days, people=None, occasions=(),
                    card_url=None):
    """Render one permanent /day/YYYY-MM-DD/ page.

    `occasions` is any submitted paid listing claiming this date (E6). They
    render in their own labelled block after everything else on the page and
    are deliberately absent from `items`, so they reach neither the observance
    table nor its ItemList structured data.

    `card_url` is this date's share card (E7) when cards are being generated
    this run; without one the page keeps the lead observance's stock category
    hero as its og:image, exactly as before."""
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
        "HERO_IMAGE_ABS": card_url or f"{SITE_BASE_URL}{hero_rel}",
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
        "OCCASIONS": occasions_block_html(occasions),
        "DAY_NAV": stepper,
        "DAY_PN": "".join(nav),
        "HTML_CLASS": html_class(),
        "DATE_PLAIN": esc_attr(long_date(date)),
        "LD_JSON": ld_json,
        "SHARE_TITLE": esc_attr(share_title),
        "SHARE_TEXT": esc_attr(share_text),
        "SHARE_LINKS": share_links(path, share_title),
        "WEEK_LIST": week_list_html(date, day_index, published_days),
        # The dated page's two upward links, both derived from the date alone
        # so a past dated page still regenerates byte-identically: the
        # perennial page for this month-day, and the index of this year's
        # archive. YEAR_LINK is what keeps the /holidays/<year>/ pages
        # reachable from the 351 pages they index, rather than only from the
        # /dates/ hub.
        "YEAR_LINK": (
            f'<p>For every date on record in {date.year}, see '
            f'<a href="{year_index_path(date.year)}">'
            f'{date.year} holidays and observances</a>.</p>'
        ),
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
        annual = sorted(bucket["annual"].values(), key=obs_sort_key)
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


def dates_hub_html(perennial_index, month_days, published, year_links=""):
    """/dates/ -- the hub for the 366 perennial pages. Returns (body, side).

    Why this page exists: 366 pages reachable only from each other and from the
    sitemap are technically not orphaned but practically invisible, and a site
    with a nav item pointing at a homepage fragment (`/#calendar`) was spending
    a sitewide link on something no crawler can follow. One hub, linked from the
    header and the footer, puts every date one click from every page on the
    site. The homepage calendar widget is unchanged and still linked from here.

    `published` is the set of (month, day) keys that actually got a page, so
    that with `PERENNIAL_EMPTY_PAGES` off the hub still shows the whole
    calendar but renders the eight blank dates as plain text rather than as
    links to pages that were never written.
    """
    months = []
    side = []
    for m in range(1, 13):
        days = [k for k in month_days if k[0] == m]
        items = []
        total = 0
        for key in days:
            n = len(perennial_index[key]["annual"])
            total += n
            count = f"{n} {plural(n, 'observance')}" if n else "moveable dates only"
            if not n and not perennial_index[key]["floating"]:
                count = "nothing on record"
            label = esc_attr(month_day_label(*key))
            if key in published:
                items.append(
                    f'<li><a href="{perennial_path(*key)}">'
                    f'<span>{label}</span>'
                    f'<span class="mono">{count}</span></a></li>'
                )
            else:
                items.append(
                    f'<li><span class="cat-list-off"><span>{label}</span>'
                    f'<span class="mono">{count}</span></span></li>'
                )
        months.append(
            f'<h2 id="{MONTH_NAMES[m].lower()}">{MONTH_NAMES[m]}</h2>'
            f'<ul class="cat-list">{"".join(items)}</ul>'
        )
        side.append(
            f'<li><a href="#{MONTH_NAMES[m].lower()}"><span>{MONTH_NAMES[m]}</span>'
            f'<span class="mono">{total}</span></a></li>'
        )

    body = (
        '<div class="plain">'
        '<p class="intro">Every date of the year has a page of its own, listing '
        "what falls on it in any year. Dates set by a rule &mdash; the last Monday "
        "of May, or a number of days after Easter &mdash; are named on the date "
        "they land on, with the years they land there.</p>"
        '<p class="intro">Looking for one particular year instead? Each date page '
        'links to the dated record for that year'
        + (f", and the archive has a year at a time: {year_links}" if year_links else "")
        + '. Or <a href="/#calendar">pick a '
        'date on the calendar</a> on the home page.</p>'
        + "".join(months)
        + "</div>"
    )
    side_html = (
        f'<h2>Months</h2><ul class="list-side">{"".join(side)}</ul>'
    )
    return body, side_html


def year_index_html(year, dates, day_index, years, gaps):
    """/holidays/<year>/ -- the index of one year of the dated archive.

    E3's fourth bullet, and the one page type the site was missing. `/dates/`
    indexes the 366 year-less pages; this indexes one year's
    `/day/YYYY-MM-DD/` pages, which is a different question over a different
    set of URLs. Until now those pages were reachable one day at a time --
    prev/next, the week rail in the sidebar, the homepage calendar widget and
    the sitemap -- so there was no page on the site from which a reader or a
    crawler could see a year of the archive at once.

    Both ends of the archive are partial: it opens at DAY_ARCHIVE_START and
    ends at a derived horizon (see "The dated archive's forward horizon is
    derived, not configured" in scripts/README.md). So the page states its
    coverage in a sentence instead of rendering twelve month headings with
    nine of them empty -- someone who came looking for March 2026 needs to be
    told the record does not reach back that far, not handed an empty March.

    `gaps` is the number of dates inside the covered span that have no page,
    which happens when nothing at all is on the calendar for that date.

    Returns (body, side). Reuses the /dates/ hub's markup exactly -- the
    `.plain` wrapper, `.cat-list` two-column list and `.list-side` rail -- so
    this page type needs no CSS of its own.
    """
    by_month = {}
    for d in dates:
        by_month.setdefault(d.month, []).append(d)

    months_html = []
    side_months = []
    for m in sorted(by_month):
        items = []
        for d in by_month[m]:
            n = len(day_index.get(d, []))
            items.append(
                f'<li><a href="{day_path(d)}">'
                f'<span>{esc_attr(weekday_month_day(d))}</span>'
                f'<span class="mono">{n} {plural(n, "observance")}</span></a></li>'
            )
        anchor = MONTH_NAMES[m].lower()
        months_html.append(
            f'<h2 id="{anchor}">{MONTH_NAMES[m]} {year}</h2>'
            f'<ul class="cat-list">{"".join(items)}</ul>'
        )
        nd = len(by_month[m])
        side_months.append(
            f'<li><a href="#{anchor}"><span>{MONTH_NAMES[m]}</span>'
            f'<span class="mono">{nd}</span></a></li>'
        )

    first, last = dates[0], dates[-1]
    if first == last:
        # The case the forward horizon produces every time it crosses a New
        # Year: the far year opens with one date on record. "runs from
        # January 1 to January 1" would be a silly way to say that.
        cover = [
            f"The record for {year} is one date so far, "
            f"{esc_attr(long_date(first))}."
        ]
    else:
        cover = [
            f"The record for {year} runs from {esc_attr(long_date(first))} to "
            f"{esc_attr(long_date(last))}, {len(dates)} "
            f"{plural(len(dates), 'day')} in all."
        ]
    if (first.month, first.day) != (1, 1):
        cover.append(
            f"The dated archive opens on "
            f"{esc_attr(long_date(DAY_ARCHIVE_START))}, so earlier dates in "
            f"{year} have no dated page."
        )
    if (last.month, last.day) != (12, 31):
        cover.append(
            f"It reaches about a year ahead and extends a day at a time, so "
            f"later dates in {year} appear here as they come into range."
        )
    if gaps:
        cover.append(
            f"{gaps} {plural(gaps, 'date')} inside that range "
            f"{plural(gaps, 'has', 'have')} nothing on the calendar and so "
            f"{plural(gaps, 'has', 'have')} no page; "
            f"{plural(gaps, 'it is', 'they are')} not listed."
        )

    year_nav = []
    for y in years:
        if y == year:
            year_nav.append(f'<span aria-current="page">{y}</span>')
        else:
            year_nav.append(f'<a href="{year_index_path(y)}">{y}</a>')

    body = (
        '<div class="plain">'
        f'<p class="intro">Every date in {year} with a record on Today '
        f"Celebrates, month by month. Each entry links to that day&rsquo;s "
        f"page: the national, international and world observances on the "
        f"calendar for it, with the weekday and the ones whose date moved."
        "</p>"
        f'<p class="intro">{" ".join(cover)}</p>'
        + "".join(months_html)
        + '<div class="note">'
        f'<p>The dated record by year: {" &middot; ".join(year_nav)}.</p>'
        '<p>For what falls on a calendar date in <em>any</em> year, see '
        '<a href="/dates/">every date of the year</a>.</p>'
        "</div>"
        "</div>"
    )
    side = (
        f'<h2>{year}</h2><ul class="list-side">{"".join(side_months)}</ul>'
    )
    return body, side


def render_perennial_page(key, bucket, prev_key, next_key, template, chrome,
                          month_days, perennial_index, dated, today, people=None,
                          occasions=(), card_url=None):
    """Render one permanent /<month>-<day>/ page.

    `occasions` is the submitted paid listings that recur on this month-day
    (E6); a one-off listing appears only on its dated page. Same separation as
    on the dated pages: own block, below everything, never in the table.

    `card_url` is this date's share card (E7) when cards are being generated
    this run; without one the page keeps its stock category hero."""
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
        "HERO_IMAGE_ABS": card_url or f"{SITE_BASE_URL}{hero_rel}",
        "CRUMBS": crumbs_html(("Calendar", "/dates/"), (label, None)),
        "EYEBROW": esc_attr(f"EVERY {label}").upper(),
        "HEADLINE": esc_attr(share_title),
        "INTRO": intro,
        "LIST_BLOCK": list_block,
        "MOVES_NOTE": perennial_moves_html(label, floating),
        "PEOPLE_BLOCK": people_block_html(
            people, month, day, PEOPLE_PERENNIAL_LIMIT, full_page=True
        ),
        "YEARS_NOTE": perennial_years_html(label, dated),
        "OCCASIONS": occasions_block_html(occasions),
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
        "TYPE_JSON": type_json(),
        **chrome,
    })


def render_simple_page(template, chrome, *, title, description, path, headline,
                       body, side="", crumbs="", image=None):
    """/about/, /categories/, /category/<slug>/, /dates/, the year indexes and
    the occasion pages.

    `image` overrides the stock og:image; the year-index and category pages
    pass their own share card (E7) when cards are being generated this run.
    """
    return fill(template, {
        "HTML_CLASS": html_class(),
        "TITLE": esc_attr(title),
        "DESCRIPTION": esc_attr(description),
        "URL": f"{SITE_BASE_URL}{path}",
        "IMAGE_ABS": image or f"{SITE_BASE_URL}/images/hero/celebration.jpg",
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
        "to calendar link: it downloads a calendar file you can open in Apple "
        "Calendar, Google Calendar or Outlook, and observances with a fixed date "
        "repeat every year.</p>"
        "<h2>Subscribe to the calendar</h2>"
        '<p>The whole calendar is published as a subscribable feed: '
        f'<a href="webcal://{ics_host()}/calendar.ics">subscribe to every '
        "observance</a> and the dates appear in your own calendar, updated "
        'every day, or <a href="/calendar.ics">download the file</a> instead. '
        'Each <a href="/categories/">category</a> has a feed of its own, and so '
        "does every single observance. Observances with a fixed date repeat "
        "every year; ones set by a rule carry their next ten dates, and the "
        "feed refreshes as the years roll on.</p>"
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
             people=None, occasions=None, cards=SHARE_CARDS):
    """Returns a report dict describing what changed.

    `people` is the parsed scripts/people.json (see load_people), or None to
    render the date pages without the "born on this day" blocks.
    `occasions` is the parsed scripts/occasions.json (see load_occasions), or
    None for no submitted occasions -- in which case every page this function
    writes is byte-identical to what it wrote before E6.
    `cards` turns the E7 share cards on (default SHARE_CARDS, i.e. off). Off,
    or with Pillow or the pinned font missing, every file written is
    byte-identical to a build without that feature."""
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

    # ---- submitted occasions (E6) ----
    # Indexed before the pages are written, and kept rigorously apart from
    # `holidays`, `day_index` and `occurrences`: an occasion contributes no
    # date to the archive horizon (one paid listing dated 2031 must not
    # backfill five years of /day/ pages), no entry to the month data files,
    # no row to search.json and no event to any feed.
    occasions, occasion_problems = validate_occasions(
        occasions or [], set(by_slug)
    )
    occ_by_date, occ_by_md = {}, {}
    for o in occasions:
        od = datetime.date.fromisoformat(o["date"])
        occ_by_date.setdefault(od, []).append(o)
        if o.get("recurs"):
            occ_by_md.setdefault((od.month, od.day), []).append(o)
    # A listing whose date has no dated page and which does not recur is
    # reachable only from /occasions/ and its own URL. That is a thing someone
    # paid for, so it is reported rather than left to be noticed.
    occasions_unlisted = sorted(
        o["slug"] for o in occasions
        if not o.get("recurs")
        and datetime.date.fromisoformat(o["date"]) not in published_days
    )

    # ---- month data files (v2): [name, slug, category, yearly] per day ----
    # Written to data/v2/ rather than over the old data/YYYY-MM.json: pages the
    # previous design left in browser and CDN caches still read the old files,
    # and a changed shape under the same URL would break them until they expire.
    by_month = {}  # "YYYY-MM" -> { "YYYY-M-D": [[name, slug, category, yearly], ...] }
    for d in sorted(day_index):
        mk = f"{d.year:04d}-{d.month:02d}"
        # [name, slug, category, yearly] -- plus a 5th element, the Type, on
        # rows that have one. Appended rather than always-present on purpose:
        # a 4-element entry is exactly the bytes it was before E4, so the month
        # files only change where a row was actually typed, and the home page's
        # inline script reads it[4] as undefined for the rest. Old cached
        # copies of either side keep working.
        by_month.setdefault(mk, {})[f"{d.year}-{d.month}-{d.day}"] = [
            [h["name"], h["slug"], h["category"], 1 if h["recurrence"] == "Annual" else 0]
            + ([h["type"]] if type_slug(h) else [])
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

    # ---- share cards (E7) ----
    #
    # Worked out before any page loop, because a page's og:image depends on
    # whether its card is being written this run: the switch moves the pages
    # and the images together or not at all. Five page types carry a card --
    # the observance pages, the dated and perennial date pages, the year
    # indexes and the category pages -- and all five go through write_card so
    # one run has one set of totals.
    card_loader, card_off_reason = card_fonts() if cards else (None, "SHARE_CARDS is off")
    card_on = card_loader is not None
    card_slugs = ({h["slug"] for h in holidays if h["slug"] in occurrences}
                  if card_on else set())
    card_diffs = {"created": [], "changed": [], "unchanged": 0}
    card_kinds = {k: 0 for k in
                  ("holiday", "day", "perennial", "year", "category")}
    card_bytes_total = 0

    def write_card(rel_path, data, kind):
        """Write one card beside its page and book it against the totals."""
        nonlocal card_bytes_total
        card_bytes_total += len(data)
        card_kinds[kind] += 1
        changed, created = write_raw_if_changed(
            os.path.join(site_dir, rel_path.strip("/")), data, dry_run)
        if created:
            card_diffs["created"].append(rel_path)
        elif changed:
            card_diffs["changed"].append(rel_path)
        else:
            card_diffs["unchanged"] += 1

    # ---- /day/YYYY-MM-DD/ permanent dated pages ----
    day_template = load_template(templates_dir, "day.html")
    day_diffs = {"created": [], "changed": [], "unchanged": 0}
    for i, d in enumerate(day_dates):
        prev_d = day_dates[i - 1] if i > 0 else None
        next_d = day_dates[i + 1] if i + 1 < len(day_dates) else None
        day_card = card_rel_for(day_path(d))
        new_html = render_day_page(
            d, day_index[d], prev_d, next_d, day_template, by_slug, memo,
            chromes["CALENDAR"], day_index, published_days, people=people,
            occasions=occ_by_date.get(d, ()),
            card_url=f"{SITE_BASE_URL}{day_card}" if card_on else None,
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
        if card_on:
            write_card(day_card,
                       day_card_png_bytes(d, day_index[d], card_loader), "day")

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

    # ---- calendar-feed occurrences (E5) ----
    # Every date inside the ten-year window, per observance, taken straight out
    # of the pass above rather than recomputed: a date in a feed is therefore a
    # date the date pages show. From `today` forward only -- a subscriber wants
    # what is coming, not this year's already-past observances. Fixed-date rows
    # appear here too, but their feed entry is a single RRULE event (see the
    # ICS_* constants), so for them this list is only used to count dates.
    ics_occ = {}
    for d, items in wide_index.items():
        if d < today:
            continue
        for h in items:
            ics_occ.setdefault(h["slug"], []).append(d)
    for dates in ics_occ.values():
        dates.sort()
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
            people=people, occasions=occ_by_md.get(key, ()),
            card_url=(f"{SITE_BASE_URL}{card_rel_for(path)}"
                      if card_on else None),
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
        if card_on:
            write_card(card_rel_for(path),
                       perennial_card_png_bytes(key[0], key[1], bucket["annual"],
                                                bucket["floating"], card_loader),
                       "perennial")
    perennial_skipped_paths = set(perennial_diffs["skipped"])
    perennial_published = {
        k for k in perennial_mds if perennial_path(*k) not in perennial_skipped_paths
    }
    perennial_paths = [
        perennial_path(*k) for k in perennial_mds if k in perennial_published
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
            ics_dates=ics_occ.get(slug, ()),
            card_url=(f"{SITE_BASE_URL}{card_rel_path(slug)}"
                      if slug in card_slugs else None),
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
        if slug in card_slugs:
            write_card(card_rel_path(slug), card_png_bytes(h, occ, card_loader),
                       "holiday")

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

    # ---- /holidays/<year>/ year indexes (E3, fourth bullet) ----
    # One page per year the dated archive touches. Derived entirely from
    # day_dates, so a year appears the day its first dated page does and the
    # current year's page grows as the horizon moves; nothing to configure.
    dates_by_year = {}
    for d in day_dates:
        dates_by_year.setdefault(d.year, []).append(d)
    archive_years = sorted(dates_by_year)
    year_links_html = " &middot; ".join(
        f'<a href="{year_index_path(y)}">{y}</a>' for y in archive_years
    )

    dates_body, dates_side = dates_hub_html(
        perennial_index, perennial_mds, perennial_published,
        year_links=year_links_html,
    )
    simple_pages["/dates/"] = render_simple_page(
        page_template, chromes["CALENDAR"],
        title="Holidays by Date: Every Day of the Year | Today Celebrates",
        description=(
            "Every date of the calendar, January 1 to December 31, with the "
            "national, international and world observances that fall on each one."
        ),
        path="/dates/", headline="The calendar, date by date",
        body=dates_body,
        side=dates_side,
        crumbs=crumbs_html(("Calendar", None)),
    )

    for y in archive_years:
        ydates = dates_by_year[y]
        # Dates inside the covered span that have no page at all: nothing is
        # on the calendar for them. Counted so the page can say so rather than
        # look as though days went missing.
        span = (ydates[-1] - ydates[0]).days + 1
        gaps = span - len(ydates)
        ybody, yside = year_index_html(y, ydates, day_index, archive_years, gaps)
        simple_pages[year_index_path(y)] = render_simple_page(
            page_template, chromes["CALENDAR"],
            title=f"{y} Holidays and Observances, Day by Day | Today Celebrates",
            description=(
                f"Every date in {y} with holidays and observances on the "
                f"calendar: {len(ydates)} days on record, "
                f"{long_date(ydates[0])} to {long_date(ydates[-1])}."
            ),
            path=year_index_path(y),
            headline=f"Holidays and observances in {y}",
            body=ybody,
            side=yside,
            crumbs=crumbs_html(("Calendar", "/dates/"), (str(y), None)),
            image=(f"{SITE_BASE_URL}{card_rel_for(year_index_path(y))}"
                   if card_on else None),
        )
        if card_on:
            write_card(card_rel_for(year_index_path(y)),
                       year_card_png_bytes(y, card_loader), "year")

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
                + cal_feed_links_html(f"{title.lower()} observances",
                                      f"/category/{c}/calendar.ics", len(members))
                + f'<ul class="cat-list">{"".join(lis)}</ul>'
            ),
            side=category_side_html(category_counts, current=c),
            crumbs=crumbs_html(("Categories", "/categories/"), (title, None)),
            image=(f"{SITE_BASE_URL}{card_rel_for(f'/category/{c}/')}"
                   if card_on else None),
        )
        if card_on:
            write_card(card_rel_for(f"/category/{c}/"),
                       category_card_png_bytes(c, len(members), card_loader),
                       "category")

    # ---- /occasions/ and /occasions/<slug>/ (E6) ----
    # Routed through simple_pages so they are written, diffed and sitemapped
    # by the same code every other static page uses -- and so they are
    # rendered from page.html, the one template with no JSON-LD slot.
    # With no approved occasions neither the index nor any page is created, so
    # the site gains nothing: no files, no sitemap URLs, no bytes.
    occasion_pages = []
    for o in occasions:
        html_out, problem = occasion_page_html(
            o, page_template, chromes[None], published_days
        )
        if problem:
            occasion_problems.append(problem)
            continue
        simple_pages[occasion_path(o["slug"])] = html_out
        occasion_pages.append(occasion_path(o["slug"]))
    if occasion_pages:
        simple_pages["/occasions/"] = render_simple_page(
            page_template, chromes[None],
            title="Submitted Occasions | Today Celebrates",
            description=(
                "Paid listings submitted by readers and businesses, reviewed "
                "before publication. Not national or official observances."
            ),
            path="/occasions/", headline="Submitted occasions",
            body=occasions_index_body(occasions, today),
            side="",
            crumbs=crumbs_html(("Submitted occasions", None)),
        )
    # Pages on disk for listings that are no longer approved. The generator
    # never deletes generated output, so a withdrawn paid listing would
    # otherwise stay up silently -- which is the one kind of stale page that
    # really matters here. Reported, and main() warns.
    occasions_stale = []
    occ_dir = os.path.join(site_dir, "occasions")
    if os.path.isdir(occ_dir):
        live = {o["slug"] for o in occasions}
        occasions_stale = sorted(
            name for name in os.listdir(occ_dir)
            if name not in live
            and os.path.isfile(os.path.join(occ_dir, name, "index.html"))
        )

    simple_changed = set()
    for path, html in simple_pages.items():
        changed, _created = write_if_changed(
            os.path.join(site_dir, path.strip("/"), "index.html"), html, dry_run
        )
        if changed:
            simple_changed.add(path)

    # ---- calendar feeds: /calendar.ics, per category, per observance (E5) ----
    # Deliberately not in sitemap.xml: a sitemap lists indexable pages, and
    # these are downloads. They are linked from the pages instead -- every
    # observance page, every category page and /about/ -- and named in
    # llms.txt.
    ics_diffs = {"created": [], "changed": [], "unchanged": 0}
    ics_sizes = {}

    def write_feed(path, name, description, events):
        content = ics_calendar(name, description, path, events)
        changed, created = write_bytes_if_changed(
            os.path.join(site_dir, path.lstrip("/")), content, dry_run
        )
        if created:
            ics_diffs["created"].append(path)
        elif changed:
            ics_diffs["changed"].append(path)
        else:
            ics_diffs["unchanged"] += 1
        ics_sizes[path] = len(content.encode("utf-8"))

    def events_for(h):
        """This observance's VEVENTs: one recurring, or one per enumerated date."""
        if h["recurrence"] == "Annual":
            start = occurrences.get(h["slug"])
            return [ics_event(h, start, yearly=True)] if start else []
        return [ics_event(h, d) for d in ics_occ.get(h["slug"], [])]

    ics_events = {}
    for h in sorted(holidays, key=lambda h: h["slug"]):
        evs = events_for(h)
        if evs:
            ics_events[h["slug"]] = evs

    all_events = [e for h in sorted(holidays, key=lambda h: h["slug"])
                  for e in ics_events.get(h["slug"], [])]
    write_feed(
        "/calendar.ics", "Today Celebrates",
        f"Every national, international and world observance on Today "
        f"Celebrates: {len(ics_events):,} of them. Rebuilt daily at "
        f"{SITE_BASE_URL}/.",
        all_events,
    )

    for c, members in sorted(by_category.items()):
        cat_events = [e for h in sorted(members, key=lambda h: h["slug"])
                      for e in ics_events.get(h["slug"], [])]
        write_feed(
            f"/category/{c}/calendar.ics",
            f"Today Celebrates: {cat_title(c)}",
            f"{len(members):,} {cat_title(c).lower()} observances from "
            f"{SITE_BASE_URL}/category/{c}/. Rebuilt daily.",
            cat_events,
        )

    for slug, evs in ics_events.items():
        h = by_slug[slug]
        write_feed(
            f"/holiday/{slug}/event.ics", h["name"],
            f"{h['name']} — {SITE_BASE_URL}/holiday/{slug}/",
            evs,
        )

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

    # E4 is typed over several runs, so every run says how far it has got and
    # names any Type option that exists in Notion but not in TYPE_ORDER (those
    # render and sort as untyped rather than being guessed at). main() warns.
    type_counts = {}
    unknown_types = set()
    for h in holidays:
        t = h.get("type")
        key = t or "(untyped)"
        type_counts[key] = type_counts.get(key, 0) + 1
        if t and t not in TYPE_RANK:
            unknown_types.add(t)

    return {
        "today": today_iso,
        "months_covered": sorted(by_month.keys()),
        "type_counts": dict(sorted(type_counts.items())),
        "unknown_types": sorted(unknown_types),
        "month_diffs": month_diffs,
        "stale_month_files": sorted(stale_month_files),
        "cards_enabled": card_on,
        "cards_disabled_reason": None if card_on else card_off_reason,
        "cards_total": sum(card_kinds.values()),
        "cards_by_kind": dict(card_kinds),
        "cards_created": len(card_diffs["created"]),
        "cards_changed": sorted(card_diffs["changed"]),
        "cards_unchanged_count": card_diffs["unchanged"],
        "cards_bytes_total": card_bytes_total,
        "pages_created": sorted(page_diffs["created"]),
        "pages_changed": sorted(page_diffs["changed"]),
        "pages_unchanged_count": len(page_diffs["unchanged"]),
        "pages_skipped": sorted(page_diffs["skipped"]),
        "unresolved_holidays": sorted(unresolved, key=lambda u: u["slug"]),
        "home_changed": home_changed,
        "search_index_entries": len(search_index),
        "search_index_changed": search_changed,
        "simple_pages_total": len(simple_pages),
        "year_index_pages": [year_index_path(y) for y in archive_years],
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
        "ics_files_total": len(ics_sizes),
        "ics_files_created": len(ics_diffs["created"]),
        "ics_files_changed": sorted(ics_diffs["changed"]),
        "ics_files_unchanged_count": ics_diffs["unchanged"],
        "ics_events_total": sum(len(v) for v in ics_events.values()),
        "ics_observances": len(ics_events),
        "ics_main_feed_bytes": ics_sizes.get("/calendar.ics", 0),
        "ics_total_bytes": sum(ics_sizes.values()),
        "occasions_total": len(occasions),
        "occasions_pages": occasion_pages,
        "occasions_problems": occasion_problems,
        "occasions_unlisted": occasions_unlisted,
        "occasions_stale_pages": occasions_stale,
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
    ap.add_argument("--occasions", default=DEFAULT_OCCASIONS_PATH,
                    help="path to occasions.json, the approved submitted "
                         "occasions built by export_occasions_from_notion.py "
                         "(default: scripts/occasions.json; the feature is "
                         "simply off if the file is absent)")
    ap.add_argument("--cards", action="store_true", default=SHARE_CARDS,
                    help="generate the E7 share cards (a card.png beside every "
                         "observance, date, year-index and category page) and "
                         "use each as its page's og:image. Needs Pillow and "
                         "the pinned DejaVu faces; off by default, because "
                         "turning it on adds ~3,200 images to the repo")
    ap.add_argument("--people", default=DEFAULT_PEOPLE_PATH,
                    help="path to people.json, the born-on-this-day data built by "
                         "build_people.py (default: scripts/people.json; the "
                         "feature is simply off if the file is absent)")
    args = ap.parse_args()

    holidays = json.load(open(args.holidays, encoding="utf-8"))
    today = datetime.date.fromisoformat(args.today)
    people = load_people(args.people)
    occasions = load_occasions(args.occasions)

    report = generate(holidays, today, args.site, dry_run=args.dry_run,
                      templates_dir=args.templates, people=people,
                      occasions=occasions, cards=args.cards)

    # Asked for cards and did not get them: the pages silently keep the stock
    # hero image, which is a quiet half-failure, so say it out loud.
    if args.cards and not report.get("cards_enabled"):
        note = ("--cards was requested but no share cards were generated: "
                f"{report.get('cards_disabled_reason')}. Every page kept its "
                "stock category hero as its og:image.")
        print(f"WARNING: {note}", file=sys.stderr)
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::warning title=Share cards disabled::{note}")

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
    # Submitted occasions (E6). Every one of these is about something a
    # person paid for, so none of them is allowed to be quiet.
    for p in report.get("occasions_problems", []):
        print(f"WARNING: submitted occasion -- {p}", file=sys.stderr)
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::warning title=Submitted occasion problem::{p}")
    for slug in report.get("occasions_unlisted", []):
        note = (f"submitted occasion {slug!r} has a date outside the published "
                f"/day/ archive and does not recur, so it is reachable only "
                f"from /occasions/ and its own URL.")
        print(f"WARNING: {note}", file=sys.stderr)
    for slug in report.get("occasions_stale_pages", []):
        note = (f"public/occasions/{slug}/ exists but {slug!r} is no longer an "
                f"approved occasion. The page is still live; delete the "
                f"directory to take the listing down.")
        print(f"WARNING: {note}", file=sys.stderr)
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::warning title=Withdrawn occasion still published::{note}")

    for t in report.get("unknown_types", []):
        note = (f"holidays.json has Type {t!r}, which TYPE_ORDER in this script "
                f"does not list, so those rows sort and render as untyped. Add "
                f"it to TYPE_ORDER/TYPE_SLUG and give it a .tg- rule in "
                f"public/styles/site.css.")
        print(f"WARNING: {note}", file=sys.stderr)
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::warning title=Unknown observance type::{note}")

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
