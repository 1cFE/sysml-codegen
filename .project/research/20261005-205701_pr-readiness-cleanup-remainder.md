---
date: 2026-10-05T20:57:01-07:00
researcher: Codex
topic: "Remaining cleanup for a sound PR after the elaborator and repository cleanup shipments"
tags: [research, cleanup, release-readiness, elaboration, assurance]
status: complete
last_updated: 2026-10-05
---

# Research: What remains before the next cleanup PR

## Research question and authority

[OWNER-VERBATIM] “I need you to run $my-research to figure out EXACTLY what still needs to be done for cleanup. my goal is within a few days to PR so everything is in a good working state without remnant and slop leftover.”

This is research and a proposed execution scope. Recommendations below are [AGENT], not owner-settled requirements. The baseline is codegen `6872977541eae935d4be2789f48f723ffea7101b` on `main`, after PR #15. Companion artifacts are Agentic `9e3a847393cabe0471391842b4da5861654abbed` and TEAx `8d877460ac4f6f264561d916e40c1708adb13397`. Fusion was inspected at `a58a0911c` on its existing work branch; its unrelated working changes were preserved. Current evidence is distinguished from older recorded evidence throughout.

## Summary

- The elaborator implementation and legacy-code retirement are done. PR #10 (`385e163`) shipped the cutover, PR #13 (`82244a0`) shipped parser/identity follow-through, and PR #15 (`6872977`) shipped repository cleanup. The durable decision is `.project/adr/0005-exact-identity-elaboration-replaces-string-resolution.md:19`; absence is tested by `tests/conformance/test_public_authority_switch.py:158` and `tests/unit/test_elaboration_import_boundaries.py:25`.
- Fresh licensed validation has one guidance-contract failure, 2,139 passes, nine intentional parity skips, and 96 execution deselections. All 96 real-TEAx tests pass against archived current revisions. Ruff passes; mypy still reports 27 errors in six files. Logs and artifact identities are recorded below.
- Actual cleanup remains in serialization, unit metadata, the duplicate-driver fixture and its acceptance pins, small typing/test residue, documentation, and traceability. No evidence supports another elaborator rebuild or a broad source refactor. Concrete paths and acceptance criteria appear in the execution table.
- The surviving downstream spec is partly delivered and partly superseded, but has genuine composed-proof, lineage, and historical-impact obligations. Its unchecked boxes are not a current implementation plan. The complete criterion disposition is below; the original requirement grades must survive any amendment.
- A codegen cleanup PR can ship without claiming full ELABORATE-FIRST completion. Formal Item 8 closure additionally requires the named historical assurance evidence and external-use attestation. A green suite cannot substitute for those obligations (`.project/active/elaborator-downstream/spec.md:76`, `:87`; `.project/backlog/epic_elaborate_first_architecture.md:493`).

## Fresh working-state evidence

| Check | Observed result | Scope and evidence |
|---|---|---|
| Licensed default suite | 2,139 passed; 1 failed; 9 skipped; 96 deselected | `.venv/bin/python -m pytest tests/ -q --tb=short`, after loading the companion license environment. `/tmp/cleanup-research-default-pytest.log`; 161.59 seconds. |
| Guidance failure reproduced alone | Same single failure | `tests/conformance/test_self_binding_guidance_contract.py:201`; `/tmp/cleanup-research-guidance-recheck.log`. |
| Real TEAx | 96 passed; zero skips/failures | Archived codegen/Agentic/TEAx revisions above, built Agentic wheel, explicit provenance and SimKit root; `/tmp/cleanup-research-execution.log`; 9.45 seconds. |
| Skip reasons checked separately | 28 parity cases passed; nine skipped because the golden has no calculation output expressions | `tests/conformance/test_calc_compat_parity.py:74`; `/tmp/cleanup-research-compat-skips.log`. These are not license skips. |
| Ruff | Pass, with deprecated configuration warning | `.venv/bin/ruff check src/`; `/tmp/cleanup-research-ruff.log`. Move `select` into `[tool.ruff.lint]` (`pyproject.toml:61`). |
| Mypy | 27 errors in six source files | `.venv/bin/mypy src/`; `/tmp/cleanup-research-mypy.log`. Breakdown below. |
| Ledger paths / public surface | 304 rows, zero path problems / zero unrowed breakages | `.venv/bin/python scripts/check_ledger_4a.py paths` and `surface`. Use the project interpreter; the system interpreter lacks Agentic. |
| Document distinctness | 19 documents; zero identical-content groups | `python3 scripts/check_doc_distinctness.py`. This establishes distinct bytes, not accurate teaching. |
| Gated derivative accounting | `65 = 56 carriers + 9 deletions` | `python3 scripts/check_gated_manifest.py --check`. |
| Wheel builds | Codegen and Agentic wheels build | Hatchling against archived committed sources; wheels under `/tmp/cleanup-research-artifacts/wheels/`. |

`/tmp/cleanup-research-artifacts/execution-provenance.json` binds full commits, source archive hashes, the Agentic wheel hash, resolved roots, and interpreter. `/tmp/cleanup-research-artifacts/validation-evidence.json` retains result counts and SHA-256 hashes of the six validation logs. Scratch artifacts are session evidence, not permanent release archives. Final PR validation must record its own final revisions.

The guidance failure is a wording/contract mismatch, not broken elaboration. Agentic's `project_templates/MODELING_PROCESS.md.template:71` contains an inline warning, “A self-named `in volume = volume;` binds to itself.” The semicolon matches the codegen test's unmarked executable-example detector. The published convention already permits warning prose without that terminator (`tests/conformance/test_self_binding_guidance_contract.py:13`, `:191`). [AGENT] Amend that warning to the convention; keep the test's ability to detect actual unmarked self-binding examples. The change originated in Agentic `ce80472` on September 14, and is now in its main checkout. October 4 validation against Agentic `88e2489` did not exercise this newer template.

