# Design Review: Stop Reinventing the Parser — Revision 5

**Design:** `.project/active/stop-reinventing-the-parser/design.md` (draft Revision 5, 2026-08-17)
**Spec:** `.project/active/stop-reinventing-the-parser/spec.md` (approved rev 4)
**Review File:** `.project/active/stop-reinventing-the-parser/design-review.md`
**Date:** 2026-08-17
**Supersedes:** the Revision-4 review's D5/D7/D9 and F4/F7 claims (per the fresh audit); its D1-D4/D6
verifications stand.
**Review inputs:** `.project/research/20260817-164828_expression-evidence-boundary-convergence-assessment.md`;
fresh audit `audit.md` (CI-1..CI-6); product-lens entry `design-rev5` in `product-lens.md`; an
independent code fact-check at `C_prod` `78a9beb9` and `A_final` `2171016d` (findings inline below).

---

## The Point

The product is three steps and nothing else: parse the models with a SysML v2 parser, walk the
parser's resolved tree to reconstruct the math, and emit that math into TEAx Python. Every modeled
reference must arrive in generated math meaning what the model wrote, decided from the parser's own
resolved evidence. A reference the toolchain cannot honor is refused by name — never quietly turned
into a different expression, never patched by a fallback (P-003, P-004, owner grade; P-002 exact
owner anchoring, agent/ratified). This item removes the two remaining boundaries that can corrupt
that: occurrence election not derivable from the model (Lane A) and evidence loss between SysIDE and
generation (Lane B). Revision 5 exists because three remediation passes fixed named helpers while
leaving weaker sibling routes legal; its job is to make the typed owner the *only* legal route and
to give the item a mechanical stop condition.

## Fundamental Assessment

**Sound. This is the right piece of work and the right approach.** The review pressed hardest on
three questions; the answers hold:

1. **Is the diagnosis right?** Yes. The independent fact-check confirmed the design's route census
   almost claim-for-claim at the pinned commits: the preflight really covers only `direction is In`
   top-level chains; `_expression_references` really destructures around `has_index_segment`
   (structurally dropped, no depth budget); the raw operand read, the optional
   `semantic_reference=None` binding state, the walrus-filtered deep path, and the trusted registry
   parameter are all exactly as described. The failure class is one bounded thing — typed owners
   exist, alternate weaker evidence paths remain legal — and site-by-site patching demonstrably did
   not converge on it.
2. **Is exclusivity-by-construction the right fix, or over-engineering?** It is the right fix, and
   it is built from patterns already in the repo, not new machinery: the closed-tagged-union +
   fail-closed-decode pattern is `ExpressionIR` (verified at A_final), the AST manifest gate extends
   `test_elaboration_import_boundaries.py` (verified: a real scanner with exemption-must-trigger
   checks), and graph-derived invariants follow `ships_constraint_machinery`. The design explicitly
   rejects the seductive wrong answer (a universal expression tree) with reasons. The on-route
   consumer migration is small — the fact-check counted ~5 live call sites of the permissive
   helpers in two files — so the plan is genuinely bounded, not a restart.
3. **Does the mechanical stop condition actually stop the whack-a-mole?** *Mostly, and this is
   where the design must be revised before implementation.* The closure claim as written is
   stronger than the gate that backs it (Critical-1 below), and the defense-in-depth backstop is
   unobservable as specified (Critical-2). Both are bounded revisions to the closure argument, not
   to the architecture.

**Product-lens gate:** the ledger entry `design-rev5` records **Gate: BLOCKED (audit3-F1)** — a
carried block, not a new contradiction. audit3-F1 is dispositioned **DEFERRED**: Revision 5
specifies the fix and names a proof matching the recorded falsifier exactly; the block clears only
when that live-and-capture computed-attribute test is green on a production commit. The design
itself honestly self-reports this state on line 1. The two new lens findings (design-rev5-F1, -F2)
are `[AGENT]/[INFERRED]` grade, both **DISPOSED** with named dispositions, and both are escalated
into this review as Critical-1 and Critical-2. **Smell check:** Smell 2 (consumer compensating for
a producer/platform guarantee) **fires, disclosed** — the runtime resolver type-check compensates
for a mypy lane that is not a green gate, and the per-consumer index backstop compensates for the
pre-graph inventory; both are stated in the design with reasons, so the smell escalates into
Critical-2 rather than flipping the verdict. Smell (ownership moved silently) is **clear**: the
codegen→agentic transfer of index classification, authored form, operand materialization, and the
depth budget is declared three ways (ownership table, versioned `semantic-evidence/v2` API marker,
per-repo manifests).

The fundamental approach passes. Detailed review follows.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Pass (one factual correction required)

- Every A1–A6 and B1–B10 row has a Revision-5 owner and a proof form matching its row; the
  transition ledger's A5 row now covers every expression site plus the consumer backstop, which is
  exactly the audit's CI-1 demand. The natural-route closure matrix directly answers the audit's
  "why the tests passed" analysis: it forbids internal-helper substitutes and requires live +
  admitted/capture arms per consumer.
- `[HARD]` items are preserved: parser referent authority (B4 exact-only), codegen occurrence
  materialization (D1–D4 untouched), enumeration `::` (explicit reviewed exception).
- Capture fidelity: the owner-verbatim PDF-suite retirement is carried with its quote and applied
  (isolated-run list excludes it). Provenance grades are carried; challengeable `[INFERRED]` items
  (candidate enumeration as technique) are treated as technique, not contract.
- **Correction required (fact-check claim 6):** the spec's B9 row and the design's D9 both describe
  a "warn and omit" branch in `generation/registry.py`. At `C_prod` no such branch exists — the
  collector *raises* (`RuntimeError`, registry.py:62-67); the actual defect is narrower: the
  exported generator trusts a caller-supplied pre-computed list it never revalidates (CI-5). D9's
  remedy (delete the parameter, derive from the graph at every seam) is still the right fix and is
  unaffected. The design text "The warning branch in generation/registry.py is deleted" targets a
  branch that does not exist and must be corrected so the audit can reconcile the transition ledger
  against reality. Surfaced, not silently fixed — the spec wording is the owner-approved contract.

### 2. Pattern Consistency

**Assessment:** Pass

Verified against the code, not taken on faith: the closed-union pattern is `ExpressionIR`
(`expression_ir.py:50-133`, fail-closed decoding confirmed); the static gate extends the real
`test_elaboration_import_boundaries.py` scanner (six pinned files, per-function violation families,
exemptions that must still trigger); graph-derived invariants follow the existing
`ships_constraint_machinery` precedent; frozen dataclasses + private factories match
`ExactPipelineContext` without importing its heavier sealed-context machinery (the design correctly
declines that). No parallel framework is introduced.

**One correction (fact-check claim 8):** D7 says the pipeline "gains one function,
`elaborate_loaded_extractor`". That function already exists and is exported at `C_prod`
(`elaborated_pipeline.py:143`, `__all__`). D7 is modifying it, not introducing it. Reword —
this matters because the replacement plan's diff expectations and manifest bootstrap depend on an
accurate account of what exists.

### 3. Abstraction Quality

**Assessment:** Pass

Each new abstraction was challenged; each earns its place:

- `ReferenceUse = ExactReferenceUse | IndexedReferenceUse` — the load-bearing one. It converts
  "remembered the `if has_index_segment`" into a construction error. Removing it returns the
  correctness obligation to every use site, which is precisely the defect.
- `ExpressionEvidenceInventory` — earns its place two ways: it is the single pre-graph refusal
  point (capture atomicity), and consumers fetch their row by key with missing-row = invariant
  failure, so an enumerator gap fails loudly instead of falling back to `extract_feature_refs`.
  Without it, an omitted `inspect_reference_uses` call would be silent.
- Separate `exact_path_from_relationship` factory — right call; deep redefinition paths are
  relationship paths, not expressions, and forcing them through the expression union would be the
  wrong-abstraction smell.
