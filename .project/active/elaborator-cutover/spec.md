# Spec: Atomic Cutover — Switch, Delete, Snapshot, Recapture

**Item:** ELABORATE-FIRST Item 7
**Status:** Draft — P0/P1 spec-review corrections incorporated
**Owner:** Reid W
**Created:** 2026-08-10 06:29:00 PDT
**Revised:** 2026-08-10
**Complexity:** HIGH
**Branch:** `source-identity-epic`

---

## Pipeline Rationale

Shaping is skipped because the epic, governing contract, architecture research, shared elaborator
design, and certified Items 5–6 already define the work at their recorded authority grades. Owner
ratification does not upgrade an agent-authored strategy to owner provenance. Product design is
skipped because this item changes an internal authority, snapshot/API boundary, and validation
route without adding a new interaction model. Technical design must close the public API and wire
mechanics within the outcomes below.

## Problem

**[NEED]** The owner requires codegen to use the resolved referents available when the model is
loaded and not reconstruct them later. The owner also ruled that snapshots are a format choice and
must serialize the representation the pipeline actually needs: here, the instance graph. Authority:
`.project/backlog/epic_elaborate_first_architecture.md:61-70`.

**[INHERITED]** Item 6 certified the exact-ID instance graph and one-way projection, but the shipped
live builder, capture path, and v5 loader still use the legacy string-based front end. The exact
route remains a parallel internal entry point. The current product therefore has two authorities,
retains the defect-producing resolution machinery and its wrong-oracle tests, and cannot carry its
resolved graph through the public offline route. Sources: `.project/CURRENT_WORK.md` and
`.project/completed/20260810_elaborator-identity-completion/audit_v3.md`.

## Success Criteria

- [ ] **[NEED] Mission outcome.** One semantic source occurrence becomes exactly one runtime source
  across every and only its calculation, constraint, and aggregation consumers; public mutation
  proves the topology, and unsupported forms fail before generation. Authority: the owner mission
  invariant at `.project/backlog/epic_elaborate_first_architecture.md:78-80`.
- [ ] **[INHERITED] Certified consumer-surface extension.** The every-and-only proof also covers
  FORMULA and alias consumers at the public generation boundary, with Item 7 retaining the shipped
  live and relocated-snapshot proof. Sources: the inherited identity invariants at
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:350-379`,
  `.project/completed/20260810_elaborator-identity-completion/spec.md:48-51` and its certification
  at `.project/completed/20260810_elaborator-identity-completion/audit_v3.md:287-302`.
- [x] **[NEED] Instance-graph snapshot outcome.** The public snapshot carries the resolved instance
  graph the pipeline needs, not extraction facts that require semantic reconstruction. Authority:
  the owner snapshot ruling at `.project/backlog/epic_elaborate_first_architecture.md:67-70`.
- [ ] **[INFERRED] One atomic shipped authority.** Public live generation, capture, snapshot load,
  relocated load, and projection use one authority. The old front end, parallel exact entry point,
  dual-run route, and alternate projectable adapters are absent. Cutover, deletion, version bump,
  accepted recapture, and owner disposition form one mergeable unit. Source: epic `[AGENT]
  (ratified by owner, 2026-08-07)` strategy and gates at
  `.project/backlog/epic_elaborate_first_architecture.md:85-97,113-137`.
- [ ] **[INHERITED] Outcome-specific route acceptance.** Every inherited contract cell satisfies
  R7. Only `RUNTIME_SOURCE` requires live, in-place-snapshot, and relocated-snapshot parity;
  diagnostic and load-error cells retain their own route obligations. Source:
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:749-768`.
- [x] **[INFERRED] F19 in-place customer proof.** The existing maintained
  `tests/fixtures/fusion_tea/` model is migrated in place, without a parallel fixture or a 38th
  corpus row. All current SRC-01 sites migrate to the bare-renamed D-5 form, the C25/C2 topology in
  R9 is exact, and separate off-default mutations of availability and thermal efficiency reach
  every and only their declared consumers on public live, in-place-snapshot, and relocated-snapshot
  routes. Source: contract D-5 and customer checkpoint item 8, both `[AGENT] (ratified by owner,
  2026-08-05)`, plus C25/C2 in
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:443-476,932-947,1201-1224`.
- [x] **[INHERITED] C19 runtime proof.** The named nested-occurrence fixture applies `80.0` to its
  one calculation and one constraint consumer on public live, in-place-snapshot, and relocated-
  snapshot routes. Source:
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:1317-1330`.
- [ ] **[INFERRED] C19 legacy deletion.** The supplied-value tripwire and its mechanism test are
  deleted with the cutover mechanism. Source: the agent-authored Item-7 deletion scope at
  `.project/backlog/epic_elaborate_first_architecture.md:427-466`.
