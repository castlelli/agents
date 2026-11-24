#!/usr/bin/env bash
# Run the same command on two revisions and diff what it produces.
#
# Usage: compare.sh <repo> <base-rev> <head-rev> -- '<command>'
#
# Each side gets its own detached worktree and its own empty output directory.
# The command runs inside that output directory through bash -c, with:
#   WT          the worktree root (use "$WT/test/data/..." for repo fixtures)
#   PYTHONPATH  "$WT/lib" prepended
#   PATH        "$WT/bin" prepended
#   PYTHON      $ROTIFER_PYTHON or python3
# Stdout, stderr, the exit code and any files written are compared.
# Nothing is timed. Worktrees are removed afterwards; outputs are kept under
# ${PR_BRIEF_SCRATCH:-${TMPDIR:-/tmp}/pr-brief-$USER}/compare/<base>-<head>/.
set -euo pipefail

if [[ $# -lt 5 || "$4" != "--" ]]; then
  sed -n '2,15p' "$0"; exit 2
fi
repo=$(cd "$1" && pwd); base=$2; head=$3; shift 4; cmd="$*"
b=$(git -C "$repo" rev-parse --short "$base"); h=$(git -C "$repo" rev-parse --short "$head")
scratch=${PR_BRIEF_SCRATCH:-${TMPDIR:-/tmp}/pr-brief-$USER}
root="$scratch/compare/$b-$h"
mkdir -p "$root"
run_id=$(date +%Y%m%d-%H%M%S)
py=${ROTIFER_PYTHON:-python3}

cleanup() {
  for side in base head; do
    [[ -d "$root/wt-$side" ]] && git -C "$repo" worktree remove --force "$root/wt-$side" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT

for side in base head; do
  rev=$([[ $side == base ]] && echo "$base" || echo "$head")
  [[ -d "$root/wt-$side" ]] || git -C "$repo" worktree add --quiet --detach "$root/wt-$side" "$rev"
  out="$root/$run_id/$side"; mkdir -p "$out/files"
  set +e
  ( cd "$out/files" && WT="$root/wt-$side" PYTHON="$py" \
      PYTHONPATH="$root/wt-$side/lib${PYTHONPATH:+:$PYTHONPATH}" PATH="$root/wt-$side/bin:$PATH" \
      bash -c "$cmd" >"$out/stdout" 2>"$out/stderr" )
  echo $? >"$out/exit_code"
  set -e
done

printf '%s\n' "$cmd" >"$root/$run_id/command"
echo "command: $cmd"
echo "base $b exit=$(cat "$root/$run_id/base/exit_code")   head $h exit=$(cat "$root/$run_id/head/exit_code")"
for part in stdout stderr; do
  if cmp -s "$root/$run_id/base/$part" "$root/$run_id/head/$part"; then
    echo "== $part: identical ($(wc -l <"$root/$run_id/base/$part") lines)"
  else
    echo "== $part differs (base vs head, first 60 lines of diff):"
    diff -u --label "base:$part" --label "head:$part" "$root/$run_id/base/$part" "$root/$run_id/head/$part" | head -60 || true
  fi
done
if diff -rq "$root/$run_id/base/files" "$root/$run_id/head/files" >/dev/null; then
  echo "== files written: identical ($(find "$root/$run_id/base/files" -type f | wc -l) files)"
else
  echo "== files written differ:"
  diff -ru "$root/$run_id/base/files" "$root/$run_id/head/files" | head -80 || true
fi
echo "outputs kept in $root/$run_id"
