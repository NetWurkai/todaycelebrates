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
