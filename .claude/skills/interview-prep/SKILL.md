---
name: interview-prep
description: Prepare the user for a specific interview (recruiter screen, hiring manager, panel, case or executive round) or run a mock interview. Builds a one-page prep doc from the company brief, fit report, posting and the story bank, with a tailored tell-me-about-yourself, stories mapped to the round, ready answers, questions to ask, and what to avoid. Also builds and maintains the story bank. Use when the user says they have an interview, a screen, a call with someone at a company, or asks for a mock interview or story practice.
---

# Interview prep

The shared rules in `CLAUDE.md` apply. Every claim about the user comes from the master resume or `Profile/Story Bank.md`; never invent a result, title, number or story detail. Facts about the company and people come from the company brief, with sources; anything unverified is labeled. Facts about interviewers are public professional information only.

## Inputs
Ask in one message for whatever is missing (keep it to 2-3 questions, with a sensible default for each):
- Company and role (match a tracker row).
- The round: recruiter screen, hiring manager, panel, technical or case, executive, or "unknown" (default: recruiter screen if it's the first contact).
- Interviewer names and titles, if known; date, time and length.
- Anything already said by the company (emails, prior calls, notes in the company folder).

## Read first
- `Companies/<Company>/`: the posting (`JD - <Role>.md` or a PDF), `Fit - <Role>.md`, `Company Brief.md`, earlier prep and notes.
- `Profile/Story Bank.md` (its "which story for which question" table), `Profile/Search Profile.md`, the tracker row.
- `.claude/skills/interview-prep/answer-playbook.md`: answer structures, landmines and recurring questions. Reuse them; adapt to the company.
- If there's no company brief, run the `company-research` skill first (quick depth for a recruiter screen, deep otherwise).
- If there's no story bank yet, build it first (see "Story bank" below), at least the stories this round needs.

## What each round is testing
- Recruiter screen (20-30 min): fit to the role's basics, motivation ("why us, why now, why leaving"), level and scope, location and logistics, compensation expectations, red flags. Keep stories to 60 seconds.
- Hiring manager: judgment on the role's core problem, depth on 2-3 stories, how the user would approach the first 90 days, working style.
- Panel or cross-functional: partnership with neighboring functions, trade-offs, conflict.
- Technical or case: the craft of the role (for product: product sense, metrics, system design, prioritization). Use frameworks lightly; lead with the customer and the metric.
- Executive: strategy, business outcomes, scope, why this person is the bet.

## Prep doc
Write `Companies/<Company>/Interview Prep - <Round> - <Interviewer or Role>.md`, in this order:
1. **Goal for the call**: what the interviewer should leave thinking, and what the user should leave knowing. One "role tension to settle" if there is one (level, scope, location, reporting line).
2. **At a glance**: the interviewer (verified background, what they likely care about) and 3-5 company signals with dates and sources, from the brief.
3. **Positioning**: one line tailored to this role, built from the story bank's core narrative and the fit report's "why you".
4. **Tell me about yourself** (timed, about 2 minutes; 60 seconds for a recruiter screen): intro and angle of mastery → transition → one anchor story (the best match for this role) → one personal line → why this role → hand back. Give word counts. Reuse earlier TMAY drafts as the base; change the story and the closing for the role.
5. **Running the call**: rough time plan and a close line ("Is there anything in my background that gives you pause? What are the next steps?").
6. **Stories to prep**: 4-6 stories from the bank mapped to what this round tests and to the posting's top requirements, each with its hook, the one number to land, what the user gave up, and its "do not exceed" line. For technical rounds include each story's probe defense. Name any needed story the bank doesn't have yet.
7. **Ready answers** (20-30 seconds each): why this company, why this role, why now and why leaving the last role (short and forward-looking; ask the user for their own words the first time), level or scope questions, location and relocation, compensation (follow `Profile/Application Facts.md`; suggest deferring until the range is known or anchoring on the posted range; the user decides), and the top 2 gaps from the fit report with their bridge lines. Where the reason is personal, leave a bracketed frame for the user to fill, not invented reasons.
8. **Questions to ask**: 5-8, each grounded in the brief or the interviewer's background so only this candidate could ask it. Mark the top 3. Recruiter screens: also ask about the process, the team, and what success looks like.
9. **Avoid, and follow up**: claims to avoid (from `CLAUDE.md`: no "Never mention" terms, no mixing projects, no upgraded claim strength; back-pocket items are fine to say in interviews but never in writing such as the thank-you note), topics to steer around, a before-the-call checklist, and an after-the-call checklist (thank-you within 24 hours that adds one idea; log notes and next steps in the tracker).

Then update the tracker with the `tracker` skill: Status `Interview` once an interview is scheduled (an invitation not yet scheduled stays `Responded`), Next action with the date and the prep doc.

## Mock interview mode
When the user asks to practice: pick the persona for the round (recruiter, hiring manager, cross-functional partner, case interviewer, executive). Ask one question at a time, cold. After each answer, reply in this format:
- **What landed**: specific.
- **What didn't**: specific (buried result, too long, vague "we", missing number, claim stronger than the master).
- **Sharper version**: the same answer rewritten in 60-90 seconds using only true facts.
- **Follow-up**: the probe a real interviewer would ask next.
Be candid; don't flatter. Probe individual contribution ("what did you do vs. the team?"). Stop after 5-6 questions or when the user says so, then give a 3-line summary of patterns to fix.

## Story bank
`Profile/Story Bank.md` holds 8-15 interview stories. Build it the first time it's needed, from the master's roles and "Story:" lines, then ask the user to fill what the master doesn't hold (what they decided, what they gave up, what they'd do differently). File layout:
- **Rules** (one line: every number comes from the master).
- **Core narrative**: 3-4 sentences on the thread that runs through the user's career.
- **Which story for which question**: a table (tell me about yourself, hard decision, disagreement, failure, influence without authority, prioritization, biggest impact, leading people, ambiguity).
- One section per story: Hook, Situation, Task, Action, Result (the master's number), Gave up, Do not exceed (the claim limit), Probe defense, Reflection, Tags, Source (master role and dates).

Upkeep: when the user tells a story detail, a reflection, or a new story in prep or practice, add it marked "(you)", update the question table, and say what you added. Never add a number that isn't in the master; if they give a new number, offer to add it to the master first ("add this to my master resume", via `setup`).

## Reply in chat
Lead with the goal for the call and the TMAY anchor choice, then link the prep doc. List any bracketed answers the user needs to fill and any missing story.
