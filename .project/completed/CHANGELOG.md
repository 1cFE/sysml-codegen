# Changelog

Historical record of completed work.

---

## [2026-08-13] - [CONSTRAINT-SEMANTICS Item 2] Canonical Usage Domain and Catalog Totality

**Type**: Item (orchestrated run; audited Needs-work → cured → re-audited Certify-with-residuals)
**Duration**: spec 2026-08-12 → closed 2026-08-13
**Archived to**: `.project/completed/20260813_constraint-catalog-totality/`
**Commits**: codegen item tip `35ee82f` (branch `item7-rebuild`, unpushed) / companion
`bc69f04` in `/home/reid/1cfe/agentic-mbse-item7-rebuild`

### Summary
The lifecycle contract promised that every authored constraint usage stays visible with exactly one
disposition, and the exact route did not keep it. Constraint records only began *after*
owner-to-scope expansion, so on `catf_mfe_d5` — the richest model in the corpus — 65 authored
constraint usages produced 9 carriers and the other 56 were not excluded, not deferred, but
**absent**: nothing recorded that they had ever been written. Worse, a totality gate written against
that data would have been circular, comparing two projections of an already-truncated set, and the
two requirement rows meant to catch this read PASS because each specimen fixture happened to have a
carrier.

This item makes the domain total and proves it with evidence that does not descend from the domain.
The instance graph now mints one `ConstraintUsageRecord` per authored usage **before** occurrence
expansion, each carrying exactly one disposition (eligible / excluded-with-reason /
non-reaching-with-reason) plus its severity, occurrence count, and inapplicability state, joined to
the per-occurrence tier by declaration identity. Severity follows cause, not convenience. A
generation-time completeness gate fails on a removed, duplicated, or misjoined disposition and names
the offending usage. The domain travels through a bumped `instance-graph/v3` codec that fails closed
on v2 and on stripped-tier shapes, with live, in-place-snapshot, and relocated-snapshot routes
verified field for field.

The result on the fixture: **65 members, 9 reaching, 0 eligible** — a measured correction to the
item's inherited "9 eligible" premise (all 65 usages are bare `constraint`, so the 9 that expand
grade `excluded`/`unassessed_form`). And the strongest evidence that this was the right piece of
work is what it deleted: `collect_constraint_manifest`, its two classifiers,
`extraction/constraint_report.py`, and all seven test call sites are **gone** from `src/` and
`tests/` rather than demoted to a second inventory kept in sync. The replacement oracle reads
`.sysml` source through a licence-free scanner that shares no code, no adapter, and no parse with
the elaborator.

### Deliverables
- `spec.md`, `spec-review.md` (11 findings resolved), `design.md` rev 3, `design-review.md`,
  `plan.md` (8 phases with completion notes and deviations), `verification.md` (+ dated cure
  addendum), `audit.md` (original record + re-audit with per-finding cure verdicts),
  `product-lens.md` (spec / design / audit / close blocks), `briefs/`, `probes/`,
  `v2-refusal-list.txt`.
- Canonical authored-usage domain, disposition minting, `@inapplicable:` mechanism, completeness
  preflight (the fifth), `instance-graph/v3` codec, and named diagnostics.
- Independent totality oracle: 42 reviewed expected-population files + licence-free source scanner
  (`tests/conformance/test_constraint_population_oracle.py`).
- Schema pins: `instance-graph/v2`→`v3`, `CATALOG_SCHEMA_VERSION` `2.0.0`→`3.0.0`, companion
  `constraint-facts/v2`→`v3` (new `vacuous_asserted_gate` ADVISORY kind, agentic-mbse `bc69f04`).
  All 21 snapshot-bearing fixtures recaptured **once** at the final schema.
- REQ-EXT-09 and REQ-CL-04 re-graded and re-anchored to the oracle; REQ-EXT-09's domain-vs-carrier
  self-contradiction resolved; reference doc 28 banner-retired; CLAUDE.md preflight count corrected.
- Gates: codegen **1860 passed / 34 skipped / 65 deselected / 0 failed**, zero licence-skip lines;
  `ruff check src` 12, `mypy src` 55 (both at/below baseline); `git diff --check` clean.

### Carried forward (not closed by this item)
- **TEAx must re-vendor `ACCEPTED_CATALOG_SCHEMA_VERSIONS` with `3.0.0`.** B3 forbids TEAx importing
  sysml-codegen, so nothing here can enforce it. While pending, TEAx fails closed on every newly
  generated package — loudly, which is the intended direction. Do not bump TEAx first.