- The design's own rejection of a universal expression tree / strict aggregate follows the
  research's recommendation and names why (would duplicate the IR, conflate math reconstruction
  with occurrence authority).

### 4. Duplication Avoidance

**Assessment:** Pass

One owner per semantic fact, stated in a table. The pre-graph refusal + per-consumer backstop is
deliberate documented defense-in-depth, not drift (but see Critical-2 for its observability). The
dead `SysMLDataExtractor` reconstruction cluster is verified genuinely dead at `C_prod` (zero
callers including tests) and is deleted, not wrapped. The three off-route extraction modules are
verified off-route (sole real import is internal to the cluster) and get an explicit reachability
exclusion instead of silent omission — the correct disposal.

### 5. Data Structure Clarity

**Assessment:** Pass

Frozen dataclasses, closed enums, invariant-enforcing constructors (`ExactSemanticPath` requires
non-null root/leaf, one fact per segment, endpoint equality). `BindingSourceEvidence` variants make
`semantic_reference=None`-on-a-supported-form unrepresentable, which kills CI-3's state at the type
level. One residual to record explicitly (fact-check claim 13): agentic's IR-layer
`FeatureReferenceFact.target` remains `Optional` while the total operations refuse a missing
target. The design already rules the IR out of dependency-edge creation; the ownership manifest
should carry that fact as a row (permissive IR fact = math-reconstruction-only, off the exact
route) so the disagreement between layers is a recorded boundary, not an ambient fact.

### 6. Route Safety

**Assessment:** Concerns — the two Critical findings live here; see Issues below.

What passes: live and admitted/capture arms share one conversion boundary (verified existing);
sealed from-snapshot is proven outside the raw matrix by a reachability gate; strict and lenient
modes pin identical evidence-integrity refusal; capture failure asserts no snapshot byte creation;
D9 refuses before any output mutation with a byte-identity proof through the real public command.

What doesn't yet: (a) the mechanical closure condition is a five-selector blacklist and cannot, by
itself, observe the audit3-F1 defect class (a *dropped field* on a permissive fact is invisible to
a read-selector scan); (b) the consumer backstop emits the same diagnostic as the pre-graph
inventory, so the design's claim that an omitted preflight category becomes "a failing test" is
false as specified — the test passes identically either way, and the backstop layer can rot
undetected.

### 7. Bets & Decisions Integrity

**Assessment:** Concerns — the stated bets are honest; two load-bearing bets are unstated.

Stated and supported: the live route set is finite (fact-check confirmed the census; the manifest
gate makes future additions fail); D1–D4 are sound (audit reproduced them); the requirements are
right and only enforcement was wrong.

Hidden bets to surface in the design:

- **The selector list is complete.** The closure condition's authority rests on the bet that
  `.operands` / `.referent` / `.target_feature` / `.chaining_features` / metatype-name dispatch is
  the entire raw evidence-acquisition surface for expressions. If false → the gate certifies
  closure that doesn't exist, which is this item's worst failure mode. The design states it as
  fact. It must be stated as a bet with its justification (derived from SysIDE's expression API
  surface) and the gate's evasion surface specified (string-literal `getattr`, helper aliasing —
  the import-alias scan is specified; attribute-access evasion is not).
- **`IndexExpression` is mappable through `SysideAdapter`'s metatype table at SysIDE 0.8.4.**
  Almost certainly true (the class demonstrably exists — both current detectors name it), but D5
  hangs the entire index-classification authority on it; one line citing the stub or a probe row
  covers it.
- Disclosed and accepted: runtime concrete-value checks because mypy is not a green gate (see
  Recommendation 4); cross-repo landing coordination (mitigated by gate ordering and the committed
  runner rule answering CI-6).

Decisions name their alternatives (universal tree rejected; strict-variants-beside-IR chosen over
the aggregate per the research's open question; sealed-context machinery declined). Pass on that
half.

### 8. Reader Comprehension

**Assessment:** Pass

The Outcome section states the correction plainly before mechanism; the One Architecture diagram
carries the model; D-numbered decisions are navigable. The document is long, but the length is
carried-forward Rev-4 verification apparatus, not new complexity, and the Revision-5 delta is named
in the header and Outcome. One template note: there is no "The Point" section (this review carries
it above); add one line or keep relying on Outcome — reviewer's carry suffices.

---

## Issues by Severity

### Critical (must address before implementation)

- **C1 — The mechanical closure claim overstates what the gate proves** (Route Safety / lens
  design-rev5-F1). Three parts: (a) the AST gate is a read-selector blacklist and cannot see the
  audit3-F1 class — a consumer *ignoring a field* on a permissive fact performs no scanned read;
  the real closure for that class is the unrepresentable-state design, and the stop condition must
  say the three legs are jointly load-bearing (selector manifest + closed variants +
  natural-route matrix), not present the manifest equality as sufficient. (b) The permissive
  index-flag-bearing fact API survives on agentic's production surface "for non-codegen
  compatibility", and agentic's own live consumers of it (`sysml/aggregation.py:251-271`,
  `sysml/binding.py:164` at A_final) appear in no manifest — they are off codegen's route today
  only by a reachability fact. Either those modules enter agentic's ownership manifest with route
  state and proof, or the permissive fact API leaves the production surface. (c) Specify the
  gate's evasion coverage: string-literal `getattr(x, "operands")` and access through a local
  alias must be caught or explicitly out-of-scope with the compensating control named.
- **C2 — The consumer backstop is unobservable as specified** (Route Safety / lens design-rev5-F2,
  escalated Smell 2). D7 claims an omitted preflight category becomes "a failing test rather than
  a silent de-indexing route", but the backstop raises the same `SI_INDEXED_SOURCE_UNSUPPORTED`
  with the same public shape, so the matrix cell passes identically whichever layer refused. Add a
  layer-distinguishing assertion (e.g., the matrix's indexed rows assert refusal occurred at the
  pre-graph inventory before any consumer ran, plus one targeted test that disables/bypasses the
  inventory and proves the backstop alone still refuses). Same pattern: the matrix marks the
  deep-override row "not an expression route" for index refusal with no case behind it — the exact
  assumption shape that produced audit3-F1; add the case (prove a relationship path cannot carry
  an index, or refuse it).

### Major (should address)

- **M1 — The implementation base tree is unstated** (fact-check claim 15). Branch HEAD is *not* a
  descendant of `C_prod` (128 files differ; `verification/` absent at HEAD). The design freezes
  the failed candidate as evidence and requires a fresh plan, but never names the commit the next
  pass builds on (the `C_prod` tree corrected in place? the production parent `7b29d8b`?
  something else?). The replacement plan cannot be written without this; one sentence in
  Sequencing gate 1 settles it and protects the audited, working D1–D4 implementation from being
  re-derived or lost.
- **M2 — Two stale code facts** (fact-check claims 6, 8). (i) D9's "warning branch … is deleted"
  names a branch that doesn't exist at `C_prod`; restate the actual defect (trusted parameter;
  collector raises untyped `RuntimeError`) — remedy unchanged. (ii) D7's "gains one function"
  for `elaborate_loaded_extractor`, which already exists and is exported; restate as modifying
  it. Both matter for audit reconciliation, not for the mechanism.
- **M3 — Type-level exclusivity has no type checker behind it.** The resolver's
  `ExactReferenceUse`-only signature is enforcement-by-convention plus runtime check, because the
  mypy lane is not a green gate (disclosed in D5). Cheap, high-leverage hardening: a scoped
  strict type-check gate over only the new closed-variant modules (agentic reference-use values +
  errors; codegen binding variants + resolver entry), added to the static-gate suite. This makes
  "valid by construction" machine-checked where it matters without taking on the repo-wide mypy
  baseline.

### Minor (consider addressing)

- **m1** — Record the IR-layer optional-target fact (`FeatureReferenceFact.target: IdentityFact |
  None`) as an explicit manifest row (math-reconstruction-only, off the exact route) so the
  layer disagreement is a recorded boundary.
