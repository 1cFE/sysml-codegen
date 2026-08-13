#!/usr/bin/env bash
# THROWAWAY (Item 5 design stage). Run a command under the task venv with the syside
# licence sourced. Copied from the Item 2 probes' precedent.
set -euo pipefail
set -a
# shellcheck disable=SC1091
source /home/reid/1cfe/agentic-mbse/.env
set +a
exec /home/reid/1cfe/item7-rebuild-venv/bin/python "$@"
