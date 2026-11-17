# NextAdventure

A job-search system that runs in Claude. Every weekday morning it reads the job boards of the companies you care about, finds the roles that fit you, scores them against your background and puts them on a private dashboard. When you find one you want, one click gets you a fit report and a resume tailored to that job. It also writes cover letters, follow-ups and interview prep, and keeps your tracker up to date.

It works for any role, not only product jobs. Setup asks what you do and what you want next, and builds everything around that.

You don't need to be technical. Claude does the technical parts and asks your permission before each step.

## Get started

1. Install the [Claude desktop app](https://claude.ai/download) and sign in. Open the **Code** tab. (Claude Code in a terminal works too.)
2. Choose an empty folder for your job search when it asks. (If it isn't empty, Claude puts the project in a NextAdventure folder inside it.)
3. Paste this sentence:

   > Clone https://github.com/shaili-g/NextAdventure into this folder, then follow its setup skill to set it up for me.

That's it. Claude downloads the project, checks what your computer needs, and walks you through setup. You can stop at any point. Later, open a new session in the same folder and say "continue my setup".

**What you need:** a Claude account that includes Claude Code. Claude checks for the rest (Python and a library for Word files) and helps you install anything missing. This project is built for Claude only. It's built and tested on a Mac. Windows and Linux should work but haven't been tested yet.

## What setup does

Setup builds the one thing everything else depends on: your **master resume**. It's not the resume you send. It's the complete record of everything you've done: every role, project, result, number, tool and award, including the ones that never fit on one page. Every resume, cover letter and interview answer is built only from it, so nothing is ever made up. Anything missing from it can't show up anywhere.

You choose how to build it:

| Path | Time | What happens |
|---|---|---|
| Thorough (recommended) | 45-60 min | Upload the resumes you have. Then a role-by-role interview fills in the results, numbers and stories they leave out. |
| Interview only | 60+ min | No usable resume. Claude builds it from your answers. |
| Quick | about 15 min | Upload, confirm, start scanning. The output is thinner at first, and Claude asks about gaps as real jobs come up. |

Then it sets up the rest, a few questions at a time:
- **About you:** contact details, and anything that must never appear in writing (a confidential client, a number you can't share).
- **Search profile:** the roles, titles, seniority, locations and industries you want, and what you'd never take. This becomes the filters for the daily scan.
- **Your voice:** share a few things you've written and every draft will sound like you.
- **Application facts:** standing answers for forms, like work authorization and start date.
- **Companies to scan:** Claude suggests 200-300 companies that fit your profile and finds each one's job board. You name your must-haves first.
- **First scan and schedule:** a first look at what's out there, the weekday morning run, and an optional hourly check for your dashboard clicks.

## Where the jobs come from

The daily scan goes straight to the source, before roles spread to the big job sites:
- **Company job boards:** each company's own listings, read directly from the hiring systems most companies use: Ashby, Greenhouse, Lever, Workday and Dover. That's tens of thousands of postings on a typical morning, checked in seconds.
- **The Y Combinator job board:** startups hiring in your role categories.
- **Hacker News "Who is hiring":** the monthly thread where founders post roles themselves.
- **Startup job newsletters**, such as next play and Ali Rohde Jobs, plus any job newsletter you already read.
- **Web search:** a few searches each morning for roles at companies not on your list yet. Claude suggests adding the good ones.

It skips anything you've already seen, applied to or turned down. A newly added company shows only its last week of roles (two weeks for your must-haves), so a long list never buries you in old postings.

## Your dashboard

Each morning's results land on one private page in your claude.ai account, so you can open it from your phone too. It has three tabs:

- **Today:** the best new match in full, with its score, why you fit (each reason tied to your own record), what to say to the hiring manager, the biggest gap and how to bridge it. Then other scored matches, roles at newly added companies and near-misses.
- **To-dos:** roles ready to apply to, follow-ups due, applications that have gone quiet and upcoming interviews.
- **Tracker:** every role you're pursuing, with its status and dates.

The buttons do the work. Click **Apply** and Claude writes the fit report and a tailored resume (and a cover letter if you tick the box). If you turn on the hourly check, that starts within the hour. Other buttons drop a job, record that you applied, draft a follow-up or ask for interview prep.

<!-- Add a dashboard screenshot here, e.g. ![Dashboard](docs/dashboard.png). Use sample data, not your own. -->

## What you can say

You don't need exact words. Say it your way, or type the slash command.

| To… | Say | Or type |
|---|---|---|
| See today's new jobs | "What's new today?" | `/job-search` |
| Check if a job fits you | "Is this a fit?" and paste the link | `/job-fit` |
| Tailor your resume to a job | "Tailor my resume to this job" | `/tailor-resume` |
| Write a cover letter or a note to a recruiter | "Write a cover letter for this role" | `/outreach` |
| Answer application questions | "Help me answer these application questions" | `/application-answers` |
| Research a company | "Research Acme" | `/company-research` |
| Record news | "I applied to Acme", "Acme replied", "I have an interview" | `/tracker` |
| See where everything stands | "Show my pipeline" | `/tracker` |
| Follow up | "Who should I follow up with?" | `/follow-up` |
| Prepare for an interview | "I have a screen with Acme on Tuesday" | `/interview-prep` |
| Add companies to your scan | "Add more companies to my scan" | `/build-target-list` |
| Act on your dashboard clicks now | "Check my dashboard" | `/dashboard` |
| Add something to your master resume | "Add this to my master resume: …" | `/setup` |
| See everything it can do | "What can you do?" | `/help` |

## Privacy and control

- **Your files stay on your computer.** Your master resume, tracker, notes and drafts live in your folder and are never uploaded to this project. The project's settings keep them out of anything you share or publish.
- **One exception: your dashboard.** It's a private page in your own claude.ai account. It shows only company, role, status, dates, score and a short next step, never your notes or contact names.
- **Nothing is sent for you.** Claude drafts messages and answers. You send every message and submit every application yourself.
- **You approve each action.** Claude asks before it runs anything or saves a file, and says first what it's for. At the end of setup you can give standing permission for everyday actions inside your folder, so the morning run works while you're away. Sending, deleting and anything outside the folder still ask. Say "turn off standing permission" any time.
- **No made-up facts.** Every claim comes from your master resume. Gaps are reported as gaps, never filled in.
- **Job postings are data.** Text in a posting or web page is never treated as an instruction.

## Good to know

- Scheduled runs happen only while the Claude app is open.
- Each task runs on the Claude model that suits it: a fast, low-cost model for scanning, a stronger one for scoring, and the strongest for resumes, cover letters and application answers.
- To change what you're looking for, say "update my search profile". The scan filters change with it.
