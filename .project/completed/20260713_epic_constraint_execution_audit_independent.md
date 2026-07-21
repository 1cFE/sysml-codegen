# Independent Audit of Findings — CONSTRAINT-EXEC Epic Run

**Verdict:** Findings record CONFIRMED — every claim sampled reproduces exactly; two record-keeping findings to resolve at close (no code findings)
**Audited:** 2026-07-13 (owner session, after the 2026-07-12→13 orchestrated run)
**Auditor:** fresh session; did not implement or orchestrate the run
**Scope:** the run's *findings record* — the acceptance's 7 boundary-row divergences, the three
integration gaps (CE-F1..F3) and their fusion-tea bridges, and a sample of the
orchestrator-executed probes that upgraded item audits to Certify. This is an audit of the
evidence, not a re-audit of every item.

---

## Summary

The run's findings record is accurate and, where sampled, exactly reproducible. Both mutation
probes re-executed verbatim produce the recorded RED/GREEN signatures; all three repos' final
gates re-run to the recorded counts; the acceptance table's boundary story verifies at the data
level; and all three integration gaps are real, confirmed at named source lines on both the
producing and consuming side. Two record-keeping discrepancies need a one-line resolution at
close (Findings 1–2 below). Nothing sampled contradicts the certification record.

## What was verified, with evidence

### 1. The acceptance's 7 boundary-row divergences — CONFIRMED at data level

Recomputed independently from `fusion-tea/exploration/ife_e2e/study/acceptance_table.csv`
(2301 rows):

- Exactly **7 rows** have `old_viable != new_viable`; all 7 have `eta_g == 10.0` and
  `at_boundary == True`; **2294 match exactly** — the recorded 99.7%.
- Direction is uniform: old = False, new = True (`satisfied`). The generated `>=` admits the
  boundary the hand rule's strict `>` excluded — the "model-favoring" reading is correct.
- The epsilon window (`at_boundary`) excused **zero** real mismatches: boundary-flagged rows (7)
  and divergent rows (7) are the same set; non-boundary mismatches are 0.
- The hand rule is genuinely retired: `sweep_ife.py` now imports and calls
  `constraint_pred_ife_plant__ife_power_plant__viability` in the grid loop
  (`sweep_ife.py:46`, `:93`).

**Open (owner):** whether "met with recorded divergence" satisfies the epic's Critical Success
Factor wording is still the owner's call — raised, not yet ratified.

### 2. Integration gaps CE-F1..F3 — all three CONFIRMED real, bridges read and sound

