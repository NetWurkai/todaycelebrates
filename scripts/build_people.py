#!/usr/bin/env python3
"""Build scripts/people.json: who was born on each calendar date.

Two lists per date, shown as separate sub-blocks on the date pages:

  historic  deceased people, ranked by Wikipedia language-edition count
            ("sitelinks"): a stable, global notability signal
  living    living people, ranked by a 50/50 blend of sitelinks and median
            daily English Wikipedia pageviews over the last 60 days: sitelinks
            alone under-ranks famous Americans, pageviews alone follows the news

Sources, and why each is used
  * English Wikipedia's "On this day" births feed decides WHO is a candidate
    for a date. It is editor-curated, and it is the authority on the date.
  * Wikidata confirms the date, says whether the person has died, and supplies
    the sitelink count. A person is kept only when both sources agree on the
    month and day; disagreements are logged, never guessed at.
  * Wikipedia's pageviews API supplies the recency signal for living people.

Birth facts are Wikidata (CC0). Names link out to Wikipedia; descriptors are
the short factual phrase from the feed ("American actor"), not prose.

This is a data build, not a site build: run it by hand (about monthly, to catch
deaths among the living lists), review the diff of scripts/people.json, commit.
generate.py only ever reads the committed file, so the daily workflow makes no
network calls for this feature. Resumable: per-date responses are cached in
--cache, so an interrupted run picks up where it stopped.

  python3 scripts/build_people.py                    # fetch what is missing, then assemble
  python3 scripts/build_people.py --dates 10-10,02-29
  python3 scripts/build_people.py --assemble-only    # rebuild people.json from the cache
  python3 scripts/build_people.py --refresh          # ignore the cache, refetch

Stdlib only; Python 3.8+.
"""
import argparse
import collections
import datetime
import json
import math
import os
import re
import statistics
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

UA = "TodayCelebratesPeopleBuild/0.1 (https://todaycelebrates.com)"

FEED_URL = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/births/{mm}/{dd}"
WIKI_API = "https://en.wikipedia.org/w/api.php"
SPARQL_URL = "https://query.wikidata.org/sparql"

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "people.json")
DEFAULT_CACHE = os.path.join(HERE, ".people_cache")
DEFAULT_OVERRIDES = os.path.join(HERE, "people_overrides.json")

# ---- selection knobs -------------------------------------------------------
HISTORIC_KEEP = 12        # stored per date; the templates show fewer
LIVING_KEEP = 12
MIN_SL_HISTORIC = 25      # Wikipedia language editions
MIN_SL_LIVING = 20
MIN_VIEWS_LIVING = 150    # median English-Wikipedia views per day, last 60 days
PV_FETCH_MIN_SL = 15      # only living people at least this notable get a pageview lookup
PV_DAYS = 60

GREGORIAN = "Q1985727"
JULIAN = "Q1985786"

# Editorial policy: nobody with a recorded conviction (Wikidata P1399) is added
# automatically. It is deliberately blunt -- it keeps dictators and mass
# murderers off a "born on this day" list without a hand-kept deny list, at the
# price of also dropping the occasional fraud or tax conviction. Everything it
# drops is logged to <cache>/report.json, and any person can be put back with an
# "include" entry in people_overrides.json. Set False to turn the rule off.
EXCLUDE_CONVICTED = True

# Clauses that go stale or read wrong on a page that is regenerated for years:
# "current Governor", "since 2019", "61st Prime Minister". Dropped for living people.
STALE_CLAUSE = re.compile(r"\b(current|incumbent|since\s+\d{4}|\d+(?:st|nd|rd|th))\b", re.I)
DESCRIPTOR_MAX = 70

# Occupations that keep someone off an automatic birthday list. Matched by
# Wikidata QID and verified by label at run time (see verify_deny_labels), so a
# wrong id fails loudly instead of silently excluding the wrong people.
DENY_OCCUPATIONS = {
    "Q484188": "serial killer",
}


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ---- http ------------------------------------------------------------------
def http_json(url, data=None, headers=None, timeout=60, tries=6):
    hdr = {"User-Agent": UA, "Accept": "application/json"}
    hdr.update(headers or {})
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, data=body, headers=hdr)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504):
                try:
                    wait = int(e.headers.get("Retry-After") or 0)
                except ValueError:
                    wait = 0
                wait = wait or min(60, 5 * (attempt + 1))
                log("  HTTP %s from %s, waiting %ss" % (e.code, urllib.parse.urlparse(url).netloc, wait + 1))
                time.sleep(wait + 1)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("giving up on %s: %s" % (url, last))


