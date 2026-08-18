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
