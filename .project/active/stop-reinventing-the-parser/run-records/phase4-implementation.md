# Phase 4 implementation record

**Date:** 2026-08-18
**Scope:** Phase 4 only — public-route closure and graph-derived registry authority
**Status:** Implementation complete; independent audit pending

## Identities

| Input / candidate | Identity |
|---|---|
| Codegen Phase 4 base | `1451615609e29b1f511c6b8e69fe425d8afe355e` |
| Codegen candidate | `e5f73e6cff653f5b6a0c3861c0d3d5cd5b2544da` |
| Agentic input, read-only | `3f8bd587af40f05b929dd56645901dada7daea37` |
| TEAx source, read-only | `744745f895677f3344b9884627369a6a47ed987f` |
| Historical Codegen base (`C_base`) | `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6` |
| Historical fixture tree (`P_seed`) | `20f9e60a19b30bc1ec9a27aacb08380f4bc45602` |

The fresh extraction is `/tmp/stop-parser-rev2/phase4-extraction-r2`. Its Codegen archive SHA-256
is `958faea57d23814b45fa298fc83758de2f39f8e2662df6e41ef1ad21a6e5bc4c`; Agentic archive
SHA-256 is `c2924387d6d91360b951d5c9e17386b192148e2d719628feaec38fd41347afb2`; and the Codegen all-ref
bundle SHA-256 is `bc12c00b8a27b2d3ec6c94fda748b082df833cfc6702748119cc9a732b8e123f`.
`artifact-source-inputs.json` records those inputs. `execution-provenance.json` additionally pins the
Phase 3 Agentic wheel
(`d83ca523c85c163a57b0e8d196f2c01b58a383bdb8db88e18826b34453365662`), the TEAx archive
(`3dea651f0b67340a11e28bac61ff1710b3cf20ef8b7ce498172f79c7ca0f8346`), resolved roots, and
Python 3.12.11. These are validation inputs, not Phase 5 artifacts.

## Implementation commits

| Commit | Change |
|---|---|
| `47f2f56238894d78879599617f9ef87465a7f763` | Tests require graph-derived registry authority |
| `348a02e260c575aab79a190d66499c0abf696ab6` | Derive and validate registry wrappers from the graph |
| `68c1ffe714c982887cc8d798a416ba7c875e4e3a` | Close public expression-evidence routes and add A5a/A5b |
| `1ce8638ff62aae4f991890e652fd7ad28a683c28` | Reconcile registry documentation and the deep fixture comment |
| `891923230653b874822148e49ccb5a93e55459d7` | Verify the frozen fixture inventory from Git history |
| `e5f73e6cff653f5b6a0c3861c0d3d5cd5b2544da` | Ledger-own the verification-code transition |

The registry operation now derives a stable, deduplicated wrapper set from the immutable graph. No
root, one root, repeated roots, multiple roots, and unsupported roots are covered through the CLI,
direct generator, and every exported alias. Unsupported input raises typed
`EXIT_POINT_TYPE_UNSUPPORTED` before output mutation. The fifth caller-supplied type-set parameter
and its CLI collector are gone.

The natural-route matrix covers calculation-definition dependencies, calculation and constraint
bindings, aliases, computed attributes, predicates, and deep overrides. It exercises live,
admitted, and capture routes, strict and lenient modes where offered, exact success, indexed
refusal, operand/depth failure, and missing targets. Each expression consumer has both a public
inventory-first proof and a real adapter backstop proof. The Phase 1 deferred node
`test_every_consumer_cell_names_a_proof` is green.

A5a and A5b now record the two measured indexed bare-chain transitions. A5a changes the silently
rewritten singular graph to pre-graph `SI_INDEXED_SOURCE_UNSUPPORTED`. A5b changes both the strict
wrong-name refusal and lenient diagnostic-bearing graph to the same pre-graph refusal, with the
lenient graph absent. `deep_cross_scope_probe` remains the A2 `SI_OCCURRENCE_MISSING` refusal with
the authored reference preserved and no snapshot.

## Recomputable validation

All licensed Codegen commands were run after loading the existing environment with:

```bash
set -a
source /home/reid/1cfe/agentic-mbse/.env
set +a
```

The complete focused Phase 4 selection was:

```bash
uv run --extra dev pytest \
  tests/conformance/test_expression_evidence_integrity.py \
  tests/unit/test_expression_evidence_boundary.py \
  tests/conformance/test_generation_exit_type_preflight.py \
  tests/conformance/test_module_kind_faildloud.py \
  tests/unit/test_registry_generation.py \
  tests/unit/test_hygiene_tail_registry.py \
  tests/conformance/test_elaboration_generation_boundary.py
```