- **Residual R1** — the internal bare-`ComputationGraph` seam is seal-only; a *resealed* removal of a
  non-reaching row passes silently there. No production caller reaches it; both public routes hold.
- **Residual R3** — the calc-def-only package shape has no pre-item baseline, so the A4 cure's
  "this is alignment, not new behaviour" justification is asserted rather than demonstrated. Pinned
  only by two generation-level tests. Natural home: Item 5.
- **The [AGENT] severity exception the owner has not ruled on** — a malformed `@inapplicable:`
  directive halts at `error` grade **whatever the usage's form**, overriding an `[INHERITED]` line
  that says plain forms are never errors. Recorded beside that line in the spec, surfaced in the
  epic's Item 2 section and the lens close block.
- Both R1/R3 and the exception are recorded in
  `.project/backlog/epic_constraint_semantics_contract.md` §Item 2.

### Lessons Learned
- **A totality proof must not descend from the thing it checks.** The tempting build here was a
  second constraint inventory compared against the graph; it would have produced a green gate that
  could never detect the failure that mattered. Deleting the sweep and reading `.sysml` source
  through an independent scanner is what made the evidence worth anything.
- **Absence is worse than a bad answer, because it is invisible.** Two requirement rows read PASS
  for as long as this defect existed, purely because every specimen fixture happened to have a
  carrier. Selection bias in the fixture set is a failure mode a green matrix cannot show you.
- **Two deviations were accepted at audit, both because they were surfaced rather than smoothed
  over**: the 42 expectation files were scanner-generated then reviewed (independence *from the
  domain* is the load-bearing property, and a full 42-fixture cross-check before any file was
  written found and fixed two scanner bugs); and Phase 5's codec work was pulled into the Phase 3
  window when the plan's own recorded contingency fired, with the intermediate gate redefined as a
  committed, enumerated 61-node frozen refusal list that the Phase 8 recapture discharged to zero.
- **The product-lens ledger was not run at plan or implement stage** (audit A7 / residual R5). The
  point was still checked — later, once, by the audit, with probes — but the audit-stage pass fired
  the ledger's own falsifier and two structural smells that an earlier pass could plausibly have
  caught before they reached an auditor. Dispositioned at close as a recorded gap; retroactive
  stage entries were deliberately **not** written, because a judgment made with the outcome in hand
  is not stage-time evidence.
- **Tooling gap noted at close:** this repo has no `.project/adr/` or `.project/product/` ledger and
  no `adr.sh`/`product.sh` (decision records live as ADR sections in
  `docs/architecture/modeling-assumptions.md`). No ids were hand-minted. Item 2's cross-cutting
  decisions are recorded in its archived `design.md` (D1–D10, invariants 1–9) and in the
  requirement rows it re-anchored.

---

## [2026-08-10] - [SOURCE-IDENTITY] Epic + Item 4 archived as SUPERSEDED

**Type**: Supersession archive (not a completion)
**Duration**: epic 2026-08-03 → superseded 2026-08-07 → archived 2026-08-10

### Summary
Archived the SOURCE-IDENTITY epic (`20260810_epic_semantic_source_identity.md`) and its Item 4
(`20260810_source-identity-occurrence-foundation/`) with superseded markers. The Item-4
shadow-layer architecture — a production identity manifest running beside the legacy string
resolver that ignored it by design — was stopped after Phases 1–2 (audit: Needs Work; product
lens BLOCKED on C24). The recovery assessment led the owner to ratify the elaborate-first
replacement on 2026-08-07: the major pivot the ELABORATE-FIRST epic executes, with the string-
compensation machinery deleted at cutover rather than wrapped. Items 1–3 (binding-semantics
spike, route-evidence spike, ratified source-identity contract with the 29-cell matrix) remain
complete and inherited unchanged as the semantic authority; Items 6–8 intent is absorbed into
ELABORATE-FIRST Items 7–8. The stopped Phase-1–2 implementation is preserved forensically on
`item4-phases12-forensic` (codegen `69eef3b`, agentic-mbse `9724f1d`); the salvage subset
landed via ELABORATE-FIRST Item 2.

### Deliverables
- `20260810_epic_semantic_source_identity.md` — epic with supersession record and final status.
- `20260810_source-identity-occurrence-foundation/` — Item-4 spec, design, plan (do-not-resume
  banner), audit (Needs Work), spec/design reviews, product-lens ledger; superseded markers on
  spec/design/plan.
- No code shipped from this item; salvaged evidence types/queries/fixtures are recorded in the
  ELABORATE-FIRST Item 2 entry (codegen `66a61f3`, agentic-mbse `65a35d7`).

