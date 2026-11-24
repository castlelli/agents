<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/castelli-on-ink.svg">
    <img src="assets/castelli.svg" alt="castelli" width="220">
  </picture>
</p>

# agents

Skills I use in day-to-day building.

- [delegate](#delegate): splits coding work between models by cost.
- [pr-brief](skills/pr-brief/README.md): briefs a reviewer on a pull request they didn't write, then answers questions about it.

## delegate

`/delegate` splits coding work between models by cost. Claude Code (Opus) plans the task and reviews the result at the end. Free models do the typing in between: Kimi, DeepSeek, Nemotron, Mistral and others, running headless through [OpenCode](https://opencode.ai).

One task goes like this:

1. Opus reads the code and writes a brief: objective, files, constraints, steps, acceptance criteria, one verification command.
2. `delegate.sh` creates a git worktree and hands the brief to the first free model in the chain. If that model is rate-limited, down or silent for 7 minutes, the script moves to the next one.
3. The script runs the verification command itself. A model saying "tests pass" counts for nothing.
4. A free model from a different family reviews the diff, read-only.
5. Opus reads the diff and the review, runs the tests again, and accepts, writes a fix brief (at most 3 rounds), or drops the task.

If every free model is down, the same steps run with Claude subagents: Sonnet implements and Haiku reviews.

### What the models cannot do

The script owns git. Agents cannot commit, stash, push or switch branches. If an agent touches git anyway, the run stops with exit code 7 and the orchestrator has to show it to you. The OpenCode agent permissions, and a hook (`agent-guard.py`) for the Claude fallback, block git, network access, `sudo`, file deletion and reading `.env` files. Shims put `sbatch`, `srun`, `scancel` and the rest ahead of the real ones on `PATH`, so an agent cannot submit jobs to the cluster.

### What each task leaves behind

`~/.delegate/runs/<task>/` keeps the brief, the model that wrote the code, the model that reviewed it, the base commit, the diff, the verification log and the review. You can tell who changed what, against which commit, and whether the tests really passed.

### Install

Requirements: Claude Code, [OpenCode](https://opencode.ai), git and bash. An NVIDIA developer key (`NVIDIA_API_KEY`) and a Google AI Studio key from a project with no billing (`GEMINI_API_KEY`) add more free models. Both are optional, and OpenCode Zen's free models work without either.

```bash
cp -r skills/delegate ~/.claude/skills/
cp skills/delegate/subagents/*.md ~/.claude/agents/
mkdir -p ~/.config/opencode/agents
cp skills/delegate/opencode/agents/*.md ~/.config/opencode/agents/
# merge skills/delegate/opencode/opencode.example.json into ~/.config/opencode/opencode.json
~/.claude/skills/delegate/scripts/delegate.sh doctor
```

Then, in Claude Code: `/delegate <task, or a path to a plan>`.

Free tiers change every few weeks. `delegate.sh models --probe` shows which models in `models.conf` still answer. Check a provider's pricing page before adding a model to the chain.