- [ ] **[INFERRED] Closed API and deletion surface.** The public-API census in R3 and cutover census
  in R6 are closed with no undecided row. Every R4 responsibility and Item-6 transitional dual is
  deleted, migrated, or retained under one nonlegacy owner; every deleted behavioral oracle has an
  independent one-to-one replacement; static gates prove no residue.
- [ ] **[INFERRED] F26 and dual-run removal.** The live legacy-oracle assertion is replaced by
  independently pinned public names and stable IDs. The dual-run runner, diff code, parallel entry
  point, and executable ledger-comparison tests are gone. The Item-5 ledger remains historical
  authority at `.project/completed/20260809_elaborator-breadth/diff-ledger.md`.
- [ ] **[INFERRED] Measurable customer-scale and real-TEAx evidence.** The in-place Fusion Tea model
  meets the thresholds and environment record in R10. Temporary packages generated from public
  live and relocated-snapshot routes pass the seal and real-TEAx checks in R11 and reproduce the
  independently derived LCOE result. No generated package or TEAx product change is committed.
- [ ] **[INFERRED] Coordinated repository gates.** `sysml-codegen` and `../agentic-mbse` pass the
  fresh exact-count, license, Ruff, mypy, and diff gates in R12. TEAx is evidence-only unless the
  item is explicitly amended to modify it.
- [ ] **[INFERRED] One accepted recapture batch.** R13 produces one owner-accepted committed batch,
  a timestamp-churn-controlled classified diff, and zero unclassified changes. The owner's
  recapture review and recorded disposition are prerequisites to Item-7 completion and merge. The
  checkpoint is **pending**; this spec does not claim approval.

## Known Requirements

- **[INFERRED] R1 — Atomic landing.** The authority switch, v6 envelope, public API migration,
  deletion ledger, test migration, accepted corpus batch, and dual-run removal are one landing unit.
  Internal implementation phases may be reviewable, but no completed or releasable state may expose
  both projectable authorities. Source: epic `[AGENT] (ratified by owner, 2026-08-07)` strategy at
  `.project/backlog/epic_elaborate_first_architecture.md:113-137`.
- **[INFERRED] R2 — Complete integrity-bound v6 envelope.** *Amended after implementation: the
  shipped envelope carries no `capture` object. See design.md "Amendments", A2 —
  `[AGENT amendment, re-derived 2026-08-12 — pending owner ratification at the gate]`.* The
  shipped envelope uses
  `snapshot_format_version = 6`. A later integer is allowed only if another committed format change
  has already consumed v6 and the design records that fact. The envelope carries model identity,
  capture provenance, a portable source-staleness manifest, the validated instance graph and its
  schema/fingerprint, and every version/certifiability marker needed to reject semantic skew.

  - Every field that can affect identity, staleness judgment, validation, projection, generated
    output, or certifiability is load-bearing. It must be integrity-bound and validated before graph
    construction/projection, or explicitly classified as non-authoritative and proven unable to
    affect those outcomes.
  - `captured_at` and any other non-authoritative provenance field may remain outside the semantic
    fingerprint only if mutation cannot change validation, projection, generated bytes, or the
    accepted semantic diff.
  - Tests cover missing/old v5 and older/unknown-future envelope versions; missing, added,
    duplicated, wrong-typed, and tampered authoritative outer fields; model-identity and
    source-manifest/hash skew; certifiability/profile/schema-marker skew; graph replacement;
    inner-fingerprint mismatch; and a correctly re-fingerprinted inner graph paired with tampered
    outer authority. A separate field-order case proves the canonicalization rule chosen by design.
    Every semantic tamper or skew fails before projection with the named recapture/skew outcome.
  - There is no upgrader, grandfathered projectable path, or compatibility loader.

  Exact JSON nesting, canonicalization, and whether one outer signature or nested integrity records
  bind these fields remain design choices. Source: shared design D9 and Item-6 cutover census, both
  agent-authored inputs; this requirement is therefore `[INFERRED]`, not owner-settled.
