# Audit: Baseline Repair & Silent-Failure Diagnostics (UPSTREAM-FINDINGS Item 1)

**Verdict:** CONDITIONAL — implementation certifiable; two finish-line doc/hygiene fixes and a live green-suite reconfirmation stand between it and a clean PASS.
**Audited:** 2026-07-05
**Branch:** upstream-findings-epic
**Commit:** 3c42dd1

---

## Summary

The four production edits are exactly what the design specified, routed to the sites the design named, and each is a few lines with no new abstraction. Diagnostics fire on the live path (constraint pass in `pipeline_builder` Step 2.5; zero-output guard before the calc-def return; two reworded EXPOSE warnings that now name the canonical channel). Fixtures, tests, docs, and the dead-code deletion are all present and traceable. The five recorded deviations are sound.

Three things keep this from a clean PASS, none of them an implementation defect:

1. The verification matrix — the R1 traceability contract — still marks REQ-BASE-05 "PENDING RE-CAPTURE" even though the re-capture is committed in this very commit and (per the recorded gate) the suite is green. The matrix now misstates delivered status.
2. Scope hygiene: an Item-2 artifact (`snapshot-generation/design-review.md`, +296 lines) is bundled into the Item-1 commit.
3. I could not run the suite, ruff, or mypy this session — the harness gates all `uv`/`pytest` invocations and this is a non-interactive run. The green-suite claim rests on the prior-session gate recorded in the plan (1821 passed / 4 skipped / 5 xfailed; ruff 21 = main; mypy 109 = main) plus the committed state matching that gate. It was not independently re-verified here.

