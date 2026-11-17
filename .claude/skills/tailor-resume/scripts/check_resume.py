"""Code checks for a tailored resume against the master.

Usage:
  python3 check_resume.py "<tailored>.docx" [keywords.txt]

1. Numbers: every number in the tailored resume (%, $, K/M, X, years, counts)
   must appear in the master. Anything missing is printed for review.
2. Names: capitalized words not found anywhere in the master (possible client,
   agency or tool names, or invented terms). Printed for review. Terms on the
   "Never mention" list in Profile/About Me.md fail the check.
3. Keywords (optional): keywords.txt has one JD phrase per line; prints which
   are present in the tailored resume and which are missing.
"""
import re
import sys
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[4]
MASTER = ROOT / "Master Resume" / "Master Resume.md"
ABOUT = ROOT / "Profile" / "About Me.md"
WORDS = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
         "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten"}
NUM_RE = re.compile(r"[$]?\d+(?:[.,]\d+)*(?:%|[KkMmBbXx+](?![A-Za-z])|s\b)?")
CAP_RE = re.compile(r"\b[A-Z][A-Za-z0-9&\-]+\b")


def paragraphs(path):
    doc = Document(path)
    paras = [p.text for p in doc.paragraphs]
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                paras += [p.text for p in cell.paragraphs]
    return [p.strip() for p in paras if p.strip()]


def load_master():
    """The master resume's text, without its Back pocket section (never used in writing)."""
    text = MASTER.read_text()
    return re.split(r"^##\s+Back pocket", text, flags=re.I | re.M)[0]


def never_mention():
    """Terms under "## Never mention" in About Me (bullets), lowercased."""
    if not ABOUT.exists():
        return []
    m = re.search(r"^##\s+Never mention\s*$(.*?)(?=^##\s|\Z)", ABOUT.read_text(), re.M | re.S | re.I)
    if not m:
        return []
    terms = [re.sub(r"^\s*[-*]\s*", "", l).strip() for l in m.group(1).splitlines() if re.match(r"\s*[-*]\s+\S", l)]
    return [t.lower() for t in terms if t and not t.startswith("[")]


def norm(s):
    s = s.replace("–", "-").replace("—", "-").replace("’", "'")
    return re.sub(r"\s+", " ", s).lower()


def numbers(text):
    out = []
    for m in NUM_RE.finditer(text):
        tok = m.group().rstrip(".,").replace(" ", "")
        if tok:
            out.append(tok)
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tailored = paragraphs(sys.argv[1])
    master_text = norm(load_master())
    master_nums = {n.lower() for n in numbers(master_text)}
    fail = False

    print("== 1. Numbers not found in master ==")
    missing = []
    for para in tailored:
        for n in numbers(para):
            key = n.lower()
            bare = key.rstrip("%kmbx+s").lstrip("$")
            if key in master_nums:
                continue
            if bare in WORDS and WORDS[bare] in master_text:
                continue
            missing.append((n, para[:90]))
    for n, ctx in missing:
        print(f"  {n:<10} in: {ctx}")
    print("  none" if not missing else f"  {len(missing)} to review")
    fail |= bool(missing)

    banned = [t for t in never_mention() if norm(t) in norm(" ".join(tailored))]
    print("\n== 2a. Never-mention terms (About Me) ==")
    print("  FAIL: " + "; ".join(banned) if banned else "  none")
    fail |= bool(banned)

    print("\n== 2. Capitalized words not in master (check for names) ==")
    seen = {}
    for para in tailored:
        for i, m in enumerate(CAP_RE.finditer(para)):
            w = m.group()
            if i == 0 or w.lower() in master_text:
                continue
            seen.setdefault(w, para[:90])
    for w, ctx in seen.items():
        print(f"  {w:<20} in: {ctx}")
    print("  none" if not seen else f"  {len(seen)} to review")

    if len(sys.argv) > 2:
        print("\n== 3. JD keyword coverage ==")
        text = norm(" ".join(tailored))
        kws = [k.strip() for k in Path(sys.argv[2]).read_text().splitlines() if k.strip()]
        hit = [k for k in kws if norm(k) in text]
        miss = [k for k in kws if norm(k) not in text]
        print(f"  present ({len(hit)}/{len(kws)}): " + "; ".join(hit))
        print(f"  missing ({len(miss)}): " + "; ".join(miss))

    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
