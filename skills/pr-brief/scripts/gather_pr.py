#!/usr/bin/env python3
"""Collect everything attached to a pull request into one JSON file.

Fetches the PR head as refs/pr-brief/<N> and writes <out>/pr.json with:
metadata, description, commits, reviews, conversation comments, inline review
comments, linked/referenced issues (with their comments), the author's
repository permission, and the base/head/merge-base SHAs to diff.

Usage: gather_pr.py <PR#> [--repo PATH] --out DIR
"""
import argparse
import json
import os
import re
import subprocess
import sys

FIELDS = ",".join([
    "number", "title", "url", "state", "isDraft", "author", "body", "labels",
    "baseRefName", "headRefName", "baseRefOid", "headRefOid", "additions",
    "deletions", "changedFiles", "commits", "reviews", "comments",
    "closingIssuesReferences", "mergedAt", "createdAt",
])


def run(cmd, cwd=None, check=True):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}\n{p.stderr.strip()}")
    return p


def gh_json(args, cwd):
    return json.loads(run(["gh", *args], cwd=cwd).stdout or "null")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pr", type=int)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-issues", type=int, default=15)
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    os.makedirs(a.out, exist_ok=True)

    nwo = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], cwd=repo).stdout.strip()
    pr = gh_json(["pr", "view", str(a.pr), "--json", FIELDS], repo)

    inline = gh_json(["api", "--paginate", "--slurp", f"repos/{nwo}/pulls/{a.pr}/comments"], repo) or []
    inline = [c for page in inline for c in page]
    pr["reviewComments"] = [
        {"author": (c.get("user") or {}).get("login"), "path": c.get("path"),
         "line": c.get("line") or c.get("original_line"), "body": c.get("body"),
         "createdAt": c.get("created_at"), "inReplyTo": c.get("in_reply_to_id")}
        for c in inline
    ]

    # Issues linked or referenced anywhere in the PR's text.
    texts = [pr.get("body") or ""]
    texts += [c.get("messageHeadline", "") + "\n" + c.get("messageBody", "") for c in pr.get("commits", [])]
    texts += [c.get("body") or "" for c in pr.get("comments", [])]
    texts += [r.get("body") or "" for r in pr.get("reviews", [])]
    texts += [c["body"] or "" for c in pr["reviewComments"]]
    refs = {i["number"] for i in pr.get("closingIssuesReferences", [])}
    for t in texts:
        refs |= {int(m) for m in re.findall(r"(?<![\w/])#(\d+)\b", t)}
    refs.discard(a.pr)
    issues = []
    for n in sorted(refs)[: a.max_issues]:
        p = run(["gh", "issue", "view", str(n), "--json", "number,title,state,body,comments,url"], cwd=repo, check=False)
        if p.returncode == 0:
            iss = json.loads(p.stdout)
            iss["closedByThisPR"] = n in {i["number"] for i in pr.get("closingIssuesReferences", [])}
            issues.append(iss)
        else:
            issues.append({"number": n, "error": p.stderr.strip()[:200]})
    pr["referencedIssues"] = issues
    if len(refs) > a.max_issues:
        pr["referencedIssuesTruncated"] = sorted(refs)[a.max_issues:]

    login = (pr.get("author") or {}).get("login")
    p = run(["gh", "api", f"repos/{nwo}/collaborators/{login}/permission", "-q", ".permission"], cwd=repo, check=False)
    pr["authorPermission"] = p.stdout.strip() if p.returncode == 0 else "unknown"
    pr["authorIsMaintainer"] = pr["authorPermission"] in {"admin", "maintain", "write"}

    ref = f"refs/pr-brief/{a.pr}"
    run(["git", "fetch", "--quiet", "origin", f"+pull/{a.pr}/head:{ref}"], cwd=repo)
    run(["git", "fetch", "--quiet", "origin", pr["baseRefName"]], cwd=repo, check=False)
    base = pr["baseRefOid"]
    if run(["git", "cat-file", "-e", base + "^{commit}"], cwd=repo, check=False).returncode != 0:
        base = f"origin/{pr['baseRefName']}"
    mb = run(["git", "merge-base", base, ref], cwd=repo).stdout.strip()
    pr["diff"] = {"headRef": ref, "head": run(["git", "rev-parse", ref], cwd=repo).stdout.strip(),
                  "base": base, "mergeBase": mb, "repo": nwo}

    # Stacked PR hint: base branch is another open PR's head branch.
    p = run(["gh", "pr", "list", "--head", pr["baseRefName"], "--json", "number,title,state"], cwd=repo, check=False)
    pr["baseIsPR"] = json.loads(p.stdout) if p.returncode == 0 and p.stdout.strip() else []

    path = os.path.join(a.out, "pr.json")
    with open(path, "w") as fh:
        json.dump(pr, fh, indent=1)
    print(f"wrote {path}")
    print(f"PR #{a.pr} by {login} ({pr['authorPermission']}): {pr['title']}")
    print(f"diff: {mb[:9]}..{pr['diff']['head'][:9]} ({ref}); {len(pr.get('commits', []))} commits; "
          f"{len(pr.get('comments', []))} comments, {len(pr['reviewComments'])} inline, {len(issues)} issues")


if __name__ == "__main__":
    main()
