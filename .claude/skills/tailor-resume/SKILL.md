---
name: tailor-resume
description: Tailor the user's resume to a pasted job posting (or link) using their master resume and standing rules. Output is a Word (.docx) file only, checked by code against the master. Use when the user pastes a job description and asks to tailor, optimize, or customize their resume.
model: opus
---

# Tailor resume

Input: the job posting text, or a URL. If the URL can't be read, ask for the text. Never work from a job title alone.

The shared rules in `CLAUDE.md` (source of truth, claims and wording) apply throughout. This skill's scripts are in `.claude/skills/tailor-resume/scripts/`.

## Read first
1. `Master Resume/Master Resume.md`: the only source of facts. Never use its "Back pocket" section.
2. `Master Resume/Fact Log.md`: rulings, before questioning or rewording any fact.
3. `Profile/About Me.md`: name, contact details, "Never mention" list, standing wording rules.
4. `Companies/<Company>/Fit - <Role>.md`, if it exists: reuse its role type, core focus, requirement match, keywords and gaps for step 1 instead of redoing them. Confirm they still hold against the posting. If no fit report exists, suggest running `job-fit` first, but go ahead if the user wants.

## 1. Analyze the posting
- Extract the role title, company, key responsibilities (most-emphasized first) and hard requirements.
- Second-order: what problem the company is trying to solve, i.e., the most likely reason this role exists.
- Core focus: what the role mainly is (e.g., product delivery vs. transformation vs. governance). It drives bullet selection in step 4.
- ATS keywords: the exact skills, tools and phrases the posting repeats. Mark each "supported" (a master line backs it) or "gap". Save the supported ones one per line to `keywords.txt` in the session scratchpad for the step-8 script.

## 2. Headline and summary
- Headline: a functional title in bold caps (e.g., "Senior Product Manager | Payments", or the posting's own job title when it's true for the user). Role titles under Experience stay exactly as the master has them.
- Summary: 3-4 sentences, about 400 characters at most. Open with experience, name the 2-3 most relevant wins, work in keywords naturally. It must answer "why this person" in a way any strong applicant couldn't, using the step-1 analysis.

## 3. Source map
Before writing any bullet, tie the summary and every bullet to the specific master line(s) it draws on. A bullet with no source line doesn't go in. One bullet, one project, unless the master itself links them.

## 4. Pick and order bullets
- Core focus first: fill most bullets with what the role mainly is. Cover the posting's supporting themes in the summary or skills by default. A supporting theme gets its own bullet only if it's a big part of the posting, or the role still has room and the theme earns it.
- Counts are ceilings, not targets: 4-5 bullets for the most recent role, 4 for the next, 2-3 for older roles. Never more than 6 for any role. Add a bullet only if it beats the weakest one against the posting's top ask.
- Order: strongest match first, judged against the posting's top ask. Recruiters read the top third closely and scan the rest, so the headline, summary and first 3-4 bullets of the most recent role carry the strongest match and the most varied, specific verbs.
- Sections, in this order, using only what the master has: Summary, Experience, then any of Founder and Venture Experience, Advisory and Mentoring, Earlier Experience (one line per older role), then Skills and Education.

## 5. Write bullets
- Shape: result-first, "Accomplished [X] as measured by [Y] by doing [Z]". One sentence, max 2 lines. Past tense for every role, even the current one.
- Numbers: one headline result plus at most one supporting measure. No honest number: show scope or scale.
- Verbs:
  - Every bullet opens with a strong, specific action verb. Never: Took, Ran, Helped, Worked, Reached, Responsible for, Involved in, Participated.
  - Prefer plain, precise verbs (Reduced, Improved, Grew, Built, Cut, Scaled) over dramatic ones.
  - Never start two bullets with the same word anywhere in the resume, and never repeat an action verb or its variants within a role. Align verbs with the posting's own where true.
  - Builder exception: when the posting signals hands-on building (build, prototype, ship, hands-on, zero-to-one, founding), the top 2-3 bullets of the most recent role may open with a build verb (Built, Shipped, Launched, Prototyped), but each must still carry its result and measure.
  - Decision exception: a bullet whose point is a judgment call may open with that decision verb (Redirected, Prioritized, Stopped) if it still states the result.
