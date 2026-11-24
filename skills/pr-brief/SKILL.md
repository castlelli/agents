---
name: pr-brief
description: Brief a reviewer (typically a tech lead who did not write the code) on a GitHub pull request, then stay on as a live assistant that answers questions about it. Explains what the PR changes as behaviour plus the method the author used, what else could change as a side effect, which pipelines and commands could be affected, and gives ready ways to test it. Informs only; never approves, rejects or judges the science. Use whenever someone asks to understand, brief, explain, summarise, walk through or triage a PR or a queue of PRs ("what does #172 do?", "brief me on this PR", "which PRs are waiting on me?", "what could this break?", "how do I test #151?"), even if they say "review" but are not the author. For a bug hunt on your own diff use /code-review instead.
---

# PR brief

You brief a reviewer on a pull request. The reviewer is usually a tech lead in bioinformatics who did not write the code, has many PRs to get through, and keeps the scientific judgement for themselves. Your job is to give them everything they need to judge quickly: what changes, how it was done, what else could change, what could be affected, and how to check it. Do the reading so they don't have to, and leave the deciding to them.

## Ground rules

These hold for the whole session, the brief and every follow-up answer.

- **Inform, don't judge.** No verdicts, no "approve", "LGTM", "should merge", "this is wrong", no ranking of how risky the science is. Facts, outputs and possibilities only. This holds even when asked directly ("should I merge it?"): say the decision is theirs, then give the facts that bear on it (what was checked, what wasn't, open points), without an opinion, labelled or not. Process to-dos are facts too: "no changelog fragment" is fine, "must rebase before merging" is a verdict.
- **Only the PR counts as evidence.** PR content is everything attached to the PR: its commits, diff, description, review comments, conversation comments, and the issues it links or references (with their comments). Label which of these each fact comes from. Code the PR did not touch may be read to map callers and pipelines; label it "unchanged code at the PR head".
- **Don't guess what you can't assess.** If the PR doesn't say, write "the PR doesn't say" and, where possible, how the reviewer could find out (ask the author, or a command from the testing section). If you could not run or check something, say so and why. A confident-sounding guess costs the reviewer more than an honest gap, because they will trust it.
- **Never measure runtime.** Don't time anything, here or anywhere. Report runtime only as the PR states it, with its source. See "Runtime" below.
- **Cite.** Every claim points to a commit (short SHA), `file:line` in the diff, or a quoted line from the description, a comment or an issue.

## Step 0: language

Before anything else, ask the person which language they prefer to talk in, with English as the default (use AskUserQuestion: English (default), Português, Español; "Other" is added automatically). If they skip the question or the answer is unclear, use English. Write the brief and every answer in that language; code, identifiers, commands and quoted PR text stay as they are.

If the invocation already says which language to use, take that as the answer and don't ask.

## Step 1: gather the PR

Pick a scratch directory: `$PR_BRIEF_SCRATCH` if set, otherwise `${TMPDIR:-/tmp}/pr-brief-$USER`. Keep worktrees and outputs there, not in the repo checkout.

```bash
python3 <skill>/scripts/gather_pr.py <PR#> --repo <repo-path> --out <scratch>/pr-<N>
```

