#!/usr/bin/env python3
"""Split a diff into hunks and sort each into a class.

Classes: renamed-identical, docstring-or-format, moved, deleted-file, deletion,
docs, changelog, tests, data, binary, added-file, change.

The mechanical classes (renamed-identical, docstring-or-format, moved, and
deletions with no references left at the head) are checked by machine:
git rename detection, AST comparison, line matching across the diff and
git grep. Everything else needs a human-readable explanation.

Usage: classify_hunks.py --repo PATH --base REV --head REV --out hunks.json
"""
import argparse
import ast
import json
import os
import re
import subprocess
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning)
import sys
from collections import Counter

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
DEF_RE = re.compile(r"^\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)")
TRIVIAL = {"", "else:", "try:", "finally:", "pass", "return", "break", "continue",
           ")", "]", "}", "),", "],", "},", '"""', "'''", "#", "else", "fi", "done", "end"}
DATA_EXT = {".tsv", ".csv", ".fa", ".faa", ".fna", ".fasta", ".gb", ".gbk", ".gff",
            ".gff3", ".json", ".txt", ".aln", ".sto", ".hmm", ".tbl", ".out", ".xml"}
MECHANICAL = {"renamed-identical", "docstring-or-format", "moved", "deletion-unreferenced",
              "deleted-file-unreferenced"}


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, errors="replace")
    if check and p.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def norm(line):
    return line.strip()


def nontrivial(lines):
    return [norm(l) for l in lines if norm(l) not in TRIVIAL and len(norm(l)) >= 6]