# ---- stage A: the Wikipedia feed ------------------------------------------
def fetch_feed(mm, dd):
    d = http_json(FEED_URL.format(mm=mm, dd=dd))
    out = {}
    for b in (d or {}).get("births", []):
        pages = b.get("pages") or []
        if not pages:
            continue
        p = pages[0]
        qid = p.get("wikibase_item")
        title = (p.get("titles") or {}).get("canonical") or p.get("title")
        if not qid or not title:
            continue
        out.setdefault(qid, {
            "qid": qid,
            "title": title,
            "year": b.get("year"),
            "text": b.get("text", ""),
            "desc": p.get("description", ""),
        })
    return list(out.values())


# ---- stage B: Wikidata -----------------------------------------------------
def fetch_wikidata(qids):
    """qid -> {sl, dob:[(iso, precision, calendar, rank)], dod:[iso], deny:[labels], convicted:bool}"""
    result = {}
    deny_values = " ".join("wd:" + q for q in DENY_OCCUPATIONS)
    for i in range(0, len(qids), 150):
        chunk = qids[i:i + 150]
        values = " ".join("wd:" + q for q in chunk)
        query = """
SELECT ?p ?sl ?dob ?prec ?cal ?rk ?dod ?deny ?conv WHERE {
  VALUES ?p { %s }
  ?p wdt:P31 wd:Q5 ; wikibase:sitelinks ?sl .
  OPTIONAL {
    ?p p:P569 ?st . ?st wikibase:rank ?rk . FILTER(?rk != wikibase:DeprecatedRank)
    ?st psv:P569 ?n .
    ?n wikibase:timeValue ?dob ; wikibase:timePrecision ?prec ; wikibase:timeCalendarModel ?cal .
  }
  OPTIONAL { ?p wdt:P570 ?dod }
  OPTIONAL { VALUES ?deny { %s } ?p wdt:P106 ?deny }
  BIND(EXISTS { ?p wdt:P1399 [] } AS ?conv)
}""" % (values, deny_values)
        d = http_json(SPARQL_URL, data={"query": query, "format": "json"}, timeout=120)
        for row in d["results"]["bindings"]:
            g = lambda k: row.get(k, {}).get("value")
            qid = g("p").rsplit("/", 1)[-1]
            rec = result.setdefault(qid, {
                "sl": int(g("sl")), "dob": [], "dod": [], "deny": [], "convicted": False,
            })
            if g("dob"):
                item = [g("dob"), int(g("prec")), g("cal").rsplit("/", 1)[-1], g("rk").rsplit("#", 1)[-1]]
                if item not in rec["dob"]:
                    rec["dob"].append(item)
            if g("dod") and g("dod") not in rec["dod"]:
                rec["dod"].append(g("dod"))
            if g("deny"):
                lab = DENY_OCCUPATIONS.get(g("deny").rsplit("/", 1)[-1])
                if lab and lab not in rec["deny"]:
                    rec["deny"].append(lab)
            if g("conv") == "true":
                rec["convicted"] = True
        time.sleep(0.5)
    return result


def verify_deny_labels():
    """Fail loudly if a DENY_OCCUPATIONS id does not mean what we say it does."""
    values = " ".join("wd:" + q for q in DENY_OCCUPATIONS)
    q = "SELECT ?x ?l WHERE { VALUES ?x { %s } ?x rdfs:label ?l FILTER(LANG(?l)='en') }" % values
    d = http_json(SPARQL_URL, data={"query": q, "format": "json"})
    seen = {r["x"]["value"].rsplit("/", 1)[-1]: r["l"]["value"].lower() for r in d["results"]["bindings"]}
    for qid, want in DENY_OCCUPATIONS.items():
        if seen.get(qid) != want:
            raise SystemExit("DENY_OCCUPATIONS mismatch: %s is %r in Wikidata, expected %r" % (qid, seen.get(qid), want))


