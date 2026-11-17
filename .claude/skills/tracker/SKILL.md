---
name: tracker
description: Update and show the job tracker (Pipeline/Tracker.csv). Records that the user applied, heard back, got an interview, an offer or a rejection, or dropped a role, and shows the pipeline (counts by status, active roles, what's stale, follow-ups due). Use when the user says "I applied to…", "Acme replied", "I got rejected", "I have an offer", "not interested in…", "show my pipeline", "where do things stand", or "update my tracker".
model: haiku
---

# Tracker

`Pipeline/Tracker.csv` has one row per job. Change it only through `python3 .claude/skills/tracker/scripts/tracker.py`, which enforces the rules in `CLAUDE.md`: only Status, Applied on, Follow up on, Next action and Updated change; rows are appended, never reordered or deleted; Status is one of Evaluated, Applied, Responded, Interview, Offer, Rejected, Discarded, Skip.

## Find the row
Run `tracker.py find "<company>"`. One match: use it. Several (e.g., two roles at one company): ask which, listing the roles. None: for "I applied", add a row (below); for anything else, say so and ask.

## Update it
| The user says | Run | Next action |
|---|---|---|
| "I applied to X" | `set <row> --status Applied` (add `--applied YYYY-MM-DD` if not today) | "Applied <date>. First follow-up due <date + 7 days>." |
| Applied to a job not in the tracker | `add --company "<c>" --role "<r>" --url "<link>"` | Same, plus "Not scored: say 'is this a fit' to score it." |
| "X replied / wants to talk" | `set <row> --status Responded` | What they asked for and by when |
| "I have an interview with X" | `set <row> --status Interview` | The date and round. Offer interview prep. |
| "I got an offer" | `set <row> --status Offer` | Deadline and amount if they share them |
| "X rejected me" | `set <row> --status Rejected` | "Rejected <date>" plus any reason given |
| "Not interested in X" / "drop X" | `set <row> --status Discarded` | Their reason, if they give one |

Pass the Next action with `--next "..."`. Use `--follow "YYYY-MM-DD"` only when they name a date to follow up (e.g., "they said to check back in January"). For a plain application leave it empty: the follow-up skill flags first follow-ups 7 days after the applied date on its own.

Run with `--dry-run` first when the match was uncertain, show them the change, then run it for real. Confirm in one line: "Acme, Senior PM: Applied (Mar 3). First follow-up due Mar 10."

## Show the pipeline
Run `tracker.py show` and `python3 .claude/skills/follow-up/scripts/due.py`. Reply with:
1. One line of counts (e.g., "8 applied, 1 responded, 1 interview; 1 applied this week").
2. Active roles, most advanced first: company, role, status, days since applying, next action.
3. Stale: applied 21+ days ago with no response. Suggest one follow-up or marking it Discarded; the user decides.
4. Follow-ups due, from due.py, with "Say 'draft follow-ups' to get drafts."

Keep it to what the user can act on. Don't list Skip, Discarded or Rejected rows unless they ask.

After a change, the dashboard's Tracker tab updates on the next daily run. If they want it now, run the `dashboard` skill's step 3.
