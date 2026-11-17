---
name: help
description: Show what this job-search system can do and the exact words or slash commands to use. Use when the user asks "what can you do", "help", "what are the commands", "how do I…", "what next", or seems unsure how to use the system.
model: haiku
---

# Help

Show the cheat sheet below as it is. Then, if `Profile/Setup Progress.md` shows setup isn't finished, add one line: "Setup isn't finished yet. Say 'continue my setup' to pick up where you left off." If they asked about one task, answer that one first and show only its row.

## Cheat sheet

You don't need the exact words. Say it your way, or type the slash command.

**Your dashboard** (the alert link you open each morning)
| To… | Do or say | Or type |
|---|---|---|
| Ask for a fit report and tailored resume | Click **Apply** on a job (tick "+ cover letter" for one) | |
| Drop a job | Click **Not for me**, with a reason if you like | |
| Record that you applied, sent a follow-up or changed status | Use the buttons on the To-dos and Tracker tabs | |
| Act on your clicks now instead of waiting for the next check | "Check my dashboard" | `/dashboard` |
| Refresh the page after a change | "Refresh my dashboard" | `/dashboard` |

**Find jobs**
| To… | Say | Or type |
|---|---|---|
| See today's new jobs | "What's new today?" | `/job-search` |
| Check if a job fits you | "Is this a fit?" and paste the link or the posting | `/job-fit` |
| Add companies to your daily scan | "Add more companies to my scan" | `/build-target-list` |
| Research a company | "Research Acme" | `/company-research` |

**Apply**
| To… | Say | Or type |
|---|---|---|
| Tailor your resume to a job | "Tailor my resume to this job" | `/tailor-resume` |
| Write a cover letter | "Write a cover letter for this role" | `/outreach` |
| Message a recruiter, hiring manager or someone for a referral | "Write a note to the hiring manager at Acme" | `/outreach` |
| Answer application questions | "Help me answer these application questions" and paste them | `/application-answers` |

**Track and follow up**
| To… | Say | Or type |
|---|---|---|
| Record an application | "I applied to Acme" | `/tracker` |
| Record news | "Acme replied", "I have an interview with Acme", "Acme rejected me", "I got an offer" | `/tracker` |
| See where everything stands | "Show my pipeline" | `/tracker` |
| Follow up | "Who should I follow up with?" or "Write a thank-you note to Acme" | `/follow-up` |

**Interview**
| To… | Say | Or type |
|---|---|---|
| Prepare for an interview | "I have a screen with Acme on Tuesday" | `/interview-prep` |
| Practice | "Run a mock interview for Acme" | `/interview-prep` |

**Your profile**
| To… | Say | Or type |
|---|---|---|
| Finish or redo setup | "Continue my setup" or "Redo my search profile" | `/setup` |
| Add to your master resume | "Add this to my master resume: …" | `/setup` |
| See this list again | "What can you do?" | `/help` |

## Good to know
- Your files (resume, tracker, notes, drafts) stay on your computer, in this folder. The one exception is your private dashboard page in claude.ai (see below). Nothing is sent or submitted for you. You send every message and submit every application yourself.
- Facts about you come only from your master resume. If something's missing there, it won't show up anywhere, so add it.
- Claude asks before it runs anything or saves a file, and says first what it's for. If you gave standing permission at the end of setup, say "turn off standing permission" any time to go back to being asked.
- The daily scan runs on weekday mornings while the Claude app is open. Your dashboard link is in `Pipeline/alert-url.txt`.
- Dashboard clicks are saved and picked up by the hourly check if you turned it on (8am to 10pm), otherwise by the next morning run, or right away when you say "check my dashboard". Buttons only work when you open the page in claude.ai while signed in.
- The dashboard shows only company, role, status, dates and a short next step. Your notes stay on your computer.