### Lessons Learned
Recorded in the recovery assessment
(`.project/research/20260807-143615_source-identity-recovery-assessment.md`): the epic/spec/
design chain explicitly required a parallel identity subsystem the runtime would ignore until a
later item — artifact-to-artifact gates passed while no observable behavior changed. The
ELABORATE-FIRST epic rules (product-behavior gates, one-authority gate, fail-fast spikes) are
the direct answer.

---

## [2026-08-10] - [ELABORATE-FIRST Item 6] Exact-Identity Completion — Payload, Occurrence, Projection

**Type**: Item (three audit rounds: phases-1/2 Needs Work, phases-3/4 Needs Work, full-item v3
Needs Work → certified 2026-08-10 after targeted re-audit of F7–F9)
**Duration**: spec 2026-08-09 → certified 2026-08-10

### Summary
Closed the remaining exact-identity gaps on the internal elaborate-then-project route before the
Item-7 authority switch. Calculation definitions, formals, outputs, compilation results, port
metadata, and constraint profile decisions now attach by exact SysIDE declaration UUID — display
renames, normalized-name collisions, duplicate QNs, and enumeration reorders cannot move
executable payload, and missing/duplicate/mismatched identity blocks with named `SI_*`
diagnostics instead of defaulting to `UNKNOWN`/`float`/null-metadata/`ADMIT`. SysIDE's native
`Usage.usages` view became the sole effective-child-declaration authority (codegen keeps only
finite concrete expansion; audit-F31 closed with a scoped valid-model witness). The validated
graph gained structured occurrence records, typed `ExpressionIR`, declaration-bound formal
provenance, and closed eligibility/compilability inside a fingerprinted internal
`instance-graph/v2`; projection became one-way (ownership/aliases from occurrence records,
execution order from `ProducerRef` edges, entry classification from `ValueSite`) with semantic
collision guards on every public spelling. Nine audit findings across three rounds were
remediated and independently verified — headline fixes: the public constraint source key is
rendered from model metadata, not a parser UUID (F1); formal provenance flows through typed ports
instead of a rendered-name join with a fabricated fallback (F5); profile `BLOCK` halts with the
new `SI_CONSTRAINT_BLOCKED` D10 diagnostic on strict, lenient, and snapshot round-trip routes
where it previously generated an executable module (F7); and the F30 boundary guard is
deny-by-default over every function in all six boundary files with five named, mechanically
exercised exemptions (F9). Every runtime-source matrix cell proves off-default mutation reaching
every and only its bound consumers at the generated public boundary. The shipped legacy route,
snapshot v5 bytes, neutral constraint-fact schema, and generated baselines stayed frozen
throughout; Item 7's deletion ledger now names the four Item-6 transitional dual mechanisms.

### Deliverables
- `20260810_elaborator-identity-completion/`: spec, design authority map, five-phase plan with
  red-first evidence and three remediation records, audit rounds (`audit.md`, `audit_v2.md`,
  `audit_v3.md` — certification in the v3 re-audit addendum), product-lens ledger (spec-F1 +
  audit-F1..F9, full resolution-by-citation history, final gate CLEAR).
- Code: exact-ID sidecars and maps in `extraction/{data_models,extractor,expression_compiler}.py`
  (`compile_calc_def_exact`); UUID-keyed payload/constraint attachment, `SI_CONSTRAINT_BLOCKED`
  enforcement, and native-child occurrence authority in `elaboration/{elaborate,occurrence}.py`;
  occurrence records, typed IR, formal provenance, and closed state in `elaboration/graph.py` +
  `snapshot/instance_graph.py` (internal v2 codec); one-way projection in
  `elaboration/project.py`; deny-by-default guard in `tests/unit/test_elaboration_import_boundaries.py`;
  new fixtures `elab_payload_identity`, `elab_constraint_formal_identity`,
  `elab_native_plural_scope`; coordinated agentic-mbse identified constraint
  extraction/evaluator (`extract_identified_constraint_facts`, `evaluate_identified_profile`) on
  `elaborate-first-salvage`.
- Gates at certification: codegen 3,358 passed / 47 skipped / 18 deselected (zero license-skip
  lines); agentic 1,819 / 1 / 33; corpus 37/37 matching the archived Item-5 ledger; frozen
  artifact hash unchanged (`25e45ad6…`).

### Lessons Learned
[TODO: Add lessons learned]

---

## [2026-08-09] - [ELABORATE-FIRST Item 5] Exact-Identity Elaborator Breadth

**Type**: Item (five audit rounds: phases-1/2 partial certify, rendered-path Needs Work, v1/v2
Needs Work, v3 certified after two remediation waves)
**Duration**: plan 2026-08-08 → certified 2026-08-09 (exact-ID rewrite; supersedes the 2026-08-07
rendered-path implementation)

