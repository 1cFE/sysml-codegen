# Stage brief — Phase 4, Gate 4C part 6 completion: the six-file re-derivation

**You are completing a bounded, precisely inventoried piece** of the recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: the Gate 4C part 6 notes in the plan (the prior session's exact inventory and the
narrowed L-006/L-241 weakness), `ledger-4a.md`/`.json`, the variant fixtures' PROVENANCE
records (`catf_mfe_d5`, `solar_battery_d5`, `chain_spike_d5`), and the 3E mechanism records
(consumer collapse, declaration-site groups, per-occurrence expansion) — they are the ratified
reading of expectation deltas.

## State you inherit

Head `6822685`+records, clean. Suite 3810/47/38 licensed; corpus 15/22; execution 38 at
anchors; checker paths 298/0, surface 0 both axes, replacements green incl. L-006/L-241 (via
the repointed `test_gen_stencils.py`). The prior session repointed `test_gen_stencils.py`
(32 nodes, nothing thinned) and reverted six files rather than commit them half-migrated.

## The work — six files, 17 failures + 18 errors, every one a real re-derivation

Repoint onto the variant fixtures (v6-backed graphs) and re-derive every expectation
independently — hand arithmetic and model-derived values, never copied from legacy output:

- `test_generation_boundary.py` (7): preservation, backlog, auto-impl dispatch on variant
  graphs. This file is also the third proof module for L-006/L-241 — its migration CLOSES the
  narrowed weakness; remove the weakness note from the plan when `replacements` confirms.
- `test_gen_pipeline_yaml.py` (5): YAML baselines and entry-point fusion counts. Baselines are
  generator-owned bytes — regenerate through the public route and hand-check the load-bearing
  values; do not hand-edit baselines.
- `test_gen_json_templates.py` (5): group counts (the 3E declaration-site change) and renamed
  keys (`width` → `width_in` per the D-5 recipe).
- `test_gen_schemas.py`, `test_gen_module_wrappers.py`: complete their repoints at the same
  bar (the prior session's mechanical pass may leave them green — verify, don't assume).
- `test_gen_registry.py` (18 errors, the deepest): it reads the legacy classifier intermediate
  (`inputs["snap"]`) and one test drives `generate_via_legacy_route` from a v5 snapshot. Rebuild
  its subjects on the exact route's public surface. Any node whose subject is intrinsically the
  legacy classifier intermediate gets a recorded responsibility disposition (what covers the
  behavior now — likely the 3B/3E selection and registry tests; name nodes), not a silent drop.

Known-good re-derivation examples from the prior session: the exact route expands arrayed parts
per occurrence (`pv_module[0..9]` → 38 cost models) where legacy collapsed; group-count deltas
follow the 3E mechanisms. When a delta fits no ratified mechanism: rule-10 STOP with the
measurement — do not invent a new mechanism to make a test pass.

## Requirements

- Declared path set: the six files, the plan, ledger JSON if rows change state. Nothing else.
- No assertion thinning: node counts per file stay equal unless a node's subject is retired
  with a recorded disposition (registry intermediates are the only expected case; name each).
- Battery before commit: full licensed suite (delta explained node-by-node), corpus 15/22
  unmoved, v6 batch verify, execution lane 38 at anchors, ruff/mypy measured, `git diff
  --check`, checker all-green, `replacements` re-run with L-006/L-241 backed by all three
  modules.
- One commit + OID record; plan part-6 notes updated to COMPLETE (or the honest remainder).

## After this (same session if budget allows, otherwise report and stop)

The proof-node v6 repoint (the 10 files inventoried in the Part B stop, minus those part 5/6
already handled — re-derive the list with the checker) as its own commit, `replacements` all
green against v6-backed evidence. Do NOT start retirement steps 1–4; report readiness instead.

## Report back

Per-file: nodes before/after, re-derived expectations with their mechanism citations, any
retired-node dispositions; the weakness-closure proof; battery; readiness state for the
retirement steps; OIDs. `ARTIFACT:` the updated plan.
