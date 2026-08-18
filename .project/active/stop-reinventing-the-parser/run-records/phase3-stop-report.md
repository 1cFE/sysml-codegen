# Phase 3 stop report — compound unit annotations are refused upstream

**Date:** 2026-08-18
**Branch:** `stop-parser-impl-r2`, worktree `/tmp/stop-parser-rev2/worktrees/sysml-codegen`
**Commit:** `b4e97dd` (one commit on top of `d257ef1`; worktree clean; both user
checkouts and the read-only Agentic worktree untouched at `68bca37`)
**Status:** Phase 3 is **incomplete and halted** on a falsified design premise.

## The blocker

`inspect_reference_uses` in Agentic `0.1.3` refuses any expression whose unit annotation
has a **compound** unit. Measured on the real corpus:

```
CATFMFEShield::catf_shield::gamma_shield::thickness  = 0.04 [m]        -> unit operand is a
                                                                          FeatureReferenceExpression, accepted
CATFMFEShield::catf_shield::gamma_shield::density    = 9400 [kg/m^3]   -> unit operand is an
                                                                          OperatorExpression, REFUSED
```

The refusal is `SemanticEvidenceError(EXPRESSION_KIND_UNSUPPORTED, "unit annotation's unit
operand is not a feature reference")`, which the Codegen boundary converts to a public
`SI_EVIDENCE_INCOMPLETE` and no graph. Any model carrying a compound unit therefore fails
to elaborate at all.

This is not a Phase-2 implementation defect. Phase 2 implemented
`design.md#one-total-inspection-operation` faithfully — *"A structural unit annotation
visits its value operand and validates its shape but never emits the unit operand as a data
reference."* What is false is the design's **premise** that a unit operand is a feature
reference. `[m]` is; `[kg/m^3]` is an `OperatorExpression`, and so is every compound unit.

At `A_base` this could not bite: unit annotations were filtered by document tier and never
structurally validated, so the unit operand's shape was never asserted.

## Blast radius

Compound units are pervasive in exactly the models this product exists to serve. Distinct
forms found under `tests/fixtures/`:

```
[$/MWh] [$/year] [10^19 m^-3] [cm^-1] [kg/m^3] [kg/m³] [kg/s] [m^2] [m^3] [m³/s]
[mm/year] [MWh/year] [MW/m²] [MW·yr/m²] [neutrons/cm²/s] [Pa·m³/s] [particles/s]
[USD/kg] [W/(m·K)]
```

They appear across `catf_mfe_model`, `catf_mfe_d5`, `catf_mfe_gated`, `fusion_tea`,
`feature_metadata_multifile`, and others. Five `test_elaboration_expose_shapes.py` tests
fail on it today; the full-suite figure is not yet measured because the phase halted here.

## Why it was not resolved in place

- The Agentic worktree is **read-only** for this phase and Phase 2 is closed and audited.
- Any Codegen-side accommodation — catching the refusal, pre-unwrapping the annotation,
  or restoring a raw AST unit walk — is precisely the compatibility surface plan rev 3
  forbids ("no wrapper, deprecated alias, manifest exemption, optional semantic path, or
  second resolution mode for any deleted weak surface").
- Capture-fidelity Law 4: genuine surprise produced evidence against a premise the plan
  rests on. Surface it, park dependent conclusions, never resolve it silently.

## What landed and holds

- **The 12 indexed bare-chain red nodes are green** — both cases, all three public arms
  (live / admitted / capture), strict and lenient, asserting
  `code == SI_INDEXED_SOURCE_UNSUPPORTED`, `reference == "cells#(2).mass"`,
  `source_file == "root-0/model.sysml"`, `source_line == 15`, refusal before consumers and
  before `OccurrenceIndex.resolve_address`, and no graph or snapshot bytes. Turned green by
  satisfying the tests; not one assertion was weakened.
- New `elaboration/expression_evidence.py` and `extraction/binding_source.py`; the scoped
  strict gate returns **zero** on both.
- Deletions with no compatibility surface: `SourceReferenceEvidence`, `SourceForm`,
  `screen_source_readiness`, the four `binding_evidence` builders, `annotated_ast_value`,
  `_reject_indexed_sources`, `_expression_references`, `_reference_from_elements`,
  `_UnsupportedExpressionError`, and the dead `SysMLDataExtractor` reconstruction cluster.
- `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py` is **empty**.
- `deep_cross_scope_probe` was never restored to a captured graph.
- The owner-directed PDF-suite exclusion was honored; it was never invoked.

## Two further premise conflicts, surfaced not resolved

1. **The raw-selector manifest cannot go green by deletion.** Phase 1 recorded that Phase 3
   "removes" the ~26 unowned reads. That premise is false for 11 of them: six modules read
   `.operands` on neutral `ExpressionIR` dataclasses (`elaboration/graph.py`,
   `elaboration/project.py`, `extraction/calc_compat_renderer.py`,
   `extraction/modeled_defaults.py`, `generation/predicate_compiler.py`,
   `generation/constraint_name_safety.py`), and five read `.referent` on Codegen's own
   `SourceFile` dataclass (`extraction/source_manifest.py` ×4,
   `orchestration/elaborated_pipeline.py` ×1) — where `referent` is a **serialized snapshot
   key**, so renaming it changes sealed bytes. Phase 2 hit the identical thing on the
   Agentic side and resolved it by scoping the gate to adapter-importing modules
   (deviation 2, audited). That precedent clears the six IR readers; it does **not** clear
   the five `.referent` reads, which sit inside adapter-importing modules.
   `test_discovered_raw_selectors_equal_the_reviewed_manifest` is untouched and still red.

2. **`annotated_ast_value`'s deletion removes a rule with no upstream replacement.** The
   plan directs its deletion because the reference walk no longer needs it. But the
   elaborator's *value-shape* decision also used it, and that is not a dependency walk:
   without the unwrap, `= 0.2 [m]` reads as general math and mints a computed node instead
   of a literal value site. `extract_literal_value` does not cover it (it returns `None`
   for a unit annotation). Resolved in this commit by moving the rule to
   `expression_evidence.unit_annotated_value`, implemented over Agentic's owned
   `materialize_operands` rather than a raw selector — the behaviour is preserved and the
   raw read is gone, but a Codegen-owned AST unit walk still exists, which the design says
   to delete. Recorded for ratification.

## Not done

Ownership manifest completion (Phase-1 Minors 6 and 7), probe-lock Minor 8 and
Informational 12, the dependency pin bump, the new focused constructor / inventory /
deep-path tests, the D1-D4 rerun, and the extraction-based full suite. Phase-1 red node
`test_every_consumer_cell_names_a_proof` remains red and is **deferred to Phase 4** by that
phase's own checklist item, "**Full natural-route matrix:** complete
`tests/conformance/test_expression_evidence_integrity.py` for calculation-definition
dependencies, calculation/constraint bindings, aliases, computed attributes, predicates,
and deep overrides."

## Rollback point

`git reset --hard d257ef1` on `stop-parser-impl-r2`.