### Summary
Built and proved the complete exact-identity elaboration front end (ELABORATE-FIRST Item 5) while
the legacy string-resolution route stayed shipped and byte-frozen. SysIDE declaration UUIDs are
wrapped once into typed declaration/slot/occurrence/node identities; a finite occurrence walker,
one contextual resolver, and fail-closed diagnostics feed a typed instance graph that projects
mechanically onto the existing `ComputationGraph` seam and round-trips through canonical
`instance-graph/v1` JSON. Evidence: all 29 inherited contract cells execute at generated-public or
named-diagnostic tier with off-default mutations on live and relocated routes; the 37-fixture
dual-run ledger is machine-verified against a live corpus run (26 expected-collapse / 11
expected-fix, zero unresolved). Audit rounds successively removed rendered-path edge selection
(spec R9), fail-open qualifier fallback, source-text-as-evidence, and — the v3 finding — silent
admission of an invalid same-name inherited/owned part re-declaration, which now blocks
`SYSML_NAMESPACE_NOT_DISTINGUISHABLE` before occurrence expansion via SysIDE's own validation
diagnostic (loader diagnostics are now a required elaborate() input). The deep-cross-scope witness
fixture was repaired to valid explicit `:>>` form and its deep producer-output reference resolves
to its one exact producer channel.

### Deliverables
- `20260809_elaborator-breadth/`: plan (5 phases + two remediation decision records, all
  owner-ratified `[AGENT]`), `diff-ledger.md` (37 rows), `product-lens.md` (findings F1–F31 with
  full resolution-by-citation history), audit rounds (`audit-20260808-phases12.md`,
  `audit-20260808-rendered-path.md`, `audit.md`, `audit_v2.md`, `audit_v3.md` — certification in
  the v3 addendum).
- Code: `src/sysml_codegen/elaboration/` (identity, occurrence, elaborate, graph, project,
  diagnostics, diff, display), `snapshot/instance_graph.py`, `orchestration/elaborated_pipeline.py`
  (internal, no shipped flag), shared `extraction/{source_evidence,binding_evidence}.py`,
  `scripts/run_elaboration_corpus.py`; coordinated agentic-mbse exact-UUID adapter surface.
- Tests: 154 exact-elaboration tests (identity foundation, occurrence, fail-closed, collisions,
  contract matrix, projection, round-trip, public mutation, corpus ledger, model validation,
  import/AST boundaries) plus new fixtures incl. `elab_matrix_c2..c23`,
  `elab_namespace_distinguishability_probe`, repaired `deep_cross_scope_probe`.
- Contract: referent-table "Deep-cross-scope evidence boundary" amendment (corrected premise,
  owner-ratified) in the authoritative lifecycle contract.
- Carried forward: audit-F30 (guard scope) and audit-F31 (plural-fallback fixture) open
  non-blocking; F19 customer-scale proof and F26 legacy-oracle replacement are Item-6
  obligations.

### Lessons Learned
- A ruling is only as good as its premise: the F21 "parser limitation" classification survived
  one audit round because nobody counted the modeled occurrences behind the ambiguity. Reproduce
  the subject of a ruling, not just its record.
- SysML has no name-based implicit redefinition; a same-named nested re-declaration is an invalid
  model. Prefer promoting the parser's own validation diagnostic over reimplementing spec checks,
  and make the diagnostics feed a required argument so no caller can skip it.
- Kept falsifier-shaped assertions (`[x] = list-comp` destructuring on the expected-unique node)
  turn a duplication bug into a loud test failure instead of a green suite.

---

## [2026-07-24] - [DOCS-LIFECYCLE-SYNC] Post-Epic Documentation Reconciliation

**Type**: Item (orchestrated: Opus implement stages + two independent audits; briefs committed)
**Duration**: spec 2026-07-20 (re-verified 07-24); implemented + audited in one orchestrated run 2026-07-24

### Summary
Reconciled `docs/architecture/` and `EXPLAINER_PROMPT.md` with merged main `936315c` after the
CONSTRAINT-LIFECYCLE epic. Five phases against a four-sweep claim register: replaced
`04-input-resolver.md` (documented a deleted module) with `04-producer-resolution.md`,
rewrote doc 24 to the unified-ladder narrative, wrote `30-diagnostic-severity.md` (severity
contract had zero public coverage; documents three stacked fail-closed guards), added matrix
rows REQ-SNAP-21/22 (274→276, index reconciled; pre-existing DM/RES drift fixed), swept the
retired module_kind bool flags, added the nested-override honesty note, re-anchored the
explainer prompt (19 registered re-anchors). Final audit Pass with notes; the one note
(agentic-mbse citations unreachable from the audit sandbox) closed by orchestrator
verification at `f4ebdce` — no open findings.

