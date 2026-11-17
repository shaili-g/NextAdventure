---
name: setup
description: Set up the job-search system for a new user, step by step, and keep their profile current. Builds the master resume (from uploaded resumes, an interview, or both), writes the search profile and scan filters, about-me details, writing style and application facts, builds the list of companies to scan, runs a first scan and schedules the daily one. Resumable. Use when someone has just cloned or downloaded this project, says "set this up", "get started", "continue my setup", "redo my search profile", "update my profile", or "add this to my master resume".
---

# Setup

The user may not be technical. Do the technical work yourself (run scripts, create files, install what's missing) and keep what you say plain: no file paths, JSON or code unless they ask. Ask a few questions at a time, never a long form. After each step, say in one line what was saved and what's next.

Their files (master resume, tracker, notes, drafts) stay on their computer. The one exception is their private dashboard page in claude.ai, which shows the daily alert and minimal tracker fields (company, role, status, dates, a short next step), never notes. The `dashboard` skill explains this to them before its first publish, so don't repeat it here. Nothing is sent, posted or submitted for them, in setup or later.

## Start or resume
Run every command from the project folder (the one holding this project's `CLAUDE.md`). If the user's folder already had files and the project went into a `NextAdventure` subfolder, that subfolder is the project folder: tell them in one line, and open new sessions there. If this session started before the project was downloaded, the project's skills and `CLAUDE.md` aren't loaded yet: read `CLAUDE.md` and this file directly and carry on. Don't make the user restart. Each skill's `SKILL.md` is at `.claude/skills/<name>/SKILL.md`. When setup is done, tell them to open new sessions in this folder from now on.

Read `Profile/Setup Progress.md`. If it exists, say which steps are done and continue at the first one that isn't (or the one they asked for). If it doesn't, start at step 1. Update the file after every step: set its Status, and put a short dated note under Notes (what was saved, or what's left, e.g. "Thorough path; 3 of 5 roles done (Nov 17)"). Add any unanswered question under "Open questions" so a later session can pick it up.

## 1. Welcome, requirements and folders
First welcome them in a few lines: what the system does (finds jobs every weekday, scores them against their background, tailors resumes, writes cover letters and follow-ups, preps interviews, tracks applications), and that setup builds the one thing everything else depends on: a complete master resume.

Then explain permission requests in two plain sentences: "Claude will ask your permission before it runs anything on your computer or saves a file. Each time, I'll say what it does first, and you can say no." From then on, before every action that triggers a request during setup, say in one line what it is for (e.g., "Next I'll check your computer has what this needs and create the folders for your resume and tracker. You'll see a request to allow it.").

Then run `python3 .claude/skills/setup/scripts/init.py`. It creates the folders and empty tracker files and lists anything missing, with the command to fix it. Run fix commands yourself. If one needs their password or an installer, explain in one sentence what it is and why it's needed, and wait.

## 2. Master resume (the step that decides quality)
Read `master-resume-guide.md` (next to this file) and follow it. First explain what a master resume is, using the guide's wording. Then offer the three paths and record the choice in Setup Progress:

| Path | Time | What happens |
|---|---|---|
| Thorough (recommended) | 45-60 min | Upload any resumes you have, then a role-by-role interview fills in the results, numbers and stories they leave out. |
| Interview only | 60+ min | No usable resume. We build it from your answers. |
| Quick | about 15 min | Upload, confirm, start scanning. Output is thinner until the master is filled in; the system will ask about gaps as real jobs come up. |

Recommend Thorough, and say why in one line: every resume, letter and interview answer is only as good as the master.

Write the master as Markdown at `Master Resume/Master Resume.md`, starting from `templates/Master Resume.md`, and create `Master Resume/Fact Log.md` from `templates/Fact Log.md`. When it's done (or at a good stopping point), build the Word copy: `python3 .claude/skills/setup/scripts/master.py build "Master Resume/Master Resume.md" "Master Resume/Master Resume.docx"`. Tell them the Word copy is for reading and printing, and that changes go through you ("add this to my master resume") so the two stay in step.

## 3. About you
Copy `templates/About Me.md` to `Profile/About Me.md` and fill it from the master: name, email, phone, LinkedIn, location. Ask them to confirm and add other links. Then ask one question: "Is there anything that should never appear in what we write for employers? For example a confidential client, a project name, or a number you can't share." Record answers under "Never mention".

## 4. Search profile and scan filters
Draft `Profile/Search Profile.md` from `templates/Search Profile.md` and the master: propose 2-5 role types with posting signals and lead proof points, titles at their level, seniority, and industries their background points to. Then ask only what the master can't tell you, two or three at a time:
1. Where do you want to work: which cities, remote, hybrid?
2. Any industries or companies you'd never work for?
3. A salary floor, or no floor?
4. What makes one job better than another for you?
5. Anything you want next that your resume doesn't show yet?

Show the whole profile as one short page and let them correct it. Then write `Profile/Scan Config.json` from `templates/Scan Config.json`:
- `title_include`: the titles and title words to search, lowercase (e.g., "product manager", "head of product").
- `title_exclude`: add titles they'd skip and other functions that share words with theirs (e.g., "product marketing" for a product manager).
- `title_include_needs`: for broad title words that only count with a second word (e.g., "member of technical staff" counts only with "product").
- `yc_roles`: the YC job board categories that match their role types (from ycombinator.com/jobs/role/<category>, e.g. `product-manager`, `software-engineer`, `designer`, `sales-manager`, `marketing`, `operations`). Leave it empty if they don't want startups.
- `newsletters`: offer the startup-jobs newsletters listed in the template's note when they want startups, and add any job newsletter they already read that has an RSS feed.
- `location_home`: each city plus its common spellings and nearby cities (e.g., "new york", "nyc", "brooklyn"; "san francisco", "bay area", "palo alto").
- The template's remote and block lists assume a US search. For anyone searching elsewhere, rewrite `location_remote_ok` with their country's names and remove their country and cities from `location_block`.
Explain the filters back in plain words ("You'll see product manager to director roles in Boston, New York or remote in the US; product marketing, project manager and intern roles are dropped.").

## 5. Writing style (Thorough and Interview-only paths; Quick: defer)
Ask for 3 or more pieces of their own writing: posts, essays, long emails, a cover letter they liked. Pasted text or links both work. Save each as a text file in the session scratchpad and run `python3 .claude/skills/setup/scripts/measure_style.py <files>`. Fill `Profile/Writing Style.md` from `templates/Writing Style.md` with the measures, a few habits you notice, and rules for employer writing. With no samples, copy the template's defaults and say so. On the Quick path, copy the template with defaults and mark the step "deferred".

## 6. Application facts (Thorough and Interview-only; Quick: defer)
Copy `templates/Application Facts.md` to `Profile/Application Facts.md` and ask the rows a few at a time. Any they'd rather not answer stay "[ask me]". On the Quick path, copy the template and mark the step "deferred".

## 7. Companies to scan
Explain in one or two lines: the daily scan reads each company's own job feed, so it only sees companies on their list. Then hand over to the `build-target-list` skill, which asks for must-have companies first. Aim for 200-300 companies.

## 8. First scan and daily schedule
During setup every action asks for approval, as explained in step 1. Keep it that way until step 9.
- Run `python3 .claude/skills/job-search/scripts/scan.py --dry-run` and tell them in one line what it found (e.g., "Checked 18,000 postings at 240 companies; 35 match your filters this week.").
- Ask one yes/no question: run the search every weekday morning? If yes, create a scheduled task that runs the `job-search` skill on weekdays around 7am, using the scheduled-tasks tool if it's available. If it isn't, tell them how: in the Claude app's Code tab, ask "schedule the job search every weekday at 7am". Mention once that it only runs while the Claude app is open.
- Ask a second yes/no question: check the dashboard every hour for their clicks? Explain in one line: when they click Apply on a job, the fit report and tailored resume start within the hour instead of waiting for the next morning; when nothing is queued the check stops after one quick look. If yes, create a scheduled task that runs the `dashboard` skill every hour from 8am to 10pm (cron `0 8-22 * * *`), with the instruction to stop at once when nothing is queued. Either way, "check my dashboard" acts on clicks right away.
- Offer to run the first full search now. It writes their first daily alert and creates their dashboard page (the `dashboard` skill explains the page in two sentences before it publishes it).

## 9. Standing permission (the last step)
Setup is done, and they've now seen every kind of request the system makes. Explain plainly that from here on they can keep approving each action, or give standing permission for the everyday ones, then ask a yes/no:
- What standing permission covers: running this project's own scripts (scan job feeds, update the tracker, build and check resumes and drafts), web searches, reading pages on the main job boards (Ashby, Greenhouse, Lever, Dover, YC, Hacker News; other sites still ask, so a page can't quietly send their files anywhere), saving files only inside this folder (Profile, Master Resume, Pipeline, Companies), and updating their private dashboard page and reading its clicks.
- What it never covers: sending, posting or submitting anything to anyone (it only updates their own private dashboard page), deleting files, or changing anything outside this folder. Those still ask, every time.
- Why it matters for the daily run: a scheduled run happens while they're away and can't stop to ask. Without standing permission it pauses at each request until they answer.
- How to undo it: say "turn off standing permission", or delete `.claude/settings.local.json`.
On yes, copy `templates/settings.local.json` to `.claude/settings.local.json` (it stays on their computer and out of the repo) and confirm in plain words what's now allowed. On no, say that every action keeps asking, and if they scheduled the daily run, that it will wait for their answers; offer to run the search by hand instead ("what's new today?").

Finish with the `help` skill's cheat sheet, and set every step in Setup Progress to done or deferred.

## Later: keeping the profile current
- **"Turn off standing permission"**: delete `.claude/settings.local.json` (after confirming), and say that every action will ask again and the daily run will pause at each request.

- **"Add this to my master resume"**: follow the guide's rules (their words, no upgrades, numbers only from them). Edit `Master Resume.md`, rebuild the Word copy with `master.py build`, and log any changed fact in the Fact Log.
- **Gaps found by other skills**: when job-fit or tailor-resume finds a requirement with no evidence in the master, they ask one question. When the user answers with something true, add it here the same way.
- **"Update my search profile"**: change `Search Profile.md` and `Scan Config.json` together. After filter changes, run `python3 .claude/skills/job-search/scripts/scan.py --recheck`.
- **A deferred step comes due** (first cover letter or outreach: writing style; first application form: application facts): the skill that needs it runs that step here first, then carries on.
