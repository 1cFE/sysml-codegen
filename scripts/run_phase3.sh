#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache-sysml-codegen}" \
  uv run pytest \
  tests/conformance/test_elaboration_occurrence.py \
  tests/conformance/test_elaboration_projection.py \
  tests/conformance/test_exact_compiler_core.py \
  tests/conformance/test_exact_constraint_route.py \
  -q
