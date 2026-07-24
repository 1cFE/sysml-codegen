# Item 0 Evidence: Compatible Candidate Pin

**Status:** Complete — local, non-certifying
**Date:** 2026-07-19

## Pinned revisions

| Repository | Revision | Role |
|---|---|---|
| agentic-mbse | `515e08bbcd70aa9d23212765161bd02b3e3d8f23` | PR #11 candidate; merge of local `205debd` and remote `54a95d2` |
| sysml-codegen | `ecdc7285be1508c08e82830c93072306f40e6b34` | PR #9 candidate before Item 0 bookkeeping |
| TEAx | `d545701f575133350474108c96202a2ac5244462` | teax-simkit candidate |
| fusion-tea | `bfff2b4f1712a1c776d1cb9b4f32d01e6917837b` | IFE baseline |
| stellarator consumer | `bceaf40a13941af81f6b5d462d8c373e395b8cf1` | stellarator baseline |

The agentic merge has parents `205debdb5a39449f369ef0ac91c94661fbcfe699` and
`54a95d2ffe18f8e7b437a7f895843e0c89c98c27`. Both ancestry checks pass. The committed
modeling-orchestrator work remains in the candidate by owner direction.

## Versions and locks

| Repository | Package/profile | `uv.lock` SHA-256 |
|---|---|---|
| agentic-mbse | package `0.1.2`; `executable-profile/v4` | `ed48eb993406d6dba1ed1c2a64ff752bf871a283f9157ae41ffcbb9ff7036a4f` |
| sysml-codegen | package `0.1.0`; requires `agentic-mbse>=0.1.2` | `fea88fbb1b4cb2b3aadf27f7511999533bcbb70c841ea928c5399cd7f3be08f2` |
| TEAx | teax-simkit `0.1.0` | `d9b41eef19354cd009448e9bed8317e66a4dd8ba34c8e3fb774f6bf14a22413d` |

## Narrow compatibility evidence

- Agentic merge regression:
  `uv run pytest -q tests/test_constraint_documentation.py tests/test_package_version.py
  tests/test_sysml/test_executable_profile_arithmetic.py
  tests/test_sysml/test_executable_profile_v4.py` — **323 passed**.
- Codegen locked-environment smoke:
  `uv run --frozen python -c <import/version assertions>` — imported agentic-mbse `0.1.2`,
  `executable-profile/v4`, and sysml-codegen `0.1.0`.
- TEAx source import in its existing environment loaded Pydantic `2.13.4`, pandas `3.0.3`, and
  `simkit.evaluation.evaluator` from the pinned checkout.
- The actual `packages/teax-simkit` distribution built successfully as
  `teax_simkit-0.1.0-py3-none-any.whl`; temporary wheel SHA-256
  `fc07fb2ed5ae970d13b46911a318266322c854ec96f529ea51032fdbaeaa8d1f`.

The TEAx workspace-root project is not the teax-simkit distribution and cannot be built by default
setuptools discovery because it contains multiple top-level directories. Item 0 therefore built the
actual package at `packages/teax-simkit`; no product change was needed.

## Production LOC baseline

Counting rule: tracked newline-delimited `*.py`, `*.jinja2`, and lifecycle model `*.sysml` files.
Tests, fixtures, generated output, docs, project artifacts, caches, and result directories are
excluded. Commands use `git ls-files ... | xargs wc -l` at the revisions above.

| Repository | Subsystem | Lines |
|---|---|---:|
| agentic-mbse | constraint facts/profile and shared SysML support | 5,558 |
| agentic-mbse | validation consumers | 3,281 |
| sysml-codegen | extraction and analysis | 8,008 |
| sysml-codegen | resolution, orchestration, and snapshot | 6,612 |
| sysml-codegen | generation and templates | 4,189 |
| sysml-codegen | contracts | 881 |
| TEAx | evaluation | 546 |
| TEAx | study bridge/evidence/store | 1,618 |
| TEAx | shared core/config/I/O | 3,594 |
| fusion-tea | tracked non-generated IFE lifecycle Python/SysML | 2,175 |
| stellarator consumer | tracked non-generated lifecycle Python/SysML | 4,081 |

Later items compare their touched production files against these rows and report tests, fixtures,
generated output, and docs separately.

## Scope statement

This record establishes a local compatible starting set. It does not certify an acceptance cell,
the end-to-end lifecycle, release readiness, or the final PR revisions. No push or PR update was
performed. Items 4, 7, 8, 12, and 13 retain their schema, runtime, catalog, legacy, and composed
proof obligations.