## Architecture insights

The live boundary is parse → exact identity/occurrence elaboration → one graph projection → rendering → semantic/physical seal. Names remain rendering metadata. The public live and snapshot routes share that authority; codegen tests pin the retired builders' absence (`CLAUDE.md:48`; `.project/adr/0005-exact-identity-elaboration-replaces-string-resolution.md:19`). Current cleanup belongs at concrete metadata, rendering, test-evidence and documentation boundaries. Reintroducing name-based formal binding, a second catalog authority, or the deleted release harness would work against that architecture.

## Feasibility assessment

[AGENT] The local cleanup fits a few-day PR because it mostly corrects narrow code defects, removes small dead test/annotation bodies, reuses existing generation/runtime helpers, and amends stale documentation. The larger uncertainty is assurance closure, not an unimplemented elaborator. Licensed snapshot recapture is required for C4; public generation regression itself does not need the license. A small Agentic documentation change resolves C1; the real-TEAx capability required by current tests is already delivered and freshly passing.

## Proposed cleanup PR: finite execution list

All actions in this table are [AGENT] recommendations. Each has a concrete stopping condition. Estimates are implementation time, not a guarantee; rows can share validation and document edits.

| ID | Required work for the proposed PR | Files and evidence | Acceptance | Estimate |
|---|---|---|---|---|
| C1 | Repair the current guidance-contract failure | Agentic `project_templates/MODELING_PROCESS.md.template:71`; codegen `tests/conformance/test_self_binding_guidance_contract.py:191` | Published warning stays accurate; the focused guidance file and full licensed default suite pass. If done upstream, record the companion commit in the codegen gate. | Under 1 hour |
| C2 | Reject nonfinite contract JSON in both serialization forms | `src/sysml_codegen/contracts/serialize.py:28`, `:34`; `contracts/models.py:33`; existing tests `tests/unit/test_contract_models.py` | NaN and positive/negative infinity cannot be fingerprinted or written as contract JSON. Both encoders reject before writing; finite contract bytes remain unchanged. Extend actual contract tests, not only an arbitrary JSON helper test. | 1–2 hours |
| C3 | Repair UTF-8 unit-source positioning; make prose-unit ambiguity explicit | `src/sysml_codegen/extraction/feature_metadata.py:96`, `:104`, `:165`; `tests/conformance/test_extractor.py:29`; `tests/conformance/test_unit_lane_port_metadata.py:110` | A multibyte comment before a declaration cannot move its unit read onto another line. Existing authored unit strings and agreement/refusal behavior are preserved. Add a located regression with neighboring misleading prose. General comment/parenthesis heuristics require the compatibility disposition described below. | 2–4 hours for offset repair |
| C4 | Remove the historical fixture's inert standalone driver occurrence and re-anchor its pins | `tests/fixtures/fusion_tea/designs/hif_ife/hif_driver.sysml:100`, its committed snapshot; `tests/conformance/test_projection_wiring_contract.py:41`, `test_elaboration_fail_closed.py:158`, `tests/execution/test_fusion_tea_real_teax.py:55`, `:213` | Licensed recapture; nine total exits instead of eleven; no standalone-driver channels; historical LCOE remains `270.1211779380445`; every-and-only mutations and located enum refusal still pass on remaining owners. Document the fixture's historical provenance. | 2–4 hours |
| C5 | Clear the existing type-check errors without weakening the configuration | Six generation files listed below; fresh mypy log | `mypy src/` exits zero; precise annotations and validated optional values; no broad ignores or disabled checks; valid generated bytes unchanged. | 3–5 hours |
| C6 | Delete the uncollected retired test body and tighten licensed fixture failure behavior | `tests/conformance/test_dm08_enforced_surface.py:83`; `extraction/data_models.py:66`; `test_extractor.py:334`, `test_return_style_extraction.py:46`, `test_calc_compat_parity.py:53`, `tests/conftest.py:144` | Remove the dead registry method and its exclusive expectation data; retained NewType tests still pass. Remove inert v5-only field metadata after re-anchoring its tests to the actual live/snapshot contract. Once a valid license is established, failure to load a required fixture fails instead of silently skipping. Nine empty-golden parity skips remain accurately explained. | 1–2 hours |
| C7 | Add a compact public generation output-regression gate | `tests/conformance/test_zero_entry_package_golden.py:35`, `:91`; `test_public_route_baselines.py:144`; `[EMIT-STEP-REGRESSION-GATE]` at `.project/backlog/BACKLOG.md:93` | Public `run_codegen` from representative committed snapshots compares a complete file set and committed expected bytes/digests for calculation/multi-output, aggregation/alias, and constraint/report shapes. A real template mutation fails. Intentional differences are reviewed; regenerating both sides in one run is insufficient. Snapshot generation is license-free. | Half to one day |
| C8 | Correct live documentation and CLI help | Exact document list below; `README.md:51`; `src/sysml_codegen/cli/__init__.py:1046`, `:1075`, `:1088` | README commands actually run; live documents describe current types, UUID evidence, occurrence sums, preflight checks, and zero-executable-constraint reports; snapshot help names the actual default. | Half to one day |
| C9 | Repair the current traceability matrix and add its missing source-identity projection | `docs/architecture/verification-matrix.md:147`, `:155`, `:227`, `:320`, `:402`, `:449`, `:504`; `.project/concepts/constraint-execution-lifecycle-requirements.md:495` | Remove retired mechanisms from current PASS claims; preserve any surviving product obligations with real tests; no absent-test citations; add bounded `REQ-SI` rows from durable `LC-SI-*`/Item 3 coordinates; recount totals. The matrix still exists; retired `verification/` tooling is unrelated. | Half day, combined with C8 |
| C10 | Reconcile project state and isolate unrelated owner drafts | `.project/CURRENT_WORK.md`, `.project/backlog/BACKLOG.md`, `.project/backlog/README.md:36`, epic files, `.project/mental-alignment/coordinator-lessons-20260906.md:3` | One short current-status document; one entry per open ticket with honest priority; completed/superseded obligations referenced through registers/history; active downstream requirements reconciled; no unrelated mental drafts included or discarded. Existing text-contract tests must preserve meaning and close provenance when updated. | 2–4 hours |