- **m2** — Note the actual migration scale in D7 (~5 on-route call sites of the permissive
  helpers, two files, at `C_prod`) so the plan is sized to reality rather than to the
  "every caller migrates" framing.
- **m3** — Add a one-line "The Point" (or keep Outcome as its carrier deliberately).

## Recommendations Summary

1. Rescope the closure condition (C1): state the three-legged stop condition, bring agentic's
   permissive-fact consumers into a manifest or delete the permissive API from the production
   surface, and specify the AST gate's evasion coverage.
2. Make the defense layers observable (C2): layer-distinguishing assertions in the indexed matrix
   rows plus the deep-override indexed case.
3. Name the implementation base tree (M1) in Sequencing gate 1.
4. Correct the two stale code facts (M2) and add the scoped strict type-check gate (M3).
5. Fold m1–m3 opportunistically in the same revision pass.

---

## Resolutions

All findings resolved with the owner, 2026-08-17. Each ruling is `[OWNER]` (option selected by the
owner from agent-presented alternatives); sizing evidence is agent-measured at the pinned commits.

- **M1 — implementation base tree:** `[OWNER 2026-08-17]` **Build on the `C_prod` tree
  (`78a9beb9`) and correct it in place.** New work branches from the failed candidate's tree; the
  audited D1–D4 implementation, probes, and verification harness are preserved. Gate 6 reseals a
  fresh `C_prod`, so the certified identity is unaffected by lineage. Sequencing gate 1 must name
  this base. Restarting from the production parent and continuing on the diverged docs HEAD were
  both declined.

- **C1(b) — permissive reference-fact API:** `[OWNER 2026-08-17]` **Delete the permissive
  index-bearing API from agentic's production surface** (the stronger of the two dispositions the
  finding offered). The owner explicitly rejected the manifest-the-consumers option as the
  compatibility-shim pattern this item exists to kill. Consequences for the design:
  - D5's "may remain for non-codegen compatibility" clause for `extract_feature_refs`,
    `feature_reference_facts`, and `feature_chain_facts` is replaced by deletion from the
    production surface.
  - All measured consumers migrate to the closed inspector output: `sysml/aggregation.py` (2
    sites; an `IndexedReferenceUse` inside an aggregation term refuses like every other consumer),
    `sysml/binding.py` (1 site), and `validation/adr002.py` (2 sites — the validation lane
    migrates too, so no "off-route survivor" is recreated). `expression.py`'s internal callers are
    rebuilt under D5 regardless.
  - `has_index_segment: bool` leaves the fact surface entirely; the defect class becomes
    unrepresentable in both repositories.
  - Sizing basis: ~5 call sites across 3 files; the only codegen consumer of aggregation's
    `FeatureChainNode`/`SingletonTerm` output is `hierarchy_resolver.py`, already off-route and
    already slated for deletion/inventory by this design.

- **M3 — scoped strict type gate:** `[OWNER 2026-08-17]` **Add it.** Strict mypy over only the new
  closed-variant modules (agentic reference-use values and errors; codegen binding variants and
  the resolver entry) joins the static-gate suite. Not a repo-wide mypy cleanup; the two-mode
  invocation (strict-scoped vs baseline) is documented so it is not "fixed" away.

- **C1(a), C1(c), C2, M2:** accepted as written — each has a single reasonable resolution and the
  owner raised no objection when they were presented as accepted-by-default amendments. For the
  record: C1(a) restate the stop condition as three jointly load-bearing legs (selector manifest +
  closed variants + natural-route matrix); C1(c) specify the AST gate's evasion coverage
  (string-literal `getattr`, local aliasing) or name the compensating control; C2 add
  layer-distinguishing assertions to the indexed matrix rows plus the deep-override indexed case;
  M2 correct the two stale code facts (no registry warning branch exists — the defect is the
  trusted parameter; `elaborate_loaded_extractor` already exists and is modified, not introduced).

- **Minor m1–m3:** fold into the same revision pass. m1 records the IR-layer optional target
  (`FeatureReferenceFact.target`) as a manifest row (math-reconstruction-only, off the exact
  route) — unaffected by the C1(b) deletion, which removes the helper functions, not the IR. m2's
  migration-scale note now covers both repos (~5 on-route codegen sites + ~5 agentic sites). m3
  at the design agent's discretion.

---

## Revision-6 targeted re-check — 2026-08-17

Per the agreed minor-fix rule, the reviewer re-checked the revised sections of design.md
(Revision 6) against this review's Resolutions instead of rerunning a full review. Every
resolution is incorporated, and D1–D4 are not reopened:

- **M1** — "Revision-6 implementation base" section, `[OWNER]` stamped: branch from `C_base`
  (old `C_prod` `78a9beb9`) / `A_base` (`2171016d`); the docs checkout explicitly ruled out as a
  base; gate 6 assigns fresh final identities. The design agent also caught and corrected a
  latent contradiction (probe commits previously described as recreated from the production
  parent; retained ancestry now recorded) — verified as claimed.
- **C1(a)** — closure restated as three jointly load-bearing legs (acquisition / representation /
  routes) with "no leg substitutes for another" (design.md:627-642).
- **C1(b)** — `[OWNER]` deletion section (design.md:429-456): permissive helpers,
  `ResolvedSemanticReferenceFact`, `has_index_segment`, `ExpressionRef`,
  `BindingInfo.references`, aliases, and exports all deleted; every measured consumer migrated
  including the adr002 validation lane; the rejected manifest alternative recorded as a one-line
  decision record; migration counts recorded as sizing evidence, not a closure oracle.
- **C1(c)** — AST gate covers direct attributes, literal `getattr`, local/import aliases, and
  rejects any non-literal `getattr` in the raw-SysIDE module set; five mutation kills required
  (design.md:618-625). Stronger than requested.
- **C2** — leg 3 requires proving both inventory-before-consumer refusal and the
  bypassed-inventory backstop; the CI-4 closure row adds the real `Feature`-only deep-path proof
  plus a forced mapped-`IndexExpression` refusal, closing the "not an expression route" assumption.
- **M2** — D7 now describes `elaborate_loaded_extractor` as existing; Current-code-facts records
  the registry defect accurately (trusted parameter; untyped `RuntimeError`; no warning branch).
- **M3** — scoped strict lane over four named new boundary files with exact commands; scoped zero
  errors and the repo-wide baseline cannot waive each other.
- **m1–m3** — `FeatureReferenceFact.target` carried as a typed-surface manifest row that cannot
  satisfy the raw-selector gate; migration sizes recorded; a Load-bearing bets section (B1–B3)
  now states the previously hidden bets with if-false consequences.

**Design-agent pushback, vetted and accepted:** deletion is not tag-only — the inspector's
`ExactReferenceUse` payload is provenance-complete (per-target declaration identity, member and
qualified names, owner identity/kind, document URL and tier, location) so migrated consumers
cannot be forced to reconstruct the weak route under new names. Checked against the
universal-tree rejection: the payload carries reference-target provenance only, no operator or
literal structure — the IR remains the sole math representation, and D6 keeps sole classification
authority (target document URL restated as having no classification role). The line holds.

**Independent spot-checks:** the B3 bet's stub citation is exact
(`class IndexExpression(OperatorExpression)` at `syside/core/__init__.pyi:10897`); `ExpressionRef`
consumers at `A_base` are exactly the named migration set — the "no unrelated consumer" deletion
claim holds; `git diff --check` clean per the design agent's validation.

---

**Overall: Approve (Revision 6).** The Revision-5 verdict was Revise; all findings are resolved
and verified incorporated. The architecture targets the actual recurring defect class (missing
exclusivity) rather than its latest instance, its code census is independently fact-checked, its
stop condition now claims exactly what its gates prove, and the owner's deletion ruling made it
simpler than the draft. D1–D4, D6, D8, D10, and the artifact topology are not reopened.

