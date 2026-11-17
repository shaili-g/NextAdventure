---
name: outreach
description: Write the user's first-contact messages and cover letters in their voice. Messages to a recruiter, a hiring manager, a peer or possible referrer, or an interviewer before a call (email and LinkedIn versions), and cover letters as Word files. Every claim comes from the master resume; drafts are checked by code. Never sends anything. Use when the user asks to "reach out to", "message the hiring manager", "ask for a referral", "write a LinkedIn note", "write a cover letter", or when an application asks for one.
model: opus
---

# Outreach and cover letters

The shared rules in `CLAUDE.md` apply: facts come only from the master resume, never invent a number, title or tool, back-pocket items and "Never mention" terms never go in writing. Write in the user's voice: read `Profile/Writing Style.md` first, every time. If it still holds only defaults (or `Profile/Setup Progress.md` marks writing style "deferred"), offer the writing-style step of `setup` once before drafting; if they decline, use the defaults. Nothing here sends anything; the user sends every message and submits every letter themselves. For notes after an application or interview, use the `follow-up` skill instead.

## 1. Gather
- The company folder `Companies/<Company>/`: `Fit - <Role>.md` ("Why the role exists", "Why you", "Say this", gaps), the posting (JD .md or .pdf), `Company Brief.md` (the gap this role owns, the point of view), the tailored resume.
- No fit report? Run `job-fit` first for a cover letter; for a short message, the posting and the tailored resume are enough.
- `Profile/Story Bank.md` (or the master's "Story:" lines) for a story that fits the person's likely interest.
- The person: name and role from the user. If they have none and ask you to find one, use public professional information only (company site, posting, LinkedIn headline, talks, posts) and say where it came from. Never guess an email address.
- What the user wants from it, if not obvious: a conversation, a referral, a pointer to the right person.

## 2. Pick the angle
One message makes one point. Choose the single strongest match between what the person cares about and a master result, and say where it came from. Prefer, in order: the role's core problem (fit report), something the person or team has said publicly (brief), the posting's top requirement.

## 3. Draft (email + LinkedIn for messages)
Lengths: email under 150 words; LinkedIn under 300 characters (aim for 200: LinkedIn limits connection notes on free accounts more tightly). Subject lines are specific: the role or the problem, not "Quick question".

| Type | Shape | Ask |
|---|---|---|
| **Hiring manager** | The problem their team faces (from the posting or their own words) → the user's proof, with one receipt → one sentence on how they'd think about it | "Would you have 20 minutes in the next two weeks?" |
| **Recruiter** | The role, one line on fit with a receipt, logistics that matter (location, availability) | "Could we find 15 minutes this week or next?" |
| **Peer or possible referrer** | Why them specifically (their work, a shared context), what they're exploring | No job ask in the first note: ask for 15 minutes of their perspective on the team. A referral comes later, if they offer or the conversation goes well. |
| **Interviewer, before a call** | A short connection note: looking forward to the conversation on <date>, one line on what they'd like to learn | None, or "Anything you'd suggest I read beforehand?" |

Rules: open with them or the problem, not with the user ("I am a product leader..." is out). One receipt, not a list. No flattery about the company. Sign-off: the user's name (About Me), then their LinkedIn URL; phone only in email.

## 4. Cover letters
Only when the application asks for one, allows one and the role is a strong fit (score 4.0+), or the user asks. 250-350 words, four short paragraphs, under a `## Cover letter` heading:
1. **The problem**: what the role exists to fix, in plain words, and the user's one-line connection to it. Never "I am writing to apply for".
2. **Proof**: the strongest match, told as cause → what the user changed → result, with the master's number.
3. **Second proof or point of view**: another receipt for the next requirement, or how the user would approach the first problem (from the brief's "gap this role owns"). Label opinions as theirs.
4. **Why here, and close**: a real reason for this company (the Search Profile's "what makes one job better" is a guide; if the user hasn't given a reason, ask rather than invent), then a one-line ask. Sign-off "Best," on one line and the user's name on the next.
Use the posting's language where it's true for the user. Don't repeat the resume line by line: pick two stories and tell them well.

## 5. Source map and check
Every draft file starts (before the first `## ` heading) with:
```
# <Type>: <Company>, <Role or person> (<date>)
Send to: <name, role> (<where the name came from>)
Sources:
- "<claim as written>" → master: "<master line>"
```
One Sources line per factual claim about the user. Then run:
`python3 .claude/skills/follow-up/scripts/check_message.py "<draft>.md"`
It checks lengths (a `## Cover letter` heading uses the 400-word limit), banned phrases, the user's punctuation rules from Writing Style and "Never mention" terms, and lists numbers not in the master. Fix every FAIL; remove any listed number that isn't from the posting or the user's own note. Re-run until clean. Then do a cold read as the recipient: would a busy hiring manager know in 10 seconds who this is, why them, and what they're asking?

## 6. Save, build, log
- Messages: `<company folder>/Outreach - <Person or Role> - <YYYY-MM-DD>.md`.
- Cover letters: `<company folder>/Cover Letter - <Role>.md`, then build the Word file:
  `python3 .claude/skills/outreach/scripts/build_cover_letter.py "<md>" "<company folder>/<Name> Cover Letter - <Role>.docx" "<resume headline>"` (use the tailored resume's headline so the two match). Open the result and re-read it against the .md.
- Log each message in `Pipeline/Follow-ups.csv` (Type `outreach-hm`, `outreach-recruiter`, `outreach-peer`, `outreach-interviewer` or `cover-letter`; Status `drafted`). Tracker: `tracker.py set <row> --next "<step>"` for the role's row if one exists.
- When the user says they sent a message: set the log row to `sent` with the date, and `tracker.py set <row> --follow <date 7 days later>` so `follow-up` picks it up if there's no reply.