[AGENT] A focused cleanup PR is plausible in roughly three working days if C8–C10 are handled together and C7 reuses existing generation helpers. Full historical Item 8 closure adds the assurance work below; do not promise its completion from this estimate. Use a separate clean branch/worktree for implementation because the present index contains owner mental-model drafts (`git status` at research start). Research itself did not modify production code or tests.

### Serialization and unit metadata details

Both serializer functions were called directly with NaN and both infinities during research. Compact output contained `NaN`/`Infinity` tokens; written JSON was rejected by `json.loads(..., parse_constant=raise)`. This reproduces the encoder defect. It does not claim a fresh end-to-end invalid-model seal run. The model fingerprint uses the compact encoder (`src/sysml_codegen/contracts/model_contract.py:75`), and float defaults admit nonfinite values (`contracts/models.py:33`). `allow_nan=False` on both forms preserves finite serialization and stops the invalid JSON path.

The unit offset defect is source-code evident: CST `start_byte` is compared to cumulative character lengths (`feature_metadata.py:96`). Fixing only offsets does not cure arbitrary comment words or short parentheses being treated as units (`:104`, `:165`). This is a second, real metadata ambiguity. [AGENT] Tighten nonunit-prose rejection while explicitly preserving accepted authored unit annotation forms; do not silently replace the existing contract with brackets-only units. Existing source/test acceptance includes bare `m³/s`, and snapshots carry `Dimensionless`, `Fraction`, `K`, `MW`, `Pa`, `T`, `W`, `m`, `m²`, `m³`, `m³/s`. Retyping or dropping legitimate units needs a recorded compatibility decision. The narrow byte-offset repair can proceed independently (`tests/fixtures/catf_mfe_gated/PROVENANCE.md:455`, `:503`; `tests/conformance/test_unit_lane_port_metadata.py:125`).

### Exact typing work

| File | Fresh diagnostics | Minimum correction |
|---|---|---|
| `generation/preservation.py:118`, `:175` | Two untyped module arguments | Annotate the actual graph module input and preserve implementation-protection behavior. |
| `generation/test_gen.py:22` | One untyped argument | Annotate the actual graph input. |
| `generation/schemas.py:17`, `:32`, `:48` | Three untyped arguments | Annotate existing module/graph/template inputs. |
| `generation/stencils.py:22`, `:34`, `:55`, `:111`, `:156`, `:202` | Six untyped functions; four Any returns at `:30`, `:31`, `:48`, `:50` | Use existing graph/template types and make returned context strings type-correct; avoid changing stencil behavior just to satisfy typing. |
| `generation/modules.py:28`, `:40`, `:61`, `:397` | Four untyped functions; four Any returns at `:36`, `:37`, `:54`, `:56` | Same correction for wrapper rendering. |
| `generation/pipeline.py:178`, `:183`, `:190` | Three unchecked optional channel/key values | Narrow/validate `producer_channel` and `qualified_name` before lookup/rendering. A blanket cast would hide the real invalid-input boundary. |

The numeric totals in this table are grouped by diagnostic kind; the authoritative exact 27 lines are `/tmp/cleanup-research-mypy.log`. Changes should be validated against generated output and the existing relevant generation tests. This is annotation/boundary cleanup, not a module redesign.

### Exact documentation corrections

| Home | Current false or obsolete claim | Concrete amendment |
|---|---|---|
| `README.md:35`, `:51`, `:57` | Dev-extra ambiguity; commands omit `generate`; no snapshot examples | Align installation/development with the companion layout; use `--extra dev`; show live generation, snapshot capture, and license-free from-snapshot generation. |
| `CLAUDE.md:69`; `reference/02-orchestration.md:76` | Fixed preflight list omits current checks; doc 02 still advertises deleted V11 | Describe the actual preflight block at `cli/__init__.py:1241` or delegate to one current account. |
| `docs/architecture/overview.md:55`; `reference/00-pipeline-overview.md:168` | Report only exists when executable constraint outputs exist | Any authored constraint usage requires a report, including an empty assessment denominator (`elaboration/project.py:1023`; product `0005`). |
| `reference/01-extraction.md:99`, `:112`, `:187` | Deleted usage/hierarchy extraction treated as live; array sum becomes multiplicity times one value | Retain live calculation extraction and the semantic-evidence boundary; remove obsolete extractor mechanisms; describe occurrence-based elaboration by pointer. |
| `reference/09-data-models.md:29`, `:98`, `:119`, `:158` | Deleted registry enforcement; old name-keyed compiler inventories; obsolete catalog shape; positional Pydantic example | Describe exact UUID fields (`extraction/data_models.py:101`), current four catalog lists (`resolution/models.py:418`), surviving name wrappers, and valid keyword construction. |
| `reference/14-expression-compiler.md:15`, `:31`, `:126`, `:204`, `:216` | Old compiler entry point and name-based dependency inventory; deleted aggregation walker treated as a second current path | Document `compile_calc_def_exact`, UUID-based attachment/dependency discovery, and names only at Python rendering. Remove the obsolete walker comparison. |
| `reference/16-computed-attributes.md:37` | Deleted computed-attribute model classes supposedly remain importable | Delete that statement. |
| `reference/20-module-registry-generation.md:202` | Registry model table includes deleted extraction classes | Replace with the actual graph module inputs. |
| `docs/architecture/overview.md:236` | C05 categorized as retired while its row names current elaboration | Correct the live component index; historical deleted components need no current module pointers. |
| `tests/conformance/README.md:32`, `:78`; `tests/fixtures/fusion_tea/README.md:68` | Training material still recommends deleted extraction snapshots/baselines or future v5 retirement | Show current fixture/source expectations and historical provenance accurately. |
| `.project/backlog/README.md:36` | Archive-to-completed workflow contradicts record-then-delete | Point at `.project/README.md:46`. |

