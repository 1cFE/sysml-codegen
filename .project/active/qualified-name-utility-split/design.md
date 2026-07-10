# Design: Qualified-Name Utility Split

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-08 15:51 PDT
**Branch:** push-down-item1-expression
**Commit:** 810fed3

## Overview

Move the SysML-general qualified-name helpers into `agentic_mbse.sysml.qualified_names` and keep
sysml-codegen's ADR-003 builders local. sysml-codegen keeps its current import paths as permanent
compatibility surfaces, so this is a shared-implementation move, not a generated-name change.

## Related Artifacts

- Spec: `.project/active/qualified-name-utility-split/spec.md`
- Spec review: `.project/active/qualified-name-utility-split/spec-review.md`
- Epic: `.project/backlog/epic_push_down.md`
- Prior item audit: `.project/active/expression-reconstruction-push-down/audit.md`
- Push-down design context: `.project/concepts/agentic-mbse-push-down-design.md`
- Boundary research: `.project/research/20260220-163000_agentic-mbse-boundary-analysis.md`
- Truth-debt context: `.project/completed/20260708_epic_truth_debt.md`
- sysml-codegen source: `src/sysml_codegen/core/qualified_names.py`
- agentic-mbse source: `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py`
- agentic-mbse validation: `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`

## Research Findings

- `src/sysml_codegen/core/qualified_names.py:14` through `:146` contains the shared subset:
  segment sanitization, element qualified-name construction, SysML/Python qualified-name
  conversion, and simple-name extraction.
- `src/sysml_codegen/core/qualified_names.py:97` through `:109` contains codegen-owned ADR-003
  builders for parameter, module, and channel names. `owning_part_leaf` at
  `src/sysml_codegen/core/qualified_names.py:149` is also codegen-owned because it encodes
  EXPOSE_PURE alias/scoping policy.
- `sanitize_qualified_name` already documents the apply-once boundary at
  `src/sysml_codegen/core/qualified_names.py:117`. The move must preserve that exact behavior:
  split a `::` SysML qualified name, sanitize each segment once, and join with `__`.
- `src/sysml_codegen/core/__init__.py:35` re-exports most qualified-name helpers but currently
  omits `sanitize_qualified_name`. The spec calls the core import surface permanent, so the plan
  should pin the existing exports and add `sanitize_qualified_name` only if the implementation
  deliberately chooses to broaden the package-level compatibility surface.
- `agentic_mbse.sysml.__init__` already re-exports the Item 1 expression helpers at
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py:12`. Qualified-name helpers
  should follow that public API pattern.
- agentic-mbse Level 6 already has qualified-name validation in
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py:144`, but it
  uses local format checks rather than the shared sanitizer.
- Existing agentic-mbse backlog row `ITEM-SYNC-C8` waits for a shared sanitizer at
  `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:118`. Item 2 must update that row or
  implement it. Filing a duplicate row would lose the dependency thread.
- sysml-codegen INV-5 coverage lives in `tests/conformance/test_naming_conventions.py:157` and
  `tests/conformance/test_sanitize_invariance.py:144`. Codegen-only naming coverage lives in
  `tests/conformance/test_naming_conventions.py:235`, `:259`, and `:317`.

## Core Concept

The shared system is one small name-normalization library owned by agentic-mbse. It knows how to
turn SysML element names and `::` qualified names into Python-safe identifier segments. sysml-codegen
then composes that shared library with its own ADR-003 naming policy for parameters, modules,
channels, and alias scopes. This keeps the direction of dependency correct: agentic-mbse owns the
SysML facts and optional codegen-compatible profile checks; sysml-codegen owns how those facts become
generated artifacts.

## Key Bets

- **B1.** The six named helpers are SysML-general enough for agentic-mbse and do not carry TEAx or
  codegen artifact policy. *If false -> the shared package would expose codegen behavior and invert
  the push-down boundary.*
- **B2.** Existing generated names are already formed through these helpers, so re-exporting the same
  implementation preserves byte identity. *If false -> baselines change even though this item is
  intended to be a move.*
- **B3.** agentic-mbse Level 6 is the right home for codegen-compatible naming diagnostics.
  *If false -> the checking-profile loop remains late in sysml-codegen and SC-G is not met.*

## Key Decisions

