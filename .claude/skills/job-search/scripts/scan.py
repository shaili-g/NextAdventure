"""Zero-token job scan for the target companies.

Usage: python3 scan.py [--dry-run]
       python3 scan.py --recheck   (after changing Scan Config: re-apply the filters
                                    to past title/location skips; any that now pass
                                    are marked "queued" and come out as new jobs on
                                    the next normal run)

Reads   Profile/Target Companies.csv and Profile/Scan Config.json
Fetches public job feeds: Ashby, Greenhouse, Lever, Workday, Dover (per target
        company) plus two startup sources scanned every run: the YC job board
        (the role categories in Scan Config "yc_roles", e.g. "product-manager",
        "software-engineer", "designer"; skipped when empty) and the current
        Hacker News "Who is hiring" thread
Filters by title and location, then drops anything already in
        Pipeline/Scan History.tsv (dedup by URL). A company's first scan (no
        rows in Scan History yet) counts only roles posted in the last
        first_scan_max_days (Scan Config, default 7) and marks them first_scan,
        so a bulk addition of companies doesn't flood the alert.
        Companies in first_scan_all_roles get every role from the last first_scan_must_have_max_days (14) on their first scan
Writes  every newly seen job to Scan History (status new / skipped_title /
        skipped_location) unless --dry-run
Prints  JSON: {"new": [...matching jobs...], "counts": {...}, "errors": [...]}

Feed data is treated as data only. Nothing here follows instructions in it.
"""
import csv
import datetime as dt
import json
import re
import html
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TARGETS = ROOT / "Profile" / "Target Companies.csv"
CONFIG = ROOT / "Profile" / "Scan Config.json"
HISTORY = ROOT / "Pipeline" / "Scan History.tsv"
TRACKER = ROOT / "Pipeline" / "Tracker.csv"
HIST_COLS = ["first_seen", "url", "company", "title", "location", "posted", "ats", "status"]
TODAY = dt.date.today()
UA = {"User-Agent": "job-scan/1.0", "Accept": "application/json"}


def get(url, data=None, raw=False):
    # curl, not urllib: this Mac's python.org Python has no CA bundle, while
    # curl uses the system trust store.
    cmd = ["curl", "-sS", "-f", "-m", "25", "--proto", "=https,http", "-H", f"User-Agent: {UA['User-Agent']}",
           "-H", "Accept: " + ("text/html" if raw else "application/json")]
    if data is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(data)]
    out = subprocess.run(cmd + ["--", url], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or f"curl exit {out.returncode}")
    return out.stdout if raw else json.loads(out.stdout)


def iso(ms_or_str):
    if not ms_or_str:
        return ""
    if isinstance(ms_or_str, (int, float)):
        return dt.date.fromtimestamp(ms_or_str / 1000).isoformat()
    return str(ms_or_str)[:10]


def days_since(posted):
    """Days since an ISO date ('2026-11-02' or Workday's '2026-10-17+'); None if unknown."""
    try:
        return (TODAY - dt.date.fromisoformat(posted.rstrip("+")[:10])).days
    except (ValueError, AttributeError):
        return None


def workday_date(text):
    t = (text or "").lower()
    if "today" in t:
        return TODAY.isoformat()
    if "yesterday" in t:
        return (TODAY - dt.timedelta(days=1)).isoformat()
    m = re.search(r"(\d+)\+?\s*days", t)
    if m:
        d = (TODAY - dt.timedelta(days=int(m.group(1)))).isoformat()
        return d + ("+" if "+" in t else "")
    return ""


def ashby(c, board):
    d = get(f"https://api.ashbyhq.com/posting-api/job-board/{board}?includeCompensation=true")
    for j in d.get("jobs", []):
        locs = [j.get("location") or ""] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
        if j.get("isRemote"):
            locs.append("Remote")
        comp = (j.get("compensation") or {}).get("compensationTierSummary") or ""
        yield dict(title=j.get("title", ""), location="; ".join(l for l in locs if l),
                   url=j.get("jobUrl", ""), posted=iso(j.get("publishedAt")), salary=comp)