Paths beginning `reference/` in this table are under `docs/architecture/`. This is a finite live-document repair, not a new numbered-document set. Clearly labeled historical material in docs 02, 06, 18, 26 is not a current semantic promise; [AGENT] remove irrelevant historical bodies when it makes the live account shorter, while retaining needed current links and durable decisions. Git preserves the removed material. Ordinary Markdown links/anchors in README, CLAUDE, and architecture docs resolve; the larger problem is links to semantically stale content.

### Traceability defects already established

Seventeen current PASS rows cite six absent test basenames. This is a mechanical minimum, not proof that every other row is sound: REQ-AST-10; REQ-BASE-01–04; REQ-CL-03; REQ-EXT-13–14; REQ-HR-01–08; REQ-LVP-08. Absent files are `test_agg_literal_dispatch.py`, `test_baselines.py`, `test_concrete_constraint_model.py`, `test_type_indexing.py`, `test_hierarchy_resolver.py`, `test_uncovered_params.py`. REQ-CL-03 and REQ-BASE-01 also cite retained tests; remove stale citations without discarding their genuinely surviving evidence. BASE rows about deleted committed baselines cannot be certified merely by same-generator determinism (`verification-matrix.md:155`; `test_public_route_baselines.py:144`).

REQ-EXT-02–05 cite an existing extractor test file but their old test bodies were retired; comment headings remain (`tests/conformance/test_extractor.py:174`). REQ-DM-08 still claims four deleted registry dictionaries, while the matching test method was only renamed out of collection (`test_dm08_enforced_surface.py:83`). REQ-EXT-07 and REQ-EC-07 retain useful exact-route behavior but need their UUID fields and current evidence described accurately. Retirement applies to the obsolete mechanism; a surviving model-level obligation needs its own current evidence, not automatic deletion.

### Additional matrix corrections and exact counts

The present table contains **288 rows: 149 PASS, 138 RETIRED, one PARTIAL**. Its summary incorrectly reports 156 PASS and 131 RETIRED (`verification-matrix.md:9`). The family index omits the eight-row CS family and has stale family grades. Recount the rows, summary, index and footer together after amendments.

| Rows | Action | Current evidence |
|---|---|---|
| REQ-AST-02, REQ-AST-05, REQ-AST-10 | Retire deleted dispatch subjects/conventions. | `test_ast_dispatch_invariant.py:105`; deleted legacy walker. |
| REQ-EXT-02–05, REQ-EXT-13–14, REQ-HR-01–08, REQ-LVP-08 | Retire deleted extraction mechanisms, preserving any separately supported model-level invariant. | `test_extractor.py:174`; retired hierarchy/usage extraction and absent type-indexing tests. |
| REQ-EC-01, REQ-DM-06 | Retire the original dispatch/importability claims. | `test_expression_compiler.py:105` records retirement; `test_data_models.py:516` proves a model is absent, not importable. |
| REQ-AST-01/03/04 | Describe the actual retained no-FCE/OE-site guard, two audited multi-type sites, and FCE-before-FRE order. | `test_ast_dispatch_invariant.py:109`, `:127`, `:135`. |
| REQ-EXT-07, REQ-EC-07, REQ-DM-08 | Correct exact sidecars/UUID intermediate inventory and surviving NewType surface. | `test_extractor.py:307`; `test_exact_compiler_core.py:183`; `test_elaboration_payload_identity.py:93`; `test_dm08_enforced_surface.py:90`. |
| REQ-EC-05, REQ-REG-02 | Keep live obligations and correct their evidence nodes. | `test_exact_compiler_core.py:104` proves cycle treatment; `test_exact_route_registry.py:58` proves imports point to files. |
| REQ-CA-09, REQ-PIPE-03, REQ-RES-04 | Keep the live alias/channel obligations; remove deleted registry mechanism wording. | Their current row-local evidence targets exact projection. |
| REQ-PMM-01–03 | Narrow to genuinely tested metadata field presence or mark rendering fidelity PARTIAL; YAML/registry smoke is not comment/default evidence. | `test_data_models.py:211`, `:238`, `:255`; `test_elaboration_generation_boundary.py:21`. |
| REQ-BASE-01–04 | Retire obsolete captured-baseline claims; preserve a separately stated reproducibility property or replace with C7's actual output gate. | Deleted baseline reader; `test_public_route_baselines.py:125` proves repetition, not an independent expected result. |
| REQ-BASE-06 | Identify a specific sorting/discovery-order proof or grade the preserved obligation UNTESTED. | Its cited same-snapshot byte-repeat test does not vary discovery order. |
| REQ-SR-03 | Grade PARTIAL unless retained evidence covers the two missing leaves. | The current evidence cell itself says four of six leaves; `tests/unit/test_stencils.py::TestSmartRegenStubUpgrade`. |
| REQ-CL-03 | Keep the live catalog requirement; remove the absent model-test citation. | Retained `test_constraint_catalog_totality.py` nodes in its existing cell. |

