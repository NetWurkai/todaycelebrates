#!/usr/bin/env python3
"""
Pull every Published holiday from the "Today Celebrates — Holidays" Notion
database and write it out as scripts/holidays.json, in the format
generate.py expects.

Requires NOTION_TOKEN in the environment: an internal Notion integration
token that has been shared with the database (Notion -> database -> ...
-> Connections -> add the integration). See scripts/README.md for the
one-time setup.

Notion has no field for *how* a Floating holiday's date is computed each
year (nth-weekday-of-month, "Sunday after Labor Day", or the Autumnal
Equinox's hand-confirmed almanac lookup) -- that logic is hardcoded below,
keyed by slug. It only needs updating if a Floating holiday is added,
removed, or its rule changes; the Autumnal Equinox table needs a new
almanac-checked year added well before 2036.

Usage:
  NOTION_TOKEN=secret_xxx python3 scripts/export_from_notion.py scripts/holidays.json
"""
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = "68fdbc80-5de5-4d9e-8ef6-52926b74f9c4"
NOTION_VERSION = "2022-06-28"
API_BASE = "https://api.notion.com/v1"

FLOATING_RULES = {
    # ---- pre-existing rules (Sep-Oct batch) ----
    "labor-day": {"rule": "nth_weekday", "month": 9, "weekday": 0, "n": 1},                  # 1st Monday of September
    "national-grandparents-day": {"rule": "after_labor_day_sunday"},                          # 1st Sunday after Labor Day
    "columbus-day": {"rule": "nth_weekday", "month": 10, "weekday": 0, "n": 2},               # 2nd Monday of October
    "indigenous-peoples-day": {"rule": "nth_weekday", "month": 10, "weekday": 0, "n": 2},      # 2nd Monday of October
    "canadian-thanksgiving-day": {"rule": "nth_weekday", "month": 10, "weekday": 0, "n": 2},   # 2nd Monday of October
    "sweetest-day": {"rule": "nth_weekday", "month": 10, "weekday": 5, "n": 3},                # 3rd Saturday of October
    "autumnal-equinox": {
        "rule": "lookup_table",
        # US Eastern local date, hand-confirmed against precise UTC equinox
        # times (astropixels.com / Wikipedia) -- see roadmap.md's Phase 3
        # entry for the conversion. Extend this well before it runs out.
        "table": {
            "2026": "09-22", "2027": "09-23", "2028": "09-22", "2029": "09-22",
            "2030": "09-22", "2031": "09-23", "2032": "09-22", "2033": "09-22",
            "2034": "09-22", "2035": "09-23", "2036": "09-22",
        },
    },

    # ---- November ----
    "daylight-saving-time-ends": {"rule": "nth_weekday", "month": 11, "weekday": 6, "n": 1},   # 1st Sunday of November
    "u-s-general-election-day": {"rule": "us_election_day"},                                    # Tuesday after 1st Monday of November
    "great-american-smokeout": {"rule": "nth_weekday", "month": 11, "weekday": 3, "n": 3},       # 3rd Thursday of November (= Thu before Thanksgiving)
    "beaujolais-nouveau-day": {"rule": "nth_weekday", "month": 11, "weekday": 3, "n": 3},         # 3rd Thursday of November (French AOC release-date rule)
    "thanksgiving-day": {"rule": "nth_weekday", "month": 11, "weekday": 3, "n": 4},               # 4th Thursday of November
    "national-adoption-day": {"rule": "offset_from_slug", "slug": "thanksgiving-day", "days": -5},  # Saturday before Thanksgiving
    "tie-one-on-day": {"rule": "offset_from_slug", "slug": "thanksgiving-day", "days": -1},       # Wednesday before Thanksgiving
    "buy-nothing-day": {"rule": "offset_from_slug", "slug": "thanksgiving-day", "days": 1},       # Friday after Thanksgiving
    "black-friday": {"rule": "offset_from_slug", "slug": "thanksgiving-day", "days": 1},
    "national-leftovers-day": {"rule": "offset_from_slug", "slug": "thanksgiving-day", "days": 1},
    "small-business-saturday": {"rule": "offset_from_slug", "slug": "thanksgiving-day", "days": 2},
    "small-brewery-sunday": {"rule": "offset_from_slug", "slug": "thanksgiving-day", "days": 3},
    "secondhand-sunday": {"rule": "offset_from_slug", "slug": "thanksgiving-day", "days": 3},
    "cyber-monday": {"rule": "offset_from_slug", "slug": "thanksgiving-day", "days": 4},
    "givingtuesday": {"rule": "offset_from_slug", "slug": "thanksgiving-day", "days": 5},
    "advent-sunday": {"rule": "nearest_weekday_to_date", "weekday": 6, "month": 11, "day": 30},   # Sunday closest to Nov 30
    "stir-up-sunday": {"rule": "offset_from_slug", "slug": "advent-sunday", "days": -7},          # last Sunday before Advent

    # ---- December ----
    "green-monday": {"rule": "nth_weekday", "month": 12, "weekday": 0, "n": 2},                   # 2nd Monday of December
    "super-saturday": {"rule": "last_weekday_before_date", "weekday": 5, "month": 12, "day": 25}, # last Saturday before Christmas ("Panic Saturday")
    "national-wreaths-across-america-day": {"rule": "nth_weekday", "month": 12, "weekday": 5, "n": 3},  # 3rd Saturday of December
    "yule": {
        "rule": "lookup_table",
        # December solstice, US Eastern date (astropixels.com). All 11 confirmed
        # years land on Dec 21 with no borderline UTC/EST conversion cases.
        "table": {
            "2026": "12-21", "2027": "12-21", "2028": "12-21", "2029": "12-21",
            "2030": "12-21", "2031": "12-21", "2032": "12-21", "2033": "12-21",
            "2034": "12-21", "2035": "12-21", "2036": "12-21",
        },
    },
    "first-day-of-winter": {
        "rule": "lookup_table",
        "table": {
            "2026": "12-21", "2027": "12-21", "2028": "12-21", "2029": "12-21",
            "2030": "12-21", "2031": "12-21", "2032": "12-21", "2033": "12-21",
            "2034": "12-21", "2035": "12-21", "2036": "12-21",
        },
    },
    "the-start-of-hanukkah": {
        "rule": "lookup_table",
        # First day/candle, from Hebcal.com (authoritative Hebrew-calendar calc).
        "table": {
            "2026": "12-04", "2027": "12-24", "2028": "12-12", "2029": "12-01",
            "2030": "12-20", "2031": "12-09", "2032": "11-27", "2033": "12-16",
            "2034": "12-06", "2035": "12-25", "2036": "12-13",
        },
    },

    # ---- January ----
    "blue-monday": {"rule": "nth_weekday", "month": 1, "weekday": 0, "n": 3},                     # 3rd Monday of January
    "national-day-of-service": {"rule": "nth_weekday", "month": 1, "weekday": 0, "n": 3},         # same day as MLK Day
    "martin-luther-king-jr-day": {"rule": "nth_weekday", "month": 1, "weekday": 0, "n": 3},       # 3rd Monday of January
    "tu-bishvat": {
        "rule": "lookup_table",
        "table": {
            "2026": "02-02", "2027": "01-23", "2028": "02-12", "2029": "01-31",
            "2030": "01-19", "2031": "02-08", "2032": "01-28", "2033": "01-15",
            "2034": "02-04", "2035": "01-25", "2036": "02-13",
        },
    },

    # ---- February ----
    "chinese-new-year": {
        "rule": "lookup_table",
        # Lunar New Year. 2027 confirmed as Feb 6 (not Feb 7) via 3 independent
        # sources (qppstudio, chinahighlights, travelchinaguide) plus the new-moon
        # instant itself (Feb 6, 2027 23:56 China Standard Time).
        "table": {
            "2026": "02-17", "2027": "02-06", "2028": "01-26", "2029": "02-13",
            "2030": "02-03", "2031": "01-23", "2032": "02-11", "2033": "01-31",
            "2034": "02-19", "2035": "02-08", "2036": "01-28",
        },
    },
    "the-start-of-ramadan": {
        "rule": "lookup_table",
        # 1 Ramadan, Umm al-Qura tabular calendar (qppstudio.net, cross-checked
        # against Muhammadiyah's independently-calculated calendar for 2026).
        # NOTE: because the Islamic year (~354 days) drifts against the Gregorian
        # year, TWO Ramadan-starts fall within Gregorian 2030 (Jan 5 and ~Dec 26);
        # this table only captures one per row. Re-verify closely before 2030-2031
        # generation runs -- the "year+1" rollover in next_occurrence() may need
        # the Dec 2030 date added by hand when that time comes.
        "table": {
            "2026": "02-18", "2027": "02-08", "2028": "01-28", "2029": "01-16",
            "2030": "01-05", "2031": "12-15", "2032": "12-04", "2033": "11-23",
            "2034": "11-12", "2035": "11-01", "2036": "10-20",
        },
    },
    "mardi-gras": {"rule": "easter_offset", "days": -47},
    "ash-wednesday": {"rule": "easter_offset", "days": -46},
    "presidents-day": {"rule": "nth_weekday", "month": 2, "weekday": 0, "n": 3},                  # 3rd Monday of February
    "national-womans-heart-day": {"rule": "nth_weekday", "month": 2, "weekday": 4, "n": 1},       # 1st Friday of February
    # NOTE: the row's stored Notion date (2027-02-19) appears to be a mix-up with
    # National Caregivers Day's date -- National Woman's Heart Day / National Wear
    # Red Day is the 1st Friday of February (Feb 5, 2027), confirmed via
    # nationaltoday.com. Doesn't affect the live site (Floating rows' Notion dates
    # are cosmetic only) but the Notion row is worth a look.
    "national-caregivers-day": {"rule": "nth_weekday", "month": 2, "weekday": 4, "n": 3},         # 3rd Friday of February

    # ---- March ----
    "eid-al-fitr": {
        "rule": "lookup_table",
        # 1 Shawwal, Umm al-Qura tabular calendar (qppstudio.net).
        # NOTE: 2033 has two Eid al-Fitr occurrences in one Gregorian year
        # (Jan 2 and ~Dec 23) for the same reason as Ramadan above -- re-verify
        # before 2033-2034 generation runs.
        "table": {
            "2026": "03-20", "2027": "03-09", "2028": "02-26", "2029": "02-14",
            "2030": "02-04", "2031": "01-24", "2032": "01-14", "2033": "01-02",
            "2034": "12-12", "2035": "12-01", "2036": "11-19",
        },
    },
    "the-start-of-daylight-saving-time": {"rule": "nth_weekday", "month": 3, "weekday": 6, "n": 2},  # 2nd Sunday of March
    "companies-that-care-day": {"rule": "nth_weekday", "month": 3, "weekday": 3, "n": 3},          # 3rd Thursday of March
    "oranges-and-lemons-day": {"rule": "nth_weekday", "month": 3, "weekday": 3, "n": 3},           # 3rd Thursday of March (per nationaltoday.com's stated rule)
    "absolutely-incredible-kid-day": {"rule": "nth_weekday", "month": 3, "weekday": 3, "n": 3},    # 3rd Thursday of March
    "the-first-day-of-spring": {
        "rule": "lookup_table",
        # March equinox, US Eastern date (astropixels.com UTC instants, hand-
        # converted for DST). 2028/2032/2036 land on Mar 19 Eastern even though
        # the equinox is UTC Mar 20, because DST has already started by then.
        "table": {
            "2026": "03-20", "2027": "03-20", "2028": "03-19", "2029": "03-20",
            "2030": "03-20", "2031": "03-20", "2032": "03-19", "2033": "03-20",
            "2034": "03-20", "2035": "03-20", "2036": "03-19",
        },
    },
    "ostara": {
        "rule": "lookup_table",
        "table": {
            "2026": "03-20", "2027": "03-20", "2028": "03-19", "2029": "03-20",
            "2030": "03-20", "2031": "03-20", "2032": "03-19", "2033": "03-20",
            "2034": "03-20", "2035": "03-20", "2036": "03-19",
        },
    },
    "world-sleep-day": {"rule": "last_weekday_before_slug", "weekday": 4, "slug": "the-first-day-of-spring"},  # Friday before the equinox
    "naw-ruz": {
        "rule": "lookup_table",
        # Baha'i New Year -- NOT simply equinox + a fixed offset; it's the
        # Baha'i sunset-to-sunset day containing the equinox as determined at
        # Tehran (2014 Universal House of Justice ruling). Cross-checked
        # against the Baha'i National Spiritual Assembly of Canada's 2026
        # announcement and nationaltoday.com's 2027 date.
        "table": {
            "2026": "03-21", "2027": "03-21", "2028": "03-21", "2029": "03-20",
            "2030": "03-20", "2031": "03-21", "2032": "03-20", "2033": "03-20",
            "2034": "03-20", "2035": "03-21", "2036": "03-20",
        },
    },
    "palm-sunday": {"rule": "easter_offset", "days": -7},
    "purim": {
        "rule": "lookup_table",
        "table": {
            "2026": "03-03", "2027": "03-23", "2028": "03-12", "2029": "03-01",
            "2030": "03-19", "2031": "03-09", "2032": "02-26", "2033": "03-15",
            "2034": "03-05", "2035": "03-25", "2036": "03-13",
        },
    },
    "holy-tuesday": {"rule": "easter_offset", "days": -5},
    "american-diabetes-association-alert-day": {"rule": "nth_weekday", "month": 3, "weekday": 1, "n": 4},  # 4th Tuesday of March (ADA's own rule)
    "good-wednesday": {"rule": "easter_offset", "days": -4},
    "maundy-thursday": {"rule": "easter_offset", "days": -3},
    "good-friday": {"rule": "easter_offset", "days": -2},
    "holy-saturday": {"rule": "easter_offset", "days": -1},
    "earth-hour": {"rule": "last_weekday", "month": 3, "weekday": 5},                              # last Saturday of March
    "easter-sunday": {"rule": "easter_offset", "days": 0},
    "dyngus-day": {"rule": "easter_offset", "days": 1},
    "easter-monday": {"rule": "easter_offset", "days": 1},

    # ---- April ----
    "national-walk-to-work-day": {"rule": "nth_weekday", "month": 4, "weekday": 4, "n": 1},        # 1st Friday of April
    "hospital-admitting-clerks-day": {"rule": "nth_weekday", "month": 4, "weekday": 4, "n": 1},
    "student-government-day": {"rule": "nth_weekday", "month": 4, "weekday": 4, "n": 1},
    "passover": {
        "rule": "lookup_table",
        # First day (15 Nisan), from Hebcal.com.
        "table": {
            "2026": "04-02", "2027": "04-22", "2028": "04-11", "2029": "03-31",
            "2030": "04-18", "2031": "04-08", "2032": "03-27", "2033": "04-14",
            "2034": "04-04", "2035": "04-24", "2036": "04-12",
        },
    },
    "education-and-sharing-day": {"rule": "offset_from_slug", "slug": "passover", "days": -4},     # 11 Nisan (Lubavitcher Rebbe's birthday), always 4 days before Passover within the same Hebrew month
    "boston-marathon-day": {"rule": "nth_weekday", "month": 4, "weekday": 0, "n": 3},               # 3rd Monday of April (MA/ME Patriots' Day, by law since 1969)
    "patriots-day": {"rule": "nth_weekday", "month": 4, "weekday": 0, "n": 3},
    "administrative-professionals-day": {"rule": "last_weekday_offset", "month": 4, "weekday": 5, "offset_days": -3},  # Wednesday of the last full (Sun-Sat) week in April
    "national-teach-your-children-to-save-day": {
        "rule": "lookup_table",
        # No reliable formula found -- the ABA sets this administratively each
        # year within Financial Literacy Month and the date has NOT followed a
        # consistent weekday or fixed-date rule historically (2021=Apr21 Wed,
        # 2026=Apr23 Thu per ABA's own release, 2027=Apr27 Tue per
        # nationaltoday.com). Only add a year here after checking aba.com's
        # press release for that year -- don't extrapolate a pattern.
        "table": {
            "2026": "04-23", "2027": "04-27",
        },
    },

    # ---- May ----
    "mothers-day": {"rule": "nth_weekday", "month": 5, "weekday": 6, "n": 2},                      # 2nd Sunday of May
    "preakness-stakes": {
        "rule": "lookup_table",
        # Historically 3rd Saturday of May, but the Maryland Jockey Club moved
        # the 2027 race to Sun May 23 (more spacing after the Derby) without
        # committing to a permanent new formula -- confirm each year via
        # official MJC/Laurel Park announcements before adding it here.
        "table": {
            "2026": "05-16", "2027": "05-23",
        },
    },
    "armed-forces-day": {"rule": "nth_weekday", "month": 5, "weekday": 5, "n": 3},                 # 3rd Saturday of May
    "pentecost": {"rule": "easter_offset", "days": 49},
    "stepmothers-day": {"rule": "offset_from_slug", "slug": "mothers-day", "days": 7},              # Sunday after Mother's Day
    "memorial-day": {"rule": "last_weekday", "month": 5, "weekday": 0},                             # last Monday of May

    # ---- June ----
    "belmont-stakes": {
        "rule": "lookup_table",
        # No fixed formula -- NYRA sets the date administratively each year and
        # the venue has been in flux (Saratoga in 2024-2026 while Belmont Park
        # was rebuilt; back at Belmont Park for 2027's Jun 5 date). Confirm each
        # year via NYRA's official announcement before adding it here.
        "table": {
            "2026": "06-06", "2027": "06-05",
        },
    },
    "islamic-new-year": {
        "rule": "lookup_table",
        # 1 Muharram, Umm al-Qura tabular calendar (qppstudio.net). No
        # double-occurrence years in this range.
        "table": {
            "2026": "06-16", "2027": "06-06", "2028": "05-25", "2029": "05-14",
            "2030": "05-03", "2031": "04-23", "2032": "04-11", "2033": "04-01",
            "2034": "03-21", "2035": "03-11", "2036": "02-28",
        },
    },
    "fathers-day": {"rule": "nth_weekday", "month": 6, "weekday": 6, "n": 3},                      # 3rd Sunday of June
    "the-first-day-of-summer": {
        "rule": "lookup_table",
        # June solstice, US Eastern date (astropixels.com UTC instants, hand-
        # converted for EDT -- always in effect by late June).
        "table": {
            "2026": "06-21", "2027": "06-21", "2028": "06-20", "2029": "06-20",
            "2030": "06-21", "2031": "06-21", "2032": "06-20", "2033": "06-20",
            "2034": "06-21", "2035": "06-21", "2036": "06-20",
        },
    },

    # ---- July ----
    "international-cherry-pit-spitting-day": {"rule": "nth_weekday", "month": 7, "weekday": 5, "n": 1},  # 1st Saturday of July
    "international-day-of-cooperatives": {"rule": "nth_weekday", "month": 7, "weekday": 5, "n": 1},       # 1st Saturday of July (UN's own stated rule)
    "national-build-a-scarecrow-day": {"rule": "nth_weekday", "month": 7, "weekday": 6, "n": 1},          # 1st Sunday of July (consistently applied across novelty-calendar sites despite the odd autumn-themed subject)

    # ---- August ----
    "american-family-day": {"rule": "nth_weekday", "month": 8, "weekday": 6, "n": 1},              # 1st Sunday of August
    "sisters-day": {"rule": "nth_weekday", "month": 8, "weekday": 6, "n": 1},
    "friendship-day": {"rule": "nth_weekday", "month": 8, "weekday": 6, "n": 1},
    "national-night-out": {"rule": "nth_weekday", "month": 8, "weekday": 1, "n": 1},                # 1st Tuesday of August (some states observe 1st Tue of October instead)
    "friday-the-13th": {"rule": "next_friday_13"},                                                  # special-cased in next_occurrence(); can't be resolved "for a year"
    "national-medical-dosimetrist-day": {"rule": "nth_weekday", "month": 8, "weekday": 2, "n": 3},  # 3rd Wednesday of August (inferred from aggregator dates, no primary-source rule found)
    "international-homeless-animals-day": {"rule": "nth_weekday", "month": 8, "weekday": 5, "n": 3},  # 3rd Saturday of August
    "break-the-monotony-day": {"rule": "nth_weekday", "month": 8, "weekday": 5, "n": 3},            # 3rd Saturday of August (inferred, no primary source found)
    "international-geocaching-day": {"rule": "nth_weekday", "month": 8, "weekday": 5, "n": 3},      # 3rd Saturday of August

    # ---- lunar/lunisolar holidays without a slug-offset shortcut ----
    "diwali": {
        "rule": "lookup_table",
        "table": {
            "2026": "11-08", "2027": "10-29", "2028": "10-17", "2029": "11-05",
            "2030": "10-26", "2031": "11-14", "2032": "11-02", "2033": "10-22",
            "2034": "11-10", "2035": "10-30", "2036": "10-18",
        },
    },
}


