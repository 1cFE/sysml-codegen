# Epic: Elaborate First — Instance-Graph Front End

**Epic ID**: ELABORATE-FIRST
**Status**: Ready (direction ratified by owner 2026-08-07; supersedes SOURCE-IDENTITY Items 4–5)
**Priority**: Critical (P0 — same defect family as SOURCE-IDENTITY)
**Created**: 2026-08-07
**Estimated Effort**: 3–4 weeks (re-estimate after the Item-3 go/no-go spike)

---

## Executive Summary

The library never performs SysML elaboration — expanding usages into a concrete occurrence
tree, applying `:>>` redefinitions innermost-wins, and resolving every binding referent to a
node while the AST is in hand. Instead it flattens declarations to name strings and then
simulates elaboration in six accreted layers (~3,450 lines) that guess identity back out of
strings. The customer fan-out defect is that composition working as built.

This epic replaces the front end with elaborate-then-project: one elaboration pass produces an
instance graph (the single IR and the snapshot payload), and a mechanical projection emits the
existing `ComputationGraph`, leaving generation untouched. Source identity then holds by
construction — several consumers of one modeled value are several edges to one node — and the
simulation layers are deleted, not wrapped.

**Delivery philosophy (owner directive, 2026-08-07):** *"plenty of spikes and learning tests so
we fail fast."* Every item that carries architectural risk starts with a spike or learning-test
leg whose failure is cheap, whose findings are kept, and whose kill criteria are written down
before the work starts. No phase commits expensive, hard-to-unwind work (snapshot formats,
corpus recaptures, deletions) before the representation it depends on is proven load-bearing.

**Critical Success Factor** (inherited, owner grade — SOURCE-IDENTITY mission invariant): every
consumed modeled value resolves to exactly one runtime source across all bound consumers; an
unsupported authored form fails loudly before generation.

---

## Source Documents

- **[research]** [The simpler design: elaborate first, project second](../research/20260807-145336_elaborate-first-instance-graph-architecture.md)
  — the ratified direction: diagnosis, deletion inventory, seam verification, hard-shape
  pressure test, SysIDE capability survey.
- **[research]** [Recovery assessment after Item 4 phases 1–2](../research/20260807-143615_source-identity-recovery-assessment.md)
  — why the Item-4 shadow-layer architecture was stopped; salvage classification; the process
  failure analysis this epic's rules answer.
- **[INHERITED: SOURCE-IDENTITY Items 1–3]** The binding-semantics spike, route-evidence spike,
  and the ratified source-identity contract (29-cell acceptance matrix, dispositions D-4..D-19,
  invariants 19/20/22/26 + 54–60). **These remain the semantic authority.** This epic changes
  the architecture that implements the contract, not the contract.
- **[research]** Both 2026-08-03 forensic reports (defect mechanism and blast radius).

## Relationship to SOURCE-IDENTITY

- Items 1–3 (evidence and contract): complete, inherited unchanged.
- Items 4–5 (occurrence foundation, resolution cutover): **superseded** — their approved
  design built a parallel identity ledger the resolver ignored by design. Item 1 below records
  the supersession in that epic and preserves the dirty tree forensically.
- Items 6–8 (corpus migration, downstream remediation, certification): intent absorbed into
  Items 6–7 below; their deliverables are unchanged, and the dual-run diff ledger from Item 5
  produces Item 6's semantic-diff ledger as a migration byproduct.

## Owner-originated rulings carried forward

- **[OWNER-VERBATIM]** "Never reinterpret a self-binding as an outer reference."
  (2026-08-05, SOURCE-IDENTITY D-3.) Under this architecture: `in R = R` fails with a hard
  diagnostic at elaboration. No rescue code exists.
- **[OWNER]** (2026-08-07) `in R = R` is a modeling bug; we do not work around bad modeling.
- **[OWNER]** (2026-08-07) Resolved referents are available when the model is loaded; the
  architecture must use them then, not reconstruct them later.
- **[OWNER]** (2026-08-07) Snapshots are a serialization-format choice; the format is whatever
  representation the pipeline actually needs — here, the instance graph.
