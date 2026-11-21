#!/usr/bin/env python3
"""agent-guard.py — PreToolUse hook for the delegate-implementer / delegate-reviewer subagents.

Same rules as the OpenCode agents: edits only inside ~/.delegate, Bash only for inspection and
tests, never git, Slurm, network, installs or sudo. Usage (from the subagent frontmatter):
    python3 -I $HOME/.claude/skills/delegate/scripts/agent-guard.py implementer|reviewer
Exit 0 + JSON "allow" → runs without a prompt; exit 2 → blocked, stderr goes back to the agent.
"""
import json, os, re, shlex, sys

ROLE = sys.argv[1] if len(sys.argv) > 1 else "implementer"
HOME = os.path.expanduser("~")
DELEGATE = os.path.realpath(os.environ.get("DELEGATE_HOME", os.path.join(HOME, ".delegate")))
WORKTREES = os.path.join(DELEGATE, "worktrees")
RUNS = os.path.join(DELEGATE, "runs")

ALLOW_CMDS = {
    # inspection
    "ls", "cat", "head", "tail", "wc", "grep", "rg", "find", "diff", "pwd", "echo", "tree",
    "sort", "uniq", "cut", "true", "test", "[", "cd", "stat", "file", "realpath", "dirname", "basename",
    # tests, linters, builds
    "pytest", "mypy", "ruff", "black", "flake8", "pylint", "tox", "nox", "ctest", "Rscript",
    "npm", "npx", "pnpm", "yarn", "node", "cargo", "go", "make", "cmake",
    "python", "python3", "timeout",
}
if ROLE == "implementer":
    ALLOW_CMDS |= {"mkdir", "touch", "cp", "mv"}

DENY_CMDS = {
    "git", "gh", "sbatch", "srun", "salloc", "scancel", "scontrol", "sbcast", "qsub", "qdel",
    "ssh", "scp", "rsync", "curl", "wget", "nc", "sudo", "su", "conda", "mamba", "micromamba",
    "pip", "pip3", "uv", "rm", "chmod", "chown", "kill", "pkill", "tmux", "agent-deck", "opencode", "claude",
}
DENY_ARGS = [  # forbidden even under an allowed command
    (re.compile(r"\b(install|add|publish|link)\b"), {"npm", "pnpm", "yarn", "cargo", "go"}),
]


def block(msg):
    sys.stderr.write(f"Blocked by the delegate guard ({ROLE}): {msg}. "
                     "This is a delegated run: do not retry; list it under Concerns in your final block.\n")
    sys.exit(2)


def allow():
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": "allow",
                                             "permissionDecisionReason": "delegate guard"}}))
    sys.exit(0)


def inside(path, root):
    p = os.path.realpath(os.path.expanduser(path))
    return p == root or p.startswith(root + os.sep)


def check_bash(cmd):
    if re.search(r"`|\$\(|<\(|>\(", cmd):
        block("command substitution is not allowed")
    for m in re.finditer(r"(?<![0-9&])>>?\s*([^\s;&|]+)", cmd):  # output redirections
        target = m.group(1)
        if target not in ("/dev/null",) and not target.startswith("&") and not inside(target, DELEGATE):
            if os.path.isabs(os.path.expanduser(target)):
                block(f"redirect to {target} is outside ~/.delegate")
    for seg in re.split(r"&&|\|\||;|\||\n", cmd):
        seg = seg.strip()
        if not seg:
            continue
        try:
            words = shlex.split(seg)
        except ValueError:
            block("could not parse the command")
        while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):  # VAR=value prefixes
            words = words[1:]
        if not words:
            continue
        exe = os.path.basename(words[0])
        if exe in DENY_CMDS or any(os.path.basename(w) in ("git", "sbatch", "srun") for w in words[1:]):
            block(f"'{exe}' is not allowed (no git, Slurm, network, installs, deletions)")
        if exe not in ALLOW_CMDS:
            block(f"'{exe}' is not on the allowed list (inspection and test commands only)")
        if exe in ("python", "python3") and len(words) > 1 and words[1] == "-m" and len(words) > 2 \
                and words[2] in ("pip", "venv", "ensurepip", "http.server"):
            block(f"python -m {words[2]} is not allowed")
        for rx, exes in DENY_ARGS:
            if exe in exes and len(words) > 1 and rx.search(words[1]):
                block(f"'{exe} {words[1]}' is not allowed")
        if exe == "cd" and len(words) > 1 and not inside(words[1], DELEGATE):
            block("cd outside ~/.delegate")
        if exe == "find" and any(w in ("-delete", "-exec", "-execdir", "-ok", "-fprint") for w in words):
            block("find may only list files")
        if exe in ("mkdir", "touch", "cp", "mv"):
            for w in words[1:]:
                if not w.startswith("-") and os.path.isabs(os.path.expanduser(w)) and not inside(w, WORKTREES):
                    block(f"{exe} target {w} is outside the worktree")
    allow()


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        block("unreadable hook input")
    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}
    if tool == "Bash":
        check_bash(ti.get("command", ""))
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = ti.get("file_path") or ti.get("notebook_path") or ""
        if ROLE == "reviewer":
            if not (inside(path, RUNS) and re.search(r"/review-\d+\.md$", path)):
                block("the reviewer may only write its review-N.md file")
        elif not (inside(path, WORKTREES) or (inside(path, RUNS) and path.endswith("/output.md"))):
            block(f"{path} is outside the delegated worktree")
        allow()
    if tool in ("Read", "Grep", "Glob"):
        sys.exit(0)  # normal permissions (secrets are denied in settings.json)
    block(f"tool {tool} is not available to delegated agents")


main()
