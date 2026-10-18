# Design: Independent conformance corpus and per-site codes (EXEC-SUBSET-CONTRACT Item 2a)

**Status:** Draft, revision 3 (2026-10-18). Revision 2 answered the round-1 review (Rework) and spike S1 ([spikes/s1/findings.md](spikes/s1/findings.md)). Revision 3 answers the round-2 review (Revise, four Majors, [design-review.md](design-review.md)), which needs no third round. Next: the orchestrator checks the Majors against this text, then `/_my_plan`.
**Owner:** Reid Westwood
**Created:** 2026-10-18 · **Revised:** 2026-10-18
**Branch / base:** sysml-codegen `subset-conformance` at `07fd2374` (spec base `b5663c07`); agentic-mbse sibling `subset-conformance`, base `ccd57d83` (Item 1 merge), spike run at `882edc6a`

## Overview

2a builds a corpus of small SysML models, each with a stored answer for what the generator does and what the shared contract (the screen) says. Tests run both halves, check that the stored answers agree, and make any drift between the generator, the contract and the stored answers fail a test. A required pre-merge run in agentic-mbse carries that check to contract changes, since neither repository has CI.

## Related Artifacts

- Spec: [spec.md](spec.md); review with resolutions: [spec-review.md](spec-review.md); product-lens ledger: [product-lens.md](product-lens.md); owner gates RG-1..3: [briefs/align.md](briefs/align.md)
- Design review: [design-review.md](design-review.md) (Rework; resolved in § Orchestrator decisions); spike S1: [spikes/s1/findings.md](spikes/s1/findings.md)
- Epic: agentic-mbse `.project/backlog/epic_executable-subset-contract.md`, Item 2a. The epic lists no Required Reading for 2a.
- Item 1 archive (agentic-mbse `.project/completed/20261018_exec-subset-profile/`): `design.md`, `evidence/r3-proposal.md`, `evidence/site-reconciliation.md`, `evidence/acceptance.md`, `evidence/r2-mutations.md`, `evidence/adr-0012-amendment-draft.md`
- Decision records: sysml-codegen `.project/adr/0004-derive-occurrences-from-exact-evidence-or-refuse.md`, `0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md`, `0008-cross-repo-merges-use-merge-commits.md`, `0012-exclusive-semantic-evidence-ownership.md`, `0016-installer-reuse-through-an-api-version-pin.md`; agentic-mbse `.project/adr/0001-subset-profile-capability-ownership.md`; product `.project/product/0003-no-workarounds-for-bad-models.md`

## The Point

**[INFERRED]** (ratified by owner, 2026-10-18, spec brief and `briefs/align.md`) Prove, with evidence independent of the screen, that the shared contract matches what this generator actually does, and make drift between them fail a test in sysml-codegen. Test volume is not the goal, and neither are tests that check the screen against itself.

Why it matters: Item 1 wrote down which SysML shapes the generator executes, as rule records in agentic-mbse, and checked them once against 80 probe runs of codegen `b5663c07`. Nothing fails today when the generator changes. Later items (2b `check`, 3 L6, 5 guidance) will tell modelers what will generate on the strength of this contract, so it has to be held to the generator mechanically.

Two owner constraints bound the work. **[NEED]** (owner, `briefs/align.md`) Any change to what the generator accepts or refuses is RG-1, String policy is RG-2, and merges and ADR filing are RG-3. **[NEED]** (P-0003, owner-verbatim: "we do NOT create workarounds to accept bad models -- we follow what KerML, SysMLv2 and SysIDE support") Recommendations follow the language, not convenience.

## Orchestrator decisions (2026-10-18)

All **[AGENT] (orchestrator, 2026-10-18)**, made on the design review and spike S1. Agent-grade: challenge by re-deriving against the reason given.

| # | Decision | Where |
|---|---|---|
| O1 | No CI exists. Keep a required pre-merge run in agentic-mbse that exercises codegen against the screen, using `codegen_suite.py` and what it imports from `probe.py`, with its output directory a parameter. Stage a fuller ADR 0001 amendment. State plainly what only that run catches. | D13, § Cross-repo enforcement |
| O2 | agentic-mbse keeps screen tests on real models, with one copy of each model. Choose a single-source layout; a hash-guarded copy is the fallback only. | D14 |
| O3 | Screen mutations are judged against the stored generator answer. | D5, § B |
| O4 | `disagreements.json` is hand-edited only, and a test fails if a writer appears. | D3 |
| O5 | The reason carrier keeps the 22 committed v6 snapshots byte-stable; 2a changes no snapshot format. | D8 |
| O6 | Define agreement for generation-stage refusals that have no code. | D15, § C |
| O7 | Fixtures with several constructs are judged by the spec's per-subject rule, not a stricter one. | § C |
| O8 | A plain exception becomes a coded refusal outside RG-1 only if it already reaches `run_codegen` as a refusal. Otherwise it is an RG-1 candidate. | § E |
| O9 | Group E gets an estimate so the split can trigger; the E5 rescan moves to the final phase. | § E, Handoff |
| O10–O13 | Spike amendments: D5 neutralizes the statement that emits a site, with 4 hand patches; mutations compare reasons and stub causes, so reasons come first and shadowing sites get distinct reasons; shared agentic-mbse site mutations are not independent evidence; the spike's unchecked shapes are known limits. | D5, D8, § Independence limits |
| O14 | D12 (no version bump, A2 in ADR 0016 form) stands; the review found no harm. | D12 |
| O15 | (R2-M1) The receipt hashes every file under `src/agentic_mbse/sysml/` plus `src/agentic_mbse/errors.py`, found by glob, not a hand list, so a new module is covered without anyone adding it. | D13 |
| O16 | (R2-M2) The runtime loader checks only the `case:<id>` form. Whether the case exists is checked by an agentic-mbse test. `tests/helpers/subset_records.py` keeps working. | D4, D14 |
| O17 | (R2-M3) The per-site `reason` survives the rebuild in `orchestration/elaborated_pipeline.py` (`:289-356`, `:446`). `ExactTypeError` and `ExpressionInventoryError` gain the field. A test checks that a reason set at the raise site reaches the harness. | D8 |
| O18 | (R2-M4) The receipt test lands in P7. | D13, Handoff |
| O19 | (round 2, phasing) The two group A tests that need P2's cases land in P2. The split trigger becomes a count an agent can evaluate. | § A, § E, Handoff |
| O20 | (round 2, minors) The receipt records the codegen revision, and a `pre_pr` check ties it to the merging codegen commit. A P-0001 amendment is staged beside the ADR 0001 one; filing both is the owner's at merge (RG-3). The concurrent Item 4 session is a merge-order risk for covered files. | D13, Decision records, Risks |

O15–O20 come from the round-2 review ("Revise", [design-review.md](design-review.md) round 2), which also asked for the minor fixes m2, m3, m5 and m8. Those are applied in place.

## Research Findings

Verified at sysml-codegen `07fd2374` and agentic-mbse `subset-conformance`. Paths are relative to each repo's `src/` package unless stated.

**The generator route**
- `run_codegen` (`sysml_codegen/cli/__init__.py:1144`) is the one entry point. It returns `bool` and logs every refusal at ERROR as text (`:1189-1230`). The name-safety refusal already passes structured data with `extra={"constraint_name_safety": ...}` (`:1208`), read back in `tests/unit/test_cli_generation.py:348`.
- Refusal carriers: `ElaborationError.findings` of `ReadinessFinding` (`extraction/source_evidence.py:40`); `ElaborationDiagnosticError.diagnostics` of `Diagnostic` (`elaboration/graph.py:74`); `CodeGenerationError` (`core/errors.py:33`), whose code is only a message prefix such as `REGISTRY_CLASS_NAME_COLLISION:` or `PREDICATE_COMPILE_FAILED:`. None has a reason field.
- `Diagnostic` is part of the v6 snapshot encoding with a fixed key set (`snapshot/instance_graph.py:947-995`). But `InstanceGraph.require_projectable` raises on any diagnostic (`elaboration/graph.py:922-926`) and runs before sealing (`snapshot/envelope.py:310`), so a sealed graph, and every committed snapshot, has an empty diagnostics list.
- The live route rebuilds every refusal before `run_codegen` sees it (`orchestration/elaborated_pipeline.py:289-356`). It converts `SemanticEvidenceError`, `ExpressionInventoryError`, `ExactTypeError`, `ElaborationInvariantError` and `GraphValidationError` into new `Diagnostic`s, and `ElaborationError` findings into new `ReadinessFinding`s (`_readiness_with_referent`, `:399`). `_diagnostic_with_referent` (`:438-455`) copies a `Diagnostic` field by field, so a new field is dropped there unless it is copied.
- A calc def output the renderer cannot compile becomes `MANUAL_REQUIRED` (`extraction/expression_compiler.py:291`); its cause is free text and is dropped at `elaboration/elaborate.py:1266`. Compilation happens once per calc def at `elaborate.py:704`.
- The generated `model_contract.json` embeds the constraint catalog, whose `usage_records` carry a closed disposition (`resolution/models.py:303`, vocabulary `elaboration/graph.py:262`).