- **[OWNER-VERBATIM]** "we MUST document allowable patterns in our `agentic-mbse` docs as
  well…" (2026-08-05.) Item 7 keeps this obligation.

---

## Success Criteria

- [ ] **[OWNER] Mission invariant** (inherited): one semantic source occurrence → exactly one
  runtime source across all calculation, constraint, and aggregation consumers; public mutation
  reaches every and only the bound consumers; unsupported forms fail loudly pre-generation.
- [ ] **[AGENT] Fail-fast gate:** every risk-bearing item opens with a spike or learning-test
  leg with written kill criteria; a failed spike stops the epic for redesign at spike cost, not
  after production landings.
- [ ] **[AGENT] Product-behavior gates:** every item's completion gate is an observable public
  behavior (a mutation that propagates, a diagnostic that fires, a diff that is empty or
  classified) — never artifact-to-artifact fidelity.
- [ ] **[AGENT] One-authority gate:** no item completes with old and new front ends both live.
  The dual-run harness is internal scaffolding only and is deleted in the cutover landing.
- [ ] **[AGENT] Deletion ledger:** the cutover lands the research report's deletion inventory
  (VBR + rescue, virtual-usage expansion, aggregation QN-surgery, backtracker ladder,
  21-key-form table, supplied-value materializer, registry namespaces, value backfill, and
  their wrong-oracle tests). New mechanisms name what they delete.
- [ ] The 29-cell Item-3 acceptance matrix passes at the public boundary on live and
  relocated-snapshot routes; the C19 nested-occurrence fixture applies 80.0 on both consumer
  paths; the exact customer composition proves one input with mutation reaching all consumers.
- [ ] Snapshot format = serialized instance graph, version-bumped fail-closed, all 37 fixtures
  recaptured exactly once, in the same landing as the cutover.
- [ ] Downstream packages, studies, certification record, and `agentic-mbse` modeling guidance
  corrected (absorbed SOURCE-IDENTITY 6–8 intent).

## Non-Goals

