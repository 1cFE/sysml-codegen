# Staleness Survey — post-CONSTRAINT-EXEC doc surfaces (2026-07-13)

Condensed findings from three survey passes run at spec time (owner session, branches:
`constraint-exec-epic` everywhere, fusion-tea `main`). This is the evidence base for
`spec.md`; the implementing agent should trust-but-spot-check, not re-survey.

## sysml-codegen

**What Item 14's `ccfe9db` already flipped (do not redo):** modeling-assumptions §8
("Constraints Execute Under a Profile"), NEW `reference/28-constraint-lowering-and-catalog.md`,
orchestration step table (2.6 / 5.65 / P1-RESOLVE / P4-CATALOG rows), REQ-EXT-09 re-anchor,
verification-matrix CL family (5 rows; totals 264 rows / 31 families / 71 test files).

**Stale (file:line → wrong claim):**
- `docs/architecture/reference/27-snapshot-generation.md:37` — "Current: **1**"; code is
  `SNAPSHOT_FORMAT_VERSION = 3` (`snapshot/__init__.py:19`). Also `:40-43` format-schema key
  list has no constraint-facts section; `:58-64` + `verification-matrix.md:506` (REQ-SNAP-09)
  still narrate V1/V2 — need v2→v3 migration note.
- `docs/architecture/reference/14-expression-compiler.md` — pervasive `ExpressionAST` /
  `build_expression_ast()` / `compile_expression()` (lines 28-226); those defs no longer exist
  (only `compile_calc_def`/`classify_compilability` remain; IR is `ExpressionIR`, rendering in
  `extraction/calc_compat_renderer.py`).
- `reference/16-computed-attributes.md:15,62,156,157` and `reference/19-ast-dispatch-invariant.md:42,89`
  — same retired symbols. `verification-matrix.md:96` (REQ-AST-06), `:144` (REQ-CA-02) — same
  in requirement text.
- `docs/architecture/overview.md:218` — "29 requirement families"; matrix says 31.

**Gaps (new sections/docs, not corrections):**
- Contracts/sealing entirely undocumented: `ModelContract`/`PackageContract`
  (`contracts/models.py:51,92`), `seal_package` (`contracts/seal.py:57`), `seal` CLI
  (`cli/__init__.py:704,876`) — no reference doc, no matrix family. 28.md §contracts covers
  only the GENERATOR_MISMATCH note.
- `ModuleKind` (`resolution/models.py:161-170`, five values incl. CONSTRAINT /
  REPORT_AGGREGATOR) has ZERO doc hits: `reference/08-generation.md` (render seams),
  `reference/09-data-models.md` (PipelineModule still described via the two retired bool
  flags; ComputationGraph field list omits `constraint_catalog`), `reference/00-pipeline-overview.md`
  (REQ-PIPE-06 line 22 still says "all three module types").
- `overview.md` 7-step narrative has no constraint-lowering phase.

## agentic-mbse

**Already flipped by `d83109a` (do not redo):** `docs/patterns/constraints.md` — three-outcome
profile model, block list w/ reason codes, real-equality band idiom, L4/L6 named diagnostics,
CLI note.

**Stale:**
- `docs/subtype-enumeration-decision-table.md:13-14,18,24,33-35` — still teaches
  `report_dropped_constraints` / `is_droppable_constraint` / "dropped predicates" / "documented
  v2 limitation, revisited by the constraint-execution epic" (epic has landed). constraints.md
  links to it at `:338`, so the flip is undermined by its own reference.
- `modeling_project/MODELING_GUIDE.md:280` — patterns index still: "constraints.md | Constraint
  syntax and prefixes; not executable".

**Gaps:** no durable (`docs/`) coverage of the ConstraintFacts neutral schemas + extraction
(Item 1) or the production `ExpressionIR` (Item 2) — both live only in `.project/` artifacts.

## teax

Essentially current. `docs/evaluation-and-study.md` (added `245f687`, 152 lines) covers
loading/seal verification, both evaluator backends, failure taxonomy, study layer, CLI,
tracking-key note; CLAUDE.md + AGENTS.md pointers in place. One thin gap: the CE-F3
`entry_models` property (`0d606a4`) is not named — `:51` describes typed entry generically.
No doc ever mentioned the removed ToyPlantParams attribute (nothing to retract).

## Explainer prior art (sysml-codegen)

Two generations — do not conflate:
- **Gen 1 (built):** `.project/diagrams/new_pipeline_explainer.html` (268 KB) per
  `.project/active/new-pipeline-explainer/{spec,design,plan}.md`. 4-act narrative, solar_battery
  LCOE spine, 10 step sections, three Act-3 hard-part deep-dives, vanilla-JS machinery
  (ZoomPanController, tier-slot DAG layout, traceUpstream, renderDataPanel, glossary/nav).
  Content updated once (update-plan Phases 1-5, 2026-02-22) but never browser-verified after,
  and now ~2 epics behind HEAD.
- **Gen 2 (brief only):** `.project/active/EXPLAINER_PROMPT.md` — a generation brief for a
  never-built `pipeline_explainer_v2.html`. Rewritten truthful at PIPELINE-TRUTH close (Item
  10, anchored to `pipeline-truth-epic` HEAD, dated Jul 8). Adds L0-L4 depth stack,
  responsibility map, SysML/AST-primitives layer, V1-V11 diagnostics-as-contract, operational
  reality (live vs snapshot), agentic-mbse complement, honest-caveats.
  **Now stale:** caveats still claim "constraints are dropped … no execution path" and
  `resolve_input()` not wired; knows nothing of lowering, module_kind, Kleene modules,
  aggregator, catalog, contracts/sealing, snapshot v3, or the teax study layer.
- Reuse estimate: rendering machinery + 4-act frame ~70-80% reusable; content/data layer
  largely a rewrite. Slot map for the eight constraint-exec artifact areas is in the spec.

## fusion-tea

- `pipeline-walkthrough.html` (repo root, May 1, 9.5 KB) — older consumer-side walkthrough,
  stale twice over. [OWNER] 2026-07-13: pointer/retirement note only.
- `exploration/ife_e2e/study/run_viability_study.py` + `bench_prepare_once.py` still alias
  `module.ToyPlantParams = module.IfePlantParams` — unnecessary since CE-F3 (`teax 0d606a4`);
  retire the alias (or comment it historical).
