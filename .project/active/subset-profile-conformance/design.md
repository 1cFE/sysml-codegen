# Design: Independent conformance corpus and per-site codes (EXEC-SUBSET-CONTRACT Item 2a)

**Status:** Draft (2026-10-18). Not reviewed. Next: `/_my_design_review` in a fresh session.
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Branch / base:** sysml-codegen `subset-conformance` at `99d46685` (spec base `b5663c07`); agentic-mbse sibling `subset-conformance`, base `ccd57d83` (Item 1 merge)

## Overview

2a builds a corpus of small SysML models in sysml-codegen, each with a stored answer for what the generator does and what the shared contract (the screen) says. Tests run both halves, check that the stored answers agree, and make any drift between the generator, the contract and the stored answers fail a codegen test.

## Related Artifacts

- Spec: [spec.md](spec.md); review with resolutions: [spec-review.md](spec-review.md); product-lens ledger: [product-lens.md](product-lens.md); owner gates RG-1..3: [briefs/align.md](briefs/align.md)
- Epic: agentic-mbse `.project/backlog/epic_executable-subset-contract.md`, Item 2a. The epic lists no Required Reading for 2a.
- Item 1 archive (agentic-mbse `.project/completed/20261018_exec-subset-profile/`): `design.md` (data model, D3 evidence gate, D11, probe harness), `evidence/r3-proposal.md`, `evidence/site-reconciliation.md`, `evidence/acceptance.md`, `evidence/r2-mutations.md`, `evidence/adr-0012-amendment-draft.md`
- Decision records: sysml-codegen `.project/adr/0004-derive-occurrences-from-exact-evidence-or-refuse.md`, `0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md`, `0008-cross-repo-merges-use-merge-commits.md`, `0012-exclusive-semantic-evidence-ownership.md`, `0016-installer-reuse-through-an-api-version-pin.md`; agentic-mbse `.project/adr/0001-subset-profile-capability-ownership.md`; product `.project/product/0003-no-workarounds-for-bad-models.md`

## The Point

**[INFERRED]** (ratified by owner, 2026-10-18, spec brief and `briefs/align.md`) Prove, with evidence independent of the screen, that the shared contract matches what this generator actually does, and make drift between them fail a test in sysml-codegen. Test volume is not the goal, and neither are tests that check the screen against itself.

Why it matters: Item 1 wrote down which SysML shapes the generator executes, as rule records in agentic-mbse, and checked them once against 80 probe runs of codegen `b5663c07`. Nothing fails today when the generator changes. A relaxed or added refusal would leave the contract stale with every test green. Later items (2b `check`, 3 L6, 5 guidance) will tell modelers what will generate on the strength of this contract, so it has to be held to the generator mechanically.

Two owner constraints bound the work. **[NEED]** (owner, `briefs/align.md`) Any change to what the generator accepts or refuses is RG-1, String policy is RG-2, and merges and ADR filing are RG-3. **[NEED]** (P-0003, owner-verbatim: "we do NOT create workarounds to accept bad models -- we follow what KerML, SysMLv2 and SysIDE support") Recommendations follow the language, not convenience.

## Research Findings

Verified at sysml-codegen `99d46685` and agentic-mbse `ccd57d83` working trees. Paths are relative to each repo's `src/` package unless stated.

**The generator route**
- `run_codegen` (`sysml_codegen/cli/__init__.py:1144`) is the one entry point. It returns `bool` and never raises. Every refusal is caught and logged at ERROR as text (`:1189-1230`), so a caller sees typed exceptions only by reaching inside.
- There is a precedent for structured log data: the name-safety refusal passes `extra={"constraint_name_safety": ...}` (`cli/__init__.py:1208`), and `tests/unit/test_cli_generation.py:348` reads it back as `records[0].constraint_name_safety`.
- Live construction is `build_exact_pipeline_context([path])` (`orchestration/exact_pipeline_context.py:273`), which calls `elaborate_model_paths` then `_seal`. `run_codegen` imports the builder inside its body, so patching the module attribute reaches it. `ExactPipelineContext` exposes the computation graph but not the instance graph (`:143-212`).
- Refusal carriers: `ElaborationError.findings` of `ReadinessFinding` (`extraction/source_evidence.py:40`, codes `ReadinessCode` at `:26`); `ElaborationDiagnosticError.diagnostics` of `Diagnostic` (`elaboration/graph.py:74`, code `ElaborationCode | ReadinessCode`); `CodeGenerationError` (`core/errors.py:33`), whose "code" is only a message prefix such as `REGISTRY_CLASS_NAME_COLLISION:`. No carrier has a reason or sub-code field.
- `scripts/capture_v6_batch.py:110` `_refusal_record` already turns a refusal into a sorted code multiset. That is the comparison shape to reuse.

**Seams for omissions and losses**
- The generated `model_contract.json` embeds the constraint catalog. Its `usage_records` give each authored constraint usage a closed `disposition_kind` / `disposition_reason` (`resolution/models.py:303`, vocabulary `elaboration/graph.py:262`), for example `excluded` / `non_numerical`. This is the seam for ES-007.
- A calc def output that the renderer cannot compile becomes `MANUAL_REQUIRED` (`extraction/expression_compiler.py:291`). The per-output cause is free text in `ExactCompilationResult.unsupported_reason` and is dropped at `elaboration/elaborate.py:1266`. Only the overall `CalcNode.compilability` survives into the instance graph. The contract does not record compilability (`contracts/models.py:51-77`).
- The stub causes are the `raise CompilationError` lines in `extraction/calc_compat_renderer.py:62, :76, :78, :96, :103, :109, :115, :117, :120`, plus `expression_compiler.py:246` (cycle) and `:271` (no AST).

