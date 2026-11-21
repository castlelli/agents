#!/usr/bin/env bash
# delegate.sh — run OpenCode implementer/reviewer agents in isolated git worktrees
# on behalf of a Claude Code orchestrator. Claude plans and decides; free models
# implement and pre-review; this script owns every git operation.
#
# Subcommands:
#   doctor                                   check tools, agents, network, models file
#   models [--probe]                         show the model chains; --probe sends a tiny prompt to each
#   implement --task SLUG --brief FILE --verify CMD [--repo DIR] [--base REF] [--model ID]
#   fix       --task SLUG --brief FILE [--model ID]
#   review    --task SLUG [--model ID]
#   status    [SLUG]
#   accept    --task SLUG [-m MESSAGE]       commit the worktree on its delegate/<slug> branch
#   clean     --task SLUG [--force] [--purge]
#   handoff   --task SLUG --role implementer|reviewer [--brief FILE]
#             prepare a round for a Claude Code subagent (fallback when the free models are down)
#   collect   --task SLUG --model ID       process what the subagent left (diff, verify, summary)
#
# Exit codes: 0 ok | 1 error | 2 bad usage/brief | 3 no changes | 4 all models unavailable
#             5 all models rate-limited | 6 stalled | 7 policy violation detected | 8 repair limit
#             9 changes made but the verification command failed
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# ---- settings (override with environment variables) --------------------------
DELEGATE_HOME="${DELEGATE_HOME:-$HOME/.delegate}"
DELEGATE_MODELS_FILE="${DELEGATE_MODELS_FILE:-$SKILL_DIR/models.conf}"
DELEGATE_TIMEOUT="${DELEGATE_TIMEOUT:-2400}"            # max seconds per model run
DELEGATE_IDLE_TIMEOUT="${DELEGATE_IDLE_TIMEOUT:-420}"   # kill a run silent for this long
DELEGATE_VERIFY_TIMEOUT="${DELEGATE_VERIFY_TIMEOUT:-900}"
DELEGATE_MAX_ROUNDS="${DELEGATE_MAX_ROUNDS:-3}"         # fix rounds per task
DELEGATE_SLICE_FILES="${DELEGATE_SLICE_FILES:-8}"
DELEGATE_SLICE_LINES="${DELEGATE_SLICE_LINES:-300}"
DELEGATE_FORCE="${DELEGATE_FORCE:-0}"
OPENCODE_BIN="${OPENCODE_BIN:-opencode}"

RUNS="$DELEGATE_HOME/runs"
EXCLUDES="$DELEGATE_HOME/gitignore"   # build/test junk never counted as part of a delegated change
WORKTREES="$DELEGATE_HOME/worktrees"
SHIMS="$DELEGATE_HOME/shims"

die()  { echo "delegate: $1" >&2; exit "${2:-1}"; }
note() { echo "delegate: $*" >&2; }

