# Brief: <slug> — <one-line title>

<!-- The implementer sees ONLY this file and the repository. Write it for a capable
engineer who has never seen this codebase or this conversation. Delete these comments. -->

## Objective
<What must be true when this is done, and why, in 2-4 sentences. The behaviour, not the method.>

## Context
- Read first: `<path>` (<why: the pattern to copy, the function being changed>)
- Existing example to imitate: `<path>:<symbol>`
- Relevant facts the code does not make obvious: <units, invariants, data formats, gotchas>

## Files
Modify:
- `<path>`
Create:
- `<path>`
Do not touch anything else.

## Constraints
- Language/runtime version: <e.g. Python 3.11, no new dependencies>
- Public interfaces that must not change: <signatures>
- Style: follow the surrounding code; <project-specific rule if any>
- Do not read, open or screenshot any image or binary file.

## Steps
1. <Concrete step. Name the function/class and the exact signature when one is new:
   `def parse_record(line: str) -> Record | None`>
2. <...>
3. Add tests in `<test path>` covering: <case 1>, <case 2>, <edge case>.

## Acceptance
- [ ] <observable behaviour 1>
- [ ] <edge case behaviour>
- [ ] Existing tests in `<path>` still pass, unmodified.

## Verification
```
<the exact command, runnable from the repo root, no job submission>
```
Expected: exit code 0.

## Out of scope
- <things a helpful model might "improve" that you do not want touched>

---

# Fix brief template (for `delegate.sh fix`)

The implementer starts a FRESH session for each fix round: it does not remember the first
round. It sees only this fix brief and the worktree, which already contains the previous
round's changes.

## Objective
Fix the problems below in the existing changes for task <slug>. The original goal was:
<one-sentence restatement of the original Objective>.

## Context
The worktree already contains an implementation of <feature>. Keep everything that is not
listed below.

## Files
Modify: `<only the files that need fixing>`

## Steps
1. `<path>:<line>` — <the problem> — <the expected behaviour / exact fix>
2. ...

## Acceptance
- [ ] Each problem above is resolved.
- [ ] Nothing outside these fixes changes.

## Verification
```
<same command as the original brief, or a narrower one>
```

## Out of scope
- Any refactor or change not listed above.
