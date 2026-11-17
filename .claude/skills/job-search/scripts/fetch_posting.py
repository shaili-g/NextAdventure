"""Print a job posting's full text from its job feed (data only).

Usage: python3 fetch_posting.py <posting URL> [board]
Supports Ashby, Greenhouse (incl. branded pages with ?gh_jid=, pass the board),
Lever and Workday URLs. Exit code 2 = unsupported or not found (use the web).
"""
import html
import json
import re
import subprocess
import sys
from urllib.parse import urlparse, parse_qs


def get(url):
    out = subprocess.run(["curl", "-sS", "-f", "-m", "25", "--proto", "=https,http",
                          "-H", "Accept: application/json", "--", url],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or "not found")
    return json.loads(out.stdout)


def text(h):
    h = html.unescape(html.unescape(h or ""))  # Greenhouse double-escapes
    h = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", h, flags=re.I)
    h = re.sub(r"<li[^>]*>", "- ", h, flags=re.I)
    h = re.sub(r"<[^>]+>", "", h)
    return re.sub(r"\n\s*\n+", "\n\n", h).strip()


def main():
    url = sys.argv[1]
    board = sys.argv[2] if len(sys.argv) > 2 else ""
    u = urlparse(url)
    parts = [p for p in u.path.split("/") if p]
    q = parse_qs(u.query)
    if "ashbyhq.com" in u.netloc:
        b, jid = parts[0], parts[1]
        d = get(f"https://api.ashbyhq.com/posting-api/job-board/{b}?includeCompensation=true")
        j = next(x for x in d["jobs"] if x["id"] == jid or x.get("jobUrl", "").endswith(jid))
        comp = (j.get("compensation") or {}).get("compensationTierSummary") or "Not listed"
        head = [j["title"], j.get("location", ""), f"Posted: {j.get('publishedAt','')[:10]}", f"Salary: {comp}"]
        body = j.get("descriptionPlain") or text(j.get("descriptionHtml"))
    elif "greenhouse.io" in u.netloc or "gh_jid" in q:
        jid = q.get("gh_jid", [None])[0] or parts[-1]
        b = board or parts[0]
        j = get(f"https://boards-api.greenhouse.io/v1/boards/{b}/jobs/{jid}")
        head = [j["title"], (j.get("location") or {}).get("name", ""),
                f"Posted: {(j.get('first_published') or '')[:10]}", "Salary: see text"]
        body = text(j.get("content"))
    elif "lever.co" in u.netloc:
        j = get(f"https://api.lever.co/v0/postings/{parts[0]}/{parts[1]}")
        lists = "\n\n".join(f"{l['text']}\n{text(l['content'])}" for l in j.get("lists", []))
        head = [j["text"], (j.get("categories") or {}).get("location", ""), "", "Salary: see text"]
        body = "\n\n".join([j.get("descriptionPlain", ""), lists, j.get("additionalPlain", "")])
    elif u.netloc.endswith(".myworkdayjobs.com"):
        tenant = u.netloc.split(".")[0]
        site, ext = parts[0], "/" + "/".join(parts[1:])
        d = get(f"https://{u.netloc}/wday/cxs/{tenant}/{site}{ext}")["jobPostingInfo"]
        head = [d["title"], d.get("location", ""), f"Posted: {d.get('startDate','')} ({d.get('postedOn','')})",
                "Salary: see text"]
        body = text(d.get("jobDescription"))
    else:
        print("Unsupported job system; open the page in a browser or use web fetch.")
        sys.exit(2)
    print("\n".join(h for h in head if h) + "\n\n" + body)


if __name__ == "__main__":
    try:
        main()
    except (StopIteration, RuntimeError, KeyError) as e:
        print(f"Posting not found or unreadable: {e}")
        sys.exit(2)
