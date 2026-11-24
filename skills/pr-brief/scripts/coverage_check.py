#!/usr/bin/env python3
"""Check that every hunk needing an explanation belongs to a described change.

Usage: coverage_check.py hunks.json changes.json

changes.json: {"changes": [{"id": "C1", "title": "...", "hunks": ["H0001", ...]}]}

Hunks in these classes must be covered: change, added-file, tests, deletion,
deleted-file (deletions that still have references at the head). Mechanical
classes and docs/changelog/data/binary are reported as groups and need not be.
Exits 1 and lists the hunks left over when coverage is incomplete.
"""
import json
import sys

MUST_EXPLAIN = {"change", "added-file", "tests", "deletion", "deleted-file"}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    hunks = json.load(open(sys.argv[1]))["hunks"]
    changes = json.load(open(sys.argv[2]))["changes"]
    by_id = {h["id"]: h for h in hunks}
    covered = {}
    unknown = []
    for c in changes:
        for hid in c.get("hunks", []):
            if hid not in by_id:
                unknown.append((c["id"], hid))
            covered.setdefault(hid, []).append(c["id"])
    need = [h for h in hunks if h["class"] in MUST_EXPLAIN]
    missing = [h for h in need if h["id"] not in covered]
    print(f"{len(need) - len(missing)}/{len(need)} hunks needing explanation are covered by {len(changes)} changes")
    for cid, hid in unknown:
        print(f"  change {cid} lists unknown hunk id {hid}")
    for h in missing:
        loc = f"{h['file']}:{h.get('new_start', '')}" if h.get("new_start") else h["file"]
        print(f"  UNEXPLAINED {h['id']} [{h['class']}] {loc} (+{h['added']}/-{h['removed']})")
    sys.exit(1 if missing or unknown else 0)


if __name__ == "__main__":
    main()
