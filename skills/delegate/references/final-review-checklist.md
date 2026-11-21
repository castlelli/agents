# Final review checklist (orchestrator)

Run through this on every delegated slice before `accept`.

## Evidence
- [ ] I re-ran the verification command myself in the worktree and it passed.
- [ ] The summary shows no POLICY VIOLATION and no OVERSIZED warning (or I accept why).
- [ ] Every file in the diffstat is in the brief's Files list, or its RESULT explains why.

## Correctness
- [ ] The diff implements every Acceptance item; I can point to the line for each.
- [ ] Edge cases from the brief are handled in code, not only mentioned in RESULT.
- [ ] Error paths: failures are surfaced, not swallowed (`except: pass`, empty catch).
- [ ] No hard-coded paths, hostnames, credentials, or values that belong in config.
- [ ] For data/scientific code: units, dtypes, off-by-one in ranges/coordinates, and NaN /
      empty-input behaviour are right.

## Tests
- [ ] New tests fail without the change (reason it out, or revert a line mentally).
- [ ] No existing test was deleted, skipped, loosened or had its expected value edited
      to match new output.

## Fit
- [ ] Matches surrounding conventions; no unrelated reformatting or renames.
- [ ] No new dependency unless the brief allowed it.
- [ ] Assumptions listed in RESULT are ones I agree with.

## Reviewer findings
- [ ] Each Critical/Major finding is confirmed (fix it) or refuted (note why) — never
      ignored silently.