### Deliverables
- `20260724_docs-lifecycle-sync/`: spec (R1–R7), 5-phase plan, `inventory.md` (the full
  per-claim register incl. E1–E19 and matrix-row candidates MG1–MG3), `audit-midrun.md`,
  `audit.md` (+ N1-closure addendum), stage briefs.
- Follow-on ticketed: `[MATRIX-EPIC-SURFACE-ROWS]` (P3) for the three surfaces registered
  but not added to the matrix.
- NOTE at close: delivered on branch `docs-lifecycle-sync`; owner merge pending.

### Lessons Learned
- Re-verify a spec written from a close-handoff against the merged diff before implementing:
  the original spec missed the epic's largest doc casualty (the resolver unification, six
  stale files) because the handoff's deferred-docs list predated a late refactor.
- Stage briefs that seed verified facts but demand re-verification pay off: the stages
  corrected two orchestrator-supplied citations and surfaced a third fail-closed guard no
  design doc named.

---

## [2026-07-24] - [NESTED-OVERRIDE-TRIPWIRE] Unmatched-Override Warning (interim guard)

**Type**: Item (probe-first; single Opus implement stage; gates re-verified by orchestrator)
**Duration**: same-day (2026-07-24)

### Summary
Made the `[NESTED-OCCURRENCE-OVERRIDE]` calc-path value loss loud: the supplied-value
materializer now warns when a dotted demand falls through silently while the capture carries
an override for that attribute of that part usage, naming captured vs demanded scopes. The
naive predicate false-fired 4× on the clean corpus (reference-form aggregation rollups); two
narrowings (dotted-form gate + part-usage gate) reached 0 fires across all 19 snapshot
fixtures before any production code was written. No resolution outcome or output byte changes;
suite 3118/47 licensed, ruff clean. The occurrence→definition-bridge fix remains filed in
`[NESTED-OCCURRENCE-OVERRIDE]` with an explicit filed-fix scope block.

### Deliverables
- `src/sysml_codegen/resolution/supplied_values.py`: `_BindingTarget.form` (diagnostics-only),
  `_unmatched_override_scopes`, collect-then-drain warning.
- `tests/unit/test_supplied_values.py`: RED-verified positive on the recorded coordinate +
  two pinned silent-on-clean negatives.
- `20260724_nested-override-tripwire/`: brief, probe (`unmatched_override_scan.py`),
  corpus verdict, evidence. No independent audit (orchestrator-verified gates; probe verdict
  committed as the acceptance record).
- NOTE at close: delivered on branch `nested-override-tripwire` (stacked on
  docs-lifecycle-sync); owner merge pending.

### Lessons Learned
- The corpus false-fire scan earned its gate status: the obvious predicate was wrong in a way
  only the corpus could show (site-4 precedent repeated exactly).

---

## [2026-07-20] - [CONSTRAINT-LIFECYCLE] Constraint Execution Lifecycle Remediation

**Type**: Epic (includes the superseded CONSTRAINT-WAVE-REMEDIATION epic doc, archived alongside as frozen history)
**Duration**: ~1.5 days wall-clock (created 2026-07-19; merged + archived 2026-07-20; orchestrated multi-session run + owner merge)

### Summary
The open constraint PR wave carried semantic, graph, package, evaluator, and study-seam defects
that item-level certification alone could not close. This epic implemented the owner-ratified
lifecycle contract across agentic-mbse, sysml-codegen, TEAx, IFE, and the stellarator consumer:
occurrence/demand integrity, shared producer resolution (Gate A), Gate B vacuity deletion,
diagnostic severity (constraint-facts/v2), whole-tree snapshot portability (v5), trusted package
bootstrap/seal provenance, canonical embedded catalog (schema 2.0.0), multi-entry candidate
bridge, producer completeness, TEAx evidence durability, and legacy identity closure — then
proved one sealed artifact thread end-to-end with a 41/41 composed public proof at a
commit-pinned set (16 negative mutations at boundary, 6/6 byte checks). Merged 2026-07-20 in
the test-enforced order agentic-mbse #11 → sysml-codegen #9 → teax #3; post-merge smoke on
codegen main 3115 passed / 47 skipped with zero license-skip lines.

