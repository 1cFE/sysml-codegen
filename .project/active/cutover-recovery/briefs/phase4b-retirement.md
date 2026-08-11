# Stage brief — Phase 4, Gate 4B retirement execution (steps 1–4)

**You are executing the approved retirement sequence** of the recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: the Gate 4A approval + regrouping records, Gate 4C parts 3/5/6 notes (especially the
part-6 completion at `15b8486` and its readiness section), `ledger-4a.md`/`.json`, and the
checker's `groups` mode output at HEAD. Environment note from part 6 is binding: the wired pair
is `/home/reid/1cfe/item7-rebuild-venv` + `/home/reid/1cfe/agentic-mbse-item7-rebuild`; assert
imports before anything.

## Orchestrator rulings you carry in (recorded)

1. **YAML baselines (the 4 legacy-backed nodes + L-039):** at v5-family retirement, regenerate
   the baselines through the PUBLIC exact route as new v6-backed byte baselines. The part-6
   measurement (every diff maps to a named mechanism) is the review basis — cite it in the
   commit; hand-check the load-bearing values; `test_e2e_output_registry.py` follows its row's
   disposition in the same commit. `capture_baseline_yaml.py` / `capture_pipeline_baselines.py`
   retire with the family per their rows (their replacement: the public-route regeneration path
   you just used — name it).
2. **Zero-constraint aggregator asymmetry:** the exact route's early return STANDS (no synthetic
   module without content — consistent with the epic's no-synthetic-entries direction). Record
   it as a named mechanism in the ledger/mechanism list and the Phase 5 packet. No code change.
3. **`test_public_authority_switch.py` legacy-arm nodes:** their subject ("legacy still
   generates what the public route refuses") ceases to exist when the legacy route retires. At
   the retirement commit that deletes their subject, retire those nodes with per-node recorded
   dispositions; public-arm assertions survive. Re-derive which of the 11 rows they back need
   re-backing onto surviving public-arm or Phase 3 nodes — `replacements` must be green after,
   with no row backed by a deleted node.
4. **L-036/L-037 (agentic duals):** retire in the paired G4′ commit as previously ruled
   (agentic first, codegen names it).

## Sequence

0. **Proof-node repoint remainder:** `test_uncovered_params.py` (10 nodes) onto v6 evidence,
   own commit. Then `replacements` all green with no v5-family-dependent proof left except
   `test_public_authority_switch.py` (ruling 3 handles it at its retirement commit).
1. **v5-family retirement** (the 23-row family + the 159 defer-to-family files + ruling 1):
   37 v5 fixtures, capture script, `capture_snapshot`, serializer, write-path re-exports; every
   file executes its recorded row; baselines regenerated per ruling 1.
2. **G2′** (read path): re-derive readiness with the checker post-step-1; execute when green.
3. **G3′ + freed G3 rows** (pipeline_builder + analysis/resolution stack + package `__init__`
   re-export amendments + the codegen duals from L-033/L-034): the epic's core deletion. The 3E
   single-authority and residual pins get their final amendments (assert emptiness, never
   delete the pins).
4. **G4′** (comparator, `legacy_route.py` adapter, `_CONSTRAINT_LOGGER` rename, paired agentic
   dual retirement).

## Per-commit battery (no exceptions)

Full licensed suite with node-level delta accounting against ledger rows; corpus 15/22 unmoved
(the ledger test); v6 batch `--verify` 15/22/0; execution lane 38 incl. real TEAx at anchors;
ruff/mypy measured; `git diff --check`; checker `paths`/`surface`/`groups`/`replacements` all
consistent with Git truth (executed rows recorded). After step 4 additionally: the v5 typed
refusal still typed; every 3E pin green in its amended form; `git grep` residue sweep for the
deleted module names in src/ (report, don't auto-delete docs — 4D owns docs).

## Stops

Unledgered breakage on any axis; a row whose recorded disposition doesn't match what execution
requires; corpus/hand-value drift; a `replacements` row left backed by a deleted node. Any of
these: STOP with the measurement. If budget runs short: complete the current step's commit +
battery, report the honest remainder — never a half-executed step.

## Report back

Per-step: rows executed, nodes retired with dispositions, battery numbers, checker state, OIDs
(paired for G4′). Then Phase 4 remaining state (4D docs + any remainder).
`ARTIFACT:` the updated plan.
