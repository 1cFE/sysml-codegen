# Design: Repeated computed attributes register one class per definition

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-25
**Branch:** `repeated-rollup-collision` (design written at `645193d3`)
**Complexity:** MEDIUM

---

## Overview

Several copies of a part definition whose own value is computed (a formula or a rollup) should share one generated class, registered once, with one pipeline entry per copy. Today the registry registers that class once per copy and refuses the model. This design makes the registry treat formula and rollup classes the way it already treats calc-def classes, and settles at projection the one case where copies cannot share a class.

## Related Artifacts

- **Spec:** `.project/active/repeated-rollup-collision/spec.md` (the contract)
- **Product lens:** `.project/active/repeated-rollup-collision/product-lens.md` (spec-F1 to F4 disposed)
- **Brief:** `.project/active/repeated-rollup-collision/briefs/design.md`
- **Reproducers:** `.project/active/repeated-rollup-collision/repro/`
- **Backlog:** `.project/backlog/BACKLOG.md` `[REPEATED-ROLLUP-REGISTRY-COLLISION]`; related `[SC11-IMPORT-REWRITE]` (`:271`) and `[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]` (`:41`)
- **ADRs:** 0009 (compute identifiers once), 0011 (typed graph projection)

## The Point

[OWNER-VERBATIM] 2026-10-25: "yes file it and orchestrate a fix in sysml-codegen". The ordinary costing shape, several identical racks each summing its own servers, must check, generate and compute the right numbers. Each copy keeps its own inputs, its own output channel and its own pipeline entry, and values are never merged across copies (`[HARD]`, ADR 0011, `docs/architecture/modeling-assumptions.md` §6). A genuine collision between two different classes still refuses before anything is written (`[HARD]`, REQ-REG-08). Refusing a well-formed model is not an acceptable answer to this defect (product 0003; product-lens spec-F1).

## Research Findings

What I ran, all in the scratchpad, no `src/` change. Probes monkeypatched the generator and ran the packages in real TEAx through dc3's venv (`/home/reid/src/dc3/.venv/bin/python`, `simkit` from `/home/reid/src/teax`), using `tests/execution/real_teax.py:execute_sealed_package` and the `PreparedEvaluator` harness from `tests/execution/test_occurrence_derivation_mutation_teax.py:105`.

