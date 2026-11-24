<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/castelli-on-ink.svg">
    <img src="assets/castelli.svg" alt="castelli" width="220">
  </picture>
</p>

# agents

Skills for ambitious builders.

### Building and reviewing code

- [delegate](skills/delegate/README.md): splits coding work between models by cost.
- [pr-brief](skills/pr-brief/README.md): briefs a reviewer on a pull request they didn't write, then answers questions about it.

### Software design

- [design-patterns](skills/design-patterns/SKILL.md): teaches and applies the 23 Gang of Four design patterns.
- [domain-driven-design](skills/domain-driven-design/SKILL.md): explains DDD from Eric Evans's book and checks modelling decisions against it.

### Studying

- [mock-exam](skills/mock-exam/SKILL.md): turns a sample exam into a timed practice test with commented answers (in Portuguese).
- [poli-integrated-exam](skills/poli-integrated-exam/SKILL.md): writes practice exams for Poli-USP's integrated Calculus II and Linear Algebra II tests (in Portuguese).
- [anki-to-gizmo](skills/anki-to-gizmo/SKILL.md): converts Anki decks into a text file Gizmo can import.

## Install

Each skill's README has its own install steps. As Claude Code plugins:

```bash
claude plugin marketplace add castlelli/agents
claude plugin install pr-brief@castlelli-agents --scope user
```

Or as standalone skills: `npx skills add castlelli/agents --skill pr-brief -a claude-code -g`.