- **[INFERRED] R3 — Closed public-API disposition census.** Design must create a durable, closed
  census for every current and proposed public surface. Each row records repository, import path and
  symbol/command, current signature/flags, current return type and exceptions, current callers and
  re-exports, final keep/migrate/delete disposition, final signature/flags, final return type and
  exceptions, compatibility decision, migration owner, and acceptance test. No row may be `TBD` at
  design approval. The census includes, at minimum:

  - live `build_pipeline_context(model_paths, targets, include_all, design_path_filter,
    lower_constraints_enabled) -> PipelineContext` and the internal
    `build_elaborated_pipeline(...) -> ComputationGraph`;
  - `capture_snapshot(model_paths, output_path, design_path_filter)`, its write/return/error
    behavior, and every public capture helper;
  - `build_pipeline_context_from_snapshot(...)`, the low-level envelope loader/validator/projector,
    and every public snapshot-load helper;
  - CLI `generate` and `snapshot`, including `--models`, `--from-snapshot`, target/include/filter
    behavior, output/overwrite/package flags, mutual-exclusion rules, exit codes, and emitted errors;
  - `PipelineContext`, any replacement return/container type, all fields, constructor behavior,
    exception classes, and imports/re-exports from `sysml_codegen.orchestration`,
    `sysml_codegen.generation`, `sysml_codegen.generation.initialization`,
    `sysml_codegen.snapshot`, and the package root.

  Design may return `ComputationGraph` directly, retain a narrow graph-bearing context, or expose a
  single load/elaborate result that capture can serialize before projection. Any retained parameter
  or type must run on the sole instance-graph authority. No compatibility object, deprecated field,
  flag, exception alias, or re-export may retain or reconstruct the deleted route merely to avoid a
  caller migration.
- **[INFERRED] R4 — Complete deletion ledger.** The cutover removes or converges the following
  agent-authored responsibilities from the shared design deletion ledger, Item-6 cutover census,
  and epic Item 7:

  - legacy occurrence identity and rendered-path reconstruction, including `PartInstanceIndex`,
    `PathStep`, `InstanceOccurrence`, and consumers that parse `instance_path` into structure;
  - virtual-binding rewrite, specialized-chain rewrite, alias expansion, and self-named rescue;
  - legacy aggregation scope re-derivation and qualified-name surgery;
  - virtual calculation-usage expansion;
  - the dependency backtracker's semantic edge-discovery ladder and channel-to-producer reverse
    parsing; topological ordering survives only as direct graph-edge behavior;
  - the 21-key-form producer-resolution table and scope climb;
  - the supplied-value materializer, including the C19 tripwire;
  - `OutputRegistry` identity namespaces and the old registry builder;
  - legacy graph assembly and group-deriver value backfill;
  - extraction-snapshot v5 capture, serialization, loading, semantic rebuild, and snapshot-context
    route; route-neutral helpers still used by exact elaboration/projection move to neutral owners;
  - the dual-run diff, runner, parallel entry point, corpus comparison tests, and wrong-oracle tests;
  - **Item-6 dual 1:** identified and neutral constraint extraction converge on one live extraction
    pass and one public authority; no parallel-facing wrapper remains for codegen;
  - **Item-6 dual 2:** exact-ID profile evaluation is the sole codegen path; the QN adapter is
    removed after non-codegen validation callers migrate or is explicitly retained as a neutral
    validation-only surface that cannot become codegen authority;
  - **Item-6 dual 3:** the exact compiler becomes the single compiler core; the name-keyed parallel
    AST walk and coexistence assertion are deleted; and
  - **Item-6 dual 4:** name-keyed calculation payload maps and temporary v5-excluded ID sidecars
    converge into one exact-ID payload when v5 is removed.