Result: **204 passed**, no skips. Public refusals assert the code, authored reference,
root-relative location, cause, one rendered code token, and unchanged graph/snapshot/output state.

The D1–D4 and retained-harness selection used these 15 paths:

```text
tests/conformance/test_occurrence_domain_derivation.py
tests/conformance/test_occurrence_calc_domain_derivation.py
tests/conformance/test_definition_owned_reference_positions.py
tests/conformance/test_occurrence_multiplicity_authority.py
tests/conformance/test_feature_typing_integrity.py
tests/conformance/test_usage_owned_reference_anchoring.py
tests/conformance/test_elaboration_plural_scope.py
tests/conformance/test_exact_group_identity.py
tests/conformance/test_baselines.py
tests/conformance/test_evidence_artifact_topology.py
tests/unit/test_elaboration_occurrence.py
tests/unit/test_elaboration_containment_address.py
tests/unit/test_elaboration_identity.py
tests/unit/test_occurrence_identity_boundary.py
tests/unit/test_coverage_probes.py
```

Run together with `uv run --extra dev pytest <paths-above>`, they give **163 passed**. The exact
public live/snapshot mutation command
`uv run --extra dev pytest tests/execution/test_occurrence_derivation_mutation_teax.py -m execution`
gives **6 passed**.

The final extraction's default `uv run --extra dev pytest` collected 2,620 nodes, deselected 94,
and returned **2,492 passed, 34 skipped, 94 deselected**, zero failures. The focused Agentic
ownership/reference-use selection returned **58 passed**. The Codegen ownership, transitive
reachability, deleted-cluster, symbol-absence, and registry-authority selection returned **68
passed**. Static closure also confirmed that `_collect_exit_point_wrapper_types` has no references.

```bash
uv run --extra dev mypy --strict \
  src/sysml_codegen/extraction/binding_source.py \
  src/sysml_codegen/elaboration/expression_evidence.py
uv run --extra dev mypy src/
uv run --extra dev ruff check src tests verification scripts
```

Scoped strict mypy returned **Success: no issues found in 2 source files**. Repository-wide mypy
returned the unchanged Phase 3 baseline, **30 errors in 8 files** across 76 source files. The broad
Ruff comparison returned **608 errors**, a pre-existing non-green baseline; targeted Ruff over
every changed Python file returned zero. A broader, non-required strict probe that included
`generation/registry.py` found seven existing missing-generic-parameter diagnostics; it is not
reported as a required gate.

```bash
uv run --extra dev python verification/capture_baseline.py \
  --check --check-current-batch --check-output-transitions
```

Reconciliation returned 14 captured / 23 refused with current batch hash `7f926…` against frozen
`bd7bf…`; 23 metadata-only snapshots; 22 maintained snapshots; and exactly the two named record
transitions, `deep_cross_scope_probe` and `plant_value_shapes`, with their two golden rows. The
historical lock, documentation contract, and snapshot inventory selection returned **30 passed**.

`git diff 78a9beb956f9b5a517c08836b067f0cb0dc4ccc6 -- src/sysml_codegen/elaboration/occurrence.py`
is empty. `git diff --check` passed. Both production
worktrees were clean at their recorded commits. The owner-retired Agentic PDF/HTML suite and paid or
network cases were not run.

## Issues and deviations

The first full extraction at `1ce8638` returned **1 failed, 2,491 passed, 34 skipped, 94
deselected**. The sole failure exposed a validator defect: the frozen fixture manifest names
`P_seed`, but `capture_baseline.py` compared its source hashes with current working-tree bytes. The
required documentation-only fixture comment therefore looked like historical drift. Commit
`8919232` reads the locked inventory from the named Git tree and retains current file-set and
portable-path checks. Because this changes a locked verification file, `e5f73e6` records its old
and new hashes in the transition ledger. The rebuilt final extraction is fully green.

The TEAx command had two setup-only attempts before its six passing tests: first the declared
execution provenance was missing, then the extracted environment lacked `pandas`. The final run
used the checked provenance manifest and third-party dependencies already present in the existing
venvs. No source or product failure occurred, and no dependency was installed or updated.

The Phase 4 brief assumed the indexed-expression and output-alias backlog rows already existed.
They did not. The binding design requires both before close, so Phase 4 files them as `[AGENT]`
rows alongside `[DEEP-QUALIFIED-OUTPUT-WIRING]`; none is marked settled.

There was no product-semantic deviation. Phase 5 was not started. Rollback point:
`1451615609e29b1f511c6b8e69fe425d8afe355e`.