**Next Steps:** Proceed to the replacement `/_my_plan` from Revision 6. The plan must keep both
ownership manifests, the scoped strict gates, the full natural-route matrices, the probe/fixture
lock, and the `C_prod`/`F_final`/`C_evidence` boundaries as checked deliverables, and must not
append tasks to the Revision-4 plan. Product-lens gate remains `BLOCKED (audit3-F1, DEFERRED)` by
design until the named live-and-capture computed-attribute proof is green on a production commit —
an implementation-time clearance, not a review-time one. Implementation is followed by an
independent `/_my_audit`; the implementing agent does not self-certify.

---
---

# Targeted review — Revision 7 amendment

**Design:** `.project/active/stop-reinventing-the-parser/design.md`, Revision 7 (`f53ae94`)
**Governing record:** `run-records/phase1-stop-report.md` revision 3, rulings 1-7 owner-ratified
2026-08-17
**Scope:** the amendment only. Everything the Revision-6 verdict above approved stays approved and
was not re-litigated.
**Fact-check base:** all cited commits are reachable from this checkout's object store, so every
claim below was checked against Git directly rather than through the `C_base` worktree.
**Date:** 2026-08-17

## What was checked and found correct

Recording this first, because the verdict below is Revise on two narrow points and the rest of the
amendment holds up under direct verification.

**Counts, hashes, and commits — all confirmed:**

- `verification/probe-fixture-lock.json` at `C_base` contains exactly **118** path/sha256 rows.
- Exactly **two** of those 118 paths differ between the lock commit and `C_base`:
  `tests/fixtures/v6_recapture_batch/batch.json` and `verification/capture_baseline.py`. This
  reproduces the stop report's Finding 1 independently. The five probe scripts and all 111 source
  rows are byte-identical across that span.
- Frozen batch at `P_seed` `52a03cd2`: `captured` = **15**, `fixtures` = 37, so 22 refusals.
  `FROZEN_BATCH_SHA256 = bd7bf245…` (`capture_baseline.py:31`). Current batch at `C_base`:
  `captured` = **14**, so 23 refusals; `CURRENT_BATCH_SHA256 = 7f926978…` (`capture_baseline.py:33`).
  The frozen/current table at design.md:1177-1180 is exact in every cell.
- `P_SEED = 52a03cd2d0a9fdd340b60b16cea79a5b72234b08` (`capture_baseline.py:29`) — matches
  design.md:1139. Both `43edf9bd` and `52a03cd2` are ancestors of `C_base` — matches design.md:1107.
- `validate_current_batch` is at `capture_baseline.py:166` — exact, and it does require a closed
  record inventory (37 fixtures, `captured | refused == fixtures`, disjoint), as design.md:1142-1143
  claims.

**Behavior and mechanism claims — all confirmed:**

- `deep_cross_scope_probe` moved `"status": "graph"` → `"status": "refused"` with
  `codes: ["SI_OCCURRENCE_MISSING"]` and `error_type: ElaborationDiagnosticError`. Exactly as
  design.md:1241-1269 states.
- `plant_value_shapes` moved refusal-code only (`SI_SELF_BINDING` ×2 → `SI_TYPE_INVALID`), leaving
  the graph/refusal totals unchanged. design.md:1183-1184 states this correctly, and the arithmetic
  works only under that reading (15 − 1 = 14).
- `validate_output_transitions` hard-codes
  `moved_records != ["deep_cross_scope_probe", "plant_value_shapes"]` as a failure and validates the
  captured/refused delta as "the exact A2 move." The design's A2-ownership claim is enforced in
  committed code, not just asserted.
- `_snapshot_semantics` deletes exactly `authority.agentic_mbse_version`,
  `authority.sysml_codegen_version`, and `integrity.digest` — "two version fields plus
  `integrity.digest`" (design.md:1145) is exact.
- `build_manifest` reads the batch through `_frozen_batch()` → `_git_bytes(P_SEED, …)` and sets
  `canonical_batch.sha256 = FROZEN_BATCH_SHA256`. "Names those frozen bytes by construction, never
  the working-tree file" (design.md:1140-1141) is exactly right.