- **[INHERITED] R5 — Certified prerequisite is preserved.** Build on the certified codegen Item-6
  state and coordinated `../agentic-mbse` exact-constraint state. Graph validation, exact payload
  identity, native effective-child selection, typed IR, formal provenance, fail-closed constraint
  eligibility, and the deny-by-default boundary guard remain load-bearing. Source:
  `.project/completed/20260810_elaborator-identity-completion/{spec,design,plan,audit_v3}.md`.
- **[INFERRED] R6 — Closed production/export/caller/script/test census.** Design creates
  `.project/active/elaborator-cutover/cutover-census.md`; implementation and plan keep it current.
  The population is mechanically enumerated from both coordinated repositories and is closed before
  design approval. Each stable row identifies a production file/symbol or responsibility, export,
  caller, executable script, and affected test responsibility, then records one of:

  - **delete:** deletion justification, replacement owner, exact independent replacement-test ID,
    and no-residue gate;
  - **migrate:** final owner/path, caller/export/API migration, preserved behavioral oracle, and
    final test ID; or
  - **retain:** a positive nonlegacy responsibility and proof that the retained code neither calls,
    adapts, nor reconstructs a deleted authority.

  Every deleted behavioral test responsibility has its own one-to-one replacement record naming
  the independent source of expected behavior and exact kept/migrated test. A replacement may not
  execute the legacy front end, copy its runtime output, or inspect a private compatibility field.
  Static gates derived from the closed census fail on any deleted file, symbol, import, export,
  call, CLI route, script entry, compatibility flag, or wrong-oracle test that remains outside
  historical `.project/` records. The census also covers independently useful legacy suites such as
  backtracker, dual-resolution, aggregation-key, OutputRegistry, VBR, orchestrator, graph-builder,
  snapshot, runtime, and execution tests; the 29-cell matrix alone is not accepted as their blanket
  replacement.