# ---- helpers -----------------------------------------------------------------
load_models() {
  IMPLEMENTER_MODELS=(); REVIEWER_MODELS=()
  [[ -f "$DELEGATE_MODELS_FILE" ]] || die "models file not found: $DELEGATE_MODELS_FILE"
  # shellcheck disable=SC1090
  source "$DELEGATE_MODELS_FILE"
  [[ ${#IMPLEMENTER_MODELS[@]} -gt 0 ]] || die "IMPLEMENTER_MODELS is empty in $DELEGATE_MODELS_FILE"
  [[ ${#REVIEWER_MODELS[@]} -gt 0 ]] || die "REVIEWER_MODELS is empty in $DELEGATE_MODELS_FILE"
}

check_slug() { [[ "$1" =~ ^[a-z0-9][a-z0-9._-]{0,60}$ ]] || die "task slug must match [a-z0-9][a-z0-9._-]* (got '$1')" 2; }

meta_set() { # meta_set RUN_DIR KEY VALUE
  local f="$1/meta.env" k="$2" v="$3"
  touch "$f"; grep -v "^${k}=" "$f" > "$f.tmp" || true
  printf '%s=%q\n' "$k" "$v" >> "$f.tmp"; mv "$f.tmp" "$f"
}
meta_load() { [[ -f "$1/meta.env" ]] || die "no such task: $(basename "$1")"; # shellcheck disable=SC1091
  source "$1/meta.env"; }

ensure_excludes() {
  mkdir -p "$DELEGATE_HOME"
  [[ -f "$EXCLUDES" ]] || printf '%s\n' '__pycache__/' '*.py[cod]' '.pytest_cache/' '.mypy_cache/' \
    '.ruff_cache/' '.coverage' 'htmlcov/' '.tox/' '.venv/' 'venv/' '*.egg-info/' 'node_modules/' \
    '.ipynb_checkpoints/' '.opencode/' '.DS_Store' > "$EXCLUDES"
}
gitx() { git -c core.excludesFile="$EXCLUDES" "$@"; }

ensure_shims() { # block Slurm/PBS submission for delegated processes (defense in depth)
  mkdir -p "$SHIMS"
  local c
  for c in sbatch srun salloc scancel sbcast scontrol qsub qdel; do
    if [[ ! -x "$SHIMS/$c" ]]; then
      printf '#!/bin/sh\necho "%s: blocked by delegate policy (delegated agents may not submit or manage jobs)" >&2\nexit 126\n' "$c" > "$SHIMS/$c"
      chmod +x "$SHIMS/$c"
    fi
  done
}

# Text the model wrote (all "text" parts of the JSON event stream, in order).
extract_text() { python3 -I - "$1" <<'PY'
import json, sys
out = []
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    line = line.strip()
    if not line.startswith("{"):
        continue
    try:
        ev = json.loads(line)
    except Exception:
        continue
    if ev.get("type") == "text":
        part = ev.get("part") or {}
        t = part.get("text") if isinstance(part, dict) else None
        if t:
            out.append(t)
print("\n".join(out))
PY
}

# Print from the last line starting with "## <HEADER>" to the end (bounded).
block_from() { python3 -I - "$1" "$2" "${3:-80}" <<'PY'
import sys
text = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
head, limit = "## " + sys.argv[2], int(sys.argv[3])
idx = max((i for i, l in enumerate(text) if l.strip().upper().startswith(head)), default=None)
if idx is None:
    print(f"(no '{head}' block found in the model output)")
else:
    blk = text[idx: idx + limit]
    print("\n".join(blk))
    if len(text) - idx > limit:
        print(f"... ({len(text) - idx - limit} more lines in the result file)")
PY
}

# run_agent AGENT MODEL WORKDIR LOGBASE MESSAGE FILE...
# returns 0 ok | 4 unavailable/auth/model error | 5 rate limited | 6 stalled | 1 other error
run_agent() {
  local agent="$1" model="$2" wd="$3" logbase="$4" msg="$5"; shift 5
  local files=() f
  for f in "$@"; do files+=(-f "$f"); done
  local log="$logbase.jsonl" err="$logbase.stderr"
  : > "$log"; : > "$err"
  ensure_shims
  (
    cd "$wd" || exit 1
    export OPENCODE_DISABLE_CLAUDE_CODE=1      # do not load ~/.claude/CLAUDE.md or Claude skills
    export OPENCODE_DISABLE_AUTOUPDATE=1
    export GIT_SSH_COMMAND=false GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false  # no remote git
    export PATH="$SHIMS:$PATH"
    exec "$OPENCODE_BIN" run "$msg" --agent "$agent" -m "$model" --dir "$wd" \
         --format json --title "delegate:$(basename "$logbase")" --auto "${files[@]}" \
         < /dev/null > "$log" 2> "$err"
  ) &
  local pid=$! start now last_size=-1 size last_change
  start=$(date +%s); last_change=$start
  while kill -0 "$pid" 2>/dev/null; do
    sleep 5
    now=$(date +%s)
    size=$(( $(stat -c %s "$log" 2>/dev/null || echo 0) + $(stat -c %s "$err" 2>/dev/null || echo 0) ))
    if [[ "$size" != "$last_size" ]]; then last_size=$size; last_change=$now; fi
    if (( now - start > DELEGATE_TIMEOUT )); then
      note "$model: hit DELEGATE_TIMEOUT (${DELEGATE_TIMEOUT}s), killing"; kill "$pid" 2>/dev/null; sleep 2; kill -9 "$pid" 2>/dev/null
      wait "$pid" 2>/dev/null; return 6
    fi
    if (( DELEGATE_IDLE_TIMEOUT > 0 && now - last_change > DELEGATE_IDLE_TIMEOUT )); then
      note "$model: no output for ${DELEGATE_IDLE_TIMEOUT}s (silent throttle?), killing"; kill "$pid" 2>/dev/null; sleep 2; kill -9 "$pid" 2>/dev/null
      wait "$pid" 2>/dev/null; return 6
    fi
  done
  wait "$pid"; local rc=$?
  local errtext; errtext="$(grep -hiE '"type":"error"|error' "$err" "$log" 2>/dev/null | tail -n 20)"
  if grep -qiE '429|rate.?limit|too many requests|quota|insufficient (credit|balance)|usage limit' <<<"$errtext"; then return 5; fi
  if [[ $rc -ne 0 ]] || [[ -n "$errtext" && -z "$(extract_text "$log")" ]]; then
    if grep -qiE 'model.*not found|unknown model|not available|unauthori[sz]ed|401|403|invalid api key|no provider' <<<"$errtext"; then return 4; fi
    [[ -n "$(extract_text "$log")" ]] && return 0
    return 1
  fi
  return 0
}

# try_chain AGENT WORKDIR LOGPREFIX MESSAGE "MODEL..." -- FILE...   (sets USED_MODEL, LAST_LOG)
try_chain() {
  local agent="$1" wd="$2" prefix="$3" msg="$4"; shift 4
  local models=() files=()
  while [[ $# -gt 0 && "$1" != "--" ]]; do models+=("$1"); shift; done
  [[ "${1:-}" == "--" ]] && shift
  files=("$@")
  local m rc worst=1 i=0 any_rl=0 any_stall=0
  USED_MODEL=""; LAST_LOG=""
  for m in "${models[@]}"; do
    i=$((i+1))
    local lb="$prefix.$i.$(echo "$m" | tr '/:' '__')"
    note "$agent → $m"
    run_agent "$agent" "$m" "$wd" "$lb" "$msg" "${files[@]}"; rc=$?
    LAST_LOG="$lb.jsonl"
    case $rc in
      0) USED_MODEL="$m"; return 0 ;;
      5) any_rl=1; note "$m rate-limited; trying next model" ;;
      6) any_stall=1; note "$m stalled; trying next model" ;;
      4) note "$m unavailable (auth/model id); trying next model" ;;
      *) note "$m failed (rc=$rc); trying next model" ;;
    esac
    worst=$rc
  done
  if (( any_rl )); then return 5; fi
  if (( any_stall )); then return 6; fi
  [[ $worst -eq 4 ]] && return 4
  return 1
}

require_sections() { # require_sections FILE SECTION...
  local f="$1"; shift; local s missing=()
  for s in "$@"; do grep -qiE "^#+ *$s" "$f" || missing+=("$s"); done
  [[ ${#missing[@]} -eq 0 ]] || die "brief $f is missing section(s): ${missing[*]}" 2
}

snapshot_diff() { # snapshot_diff WT BASE OUTDIR → writes diff.patch, diffstat.txt; echoes "files insertions deletions"
  local wt="$1" base="$2" out="$3"
  ensure_excludes
  gitx -C "$wt" add -A >/dev/null 2>&1
  git -C "$wt" diff --cached --binary "$base" > "$out/diff.patch"
  git -C "$wt" diff --cached --stat=120 "$base" > "$out/diffstat.txt"
  local nums; nums="$(git -C "$wt" diff --cached --shortstat "$base")"
  git -C "$wt" reset -q >/dev/null 2>&1
  local files ins del
  files=$(grep -oE '[0-9]+ files? changed' <<<"$nums" | grep -oE '^[0-9]+' || echo 0)
  ins=$(grep -oE '[0-9]+ insertions?' <<<"$nums" | grep -oE '^[0-9]+' || echo 0)
  del=$(grep -oE '[0-9]+ deletions?' <<<"$nums" | grep -oE '^[0-9]+' || echo 0)
  echo "${files:-0} ${ins:-0} ${del:-0}"
}

run_verify() { # run_verify WT CMD LOG → rc
  local wt="$1" cmd="$2" log="$3"
  ( cd "$wt" && timeout "$DELEGATE_VERIFY_TIMEOUT" bash -c "$cmd" ) > "$log" 2>&1
}

integrity_check() { # integrity_check WT EXPECTED_HEAD BRANCH → prints violations
  local wt="$1" expect="$2" branch="$3" v=()
  local head; head="$(git -C "$wt" rev-parse HEAD 2>/dev/null)"
  [[ "$head" == "$expect" ]] || v+=("HEAD moved from ${expect:0:9} to ${head:0:9} (the agent committed, reset or checked out)")
  local cur; cur="$(git -C "$wt" symbolic-ref --short -q HEAD || echo DETACHED)"
  [[ "$cur" == "$branch" ]] || v+=("worktree is on '$cur', expected '$branch'")
  [[ -z "$(git -C "$wt" stash list 2>/dev/null)" ]] || v+=("git stash entries were created")
  printf '%s\n' "${v[@]}"
}

# ---- run one implement/fix round --------------------------------------------
do_round() { # do_round KIND(implement|fix) RUN WT BRIEF MODEL_OVERRIDE
  local kind="$1" run="$2" wt="$3" brief="$4" override="$5"
  meta_load "$run"
  local round=$(( ${ROUNDS:-0} + 1 ))
  local rdir="$run/round-$round"; mkdir -p "$rdir"
  cp "$brief" "$rdir/brief.md"
  local pre_head; pre_head="$(git -C "$wt" rev-parse HEAD)"

  local chain=()
  if [[ -n "$override" ]]; then chain=("$override"); else chain=("${IMPLEMENTER_MODELS[@]}"); fi
  local msg="Execute the attached brief exactly, following your agent instructions. Finish with the '## RESULT' block."
  try_chain implementer "$wt" "$rdir/implementer" "$msg" "${chain[@]}" -- "$rdir/brief.md"
  local rc=$?
  if [[ $rc -ne 0 ]]; then   # a failed round is not counted; its directory is reused by the next try
    meta_set "$run" STATE "failed"
    { echo "# $kind round $round: FAILED (rc=$rc)"; echo "No model completed the brief. Last log: $LAST_LOG"
      echo "Codes: 4 unavailable, 5 rate-limited, 6 stalled, 1 error."
      [[ $rc -eq 4 || $rc -eq 5 || $rc -eq 6 ]] && echo "Fallback: $0 handoff --task $TASK --role implementer"; } | tee "$rdir/summary.md"
    return $rc
  fi
  extract_text "$LAST_LOG" > "$rdir/output.md"
  finish_round "$kind" "$run" "$wt" "$rdir" "$pre_head" "$round" "$USED_MODEL"
}

# finish_round KIND RUN WT RDIR PRE_HEAD ROUND MODEL — diff, verify, integrity, summary (meta loaded)
finish_round() {
  local kind="$1" run="$2" wt="$3" rdir="$4" pre_head="$5" round="$6" used="$7"
  meta_set "$run" ROUNDS "$round"
  meta_set "$run" LAST_ROUND_DIR "$rdir"
  meta_set "$run" IMPLEMENTER_MODEL "$used"
  USED_MODEL="$used"

  local violations; violations="$(integrity_check "$wt" "$pre_head" "$BRANCH")"
  read -r nfiles nins ndel < <(snapshot_diff "$wt" "$BASE_SHA" "$rdir")
  cp "$rdir/diff.patch" "$run/diff.patch"; cp "$rdir/diffstat.txt" "$run/diffstat.txt"

  local vrc=0
  run_verify "$wt" "$VERIFY" "$rdir/verify.log"; vrc=$?
  cp "$rdir/verify.log" "$run/verify.log"
  local vhash; vhash="$(tail -n 40 "$rdir/verify.log" | sed -E 's/[0-9]+(\.[0-9]+)?s\b//g' | sha1sum | cut -c1-12)"
  meta_set "$run" LAST_VERIFY_RC "$vrc"
  meta_set "$run" PREV_VERIFY_HASH "${LAST_VERIFY_HASH:-}"
  meta_set "$run" LAST_VERIFY_HASH "$vhash"

  local oversize=""
  if (( nfiles > DELEGATE_SLICE_FILES || nins > DELEGATE_SLICE_LINES )); then
    oversize="OVERSIZED slice ($nfiles files, +$nins lines; limits $DELEGATE_SLICE_FILES files / $DELEGATE_SLICE_LINES lines) — consider splitting"
  fi
  local state="implemented"; [[ -n "$violations" ]] && state="violation"
  [[ "$nfiles" -eq 0 ]] && state="no-changes"
  meta_set "$run" STATE "$state"

  {
    echo "# $kind round $round — task $TASK"
    echo "model:    $USED_MODEL"
    echo "worktree: $wt  (branch $BRANCH, base ${BASE_SHA:0:9})"
    echo "changes:  $nfiles files, +$nins/-$ndel"
    echo "verify:   \`$VERIFY\` → exit $vrc   (full log: $run/verify.log)"
    [[ -n "$oversize" ]] && echo "WARNING:  $oversize"
    if [[ -n "$violations" ]]; then echo "POLICY VIOLATION:"; sed 's/^/  - /' <<<"$violations"; fi
    echo
    echo "## diffstat"; tail -n 25 "$rdir/diffstat.txt"
    echo
    if [[ $vrc -ne 0 ]]; then echo "## verify tail"; tail -n 25 "$rdir/verify.log"; echo; fi
    block_from "$rdir/output.md" RESULT 45
    echo
    echo "diff:   $run/diff.patch"
    echo "output: $rdir/output.md"
  } > "$rdir/summary.md"
  cp "$rdir/summary.md" "$run/summary.md"
  cat "$rdir/summary.md"
  [[ -n "$violations" ]] && return 7
  [[ "$nfiles" -eq 0 ]] && return 3
  [[ $vrc -ne 0 ]] && return 9
  return 0
}

# ---- subcommands -------------------------------------------------------------
cmd_implement() {
  local task="" brief="" repo="$PWD" base="HEAD" verify="" model=""
  while [[ $# -gt 0 ]]; do case "$1" in
    --task) task="$2"; shift 2 ;; --brief) brief="$2"; shift 2 ;; --repo) repo="$2"; shift 2 ;;
    --base) base="$2"; shift 2 ;; --verify) verify="$2"; shift 2 ;; --model) model="$2"; shift 2 ;;
    *) die "implement: unknown option $1" 2 ;; esac; done
  [[ -n "$task" && -n "$brief" && -n "$verify" ]] || die "implement needs --task, --brief and --verify" 2
  check_slug "$task"; [[ -f "$brief" ]] || die "brief not found: $brief" 2
  require_sections "$brief" Objective Files Steps Acceptance Verification
  load_models
  local root; root="$(git -C "$repo" rev-parse --show-toplevel 2>/dev/null)" || die "not a git repository: $repo" 2
  local run="$RUNS/$task"
  if [[ -f "$run/meta.env" ]] && grep -q '^STATE=cleaned$' "$run/meta.env"; then mv "$run" "$run.old-$(date +%s)"; fi
  [[ -e "$run" ]] && die "task '$task' already exists — use 'fix', or 'clean --task $task' first" 2
  local base_sha; base_sha="$(git -C "$root" rev-parse --verify "$base^{commit}")" || die "bad base ref: $base" 2
  local wt="$WORKTREES/$(basename "$root")/$task" branch="delegate/$task"
  git -C "$root" show-ref --quiet "refs/heads/$branch" && die "branch $branch already exists in $root" 2
  mkdir -p "$run" "$(dirname "$wt")"
  git -C "$root" worktree add -q -b "$branch" "$wt" "$base_sha" || die "git worktree add failed"
  if [[ -x "$root/.delegate/setup.sh" ]]; then
    note "running $root/.delegate/setup.sh in the worktree"
    ( cd "$wt" && DELEGATE_REPO_ROOT="$root" DELEGATE_WORKTREE="$wt" timeout 300 "$root/.delegate/setup.sh" ) > "$run/setup.log" 2>&1 \
      || note "setup.sh failed (see $run/setup.log); continuing"
  fi
  meta_set "$run" TASK "$task";  meta_set "$run" REPO "$root"; meta_set "$run" WT "$wt"
  meta_set "$run" BRANCH "$branch"; meta_set "$run" BASE_SHA "$base_sha"; meta_set "$run" VERIFY "$verify"
  meta_set "$run" ROUNDS 0; meta_set "$run" STATE "created"; meta_set "$run" CREATED "$(date -Iseconds)"
  do_round implement "$run" "$wt" "$brief" "$model"
}

cmd_fix() {
  local task="" brief="" model=""
  while [[ $# -gt 0 ]]; do case "$1" in
    --task) task="$2"; shift 2 ;; --brief) brief="$2"; shift 2 ;; --model) model="$2"; shift 2 ;;
    *) die "fix: unknown option $1" 2 ;; esac; done
  [[ -n "$task" && -n "$brief" ]] || die "fix needs --task and --brief" 2
  [[ -f "$brief" ]] || die "brief not found: $brief" 2
  load_models; local run="$RUNS/$task"; meta_load "$run"
  [[ "$STATE" == "accepted" ]] && die "task already accepted" 2
  local fixes=$(( ROUNDS - 1 ))
  if (( fixes >= DELEGATE_MAX_ROUNDS )) && [[ "$DELEGATE_FORCE" != 1 ]]; then
    die "repair limit reached ($DELEGATE_MAX_ROUNDS fix rounds). Re-plan the slice, do it yourself, or set DELEGATE_FORCE=1" 8
  fi
  if [[ -n "${PREV_VERIFY_HASH:-}" && "${LAST_VERIFY_HASH:-}" == "$PREV_VERIFY_HASH" && "${LAST_VERIFY_RC:-0}" != 0 && "$DELEGATE_FORCE" != 1 ]]; then
    die "the last two rounds failed verification identically — no progress. Rewrite the brief or take over (DELEGATE_FORCE=1 to override)" 8
  fi
  do_round fix "$run" "$WT" "$brief" "$model"
}