- Threading a source-identity reference through the existing string resolver (the recovery
  report's interim variant). Decision record: rejected 2026-08-07 because it retains the
  ladder/registry skeleton the diagnosis identifies as the defect's home.
- Preserving the Item-4 manifest/authority/recorder layer (`analysis/source_identity.py`).
  Salvage is limited to extraction evidence, index queries, fixtures, and red tests.
- Non-finite multiplicity support. Expand-finite or block-loud remains the full disposition.
- New study features, model physics, or the two queued `agentic-mbse pm` CLI defects.

---

## Epic Strategy

**[AGENT] (ratified by owner, 2026-08-07)** unless marked otherwise.

The order is: freeze → salvage → **spike (go/no-go)** → **learning tests + dual-run breadth** →
one atomic cutover → downstream. Two structural choices carry the risk management:

1. **The `ComputationGraph` seam is the migration instrument.** Generation verifiably consumes
   only the populated graph, so old-vs-new front ends produce diffable objects. Breadth is
   "make the diff empty except where the contract says it must change."
2. **Expensive irreversibles come last and land atomically.** Cutover, deletion, snapshot
   version bump, and the single 37-fixture recapture are one landing unit (old snapshots
   cannot feed the new front end — they serialize post-VBR bindings without referent facts —
   so these cannot be separated without a dead offline route).

Process rules (correcting the recorded failure mode where artifact consistency substituted for
the product invariant):

- Gates are product behaviors at the public boundary.
- Spike/learning-test findings are kept artifacts; failed probes are findings, not waste.
- Artifacts are sized to the decision they carry: one spec/design pair for the elaborator +
  projection, findings docs for spikes. The 29-cell matrix is inherited, never restated.
- Owner checkpoints: after the Item-3 spike (go/no-go), on the Item-5 classified diff ledger
  (pre-cutover), and on the Item-6 recapture review.

---

## Backlog Items

#### Item 1: Forensic Freeze and Epic Transition (0.5 day)

**Type**: Housekeeping / Decision record

**Objective**: Preserve the stopped Item-4 work recoverably and make this epic the single
active plan, with no competing authority left ambiguous.

**Scope**:
1. Safety-branch both repos' dirty trees (`item4-phases12-forensic`), recording the known
   breakage in the commit message: `feature_chain_facts` returns 5 values while
   `agentic_mbse/sysml/aggregation.py:249,405` unpack 4 (licensed aggregation extraction
   raises).
2. Amend `epic_semantic_source_identity.md`: Items 4–5 superseded (pointer to both research
   reports and this epic), Items 1–3 inherited, Items 6–8 absorbed. Amend, don't accrete.
3. Update `CURRENT_WORK.md` and the SOURCE-IDENTITY active-item artifacts to point here.

**Success Criteria**:
- [ ] Both dirty trees recoverable from named branches; working branches clean at base.
- [ ] Exactly one epic reads as active for this defect family.

**Dependencies**: None.

---

#### Item 2: Salvage Landing (0.5–1 day) — ✅ Complete 2026-08-07

**Landed**: codegen `66a61f3` (on `source-identity-epic`) + agentic-mbse `65a35d7` (on
`elaborate-first-salvage`; merge decision with owner). Gates: codegen full licensed suite
3153/47/18 with zero license-skip lines, ruff clean, mypy at the 72-error baseline, committed
baselines byte-identical; agentic-mbse 1811/1/33. The forensic arity bug is fixed (both
aggregation callers unpack the 5-tuple), chain root/member evidence is threaded to terms instead
of dropped, and `redefining_target_on` is query-order independent (new unit pin).

**Type**: Code (additive, behavior-neutral)

**Objective**: Land the elaborator's *inputs* from the stopped work as one green, reviewed
commit. Nothing user-visible changes.

**Scope**:
1. `agentic-mbse`: `ResolvedTargetFact`; the 5-tuple `feature_chain_facts` **with both
   aggregation callers fixed** and field-contract tests updated.
2. codegen: `extraction/source_evidence.py`; the `PartInstanceIndex` extensions (drop or
   redesign the query-order-dependent `redefining_target_on` internal-map coupling,
   `analysis/part_instance_index.py:333-339` — a reverse query must not depend on earlier
   query order); the four new fixture directories; the red tests re-labeled as falsifiers
   (xfail pins the new front end must flip).
3. Explicitly excluded: `analysis/source_identity.py` and every manifest/recorder/coordinate
   test. Record the exclusion as one decision line, not a prohibition essay.

**Success Criteria**:
- [x] Full maintained suites green in both repos (licensed leg included — source the env per
  the capture protocol).
- [x] Zero behavior change: generated outputs byte-identical for the committed corpus (suite
  baseline/snapshot gates green).

**Dependencies**: Item 1.

---

#### Item 3: Elaborator Spike — Go/No-Go (2–3 days)

**Type**: **Spike** (via `/_my_spike`; findings doc, no production merge)

**Objective**: Prove or kill the architecture at spike cost. Build a prototype
`elaborate(model) -> InstanceGraph` plus a thin projection to `ComputationGraph`, on exactly
three fixtures chosen to burn the three biggest unknowns.

**Scope** — each leg is a probe with kept findings:
1. **Customer shape**: fan-out collapse; def-level referent (`'Plant'::R`) contextualized to
   the consumer's enclosing occurrence; `in R = R` produces the hard diagnostic.
2. **`nested_occurrence_override_probe` (C19)**: innermost-wins override application during
   elaboration; both calc and constraint consumers read the node holding 80.0.
3. **Aggregation shape** (fusion_tea subset or equivalent): fold over
   `occurrences_of(child_def)` under the parent occurrence; per-child `:>>` values; a
   cross-part term as an edge to a sibling-subtree node.
4. **Node-ID probe**: confirm `InstanceOccurrence.instance_path` works as the stable node ID;
   record its behavior under the model edits we care about (positional indexed occurrences).

**Kill criteria (written before work starts)**: any of — (a) SysIDE cannot supply a fact the
elaborator needs at a probe site (contradicting the capability survey); (b) def-referent
contextualization requires consumer-specific special-casing rather than one rule; (c) the
projection cannot produce a valid `ComputationGraph` the existing generation layer accepts
unchanged. A kill stops the epic for redesign — that outcome is a success of the process, and
the findings are the deliverable either way.

**Success Criteria**:
- [ ] All three fixtures pass their product-behavior checks from the projected graph, with
  generation untouched.
- [ ] Kept findings + kill-criteria verdicts; owner go/no-go checkpoint recorded.

**Location**: `.project/active/elaborator-spike/`

**Dependencies**: Item 2.

---

#### Item 4: Elaborator + Projection Design (1–1.5 days)

**Type**: Specification / Design

**Objective**: One right-sized spec/design pair for the production elaborator and projection,
written *after* the spike so it records proven mechanics, not speculation.

**Scope**:
1. `InstanceGraph` node/edge model; node-ID scheme (from the Item-3 probe); the single
   def-referent contextualization rule; diagnostic catalog for rejected forms (from the Item-3
   contract's dispositions).
2. Projection contract: everything the seam verification requires — `modules`,
   `entry_point_groups`, `execution_order`, `output_aliases`, attached `constraint_catalog`;
   `fallback_entry_points` retired (no fallback minting exists) with the V11 boundary check
   retained as an invariant; names rendered via the existing `core/qualified_names.py`
   helpers (ADR-003 unchanged).
3. Deletion ledger (from the research report's inventory) attached to the design as the
   cutover's checklist.
4. Decision: elaborator lives in codegen for this epic (consuming `agentic-mbse` facts);
   any ownership move is explicitly deferred.
5. Named open ruling for the owner: multi-occurrence definition-default — one shared public
   input vs one per occurrence. The elaborator forces this choice explicitly; it must not be
   resolved silently.

**Success Criteria**:
- [ ] Design names the exact types/functions it replaces and deletes; introduces no manifest,
  transcript, or second authority.
- [ ] The multi-occurrence default ruling is dispositioned by the owner and recorded in the
  Item-3 contract's register (grade preserved).

**Dependencies**: Item 3 go.

---

#### Item 5: Shape Learning Tests and Dual-Run Breadth (1–2 weeks)

**Type**: Code / **Learning tests** / Integration

**Objective**: Grow the elaborator across every supported shape, with each risky shape probed
by a learning test *before* its implementation, and prove breadth mechanically via an
old-vs-new `ComputationGraph` diff over the whole corpus.

**Scope**:
1. **Per-shape learning tests first** (each a small kept test that pins current behavior and
   states the expected new behavior; failure of an expectation is a cheap early signal):
   cross-package / multi-hop EXPOSE; sibling same-name channels; multiplicity expansion
   (`[3]`, indexed paths); specialization + usage-level retypes (two-level); FORMULA computed
   attributes including the previously unsupported FORMULA→FORMULA edge; constraint catalog
   assembly through projection; independent equal-valued literals staying distinct;
   the shadowing/specialization referent fixtures the capability survey flagged as missing
   evidence.
2. **Snapshot round-trip learning test**: serialize the instance graph → rebuild → project;
   parity with the live projection on the same fixtures. This de-risks the Item-6 format
   before anything is versioned or recaptured.
3. **Dual-run harness**: internal parallel entry point (never a shipped flag) + one diff tool
   comparing old-vs-new graphs per fixture (modules, channels, wiring, entry-point sets).
   Every diff classified: *expected-collapse* (the 75 per-consumer mints), *expected-fix*
   (C19), *needs-review*, *new-bug*. Zero unclassified diffs at item close.
4. **Coverage checklist = the inherited 29-cell matrix.** Breadth is done when every supported
   cell passes on the new path and every rejected cell fails with its named diagnostic. No new
   completeness standard is invented.

**Stop condition**: a shape whose learning test reveals a semantics question the Item-3
contract does not answer → surface to owner; do not disposition silently.

**Success Criteria**:
- [ ] Every learning test kept, with findings; every matrix cell green-or-named-diagnostic on
  the new path.
- [ ] Classified diff ledger over all 37 fixtures with zero unclassified rows — **owner
  checkpoint on the ledger before Item 6 starts.**
- [ ] Old front end untouched and still authoritative for shipped behavior (both suites green
  throughout).

**Location**: `.project/active/elaborator-breadth/`

**Dependencies**: Item 4.

---

#### Item 6: Atomic Cutover — Switch, Delete, Snapshot, Recapture (3–5 days)

**Type**: Code / Integration (one landing unit)

**Objective**: Make the instance-graph front end the only front end. These four moves are one
atomic landing because old snapshots cannot feed the new front end.

**Scope**:
1. `build_pipeline_context` switches to elaborate-then-project.
2. Execute the deletion ledger: VBR + specialized-chain rewrite + self-named rescue,
   virtual-usage expansion, aggregation scope re-derivation, the backtracker resolution
   ladder (DFS edge discovery re-sourced from the graph; toposort kept), the 21-key-form
   producer table, the supplied-value materializer, the OutputRegistry namespaces, the
   group-deriver value backfill — and their wrong-oracle tests, replaced by the Item-5
   independently anchored tests.
3. Snapshot payload = serialized instance graph; `snapshot_format_version` bump, fail-closed
   old versions; capture and `graph_rebuild` updated together; **one** recapture of all 37
   fixtures (timestamp-churn diff protocol so only real changes show), reviewed against the
   Item-5 ledger.
4. Delete the dual-run harness and parallel entry point in the same landing.

**Success Criteria**:
- [ ] Customer composition: one public input, off-default mutation reaching every bound
  consumer, proven live **and** relocated-snapshot.
- [ ] C19 fixture applies 80.0 on both consumer paths; tripwire deleted with its mechanism.
- [ ] Deletion ledger fully executed; no superseded route remains behind a flag or adapter.
- [ ] Full maintained unit/conformance/generation/type/lint gates green with exact counts and
  license evidence recorded; every committed output change appears in the classified ledger.

**Location**: `.project/active/elaborator-cutover/`

**Dependencies**: Item 5 ledger checkpoint.

---

#### Item 7: Downstream Remediation and Certification (3–5 days)

**Type**: Integration / Documentation (absorbed SOURCE-IDENTITY Items 6–8 intent)

**Objective**: Move real consumers, studies, guidance, and the assurance record onto the
corrected architecture.

**Scope**:
1. Regenerate Fusion Tea and Stellarator packages/contracts; remove duplicate-field
   workarounds; new study lineage where identity changed; TEAx compatibility through stock
   APIs.
2. July IFE impact audit: rerun or explicitly correct decision-relevant outputs that consumed
   frozen-design-point cost values.
3. Certification repair: verification matrix gains an independently anchored source-identity
   family with public mutation evidence; contradictory acceptance claims corrected; README and
   architecture references (docs 11/12/13/16/24/25 rewritten or retired to match the new front
   end) state the library's purpose plainly.
4. **[OWNER-VERBATIM obligation]** publish the allowable-modeling-pattern guidance in
   `agentic-mbse` docs, including the `in R = R` diagnostic and its two valid replacement
   forms with their distinct meanings.
5. One composed model→package→study proof thread as the epic's closing evidence.

**Success Criteria**:
- [ ] Downstream packages regenerate/seal/execute with corrected topology and no identity
  workarounds; IFE impact report names every affected consumer with rerun/correction status.
- [ ] Certification and guidance obligations from the Item-3 contract discharged.

**Location**: `.project/active/elaborator-downstream/`

**Dependencies**: Item 6.

---

## Risks

- **Item-3 spike fails** → the epic stops at spike cost; the fallback is the recovery report's
  incremental vertical repair, which remains documented and unchosen, not destroyed.
- **Breadth long tail** (Item 5) → bounded by the inherited 29-cell matrix and the
  zero-unclassified-diffs rule; a shape outside the matrix is an owner question, not silent
  scope growth.
- **Coexistence temptation** → the harness is internal-only and its deletion is inside the
  Item-6 landing's success criteria.
- **Recapture churn** → single recapture, after the round-trip learning test, reviewed against
  the classified ledger; the timestamp-churn protocol isolates real changes.
