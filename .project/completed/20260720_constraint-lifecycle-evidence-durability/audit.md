# Audit: TEAx Constraint Evidence Durability (Lifecycle Item 11)

**Verdict:** Certify
**Audited:** 2026-07-20
**Branch:** constraint-exec-epic (codegen); teax `constraint-exec-epic`
**Commit:** teax `c342b10` (HEAD confirmed); codegen `d5f155b` (artifacts only)

---

## Summary

The four unsound paths the spec named are fixed, and every design-review revision — the Critical
(C1) and three Majors (M1/M2/M3), applied without a second review round — was reproduced
independently and holds. Both evaluator routes now converge on one tolerant report read; evidence is
sealed into a deep-frozen tree that defeats nested mutation at depth while still encoding
byte-identically; `OUTPUT_WRITE` emits off a positive executor signal (never a null-key inference);
and an absent channel on a constraint-bearing catalog raises loudly instead of committing a
healthy-looking empty case. Full teax suite is 310 passed; codegen source is untouched. The findings
below are all Minor and non-blocking — coverage/framing gaps the evidence largely discloses, not
defects.

## Findings

### Plan completion

All six design phases verified against the committed code and re-run tests.

- **Phase 0 (RED→GREEN).** GREEN proven on both routes (`test_constraint_free_{prepared,file_backed}_empty_evidence`,
  green). RED is structurally sound — the deleted `report = result.outputs[REPORT_CHANNEL]`
  (`evaluator.py:132`/`:203`) `KeyError`s on a report-less mapping — and the evidence honestly
  discloses that the file-backed route hit a *separate* pre-fix blocker (the `toy_plant_params.json`
  hardcode) rather than the bare KeyError. Honest, not a gap.
- **Phase 1 (absence seam + M3).** One read in `project(result, *, provenance, expects_report)`
  (`projection.py`); both evaluator reads deleted. `CorruptConstraintEvidence(RuntimeError)` raised on
  absent+`expects_report`, and it is deliberately *not* `EvaluationFailed` (`evidence.py`) so it
  crashes past `runner.py`'s `except EvaluationFailed` — verified in source.
- **Phase 2 (immutability + migration).** Confirmed independently (see M2 below).
- **Phase 3 (OUTPUT_WRITE).** Confirmed independently (see C1 below).
- **Phase 4 (four-status + excluded-only).** `excluded_only` fixture green; four statuses covered by
  the existing composition re-run on the sealed tree.
- **Phase 5 (deletions).** Confirmed (see Code integrity).

### Spec conformance

- **SC1 — constraint-free → empty evidence, both routes, no KeyError.** Met.
  `responses == {}`, `report is None`, real `outputs` survive (asserted at
  `test_constraint_evidence_durability.py:59-74`).
- **SC2 — excluded-only → exact `not_assessed`, distinct from constraint-free.** Met. Present report,
  `headline == "not_assessed"`, `assessed_count == 0`, `results == []` (`:190-193`) — structurally
  distinct from `{}`/`None`, and both distinct from a satisfied report (non-empty `results`). Three
  surfaces confirmed distinct.
- **SC3 — nested mutation cannot change authoritative or persisted evidence.** Met. Reproduced
  independently: the sealed tree is `mappingproxy`/`tuple`/`mappingproxy` at depth; `report["results"][0]["status"]`,
  `["margin"]`, list-append, and both mappings all raise. Persisted copy protected by construction
  (INV-D subsumed by immutability + `test_evidence_digest_identical_across_dispositions`).
- **SC4 — exact report JSON persists/harvests for the four statuses, each with `executable_fingerprint`,
  never merged across fingerprints.** Met via existing composition (`test_runner_matrix`
  {satisfied/violated/indeterminate/not_assessed}, `test_runner_failures` assessment_failed,
  `test_query::test_every_result_carries_executable_fingerprint`). See F2 for a framing caveat on the
  "never merged" control.
- **SC5 — fixture-pinned phases, not evaluator agreement.** Met.
  `test_f1_arithmetic_normalization.py:64-80` asserts `prepared == file == expected`, where `expected`
  carries the phase/module from the parametrized fixture tuple — the `== expected` clause is the pin.
  Grep found no `prepared.phase == filebacked.phase` derivation anywhere.
