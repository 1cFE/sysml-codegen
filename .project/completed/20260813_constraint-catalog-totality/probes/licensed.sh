#!/usr/bin/env bash
# Run a command under the task venv with the syside licence sourced.
#
# The licence lives in the MAIN agentic-mbse checkout, not the worktree; the interpreter
# is the task-specific venv, whose editable install reads the companion WORKTREE. Using
# `uv run` here resolves the wrong companion and the suite does not even collect.
set -euo pipefail
set -a
# shellcheck disable=SC1091
source /home/reid/1cfe/agentic-mbse/.env
set +a
exec /home/reid/1cfe/item7-rebuild-venv/bin/python "$@"
