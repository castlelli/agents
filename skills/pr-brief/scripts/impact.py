#!/usr/bin/env python3
"""Map which functions/classes a PR touches and where they are used at the head.

For each Python hunk that needs explaining, find the enclosing def/class at the
head (or at the base for pure deletions), then git grep the name across the
repo at the head: library modules, bin/ commands (many have no extension),
tests and docs.

Usage: impact.py --repo PATH --head REV --hunks hunks.json --out impact.json
"""
import argparse
import ast
import json
import os
import subprocess
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning)
from collections import defaultdict

EXPLAIN = {"change", "added-file", "tests", "deletion", "deleted-file"}
GENERIC = {"main", "run", "__init__", "__call__", "__repr__", "__str__", "setup", "test",
           "parse", "read", "write", "load", "save", "get", "set", "update", "apply"}


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, errors="replace")
    return p.stdout if p.returncode == 0 else ""


def symbols(src):
    """Return [(qualname, name, start, end)] for defs and classes."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out = []

    def walk(node, prefix):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                q = f"{prefix}.{ch.name}" if prefix else ch.name
                out.append((q, ch.name, ch.lineno, ch.end_lineno or ch.lineno))
                walk(ch, q)
    walk(tree, "")
    return out


def innermost(syms, lo, hi):
    hits = [s for s in syms if s[2] <= hi and s[3] >= lo]
    if not hits:
        return []
    depth = max(s[0].count(".") for s in hits)
    return [s for s in hits if s[0].count(".") == depth]


def kind(path):
    if path.startswith("bin/"):
        return "bin"
    if path.startswith(("test/", "tests/")):
        return "test"
    if path.startswith("docs/") or path.endswith((".md", ".rst", ".ipynb")):
        return "docs"
    if path.startswith("lib/"):
        return "lib"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--head", required=True)
    ap.add_argument("--hunks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-hits", type=int, default=40)
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    data = json.load(open(a.hunks))
    base, head = data["base"], git(repo, "rev-parse", a.head).strip()

    cache = {}

    def syms_at(rev, path):
        key = (rev, path)
        if key not in cache:
            cache[key] = symbols(git(repo, "show", f"{rev}:{path}"))
        return cache[key]

    touched = defaultdict(lambda: {"hunks": [], "files": set()})
    for h in data["hunks"]:
        if h["class"] not in EXPLAIN or not h["file"].endswith(".py"):
            continue
        if h.get("new_len", 0) and h.get("new_start"):
            found = innermost(syms_at(head, h["file"]), h["new_start"], h["new_start"] + h["new_len"] - 1)
            where = h["file"]
        else:
            lo = h.get("old_start", 1)
            found = innermost(syms_at(base, h["old_file"]), lo, lo + max(h.get("old_len", 1), 1) - 1)
            where = h["old_file"]
        if not found and h["class"] in {"added-file", "deleted-file"}:
            rev = head if h["class"] == "added-file" else base
            found = [s for s in syms_at(rev, where) if "." not in s[0]]
        if not found:
            found = [(f"<module {where}>", None, 0, 0)]
        for q, name, *_ in found:
            touched[(q, name)]["hunks"].append(h["id"])
            touched[(q, name)]["files"].add(where)

    result = []
    for (q, name), info in sorted(touched.items()):
        entry = {"symbol": q, "defined_in": sorted(info["files"]), "hunks": info["hunks"]}
        if name and name not in GENERIC and len(name) >= 4:
            hits = defaultdict(list)
            for line in git(repo, "grep", "-n", "-w", "-I", name, head, "--", ".").splitlines():
                parts = line.split(":", 3)
                if len(parts) < 4 or parts[1] in info["files"]:
                    continue
                text = parts[3].strip()
                if text.startswith(("def ", "class ", "async def ")):
                    continue
                hits[kind(parts[1])].append(f"{parts[1]}:{parts[2]}")
            entry["used_by"] = {k: v[: a.max_hits] for k, v in hits.items()}
            entry["used_by_counts"] = {k: len(v) for k, v in hits.items()}
        else:
            entry["used_by"] = "not searched (name too generic or module-level change)"
        result.append(entry)

    with open(a.out, "w") as fh:
        json.dump({"head": head, "symbols": result}, fh, indent=1)
    for e in result:
        c = e.get("used_by_counts")
        cs = ", ".join(f"{k}:{v}" for k, v in sorted(c.items())) if c else ("none found" if c == {} else "not searched")
        print(f"{e['symbol']:60} {cs}")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