def julian_shift_match(y, mo, da, mm, dd):
    """True when Wikidata's date is Wikipedia's Julian date moved to Gregorian.

    Before 1583 Wikipedia files people under the date they were born on at the
    time (Julian); Wikidata often stores the Gregorian equivalent, so Zwingli is
    Jan 1 on Wikipedia and Jan 10 in Wikidata. Accept it when the gap is the
    expected Julian-Gregorian offset for that century (give or take a day).
    """
    if not 1100 <= y <= 1582:
        return False
    shift = y // 100 - y // 400 - 2
    for ty in (y - 1, y, y + 1):
        try:
            gap = (datetime.date(y, mo, da) - datetime.date(ty, int(mm), int(dd))).days
        except ValueError:
            continue
        if abs(gap - shift) <= 1:
            return True
    return False


def evaluate_date(claims, mm, dd):
    """-> (year, None) when Wikidata agrees this person was born on mm-dd, else (None, reason)."""
    live = [c for c in claims if c[1] == 11]
    if not live:
        return None, "no day-precision birth date"
    preferred = [c for c in live if c[3] == "PreferredRank"]
    use = preferred or live
    year = None
    for iso, prec, cal, rk in use:
        m = re.match(r"^(-?\d+)-(\d\d)-(\d\d)", iso)
        if not m:
            return None, "unparseable date"
        y, mo, da = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if (mo, da) != (int(mm), int(dd)) and not julian_shift_match(y, mo, da, mm, dd):
            return None, "wikidata says %s" % iso[:10]
        if y < 1:
            return None, "BCE"
        if cal == JULIAN and y >= 1583:
            return None, "Julian date after 1582 (ambiguous)"
        year = y
    return year, None


# ---- stage C: pageviews ----------------------------------------------------
def fetch_pageviews(titles):
    """title -> {median, max, days}, via the batched MediaWiki pageviews prop."""
    out = {}
    for i in range(0, len(titles), 50):
        batch = [t.replace("_", " ") for t in titles[i:i + 50]]
        params = {
            "action": "query", "format": "json", "prop": "pageviews", "pvipdays": PV_DAYS,
            "titles": "|".join(batch), "redirects": 1, "formatversion": 2,
        }
        back = {t: t for t in batch}
        # prop=pageviews answers only a slice of a batch per response and hands
        # back a `continue` token for the rest. Ignoring it silently loses about
        # a third of the titles, so follow it until the batch is complete.
        for _ in range(20):
            d = http_json(WIKI_API, data=params)
            q = (d or {}).get("query", {})
            for n in q.get("normalized", []):
                back[n["to"]] = back.get(n["from"], n["from"])
            for r in q.get("redirects", []):
                back[r["to"]] = back.get(r["from"], r["from"])
            for pg in q.get("pages", []):
                days = [v for v in (pg.get("pageviews") or {}).values() if v is not None]
                if days:
                    out[back.get(pg["title"], pg["title"])] = {
                        "median": statistics.median(days), "max": max(days), "days": len(days),
                    }
            cont = (d or {}).get("continue")
            if not cont:
                break
            params.update(cont)
            time.sleep(0.3)
        time.sleep(0.5)
    return out


# ---- per-date fetch, cached ------------------------------------------------
def views_needed(feed, wd, mm, dd):
    """Titles of living people on this date who are notable enough to need a pageview figure."""
    need = []
    for f in feed:
        w = wd.get(f["qid"])
        if not w or w["dod"] or w["sl"] < PV_FETCH_MIN_SL:
            continue
        year, _ = evaluate_date(w["dob"], mm, dd)
        if year:
            need.append(f["title"].replace("_", " "))
    return need


