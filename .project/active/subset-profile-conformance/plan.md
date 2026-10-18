# Implementation Plan: Independent conformance corpus and per-site codes (EXEC-SUBSET-CONTRACT Item 2a)

**Status:** Implementation in progress (Phases 1–4 done; Phases 1–2 audited mid-run; Phases 3–4 not yet audited; Phase 5 next)
**Created:** 2026-10-18
**Last Updated:** 2026-10-18

## Source Documents

- **Spec:** [spec.md](spec.md)
- **Design:** [design.md](design.md), revision 3, approved for planning. Component details, decisions D1–D15, the agreement rule and the invariants live there; this plan links to them and does not repeat them.
- **Spike S1:** [spikes/s1/findings.md](spikes/s1/findings.md) (P0, done). **Owner gates:** [briefs/align.md](briefs/align.md) (RG-1..3).

## The Point

**[INFERRED]** (ratified by owner, 2026-10-18, spec brief and `briefs/align.md`) Prove, with evidence independent of the screen, that the shared subset contract in agentic-mbse matches what this generator actually does, and make drift between them fail a test in sysml-codegen. Test volume is not the goal, and neither are tests that check the screen against itself.

Why: Item 1 checked the contract once, against 80 probe runs of codegen `b5663c07`. Nothing fails today when the generator changes, so a relaxed or added refusal leaves the contract stale with every test green. Items 2b, 3 and 5 will tell modelers what will generate on the strength of this contract, so it has to be held to the generator mechanically.

Two owner constraints bound every phase:
- **[NEED]** RG-1 (any change to what the generator accepts or refuses), RG-2 (String policy) and RG-3 (merges, PRs, filing ADRs and product amendments) are the owner's. This plan produces candidates, recommendations and staged text for them and never acts on them.
- **[NEED]** (P-0003, owner-verbatim: "we do NOT create workarounds to accept bad models -- we follow what KerML, SysMLv2 and SysIDE support") Every recommendation follows the language.

## Implementation Strategy

**Phasing rationale.** The design fixes seven phases (design.md § Next-Stage Handoff). This plan keeps them and their numbers, and splits the two big ones into numbered steps with their own commit points so each step can be audited alone. The order follows three dependencies:
1. **Reasons before the mutations that compare them** (S1). A generator mutation passes only when the witness's stored reason or stub cause changes, so a site's `SiteReason` must exist before its mutation test. The carrier mechanism lands in P1; shared-rule sites get reasons in P2, stub causes in P4, R3-row sites in P5, tail sites in P6.
2. **Cases before the tests that need cases.** The mapping-witness test and occurrence parity over cases land in P2, when the packaged cases exist (O19). R3-row cases are built in P3 and become P5's witnesses.
3. **Group E's tail behind the split point.** P6 starts only after the counted trigger at P5's close (§ Split point below).

**Critical path.** P1.1 baseline → P1.3 reason carriers and harness → P2.1 packaged cases and `case:` citations → P2.4 shared-rule reasons and mutations → P3 agreement → P4 silent losses → P5 head → split count → P6 tail → P7 final gate run, receipt and checks.

**First proof point.** P1.3's `test_site_reason_reaches_harness.py`: a `SiteReason` set at a raise site appears in the harness's `extra={"refusal": …}` observation, for every carrier type and every converter branch in `orchestration/elaborated_pipeline.py`. If that fails, every later mutation test fails in a way that looks like shadowing, so it is proved first.

**Overall validation approach.**
- Each step starts with its tests.
- Each step ends with an exact command that proves it done. Licensed commands run after `set -a; source ../agentic-mbse/.env; set +a` (from the codegen worktree root) and pass `-rs` so skips are listed; a license-gated test counts only if it ran (spec Independence).
- Every phase close runs the **phase gate** (below), which guards invariants 9 and 10 and the Item 4 merge-order risk.

## Repositories and paths

- **codegen** = sysml-codegen worktree `/home/reid/src/subset-conformance/sysml-codegen`, branch `subset-conformance`. Plan written at `d73a4fc5`.
- **agentic** = agentic-mbse sibling worktree `/home/reid/src/subset-conformance/agentic-mbse`, branch `subset-conformance` (base `ccd57d83` plus epic commits). Commands run there use `uv run` from that directory.
- **Never touch** `/home/reid/src/agentic-mbse` (concurrent Item 4 session, branch `positional-binding-check`) or `/home/reid/src/sysml-codegen`.
- **This folder** = `.project/active/subset-profile-conformance/` in codegen. Evidence goes to `evidence/` here. Nothing writes into agentic-mbse's archived Item 1 folder.

## Plan decisions

All **[AGENT] (plan, 2026-10-18)**. They settle what the design left open for the plan (design.md § Next-Stage Handoff, "Open for the plan") and what the brief asked to decide. Challenge by re-deriving against the reason.

