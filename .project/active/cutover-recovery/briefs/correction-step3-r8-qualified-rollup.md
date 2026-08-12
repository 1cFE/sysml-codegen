# Stage brief — narrow-correction step 3: fix R8 qualifier-dropping rollups

You are executing step 3 of the 2026-08-12 narrow correction for Item 7. The authority is
`.project/active/cutover-recovery/plan.md`, "Narrow correction — executable sequence", and
`owner-disposition-20260811.md` disposition 1:

**[AGENT] (ratified for execution by owner, 2026-08-12)** Fix R8 first by preserving enough
qualified identity through rendering. Fall back to a shipping gate only if measurement shows a
substantially larger naming-contract change. Item 10 is not an Item 7 dependency when R8 is fixed
here.

Work synchronously. Never pause for background agents. Finish or stop on a concrete premise
conflict.

## Preflight and evidence

Use only `/home/reid/1cfe/item7-rebuild-venv/bin/python`, with that venv's `bin` first on `PATH`.
Load the SysIDE license from `/home/reid/1cfe/agentic-mbse/.env`. Assert imports resolve into the two
rebuild worktrees and TEAx checkout. Confirm both rebuild worktrees are clean; never touch the
protected originals.

Read:

- Plan Gate 4C S4 / R8 and the narrow-correction step-2 completion note.
- `src/sysml_codegen/elaboration/elaborate.py`, especially `_resolve_computed_expressions`.
- `src/sysml_codegen/elaboration/project.py`, especially `_computed_inputs` and
  `_compile_computed_expression`.
- `tests/integration/test_costed_component_exact_route.py`, especially
  `test_a_two_term_same_name_rollup_is_refused`.
- `tests/fixtures/costed_cart_d5/{PROVENANCE.md,library.sysml}`.
- The Slice-3B option-C pins in `tests/conformance/test_exact_group_identity.py` and
  `test_elaboration_phase5_remediation.py`.

Measure the existing failing model before editing. Confirm the typed graph resolves distinct
sources for `panel.capital_cost` and `caster.capital_cost`, and confirm the public route refuses
only because both expression references render the same parameter base.

## Required implementation

Fix the name loss at the elaboration seam without changing the typed port identities or source
edges.

- For a computed expression, keep the existing leaf-only input name when that leaf name is unique
  among its reference occurrences.
- When two or more expression references share a leaf name, render each reference with enough of
  its resolved chain to distinguish it. For the R8 witness this means separate bases derived from
  `panel.capital_cost` and `caster.capital_cost`; the projector may still append edge ordinals for
  plural expansions.
- Use resolved semantic facts, never written text or string lookup, to choose the qualifier.
- Preserve deduplication when the same semantic source is referenced twice. Preserve plural edge
  ordering and all typed identities.
- Do not qualify every chain unconditionally. The measured narrow fix should change only
  same-leaf collisions within one computed expression. If the implementation cannot be kept this
  narrow, stop and report the actual naming-contract blast radius before applying a broader rule.

## Required public proof

Invert, do not delete, the public refusal test at
`tests/integration/test_costed_component_exact_route.py`:

- The exact pipeline context builds successfully from the authored two-term model.
- The public `run_codegen` route returns true and writes a complete package.
- The projected computed module has two distinct source families and distinct parameter names
  that retain `panel` versus `caster` identity. For the two arrayed children, assert the exact
  four consumer parameters and their exact source channels/scopes; a graph that silently drops or
  merges one term must fail.
- Assert the generated implementation expression consumes all four distinct parameters and that
  hand-derived execution produces `2 * (1.0 * 2.0) + 2 * (3.0 * 2.0) = 16.0`.
- Keep the public no-half-written-tree refusal behavior covered elsewhere; this node no longer has
  a refusal subject.

Update the stale R8 statements in `costed_cart_d5/PROVENANCE.md` and the fixture doc comment by
amendment: named intermediate terms remain a useful authored pattern, but they are no longer
required to avoid `SI_RENDERING_COLLISION`. Do not add a rejected-path prohibition.

## Blast-radius proof

- Run the option-C parameter-group naming pins and assert their expected sets/filenames are
  unchanged.
- Add or retain a focused assertion that a non-colliding feature chain keeps its prior leaf-only
  parameter name. This is the boundary that prevents an accidental global public-name change.
- Compare generated package paths or graph surfaces for representative non-colliding fixtures as
  needed. Any change to parameter-group identity, JSON key, schema field, module name, or output
  channel outside the R8 witness is a premise conflict and must stop the stage.

## Persistent record

Amend `plan.md` with the measurement, implementation rule, exact changed public names, focused and
full validation, and the conclusion that Item 10 is not an Item 7 dependency because fix-first
succeeded. Check narrow-correction step 3 only after validation. Update `.project/CURRENT_WORK.md`
so replacement/matrix coverage (step 4) is next.

## Declared path set

Only these paths may change:

- `src/sysml_codegen/elaboration/elaborate.py`
- `tests/integration/test_costed_component_exact_route.py`
- `tests/fixtures/costed_cart_d5/PROVENANCE.md`
- `tests/fixtures/costed_cart_d5/library.sysml`
- `.project/active/cutover-recovery/plan.md`
- `.project/CURRENT_WORK.md`

No agentic-mbse path may change. If a kept narrow regression belongs in a different existing test
file, stop before editing it and report the needed path expansion.

## Validation

At minimum:

1. Focused R8 integration file, exact group-identity pins, parameter-group filename pin, computed
   expression/elaboration tests affected by the helper, and any public generation test the diff
   reaches.
2. Full licensed sysml-codegen suite with `-rs`; zero license-skip lines. Explain every node-count
   change (the inverted test should keep its node count).
3. `capture_v6_batch.py --verify` 15/22/0 and corpus 9.
4. Execution lane `pytest tests/execution -m execution`; no regression.
5. Ledger paths/surface/groups and proof integrity.
6. Ruff on changed Python files, `ruff check src` no worse than 14, and `mypy src` no worse than
   57 errors in 11 files.
7. `git diff --check`, exact declared path set, both rebuild worktrees clean after the commit.

Commit code/tests/docs/record as one focused commit if possible. Report the commit OID, exact R8
before/after graph and generated names, arithmetic result, blast-radius evidence, gates, and any
premise conflict.

`ARTIFACT:` `tests/integration/test_costed_component_exact_route.py`
