---
name: follow-up
description: Draft the user's job-search follow-ups: notes after an application goes quiet, second follow-ups, nudges after a recruiter replies, thank-you notes after interviews, and scheduled check-ins. Lists what's due from the tracker, drafts email and LinkedIn versions with one specific value point, checks them by code, and logs them. Never sends anything. Use when the user asks "who should I follow up with", "draft a follow-up", "write a thank-you note", says they had an interview, or says they sent a follow-up.
---

# Follow-up

The shared rules in `CLAUDE.md` apply: facts come only from the master resume, never invent a number, back-pocket items and "Never mention" terms never go in writing. Nothing here sends anything; the user sends every message themselves.

## Files
- `Pipeline/Tracker.csv`: change it only with `.claude/skills/tracker/scripts/tracker.py` (Status, Applied on, Follow up on, Next action; Updated is set for you).
- `Pipeline/Follow-ups.csv`: the log. Columns: `Date,Company,Role,Type,Channel,To,Status,File`. Type is first / second / nudge / thank-you / check-in / close (outreach rows use `outreach-*` or `cover-letter` and don't count toward follow-up timing); Status is `drafted` or `sent`. Create it with that header if missing. Append only; to record a send, change that row's Status to `sent` and its Date to the send date.
- Drafts: `<Folder from the tracker>/Follow-up - <Role> - <YYYY-MM-DD>.md`.

## 1. What's due
Run `python3 .claude/skills/follow-up/scripts/due.py`. It applies the timing rules and groups by company (two roles at one company get one message):
- **scheduled**: a "Follow up on" date within 3 days (e.g., a check-in the company asked for).
- **first**: Applied 7+ days ago, nothing sent.
- **nudge**: Responded, no movement for 3+ days.
- **thank-you**: Interview stage with no follow-up date set.
- **close**: 2 follow-ups sent, no reply.
- Flagged "another role here is in process": don't send a cold note; mention the other role in the live conversation instead.

Show the user the list with a recommendation for each (draft now / skip / close). If they named a company, skip straight to it. Draft only what they pick.

## 2. Gather (per company)
Read, in this order, and stop when you have one strong, specific value point:
1. `Fit - <Role>.md` in the folder: "Why you", "Say this", the role's core problem.
2. The posting (JD .md or .pdf in the folder): what the team needs most.
3. The tailored resume in the folder (`<Name> Resume - <Role>.docx`): the lines already chosen and checked for this role.
4. For interviews and check-ins: the interview prep doc, company brief and any notes the user gives about the conversation.
5. `Pipeline/Follow-ups.csv`: what was already sent, so a second note uses a new angle.

Who to send to: use the name the user gives. If none, write `[Name]` and say who it should go to, in order of usefulness: the hiring manager (the role's likely manager), the recruiter on the posting, or a reply to the application confirmation email. Find a name only if they ask, using public professional info only.

## 3. Draft
Write in the user's voice: read `Profile/Writing Style.md` first (if it still holds only defaults, offer the writing-style step of `setup` once). No flattery or filler. First-contact messages and cover letters belong to the `outreach` skill.

**First follow-up (email):** subject line plus 3-4 sentences, under 150 words.
1. The role and when the user applied, in one clause.
2. One value point tied to the team's need, with a receipt from the master (a number or concrete scope), e.g., "Your posting centers on onboarding drop-off; at Acme I cut onboarding from 10 days to 3."
3. A soft ask with a time window: "Would you have 20 minutes in the next two weeks? If someone else owns this search, I'd be grateful for a pointer."
4. Sign-off: the user's name, then their LinkedIn URL (About Me). Include the phone number only in email.

**LinkedIn version:** under 300 characters (the connection-note limit): role, one receipt, the ask.

**Second follow-up:** 2-3 sentences, a new angle (a different proof point, a short idea for their product, or a relevant post or piece of the user's writing), the same soft ask. Not "following up on my note below".

**Nudge (Responded):** 2-3 sentences. Thank them, restate availability with concrete windows, ask about next steps.

**Thank-you (after an interview):** within 24 hours, under 150 words. Ask the user for one or two specifics from the conversation first (a problem they raised, a question they'd answer better now). Thank them, add one idea that builds on that specific, restate interest in one line. Never invent what was discussed.

**Check-in (scheduled):** reference the last conversation and its date, one update since (new work, a post, a relevant result from the master), and ask about their timing.

**Close (2 sent, no reply):** don't draft a third note. Recommend: set Status to Discarded, or try a different contact (one LinkedIn note to someone else on the team). The user decides.

Banned in every draft: "just checking in", "just following up", "touching base", "circling back", "hope this finds you well", "I wanted to reach out", "any update", "passionate". The checker also blocks "Never mention" terms.

## 4. Check
Run `python3 .claude/skills/follow-up/scripts/check_message.py "<draft file>"`. Fix every FAIL. For every number it lists as not in the master: keep it only if it comes from the posting or from the user's own note in this conversation; otherwise remove it. Re-run until clean.

Draft file layout (the checker reads the `## ` headings):
```
# Follow-up: <Company>, <Role> (<date>)
Send to: <name or [Name]> (<who and why>)
Value point from: <file and line>

## Email: first follow-up
Subject: ...
<body>

## LinkedIn: first follow-up
<body>
```

## 5. Log and update
- Append one row per drafted message to `Pipeline/Follow-ups.csv` with Status `drafted`.
- Tracker: `tracker.py set <row> --next "Follow-up drafted (<date>); send"`. Don't change Status.
- Show the user the drafts and the checker result, and remind them to send the messages themselves.

When the user says they sent one: set the log row to `sent` with the send date; in the tracker set "Follow up on" to 7 days after the send (for a scheduled check-in, remove only the date just handled and keep later ones) (for the second follow-up, 7 days again, after which due.py flags it to close), Next action "Follow-up sent <date>; next <date>", Updated today. If they say someone replied: set Status to Responded (or Interview if one is scheduled), clear "Follow up on" unless they give a date, and add the reply's next step to Next action.