def write_cache(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(data, fh, ensure_ascii=False)
    os.replace(tmp, path)


def fill_views(data, mm, dd):
    """Fetch pageviews for anyone still missing one; returns (still_missing, fetched_now)."""
    need = views_needed(data["feed"], data["wd"], mm, dd)
    missing = [t for t in need if t not in data["views"]]
    for _ in range(2):  # a title can be missing for a transient reason; try twice
        if not missing:
            break
        data["views"].update(fetch_pageviews(missing))
        missing = [t for t in need if t not in data["views"]]
    return missing, len(need)


def fetch_date(mm, dd, cache_dir, refresh=False, fix_views=False):
    path = os.path.join(cache_dir, "%s-%s.json" % (mm, dd))
    if not refresh and os.path.exists(path):
        data = json.load(open(path))
        if fix_views and not data.get("views_ok"):
            before = len(data["views"])
            missing, need = fill_views(data, mm, dd)
            data["views_ok"] = True  # checked; later passes skip this date
            write_cache(path, data)
            log("  %s-%s: views %d -> %d of %d needed" % (mm, dd, before, len(data["views"]), need))
            return data, False
        return data, True
    feed = fetch_feed(mm, dd)
    wd = fetch_wikidata([f["qid"] for f in feed]) if feed else {}
    data = {
        "fetched": datetime.date.today().isoformat(),
        "feed": feed, "wd": wd, "views": {},
    }
    missing, need = fill_views(data, mm, dd) if feed else ([], 0)
    # Titles with no pageview figure after two retries are mostly brand-new or
    # renamed pages; a large shortfall means the service is misbehaving and the
    # living list for this date would be skewed, so say so.
    if need and len(missing) / need > 0.25:
        log("  WARNING %s-%s: pageviews missing for %d of %d candidates" % (mm, dd, len(missing), need))
    data["views_ok"] = True
    write_cache(path, data)
    return data, False


# ---- assembly ---------------------------------------------------------------
def clean_name(title):
    return re.sub(r"\s*\([^)]*\)\s*$", "", title.replace("_", " ")).strip()


def _norm(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower().strip()


def _shorten(rest, living):
    rest = re.sub(r"\s*\([^()]*\)\s*$", "", rest or "").strip()
    clauses = [c.strip(" ,;–—-") for c in re.split(r"[,;]\s+", rest) if c.strip(" ,;–—-")]
    if living:
        # Offices and affiliations are where a living person's descriptor goes
        # stale (an IMF director who left in 2019, a "current" governor). Keep
        # only the lead clause -- nationality and occupation -- and drop it too
        # if it carries a dating marker.
        clauses = [c for c in clauses[:1] if not STALE_CLAUSE.search(c)]
    out = ""
    for c in clauses:
        nxt = c if not out else out + ", " + c
        if out and len(nxt) > DESCRIPTOR_MAX:
            break
        out = nxt
    return out[:DESCRIPTOR_MAX * 2]


def clean_descriptor(text, name, wd_desc, living):
    """The short "American actor" phrase: the feed text after the name.

    The feed writes "Name, descriptor, descriptor". Take what follows the
    name; shorten to whole clauses; for living people drop clauses that date
    ("current Governor", "since 2019", "61st Prime Minister").
    """
    t = (text or "").strip()
    rest = ""
    if ", " in t:
        seg0, tail = t.split(", ", 1)
        a, b = _norm(seg0), _norm(name)
        if a and b and (a == b or a in b or b in a or a.split()[0] == b.split()[0]):
            rest = tail
    out = _shorten(rest, living)
    if not out:
        out = _shorten(re.sub(r"\s*\((?:born|died|\d)[^)]*\)\s*$", "", wd_desc or ""), living)
    return out


def all_dates():
    d = datetime.date(2024, 1, 1)  # a leap year, so 02-29 is included
    while d.year == 2024:
        yield "%02d" % d.month, "%02d" % d.day
        d += datetime.timedelta(days=1)


def load_overrides(path):
    if not os.path.exists(path):
        return {"exclude": {}, "include": []}
    data = json.load(open(path))
    data.setdefault("exclude", {})
    data.setdefault("include", [])
    return data


def collect_candidates(mm, dd, cached, report):
    """Everyone who passes the date check for one date, with a list assignment."""
    out = []
    for f in cached["feed"]:
        w = cached["wd"].get(f["qid"])
        label = "%s-%s %s (%s)" % (mm, dd, f["title"], f["qid"])
        if not w:
            report["dropped"].append([label, "not a human in Wikidata"])
            continue
        year, why = evaluate_date(w["dob"], mm, dd)
        if not year:
            report["dropped"].append([label, why])
            continue
        if w["deny"]:
            report["dropped"].append([label, "occupation: " + ", ".join(w["deny"])])
            continue
        if EXCLUDE_CONVICTED and w["convicted"]:
            report["dropped"].append([label, "has a recorded conviction (P1399)"])
            continue
        name = clean_name(f["title"])
        dyear = None
        if w["dod"]:
            # More than one death-date claim happens (Eva Braun carried a stray
            # 2026 next to 1945). Take the earliest year: a wrong late date is
            # the common error, and for a living person any death claim already
            # moves them off the living list, which is the safe direction.
            years = [int(m.group(1)) for m in (re.match(r"^(-?\d+)", s) for s in w["dod"]) if m]
            dyear = min(years) if years else 0
            if len(set(years)) > 1:
                report.setdefault("death_date_conflicts", []).append([label, sorted(set(years))])
        v = cached["views"].get(f["title"].replace("_", " "))
        out.append({
            "qid": f["qid"], "name": name, "title": f["title"].replace(" ", "_"),
            "y": year, "d": dyear,
            "w": clean_descriptor(f["text"], name, f.get("desc"), dyear is None),
            "sl": w["sl"], "v": int(v["median"]) if v else None,
        })
    return out


def assemble(cache_dir, out_path, overrides_path):
    ov = load_overrides(overrides_path)
    excluded = set(ov["exclude"])
    report = {"dropped": [], "missing_dates": []}
    per_date = {}
    for mm, dd in all_dates():
        p = os.path.join(cache_dir, "%s-%s.json" % (mm, dd))
        if not os.path.exists(p):
            report["missing_dates"].append("%s-%s" % (mm, dd))
            continue
        per_date["%s-%s" % (mm, dd)] = collect_candidates(mm, dd, json.load(open(p)), report)

    # A person who passes the date check on two different dates has a disputed
    # birthday (Maimonides is the usual example). Showing them on both is wrong
    # on at least one, so drop them from every date; an "include" override can
    # put them back on the right one.
    seen = collections.Counter(c["qid"] for lst in per_date.values() for c in lst)
    disputed = {q for q, n in seen.items() if n > 1}
    if disputed:
        for key, lst in per_date.items():
            for c in lst:
                if c["qid"] in disputed:
                    report["dropped"].append(["%s %s (%s)" % (key, c["title"], c["qid"]),
                                              "appears on %d dates" % seen[c["qid"]]])
            per_date[key] = [c for c in lst if c["qid"] not in disputed]

    # Global normalization for the living blend, so scores are comparable
    # across dates (z-scoring inside one date would reshuffle a thin date's list).
    living = [c for lst in per_date.values() for c in lst
              if c["d"] is None and c["v"] and c["sl"] >= MIN_SL_LIVING]
    ls = [math.log(c["sl"]) for c in living]
    lv = [math.log(max(c["v"], 1)) for c in living]
    ms, ss = (statistics.mean(ls), statistics.pstdev(ls) or 1) if ls else (0, 1)
    mv, sv = (statistics.mean(lv), statistics.pstdev(lv) or 1) if lv else (0, 1)

    dates = {}
    for key, cands in sorted(per_date.items()):
        # Overrides name people by QID ("Q352") or by Wikipedia title ("Joseph_Stalin").
        cands = [c for c in cands if c["qid"] not in excluded and c["title"] not in excluded]
        hist = [c for c in cands if c["d"] is not None and c["sl"] >= MIN_SL_HISTORIC]
        live = [c for c in cands if c["d"] is None and c["v"] and
                c["sl"] >= MIN_SL_LIVING and c["v"] >= MIN_VIEWS_LIVING]
        for c in live:
            c["score"] = 0.5 * (math.log(c["sl"]) - ms) / ss + 0.5 * (math.log(max(c["v"], 1)) - mv) / sv
        hist.sort(key=lambda c: (-c["sl"], c["y"], c["name"]))
        live.sort(key=lambda c: (-c["score"], c["name"]))
        dates[key] = {
            "historic": [rec(c) for c in hist[:HISTORIC_KEEP]],
            "living": [rec(c) for c in live[:LIVING_KEEP]],
        }

    for inc in ov["include"]:  # manual additions: {"date","list","name","title","y","d","w","sl"}
        slot = dates.setdefault(inc["date"], {"historic": [], "living": []})[inc["list"]]
        slot.append({k: inc[k] for k in ("name", "title", "y", "d", "w", "sl") if k in inc})
        slot.sort(key=lambda r: -r.get("sl", 0))

    meta = {
        "generated": datetime.date.today().isoformat(),
        "sources": "Dates and notability counts: Wikidata (CC0). Names link to Wikipedia.",
        "rules": {
            "historic": "deceased; ranked by Wikipedia language editions (sl)",
            "living": "living; ranked by blend of log(sl) and log(median daily views, %dd)" % PV_DAYS,
            "min_sl_historic": MIN_SL_HISTORIC, "min_sl_living": MIN_SL_LIVING,
            "min_views_living": MIN_VIEWS_LIVING,
        },
    }
    write_people(out_path, meta, dates)
    return dates, report


def rec(c):
    r = {"name": c["name"], "title": c["title"], "y": c["y"], "d": c["d"], "w": c["w"], "sl": c["sl"]}
    if c["d"] is None:
        r["v"] = c["v"]
    return r


def write_people(path, meta, dates):
    """One record per line, so a monthly refresh is a readable git diff."""
    lines = ["{", '"meta": ' + json.dumps(meta, ensure_ascii=False) + ",", '"dates": {']
    keys = sorted(dates)
    for i, k in enumerate(keys):
        lines.append('"%s": {' % k)
        for j, lst in enumerate(("historic", "living")):
            recs = dates[k][lst]
            body = ",\n".join("  " + json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in recs)
            lines.append(' "%s": [%s]%s' % (lst, ("\n" + body + "\n ") if recs else "", "," if j == 0 else ""))
        lines.append("}" + ("," if i < len(keys) - 1 else ""))
    lines += ["}", "}"]
    text = "\n".join(lines) + "\n"
    json.loads(text)  # refuse to write anything that is not valid JSON
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--overrides", default=DEFAULT_OVERRIDES)
    ap.add_argument("--dates", help="comma-separated MM-DD list (default: all 366)")
    ap.add_argument("--refresh", action="store_true", help="ignore cached responses")
    ap.add_argument("--assemble-only", action="store_true")
    ap.add_argument("--fix-views", action="store_true",
                    help="top up missing pageview figures in already-cached dates")
    ap.add_argument("--budget", type=int, default=0,
                    help="stop fetching after this many seconds (re-run to resume)")
    args = ap.parse_args()

    if not args.assemble_only:
        verify_deny_labels()
        wanted = [tuple(x.split("-")) for x in args.dates.split(",")] if args.dates else list(all_dates())
        t0 = time.time()
        fetched = 0
        for n, (mm, dd) in enumerate(wanted, 1):
            if args.budget and time.time() - t0 > args.budget:
                log("budget reached after %d fetches; re-run to resume" % fetched)
                break
            _, from_cache = fetch_date(mm, dd, args.cache, args.refresh, args.fix_views)
            if not from_cache:
                fetched += 1
                log("[%d/%d] %s-%s %s" % (n, len(wanted), mm, dd, "topped up" if args.fix_views else "fetched"))

    dates, report = assemble(args.cache, args.out, args.overrides)
    h = [len(v["historic"]) for v in dates.values()]
    l = [len(v["living"]) for v in dates.values()]
    log("dates assembled: %d | historic avg %.1f (min %d) | living avg %.1f (min %d)" % (
        len(dates), sum(h) / max(len(h), 1), min(h or [0]), sum(l) / max(len(l), 1), min(l or [0])))
    if report["missing_dates"]:
        log("no cache for %d dates (people.json is incomplete): %s%s" % (
            len(report["missing_dates"]), ", ".join(report["missing_dates"][:8]),
            " ..." if len(report["missing_dates"]) > 8 else ""))
    os.makedirs(args.cache, exist_ok=True)
    with open(os.path.join(args.cache, "report.json"), "w") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    log("wrote %s (dropped-candidate log: %s)" % (args.out, os.path.join(args.cache, "report.json")))


if __name__ == "__main__":
    main()
