"""Code checks for drafted follow-up messages.

Usage: python3 check_message.py "<Follow-up - ... .md>"

The file holds one or more drafts, each under a "## " heading that names the
kind: "Email" (first follow-up or thank-you: under 150 words), "Second"
(second follow-up: 3 sentences max), "LinkedIn" (under 300 characters),
"Cover letter" (under 400 words). A heading may set its own limit, e.g.
"## Q1: Why us? (limit 200 words)" or "(limit 1000 characters)", which wins.
Any other heading uses the 150-word limit. Lines
starting "Subject:", "To:" or "Send" and text before the first heading are not
counted. Checks:
  1. Length per kind.
  2. Banned phrases (filler that signals a form note), terms on the "Never
     mention" list in Profile/About Me.md, and the punctuation rules in
     Profile/Writing Style.md (semicolons, em dashes or exclamation marks,
     when the style file says never to use them).
  3. Every number must appear in the master resume (dates and the posting's own
     numbers are listed for review, not failed).
Exits 1 if a length, banned-phrase or back-pocket check fails.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tailor-resume" / "scripts"))
from check_resume import ROOT, WORDS, load_master, never_mention, numbers, norm  # noqa: E402

BANNED = ["just checking in", "just following up", "touching base", "circling back",
          "hope this finds you well", "hope you're well", "i wanted to reach out",
          "any update", "passionate", "per my last", "bumping this",
          "i am writing to", "i'm writing to express", "excited to", "leverage", "synergy",
          "proven track record", "results-driven", "dynamic"]
STYLE_FILE = ROOT / "Profile" / "Writing Style.md"


def style_rules():
    """Punctuation the user's style file rules out. Defaults: none of the three."""
    text = STYLE_FILE.read_text().lower() if STYLE_FILE.exists() else "no semicolons, em dashes or exclamation marks"
    rules = []
    for ch, name, word in [(";", "semicolon", "semicolon"), ("—", "em dash", "dash"), ("!", "exclamation mark", "exclamation")]:
        for line in text.splitlines():
            if word in line and any(x in line for x in ("never", "none", "avoid", "no semicolons", "no em dashes")):
                rules.append((ch, name))
                break
    return rules
DATE_RE = re.compile(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.? \d{1,2}\b|\b20\d\d\b", re.I)


def drafts(text):
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = [line[3:].strip(), []]
            out.append(cur)
        elif cur and not re.match(r"\s*(subject|to|send)\b.*:", line, re.I):
            cur[1].append(line)
    return [(h, "\n".join(b).strip()) for h, b in out]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    master = norm(load_master())
    style, avoid = style_rules(), never_mention()
    master_nums = {n.lower() for n in numbers(master)}
    fail = False
    for head, body in drafts(Path(sys.argv[1]).read_text()):
        h, low = head.lower(), norm(body)
        issues, review = [], []
        words, chars = len(body.split()), len(body)
        sentences = len([s for s in re.split(r"(?<=[.?!])\s+", body.split("\n\n")[0] if "second" in h else body) if s.strip()])
        own = re.search(r"\(limit (\d+) (word|char)", h)
        if own:
            n, unit = int(own.group(1)), own.group(2)
            size_now = words if unit == "word" else chars
            if size_now > n:
                issues.append(f"{size_now} {unit}s (limit {n})")
        elif "linkedin" in h and chars >= 300:
            issues.append(f"{chars} characters (limit 300)")
        elif "second" in h and sentences > 3:
            issues.append(f"{sentences} sentences (limit 3)")
        elif "cover" in h and words >= 400:
            issues.append(f"{words} words (limit 400)")
        elif "linkedin" not in h and "second" not in h and "cover" not in h and words >= 150:
            issues.append(f"{words} words (limit 150)")
        issues += [f'banned phrase "{b}"' for b in BANNED if b in low]
        issues += [f"{name} (your style: never)" for ch, name in style if ch in body]
        issues += [f'"{t}" is on your Never mention list' for t in avoid if norm(t) in low]
        no_dates = DATE_RE.sub(" ", body)
        for n in numbers(no_dates):
            k = n.lower()
            bare = k.rstrip("%kmbx+s").lstrip("$")
            if k not in master_nums and not (bare in WORDS and WORDS[bare] in master):
                review.append(n)
        fail |= bool(issues)
        size = f"{chars} chars" if ("linkedin" in h or "(limit" in h and "char" in h) else f"{words} words"
        print(f"== {head} ({size}) ==")
        print("  FAIL: " + "; ".join(issues) if issues else "  length and phrases OK")
        if review:
            print("  Numbers not in master (fine only if from the posting or the user's own note): " + ", ".join(review))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