- Both `expected-transitions.md` quotations at design.md:1149-1151 are verbatim, and the A5 ledger
  row quoted at design.md:1302 ("an element index is ignored → pre-graph
  `SI_INDEXED_SOURCE_UNSUPPORTED`") is verbatim from the committed ledger.
- D11's quotation of D7 is verbatim: design.md:575 reads "Refuse every `IndexedReferenceUse` before
  calculation-definition extraction, `_ExactElaborator`, or `InstanceGraph` allocation."

**Faithfulness to rulings 1-7 — met:**

Ruling 1 (design.md:121-123), ruling 2 and the never-re-derive clause (design.md:1133-1135, stated
twice with the "returns to design, never authorizes a replacement lock" consequence explicit),
ruling 3 (the two legs, design.md:1129-1154), rulings 4-5 (design.md:1241-1269 plus the
`[DEEP-QUALIFIED-OUTPUT-WIRING]` backlog row and fixture-comment fix at design.md:1515-1526),
ruling 6 (design.md:1305-1335, both cases kept tests with their recorded `C_base` diagnostics, and
the explicit "neither case substitutes for the other" argument), ruling 7 (the amendment itself).
The `deep_cross_scope` never-restore is stated as a stop condition in the ruling's own terms — "not
a reconciliation to negotiate" — which is the right strength.

**No mechanism change — confirmed.** The diff has no hunk anywhere in design.md:207-866 (D1-D10),
the closed-variant sections, the artifact chain, the acyclic topology, or the consumer/ownership
manifests. Every hunk lands in one of the five declared areas.

**D11 adds no mechanism — confirmed.** It restates D7's ordering, adds the public-diagnostic
consequence (always `SI_INDEXED_SOURCE_UNSUPPORTED`, never `SI_OCCURRENCE_*`) that already follows
from that ordering plus D7:600's consumer backstop, and adds a test obligation and a ledger row.
Nothing in it requires behavior D7 does not already require. The rejected-alternative note is a
decision record, correctly phrased.

**Anchor integrity — confirmed.** All 33 distinct `design.md#…` targets used in `plan.md` rev 2
resolve against Revision 7's headings, including `#revision-6-implementation-base`, which the
amendment edited under but did not rename. Four `plan.md` links have labels that look like stale
anchors (`#commit-boundary-is-closed`, `#natural-route-closure-matrix`, `#diagnostic-ownership`,
`#one-codegen-conversion-boundary`) — in every case that text is the link *label* and the target is
valid. The amendment broke nothing.

**Anti-vacuity vs the frozen/current table — consistent.** design.md:1234-1235 now requires 15/22
frozen *and* 14/23 current; both sum to 37 and both match the measured states.

---

## Findings

### Major 1 — the amendment names the wrong commit as "the lock commit," and it passes by accident

**Location:** design.md:1131-1132, and consequently 1158, 1161-1162, 1541. Interacts with
design.md:1104-1110.

The new Lock leg says the 118 hashes "must recompute against the lock commit's own tree,
`43edf9bde4db44e7973458ada732d2cd75e764f6`." But the lock file self-identifies differently:

    "probe_fixture_commit": "20f9e60a19b30bc1ec9a27aacb08380f4bc45602",
    "probe_fixture_parent": "7b29d8b636e284364a4fdce9079f153c51c867ea"

`20f9e60a` is the commit whose tree the hashes were computed against. `43edf9bd` is its child,
titled "chore: lock corrected parser probes and fixture corpus," and `git diff 20f9e60a 43edf9bd`
is exactly one file changed: the lock file itself. The design's own earlier paragraph
(design.md:1104-1107) gets this right — retained probe/fixture commit `20f9e60a`, manifest-only lock
child `43edf9bd`.

So the `[verified]` zero-mismatch claim is **true against either tree**, because the two trees are
byte-identical for all 118 locked paths. It is true by accident, and the amendment never says why.

Why this matters here specifically: design.md:1110 requires the runner to check
"`probe_fixture_commit` to equal that locked 40-character SHA," and two paragraphs later the
amendment introduces `43edf9bd` as "the lock commit." An implementer wiring the new Phase-1 kept
test from §"What the lock is verified against" — the section written for exactly that purpose — can
reasonably assert `lock["probe_fixture_commit"] == "43edf9bd…"`, which is **false against the actual
file** and trips a stop for the same class of reason that produced the Phase-1 stop this amendment
exists to fix.

**What correct looks like:** state both SHAs and their roles in the Lock leg. For example: the lock
records `probe_fixture_commit = 20f9e60a…` and `probe_fixture_parent = 7b29d8b6…`; hashes are
computed against `20f9e60a`'s tree; the manifest-only child `43edf9bd…` reproduces those bytes
exactly because it adds only the lock file, so either commit satisfies the recompute. Then name one
of them as the commit the Phase-1 kept test reads from, and use that same SHA at design.md:1158,
1161-1162, and 1541.

### Major 2 — replacing the byte rule leaves two locked file classes with no current-state pin

**Location:** design.md:1123-1154 (the two legs), with design.md:1114-1116 (D10 "locked input").

The amendment's claim that the new rule "is not weaker: it checks strictly more" holds for most of
the lock, and I verified the coverage file class by file class:

| Locked class | Rows | Current-state pin under leg 2 |
|---|---|---|
| 111 source `.sysml`/`.kerml` rows | 111 | `validate_manifest` hashes the **working tree** against `fixture-manifest.json` (`capture_baseline.py:161-163`) — covered |
| `verification/fixture-manifest.json` | 1 | pinned to its `P_seed` bytes (`capture_baseline.py:135-137`) — covered |
| `tests/fixtures/v6_recapture_batch/batch.json` | 1 | `validate_current_batch` at `CURRENT_BATCH_SHA256` — covered |
| `verification/capture_baseline.py` | 1 | **nothing** |
| 5 probe scripts under `.project/…/probes/` | 5 | **nothing** |

Leg 1 pins the last two rows only at their *historical* bytes. Leg 2 is scoped to `tests/fixtures`
(`validate_output_transitions` passes `-- tests/fixtures` to `git diff`) and does not reach either.
Revision 6's "any changed byte invalidates the verdicts" did cover them — over-broadly, which is why
it was deleted, but the amendment's replacement is genuinely weaker for exactly these two classes.
The irony is sharp: `capture_baseline.py` is one of the only two locked files that actually moved,
and it is now the one file whose current bytes no leg pins.

Compounding it, design.md:1114-1116 redefines D10's rerun trigger as "a change to the frozen
historical bytes." Bytes at a past commit cannot change, so as literally written the probe-rerun
trigger can never fire. Under Revision 6, editing a probe script during Phases 2-5 would have
invalidated the verdicts; under Revision 7 nothing catches it.

**What correct looks like:** add a short paragraph to §"What the lock is verified against" naming
the residual class explicitly — `verification/capture_baseline.py` and the five probe scripts are
historical-only rows; their current state is owned by the committed tests that exercise them
(`tests/conformance/test_public_route_baselines.py`,
`test_stop_parser_documentation_contract.py`) and by the recorded probe verdicts, not by a byte pin
— and either add a current-state pin for the five probe scripts or state which artifact owns them.
Then reword design.md:1114-1116 so the D10 trigger is fireable: "locked input" means a change to any
locked probe or fixture source in the implementation tree, as distinct from a ledger-owned
current-output transition.

### Minor 1 — `source_evidence.py:173` is a blank line

**Location:** design.md:105-106 (also design.md:88 in the Current-code-facts bullet).

At `C_base`, `def screen_source_readiness` is at line **174** and `for binding in usage.bindings` —
the claim being cited — is at line **195**. Line 173 is blank. The stop report carries the same
off-by-one, so the amendment inherited it rather than introduced it, but a design that governs
byte-level gates should not ship a citation that points at whitespace.

**What correct looks like:** `extraction/source_evidence.py:195` for the iteration claim, or
`:174-196` for the function.

### Minor 2 — `capture_baseline.py:76` does not contain the functions named beside it

**Location:** design.md:1138-1140.

The bullet attributes the frozen reconstruction to "`build_manifest` / `validate_manifest`" and cites
`capture_baseline.py:76`. Line 76 is `def _frozen_batch`, which performs the `FROZEN_BATCH_SHA256`
check at line 78. `build_manifest` is at 86, `validate_manifest` at 134. The substance is right —
`build_manifest` calls `_frozen_batch` — but the citation and the names do not line up.

**What correct looks like:** "…reconstruct the frozen source inventory from Git at the named
`P_seed` commit through `_frozen_batch` (`capture_baseline.py:76-79`) and check it against
`FROZEN_BATCH_SHA256`."

### Minor 3 — `design.sysml:75` is the comment, not the authored input

**Location:** design.md:1247-1248.

The sentence "the fixture's Pattern B authors an input aimed at the one concrete produced output
(`tests/fixtures/deep_cross_scope_probe/design.sysml:75`)" cites the comment line. The authored
input `in data_point = measurement_system::station::array::sensor::core::metric_value;` is at line
**77**. The separate citation of `:75` for the stale comment at design.md:1519-1521 is correct.

**What correct looks like:** `design.sysml:77` for the authored input; leave `:75` where it names
the comment.

### Minor 4 — the four-row behavior table flattens two provenance grades into one

**Location:** design.md:104-113.

The stop report grades its matrix row by row: rows 1 and 4 orchestrator-verified, rows 2 and 3 "the
agent's retained probes." The amendment presents all four rows under one heading ("The measured
behavior at `C_base`") with no per-row grade, and the `[verified]` bracket at design.md:97-98
attaches to the mechanism, not the table. Capture-fidelity rule 1 requires the grade to survive
every hop.

This does not touch the red set: both red-set cases (design.md table rows 1 and 4) rest on
orchestrator-verified rows. What it does affect is the exclusion argument — "Operator-wrapped forms
are real expressions, enter the screen, and refuse correctly today" (design.md:111-113) rests on
agent-probe row 2, and the amendment states it in bold as settled fact.

**What correct looks like:** mark rows 2 and 3 as agent-probe evidence in the table, or add one
sentence: rows 1 and 4 were reproduced by the orchestrator; rows 2 and 3 are the Phase-1 agent's
retained probes.

### Minor 5 — "every post-`P_seed` output byte" overstates `validate_output_transitions`

**Location:** design.md:1144.

The function diffs `P_SEED..FOUR_A` restricted to `-- tests/fixtures`, then checks current bytes
against the 4A bytes for the 23 maintained snapshots and the golden file. It does not reach outputs
outside `tests/fixtures` (`verification/pre-change-baseline.json`, the probe verdict JSONs). The
claim as written is broader than the code.

**What correct looks like:** "proves every post-`P_seed` output byte **under `tests/fixtures`** is
either metadata-only … or owned by a named A/B row."

### Minor 6 — the ruling markers upgrade agent-grade items past the vocabulary they were given

**Location:** design.md:121, 1123, 1243, 1307.

The stop report is explicit: "Origin of the rulings remains agent-grade (external review +
orchestrator verification), ratified by owner; challenge them by re-deriving against the recorded
evidence above." Capture-fidelity rule 1 gives that exact case a form: `[AGENT] (ratified by owner,
date)`. The amendment writes `[OWNER-ratified 2026-08-17, ruling N]`, which is honest about the
ratification but reads as owner-grade at a glance, and the design nowhere records the
challenge-by-re-derivation affordance the stop report preserved.

**What correct looks like:** `[AGENT] (ratified by owner, 2026-08-17) — ruling N`, with one sentence
in the revision history noting these are challengeable by re-deriving against
`run-records/phase1-stop-report.md`, not by asking the owner again.

### Minor 7 — the handoff's Plan-Revision-3 list omits the `deep_cross_scope` obligations

**Location:** design.md:1683-1687.

The handoff enumerates three things Plan Revision 3 "must carry": the two-leg lock rule plus the new
committed check, both indexed red cases, and the A5a/A5b rows. It reads as a complete list, and it
omits ruling 4-5's operational half — the never-restore stop condition, and the fixture-comment plus
`[DEEP-QUALIFIED-OUTPUT-WIRING]` backlog obligations. The design body binds implementation either
way, but the plan is where a reconciliation gate gets written, and "restore the old graph to get the
counts back to 15/22" is precisely the wrong move the stop condition exists to forbid.

**What correct looks like:** add a fourth item — Phase 4's reconciliation gate treats
`deep_cross_scope_probe` returning to a captured graph as a stop, and the landing unit carries the
fixture-comment fix and the `[DEEP-QUALIFIED-OUTPUT-WIRING]` row.

### Minor 8 — D11 is numbered like D1-D10 but does not live with them

**Location:** design.md:1336, under `## Test design` → `### The indexed red set`.

