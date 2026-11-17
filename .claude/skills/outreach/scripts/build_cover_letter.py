#!/usr/bin/env python3
"""Render the "## Cover letter" section of a draft .md into a Word file whose
header matches the tailored resumes (name, headline, contact line, blue rule).
The name and contact line come from Profile/About Me.md.

Usage: python3 build_cover_letter.py "<Cover Letter - Role.md>" "<output>.docx" ["HEADLINE"]

In the .md section: the first line is the greeting ("Dear Wil,"), paragraphs are
separated by blank lines, and the last paragraph is the sign-off ("Best,\\nJane
Doe"). Lines starting "Subject:" are ignored. **bold** works.
"""
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tailor-resume" / "scripts"))
from build_resume import BODY, FONT, add_link, bottom_rule, rich, set_font, spacing  # noqa: E402
from docx import Document  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.shared import Inches, Pt  # noqa: E402

ABOUT = Path(__file__).resolve().parents[4] / "Profile" / "About Me.md"


def about():
    """Name and contact items from About Me ("- Name: ...", "- Email: ...", etc.)."""
    if not ABOUT.exists():
        sys.exit("Profile/About Me.md is missing. Run setup first.")
    f = {}
    for line in ABOUT.read_text().splitlines():
        m = re.match(r"\s*-\s*([A-Za-z ()/,]+):\s*(.+)", line)
        if m and not m.group(2).strip().startswith("["):
            f[m.group(1).strip().lower()] = m.group(2).strip()
    name = f.get("name", "")
    if not name:
        sys.exit("No name in Profile/About Me.md. Run setup first.")
    contact = [(f[k], None) for k in ("location", "email", "phone") if f.get(k)]
    if f.get("linkedin"):
        url = f["linkedin"] if f["linkedin"].startswith("http") else "https://" + f["linkedin"]
        contact.append(("LinkedIn", url))
    for link in [x.strip() for x in f.get("other links (portfolio, github, substack)", "").split(",") if x.strip()]:
        contact.append((link, link if link.startswith("http") else "https://" + link))
    return name, contact


def section(md):
    m = re.search(r"^## Cover letter[^\n]*\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    if not m:
        sys.exit("No '## Cover letter' section found")
    lines = [l for l in m.group(1).splitlines() if not re.match(r"\s*subject:", l, re.I)]
    return [p.strip() for p in re.split(r"\n\s*\n", "\n".join(lines)) if p.strip()]


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    paras = section(Path(sys.argv[1]).read_text())
    headline = sys.argv[3] if len(sys.argv) > 3 else ""
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Inches(8.5), Inches(11)
    s.left_margin = s.right_margin = Inches(0.9)
    s.top_margin = s.bottom_margin = Inches(0.7)
    d.styles["Normal"].font.name = FONT
    d.styles["Normal"].font.size = Pt(BODY)

    name, contact = about()
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; spacing(p, 0, 0)
    set_font(p.add_run(name.upper()), 14)
    if headline:
        p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; spacing(p, 0, 0)
        set_font(p.add_run(headline), BODY, bold=True)
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; spacing(p, 0, 10)
    for i, (text, url) in enumerate(contact):
        if i:
            set_font(p.add_run(" | "), 10)
        add_link(p, text, url, 10) if url else set_font(p.add_run(text), 10)
    bottom_rule(p)

    p = d.add_paragraph(); spacing(p, 6, 12)
    set_font(p.add_run(dt.date.today().strftime("%B %-d, %Y")), BODY)
    for i, para in enumerate(paras):
        p = d.add_paragraph(); spacing(p, 0, 10, 1.1)
        for j, line in enumerate(para.splitlines()):
            if j:
                p.add_run().add_break()
            rich(p, line.strip())
    d.save(sys.argv[2])
    print(f"Saved {sys.argv[2]} ({len(paras)} paragraphs)")


if __name__ == "__main__":
    main()
