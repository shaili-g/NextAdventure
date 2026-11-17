"""Read Word files as text, and build the master resume Word file from Markdown.

Usage:
  python3 master.py text "<file.docx>"                 print a Word file's text (headings marked with #)
  python3 master.py build "<Master Resume.md>" "<Master Resume.docx>"
                                                      render the Markdown master as a Word file;
                                                      an existing .docx is kept as "<name> (previous).docx"
  python3 master.py check "<Master Resume.md>"         count roles, bullets, bullets with a number, and list
                                                      roles with no numbers (gaps to ask about)

The Markdown master uses: "# Name", a contact line, "## Section", "### Role line", "#### Project",
"- bullet" and plain paragraphs. **bold** and *italic* are kept. PDFs: read them with Claude's own
file reader; this script handles Word files only.
"""
import json
import re
import shutil
import sys
from pathlib import Path


def need_docx():
    try:
        import docx  # noqa: F401
        return docx
    except ImportError:
        sys.exit("python-docx is missing. Run: python3 -m pip install --user python-docx")


def text(path):
    docx = need_docx()
    d = docx.Document(path)
    out = []
    for p in d.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        style = (p.style.name or "").lower()
        m = re.match(r"heading (\d)", style)
        if style == "title":
            out.append("# " + t)
        elif m:
            out.append("#" * (int(m.group(1)) + 1) + " " + t)
        elif "list" in style or p._p.pPr is not None and p._p.pPr.numPr is not None:
            out.append("- " + t)
        else:
            out.append(t)
    for table in d.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells]
            if any(cells):
                out.append(" | ".join(dict.fromkeys(cells)))
    print("\n".join(out))


def runs(par, line):
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", line):
        if part.startswith("**") and part.endswith("**"):
            par.add_run(part[2:-2]).bold = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            par.add_run(part[1:-1]).italic = True
        elif part:
            par.add_run(part)


def build(src, dst):
    docx = need_docx()
    from docx.shared import Pt, Inches
    dst = Path(dst)
    if dst.exists():
        shutil.copy2(dst, dst.with_name(dst.stem + " (previous)" + dst.suffix))
    d = docx.Document()
    for s in d.sections:
        s.left_margin = s.right_margin = Inches(0.8)
        s.top_margin = s.bottom_margin = Inches(0.7)
    d.styles["Normal"].font.name = "Calibri"
    d.styles["Normal"].font.size = Pt(10.5)
    for line in Path(src).read_text().splitlines():
        raw = line.rstrip()
        if not raw.strip():
            continue
        m = re.match(r"(#{1,4})\s+(.*)", raw)
        if m:
            level = len(m.group(1))
            h = d.add_heading(level=0 if level == 1 else level - 1)
            runs(h, m.group(2))
        elif re.match(r"\s*[-*]\s+", raw):
            runs(d.add_paragraph(style="List Bullet"), re.sub(r"^\s*[-*]\s+", "", raw))
        else:
            runs(d.add_paragraph(), raw)
    d.save(dst)
    print(json.dumps({"built": str(dst)}))


NUM = re.compile(r"\d|\bone\b|\btwo\b|\bthree\b|\bfour\b|\bfive\b|\bdoubled\b|\btripled\b|\bhalved\b", re.I)


def check(src):
    roles, cur = [], None
    section = ""
    for line in Path(src).read_text().splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            cur = None
        elif line.startswith("### "):
            cur = {"role": line[4:].strip(), "section": section, "bullets": 0, "with_numbers": 0}
            roles.append(cur)
        elif re.match(r"\s*[-*]\s+", line) and cur:
            cur["bullets"] += 1
            cur["with_numbers"] += bool(NUM.search(line))
    exp = [r for r in roles if "experience" in r["section"].lower() or "work" in r["section"].lower()] or roles
    print(json.dumps({
        "roles": len(exp),
        "bullets": sum(r["bullets"] for r in exp),
        "bullets_with_numbers": sum(r["with_numbers"] for r in exp),
        "roles_with_no_numbers": [r["role"] for r in exp if r["bullets"] and not r["with_numbers"]],
        "roles_with_under_3_bullets": [r["role"] for r in exp if r["bullets"] < 3],
        "per_role": exp}, indent=1))


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("text", "build", "check"):
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "text":
        text(sys.argv[2])
    elif cmd == "build":
        if len(sys.argv) < 4:
            sys.exit(__doc__)
        build(sys.argv[2], sys.argv[3])
    else:
        check(sys.argv[2])


if __name__ == "__main__":
    main()