- **Copies of one definition feature already produce the same class.** With the collision check disabled, `repro/two` writes `modules/p/top/sub_0/capital_cost.py` and `sub_1/capital_cost.py`. They differ only in three lines that name their own file path (docstring, the handwritten import, the stencil's import). Input field names are positional (`capital_cost_0..2`), not occurrence keys; the pipeline entry maps them to each copy's keys.
- **TEAx refuses a module type registered twice.** With both copies registered (collision check disabled, alias dropped by hand), the package raises `Duplicate module_type 'p.sub.capital_costModule'` at registry build. So "register once" is required by the runtime, not just tidier.
- **The alias import rewrite is broken for rollups, today, with one copy.** `_resolve_class_name_collisions` (`registry.py:110-118`) finds the import to alias by checking that the module type's prefix (`p.sub`) is a substring of the import line. A rollup's import path is the occurrence path (`modules.p.top.a.capital_cost`), so the prefix only matches by accident (`p.top.sub_0` happens to contain `p.sub`). I built a one-copy model (`Top { part a : Sub; capital_cost = a.capital_cost + extra; }`, Sub sums three leaves) with the stock generator. It passes `check` and `generate`, and the package fails to import: `NameError: name 'Sub_capital_costModule' is not defined`. This is the defect `[SC11-IMPORT-REWRITE]` names. Once rollup classes are deduplicated, a rollup class and a parent formula class share a class name in every repeated model, so this fix is required for the spec's named-parts criterion.
- **Only the arity case has differing classes.** Comparing each copy's module with its occurrence fields removed (`name`, `execution_order`, each input's `source`, each output's `channel_name`): `repro/arity` has two signatures under `p.sub.capital_costModule` (3 and 2 inputs). `repro/nested` and `unresolvable_attr_probe` have one per module type.
- **A prototype of this design builds and computes every spec case.** Values in real TEAx: `two` 60 with each copy 30; `two` with `sub_1.leaf_0` set to 20 gives `sub[1]` 40, `sub[0]` 30, total 70; `named` 60; `nested` 120 (rows 60, racks 30); `named_total` 60; `leafformula` 30; `arity` 50 (a 30, b 20); the one-copy named model above 35; `unresolvable_attr_probe` builds and runs.
- **Byte identity holds.** With the prototype loaded as a pytest plugin, `tests/conformance/test_public_package_oracle.py` and `test_public_route_baselines.py` pass except `unresolvable_attr_probe`, which turns from refused to built (expected). Full default-suite result is in Appendix A.
- **A second committed fixture hits this defect.** `tests/fixtures/elab_native_plural_scope` (two copies of `BaseContainer`, one retyped to `SpecializedContainer`, each summing its leaves) is stored as refusing with `REGISTRY_CLASS_NAME_COLLISION` in `tests/expectations/refusal_cases/fixture_classes.json:307`. The spec's search of the refusal corpus missed it because it is a fixture class, not a refusal case. Under the prototype it builds and runs: `selected.total` 14.0 (two leaves at 7.0), `shadow.total` 4.0 (two at 2.0), which matches the model.

Code read: `generation/registry.py` (whole file), `cli/prepare.py:233-470`, `cli/emit.py:246-360`, `elaboration/project.py:275-330`, `:379-386`, `:865-975`, `:1216-1227`, `core/identifier_types.py:114-200`, `resolution/models.py:160-240`, the pins listed in the spec.

## Core Concept

A generated class is identified by its module type. One module type must mean one class body, and the registry registers each module type once. Calc defs already work this way. Formula and rollup modules break it in two places: the registry emits one entry per copy, and nothing guarantees that copies under one module type have the same class body.

The fix has two halves. Projection settles identity: after it builds the computed modules, it checks that all copies under one module type have the same class signature (the module with its occurrence fields removed). If they do, nothing changes. If they don't, every copy in that group takes its own module type, derived from its occurrence path, as if it were the only copy. Generation then looks up: for formula and rollup modules it writes and registers one class per module type, from the first copy by module name, and builds each import line from the entry it belongs to instead of searching for it.

Why this is right: identity stays where ADR 0009 puts it (projection), the registry gains one rule rather than a rollup special case, and the runtime already maps each copy's inputs through its own pipeline entry, so sharing the class costs nothing in separation.

## Key Bets

- **B1.** Two computed modules with equal class signatures render to the same class, apart from the lines that name the class's own file. *If false → the shared class could carry one copy's behaviour into another copy's entry.* Evidence: the `sub_0`/`sub_1` diff above; the signature includes every field the module template reads except `name`.
- **B2.** TEAx keys a module on its pipeline entry, so one registered class serves many entries with separate inputs and outputs. *If false → copies would merge values.* Evidence: the `sub_1.leaf_0` mutation run above; calc defs already rely on this.
- **B3.** Copies that differ in shape are rare and flat in real models (one named copy overriding a multiplicity). *If false → the per-copy fallback hits the parent-segment alias limit (D3) often, and refusals return for valid models.*

## Key Decisions

- **D1. Formula and rollup modules get one registry entry per module type.** The rule lives in one helper that returns the modules that own a generated class: every module, except that formula and rollup modules are reduced to the first copy (by module name) of each module type. The registry, the module writer, the stencil writer and the duplicate-path check all use it. *Rejected: one entry per module type for every kind, calc defs included (it would also change `[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]`, which the spec puts out of scope; the calc-def pass at `registry.py:169-178` and `:295-306` is left exactly as it is).*
- **D2. The shared class file lives at its first copy's path.** For one copy that is its current path, so single-copy output is unchanged. For `Sub[2]` it is `modules/p/top/sub_0/capital_cost.py`, and no `sub_1` file is written. Formula modules already use one definition path and keep it. `[AGENT]` *Rejected: the definition path (`modules/p/sub/capital_cost.py`) when there are several copies (a second path rule, and a new way to collide with an occurrence path such as a top-level `part sub`); one file per copy registered once (spec forbids it unless the files cannot drift, and the self-path lines already differ).*
- **D3. Copies that differ in shape build, each with its own module type.** `[AGENT]` The arity case is a valid model (§6: non-uniform arrays are a normal shape), so it builds. When the copies under one module type do not all share one signature, projection gives every copy in that group the module type of its occurrence path (`p.top.b.capital_costModule`, the same path its rollup file already uses), and no class is shared in that group. The whole group goes per-copy, not just the odd one out, so no copy is privileged and the rule does not depend on which copy matches the definition. Known limit: if two such copies have the same parent name under different grandparents (`top.x.a` and `top.y.a`), their aliases collide and REQ-REG-08 refuses, naming both module types. I reproduced this. It is the existing alias limit, which the spec keeps out of scope; the plan files a backlog row for it. *Rejected: refuse every arity divergence (refuses the flat case the spec asks to build); a numbered second identity such as `capital_cost_2Module` (a name-mangling rule with no meaning to the modeller).*
- **D4. Identity is settled over the whole projection, before target selection.** The check runs at the end of `_build_calculation_modules` (`project.py:865`) on `modules_by_semantic`, which both `run()` and `select()` read. So selecting only `b` cannot give it a different module type from the full build. `[AGENT]`
- **D5. The class signature is defined once, beside `PipelineModule`.** A function in `resolution/models.py` returns the module with `name`, `execution_order`, `module_type`, input sources and output channel names removed. Projection uses it to settle identity; the registry preflight uses it as a backstop. *Rejected: comparing rendered file text (a generation-time re-derivation of an identity decision, against ADR 0009).*
- **D6. Each registry entry carries its import module, and import lines are rendered from the entries after aliasing.** This replaces the substring search at `registry.py:110-118`. Calc-def, formula, rollup and constraint import paths are derived exactly as today, and imports keep today's order (four groups, each sorted), so unaffected packages stay byte-identical. The prototype confirmed byte identity with an exact-line alias match rather than full rendering from entries, so phase 2 re-checks it. This also closes `[SC11-IMPORT-REWRITE]`, which was sized as "not small, cross-module AST rework". The change needed here is local to `registry.py`, because the entry already knows its path. `[AGENT]` *Rejected: keeping the substring search and adding a rollup branch (keeps the first-match defect for every other case).*
- **D7. The registry preflight also refuses a module type whose owners disagree on signature.** After D3 this can only happen if a per-copy module type meets an existing one, or if two definitions differ only in letter case. It reports as `REGISTRY_CLASS_NAME_COLLISION` from the existing preflight site (`prepare.py:439-458`), so there is no new refusal code. `[AGENT]` *Rejected: a new projection diagnostic (a new refusal site and site-account rows, for a case no reproducer reaches).*

## Architecture

```
project.py  _build_calculation_modules ──► settle identities (D3, D4)
                                         uses class_signature (D5)
                 │ ComputationGraph: every module has its final module_type
                 ▼
prepare.py  _check_duplicate_output_paths(class owners)   ─┐
            _preflight_registry_class_names  (+ D7)        │  all before any write
                 ▼                                          │
emit.py     _generate_modules / _generate_stencils(class owners)
            _generate_pipeline(all modules: one entry per copy, unchanged)
            _generate_registry ──► registry entries (D1, D6) ──► __init__.py
```

The pipeline YAML, schemas, inputs and model contract still iterate every module, so each copy keeps its own entry, input keys and output channel. Only the three per-class writers (module file, stencil, registry entry) iterate class owners.

## Required Invariants

- **I1.** After projection, all formula and rollup modules sharing a module type have equal class signatures.
- **I2.** In every built package, each module type named in `pipelines/*.yaml` is registered exactly once in `__init__.py`, and the registered class's input fields equal the input names of every pipeline entry that uses it (the spec's default-suite criterion).
- **I3.** A model with one occurrence of each definition generates byte-identical output (public baselines unchanged apart from `unresolvable_attr_probe`).
- **I4.** A residual collision between different module types refuses before the output tree is touched (REQ-REG-08; `refusal_cases/output-naming__registry_class_collision` still refused).
- **I5.** Every class file written is imported by the registry, and every registry import names a written file (`test_public_route_baselines.py:109` already checks this both ways).

