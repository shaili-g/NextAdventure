"""Build the dashboard page (today's alert, to-dos, tracker) from local files.

Usage: python3 build_dashboard.py [--alert Pipeline/Alerts/YYYY-MM-DD.json] [--print-data]

Reads   the newest Pipeline/Alerts/<date>.json (or --alert), Pipeline/Tracker.csv,
        follow-up/scripts/due.py and the company folders (for interview prep files)
Writes  Pipeline/Alerts/dashboard.html: dashboard/template.html with the data embedded

Privacy: only minimal tracker fields leave this computer: company, role,
status, dates, score, link and a short derived step label. Never the Next action text,
contact names or other notes.
"""
import csv
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SKILL = Path(__file__).resolve().parents[1]
ALERTS = ROOT / "Pipeline" / "Alerts"
TRACKER = ROOT / "Pipeline" / "Tracker.csv"
DUE = ROOT / ".claude" / "skills" / "follow-up" / "scripts" / "due.py"
OUT = ALERTS / "dashboard.html"
TODAY = dt.date.today()
ABOUT = ROOT / "Profile" / "About Me.md"
HIDDEN = {"Skip", "Discarded", "Rejected"}


def key(company, title):
    """Stable id shared by alert jobs, tracker rows and dashboard requests."""
    return re.sub(r"[^a-z0-9]+", "-", f"{company} {title}".lower()).strip("-")[:90]


def day(s):
    try:
        return dt.date.fromisoformat((s or "").strip()[:10])
    except ValueError:
        return None


def step_label(r, days):
    st, na = r["Status"], r.get("Next action", "")
    dates = sorted(d for d in (day(x) for x in r.get("Follow up on", "").split(";")) if d and d >= TODAY)
    nxt = dates[0].strftime("%b %-d") if dates else ""
    if st == "Offer":
        return "Offer: decide"
    if st == "Interview":
        return f"Interview process · check in {nxt}" if nxt else "Interview process"
    if st == "Responded":
        return "They replied: next step"
    if st == "Applied":
        if nxt:
            return f"Follow up {nxt}"
        if days is not None and days >= 21:
            return "Stale: follow up or drop"
        if days is not None and days >= 7:
            return "Follow-up due"
        return "Waiting to hear"
    if st == "Evaluated":
        return "Ready to apply" if re.search(r"resume ready", na, re.I) else "Scored: decide"
    return st


def tracker_rows():
    rows = list(csv.DictReader(TRACKER.open())) if TRACKER.exists() else []
    out = []
    for r in rows:
        a = day(r.get("Applied on"))
        days = (TODAY - a).days if a else None
        nxt = sorted(d for d in (day(x) for x in r.get("Follow up on", "").split(";")) if d and d >= TODAY)
        out.append({"key": key(r["Company"], r["Role"]), "company": r["Company"], "role": r["Role"],
                    "status": r["Status"], "score": r.get("Score", ""), "applied_on": r.get("Applied on", ""),
                    "days": days, "next_date": nxt[0].isoformat() if nxt else "",
                    "step": step_label(r, days), "url": r.get("URL", ""), "updated": r.get("Updated", ""),
                    "_folder": r.get("Folder", ""), "_next": r.get("Next action", "")})
    return out


def todos(rows):
    ready = [r for r in rows if r["status"] == "Evaluated" and r["step"] == "Ready to apply"]
    stale = [r for r in rows if r["status"] == "Applied" and r["days"] is not None and r["days"] >= 21]
    interviews = []
    for r in rows:
        if r["status"] != "Interview":
            continue
        folder = ROOT / r["_folder"] if r["_folder"] else None
        prep = bool(folder and folder.exists() and any(p.name.startswith("Interview Prep") for p in folder.iterdir()))
        interviews.append({**r, "prep_ready": prep})
    due = []
    try:
        d = json.loads(subprocess.run([sys.executable, str(DUE), "--json"], capture_output=True,
                                      text=True, check=True).stdout)
        for x in d.get("due", []):
            why = re.sub(r"\s*\(.*?\)", "", x.get("why", ""))
            due.append({"key": key(x["company"], x["roles"][0] if x["roles"] else ""), "company": x["company"],
                        "roles": x["roles"], "kind": x["kind"], "why": why,
                        "sent_so_far": x.get("sent_so_far", 0), "live": x.get("live_process_at_company", False)})
    except Exception as e:  # show the page anyway; the section says it couldn't load
        due = [{"error": f"Couldn't read follow-ups: {type(e).__name__}"}]
    return {"ready": ready, "followups": due, "stale": stale, "interviews": interviews}


def page_title():
    """'<First name>'s Job Dashboard' from About Me, or a plain title."""
    try:
        m = re.search(r"^- Name:\s*(.+)$", ABOUT.read_text(), re.M)
        first = m.group(1).strip().split()[0] if m else ""
    except OSError:
        first = ""
    if not first or first.startswith("["):
        return "Job Dashboard"
    return f"{first}'s Job Dashboard"


def public(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


def main():
    alert_path = Path(sys.argv[sys.argv.index("--alert") + 1]) if "--alert" in sys.argv else \
        max(ALERTS.glob("20??-??-??.json"), default=None)
    alert = json.loads(alert_path.read_text()) if alert_path else {}
    for j in ([alert.get("top")] if alert.get("top") else []) + alert.get("scored", []) + alert.get("worth_look", []) \
            + alert.get("new_companies", {}).get("must_have", []) + alert.get("new_companies", {}).get("recent", []):
        j["key"] = key(j["company"], j["title"])
    rows = tracker_rows()
    t = todos(rows)
    status_by_key = {r["key"]: r["status"] for r in rows}
    data = {"generated": dt.datetime.now().isoformat(timespec="minutes"), "alert": alert,
            "tracker_status": status_by_key,
            "todos": {k: [public(x) if isinstance(x, dict) else x for x in v] for k, v in t.items()},
            "tracker": [public(r) for r in rows]}
    if "--print-data" in sys.argv:
        print(json.dumps(data, indent=1))
        return
    blob = json.dumps(data).replace("</", "<\\/")
    html = (SKILL / "template.html").read_text().replace("/*__DATA__*/null", blob)
    html = html.replace("/*__TITLE__*/", page_title().replace("<", ""), 1)
    OUT.write_text(html)
    print(json.dumps({"written": str(OUT), "alert": str(alert_path), "tracker_rows": len(rows),
                      "todos": {k: len(v) for k, v in t.items()}, "bytes": len(html)}))


if __name__ == "__main__":
    main()
