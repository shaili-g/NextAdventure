#!/usr/bin/env python3
"""Render a tailored resume (JSON) into a clean, ATS-friendly .docx.

Usage:  python3 build_resume.py content.json "Output Name.docx"
Needs:  pip install python-docx

JSON shape (see example_resume.json):
{
  "name": "JANE DOE",
  "headline": "APPLIED AI PRODUCT MANAGER | ENTERPRISE",
  "contact": [{"text": "Boston, MA"}, {"text": "jane@example.com"}, {"text": "LinkedIn", "url": "https://..."}],
  "sections": [
    {"title": "Summary", "type": "text", "text": "..."},
    {"title": "Experience", "type": "experience", "entries": [
        {"line": "Acme | 2019–2025", "desc": "italic company description",
         "roles": [{"title": "Head of Product, 2023–2026", "scope": "italic scope line",
                    "note": "optional italic line, e.g. Previously ...", "bullets": ["...", "..."]}]}]},
    {"title": "Founder and Venture Experience", "type": "experience", "entries": [...]},
    {"title": "Advisory and Mentoring", "type": "lines", "gap": 4, "lines": ["**Capstone Mentor, ..., 2025–2026**: ..."]},
    {"title": "Skills", "type": "skills", "lines": [["Agents & safety", "RAG, evals, ..."]]},
    {"title": "Education", "type": "lines", "lines": ["**BA**, Economics | State University"]}
  ]
}
Text in "text", "lines" and skills items may use **bold** markup. "gap" = points after each line (default 1).
Section order (Nov 8): Summary, Experience, Founder and Venture, Advisory and Mentoring, Earlier Experience, Skills, Education.
"""
import json, re, sys
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BLUE = RGBColor(0x2F, 0x54, 0x96)
FONT = 'Calibri'
BODY = 11          # body/bullet size in pt
BULLET_GAP = 3     # space after each bullet in pt


def set_font(run, size, bold=False, italic=False, color=None):
    run.font.name = FONT
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def spacing(p, before=0, after=0, line=1.0):
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), line


def bottom_rule(p, color='2F5496'):
    pPr = p._p.get_or_add_pPr()
    b = OxmlElement('w:pBdr')
    bt = OxmlElement('w:bottom')
    for k, v in (('val', 'single'), ('sz', '6'), ('space', '1'), ('color', color)):
        bt.set(qn('w:' + k), v)
    b.append(bt)
    pPr.append(b)


def rich(p, text, size=None):
    """Add text to p; **...** spans are bold."""
    for i, part in enumerate(re.split(r'\*\*', text)):
        if part:
            set_font(p.add_run(part), size or BODY, bold=(i % 2 == 1))


def round_bullets(d):
    """Make 'List Bullet' use a solid round bullet (●) instead of the small Symbol dot."""
    numbering = d.part.numbering_part.element
    style = d.styles['List Bullet']._element
    numId = style.find('.//' + qn('w:numId'))
    if numId is None:
        return
    nid = numId.get(qn('w:val'))
    num = [n for n in numbering.findall(qn('w:num')) if n.get(qn('w:numId')) == nid][0]
    aid = num.find(qn('w:abstractNumId')).get(qn('w:val'))
    absn = [a for a in numbering.findall(qn('w:abstractNum')) if a.get(qn('w:abstractNumId')) == aid][0]
    for lvl in absn.findall(qn('w:lvl')):
        if lvl.get(qn('w:ilvl')) != '0':
            continue
        lvl.find(qn('w:lvlText')).set(qn('w:val'), '\u25CF')
        rPr = lvl.find(qn('w:rPr'))
        if rPr is None:
            rPr = OxmlElement('w:rPr'); lvl.append(rPr)
        for f in rPr.findall(qn('w:rFonts')):
            rPr.remove(f)
        f = OxmlElement('w:rFonts')
        for k in ('ascii', 'hAnsi', 'cs'):
            f.set(qn('w:' + k), 'Arial')
        rPr.append(f)
        sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '20'); rPr.append(sz)


