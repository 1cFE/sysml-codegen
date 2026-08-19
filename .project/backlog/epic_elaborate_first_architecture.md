# Epic: Elaborate First — Instance-Graph Front End

**Epic ID**: ELABORATE-FIRST
**Status**: Ready (direction ratified by owner 2026-08-07; supersedes SOURCE-IDENTITY Items 4–5)
**Priority**: Critical (P0 — same defect family as SOURCE-IDENTITY)
**Created**: 2026-08-07
**Estimated Effort**: 4–5 weeks (re-estimated 2026-08-09 after inserting identity completion)

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
  Items 7–8 below; their deliverables are unchanged, and the dual-run diff ledger from Item 5
  produces Item 7's semantic-diff ledger as a migration byproduct.

## Owner-originated rulings carried forward

- **[OWNER-VERBATIM]** "Never reinterpret a self-binding as an outer reference."
  (2026-08-05, SOURCE-IDENTITY D-3.) Under this architecture: `in R = R` fails with a hard
  diagnostic at elaboration. No rescue code exists.
- **[OWNER]** (2026-08-07) `in R = R` is a modeling bug; we do not work around bad modeling.
- **[OWNER]** (2026-08-07) Resolved referents are available when the model is loaded; the
  architecture must use them then, not reconstruct them later.
- **[OWNER]** (2026-08-07) Snapshots are a serialization-format choice; the format is whatever
  representation the pipeline actually needs — here, the instance graph.
