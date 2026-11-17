"""Read and update Pipeline/Tracker.csv safely.

Usage:
  python3 tracker.py show [--json]              pipeline summary: counts, active roles, stale ones
  python3 tracker.py find "<text>"              rows whose company or role contains the text
  python3 tracker.py set <row> [--status S] [--applied YYYY-MM-DD] [--follow "YYYY-MM-DD; ..."]
                               [--next "text"] [--dry-run]
  python3 tracker.py add --company C --role R [--url U] [--status S] [--applied YYYY-MM-DD]
                         [--location L] [--folder F] [--next "text"] [--score N] [--verdict V]
                         [--role-type T] [--ghost G] [--salary S] [--dry-run]

<row> is the number `find` prints (1 = first data row). Rules (from CLAUDE.md):
- Only Status, Applied on, Follow up on, Next action and Updated change on an existing row.
  Rows are never reordered or deleted. New rows are appended.
- Status must be one of STATUSES. Setting Applied without --applied uses today.
- Updated is set to today on every change.
"""
import csv
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TRACKER = ROOT / "Pipeline" / "Tracker.csv"
STATUSES = ["Evaluated", "Applied", "Responded", "Interview", "Offer", "Rejected", "Discarded", "Skip"]
ACTIVE = ["Applied", "Responded", "Interview", "Offer"]
COLS = ["Date", "Company", "Role", "Role type", "Score", "Verdict", "Ghost tier", "Status", "Applied on",
        "Location", "Salary", "URL", "Folder", "Follow up on", "Next action", "Updated"]
TODAY = dt.date.today()
STALE_DAYS = 21  # applied this long ago with no response


def load():
    if not TRACKER.exists():
        return COLS, []
    with TRACKER.open(newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def save(cols, rows):
    with TRACKER.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def date_ok(s):
    for part in [p.strip() for p in s.split(";") if p.strip()]:
        dt.date.fromisoformat(part)
    return s


def day(s):
    try:
        return dt.date.fromisoformat((s or "").strip()[:10])
    except ValueError:
        return None


def brief(i, r):
    return {"row": i, "company": r["Company"], "role": r["Role"], "status": r["Status"],
            "applied_on": r.get("Applied on", ""), "follow_up_on": r.get("Follow up on", ""),
            "next_action": r.get("Next action", ""), "updated": r.get("Updated", "")}


def show(rows):
    counts = {s: sum(1 for r in rows if r["Status"] == s) for s in STATUSES}
    active, stale = [], []
    for i, r in enumerate(rows, 1):
        if r["Status"] not in ACTIVE:
            continue
        b = brief(i, r)
        a = day(r.get("Applied on"))
        b["days_since_applied"] = (TODAY - a).days if a else None
        active.append(b)
        if r["Status"] == "Applied" and a and (TODAY - a).days >= STALE_DAYS:
            stale.append(b)
    order = {s: n for n, s in enumerate(["Offer", "Interview", "Responded", "Applied"])}
    active.sort(key=lambda b: (order[b["status"]], -(b["days_since_applied"] or 0)))
    week = TODAY - dt.timedelta(days=7)
    applied_week = sum(1 for r in rows if (day(r.get("Applied on")) or dt.date.min) >= week)
    out = {"date": TODAY.isoformat(), "total": len(rows), "counts": counts,
           "applied_last_7_days": applied_week, "active": active, "stale": stale,
           "stale_rule": f"Applied {STALE_DAYS}+ days ago, still no response"}
    if "--json" in sys.argv:
        print(json.dumps(out, indent=1))
        return
    print(f"Pipeline on {out['date']}: " + ", ".join(f"{s} {n}" for s, n in counts.items() if n))
    print(f"Applied in the last 7 days: {applied_week}")
    for b in active:
        age = f", applied {b['days_since_applied']}d ago" if b["days_since_applied"] is not None else ""
        print(f"  [{b['row']}] {b['status']:9} {b['company']} | {b['role']}{age}"
              + (f" | next: {b['next_action']}" if b["next_action"] else ""))
    if stale:
        print(f"Stale ({out['stale_rule']}): " + "; ".join(f"{b['company']} ({b['days_since_applied']}d)" for b in stale))


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("show", "find", "set", "add"):
        sys.exit(__doc__)
    cmd, dry = sys.argv[1], "--dry-run" in sys.argv
    cols, rows = load()
    if cmd == "show":
        return show(rows)
    if cmd == "find":
        q = sys.argv[2].lower()
        hits = [brief(i, r) for i, r in enumerate(rows, 1)
                if q in r["Company"].lower() or q in r["Role"].lower()]
        return print(json.dumps(hits, indent=1))
    status = arg("--status")
    if status and status not in STATUSES:
        sys.exit(f"Status must be one of: {', '.join(STATUSES)}")
    applied = arg("--applied")
    if applied:
        date_ok(applied)
    follow = arg("--follow")
    if follow:
        date_ok(follow)
    if cmd == "set":
        i = int(sys.argv[2])
        if not 1 <= i <= len(rows):
            sys.exit(f"No row {i}; the tracker has {len(rows)} rows")
        r, before = rows[i - 1], dict(rows[i - 1])
        if status:
            r["Status"] = status
            if status == "Applied" and not applied and not r.get("Applied on"):
                applied = TODAY.isoformat()
        if applied:
            r["Applied on"] = applied
        if follow is not None:
            r["Follow up on"] = follow
        if arg("--next") is not None:
            r["Next action"] = arg("--next")
        r["Updated"] = TODAY.isoformat()
        changed = {k: [before[k], r[k]] for k in r if before.get(k) != r[k]}
    else:  # add
        company, role = arg("--company"), arg("--role")
        if not company or not role:
            sys.exit("add needs --company and --role")
        status = status or "Applied"
        if status == "Applied" and not applied:
            applied = TODAY.isoformat()
        r = {c: "" for c in cols}
        r.update({"Date": TODAY.isoformat(), "Company": company, "Role": role, "Status": status,
                  "Applied on": applied or "", "URL": arg("--url", ""), "Location": arg("--location", ""),
                  "Folder": arg("--folder", ""), "Next action": arg("--next", ""),
                  "Updated": TODAY.isoformat(), "Verdict": arg("--verdict", "Not scored"),
                  "Score": arg("--score", ""), "Role type": arg("--role-type", ""),
                  "Ghost tier": arg("--ghost", ""), "Salary": arg("--salary", "")})
        rows.append(r)
        i, changed = len(rows), {"added": brief(len(rows), r)}
    if not dry:
        save(cols, rows)
    print(json.dumps({"row": i, "dry_run": dry, "changed": changed}, indent=1))


if __name__ == "__main__":
    main()