def slugify(name):
    # Mirrors public/index.html's client-side slugify() exactly.
    s = name.lower()
    s = s.replace("&", "and")
    s = re.sub(r"[‘’']", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    s = re.sub(r"-+", "-", s)
    return s


def notion_request(path, payload=None):
    url = f"{API_BASE}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if payload is not None else "GET")
    req.add_header("Authorization", f"Bearer {NOTION_TOKEN}")
    req.add_header("Notion-Version", NOTION_VERSION)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"Notion API error {e.code} for {path}: {body}") from None


def fetch_all_rows():
    rows = []
    cursor = None
    while True:
        payload = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        result = notion_request(f"/databases/{DATABASE_ID}/query", payload)
        rows.extend(result["results"])
        if not result.get("has_more"):
            break
        cursor = result["next_cursor"]
    return rows


def plain_text(rich_text_list):
    return "".join(rt.get("plain_text", "") for rt in rich_text_list)


def extract_holiday(page):
    """Returns (entry_or_None, warning_or_None). entry is None with no
    warning for a row that's simply not Published (not an error)."""
    props = page["properties"]

    name = plain_text(props.get("Holiday", {}).get("title", [])).strip()
    if not name:
        return None, "a row has no Holiday name (title) set -- skipped"

    if not props.get("Published", {}).get("checkbox", False):
        return None, None

    date_prop = props.get("Date", {}).get("date")
    if not date_prop or not date_prop.get("start"):
        return None, f"{name!r}: Published but missing Date -- skipped"
    date_start = date_prop["start"][:10]

    category_prop = props.get("Category", {}).get("select")
    category = category_prop["name"] if category_prop else None
    if not category:
        return None, f"{name!r}: Published but missing Category -- skipped"

    description = plain_text(props.get("Description", {}).get("rich_text", []))
    if not description:
        return None, f"{name!r}: Published but missing Description -- skipped"

    recurrence_prop = props.get("Recurrence", {}).get("select")
    recurrence = recurrence_prop["name"] if recurrence_prop else None
    if recurrence not in ("Annual", "Floating"):
        return None, f"{name!r}: Published but Recurrence is {recurrence!r}, not Annual/Floating -- skipped"

    order_prop = props.get("Order", {}).get("number")
    display_order = order_prop if order_prop is not None else 999

    slug = slugify(html.unescape(name))

    entry = {
        "slug": slug,
        "name": html.unescape(name),
        "category": category.lower(),
        "description": html.unescape(description),
        "recurrence": recurrence,
        "display_order": display_order,
    }

    if recurrence == "Annual":
        y, m, d = date_start.split("-")
        entry["month"] = int(m)
        entry["day"] = int(d)
    else:
        rule = FLOATING_RULES.get(slug)
        if rule is None:
            return None, (
                f"{name!r} (slug {slug!r}) is marked Floating but has no rule in "
                f"FLOATING_RULES in this script -- add one by hand, don't guess a "
                f"fixed date. Skipped for this run."
            )
        entry["floating_rule"] = rule

    return entry, None