**Existing test idioms**
- Per-fixture expectations are JSON under `tests/expectations/<topic>/<fixture>.json`, with "missing file fails, stranded file fails" (`tests/conformance/test_constraint_population_oracle.py:89`). There is no TOML expectation store.
- `tests/fixtures/v6_recapture_batch/batch.json` records the elaboration outcome of the 37 corpus fixtures (14 graph, 23 refused with codes). `tests/expectations/public_package_oracle/baseline.json` records that 3 of the 14 refuse at generation.
- License gating is `tests/conftest.py:37` `requires_license`. `tests/conformance/README.md` bans `f(x) == f(x)` oracles and asks for selection by identity.
- No test today disables a detector and checks that an outcome flips. Item 1's mutations ran as a script on scratch copies (`evidence/r2-mutations.md`), not in the suite.
- The only raise-site scanner in codegen is narrow: four codes in three files (`tests/conformance/test_diagnostic_provenance_sites.py:44-95`).
- There is no index classifying the 155 directories under `tests/fixtures/`.

**The contract side (agentic-mbse)**
- `extract_subset_facts(model, extra_roots=())` takes a loaded SysIDE model (`sysml/subset_extraction.py:466`). `evaluate_subset_profile(facts, rules, roots)` is pure (`sysml/subset_profile.py:1285`). Neither is exported from `agentic_mbse.sysml`; import by submodule.
- 16 reason codes (`subset_profile.py:124-143`), 8 rules, 37 record pairs (24 refused, 8 admitted, 1 excluded, 4 omitted) citing 62 probes. `Qualification` has `none` and `manual_stub` (`:235`).
- The loader accepts two citation forms only: `probe:<rule>__<shape>__<context>[__…]` and `corpus:<snapshot fixture>` (`:396-409`). It checks form; `tests/test_subset_probe_evidence.py` checks that probes exist and certify.
- The occurrence parity seed (34 cases) and the normalizer live in agentic-mbse's `tests/` tree, with `expected.json` files captured from codegen `b5663c07` (`tests/helpers/occurrence_oracle_schema.py`). The site account (`tests/fixtures/subset_profile/inventory/site_account.csv`) holds 441 codegen rows and 61 agentic-mbse rows, keyed `file::Outer.inner::channel::code::ordinal`.
- `scripts/subset_profile/{probe,occurrence_parity,run_trees,render_matrix}.py` hardcode the archived evidence folder as output. `scan_sites.py` hardcodes `~/src/sysml-codegen` as the codegen tree.