### Deliverables
- 14 items (0–13) plus the ratified lifecycle-contract spec; item folders archived here as
  `20260720_constraint-lifecycle-*` and `20260720_constraint-execution-lifecycle-contract/`
  (specs, designs, design reviews, plans, evidence, independent audits, briefs).
- Composed-proof records: `20260720_constraint-lifecycle-composed-proof/release-readiness.md`
  (pinned set, mutations, byte checks, remaining-state ledger) and
  `evidence-coordinate-register.md` (the 41/41 register).
- Ratified authority remains at
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`.
- Merged mains: agentic-mbse `f4ebdce`, sysml-codegen `936315c`, teax `fa0e06a`. fusion-tea
  (`be1ee7c0`) and stellarator (`342cc799`) evidence branches stay local pending owner delivery.
- Follow-ons filed, not silently dropped: `[NESTED-OCCURRENCE-OVERRIDE]` (BACKLOG P2, probe
  fixture in-tree), Item-10 completeness-check MODULE_OUTPUT exemption (owner ruling pending),
  stale-baseline class (four members, pre-existing), deferred documentation debt (severity
  system, portability matrix row, docs/architecture sweep).

### Lessons Learned
- The composed proof caught what component certification could not: every item certified in
  isolation, yet the composed run surfaced the case-40 IFE harness drift and the case-18
  fixture over-build. Consumer acceptance scripts rot unless something smoke-runs them.
- Byte-identity discipline held — the pinned codegen reproduced the sealed thread
  byte-for-byte, so "run at HEAD" was provably "run at the pin."
- Strict resolution stayed strict: the case-18 halt was INV-2 fail-loud behavior; the fix was
  a fixture correction, not a loosening. Check "author if absent" fixtures against the row
  verbatim before concluding a product defect.
- A general occurrence-materialization gap hid behind a constraint symptom
  (`[NESTED-OCCURRENCE-OVERRIDE]` — def-relative capture vs occurrence-relative demand).
- Merge-order enforcement by a test (`test_upstream_pins`), not a note, survived a long
  multi-session epic; mechanical enforcement beats documentation.

---

## [2026-07-13] - [CONSTRAINT-EXEC] Constraint Execution and Design-Space Studies

**Type**: Epic
**Duration**: ~1 day wall-clock (created 2026-07-12; archived 2026-07-13; one ~14h orchestrated run + owner close session)

### Summary
Modeled physical limits (`assert constraint`) previously died at a drop-report warning, and every
design study re-implemented the judgment by hand. This epic makes modeled assertions execute inside
the generated forward model — Kleene-compiled graph modules feeding an exact-schema report
aggregator, verdicts as data beside ordinary outputs — and adds sealed package contracts plus a
crash-safe study layer (evaluator → store/runner → policy/query/CLI) in teax. Snapshots carry
constraint facts load-bearing (v3); `ExpressionAST` retired onto the shared `ExpressionIR`; the IFE
sweep's hand-coded viability rule is deleted, replaced by the generated assertion (2294/2301 exact,
7 model-favoring boundary rows, [OWNER] ratified).

### Deliverables
- 15 items (0–14) across four repos, each with spec/design/plan/audit + briefs; 8 item folders
  archived here, 3 in agentic-mbse, 4 in teax; fusion-tea acceptance evidence in
  `exploration/ife_e2e/study/` there.
- Independent findings audit: `20260713_epic_constraint_execution_audit_independent.md` (every
  sampled claim reproduced exactly: both mutation probes verbatim, all final gates, boundary rows
  at data level, CE-F1..F3 at source).
- Follow-ons: CE-F1 (standalone catalog emission) and CE-F2 (multi-channel CandidateBridge) in
  BACKLOG; CE-F3 fixed post-run (teax `0d606a4`).
- Gates at close: sysml-codegen 2330/23, mypy 76 baseline, ruff clean; agentic-mbse 1401/1; teax
  fully green 262.

### Lessons Learned
- Item-level certification covers what the item's fixtures exercise: the first real
  multi-entry-channel package through the certified path surfaced three integration gaps the
  single-channel toy fixture could not. An epic-level integration acceptance (real package, all
  layers) belongs in the plan, not just at the end.
- Audits that cannot execute should write "requested live probes" for the orchestrator; the
  probe-addendum + independent re-execution pattern held (both re-run probes reproduced verbatim).

---

## [2026-07-10] - [PUSH-DOWN] agentic-mbse Push-Down

**Type**: Epic (doc archived 2026-07-20 with audit, independent audit, and pre-PR reports)
**Duration**: ~2 days (created 2026-07-08; certified 2026-07-10 after independent-audit remediation)

### Summary
Reusable SysML helpers moved from sysml-codegen into agentic-mbse under a "moves, not behavior
changes" contract: expression reconstruction, the qualified-name utility split, hierarchy
primitives/data models, and aggregation decomposition with compatibility gates. Design
overrides, usage-type indexing, Python rewriting, aliases, scoping, and module construction
stayed in sysml-codegen. Merged as sysml-codegen PR #8 + agentic-mbse PR #10.

### Deliverables
- 4 items, each with spec/design/plan/audit, archived as `20260720_{expression-reconstruction-push-down,qualified-name-utility-split,hierarchy-primitives-models,aggregation-decomposition}/`.
- Independent audit (`20260720_epic_push_down_audit_independent.md`): original verdict Needs
  Work (over-claimed SC-D hazards, undocumented behavior changes in Item 1's move); remediated
  same day; final Certify.

### Lessons Learned
- A "moves only" epic needs its certification record held to the same bar as the code: the
  independent audit caught certified-as-resolved claims the epic audit missed.

---

## [2026-07-08] - [TRUTH-DEBT] Truth-Debt Retirement

**Type**: Epic
**Duration**: ~2 days (created 2026-07-06; archived 2026-07-08)

### Summary
Retired the PIPELINE-TRUTH follow-on ledger in one pass. The live aggregation path now runs
through `resolve_input(AGG_STRATEGIES)`, 3+-segment calc-usage chains resolve instead of
hard-rejecting, matrix test gaps are pinned, inherited-attr classification is fixed, and the
remaining sweep and hygiene debt is either closed or filed with named residue.

### Deliverables
- Archived item artifacts: `spec.md`, `design.md` where present, `plan.md`, `audit.md`, and
  supporting probes/impact notes for six TRUTH-DEBT items.
- Item 1: F4 aggregation-resolution cutover, Strategy D deletion, and `param_groups` typing cleanup.
- Item 2: resolved multi-hop CHAIN bindings with loud fallback diagnostics and live/offline parity.
- Item 3: REQ-DM-08, REQ-RES-05, and REQ-RES-08 test pins and matrix flips.
- Item 4: inherited-attribute classifier fix, snapshot recapture, and xfail retirement.
- Item 5: matrix sweep residue pass, EC-04/AS-06 mutation-proven strengthens, reframes, citations,
  and named overflow filing.
- Item 6: D3 hygiene-tail hardening for loader, aggregation compile, and registry warnings, plus
  site-4 reclassification.
- Pre-PR gates: 2120 passed / 4 skipped / 0 xfailed; ruff src clean; mypy src 97.

### Lessons Learned
- [TODO: Add lessons learned]

---

## [2026-07-06] - [PIPELINE-TRUTH] The Generated Package Is the Truth

**Type**: Epic (doc archived 2026-07-20)
**Duration**: ~2 days (orchestrated)

### Summary
Made the generated package the ground truth for fusion-tea: end-to-end generation/wiring/execution
at true zero V11 offenders, run-C LCOE reproduced bit-exact ($270.1211779380445), and every
downstream workaround deleted upstream. Also: constraint drop report made subtype-aware
(catches `assert constraint`), 13 silent-failure findings fixed by family, 25 self-referential
tests re-anchored, verification matrix reconciled to 253 rows (249 PASS + 4 UNTESTED-argued),
dead code cleared, agentic-mbse guidance taught + checked, docs and explainer refreshed.

### Deliverables
- 10 items, all landed and audited PASS. Epic doc: `20260720_epic_pipeline_truth.md` (Lessons
  Learned inside). Follow-on filings retained in BACKLOG.md (F4 cutover, matrix gaps, classifier
  fix — all later retired by TRUTH-DEBT; plus the still-filed P3 tail).

### Lessons Learned
- See the epic doc's Lessons Learned section (archived with full detail).

---

## [2026-07-06] - [UPSTREAM-FINDINGS] Upstream Findings Remediation & Plant-Idiom Support

**Type**: Epic (doc archived 2026-07-20)
**Duration**: ~2 days (orchestrated); merged as PR #3

### Summary
Fixed the SC-1–SC-11 findings and six research defects surfaced by fusion-tea's real plant
model, added staged cross-part wiring and the snapshot CLI, and synced agentic-mbse. Residue
(10 V11 offenders, assert-constraint silence, F2/F4) was shaped into — and later closed by —
PIPELINE-TRUTH.

### Deliverables
- 12 items, all landed and audited PASS. Epic doc: `20260720_epic_upstream_findings.md`.

### Lessons Learned
- See the epic doc (archived).

---

## [2026-02-22] - [OUTPUT-REGISTRY] Output Registry & Backtracker Redesign

**Type**: Epic (doc archived 2026-07-20)
**Duration**: ~9 days (created 2026-02-13)

### Summary
Replaced the single-dict output registry with typed registries and cut the backtracker over to
typed dispatch: ~715 lines of legacy resolution removed, 39 tests migrated, E2E YAML diffs
clean on all 4 models, 641 tests passing at close.

### Deliverables
- 4 items. Epic doc: `20260720_epic_output_registry_backtracker_redesign.md`.

### Lessons Learned
- See the epic doc (archived).

---

## [2026-02-10] - [COST-PATTERN] Item 4: Pipeline Integration -- Hierarchy-Aware Module Generation

**Type**: Epic Item (COST-PATTERN Item 4)
**Duration**: ~1 day

### Summary
Integrated hierarchy-aware extraction (Items 2-3) into the full codegen pipeline. Virtual CalcUsage binding rewriting resolves `:>>` redefinitions (LITERAL, CHAIN, design deep-path) before the backtracker runs. Aggregation modules generate from `AggregationExpressionData` with symbolic channel resolution, multiplicity entry points, and `# source: aggregation` YAML comments. Extended CLI generation layer with aggregation module wrappers, auto-implementations, registry entries, and backlog reporting.