| # | Decision | Reason |
|---|---|---|
| PD1 | P1 runs as six steps in the order 1.1 baseline → 1.2 scripts → 1.3 reason carriers and harness → 1.4 scanner and account → 1.5 group A → 1.6 staged amendments. P2 runs as four steps (2.1–2.4). | The baseline must precede any change. The scripts change must precede the pre-existing-failure run, which uses `codegen_suite.py`. The reach test is the first proof point. |
| PD2 | P3, P4 and P5 run in that order, not in parallel. | The design lets them run after P2 in any order, but P5's R3-row witnesses are the cases P3 builds, and P4 assigns the stub-cause reasons P5's count includes. One implementer gains nothing from parallel order. |
| PD3 | The agreement function, `disagreements.json`, its reader and the D3 writer guard land in P2.1. The tests over all subjects (C1–C3) land in P3. | Screen mutations (P2.4) are judged by agreement, and the capture helper refuses a screen answer that fails agreement without a matching entry (D3). Both need the function and the file in P2. |
| PD4 | **Head and tail are decided by columns of the moved codegen account.** Head = rows with a non-empty `rule` or `matrix_row`, plus every row in `extraction/calc_compat_renderer.py` (the stub family, which P4 must witness per cause). Tail = every other `public_capability` or `unknown` row. In P1.4 the move fills `matrix_row` for the unknown sites the spec's R3 table names: `extraction/binding_source.py:236, :243, :251` → `PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS`; `elaboration/project.py:812` → `PUSH-DOWN-AGG-PROFILE-SUM-SHAPE`. agentic-mbse's account does the same for `reference_use.py:545, :557, :594, :618`. | The design defines the tail by these columns (§ E). The stub-family sites have no row but their reasons land in P4, before the split. Without this rule they would count as tail work that is already done. |
| PD5 | The E3 test is two tests. `test_site_reasons.py` (from P2) checks every row that has a `reason`: the raise passes it, and every witness site ID resolves. `test_site_account_completeness.py` (P6) requires every `public_capability` row to have a reason and a witness. agentic-mbse's witness check is split the same way: linked rows from P2, all public rows from P6. | A completeness test landed in P2 would stay red until P6, or need a pending list, which is an escape hatch. Splitting keeps every landed test green and makes the tail's gate a single named test. |
| PD6 | **Shared-table sites in `executable_profile.py`.** The 19 sites in the expression walkers (`_walk_arithmetic`, `_walk_value`, `_walk_comparison`, `_walk_proposition`, lines 542–852) are the shared decision table: they get witnesses, not mutations. The 3 sites in `_evaluate_usage_against_definition` (993, 1014, 1022) are usage and definition context logic: they are mutated through the 3 named hand patches, tagged `shared`. `reference_use.py:443, :514, :702` are mutated and tagged `shared`; the table `invocation_allowlist.py` is not. | The spec names `executable_profile.py` as the predicate-eligibility table (Independence). The walkers decide eligibility per expression node, which is the table. The usage-level function decides by attachment and definition, which is context. This matches the design's choice of those three for hand patches. |
| PD7 | **`SiteReason` and `GenerationCode` members.** `GenerationCode` members are exactly today's `CodeGenerationError` message prefixes, found in P1.3 by `grep -rn 'CodeGenerationError(' src/`. `SiteReason` members are snake_case `<stage>_<condition>` (for example `occurrence_containment_unanchored`), minted in the step that assigns them. Members are named before their mutation test is written. Known shadowing pairs get distinct members: `occurrence.py:180` (ES-002) vs `elaborate.py:2345` (ES-009), and `calc_compat_renderer.py:78` vs `:81`. | Minting all members up front would guess at sites not yet read. The two shadowing pairs are known from S1 and must not collide (B6). |
| PD8 | **CALC-USAGE-BARE-RESULT-DROP seam:** the usage's `CalcNode` in the instance graph, found by the usage's `DeclarationId`; the case asserts that its output set has no entry for the bare result. The control is the same usage with a named `return r`, whose output is present. | This is the design's § D table row, confirmed here as the exact seam. It needs no snapshot change and no text search. |
| PD9 | **Case list and homes.** A case is packaged in agentic-mbse when a record cites it or it tests a shared rule's recognizer; otherwise it lives in codegen (D14). IDs follow D1. No separate case manifest: the case set is the union of the two stores, and the P2.1 store test (exactly one generator answer per case, no ID in both homes) is what makes it total. Each step below names the case families it adds. | A third list of IDs would be one more thing to keep in sync. |
| PD10 | **G2 probe in P1.1; `kerml-expert` for G1 and G2 together in P4.** The probe runs the spike harness (`spikes/s1/harness.py`) on one minimal model at the baseline revisions, before any change, so it records the pinned generator's behavior. It decides whether P4's G2 case asserts a silent loss or a refusal. G1 and G2 go to one `kerml-expert` invocation in P4, as two questions, once both case models exist, because both ask how a redefining usage's multiplicity bounds are determined, and the RG-1 recommendation for both is written in P4. Other candidates get their `kerml-expert` question at the end of the phase that produces them. P7 checks that every candidate has one. | The harness already exists, so the probe costs one model and one run. Running it later would mean P4 builds the case before knowing what it asserts. Asking `kerml-expert` at candidate creation lets the recommendation cite the answer, rather than being rewritten in P7. |
| PD11 | **Baseline method.** Record at HEAD in both repos first. Then decide pre-existing failures by rerunning at the 2a bases (codegen `b5663c07`, agentic `ccd57d83`) in isolated exported trees. agentic-mbse's own suite at `ccd57d83` is run only if its HEAD baseline has failures. | A failure present at both bases predates 2a. One present only at HEAD came from epic commits after the base, and is named as such. |
| PD12 | All agentic-mbse script output paths become parameters in P1.2, in one commit: `codegen_suite.py`, `run_trees.py`, `render_matrix.py`, `validate_diff.py`, `scan_sites.py`. | Spec Boundaries: the scripts are reused only after their output path is a parameter. One commit makes "nothing writes into the archive" auditable at once. |
| PD13 | `SUBSET_PROFILE_VERSION` moves to `subset-profile/v2` in P2.1, at the first record change, and stays `v2` to merge. The digest test is updated with every later record change. | design.md § Implementation Notes. |
| PD14 | `RG1-<n>` IDs are allocated in order of creation in `rg1-recommendations.md`. Each entry holds the question, the case IDs, today's behavior, the `kerml-expert` answer and a recommendation. | D3's test requires an `RG1-<n>` on every `rg1_pending` entry; one allocator avoids collisions. |
| PD15 | agentic-mbse's suite runs with its default marker set (`uv run pytest tests/`) at P1 and P7 alike. | The baseline and the final run must be the same command to be comparable. |

## Owner-gate stops

Each row produces an artifact and the phase **continues**. Nothing in this plan changes what the generator accepts or refuses, decides String policy, merges, opens a PR or files an ADR.

| Gate | Artifact | Phase |
|---|---|---|
| RG-3 | `adr-0012-amendment.md`, `adr-0001-amendment.md`, `p0001-amendment.md`, `adr-0016-amendment.md` (D12), `adr-fact-placement-draft.md` (codegen half of D14) | P1.6 |
| RG-1 | `rg1_pending` disagreements from R3 rows (ES-010 refusal side if judged semantically wrong, any screen-refuses-generator-builds case under spec Gates L3-6) | P3 |
| RG-1 | candidate refusals: CALC-USAGE-BARE-RESULT-DROP, each stub cause, G1, G2 | P4 |
| RG-2 | `rg2-string-policy.md` | P4 |
| RG-1 | O8 plain-exception candidates found among head sites | P5 |
| RG-1 | O8 plain-exception candidates among tail sites | P6 |
| RG-3 | the coordinated merge; the `pre_pr` check that the receipt's `codegen_rev` matches the merging codegen head (D13) | after P7, owner's |
| — | split taken at P5's close: the orchestrator tells the owner | P5 close |

## The phase gate (run at every phase close)

- [ ] **Snapshots byte-stable (invariant 9).** codegen: `git diff --exit-code d73a4fc5 -- ':/tests/fixtures/*/instance_graph_snapshot.json'` exits 0 (22 files).
- [ ] **Accept/refuse unchanged (invariant 10).** codegen, licensed: `uv run --extra dev pytest tests/conformance/test_public_package_oracle.py tests/conformance/test_v6_recapture_batch.py -rs` passes. Any diff to `tests/expectations/public_package_oracle/baseline.json` or `tests/fixtures/v6_recapture_batch/batch.json` changes message text only, and is listed in `evidence/changed-outputs.md` with its cause.
- [ ] **No regressions against the baseline.** codegen licensed suite and agentic-mbse suite, compared by test ID with `evidence/baseline.md`. A new failure is fixed before the phase closes. From P2 on, agentic-mbse runs with all extras installed (`uv run --all-extras pytest tests/ -q -rfEs`), and its pre-existing set is the 5 IDs of the all-extras baseline (3 Pandoc, 2 hardcoded `/home/reid/1cfe` path); the 129-ID default-extras set is history.
- [ ] **Item 4 merge order.** In agentic: `git log --oneline subset-conformance..main`. If `main` has new commits touching `src/agentic_mbse/sysml/` or `src/agentic_mbse/errors.py`, rebase `subset-conformance` onto it, rerun this phase's tests and note it in Implementation Notes. Same check in codegen against `main`.
- [ ] **Static checks.** codegen: `uv run --extra dev mypy src/` and `uv run --extra dev ruff check src/ tests/`. agentic: `uv run mypy src/` and `uv run ruff check src/ tests/`. Compared with the baseline.
- [ ] **Audit.** `/_my_audit` reviews every diff to stored answers, `disagreements.json`, `REASON_MAPPING` and the site account as the named reviewer (spec Independence).

---

## Phase 1: Baseline, carriers, harness, inventory foundation, group A

### Goal

Fix the starting point, then build everything later phases stand on: the reason carriers, the observation harness, the ported scanner and account, the pin and mapping, occurrence parity, and the staged amendment texts.

### Assumption under test

That a `SiteReason` set at a raise site survives the live route's rebuild (`orchestration/elaborated_pipeline.py:289-455`) and reaches `run_codegen`'s log observation, and that adding it changes no snapshot byte and no accept/refuse outcome.

### Step 1.1: Baseline and G2 probe (no code changes)

**Repos:** both, read-only; writes only to this folder.

- [x] Record revisions: codegen `git rev-parse HEAD`; agentic `git rev-parse HEAD`; SysIDE version; `agentic_mbse.__version__`.
- [x] codegen licensed suite: `uv run --extra dev pytest tests/ -q -rfEs -p no:cacheprovider --junitxml=/tmp/subset-2a/baseline-codegen.xml`. Expected from S1: 2735 passed, 9 skipped, 10 failed.
- [x] agentic licensed suite: `uv run pytest tests/ -q -rfEs --junitxml=/tmp/subset-2a/baseline-agentic.xml`.
- [x] Static checks in both repos (commands in the phase gate).
- [x] **G2 probe** (PD10). Write `spikes/g2/model.sysml`: a part definition with a referenced multiplicity bound, and a usage that overrides it. Run it through `spikes/s1/harness.py`'s generator half. Record occurrence count, codes and the definition-bound control in `evidence/g2-probe.md`.
- [x] Write `evidence/baseline.md`: pass, fail and skip by test ID in both repos, with each skip's reason.

### Step 1.2: Scripts take output parameters; pre-existing failures decided

**Repos:** agentic (scripts), codegen (evidence).

Test first: agentic `tests/test_subset_profile_scripts.py` (new, pure) asserts that `codegen_suite.py run` requires `--out` and `--codegen-rev`, that no script in `scripts/subset_profile/` names `.project/completed/` as a literal, and that `isolated_tree.py` exports the seven helpers `codegen_suite.py` imports.

- [x] `scripts/subset_profile/isolated_tree.py` (new): move `build_tree`, `child_env`, `read_identity`, `read_license_key`, `resolve_rev`, `sibling_state`, `IsolationBreachError` from `probe.py` (design.md D13). `probe.py` stays until P2.1 retires it, importing from `isolated_tree.py`.
- [x] `codegen_suite.py`: `--codegen-rev` replaces `PINNED_CODEGEN_REV`; `--out` replaces the archive path (`:43-50`); `--select` defaults to `tests/conformance/subset_profile`. No receipt writing yet.
- [x] `run_trees.py`, `render_matrix.py`, `validate_diff.py`, `scan_sites.py`: output path is a required parameter (PD12).
- [x] **Pre-existing run** (PD11): `uv run python scripts/subset_profile/codegen_suite.py run --agentic-rev ccd57d83 --codegen-rev b5663c07 --label baseline-2a --select tests/ --out /tmp/subset-2a/preexisting`. For each of the 10 known failures, record whether it fails at the bases.
- [x] For `tests/unit/test_check_ledger_4a.py` (9 failures): also run `git cat-file -e 1672c57^{commit}` and `git cat-file -e 07531e64^{commit}` in codegen and record whether the commits exist. A missing commit makes it an environment failure, not a 2a one.
- [x] For `test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees`: record whether `project_templates/MODELING_PROCESS.md.template` differs between agentic `ccd57d83` and HEAD (`git diff ccd57d83 HEAD -- project_templates/MODELING_PROCESS.md.template`).
- [x] If agentic's HEAD baseline had failures, export `ccd57d83` with `git archive` into `/tmp/subset-2a/agentic-ccd57d83` and run its suite there.
- [x] Add a "Pre-existing" table to `evidence/baseline.md`: test ID, fails at bases (yes/no), cause.

**Done when:** agentic `uv run pytest tests/test_subset_profile_scripts.py tests/test_subset_probe_judge.py -q` passes, and `evidence/baseline.md` classifies all 10 failures.

**Commits:** agentic "Item 2a P1.2: subset_profile scripts take output paths; helpers move to isolated_tree.py". codegen "Item 2a P1.1–1.2: licensed baseline, pre-existing failures, G2 probe".

### Step 1.3: Reason carriers, refusal observation, harness, reach test

**Repo:** codegen.

Test stencil (write first):

```python
# tests/conformance/subset_profile/test_site_reason_reaches_harness.py  (licensed)
@pytest.mark.parametrize("witness", REACH_WITNESSES, ids=lambda w: w.branch)
def test_reason_set_at_site_reaches_harness(witness):
    obs = observe.generator_half(witness.model_root)        # run_codegen, screen tripwired
    assert not obs.generated
    assert witness.reason in {r.reason for r in obs.refusals}  # from extra={"refusal": ...}

# tests/conformance/subset_profile/test_committed_snapshots_have_no_diagnostics.py  (pure)
@pytest.mark.parametrize("path", COMMITTED_V6_SNAPSHOTS)      # all 22
def test_sealed_graph_diagnostics_empty(path):
    assert decode_snapshot(path).graph.diagnostics == ()
```

`REACH_WITNESSES` has one entry per carrier type (`ReadinessFinding`, `Diagnostic`, `ElaborationInvariantError`, `CodeGenerationError`, `ExactTypeError`, `ExpressionInventoryError`) and per converter branch (`orchestration/elaborated_pipeline.py:289-356`, `_readiness_with_referent` `:399`, `_semantic_evidence_diagnostic` `:419`, `_diagnostic_with_referent` `:438-455`). Pick each witness from an existing fixture or Item 1 probe; prefer a shared-rule site so its reason counts toward P2. A branch with no reachable witness is listed by name in the test module with the attempt made.

Changes (design.md D2, D8, D15):
- [x] `elaboration/diagnostics.py`: `SiteReason` (PD7), with only the members the reach witnesses need. Pure test: disjoint from `SUBSET_REASON_CODES`.
- [x] `core/errors.py`: `GenerationCode` (today's prefixes, PD7); `CodeGenerationError` gains `code` and `reason`; message text unchanged.
- [x] `reason: SiteReason | None` on `ReadinessFinding`, `ElaborationInvariantError`, `CompilationError`, `ExactTypeError`, `ExpressionInventoryError`, and on `Diagnostic` with default `None`.
- [x] `orchestration/elaborated_pipeline.py`: every converter copies `reason` (O17). `_semantic_evidence_diagnostic` reads a total `SemanticEvidenceCode → SiteReason` table (pure totality test).
- [x] `elaboration/elaborate.py:133, :194`: messages end in ` (reason: <id>)` when a reason is set.
- [x] `snapshot/instance_graph.py:947`: the encoder refuses a `Diagnostic` with a reason set; output otherwise unchanged. Unit test for the refusal.
- [x] `cli/__init__.py:1189-1230`: every refusal log call gains `extra={"refusal": …}` (codes, reasons, locations); the `except Exception` branch carries the converted `unexpected_public_failure`. Unit test beside `tests/unit/test_cli_generation.py:348`.
- [x] `tests/helpers/subset_profile/observe.py`: generator half (run `run_codegen`, tripwire on the three screen entry points, read `extra`, spy on `elaborate_model_paths`, read `model_contract.json`) and screen half. `tests/helpers/subset_profile/cases.py`: answer schema (Appendix A) and loading only; agreement comes in P2.1.

**Done when:** licensed `uv run --extra dev pytest tests/conformance/subset_profile/ tests/unit/test_cli_generation.py tests/conformance/test_snapshot_v6_envelope.py -rs` passes with zero skips of license-gated tests, and the phase-gate snapshot and oracle checks pass. Changed refusal text (the reason suffix) is listed in `evidence/changed-outputs.md`.

**Commit:** codegen "Item 2a P1.3: SiteReason/GenerationCode carriers survive the live rebuild; run_codegen logs structured refusals; harness".

### Step 1.4: Scanner port, account move, E1, E2

**Repos:** codegen (port, account, tests), agentic (narrowing). One commit in each, made together.

Test stencil:

```python
# tests/conformance/subset_profile/test_site_account.py  (pure, E1)
def test_every_scanned_site_has_one_row_and_every_row_a_site():
    scanned = site_scan.scan(SRC)
    rows = site_scan.load_account(ACCOUNT)
    assert scanned.ids() - rows.ids() == set(), "sites with no row"
    assert rows.ids() - scanned.ids() == set(), "rows with no site"
    assert site_scan.code_generation_errors_without_code(scanned) == []   # D15

# tests/conformance/subset_profile/test_site_scan_mutations.py  (pure, E2)
@pytest.mark.parametrize("snippet", [NEW_RAISE_PER_FORM, NEW_EXCEPTION_CLASS, NEW_RAISING_HELPER, COMPUTED_CODE_MAP])
def test_synthetic_site_detected_or_reported_unrecognized(snippet, tmp_path): ...
```

- [x] `tests/helpers/subset_profile/site_scan.py`: port of `scan_sites/1` codegen half, plus `unrecognized` for every other `raise` under `src/sysml_codegen/`, plus agentic-mbse site-ID resolution from the installed package source (design.md D7, § E).
- [x] `tests/expectations/subset_profile/site_account.csv`: the 441 codegen rows, plus a `reason` column, plus a row for each `unrecognized` site with its role. Apply PD4's `matrix_row` fills. The header lists the remaining blind spots.
- [x] Fold `tests/conformance/test_diagnostic_provenance_sites.py:44-95` into a query over `site_scan.py` output.
- [x] `tests/conformance/subset_profile/test_site_reasons.py` (PD5, first form): every row with a `reason` is passed by its raise. It covers the P1.3 reach witnesses.
- [x] agentic: `site_account.csv` drops the 441 codegen rows and gains PD4's `matrix_row` fills for its 4 chain-segment sites; `matrix.toml` drops codegen `sites` lists; `scanner.toml` and `scan_sites.py` cover agentic-mbse only; `tests/test_subset_matrix.py`, `tests/test_subset_site_account.py`, `tests/helpers/subset_matrix.py`, `subset_site_account.py` updated (Appendix B).
- [x] **Record the split counts' denominators** (§ Split point): H and T from the moved accounts, in Implementation Notes.

**Done when:** codegen `uv run --extra dev pytest tests/conformance/subset_profile/test_site_account.py tests/conformance/subset_profile/test_site_scan_mutations.py tests/conformance/subset_profile/test_site_reasons.py tests/conformance/test_diagnostic_provenance_sites.py -q` and agentic `uv run pytest tests/test_subset_matrix.py tests/test_subset_site_account.py -q` pass.

**Commits:** codegen "Item 2a P1.4: site scanner and codegen site account move to sysml-codegen (E1, E2)". agentic "Item 2a P1.4: site account and matrix narrow to agentic-mbse sites".

### Step 1.5: Group A — pin, mapping, renderer, occurrence parity

**Repos:** codegen; agentic (occurrence retirements).

Test stencil:

```python
# tests/conformance/subset_profile/test_reason_mapping.py  (pure)
def test_mapping_keys_equal_subset_reason_codes():
    assert set(REASON_MAPPING) == set(SUBSET_REASON_CODES)

@pytest.mark.parametrize("record", load_rule_records(), ids=str)
def test_record_expected_code_is_among_its_reason_codes(record):
    assert record.expected_code in REASON_MAPPING[record.reason].codes()

# tests/conformance/subset_profile/test_occurrence_parity.py  (licensed)
@pytest.mark.parametrize("root", SEED + CORPUS_37, ids=str)
def test_agentic_summary_equals_codegen_index(root):
    assert normalize_agentic(root) == normalize_codegen(root)
```

- [x] `_upstream_pins.py`: `SUBSET_PROFILE_VERSION` (still `v1` here); `tests/conformance/test_upstream_pins.py` extended.
- [x] `src/sysml_codegen/subset_profile_adapter.py` (new): `REASON_MAPPING`, `SubsetDiagnostic`, `render_finding`, the import-time profile check (design.md § A, D12). Tests: keys, `NO_REFUSAL` exactly when no record refuses the shape, `expected_code` membership, renderer unit test per reason, import-boundary test (nothing on the generate route imports the adapter).
- [x] Occurrence parity (D6): move the 34 seed models to `tests/fixtures/subset_profile_occurrence_seed/<case>/`; `tests/helpers/subset_profile/occurrence_parity.py` normaliser; the licensed test over seed plus the 37 corpus fixtures, failing by name on a missing input; the companion mutation test patching `_multiplicity_indices` (`elaboration/occurrence.py:812`).
- [x] agentic: remove `tests/test_sysml/test_occurrence_parity.py`, `tests/fixtures/subset_profile/occurrence/`, `tests/helpers/occurrence_oracle_schema.py`, `scripts/subset_profile/occurrence_oracle.py`, `occurrence_parity.py`, `occurrence_port_run.py`.
- [x] `evidence/versioning.md`: no version identifies the contract; `SUBSET_PROFILE_VERSION` does (D12, criterion A2). State how it was checked (`agentic_mbse.__version__` before and after; tags and package index not checked unless done here).

**Done when:** codegen licensed `uv run --extra dev pytest tests/conformance/subset_profile/ tests/conformance/test_upstream_pins.py -rs` passes, and agentic `uv run pytest tests/test_sysml/ -q` passes.

**Commits:** codegen "Item 2a P1.5: subset pin, reason mapping, finding renderer, occurrence parity owned by codegen". agentic "Item 2a P1.5: occurrence parity seed and oracle retire to sysml-codegen".

### Step 1.6: Staged amendments (RG-3, record and continue)

**Repo:** codegen, this folder only.

- [x] `adr-0012-amendment.md` from the archived draft; its "until Item 2 lands" invariant names `tests/conformance/subset_profile/test_occurrence_parity.py` and the pre-merge run (design.md § A).
- [x] `adr-0001-amendment.md` (design.md § Cross-repo enforcement) and `p0001-amendment.md` (O20).
- [x] `adr-0016-amendment.md` (D12) and `adr-fact-placement-draft.md`, the codegen register's half of D14 and the split enforcement of invariant 1.

**Done when:** each file exists, states its target file and line, and ends "Filing: owner, at merge (RG-3)".

**Commit:** codegen "Item 2a P1.6: stage ADR 0001/0012/0016 and P-0001 amendments for the owner".

### What we know works after Phase 1

The baseline and its pre-existing failures are recorded. A reason set at a site reaches the harness on every converter branch. The codegen inventory is total over `raise`, and its account is codegen-owned. The pin, mapping and occurrence parity are tested. Snapshots and accept/refuse are unchanged.

---

## Phase 2: Group B — packaged cases, `case:` citations, contract v2, shared-rule reasons and mutations

### Goal

Replace the 80 probes with packaged conformance cases, hold the generator to every case live, and prove each shared rule's detectors matter by mutation.

### Assumption under test

That codegen can read case models, screen answers and records through agentic-mbse's package alone (B4), and that every shared-rule site's mutation changes its witness's stored reason (B2, B6).

### Step 2.1: Packaged cases, citations, v2, case store

**Repos:** agentic, codegen. Commit both together.

Test stencil:

```python
# agentic tests/test_subset_case_citations.py  (pure, D4)
@pytest.mark.parametrize("record, citation", case_citations(load_shipped_records()), ids=str)
def test_cited_case_is_packaged_and_shows_its_pair(record, citation):
    case = load_packaged_case(citation.case_id)          # importlib.resources
    assert record.pair in {f.pair_with_outcome for f in case.screen.findings}

# codegen tests/conformance/subset_profile/test_case_store.py  (pure)
def test_every_case_has_exactly_one_generator_answer_and_one_home():
    packaged, local, answers = cases.packaged_ids(), cases.codegen_ids(), cases.answer_ids()
    assert packaged.isdisjoint(local)
    assert answers == packaged | local
```

- [x] agentic: move the 80 probe models to `src/agentic_mbse/sysml/subset_cases/<id>/` with `case.json` (`schema: subset-case/1`, construct, screen answer, `agentic_site_witnesses`, `provenance.from_probe`); retire `observation*.json`. Check `pyproject.toml:49-63` ships `*.sysml` and `case.json`.
- [x] agentic: loader accepts `case:` by form only, rejects `probe:` (`subset_profile.py:396-409`); records cite `case:<id>`; `tests/helpers/subset_records.py:85, :101` switch to `case:<pair>`; retired shapes leave records, rule and `SUBSET_REASON_CODES`; `v2` and the digest test (PD13); vocabulary, records and version tests updated.
- [x] agentic: repoint `test_subset_profile_rules_{instantiation,modelwide}.py` to packaged cases; remove `tests/test_subset_probe_evidence.py`, `tests/test_subset_probe_judge.py`, `tests/helpers/subset_probe_judge.py`, `scripts/subset_profile/probe.py`.
- [x] codegen: pin to `v2`; mapping drops retired reasons; `cases.py` gains packaged-case loading, the agreement function (design.md § C) and the `disagreements.json` reader (PD3); `tests/expectations/subset_profile/disagreements.json` created by hand (empty or with entries the captures need); D3 writer-guard test.
- [x] codegen: capture the 80 stored generator answers with the capture helper (writes generator blocks only; refuses a failing screen answer without an entry). Review each diff.
- [x] codegen licensed `test_generator_half.py`: every case's live generator half equals its stored answer, and case isolation holds (refusal locations inside the construct lines, after `root-N/` normalisation).

**Done when:** agentic `uv run pytest tests/test_subset_case_citations.py tests/test_sysml/ -q` and codegen licensed `uv run --extra dev pytest tests/conformance/subset_profile/ -rs` pass. Manual: `uv build --wheel` in agentic, and the wheel listing contains `agentic_mbse/sysml/subset_cases/`.

**Commits:** agentic "Item 2a P2.1: probes become packaged conformance cases; records cite case:; contract v2". codegen "Item 2a P2.1: stored generator answers for packaged cases; case store, agreement function, disagreement record".

### Step 2.2: New cases and unconfirmed pairs

**Repos:** agentic (packaged cases, `unobservable`), codegen (answers, codegen-home cases).

- [x] Case families per rule, where they apply (spec B4): near-neighbor, inherited and redefined contexts, alternate spellings, template versus instance. dc3 `proto3`, `proto4nest`, `conv` rebuilt as minimal models from a pinned dc3 export (record the dc3 revision).
- [x] One case per R3 § 3 `unconfirmed` pair (spec R3 rows table). Observed → record moves to its outcome. Unobservable → record keeps `unconfirmed` and gains `unobservable = {context, reason, evidence = ["case:…"]}`; agentic loader and records test learn the field.
- [x] `observe.py` seams: `graph_attr`, `entry_point`, `catalog_usage`, `calc_compilability`, `occurrences`, by `DeclarationId` (D9). Needed here for `omitted`/`excluded` pairs, including the three site rules' `other_expression_site`.
- [x] Record-coverage pure tests (design.md § B): refused pair → refusing case; refused shape → non-refused case or SA-1; `omitted`/`excluded` pair → seam-asserting case.

**Done when:** codegen `uv run --extra dev pytest tests/conformance/subset_profile/test_record_coverage.py -q` and the licensed generator-half test pass; agentic `uv run pytest tests/test_subset_case_citations.py tests/test_sysml/ -q` passes.

**Commits:** agentic "Item 2a P2.2: neighbor, context and dc3-shape cases; unconfirmed pairs observed or marked unobservable". codegen "Item 2a P2.2: answers and seams for new cases; record coverage".

### Step 2.3: Tripwire, fixture classes, mapping witnesses, parity over cases

**Repo:** codegen.

- [x] `test_tripwire.py` (licensed): the three screen entry points patched to raise wherever bound; every case's generator half still yields its stored outcome. 2b inherits it.
- [x] `tests/expectations/subset_profile/fixture_classes.json` and `test_fixture_classes.py` (pure): every directory under `tests/fixtures/` is a model root, inside one, or a container, with exactly one class source (design.md § B).
- [x] `test_reason_mapping.py::test_every_mapping_pair_has_a_witnessing_case` (O19).
- [x] Occurrence parity extended to every case whose summary has nodes.

**Done when:** licensed `uv run --extra dev pytest tests/conformance/subset_profile/ -rs` passes.

**Commit:** codegen "Item 2a P2.3: screen tripwire, fixture classification, mapping witnesses, parity over cases".

### Step 2.4: Shared-rule reasons, witnesses and mutations

**Repos:** codegen; agentic (`agentic_site_witnesses` in `case.json`).

Test stencil:

```python
# tests/conformance/subset_profile/test_generator_mutations.py  (licensed)
@pytest.mark.parametrize("site", mutate.sites_with_witnesses(scope="shared_rule"), ids=str)
def test_neutralising_site_changes_witness_reason(site):
    with mutate.neutralize(site):
        for case in site.witnesses:
            obs = observe.generator_half(case.root)
            assert obs.reasons_and_stubs() != case.generator.reasons_and_stubs(), site.id

# tests/conformance/subset_profile/test_screen_mutations.py  (licensed)
@pytest.mark.parametrize("rule_shape", mutate.screen_recognizers(), ids=str)
def test_disabling_recognizer_breaks_agreement(rule_shape):
    with mutate.disable_recognizer(rule_shape):
        assert any(not cases.agrees(c.generator, observe.screen_half(c.root)) for c in rule_shape.cases)
```

- [x] `SiteReason` members for the 11 shared-rule codegen sites (`elaborate.py:814, :1353, :1624, :1939`; `expression_evidence.py:210`; `occurrence.py:826, :834, :858, :868, :885, :893`), set at each raise; `reason` column filled; stored answers re-captured (reviewed diff).
- [x] Witnesses: codegen sites in `generator.witnesses`; the 25 linked agentic sites in `agentic_site_witnesses`. agentic account test requires a packaged witness for every linked public row (PD5).
- [x] `tests/helpers/subset_profile/mutate.py` (D5): statement neutraliser, the 4 hand patches, recognizer patches, the patched-name table, `shared` tags (PD6), refusal on caching wrappers. `test_mutator.py` (pure unit tests): each code shape from S1, a zero-argument `super()` function, a refused `lru_cache` site, restore check.
- [x] Generator mutation test over shared-rule sites; screen mutation test per (rule, shape). No mutation of the 19 walker sites or of `invocation_allowlist.py` (PD6); that limit is recorded in `evidence/independence.md`, with shared mutations counted apart.
- [x] Record "other cases flipped" per mutation, rather than asserting none (design.md § Implementation Notes).

**Done when:** licensed `uv run --extra dev pytest tests/conformance/subset_profile/ -rs` passes, including `test_site_reasons.py` for every filled row; agentic `uv run pytest tests/test_subset_site_account.py -q` passes.

**Commits:** agentic "Item 2a P2.4: agentic site witnesses for shared-rule rows". codegen "Item 2a P2.4: shared-rule site reasons, witnesses, generator and screen mutations".

### What we know works after Phase 2

Every record pair rests on a packaged case, checked live in both repos. In codegen, each case's generator half and screen half are both run live and compared with the stored answers (`test_generator_half.py`, `test_screen_half.py`, the latter added by the mid-run audit fix), so an extractor or evaluator change fails codegen's suite, the pre-merge gate, and not only agentic-mbse's. The generator half never runs the screen. Every shared-rule detector, on either side, is tied to a witness that a mutation breaks, except the shared tables, whose limit is recorded. A screen mutation judges an unmutated live run against a mutated live run.

---

## Phase 3: Group C — agreement and the R3 rows

### Goal

Make every subject's two answers agree or be recorded as a disagreement, and close the R3 rows routed to 2a that are not silent losses or site work.

### Assumption under test

That the agreement rule, applied to every case and fixture, yields a disagreement set small enough to hand-record, and that ES-002, ES-008, ES-009 and CALC-DEF-BARE-RESULT can each be decided by the rule criterion (D11).

### Test stencil

```python
# tests/conformance/subset_profile/test_agreement.py  (pure)
def test_computed_disagreements_equal_the_record():
    computed = {cases.disagreement(s) for s in cases.all_subjects() if not cases.agrees(s)}
    assert computed == cases.read_disagreements().keyed()   # (subject, kind, codes, reasons)

# tests/conformance/subset_profile/test_fixture_agreement.py  (licensed)
@pytest.mark.parametrize("fixture", fixture_classes.model_roots(), ids=str)
def test_fixture_class_confirmed_then_screen_agrees(fixture): ...
```

### Changes

**Repos:** codegen; agentic for any D11 rule.

- [x] C1 pure agreement over all cases; C2 licensed fixture test (stored class confirmed by the generator half, then the live screen judged against it); C3 record equality (design.md § C, D3).
- [x] R3 cases (Appendix C): ES-002 (binding, admitted neighbor, other shapes reaching `occurrence.py:180`); ES-008 (five spellings, plain-nesting control); ES-009 (other shapes reaching `elaborate.py:2345`); ES-010 refusal side (one per projection entry path); ES-011 (`return r`, `out attribute r`); CALC-DEF-BARE-RESULT (arithmetic, `max`, conditional); DEEP-QUALIFIED-WIRING (minimal case plus fixture `deep_cross_scope_probe`); PUSH-DOWN literal shape (`sum(5.0)`); PUSH-DOWN redefinition precedence and ambiguous inherited attribute (pinned cases).
- [x] D11 per row, written to `evidence/r3-closure.md` one line per row. A rule adds its function, reason, record and facts in agentic, plus mapping entry and witness case in codegen. A gap adds a `reproduced_gap` entry; its `SiteReason` lands in P5.
- [x] **RG-1 stop:** any `rg1_pending` disagreement gets `RG1-<n>` in `rg1-recommendations.md` and its `kerml-expert` question (PD10). Continue.

**Done when:** codegen pure `uv run --extra dev pytest tests/conformance/subset_profile/test_agreement.py -q` and licensed `uv run --extra dev pytest tests/conformance/subset_profile/ -rs` pass; agentic suite passes; every R3 row assigned to P3 has a line in `evidence/r3-closure.md` (rows finished in P5 say so).

**Commits:** codegen "Item 2a P3: agreement over every subject; disagreement record equality; R3 cases and closures". agentic, if a rule lands: "Item 2a P3: <rule> rule from R3 row <row>".

### What we know works after Phase 3

A model the contract calls fine and the generator refuses, or the reverse, fails a test unless it is in the hand-edited record.

---

## Phase 4: Group D — silent losses, String, stubs, docs

### Goal

Pin each known silent-loss family at a semantic seam with a control, mark the losses that should block as candidates, and bring the String recommendation.

### Assumption under test

That each family's loss is visible at a named seam by declaration identity (D9), and that a stub's cause can be announced on a successful run without changing any outcome.

### Test stencil

```python
# tests/conformance/subset_profile/test_silent_loss_seams.py  (licensed)
@pytest.mark.parametrize("case", cases.with_loss_family(), ids=str)
def test_loss_absent_at_seam_and_control_present(case):
    obs = observe.generator_half(case.root)
    for seam in case.generator.seams:
        assert observe.at_seam(obs, seam) == seam.expect, (case.id, seam.kind)

# tests/conformance/subset_profile/test_candidate_refusal_marks.py  (pure, D10)
def test_record_candidate_refusal_iff_case_loss_marks_it(): ...
```

### Changes

**Repos:** codegen; agentic (`candidate_refusal`, CALC-USAGE-BARE-RESULT rule if the criterion holds).

- [x] Families and controls per design.md § D: ES-010 String; CALC-USAGE-BARE-RESULT-DROP at PD8's seam; ES-007 NON_NUMERICAL; G1; G2 (asserting what P1.1's probe found); one stub case per cause with its compiled control.
- [x] String fixtures: both spellings × uninstantiated template, instantiated part, bound to a calc input, read by another attribute.
- [x] Stubs (D9): `CompilationError` reasons for every `calc_compat_renderer.py` site (`:62, :76, :78, :81, :96, :103, :109, :115, :120`; `:117` if found reachable), distinct for `:78`/`:81`; `ManualStubNotice` logged once per (calc def, output) at `elaborate.py:704` with `extra={"manual_stub": …}`; listed as new warnings in `evidence/changed-outputs.md`.
- [x] Stub-cause mutations: neutralising each renderer site changes its witness's stub cause.
- [x] D10: `Qualification.candidate_refusal` in agentic; `loss` block in each case; two-way pure test.
- [x] CALC-USAGE-BARE-RESULT-DROP: if the rule criterion holds, the contract reports every calc-usage bare result `omitted` with `candidate_refusal`. Otherwise file a codegen backlog item (owner Reid Westwood) stating the limit.
- [x] **RG-1 stop:** `RG1-<n>` entries for CALC-USAGE-BARE-RESULT-DROP, each stub cause, G1, G2. One `kerml-expert` invocation asks G1 and G2 with both case models attached (PD10); one question per other candidate. Answers to `evidence/semantics-checks.md`. Continue.
- [x] **RG-2 stop:** `rg2-string-policy.md`: options, effect of each on generated output and native consumers, recommendation. Continue.
- [x] `docs/architecture/modeling-assumptions.md`: today's behavior for String values, NON_NUMERICAL constraints, calc-usage bare results and stubbed outputs, citing case IDs; the redefinition-precedence and inherited-typing statement from P3's pinned cases; POSITIONAL-FORMAL-REDEFINITION linked as pending Item 4.

**Done when:** licensed `uv run --extra dev pytest tests/conformance/subset_profile/ -rs` passes; agentic suite passes; `rg1-recommendations.md` and `rg2-string-policy.md` contain the entries above; the phase gate shows no accept/refuse change.

**Commits:** agentic "Item 2a P4: candidate_refusal qualification". codegen "Item 2a P4: silent-loss seams, String cases, stub causes and notices; RG-1 and RG-2 recommendations; modeling-assumptions".

### What we know works after Phase 4

Each known silent loss is pinned at a seam with a control, and every loss that should block is marked as a candidate in both the record and the case, with a written recommendation.

---

## Phase 5: Group E head — R3-row site reasons and head E4

### Goal

Give every R3-row site its reason and witness, and classify the head's unknown sites.

### Assumption under test

That ES-002 and ES-009, which shadow each other, can be told apart by distinct reasons (B6). If not, the pair gets a recorder observable, listed by name.

### Test stencil

```python
# tests/conformance/subset_profile/test_generator_mutations.py  (licensed, extended)
@pytest.mark.parametrize("site", mutate.sites_with_witnesses(scope="r3_row"), ids=str)
def test_neutralising_r3_site_changes_witness_reason(site): ...   # same body as P2.4

def test_es002_and_es009_reasons_distinct():
    assert reason_of("occurrence.py:180") != reason_of("elaborate.py:2345")
```

### Changes

**Repos:** codegen; agentic for the 4 chain-segment sites.

- [ ] Reasons and witnesses for the 6 R3-row codegen sites: `occurrence.py:180` (ES-002), `elaborate.py:946` (ES-008), `:2345` (ES-009), `:2474` (DEEP-QUALIFIED-WIRING), `project.py:213` (ES-010 refusal), `extractor.py:221` (CALC-DEF-BARE-RESULT). Witnesses are P3's cases. Mutations for each.
- [ ] E4 for the head's unknown sites: `binding_source.py:236, :243, :251`, `project.py:812`, agentic `reference_use.py:545, :557, :594, :618` (and `calc_compat_renderer.py:117` if P4 left it). Each is reachable (then reason, witness and mutation), internal invariant with a cited guard, or unknown with attempt, owner and limit. Verdicts for the PUSH-DOWN chain-segment and sum-shape rows go to `evidence/r3-closure.md` for Item 3.
- [ ] O8: a plain-exception head site becomes a coded refusal only if its witness shows `SI_INTERNAL_DEFECT` with that exception in the cause chain today. Otherwise **RG-1 stop**: pin current behavior, `RG1-<n>`, `kerml-expert` question. Continue. Every changed code goes to `evidence/changed-outputs.md`.
- [ ] Finish `evidence/r3-closure.md` for the rows P3 left open.

**Done when:** licensed `uv run --extra dev pytest tests/conformance/subset_profile/ -rs` passes, including `test_site_reasons.py` for every head row.

**Commit:** codegen "Item 2a P5: R3-row site reasons, witnesses and mutations; head unknown sites classified". agentic, if witnesses change: "Item 2a P5: chain-segment site witnesses".

### Split point (at P5's close)

Design.md § E fixes the rule; this plan supplies the numbers and the count.

**Denominators, from the account at plan time** (agentic `site_account.csv` at the sibling HEAD, `b5663c07` scan). P1.4 re-counts them after the move and the `unrecognized` rows, and records the final values in Implementation Notes; the trigger uses those.

| Set | codegen rows | agentic rows | Total |
|---|---|---|---|
| Head, public: `rule` or `matrix_row` set | 17 | 25 | 42 |
| Head, public: stub family (`calc_compat_renderer.py`) | 8 | 0 | 8 |
| **H** (head public) | 25 | 25 | **50** |
| Head, unknown: E4 in P5 (PD4 fills) | 5 | 4 | 9 |
| Tail, public (incl. the 10 naming collisions) | 34 | 7 | 41 |
| Tail, unknown | 34 | 3 | 37 |
| **T** (tail) | 68 | 10 | **78**, plus P1.4's `unrecognized` unknown rows |

H grows by each head unknown site P5 classes reachable.

**The count.**
- L = head public rows that pass `test_site_reasons.py` with a reason and at least one witness (codegen), or have a packaged witness (agentic). Command: licensed `uv run --extra dev pytest tests/conformance/subset_profile/test_site_reasons.py -rs`, then count head rows in `tests/expectations/subset_profile/site_account.csv` with a non-empty `reason` and witness, plus agentic head rows the account test reports witnessed.
- Tail count = rows with role `public_capability` or `unknown` not in the head, in both accounts.
- **Take the split if** L < H, or tail count > 1.25 × T (P1.4's value).
- Record H, L, T and the tail count in Implementation Notes. If the split is taken, P6 becomes a follow-on item, `test_site_account_completeness.py` and the all-rows agentic witness check go with it, and the orchestrator tells the owner. P7 still runs, including E5.

---

## Phase 6: Group E tail (skipped if the split is taken)

### Goal

Reasons and witnesses for every remaining public site, and a verdict for every remaining unknown site.

### Assumption under test

That the tail sites are reachable from small models at roughly the head's cost per site (design estimate 4–6 days).

### Test stencil

```python
# tests/conformance/subset_profile/test_site_account_completeness.py  (pure, PD5)
@pytest.mark.parametrize("row", account.rows(role="public_capability"), ids=str)
def test_public_row_has_reason_and_witness(row):
    assert row.reason and row.witnesses, row.site_id
```

### Changes

**Repos:** codegen; agentic for its 7 public and 3 unknown tail sites.

- [ ] The 10 naming-collision sites (`cli/__init__.py:224, :239`; `project.py:363, :386, :479, :679, :724, :1083`; `generation/entry_point.py:37`; `generation/predicate_compiler.py:319`): reasons (generation-stage ones also carry `GenerationCode`), codegen-home cases, witnesses, mutations.
- [ ] The other tail public sites: same treatment. O8 applies; **RG-1 stop** per candidate, then continue.
- [ ] E4 for every tail unknown site.
- [ ] agentic: witnesses for its 7 tail public rows; widen the account test to all public rows.

**Done when:** licensed `uv run --extra dev pytest tests/conformance/subset_profile/ -rs` passes, including `test_site_account_completeness.py`; agentic `uv run pytest tests/test_subset_site_account.py -q` passes.

**Commits:** codegen "Item 2a P6: tail site reasons, witnesses and verdicts; account completeness". agentic "Item 2a P6: witnesses for every public agentic-mbse site".

---

## Phase 7: Group F, rescan, receipt, final checks

### Goal

Close the evidence, put the pre-merge gate in force, and compare final checks with the baseline.

### Assumption under test

That a gate run at both final revisions passes with no license-gated skips, so the first receipt is real.

### Test stencil

```python
# agentic tests/test_subset_gate_receipt.py  (pure, D13)
def test_receipt_digest_matches_covered_files():
    receipt = json.loads(RECEIPT.read_text())
    assert receipt["digest"] == digest(sorted(glob("src/agentic_mbse/sysml/**/*")) + ["src/agentic_mbse/errors.py"]), RERUN_HINT

def test_receipt_lists_every_packaged_case():
    assert set(packaged_case_ids()) <= set(json.loads(RECEIPT.read_text())["case_ids"]), RERUN_HINT
```

### Changes

- [ ] **`kerml-expert` completeness:** every `rg1_pending` entry and every candidate has a recorded question and answer in `evidence/semantics-checks.md`.
- [ ] **E5 rescan:** codegen `test_site_account.py` and agentic `scan_sites.py --out <dir>` at the final revisions; `evidence/rescan.md` itemizes each added or removed site with its cause; zero unaccounted sites, zero orphan rows.
- [ ] **dc3:** `run_trees.py --out <dir>` on dc3 `808464df` and `60b44d53` with contract v2; `evidence/dc3-rerun.md` itemizes each difference from Item 1's `acceptance.md`; the generator half generates dc3 repaired at the final codegen revision.
- [ ] agentic `codegen_suite.py` gains receipt writing (digest from the exported tree, `codegen_rev`, `agentic_rev`, `case_ids`), fails on any license-gated skip; `scripts/subset_profile/README.md` rewritten.
- [ ] agentic `tests/test_subset_gate_receipt.py` (O18). Then the first gate run: commit both repos' final work, run `uv run python scripts/subset_profile/codegen_suite.py run --agentic-rev HEAD --codegen-rev <final codegen HEAD> --label gate --out /tmp/subset-2a/gate`, commit the receipt `tests/fixtures/subset_profile/codegen_gate.json`.
- [ ] **Final checks:** both repos' licensed suites, mypy and ruff, compared by test ID with `evidence/baseline.md`; `evidence/repository-checks.md` names every skip and every check not run. No failure absent from the baseline's pre-existing table.
- [ ] Record in Implementation Notes that the receipt names codegen `<rev>`, for the owner's `pre_pr` check (RG-3).

**Done when:** agentic `uv run pytest tests/ -q -rs` and codegen licensed `uv run --extra dev pytest tests/ -q -rs` match the baseline's pre-existing failures and nothing else; the receipt test passes on the committed receipt.

**Commits:** codegen "Item 2a P7: semantics checks, rescan, dc3 rerun, repository checks". agentic "Item 2a P7: pre-merge gate receipt and its test" (receipt committed last, after the gate run on the final codegen commit).

---

## Environment Setup

See `CLAUDE.md` in each repo. License: `set -a; source ../agentic-mbse/.env; set +a` from the codegen root; in agentic, `.env` is local. Without the key, license-gated tests skip, and a run with skips does not count (spec Independence).

## Risk Management

See design.md § Potential Risks. Phase-specific:
- **P1.3:** a converter branch with no reachable witness. List it by name in the test module with the attempt; do not drop it silently.
- **P2.1:** the wheel misses `subset_cases/`. The manual `uv build --wheel` listing catches it before P2.2 builds on it.
- **P2.4, P5:** a shadowed mutation survives. Check the two sites have distinct reasons (PD7); if they cannot, add a recorder observable and list the pair.
- **P3–P6:** a test can only pass by changing accept/refuse. Stop that item, record an RG-1 candidate, pin today's behavior, and continue with the rest.
- **Every phase:** Item 4 merges into agentic `main` mid-run. The phase gate's rebase check catches it; the final gate run covers the merged tree.

## Not checked while planning

- agentic-mbse's current HEAD and whether `main` has moved since `ccd57d83` (the plan's git commands against the sibling needed approval this session). P1.1 records it.
- The site counts come from agentic's `site_account.csv` as it stands; the scanner port may add `unrecognized` rows. P1.4 re-counts.
- Whether `pyproject.toml:49-63` already ships non-Python files under `sysml/`. P2.1 checks it.

## Implementation Notes

Phase 1 notes are below, per step. Later phases add their own sections.

### Phase 1 Completion
**Completed:** 2026-10-18. Phase gate passed, except the audit, which is the orchestrator's to run (`/_my_audit`).
**Actual Changes:** codegen `5e5a57b8` (1.1–1.2), `06f938fc` (1.3), `a353ddd3` (1.4), `d2319b97` (1.5), `ec04304a` (1.6), and the phase-gate fix commit after them; agentic-mbse `c39b4cda` (1.2), `186d7ff3` (1.4), `8be21e04` (1.5). Per-step detail is in the step notes below.
**Split denominators (H, T) after P1.4:** codegen account H = 31, T = 86 (47 `unknown`, 39 `public_capability`); agentic-mbse account H = 29, T = 10. Counted by PD4's rule: head is a row with a `rule` or `matrix_row`, plus the 10 rows in `extraction/calc_compat_renderer.py`; tail is every other `public_capability` or `unknown` row. Codegen's T includes 13 `unknown` rows added at the move for unrecognized raises (see Step 1.4 notes).
**Issues:** One new failure at the phase gate, caused by this branch and fixed before close. `tests/conformance/test_constraint_population_oracle.py` treats every top-level fixture directory as one model, so it read the P1.5 seed directory (34 independent models) as one fixture and failed 4 tests. It now skips directories named in `MODEL_COLLECTIONS`, each with the test that covers its models. P2's `tests/fixtures/subset_profile/` (codegen-only cases, D14) is the same kind of directory and must be added there when it is created.
**Phase gate (2026-10-18):**
- Snapshots: `git diff --exit-code d73a4fc5` over the 22 committed `instance_graph_snapshot.json` files exits 0.
- Accept/refuse: the 88 tests in `test_public_package_oracle.py` and `test_v6_recapture_batch.py` pass, and `baseline.json` and `batch.json` are unchanged since `d73a4fc5`.
- Regressions: codegen licensed suite 2945 passed, 10 failed, 9 skipped, with the 10 failing IDs exactly the baseline's; 210 tests added, none removed. agentic-mbse 3473 passed, 94 failed, 35 errors, 9 skipped, with the 129 failing IDs exactly the baseline's. Its 70 removed IDs are the retired parity test (69) and `test_both_trees_are_accounted`, and its 19 added are the P1.2 script tests and the P1.4 account tests.
- Merge order: `git log subset-conformance..main` is empty in both repositories. Checked against the local `main` refs; nothing was fetched.
- Static checks: codegen mypy clean (87 files), ruff 94 (baseline 94); agentic-mbse mypy 98 errors (baseline 98), ruff 118 (baseline 118).
- Audit: not run here.
**Deviations:** listed per step below. The ones that change a planned contract: `GenerationCode` has 20 members and `code` is required (1.3); the refusal payload also covers package-write failures (1.3); an explicit follow-up row may name a matrix row, and the matrix gains `codegen_account` (1.4); agentic-mbse's scanner is `scan_sites/2` (1.4); the `NO_REFUSAL` rule follows the record's `expected_code` (1.5); four agentic-mbse models moved to `cases/` (1.5).

#### Steps 1.1–1.2 (2026-10-18)
- Baseline in `evidence/baseline.md`: codegen 2735 passed, 10 failed, 9 skipped; agentic-mbse 3524 passed, 94 failed, 35 errors. Every failure predates 2a: the 10 codegen failures also fail at `b5663c07` + `ccd57d83`, and agentic-mbse fails on the same 129 IDs at `ccd57d83`. All are environment failures (missing `web` extra, Pandoc, PIL; a hardcoded `/home/reid/1cfe` path; a commit, `07531e64`, absent from this clone; argparse quoting in the system Python). S1 said nine `test_check_ledger_4a.py` failures; there are eight, plus one in `tests/study/test_study_cli.py`.
- The base run in an exported tree adds 50 failures that pass at HEAD, because `git archive` carries no `.git` and the study-layer tests need a git work tree. Recorded in `baseline.md` as a method artifact. It matters for P7: the gate's default selection, `tests/conformance/subset_profile`, must not read git state.
- G2 probe (`evidence/g2-probe.md`): the usage override is ignored and generation succeeds, so P4's G2 case asserts a silent loss (2 occurrences, not 3).
- agentic `c39b4cda`: `isolated_tree.py` holds the tree helpers; `read_identity` now returns a dict, so it no longer depends on the probe judge that P2.1 retires, and `probe.py` wraps it in its `Identity`. Every script imports from `isolated_tree.py`, and none imports from `probe.py` (tested), so P2.1 can delete `probe.py` alone.
- Beyond PD12's five scripts, `probe.py` (`--log-dir`) and `occurrence_parity.py` (`--out` on `compare` and `controls`) also stopped writing into the archive, because the plan's own test ("no script in `scripts/subset_profile/` names `.project/completed/`") covers them. `scan_sites.py --out` was already a parameter with no default; it stays optional because `--reconcile` alone writes nothing.
- The scripts' codegen checkout default moved from `~/src/sysml-codegen` (the owner's main checkout) to the sibling of the agentic-mbse checkout, the same layout as codegen's `../agentic-mbse` path dependency. The base run read this worktree.

