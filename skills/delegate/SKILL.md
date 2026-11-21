---
name: delegate
description: Orchestrate a coding task by delegating implementation and first-pass review to free models via OpenCode in isolated git worktrees, then do the final review yourself. Use only when the user invokes /delegate.
disable-model-invocation: true
argument-hint: "<task description, or a path to a plan/spec>"
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/delegate.sh *) Read(~/.delegate/**)
---

# /delegate — you orchestrate, free models type

Task from the user: $ARGUMENTS

Run it with `D=${CLAUDE_SKILL_DIR}/scripts/delegate.sh`. You are the architect and the final
reviewer. Implementers and the first-pass reviewer are free models (Kimi, DeepSeek, OpenCode
Zen free models and, when a key is set, Gemini) running through OpenCode, with Claude Sonnet/Haiku subagents as the fallback. They cannot use git, the network, or the Slurm scheduler;
the script owns every git operation and every worktree.

## Your budget rule
Your context is the expensive resource. Read briefs, summaries, `diff.patch` and the REVIEW
block. Never `cat` the `*.jsonl` logs or whole verify logs; use `tail`/`grep` if a summary is
not enough. Each script command prints a bounded summary: trust it and act on it.

## 1. Scope (before any delegation)
- Read just enough code to plan. If something is unclear and it changes the design, ask the
  user one question, then continue.
- Keep for yourself: architecture and interface decisions, unknown-cause debugging, security,
  auth, secrets, anything under ~25 changed lines (a brief costs more than the edit), and
  anything you cannot describe precisely. Delegate the rest.
- Split work into slices of at most ~8 files and ~300 added lines, each independently
  verifiable. Run slices sequentially. Run two in parallel only when they touch disjoint files
  and the user asked for speed (free tiers are rate-limited per account/IP).
- Choose one verification command per slice that proves it (a focused test file or target,
  not the whole suite if that is slow). It must run on this node without submitting jobs.
- Show the user the slice plan (one line per slice + verify command) and proceed unless
  they object.

## 2. Write the brief
Copy `references/brief-template.md` into `~/.delegate/briefs/<slug>.md` and fill every
section. The brief is your leverage: when a run disappoints, the first suspect is the brief.
Required sections: Objective, Context, Files, Constraints, Steps, Acceptance, Verification,
Out of scope. Name exact files, functions, signatures, edge cases, and the existing code to
imitate. Never paste secrets into a brief.

## 3. Implement
Start it in the background (Bash tool with run_in_background) because runs take minutes:
```
$D implement --task <slug> --brief ~/.delegate/briefs/<slug>.md --verify "<command>" --repo <repo path>
```
When it exits, read its printed summary (also in `~/.delegate/runs/<slug>/summary.md`).
Exit codes: 0 ok · 3 no changes · 4 every model unavailable · 5 rate-limited · 6 stalled ·
7 POLICY VIOLATION (agent touched git) · 8 repair limit · 9 changes made but verification
failed (go to review/fix; the RESULT block's own claim that tests pass is not evidence).
On 4/5/6 every free model is down: tell the user in one line and use the **Claude fallback**
below for this round. On 7, stop and show the user the violation before anything else.

## 4. First-pass review (free model, read-only)
```
$D review --task <slug>
```
It picks a reviewer from a different model family than the implementer when possible.
On 4/5/6, use the Claude fallback with `--role reviewer`.

## Claude fallback (free models down: exit 4, 5 or 6)
The same worktree, checks and limits, with Claude Code subagents doing the typing:
Sonnet implements (`delegate-implementer`), Haiku pre-reviews (`delegate-reviewer`). They use
the user's Claude plan, so use them only after the free chain has failed for that step.
1. `$D handoff --task <slug> --role implementer [--brief <fix brief>]` (or `--role reviewer`).
   It prints the worktree, brief/context, verify command, diff and result paths.
2. Run the subagent named in the output with the Agent tool, in the foreground. The task
   message is just those printed lines; the subagent knows its rules.
3. `$D collect --task <slug> --model claude/sonnet` (or `claude/haiku` for a review). It
   prints the same summary/REVIEW block as the normal commands, with the same exit codes.
For a fix round with the fallback, `handoff --brief <fix brief>` replaces `fix`. Try the free
chain again on the next round; it is often back after a few minutes. If the subagents hit the
plan's limits too, stop and tell the user.

## 5. Your final review — the step that matters
Read `~/.delegate/runs/<slug>/diff.patch` fully, plus the REVIEW block. Then:
- Re-run the verification yourself inside the worktree (path in the summary). Never trust a
  model's claim that tests pass. Add one extra check of your own when the change is risky.
- Check against `references/final-review-checklist.md`.
- Treat the reviewer's findings as leads, not verdicts: confirm each against the code.

Then decide:
- **Accept**: `$D accept --task <slug> -m "<conventional commit message>"`, then report the
  merge command it prints and ask the user before merging into their branch.
- **Fix round**: write `~/.delegate/briefs/<slug>-fix<N>.md` from the template's "Fix brief"
  section (the exact problems, file:line, expected behaviour; the implementer starts a fresh
  session and only sees this brief and the worktree), then
  `$D fix --task <slug> --brief <file>` and go back to step 4. At most 3 fix rounds (the
  script enforces it and stops identical repeat failures).
- **Small fix**: if what is left is under ~25 lines, edit the worktree yourself and accept.
- **Abandon**: `$D clean --task <slug> --force` and do it yourself or re-plan.

## 6. Finish
Report per slice: what changed, which models implemented and reviewed it, verification
results, rulings you made on reviewer findings, and anything you fixed by hand. After the user
merges: `$D clean --task <slug>`.

## Other commands
`$D status [slug]` · `$D models [--probe]` · `$D doctor` · `$D handoff` / `$D collect` (fallback)