**Existing test idioms**
- Per-fixture expectations are JSON under `tests/expectations/<topic>/`, with missing-fails and stranded-fails (`tests/conformance/test_constraint_population_oracle.py:89`). `scripts/capture_v6_batch.py:110` turns a refusal into a sorted code multiset.
- `tests/fixtures/v6_recapture_batch/batch.json` records the elaboration outcome of the 37 corpus fixtures; `tests/expectations/public_package_oracle/baseline.json` records that 3 of them refuse at generation.
- `tests/conformance/test_diagnostic_provenance_sites.py:44-95` is a narrow raise-site scanner (four codes, three files).

**The contract side (agentic-mbse)**
- `extract_subset_facts(model, extra_roots=())` (`sysml/subset_extraction.py:466`) and the pure `evaluate_subset_profile` (`sysml/subset_profile.py:1285`); import by submodule.
- The loader accepts `probe:` and `corpus:` citations and checks form only (`subset_profile.py:396-409`). `SUBSET_PROFILE_VERSION` is pinned to a digest of the records and the allowlist only (`tests/test_sysml/test_subset_profile_version.py`), not to extractor or evaluator code.
- Real-model screen tests: `tests/test_sysml/test_subset_profile_rules_instantiation.py` and `test_subset_profile_rules_modelwide.py` read the 80 probe models through `tests/helpers/subset_probe_judge.py`.
- `scripts/subset_profile/codegen_suite.py` runs codegen's pytest suite against a chosen agentic-mbse revision in an isolated tree. It imports `build_tree`, `child_env`, `read_identity`, `read_license_key`, `resolve_rev`, `sibling_state` and `IsolationBreachError` from `probe.py`, and `PINNED_CODEGEN_REV` from `subset_probe_judge.py`. Its output directory is hardcoded to the Item 1 archive (`:43-50`).
- agentic-mbse ships package data through hatch (`pyproject.toml:49-63`). `extraction/check_corpus/` is shipped data, but it is runtime data for `agentic-mbse extract --check` (`extraction/check.py:120`), not test inputs for another repository.
- Both halves import agentic-mbse modules well beyond the subset-profile files: codegen uses `sysml/expression_ir`, `syside_adapter`, `expression`, `constraint_extraction`, `constraint_facts`, `data_models`, `expression_facts`, `qualified_names`, `helpers`, `types` and `agentic_mbse.errors`. The screen uses `subset_facts`, `occurrence_facts`, `fact_refs`, `expression` and `constraint_extraction` (round-2 review, H5).
- `tests/helpers/subset_records.py:85, :101` builds synthetic records that cite `probe:<pair>` for every pair and loads them with `load_rule_records`, which is pure over text (`subset_profile.py:587-596`).
- Neither repository has CI configuration. codegen depends on the sibling checkout by editable path (`pyproject.toml:122`).

**Spike S1** (`spikes/s1/findings.md`)
- In-process site disabling works at every code shape tried, by replacing the owning function's `__code__`. Identity is kept, so by-name imports need no re-binding.
- Eliding only `raise` reaches 15 of the 42 linked public sites; neutralizing the emitting statement reaches 38 of 42, and 478 of 502 sites. Four linked sites need hand patches.
- 8 of 10 behavioral mutations flipped their witness. 2 were shadowed: a later check produced the same code (ES-002's site fell through to ES-009's; `_render` line 78 fell through to line 81).
- Mutating a shared agentic-mbse site moved both the generator and the screen.
- Timing: about 9 ms per case for the generator half and 4 ms for the screen half. Both halves over all 152 fixture directories take 22.5 s. The corpus extrapolates to 30–40 s against a current licensed suite of 113 s.
- The licensed suite had 10 failures before any 2a change (see Implementation Notes).

**Versioning.** agentic-mbse reports 0.1.3 before and after Item 1. The v6 envelope refuses a different `agentic_mbse.__version__` (`snapshot/envelope.py:459-461`), so a bump invalidates the 22 committed snapshots. Not checked: agentic-mbse git tags or any package index.

## Core Concept

**The corpus is a set of small models, each carrying two stored answers that must agree.**

1. A **conformance case** is one model (usually one construct plus a control sibling) with two stored answers: the generator's (generated, or refused with these codes and reasons) and the screen's (these findings, this verdict).
2. **Live tests hold each stored answer to its source.** The generator half runs `run_codegen` on the case with the screen patched to raise. The screen half runs `extract_subset_facts` and `evaluate_subset_profile`.
3. **A pure test holds the two stored answers to each other.** Under codegen's reason-to-code mapping, the stored screen answer must agree with the stored generator answer, or the case must be in the hand-edited disagreement record. This stops the screen checking itself: its stored answer is constrained by the generator's.
4. **Everything else checks against the corpus.** Records cite cases. The mapping must be witnessed by cases. A mutation disables one detector and must break agreement with, or the match to, the stored generator answer.

**Where each fact lives: a fact lives in the repository that can check it live.**
- **Screen facts live in agentic-mbse's package.** A case that a record cites, or that tests a shared rule's recognizer, keeps its model and its stored screen answer as package data. agentic-mbse's own tests run the screen on those real models, and check that each `case:` citation exists and shows its pair. codegen reads them through the package it already depends on.
- **Generator facts live in sysml-codegen.** Every case's stored generator answer, the cases that exist only for codegen observations (site witnesses with no rule, stub causes), the codegen half of the site account and the occurrence seed.
- **Each model has one copy.** Nothing is duplicated, so nothing has to be kept in sync by hand. The rule applies to facts; a test input sits with the fact it serves.

Because neither repo has CI, one link is procedural: a change to the screen is checked against the generator only when codegen's suite runs against it. A required pre-merge run, with a receipt that agentic-mbse's own tests demand, makes skipping it fail a test (D13).

## Key Bets

- **B1. A single-construct case pins one (rule, shape, context) pair for the generator.** The generator fails fast and reports one error class, so one construct plus a passing control isolates it. Item 1's 80 probes rested on this. *If false → a case witnesses the wrong pair; the construct-location check catches most of it.*
- **B2. Neutralizing the one statement that emits a site disables exactly that detector, in-process.** **Confirmed by S1** for the mechanism (every shape tried) and for 478 of 502 sites; 4 linked sites need hand patches. *If false for a later site → it joins the named hand-patch list.*
- **B3. The corpus runs in a time the licensed suite can carry.** **Confirmed by S1**: about 30–40 s added to 113 s, running each mutation only on its witnesses. *If false → people skip the suite and drift detection weakens.*
- **B4. Codegen can read case models, screen answers, records and the occurrence summary through agentic-mbse's package alone.** All are package code or package data under D14. *If false → the [HARD] boundary forces copies.*
- **B5. The generator's outcome is constant within each context label** (Item 1 B5, carried). *If false → variation cases split the context.*
- **B6. Distinct per-site reasons are enough to tell a disabled site from a shadowing one.** S1 showed both shadowed mutations differed only in which site fired, not in code. *If false (two shadowing sites must share a reason) → that pair needs a recorder observable instead; S1 named but did not test it.*

## Key Decisions

| Spec "Deferred to design" question | Decision |
|---|---|
| How expectations are stored | D1, D14 |
| How detectors are disabled | D5 |
| Form of the disagreement record | D3 |
| `run_codegen` or stage calls | D2 |
| Seam per silent-loss family; how a stub is observed | D9 |
| Where the parity seed and normalizer live | D6 |
| Whether the codegen half of `site_account.csv` moves | D7 |
| How the stable site reason is spelled, carried, rendered | D8 |
| How agentic-mbse records cite cases | D4, D13 |
| How a record marks a candidate refusal | D10 |
| Rule or reproduced gap for ES-002/008/009/CALC-DEF-BARE-RESULT | D11 |
| Version bump and publish | D12 |