#### Step 1.3 (2026-10-18)
- The reach test passes for every carrier type and every converter branch in `_build_from_extractor` (`orchestration/elaborated_pipeline.py`): ReadinessFinding, GraphValidationError diagnostics, ElaborationInvariantError, SemanticEvidenceError, ExactTypeError, CodeGenerationError re-raised during construction, and CodeGenerationError at generation. Checked against a mutation: when the two `*_with_referent` converters drop `reason`, the six witnesses that pass through a converter fail, and the four that do not still pass.
- Two branches have no model that reaches them, so they are listed by name in the test module and witnessed by a raise patched in at the inventory call. `ExpressionInventoryError`: every raise is a consistency check over the inventory the same call built, and the one authored form it refuses, an index, leaves through `_indexed_refusal` as a `SemanticEvidenceError`. `except Exception`: by definition nothing classified reaches it.
- The witness models are written inline in the test, not read from agentic-mbse's Item 1 probes. The plan said "pick each witness from an existing fixture or Item 1 probe", but the probes live in agentic-mbse's `tests/` tree, and the spec's [HARD] boundary says codegen takes nothing from there. The inline models have the probes' shape. Two (blocked predicate, indexed reference) gained a calc, so the model has executable content beside the refused construct. After P2.1 packages the probes, the reach witnesses can cite packaged cases instead.
- `SiteReason` (`elaboration/diagnostics.py`) has the six members the witnesses need plus nine `evidence_*` members, one per `SemanticEvidenceCode`, for the total relay table `_EVIDENCE_REASONS`.
- `run_codegen` and `_generate_package_from_graph` log one `Refusal` (`cli/refusal.py`, new) on every failing path. The harness (`tests/helpers/subset_profile/observe.py`) requires exactly one on a refusal and none on success. Changed message text is in `evidence/changed-outputs.md`.
- Verification: the done-when command passes (163 tests, no skips); the full licensed suite has the baseline's 10 failures and no others (2794 passed); the 22 snapshots are byte-stable against `d73a4fc5`; the oracle and recapture-batch tests pass; mypy `src/` is clean and ruff `src/ tests/` still reports the baseline's 94.
- Deviations:
  - `GenerationCode` has 20 members, not only today's eight message prefixes. Twelve raises had no prefix, and D15 needs every raise to carry a code, so they got members named for their condition (for example `NOTHING_TO_GENERATE`, `RECEIPT_INVALID`). Message text is unchanged.
  - `code` is a required keyword on `CodeGenerationError`, so a raise without a code fails at construction rather than waiting for the E1 scan.
  - `_readiness_with_referent` and `_diagnostic_with_referent` now use `dataclasses.replace`, so a field added later is carried without editing them.
  - The refusal payload is also attached in `_generate_package_from_graph`, with a `PACKAGE_WRITE` kind (carrying no code) for write and seal failures. The plan named only `cli/__init__.py:1189-1230`, but a generation-stage refusal is logged there, and the harness needs it.
  - `test_elaboration_payload_identity.py::test_profile_block_halts_exact_route_before_projection` round-trips a non-strict graph that holds a blocked diagnostic. With the encoder refusal it now asserts the refusal first, then strips the reasons and round-trips as before. Production encodes only after `require_projectable`, so D8's premise holds.

