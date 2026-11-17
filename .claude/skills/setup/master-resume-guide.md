# Master resume guide

Read by the setup skill for step 2. Everything the system writes about the user (resumes, cover letters, application answers, interview answers) comes only from the master resume. A thin master means thin output, so this step is where quality is won.

## What to tell the user (say it in your own words, briefly)
A master resume is one long document with everything you've done: every role and title with its dates, every project worth talking about, the numbers behind your results, the tools you used, awards, education, side work. It isn't a resume you'd send, so length doesn't matter and nothing is too small. When you apply for a job, the system picks the best pieces from it for that job. If something isn't in the master, the system will never mention it, so it's worth getting it all down once.

## Merging uploaded resumes
1. Read every file. PDFs: read them directly. Word: `python3 .claude/skills/setup/scripts/master.py text "<file>"`. LinkedIn: ask them to save their profile as a PDF (More > Save to PDF) and drop it in.
2. Build one list of roles, newest first. The same work described in several files becomes one entry with the most specific version of each fact.
3. List conflicts: the same role, project or result with different titles, dates, numbers or claim strength ("led" vs "co-led", "40%" vs "35%"). Ask about them five at a time, each as a short choice: "Your 2022 resume says the redesign raised conversion 40%; the 2024 one says 35%. Which is right, or neither?" Record each ruling in `Master Resume/Fact Log.md` with the date and why.
4. Never resolve a conflict by guessing or by picking the bigger number. If they don't know, use the smaller claim or leave the number out, and log that.

## Interview: one role at a time
Start with the most recent role. Ask two or three questions per message, never a long list. Write what they say into the master as you go (show them the new bullets every few answers).

**Context (once per role)**
- What does the company do, and how big was it (people, revenue, stage)?
- What was your team, how many people, who did you report to, and how many reported to you?
- Why were you hired, or what was broken when you arrived?

**Results (for each piece of work)**
- What did you own, decide or build yourself, and what did others do? (This sets the verb: led, co-led, built, advised, supported.)
- What changed because of it? Before and after.
- How do you know? Where would that number come from?

**When there's no number, climb this ladder** (stop at the first rung they can answer honestly):
1. An exact measure: %, $, time, count.
2. A before/after comparison: "from weekly to daily", "from 3 tools to 1".
3. Scale: users, customers, revenue covered, teams, countries, budget.
4. A rank or first: "first in the company to…", "largest account".
5. Recognition: promoted, adopted by other teams, asked to repeat it.
Never suggest a number. If none is true, say "We'll show this one by scope" and move on.

**Depth that later skills need**
- Tools, methods and technologies, by name.
- One story per role for interviews: a hard decision, a disagreement, a mistake. Note it in the role as "Story: …" (one line); the interview-prep skill expands it later.
- Anything true they don't want in writing goes under "Back pocket".

**Don't forget to ask about:** promotions and title changes (each title separately with its dates), short stints and contract work, gaps (one neutral line if they want it), side projects, volunteering, teaching, writing and talks, patents, certifications, languages.

## Rules while writing the master
- Their words, made concise. Don't upgrade claims: co-led stays co-led, a team's size describes the team, not their span of control.
- Every number must come from them or their files. Mark nothing as a fact that you inferred.
- Keep dates as month and year. Keep titles exactly as they held them, unless a Fact Log ruling says otherwise.
- Write one result per bullet. Start with what changed, then how.

## When the master is good enough
Run `python3 .claude/skills/setup/scripts/master.py check "Master Resume/Master Resume.md"`. Aim for: every role from the last 10 years has 3+ bullets, and at least half the bullets carry a number or a clear scale. Show them the gaps it lists (roles with no numbers, roles with under 3 bullets) and offer to fill them now or later. Quick-path users stop here even with gaps; note the gaps in `Profile/Setup Progress.md` under Open questions.