cmd_review() {
  local task="" model=""
  while [[ $# -gt 0 ]]; do case "$1" in
    --task) task="$2"; shift 2 ;; --model) model="$2"; shift 2 ;;
    *) die "review: unknown option $1" 2 ;; esac; done
  [[ -n "$task" ]] || die "review needs --task" 2
  load_models; local run="$RUNS/$task"; meta_load "$run"
  [[ -s "$run/diff.patch" ]] || die "no diff to review for '$task'" 3
  local rdir="${LAST_ROUND_DIR:-$run}"
  local n=1; while [[ -e "$rdir/review-$n.md" ]]; do n=$((n+1)); done
  local chain=()
  if [[ -n "$model" ]]; then chain=("$model")
  else  # prefer a different model than the one that wrote the code
    local m; for m in "${REVIEWER_MODELS[@]}"; do [[ "$m" != "${IMPLEMENTER_MODEL:-}" ]] && chain+=("$m"); done
    [[ ${#chain[@]} -eq 0 ]] && chain=("${REVIEWER_MODELS[@]}")
  fi
  local ctx="$rdir/review-context.md"
  build_review_ctx "$run" "$ctx"
  local msg="Review the attached diff against the attached briefs, following your agent instructions. Finish with the '## REVIEW' block."
  try_chain reviewer "$WT" "$rdir/reviewer-$n" "$msg" "${chain[@]}" -- "$ctx" "$run/diff.patch"
  local rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "# review FAILED (rc=$rc) — no reviewer model completed. Last log: $LAST_LOG"
    [[ $rc -eq 4 || $rc -eq 5 || $rc -eq 6 ]] && echo "Fallback: $0 handoff --task $TASK --role reviewer"
    return $rc
  fi
  extract_text "$LAST_LOG" > "$rdir/review-$n.md"
  finish_review "$run" "$rdir" "$n" "$USED_MODEL"
}

# Give the reviewer every brief of this task (original + fixes) and the verify log tail.
build_review_ctx() { # build_review_ctx RUN OUT (meta loaded)
  local run="$1" ctx="$2"
  { echo "# Review context for task $TASK"; echo; echo "Verification command: \`$VERIFY\` (last exit code ${LAST_VERIFY_RC:-?})"; echo
    echo "## Verification log (tail)"; echo '```'; tail -n 60 "$run/verify.log" 2>/dev/null; echo '```'
    local b; for b in "$run"/round-*/brief.md; do echo; echo "## Brief: ${b#"$run"/}"; cat "$b"; done
  } > "$ctx"
}

finish_review() { # finish_review RUN RDIR N MODEL (meta loaded)
  local run="$1" rdir="$2" n="$3"; USED_MODEL="$4"
  cp "$rdir/review-$n.md" "$run/review.md"
  local post; post="$(integrity_check "$WT" "$(git -C "$WT" rev-parse HEAD)" "$BRANCH")"
  ensure_excludes; local dirty; dirty="$(gitx -C "$WT" status --porcelain | wc -l)"
  meta_set "$run" REVIEWER_MODEL "$USED_MODEL"
  echo "# review $n — task $TASK — reviewer $USED_MODEL (implementer ${IMPLEMENTER_MODEL:-?})"
  [[ -n "$post" ]] && { echo "POLICY VIOLATION during review:"; sed 's/^/  - /' <<<"$post"; }
  block_from "$rdir/review-$n.md" REVIEW 70
  echo; echo "full review: $rdir/review-$n.md   (worktree files with uncommitted changes: $dirty)"
}

# ---- fallback: hand a round to a Claude Code subagent ------------------------
# The free models are down (exit 4/5/6). The orchestrator runs a Claude Code subagent
# (delegate-implementer / delegate-reviewer) on the same worktree, then calls `collect`,
# which applies exactly the same diff, verification and integrity checks.
cmd_handoff() {
  local task="" role="" brief=""
  while [[ $# -gt 0 ]]; do case "$1" in
    --task) task="$2"; shift 2 ;; --role) role="$2"; shift 2 ;; --brief) brief="$2"; shift 2 ;;
    *) die "handoff: unknown option $1" 2 ;; esac; done
  [[ -n "$task" && -n "$role" ]] || die "handoff needs --task and --role implementer|reviewer" 2
  local run="$RUNS/$task"; meta_load "$run"
  [[ "$STATE" == "accepted" || "$STATE" == "cleaned" ]] && die "task is $STATE" 2
  case "$role" in
    implementer)
      local round=$(( ${ROUNDS:-0} + 1 )); local rdir="$run/round-$round"; mkdir -p "$rdir"
      if [[ -n "$brief" ]]; then [[ -f "$brief" ]] || die "brief not found: $brief" 2; cp "$brief" "$rdir/brief.md"
      elif [[ ! -f "$rdir/brief.md" ]]; then die "no brief for round $round: pass --brief FILE" 2; fi
      if (( round > 1 )); then   # same limits as `fix`
        if (( round - 1 > DELEGATE_MAX_ROUNDS )) && [[ "$DELEGATE_FORCE" != 1 ]]; then
          die "repair limit reached ($DELEGATE_MAX_ROUNDS fix rounds). Re-plan, do it yourself, or set DELEGATE_FORCE=1" 8
        fi
      fi
      rm -f "$rdir/output.md"
      meta_set "$run" HANDOFF_ROLE implementer; meta_set "$run" HANDOFF_DIR "$rdir"
      meta_set "$run" HANDOFF_HEAD "$(git -C "$WT" rev-parse HEAD)"; meta_set "$run" STATE handoff
      echo "HANDOFF implementer — task $TASK, round $round"
      echo "worktree: $WT"
      echo "brief:    $rdir/brief.md"
      echo "verify:   $VERIFY"
      echo "result:   $rdir/output.md"
      echo "next: run the delegate-implementer subagent with these four paths/commands, then"
      echo "      $0 collect --task $TASK --model claude/sonnet" ;;
    reviewer)
      [[ -s "$run/diff.patch" ]] || die "no diff to review for '$task'" 3
      local rdir="${LAST_ROUND_DIR:-$run}"
      local n=1; while [[ -e "$rdir/review-$n.md" ]]; do n=$((n+1)); done
      build_review_ctx "$run" "$rdir/review-context.md"
      meta_set "$run" HANDOFF_ROLE reviewer; meta_set "$run" HANDOFF_DIR "$rdir"
      meta_set "$run" HANDOFF_N "$n"; meta_set "$run" HANDOFF_HEAD "$(git -C "$WT" rev-parse HEAD)"
      echo "HANDOFF reviewer — task $TASK"
      echo "worktree: $WT"
      echo "context:  $rdir/review-context.md"
      echo "diff:     $run/diff.patch"
      echo "result:   $rdir/review-$n.md"
      echo "next: run the delegate-reviewer subagent with these paths, then"
      echo "      $0 collect --task $TASK --model claude/haiku" ;;
    *) die "--role must be implementer or reviewer" 2 ;;
  esac
}