- **SC6 — OUTPUT_WRITE emitted honestly or collapsed.** Met (emitted). See C1.
- **SC7 — duplicate reads + encode-before-policy removed; one mechanism.** Met. See Code integrity.

### Design conformance

Implementation follows the design. C1/M1/M2/M3 resolutions land as written:

- **C1 (positive write-phase signal).** `context.in_output_write` set True immediately before
  `write_outputs(...)` and cleared on success — **no `finally`** (`pipeline_executor.py:156-172`), so a
  mid-write exception propagates with the flag still True. `_normalize_run_failure` reads the flag only,
  never exception type or null key (`evaluator.py:57-73`). Verified against three coordinates:
  unwritable `output_dir` (bare `OSError`) → `OUTPUT_WRITE`, module_or_channel None; malformed entry
  JSON → `MODULE_EXECUTION`, never over-stamped; the pre-existing router-setup test flipped honestly
  from `MODULE_EXECUTION` to `OUTPUT_WRITE`. Prepared route (`persist_outputs=False`) never enters the
  block, so OUTPUT_WRITE stays file-backed-only.
- **M1 (test migration).** All six typed-report sites migrated faithfully — identity→value
  (`test_projection.py`), `object()`→dict tree with the INV1 opacity pin re-expressed
  (`test_isolation.py:61`), `_StubReport`/`_TypedReport`/`_PoisonedReport`/`ConstraintReport`→dict trees
  (`test_policy.py`, `test_evidence_io.py` ×2, `study/conftest.py`). The broad `report=`/`.report` grep
  claim holds (no other typed consumers).
- **M2 (frozen tree + widened walkers).** `_freeze` recurses dict→`MappingProxyType`, list/tuple→`tuple`;
  `ModelEvidence` seals via a `field_validator`; `report: Mapping[str, Any] | None`. The three walkers
  (`_tag_nonfinite`, `_untag_nonfinite`, encode payload) accept `Mapping`/`(list, tuple)`;
  `encode_evidence` drops its own `model_dump`. **Independently reproduced:** non-finite floats nested
  inside a frozen `results` tuple still emit `{"__nonfinite__": …}` tags (byte-identity crux), and the
  MF-3 reserved-key collision still raises inside the sealed report.
- **M3 (catalog authority).** `study/cli.py:_prepared_evaluator` derives
  `bool(load_model_contract(package_dir).concrete_entries)`; the evaluator forwards a plain bool
  (evaluation stays isolation-clean). Ground-truth confirmed: `constraint_free`/`excluded_only` →
  `concrete_entries == {}` (False), `sealed_package` → True. The spec-derived default
  (`_report_declared_in_spec`) agrees with the catalog for constraint-free (its pipeline declares no
  `constraint_report` field). See F1 for the coverage caveat.

### Code integrity

No slop or failure-honesty problems in the changed source.

- **Deletions verified.** Two duplicated bare reads → one tolerant read in `project`. The
  encode-before-policy *rationale* is removed (`runner.py`): `encode_evidence` now sits inline at each
  commit site, and the atomic durability seam `store.commit_case(..., crash=self.crash)` is untouched.
  Crash-safety is preserved — a crash between `assess` and `commit_case` persists nothing in either the
  old or new ordering, and evidence immutability makes the ordering non-load-bearing. `test_crash_regimes`
  green.
- **File-backed entry-path generalization** derives the write path from the spec's single entry binding
  (`bindings[0].artifact_path`, `evaluator.py:_entry_artifact_path`), not a hardcode. It does not open a
  silent fallback: f1 resolves identically (`test_f1_arithmetic_normalization.py:100` asserts the entry
  bytes land at the derived path), and a spec-vs-path mismatch fails loud at entry load (no wrong-file
  read). See F4 for the residual legacy fallback.
- **No broad excepts, no invariant-swallowing fallbacks.** The corruption path raises loudly; the
  absence path is a positive `expects_report=False`, not a bare `.get() or default`.