- **[INHERITED] R7 — Route behavior follows the governing outcome matrix.** The 29 cells remain
  authoritative by path and are not restated individually:

  - `RUNTIME_SOURCE`: one public source; full public live = in-place snapshot = relocated snapshot
    projection/generation parity; an off-default mutation reaches every and only its bound
    consumers.
  - `AUTHORING_DIAGNOSTIC`: live codegen emits the blocking named diagnostic before generation;
    capture refuses and produces no snapshot artifact or loader input.
  - `AMBIGUITY_DIAGNOSTIC`: a named diagnostic occurs before a source exists; any route that reaches
    resolution has the same disposition, and no route yields a source.
  - `POLICY_DIAGNOSTIC`: the exact cell-specific policy outcome remains; no route mints a source or
    selects a same-named candidate.
  - `LOAD_ERROR`: model load fails; capture and snapshot routes do not exist for that case.

  Non-authoritative logs or the recapture review manifest may record a refusal. A diagnostic-bearing
  graph may be used transiently by internal review tooling only if it is not persisted as a snapshot
  artifact, cannot be passed to any public loader/projector, and cannot become corpus authority.
  Source: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:749-768`.
- **[INFERRED] R8 — Affected-test disposition.** The closed census classifies responsibility, not
  whole files:

  - **Kept:** independently anchored exact-identity, payload, occurrence, model-validation,
    graph-validation, one-way projection, collision, generation-boundary, boundary-guard, and shape
    learning tests that do not inspect deleted helpers. This includes the C19 structural oracle in
    `tests/conformance/test_elaboration_spike_parity.py`.
  - **Migrated:** the contract matrix, public mutation, graph round-trip, snapshot
    generation/contract/version/portability, public generation-boundary, real execution, and
    public import/return tests move from internal graph-v2, v5, or legacy context paths to the sole
    public live/capture/in-place/relocated v6 route while preserving independent behavior.
  - **Deleted with replacement:** the dual-run files/runner, F26 legacy comparison, legacy
    `PipelineContext` field oracles, exact/legacy compiler-coexistence assertion, v5-sidecar-shape
    assertions, C19 supplied-value tripwire, and mechanism-only VBR/backtracker/key-table/
    supplied-value/registry/legacy-assembly/rebuild assertions. Each responsibility carries the
    one-to-one independent replacement required by R6.
- **[INFERRED] R9 — F19 is the in-place Fusion Tea migration.** Modify the one maintained
  `tests/fixtures/fusion_tea/` corpus fixture; do not create a corrected sibling or change the
  inherited 37-path population. Migrate all 15 current SRC-01 self-binding sites in place to the
  bare-renamed D-5 form while preserving each intended referent. In particular:

  - **C25 availability:** the source declaration remains
    `IFE Power Plant::availability`; the concrete occurrence remains `hif_plant` with its `0.90`
    override. The usage-authored `meier_coe_calc` binding resolves to the occurrence-level feature;
    the definition-authored `lcoe_calc` binding resolves to the def-level feature and reaches that
    same occurrence through the occurrence bridge. Projection exposes one
    `hif_plant.availability` public input and exactly two consumer edges.
  - **C2 thermal efficiency:** the source declaration remains
    `IFE Power Plant::thermal_efficiency`; the concrete occurrence remains `hif_plant` with its
    `0.43` override. The definition-authored `lcoe_calc` and `recirc_calc` bindings resolve to the
    def-level feature and reach that same occurrence through the occurrence bridge. Projection
    exposes one public input at the concrete occurrence and exactly two consumer edges.

  Separate off-default mutations of those two public sources assert exact consumer-key equality:
  availability changes `meier_coe_calc` and `lcoe_calc` only; thermal efficiency changes
  `lcoe_calc` and `recirc_calc` only. The fixture's physical source attributes, defaults, semantic
  referents, numerical equations, and model physics remain unchanged. Renames of calculation formal
  identifiers and their corresponding expression identifiers are permitted and required where
  needed to make all 15 bindings D-5 bare-renamed; they change naming, not arithmetic semantics.
  Record every resulting generated module-name, schema-name, input-name, and test consequence in
  the closed R3/R6 censuses, including its old and final name, disposition, caller/test owner, and
  independent acceptance oracle. Temporary Item-7 packages may exercise the renamed surfaces;
  committed downstream package and study migration remains Item 8. Authority: D-5 and customer
  checkpoint item 8 remain `[AGENT] (ratified by owner, 2026-08-05)` at contract lines 443–476; C2 and C25 are
  the inherited acceptance targets at contract lines 932–947 and 1201–1224, respectively.
- **[INFERRED] R10 — Measurable customer-scale budget.** The measured model is the migrated
  `tests/fixtures/fusion_tea/` fixture. Evidence records OS/kernel, CPU model and logical count,
  total RAM, Python and `uv` versions, lockfile hash, SysIDE version/license status, repository
  SHAs/dirty state, and command lines. After one warm-up, three measured runs on the same machine
  must each satisfy: live load + elaboration <= 10.0 s; projection <= 2.0 s; capture + envelope
  serialization <= 5.0 s; generation + seal <= 30.0 s; real-TEAx execution <= 30.0 s; peak RSS <=
  512 MiB; and v6 envelope size <= 25 MiB. Occurrence, node, edge, and envelope-byte counts are
  recorded and identical across repeated runs and live/in-place/relocated graph semantics. These
  thresholds are an agent inference with headroom over the Item-6 `0.97 s / 208,220 KiB`
  diagnostic-only reference; changing them requires a spec amendment, not a quiet design choice.
- **[INFERRED] R11 — Real TEAx smoke is temporary evidence.** Generate and auto-seal temporary
  packages from the migrated Fusion Tea model through the stock public codegen live and relocated-
  snapshot surfaces. Before execution, both the trusted
  `sysml_codegen.contracts.verify.verify_package(...).ok` oracle and the emitted verifier must
  accept the package and agree on the covered artifact hashes. Discover modules through the
  generated package's public `create_<package>_registry` surface, backed by TEAx
  `simkit.core.registry_builder.create_registry`, and execute through
  `simkit.core.pipeline.execute_pipeline`; no stub, private generation helper, or compatibility API
  counts. Both routes reproduce the independently hand-derived Fusion Tea LCOE
  `270.1211779380445` within relative tolerance `1e-6`, and the R9 mutations produce the independently
  declared every-and-only consumer changes. Evidence records the TEAx checkout/distribution path,
  commit or installed version, lock/package state, and dirty status. Generated packages and run
  outputs live under a temporary directory and are not committed.
- **[INFERRED] R12 — Coordinated repository and quality gates.** The coordinated implementation
  repositories are this `sysml-codegen` worktree and `../agentic-mbse`. Record fresh exact
  passed/skipped/deselected counts after deletions and migrations; Item-6 counts (codegen
  `3,358/47/18`, agentic `1,819/1/33`) are historical context only. Required commands in each repo
  are `uv run pytest tests/`, `uv run ruff check src`, `uv run ruff check src tests`,
  `uv run mypy src/`, and `git diff --check`.

  - Production Ruff (`ruff check src`) and all changed-file Ruff selections are clean.
  - Full-tree Ruff introduces zero new findings relative to the Item-6 baselines of 358 codegen and
    127 agentic findings; totals may fall when obsolete tests are deleted.
  - Mypy introduces zero new findings, reports no error in a changed file, and does not exceed the
    Item-6 baselines of 71 errors in 17 codegen files and 105 errors in 23 agentic files.
  - Intended licensed tests are collected, no acceptance is hidden by xfail, and outputs contain
    zero `no live syside license` skip lines.

  TEAx is an evidence-only checkout/dependency for Item 7. It must be revision/state-pinned and
  unchanged. If Item 7 truly needs a TEAx production or test change, amend this spec and the closed
  censuses to add TEAx as a coordinated modified repository before making that change.
- **[INFERRED] R13 — One accepted recapture batch and owner gate.** After the authority, envelope,
  and deletion work is stable, produce one candidate batch covering exactly the inherited 37 paths
  and recording each path's actual public outcome. For every matrix-derived result, R7 governs the
  outcome, route, and mutation obligations; the manifest names every contributing cell and retains
  every cell obligation when one fixture covers several cells. Classified non-R7 control paths
  retain their exact Item-5 ledger outcomes rather than being forced into an R7 outcome.
  `agg_literal_probe` is **not** such a control. **[OWNER 2026-08-10] Modeled aggregation is
  accepted as executable**, re-verified on the clean Item 6 baseline in recovery Phase 2: the
  fixture's `CodeGenerationError` comes from the pre-elaboration calc-def presence gate, not from
  aggregation semantics, so a route that reaches the elaborator is required to produce a graph for
  it. A separate, genuinely empty control carries the no-calculation-definition responsibility.
  Source: `.project/completed/20260809_elaborator-breadth/diff-ledger.md` (B37-01 ruling section).
  `RUNTIME_SOURCE` rows produce v6 snapshots; `AUTHORING_DIAGNOSTIC` rows record capture refusal and
  leave no snapshot artifact; `LOAD_ERROR` rows record the load failure and have no capture
  artifact. Remove every stale v5 artifact.

  The candidate includes a durable path/outcome manifest and a human-reviewable diff with
  `captured_at` and other known mechanical churn normalized or isolated. Every semantic change is
  classified by reference to the Item-5 ledger, with zero unclassified changes. The owner reviews
  that candidate and records an explicit accept/revise disposition. Item 7 cannot be marked
  complete, committed as the final atomic landing, or merged before acceptance. Exploratory runs
  and owner-rejected candidates remain temporary evidence and never become committed corpus
  authority. Corrections made before acceptance replace the candidate batch; only the accepted
  batch is committed, so the repository has one committed recapture authority rather than an
  accretion of rejected batches. The checkpoint remains pending.

## Non-Goals

- **[INFERRED]** Item 8 owns committed Fusion Tea/Stellarator generated packages, downstream study
  reruns, July IFE impact work, assurance/certification repair, modeling guidance, and architecture
  documentation. Item 7 may change the maintained codegen Fusion Tea fixture and produce temporary
  package evidence only. Source: the agent-authored Item-8 scope at
  `.project/backlog/epic_elaborate_first_architecture.md:472-501`.
- **[INFERRED]** TEAx production, tests, or committed artifacts are outside Item 7 unless this spec
  is explicitly amended to add TEAx as a modified coordinated repository.
- **[NEED]** Self-binding remains a modeling error and is never reinterpreted as an outer
  reference. Authority: owner rulings at
  `.project/backlog/epic_elaborate_first_architecture.md:61-66`.
- **[INHERITED]** The 29-cell semantics and contract-specific diagnostic outcomes are unchanged.
  Source: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:735-768`.
