"""Check requirements and create the folders and empty files the system needs.

Usage: python3 .claude/skills/setup/scripts/init.py

Safe to run again: it never overwrites a file that exists. Prints JSON with what it
created, what was already there, and any missing requirement with the command to fix it.
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TEMPLATES = Path(__file__).resolve().parents[1] / "templates"

FILES = {  # path in the project: template file name
    "Pipeline/Tracker.csv": "Tracker.csv",
    "Pipeline/Follow-ups.csv": "Follow-ups.csv",
    "Pipeline/Scan History.tsv": "Scan History.tsv",
    "Profile/Target Companies.csv": "Target Companies.csv",
    "Profile/Setup Progress.md": "Setup Progress.md",
}
FOLDERS = ["Master Resume", "Profile", "Pipeline", "Pipeline/Alerts", "Companies"]


def main():
    missing = []
    if sys.version_info < (3, 9):
        missing.append({"need": "Python 3.9 or newer", "fix": "Install Python from https://www.python.org/downloads/"})
    if importlib.util.find_spec("docx") is None:
        missing.append({"need": "python-docx (reads and writes Word files)",
                        "fix": f"{Path(sys.executable).name} -m pip install --user python-docx"})
    if shutil.which("curl") is None:
        missing.append({"need": "curl (fetches job feeds)", "fix": "Install curl for your system"})
    created, existing = [], []
    for d in FOLDERS:
        p = ROOT / d
        (existing if p.exists() else created).append(d + "/")
        p.mkdir(parents=True, exist_ok=True)
    for rel, tpl in FILES.items():
        p = ROOT / rel
        if p.exists():
            existing.append(rel)
        else:
            p.write_text((TEMPLATES / tpl).read_text())
            created.append(rel)
    print(json.dumps({"root": str(ROOT), "python": sys.executable, "created": created,
                      "already_there": existing, "missing": missing, "ready": not missing}, indent=1))


if __name__ == "__main__":
    main()
