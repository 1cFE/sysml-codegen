#!/usr/bin/env bash
set -euo pipefail

# Phase 2: Core Infrastructure Spikes — automated plan+build loop
#
# Each task gets two claude invocations:
#   1. PLAN: reads PROMPT-plan.md, produces .project/active/{name}/plan.md
#   2. BUILD: reads PROMPT-build.md, builds from plan
#
# Skips plan if plan.md already exists. Skips build if plan status is DONE.
#
# Usage:
#   ./scripts/run_phase2.sh          # run all 3 tasks
#   ./scripts/run_phase2.sh 2.1      # run only task 2.1
#   ./scripts/run_phase2.sh 2.2 2.3  # run tasks 2.2 and 2.3

PROJECT_DIR="/home/reid/1cfe/sysml-codegen"
DESIGN_DIR="$PROJECT_DIR/.project/concepts/refactor-design-intent"
ACTIVE_DIR="$PROJECT_DIR/.project/active"
LOG_DIR="$PROJECT_DIR/.project/logs/phase2"

PLAN_PROMPT_FILE="$DESIGN_DIR/PROMPT-plan.md"
BUILD_PROMPT_FILE="$DESIGN_DIR/PROMPT-build.md"

mkdir -p "$LOG_DIR"

# ── Phase 2 task definitions ──────────────────────────────────────────
# Format: STEP_ID|COMPONENT_DIR_NAME|TASK_LABEL
TASKS=(
  "2.1|output-registry|Output Registry Spike (C08)"
  "2.2|virtual-binding-rewrite|Virtual Binding Rewrite Spike (C09)"
  "2.3|aggregation-scoping|Aggregation Scoping Spike (C10)"
)

# ── Filter tasks if args provided ─────────────────────────────────────
if [[ $# -gt 0 ]]; then
  FILTERED=()
  for arg in "$@"; do
    for task in "${TASKS[@]}"; do
      step_id="${task%%|*}"
      if [[ "$step_id" == "$arg" ]]; then
        FILTERED+=("$task")
      fi
    done
  done
  TASKS=("${FILTERED[@]}")
fi

echo "═══════════════════════════════════════════════════════"
echo "  Phase 2: Core Infrastructure Spikes"
echo "  Tasks to run: ${#TASKS[@]}"
echo "═══════════════════════════════════════════════════════"
echo ""

for task in "${TASKS[@]}"; do
  IFS='|' read -r STEP_ID COMPONENT_NAME TASK_LABEL <<< "$task"

  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  PLAN_LOG="$LOG_DIR/${STEP_ID}_plan_${TIMESTAMP}.log"
  BUILD_LOG="$LOG_DIR/${STEP_ID}_build_${TIMESTAMP}.log"
  PLAN_PATH="$ACTIVE_DIR/$COMPONENT_NAME/plan.md"

  echo "───────────────────────────────────────────────────────"
  echo "  Step $STEP_ID — $TASK_LABEL"
  echo "  Component dir: $COMPONENT_NAME"
  echo "───────────────────────────────────────────────────────"

  # ── PLAN phase (skip if plan already exists) ─────────────────────
  if [[ -f "$PLAN_PATH" ]]; then
    echo ""
    echo "  [1/2] PLAN: already exists — skipping."
    echo "         $PLAN_PATH"
  else
    echo ""
    echo "  [1/2] PLAN: generating plan..."
    echo "         Log: $PLAN_LOG"

    PLAN_PROMPT="$(cat "$PLAN_PROMPT_FILE")

**$STEP_ID — $TASK_LABEL**

**IMPORTANT**: The plan file MUST be saved to exactly this path: \`.project/active/$COMPONENT_NAME/plan.md\`
Do NOT use a different directory name. Create the directory \`.project/active/$COMPONENT_NAME/\` if it doesn't exist."

    cd "$PROJECT_DIR"
    claude --dangerously-skip-permissions -p "$PLAN_PROMPT" \
      2>&1 | tee "$PLAN_LOG"

    # Verify plan was created at expected path; auto-fix if misnamed
    if [[ ! -f "$PLAN_PATH" ]]; then
      echo ""
      echo "  WARNING: Plan not at expected path: $PLAN_PATH"
      echo "  Searching for recently created plan files..."

      FOUND_PLAN=$(find "$ACTIVE_DIR" -name "plan.md" -newer "$PLAN_LOG" -type f 2>/dev/null | head -1)

      if [[ -n "$FOUND_PLAN" ]]; then
        FOUND_DIR=$(basename "$(dirname "$FOUND_PLAN")")
        echo "  Found: $FOUND_PLAN"
        mv "$ACTIVE_DIR/$FOUND_DIR" "$ACTIVE_DIR/$COMPONENT_NAME"
        echo "  Renamed: $FOUND_DIR -> $COMPONENT_NAME"
      else
        echo "  No new plan.md found. Aborting step $STEP_ID."
        exit 1
      fi
    fi

    echo "  Plan created: $PLAN_PATH"
  fi
  echo ""

  # ── BUILD phase (skip if plan status is DONE) ───────────────────
  if grep -q '^\*\*Status\*\*:.*DONE' "$PLAN_PATH" 2>/dev/null; then
    echo "  [2/2] BUILD: plan status is DONE — skipping."
  else
    echo "  [2/2] BUILD: implementing from plan..."
    echo "         Log: $BUILD_LOG"

    BUILD_PROMPT="$(cat "$BUILD_PROMPT_FILE")

**Component**: \`$COMPONENT_NAME\` (plan at \`.project/active/$COMPONENT_NAME/plan.md\`)"

    cd "$PROJECT_DIR"
    claude --dangerously-skip-permissions -p "$BUILD_PROMPT" \
      2>&1 | tee "$BUILD_LOG"

    echo ""
    echo "  Step $STEP_ID build complete."
  fi
  echo ""

  # ── Quick health check ──────────────────────────────────────────
  echo "  Running test suite health check..."
  cd "$PROJECT_DIR"
  if uv run pytest tests/ -x -q --tb=line 2>&1 | tail -5; then
    echo "  Tests healthy."
  else
    echo ""
    echo "  WARNING: Test suite has failures after step $STEP_ID."
    echo "  Review build log: $BUILD_LOG"
    read -rp "  Continue to next task? [y/N]: " CONTINUE
    if [[ "${CONTINUE:-N}" != [yY] ]]; then
      echo "  Stopping. Fix issues and re-run: ./scripts/run_phase2.sh ${STEP_ID}"
      exit 1
    fi
  fi

  echo ""
done

echo "═══════════════════════════════════════════════════════"
echo "  Phase 2 complete."
echo "  Logs: $LOG_DIR/"
echo "═══════════════════════════════════════════════════════"