- **[INHERITED]** Non-finite multiplicity support and automatic public-name disambiguation remain
  outside this item. Sources: `.project/backlog/epic_elaborate_first_architecture.md:106-109` and
  `.project/active/elaborator-design/design.md:288-291`.
- **[INFERRED]** v5 and older snapshots receive no migration, grandfathering, or compatibility
  adapter.

## Open Questions / Deferred to design

- The exact v6 envelope field layout, canonicalization, and integrity mechanism. R2 fixes which
  fields are authoritative and the tamper/skew outcomes.
- The final public return/container shape and retained parameter set. R3 requires a row-level closed
  disposition before design approval.
- The internal deletion/refactor sequence and route-neutral helper homes. R4 and R6 fix the final
  authority and no-residue outcome.
- The implementation of recapture staging, timestamp normalization, and review rendering. R13 fixes
  the one accepted committed batch and owner-gated completion rule.
- The temporary package directory and exact TEAx checkout/distribution location. R11 fixes the
  public discovery/execution APIs, seal oracle, revision evidence, and expected result.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_elaborate_first_architecture.md` (ELABORATE-FIRST Item 7)
- **Governing contract:**
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` (inherited 29-cell
  contract and C25/C2 customer targets; referenced by path, not restated wholesale)
- **Classified corpus ledger:**
  `.project/completed/20260809_elaborator-breadth/diff-ledger.md` (37 paths; referenced by path, not
  restated)
- **Shared elaborator authority:** `.project/active/elaborator-design/spec.md` and
  `.project/active/elaborator-design/design.md`
- **Cutover research:**
  `.project/research/20260809-153245_item6-identity-completion-and-cutover-census.md` and
  `.project/research/20260807-145336_elaborate-first-instance-graph-architecture.md`
- **Certified prerequisite:**
  `.project/completed/20260810_elaborator-identity-completion/spec.md`, `design.md`, `plan.md`, and
  `audit_v3.md`
- **Spec review:** `.project/active/elaborator-cutover/spec-review.md`
- **Product lens:** `.project/active/elaborator-cutover/product-lens.md`
- **Required design census:** `.project/active/elaborator-cutover/cutover-census.md` (to be created)
- **Design:** `.project/active/elaborator-cutover/design.md` (to be created)

---

**Next Steps:** Rerun `$my-spec-review`. After a clean review and owner approval of this spec,
proceed to `$my-design`. Product design remains skipped for the rationale above. The recapture owner
checkpoint is a later Item-7 completion/merge gate and remains pending.