#### Step 1.4 (2026-10-18)
- `tests/helpers/subset_profile/site_scan.py` reproduces `scan_sites/1` exactly: run on this tree it gives the 441 moved IDs, apart from three changes step 1.3 made. One site is new: the encoder's `ValueError` in `_diagnostic_to_data`. Two relay rows are gone, because `_readiness_with_referent` and `_diagnostic_with_referent` now use `dataclasses.replace` and no longer rebuild the carrier with `code=…code`.
- The `unrecognized` channel adds 50 rows. Each row's role comes from reading the raise. 27 are relays (re-raises, catch-all conversions, raises of a site built elsewhere). 5 are public generation refusals raised through a factory: name safety ×2, class-name collision, exit-point type, and predicate function-name collision. 3 are snapshot integrity (the receipt failure ×2 and the envelope's duplicate-key refusal). 2 are internal invariants with a cited guard: the registry's class-name backstop and `CONSTRAINT_DOMAIN_INCOMPLETE`. The other 13 are `unknown` / `explicit_follow_up`, owner "EXEC-SUBSET-CONTRACT Item 2a (E4 triage)", because valid-input reachability was not traced at the move: `MODULE_KIND_UNRENDERABLE` ×5, `PREDICATE_IR_INCONSISTENT` ×3, `GENERATION_METADATA_MISSING` ×2, `PREDICATE_SCOPE_MISMATCH` ×2 and `PREDICATE_INPUT_UNRECONCILED`.
- The codegen account is 490 rows. Each moved row's `line` and first evidence pointer were refreshed to this tree. The header says later evidence pointers still cite `b5663c07`. The scan is the authority for location; E1 compares IDs only, so a line move does not break it.
- Six rows carry a `reason`, the ones step 1.3 set at a scanned site. `test_site_reasons.py` checks both directions: a recorded reason is the one the site passes, and a reason a site passes is recorded. Two reasons are set off a scanned site, so no row carries them: the relayed `evidence_*` table, and `generation_constraint_name_unsafe`, set inside the `constraint_name_safety_error` factory.
- The provenance guard in `test_diagnostic_provenance_sites.py` is now a query over the scan. It covers 38 sites, where the old AST walk counted 40. The two dropped calls are the `super().__init__` calls inside `InvalidRedefinitionFamilyError` and `RecursiveContainmentError` themselves, which are not refusal sites.
- Found while narrowing agentic-mbse's scanner: `scan_sites/1` found executable_profile's `_diagnostic` factory only because sysml-codegen has a function of the same name (`elaboration/project.py:127`), since its factory search ran over both trees. Scanned alone, agentic-mbse would have lost 34 of its 61 sites. `scan_sites/2` declares `_diagnostic` as a form (`scanner.toml` `shared_profile_factory`), and its 61 IDs and lines are identical to before. The dependence the other way is real and kept: codegen calls agentic-mbse's `evidence_error`, so codegen's scan still searches for factories over both trees.
- agentic `site_account.csv` keeps its 61 rows. Its header drops the sysml-codegen revision and points to codegen's account. PD4 joins the four `reference_use.py` chain-segment sites to `PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS`. That matrix row becomes `listed`, and its statement says why.
- Deviations:
  - PD4 puts `matrix_row` on `explicit_follow_up` rows, which both loaders had refused ("matrix_row iff in scope"). The rule is now: an in-scope row needs a matrix row, a row handled elsewhere has none, and an explicit follow-up may name the row it is routed to. agentic's account test pins the four routed rows.
  - The matrix gains a site status, `codegen_account`, for the 13 rows whose sites are all sysml-codegen sites (12 that were `listed`, plus `PUSH-DOWN-AGG-PROFILE-SUM-SHAPE` from PD4). Without it, those rows would be `listed` with no sites, which the matrix loader refuses. `listed` rows keep only their agentic-mbse sites; ES-007 and INDEXED-REFERENCE also have codegen sites in codegen's account. `render_matrix.py` renders the new status.

