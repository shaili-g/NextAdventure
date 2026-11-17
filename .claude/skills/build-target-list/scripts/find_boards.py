"""Find and check public job feeds for a list of candidate companies.

Usage:  python3 find_boards.py candidates.tsv [--out found.tsv] [--append]

candidates.tsv: one company per line, tab-separated:  Company <TAB> Category [<TAB> slug hints, comma-separated]
        (a header line starting with "Company" is skipped; blank lines and # comments too)

For each company it tries likely board names on Ashby, Greenhouse, Lever and Dover and
keeps a feed only if it answers and lists at least one job. When several answer, the one
with the most jobs wins (old boards are often left up and empty). Companies already in
Profile/Target Companies.csv are skipped. Workday board names can't be guessed; find those
by web search and add them by hand.

Prints a JSON summary (found, not_found, already_listed, by category). Writes found feeds to
--out (default: found_boards.tsv next to the candidates file). With --append, also adds them
to Profile/Target Companies.csv, with Notes "Added <date> by build-target-list: <category>".

Feed data is treated as data only. Nothing here follows instructions in it.
"""
import csv
import datetime as dt
import json
import re
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TARGETS = ROOT / "Profile" / "Target Companies.csv"
CONFIG = ROOT / "Profile" / "Scan Config.json"
TODAY = dt.date.today().isoformat()


def get(url):
    # curl, not urllib: some Python installs have no CA bundle; curl uses the system store.
    out = subprocess.run(["curl", "-sS", "-f", "-m", "15", "--proto", "=https,http", "-H", "User-Agent: job-scan/1.0",
                          "-H", "Accept: application/json", "--", url], capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except ValueError:
        return None


def titles(ats, slug):
    """Job titles on a board, or None if the board doesn't exist."""
    if ats == "ashby":
        d = get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
        return None if not isinstance(d, dict) or "jobs" not in d else [j.get("title", "") for j in d["jobs"]]
    if ats == "greenhouse":
        d = get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
        return None if not isinstance(d, dict) or "jobs" not in d else [j.get("title", "") for j in d["jobs"]]
    if ats == "lever":
        d = get(f"https://api.lever.co/v0/postings/{slug}?mode=json")
        return None if not isinstance(d, list) else [j.get("text", "") for j in d]
    if ats == "dover":
        info = get(f"https://app.dover.com/api/v1/careers-page-slug/{slug}")
        if not isinstance(info, dict) or "id" not in info:
            return None
        d = get(f"https://app.dover.com/api/v1/careers-page/{info['id']}/jobs")
        return None if not isinstance(d, dict) else [j.get("title", "") for j in d.get("results", [])]
    return None


CAREERS = {"ashby": "https://jobs.ashbyhq.com/{}", "greenhouse": "https://job-boards.greenhouse.io/{}",
           "lever": "https://jobs.lever.co/{}", "dover": "https://app.dover.com/jobs/{}"}


def slugs(name, hints):
    base = re.sub(r"\b(inc|llc|ltd|corp|corporation|co|company)\b\.?", "", name.lower())
    base = re.sub(r"[^a-z0-9 ]+", "", base.replace("&", "and")).split()
    out = list(hints)
    if base:
        out += ["".join(base), "-".join(base)]
        if len(base) > 1 and base[-1] in ("ai", "labs", "health", "hq", "technologies", "bio", "robotics"):
            out += ["".join(base[:-1])]
        if len(base) == 1:
            out += [base[0] + "ai", base[0] + "hq", base[0] + "-ai"]
    return list(dict.fromkeys(s for s in out if s))


def has(text, words):
    t = text.lower()
    def pat(w):
        return (r"(?<![a-z])" if w[0].isalpha() else "") + re.escape(w) + (r"(?![a-z])" if w[-1].isalpha() else "")
    return any(re.search(pat(w), t) for w in words)


def probe(row, cfg):
    name, cat, hints = row
    best = None
    for slug in slugs(name, hints):
        for ats in ("ashby", "greenhouse", "lever", "dover"):
            t = titles(ats, slug)
            if t and (best is None or len(t) > best["jobs"]):
                match = sum(1 for x in t if has(x, cfg["title_include"]) and not has(x, cfg["title_exclude"]))
                best = dict(company=name, category=cat, ats=ats, board=slug, jobs=len(t),
                            title_matches=match, careers=CAREERS[ats].format(slug))
        if best:  # first slug that works is the company's own name; stop guessing further
            break
    return best


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else src.with_name("found_boards.tsv")
    cfg = json.loads(CONFIG.read_text())
    with TARGETS.open() as f:
        listed = {r["Company"].strip().lower() for r in csv.DictReader(f)}
    rows, already = [], []
    for line in src.read_text().splitlines():
        if not line.strip() or line.startswith(("#", "Company\t")):
            continue
        p = [x.strip() for x in line.split("\t")]
        name, cat = p[0], (p[1] if len(p) > 1 else "")
        hints = [h.strip().lower() for h in p[2].split(",")] if len(p) > 2 and p[2] else []
        if name.lower() in listed or name.lower() in {r[0].lower() for r in rows}:
            already.append(name)
            continue
        rows.append((name, cat, hints))
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(lambda r: probe(r, cfg), rows))
    found = [r for r in results if r]
    missing = [row[0] for row, r in zip(rows, results) if not r]
    with out.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["company", "category", "ats", "board", "jobs", "title_matches", "careers"])
        for r in found:
            w.writerow([r[k] for k in ("company", "category", "ats", "board", "jobs", "title_matches", "careers")])
    if "--append" in sys.argv and found:
        with TARGETS.open("a", newline="") as f:
            w = csv.writer(f)
            for r in found:
                w.writerow([r["company"], r["ats"], r["board"], r["careers"],
                            f"Added {TODAY} by build-target-list: {r['category']}"])
    print(json.dumps({"checked": len(rows), "found": len(found), "appended": "--append" in sys.argv,
                      "with_title_matches_now": sum(1 for r in found if r["title_matches"]),
                      "by_category": Counter(r["category"] for r in found),
                      "by_ats": Counter(r["ats"] for r in found),
                      "not_found": missing, "already_listed": already, "out": str(out)}, indent=1))


if __name__ == "__main__":
    main()