One additional small remnant is literal `metadata={"snapshot_exclude": True}` on six exact extraction dataclass fields (`extraction/data_models.py:66`, `:103`). The only readers found are tests asserting that metadata dictionary, not any production serializer (`tests/unit/test_extractor.py:127`; `tests/conformance/test_extractor.py:303`). The v5 dataclass serializer retired; v6 serializes the normalized instance graph. [AGENT] Remove the inert annotations/comment and replace the metadata-self-assertions with current UUID sidecar and actual snapshot-boundary evidence. Preserve the live declaration identity fields themselves and the v6 serialized schema. This is a small obsolete annotation removal, not a schema migration.

## Downstream spec: every success criterion reconciled

This table follows the 21 success criteria in `.project/active/elaborator-downstream/spec.md`, in order. “Delivered” below is read-only source/evidence inspection unless covered by the fresh codegen gates above. Customer results are inherited from their retained artifacts; customer suites were not rerun by this research.

| SC | Disposition | Remaining action and evidence |
|---|---|---|
| 1 | Delivered customer route; final adoption not recorded in this old item | Cite live/snapshot generation and authenticated stock TEAx loading in `../fusion-tea/tests/test_codegen_teax_acceptance.py:60`, `:91`, `:137`. |
| 2 | Delivered customer workaround removal | Fusion `5a889ac57` removed the standalone occurrence; `9e1ff87bb` delivered D5 migration; current customer channels are canonical (`test_codegen_teax_acceptance.py:35`). |
| 3 | Fixture cleanup remains; exact present-day customer convergence is superseded | C4 removes the inert historical fixture occurrence. Later owner-directed customer physics repairs mean today's customer is a separate acceptance surface. |
| 4 | Fixture pins remain | Update the three named C4 test files; nine total exits includes constraint evaluation and report. |
| 5 | Historical anchor delivered; current-customer numerical premise superseded | Historical `270.1211779380445` remains in `tests/execution/fusion_tea_arithmetic.py:148`. Customer Fusion `243625b47` repaired physical/source facts; Sept 10 study `record.md` §3 reports `240.666461`. Preserve each identity's own result. |
| 6 | Strong component evidence; one joined model-to-study proof remains | Reuse `test_fusion_tea_mutation_teax.py:329`, stock study persistence from `test_numeric_evidence_teax.py:76`, and customer source mutation tests. Join one modeled source mutation, verified package, affected consumers, constraint report, and reopened study under named package identities; no new release harness is needed. |
| 7 | Every-and-only behavior delivered; carry into SC6 composition | Existing gain mutation tests check changed and unchanged outputs (`test_fusion_tea_mutation_teax.py:329`); select a named unrelated consumer in the joined proof. |
| 8 | Specific predecessor/new lineage link missing | Record the retained predecessor store and all eight old/new compatibility fields; current Sept 10 record §12 is single-fingerprint, not a July lineage link. |
| 9 | Generic refusal delivered; named historical transition remains | Customer `tests/study/test_ife_native_route.py:55` proves mismatch refusal and unchanged store bytes; demonstrate the named transition against a copied historical store, preserving the original. |
| 10 | Historical impact census needs final recorded disposition | Use the finite census below; distinguish module-direct numeric sweeps from stock-study output evidence. |
| 11 | Verdict-only acceptance stands; historical prose needs bounded amendment | Preserve `2294/2301 + 7` as a verdict comparison. Amend `../fusion-tea/exploration/ife_e2e/study/findings.md:7`, `:30`, `:49` at its existing home instead of promoting historical numerical output to current swept truth. |
| 12 | External-use attestation pending | The owner was asked during research. Repository searches cannot establish absence of external reports or decisions. Preserve a bounded unknown until answered. |
| 13 | Still open; not retired by deleting release tooling | Add the independently grounded `REQ-SI` projection to the surviving matrix. `verification/` deletion (`7fb488f`) did not delete `docs/architecture/verification-matrix.md`; `test_register_contract.py:149` still reads it. |
| 14 | Delivered bounds | Preserve product `0002`'s deep-override evidence bound and `[ANCHORING-ARRAYED-DIAGNOSTIC]`. |
| 15 | Final obligation/evidence reconciliation missing | Adopt this criterion table with durable `LC-SI-*`/Item 3 → final test/evidence coordinates when implementation/assurance is completed. |
| 16 | Delivered authoring guidance | Agentic `docs/patterns/plant-idiom.md` covers D5/D6/D7, self-binding, definition/redefinition, indexed refusal, and labeled pinned/measured examples; codegen contract tests at `:152`, `:164` pin it. C1 repairs one later summary warning. |
| 17 | README work remains | C8. |
| 18 | Retirement largely delivered; live-document residue remains | Cleanup `201483c` retired the obsolete numbered docs. C8 fixes surviving inaccurate accounts; do not resurrect retired docs. |
| 19 | Superseded by later owner-authorized retirement | Legacy hierarchy extractor, its tests, and doc 25 retired in cleanup. Remove their old preservation requirement from the active spec. |
| 20 | Fresh baseline captured | This report records exact current gates and one failure; compare final cleanup against corresponding commands and dependency identities. |
| 21 | Final assurance evidence/close still to do | Record what was newly run, inherited, superseded, or still unknown. Keep the single Item 8 completion authority; a partially delivering PR does not close the epic. |

