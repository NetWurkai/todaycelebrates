#!/usr/bin/env python3
"""
Pull every APPROVED row from the "Today Celebrates — Submitted Occasions"
Notion database and write it out as scripts/occasions.json, in the format
generate.py expects.

This is E6's half of the export. It is a *separate* script against a
*separate* database on purpose, and that separation is the whole safety
argument:

  - A paid occasion can never appear in the real observance list, in a
    /holiday/ URL, in Event structured data or in a calendar feed, because it
    is never in holidays.json at all. No field value, typo or mis-set
    checkbox can put it there. See docs/EXECUTION_PLAN.md E6's
    non-negotiable constraints.
  - The two datasets can be regenerated independently, and a failure of this
    one leaves the observance site untouched.

The review gate is `Review Status`: only `Approved` rows are carried through.
The submission worker leaves every new row at `Pending`, so a paid listing
reaches the site only after a human has read it. Setting a row back to
`Pending` or `Rejected` is the revert -- the listing leaves the site at the
next regeneration with nothing lost.

Requires NOTION_TOKEN in the environment: the same internal integration token
export_from_notion.py uses, shared with THIS database as well (Notion ->
database -> ... -> Connections -> add the integration). See scripts/README.md.

Usage:
  NOTION_TOKEN=secret_xxx python3 scripts/export_occasions_from_notion.py scripts/occasions.json
"""
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")

# "Today Celebrates — Submitted Occasions", created 2026-10-15. Distinct from
# the Holidays database id in export_from_notion.py; do not point either script
# at the other's database.
DATABASE_ID = "7c9d328c-0360-4feb-aabf-998f6402eed9"
NOTION_VERSION = "2022-06-28"
API_BASE = "https://api.notion.com/v1"

# The one Review Status at which a submitted occasion reaches the site.
RELEASED_STATUSES = ("Approved",)

# Launch tier (E6: "Launch with the Listed tier only"). A row carrying any
# other tier is dropped with a warning rather than rendered, so adding an
# option in Notion cannot ship a tier the generator has no design for.
ALLOWED_TIERS = ("Listed",)

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def slugify(name):
    # Same transform as export_from_notion.py's, so a submitted occasion and a
    # holiday would slugify identically -- which is what lets the collision
    # check below be meaningful.
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
    req = urllib.request.Request(url, data=data,
                                 method="POST" if payload is not None else "GET")
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


def load_holiday_slugs(path):
    """Every slug the observance dataset already uses, or an empty set.

    Used only to refuse a collision. A missing holidays.json is not an error
    here -- it just means the check cannot run this time, and the run says so.
    """
    try:
        with open(path, encoding="utf-8") as f:
            return {h["slug"] for h in json.load(f)}
    except (OSError, ValueError, KeyError, TypeError):
        return set()


def extract_occasion(page, holiday_slugs):
    """Returns (entry_or_None, warning_or_None).

    entry is None with no warning for a row that is simply not Approved yet --
    that is the review queue working, not a problem to report.
    """
    props = page["properties"]

    name = plain_text(props.get("Occasion", {}).get("title", [])).strip()
    if not name:
        return None, "a row has no Occasion name (title) set -- skipped"

    status_prop = props.get("Review Status", {}).get("select")
    status = status_prop["name"] if status_prop else None
    if status not in RELEASED_STATUSES:
        return None, None

    tier_prop = props.get("Tier", {}).get("select")
    tier = tier_prop["name"] if tier_prop else None
    if tier not in ALLOWED_TIERS:
        return None, (
            f"{name!r}: Approved but Tier is {tier!r}, not one of "
            f"{', '.join(ALLOWED_TIERS)} -- skipped. Only tiers the generator "
            f"has a design for may ship."
        )

    date_prop = props.get("Date", {}).get("date")
    if not date_prop or not date_prop.get("start"):
        return None, f"{name!r}: Approved but missing Date -- skipped"
    date_start = date_prop["start"][:10]

    blurb = " ".join(plain_text(props.get("Blurb", {}).get("rich_text", [])).split())
    if not blurb:
        return None, f"{name!r}: Approved but missing Blurb -- skipped"

    slug = plain_text(props.get("Slug", {}).get("rich_text", [])).strip().lower()
    if not slug:
        slug = slugify(html.unescape(name))
    if not SLUG_RE.match(slug):
        return None, (
            f"{name!r}: Slug {slug!r} is not a usable URL slug (lowercase "
            f"a-z 0-9 and single hyphens only) -- skipped"
        )
    if slug in holiday_slugs:
        return None, (
            f"{name!r}: Slug {slug!r} is already a holiday slug -- skipped. A "
            f"paid listing must not share a name with a real observance; "
            f"rename it in Notion before approving."
        )

    entry = {
        "slug": slug,
        "name": html.unescape(name),
        "date": date_start,
        "blurb": html.unescape(blurb),
        "tier": tier,
        "recurs": bool(props.get("Recurs Yearly", {}).get("checkbox", False)),
    }

    body = plain_text(props.get("Body", {}).get("rich_text", [])).strip()
    if body:
        entry["body"] = html.unescape(body)

    link = (props.get("Link", {}).get("url") or "").strip()
    if link:
        if not link.startswith(("http://", "https://")):
            return None, (
                f"{name!r}: Link {link!r} is not an http(s) URL -- skipped"
            )
        entry["link"] = link

    # Payment reference. Not a gate: a comped or manually created listing is
    # legitimate. But an Approved row with no payment recorded should never
    # pass unremarked, because the ordinary path always writes one.
    payment = plain_text(props.get("Stripe Payment", {}).get("rich_text", [])).strip()
    warning = None
    if payment:
        entry["payment"] = payment
    else:
        warning = (
            f"{name!r}: Approved with no Stripe Payment recorded. Fine if it was "
            f"comped; otherwise the webhook did not finish and this listing may "
            f"not have been paid for."
        )

    return entry, warning


def main():
    if not NOTION_TOKEN:
        print("ERROR: NOTION_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    out_path = sys.argv[1] if len(sys.argv) > 1 else "scripts/occasions.json"
    holidays_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(out_path)), "holidays.json"
    )

    holiday_slugs = load_holiday_slugs(holidays_path)
    if not holiday_slugs:
        print(
            f"NOTE: no holiday slugs could be read from {holidays_path}; the "
            f"slug-collision check is off for this run.",
            file=sys.stderr,
        )

    pages = fetch_all_rows()
    print(f"fetched {len(pages)} rows from Notion")

    occasions = []
    warnings = []
    seen = {}
    for page in pages:
        entry, warning = extract_occasion(page, holiday_slugs)
        if warning:
            warnings.append(warning)
        if entry is None:
            continue
        if entry["slug"] in seen:
            warnings.append(
                f"duplicate slug {entry['slug']!r}: {entry['name']!r} collides "
                f"with {seen[entry['slug']]!r} -- keeping the first, skipping "
                f"this one"
            )
            continue
        seen[entry["slug"]] = entry["name"]
        occasions.append(entry)

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    # Deliberately NO empty-file guard and NO shrink guard, unlike
    # export_from_notion.py. Zero approved occasions is the normal state of
    # this database -- it is how the site looks today -- and a listing that
    # expires or is withdrawn *should* disappear immediately. Refusing to
    # write a short file here would keep a withdrawn paid listing live.
    occasions.sort(key=lambda o: (o["date"], o["slug"]))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(occasions, f, ensure_ascii=False, separators=(",", ":"))

    print(f"wrote {len(occasions)} approved occasion(s) to {out_path} "
          f"({len(warnings)} warnings)")


if __name__ == "__main__":
    main()
