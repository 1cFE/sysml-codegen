# Implementation Plan: PR-readiness cleanup

**Status:** Phases 1–4 complete — independent audit in progress
**Created / updated:** 2026-10-08
**Authority:** Owner authorized the orchestration through implementation and independent audit and delegated routine judgment. Design/phase choices remain `[AGENT]`, not owner-originated settled requirements.
**Inputs:** [spec](spec.md), [design](design.md), [owner resolutions](spec-review.md), [corrected fresh review](spec-review-20261008.md), and `CLAUDE.md`.

## The Point

`[NEED]` Make the shipped elaborator ready for a PR without remnant code, misleading guidance, or claims stronger than the evidence. Use real functional regression checks and establish current customer compatibility before the PR. Owner-authorized model or consumer repairs may be coordinated with the ongoing customer cleanup; reproduce causes rather than treating a failure-count change as proof of a codegen defect. Source authority is carried from the spec's Known Requirements.

## Strategy and Environment

**Critical path:** Freeze pre-change output and licensed/customer identities → bounded fixes and recaptures → reconcile documentation/evidence → commit and archive the candidate → final validation and independent audit. The first proof point is successful replay of the immutable all-22 baseline, including refusals, before production/template/fixture changes. See [design decisions](design.md#key-decisions) and [risks](design.md#potential-risks).

Work in `/tmp/pr-readiness-cleanup-run`, branch `pr-readiness-cleanup`. Source `/tmp/pr-readiness-run-env.sh`; use `"$PR_READINESS_PYTHON"` for Python/pytest/mypy/Ruff. The companion clone is `/tmp/pr-readiness-agentic-mbse`, branch `pr-readiness-guidance`. Existing virtualenvs and explicit isolated `PYTHONPATH` are sufficient: no dependency sync or virtualenv writes. Never print the original companion `.env` contents. Record the license file path and independently confirmed licensed syside availability.

Preserve the original checkout against `/tmp/pr-readiness-original-state.json`, including its index and mental-alignment drafts. Customer validation starts from an archive of the current committed fusion-tea model tree; coordinate any repair with its active owner and isolate it from concurrent working-tree edits. No broad physics refactor. Phase checkboxes are unchecked until evidence exists; mark them immediately and append concise completion notes.

## Phase 1 — Freeze the independent baseline

**Goal / assumption:** Prove what the unchanged starting code actually emits and whether committed snapshots match their live sources. This establishes the independent expectation before any fix; inherited reports cannot replace it. Covers SC7a and the starting evidence for SC4/SC11/SC13.

**Test stencil — implement the replay first, then capture once from `6872977541eae935d4be2789f48f723ffea7101b`:**

```python
assert set(baseline) == set(committed_snapshot_paths)
assert len(baseline) == 22
for snapshot, expected in baseline.items():
    result = run_public_codegen(snapshot, isolated_output(snapshot))
    assert result.refusal == expected.refusal
    assert result.file_sha256 == expected.file_sha256
```

- [x] Add a small public-route capture/replay helper and durable JSON expectations under `tests/expectations/`; record exact codegen/Agentic identities, snapshot SHA-256s, generation configuration, complete file sets/digests, and public refusal diagnostics. Retain generated trees in scratch for later textual diff. Add the replay test in `tests/conformance/test_public_package_oracle.py` (new); no production changes yet.
- [x] Replay all 22 unchanged snapshots and verify the successful/refused partition from fresh evidence. A refusal produces no package; exercise existing-output sentinels too. Pin complete version fields and the trusted verifier file/hash as the unchanged reference.
- [x] Establish licensing independently of fixture validity; run `scripts/assess_v6_snapshot_churn.py` or its existing callable inventory against every committed snapshot. Regenerate collapsed D5 sources in scratch with `scripts/make_d5_variant.py` before assessing them. Licensed pre-C4 recapture must reproduce `fusion_tea` byte for byte. Record each stale/missing-source finding before any snapshot update; do not quietly allow unexplained drift.
- [x] Archive the named current fusion-tea committed tree and record its codegen pin/dependencies, source hashes, and the three generated cases. Reproduce baseline numerical/report results needed for C4 and current-customer comparison, separating fresh results from the review's inherited baseline. Save pre-change oracle/evidence with a path-specific commit before releasing source-edit workers.

**Validation / proof:** Run the new replay test through public `run_codegen` for every snapshot; inspect the durable inventory and licensed pre-capture reports. All output expectations are immutable data, outside generated-Python collection/formatting hazards. If baseline collection or pre-C4 identity fails, diagnose before dependent fixes.

## Phase 2 — Apply narrow code, companion, and fixture changes

**Goal / assumption:** The authorized changes remove wrong metadata/dead evidence and tighten encoding/typing without changing valid arithmetic, wiring, preservation, or verifier behavior. Phase 1 is a hard prerequisite. Covers SC1–SC6.

**Test stencil — public boundary and preservation checks precede the relevant edits:**

```python
before = tree_bytes(existing_output)
assert run_public_codegen(nonfinite_source, existing_output) is False
assert recorded_diagnostic == expected_diagnostic
assert tree_bytes(existing_output) == before
assert run_public_codegen(consumed_unit_fixture, new_output) is True
assert regenerate_real_package_with_handwritten_code() == original_handwritten_bytes
```

- [x] **Encoding/typing owner:** `contracts/serialize.py`, `generation/entry_point.py`, and C5's `generation/{preservation,test_gen,schemas,stencils,modules,pipeline}.py`. Add strict finite encoding; annotate existing types and validate optional values through preflight if needed. Extend `tests/unit/test_contract_models.py` and focused public-route tests on both representable live-model ±infinity inputs and sealed-snapshot NaN/±infinity inputs, finite ordinary/extreme/subnormal/exponent/signed-zero values, nonexistent/existing output, calculation/constraint/report generation, and real-package handwritten regeneration. Retain snapshot `SI_INTERNAL_DEFECT` and verifier bytes/hash. Run focused tests, mypy, and unchanged-snapshot oracle comparisons.
- [x] **Units/fixtures owner:** `extraction/feature_metadata.py`, its extractor/elaborator callers, `tests/conformance/test_unit_lane_port_metadata.py`, consumed-declaration live/snapshot fixtures, and `tests/fixtures/fusion_tea/designs/hif_ife/hif_driver.sysml`. Delete all three guessers and dead paths; retain parser-native written-value unit facts/constraint behavior. Test bare/bracketed/multibyte comments, parenthetical prose, and shared-input conflicts. Delete only the inert driver; update calculation/graph/channel pins in projection, fail-closed, and historical execution tests. Preserve seven numerical channels plus the two constraint/report exits, LCOE tolerance, enum checks, and dependent/unrelated mutation assertions.
- [x] **Dead-evidence owner:** `tests/conformance/test_dm08_enforced_surface.py`, its exclusive expectations, `tests/conftest.py`, `extraction/data_models.py`, and affected extraction/return-style/parity tests. Delete unused root fixtures and codegen-only v5 annotations, retain UUID sidecars/name wrappers/v6 payload evidence, and make required model-load failure fail. Give all nine missing parity-golden cases individual dispositions. Preserve the fixture diagnostic-accounting test's ledger-cited name. Coordinate the changed REQ-EXT-07 row with Phase 3's matrix owner.
- [x] **Companion owner:** Repair only the self-binding warning in Agentic `project_templates/MODELING_PROCESS.md.template`; commit it in the isolated companion clone and record commit/content hashes. Run `tests/conformance/test_self_binding_guidance_contract.py`, including the unmarked-executable-example detection. Do not amend the general units convention.

**Coordination / validation:** If workers are used, assign these disjoint owners explicitly and name every shared test/CLI edit before starting; workers accommodate others and never revert their edits. Use focused affected tests and oracle subsets during edits, not the whole suite after each change. Diagnose any valid-output delta beyond C3/C4 rather than refreshing expectations.

## Phase 3 — Seal intended differences and reconcile current records

**Goal / assumption:** Licensed recapture and exact output differences agree with the bounded owner decisions, and current records preserve surviving obligations honestly. Starts after the relevant Phase 2 changes; one coordinator owns matrix/tracking/recapture records. Covers SC3b/SC4a/SC7/SC8–SC10.

**Test stencil — use retained guards and exact approved comparisons first:**

```python
assert candidate_files == baseline_files_with_exact_reviewed_changes
assert arithmetic_and_wiring(candidate) == retained_expected_semantics
assert matrix_summary == recount_rows(matrix)
assert all_evidence_citations_resolve(matrix)
assert owner_provenance_guards_keep_original_force()
```

- [x] Licensed recapture `catf_mfe_gated`, regenerated `catf_mfe_d5`, and `fusion_tea`; update snapshot/batch/breadth/provenance records and their tests. Verify C4 deltas (one occurrence, 12 attributes, one calculation; `9/27/1/7` → `8/23/1/5`) and historical source identity at fusion-tea `9e1ff87bb`. Review textual generated diffs against scratch baseline, then record exact old/new file hashes separately from the immutable original oracle. Limit C4 to the six spec-named files; account individually for C3 label/seal changes.
- [x] Complete all-22 candidate replay and coverage inventory. Add/run one failing mutation per calculation/multi-output, aggregation/alias, constraint/report template shape and one rendering-code mutation, then restore source bytes. Record oracle limits for stubs, smart regeneration, handwritten preservation, and non-float outputs; link their functional evidence where available.
- [x] Repair the finite C8 document set in the research table, `docs/architecture/modeling-assumptions.md`, README companion-layout commands, and CLI snapshot default help. Retarget `tests/conformance/test_register_contract.py` and reference-doc guards at equal force; retain the minimum numbered reference-document set and test ordinary links/examples.
- [x] Reconcile `docs/architecture/verification-matrix.md`, including REQ-EXT-07, independent LC-SI/Item-3 authority mapping, original grades, and supported evidence dispositions. Add the smallest rerunnable count check for summary/family/footer agreement. Reconcile `.project/CURRENT_WORK.md`, backlog/epic records, all 21 downstream criteria, and Item-3 evidence. Owner-descoped assurance is marked descoped, not PASS; July supersession gets its one recorded line without a census. Preserve historical audit/close provenance, diagnostic debt, surviving evidence bounds, and resolve every remaining backlog-tag reference.
- [x] Run focused recapture/inventory/oracle/register/distinctness checks; ledger `paths`, `surface`, and `replacements`; matrix recount; Ruff/mypy on touched code; and whitespace. Check original checkout state and absence of mental-alignment files in the candidate diff. Mark phase complete only after every intended difference has evidence.

**Proof:** Candidate package changes are exhaustively accounted for without changing the starting oracle. Documents and tracking describe implemented behavior and retained authority rather than converting removed scope into proof.

## Phase 4 — Validate the immutable candidate and current customer

**Goal / assumption:** Final results execute the candidate rather than an old archive or concurrent editable checkout. Finish implementation, commit it, then bind all substantive acceptance to that identity. Covers SC11/SC13.

**Acceptance stencil — reuse existing runtime/customer tests:**

```python
assert provenance.codegen_commit == candidate_commit
assert imported_codegen_root == provenance.archived_codegen_root
assert final_license_skip_count == 0
assert current_customer_cases == {"ife_canonical", "ife_exploration", "mfe"}
assert all_unexpected_customer_results_have_reproduced_causes()
```

- [x] Commit the implementation candidate with path-specific staging; archive that codegen commit and committed companion dependency, build using existing build tooling without dependency sync, and record wheel/archive hashes and resolved source roots in `CODEGEN_EXECUTION_PROVENANCE`. Keep logs under `/tmp` and a concise durable evidence record with fresh/inherited separation. Existing dependencies include stock TEAx; do not use a fake runtime.
- [x] Run archived default tests with `-rs` under the independently established license: zero failures and zero license skips, with exact remaining skip identities/dispositions. Run archived all-snapshot live freshness, oracle replay, Ruff, mypy, ledger three modes, register/index, document-distinctness, gated-manifest, build, and whitespace checks. Use existing script help for exact arguments. Inspect index regeneration diffs rather than hiding them.
- [x] Run archived `pytest tests/execution -m execution -rs` from the Agentic/runtime environment with provenance bound to the candidate. Verify historical nine-exit numerical/report results and remaining-source mutations; record candidate/dependency/import identities with results.
- [x] Generate all three archived current-customer cases with candidate and baseline codegen under named dependencies. Compare complete package paths/bytes, fingerprints, stock-TEAx outputs, model-family mutation tests, and real handwritten preservation. Confirm expected MFE removed labels (68 at the recorded starting revision) and unchanged IFE labels; explain any count change due to coordinated customer revisions. Run relevant customer acceptance/family tests; reproduce every unexpected difference/failure and classify codegen, model, consumer/test expectation, or environment. Repair codegen regressions; coordinate isolated model/consumer repairs and rerun affected evidence, recording customer before/after commits and remaining unrelated cleanup.

**Proof / restart rule:** No material regression remains unattributed. A source, template, fixture, dependency, or runtime-affecting fix after the candidate freeze requires a new candidate/archive identity and affected acceptance reruns. Documentation-only evidence commits may follow with the tested ancestor named explicitly; never label that ancestor's runtime evidence as a newly tested commit.

## Phase 5 — Independent audit and completion record

**Goal / assumption:** Independent inspection catches omitted product/evidence obligations that implementers miss. Covers SC12 and final requirement reconciliation; it is not another implementation lane.

**Review stencil — no redundant new test framework:**

```text
For each spec criterion: name changed files, fresh evidence, and remaining bounds.
For each removed check: identify retired responsibility or functional replacement.
For each baseline/customer delta: inspect cause and exact accepted difference.
For each owner grade: preserve original source and closure/descoping authority.
Any unresolved material contradiction blocks completion.
```

- [x] Run `$my-audit` through a fresh independent reviewer against this spec, plan, final candidate diff, and durable evidence; include focused assurance/provenance review of C9/C10 and Item 8's single completion authority. Record `audit.md` and dispositions without self-certifying the implementation.
- [x] Fix material audit findings under the same bounded scope, check off completed plan actions immediately, and rerun only affected checks/candidate-bound evidence unless new uncertainty justifies broader reruns. Final audit must show no unresolved material regression, provenance, or requirement-disposition finding.
- [x] Update concise persistent current status and evidence/requirement dispositions. Recheck original index/drafts and concurrent customer state preservation. Keep the item open until its retained obligations are evidenced; subsequent close/pre-PR follow the project's record-then-delete rule, not an invented completed-folder archive.

**Proof:** Independently reviewed implementation and evidence meet the corrected contract; owner-descoped work remains accurately descoped and unrelated originals remain unchanged.

## Completion Notes

2026-10-08 partial Phase 1: committed immutable all-22 public oracle at `2c278f4`, 23 replay checks pass. Licensed all-22 assessment and exact pre-C4 capture are retained under `/tmp/pr-readiness-evidence/`; customer starting archive/generation is coordinated by root. [AGENT] Two preexisting quote-display/plural-input ordering recaptures are a documented bounded deviation: see `evidence.md`. Phase 2 C1/C6 complete at companion `dfd9169` / codegen `468b1af`, focused 65 pass and nine individually dispositioned missing historical parity goldens. Encoding/typing and unit/fixture owners are executing disjoint changes. Six oracle mutation checks pass without changing source files. Standalone design review was skipped for the reasons recorded in [design handoff](design.md#next-stage-handoff); the independent implementation audit remains required.

### Phase 2 encoding/typing completion — 2026-10-08

Codegen `5374a40` changes strict JSON encoding, existing generator types, and a pure metadata preflight before output clearing. Focused validation: 84 passed, mypy zero over 71 source files, touched Ruff and whitespace clean. Trusted verifier source/hash and version constants are unchanged. Live ±Inf overflow defaults and coherent sealed NaN/±Inf inputs prove named refusal before output mutation; no accepted live-model NaN spelling was established, so live NaN is an explicit parser-representation coverage bound rather than invented evidence. Real public calc/constraint/report generation and handwritten regeneration remain covered.

### Phase 3 oracle completion — 2026-10-08

The immutable starting oracle is retained. `reviewed_changes.json` carries only exact old/new file hashes: C3 eleven files per MFE fixture, C4 six named files, quote recapture zero files, preexisting plural-order recapture two files. All 29 candidate checks pass. Five actual template mutations (calc, multioutput, aggregation pipeline, constraint, report) and one renderer function mutation make fixed-manifest comparison fail. Mutation tests overlay templates/patch rendering in-process and restore automatically; source bytes never change. Snapshot oracle covers initial stub/auto generation, float multioutputs, aliases/aggregation, constraints/report; it does not claim preserved handwritten behavior or smart regeneration, supplied by `test_public_handwritten_preservation.py` and existing smart-regeneration tests, nor nonfloat runtime output behavior, supplied by `tests/execution/test_numeric_evidence_teax.py`.

### Phase 1 complete — 2026-10-08

Root froze customer `0e045fb30d9ba1b2f62b3a14b3c3fbfcb3985bc9` at `/tmp/pr-readiness-customer-baseline/source` (archive SHA-256 `1b15c5212dae15f6fe3c5466c050d007e2468ae3344b35222a4dd0c848daa220`). All 18 current generation units pass under archived starting codegen/companion: three principal cases plus 15 declared source collections. Both IFE packages execute stock TEAx with 35 outputs; MFE/additional units have generation-only baseline coverage, explicitly recorded. Three principal package file counts are 55/55/443. Receipts include all model and package hashes. Baseline sources and identities were frozen before source workers; starting generation used its independent old-code archive while edits proceeded. Immutable public oracle commit preceded all source changes. Unexpected preexisting freshness drift is explicitly dispositioned above, with dependent final snapshot checks still required.

### Phase 2 unit/fixture completion — 2026-10-08

`80273b6` removes all three guessed-unit paths and the inert historical driver. `8030e19` fixes three remaining obsolete test premises while retaining declaration-identity attachment, sealed-unit metadata collision refusal, and genuine public CLI refusal/preservation. Focused tests: 140 initial plus 85 follow-up passed. Historical source files match `fusion-tea 9e1ff87bb` byte for byte. Historical live recapture changes exactly one occurrence, twelve attributes, one calculation and graph counts `9/27/1/7` → `8/23/1/5`. C3 exact normalized graph comparison proves only unit labels changed (177 gated / 159 D5 serialized unit records); generated descriptions lose 29 label occurrences in each fixture, without semantic model-contract change. Editable stock-TEAx baseline11→candidate9 exits retain seven numeric outputs and constraint evaluation/report exactly, LCOE `270.1211779380445`; remaining-source mutations preserve every unrelated output. Final acceptance below separately executes archived candidate.

### Phase 4 underway — 2026-10-08

Production archive `80273b65f4832e398502e956099752a18870bd4e`, committed Agentic `dfd9169e266292b9320d2ad3102233b792ca251a` wheel, and stock TEAx `8d877460ac4f6f264561d916e40c1708adb13397` archive are bound in `/tmp/pr-readiness-artifacts/execution-provenance.json`. Cached existing Hatchling dependencies built both wheels without installation or virtualenv/cache writes. Archived real-TEAx lane: 96 passed. Archived licensed all-snapshot freshness: 22 tracked / zero stale, regenerating D5 in scratch. Default tests use a separate `8030e19` archive with its test-only fixes and archived companion source for documentation contracts. Current customer comparisons cover all 18 generation units; principal-family runtime/mutation/preservation checks remain in progress.

### Phases 3 and 4 complete — 2026-10-08

All bounded changes and record reconciliation are committed; the durable source-identity reconciliation lives at `.project/reference/source-identity-reconciliation.md`. Final archived candidate `0046fa1`: licensed default 2,207 passed / nine explicitly dispositioned historical parity-golden skips / 96 deselected / zero failures and license skips; real-TEAx 96 passed. All 22 licensed snapshots are fresh at the identical production source ancestor, including regenerated D5. Public oracle 29 passed including six effective mutations. Matrix 313 requirements / 35 families / 77 active test files; mypy zero / Ruff pass; register/distinctness/gated/matrix focused 36 pass; index regeneration produces no diff; both wheels build; actual snapshot help and whitespace pass. All three principal customer cases have stock runtime/mutation/preservation evidence; all 18 current units have complete generation comparisons. Exact customer consumer-test repairs remain isolated and committed.

The full replacement gate exposed three stale proof references at `0046fa1`. `bb39824` retargeted the two renamed functional nodes and removed the extra conftest EOF line. The first consumed-runbook disposition lacked a named proof and the existing ledger invariant correctly rejected it. `1175f2c` preserves that invariant by naming the current ledger-record guard with the original retirement authority; patch-application responsibility remains retired. Both failed receipts are retained. The repaired original checker policy checks all 302 codegen rows and exits zero: 223 real passing row proofs are reused only after source/fixture/script/test identity checks, conftest AST equivalence, and unchanged proof-coordinate validation; changed references and ledger/register/matrix dependencies run fresh (ten subprocess probes). A further 74 affected checks pass; ledger paths checks 304 rows / zero problems and surface zero breakages. See `final-checks.json` and `final-ledger-receipt.json`. Later ledger/whitespace/evidence metadata does not claim a new broad suite or runtime run; fully tested source ancestors are named explicitly. Independent audit owns Phase 5.

### Independent audit and coordinator completion — 2026-10-08

The fresh audit certifies the bounded cleanup with no unresolved material findings; the independent product lens is CLEAR. All plan actions are complete. Original index bytes and all 17 protected mental-alignment draft hashes were rechecked unchanged. Companion and customer repairs are preserved as local branches without checkout changes; the final codegen branch is imported after this completion record. The original source checkout and concurrent customer worktree remain untouched. Item 8 and the epic retain their own open closure authority. Close and post-close pre-PR remain the next human-controlled stages.