- **[OWNER-VERBATIM]** (2026-08-15, restating and superseding the 2026-08-05 wording, which
  the owner ruled was taken out of context) "all I care about is: We know what the RIGHT
  pattern(s) are for the given situation / We document those right patterns / We fix the models
  to use the right patterns. `in R = R` is the wrong pattern. I would like to detect the use of
  it so we avoid it in the future. that's it, that's all I care about."
  Item 8 keeps this obligation. The earlier 2026-08-05 quote ("we MUST document allowable
  patterns in our `agentic-mbse` docs as well…") is the same obligation in its original wording;
  it carries no count of replacement forms.

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
exact-identity completion → one atomic cutover → downstream. Two structural choices carry the
risk management:

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
  (pre-cutover), and on the Item-7 recapture review.

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

#### Item 3: Elaborator Spike — Go/No-Go (2–3 days) — spike executed 2026-08-07; owner checkpoint PENDING

**Spike result**: assumption CONFIRMED, no kill criterion triggered —
[findings](../active/elaborator-spike/findings.md). A 381-line prototype passed all product
checks: C25 customer collapse to one input (proven in real generated YAML), C8 twins distinct,
C24 producer edge, **C19 80.0 applied on both calc and constraint paths** (the def-context remap
rule is the fix), `in gain = gain` → hard `SI_SELF_BINDING`, Bank aggregation terms on
`cell[i]` nodes, stable node IDs, and `generate_pipeline_yaml`/`generate_registry` accepting the
projected graph unchanged. **[AGENT] recommendation: GO.** The go/no-go decision itself is the
owner's.

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
- [x] All three fixtures pass their product-behavior checks from the projected graph, with
  generation untouched (2026-08-07; probes 1–4 in `.project/active/elaborator-spike/`).
- [x] Kept findings + kill-criteria verdicts done; **owner go/no-go: GO**
  (**[OWNER-VERBATIM]** 2026-08-07: "hell yeah. clean this fucker up.").

**Location**: `.project/active/elaborator-spike/`

**Dependencies**: Item 2.

---

#### Item 4: Elaborator + Projection Design (1–1.5 days) — ✅ spec/design landed 2026-08-07

**Landed**: `.project/active/elaborator-design/spec.md` + `design.md` (post-spike, mechanics
proven). Key decisions: elaborator walks calc/constraint usages off the AST itself (the spike's
extractor-consuming shortcut rejected — it would keep the legacy expansion alive); one
def-context remap rule anchors overrides AND places def-declared consumers (the C19 fix); value
tiers innermost-wins with value-site driving EP classification (backfill has no role);
EXPRESSION redefinitions become computed nodes (folds the `attr_resolution_map` path);
`constraint_lowering` adapted to read node edges; deletion ledger attached. The
multi-occurrence-default ruling needed no new checkpoint — the contract's ratified 2026-08-05
rule (distinct occurrences remain distinct sources; C23) is cited as the authority.

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
- [x] Design names the exact types/functions it replaces and deletes; introduces no manifest,
  transcript, or second authority.
- [x] The multi-occurrence default ruling is dispositioned — already in the Item-3 contract
  (**[AGENT] ratified by owner 2026-08-05**: equal inherited defaults on distinct concrete
  occurrences remain distinct sources; one overridable default per concrete calc usage, C23).
  Cited, not re-decided; no register change needed.

**Dependencies**: Item 3 go.

---

#### Item 5: Shape Learning Tests and Dual-Run Breadth (1–2 weeks) ✅

**Type**: Code / **Learning tests** / Integration

**Current:** CERTIFIED 2026-08-09 (`active/elaborator-breadth/audit_v3.md` addendum; targeted
re-verification of the audit-v3 remediation, all gates live-reproduced). All 29 cells execute
without xfails at their public or named-
diagnostic boundary. All 37 fixtures have live-checked route outcomes, classified as 26
`expected-collapse` and 11 `expected-fix` with zero unresolved rows. F20's rendered-path string
selector is removed. The corrected owner-ratified F21 ruling keeps DCS:92 as C5 referent evidence
and `elab_matrix_c5` as public acceptance, and supports DCS:82 on the repaired valid witness: one
exact core producer projects to the consumer. The former plain same-name nested part shape now
fails `SYSML_NAMESPACE_NOT_DISTINGUISHABLE` before occurrence expansion. The shipped legacy route
and snapshot v5 remain unchanged. Item 5 criteria are checked per the audit; audit-F30/F31 remain
open disposed (non-blocking); Item 6 implementation has not started and needs the owner's go.

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
   parity with the live projection on the same fixtures. This de-risks the Item-7 format
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
- [x] Every learning test kept, with findings; every matrix cell green-or-named-diagnostic on
  the new path.
- [x] Classified diff ledger over all 37 fixtures with zero unclassified rows — **owner
  checkpoint on the ledger before Item 6 starts.**
- [x] Old front end untouched and still authoritative for shipped behavior (both suites green
  throughout).

**Location**: `.project/completed/20260809_elaborator-breadth/` (closed 2026-08-09)

**Dependencies**: Item 4.

---

#### Item 6: Exact-Identity Completion — Payload, Occurrence, Projection (3–5 days) ✅

**Type**: Code / Integration (new route only; shipped authority unchanged)

**Authority**: **[OWNER]** Insert a separate work item before cutover (2026-08-09).
The estimate, objective, scope, and gates below are **[AGENT] (ratified by owner 2026-08-09)**.

**Current:** All five implementation phases completed 2026-08-09. Exact payload attachment,
native effective-child selection, concrete occurrence identity, structured graph v2, one-way
projection, the complete boundary guard, runtime-cell public mutation, and the 29-cell/37-fixture
gates are implemented. The neutral constraint schema, shipped legacy route, snapshot v5, and
generated baselines remain unchanged. **Independent full-item audit 2026-08-09
(`completed/20260810_elaborator-identity-completion/audit_v3.md`): Needs Work (narrow).** audit-F1..F6 fixes
verified; all recorded gates reproduced. Blocking: audit-F7 — the exact route generates an
executable module for a `BLOCK`-eligibility constraint where the legacy route halts by name
(reproduced live on `elab_payload_identity`). Dispositions owed: audit-F8 (the four transitional
dual mechanisms must be named in Item 7's deletion ledger; identity-keyed fact pairing) and
audit-F9 (F30 guard is allowlist-scoped, or narrow SC5's wording). **Implementation response
2026-08-10:** audit-F7 now emits `SI_CONSTRAINT_BLOCKED`; strict elaboration and every projection
halt while lenient inspection retains the typed node and named reason. audit-F8's live facts are
paired by exact usage UUID, and the four transitional duals are in Item 7's deletion ledger.
audit-F9's guard now scans every boundary function by default with five narrow, exercised
wire/rendering exemptions; SC5 was not narrowed. **CERTIFIED 2026-08-10 by targeted independent
re-audit** (`completed/20260810_elaborator-identity-completion/audit_v3.md` addendum): all three fixes
verified live (F7 falsifier halts on strict/lenient/round-trip routes; F8 identity-keyed pairing +
ledger entry confirmed; F9 deny-by-default guard with pinned unlisted-function falsifier), full
gates reproduced (codegen 3,358/47/18, agentic 1,819/1/33, corpus 37/37, freeze intact),
product-lens gate CLEAR. Item 7 is unblocked.

**Objective**: Close the remaining exact-identity gaps before the new front end can become the
shipped authority. Exact graph edges are already proven; this item makes executable payload
attachment, occurrence child selection, graph structure, and projection obey the same invariant.

**Required Reading**:
- `.project/research/20260809-153245_item6-identity-completion-and-cutover-census.md`
- `.project/active/spike-syside-occurrence-authority/findings.md`
- `.project/active/elaborator-design/spec.md`
- `.project/active/elaborator-design/design.md`

**Scope**:
1. Carry exact declaration identity through calculation-definition, input/output-port,
   compilation, and constraint-profile payloads. Missing, duplicate, or mismatched executable
   payload blocks by a named diagnostic; it never defaults by QN or member name.
2. Consume SysIDE's effective `Usage.usages` declaration view, while codegen retains supported
   containment filtering, finite multiplicity expansion, parent/index context, and cycle handling.
   Remove traversal-order fallbacks and disposition the F31 plural branches with a kept witness.
3. Make the instance graph carry the structured occurrences and neutral expression/predicate
   information projection needs. Projection derives ownership, aliases, and execution order from
   typed graph structure and never reconstructs them from rendered strings. Extend F30's guard over
   the complete resolution/projection boundary.
4. Re-run the 29-cell and 37-fixture exact-route gates. The legacy shipped route and v5 snapshot
   remain frozen; this item does not switch authority, recapture the corpus, or execute the deletion
   ledger.

**Success Criteria**:
- [x] QN, member-name, display-path, and iteration-order perturbations cannot change executable
  payload attachment, constraint eligibility, occurrence selection, or projected dependencies.
- [x] Every required calc/port/compilation/constraint payload has one exact declaration association;
  missing, duplicate, invalid-vocabulary, and anonymous cases have explicit tested outcomes.
- [x] SysIDE owns effective child declarations and codegen owns only concrete expansion/context,
  proven on inheritance, retyping, multiplicity, and explicit/implied redefinition fixtures.
- [x] Projection is one-way over a validated structured graph; F30 protects the whole boundary and
  F31 has a kept valid-model disposition.
- [x] All 29 cells and 37 corpus rows remain green-or-named-diagnostic with zero unclassified diffs;
  shipped legacy output and v5 snapshot bytes remain unchanged.
- [x] Every supported runtime-source cell proves off-default propagation to every and only its
  bound consumers through the internal exact route's public projection; Item 7 retains the final
  shipped live-and-relocated-snapshot proof.

**Location**: `.project/completed/20260810_elaborator-identity-completion/` (closed 2026-08-10)

**Dependencies**: Item 5 ledger checkpoint.

---

#### Item 7: Atomic Cutover — Switch, Delete, Snapshot, Recapture (3–5 days) ✅

**Type**: Code / Integration (one landing unit)

**Objective**: Make the instance-graph front end the only front end. These four moves are one
atomic landing because old snapshots cannot feed the new front end.

**Scope**:
1. Define the complete instance-graph snapshot envelope, then switch `build_pipeline_context` to
   elaborate-then-project. Capture, live load, relocated load, and projection share one graph
   authority; old and unknown snapshot versions fail before projection.
2. Execute the deletion ledger: VBR + specialized-chain rewrite + self-named rescue,
   virtual-usage expansion, aggregation scope re-derivation, the backtracker resolution
   ladder (DFS edge discovery re-sourced from the graph; toposort kept), the 21-key-form
   producer table, the supplied-value materializer, the OutputRegistry namespaces, the
   group-deriver value backfill — and their wrong-oracle tests, replaced by the Item-5
   independently anchored tests. **[AGENT] (audit_v3 disposition, 2026-08-10)** Converge the four
   Item-6 transitional duals in the same landing: fold `extract_identified_constraint_facts` into
   one live constraint-fact extraction pass; make exact-ID profile evaluation the sole codegen path
   and remove the QN adapter when its non-codegen callers are disposed; promote
   `compile_calc_def_exact` to the single compiler core and delete the parallel name-keyed walk;
   remove the paired name-keyed calculation payload maps and live ID sidecars when snapshot v5 and
   its legacy route are deleted.
3. Snapshot payload = serialized instance graph; `snapshot_format_version` bump, fail-closed
   old versions; capture and `graph_rebuild` updated together; **one** recapture of all 37
   fixtures (timestamp-churn diff protocol so only real changes show), reviewed against the
   Item-5 ledger.
4. Delete the dual-run harness and parallel entry point in the same landing.

**Success Criteria**:
- [x] Customer composition: one public input, off-default mutation reaching every bound
  consumer, proven live **and** relocated-snapshot.
- [x] C19 fixture applies 80.0 on both consumer paths; tripwire deleted with its mechanism.
- [x] Deletion ledger fully executed; no superseded route remains behind a flag or adapter.
- [x] A recorded scale budget and one real TEAx generation/seal/execute smoke pass on the new
  authority without private compatibility APIs.
- [x] Full maintained unit/conformance/generation/type/lint gates green with exact counts and
  license evidence recorded; every committed output change appears in the classified ledger.

Ticked at close 2026-08-14 on the step-10 record: narrow-correction steps 1–10 executed, step-9
independent audit CERTIFY-WITH-RESIDUALS (0 blocking), **[OWNER 2026-08-14] final acceptance**
at Gate 3 (three consecutive batteries, 51/51 fields identical, at codegen `2819501` / agentic
`6372ef7` / TEAx `75eecb3`).

**Location**: `.project/completed/20260814_cutover-recovery/` (execution + acceptance record)
and `.project/completed/20260814_elaborator-cutover/` (spec, design, census — superseded plan
retained as shaping evidence). The deletion ledger lives on as live gate data at
`.project/ledger/ledger-4a.{json,md}` (moved at close; checker constants repointed).

**Dependencies**: Item 6.

---

#### Item 8: Downstream Remediation and Certification (3–5 days)

**Type**: Integration / Documentation (absorbed SOURCE-IDENTITY Items 6–8 intent)

**Objective**: Move real consumers, studies, guidance, and the assurance record onto the
corrected architecture.

**[OWNER 2026-08-16] Item boundary:** regeneration/proof, the July impact audit, and
certification/documentation repair remain one work item. They may be phased but do not split into
separate completion authorities. Source: `.project/active/elaborator-downstream/spec-review.md`, Resolution
L2-1.

**Scope**:
1. Converge the codegen fixture and migrated Fusion Tea customer model by deleting the fixture's
   inert `hif_driver_instance` workaround; regenerate the customer package/contracts; start a new,
   linked study lineage where identity changed; and prove TEAx compatibility through stock APIs.
   **[AGENT] (ratified by owner, 2026-08-16):** Stellarator migration is excluded. The completed
   read-only triage plus separately filed P2 `[STELLARATOR-D5-MIGRATION]` discharges this item's
   Stellarator boundary without reversing the July hold. Source:
   `.project/active/elaborator-downstream/spec-review.md`, Resolutions L1-1/L1-2 and L2-2.
2. July IFE impact audit: rerun or explicitly correct decision-relevant outputs affected by frozen
   design-point values, including cost/LCOE and recirculation.
3. Certification repair: the verification matrix gains an independently anchored `REQ-SI` family
   derived from the durable Item-3 authority and backed by public mutation evidence; contradictory
   acceptance claims are corrected; README states the library's purpose plainly. The reconciled
   authorship pass covers reference documents 03, 04, 05, 07, 09, 10, 11, 12, 13, 16, 17, 18, 24,
   and 28. Document 25 is retained as a test-only, off-shipped-route legacy surface.

   *Provenance correction 2026-08-16:* this sub-item previously named documents 11, 12, 13, 16, 24,
   and 25 as one rewrite-or-retire set. The bounded Item 8 stocktake found that nine actual repair
   candidates were omitted and document 25 belonged to a separate owner-disposition class. The
   reconciled fourteen-document list comes from
   `.project/research/20260815-103905_item8-bounded-stocktake.md`; the owner ratified the correction and the
   agent recommendation to retain document 25 on 2026-08-16. The old six-document list is not
   authority for downstream scope.
4. **[OWNER-VERBATIM obligation]** (restated by the owner 2026-08-15) establish which authoring
   pattern is the right one for each situation, document those patterns in `agentic-mbse` docs,
   and fix the models to use them. `in R = R` is the wrong pattern and its use is detected.
   *Provenance correction 2026-08-15:* this sub-item previously read "publish the
   allowable-modeling-pattern guidance … including the `in R = R` diagnostic and its **two**
   valid replacement forms with their distinct meanings." No owner utterance enumerating two
   forms exists; the count was agent-authored under an owner-verbatim stamp, and the owner ruled
   the 2026-08-05 wording it derived from was taken out of context. Nothing downstream should
   treat a form count as owner-given. Item 8 also reconciles the full Item-3 guidance projection,
   including the valid-but-unsupported indexed-expression limitation and accurate example force.
5. One composed model→package→study proof thread as the epic's closing evidence.

**Success Criteria**:
- [ ] The converged Fusion Tea fixture and migrated customer package regenerate/seal/execute with
  one corrected topology and no identity workarounds; the IFE impact report names every affected consumer with
  rerun/correction/bounded-unknown status. Stellarator's completed triage and separate P2 filing
  satisfy the ratified boundary above; its migration is not an Item 8 completion gate.
- [ ] Certification and guidance obligations from the Item-3 contract discharged.

**Location**: `.project/active/elaborator-downstream/`

**Dependencies**: Item 7 complete; `self-binding-replacement` closed on 2026-08-16 with all
functional criteria independently verified and its testing/developer-tooling edge accepted as risk
by the owner. **[AGENT] (ratified by owner, 2026-08-16):** `stop-reinventing-the-parser` is
implemented, audited, and closed before Item 8 downstream design or implementation; downstream
performs none of either predecessor's remediation. Source: the active item's `spec-review.md` L4-1
and the owner's direction to apply the review fixes.

**Bounded predecessor active — Phase 5 implemented, independent audit pending 2026-08-18:**
`.project/active/stop-reinventing-the-parser/` owns exact occurrence derivation and evidence
integrity. It closes before `.project/active/elaborator-downstream/` starts so downstream
regeneration and certification measure the final semantic-authority rules.

The immutable chain is now `A_final` `3f8bd587af40f05b929dd56645901dada7daea37`, `C_prod`
`707346d616e508e55103c9246b63d172ed6a862b`, `F_final`
`2243b7ce116c0a12fb0c09a81262c5c2ec879f69`, and direct-child `C_evidence`
`a184133b99f7f71451c0b4af5a33b709f988eca2`. The committed runner executed 21 isolated lanes from
recorded archives and wheels; the Codegen default lane passed 2,511 with 34 exact policy skips and
94 deselections, and generated execution passed 94/94. The Phase 5 product gate is clear at exact
`C_prod`; `audit3-F1` and `audit-phase3-F2` have production-artifact proofs. The mechanical auditor
passes all four reconstruction groups. This is implementation evidence, not certification. An
independent `$my-audit` remains required, one omitted external-checkout entry digest is disclosed in
the plan, no epic completion checkbox is marked, and downstream work remains blocked.

**Bounded child closed 2026-08-16:** exact occurrence-owner anchoring for usage-owned one-segment
references is certified and archived at
`.project/completed/20260816_qualified-reference-occurrence-anchoring/`. P-002 carries the shipped
promise, the deep-override evidence bound, and the owner-disposed arrayed diagnostic follow-up.
This closes that repair only; Item 8's two broader success criteria remain open.

**Bounded child closed 2026-08-16 — owner-accepted testing/tooling edge risk:**
`.project/completed/20260816_self-binding-replacement/` discharges the owner-restated authoring obligation and
implements the Fusion Tea source-model migration half of sub-item 1. The re-audit verified the
injective source/consumer proof, failure-honest validation, and the owner-ruled definition-owned
lineage-miss refusal. It also found that both migration-tool CLI modes write through a dangling
pre-existing target symlink, and that the final three-repository repair set remains uncommitted.
**[OWNER 2026-08-16]** The symlink behavior is a testing/developer-tooling edge case and accepted
risk; the owner directed closure without another remediation/audit cycle. The public-oracle and
runtime functional claims are independently verified. Its temporary
live/snapshot proof stops before committed
downstream regeneration and TEAx study execution; those remain here at
`.project/active/elaborator-downstream/`.

---

## Risks

- **Item-3 spike fails** → the epic stops at spike cost; the fallback is the recovery report's
  incremental vertical repair, which remains documented and unchosen, not destroyed.
- **Breadth long tail** (Item 5) → bounded by the inherited 29-cell matrix and the
  zero-unclassified-diffs rule; a shape outside the matrix is an owner question, not silent
  scope growth.
- **Coexistence temptation** → the harness is internal-only and its deletion is inside the
  Item-7 landing's success criteria.
- **Recapture churn** → single recapture, after the round-trip learning test, reviewed against
  the classified ledger; the timestamp-churn protocol isolates real changes.