def add_link(p, text, url, size):
    rid = p.part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    h = OxmlElement('w:hyperlink')
    h.set(qn('r:id'), rid)
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    for tag, val in (('w:rFonts', None), ('w:color', '0563C1'), ('w:u', 'single'), ('w:sz', str(int(size * 2)))):
        e = OxmlElement(tag)
        if tag == 'w:rFonts':
            e.set(qn('w:ascii'), FONT); e.set(qn('w:hAnsi'), FONT)
        elif tag == 'w:color':
            e.set(qn('w:val'), val)
        elif tag == 'w:u':
            e.set(qn('w:val'), val)
        else:
            e.set(qn('w:val'), val)
        rPr.append(e)
    r.append(rPr)
    t = OxmlElement('w:t'); t.text = text; r.append(t)
    h.append(r)
    p._p.append(h)


def build(content, out):
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Inches(8.5), Inches(11)
    s.left_margin = s.right_margin = Inches(0.6)
    s.top_margin = s.bottom_margin = Inches(0.5)
    d.styles['Normal'].font.name = FONT
    d.styles['Normal'].font.size = Pt(BODY)
    round_bullets(d)

    # Header block
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; spacing(p, 0, 0)
    set_font(p.add_run(content['name']), 14)
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; spacing(p, 0, 0)
    set_font(p.add_run(content['headline']), BODY, bold=True)
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; spacing(p, 0, 4)
    for i, c in enumerate(content['contact']):
        if i:
            set_font(p.add_run(' | '), 10)
        if c.get('url'):
            add_link(p, c['text'], c['url'], 10)
        else:
            set_font(p.add_run(c['text']), 10)

    def section_header(title):
        p = d.add_paragraph(); spacing(p, 6, 3)
        set_font(p.add_run(title.upper()), BODY, bold=True, color=BLUE)
        bottom_rule(p)
        p.paragraph_format.keep_with_next = True

    def bullet(text):
        p = d.add_paragraph(style='List Bullet'); spacing(p, 0, BULLET_GAP)
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.18)
        rich(p, text)

    for sec in content['sections']:
        section_header(sec['title'])
        t = sec.get('type', 'text')
        if t == 'text':
            p = d.add_paragraph(); spacing(p, 0, 2)
            rich(p, sec['text'])
        elif t == 'bullets':
            for b in sec['bullets']:
                bullet(b)
        elif t == 'skills':
            for label, items in sec['lines']:
                p = d.add_paragraph(); spacing(p, 0, 1)
                set_font(p.add_run(label + ': '), BODY, bold=True)
                rich(p, items)
        elif t == 'lines':
            for line in sec['lines']:
                p = d.add_paragraph(); spacing(p, 0, sec.get('gap', 1))
                rich(p, line)
        elif t == 'experience':
            for e in sec['entries']:
                p = d.add_paragraph(); spacing(p, 3, 0)
                p.paragraph_format.keep_with_next = True
                set_font(p.add_run(e['line']), BODY, bold=True)
                if e.get('desc'):
                    p = d.add_paragraph(); spacing(p, 0, 2)
                    p.paragraph_format.keep_with_next = True
                    set_font(p.add_run(e['desc']), BODY, italic=True)
                for r in e.get('roles', []):
                    if r.get('title'):
                        p = d.add_paragraph(); spacing(p, 3, 0)
                        p.paragraph_format.keep_with_next = True
                        set_font(p.add_run(r['title']), BODY, bold=True, color=BLUE)
                    for key in ('note', 'scope'):
                        if r.get(key):
                            p = d.add_paragraph(); spacing(p, 0, 2)
                            p.paragraph_format.keep_with_next = True
                            set_font(p.add_run(r[key]), BODY, italic=True)
                    for b in r.get('bullets', []):
                        bullet(b)
    d.save(out)
    print('saved', out)


if __name__ == '__main__':
    build(json.load(open(sys.argv[1], encoding='utf-8')), sys.argv[2])