- Keywords: use the posting's exact wording where it fits naturally and is true, at most 1-2 keyword phrases per bullet. Never add a clause, colon list or noun pile just to carry a keyword. Cover keywords across the summary, skills and bullets. If a bullet reads worse with the keyword, leave it out.

## 6. Skills and education
- 8-12 skills from the master that the posting actually asks for, in the posting's exact words.
- Degrees, schools and certifications exactly as the master has them.

## 7. Build
- Write the content as JSON shaped like `scripts/example_resume.json`, in the session scratchpad. Name and contact line come from About Me. Then run:
  `python3 .claude/skills/tailor-resume/scripts/build_resume.py <scratchpad>/content.json "Companies/<Company>/<Name> Resume - <Role>.docx"`
  If python-docx is missing: `python3 -m pip install --user python-docx`.
- Save only the Word file. No PDF and no JSON in the user's folders.
- The script sets the format: Letter, Calibri, centered name, bold caps headline, contact line with links, blue section headers with a rule, bold company lines, italic company descriptions, blue role titles, italic scope lines, 11pt bullets. 2 pages max (1 page when the user has under about 8 years of experience).

## 8. Check the saved file (don't deliver until all pass)
1. Length: export a temporary PDF to the scratchpad and count pages, then delete it. On a Mac with Pages: AppleScript `tell application "Pages"` to open the file and `export ... as PDF`. With LibreOffice: `soffice --headless --convert-to pdf --outdir <scratchpad> "<file>"`. If neither is available, estimate (about 550 words a page) and tell the user to check the page count when they open it.
2. Script: `python3 .claude/skills/tailor-resume/scripts/check_resume.py "<output>.docx" <scratchpad>/keywords.txt`. Every number it flags as not in the master must be fixed or explained. Any "Never mention" hit is a failure. Review each capitalized word it lists for names or terms the master doesn't support.
3. Cold read: read only the headline, summary and first 3-4 bullets of the most recent role against the posting and say in one line whether they read as someone applying for this exact job. If not, fix the top third first.
4. Bullet audit: a table with one row per bullet:
   - source: the master line(s) it comes from (step 3); one project per bullet
   - (a) opener: strong, unique in the resume, not repeated within the role, exceptions used correctly
   - (b) XYZ: result, measure (or scope/scale if no honest number), how; mark any part missing
   - (c) keywords: posting's exact wording where natural, max 1-2
   - (d) fidelity: matches the master's claim strength, involvement and numbers
   - (e) readability: reads naturally aloud, no keyword-only clauses or noun piles, no more than 2 numbers
   A failure in source, (d) or (e) fails the bullet even if the rest pass. Also confirm bullet counts and past tense. Rewrite failing bullets, rebuild, and re-run checks 1-4 until every row passes or a failure is explained.

**Missing evidence.** If a must-have requirement has no support in the master, ask one specific question before building, e.g., "The posting asks for experimentation at scale. Is there work of yours that fits?" A true answer can go on this resume only after the user confirms the exact wording, marked in the report as "(you, <date>)". Offer to add it to the master ("add this to my master resume", via `setup`). Never invent or stretch to fill the gap.

## 9. Report
In this order:
1. The final audit table.
2. Keyword coverage from the script: present and missing, and for each missing one whether it was added, isn't supported by the master, or was left out for readability.
3. The cold-read verdict.
4. Which wins matched best.
5. Hard requirements the user can't cover, with 1-2 ways to handle each in a cover letter or interview.
6. Anything needing the user's call: location or visa questions, master figures left out because they looked odd.

Then, if the job is in the tracker, set its Next action: `python3 .claude/skills/tracker/scripts/tracker.py set <row> --next "Resume ready; apply"` (find the row with `tracker.py find`). Leave Status for the user to change when they apply.
