# pr-brief

Briefs a reviewer on a GitHub pull request they didn't write. It was built for a tech lead in bioinformatics who reviews many PRs a day and keeps the scientific judgement for themselves.

The skill reads the whole PR and returns a short brief, about 15 to 30 lines:

- **What was done and how:** one line per change, with the method the author used.
- **What changes:** behaviour before and after, side effects the PR doesn't mention, and which callers or commands the change reaches.

It doesn't approve, reject or judge the science. Ask it "should I merge?" and it says the decision is yours, then lists the facts.

After the brief it stays on the PR and answers questions using only the PR itself: commits, diff, description, comments and linked issues, each answer with a citation. If the PR doesn't say, it tells you so instead of guessing. Ask for ways to test, affected pipelines or runtime and you get them; they're left out of the brief to keep it short.

It never times code. Runtime is reported only as the PR states it. If the diff looks like it could change runtime a lot, the brief carries a one-line alert.

## How it works

1. Asks which language you want to talk in. The default is English.
2. Collects the PR: metadata, commits, comments, inline review comments, linked issues, and whether the author has write access (`scripts/gather_pr.py`).
3. Sorts every hunk of the diff (`scripts/classify_hunks.py`). Renames, moved code, docstring-only edits and dead deletions are checked by machine and summed up as one line. Real changes are read in full.
4. Checks that every real hunk belongs to a change in the brief (`scripts/coverage_check.py`), so nothing changes quietly.
5. Finds who uses the touched functions: library code, `bin/` commands, tests and docs (`scripts/impact.py`). If the repo has `.claude/pr-brief/pipelines.md`, a list of your team's own pipelines, it maps those too.
6. Runs small before/after examples on fixture data (`scripts/compare.sh`). It does this only when the author has write access to the repo; for anyone else it asks you first. It never installs packages.

## Requirements

Claude Code (or another agent that reads `SKILL.md` skills), `git`, the GitHub CLI `gh` logged in, and Python 3.8+. The before/after examples also need a Python that can import the project's code: set `ROTIFER_PYTHON`, or have an environment named `rotifer`.

## Install

```bash
cp -r skills/pr-brief ~/.claude/skills/
```

Or zip the folder and upload it wherever your AI tool takes skills:

```bash
cd skills && zip -r pr-brief.zip pr-brief
```

## Use

```
/pr-brief 172
/pr-brief queue          # one line for each PR waiting on your review
```

Then just ask: "does this touch acc2operon?", "how do I test C2?", "what did they say about NaN taxids?".

## Settings

- `PR_BRIEF_SCRATCH`: where worktrees and outputs go. The default is `$TMPDIR/pr-brief-$USER`.
- `ROTIFER_PYTHON`: the Python used for the before/after examples.
- `.claude/pr-brief/pipelines.md` in the reviewed repo: your team's pipelines, so the brief can name the ones a PR affects.

The conventions it looks for (coordinates, strand, missing values, identifiers and so on) and the runtime alert signals are listed in `references/conventions.md`. Edit that file to fit your field.