cmd_collect() {
  local task="" model=""
  while [[ $# -gt 0 ]]; do case "$1" in
    --task) task="$2"; shift 2 ;; --model) model="$2"; shift 2 ;;
    *) die "collect: unknown option $1" 2 ;; esac; done
  [[ -n "$task" && -n "$model" ]] || die "collect needs --task and --model (e.g. claude/sonnet)" 2
  local run="$RUNS/$task"; meta_load "$run"
  [[ -n "${HANDOFF_ROLE:-}" ]] || die "no pending handoff for '$task'" 2
  local role="$HANDOFF_ROLE" rdir="$HANDOFF_DIR"
  meta_set "$run" HANDOFF_ROLE ""
  case "$role" in
    implementer)
      [[ -s "$rdir/output.md" ]] || { note "subagent left no $rdir/output.md"; echo "(no RESULT block written)" > "$rdir/output.md"; }
      local round; round="$(basename "$rdir")"; round="${round#round-}"
      local kind=implement; (( round > 1 )) && kind=fix
      finish_round "$kind" "$run" "$WT" "$rdir" "$HANDOFF_HEAD" "$round" "$model" ;;
    reviewer)
      [[ -s "$rdir/review-$HANDOFF_N.md" ]] || die "subagent left no $rdir/review-$HANDOFF_N.md" 1
      local v; v="$(integrity_check "$WT" "$HANDOFF_HEAD" "$BRANCH")"
      [[ -n "$v" ]] && { echo "POLICY VIOLATION during review:"; sed 's/^/  - /' <<<"$v"; }
      finish_review "$run" "$rdir" "$HANDOFF_N" "$model"
      [[ -n "$v" ]] && return 7; return 0 ;;
  esac
}