### Deliverables
- Pipeline Step 3.5: `_extract_hierarchy_and_rewrite_bindings()` in initialization.py
- Pipeline Step 4.7: Aggregation expression storage on `PipelineContext`
- Graph builder: `_build_aggregation_module()`, `_extend_output_catalog_with_aggregation()`, symbolic channel resolution
- Backtracker: `_resolve_from_aggregation_output()` strategy (Strategy 7)
- CLI: `_generate_aggregation_modules()`, `_generate_aggregation_stencils()`, registry and backlog extensions
- Generation: `_module_to_context()` aggregation comment, `generate_registry_function()` and `generate_backlog_report()` aggregation params
- 454 tests, 0 failures (141 new tests across 4 phases)

### Lessons Learned
- Computed attribute pattern provided clean template for aggregation CLI generation
- `ScopedAggregationData` with `module_eqn` property cleanly handled ADR-003 naming
- Deriving input names from `PipelineModule` (vs regex-parsing expressions) was the cleaner approach

---

## [2026-02-09] - [ATTR-EXPR] Attribute Expression Capture

**Type**: Epic
**Duration**: ~2 days (estimated: ~6.5-8.5 days)

### Summary
Enabled SysML modelers to express computations as attribute-level expressions (`attribute volume = pi * r^2 * h`) instead of requiring full CalcDef+CalcUsage ceremony. Codegen detects computed attributes on PartDefs, classifies them via a 5-way scheme (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE), generates synthetic pipeline modules for FORMULA patterns, and auto-implements them using the Phase 1 expression compiler.