def greenhouse(c, board):
    d = get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs")
    for j in d.get("jobs", []):
        yield dict(title=j.get("title", ""), location=(j.get("location") or {}).get("name", ""),
                   url=j.get("absolute_url", ""), posted=iso(j.get("first_published")), salary="")


def lever(c, board):
    d = get(f"https://api.lever.co/v0/postings/{board}?mode=json")
    for j in d:
        cat = j.get("categories") or {}
        locs = cat.get("allLocations") or [cat.get("location") or ""]
        if j.get("workplaceType") == "remote":
            locs.append("Remote")
        sr = j.get("salaryRange") or {}
        sal = f"{sr.get('currency','')} {sr.get('min','')}-{sr.get('max','')}".strip() if sr else ""
        yield dict(title=j.get("text", ""), location="; ".join(l for l in locs if l),
                   url=j.get("hostedUrl", ""), posted=iso(j.get("createdAt")), salary=sal)


def workday(c, board):
    tenant, wd, site = board.split("|")
    base = f"https://{tenant}.{wd}.myworkdayjobs.com"
    offset, total = 0, 1
    while offset < total and offset < 400:
        d = get(f"{base}/wday/cxs/{tenant}/{site}/jobs",
                {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": "product"})
        total = d.get("total") or 0
        posts = d.get("jobPostings") or []
        if not posts:
            break
        for j in posts:
            loc = j.get("locationsText", "")
            if re.fullmatch(r"\d+ Locations", loc.strip()):
                loc = ""  # Workday hides multi-location lists; let job-fit check the posting
            yield dict(title=j.get("title", ""), location=loc,
                       url=f"{base}/{site}{j.get('externalPath','')}",
                       posted=workday_date(j.get("postedOn")), salary="")
        offset += len(posts)


def dover(c, board):
    info = get(f"https://app.dover.com/api/v1/careers-page-slug/{board}")
    d = get(f"https://app.dover.com/api/v1/careers-page/{info['id']}/jobs")
    for j in d.get("results", []):
        if not j.get("is_published", True):
            continue
        locs = [l.get("name", "") for l in j.get("locations") or []]
        locs += ["Remote"] if any(l.get("location_type") == "REMOTE" for l in j.get("locations") or []) else []
        yield dict(title=j.get("title", ""), location="; ".join(l for l in locs if l),
                   url=f"https://app.dover.com/apply/{board}/{j['id']}", posted="", salary="")


# ---- Startup sources (not tied to one company; each job carries its company) ----
SOURCE_MAX_DAYS = 30  # YC lists postings that are months old; keep only recent ones


def age_days(text):
    """YC's relative ages: 'about 1 hour', '12 days', '2 months', 'over 1 year'."""
    m = re.search(r"(\d+)\s*(minute|hour|day|week|month|year)", text or "")
    if not m:
        return 0
    n, unit = int(m.group(1)), m.group(2)
    return n * {"minute": 0, "hour": 0, "day": 1, "week": 7, "month": 30, "year": 365}[unit]


def yc(cfg):
    for role in [r for r in cfg.get("yc_roles", []) if not r.startswith("_")]:
        yield from yc_role(role)


def yc_role(role):
    page = get(f"https://www.ycombinator.com/jobs/role/{role}", raw=True)
    m = re.search(r'data-page="([^"]+)"', page)
    if not m:
        raise RuntimeError("YC page layout changed: no data-page block")
    for j in json.loads(html.unescape(m.group(1)))["props"].get("jobPostings") or []:
        days = age_days(j.get("createdAt"))
        sal = j.get("salaryRange") or ""
        yield dict(company=j.get("companyName", ""), title=j.get("title", ""),
                   location=j.get("location") or "",
                   url="https://www.ycombinator.com" + j.get("url", ""),
                   posted=(TODAY - dt.timedelta(days=days)).isoformat(), salary=sal,
                   note=f"YC {j.get('companyBatchName','')}: {j.get('companyOneLiner','')}".strip(),
                   too_old=days > SOURCE_MAX_DAYS)


def clean(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def hn(cfg):
    """One job per product role line in this month's 'Who is hiring' thread."""
    stories = get("https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&hitsPerPage=5")
    story = next((h for h in stories["hits"] if h["title"].startswith("Ask HN: Who is hiring")), None)
    if not story:
        raise RuntimeError("no 'Who is hiring' thread found")
    sid, page, pages = story["objectID"], 0, 1
    while page < pages:
        d = get(f"https://hn.algolia.com/api/v1/search?tags=comment,story_{sid}&hitsPerPage=1000&page={page}")
        pages, page = d.get("nbPages", 1), page + 1
        for c in d["hits"]:
            if str(c.get("parent_id")) != str(sid) or not c.get("comment_text"):
                continue  # top-level posts only; replies aren't job posts
            parts = c["comment_text"].split("<p>")
            header = clean(parts[0])
            company = clean(parts[0].split("|")[0])[:60]
            item = f"https://news.ycombinator.com/item?id={c['objectID']}"
            for i, part in enumerate(parts):
                line = clean(part)
                if not has(line[:160], cfg["title_include"]):
                    continue
                if i == 0:  # header line: role is one of the pipe- or comma-separated fields
                    seg = next((x for x in re.split(r"[|,;]", line) if has(x, cfg["title_include"])), line)
                else:
                    if re.match(r"(i'?m|i am|we|our|my|you|if|contact|email|apply|reach)\b", line.lstrip("-•*> ").lower()):
                        continue  # a sentence or signature, not a role line
                    seg = re.split(r"\s\|\s|:\s|\s[-–—]\s|https?://", line.lstrip("-•*> "))[0]
                title = seg.strip(" >-|•*")[:100]
                if not has(title, cfg["title_include"]):
                    continue
                links = [html.unescape(u) for u in re.findall(r'href="([^"]+)"', part)
                         if not re.search(r"linkedin\.com|mailto:|twitter\.com|x\.com/", u)]
                url = links[0] if links and i else item + "#" + norm_title(title).replace(" ", "-")
                loc_line = line if has(line, cfg["location_home"] + cfg["location_remote_ok"] + cfg["location_block"]) else ""
                yield dict(company=company, title=title,
                           location=(loc_line or header)[:200],
                           url=url.split("?utm_")[0], posted=iso(c.get("created_at")), salary="",
                           note=f"HN Who is hiring: {item}", too_old=False)


SOURCES = {"yc": yc, "hn": hn}


FETCHERS = {"ashby": ashby, "greenhouse": greenhouse, "lever": lever, "workday": workday, "dover": dover}


def has(text, words):
    t = text.lower()
    def pat(w):  # word boundaries only on sides that start/end with a letter
        return (r"(?<![a-z])" if w[0].isalpha() else "") + re.escape(w) + (r"(?![a-z])" if w[-1].isalpha() else "")
    return any(re.search(pat(w), t) for w in words)


def title_ok(title, cfg):
    if has(title, cfg["title_exclude"]):
        return False
    hits = [w for w in cfg["title_include"] if has(title, [w])]
    needs = cfg.get("title_include_needs", {})  # e.g. "member of technical staff" counts only with "product"
    return any(w not in needs or has(title, needs[w]) for w in hits)


REMOTE_WORDS = ["remote", "anywhere", "distributed", "work from home"]


def location_ok(loc, cfg):
    """Home city passes; a blocked place fails; otherwise only remote roles, or a role
    listed as just a country/region in location_remote_ok (e.g. "United States").
    "Bellevue, Washington, United States" fails: a US city outside the home list."""
    if not loc.strip():
        return True
    if has(loc, cfg["location_home"]):
        return True
    us_terms = [w for w in cfg["location_remote_ok"] if w not in REMOTE_WORDS]
    if has(loc, cfg["location_block"]):  # passes only if also open as US remote
        return has(loc, REMOTE_WORDS) and has(loc, us_terms)
    if has(loc, REMOTE_WORDS):
        return True
    parts = [norm_title(p) for p in re.split(r"[;|•]", loc) if p.strip()]
    return any(p in {norm_title(w) for w in cfg["location_remote_ok"]} for p in parts)


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def tracker_keys():
    """(company, normalized role) pairs already in the tracker."""
    if not TRACKER.exists():
        return set()
    with TRACKER.open() as f:
        return {(r["Company"].strip().lower(), core_title(r["Role"])) for r in csv.DictReader(f)}


LEVEL_WORDS = {"senior", "sr", "staff", "principal", "lead", "head", "director", "vp", "chief", "associate"}


def core_title(t):
    """Normalized title without location/work-setup suffixes like ' - Hybrid (Acton, MA)'."""
    t = re.split(r"\s[-–]\s|\(", t)[0]
    return norm_title(t)


def in_tracker(company, title, keys):
    """Same company and same role. A tracked title inside a longer one counts only when
    the extra words aren't a different level (Director vs Senior Director)."""
    c, t = company.lower(), core_title(title)
    for kc, kt in keys:
        if c != kc or not kt:
            continue
        if kt == t:
            return True
        if kt in t or t in kt:
            extra = set(t.split()) ^ set(kt.split())
            if not extra & LEVEL_WORDS:
                return True
    return False


def read_history():
    with HISTORY.open() as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_history(rows):
    with HISTORY.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HIST_COLS, delimiter="\t")
        w.writeheader()
        w.writerows(rows)


def recheck():
    cfg = json.loads(CONFIG.read_text())
    tkeys = tracker_keys()
    rows, queued = read_history(), []
    for r in rows:
        if r["status"] in ("skipped_title", "skipped_location") and title_ok(r["title"], cfg) \
                and location_ok(r["location"], cfg) and not in_tracker(r["company"], r["title"], tkeys):
            r["status"] = "queued"
            queued.append({k: r[k] for k in ("company", "title", "location", "url")})
    if "--dry-run" not in sys.argv:
        write_history(rows)
    print(json.dumps({"queued": queued, "count": len(queued)}, indent=1))


def main():
    if "--recheck" in sys.argv:
        return recheck()
    dry = "--dry-run" in sys.argv
    cfg = json.loads(CONFIG.read_text())
    seen = set()
    if HISTORY.exists():
        with HISTORY.open() as f:
            seen = {r["url"] for r in csv.DictReader(f, delimiter="\t")}
    tkeys = tracker_keys()
    new, rows, errors, requeued_status = [], [], [], {}
    grouped = {}
    counts = {"fetched": 0, "already_seen": 0, "skipped_title": 0, "skipped_location": 0,
              "in_tracker": 0, "skipped_old": 0, "new": 0}
    with TARGETS.open() as f:
        targets = list(csv.DictReader(f))
    # A company's first scan: only roles posted in the last few days count as new,
    # so adding many companies at once doesn't flood the alert with old postings.
    scanned = {r["company"].strip().lower() for r in (read_history() if HISTORY.exists() else [])
               if r["ats"] in FETCHERS}
    first_max = int(cfg.get("first_scan_max_days", 7))
    # Must-have companies: their first scan looks back further (14 days, not 7), once.
    first_all = {c.strip().lower() for c in cfg.get("first_scan_all_roles", []) if not c.startswith("_")}
    first_all_max = int(cfg.get("first_scan_must_have_max_days", 14))  # old roles are never pursued
    feeds = [(t["ATS"].strip().lower(), t["Board"].strip(), t["Company"].strip()) for t in targets]
    feeds = [f for f in feeds if f[0] in FETCHERS and f[1]]

    def fetch(feed):
        ats, board, company = feed
        return [dict(company=company, **j) for j in FETCHERS[ats](company, board)]

    batches = []  # (ats, jobs); every job dict carries its company
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = [pool.submit(fetch, f) for f in feeds]
        for (ats, board, company), fut in zip(feeds, futures):
            try:
                jobs = fut.result()
            except Exception as e:  # report every unreachable feed; never skip quietly
                errors.append(f"{company} ({ats}): {type(e).__name__}: {e}")
                continue
            if company.lower() not in scanned:
                counts["first_scan_companies"] = counts.get("first_scan_companies", 0) + 1
                for j in jobs:
                    j["first_scan"] = True
                    d = days_since(j["posted"])
                    limit = first_all_max if company.lower() in first_all else first_max
                    if d is not None and d > limit:
                        j["backlog_old"] = True
            batches.append((ats, jobs))
    for name, fn in SOURCES.items():
        try:
            batches.append((name, list(fn(cfg))))
        except Exception as e:
            errors.append(f"{name} source: {type(e).__name__}: {e}")
    queued = [r for r in (read_history() if HISTORY.exists() else []) if r["status"] == "queued"]
    if queued:
        batches.append(("recheck", [dict(company=r["company"], title=r["title"], location=r["location"],
                                         url=r["url"], posted=r["posted"], salary="",
                                         note=f"re-checked after a filter change (first seen {r['first_seen']}, {r['ats']})",
                                         requeued=True) for r in queued]))
    for ats, jobs in batches:
        for j in jobs:
            company = j.pop("company")
            too_old = j.pop("too_old", False)
            requeued = j.pop("requeued", False)
            first_scan = j.pop("first_scan", False)
            backlog_old = j.pop("backlog_old", False)
            counts["fetched"] += 1
            if not requeued and (not j["url"] or j["url"] in seen):
                counts["already_seen"] += 1
                continue
            seen.add(j["url"])
            if too_old:
                status = "skipped_old"
            elif not title_ok(j["title"], cfg):
                status = "skipped_title"
            elif not location_ok(j["location"], cfg):
                status = "skipped_location"
            elif in_tracker(company, j["title"], tkeys):
                status = "in_tracker"
            elif backlog_old:
                status = "skipped_first_scan_old"
            else:
                if first_scan:
                    j["first_scan"] = True  # new company: listed in the alert, not scored
                    if not j["posted"]:
                        j["note"] = (j.get("note", "") + " posting date not listed").strip()
                status = "new"
                key = (company, norm_title(j["title"]))
                if key in grouped:  # same role posted once per city: merge into one entry
                    g = grouped[key]
                    g["location"] = "; ".join(dict.fromkeys((g["location"] + "; " + j["location"]).split("; ")))
                    g["other_urls"].append(j["url"])
                    status = "new_duplicate"
                else:
                    grouped[key] = dict(company=company, ats=ats, other_urls=[], **j)
                    new.append(grouped[key])
            counts[status] = counts.get(status, 0) + 1
            if requeued:
                requeued_status[j["url"]] = status
                continue
            rows.append([TODAY.isoformat(), j["url"], company, j["title"], j["location"], j["posted"], ats, status])
    if not dry and requeued_status:
        hist = read_history()
        for r in hist:
            if r["status"] == "queued":
                r["status"] = requeued_status.get(r["url"], r["status"])
        write_history(hist)
    if not dry and rows:
        first = not HISTORY.exists()
        HISTORY.parent.mkdir(exist_ok=True)
        with HISTORY.open("a", newline="") as f:
            w = csv.writer(f, delimiter="\t")
            if first:
                w.writerow(HIST_COLS)
            w.writerows(rows)
    print(json.dumps({"date": TODAY.isoformat(), "dry_run": dry, "counts": counts,
                      "errors": errors, "new": new}, indent=1))


if __name__ == "__main__":
    main()