- **D1.** Add a new `agentic_mbse.sysml.qualified_names` module with exactly this public API:
  `sanitize_name`, `build_element_qualified_name`, `sysml_to_python_qualified_name`,
  `sanitize_qualified_name`, `python_to_sysml_qualified_name`, and `extract_simple_name`.
  *Rejected: moving the whole sysml-codegen module, because `build_parameter_qualified_name`,
  `get_module_name`, `get_channel_name`, and `owning_part_leaf` are codegen policy.*
- **D2.** Re-export the new shared API from `agentic_mbse.sysml.__init__`. *Rejected: direct-module
  imports only, because Item 1 established package-level exports for shared SysML helpers and
  hiding this API would make the public surface inconsistent.*
- **D3.** Keep `sysml_codegen.core.qualified_names` as a permanent mixed shim: import/re-export
  shared helpers from agentic-mbse and define the four codegen-only helpers locally. *Rejected:
  moving callers directly to agentic-mbse, because conformance tests and downstream users depend
  on the sysml-codegen import path.*
- **D4.** Keep `sanitize_qualified_name` non-reentrant and document it in both shared and shim
  surfaces. *Rejected: making it idempotent over `__` strings, because that would require a new
  separator parser and would change the current contract.*
- **D5.** Implement or update the `ITEM-SYNC-C8` validation row using the shared sanitizer if the
  Level 6 substrate can gather sibling names cheaply; otherwise update the existing row to
  `Ready - shared sanitizer landed, needs model-wide collision collector`. *Rejected: filing a new
  backlog item, because the existing row is the source of truth for this hazard.*

## Architecture

The target shape has three layers.

1. agentic-mbse shared API:
   `agentic_mbse.sysml.qualified_names` contains the moved implementation and private owner-chain
   helper. It imports only standard-library modules. It must not import sysml-codegen.

2. agentic-mbse public package surface:
   `agentic_mbse.sysml.__init__` imports and includes the six helpers in `__all__`, matching the
   expression helper export pattern from Item 1.

3. sysml-codegen compatibility and local policy:
   `sysml_codegen.core.qualified_names` imports the six shared helpers and keeps local definitions
   for `build_parameter_qualified_name`, `get_module_name`, `get_channel_name`, and
   `owning_part_leaf`. `sysml_codegen.core.__init__` keeps its existing public exports. If
   `sanitize_qualified_name` is added to `sysml_codegen.core`, tests must pin that as an intentional
   compatibility expansion.

The data flow remains unchanged. Extraction and analysis ask sysml-codegen for qualified-name
helpers through the old import path. The shim delegates shared operations to agentic-mbse, and local
builders compose the returned EQNs into PQNs, module names, channels, and alias leaves.

## Required Invariants

- `sanitize_name` returns a non-empty Python identifier and never returns a Python keyword for every
  input shape covered by INV-5.
- `sanitize_qualified_name` accepts a `::`-joined SysML qualified name and is applied exactly once.
  It must not be used on an already `__`-joined EQN.
- `build_element_qualified_name(elem, use_double_underscore=True)` keeps the current default output
  format and owner-chain behavior.
- `sysml_to_python_qualified_name` and `python_to_sysml_qualified_name` remain separator swaps, not
  sanitizers.
- sysml-codegen compatibility exports preserve object identity for moved helpers.
- agentic-mbse must have zero imports of `sysml_codegen`.
- No fixture baseline changes are expected. Any change under `tests/fixtures` is a defect unless a
  reviewer can tie it to an explicit behavior correction outside this item.

## Component Overview

- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py`: shared implementation
  and `__all__` for the six public helpers.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py`: package-level re-export of the
  six helpers.
