#!/usr/bin/env python3
"""Check that generated notes follow the user's Obsidian templates exactly.

Usage: check_templates.py <folder> --project "<Project page>.md"
Every other .md in the folder is checked against assets/full_note.md.
"""
import argparse, pathlib, re, sys

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
DATE = r"\d{4}-\d{2}-\d{2} - \d{2}:\d{2}"


def header_lines(template: str) -> list[str]:
    out = []
    for line in template.split("\n"):
        out.append(line)
        if line.startswith("# {{title}}"):
            break
    return out


def check(path: pathlib.Path, template: str, is_project: bool) -> list[str]:
    errs = []
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    for i, exp in enumerate(header_lines(template)):
        got = lines[i] if i < len(lines) else "<missing>"
        if exp.startswith("# {{title}}"):
            if got != f"# {path.stem}":
                errs.append(f"line {i+1}: title heading should be '# {path.stem}', got {got!r}")
        elif "{{date}}" in exp:
            if not re.fullmatch("date: " + DATE, got):
                errs.append(f"line {i+1}: expected 'date: YYYY-MM-DD - HH:MM', got {got!r}")
        elif got != exp:
            errs.append(f"line {i+1}: expected {exp!r}, got {got!r}")
    if "{{" in text:
        errs.append("unfilled {{placeholder}} left in file")
    if "[[" in text:
        errs.append("contains wikilinks — leave linking to the integration step")
    if is_project:
        heads = [l for l in lines if l.startswith("### ")]
        want = ["### Overview", "### Goals", "### Tasks and steps"]
        if heads != want:
            errs.append(f"project sections should be exactly {want}, got {heads}")
        if "### Overview" in lines:
            nxt = lines[lines.index("### Overview") + 1:lines.index("### Overview") + 2]
            if not nxt or not nxt[0].startswith("\t- "):
                errs.append("Overview must start with a tab-indented bullet ('\\t- ')")
    else:
        if "### Overview" in lines:
            errs.append("atomic note uses project-page sections")
        if len(path.stem.split()) > 4:
            errs.append(f"title has {len(path.stem.split())} words — keep it to 2–4")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--project", required=True, help="filename of the project page")
    a = ap.parse_args()
    folder = pathlib.Path(a.folder)
    full = (ASSETS / "full_note.md").read_text(encoding="utf-8")
    proj = (ASSETS / "project.md").read_text(encoding="utf-8")
    files = sorted(folder.glob("*.md"))
    if not any(f.name == a.project for f in files):
        print(f"project page {a.project!r} not found in {folder}")
        sys.exit(1)
    bad = 0
    for f in files:
        is_p = f.name == a.project
        errs = check(f, proj if is_p else full, is_p)
        print(f"[{'OK ' if not errs else 'FIX'}] {f.name}")
        for e in errs:
            print(f"      - {e}")
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
