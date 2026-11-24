# Brief template

The brief is short: a reviewer should take it in at a glance. Two sections, about 15–30 lines in all, whatever the PR's size. Translate the headings into the chosen language. Everything else you gathered (test commands, pipelines, runtime, mechanical hunks, what wasn't checked) stays ready for follow-up questions, not in the brief.

```markdown
# PR #<N>: <title>
<author handle without @> · <open/merged/draft> · <real: +a/−d in n files> · <mechanical: +a/−d, checked> · <Closes/Refs #…>

## What was done and how
- <one line per change: what the author did, then how, neutral> (`file:line`)
- …

## What changes
- <one line per behaviour difference a user of the code would see: before → after> (`file:line` or example output)
- <side effects the PR doesn't mention, if any: "Not mentioned in the PR: …">
- <callers/commands reached, in one line: "Reaches: …" or "No bin/ command reaches it.">
- <⚠ runtime alert, only if signals apply, one line>

Ask me for: ways to test it · affected pipelines · runtime as reported · <what couldn't be checked, if anything>
```

Rules for staying short:
- One line per item. Merge changes that share a cause. If a PR has more than ~8 changes, group them by module and say "N more in <module>" rather than listing each.
- Cite with a `file:line` or a short SHA in parentheses, not prose.
- No preamble, no restating the PR title, no closing summary.
- The last line always offers the details, and names anything that could not be checked so the gap is visible without taking space.