#### Step 1.5 (2026-10-18)
- `SUBSET_PROFILE_VERSION = "subset-profile/v1"` is pinned in `_upstream_pins.py`, and `test_upstream_pins.py` checks it against the installed screen. `subset_profile_adapter.py` raises `ImportError` at import when they differ. Nothing under `src/` imports the adapter; `test_reason_mapping.py` checks that over the AST.
- `REASON_MAPPING` has 16 entries, one per `SUBSET_REASON_CODES` member. Three map to `NO_REFUSAL`: `conditional_expression_resolved_branches`, `constraint_predicate_non_numerical` and `string_value_not_generated`. No entry has per-context codes, because every refused pair Item 1 observed carries its record's `expected_code`.
- `render_finding` sets a code only on a refused finding. A refused finding whose reason maps to `NO_REFUSAL` raises `ValueError`, since that means the records and the mapping disagree.
- Occurrence parity now lives in codegen. The 34 seed models are in `tests/fixtures/subset_profile_occurrence_seed/`; the normaliser is `tests/helpers/subset_profile/occurrence_parity.py`; the licensed test compares agentic-mbse's `extract_occurrence_structure` with codegen's live index on the same loaded model, over 71 roots (34 seed plus the 37 `batch.json` fixtures). A missing root fails by name. All 71 agree: 285 occurrences, 209 writers, 7 unexpandable usages and 4 fatal aborts. The mutation test drops the last index from `_multiplicity_indices` (now `elaboration/occurrence.py:818`) on `es004_admitted_exact_redefinition`, and parity fails.
- agentic-mbse's parity test, seed directory, oracle schema and the three occurrence scripts are removed; `occurrence_extraction.py`'s docstring points to codegen's test. `tests/test_sysml/` plus `test_subset_profile_scripts.py`: 1022 passed, 1 skipped.
- The adapter adds two sites to codegen's site account, which E1 caught: the import-time `ImportError` (`environment`) and the renderer's `ValueError` (`internal_invariant`, no caller under `src/`). The account is 492 rows.
- `evidence/versioning.md` records criterion A2: agentic-mbse stays 0.1.3, there are no release tags, and the package index was not checked.
- Verification: the done-when command passes (202 tests with the provenance test, no skips). mypy `src/` is clean; ruff `src/ tests/` reports the baseline 94 in codegen and 118 in agentic-mbse; agentic-mbse mypy reports the baseline 98.
- Deviations:
  - The plan's `NO_REFUSAL` rule is "exactly when no record refuses the shape". Two shapes (`part_multiplicity_nonunique`, `part_multiplicity_negative_bound`) have no decided context yet, so no record refuses them, but each record names an `expected_code`. They map to that code, and the test uses the record's `expected_code` as the rule: `NO_REFUSAL` exactly when the record has none. The two undecided shapes are pinned by name.
  - The oracle's `full_crosscheck` step is not ported. It ran codegen's full `elaborate_model_paths` and checked that its occurrences and calc nodes matched the oracle's partial run, which stops after the writers. That compares codegen with itself, not with agentic-mbse, and the old parity script only printed it as a summary column. A writer error the normaliser does not expect now raises instead of being recorded.
  - Criterion A2 asks which agentic-mbse version first carries the contract. None does: `SUBSET_PROFILE_VERSION` arrived in `b2d5768d`, and the package reports 0.1.3 on both sides of it. `evidence/versioning.md` records that and meets A2 in D12's form.
  - Two agentic-mbse test files (`test_subset_extraction.py`, `test_conditional_operator_spelling.py`) loaded four models from the retired seed directory. Those models moved to `tests/fixtures/subset_profile/cases/` (`recursive_containment`, `range_multiplicity_parts`, `product_invocation`, `conditional_operator`), and the tests point there. The plan did not list them.