def main():
    if not NOTION_TOKEN:
        print("ERROR: NOTION_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    out_path = sys.argv[1] if len(sys.argv) > 1 else "scripts/holidays.json"

    pages = fetch_all_rows()
    print(f"fetched {len(pages)} rows from Notion")

    holidays = []
    warnings = []
    seen_slugs = {}
    for page in pages:
        entry, warning = extract_holiday(page)
        if warning:
            warnings.append(warning)
        if entry is None:
            continue
        if entry["slug"] in seen_slugs:
            warnings.append(
                f"duplicate slug {entry['slug']!r}: {entry['name']!r} collides with "
                f"{seen_slugs[entry['slug']]!r} -- keeping the first, skipping this one"
            )
            continue
        seen_slugs[entry["slug"]] = entry["name"]
        holidays.append(entry)

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    if len(holidays) == 0:
        print(
            "ERROR: 0 usable holidays after filtering -- refusing to write an empty "
            "holidays.json. This almost always means the Notion query failed or "
            "auth is wrong, not that the database is actually empty.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Safety guard: refuse to shrink the dataset by a large margin in one run.
    # A sudden drop is far more likely a Notion problem than a real bulk
    # unpublish -- don't let a bad run quietly wipe most of the site.
    if os.path.exists(out_path):
        try:
            previous = json.load(open(out_path, encoding="utf-8"))
            if len(previous) > 0 and len(holidays) < len(previous) * 0.8:
                print(
                    f"ERROR: holiday count dropped from {len(previous)} to "
                    f"{len(holidays)} (more than 20%) -- refusing to write. "
                    f"Investigate before re-running.",
                    file=sys.stderr,
                )
                sys.exit(1)
        except (json.JSONDecodeError, OSError):
            pass

    holidays.sort(key=lambda h: h["slug"])
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(holidays, f, ensure_ascii=False, separators=(",", ":"))

    print(f"wrote {len(holidays)} holidays to {out_path} ({len(warnings)} warnings)")


if __name__ == "__main__":
    main()