- **CE-F1 (catalog emission shape).** sysml-codegen embeds the catalog in
  `model_contract.json` under `constraint_catalog` with `definition_qualified_name` /
  `formal_names` field names (verified in the regenerated IFE package's contract JSON); teax
  reads a *standalone* `contracts/constraint_catalog.json` with different field names
  (`simkit/study/config.py:83`, `simkit/study/cli.py:98`). The bridge
  (`materialize_constraint_catalog.py`) is honest: one genuinely synthesized field
  (`source_form`) is documented, failure raises rather than defaulting, and it records its own
  limitation — definition recovery via a QN-prefix search in `predicate_ir` breaks when one
  definition is shared by multiple usages. **That limitation belongs in the CE-F1 work item:**
  the real fix needs usage-level source data sysml-codegen does not currently emit.
- **CE-F2 (single-channel bridge).** `CandidateBridge.build` returns exactly one channel
  (`simkit/study/bridge.py:25-26`) while `MappingEntrySource.validate` requires every declared
  channel; the IFE package declares four. The bridge (`MultiChannelEvaluator`,
  `run_viability_study.py:68-90`) wraps the unmodified `PreparedEvaluator` through the
  documented `Evaluator` protocol seam and merges the three fixed channels from the package's
  own committed `inputs/*.json` — no teax source touched, as claimed.
- **CE-F3 (hardcoded fixture class).** `PreparedEvaluator.__init__` ends with
  `self.ToyPlantParams = self.package.ToyPlantParams` (`simkit/evaluation/evaluator.py`,
  prepare tail) — any package lacking that literal class name fails to construct. The
  driver-side alias bridge is as described. Fix is owner-approved for this session (before the
  teax PR), including strengthening the isolation test that missed it (it scans imports, not
  attribute-name references to generated classes).

The findings.md's own calibration note is accurate and worth preserving at close: "Items 9–12
certified" covered exactly what those items' single-channel toy fixture exercised; this run was
the first real multi-channel package through the certified path.

### 3. Orchestrator-executed probe sample — EXACT reproductions

- **Item 9 (package-contracts) extra-sweep mutation probe:** neutralized the policy walk in
  `contracts/verify.py`; exactly `test_extra_fails` RED (`assert not True`); revert; 19 passed
  (verify + contract-models suites, including the drift-guard cure
  `test_glob_matcher_bodies_identical_across_seal_and_verify`, present at
  `tests/unit/test_contract_models.py:161`). Matches the addendum verbatim.
- **Item 8 (snapshot-v3) mode-enum mutation probe:** deleted the
  `VALID_CONSTRAINT_LOWERING_MODES` guard in `snapshot/loader.py`; exactly the two
  mode-corruption cells RED (2 failed / 8 passed); revert; 10 passed. Matches the addendum
  verbatim ("cells h1/h2 FAIL, 2 failed/8 passed; revert → 10 passed").
- **Final gates, all repos, re-run this session:**
  - sysml-codegen (license env): **2330 passed / 23 skipped** — exact match; mypy **76** =
    baseline; ruff **clean**.
  - agentic-mbse: **1401 passed / 1 skipped** — exact match.
  - teax-simkit: **257 passed, 4 failed** — the 4 are exactly the known pre-existing
    `test_no_battery_deps` failures, and the recorded cause reproduces firsthand
    (`FileNotFoundError: /home/reid/teax`). Fix approved for this session as a separate commit.
- teax item audits (Items 10–12) were not re-traced line-by-line; their kept tests are inside
  the 257-passed re-run, and the store-runner audit's static trace was read and is consistent.

## Findings (to resolve at close — no code changes required)

1. **The "all 9 Success Criteria checked" claim is off by one.** The epic file's top-level
   Success Criteria are **8 of 9 checked**: the contracts/study-layer criterion
   (`epic_constraint_execution.md:44`) is `- [ ]`, and it is exactly the box carrying the
   CE-F1..F3 "Known narrowing" note. The handoff and close-out summary say all 9 are checked.
   Either state is defensible; the records must agree. Recommendation: at `/_my_close`, check
   the box **with** the narrowing note retained (the criterion's own mechanisms — seal, graph-only
   contract, atomic commit, fingerprint-bound resume — are all certified and re-verified here;
   the narrowing is interoperability scope, registered as follow-ons), and correct the run
   summary's "all boxes" wording — or leave it unchecked and fix the summary. Owner's pick.
2. **The acceptance CSV's `match` column reads as 100% standalone.** `match` is defined as
   `(old == new) or at_boundary` (`run_viability_study.py:168`), so all 2301 rows carry
   `match=True` — including the 7 divergent ones. findings.md states this honestly, but the CSV
   alone would over-read as a bare 100%, which the epic explicitly forbids ("never a bare
   100%"). Cheap cure if desired: add a `raw_match` column or a header comment; at minimum the
   close-out should cite findings.md, not the CSV, as the acceptance statement.

## Not checked

- fusion-tea's anchor re-verification (`run_anchors.py`) and the prepare-once benchmark were
  **not** re-executed (separate venv; recorded byte-exact against the pre-existing acceptance
  numbers). The benchmark's ~168× figure is taken as recorded measurement, not verified.
- Item audits other than Items 8 and 9 were sampled only via their tests inside the three
  full-suite re-runs plus a static read of the teax store-runner audit; their individual probe
  addenda were not each re-executed.
- The 44 unchecked boxes in the epic file's *per-item* sections were not reconciled item-by-item
  (the canonical per-item state lives in each item's spec/audit; only the top-level Success
  Criteria were adjudicated here).
- agentic-mbse `pytest -m ""` (PDF/Claude-API corpus) deliberately not run ([OWNER] standing
  instruction — real API spend; never a gate for SysML items).