D1-D10 are `###` subsections of `## Detailed decisions`. D11 is a `####` under a Test-design
subsection, and `## Detailed decisions` never mentions it. The handoff then asks for confirmation
"without reopening D1-D10," which reads as if D11 were outside the decision set. A reader scanning
the decisions section will miss a numbered decision.

**What correct looks like:** move D11 to `## Detailed decisions` as `### D11.` and cross-reference it
from the red-set section, or leave it in place and add a one-line pointer under D7. Either way, make
the handoff say D1-D11.

### Minor 9 — corrections re-quote the deleted text rather than deleting it

**Location:** design.md:97-99, 1123-1127, 1173-1175.

Each correction restates Revision 6's wrong claim inline before deleting it ("Revision 6's earlier
account — 'the computed attribute route reads a fact that retains `has_index_segment`, ignores that
field' — named the wrong trigger and is deleted"). Capture-fidelity rule 3 asks corrections to
shrink or amend, with the rejected content recorded once in its designated home rather than
repeated in the live text. Three inline restatements of a deleted claim anchor future agents on it.

**What correct looks like:** delete the quotations from the body and record each correction as one
line in the Revision history section, which the amendment already added for this purpose. This is a
judgment call and the smallest of the findings — the amendment's motive (an auditable trail of what
changed and why) is legitimate.

---

## Verdict

**Revise.**

The amendment is substantively right. Every ruling is implemented, no mechanism moved, no anchor
broke, and every count, hash, commit, and quotation I could reach independently checks out —
including the two that carry the most weight, the 118-row lock and the 15/22 → 14/23 transition.
The reason for Revise rather than Approve is narrow: the one section the amendment exists to rewrite
is the one that governs the gate that already stopped this run once, and it still contains an
ambiguity (Major 1) and a coverage hole (Major 2) that would be executed by a Phase-1 implementer.

**Minimal must-fix set:**

1. **Major 1** — reconcile `probe_fixture_commit` (`20f9e60a`) with "the lock commit" (`43edf9bd`)
   in the Lock leg, say why either tree satisfies the recompute, and use one SHA consistently at
   design.md:1131-1132, 1158, 1161-1162, and 1541.
2. **Major 2** — name `verification/capture_baseline.py` and the five probe scripts as
   historical-only rows with their current-state owner stated, and reword design.md:1114-1116 so the
   D10 rerun trigger is fireable.
3. **Minors 1-3** — correct the three citations (`source_evidence.py:195`,
   `capture_baseline.py:76-79` with `_frozen_batch` named, `design.sysml:77`).

Minors 4-9 are recommended but do not block. Minor 7 is worth taking with the must-fix set, since it
costs one line and closes a plausible Phase-4 failure.

Nothing here reopens Revision 6. The Approve above stands.

---

## Orchestrator verification — Revision-7 must-fix set (2026-08-17)

The authoring session applied all eight findings; the orchestrator verified each against the
artifacts rather than rerunning the reviewer (pipeline rule: record the verification for
objectively verifiable fixes).

- **Major 1:** verified from the lock file itself — `probe_fixture_commit = 20f9e60a…`,
  `probe_fixture_parent = 7b29d8b6…`, and `git diff 20f9e60a 43edf9bd` is one file, one insertion
  (the lock file). The design now names `20f9e60a` as the authoritative tree, states the
  by-construction equivalence, and the kept test reads the field from the lock file and forbids
  hard-coding `43edf9bd`.
- **Major 2:** leg 3 added, pinning the five probe scripts and `capture_baseline.py` at current
  bytes with ledger-owned differences (the existing `capture_baseline.py` move cites `da4aa78` and
  `46694e2`, both confirmed in git log). D10's trigger rewritten to two conditions that can fire.
  Count nuance recorded: by path prefix there are seven non-`tests/fixtures` lock rows; the seventh,
  `verification/fixture-manifest.json`, is classed as a fixture input and is already pinned at
  current bytes by leg 2's `validate_manifest` (must equal frozen `P_seed` bytes) — every locked
  byte is covered, and the six-row verification-code class is exactly enumerated in the text.
- **Minors 3-8:** citations spot-checked (`source_evidence.py:195` is the `for binding in
  usage.bindings:` line; `_frozen_batch` at `:76`; `design.sysml:77` authored input / `:75` comment),
  provenance markers now use the agent-grade-ratified form with the behavior table's per-row grades
  restored, output-transition scope corrected to `tests/fixtures` and interlocked with leg 3, the
  handoff carry-list gained the never-restore and fixture-comment obligations, D11 demoted to a
  named D7 clause under `#### Inventory refusal precedes occurrence resolution` with two-way
  anchors, and all inline re-quotes of deleted Revision-6 text removed.

**Disposition: the Revision-7 amendment stands as reviewed-and-corrected; the `Revise` verdict's
must-fix set is closed.** Revision 6's `Approve` is untouched.

---

# Revision 8 targeted review (2026-08-18)

**Design:** `design.md` Revision 8 — targeted amendment of Revision 7, written after the Phase 3
stop-rule halt
**Scope:** the amendment and its integration only. Revision 6's `Approve` and the closed Revision-7
amendment are not reopened. D1-D10, the closed-variant architecture, the artifact chain, the acyclic
topology, and the probe/fixture lock were not re-reviewed.
**Inputs read:** `design.md` (rev 8); `briefs/design-rev8-amendment.md` (the four owner rulings, the
input contract); `run-records/phase3-stop-report.md`; `run-records/phase2-audit.md` (m2, m3, and
their confirmation-addendum closures); `run-records/phase1-audit.md` Minor 9 context;
plan.md Phase 1 completion and its "Issues / deviations" item 3.
**Verification limit — stated plainly:** the implementation worktrees at
`/tmp/stop-parser-rev2/worktrees/{sysml-codegen,agentic-mbse}` are outside this session's sandbox and
could not be read or grepped; `git` on the documentation checkout was likewise unavailable. Every
implementation fact below is taken from the run records (which do carry file:line citations), not
re-measured against the trees. Findings that depend on a tree fact are marked.

**Verdict: `Revise`.**

The amendment is right in substance. All four rulings are present with their verbatim blocks quoted
and their grades carried, the falsified premise is deleted rather than softened, and nothing in the
approved mechanism moved. The reason for `Revise` is that the amendment repeats, in one new place,
the exact failure mode that caused the Phase 3 halt — a structural obligation stated in a word whose
reading the implementer has to choose ("enforce exactly two operands" now carries the weight that
"validates its shape" carried before) — and that its downstream handoff still addresses Revision 7
and a plan revision that has already been consumed.

## What checks out

- **Ruling 1** lands at design.md:507-526. The owner's replacement contract is quoted verbatim
  (:510-512). The distinction the brief singles out survives intact and in the owner's terms: "This
  boundary does not validate unit grammar at all — which is not the same as saying any unit shape
  passes validation; a shape SysIDE rejects never reaches here" (:515-516). The feature-reference and
  exact-referent requirements are named as **dropped** (:514-515), not quietly omitted. The falsified
  premise is explained with its measured cause and cited to the stop report (:520-526).
