---
name: application-answers
description: Draft the user's answers to job application form questions (why this company, why this role, describe something you shipped, a hard trade-off, a failure, leadership, salary expectations, work authorization, start date and other short fields). Uses the master resume, story bank, fit report and standing facts, in the user's voice, within each question's limit, checked by code. Never submits anything. Use when the user pastes application questions or says "help me fill out this application".
model: opus
---

# Application answers

The shared rules in `CLAUDE.md` apply: facts come only from the master resume, never invent a number, title, tool or date, back-pocket items and "Never mention" terms never go in writing. Write in the user's voice (`Profile/Writing Style.md`). The user reviews and submits every answer; never fill in or submit a form.

## 0. Deferred setup steps
- If `Profile/Application Facts.md` is missing or `Profile/Setup Progress.md` marks application facts "deferred", run that step of the `setup` skill first (a few questions), then carry on.
- If `Profile/Writing Style.md` still holds only defaults, offer the writing-style step of `setup` once. If the user declines, use the defaults.

## 1. Inputs
- The questions, pasted by the user, with any character or word limits (ask if a limit isn't shown; forms often enforce one silently). If they give only a link, read the posting and ask them to paste the questions: most forms aren't readable without signing in.
- The company folder `Companies/<Company>/`: `Fit - <Role>.md`, the posting, `Company Brief.md`, the tailored resume, any cover letter (answers must agree with it).
- `Profile/Story Bank.md` if it exists (question-to-story table), otherwise the "Story:" lines in the master. `.claude/skills/interview-prep/answer-playbook.md` for answer structures.
- `Profile/Application Facts.md` for factual fields.
- Earlier answers for the same company in the folder (`Application Answers - *.md`), so the user doesn't contradict themselves.

## 2. Sort the questions
| Kind | Examples | How |
|---|---|---|
| **Fact fields** | Work authorization, sponsorship, start date, relocation, in-office days, how did you hear, demographics | Copy from `Application Facts.md`. If a field there is blank or "[ask me]", leave it as `[You to answer]` and list it at the top. Never guess authorization, sponsorship or demographics. |
| **Salary** | Expected salary, desired range | The default in `Application Facts.md` (the posting's range when shown). Flag it so the user confirms per role. |
| **Motivation** | Why us, why this role, why now | The fit report's "Why the role exists" and the brief's gap give the "why this role". "Why us" needs the user's real reason: use what they've said (tracker, cover letter, conversation); if there's nothing, write the rest and leave `[your reason for <Company>]` rather than inventing enthusiasm. |
| **Experience stories** | Something you shipped, a hard trade-off, a failure, leading without authority, a metric you moved | The story closest to the posting's top requirement. Shape: situation in one sentence, what the user decided and why, the result with the master's number, one line on what they learned. Name what they gave up in trade-off answers. |
| **Skills and opinion** | How do you approach X | The user's own positions (from the playbook, story bank or conversation), anchored with one master result. Label opinions as theirs. |
| **Short answers** | One-liners, yes/no with explanation | Answer first, one clause of support. |

## 3. Write
- Use the question's limit; when none is given, aim for 100-200 words for open questions. Answer the question asked in the first sentence.
- Don't paste resume bullets. Tell the story in sentences: cause, what changed, result.
- Don't reuse the same story for two questions on one form unless the form is short; spread across the strongest 2-3 stories.
- Use the posting's language where it's true for the user.
- Keep each project's results separate.

## 4. Save and check
Save `<company folder>/Application Answers - <Role>.md`:
```
# Application answers: <Company>, <Role> (<date>)
Needs you: <fact fields left blank, salary to confirm, any [your reason] gaps>
Sources:
- "<claim>" → master: "<master line>" (or Story Bank #n)

## Q1: <question as written> (limit <N> words|characters)
<answer>
```
Put each question's limit in its heading so the checker applies it. Then run:
`python3 .claude/skills/follow-up/scripts/check_message.py "<file>"`
Fix every FAIL (length, banned phrases, style, "Never mention" terms). Remove any listed number that isn't from the master, the posting or the user's own words.

## 5. Hand over
Show the answers grouped as: needs you (blanks and salary), then the rest. Remind the user to paste them into the form and submit it themselves. Tracker: `tracker.py set <row> --next "Application answers drafted"`. When they say they submitted, use the `tracker` skill to set Applied with that date.