### Deliverables
- `ComputedAttributeData` model and 5-way `ComputedAttributeClassification` enum
- `extract_computed_attributes()` extraction module (Step 4.5 in pipeline)
- Graph builder extension for FORMULA synthetic module generation
- Backtracker computed attribute awareness (FORMULA -> MODULE_OUTPUT resolution)
- 21 E2E tests validating probe fixture (9 ground-truth values) and solar_battery `p_net_kw`
- ADR-004: Computed Attribute Pipeline Integration
- ADR-005: Computed Attribute Classification
- ADR-001 clarification (computed attribute entry points)
- ADR-002 amendment (FORMULA pattern exemption, modeling guidance)
- Full test suite: 285 tests, 0 failures, 0 xfail

### Lessons Learned
- Spike de-risked the entire epic with purpose-built probe fixture
- Phase 1 expression compiler reused with zero changes
- Option C (direct graph integration) cleaner than original Option A recommendation
- Chain handling was a non-issue (biggest simplification)
- ADR migration from monorepo should have been done during repo split

---

## [2026-02-08] - [EXPR-CODEGEN] Expression-Aware Code Generation

**Type**: Epic
**Duration**: ~8.5 days

### Summary
Built expression compiler that auto-implements CalcDef output expressions as Python code. 15/15 solar_battery CalcDefs, 19/21 CATF CalcDefs auto-implemented. Eliminated the `_impl.py` handwriting bottleneck.

### Deliverables
- Expression compiler (`expression_compiler.py`)
- Auto-implementation template (`auto_implementation.py.jinja2`)
- Step 6.5 pipeline integration
- 167 tests, 0 xfail

### Lessons Learned
- CalcDef-agnostic compiler design enabled reuse in Phase 2 (ATTR-EXPR) with zero changes

---