cmd_status() {
  local task="${1:-}"
  if [[ -z "$task" ]]; then
    [[ -d "$RUNS" ]] || { echo "no tasks"; return 0; }
    printf '%-28s %-12s %-6s %s\n' TASK STATE ROUNDS IMPLEMENTER
    local d; for d in "$RUNS"/*/; do [[ -f "$d/meta.env" ]] || continue
      ( # shellcheck disable=SC1091
        source "$d/meta.env"; printf '%-28s %-12s %-6s %s\n' "$TASK" "$STATE" "$ROUNDS" "${IMPLEMENTER_MODEL:--}" ); done
    return 0
  fi
  local run="$RUNS/$task"; meta_load "$run"
  echo "task $TASK — state $STATE — rounds $ROUNDS — repo $REPO"
  echo "worktree $WT ($BRANCH, base ${BASE_SHA:0:9}) — verify: $VERIFY"
  [[ -f "$run/summary.md" ]] && { echo; head -n 40 "$run/summary.md"; }
}

cmd_accept() {
  local task="" msg=""
  while [[ $# -gt 0 ]]; do case "$1" in
    --task) task="$2"; shift 2 ;; -m|--message) msg="$2"; shift 2 ;;
    *) die "accept: unknown option $1" 2 ;; esac; done
  [[ -n "$task" ]] || die "accept needs --task" 2
  local run="$RUNS/$task"; meta_load "$run"
  [[ "$STATE" == "accepted" ]] && die "already accepted" 2
  ensure_excludes
  [[ -n "$(gitx -C "$WT" status --porcelain)" ]] || die "nothing to commit in $WT" 3
  [[ -n "$msg" ]] || msg="delegate: $TASK"
  gitx -C "$WT" add -A
  git -C "$WT" commit -q -m "$msg" \
      -m "Delegated-task: $TASK
Implementer-model: ${IMPLEMENTER_MODEL:-unknown}
Reviewer-model: ${REVIEWER_MODEL:-none}
Verified-with: $VERIFY" || die "commit failed"
  local sha; sha="$(git -C "$WT" rev-parse --short HEAD)"
  meta_set "$run" STATE accepted; meta_set "$run" ACCEPT_SHA "$sha"
  echo "committed $sha on $BRANCH"
  echo "merge into your current branch (after the user says so):"
  echo "  git -C $REPO merge --no-ff $BRANCH"
}

cmd_clean() {
  local task="" force=0 purge=0
  while [[ $# -gt 0 ]]; do case "$1" in
    --task) task="$2"; shift 2 ;; --force) force=1; shift ;; --purge) purge=1; shift ;;
    *) die "clean: unknown option $1" 2 ;; esac; done
  [[ -n "$task" ]] || die "clean needs --task" 2
  local run="$RUNS/$task"; meta_load "$run"
  if [[ "$STATE" != "accepted" && $force -ne 1 ]]; then die "task not accepted; pass --force to discard its work" 2; fi
  if [[ "$STATE" == "accepted" ]] && ! git -C "$REPO" merge-base --is-ancestor "$BRANCH" HEAD 2>/dev/null && [[ $force -ne 1 ]]; then
    die "$BRANCH is not merged into $REPO's current branch; pass --force to delete it anyway" 2
  fi
  git -C "$REPO" worktree remove --force "$WT" 2>/dev/null || rm -rf "$WT"
  git -C "$REPO" worktree prune
  git -C "$REPO" branch -D "$BRANCH" >/dev/null 2>&1 || true
  if [[ $purge -eq 1 ]]; then rm -rf "$run"; else meta_set "$run" STATE cleaned; fi
  echo "cleaned $TASK"
}

cmd_models() {
  load_models
  local probe=0; [[ "${1:-}" == "--probe" ]] && probe=1
  local avail; avail="$("$OPENCODE_BIN" models 2>/dev/null)"
  local role m mark
  for role in IMPLEMENTER REVIEWER; do
    echo "$role chain:"
    local -n arr="${role}_MODELS"
    for m in "${arr[@]}"; do
      if grep -qxF "$m" <<<"$avail"; then mark="listed"; else mark="NOT LISTED by 'opencode models'"; fi
      if (( probe )); then
        local tmp; tmp="$(mktemp -d)"
        git -C "$tmp" init -q
        if DELEGATE_TIMEOUT=120 DELEGATE_IDLE_TIMEOUT=90 run_agent reviewer "$m" "$tmp" "$tmp/probe" "Reply with the single word OK."; then
          mark="$mark, probe OK"
        else mark="$mark, probe FAILED (rc=$?)"; fi
        rm -rf "$tmp"
      fi
      printf '  %-55s %s\n' "$m" "$mark"
    done
  done
  echo
  echo "Free models opencode currently reports (cost 0), if any:"
  "$OPENCODE_BIN" models --verbose 2>/dev/null | python3 -I -c '
import sys,re
txt=sys.stdin.read()
for line in txt.splitlines():
    if re.search(r"free", line, re.I) and "/" in line: print("  "+line.strip()[:110])
' | head -n 40
}

cmd_doctor() {
  local ok=1 c
  for c in git python3 "$OPENCODE_BIN" timeout tmux; do
    if command -v "$c" >/dev/null 2>&1; then printf 'ok    %-10s %s\n' "$c" "$(command -v "$c")"
    else printf 'MISSING %s\n' "$c"; ok=0; fi
  done
  "$OPENCODE_BIN" --version 2>/dev/null | sed 's/^/      opencode version: /'
  local a; for a in implementer reviewer; do
    if [[ -f "$HOME/.config/opencode/agents/$a.md" || -f "$HOME/.config/opencode/agent/$a.md" ]]; then echo "ok    agent $a"
    else echo "MISSING agent $a (~/.config/opencode/agents/$a.md)"; ok=0; fi
  done
  [[ -f "$DELEGATE_MODELS_FILE" ]] && echo "ok    models file $DELEGATE_MODELS_FILE" || { echo "MISSING $DELEGATE_MODELS_FILE"; ok=0; }
  local url; for url in https://opencode.ai https://integrate.api.nvidia.com https://api.anthropic.com; do
    if curl -sS -o /dev/null --max-time 10 "$url" 2>/dev/null; then echo "ok    reach $url"; else echo "FAIL  reach $url (no outbound HTTPS from $(hostname)? proxy?)"; fi
  done
  if curl -sS -o /dev/null --max-time 5 -H "Authorization: Bearer ${QWEN_API_KEY:-}" http://127.0.0.1:8000/v1/models 2>/dev/null; then
    echo "ok    self-hosted Qwen answering on 127.0.0.1:8000"
  else echo "info  self-hosted Qwen not reachable on 127.0.0.1:8000 (fine unless qwen-gn03.sh is running on this node)"; fi
  echo "      credentials known to opencode:"; "$OPENCODE_BIN" auth list 2>/dev/null | sed 's/^/        /' | head -n 20
  echo "      DELEGATE_HOME=$DELEGATE_HOME"
  [[ $ok -eq 1 ]] && echo "doctor: OK" || { echo "doctor: problems found"; return 1; }
}

usage() { sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'; }

main() {
  local sub="${1:-}"; shift || true
  case "$sub" in
    implement) cmd_implement "$@" ;; fix) cmd_fix "$@" ;; review) cmd_review "$@" ;;
    status) cmd_status "$@" ;; accept) cmd_accept "$@" ;; clean) cmd_clean "$@" ;;
    models) cmd_models "$@" ;; doctor) cmd_doctor "$@" ;;
    handoff) cmd_handoff "$@" ;; collect) cmd_collect "$@" ;;
    ""|-h|--help|help) usage ;;
    *) die "unknown subcommand '$sub' (try --help)" 2 ;;
  esac
}
main "$@"