The stale-baseline registry corrections (deviation #4) are sound but are content changes, not ordering-only, and no test asserts those files — flagged below as a residual, not a blocker.

## Findings

### Plan completion

All five phases are complete and their notes are accurate.

- Phase 0 (probe + fixtures) — probe outcomes recorded; SC-7 fallback taken because shape-A fired the malformed-refs warning (672), not a reworded one. `expose_pure_shape_a` authored then removed (correct: under the fallback it funds no test and would be dead/misleading). `zero_output_calc` committed, no snapshot (it raises once D3 lands). Sound.
- Phase 1 (D2/D3/D4 + dead-code) — all edits present in `extractor.py`, `pipeline_builder.py`, `graph_builder.py`, `output_registry_builder.py`; `constraints.py` and `constraint_validator.py.jinja2` deleted with two new deletion assertions in `test_dead_code_removal.py`.
- Phase 2 (D1 sort) — one-line `sorted(param_groups, key=lambda g: g.name)` as Step 9 before `ComputationGraph(...)`; I1 parametrized test added.
- Phase 3 (re-capture) — orchestrator-executed; baselines committed. Two further deviations (capture-script flavor fix; two stale registries) recorded.
- Phase 4 (docs/matrix/tags/impact) — all landed; see the matrix caveat in Spec conformance.

### Spec conformance

Traced against the four REQ families and the twelve success criteria.

- **REQ-BASE-06 (sort at construction, I1)** — `graph_builder.py:362-366`. Verified in code; `test_graph_assembly.py::test_entry_point_groups_sorted_by_name` covers all five baselines. **Met.**
- **REQ-BASE-05 (re-capture, ordering-only, reviewed)** — solar_battery ×3 and catf_mfe ×2 committed. catf_mfe graph diff is structurally ordering-only: the only keys appearing in changed hunks are `"name"` (entry-group reorder); no `module_id`/`execution_order`/`channel`/`source_module` lines changed. Behavior of the re-capture is delivered. **Met in substance — but the matrix row still reads "PENDING RE-CAPTURE" (Finding C-1).**
- **REQ-EXT-08 (zero-output fail-fast)** — `extractor.py:264-276`, `ValueError` before `CalculationDefinitionData(...)`, message verbatim per design. `zero_output_calc` fixture is a real single-def model with an `in` and no `out`. `test_extractor.py::TestReqExt08...` asserts the raise. The Jinja crash site (`teax_module.py.jinja2:118`) is now unreachable for zero-output. **Met.**
- **REQ-EXT-09 (constraint drop diagnostic)** — `report_dropped_constraints()` + `_constraint_owner_kind()` in `extractor.py`, called from `pipeline_builder.py` Step 2.5 on the live path. One INFO per `ConstraintUsage`, one summary WARN with the model-wide total; `elements_of_type("ConstraintUsage")` (primary mechanism, Phase-0 probe: 65 usages, owner always reachable). `test_extractor.py::TestReqExt09...` counts structurally (no magic N) and asserts both a calc-def- and a part-def-owned constraint are reported. **Met.**
- **REQ-CA-09 (EXPOSE wording)** — both name-drop warnings reworded to state the name is dropped and name the canonical channel (`graph_builder.py:688-694`, `output_registry_builder.py:182-186`); malformed-refs (672) untouched. Wording is correct and V-rule-shaped. Real-fixture test deferred to Item 8 per the recorded fallback. **Met as a wording change; test deferral is the adjudicated fallback.**
- **Docs (REQ-DOC)** — `modeling-assumptions.md` §8 "Constraints Are Not Executable" + V7 row; `01-extraction.md` REQ-EXT-08/09; `16-computed-attributes.md` REQ-CA-09 with the Item-8 deferral note. Clear and accurate. **Met.**
- **Dead-code deletion (D2)** — both files gone; `constraint_extractor.py` and `PartDefinitionData.constraints` kept, as decided. **Met.**
- **agentic-mbse impact** — recorded in `plan.md` Phase 4 Completion and `spec.md` §agentic-mbse impact: endorse A-1 (constraint non-executability WARN), with `modeling-assumptions.md` §8 as the canonical pointer, no code change in this item. Per epic R2 the item's close-out list is where Item 12 accumulates from. **Met — location is the plan close-out + spec, consistent with R2.**

Two success criteria are literally superseded by recorded deviations (not defects, but note them):

- SC "A minimal shape-A EXPOSE_PURE fixture is committed and its generation emits the reworded message" — **not met as written**; replaced by the recorded SC-7 fallback (fixture removed, test deferred to Item 8). Correct call, but the criterion text is now stale.
- SC "No baseline changes beyond the re-captured solar_battery YAML" — **not met as written**; catf_mfe (ordering-only) and the two stale registries also changed. Superseded by the design's per-model reinterpretation (I2) and deviations #2/#4.

### Design conformance

Implementation follows the design. Sort at the graph site scoped to `param_groups` only (D1); single dedicated constraint pass over `elements_of_type` covering all three owner kinds (D2); fail-fast at extraction (D3); two-warning rewording, malformed-refs untouched (D4); sequential REQ numbers (D5). No ComputationGraph schema change. No new module or abstraction. The one deviation from the design's I2 (catf_mfe also re-captured) is recorded, adjudicated (option 1), and proven ordering-only.

### Code integrity

No slop. The constraint pass is detection-only, holds no state, and nothing downstream reads it — exactly as designed. The zero-output guard raises a specific `ValueError` with an actionable message (no silent fallback). Owner-kind resolution is a small explicit dispatch. `getattr(constraint, "owner", None)` and the `"<anonymous>"`/`"<unknown>"` fallbacks are defensive but appropriate for a diagnostic that must never itself crash. No broad `except`, no back-compat shim, no optional-parameter papering.

One residual worth naming: the two stale-registry corrections (`sample_model` 5→0 modules; `catf_mfe` 21→18 classes) are content changes regenerated by the snapshot-boundary capture script from the committed graphs, so they are consistent by construction — but **no test asserts either registry file**, so their correctness is not guarded by the suite. This is pre-existing (the files were already stale) and the fix is janitorial and sound, but it means the quality bar here rests entirely on the capture script, not on a test.

---

## Findings by severity

**C-1 (should-fix before close) — verification matrix misstates delivered status.**
`docs/architecture/verification-matrix.md` marks REQ-BASE-05 "PENDING RE-CAPTURE" and BASE as "5/6 pass, 1 pending," but the re-capture is committed in 3c42dd1 and the recorded gate is green. The R1 traceability contract should read the true state. Fix: set REQ-BASE-05 → PASS and update the BASE summary/index counts (and the "PENDING RE-CAPTURE = 1" metric).

**C-2 (should-fix) — Item-2 artifact bundled into the Item-1 commit.**
`.project/active/snapshot-generation/design-review.md` (+296) belongs to Item 2 and is not traceable to Item 1's spec/design/plan/deviations. Harmless (a doc), but it muddies the "everything in this commit traces to Item 1" claim. `.gitignore` adding `.orchestrate-logs/` is benign orchestration infra. No production scope creep found — the four source edits, fixtures, tests, docs, and baselines all trace cleanly.

**L-1 (note) — stale-registry corrections are content changes, unasserted by tests.** See Code integrity. Sound and recorded (deviation #4); flagged so a future reader does not read "ordering-only" as covering these files.

**L-2 (note) — the two hard-diagnostic tests are license-gated.** REQ-EXT-08 and REQ-EXT-09 load a fixture live and `pytest.skip` when syside is unavailable, so in a license-less CI neither diagnostic is exercised. This is inherent (both need live extraction; `zero_output_calc` raises before a snapshot could exist) and acknowledged in the design. Item 2's snapshot path is the eventual mitigation. No action in Item 1.

**P-1 (process) — suite/ruff/mypy not re-run this session.** Harness gate + non-interactive. The green gate rests on the plan's recorded prior-session figures and the committed state matching them. Reconfirmation is the one thing an auditor could not do here.

---

## Fix list (to move CONDITIONAL → PASS)

1. **Reconfirm the gate.** Run `uv run pytest tests/`, `uv run ruff check src/`, `uv run mypy src/` on 3c42dd1. Expected: 1821 passed / 4 skipped / 5 xfailed; ruff 21 (= main); mypy 109 (= main). (Auditor was sandbox-blocked from running these.)
2. **Fix C-1:** flip REQ-BASE-05 to PASS in `verification-matrix.md` and correct the BASE counts + the PENDING metric.
3. **(Optional, C-2):** note or relocate the bundled `snapshot-generation/design-review.md` so the Item-1 commit's scope is clean (or accept it as orchestration bleed and move on — it is a doc).

---

## Certification

Verified by inspection of commit 3c42dd1 (source, tests, fixtures, docs, baselines, deviations) against spec, design (incl. review resolutions + both deviation rounds), plan, and epic Item 1 / R1–R3:

- Four production edits present, correct, and design-conformant; diagnostics on the live path.
- Two new real-fixture diagnostic tests (REQ-EXT-08/09), structural, no mocks; SC-7 test deferral is the recorded fallback.
- Dead-code deletion complete with guarding assertions.
- Baseline diffs ordering-only where claimed (catf_mfe graph confirmed structurally); registry corrections consistent-by-construction but test-unasserted.
- Docs + REQ tags landed; matrix present but one row is stale (C-1).
- agentic-mbse A-1 endorsement recorded for Item 12 in the plan/spec close-out.
- Five recorded deviations reviewed and found sound.

Not certified here: independent green-suite/lint reconfirmation (harness-blocked, P-1) and the stale matrix row (C-1). Verdict: **CONDITIONAL**, clearing to PASS on the three-item fix list above.


---

## Orchestrator close-out (2026-07-05)

- **C-1 fixed**: verification-matrix REQ-BASE-05 flipped to PASS; BASE counts corrected (6/6).
- **C-2 acknowledged**: the Item-2 design-review artifact rode along in commit 3c42dd1 — doc-only,
  no code impact; noted for the trail.
- **P-1 satisfied**: orchestrator independently re-ran the full suite at HEAD after the matrix fix:
  1821 passed / 4 skipped / 5 xfailed. ruff (21) and mypy (109) counts previously verified equal to main.

Verdict upgraded: **PASS**. Item 1 complete.