def strip_docstrings(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                node.body = body[1:] or [ast.Pass()]
    return tree


def same_code(old_src, new_src):
    try:
        a = strip_docstrings(ast.parse(old_src))
        b = strip_docstrings(ast.parse(new_src))
    except SyntaxError:
        return False
    return ast.dump(a, include_attributes=False) == ast.dump(b, include_attributes=False)


def path_class(path):
    low = path.lower()
    base = os.path.basename(low)
    ext = os.path.splitext(low)[1]
    if low.startswith("changelog.d/") or base.startswith("changelog"):
        return "changelog"
    if low.startswith(("test/", "tests/")) or base.startswith("test_") or base.endswith("_test.py"):
        if ext in DATA_EXT or "/data/" in low:
            return "data"
        return "tests"
    if low.startswith("docs/") or ext in {".md", ".rst"}:
        return "docs"
    return None


def parse_diff(text):
    files, cur, hunk = [], None, None
    for line in text.splitlines():
        if line.startswith("diff --git "):
            m = re.match(r"diff --git a/(.*) b/(.*)$", line)
            cur = {"old": m.group(1), "new": m.group(2), "status": "M", "similarity": None,
                   "binary": False, "hunks": []}
            files.append(cur)
            hunk = None
        elif cur is None:
            continue
        elif line.startswith("new file mode"):
            cur["status"] = "A"
        elif line.startswith("deleted file mode"):
            cur["status"] = "D"
        elif line.startswith("similarity index"):
            cur["similarity"] = int(line.split()[-1].rstrip("%"))
            cur["status"] = "R"
        elif line.startswith("rename from "):
            cur["old"] = line[len("rename from "):]
        elif line.startswith("rename to "):
            cur["new"] = line[len("rename to "):]
        elif line.startswith("Binary files"):
            cur["binary"] = True
        elif line.startswith("@@"):
            m = HUNK_RE.match(line)
            hunk = {"old_start": int(m.group(1)), "old_len": int(m.group(2) or 1),
                    "new_start": int(m.group(3)), "new_len": int(m.group(4) or 1),
                    "added": [], "removed": []}
            cur["hunks"].append(hunk)
        elif hunk is not None and line.startswith("+") and not line.startswith("+++"):
            hunk["added"].append(line[1:])
        elif hunk is not None and line.startswith("-") and not line.startswith("---"):
            hunk["removed"].append(line[1:])
    return files


def references(repo, head, names, exclude_path):
    """git grep -w at head for each name; return {name: [file:line, ...]}."""
    out = {}
    for name in sorted(set(names)):
        if len(name) < 4:
            continue
        res = git(repo, "grep", "-n", "-w", "-I", name, head, "--", ".", check=False)
        hits = []
        for l in res.splitlines():
            parts = l.split(":", 3)
            if len(parts) >= 3 and parts[1] != exclude_path:
                hits.append(f"{parts[1]}:{parts[2]}")
        if hits:
            out[name] = hits[:20] + ([f"... {len(hits) - 20} more"] if len(hits) > 20 else [])
    return out


def module_names(path):
    if not path.endswith(".py"):
        return [os.path.basename(path)]
    p = path[:-3]
    if p.startswith("lib/"):
        p = p[4:]
    dotted = p.replace("/", ".")
    if dotted.endswith(".__init__"):
        dotted = dotted[: -len(".__init__")]
    return [dotted]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--base", required=True, help="merge-base or base commit")
    ap.add_argument("--head", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    base = git(repo, "rev-parse", a.base).strip()
    head = git(repo, "rev-parse", a.head).strip()

    diff = git(repo, "diff", "-M", "--no-color", "--no-ext-diff", "-U0", base, head)
    files = parse_diff(diff)

    all_added, all_removed = Counter(), Counter()
    for f in files:
        for h in f["hunks"]:
            all_added.update(nontrivial(h["added"]))
            all_removed.update(nontrivial(h["removed"]))

    hunks, n = [], 0
    for f in files:
        pc = path_class(f["new"])
        file_level = None
        if f["binary"]:
            file_level = "binary"
        elif f["status"] == "R" and f["similarity"] == 100 and not f["hunks"]:
            file_level = "renamed-identical"
        elif f["status"] == "D":
            file_level = "deleted-file"
        elif pc:
            file_level = pc
        elif f["status"] == "A":
            file_level = "added-file"

        same = False
        if file_level is None and f["new"].endswith(".py") and f["hunks"]:
            old_src = git(repo, "show", f"{base}:{f['old']}", check=False)
            new_src = git(repo, "show", f"{head}:{f['new']}", check=False)
            same = same_code(old_src, new_src)

        if not f["hunks"]:
            n += 1
            entry = {"id": f"H{n:04d}", "file": f["new"], "old_file": f["old"], "status": f["status"],
                     "class": file_level or "change", "added": 0, "removed": 0}
            if file_level == "deleted-file":
                refs = references(repo, head, module_names(f["old"]), f["old"])
                entry["references_at_head"] = refs
                entry["class"] = "deleted-file" if refs else "deleted-file-unreferenced"
            hunks.append(entry)
            continue

        for h in f["hunks"]:
            n += 1
            cls = file_level
            extra = {}
            if cls == "deleted-file":
                pass
            elif cls is None:
                add_nt, rem_nt = nontrivial(h["added"]), nontrivial(h["removed"])
                if same:
                    cls = "docstring-or-format"
                elif Counter(map(norm, h["added"])) == Counter(map(norm, h["removed"])):
                    cls = "docstring-or-format"
                elif h["added"] and not h["removed"] and len(add_nt) >= 2 and all(all_removed[l] for l in add_nt):
                    cls = "moved"
                    extra["moved"] = "added lines found removed elsewhere in the diff"
                elif h["removed"] and not h["added"]:
                    if len(rem_nt) >= 2 and all(all_added[l] for l in rem_nt):
                        cls = "moved"
                        extra["moved"] = "removed lines found added elsewhere in the diff"
                    else:
                        names = [m.group(1) for l in h["removed"] if (m := DEF_RE.match(l))]
                        refs = references(repo, head, names, f["new"]) if names else {}
                        extra["removed_definitions"] = names
                        extra["references_at_head"] = refs
                        cls = "deletion" if (refs or not names) else "deletion-unreferenced"
                else:
                    cls = "change"
            hunks.append({
                "id": f"H{n:04d}", "file": f["new"], "old_file": f["old"], "status": f["status"],
                "class": cls, "old_start": h["old_start"], "old_len": h["old_len"],
                "new_start": h["new_start"], "new_len": h["new_len"],
                "added": len(h["added"]), "removed": len(h["removed"]), **extra,
            })

    summary = {}
    for h in hunks:
        s = summary.setdefault(h["class"], {"hunks": 0, "added": 0, "removed": 0, "files": set()})
        s["hunks"] += 1
        s["added"] += h["added"]
        s["removed"] += h["removed"]
        s["files"].add(h["file"])
    for s in summary.values():
        s["files"] = len(s["files"])

    with open(a.out, "w") as fh:
        json.dump({"base": base, "head": head, "mechanical_classes": sorted(MECHANICAL),
                   "summary": summary, "hunks": hunks}, fh, indent=1)

    print(f"{'class':28} {'hunks':>6} {'files':>6} {'+lines':>8} {'-lines':>8}  mechanical")
    for cls, s in sorted(summary.items(), key=lambda kv: -(kv[1]["added"] + kv[1]["removed"])):
        print(f"{cls:28} {s['hunks']:>6} {s['files']:>6} {s['added']:>8} {s['removed']:>8}  {'yes' if cls in MECHANICAL else ''}")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