- `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_qualified_names.py`: moved INV-5 and shared
  qualified-name tests.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`: checking-profile
  integration point for naming hazards.
- `src/sysml_codegen/core/qualified_names.py`: permanent compatibility shim plus local codegen
  builders.
- `src/sysml_codegen/core/__init__.py`: permanent package-level compatibility surface.
- `tests/unit/test_qualified_names_shim.py`: sysml-codegen object-identity and import-path pins.
- `tests/conformance/test_naming_conventions.py`: codegen-only builder tests remain here.

## Checking Profile Disposition

This is the planned close-out profile for implementation. The final implementation notes should
update each row with the actual outcome: `DONE`, `EXISTING`, `NEW RULE`, or `FILED`.

| Helper or hazard | Planned disposition | Design action |
| --- | --- | --- |
| `sanitize_name` | `DONE` | Move implementation and INV-5 tests to agentic-mbse. Use it for profile collision checks. |
| `build_element_qualified_name` | `DONE` | Move implementation and owner-chain tests. Existing profile can use it to derive EQNs from elements. |
| `sysml_to_python_qualified_name` | `DONE` | Move separator-swap tests. No standalone validation rule needed. |
| `sanitize_qualified_name` | `DONE` | Move and add a test proving apply-once/non-reentrant behavior is documented and preserved. |
| `python_to_sysml_qualified_name` | `DONE` | Move round-trip tests. No standalone validation rule needed. |
| `extract_simple_name` | `DONE` | Move simple separator tests. No standalone validation rule needed. |
| Invalid generated identifiers | `EXISTING` plus strengthen | Level 6 already checks malformed qualified names; update it to use shared sanitizer where appropriate. |
| Qualified-name ambiguity | `EXISTING` plus strengthen | Keep current missing/malformed QN checks and add shared helper tests for simple-name extraction ambiguity boundaries. |
| Non-injective sanitization | `NEW RULE` or `FILED` via `ITEM-SYNC-C8` | Prefer building the WARN now with shared `sanitize_name`; if collector scope is too broad, update `ITEM-SYNC-C8` with the remaining collector work and fixture shape. |
| `ITEM-SYNC-C8` | Update existing row | Do not duplicate. Mark implemented if the WARN lands; otherwise change the row from "needs shared sanitizer" to "shared sanitizer landed; needs sibling-name collector". |
| `build_parameter_qualified_name` | Not shared | Keep local to sysml-codegen. No agentic-mbse profile rule because this is PQN construction policy. |
| `get_module_name` | Not shared | Keep local to sysml-codegen. No agentic-mbse profile rule because lowercased module naming is generated-artifact policy. |
| `get_channel_name` | Not shared | Keep local to sysml-codegen. No agentic-mbse profile rule because channel naming is generated-artifact policy. |
| `owning_part_leaf` | Not shared | Keep local to sysml-codegen. No agentic-mbse profile rule because this is alias/scoping policy. |

If `ITEM-SYNC-C8` stays filed, the update must name the rule, fixture shape, severity, and rationale:
WARN on two distinct sibling SysML names that sanitize to the same Python identifier; fixture shape
`'a b'` plus `'a-b'` under one owning namespace; severity `WARNING`; rationale is early modeling
feedback before sysml-codegen's fail-fast duplicate-path error.

## Test Placement

- Move from `tests/conformance/test_naming_conventions.py`: `TestSanitizeName`, `TestEQN`, and
  `TestUtilities` rows for SysML/Python QN conversion and `extract_simple_name`.
- Move from `tests/conformance/test_sanitize_invariance.py`: the no dangerous fixture-corpus
  identifier churn checks for already-safe segments. Keep the fixture scan source in sysml-codegen if
  it depends on `build_pipeline_context_from_snapshot`; otherwise move only the pure segment scan or
  a copied static segment table, and leave registry-collision coverage local.
- Keep in sysml-codegen: `build_parameter_qualified_name`, `get_module_name`, `get_channel_name`,
  key-format, registry-collision, and `owning_part_leaf` tests.
- Add sysml-codegen re-export pins:
  `sysml_codegen.core.qualified_names.sanitize_name is agentic_mbse.sysml.qualified_names.sanitize_name`
  and equivalent identity checks for all six moved helpers.
- Add package-surface pins for `sysml_codegen.core` covering the existing exported helpers. If
  `sanitize_qualified_name` is exported there, pin it explicitly.

## Non-Goals

- No ADR-003 naming redesign.
- No movement of parameter, module, channel, or alias/scoping helpers into agentic-mbse.
- No expression compiler sanitizer changes.
- No item-level PR body or closeout.
- No snapshot recapture unless a failed byte-identity gate proves an existing fixture is stale.

## Implementation Notes

Use the exact shared signatures:

```python
def sanitize_name(name: str | None) -> str: ...
def build_element_qualified_name(elem: object, use_double_underscore: bool = True) -> str: ...
def sysml_to_python_qualified_name(sysml_qname: str) -> str: ...
def sanitize_qualified_name(sysml_qname: str) -> str: ...
def python_to_sysml_qualified_name(python_qname: str) -> str: ...
def extract_simple_name(qualified_path: str) -> str: ...
```

The private `_build_owner_chain_with_packages` can move with `build_element_qualified_name`, but it
must stay private. Do not export it from either repo.

The sysml-codegen shim should keep `__all__` explicit. That makes the split line reviewable and
prevents later helpers from leaking into the wrong package by wildcard import.

## Potential Risks

- A caller may import `sanitize_qualified_name` from `sysml_codegen.core` after implementation if
  it is newly added there. Mitigation: decide in implementation whether this is an intentional
  compatibility expansion and pin the result.
- The moved fixture-corpus test may accidentally import sysml-codegen from agentic-mbse. Mitigation:
  keep fixture scans that require sysml-codegen in sysml-codegen, and move only pure invariant tests.
- The profile WARN could overreach if it compares names across unrelated namespaces. Mitigation:
  scope collision collection to siblings under the same owning namespace and test the negative case.
- Cross-repo editable installs can break midway. Mitigation: land agentic-mbse API and tests first,
  then switch sysml-codegen shims and run both suites before stopping.

## Integration Strategy

Implementation should proceed in the same branch-park pattern as Item 1:

1. Add `agentic_mbse.sysml.qualified_names`, package exports, shared tests, and validation/backlog
   disposition in agentic-mbse.
2. Update the editable dependency in sysml-codegen's environment if needed, then change
   `sysml_codegen.core.qualified_names` to import the shared helpers and keep local builders.
3. Add sysml-codegen shim and local-builder tests.
4. Run both repository validation gates and confirm fixture byte identity.

## Validation Approach

agentic-mbse:

- `uv run pytest tests/test_sysml/test_qualified_names.py`
- Targeted Level 6 tests for any `ITEM-SYNC-C8` implementation or backlog-disposition tests.
- `uv run pytest tests/test_sysml tests/test_quality_gate.py tests/test_check.py` if validation
  surfaces change.
- `uv run ruff check src/agentic_mbse/sysml/qualified_names.py src/agentic_mbse/sysml/__init__.py src/agentic_mbse/validation/level6_architecture.py tests/test_sysml/test_qualified_names.py`
- `rg -n "sysml_codegen" src tests` in agentic-mbse must stay empty.

sysml-codegen:

- `uv run pytest tests/conformance/test_naming_conventions.py tests/conformance/test_sanitize_invariance.py tests/unit/test_qualified_names_shim.py`
- `uv run pytest tests/`
- `uv run pytest tests/snapshot tests/conformance`
- `uv run ruff check src/`
- `uv run mypy src/` may retain the existing baseline count, but moved-helper import errors are not
  acceptable.
- `git diff -- tests/fixtures` must be empty for byte identity.

Byte-identity profile:

- The expected result is no change under `tests/fixtures`.
- If a diff appears, stop and classify it before changing snapshots. This item is a move, so fixture
  churn should be treated as a failed invariant unless proven unrelated.

## Next-Stage Handoff

Treat these as fixed:

- Shared public API is exactly the six named helpers.
- agentic-mbse `sysml.__init__` re-exports the six helpers.
- sysml-codegen keeps permanent compatibility shims and local codegen builders.
- `sanitize_qualified_name` remains apply-once and non-reentrant.
- `ITEM-SYNC-C8` must be updated or implemented, not duplicated.

Open but bounded for implementation:

- Whether `sysml_codegen.core` adds `sanitize_qualified_name` as a package-level export. The
  minimum compatible path is to preserve current exports; adding it is acceptable only with a pin.
- Whether the non-injective sanitization check lands now or remains filed with an updated
  `ITEM-SYNC-C8` row. Prefer implementation if the sibling namespace collector is straightforward.

Risk to de-risk first:

- Add the shared module and identity pins before broader caller edits. If object identity fails,
  the compatibility shim is wrong.

## Next Steps

After approval, proceed to `my-plan` or `my-implement` for PUSH-DOWN Item 2. Do not create
item-level PR guidance; this continues the full PUSH-DOWN epic branch.
