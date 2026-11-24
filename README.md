<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/castelli-on-ink.svg">
    <img src="assets/castelli.svg" alt="castelli" width="220">
  </picture>
</p>

# agents

Skills for ambitious builders.

- [delegate](skills/delegate/README.md): splits coding work between models by cost.
- [pr-brief](skills/pr-brief/README.md): briefs a reviewer on a pull request they didn't write, then answers questions about it.

## Install

Each skill's README has its own install steps. As Claude Code plugins:

```bash
claude plugin marketplace add castlelli/agents
claude plugin install pr-brief@castlelli-agents --scope user
```

Or as standalone skills: `npx skills add castlelli/agents --skill pr-brief -a claude-code -g`.
