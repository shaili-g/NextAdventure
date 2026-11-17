"""Review what the job search screened out, to catch filters that miss good roles.

Usage: python3 screened.py [--days N | --since YYYY-MM-DD] [--all] [--json]

Reads Pipeline/Scan History.tsv and the tracker's Skip rows. Prints:
  1. Counts by reason (title, location, too old, already tracked; tracker Skips).
  2. Near-misses: title skips that share a word with the titles in Scan Config
     "title_include" and contain no "title_exclude" word. These are the
     ones to eyeball: if one should have passed, widen Scan Config, then run
     scan.py --recheck.
  3. Every location skip (few, and easy to get wrong).
  4. Tracker Skips with their reasons.
--all also lists every title skip. Default window: the last 1 day.
"""
import csv
import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HISTORY = ROOT / "Pipeline" / "Scan History.tsv"
TRACKER = ROOT / "Pipeline" / "Tracker.csv"
CONFIG = ROOT / "Profile" / "Scan Config.json"


GENERIC = {"manager", "management", "director", "head", "lead", "leader", "senior", "staff", "principal",
           "associate", "vice", "president", "chief", "officer", "group", "the", "and", "for", "with", "team"}


def _words(phrases, drop=GENERIC):
    ws = {w for p in phrases if not p.startswith("_") for w in re.findall(r"[a-z][a-z+#.]{2,}", p.lower())} - drop
    return re.compile(r"\b(" + "|".join(sorted(map(re.escape, ws))) + r")\b", re.I) if ws else re.compile(r"(?!x)x")


_cfg = json.loads(CONFIG.read_text()) if CONFIG.exists() else {}
# Near-miss = a skipped title sharing a distinctive word with the titles searched for, and no excluded title phrase.
SIGNAL = _words(_cfg.get("title_include", []))
_excl = [x.lower() for x in _cfg.get("title_exclude", []) if not x.startswith("_")]
OTHER_FUNCTION = re.compile("|".join(r"\b" + re.escape(x) + r"\b" for x in _excl), re.I) if _excl else re.compile(r"(?!x)x")


def window():
    today = dt.date.today()
    if "--since" in sys.argv:
        return dt.date.fromisoformat(sys.argv[sys.argv.index("--since") + 1])
    days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 1
    return today - dt.timedelta(days=days - 1)


def main():
    start = window()
    rows = [r for r in csv.DictReader(HISTORY.open(), delimiter="\t")
            if dt.date.fromisoformat(r["first_seen"]) >= start]
    skips = [r for r in csv.DictReader(TRACKER.open())
             if r["Status"] == "Skip" and r["Updated"] >= start.isoformat()]
    counts = Counter(r["status"] for r in rows)
    title = [r for r in rows if r["status"] == "skipped_title"]
    near, dedup = [], set()
    for r in title:
        k = (r["company"], r["title"])
        if k in dedup:
            continue
        dedup.add(k)
        if SIGNAL.search(r["title"]) and not OTHER_FUNCTION.search(r["title"]):
            near.append(r)
    loc = [r for r in rows if r["status"] == "skipped_location"]
    out = dict(since=start.isoformat(), counts=dict(counts), tracker_skips=len(skips),
               near_misses=[{k: r[k] for k in ("company", "title", "location", "url")} for r in near],
               location_skips=[{k: r[k] for k in ("company", "title", "location", "url")} for r in loc],
               skips=[{"company": r["Company"], "role": r["Role"], "reason": r["Next action"]} for r in skips])
    if "--json" in sys.argv:
        print(json.dumps(out, indent=1))
        return
    print(f"Screened out since {start} ({len(rows)} postings seen)")
    print("  " + ", ".join(f"{k}: {v}" for k, v in counts.most_common()) + f"; tracker Skips: {len(skips)}")
    print(f"\nNear-misses to eyeball ({len(near)}):")
    for r in near:
        print(f"  - {r['company']} | {r['title']} | {r['location'][:45]} | {r['url']}")
    print(f"\nLocation skips ({len(loc)}):")
    for r in loc:
        print(f"  - {r['company']} | {r['title']} | {r['location'][:60]}")
    print(f"\nScreened out after reading the posting ({len(skips)}):")
    for r in skips:
        print(f"  - {r['Company']} | {r['Role']} | {r['Next action']}")
    if "--all" in sys.argv:
        print(f"\nAll title skips ({len(dedup)} unique):")
        for c, t in sorted(dedup):
            print(f"  - {c} | {t}")


if __name__ == "__main__":
    main()