- ruff clean on all eight changed source files; mypy errors present are pre-existing
  (`pipeline_validator.py`, `pipeline_executor.py:636`), unrelated to the Item-11 edits.

---

## Minor findings (non-blocking)

- **F1 — M3 catalog→corruption effect not asserted end-to-end.**
  `test_constraint_evidence_durability.py:86` forces `expects_constraint_report=True` directly on
  `PreparedEvaluator`, bypassing `cli.py`'s `bool(concrete_entries)` derivation. The derivation is
  *executed* (the CLI run tests drive `_prepared_evaluator` against `sealed_package`, which yields True)
  and the guard branch is proven, but no single test drives a non-empty-catalog package with a dropped
  channel through `cli._prepared_evaluator` to the raise. The two halves are each proven; only their
  production join is untested. Honestly disclosed in `evidence.md:128-130`. Recommend a follow-up
  coordinate.
- **F2 — "two-fingerprint control" (design D4/INV-E) not delivered as described.** Never-merge is proven
  by fingerprint-scoping (`test_every_result_carries_executable_fingerprint`, single-fingerprint: all
  cases share the store fingerprint) plus store-incompatibility rejection
  (`test_incompatible_store_yields_new_lineage_message`), not a literal two-fingerprint merge-separation
  control. The invariant holds via a different mechanism; the design text overstates the specific test.
- **F3 — INV-G "golden" framing overstates the proof.** There is no captured old-bytes golden pinning
  byte-identity across the D2 change; equivalence rests on round-trip/inverse tests plus the walker
  descending the frozen tree (independently confirmed here). The property holds; the "golden" label is
  inaccurate.
- **F4 — residual legacy fallback in `_entry_artifact_path`.** For a non-single-binding (multi-group)
  spec it falls back to the hardcoded `work_dir/inputs/toy_plant_params.json`. Safe today (a mismatch
  fails loud, not silently) and no fixture exercises it, but it is a latent hardcode that would misdirect
  a multi-group generated package's file-backed write. Note for when multi-group file-backed lands.

---

## Certification

Checked and verified independently (reproduced, not trusted):

- **C1:** entry-load failure → not OUTPUT_WRITE; unwritable output_dir → OUTPUT_WRITE; set-before /
  clear-on-success (no `finally`) survives a mid-write exception — all three via green coordinates and
  source read.
- **M1:** six migrated sites read from the diff and confirmed faithful; broad-grep claim holds.
- **M2:** frozen tree reproduced defeating nested `status`/`margin`/`results` mutation at depth,
  encoding non-finite tags byte-identically at depth, and MF-3 firing inside the sealed report — via an
  independent probe, not only the suite.
- **M3:** corruption raise for absent+expects; excluded-only present channel never mistaken (flag moot);
  catalog authority ground-truth confirmed for all four fixtures.
- **Six audit directives:** RED→GREEN both routes + three distinct surfaces; four-status round-trip +
  fixture-owned phase pins (no evaluator-agreement derivation); entry-path generalization derives from
  the spec with no silent fallback; deletions with crash-safety preserved; batteries (teax 310 passed,
  codegen source untouched vs `b987869`, Items 8/9 surfaces green, ruff clean); evidence honesty incl.
  A3 confirmed real.

**Not checked:**
- Byte-identity was verified by mechanism and independent probe (nested non-finite tags in the frozen
  tree), **not** against a captured pre-D2 byte golden (none exists — see F3).
- The M3 corruption path was not driven end-to-end through the real `study` CLI with a dropped channel
  (see F1); only the guard branch and the catalog derivation were checked, separately.
- Cross-repo fusion-tea / stellarator downstream suites were not run — Item 11 is TEAx-side and the
  relevant Item 8/9 regression surfaces inside the teax suite are green; the external fusion packages
  were not executed.
- mypy was spot-checked on the two most-affected evaluation files, not run as a full-tree gate; the
  "no-new" claim rests on the surfaced errors being in untouched pre-existing modules.
- Nothing was pushed or re-generated; the RED KeyError was confirmed structurally from the deleted
  read, not by reverting and re-running the pre-fix evaluator.