## Component Overview

- **`class_signature` (new function, `src/sysml_codegen/resolution/models.py`).** What makes two computed modules the same class.
- **Identity settlement (new step, `src/sysml_codegen/elaboration/project.py`, end of `_build_calculation_modules`).** Groups formula and rollup modules by module type; for a group with more than one signature, re-types each member from its occurrence path with `derive_module_type`.
- **Class owners (new function, `src/sysml_codegen/generation/registry.py`).** The modules that own a generated class (D1). Exported for `cli/emit.py` and `cli/prepare.py`.
- **Registry entries (`registry.py:155-192`, `:239-398`).** Built from class owners, each with its import module; aliasing sets names only; import lines rendered from entries (D6); residual check adds the signature backstop (D7).
- **Writers and preflight (`cli/emit.py:265`, `:318`; `cli/prepare.py:256`, `:380`).** Iterate class owners instead of `graph.modules`.

## Non-Goals

- `[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]`: the calc-def pass is untouched.
- Changing how the alias is derived. Out, per the spec; this leaves the D3 limit in place.
- Constraint and report-aggregator modules on repeated parts. Not checked; they keep their current per-module behaviour.
- Removing stale per-copy handwritten files left over from earlier generations in a preserved `handwritten/` tree.

## Implementation Notes