**Versioning (answers the spec's open question)**
- agentic-mbse reports 0.1.3 before and after Item 1; the subset modules did not bump it. 0.1.3 wheels without the contract exist on disk and were installed in earlier evidence (agentic-mbse `.project/completed/20261012_research-seam-port/evidence/dry-run/README.md`).
- The v6 snapshot envelope refuses a different `agentic_mbse.__version__` (`snapshot/envelope.py:459-461`). A version bump therefore invalidates codegen's 22 committed snapshots. ADR 0016 already chose an API version pin over a package-version bound for exactly this reason.
- Not checked: agentic-mbse git tags and any package index. Git commands into the sibling repo needed approval this session.

## Core Concept

**The corpus is a set of small models, each carrying two stored answers that must agree.**

1. A **conformance case** is a directory with one model (usually one construct plus a control sibling) and one JSON expectation. The expectation holds the generator's answer (generated, or refused with these codes) and the screen's answer (these findings, this verdict).
2. **Live tests hold each stored answer to its source.** The generator half runs `run_codegen` on the case with the screen patched to raise, and compares what happened with the stored generator answer. The screen half runs `extract_subset_facts` and `evaluate_subset_profile` and compares with the stored screen answer.
3. **A pure test holds the two stored answers to each other.** Using codegen's reason-to-code mapping, the stored screen answer must agree with the stored generator answer, or the case must be in the disagreement record. This is what stops the screen checking itself: its stored answer is constrained by the generator's, not free to be re-captured.
4. **Everything else checks against the corpus.** The rule records cite cases, and a codegen test resolves each citation. The mapping must be witnessed by cases. Mutations disable one detector and require its cases to fail.

The guiding rule for where each fact lives: **a fact lives in the repository that can check it live.** Generator facts (case models and answers, the codegen half of the site account, the occurrence seed) move to sysml-codegen, because only codegen can run the generator. Contract facts (records, reasons, rules, version) stay in agentic-mbse's package, which codegen already depends on. agentic-mbse keeps only the tests that need no generator. Nothing is copied, so there is nothing to keep in sync by hand.

What this composes with: `run_codegen` and its structured-log idiom (observation), `batch.json` and the oracle baseline (corpus fixture classes), the `tests/expectations/` idiom (storage), Item 1's site-ID scheme (inventory and mutation targets), and Item 1's record loader (citations).

## Key Bets

- **B1. A single-construct case pins one (rule, shape, context) pair for the generator.** The generator fails fast and reports one error class, so a model with one construct and a passing control isolates it. Item 1's 80 probes rest on the same bet and held. *If false → a case witnesses the wrong pair; the construct-location check (the refusal's line falls in the construct's lines) catches most of it.*
- **B2. Eliding one `raise` statement disables exactly its detector, and codegen's code shapes allow doing that in-process.** Sites sit in module functions, methods of `_ExactElaborator`, and nested functions; some modules are imported by name elsewhere. *If false → mutations need a hand-written patch per site, about 110 of them, which roughly doubles group B and E mutation cost.* Unverified; spike S1 below tests it first.
- **B3. The whole corpus runs in-process in a time the default licensed suite can carry.** Rough count: about 200 cases, 150 classified fixtures and 120 mutation runs. Item 1's parity run took about 70 s for 73 models. *If false → the suite gets slow enough that people skip it, and drift detection weakens.* Unverified; spike S1 measures it.
- **B4. Codegen can read the occurrence summary and the records through agentic-mbse's package alone.** The summary function and record loader are package code; only the seed and normalizer sit in agentic-mbse's `tests/`. *If false → the [HARD] boundary (codegen reads agentic-mbse only through its package) forces copies.* Verified by reading the modules; the plan confirms at the first import.
- **B5. The generator's outcome is constant within each context label** (Item 1 B5, carried). *If false → a context hides an admitted sub-case. Variation cases split it, as in Item 1.*

## Key Decisions

Each deferred question from the spec is answered here. The table maps question to decision.

| Spec "Deferred to design" question | Decision |
|---|---|
| How expectations are stored | D1 |
| How detectors are disabled | D5 |
| Form of the disagreement record | D3 |
| `run_codegen` or stage calls | D2 |
| Seam per silent-loss family; how a stub is observed | D9 |
| Where the parity seed and normalizer live | D6 |
| Whether the codegen half of `site_account.csv` moves | D7 |
| How the stable site reason is spelled, carried, rendered | D8 |
| How agentic-mbse records cite cases | D4 |
| How a record marks a candidate refusal | D10 |
| Rule or reproduced gap for ES-002/008/009/CALC-DEF-BARE-RESULT | D11 (procedure; the cases decide) |
| Version bump and publish | D12 (and a surfaced conflict) |

- **D1. One directory per case, one JSON expectation per case, following the `tests/expectations` idiom.** Models at `tests/fixtures/subset_profile/<case_id>/`, expectations at `tests/expectations/subset_profile/cases/<case_id>.json`. A missing or stranded expectation fails. Case IDs keep Item 1's form `<rule>__<shape>__<context>[__<variant>]` for rule cases, and `<row-or-family>__<variant>` otherwise (Appendix A). *Rejected: one big table (a per-case diff is what the phase audit reviews, and the model sits next to nothing in a table); TOML (codegen has no TOML expectation store; JSON is the idiom, and a `provenance` field replaces comments).*
- **D2. The generator half calls `run_codegen` and observes through structured log data.** `run_codegen` gains `extra={"refusal": error}` on each refusal log call, the same idiom as `constraint_name_safety`. The harness reads the typed exception from the log record. For seams it also spies on `elaborate_model_paths` as `build_exact_pipeline_context` calls it, keeping the instance graph it returns, and reads `model_contract.json` from the output directory. Nothing is reimplemented; the spy only records. *Rejected: calling stage functions in order (it skips `run_codegen`'s error mapping and preflight order, which is part of what users run); parsing ERROR text (codes also appear inside detail text).*
- **D3. The disagreement record is one JSON file, and a test requires it to equal the computed set exactly.** `tests/expectations/subset_profile/disagreements.json`. Each entry has the subject (`case:<id>` or `fixture:<path>`), a closed kind (`generator_refuses_screen_silent`, `screen_refuses_generator_builds`, `code_unmapped`), the generator codes, the screen's refused reasons, a resolution (`codegen_owned`, `reproduced_gap`, `rg1_pending`, `rg2_pending`), the R3 row if any, an owner and a one-line reason. Equality on (subject, kind, codes, reasons) makes a disagreement that appears or disappears fail (criterion C3). *Rejected: a flag inside each case (fixtures have no case file, and one file is what Item 3 reads to learn what CLEAR does not cover).*
- **D4. Records cite cases as `case:<id>`; agentic-mbse checks the form, codegen resolves the citation.** agentic-mbse's loader accepts `case:` for every outcome and requires the ID to start with the pair it backs (the same prefix rule probes have, so a mis-citation fails at load). A codegen test loads the packaged records and, for each citation, requires the case to exist, its stored screen answer to contain that (rule, shape, context, outcome), and its generator half to pass. It also requires every non-`unconfirmed` pair to cite at least one case or `corpus:` fixture, and checks `corpus:` citations the same way. `probe:` citations are removed. The ADR 0001 invariant 1 amendment (staged, RG-3) makes this admissible. *Rejected: keeping probe citations beside cases (two live authorities, which ADR 0001 invariant 5 rules out); a codegen-generated citation file that agentic-mbse reads (reverse dependency).*
- **D5. A generator mutation elides one `raise` statement, chosen by its site ID.** A test helper recompiles the function or method that contains the site with that one `raise` replaced by `pass`, and patches it in place, including every module that imported the same function object by name. Site IDs are the scanner's (`file::Outer.inner::channel::code::ordinal`), so each mutation names exactly one detector. A screen mutation patches the recognizer inside one rule (the fact classification or shape test that produces the finding), never the finished findings, since filtering output would prove only what a pure check already proves. For `invocation-callable` and `constraint-predicate` the shared tables are not mutated; their context and ownership logic is (spec Independence). All run in the default licensed suite. *Rejected: hand-written patches per site (about 110 bespoke patches that drift from the source); source-copy mutation in scratch trees (Item 1's method; it cannot run in the suite).* Spike S1 confirms B2; the fallback is a hand-written patch for any site the helper cannot reach, listed by name.
- **D6. The occurrence seed and normalizer move to sysml-codegen; the stored oracle captures retire.** The 34 seed models go to `tests/fixtures/subset_profile_occurrence_seed/<case>/`. One normalizer, `tests/helpers/subset_profile/occurrence_parity.py`, maps both agentic-mbse's `OccurrenceStructure` and codegen's `OccurrenceIndex` (plus multiplicity aborts) to one schema, ported from `occurrence_oracle_schema.py` and the oracle script. The parity test compares them live. agentic-mbse's `test_occurrence_parity.py`, its seed and its `expected.json` captures retire in the coordinated merge, which is the amendment's own end state ("the CI parity test is the gate"). *Rejected: promoting the seed into agentic-mbse's package data (ships test models in a wheel, and the comparison still needs codegen); copying with a content hash (two copies).*
- **D7. The codegen half of the site account moves to sysml-codegen; agentic-mbse keeps its own 61 rows. No frozen copy.** The account goes to `tests/expectations/subset_profile/site_account.csv`, same columns plus `reason`. Which cases witness a site is recorded once, on the case (`generator.witnesses`, a list of site IDs), and derived for the account. That also covers agentic-mbse sites (ES-005, ES-006, indexed reference), whose rows codegen cannot read: `site_scan.py` resolves their IDs by scanning the installed agentic-mbse package source. agentic-mbse's matrix drops its codegen `sites` lists, so the codegen-site-to-row link lives once, in the account's `matrix_row` column. codegen checks `rule` against packaged rule IDs and `matrix_row` by form. The scanner's codegen half is ported into `tests/helpers/subset_profile/site_scan.py`; agentic-mbse's `scan_sites.py` narrows to its own tree. *Rejected: the frozen copy the spec mentions (it is a second copy that drifts silently, the smell the product-lens named).* Limit: a codegen row naming a nonexistent tracked-gap row ID is not caught, because the matrix sits in agentic-mbse's `tests/`.
- **D8. A stable site reason is a member of one closed codegen enum, `SiteReason`, carried as an optional `reason` and rendered as a suffix.** `SiteReason` lives beside `ElaborationCode` in `elaboration/diagnostics.py`. `Diagnostic`, `ReadinessFinding`, `ElaborationInvariantError` and `CodeGenerationError` gain `reason: SiteReason | None`; the boundary conversion copies it. A relayed `SemanticEvidenceError` (agentic-mbse sites) gets its reason from a total table keyed by `SemanticEvidenceCode`. Rendered messages end in ` (reason: <id>)`, so users and 2b see it. Values are snake_case and disjoint from `SUBSET_REASON_CODES` (tested). *Rejected: per-site `ElaborationCode` members (spec Non-Goal); carrying without rendering (the stable reason is for users and later items, not only for tests).*
- **D9. Each silent-loss family is asserted at one named seam, and a stub announces its cause.** Seams: an instance-graph node by declaration identity, a computation-graph entry point by source declaration, a `model_contract.json` catalog record by usage declaration, and `CalcNode.compilability`. Declarations are found by qualified name in the loaded model, then compared by `DeclarationId`, never by searching output text. A stub is observed as `CalcNode.compilability == MANUAL_REQUIRED` plus a new non-refusing notice: `CompilationError` carries a `SiteReason`, and live elaboration logs one warning per (calc def, output) with `extra={"manual_stub": ManualStubNotice(...)}` at `elaborate.py:704`. Family-to-seam table in § D. *Rejected: adding the cause to `CalcNode` (changes the v6 snapshot encoding and invalidates committed snapshots, which is 2b's snapshot work); runtime values in the default lane (generated modules need TEAx).* Limit: from-snapshot generation shows `MANUAL_REQUIRED` without the cause.
- **D10. A candidate refusal is a new qualification on the record, mirrored in the case.** `Qualification` gains `candidate_refusal`, allowed on `omitted`, `excluded` and `admitted` pairs. The case's expectation carries `loss: {family, disposition: "candidate_refusal", rg1: "RG1-<n>"}`. A pure codegen test requires the two to agree in both directions. Recommendations live in `rg1-recommendations.md` in this folder, keyed by `RG1-<n>`. Stub causes have no shared rule, so only the case carries the mark. *Rejected: a free-text note in `semantic_limits` (cannot be checked).*
- **D11. Rule or reproduced gap is decided per row by the rule criterion, after its cases exist, and recorded one line per row.** A row becomes a rule only if its cases show a refusal branch whose reaching contexts can be stated, and the facts come from shared agentic-mbse facts without a heuristic. A rule adds a rule function, reason, record and any fact to agentic-mbse. A gap adds a codegen `SiteReason`, its cases and a `reproduced_gap` disagreement entry. The decisions land in `evidence/r3-closure.md`.
- **D12. No agentic-mbse version bump; the contract is identified by `SUBSET_PROFILE_VERSION`, following ADR 0016.** `_upstream_pins.py` gains `SUBSET_PROFILE_VERSION`, checked by `test_upstream_pins.py`. The adapter module checks it at import and fails by name when the installed agentic-mbse lacks it. The requirement stays `agentic-mbse>=0.1.3,<0.2`. All of 2a's record changes go out under one bump, `subset-profile/v1` → `v2`, in the coordinated merge. No publish is needed. *Rejected: bumping to 0.1.4 with a `>=0.1.4` bound (invalidates the 22 committed snapshots through the envelope's version check, and snapshot authority is 2b's).* This does not meet criterion A2 as written; see Surfaced premise conflicts.

## Architecture

```
               tests/fixtures/subset_profile/<id>/model.sysml
                                │
        ┌───────────────────────┴───────────────────────┐
  generator half (licensed)                      screen half (licensed)
  run_codegen, screen patched to raise           extract_subset_facts → evaluate_subset_profile
  observe: log extra "refusal" / "manual_stub",   observe: findings, verdict
           spied InstanceGraph, model_contract.json
        │                                                │
        ▼ compare                                 compare ▼
  expectations/subset_profile/cases/<id>.json  { generator: …, screen: …, loss?: … }
                                │
        pure tests: agreement under subset_profile_adapter.REASON_MAPPING  ⇄  disagreements.json
                    record citations (packaged rules TOML ⇄ cases)
                    mapping pairs witnessed; candidate marks agree
```

- **Inputs.** Case models; packaged records (through `agentic_mbse.sysml.subset_profile`); the reason mapping (`sysml_codegen/subset_profile_adapter.py`).
- **Live tests** read a model, run one half and compare with one stored answer. They are license-gated, and each test reports by case ID.
- **Pure tests** read only stored answers, records and the mapping. They run without a license, so the agreement and citation guards hold even where SysIDE is absent.
- **Fixtures outside the corpus** (`tests/fixtures/*`) get a stored generator class, not a stored screen answer. The live fixture test runs the generator half to confirm the class, then the screen, and checks screen against class (criteria B4, C2). Their disagreements go in the same record as `fixture:<path>`.
- **Mutations** reuse the live halves: apply one mutation, run that detector's witness cases, require a mismatch.
- **Cross-repo flow.** codegen reads agentic-mbse's package only. agentic-mbse never reads codegen. A contract correction lands in agentic-mbse (records, rules, loader) and the codegen pin moves in the same coordinated merge (ADR 0008).

## Design by criterion group

### A. Pins, mapping and occurrence parity

- **Pin.** `SUBSET_PROFILE_VERSION` joins `_upstream_pins.py` and its test's parameter list.
- **Mapping** (`subset_profile_adapter.py`). `REASON_MAPPING: dict[reason, ReasonMapping]`. Each entry is either `NO_REFUSAL`, or a default code plus optional per-context codes (one reason, several codes, chosen by where the generator refuses). Codes are `ElaborationCode` or `ReadinessCode` values; `SI_SELF_BINDING` is a `ReadinessCode` the generator emits.
- **Mapping tests (pure).** Keys equal `SUBSET_REASON_CODES`. An entry is `NO_REFUSAL` exactly when no record refuses that reason's shape in any context, which is derived from the records. Each record's `expected_code` must be among its reason's mapped codes. Every (reason, code) pair has a case whose stored generator codes include the code and whose stored screen answer refuses a finding with that reason.
- **Renderer.** `render_finding(finding, rules) -> Diagnostic`: code from the mapping, `detail` from the record's remedy, location from `SafeLocation`, `reason` set to the subset reason. Unit tests cover every reason. Nothing on the generate route imports the adapter; an import-boundary test pins that.
- **Occurrence parity** (D6). One licensed test parametrized over the seed, the 37 v6 corpus fixtures and every case whose summary has nodes. A missing input fails by name. A companion test patches `_multiplicity_indices` (`elaboration/occurrence.py:812`) to drop one index and requires a difference.
- **ADR drafts.** `adr-0012-amendment.md` (from the archived draft, its "until Item 2 lands" invariant naming `tests/conformance/subset_profile/test_occurrence_parity.py`) and `adr-0001-inv1-amendment.md` (cases admissible). Both staged in this folder for the owner (RG-3).

### B. Shared rules against the generator's route

- **Tripwire (B1).** One licensed test patches `extract_subset_facts`, `evaluate_subset_profile` and `extract_occurrence_structure` (and any by-name import of them) to raise, then runs every case's generator half and requires each stored outcome. 2b inherits it.
- **Corpus port.** Each Item 1 record, control and reproduction probe becomes a case with `provenance.from_probe`. New cases cover the near-neighbor contexts, inherited and redefined contexts, alternate spellings, template versus instance, and the dc3 `proto3`, `proto4nest` and `conv` shapes rebuilt from a pinned dc3 export.
- **Record coverage.** Pure tests: every `refused` pair has a refusing case; every refused shape has a non-refused case or an SA-1 `no_admitted_context` with refusing cases for each computable context; every `omitted`/`excluded` pair cites a case that asserts at a seam (§ D), including the three site rules' `other_expression_site`.
- **Unconfirmed pairs.** Each R3 § 3 pair gets a case. An observed pair moves to its outcome. An unobservable pair stays `unconfirmed` and gains a record entry `unobservable = {context, reason, evidence = ["case:…"]}`, where the case shows what refuses first (for example ES-001 for `blocked_predicate` at `owner_other`). The loader learns this field; the evaluator still reports `unconfirmed`.
- **Retired shapes.** `part-multiplicity/nonunique` and `negative_bound` leave the records, the rule's shapes and `SUBSET_REASON_CODES`.
- **Fixture classification (B4).** Every directory under `tests/fixtures/` is a model root, inside a model root, or a container. Classes come from one place each: `batch.json` plus the oracle baseline for the 37 corpus fixtures, the case expectation for corpus cases, and `tests/expectations/subset_profile/fixture_classes.json` for the rest. A pure test fails on an unclassed directory or one classed twice.
- **Mutations (B5).** Generator: for each site a rule case names in `generator.witnesses`, in either tree, elide the site and run its witnesses. Screen: for each (rule, shape), disable its recognizer. Each must produce a mismatch.

### C. Agreement and the R3 gaps

- **Agreement rule (pure, every case).** Generator refused with codes C: the screen has at least one `refused` finding, every refused finding's mapped code is in C, and C is covered by those codes. Generator generated: the screen has no `refused` finding. Anything else is a disagreement of the matching kind. A screen that reports only `unconfirmed` or `unverified` on a refusing case is `generator_refuses_screen_silent`.
- **Fixtures (licensed).** The same rule, with the stored class as the generator answer and the live screen. This is criterion C2.
- **Record equality.** The computed disagreement set equals `disagreements.json` exactly (D3).
- **R3 rows.** Each closes per spec § R3 rows. Appendix C names the cases and mechanism per row; `evidence/r3-closure.md` gets one line per row.

### D. Silent losses and String metadata

| Family | Seam (case) | Control | Disposition |
|---|---|---|---|
| ES-010 String, both spellings | no instance-graph attribute node, no entry point, for the String declaration | numeric value on the same feature: node and entry point present | accepted omission, RG-2 |
| CALC-USAGE-BARE-RESULT-DROP | the `CalcNode` for the usage has no output for the bare result | named `return r` on the same usage: output present | candidate refusal, RG-1 |
| ES-007 NON_NUMERICAL | catalog `usage_records` disposition `excluded`/`non_numerical` | numeric constraint `eligible`/`admitted` | accepted exclusion |
| G1 | the part usage's occurrences: one, unindexed | explicit bounds: indexed occurrences | semantics question, RG-1 |
| G2 | occurrence count ignores the usage-level override | no override: the definition's bound | probed first, then as G1 |
| Calc def output stub, one case per cause | `CalcNode.compilability == MANUAL_REQUIRED` and a `ManualStubNotice` with that cause | the supported form compiles `FULLY_COMPILABLE` with no notice | candidate refusal per cause, RG-1 |

- **String fixtures.** Both spellings; a String on an uninstantiated template, on an instantiated part, bound to a calc input (the three ES-010 entry paths), and read by another attribute. `rg2-string-policy.md` gives the options, what each does to generated output and native consumers, and a recommendation.
- **Docs.** `docs/architecture/modeling-assumptions.md` gains a section on today's behavior for String values, NON_NUMERICAL constraints, calc-usage bare results and stubbed calc def outputs, citing case IDs. It links POSITIONAL-FORMAL-REDEFINITION's hazard entry as pending (Item 4).

### E. Per-site codes and the inventory

- **Scanner and account** (D7). `site_scan.py` reproduces Item 1's `scan_sites/1` forms for codegen. It also reports every other `raise` in `src/sysml_codegen/` by name as `unrecognized`, so the inventory is total over `raise` statements. Its remaining blind spots (refusals returned as values, raising helpers whose callers are not itemized) are listed in the account header.
- **Drift test (E1, pure).** Scan, then fail on a site with no row or a row with no site.
- **Scanner mutations (E2, pure).** Synthetic source strings: a new raise of each recognized form, a new exception class, a new raising helper and a computed code mapping. Each must be detected or reported as unrecognized by name.
- **Reasons and witnesses (E3).** Each `public_capability` row gets a `SiteReason` (per site, or per family with the justification in the row) and at least one case naming it in `generator.witnesses`. A pure test checks the raise call passes that reason, every named site ID resolves, and every public row has a witness. The licensed mutation test elides the site and requires the witness to mismatch. Stub sites get their reason through D9. A reachable plain-exception site becomes a coded refusal with a reason. Its code changes from `SI_INTERNAL_DEFECT`, and each such change is listed in the evidence.
- **Unknown sites (E4).** Each of the 46 is classed reachable (then E3), internal invariant with a cited guard, or unknown with a recorded attempt, owner and limit.
- **Split point.** The **head** covers sites joined to a shared rule or an R3-routed row. The **tail** covers the other public sites: the 10 naming collisions, the codegen-only follow-ups and the triage of the 46 unknown sites. The tail runs last. If group E passes its estimate before the tail, the split is taken: the tail moves to a follow-on item, and the orchestrator surfaces that to the owner. The tail is defined by the account's columns, not by whether a disagreement entry exists, because every codegen-only witness creates one.
- **Rescan (E5).** A recorded run of the codegen test and agentic-mbse's narrowed `scan_sites.py` at the final revisions, itemizing added and removed sites.

### F. Semantics questions and baseline evidence

- **G2** gets its reproducing case in group D.
- **`kerml-expert`.** One question per item (G1, G2, every `rg1_pending` disagreement, every candidate refusal), with the case models attached. Answers, cited spec sections and agreement with the generator go in `evidence/semantics-checks.md`.
- **dc3.** `run_trees.py`, once its output path is a parameter, evaluates dc3 `808464df` and `60b44d53` with the v2 contract. `evidence/dc3-rerun.md` itemizes each difference from Item 1's `acceptance.md`. The generator half runs on dc3 repaired at the final codegen revision.
- **Checks.** `pytest`, `mypy` and `ruff` in both repos, licensed, with skips and unrun checks named, in `evidence/repository-checks.md`.

## Required Invariants

1. No stored expectation is computed at test time. Each change to an expectation, the disagreement record or the account is a reviewed diff.
2. Every case's stored screen answer agrees with its stored generator answer under the mapping, or the case is in the disagreement record, and the record holds nothing else.
3. Every non-`unconfirmed` record pair cites at least one case or corpus fixture that a codegen test resolves. No record cites a probe.
4. The generator half never runs the screen. The tripwire test fails if it does.
5. Each mutation names one site ID or one (rule, shape) recognizer. Every mutation produces a mismatch on at least one of its witnesses.
6. Each fact has one editable home: case answers, codegen site rows and the occurrence seed in sysml-codegen; records, reasons and version in agentic-mbse's package.
7. agentic-mbse imports nothing from sysml-codegen. codegen reads agentic-mbse only through its package.
8. 2a changes no accept/refuse outcome. Changed refusal text, new warnings and changed codes for formerly crashing sites are listed in the evidence.

## Component Overview

**sysml-codegen, production (`src/sysml_codegen/`)**
- `_upstream_pins.py`: adds `SUBSET_PROFILE_VERSION`.
- `subset_profile_adapter.py` (new): `REASON_MAPPING`, `render_finding`, the import-time profile check. Off the generate route in 2a.
- `elaboration/diagnostics.py`: adds `SiteReason`. The four refusal carriers gain `reason`. `_render_public_diagnostic` and `_render_readiness_finding` (`elaboration/elaborate.py:133, :194`) append it.
- `cli/__init__.py`: `extra={"refusal": …}` on each refusal log call in `run_codegen`.
- `extraction/expression_compiler.py`, `extraction/calc_compat_renderer.py`, `elaboration/elaborate.py`: `CompilationError` carries a `SiteReason`; `ManualStubNotice` and its warning.
- Raise sites throughout: `reason=SiteReason.…` as group E reaches them.

**sysml-codegen, tests**
- `tests/helpers/subset_profile/`: `cases.py` (expectation schema, loading, agreement; pure), `observe.py` (both halves and seams; licensed), `mutate.py` (raise elision and screen recognizer patches), `site_scan.py`, `occurrence_parity.py`.
- `tests/conformance/subset_profile/`: the test modules for groups A–E.
- Data: `tests/fixtures/subset_profile/<id>/`, `tests/fixtures/subset_profile_occurrence_seed/<case>/`, and under `tests/expectations/subset_profile/`: `cases/<id>.json`, `disagreements.json`, `fixture_classes.json`, `site_account.csv`.

**agentic-mbse (coordinated merge)**
- `sysml/subset_profile.py`: `case:` evidence, `candidate_refusal`, `unobservable`, retired shapes removed, any new rules from D11, version `v2`. `sysml/subset_extraction.py`: any facts new rules need.
- `sysml/subset_profile_rules.toml`: citations move to cases; outcomes per 2a; `verified_against` updated.
- Tests retired: probe fixtures, `subset_probe_judge.py`, `test_subset_probe_evidence.py`, the per-probe reproduction tests, the occurrence seed with its captures and `test_occurrence_parity.py`, the codegen rows of the account, the matrix's codegen site lists. Tests kept: loader, vocabulary, synthetic-fact evaluator tests, hygiene, coupling, version digest, agentic-mbse's own site rows.
- Scripts: `run_trees.py` and `scan_sites.py` take an output path, and `scan_sites.py` scans agentic-mbse only. `probe.py` and the occurrence oracle and parity scripts retire.

**This folder:** `rg1-recommendations.md`, `rg2-string-policy.md`, `adr-0012-amendment.md`, `adr-0001-inv1-amendment.md`, `evidence/`.

## Non-Goals

- Deciding RG-1, RG-2 or RG-3 questions, and fixing G1, G2 or any stub.
- Running the screen inside `generate`, a `check` command, factoring the preparation path, or snapshot work, including carrying stub causes into snapshots (2b).
- A general detector for unknown silent losses (recorded limit).
- Promoting the capability matrix into agentic-mbse's package (Item 3 can decide).
- Re-verifying Item 1's 154 internal-invariant guards, except where 2a changes the code or finds one broken.

## Surfaced premise conflicts

- **Criterion A2 cannot be met as written without leaving 2a's scope.** A2 asks that the agentic-mbse requirement admit no published version lacking the contract. Contract-less 0.1.3 wheels exist, so only a version bump could satisfy it. A bump makes the envelope refuse all 22 committed snapshots (`snapshot/envelope.py:459-461`), and repairing them is snapshot authority work that 2b owns. **Recommendation:** amend A2 to the ADR 0016 form (D12): the requirement stays `>=0.1.3,<0.2`, the `SUBSET_PROFILE_VERSION` pin and import check guard the contract, and the evidence states that no package version identifies it. Until the orchestrator or owner accepts this, A2 is open. Not checked: whether 0.1.3 was ever pushed to a package index.
- **The spec expects a frozen copy if the site account moves; this design moves it without one** (D7). This removes the copy rather than freezing it, which is what the spec's Boundaries ask for ("each codegen site has one editable account row").
- **The ADR 0012 amendment's filing time has passed** (spec, carried). Filing stays RG-3; 2a stages the text with the parity test named.

## Implementation Notes

- The live path rewrites source paths to `root-N/…` referents (`orchestration/elaborated_pipeline.py:458`). The construct-location check normalizes both sides to the case-relative path.
- `run_codegen` imports `build_exact_pipeline_context` inside its body (`cli/__init__.py:1168`). The spy must patch `elaborate_model_paths` as `exact_pipeline_context` references it; the plan confirms that binding at P0.
- Screen facts are cached per case within a session. Screen recognizer mutations then re-run only the pure evaluator, unless the patched recognizer is in extraction.
- `SI_EXPRESSION_SOURCE_UNSUPPORTED` and `SI_INDEXED_SOURCE_UNSUPPORTED` exist in both `ElaborationCode` and `ReadinessCode`. Compare codes by string value.
- `SUBSET_PROFILE_VERSION` moves to `v2` at the first record change on the branch and stays `v2` until merge. The digest test updates with each change.
- Never `ruff format` generated packages in fixtures (CLAUDE.md, study fixture).

## Potential Risks

| Risk | Mitigation |
|---|---|
| Raise elision cannot reach some sites (B2) | Spike S1 first; per-site hand patches as a named fallback list |
| The licensed suite gets slow (B3) | S1 measures; cache screen facts; run each mutation only on its witnesses |
| Retiring agentic-mbse's probe and parity tests leaves agentic-mbse CI without screen-versus-generator coverage | Intended (ADR 0001 invariant 5); coordinated merges run codegen CI. agentic-mbse keeps synthetic-fact evaluator tests |
| Concurrent Item 4 work in agentic-mbse conflicts with record or loader edits | Keep agentic-mbse edits in few commits; rebase checks at each phase gate |
| A new rule (D11) needs facts agentic-mbse cannot extract without a heuristic | Then the row is a reproduced gap; the criterion decides, not effort |
| Adding reasons changes refusal text that baselines store (`public_package_oracle/baseline.json`) | Listed in the evidence and updated as reviewed changes |

## Integration Strategy

- 2a merges as one coordinated pair of PRs (RG-3, ADR 0008): agentic-mbse with contract `v2` and the retired tests; sysml-codegen with the corpus, the adapter, reasons and the moved data.
- 2b imports the adapter, inherits the tripwire, and starts its snapshot work knowing stub causes are live-only.
- Item 3 reads `disagreements.json` (`codegen_owned`, `reproduced_gap`) to say what CLEAR does not cover. Item 5 renders from the v2 records.

## Validation Approach

- Pure lane: case schema, agreement, record equality, citation resolution, mapping, candidate marks, fixture classification, account drift, scanner mutations, renderer.
- Licensed lane: generator and screen halves for every case, the tripwire, fixture classes and screen, occurrence parity with its mutation, generator and screen mutations.
- Recorded runs: rescan of both trees, dc3 re-run, `kerml-expert` checks, repository checks in both repos. The evidence names licensed runs and skips (spec Independence).
- Each phase's `/_my_audit` reviews expectation and record diffs as the named reviewer.

## Next-Stage Handoff

**Fixed:** D1–D12; the fact-placement rule; the agreement rule; the split-point definition.

**Decision records to file once the design is approved** (none filed yet): the fact-placement rule and the retirement of agentic-mbse's probe and parity tests (cross-repo, a future agent would plausibly re-add the copies), in both registers as each binds; D12 as an amendment of ADR 0016 if the A2 recommendation is accepted.

**Open for the plan:** final case list and IDs; `SiteReason` members; which rows become rules (D11, decided by cases); the exact seam for CALC-USAGE-BARE-RESULT-DROP once its graph shape is observed.

**De-risk first: spike S1** (about one day). Elide five sites in-process: a module function, an `_ExactElaborator` method, a nested function, an agentic-mbse `reference_use` site and a `calc_compat_renderer` stub site. Confirm each flips its case, and time ten cases end to end. If elision fails broadly, D5 falls back to hand patches and the group B and E estimates rise.

**Phases.** Groups map to phases one-to-one, with one exception: the scanner port and account move (E1, E2) run in P1, because group B's mutations key on site IDs.

| Phase | Content | Depends on |
|---|---|---|
| P0 | Spike S1 | — |
| P1 | Group A; harness (`cases.py`, `observe.py`, `mutate.py`); scanner port, account move, E1, E2 | P0 |
| P2 | Group B; agentic-mbse records → `case:`, `v2` | P1 |
| P3 | Group C | P2 |
| P4 | Group D, RG-2 recommendation, docs | P2 |
| P5 | Group E head (reasons and witnesses for rule and R3 sites, E4 for those) | P2 |
| — | **Split point**: take only if group E is over its estimate | P5 |
| P6 | Group E tail, E5 rescan | P5 |
| P7 | Group F | P3–P6 |

---

Next Step: `/_my_design_review` in a fresh session, then `/_my_plan`.

## Appendix A — Expectation schema

A case expectation (`tests/expectations/subset_profile/cases/<id>.json`), shown as pseudo-JSON:

```
{ "id": "binding-source__expression_source__owner_instantiated",
  "provenance": {"from_probe": "<id>"?, "r3_row": "ES-003"?, "note": "..."},
  "construct": {"file": "model.sysml", "lines": [7, 7]},
  "generator": {"outcome": "refused", "codes": ["SI_EXPRESSION_SOURCE_UNSUPPORTED"],
                "reasons": ["<SiteReason>"]?, "witnesses": ["<site ID>"]?, "stubs": [{"output": "<qn>", "reason": "<SiteReason>"}]?,
                "seams": [{"kind": "graph_attr|entry_point|catalog_usage|calc_compilability|occurrences",
                           "declaration": "<qn>", "expect": ...}]?},
  "screen": {"verdict": "refused", "findings": [{"rule","shape","context","outcome","subject": "<qn>"}]},
  "loss": {"family": "...", "disposition": "accepted_omission|candidate_refusal", "rg1": "RG1-3"?}? }
```

- `findings` is the complete set the screen reports, not only the witnessed pair, so an unrelated rule change also shows up as drift.
- `codes` is the sorted multiset, as in `scripts/capture_v6_batch.py:110`.
- `fixture_classes.json` maps a path under `tests/fixtures/` to `{"class": "generating|refusing|container|not_a_model", "codes": [...]?, "note": "..."}`.

## Appendix B — What moves between repositories

| Fact | From (agentic-mbse) | To (sysml-codegen) | agentic-mbse keeps |
|---|---|---|---|
| Probe models and outcomes | `tests/fixtures/subset_profile/probes/` | case models and expectations | nothing; git history and the Item 1 archive hold them |
| Occurrence seed | `tests/fixtures/subset_profile/occurrence/` | `tests/fixtures/subset_profile_occurrence_seed/` | nothing; `expected.json` captures retire |
| Normalizer | `tests/helpers/occurrence_oracle_schema.py` | `tests/helpers/subset_profile/occurrence_parity.py` | nothing |
| Codegen site rows (441) | `inventory/site_account.csv` | `tests/expectations/subset_profile/site_account.csv` | its 61 rows |
| Codegen site scan | `scripts/subset_profile/scan_sites.py` (codegen half) | `tests/helpers/subset_profile/site_scan.py` | agentic-mbse scan |
| Matrix codegen `sites` | `inventory/matrix.toml` | the account's `matrix_row` column | rows and agentic-mbse sites |

## Appendix C — R3 rows to mechanism

| Row | Cases | Closes through |
|---|---|---|
| ES-002 | the binding, the admitted neighbor (binding a calc output), the other shapes reaching `occurrence.py:180` | D11; gap → `reproduced_gap` entry and `SiteReason` |
| ES-008 | all five spellings, plain nesting as control | D11 |
| ES-009 | the shape and the other shapes reaching `elaborate.py:2345` | D11 |
| ES-010 refusal side | one case per projection entry path | `reproduced_gap`, `codegen_owned` (D11 of Item 1); RG-2 |
| ES-011 | arithmetic on `return r` and on `out attribute r` | reproduced gap, or retired with admitting cases |
| CALC-DEF-BARE-RESULT | arithmetic, `max`, conditional bare results | D11 |
| CALC-USAGE-BARE-RESULT-DROP | § D family | every bare result `omitted` + `candidate_refusal` if the criterion holds, else a codegen backlog item with owner Reid Westwood |
| DEEP-QUALIFIED-WIRING | a minimal case plus fixture `deep_cross_scope_probe` | `codegen_owned` disagreement |
| G1, G2 | § D | pinned behavior plus `kerml-expert` (F) |
| `unconfirmed` pairs | one per pair | observed outcome, or `unobservable` with the shadowing case |
| Retired shapes | none | removed (B) |
| 85 follow-up sites | witnesses | group E |
| PUSH-DOWN chain-segment, sum-shape sites | one case per reachable site | E4 classification; row to Item 3 with verdicts |
| PUSH-DOWN unsupported operator | stub family cases | § D; row to Item 3 |
| PUSH-DOWN literal shape | `sum(5.0)` | gap or admitted case; row to Item 3 |
| PUSH-DOWN redef precedence, ambiguous inherited attr | pinned cases | a written statement of which value wins and which typing is chosen, in `modeling-assumptions.md` |
