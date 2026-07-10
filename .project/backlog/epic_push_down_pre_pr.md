# PUSH-DOWN Epic Pre-PR Report

**Date:** 2026-07-08
**Branch:** `push-down-item1-expression`
**Base:** `main`

## Scope

The PUSH-DOWN epic spans two repositories:

- `sysml-codegen`: expression reconstruction shims, qualified-name shim, hierarchy primitive
  delegation, aggregation decomposition delegation, project artifacts, and compatibility tests.
- `agentic-mbse`: shared SysML expression, qualified-name, hierarchy, and aggregation helper modules,
  plus validation/test updates needed by the shared surfaces.

Unrelated untracked files were left untouched:

- `sysml-codegen`: `.claude/projects/`
- `agentic-mbse`: `.project/backlog/epic_command-refresh.md`
- `agentic-mbse`: `.project/research/20260703-112157_command-refresh-from-agentic-project-init.md`

## Mechanical Fixes

Pre-PR formatting found branch-touched files that were not `ruff format` clean. I applied formatter-only
cleanup and committed it separately:

- `sysml-codegen`: `1b72b83 style: format push-down branch files`
- `agentic-mbse`: `48b5274 style: format push-down branch files`

## Validation

`sysml-codegen`:

- `uv run pytest tests/`: `2138 passed, 4 skipped`
- Branch-touched file `ruff check` and `ruff format --check`: clean
- `uv run pytest tests/conformance/test_naming_conventions.py`: `46 passed`
- `git diff -- tests/fixtures`: empty
- `uv run mypy src/`: existing baseline remains `98` errors

`agentic-mbse`:

- `uv run pytest tests/`: `1290 passed, 1 skipped, 33 deselected, 6 warnings`
- Branch-touched file `ruff check` and `ruff format --check`: clean
- `uv run mypy src/`: existing baseline remains `107` errors

Known baseline notes:

- Whole-repo `ruff check src/ tests/` still fails on pre-existing lint debt outside this PR branch.
- Whole-repo `ruff format --check` still reports broader pre-existing formatting debt outside this PR
  branch.
- Mypy remains dirty in both repos at the audited baseline counts above.

## PRs

- `sysml-codegen`: https://github.com/1cFE/sysml-codegen/pull/8
- `agentic-mbse`: https://github.com/1cFE/agentic-mbse/pull/10

---

## Addendum — 2026-07-10 (mypy correction)

This report recorded sysml-codegen mypy at 98 as "existing baseline." That was wrong: main
was 97; the epic introduced +1 (shim/wrapper returns became `Any` — agentic-mbse had no
`py.typed`). The 2026-07-10 remediation added `py.typed` to agentic-mbse, removed the
`TYPE_CHECKING` mirror dataclasses and stale ignores, and fixed a `BindingInfo` annotation
bug the typing surfaced. Post-remediation: sysml-codegen mypy 77; suites 2138/4 and 1290/1;
ruff src clean; fixtures byte-identical.