- **The four required coverage cases** appear in all three places they need to, consistently:
  design.md:524-526 (ruling text), :1572-1576 (evidence and public-boundary matrix), :1861-1862
  (handoff). Each carries `[m]`, representative compound forms (`[kg/m^3]`, `[W/(m·K)]`), wrong arity
  through a synthetic node, and the value operand's references still visited. The matrix adds "which
  must elaborate rather than refuse" for the compound forms — a faithful consequence of the ruling,
  not a new requirement.
- **Ruling 2** lands at design.md:538-558, quotes the primitive's contract verbatim (:543-545), and
  is carried into the export list (:1036-1037) and the ownership table as two separate rows that
  split parser shape from value-site policy (:1008-1009). The delegation clause is specific enough to
  be checkable: Codegen's helper "performs no operand indexing, no arity check, and no metatype test
  of its own" (:554). `annotated_ast_value`'s deletion squares with it — the deletion stands (:517,
  :556-558), and the clause explicitly names the Phase-3 surfaced residual (premise conflict 2) as
  what the primitive resolves.
- **Ruling 3** lands as a new subsection, design.md:779-810, with the five requirements quoted
  verbatim (:791-797). The Agentic gate's audited scoping is left untouched and said so twice
  (:781-782, :787). The account of the m2 residual matches the Phase-2 audit exactly — including that
  m2's mechanism closed while the argument-passed reader remains open
  (`run-records/phase2-audit.md`:474-487). The owner's 20-row figure and the "a red count that
  shrinks because the scan narrowed is not progress" rule are both recorded (:807-810), and the
  three-leg closure condition below it is unweakened.
- **Ruling 4** lands in both places. The matrix row (design.md:150) and the prose under it
  (:160-169) match the measured record term for term: graph returned, `SI_OCCURRENCE_AMBIGUOUS` +
  `SI_OCCURRENCE_MISSING`, all three `cells[i]__mass` attributes present, `picked` unresolved
  (plan.md:1091-1100). The red-set Case 2 text is updated in step (:1506-1512).
- **The A5b ledger row (design.md:1465) does expect both starting states.** Its "old behavior" cell
  names the strict incidental `SI_OCCURRENCE_AMBIGUOUS` *and* the lenient graph carrying both
  diagnostics, and the paragraph at :1477-1483 tells Phase 4's reconciliation gate to expect the
  transition rather than flag it. Obligation 4 is satisfied.
- **Amendment discipline holds on the parts that matter most.** D1-D10 are unrenumbered; no heading
  was removed (the amendment adds exactly one, `#### The Codegen gate keeps repository-wide scope`,
  and both references to it resolve); every `design.md#…` anchor plan.md rev 3 links still resolves
  except a set that was already dangling before this amendment (see Minor 3).

## Must-fix

**Must-fix 1 — the wrong-arity behavior of `unit_annotation_value` is undefined, and it is the same
class of gap that halted Phase 3.** design.md:543-547.

The primitive's signature is `-> Any | None`, and the only stated meaning for `None` is "not a unit
annotation" (:547). The contract also says it must "enforce exactly two operands" (:543). What
"enforce" produces is never said, and the two readings diverge in behavior an implementer will ship:

- *Raise* `SemanticEvidenceError(EXPRESSION_KIND_UNSUPPORTED)` — a malformed annotation refuses by
  name, and Codegen's value-site policy call now has a raising path it did not have before, which
  D7 converts to `SI_EVIDENCE_INCOMPLETE`.
- *Return `None`* — the annotation is treated as "not an annotation", so `inspect_reference_uses`
  walks it as general math and **emits the unit operand as a reference use**, which is precisely the
  m3 defect the ruling exists to prevent; and Codegen mints a computed node instead of a literal
  value site.

The required test case "wrong arity through a synthetic node" (:525) has no stated expected outcome,
so the test cannot arbitrate either. The Phase-2 tree chose the raising reading
(`test_a_malformed_unit_annotation_is_refused_by_name`, per `run-records/phase2-audit.md`:451-456
— tree fact, from the record), but the design must state it rather than leave it to be inherited.

*What correct looks like:* one sentence under the ruling-2 quote — a recognized `[` annotation with
an operand count other than two raises `SemanticEvidenceError(EXPRESSION_KIND_UNSUPPORTED)`; `None`
is returned only when the expression is not a `[` annotation at all; Codegen's value-site policy does
not catch that error, so it reaches the D7 boundary as `SI_EVIDENCE_INCOMPLETE`. Then give the
wrong-arity coverage case its expected outcome in the matrix at :1572-1576.

**Must-fix 2 — the amendment adds coverage but never retires the Phase-2 assertions that pin the
falsified premise.** design.md:508-526.

Per `run-records/phase2-audit.md`:451-456 (tree fact, from the record), Agentic's
`_unit_annotation_value` at `reference_use.py:316` refuses a non-feature-reference unit operand with
`EXPRESSION_KIND_UNSUPPORTED` and an unresolved unit referent with `RESOLVED_TARGET_MISSING`, and
those refusals are pinned by kept tests. Ruling 1 drops both requirements. Those assertions are now
wrong, and the audited m3 closure — which the audit accepted partly *because* shape validation
survived (:451, "Shape validation survives") — now rests on a different mechanism: never emitting the
unit operand at all, rather than validating its referent.

The design says the requirements are dropped but says nothing about the assertions that encode them,
so an implementer resuming Phase 3 meets green tests asserting a rule the design deleted.

*What correct looks like:* one clause under ruling 1 naming what goes — the non-feature-reference and
unresolved-unit-referent refusals and their assertions — and one sentence stating that m3's closure
now rests on non-emission, so the Phase-2 audit's m3 disposition is re-established on the new
mechanism rather than silently inherited.

**Must-fix 3 — the next-stage handoff still addresses Revision 7 and Plan Revision 3.**
design.md:1873-1890.

The rev-8 carry-list at :1858-1871 is good, and it does the one thing the brief singled out: it names
the phase-boundary consequence, that ruling 2 lands in Agentic, which Phase 3 treated as read-only,
under the same `0.1.3` / `semantic-evidence/v2` contract (:1863-1866). The problem is everything
immediately below it. ":1873" still reads "Revision 7 needs targeted `my-design-review` confirmation
that the five amended areas are corrected", and ":1879" still reads "After confirmation, Plan
Revision 3 consumes this document", followed by rev-7's carry list (the three-leg lock rule "in Phase
1", the committed historical-tree check, both indexed red cases). Phases 1-2 are complete and plan
rev 3 already consumed all of it. A plan agent reading the handoff top-down is instructed to build
Phase 1 again.

*What correct looks like:* retarget the block — this review confirms Revision 8's four areas; the
consuming artifact is the next plan revision (rev 4), which resumes at Phase 3 from the stop
report's rollback point; keep the rev-7 bullets only if marked as already consumed by plan rev 3.

**Must-fix 4 — two things the plan revision needs are missing from the handoff.** design.md:1858-1871.

1. *Reopening Agentic reopens Phase 2's audited surface.* The handoff says the phase boundary "has to
   allow" the Agentic change but not what that costs. `#agentic-semantic-contract` (:1042) already
   requires the scoped strict lane, standalone tests, and lint to pass from the committed Agentic
   tree before Codegen consumes it. Say that this applies again to the ruling-2 landing, and that
   the Phase-2 audit's m3 disposition is re-established there (ties to Must-fix 2). Without it, the
   plan can land an Agentic change on a tree whose audit is dated to different bytes.
2. *Plan Phase 3's manifest premise is falsified and the handoff doesn't say so.* Phase 1 recorded
   that Phase 3 "removes" the ~26 unowned reads (plan.md:1106-1109); the stop report's premise
   conflict 1 falsifies that for 11 of them, and ruling 3 replaces removal with collision-aware rows
   plus migration or mechanical exclusion. The handoff carries ruling 3's content but never tells the
   plan revision that its own recorded premise has to change. Add that sentence — it is the
   difference between a plan that revises Phase 3 and a plan that re-states a false target.

## Should-fix

**Should-fix 1 — a collision-aware row has no defined proof form, so "field owner or receiver
contract" is not yet arbitrable.** design.md:799-805.