- **D1. One JSON answer file per case, following the `tests/expectations` idiom.** Codegen's stored generator answers sit at `tests/expectations/subset_profile/cases/<case_id>.json`, one per case wherever its model lives. Case IDs keep Item 1's form `<rule>__<shape>__<context>[__<variant>]` for rule cases and `<row-or-family>__<variant>` otherwise. Schema in Appendix A. *Rejected: one table for all cases (the phase audit reviews per-case diffs); TOML (codegen has no TOML expectation store).*
- **D2. The generator half calls `run_codegen` and observes through structured log data.** Each refusal log call in `run_codegen` gains `extra={"refusal": …}`. The `except Exception` branches carry the converted `unexpected_public_failure` error, so the harness sees what users see. The snapshot and parse branches carry their own exceptions. For seams the harness spies on `elaborate_model_paths` as `exact_pipeline_context` calls it, and reads `model_contract.json` from the output. Nothing is reimplemented. *Rejected: stage calls in order (they skip `run_codegen`'s error mapping); parsing ERROR text (codes also occur inside detail text).*
- **D3. The disagreement record is one hand-edited JSON file, equal to the computed set.** `tests/expectations/subset_profile/disagreements.json`. Entry fields: subject (`case:<id>` or `fixture:<path>`), kind (`generator_refuses_screen_silent`, `screen_refuses_generator_builds`, `code_unmapped`), generator codes, screen refused reasons, resolution (`codegen_owned`, `reproduced_gap`, `rg1_pending`, `rg2_pending`), R3 row, owner, reason. A test requires the computed set to equal the record on (subject, kind, codes, reasons). **No tool writes this file.** A pure test fails if any Python file under `src/`, `tests/` or `scripts/` other than the reader (`tests/helpers/subset_profile/cases.py`) and that test names `disagreements.json`, or if the reader contains a write call. Limit: a path built from pieces evades the text check; the phase audit is the backstop. The test also rejects an entry with an empty owner or reason, and an `rg1_pending` entry with no `RG1-<n>`. `REASON_MAPPING` is code and is edited by hand. Any capture helper for stored answers writes only the generator and screen blocks, and refuses to write a screen answer that fails agreement unless a matching disagreement entry already exists. *Rejected: a flag inside each case (fixtures have no case file).*
- **D4. Records cite cases as `case:<id>`, and enforcement of ADR 0001 invariant 1 is split by what each repo can see.** agentic-mbse's loader accepts `case:` for every outcome and checks only the form: the kind is `case:` and the ID starts with the pair it backs. It reads no package data and stays pure over text, as it is for `probe:` today (O16). An agentic-mbse test, `test_subset_case_citations.py`, checks the rest: each cited case exists in the package, and its stored screen answer contains that (rule, shape, context, outcome). So synthetic records in `tests/helpers/subset_records.py` keep loading; they switch to `case:<pair>` citations, which need no packaged case. codegen's tests require the case's stored generator answer to exist, pass live, and agree with the screen answer. Every non-`unconfirmed` pair cites at least one case or `corpus:` fixture; codegen checks `corpus:` citations the same way. `probe:` citations are removed: cases replace probes. *Rejected: probe citations beside cases (two live authorities, against ADR 0001 invariant 5); a citation file written by codegen and read by agentic-mbse (reverse dependency).*
- **D5. A generator mutation neutralizes the one statement that emits a site, chosen by site ID. It passes when the witness's observed reasons or stub causes differ from its stored generator answer.**
  - *Mechanism (S1).* The helper finds the innermost statement containing the site's line. It rewrites `raise …` → `pass`, a recorder call (`self._diagnose(…)`, `self._record_readiness(…)`, `diagnostics.append(…)`) → `pass`, and `return [finding]` → `return []`. It recompiles the owning top-level function or method and assigns the new code to the existing function's `__code__`, then restores it. Function identity is kept, so by-name imports see the change.
  - *Hand patches.* Four named sites, in `mutate.py`: agentic-mbse `executable_profile._evaluate_usage_against_definition`'s three `_non_executable_block`/`_missing_body_block` returns, and codegen `expression_evidence._indexed_refusal`, patched at its caller's raise.
  - *Judgment.* The comparison uses stored reasons (D8) and stub causes (D9), not codes or compilability alone. Shadowed sites otherwise look like survivors. So a site's mutation test can pass only once its reason exists (§ Handoff ordering).
  - *Screen mutations.* A screen mutation patches the recognizer inside one rule, not the finished findings. It passes only when the mutated live screen answer **fails agreement with the stored generator answer**: a refusing case loses its mapped refused finding, or a generating case gains one. Matching or mismatching the stored screen answer does not count.
  - All patched private names, in both repos, are listed in one table in `mutate.py`, so a rename fails by name. All mutations run in the default licensed suite.
  - *Rejected: eliding only `raise` (reaches 15 of 42 linked sites, S1); about 110 hand patches; source-copy mutation in scratch trees (cannot run in the suite).*
- **D6. The occurrence seed and normalizer move to sysml-codegen; the stored oracle captures retire.** This is already decided by ADR 0001 invariant 6 (owner choice "A (ii)": a permanent parity test in codegen). The 34 seed models go to `tests/fixtures/subset_profile_occurrence_seed/<case>/`. One normalizer, `tests/helpers/subset_profile/occurrence_parity.py`, maps agentic-mbse's `OccurrenceStructure` and codegen's `OccurrenceIndex`, aborts included, to one schema. agentic-mbse's `test_occurrence_parity.py`, its seed, the `expected.json` captures and `occurrence_oracle_schema.py` retire. agentic-mbse's other occurrence tests stay. *Rejected: seed as package data (the comparison still needs codegen); hash-guarded copy.*
- **D7. The codegen half of the site account moves to sysml-codegen; agentic-mbse keeps its 61 rows.**
  - The codegen account moves to `tests/expectations/subset_profile/site_account.csv`, adding a `reason` column. agentic-mbse's matrix drops its codegen `sites` lists, so the codegen-site-to-row link lives once, in the account's `matrix_row` column. codegen checks `rule` against packaged rule IDs and `matrix_row` by form.
  - Witness links live with the case data the site's owner can read. Codegen sites are named in the stored generator answer (`generator.witnesses`). agentic-mbse sites are named in the packaged case (`agentic_site_witnesses`). agentic-mbse's account test checks that every public agentic-mbse row has a packaged witness. Codegen's mutation test reads both.
  - The scanner's codegen half is ported to `tests/helpers/subset_profile/site_scan.py`. It also resolves agentic-mbse site IDs from the installed package source. agentic-mbse's `scan_sites.py` narrows to its own tree.
  - The narrow scanner in `test_diagnostic_provenance_sites.py:44-95` folds in: its provenance check becomes a query over `site_scan.py` output.
  - *Rejected: a frozen copy of the codegen rows in agentic-mbse.* Limit: a codegen row naming a nonexistent tracked-gap row ID is not caught.
- **D8. A stable site reason is a member of one closed codegen enum, `SiteReason`, carried off the snapshot-encoded types.**
  - `SiteReason` lives beside `ElaborationCode` in `elaboration/diagnostics.py`. It is snake_case, disjoint from `SUBSET_REASON_CODES` (tested), and distinct for sites that can shadow each other (ES-002 vs ES-009; `calc_compat_renderer.py:78` vs `:81`).
  - *Carriers.* `ReadinessFinding`, `ElaborationInvariantError`, `CodeGenerationError`, `CompilationError`, `ExactTypeError` (`extraction/errors.py`) and `ExpressionInventoryError` gain `reason: SiteReason | None`. `Diagnostic` gains the same field with default `None`.
  - *The live-route rebuild copies it (O17).* Every converter in `orchestration/elaborated_pipeline.py` passes `reason` on: the `except` branches at `:289-356`, `_readiness_with_referent` (`:399`), `_semantic_evidence_diagnostic` (`:419`, from the `SemanticEvidenceCode` table below) and `_diagnostic_with_referent` (`:438-455`). The `CodeGenerationError` branch (`:357`) re-raises the same object, so it keeps its fields.
  - *Reach test.* A licensed test, `test_site_reason_reaches_harness.py`, takes one witness per carrier type and per converter branch. It requires the `reason` set at the raise site to appear in the harness's `extra={"refusal": …}` observation. A future rebuild that drops the field then fails by name, rather than showing up later as mutations that seem to survive.
  - *Snapshot stability (O5).* `Diagnostic` is in the v6 encoding, so its encoder and decoder are unchanged and stay byte-stable. The encoder also refuses a `Diagnostic` whose `reason` is set, so a reason is never silently dropped. That cannot happen on a valid graph: `InstanceGraph.require_projectable` (`graph.py:922-926`) raises on any diagnostic before sealing (`snapshot/envelope.py:310`), so sealed graphs carry none. A pure test asserts all 22 committed snapshots have an empty diagnostics list.
  - *Relayed agentic-mbse sites* get their reason from a total table keyed by `SemanticEvidenceCode`.
  - *Rendering.* Messages end in ` (reason: <id>)`.
  - *Rejected: per-site `ElaborationCode` members (spec Non-Goal); encoding `reason` in the snapshot (a format change, 2b's).*
- **D9. Each silent-loss family is asserted at one named seam, and a stub announces its cause.** The seams are an instance-graph node by declaration identity, a computation-graph entry point by source declaration, a `model_contract.json` catalog record by usage declaration, and `CalcNode.compilability`. Declarations are found by qualified name in the loaded model, then compared by `DeclarationId`, never by text search. A stub shows as `MANUAL_REQUIRED` plus a `ManualStubNotice` warning, logged once per (calc def, output) at `elaborate.py:704` with `extra={"manual_stub": …}`. The notice carries the `CompilationError`'s `SiteReason`. Family table in § D. *Rejected: putting the cause on `CalcNode` (a snapshot change); runtime values in the default lane (generated modules need TEAx).* Limit: from-snapshot generation shows `MANUAL_REQUIRED` without the cause.
- **D10. A candidate refusal is a new record qualification, mirrored in the case.** `Qualification` gains `candidate_refusal` (on `omitted`, `excluded`, `admitted`). The stored generator answer carries `loss: {family, disposition, rg1: "RG1-<n>"}`. A pure codegen test requires the two to agree in both directions. Recommendations live in `rg1-recommendations.md` here. Stub causes have no shared rule, so only the case carries the mark.
- **D11. Rule or reproduced gap is decided per row by the rule criterion, once its cases exist.** A rule needs a refusal branch whose reaching contexts can be stated, with facts from shared agentic-mbse facts and no heuristic. A rule adds a rule function, reason, record and any fact to agentic-mbse. A gap adds a `SiteReason`, cases and a `reproduced_gap` entry. One line per row goes in `evidence/r3-closure.md`.
- **D12. No agentic-mbse version bump; the contract is identified by `SUBSET_PROFILE_VERSION`, following ADR 0016** (O14). `_upstream_pins.py` gains the pin, and the adapter checks it at import. The requirement stays `agentic-mbse>=0.1.3,<0.2`. Criterion A2 is met in that form: the evidence states that no package version identifies the contract. One bump, `subset-profile/v1` → `v2`, covers all of 2a's record changes. No publish. *Rejected: 0.1.4 with a `>=0.1.4` bound (invalidates the 22 snapshots, 2b's work).*
- **D13. A required pre-merge run carries the generator check to agentic-mbse changes, and a receipt makes skipping it fail a test** (O1).
  - *The run.* `scripts/subset_profile/codegen_suite.py` is kept. It gains `--codegen-rev` (replacing `PINNED_CODEGEN_REV`), `--out` (replacing the archive path) and `--select` (default `tests/conformance/subset_profile`). The probe helpers it imports move to `scripts/subset_profile/isolated_tree.py`. It runs codegen's licensed subset-profile tests against the agentic-mbse revision in an isolated tree. It fails on any failure, and on any skip of a license-gated test.
  - *Covered files (O15).* Every file under `src/agentic_mbse/sysml/` (code, the records TOML and `subset_cases/`) plus `src/agentic_mbse/errors.py`, found by glob in sorted path order. *Rejected: a hand-written list.* Revision 2's list already missed `expression_ir.py`, `syside_adapter.py` and nine other modules both halves import. A missed file gives a valid receipt for an ungated change, which is worse than no receipt. The cost is that more agentic-mbse edits need a gate run. That cost is real, because codegen uses those modules.
  - *When.* Required before any agentic-mbse merge that changes a covered file.
  - *The receipt.* A passing run writes `tests/fixtures/subset_profile/codegen_gate.json`. It holds:
    - `digest`: sha256 over the covered files' paths and bytes, taken from the tree exported at `--agentic-rev`, not the working tree, so uncommitted edits can never enter a receipt;
    - `codegen_rev`: the full codegen commit the run tested;
    - `agentic_rev`: the agentic-mbse commit exported;
    - `case_ids`: the packaged case IDs whose parametrized codegen tests passed.
    - no outcome field, because only a passing run writes the receipt. A failing run writes its report to `--out` and leaves the receipt alone.
  - *The receipt test* (`tests/test_subset_gate_receipt.py`, pure). It recomputes the digest over the working tree and fails when it differs. It also fails when a packaged case ID is missing from `case_ids`. Its failure message names the command to run (`uv run python scripts/subset_profile/codegen_suite.py run --agentic-rev HEAD --label gate --codegen-rev <rev> --out <dir>`; `run`, `--agentic-rev` and `--label` exist today, `codegen_suite.py:167-173`). So editing any covered file without rerunning the gate fails agentic-mbse's own suite. It lands in P7 (O18), see below.
  - *Tying the codegen revision to the merge (O20).* The receipt names the codegen commit it ran against. A `pre_pr` step for the coordinated merge checks that `codegen_rev` is the head of the codegen branch being merged, or an ancestor whose later commits touch nothing under `tests/conformance/subset_profile/`, `tests/expectations/subset_profile/` or `src/`. Without that step, a receipt from an older codegen commit would pass agentic-mbse's test. That limit is listed beside the forged-receipt one.
  - *Limits.* A forged receipt cannot be told apart from a real one. Recomputing only the digest by hand is not enough, because `case_ids` must also list every packaged case. But a deliberate forger who writes both still passes. The `pre_pr` check is procedural: it runs only when `pre_pr` runs.
  - *Why the test waits for P7 (O18).* During 2a, codegen's tests already run against the live agentic-mbse sibling tree through the editable path dependency, so a receipt would guard nothing. A receipt test landed in P1 would turn agentic-mbse red on every edit in P2–P6 and teach re-stamping as a reflex. P1 lands the gate script, because the baseline run uses it. P7 lands the receipt test and the first receipt, written by a gate run at the final revisions of both repositories. The receipt is regenerated on the result of each coordinated merge, so it applies from merge onward.
  - *What only this run catches.* An extractor or evaluator change is checked against the generator only by this run. agentic-mbse's own tests catch it only as a change from the stored screen answers, and editing those answers to match passes them. The run also guards L6 and guidance (Items 3 and 5, which read agentic-mbse directly) between an agentic-mbse change and its merge. Nothing guards them if the run is skipped and the receipt forged.
  - *Rejected: relying on "codegen CI" (none exists); a check in codegen alone (it runs only when someone runs codegen).*
- **D14. Cases that test the screen keep their models and screen answers as agentic-mbse package data; every other case lives in codegen. One copy of each model** (O2).
  - *Layout.* Screen-tested cases live at `src/agentic_mbse/sysml/subset_cases/<id>/{*.sysml, case.json}`. `case.json` holds a `schema` field (`subset-case/1`), since codegen reads its layout across repositories, then the construct, the stored screen answer, `agentic_site_witnesses` and provenance (the Item 1 probe ID). These are cases a record cites, or that test a shared rule's recognizer: near-neighbors, variations, controls and rule-candidate reproductions. Item 1's probe models move here; `observation*.json` and the generator-judging fields retire. Codegen-only cases (site witnesses with no rule, stub causes, naming collisions) live at `tests/fixtures/subset_profile/<id>/`, with their screen answer in the codegen expectation file.
  - *Checks.* agentic-mbse's `test_subset_profile_rules_{instantiation,modelwide}.py` are kept and repointed. They run the screen on every packaged case and compare with its `case.json`. A codegen pure test requires every case, in either home, to have exactly one stored generator answer, and no ID to exist in both homes. agentic-mbse's citation test (D4) requires every cited case to be packaged, which enforces the placement.
  - *Why (b) over (a).* Option (a), models in agentic-mbse's `tests/` read by codegen through the sibling path, breaks the [HARD] boundary that codegen reads agentic-mbse only through its package (spec Boundaries). Models in codegen read by agentic-mbse would make agentic-mbse's suite depend on its downstream checkout. Package data is the one place both can read. Two other options were weighed. Excluding `subset_cases/` from the wheel works only for editable installs, so codegen's tests would break silently on a wheel install. A separate test-data distribution adds a second package and version relation for about 100 KB. The hash-guarded copy stays unused.
  - *What wheel users get.* Inert minimal models, each with the screen's verdict. They are not run by any product command. That is acceptable: the files are small (the 80 probe models are 25 KB) and they document the contract, which Item 5's guidance may use. `extraction/check_corpus/` is not a precedent for this; it is runtime data for `extract --check`.
  - The packaged cases are not in the version digest, since adding a case changes no decision. They are covered by the gate receipt (D13).
- **D15. A generation-stage refusal carries a closed code, and the mapping never contains one** (O6). `CodeGenerationError` gains `code: GenerationCode`. That is a closed `StrEnum` of today's message prefixes (`DUPLICATE_OUTPUT_PATH`, `REGISTRY_CLASS_NAME_COLLISION`, `PREDICATE_COMPILE_FAILED`, …), set at each raise; message text is unchanged. The harness adds it to the case's codes. `REASON_MAPPING` holds only `ElaborationCode` and `ReadinessCode` values, by type, since no shared rule describes generation-stage output facts (ADR 0007; Item 1 D11). A refusal with no code at all is a harness failure, not a disagreement: every `CodeGenerationError` raise must pass a code (checked by the E1 scan), and unclassified failures already become `SI_INTERNAL_DEFECT`.

## Architecture

```
 agentic-mbse package                           sysml-codegen tests
 sysml/subset_cases/<id>/ model + case.json ──┐  tests/fixtures/subset_profile/<id>/ (codegen-only cases)
 subset_profile_rules.toml (cites case:<id>)  │           │
        │ loader: citation form only;         ▼           ▼
        │ test: case exists, shows pair  generator half (run_codegen, screen patched to raise)
        ▼                                 observe: log extra refusal / manual_stub, spied graph, model_contract.json
 agentic-mbse tests: screen on every            │ compare
 packaged case vs case.json                     ▼
                                 tests/expectations/subset_profile/cases/<id>.json  (generator answer, witnesses, loss)
                                                │
                       pure: agreement (mapping) ⇄ disagreements.json (hand-edited); citations; mapping witnessed
 codegen_suite.py (pre-merge, licensed) ── runs codegen's subset tests on an agentic-mbse revision → codegen_gate.json receipt
```

- **Live tests** read one model and run one half against one stored answer. They are license-gated and report by case ID.
- **Pure tests** read only stored answers, records and the mapping, so the agreement and citation guards hold without SysIDE.
- **Fixtures outside the corpus** (`tests/fixtures/*`) get a stored generator class, not a stored screen answer. The live fixture test runs the generator half to confirm the class, then the screen, and checks the screen against the class (B4, C2).
- **Mutations** reuse both halves and the agreement function.
- **Cross-repo flow.** codegen reads agentic-mbse's package only; agentic-mbse never reads codegen. A contract change lands in agentic-mbse, with the receipt, and the codegen pin moves in the same coordinated merge (ADR 0008).

## Cross-repo enforcement of ADR 0001 invariant 1

Today agentic-mbse alone enforces that a record outcome rests on retained evidence (`tests/test_subset_probe_evidence.py`). After 2a the evidence is a case, and enforcement is split:

| Check | Where it runs |
|---|---|
| Citation form | agentic-mbse loader |
| Cited case exists in the package, and its stored screen answer shows the pair | agentic-mbse test (`test_subset_case_citations.py`) |
| The screen reproduces every packaged case's stored answer | agentic-mbse tests |
| The case's stored generator answer exists, matches the generator live, and agrees with the screen answer | sysml-codegen tests |
| An agentic-mbse change was run through the codegen check | agentic-mbse receipt test (D13) |

`adr-0001-amendment.md`, written into this folder in P1 for the owner to file (RG-3), amends the Decision sentence and invariant 1:
- cases replace probes as evidence;
- a `case:<id>` citation resolves to the packaged case `agentic_mbse/sysml/subset_cases/<id>/` plus `sysml-codegen tests/expectations/subset_profile/cases/<id>.json`;
- generator backing is enforced in sysml-codegen;
- the pre-merge run and its receipt are required for changes to covered files (D13);
- invariant 6's "codegen CI" reads "the codegen parity test, run by the pre-merge gate".

It replaces the spec's staged text ("cases admissible alongside probes"), which is `[INFERRED]` and too weak once probes retire.

`p0001-amendment.md`, written beside it in P1 (O20), amends agentic-mbse `.project/product/0001-executable-subset-contract.md:3, :17`. That promise says a shape is "refused only when a retained probe of the pinned generator observed that refusal", which D4 makes false. The amended wording says a shape is refused only when a retained conformance case shows the generator refusing it, checked live in sysml-codegen and carried to agentic-mbse changes by the pre-merge gate. Filing both amendments is the owner's, at merge (RG-3).

## Design by criterion group

### A. Pins, mapping and occurrence parity

- **Pin.** `SUBSET_PROFILE_VERSION` joins `_upstream_pins.py` and its test.
- **Mapping** (`subset_profile_adapter.py`). `REASON_MAPPING: dict[reason, ReasonMapping]`. Each entry is `NO_REFUSAL`, or a default code plus optional per-context codes. Codes are `ElaborationCode | ReadinessCode`, compared by string value.
- **Mapping tests (pure).**
  - The keys equal `SUBSET_REASON_CODES`.
  - An entry is `NO_REFUSAL` exactly when no record refuses that reason's shape in any context.
  - Each record's `expected_code` is among its reason's codes.
  - Every (reason, code) pair has a case whose generator codes include the code and whose screen answer refuses a finding with that reason. This test needs P2's cases, so it lands in P2 (O19).
- **Renderer.** `render_finding(finding, rules) -> SubsetDiagnostic`, a frozen dataclass in the adapter: `code`, `subset_reason`, `remedy` (the record's text) and location. It is deliberately not a `Diagnostic`, so `Diagnostic.reason` keeps one meaning; how a `SubsetDiagnostic` joins a refusal is 2b's. Unit tests cover every reason. An import-boundary test pins that nothing on the generate route imports the adapter.
- **Occurrence parity** (D6). One licensed test over the seed, the 37 v6 corpus fixtures and every case whose summary has nodes. A missing input fails by name. P1 lands it over the seed and the corpus fixtures; P2 extends it to the cases as they arrive (O19). A companion test patches `_multiplicity_indices` (`elaboration/occurrence.py:812`) to drop one index and requires a difference.
- **ADR drafts** (RG-3). `adr-0012-amendment.md`, from the archived draft, with its "until Item 2 lands" invariant naming `tests/conformance/subset_profile/test_occurrence_parity.py` and the pre-merge run as what runs it. And `adr-0001-amendment.md` with `p0001-amendment.md` (§ Cross-repo enforcement).

### B. Shared rules against the generator's route

- **Tripwire (B1).** One licensed test patches `extract_subset_facts`, `evaluate_subset_profile` and `extract_occurrence_structure` wherever they are bound so they raise. It then runs every case's generator half and requires each stored outcome. 2b inherits it.
- **Corpus port.** Each Item 1 probe becomes a packaged case (D14) with its probe ID. New cases cover near-neighbor, inherited and redefined contexts, alternate spellings, template versus instance, and the dc3 `proto3`, `proto4nest` and `conv` shapes rebuilt from a pinned dc3 export.
- **Record coverage (pure).**
  - Every `refused` pair has a refusing case.
  - Every refused shape has a non-refused case, or an SA-1 statement. SA-1 is Item 1's `no_admitted_context` exception: a shape refused in every context the rule can compute, with a refusing case for each such context.
  - Every `omitted` or `excluded` pair cites a case that asserts at a seam (§ D), including the three site rules' `other_expression_site`.
- **Unconfirmed pairs.** Each R3 § 3 pair gets a case. An observed pair moves to its outcome. An unobservable pair stays `unconfirmed` and gains a record entry `unobservable = {context, reason, evidence = ["case:…"]}`, where the case shows what refuses first.
- **Retired shapes.** `part-multiplicity/nonunique` and `negative_bound` leave the records, the rule and `SUBSET_REASON_CODES`.
- **Fixture classification (B4).** Every directory under `tests/fixtures/` is a model root, inside a model root, or a container. Classes come from one place each: `batch.json` plus the oracle baseline for the 37 corpus fixtures, the stored answer for codegen-home cases, and `tests/expectations/subset_profile/fixture_classes.json` for the rest, including the occurrence seed. A pure test fails on an unclassed or doubly classed directory.
- **Mutations (B5).**
  - Generator: for each shared-rule site named in a witness list, in either tree, neutralize it (D5) and require the witness's reasons or stub causes to differ from its stored answer.
  - Screen: for each (rule, shape), disable its recognizer and require agreement with the stored generator answer to fail.
  - Both need the site's `SiteReason` in place, so the shared-rule sites get their reasons in this phase.

### C. Agreement and the R3 gaps

**The agreement rule** (spec C1 and C2). It is one rule for every subject, case or fixture. Let C be the generator's stored codes, elaboration and generation stage together (D15), and M the mapped codes of the screen's `refused` findings.
- Generator generated: agree when the screen has no `refused` finding. Otherwise `screen_refuses_generator_builds`.
- Generator refused: agree when at least one refused finding's mapped code is in C.
  - The screen has no refused finding (only `unconfirmed`, `unverified` or none): `generator_refuses_screen_silent`.
  - The screen refuses, but no mapped code is in C: `code_unmapped`.
- A generation-stage code is never in M, so a refusal with only generation-stage codes agrees only if an elaboration-stage code is also present. Otherwise it is a disagreement, usually `codegen_owned`.
- **Multi-construct fixtures (O7).** Extra refused findings beyond the one that matches are not disagreements. The generator stops at its first refusal, so findings it never reached cannot be judged against it. This is the spec's rule and no stricter.
- **Case isolation** is a separate check on whether a case is well formed, not on agreement. A case declares its construct lines. Every generator refusal location and every screen `refused` finding must fall inside them, so an unrelated refusal in a case shows up as a broken case.

**Other checks**
- **Fixtures (licensed).** The same rule, with the stored class as the generator answer and the live screen.
- **Record equality.** The computed disagreement set equals `disagreements.json` exactly (D3).
- **R3 rows.** Each closes per spec § R3 rows. Appendix C names cases and mechanism; `evidence/r3-closure.md` has one line per row.

### D. Silent losses and String metadata

| Family | Seam (case) | Control | Disposition |
|---|---|---|---|
| ES-010 String, both spellings | no instance-graph attribute node and no entry point for the String declaration | numeric value on the same feature: both present | accepted omission, RG-2 |
| CALC-USAGE-BARE-RESULT-DROP | the usage's `CalcNode` has no output for the bare result | named `return r` on the same usage: output present | candidate refusal, RG-1 |
| ES-007 NON_NUMERICAL | catalog `usage_records` disposition `excluded`/`non_numerical` | numeric constraint `eligible`/`admitted` | accepted exclusion |
| G1 | the part usage has one unindexed occurrence | explicit bounds: indexed occurrences | semantics question, RG-1 |
| G2 | occurrence count ignores the usage-level override | no override: the definition's bound | probed first, then as G1 |
| Calc def output stub, one case per cause | `MANUAL_REQUIRED` and a `ManualStubNotice` with that cause | the supported form compiles with no notice | candidate refusal per cause, RG-1 |

- **String fixtures.** Both spellings. A String on an uninstantiated template, on an instantiated part, bound to a calc input (the three ES-010 entry paths), and read by another attribute. `rg2-string-policy.md` gives the options, what each does to generated output and to native consumers, and a recommendation.
- **Docs.** `docs/architecture/modeling-assumptions.md` gains a section on today's behavior for String values, NON_NUMERICAL constraints, calc-usage bare results and stubbed calc def outputs, citing case IDs. It links POSITIONAL-FORMAL-REDEFINITION's hazard entry as pending until Item 4 supplies it.

### E. Per-site codes and the inventory

- **Scanner and account** (D7). `site_scan.py` reproduces Item 1's `scan_sites/1` forms. It reports every other `raise` under `src/sysml_codegen/` by name as `unrecognized`, so the inventory is total over `raise` statements. Remaining blind spots are listed in the account header: refusals returned as values, and raising helpers whose callers are not itemized.
- **Drift test (E1, pure).** Scan, then fail on a site with no row or a row with no site. It also fails on a `CodeGenerationError` raise with no `code` (D15).
- **Scanner mutations (E2, pure).** Synthetic source covers a new raise of each recognized form, a new exception class, a new raising helper and a computed code mapping. Each must be detected or reported as unrecognized by name.
- **Reasons and witnesses (E3).** Each `public_capability` row gets a `SiteReason`, per site or per justified family, and at least one witness. A pure test checks that the raise passes that reason, that every witness site ID resolves, and that every public row has a witness. The licensed mutation test neutralizes the site (D5).
- **Plain exceptions (O8).** A reachable plain-exception site becomes a coded refusal with a reason, outside RG-1, only if its witness shows it reaching `run_codegen` as a refusal today, meaning `SI_INTERNAL_DEFECT` with that exception in the cause chain. If a caller catches it and falls back, the way `CompilationError` becomes a stub, then a coded refusal would flip accept to refuse. That site is an RG-1 candidate: today's behavior is pinned and a recommendation goes in `rg1-recommendations.md`. Every changed code is listed in the evidence.
- **Unknown sites (E4).** Each of the 46 is classed reachable (then E3), internal invariant with a cited guard, or unknown with a recorded attempt, owner and limit.
- **Estimate and split point (O9).** Group E is 9–13 engineer-days of the item's 25–35:
  - **Foundation** (scanner port, account move, E1, E2, the `SiteReason`/`GenerationCode` mechanism): 2–3 days, in P1.
  - **Head** (reasons and witnesses for sites joined to a shared rule or an R3-routed row, and E4 for those): 3–4 days, in P2 and P5.
  - **Tail** (the other public sites: the 10 naming collisions, the codegen-only follow-ups, and the triage of the remaining unknown sites): 4–6 days, in P6.
  - The tail is defined by the account's `rule` and `matrix_row` columns. It is not defined by disagreement entries, because every codegen-only witness creates one.
  - *Split trigger (O19), counted from the account at P5's close.* The plan records two numbers: H, the head sites, and T, the tail sites (public rows plus unknown sites not joined to a rule or R3 row). At P5's close, count L, the head sites whose `SiteReason` and witness have landed. That means the E3 pure test passes for them. Take the split if either holds:
    - L < H: the head is not finished, so the tail would start late;
    - the tail's current count is more than 1.25 × T, because E4 triage in P5 moved unknown sites into the tail.
  - An agent evaluates both by running the E3 test and counting rows in `site_account.csv` by column. When the split is taken, the tail moves to a follow-on item and the orchestrator tells the owner.
- **Rescan (E5).** A recorded run of the codegen test and agentic-mbse's narrowed `scan_sites.py` at the final revisions, itemizing added and removed sites. It runs in P7, so taking the split does not drop it.

### F. Semantics questions and baseline evidence

- **G2** gets its reproducing case in group D.
- **`kerml-expert`.** One question per item: G1, G2, every `rg1_pending` disagreement, every candidate refusal and every O8 RG-1 candidate. Case models are attached. The answers, cited spec sections and agreement with the generator go in `evidence/semantics-checks.md`.
- **dc3.** `run_trees.py`, with an output parameter, evaluates dc3 `808464df` and `60b44d53` with contract v2. `evidence/dc3-rerun.md` itemizes each difference from Item 1's `acceptance.md`. The generator half runs on dc3 repaired at the final codegen revision.
- **Checks.** `pytest`, `mypy` and `ruff` in both repos, licensed, with skips and unrun checks named and compared with the P1 baseline. `evidence/repository-checks.md`.

## Independence limits

These are the places where the evidence is not independent of the screen. They are recorded, not hidden.
- **Shared decision tables** (spec Independence). `invocation-callable` reads `invocation_allowlist.py` and `constraint-predicate` reads `executable_profile.py`, on both sides. Their tables are not mutated. Their context and ownership logic is.
- **Shared agentic-mbse sites** (O12, S1). Mutating an agentic-mbse site that both halves run (`reference_use._require_supported_invocation`, the ES-006 and indexed-reference sites, the `executable_profile` sites) moves the generator and the screen together. Those mutations count as drift detection, meaning a change at the site is noticed. They are not evidence that the two sides agree independently. `mutate.py` tags them `shared`, and the evidence counts them apart. Which of the 22 `executable_profile` sites are table and which are context logic is a plan decision.

## Required Invariants

1. No stored answer is computed at test time. Each change to a stored answer, the disagreement record, the mapping or the account is a reviewed diff.
2. `disagreements.json` is written by hand only; no tool writes it (D3). A capture helper never writes a screen answer that fails agreement without a matching entry.
3. Every subject's stored screen answer agrees with its generator answer under the agreement rule, or the subject is in the disagreement record, and the record holds nothing else.
4. Every non-`unconfirmed` record pair cites at least one case or corpus fixture, resolved in both repos (§ Cross-repo enforcement). No record cites a probe.
5. The generator half never runs the screen; the tripwire fails if it does.
6. Each mutation names one site ID or one (rule, shape) recognizer. It passes only against the stored generator answer: reasons or stub causes for generator mutations, agreement for screen mutations.
7. Each model has one copy. Screen facts live in agentic-mbse's package, generator facts in sysml-codegen.
8. agentic-mbse imports nothing from sysml-codegen, and codegen reads agentic-mbse only through its package.
9. The 22 committed v6 snapshots stay byte-identical. 2a changes no snapshot format.
10. 2a changes no accept/refuse outcome. Changed refusal text, new warnings and changed codes for sites that crashed before are listed in the evidence.

## Component Overview

**sysml-codegen, production (`src/sysml_codegen/`)**
- `_upstream_pins.py`: adds `SUBSET_PROFILE_VERSION`.
- `subset_profile_adapter.py` (new): `REASON_MAPPING`, `SubsetDiagnostic`, `render_finding`, the import-time profile check. Off the generate route in 2a.
- `elaboration/diagnostics.py`: `SiteReason`. `core/errors.py`: `GenerationCode`, plus `code` and `reason` on `CodeGenerationError`. The carriers gain `reason`, `ExactTypeError` and `ExpressionInventoryError` included. `orchestration/elaborated_pipeline.py:289-455`: every converter copies `reason`; the renderers at `elaboration/elaborate.py:133, :194` append it. `snapshot/instance_graph.py:947`: the encoder refuses a reason-carrying `Diagnostic`, and its output is otherwise unchanged.
- `cli/__init__.py`: `extra={"refusal": …}` on each refusal log call.
- `extraction/expression_compiler.py`, `extraction/calc_compat_renderer.py`, `elaboration/elaborate.py`: `CompilationError` carries a `SiteReason`; `ManualStubNotice`.

**sysml-codegen, tests**
- `tests/helpers/subset_profile/`: `cases.py` (answer schema, loading, agreement, disagreement reader; pure), `observe.py` (both halves, seams), `mutate.py` (statement neutralizer, the 4 hand patches, screen recognizer patches, the patched-name table), `site_scan.py`, `occurrence_parity.py`.
- `tests/conformance/subset_profile/`: the test modules for groups A–E, including `test_site_reason_reaches_harness.py` (D8). `test_diagnostic_provenance_sites.py`'s scanner folds into `site_scan.py`.
- Data: `tests/fixtures/subset_profile/<id>/` (codegen-only cases), `tests/fixtures/subset_profile_occurrence_seed/<case>/`, and `tests/expectations/subset_profile/{cases/<id>.json, disagreements.json, fixture_classes.json, site_account.csv}`.

**agentic-mbse (coordinated merge).** Appendix B lists every file.

**This folder:** `rg1-recommendations.md`, `rg2-string-policy.md`, `adr-0012-amendment.md`, `adr-0001-amendment.md`, `p0001-amendment.md`, `evidence/`.

## Non-Goals

- Deciding RG-1, RG-2 or RG-3 questions, or fixing G1, G2 or any stub.
- Running the screen inside `generate`, a `check` command, the preparation path, or snapshot work, including carrying reasons or stub causes into snapshots (2b).
- Adding CI to either repository. The pre-merge run is the procedure 2a relies on.
- A general detector for unknown silent losses (recorded limit).
- Promoting the capability matrix into agentic-mbse's package (Item 3 can decide).
- Re-verifying Item 1's 154 internal-invariant guards, except where 2a changes the code or finds one broken.

## Implementation Notes

- **Baseline first.** S1 saw 10 failures in the licensed suite before any 2a change. One is `test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees`, on agentic-mbse's `project_templates/MODELING_PROCESS.md.template`. The other nine are in `tests/unit/test_check_ledger_4a.py`, which diffs commits this worktree lacks. P1 records the full baseline (pass, fail and skip by test ID) in both repos. It also runs the same suite at codegen `b5663c07` with agentic-mbse `ccd57d83` in an isolated tree (`codegen_suite.py`), to establish which failures were there before 2a. The P7 checks compare against that baseline, so 2a is neither blamed for those failures nor quietly absorbs them.
- **Known limits of the mutator (O13).** The implementation either handles each of these or lists the affected sites by name:
  - functions behind `functools.lru_cache` or other caching wrappers: swapping `__code__` does not clear cached results, so the helper refuses such a site unless the cache is cleared;
  - zero-argument `super()` (`__class__` cell): handled by the helper but never exercised, so the first such site gets its own test;
  - cases that share a site: S1 checked "only the witness flipped" on 11–12 mostly unrelated cases, so the suite records other flips rather than requiring there are none;
  - thread safety: `__code__` swaps are process-wide, which is safe under pytest-xdist processes but not under threads;
  - decorator stripping shifts traceback line numbers inside an elided function.
- The live path rewrites source paths to `root-N/…` referents (`orchestration/elaborated_pipeline.py:458`). The construct-location check normalizes both sides.
- `SI_EXPRESSION_SOURCE_UNSUPPORTED` and `SI_INDEXED_SOURCE_UNSUPPORTED` exist in both `ElaborationCode` and `ReadinessCode`; compare by string value.
- `SUBSET_PROFILE_VERSION` moves to `v2` at the first record change on the branch and stays `v2` until merge. The digest test updates with each change.

## Potential Risks

| Risk | Mitigation |
|---|---|
| The pre-merge run is skipped after 2a merges | The receipt test fails agentic-mbse's own suite; only a forged receipt (digest and `case_ids` both) passes |
| The receipt names an older codegen commit than the one merging | The `pre_pr` revision check (D13); procedural, listed as a limit |
| A red receipt test is "fixed" by re-stamping without a run | The test lands only in P7, so it is not red through 2a; it requires `case_ids`, which a hash-only re-stamp cannot supply |
| Shared-site mutations are mistaken for independent evidence | Tagged `shared` and counted apart (§ Independence limits) |
| Two shadowing sites cannot be given distinct reasons (B6) | Recorder observable for that pair, listed by name |
| Merge order with the concurrent Item 4 session (O20). Item 4 runs in `/home/reid/src/agentic-mbse` and may change covered files under `sysml/` | If Item 4 merges first, 2a rebases onto it, and 2a's final gate run on the merged tree covers its changes. If 2a merges first, Item 4's later edits hit the receipt test and need their own gate run. Either way the receipt is regenerated on the result of each coordinated merge. Keep agentic-mbse edits in few commits and rebase at each phase gate |
| Shipping case models in the agentic-mbse wheel grows it | About 25 KB of models plus `case.json` files; wheel users get inert examples (D14) |
| A new rule (D11) needs facts with no heuristic-free extraction | The row becomes a reproduced gap; the criterion decides |
| Added reasons change stored refusal text (`public_package_oracle/baseline.json`) | Listed in the evidence and updated as reviewed changes |

## Integration Strategy

- 2a merges as one coordinated pair of PRs (RG-3, ADR 0008). The agentic-mbse PR carries contract `v2`, the packaged cases, the receipt and the retired tests. The sysml-codegen PR carries the corpus answers, the adapter, reasons and the moved data. The agentic-mbse receipt names the codegen revision it ran against.
- 2b imports the adapter and `SubsetDiagnostic`, inherits the tripwire, and starts its snapshot work knowing that reasons and stub causes are live-only.
- Item 3 reads `disagreements.json` to say what CLEAR does not cover, and Items 3 and 4 run the pre-merge gate when they touch covered files. Item 5 renders from the v2 records.

## Validation Approach

- **Pure, codegen:** answer schema, agreement, record equality, the disagreement writer guard, citation resolution, mapping, candidate marks, fixture classification, account drift, scanner mutations, renderer, empty diagnostics in the committed snapshots.
- **Pure, agentic-mbse:** loader (citation form), citation test (cited cases exist and show the pair), the receipt digest and `case_ids` (from P7), agentic-mbse account witnesses.
- **Licensed, codegen:** both halves for every case, the reason-reach test, tripwire, fixture classes and screen, occurrence parity with its mutation, generator and screen mutations.
- **Licensed, agentic-mbse:** the screen on every packaged case.
- **Recorded runs:** baseline (P1), gate receipts, E5 rescan, dc3 re-run, `kerml-expert` checks, repository checks against the baseline. The evidence names licensed runs and skips.
- Each phase's `/_my_audit` reviews diffs to stored answers, the record and the mapping, as the named reviewer.

## Next-Stage Handoff

**Fixed:** D1–D15; the fact-placement rule; the agreement rule; the split-point definition and its counted trigger (the plan supplies H and T).

**Open for the plan:**
- the final case list and IDs, and which cases are packaged and which are codegen-only;
- the `SiteReason` and `GenerationCode` members;
- which rows become rules (D11);
- the exact seam for CALC-USAGE-BARE-RESULT-DROP;
- which `executable_profile` sites count as shared table.

**Ordering constraint (S1).** A site's mutation test can pass only once the site has its `SiteReason`. So the reason mechanism lands in P1, shared-rule sites get their reasons in P2 before their mutations, and R3-row sites get theirs in P5.

| Phase | Content | Depends on |
|---|---|---|
| P1 | Baseline in both repos. Group A, except the mapping-witness test and occurrence parity over cases. Harness. `SiteReason`/`GenerationCode` mechanism, the converter copies, the reason-reach test and the snapshot guard. Scanner port, account move, E1, E2. Gate script (no receipt test yet) and the probe-helper move. ADR 0001, P-0001 and ADR 0012 amendment drafts | — |
| P2 | Group B: packaged cases, records → `case:`, citation test, `v2`, reasons and mutations for shared-rule sites. The mapping-witness test, and occurrence parity extended to cases | P1 |
| P3 | Group C | P2 |
| P4 | Group D, RG-2 recommendation, docs | P2 |
| P5 | Group E head: R3-row site reasons and witnesses, E4 for those | P2 |
| — | **Split point** at P5's close (§ E trigger) | P5 |
| P6 | Group E tail | P5 |
| P7 | Group F; E5 rescan; the receipt test and the first receipt, from a gate run at both final revisions; final repository checks against the baseline | P3–P5, and P6 unless split |

**Decision records to file once the design is approved** (none filed yet):
- the fact-placement rule with packaged screen cases, and the split enforcement of invariant 1 (cross-repo; a future agent would plausibly re-add copies or re-centralize checks). It is filed in both registers as each binds; the agentic-mbse half is the staged ADR 0001 amendment.
- the pre-merge gate and receipt, as part of that amendment;
- agentic-mbse P-0001, the staged `p0001-amendment.md` (product promise: refusal backed by a retained conformance case, not a probe);
- D12, as an amendment of ADR 0016.

Filing all of them is the owner's, at merge (RG-3).

---

Next Step: the orchestrator verifies R2-M1 to R2-M4 against this revision, then `/_my_plan`.

## Appendix A — Stored answer schema

The codegen stored generator answer (`tests/expectations/subset_profile/cases/<id>.json`), as pseudo-JSON:

```
{ "id": "binding-source__expression_source__owner_instantiated", "home": "agentic|codegen",
  "generator": {"outcome": "refused", "codes": ["SI_EXPRESSION_SOURCE_UNSUPPORTED"],
                "reasons": ["<SiteReason>"], "witnesses": ["<codegen site ID>"]?,
                "stubs": [{"output": "<qn>", "reason": "<SiteReason>"}]?,
                "seams": [{"kind": "graph_attr|entry_point|catalog_usage|calc_compilability|occurrences",
                           "declaration": "<qn>", "expect": ...}]?},
  "screen": {...}?,                       # only for codegen-home cases
  "loss": {"family": "...", "disposition": "accepted_omission|candidate_refusal", "rg1": "RG1-3"?}? }
```

The packaged `case.json` holds `construct: {file, lines}`, `screen: {verdict, findings: [{rule, shape, context, outcome, subject}]}`, `agentic_site_witnesses` and `provenance: {from_probe?, note}`.
- `findings` is the complete set the screen reports, so an unrelated rule change also shows as drift.
- `codes` is the sorted multiset of elaboration and generation codes.
- `fixture_classes.json` maps a path under `tests/fixtures/` to `{class: generating|refusing|container|not_a_model, codes?, note}`.

## Appendix B — agentic-mbse files the coordinated merge touches

| File | Change |
|---|---|
| `src/agentic_mbse/sysml/subset_profile.py` | `case:` evidence checked by form only (the loader stays pure over text), `candidate_refusal`, `unobservable`, retired shapes removed, D11 rules, `v2` |
| `src/agentic_mbse/sysml/subset_profile_rules.toml` | citations → `case:`, 2a outcomes, `verified_against` |
| `src/agentic_mbse/sysml/subset_extraction.py` | facts for any D11 rule |
| `src/agentic_mbse/sysml/subset_cases/` (new) | the packaged cases, moved from `tests/fixtures/subset_profile/probes/` and added to |
| `tests/fixtures/subset_profile/probes/` | removed (moved into the package; `observation*.json` retire) |
| `tests/fixtures/subset_profile/occurrence/` | removed (moved to codegen, D6) |
| `tests/fixtures/subset_profile/inventory/site_account.csv` | the 441 codegen rows leave; adds `witness` checks for its 61 rows |
| `tests/fixtures/subset_profile/inventory/matrix.toml` | codegen `sites` lists removed; probe references → cases |
| `tests/fixtures/subset_profile/inventory/scanner.toml` | agentic-mbse tree only |
| `tests/fixtures/subset_profile/codegen_gate.json` (new) | gate receipt |
| `tests/fixtures/subset_profile/cases/` | kept (evaluator mechanics) |
| `tests/test_sysml/test_subset_profile_rules_instantiation.py`, `…_modelwide.py` | kept, repointed to packaged cases and `case.json` |
| `tests/test_sysml/test_subset_profile_records.py` | updated: `case:`, `unobservable`, `candidate_refusal`, SA-1 wording |
| `tests/test_sysml/test_subset_profile_vocabulary.py`, `…_version.py` | updated for retired shapes and `v2` |
| `tests/test_sysml/test_occurrence_parity.py` | removed (D6) |
| `tests/test_subset_probe_evidence.py`, `tests/test_subset_probe_judge.py` | removed; replaced by the citation test and the kept rule tests |
| `tests/test_subset_case_citations.py` (new, P2) | each cited case exists in the package and its `case.json` shows the pair (D4) |
| `tests/test_subset_matrix.py`, `tests/test_subset_site_account.py` | updated for D7 |
| `tests/test_subset_gate_receipt.py` (new, P7) | the receipt digest and `case_ids` test (D13) |
| `tests/helpers/subset_probe_judge.py`, `occurrence_oracle_schema.py` | removed |
| `tests/helpers/subset_matrix.py`, `subset_site_account.py` | updated for D7 |
| `tests/helpers/subset_records.py` | updated: synthetic citations `probe:<pair>` → `case:<pair>`, which load by form with no packaged case (`:85`, `:101`) |
| `tests/helpers/subset_synthetic.py`; other `test_sysml` subset, occurrence, invocation and conditional tests | unchanged |
| `scripts/subset_profile/codegen_suite.py` | kept; `--codegen-rev`, `--out`, `--select`, glob-covered digest from the exported tree, receipt writing |
| `scripts/subset_profile/isolated_tree.py` (new) | the helpers `codegen_suite.py` imports, moved from `probe.py` |
| `scripts/subset_profile/probe.py`, `occurrence_oracle.py`, `occurrence_parity.py`, `occurrence_port_run.py` | removed |
| `scripts/subset_profile/run_trees.py`, `render_matrix.py`, `validate_diff.py` | output path becomes a parameter |
| `scripts/subset_profile/scan_sites.py` | agentic-mbse tree only; output path a parameter |
| `scripts/subset_profile/README.md` | rewritten for the kept scripts and the gate |

## Appendix C — R3 rows to mechanism

| Row | Cases | Closes through |
|---|---|---|
| ES-002 | the binding, the admitted neighbor (binding a calc output), the other shapes reaching `occurrence.py:180` | D11; gap → `reproduced_gap` and a `SiteReason` distinct from ES-009's |
| ES-008 | all five spellings, plain nesting as control | D11 |
| ES-009 | the shape and the other shapes reaching `elaborate.py:2345` | D11 |
| ES-010 refusal side | one case per projection entry path | `reproduced_gap`, `codegen_owned`; RG-2 |
| ES-011 | arithmetic on `return r` and on `out attribute r` | reproduced gap, or retired with admitting cases |
| CALC-DEF-BARE-RESULT | arithmetic, `max`, conditional bare results | D11 |
| CALC-USAGE-BARE-RESULT-DROP | § D family | every bare result `omitted` + `candidate_refusal` if the criterion holds, else a codegen backlog item, owner Reid Westwood |
| DEEP-QUALIFIED-WIRING | a minimal case plus fixture `deep_cross_scope_probe` | `codegen_owned` disagreement |
| G1, G2 | § D | pinned behavior plus `kerml-expert` (F) |
| `unconfirmed` pairs | one per pair | observed outcome, or `unobservable` with the shadowing case |
| Retired shapes | none | removed (B) |
| 85 follow-up sites | witnesses | group E (head or tail by account columns) |
| PUSH-DOWN chain-segment, sum-shape sites | one case per reachable site | E4; row to Item 3 with verdicts |
| PUSH-DOWN unsupported operator | stub family cases | § D; row to Item 3 |
| PUSH-DOWN literal shape | `sum(5.0)` | gap or admitted case; row to Item 3 |
| PUSH-DOWN redef precedence, ambiguous inherited attr | pinned cases | a written statement in `modeling-assumptions.md` of which value wins and which typing is chosen |