- The signature must drop input `source` (it holds the occurrence key) and output `channel_name`; it must keep `default_value`, `description`, `python_type` and `param_name`, since the module template renders them.
- `PipelineModule` is a pydantic model; re-typing is `model_copy(update={"module_type": ...})` on `modules_by_semantic` entries.
- Per-copy module type is `derive_module_type(module.name.replace("__", "::"))`, the same derivation the rollup file path already uses (`prepare.py:314-315`). For a formula module in a divergent group, its file path must follow the new identity too, so `_get_python_path` uses the occurrence path for a formula whose module type is not its definition's. I found no formula that can diverge (formula inputs are named by expression references), so this branch is defensive. The implementer may instead refuse it as an internal defect; record which.
- Line numbers move in `registry.py` and `prepare.py`. `tests/expectations/refusal_cases/site_account.csv` pins `prepare.py:458` and the registry render site; update those rows.
- Keep the REQ-REG-07 warning ("Module class name collisions detected: ...") exactly as it is; `test_warning_reconciliation_exact_route.py:63` pins it for `costed_cart_d5`.
- `test_sc11_recheck.py` builds entries by hand. They gain an `import_module` key matching their import lines; the cases and assertions stay the same.

## Potential Risks

- **A baseline changes for a reason other than the flip.** The prototype says no, but it patched the alias match rather than rendering imports from entries. Mitigation: run the oracle after phase 2 and treat any other changed hash as a stop.
- **Corpus or refusal cases flip that the spec's search missed.** Mitigation: the full default run in phase 4 covers `test_fixture_classes_live.py` and the stored refusal answers.
- **The D3 limit surprises a user.** Mitigation: the refusal names both module types; backlog row filed; docs say so.

## Integration Strategy

The change sits entirely inside projection and generation; the CLI, snapshot format and contracts are unchanged. agentic-mbse's wrong-way example `fails="REGISTRY_CLASS_NAME_COLLISION"` in `docs/patterns/adr002-calculations.md` § "Repeated sub-assemblies" turns red; rewriting it is the orchestrator's follow-up.

## Validation Approach

- **Default suite (no `simkit`).** New fixtures under `tests/fixtures/` copied from `repro/two`, `named`, `nested`, `named_total`, `leafformula`, `arity`, plus the one-copy named model. A conformance test generates each and checks I2 statically: parse `pipelines/pipeline.yaml`, parse `__init__.py`'s imports and `module_type_override` with `ast`, then parse the imported file's `*Input` class fields. It also checks graph-level facts: arity copies have distinct module types; same-shape copies share one.
- **Execution lane (`pytest -m execution`).** A new `tests/execution/test_repeated_rollup_teax.py` asserts the spec's numbers, including the `sub[1].leaf[0]` mutation, using `generate_package_from_models` and the `PreparedEvaluator` harness. Expected values are written from the spec, not read from a run.
- **How to run the execution lane here.** The full lane needs a provenance manifest: adapt `.project/active/subset-profile-screen/evidence/execution-lane/lane.sh` (set `CG` to this checkout, point it at `lane_manifest.py` beside it) and run it against the branch commit. For a quick check during development: `PYTHONPATH=src:/home/reid/src/teax/packages/teax-simkit /home/reid/src/dc3/.venv/bin/python` runs a generated package directly through `execute_sealed_package`, which is how the numbers above were produced.
- **Fixture flips.** See phase 4.

## Next-Stage Handoff

- **Fixed:** D1, D2, D5, D6 and the invariants.
- **Open, implementer's call, record it:** the defensive formula-divergence branch (Implementation Notes); the helper names.
- **De-risk first:** phase 2's byte-identity check on the oracle.

## Plan