The August 17 spec commit `f6aec94` explicitly anticipated major revision after `stop-reinventing-the-parser`. Later changes to its folder only unblocked the predecessor and updated ledger IDs. Its old customer branch base `7703ba1e`, obsolete doc-retention requirements, and blanket numerical freeze premise are not a sound present execution contract. Amend those parts at their existing homes; preserve owner-originated scope, verdict bounds, independent-oracle requirements, and the source of ratified agent decisions (`spec-review.md`, resolutions L1/L2/L3).

## Historical July impact and lineage

The retained stock-study store is available at `../fusion-tea/exploration/ife_e2e/study/_work/viability_study.db`. It was read with SQLite `mode=ro&immutable=1`, without importing TEAx or executing the generated package. Its SHA-256 is `90f85b1ff2c7c32d17093e974d6803d52f9d4925311779cc66e50103dd51d8de`. All 2,301 completed cases have available evidence artifacts whose file hashes match their database digest references; the directory has 4,603 JSON files overall, so a directory glob is not this study's evidence set.

The retained identity has a July 20 filesystem date and is not established as the original July 13 package/run identity. Its numerical evidence is **gain-inert, not wholly frozen**: 39 efficiencies × 59 gains; LCOE and recirculation each take 39 values and never change across the 59 gains at fixed efficiency. At efficiency `0.35000000000000003`, gains 10, 80 and 300 all yield LCOE `270.12117793804447` and recirculation `0.07222302470027443`, while viability responds. Capital cost, Meier COE and reactor cost each have one value; constancy alone is not proof of a defect without their historical dependency contract. The active spec's blanket “LCOE and recirculation values are design-point values” claim must be amended to the measured source/identity bound, not inherited unchanged (`spec.md:24`).

| Compatibility field | Retained predecessor value |
|---|---|
| study ID | `ife-viability-acceptance` |
| executable fingerprint | `a04c82958096d10c0b3afaa19dcaf16012011a01de04525ea1e823b90f6ceb3b` |
| model-contract fingerprint | `d0fff42903444cfe9f14ae2190d464c9c93a093d6d8656d3a62c157092f6d539` |
| study-definition fingerprint | `80b982383aa7a5caeb8d80202a80c483506e5fb811016d0e035930f1167c7653` |
| input schema | `input-v1` |
| evidence schema | `v1` |
| strategy identity | `prepared-grid/v1` |
| strategy configuration | `21e1f1b900bb22262bb2c6395e84a57befc1413f2eeaa061fee644de8edc1806` |

Observed store queries were `SELECT * FROM compatibility` and `SELECT inputs_json,evidence_digest,state FROM cases ORDER BY commit_order`. Artifact JSON was read by each referenced digest and grouped by exact efficiency to count output variation across gain. Reproduction: `python3 /tmp/cleanup-july-census.py`; retained JSON `/tmp/cleanup-research-july-census.json`, SHA-256 `bf3f4f87d11cb13d045bd5d77704e67266f8890b3cfd9fde018ccff5ca30d1ad`. This is a read-only data census, not a new propagation implementation or a rerun of historical physics.

### Finite consumer dispositions

Paths in this table are relative to Fusion Tea unless explicitly marked codegen.

| Consumer/artifact | Disposition and cleanup |
|---|---|
| `exploration/ife_e2e/study/_work/viability_study.db` plus its 2,301 referenced artifacts | Affected historical numerical evidence. Preserve and identify it; label LCOE/recirculation as gain-inert for this retained identity. Copy the store for a compatibility refusal proof. Original store and artifacts stay untouched. |
| `exploration/ife_e2e/study/acceptance_table.csv` | Unaffected verdict comparison: fields are `eta,gain,eta_g,old_viable,new_verdict,new_viable,at_boundary,match`; no numerical cost/power columns. Preserve the 2,294 exact matches plus seven boundary rows. |
| `exploration/ife_e2e/study/prepare_once_benchmark.json`, `bench_prepare_once.py` | Bounded timing/verdict evidence, not numerical sweep certification. Historical benchmark compares responses and reports 200 parity cases. |
| `exploration/ife_e2e/study/findings.md:7`, `:30`, `:49` | Amend interpretation at this home: verdict acceptance remains; numerical source-propagation was not certified; obsolete catalog/entry-channel/toy-name bridges are historical. |
| Codegen `.project/reference/fusion-tea-ife-sweep/FACTS.md:21` | Correct result locations and distinguish the module-direct CSV, stock-study store, and verdict-only acceptance table. |
| Codegen `spec.md:24` and August 3 forensic reports at `20260803-203011_entry-surface-fanout-forensics.md:137`, `:234` and `20260803-202453_backtracking-fanout-forensics.md:428` | Reconcile overbroad carry-forward wording to the measured retained-store identity. A dated claim about the original July 13 identity remains unverified; do not silently equate it with this store. |
| `work/active/20260713_constraint-exec-acceptance/brief.md:387` | Correct the location/bound if this remains an active authority. Its verdict-only acceptance account at `:318` remains valid. |
| `.project/concepts/study-driven-model-development.md:205`, `.project/backlog/epic_stellarator_mbse_demo.md:40`, `:125`, and `work/completed/20260720_WI-027_demo-constraint-execution/{spec,design,plan}.md` | Inherited verdict/runtime/benchmark evidence remains valid at that bound. They are not numerical every-and-only certification and need no physics rerun for this defect. |
| `data/ife_sweep/sweep_results.csv`; `data/ife_sweep/{ife_viability_eta_gain,ife_viability_by_freq}.png`; mirrored `docs/demo/images/` images | Separate module-direct computation, unaffected by this binding defect. The CSV has 11,505 rows, 5,558 distinct LCOEs, 1,189 recirculation values and 6,038 net-power values. |
| `exploration/ife_e2e/{sweep_ife,plot_sweep}.py`; `work/completed/20260705_WI-015_ife-end-to-end-demo/{demo_report,findings}.md`; `docs/demo/{closed-loop-story.md,closed-loop.html,index.html}` | The historical sweep at Fusion `bcfeab044` supplies swept eta/gain/frequency directly to calculation input models; the plotter reads that CSV. These are not exports of the affected stock-study store. Preserve their separate numerical bound. |
| `modeling_project/HYPOTHESIS_DOSSIER.md:82`, `:124`; `work/backlog/epic-pipeline-derisk-demo.md:53`; `.project/reports/epic-pipeline-derisk-demo-progress.md:16`; `.project/research/20260904-135403_blog-series-topic-catalog.md:328`, `:354` | Downstream references to the separate module-direct demo route. Do not label them numerically frozen on the basis of the 2,301-case study. |
| Historical `run_anchors.py` and 72 tracked files under `exploration/ife_e2e/outputs/` | Fixed-point evidence, not swept-row numerical results. Later customer source/physics repairs are separately authorized changes. |