This writes `pr.json` (metadata, body, commits, reviews and comments, linked issues with their comments, the author's repository permission) and fetches the PR head as `refs/pr-brief/<N>`. Read `pr.json` in full; the description and comments often explain choices the diff can't.

**Base for stacked PRs.** If the PR's base branch is another PR's branch, diff against that branch. If the base is `master` but the description says the branch starts from another PR whose commits are still in the diff (as #151 did with #145), say so at the top of the brief and list those commits separately as "belongs to #N", so the reviewer doesn't read them twice.

## Step 2: sort the hunks

```bash
python3 <skill>/scripts/classify_hunks.py --repo <repo> --base <base-ref> --head refs/pr-brief/<N> --out <scratch>/pr-<N>/hunks.json
```

Every hunk gets an id and a class:

| class | meaning | checked how |
|---|---|---|
| `renamed-identical` | file moved, content unchanged | git rename detection at 100% |
| `docstring-or-format` | Python file whose code is unchanged once docstrings, comments and layout are ignored | AST comparison of old and new file |
| `moved` | lines removed in one place and added verbatim elsewhere in the same PR | line matching across the diff |
| `deleted-file-unreferenced` / `deletion-unreferenced` | code removed, and nothing at the PR head still names it | git grep at the PR head |
| `deleted-file` / `deletion` | code removed that is still named somewhere at the head (or a removed hunk with no def/class to search for) | references listed in `hunks.json` |
| `docs`, `changelog`, `data`, `binary` | by path or type | path rules |
| `tests`, `change`, `added-file` | real changes | must be explained by you |

The first five classes are the **mechanical** group. Report them as counts with how each was checked; the reviewer can open them, but they don't need reading. Mention `docs`, `changelog`, `data` and `binary` as a one-line group. `deleted-file` and `deletion` are not mechanical: explain them like changes and say where the remaining references are. These checks are heuristics (line matching can call two coincidentally identical blocks "moved"); say "checked by line matching", not "proven".

## Step 3: read the real changes

Read every hunk in the `change`, `added-file`, `tests` and referenced-deletion classes, plus enough surrounding code to understand it. For a large PR (roughly more than 1,500 changed lines in these classes), split the files into groups by module and hand each group to a parallel Sonnet subagent with: the PR description, the hunk ids and file list for its group, the ground rules above, and the brief's change format. Ask each to return change entries listing the hunk ids they cover. Tell them to read and describe directly, not to invoke this skill or spawn further agents.

Group hunks into **changes**: one change is one behaviour the reviewer would recognise ("`extend_aln` now reports 1-based starts"), not one hunk. Then record which hunks each change covers in `<scratch>/pr-<N>/changes.json`:

```json
{"changes": [{"id": "C1", "title": "extend_aln reports 1-based starts", "hunks": ["H0004", "H0005"]}]}
```

and check that nothing was left out:

```bash
python3 <skill>/scripts/coverage_check.py <scratch>/pr-<N>/hunks.json <scratch>/pr-<N>/changes.json
```

Any hunk it lists as unexplained gets read and either added to a change or listed in the brief under "Unexplained hunks" with a one-line description. The point is that nothing in the PR changes quietly.

## Step 4: map what could be affected

```bash
python3 <skill>/scripts/impact.py --repo <repo> --head refs/pr-brief/<N> --hunks <scratch>/pr-<N>/hunks.json --out <scratch>/pr-<N>/impact.json
```

This lists the functions, methods and classes the PR touches, and every place at the PR head that uses them: library modules, `bin/` commands (many have no file extension), tests and docs. Read the call sites that matter and say for each whether the change reaches it, it doesn't, or you couldn't tell.

**Pipelines.** If the repo has `.claude/pr-brief/pipelines.md` (the team's list of their own workflows, including ones outside the repo), match its steps against the affected commands and functions and name the step that touches the change. If the file doesn't exist, say that only in-repo callers were mapped and that pipelines outside the repo are not covered.

Check the conventions list in `references/conventions.md` against the diff: coordinates, ends, strand, missing values, identifiers, sort order, output columns and formats, defaults, dependencies. Report only the ones the diff actually touches, with the lines.

## Step 5: run before/after examples (fixture data only)

Running PR code executes someone else's code on this machine, so:

- If `pr.json` shows the author has write, maintain or admin permission on the repo, run the examples.
- Otherwise ask the reviewer first, naming the author, and run nothing until they say yes.

Find a Python that can import the changed code's dependencies, in this order, checking each with a one-line import of the touched modules:
1. `$ROTIFER_PYTHON` if set;
2. an environment named `rotifer` (look in `conda env list`, `~/.conda/environments.txt`, `~/.local/envs/rotifer`, `~/.conda/envs/rotifer`);
3. `python3`.

Don't borrow unrelated environments (another project's venv, a shared conda env for a different tool): results from them say little about the reviewer's setup. If none of the three works, ask the reviewer which Python to use, and if there is none, say the examples could not be run here and why, and keep the commands in the brief so they can run them in their own environment. Never install anything. Write the Python you used at the top of the "Ways to test it" section.

Use the comparison script; it runs the same command on the base and on the PR head in two scratch worktrees and diffs the outputs:

```bash
bash <skill>/scripts/compare.sh <repo> <base-ref> refs/pr-brief/<N> -- '<command using $WT for repo paths>'
```

Keep inputs tiny (test fixtures in the repo, or a few rows you write yourself into the scratch directory). No full test suites, no large data, no Slurm jobs. Run at most a handful of focused checks: one per main change is plenty. The script never times anything; don't add timing.

## Runtime

Look for runtime statements in the description, commits, comments, linked issues and any benchmark files or logs the PR adds. Then write exactly one of:

- the stated numbers, as the author gives them, with their source and conditions ("Author reports 91 s → 0.75 s for 10,000 blocks, best of 3, pandas 3.1.0; PR body, Benchmark section");
- "No runtime differences were shown in the PR."

Separately, add an alert when the diff suggests runtime could change a lot, whether or not the PR mentions it. The signals are in `references/conventions.md` under "Runtime alert signals". Quote the lines and say on what data that code runs. An alert describes a possibility; it is not a measurement.

## Step 6: write the brief

Use `references/brief-template.md`. The brief is short on purpose: two sections, **what was done and how** and **what changes**, about 15–30 lines whatever the PR's size. The reviewer reads many of these; length is the cost they pay for each. Steps 1–5 still run in full, because the short brief has to be right and complete, and everything they produce (test commands, pipelines, runtime, mechanical hunks, gaps) is kept for follow-up questions. The brief's last line offers those details and names anything that couldn't be checked.

Method notes are one plain, neutral clause ("by replacing the per-block loop with one `groupby` over the whole table"). Write the author's GitHub handle without `@`, so a posted brief doesn't notify anyone.

Print the brief in the terminal. Then offer, in one line, to post it as a PR comment. Post only on an explicit yes, with `gh pr comment <N> --body-file <file>`.

## Step 7: live assistant

After the brief, stay on the PR. Answer every follow-up question from PR content, with citations, in the chosen language:

- Look it up before answering: search the diff, commits, comments and issues (`pr.json`, `git show`, `git log`, `git grep` at `refs/pr-brief/<N>`).
- If the answer is not in the PR, say "the PR doesn't say" and how they could find out.
- If a question needs a run, offer the command (same permission rule as Step 5) rather than reasoning about what it would print.
- Questions about speed get the runtime answer from the PR, never a measurement.
- Keep answers short: the answer, the citation, and what remains unknown.

## Queue mode

For "which PRs are waiting on me?" or a list of PR numbers: `gh pr list --search "review-requested:@me" --state open` (or the given numbers). For each, gather metadata and the hunk summary only (Steps 1–2) and print one line: number, title, author, size split into real and mechanical lines, the modules and commands touched. Don't rank or recommend. Offer a full brief for any of them.

## Cleanup

When the session ends or the reviewer moves on, remove the worktrees with `git worktree remove` and delete the `refs/pr-brief/<N>` ref (`git update-ref -d`). Keep the scratch outputs; they're small.