#### Step 1.6 (2026-10-18)
- Five staged files in this folder, each naming its target file and lines and ending "Filing: owner, at merge (RG-3)": `adr-0012-amendment.md`, `adr-0001-amendment.md`, `p0001-amendment.md`, `adr-0016-amendment.md`, `adr-fact-placement-draft.md`. ADR and promise bodies are immutable, so each is a new entry plus an `amend` flip by the target repository's script, with the commands written out. The fact-placement draft is a new entry that amends nothing.
- `adr-0012-amendment.md` follows the archived draft except for its parity guard: the stored-oracle test it named is retired (P1.5), so it names codegen's live parity test, and it says "the pre-merge run" where the draft said "codegen CI". The archived draft is unchanged.
- Found while writing `adr-0001-amendment.md`: agentic-mbse ADR 0001 invariant 6 names `scripts/subset_profile/occurrence_parity.py compare --all` as the interim check, and P1.5 deleted that script. The check it stood in for exists now (codegen's parity test), so nothing is unguarded, but the filed ADR points at a deleted script until the amendment is filed. The staged file says so.
- Each staged entry's provenance is `[AGENT]` from the 2a design, with owner ratification to be recorded at filing. None of them is owner-originated.

### Phase 2 Completion
**Completed:** 2026-10-18. Phase gate passed, except the audit, which is the orchestrator's to run (`/_my_audit`).
**Actual Changes:** codegen `5f4b86ad` (2.1), `ce15587a` (2.2), `81bdc1eb` (2.3) and the 2.4 commit; agentic-mbse `e4bb619c` (2.1), `47579142` (2.2), `f360c3f6` (2.4). Per-step detail is in the step notes below.
**Rebased (merge order).** agentic-mbse `main` gained Item 4 (PR #31, 40 commits), which touches `src/agentic_mbse/sysml/syside_adapter.py` and `types.py` and adds two `parameter_redefinition_*` modules. Per the gate, `subset-conformance` was rebased onto it after the 2.4 commit. The one conflict was the epic's `**Revised**` line, merged as "Items 1 and 4 closed; Item 2 split into 2a and 2b". The gate below ran on the rebased tree. Old → new agentic-mbse IDs: `71f59820` → `f84b1f6e`, `882edc6a` → `315d5853`, `c39b4cda` → `3ad38b1c`, `186d7ff3` → `16d2ed75`, `8be21e04` → `05e9d813`, `c5b13405` → `e4bb619c`, `dfc9ce74` → `47579142`, `c6af4c1a` → `f360c3f6`. Earlier notes keep the old IDs; this line maps them.
**Phase gate (2026-10-18, after the rebase):**
- Snapshots: `git diff --exit-code d73a4fc5` over the 22 committed `instance_graph_snapshot.json` files exits 0.
- Accept/refuse: the 88 tests in `test_public_package_oracle.py` and `test_v6_recapture_batch.py` pass, and `baseline.json` and `batch.json` are unchanged since `d73a4fc5`.
- Regressions: codegen licensed suite 4182 passed, 9 failed, 9 skipped. All 9 failures are baseline IDs, and none is new. The tenth baseline failure, `test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees`, now passes, because it reads agentic-mbse guidance that Item 4 changed. agentic-mbse (`uv run --all-extras pytest tests/`, `.env` sourced): 3875 passed, 5 failed, 8 skipped, 1 xfailed. The 5 failures are exactly the all-extras baseline IDs.
- Merge order: codegen `git log subset-conformance..main` is empty. agentic-mbse: handled by the rebase above. Checked against local `main` refs; nothing was fetched.
- Static checks: codegen mypy clean (87 files), ruff 94 (baseline 94); agentic-mbse ruff 118 (baseline 118), mypy 88 (baseline 88; 90 files checked after the rebase).
- Audit: not run here.
**Deviations:** listed per step below. The ones that change a planned contract: `case.json` gains `kind`, `construct.description` and finding lines (2.1); records gain `[[rule.shape.unobservable]]` (2.2); four linked sites have no witness, each recorded with its reason (2.4); the firing tracer is `sys.monitoring` (2.4).

#### Step 2.1 (2026-10-18)
- agentic: the 80 probes are packaged cases under `src/agentic_mbse/sysml/subset_cases/<id>/`, each a `model.sysml` (moved with `git mv`) and a `case.json`. The wheel lists 80 `case.json` and 80 `.sysml` files there. Each stored screen answer was checked against its probe's recorded expectation before the probe files were removed: no mismatches, and five extra findings, each one a second finding of the same rule on the same construct.
- agentic: one module owns the case format, `src/agentic_mbse/sysml/conformance_case.py` (`load_packaged_case`, `screen_answer`, `screen_answer_from_json`). codegen reads `case.json` through it and has no parser of its own, so the format has one reader.
- agentic: records cite `case:<id>` and the loader rejects `probe:`. `SUBSET_PROFILE_VERSION` is `subset-profile/v2`, pinned in `test_subset_profile_version.py`. The two retired part-multiplicity shapes left the records, the rule and `SUBSET_REASON_CODES`.
- agentic: `tests/test_subset_case_citations.py` checks each citation from the screen side: the case is packaged, it is a record case, and its stored answer shows the cited pair. It also checks the controls and reproductions draw no refusal, and that every record case is cited. The two rule tests replay every packaged case and compare it with the stored screen answer.
- codegen: `tests/helpers/subset_profile/cases.py` holds the stored-answer schema, the agreement function (design § C) and the `disagreements.json` reader. `capture.py` writes only the generator block, and refuses a run that disagrees with the screen unless the record already lists it. `test_disagreement_record.py` holds the writer guard.
- codegen: 80 stored answers captured, 52 refused and 28 generated. Each was compared with its probe's recorded generator result. Two differ, both from the payload change below: ES-010's refusal now lists `SI_RENDERING_COLLISION` beside `PROJECTION_FAILED`, and one constraint case lists `SI_CONSTRAINT_BLOCKED` twice, because it has two blocked predicates.
- codegen: `disagreements.json` was written by hand with six entries, all of kind `generator_refuses_screen_silent`: the two bare-result calc cases, ES-002, ES-008, ES-009 (each `reproduced_gap`, for P3 to decide), and ES-010's refusal side (`codegen_owned`).
- codegen: `test_generator_half.py` (licensed, 160 tests) runs every case live and compares it with its stored answer, and checks every located refusal sits inside the construct's lines.
- codegen: the reach test's four inline witnesses that matched a packaged case now read that case (design invariant 7, one copy of each model). Those cases give the same refusal kind and reason.
- Verification: codegen licensed `tests/conformance/subset_profile/` plus the answer, CLI and oracle tests: 740 passed, no skips. agentic `tests/test_subset_case_citations.py tests/test_sysml/` plus the matrix, site-account and scripts tests: 1271 passed, 1 skipped. codegen mypy clean, ruff 94 (baseline 94). agentic ruff 118 (baseline 118), mypy 88, the same count as agentic `HEAD` (`8be21e04`) in the all-extras environment. The Phase 1 figure of 98 was taken before the all-extras sync, so 88 is the mypy baseline from P2 on.
- Deviations:
  - The projection refusal now carries the diagnostics it wraps. Before, ES-010's structured code was only `PROJECTION_FAILED`, and `SI_RENDERING_COLLISION` was in the message text only, which the harness does not parse (design D2). `CodeGenerationError` gained `diagnostics` (`core/errors.py`), `_project_or_fail` passes them (`orchestration/exact_pipeline_context.py`), and `generation_refusal` lists them (`cli/refusal.py`). Messages and accept/refuse are unchanged. The second raise in `_project_or_fail` is a new relay row in codegen's site account (493 rows).
  - `case.json` gains `kind` (record, control or reproduction) and `construct.description`, and each screen finding gains `line`, so isolation can be checked on the screen side. Codegen-home answers carry `construct` and `screen`.
  - `EvidenceStatus.PROBE_OBSERVED` became `CASE_OBSERVED`, `example_probe` became `example_case`, and the matrix statuses were renamed to match.
  - The part-multiplicity rule raises `ValueError` on the two retired resolutions instead of dropping them silently.
  - The records' `verified_against` fields still name the Item 1 revisions. P7 refreshes them.
  - `SI_CONSTRAINT_BLOCKED` carries no location in the payload, so the isolation check cannot place it. It is listed by name in `test_generator_half.py`.

#### Step 2.2 (2026-10-18)
- 26 new packaged cases. Each screen answer was computed after the record change and read against the expected outcome before it was kept; each generator answer was captured and read the same way.
  - 17 cases for the R3 § 3 `unconfirmed` pairs, one per pair, plus a calc-def-owner variant for `binding-source/expression_source` at `owner_other`.
  - 7 family cases (spec B4): a conditional inherited, redefined and in a template; an indexed reference in a template; an unsupported callable redefined and in a template; a String in a template. Each agrees with the screen. In particular, the generator refuses the site rules' shapes in an uninstantiated template, as the model-wide rules say.
  - 2 reproductions of a gap found here (below).
- Where each R3 § 3 pair landed:
  - Observed, admitted: `binding-source/expression_source` at `owner_other`; `self_reference_source` at `owner_other` and `writer_overridden`; `constraint-predicate/non_numerical_predicate` at `owner_uninstantiated` (catalog `non_reaching`).
  - Observed, excluded: `non_numerical_predicate` at `owner_package` (catalog `excluded`/`non_numerical`).
  - Unobservable, with the reason in the record: `conditional_resolved_branches` in all six site contexts (every `if` conditional, literal-only branches included, ends the reference walk in RESOLVED_TARGET_MISSING, so no model reaches the shape); the three site rules at `calc_result_expression` (CALC-DEF-BARE-RESULT refuses first); `blocked_predicate` and `non_numerical_predicate` at `owner_other` (the unattached owner is refused first, by ES-001's code).
- agentic: records gain `[[rule.shape.unobservable]]` (context, reason, case evidence). The loader refuses one on a decided context, on a context unconfirmed by design, with corpus evidence, or listed twice (`test_subset_profile_records.py`). `test_subset_case_citations.py` checks that an unobservable pair's case is packaged and shows no decided outcome for the pair. `render_matrix.py` prints the field. `v2` re-pinned at `e2983eba…`. The matrix's coverage text for ES-006, ES-007 and the site rules now says what is recorded.
- codegen: `observe.py` reads the five seams by `DeclarationId` (`seam_value`, `declaration_in`). Entry points carry no declaration, so the harness records each one's owner node as projection mints it, through a spy on `_Projection._entry_source` (`elaboration/project.py`). 12 stored answers carry seams: the four `other_expression_site` cases (the calc usage's only output is `r`), the three String cases and their numeric control, and four catalog dispositions. `test_generator_half.py::test_every_seam_holds` checks them live.
- codegen: `test_record_coverage.py` (pure, 57 tests): refused pair → a refusing case; refused shape → a generating case or SA-1; omitted/excluded pair → a case with a seam; every R3 § 3 pair decided or unobservable.
- `disagreements.json` gained 6 hand-written entries, 12 in all: the four new `calc_result_expression` cases (CALC-DEF-BARE-RESULT) and the two item def reproductions.
- `MODEL_COLLECTIONS` is unchanged: no codegen-home case exists yet, so `tests/fixtures/subset_profile/` was not created. It joins the oracle's collections when the first codegen-home case lands.
- Verification: codegen `tests/conformance/subset_profile/` plus the answer tests, licensed: 694 passed, no skips. agentic `tests/test_subset_case_citations.py tests/test_sysml/`: 1261 passed, 1 skipped; with the matrix, site-account and scripts tests, 1353 passed. agentic mypy 88, unchanged.
- **Found: a constraint owned by an item def is refused and no rule says so.** The generator refuses it as `SI_CONSTRAINT_UNATTACHED`, asserted or not. calc-owned-assertion recognizes only calc def and calc usage owners, so the screen is silent. Two reproduction cases (`candidate-unattachable-constraint-owner__*`) and two `reproduced_gap` entries hand it to P3, which decides by the rule criterion whether calc-owned-assertion widens to every owner the occurrence facts cannot attach. RG-1 is untouched.
- **Premise conflict, for P4 (surfaced, not resolved).** Design § D says a String value leaves "no instance-graph attribute node and no entry point", with a numeric control where "both are present". In fact the String attribute does get an attribute node (it holds the text value), and it gets no entry point. But an unconsumed `Real` attribute gets no entry point either (checked on a scratch model). So on these cases, "no entry point" does not separate a String omission from an attribute nothing reads. The String seams here assert what is true (node present, no entry point; the consumed numeric control has one). Whether that is evidence of a String-specific omission is parked for P4's String families and `rg2-string-policy.md`. **Closed in P4:** it is not. The String node holds its value, and the missing entry point is what any unconsumed attribute gets; the String-specific behavior is only at the calculation boundary (`rg2-string-policy.md`, "What corrects an earlier premise").
- Deviations:
  - dc3 `proto3`, `proto4nest` and `conv` were dc3 session scratch and are in no dc3 revision. dc3 `60b44d53` keeps only their descriptions (U5, U2, U6 in `.project/active/toolkit-upstream-findings.md`). The minimal models already exist as `candidate-es-002/008/009`, so their provenance now names the dc3 revision and finding, and no new model was built.
  - Constraint-predicate `owner_other` cases use a calc usage owner, where the screen and generator agree through calc-owned-assertion. The item def owner is the reproduction instead.
  - The two reproductions locate their construct on the whole item def (lines 4–7), because the generator places the refusal on the owner.

#### Step 2.3 (2026-10-18)
- `test_tripwire.py` (licensed, 110 tests): every case ends as its stored answer says with the three screen entry points rebound to raise (`observe.screen_tripwire`, made public for this test). Two checks show the tripwire works: a call through the defining module, and one through a by-name import, each fails the observation even when the caller swallows the raise. Each check also shows the originals come back afterwards.
- Fixture classes: `tests/expectations/subset_profile/fixture_classes.json` (164 entries) and its reader `tests/helpers/subset_profile/fixture_classes.py`. The 37 corpus fixtures take their class from `batch.json`, and codegen-home cases from their stored answers (none yet). `test_fixture_classes.py` (pure, 203 tests) checks:
  - every directory under `tests/fixtures/` is classed, lies inside a classed model, or lies under something classed `not_a_model`;
  - no path has two class sources;
  - each class fits the directory (a model root has `.sysml` files; `not_a_model` has none; a container holds no model files of its own).
- The 155 model roots outside the batch were classed by one generator-half run each and read before storing: 77 generating, 78 refusing. Four refuse at parsing with no code (`source_identity_absent_referent`, `source_identity_binding_forms`, `two_same_leaf_producers` and the seed's `f1_invalid_redefinition_family`); each says so in a note. Three containers: `constraint_occurrence_demand` (seven independent models), the occurrence seed, and `study_station`. Six `not_a_model` entries.
- `test_reason_mapping.py::test_every_mapping_pair_has_a_witnessing_case`: each of the 11 (reason, code) pairs has a case that refuses with the code where its screen answer refuses with the reason.
- Occurrence parity now also runs on every case in either home (179 tests). 103 of the 106 cases have occurrences; the other three compare two empty summaries, which keeps the set total without a filter that needs the license at collection time.
- Verification: licensed `tests/conformance/subset_profile/` plus the answer and oracle tests: 1276 passed, no skips. mypy clean; ruff 94 (baseline 94).
- Deviations:
  - `fixture_classes.json` gives `note` only where it is needed: required for containers, `not_a_model` and a refusal with no code, and absent for a plain generating or refusing root. Appendix A lists `note` on every entry; 155 copies of "classified by one run" would say nothing.
  - The four parse refusals have no code. P3's fixture agreement test must decide how such a fixture agrees, since the screen cannot load it either.
  - Found: the constraint population oracle treats `constraint_occurrence_demand` as one fixture (it is in its refused-by-design set), though it holds seven independent models. That is the same shape P1 fixed for the occurrence seed. It passes today and is out of 2.3's scope, so it is recorded here, not changed.

#### Step 2.4 (2026-10-18)
- Site reasons: 7 new `SiteReason` members (`elaboration/diagnostics.py`), set at the raise: the five `_multiplicity_indices` refusals in `occurrence.py` (nonunique, upper unresolved, negative, lower unresolved, range) and the two `SI_CONSTRAINT_UNATTACHED` sites in `elaborate.py` (`_owner_kind`, `_halt_on_error_dispositions`). With the three that already had one, 10 of the 11 shared-rule rows carry a reason. The eleventh, `expression_evidence.py` `_indexed_refusal`, returns agentic-mbse's `SemanticEvidenceError`, so its reason is the relayed `evidence_indexed_reference_unsupported` (`_EVIDENCE_REASONS`) and its row's `reason` stays empty, as for every relayed site. The packaged re-capture changed reasons only, each the expected new member.
- Witnesses: every stored answer names the shared-rule codegen sites its generator half fires (`generator.witnesses`, 56 answers), and every packaged case names the linked agentic-mbse sites its screen half fires (`agentic_site_witnesses`, 55 cases). The lists came from one traced run of all cases and were read before storing. 18 new agentic-home record cases make the witnesses total where a model can reach the site: 13 expression-walker branches, `block_assert_by_reference` (a named `assert constraint checked ::> positive;`), `block_missing_predicate` (a constraint def with no predicate), a predicate-root conditional and call (cited under conditional-expression and invocation-callable, whose codes the generator gives), and the lower-bound site (`[n..2]`). The records cite all 18, and `v2` is re-pinned.
- agentic `tests/test_subset_site_account.py`: every witness names an accounted site, and every linked public row (25) has a packaged witness or a `[[unwitnessed_site]]` entry in `scanner.toml` with its reason. Two have one: 1014 `block_unresolved_definition` and `reference_use.py:702`.
- `tests/helpers/subset_profile/mutate.py`: `Target` (one statement in a named function), `recording_fired` (`sys.monitoring` line events on the owning function's code only), `rewritten` and `neutral` (D5's three rewrites), `neutralize(site_id)` with the four hand patches, `disable_recognizer`, `PATCHED_NAMES` and `SHARED`. `test_mutator.py` (pure, 39 tests) covers each S1 code shape on a sample module, plus zero-argument `super()`, a nested function, a by-name import, a refused `lru_cache`, a refused one-line `if x: raise`, and restore after a raise. It also builds every planned site mutation against the real source and resolves every patched name.
- `tests/helpers/subset_profile/witnesses.py` and `tests/expectations/subset_profile/mutations.json` (`subset-mutations/1`, hand-reviewed): per mutated site the cases whose outcome or reasons change, per (rule, shape) the cases whose agreement changes, and the unwitnessed sites with why. Licensed tests: `test_witnesses.py` (each witness fires its site in its half), `test_generator_mutations.py` (13 sites: the changed set equals the stored one; an unwitnessed site fires in no case) and `test_screen_mutations.py` (11 shapes). Pure: `test_mutation_record.py` (the record is total over the planned mutations, and each generator set holds a witness).
- Results: every generator mutation changes exactly its witnesses, so no other case flips. The screen mutations break agreement on every refusing subject of their shape, except where another rule's refused finding still carries a code the generator gives (6 `blocked_predicate` subjects, design O7). `evidence/independence.md` records what is counted apart (the 4 measured `SHARED` mutations), what is not mutated (19 walker sites, `invocation_allowlist.py`), the 4 sites no case fires, and the 3 shapes with no refused context.
- `MODEL_COLLECTIONS` is still unchanged: all 18 new cases are agentic-home, so no codegen-home case directory exists.
- Verification: licensed `tests/conformance/subset_profile/`: 1401 passed, no skips. agentic `-k "subset or conformance_case"`: 599 passed; `tests/test_subset_site_account.py`: 18 passed.
- Deviations:
  - The 25 linked agentic sites do not all get a witness: 1014 and 702 cannot be reached by a model (above), and the codegen nonunique and negative-bound sites are unreachable because SysIDE rejects the shapes. Each is recorded with its reason in both repos and checked live to stay unreached.
  - The firing tracer is `sys.monitoring`, not `sys.settrace`: line events are switched on per code object, so the 124-case sweep with both halves takes about a minute.
  - Judgment is by outcome and site reasons. The harness does not observe stub causes yet (P4), and no shared-rule site produces a stub.
  - The plan's stencil asserts each witness flips. The stored-set form is stricter: it fixes the whole changed set, which also records "other cases flipped" (none today).
- **Found, for P3: an anonymous assertion by reference splits both checks.** `assert positive;` (an `AssertConstraintUsage` with no name) is refused by the generator as `SI_ID_UNSTABLE` before the profile runs, while the screen reports every rule unverified, which is a `generator_refuses_screen_silent` disagreement. Occurrence parity also fails on it: codegen's occurrence index builds, while agentic-mbse's port aborts at its writers stage with `SI_ID_UNSTABLE`, so ADR 0001 invariant 6 does not hold on this input. The case was not packaged, because keeping it would need an exception in the parity test, which is the owner's call. The named spelling witnesses the site instead. Model: a `constraint positive : Positive { in observed = x; }` in a part def, then `assert positive;`.
- **Found, for P3: three spellings refuse with an unmapped code.** The screen refuses each as `constraint-predicate/blocked_predicate` (`SI_CONSTRAINT_BLOCKED`), but the generator refuses with `SI_EDGE_DANGLING`, carrying no reason. They are an untyped `assert constraint bare;`, `assert constraint check : Constraints::ConstraintCheck;` and a sum of two quantities with different units (`len + mass <= 3.0 [m]`). In the last one the `SI_CONSTRAINT_BLOCKED` site fires, but the logged refusal is `SI_EDGE_DANGLING`. None is packaged; each would be a `code_unmapped` disagreement. A Real-plus-Boolean sum agrees and witnesses the same site.

#### Mid-run audit fixes (2026-10-18, before Phase 3)
Fixes for `audit.md` (Phases 1–2, Needs Work). Experiment plugins are committed in `evidence/experiments/` so each proof can be rerun.
- **Blocker 1 (B6, lens F1/F2).** New licensed `tests/conformance/subset_profile/test_screen_half.py`: the live screen answer equals the stored screen answer for every case, in either home (124 tests, about 2 s together with the screen mutations). `test_screen_mutations.py` now runs the unmutated screen live first and counts a case only when it agreed before and disagrees after, which also folds in Advisory 6 (a change of disagreement kind no longer counts). The stored `mutations.json` screen sets are unchanged and still match.
  - Proof: `PYTHONPATH=.project/active/subset-profile-conformance/evidence/experiments uv run --extra dev pytest -p drift_screen_range tests/conformance/subset_profile/ -q` (licensed) switches off `part-multiplicity/range` for the whole session. Result: 8 failed, 1517 passed. The failures are the 7 range cases in `test_screen_half.py` and `test_screen_mutations.py[part-multiplicity/range]`. The audit's run of the same drift before the fix: 0 failed. Without the plugin the suite is green; nothing to restore, since the plugin patches in memory only.
- **Advisory 1 (reach test).** The patched `ExpressionInventoryError` raise now carries `constraint_profile_blocked`, a reason the catch-all never assigns, and each patched witness asserts its (code, reason) pair: `SI_EVIDENCE_INCOMPLETE` for the inventory converter, `SI_INTERNAL_DEFECT` + `internal_failure_unclassified` for the catch-all. A pure test checks the two pairs and reasons differ.
  - Proof: `PYTHONPATH=… uv run --extra dev pytest -p drop_inventory_converter tests/conformance/subset_profile/test_site_reason_reaches_harness.py -q` (licensed) rebinds the converter's exception name so the branch never matches. Result: 1 failed (`[ExpressionInventoryError__diagnostic_with_referent]`), 10 passed. Before the fix the audit saw 0 failed.
- **Advisory 8 (stale text).** `evidence/versioning.md` records that `v2` landed in Step 2.1. agentic-mbse `test_subset_case_citations.py::test_a_reproduction_is_refused_by_no_rule` no longer lists an anonymous assertion by reference (it was not packaged then). This plan's status line is current.
- **Advisory 5 (disagreement `owner`).** Every entry's `owner` is now `Reid Westwood`, and the field keeps its name. Why a person and not a rename: the spec defines a recorded disagreement as having an owner, and an entry can outlive the phase or work item that wrote it, so a work item cannot be accountable for it. The field's comment in `tests/helpers/subset_profile/cases.py` says so. Which phase decides an entry is in its `reason` text.

### Phase 3 Completion
**Completed:** 2026-10-18. Phase gate passed, except the audit, which is the orchestrator's to run (`/_my_audit`).
**Actual Changes:** one commit in each repo, named in the final report of `briefs/implement_p3.md`'s run. Per-area detail below; the per-row decisions are in `evidence/r3-closure.md`.
**Phase gate (2026-10-18):**
- Snapshots: `git diff --exit-code d73a4fc5` over the committed `instance_graph_snapshot.json` files exits 0.
- Accept/refuse: `test_public_package_oracle.py` and `test_v6_recapture_batch.py` pass inside the full licensed run; `baseline.json` and `batch.json` are unchanged since `d73a4fc5`.
- Regressions: codegen licensed suite (`uv run --extra dev pytest tests/ -q -rfEs`, `.env` sourced) 5143 passed, 9 failed, 9 skipped; the 9 failures are the baseline IDs (`test_study_cli.py` bogus-tool and the 8 `test_check_ledger_4a.py` tests). agentic-mbse (`uv run --all-extras pytest tests/ -q -rfEs`) 3918 passed, 5 failed, 8 skipped, 1 xfailed; the 5 are the all-extras baseline IDs.
- Merge order: `git log subset-conformance..main` is empty in both repos (local refs; nothing fetched), so no rebase.
- Static checks: codegen mypy clean (87 files), ruff 94 (baseline 94); agentic-mbse ruff 118 (baseline 118), mypy 88 (baseline 88).
- Audit: not run here.

#### Agreement (C1–C3)
- `tests/conformance/subset_profile/test_agreement.py` (pure): each case's stored screen answer is judged against its stored generator answer; a disagreement passes only if recorded, and the record's `case:` entries must equal the computed set.
- `tests/conformance/subset_profile/test_fixture_agreement.py` (licensed): for every model root under `tests/fixtures/`, the stored class must hold live, then the live screen is judged against the live generator run, and the record's `fixture:` entries must equal the computed set. Four roots SysIDE cannot load (`source_identity_absent_referent`, `source_identity_binding_forms`, `two_same_leaf_producers`, `subset_profile_occurrence_seed/f1_invalid_redefinition_family`) are checked to be parse refusals on both sides and are not agreement subjects. Codegen-home cases are model roots here too, so their class is held live, but they are `case:` subjects only, so one model is never recorded twice.
- `disagreements.json` now holds 78 entries: 31 cases and 47 fixtures, all owner `Reid Westwood`. Of the cases, 29 are `reproduced_gap` and 2 `codegen_owned` (ES-010); of the fixtures, 26 are `reproduced_gap` and 21 `codegen_owned`. By kind: 71 `generator_refuses_screen_silent` and 7 `code_unmapped` (the five `blocked-predicate-unmapped-code__*` cases, `plant_value_shapes`, `zero_output_calc`); no `screen_refuses_generator_builds`. None is `rg1_pending`. The (subject, kind, codes, reasons) of each entry came from one reviewed run (`/tmp` scratch, not committed); resolution, R3 row and reason were written per family by hand. The two P2.2 item-def entries are gone: those cases are now record cases of the widened rule and agree.

#### Contract changes (agentic-mbse)
- **calc-owned-assertion widened (D11 holds).** New `ContextId.UNMAPPED_OWNER_KIND` and `OwnerKind.REQUIREMENT_DEFINITION`; `_calc_owned_assertion` maps `OwnerKind.OTHER` to the new context. Codegen's owner map is closed (`elaboration/elaborate.py:800-827`), so the refusing set can be stated. Records, matrix row ES-001 and the SA-1 statement updated; `subset-profile/v2` digest re-pinned (`05a9a502…`). The P2.2 item-def cases were renamed (`git mv`) into `calc-owned-assertion__*__unmapped_owner_kind`; three more owners and a requirement-def control added.
- **Occurrence copy fixed for `assert positive;`** (orchestrator call). `occurrence_extraction.py` keys constraint attachments by element ID, as codegen's `_index_constraint_associations` does (`elaborate.py:592-604`); calc attachments still key by declaration ID. Occurrence parity holds on the case; `test_occurrence_parity.py` covers it because it runs every case in either home.

#### Codegen-side changes
- New codegen-home cases (D14): the R3 controls that belong to no rule (ES-002 calc-output neighbor; ES-008 one-subset, outer-redefinition and plain-nesting; ES-009 typed, nested-untyped and package-read; ES-010 library default; ES-011 `out attribute`), the PUSH-DOWN precedence and literal-shape cases, the two DEEP-QUALIFIED-WIRING cases, and the five `blocked-predicate-unmapped-code__*` cases.
- `SeamKind.ATTR_VALUE` and its reader `_attr_value` (`tests/helpers/subset_profile/observe.py`), used to pin which value wins in the precedence cases.
- `test_generator_half.py`: `SI_EDGE_DANGLING` and `SI_ID_UNSTABLE` join `UNLOCATED_CODES`. Their raises on these cases carry no source (`elaboration/identity.py:45`, and the dangling-UUID and producer-cycle raises), so isolation cannot check them; a located refusal with either code is still held to the construct.
- `test_constraint_population_oracle.py`: `subset_profile` joins `MODEL_COLLECTIONS`, since it holds one model per subdirectory.
- `mutations.json`: the deleted item-def IDs removed; the five unmapped-owner cases added to the `_owner_kind` generator set and to both calc-owned-assertion screen sets. New answers name their witnesses: the `_owner_kind` site for the unmapped-owner cases, the `SI_CONSTRAINT_BLOCKED` site for the two quantity-operand cases (it fires, then the run ends `SI_EDGE_DANGLING`).

#### Issues Encountered
- **False premise: "captured" is not "generates".** `fixture_classes.py` classed the 14 fixtures `batch.json` lists as captured as generating. Captured means elaboration sealed a graph; three of them (`constraint_inline`, `constraint_non_numerical`: `CONSTRAINT_NAME_UNSAFE`; `unresolvable_attr_probe`: `REGISTRY_CLASS_NAME_COLLISION`) are refused at generation. The batch now classes only its `refused` fixtures, with their codes; the 14 captured ones moved into `fixture_classes.json` from the reviewed run, each confirmed live.
- **A cited refused case must show the mapped code.** P3 first packaged the three disagreeing spellings and the anonymous `assert positive;` as `blocked_predicate` record cases. `test_case_store.py` (ADR 0001 invariant 1, codegen half) failed on all five: their generator codes are `SI_EDGE_DANGLING` / `SI_ID_UNSTABLE`, not `SI_CONSTRAINT_BLOCKED`. They cannot be reproductions either, since the screen refuses them. They moved to codegen's home as `blocked-predicate-unmapped-code__*` and their citations left the records.

#### Deviations from Plan
- **The anonymous assert-by-reference case lives in codegen's home, not agentic-mbse's package.** The brief asked for it packaged. The records cannot cite it (above), and an uncited record case fails agentic-mbse's `test_every_record_case_is_cited`. In codegen's home, `test_screen_half.py` still holds its screen answer live and `test_occurrence_parity.py` still covers the fix.
- **The three disagreeing spellings were not narrowed.** The narrow-by-default rule (spec L3-6) is for a screen refusal of a model the generator builds; here both refuse. Recorded as `code_unmapped` / `reproduced_gap`; no `kerml-expert` run and no RG-1 entry, because the generator fails closed.
- **ES-010 has a third path that generates.** A calc def's String library default left unbound becomes a `str` entry point with a null default. Recorded as a P4 silent-loss finding.
- **PUSH-DOWN ambiguous typing: the backlog premise is false.** Codegen refuses incomparable typings rather than picking sorted-first.
- **New family: anonymous declarations (`SI_ID_UNSTABLE`).** Recorded as reproduced gaps; a model-wide rule is left for the owner to decide.

### Phase 4 Completion
**Completed:** 2026-10-18. Phase gate passed, except the audit, which is the orchestrator's to run (`/_my_audit`).
**Actual Changes:** agentic-mbse `301590aa` (pre-item 1: its own test for the P3 occurrence fix), `ca43aeea` (pre-item 2: backlog row amended), `95dc8aba` (P4); sysml-codegen one P4 commit, named in the final report of `briefs/implement_p4.md`'s run.
**Phase gate (2026-10-18):**
- Snapshots: `git diff --exit-code d73a4fc5` over the 22 committed `instance_graph_snapshot.json` files exits 0.
- Accept/refuse: `test_public_package_oracle.py` and `test_v6_recapture_batch.py` pass inside the full licensed run; `baseline.json` and `batch.json` are unchanged since `d73a4fc5`.
- Regressions: codegen licensed suite (`uv run --extra dev pytest tests/ -q -rfEs`, `.env` sourced) 5729 passed, 9 failed, 9 skipped; the 9 failures are the baseline IDs (`test_study_cli.py` bogus-tool and the 8 `test_check_ledger_4a.py` tests). agentic-mbse (`uv run --all-extras pytest tests/ -q -rfEs`) 3947 passed, 5 failed, 8 skipped, 1 xfailed; the 5 are the all-extras baseline IDs.
- Merge order: `git log subset-conformance..main` is empty in both repos (local refs; nothing fetched), so no rebase.
- Static checks: codegen mypy clean (87 files), ruff `src/ tests/` 94 (baseline 94); agentic-mbse ruff 118 (baseline 118), mypy 88 (baseline 88).
- Audit: not run here.

#### Pre-items (committed separately, before P4)
- **agentic-mbse guards its own occurrence fix.** `tests/test_sysml/test_occurrence_extraction_constraints.py` with model `tests/fixtures/subset_profile/cases/anonymous_assertion.sysml`: every constraint usage, the anonymous `assert positive;` included, gets an attachment keyed by its SysIDE element ID, owned by `Site`, scoped to the generator roots. Shown failing on the pre-fix `occurrence_extraction.py` (`455c1f26^`): `OccurrenceFailure(IDENTITY_UNSTABLE, stage=writers)`. Passes at HEAD.
- **Backlog row amended.** agentic-mbse `.project/backlog/BACKLOG.md`, PUSH-DOWN-HIER-PROFILE-AMBIG-INHERITED-ATTR: the "sorted-first" sentence replaced by the refusal (`SI_REDEFINITION_INVALID`), citing case `candidate-ambiguous-typing__incomparable_typings__part_usage` and `evidence/r3-closure.md`.

#### Silent-loss families (D9, § D)
- Every family has loss cases and a control: `es-010-string` (the unbound String library default; RG-2), `calc-usage-bare-result-drop` (RG1-3), `es-007-non-numerical` (accepted omission, three cases, control `constraint-predicate__numeric_and__owner_instantiated`, which gained its `catalog_usage` seam), `g1-redefinition-drops-bounds` (RG1-1), `g2-usage-override-of-referenced-bound` (RG1-2), `calc-def-output-stub` (RG1-4 to RG1-11). Each loss block now names its `control` (`LossAnswer.control`, required).
- New seam `contract_parameter` (`tests/helpers/subset_profile/observe.py`): the model contract's parameters minted from a declaration, with key, entry type, Python type and default. It is what shows the null String default and the lost calc-usage binding.
- `tests/conformance/subset_profile/test_silent_loss_seams.py` (pure): the families are exactly design § D's; each loss asserts at a seam its control shares; a stub loss has stubs and its control none. The seam values themselves are held live by `test_generator_half.py`, so the plan's licensed stencil became a pure test.
- `tests/conformance/subset_profile/test_candidate_refusal_marks.py` (pure, D10): for every case a record cites, the admission's `candidate_refusal` holds if and only if the case's loss is `candidate_refusal`.

#### String (ES-010, RG-2)
- Cases for both spellings in every position: template (`…__template`, `…__template_shorthand`), instantiated part (`…__attribute_declaration`, `…__redefinition_shorthand`), bound to a calc input (`candidate-es-010-refusal__string_to_calc_input__binding_value` and new `…__attribute_declaration`, both refused; the new one has its `codegen_owned` disagreement entry), read by another attribute (`…__read_by_attribute`, `…__read_by_attribute_shorthand`). Numeric controls `…__unconsumed_numeric_value__attribute_value` and `…__numeric_value__attribute_value__read_by_attribute`.
- Finding: outside the calculation boundary a String behaves exactly as a Real in the same position, so only the library-default case carries a loss block. This closes the P2.2 premise conflict (note amended above). `rg2-string-policy.md` gives four options and recommends refusing the library-default path (B), with filling the default (D) as the alternative. Not decided.

#### Stubs (D9)
- Twelve `SiteReason` members `compile_*` (`elaboration/diagnostics.py`): one per `CompilationError` raise in `extraction/calc_compat_renderer.py` (each raise passes it) and `compile_dependency_cycle` / `compile_no_expression` for the compiler's two non-raising stubs. `ExactCompilationResult.stub_reason` carries it; `__post_init__` refuses a result whose `MANUAL_REQUIRED`, `stub_reason` and `unsupported_reason` disagree (new `internal_invariant` row in the site account).
- `ManualStubNotice` logged once per stubbed output by `_announce_stubs` (`elaboration/elaborate.py`), right after each calc def compiles; listed in `evidence/changed-outputs.md`. The harness collects notices (`GeneratorObservation.stub_notices`, `stubs()`); `test_live_stubs_equal_the_stored_stubs` holds every stored answer's `stubs` live. Twenty `binding-source__*` answers gained a `compile_invocation` stub (their `Total` sums its input).
- Eleven codegen-home `calc-def-output-stub__*` cases, one per reachable cause, with `compiled_control`. Five renderer sites fire in a model and are mutated (`mutations.json` generator sets; `answer_changed` now compares stubs too). Five fire in none and are `unwitnessed` with the reason: the not-Python check (keyword names stub earlier), the unknown-IR-node branch (closed union), feature chains (refused upstream), no operands, and the unary-operator check (shadowed by the unsupported-operator check).

#### CALC-USAGE-BARE-RESULT-DROP
- The rule criterion holds: agentic-mbse's site facts list a calc usage's own result expression as an `other_expression_site`. New rule `calc-usage-result` (agentic `95dc8aba`), outcome `omitted`, qualified `candidate_refusal`; `REASON_MAPPING` maps `calc_usage_bare_result_not_executed` to `NO_REFUSAL` (`src/sysml_codegen/subset_profile_adapter.py`).
- Finding beyond the plan: the case also loses the usage's `in v = x` binding. Likely cause is `_collect_bound_members` consuming SysIDE's lazy `owned_members` iterator in an `or ()` test (not confirmed). It changes output, not acceptance, so it is recorded in RG1-3 as a defect for a backlog item rather than fixed here.

#### RG-1 and semantics checks
- `rg1-recommendations.md`: RG1-1 to RG1-11, each with question, cases, today's behavior, semantics answer and recommendation. Recommend refuse for RG1-1, RG1-2, RG1-3 and RG1-10; keep the stub (withdraw the mark) for RG1-4 to RG1-7, RG1-9, RG1-11; fix the sanitizer mismatch for RG1-8.
- `evidence/semantics-checks.md`: three `kerml-expert` invocations (G1 and G2 together with both case models; the calc-usage result; the stub causes).

#### Docs
- `docs/architecture/modeling-assumptions.md` § 10 (new): String values, non-numerical constraints, calc-usage result expressions, stubbed outputs, redefinition precedence and incomparable typings, multiplicity through redefinition, and POSITIONAL-FORMAL-REDEFINITION as pending Item 4. Three stale statements amended in place: the String row of "Supported Value Types" and "Literal Values" (a String reaching a calc input is refused), and Validation Rule V10 (incomparable typings are refused, not resolved first-in-order). V9's message was also removed with the legacy lane; its current behavior is marked unchecked.
- `evidence/r3-closure.md`: "Closed in Phase 4" section.

#### Issues Encountered
- A reason value `compile_expression_absent` tripped `tests/conformance/test_no_expression_ast.py` (it bans the substring `compile_expression`). Renamed to `compile_no_expression`.
- A runtime `SiteReason` import at the top of `expression_compiler.py` is circular (through `elaboration/graph.py`); it is imported inside `compile_calc_def_exact`, as the module already does for other elaboration types.
- The citation test needs exactly one finding on a cited case's construct, so the String read-by-attribute model puts the reading attribute on its own line.

#### Deviations from Plan
- **The `kerml-expert` agent link is dangling in this worktree** (`.claude/agents/kerml-expert.md` points at `/home/reid/1cfe/...`). Each check ran as a general-purpose agent given agentic-mbse's `agents/kerml-expert.md` as its role.
- **Stub causes were asked in one invocation**, one numbered question per cause, not one invocation each.
- **G1, G2 and the stub causes have no record mark.** D10 marks a candidate in the record and the case; these have no shared rule that isolates them (G1's screen pair also covers correctly unexpanded usages), so only the case carries it, as design D10 already says for stubs.
- **The record-to-recommendations check is not a test.** A test reading `rg1-recommendations.md` would break when this folder moves at close; every RG-1 id named by a case was checked against the document by hand.
- **Verdict semantics unchanged.** CLEAR still counts a `candidate_refusal`-qualified finding as clean (`indexed-reference__indexed_reference__other_expression_site` is `clear` with the new finding). Changing that is Item 2b's.

#### Orchestrator calls for Phase 5
[AGENT] 2026-10-18: Phase 5 attempts shared rules for (a) anonymous declarations codegen must index (`SI_ID_UNSTABLE`) and (b) ES-002's broad shape (reference into a feature of a calc/item/attribute usage other than a calc output). Each becomes a rule if it can be stated from shared agentic-mbse facts with codegen's indexed-declaration set pinned by cases; otherwise it stays a reproduced gap with its exact boundary written in `r3-closure.md` for Item 5's guidance.

### Phase 5 Completion
**Split count:** H = , L = , T = , tail count = , split taken: 

### Phase 6 Completion

### Phase 7 Completion
**Receipt codegen_rev:** 

---

**Status**: Draft