This census searched current codegen/Fusion project documentation, exploration, data, demo publications and direct numeric-file/store consumers, plus the named historical runner commits. Residual unknowns are external use, undiscovered exports of this gitignored store, and exact equivalence to the original July 13 numerical identity. A repository census cannot settle those by asserting absence.

[AGENT] Finish the historical cleanup with one short durable impact/lineage record adopting these bounded dispositions; amend misleading live claims at their existing homes. There is no basis for rerunning every July plot, rebuilding the customer model to its former LCOE, or declaring the verdict acceptance invalid. Owner attestation is pending; the specific copied-store compatibility proof and the joined model-to-reopened-study proof still need execution under the final chosen identities.

## Project tracking cleanup

[AGENT] Replace the 1,549-line current-work history with current state, exact inherited/fresh validation, remaining cleanup/assurance, genuine open decisions, and register/backlog pointers. Preserve the owner-directed parser close with its historical `Needs Work` audit and separately filed diagnostic debt; `tests/conformance/test_register_contract.py:232` currently pins that provenance. Update its text assertions to the new concise homes instead of retaining pages solely to satisfy a substring test.

[AGENT] Reconcile these exact backlog surfaces: absent-folder February rows (`BACKLOG.md:146`); indexed-expression P1/P3 duplicates (`:154`, `:684`); alias-silence duplicates (`:174`, `:696`); completed constraint-semantics decomposition (`:201`); resolved TRUTH-DEBT filings (`:843`, `:900`, `:989`, `:1082`); already discharged requirement-tag record (`:713`); retired-mechanism filings for nested override (`:528`), inherited formula (`:958`), v5 fixtures (`:776`, `:972`), dotted-leaf fallback (`:1098`), and old architecture-unification (`:1371`). Preserve only independently demonstrated remaining obligations. Generation boundary shipped (`6523521`); the explainer was built then purged (`507e838`). Hierarchical-output disappearance alone does not prove completion; recover its historical scope before recording a defer/retire decision.

[AGENT] Correct ELABORATE-FIRST's Ready header and stale Item 3 pending checkpoint (`epic_elaborate_first_architecture.md:4`, `:208`, `:246`). Correct GAP-CLOSE's F1-open prose against its verified July 20 closure (`BACKLOG.md:282`; `epic_gap_close.md:4`, `:63`, `:144`). Preserve or explicitly supersede its historical wave-gate evidence gap rather than falsely certifying old commits from today's tests. Completed REPO-CLEANUP can lose its epic narrative after unique rulings/evidence are accounted for; fix or remove obsolete harvest pointers (`epic_repo_cleanup.md:116`, `:326`) as part of that disposition.

The mental-alignment files contain owner feedback and proposed owner-controlled skill changes (`coordinator-lessons-20260906.md:3`). Exclusion from PR #15 is not deletion authority. [AGENT] Preserve their current index/worktree state and prepare the cleanup PR in isolation. Register scripts and the ledger checker/test are live defenders; the checker caught five stale rows during cleanup (`epic_repo_cleanup.md:344`). The test-only catalog assembler has actual fixture consumers (`tests/helpers/retired_catalog_assembly.py:9`); its name is not grounds for deletion, though obsolete explanatory prose should be amended. Historical citations in registers and research are intentionally recoverable from git; the absent `completed/CHANGELOG.md` follows the standing close rule (`.project/README.md:46`).

## Work that should stay separately owned

[AGENT] Keep schema-bumping snapshot codec consolidation, numeric-compiler unification, indexed/scalar-function capabilities, acausal relations, calculation-definition gates, and customer physics corrections in their own scope. The cleanup defects above do not require them. Calculation-definition gate implementation still has explicit owner authorization outstanding (`BACKLOG.md:391`).

The positional-formal backlog ticket does not establish a codegen name-matching bug: current elaboration uses parser redefinition identity (`elaboration/elaborate.py:1888`, `:2096`), and the fixture records positional behavior (`tests/fixtures/modeled_default_fidelity/PROVENANCE.md:27`). Better repeated-input diagnostics remain reasonable; changing binding semantics requires its own evidence. Duplicate aliases are retained in the graph (`project.py:1052`) and intentionally first-wins for the one filename per exit channel (`generation/pipeline.py:240`; `tests/unit/test_exit_point_aliases.py:65`). Correct the stale extraction-loss description before deciding an output-policy change. The previously fabricated internal-defect locations and missing parsing passthrough are already repaired (`elaborate.py:170`; `exact_pipeline_context.py:302`).