Every other row class has a named proof: a live row's proof is its public failure test, an off-route
row's is the reachability exclusion (:754-755). The collision row is required to carry "a real
closure proof" (:793, owner-verbatim) and the design's own gloss is "the same proof obligation every
other row carries" (:803-804) — but neither says what the artifact *is* for this class. An
implementer can satisfy "receiver contract" with a docstring assertion; an auditor will want
something the scan can re-derive. The design anticipates the failure ("A row asserting an owner it
cannot prove fails like any stale row", :804-805) without saying how proving works.

*What correct looks like:* name the artifact. For example: the declaring type must be provable at the
read site from a type annotation or module-local construction, and the row's proof is a test that
fails if the annotation or the declaring type changes. `SourceFile.referent`'s serialized-key status
(:801-802) makes this concrete and cheap.

**Should-fix 2 — the evasion mutant's kill criterion is stated as discovery, not as gate failure.**
design.md:772-775.

The text requires the adapter-free mutant "must still be discovered". Discovery alone is not a kill:
the gate fails on set inequality against the reviewed manifest (:776-777). As written the mutant is
in fact killed — a new `(module, function, selector)` tuple is not in the manifest — but the stated
criterion is weaker than the mechanism, and the collision rule above it is exactly the place a future
row could swallow it. Say it in the strong form: the mutant's tuple must appear in the discovered set
and fail the equality gate, and an unannotated receiver can never qualify for a receiver-contract
row. That last clause is what keeps ruling 3's own mechanism from becoming the escape ruling 3
exists to close.

**Should-fix 3 — the changed-section list at the top undercounts the sections actually edited.**
design.md:24-36.

The list is organized by ruling, and the rulings reach further than four sections. Edited but
unlisted: Outcome (:76-79), Data and responsibility ownership (:1008-1009), Transition ledger seed's
A5b row (:1465), Evidence and public-boundary matrix (:1572-1576), File-level implementation map
(:1655), and Next-stage handoff (:1858-1871). The brief requires the amendment to list its changed
sections; an auditor diffing section by section currently finds six edits the header does not
account for. Add them as a second line ("also touched, mechanically, by the four rulings: …").

**Should-fix 4 — the file-level map names a different home for the value-site rule than D5 and the
ownership table do.** design.md:1655 versus :552-555 and :1009.

The row's file list is `extraction/binding_source.py`, `elaboration/binding_evidence.py`,
`source_evidence.py`, `unit_annotation.py`, while its Change text (rewritten by this amendment) says
the value-site rule is "kept as Codegen policy over Agentic's `unit_annotation_value` primitive". D5
and the ownership table put that rule in `elaboration/expression_evidence.unit_annotated_value`. Per
the stop report, `annotated_ast_value` and the four `binding_evidence` builders are already deleted
and the rule already moved to `expression_evidence` (tree fact, from the record). An implementer
reading the map has two candidate homes.

*What correct looks like:* name `elaboration/expression_evidence.py` in that row and mark
`unit_annotation.py` / `binding_evidence.py` as deleted, or drop them from the row.

**Should-fix 5 — "D1-D10 … are untouched" reads literally false.** design.md:40-42. Ruling 2 amends
D5's text. The intended claim is that no D1-D10 *mechanism* changed. Say that: "no D1-D10 mechanism
changes; D5 gains the shared primitive." One clause, and it stops a reconciliation pass from
recording a contradiction between the header and the diff.

**Should-fix 6 — CI-2's "including a unit wrapper" proof now points at an operand that is never
traversed.** design.md:1837. With the unit operand opaque, a unit-wrapper proof of operand
materialization and the shared depth budget has to run against the annotation-level materialization
and the value operand. The row still reads as it did when the unit operand was walked. One clause
prevents a Phase-4 proof written against untraversed structure.

**Should-fix 7 — "a shape SysIDE rejects never reaches here" is the load-bearing half of ruling 1's
distinction and is asserted without its evidence.** design.md:515-516. The Phase-2 audit measured
exactly this at SysIDE 0.8.4 — two project-scoped unit spellings, both parser-refused
(`run-records/phase2-audit.md`:458-463). Cite it. The sentence is doing the work of keeping "does not
validate unit grammar" from reading as "anything passes", and it should not rest on assertion.

## Minor

1. **Ruling 2's verbatim uses "should"; the design converts it to a requirement** (:543-545 quoted,
   then :548-555 as consequences). This is the right call for an owner ruling and the quote is
   preserved intact, so provenance is not damaged — noting it only so the conversion is visible if
   the owner meant the softer reading.
2. **The 20-row figure is recorded without reconciliation to the plan's ~26.** design.md:807. The
   design itself carries no competing number, so there is no internal contradiction; the plan does
   (plan.md:1106-1109), which is why Must-fix 4(2) puts the reconciliation in the handoff rather than
   here.
3. **Pre-existing dangling anchors, plan-side, not caused by this amendment.** plan.md links
   `design.md#natural-route-closure-matrix`, `#commit-boundary-is-closed`,
   `#one-codegen-conversion-boundary`, `#diagnostic-ownership`, and a truncated `design.md#deep`;
   none of these resolve against design.md's headings, and none were removed by Revision 8 (the last
   two are almost certainly meant to be `#d7-one-codegen-conversion-boundary` and
   `#d8-diagnostic-ownership`). Recorded here so the plan revision fixes them on its own side. Every
   other plan-cited anchor resolves.

## Verdict and minimal must-fix set

**`Revise`.** Nothing here reopens Revision 6 or the closed Revision-7 amendment, and none of the
four rulings needs to be re-decided — they are encoded faithfully. The must-fix set is four items:

1. **Must-fix 1** — state what "enforce exactly two operands" produces (raise vs `None`), and give
   the wrong-arity coverage case an expected outcome. design.md:543-547, :1572-1576.
2. **Must-fix 2** — name the Phase-2 assertions that ruling 1 retires, and re-establish m3's closure
   on non-emission. design.md:508-526.
3. **Must-fix 3** — retarget the handoff from Revision 7 / Plan Revision 3 to Revision 8 and the plan
   revision that resumes Phase 3. design.md:1873-1890.
4. **Must-fix 4** — add the two missing handoff items: the Agentic re-verification obligation that
   comes with reopening that tree, and the falsified "Phase 3 removes the ~26 unowned reads" premise.
   design.md:1858-1871.

Should-fix 1 and 2 are worth taking with the must-fix set: together they cost a short paragraph and
they close the one place where ruling 3's own mechanism could become the escape it was written to
prevent.

## Resolutions — Revision 8

*(empty; to be filled when the owner engages with this section)*

---

## Orchestrator verification — Revision 8 must-fix set closed (2026-08-18)

Verified directly in `design.md` after the design session's review-incorporation pass; the
review's verdict stands as `Revise` → closed, per the rev-7 precedent (minor, objectively
verifiable fixes recorded rather than re-reviewed).

- Must-fix 1: wrong-arity outcome ruled and stated — raises the named refusal; `None` never
  describes a malformed annotation (design.md:581, :1632). [AGENT ruling, derived from the
  owner's verbatim "enforce exactly two operands".]
- Must-fix 2: "What this retires in the Phase-2 tree" names the superseded assertions and
  re-bases m3's closure on non-emission (design.md:545).
- Must-fix 3: stale "confirm Revision 7"/"Plan Revision 3 Phase 1" handoff instructions gone
  (grep-clean); handoff targets the next plan revision resuming Phase 3 from `d257ef1`.
- Must-fix 4: both consequences present — Agentic reopening re-applies the Phase-2 audited
  obligations (design.md:1933) and the "~26 unowned reads" premise restatement (design.md:1941).
- Should-fixes 1-2: collision-row proof artifact defined with the unannotated-receiver
  exclusion (design.md:815, :854) and the mutant criterion stated as failing the manifest
  equality gate (design.md:814).

Design Revision 8 is approved for consumption by the plan revision.