### Phase 1: Signature and identity at projection
- [ ] Add `class_signature` to `resolution/models.py`.
- [ ] Add the settlement step at the end of `_build_calculation_modules` (`project.py`); re-type divergent groups from occurrence paths.
- [ ] Graph-level tests: `two` copies share `p.sub.capital_costModule`; `arity` copies get `p.top.a.capital_costModule` and `p.top.b.capital_costModule`; a target selection of `b` alone gives the same module type as the full build.

### Phase 2: Registry
- [ ] Add the class-owners helper; build `_registry_class_entries` from it with `import_module` on each entry.
- [ ] Alias step assigns names only; render import lines from entries in today's group order; delete the substring search.
- [ ] Add the signature backstop to the residual check (D7).
- [ ] Update `test_sc11_recheck.py` entries with `import_module`.
- [ ] Run `test_public_package_oracle.py` and `test_public_route_baselines.py`: only `unresolvable_attr_probe` may differ. Stop if anything else does.

### Phase 3: Writers and preflight
- [ ] `_generate_modules`, `_generate_stencils` (`emit.py`) and `_check_duplicate_output_paths` (`prepare.py`) iterate class owners.
- [ ] Formula path follows a per-copy module type, or refuse it as an internal defect (record which).

### Phase 4: Fixtures, pins and tests
- [ ] Add the reproducer fixtures and their `fixture_classes.json` entries (`generating`).
- [ ] Add the default-suite structural test (I2) over the new fixtures and `unresolvable_attr_probe`.
- [ ] Add `tests/execution/test_repeated_rollup_teax.py` with the spec's values.
- [ ] `unresolvable_attr_probe`: run the built package in real TEAx and check its values by hand against the model before trusting it (my probe got `derived_instance.inherited_product` 20.0, `mixed_product` 30.0; confirm from `model.sysml`). Then set its `public_package_oracle/baseline.json` entry to the built file hashes (the README requires a reviewed, not same-run, oracle), and set its `fixture_classes.json` class to `generating` with the note updated.
- [ ] `elab_native_plural_scope`: set its `fixture_classes.json` class to `generating` after checking its values (selected 14.0, shadow 4.0) in real TEAx; add it to the structural test.
- [ ] Repoint `test_a_registry_class_name_collision_refuses_before_the_writer_runs` (`test_public_authority_switch.py:516`) at `tests/fixtures/refusal_cases/output-naming__registry_class_collision`, which still truly collides; update its docstring.
- [ ] Update `site_account.csv` rows whose line numbers moved.
- [ ] Full default run, `ruff check`, `ruff format --check`, `mypy src/`.

### Phase 5: Docs and backlog
- [ ] `docs/architecture/reference/20-module-registry-generation.md`: state the class-identity rule (one class per module type for formula and rollup modules, shared file at the first copy's path, per-copy identity when shapes differ); remove "no committed model hits the grandparent case" and the "filed follow-up" sentence about the import rewrite; describe the D3 limit.
- [ ] Backlog: file the D3 limit as a row; mark `[SC11-IMPORT-REWRITE]` resolved by this item.
- [ ] Run the execution lane (adapted `lane.sh`) and record the receipt in this folder.

## Appendix A: Prototype full-suite run

`uv run pytest tests/ -p proto_plugin` with the prototype (scratchpad, monkeypatches only): 18 failed, 8503 passed, 9 skipped. Sorted by cause:

- **Expected flips (4):** `unresolvable_attr_probe` in the oracle and in `test_fixture_classes_live.py`; `elab_native_plural_scope` in `test_fixture_classes_live.py`; `test_public_authority_switch.py:516`. Phase 4 updates each.
- **Prototype artifacts, not design effects (5):** `test_sc11_recheck.py` (2; the prototype's alias step needed a private key the hand-built entries lack, which the design replaces with `import_module`); `test_warning_reconciliation_exact_route.py:63` (the prototype dropped the REQ-REG-07 warning; output for `costed_cart_d5` was byte-identical); `test_public_diagnostic_totality.py:461` and `test_cli_generation.py` (the prototype hooked `prepare_graph`, which these tests feed a fake graph; the design settles identity in `project.py` instead).
- **Fail on the unchanged branch too (9):** `tests/unit/test_check_ledger_4a.py` (8) and one `tests/study/test_study_cli.py` case. Not related to this item; I did not investigate them.

---

**Next Steps:** design review, then `/_my_implement` against the plan above.