## PR stopping conditions

[AGENT] Ship when C1–C10 are complete, the licensed default gate has zero failures with every skip explained, the real-TEAx lane passes on final immutable artifacts, Ruff and mypy exit zero, registry/ledger checks pass, and committed output-regression expectations cover the changed emission/fixture shapes. Record intentional fixture differences separately from unchanged-output comparisons. The PR body must name any remaining Item 8 assurance obligations; full Item 8/epic closure waits for their own evidence.

[AGENT] Finish the old item with one narrowly reused composed proof, the historical store transition and lineage record, the bounded consumer census/owner attestation, and an obligation-to-evidence reconciliation. This closes assurance rather than rebuilding the elaborator. How long external-use disposition takes depends on the owner's answer; no absence was inferred.


## Recommendations

[AGENT] Start with C1–C4 and the existing failing/static gates, then C5–C7. Update C8–C10 together against the final code/fixture semantics. Run final licensed/default and artifact-bound runtime gates once at the actual PR candidate, review the diff, and ship. C7's baseline expectations must be deliberately updated after C4's known fixture change rather than generated from both sides of the same test run.

[AGENT] In parallel with ordinary cleanup documentation, record the bounded July census above and its old compatibility identity. Reuse existing mutation/study helpers for the composed proof and copied-store refusal. If the PR is ready sooner, state exactly which assurance cells remain open and keep Item 8's completion authority intact. Independent audit is useful before claiming that old item complete; a new implementation/design epic is not required merely to remove this residue.

## Open questions

The remaining owner-dependent fact is external use of the affected study outputs. The unit-comment acceptance boundary also needs a recorded compatibility decision if tightened beyond the byte-offset repair. Conflicting agent-filed capability priorities should be consolidated as unscheduled follow-ons with their recorded reasoning, rather than silently promoted to cleanup blockers. The existing mental-alignment drafts remain owner review material; implementing in an isolated worktree avoids forcing their disposition merely to submit this PR.


## Code references

The execution, documentation, matrix and criterion tables above are the file-level reference index. Start implementation with `contracts/serialize.py`, `extraction/feature_metadata.py`, the Fusion Tea fixture and its three named acceptance files, the six mypy files, and the public generation/runtime helpers. Reconciliation authority is the retained `LC-SI-*` requirements plus the active item's provenance-carrying review, not unearned PASS cells. Historical recovery coordinates are PR #10/#13/#15, `f6aec94`, purge `507e838`, and the two named Fusion sweep-runner commits; they avoid another repository archaeology pass.


## Follow-up: prior knowledge and independent review — 2026-10-06

This count concerns the ten cleanup task groups, not a count of every subfinding: six have previously documented underlying problems (C1–C5 and C7), three mix known debt with newly identified details (C8–C10), and one is predominantly newly identified residue (C6). Most of this proposed PR clears known debt; the research contributed a current baseline, exact remaining locations and corrections to stale assumptions.

| Group | Known before this research | New contribution |
|---|---|---|
| C1 | October 4 CURRENT_WORK recorded the modeling-template guidance failure on the companion branch. | Confirmed the same class of warning failure now occurs against current companion main. |
| C2 | Missing nonfinite JSON rejection was documented in August 20 research §Incidental bugs and the SERIALIZE-NAN-SEAL ticket. | Reproduced both encoders with all three nonfinite cases. |
| C3 | UNIT-SCRAPE-BYTE-OFFSET was filed August 21 (`BACKLOG.md:40`), including prose-unit heuristics. | Confirmed current source and identified why brackets-only tightening would change legitimate bare-unit behavior. |
| C4 | The August 16 downstream spec names the duplicate fixture occurrence and acceptance pins (`spec.md:53`). | Enumerated current pins and separated historical fixture cleanup from later customer physics. |
| C5 | October 4 CURRENT_WORK already records 27 mypy errors. | Located the exact six files and distinguished annotations from optional-value behavior changes. |
| C7 | EMIT-STEP-REGRESSION-GATE was filed August 25 (`BACKLOG.md:93`). | Defined a bounded public-snapshot gate and corrected the unnecessary license requirement. |
| C8 | README/documentation repair was already in the downstream spec (`:90`). | Found specific surviving false architecture accounts and stale CLI help. |
| C9 | The missing REQ-SI family was already specified (`spec.md:77`). | Established absent-test citations, overclaimed coverage, wrong summary counts and inert registry test residue. |
| C10 | Tracking drift and staged mental artifacts were documented in the October 4 status report. | Reconciled later shipments, duplicate priorities and obsolete mechanism tickets. |
| C6 | General risk of tests hiding failures was known; these exact remnants were not found in the reviewed earlier records. | Identified the uncollected registry body, test-only v5 exclusion metadata and licensed-load skip paths. |

The July impact/lineage/composed-proof obligations also predate this research (`spec.md:65`, `:69`). New findings are the retained store's measured gain/efficiency distinction, availability and verified digests of all 2,301 referenced artifacts, and the unaffected direct-module sweep/publication boundary. That evidence changes the scope of historical correction; it is not a newly discovered current elaborator defect.

[AGENT] Independent review should concentrate on C3's unit semantics, C4's inert-occurrence proof and recapture, C5's added runtime validation, C6's deletion/test-boundary claims, C7's independent regression oracle, and C9/C10's requirement/evidence dispositions. Pure annotations, CLI spelling and the two small JSON encoder changes normally need focused validation and ordinary final-diff review, not separate design review. A provenance review should check the July store identity and consumer distinction before amending historical claims or closing assurance obligations. Bundle this into one fresh code/test reviewer on the final diff and a separate focused assurance reviewer; there is no need for ten independent review cycles.
