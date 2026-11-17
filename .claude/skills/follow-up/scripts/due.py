"""List follow-ups due, from Pipeline/Tracker.csv and Pipeline/Follow-ups.csv.

Usage: python3 due.py [--date YYYY-MM-DD] [--json]

Rules (one entry per company, so two roles at one company get one message):
  scheduled  a "Follow up on" date is today or within the next 3 days
  first      Status Applied, applied 7+ days ago, nothing sent yet, no date set
  nudge      Status Responded, no update for 3+ days, no date set
  thank-you  Status Interview with no follow-up date set (send within 24h of
             the interview; then set a date)
A scheduled item after 2 sent follow-ups with no reply becomes "close": suggest
Discarded or another contact. Rows at a company that has a live process
(Responded, Interview, Offer) are flagged so the user doesn't send cold notes
alongside it. Reads only; changes nothing.
"""
import csv
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TRACKER = ROOT / "Pipeline" / "Tracker.csv"
LOG = ROOT / "Pipeline" / "Follow-ups.csv"
LIVE = {"Responded", "Interview", "Offer"}
FOLLOW_TYPES = {"first", "second", "nudge", "thank-you", "check-in"}  # outreach rows don't count


def day(s):
    try:
        return dt.date.fromisoformat(s.strip()[:10])
    except ValueError:
        return None


def main():
    today = dt.date.today()
    if "--date" in sys.argv:
        today = dt.date.fromisoformat(sys.argv[sys.argv.index("--date") + 1])
    rows = list(csv.DictReader(TRACKER.open()))
    log = list(csv.DictReader(LOG.open())) if LOG.exists() else []

    def sent(r):
        return [e for e in log if e["Status"] == "sent" and e["Type"] in FOLLOW_TYPES
                and e["Company"] == r["Company"]
                and e["Role"] == r["Role"]]

    live = {r["Company"] for r in rows if r["Status"] in LIVE}
    due = []
    for r in rows:
        st, s = r["Status"], sent(r)
        dates = [d for d in (day(x) for x in r["Follow up on"].split(";")) if d]
        nxt = next((d for d in sorted(dates) if d >= today - dt.timedelta(days=30) and
                    not any(day(e["Date"]) and day(e["Date"]) >= d - dt.timedelta(days=3) for e in s)), None)
        kind, why = None, ""
        if st in {"Evaluated", "Skip", "Discarded", "Rejected"}:
            continue
        if nxt and nxt <= today + dt.timedelta(days=3):
            kind = "close" if len(s) >= 2 and st == "Applied" else "scheduled"
            why = f"follow-up date {nxt}" + (f"; {len(s)} sent, no reply" if kind == "close" else "")
        elif not dates and st == "Applied":
            a = day(r["Applied on"])
            if a and (today - a).days >= 7 and not s:
                kind, why = "first", f"applied {a} ({(today - a).days} days ago), nothing sent"
        elif not dates and st == "Responded":
            u = day(r["Updated"])
            if u and (today - u).days >= 3:
                kind, why = "nudge", f"responded; no update since {u}"
        elif not dates and st == "Interview":
            kind, why = "thank-you", "interview stage with no follow-up date set"
        if not kind:
            continue
        due.append(dict(company=r["Company"], role=r["Role"], status=st, kind=kind, why=why,
                        sent_so_far=len(s),
                        draft_ready=any(e["Status"] == "drafted" and e["Company"] == r["Company"]
                                        and e["Role"] == r["Role"] for e in log),
                        folder=r["Folder"], next_action=r["Next action"],
                        live_process_at_company=(r["Company"] in live and st not in LIVE)))
    # one message per company and kind
    grouped = {}
    for d in due:
        g = grouped.setdefault((d["company"], d["kind"]), dict(d, roles=[]))
        g["roles"].append(d["role"])
    out = [dict({k: v for k, v in g.items() if k != "role"}) for g in grouped.values()]
    order = {"thank-you": 0, "nudge": 1, "scheduled": 2, "first": 3, "close": 4}
    out.sort(key=lambda x: (order[x["kind"]], x["company"]))
    if "--json" in sys.argv:
        print(json.dumps({"date": today.isoformat(), "due": out}, indent=1))
        return
    print(f"Follow-ups due as of {today}: {len(out)}")
    for d in out:
        flag = "  [draft ready: send it]" if d["draft_ready"] else ""
        flag += "  [another role here is in process: raise it there, don't send cold]" if d["live_process_at_company"] else ""
        print(f"- {d['kind']:<9} {d['company']}: {'; '.join(d['roles'])} ({d['why']}){flag}")


if __name__ == "__main__":
    main()
