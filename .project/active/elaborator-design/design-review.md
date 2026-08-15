# Design Review: Production Elaborator + Exact Identity Bridge (reopened)

**Design:** `.project/active/elaborator-design/design.md` (2026-08-08 revision, base `6bed968`)
**Spec:** `.project/active/elaborator-design/spec.md` (Item-4 spec, 2026-08-07, unamended)
**Review File:** `.project/active/elaborator-design/design-review.md`
**Date:** 2026-08-08
**Trigger:** breadth audit BLOCKED (`.project/active/elaborator-breadth/audit.md` — audit-F1/F2/F3);
owner reopened the design after the root-cause analysis (unique node IDs were proven, but
identity-preserving node *selection* still ran on names).

---

## The Point

One semantic source occurrence becomes exactly one runtime source across every calculation,
constraint, and aggregation consumer. SysIDE has already resolved which element a reference
denotes; codegen must consume that exact identity while the AST is live — never replace it with a
non-unique name and recover the target later. Names may exist only as auxiliary/diagnostic
metadata and as projection output. **[OWNER 2026-08-08]**, carried from
`epic_elaborate_first_architecture.md:63-70` and contract invariants 54–60.

## Fundamental Assessment

**Sound. This is the right piece of work and the right approach.** Verdict basis:

- The independent product-lens (appended to `product-lens.md`, gate **DISPOSED**, no BLOCK)
  re-derived the point from the epic/contract and found the design **clears the falsifier**: no
  name-produced, name-matched, or name-keyed identity anywhere between load and graph; the
  chain resolver contextualizes the exact resolved root (D5); aggregation enumerates exact
  occurrence IDs; invariants 7–9 state the adversarial observables; validation item 10 puts a
  mechanical guard on the identity package.
- The three-identity model (declaration ID / occurrence ID / node-port ID) is exactly the
  distinction the postmortem identified as conflated. It directly designs out audit-F1
  (leaf-name re-anchoring) and audit-F2 (name-reconstructed sum expansion).
- The bridge is transient and elaborator-owned — explicitly *not* a persisted manifest or second
  authority. That is the direct answer to the Item-4 shadow-ledger failure.
- Every code citation in Research Findings was independently verified against both repos
  (one cosmetic mismatch, see Minor). Two load-bearing assumptions were probed live this
  review (see Dimension 7); both came back favorable, with pins the design must absorb.

The design-level smells were checked by the lens: neither fires. The identity-authority
ownership move (QN/name contract in `agentic-mbse` → exact-ID contract) is declared, not
smuggled.

Complexity matches the problem: the failure family is precisely untyped-string identity, and
typed opaque IDs are the minimal mechanism that makes the failure unrepresentable. No finding
here challenges the architecture — the Criticals are a dropped-content restoration and a
one-sentence semantic pin.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

- **The reopened revision dropped spec-required material the prior revision carried** (lens
  design-F1, verified against `git show HEAD:design.md`): the old D8 projection contract
  (entry-point classification from value sites → DESIGN_ATTRIBUTE / LIBRARY_DEFAULT /
  USAGE_LITERAL; parameter groups from node source files; toposort; `entry_point_groups` /
  registry facts; `fallback_entry_points` retirement + V11 invariant; ADR-003 name helpers),
  the old D9 diagnostics-code catalog, and the **deletion ledger** section. Spec R5 and R8 are
  `[NEED]`; the ledger is an epic acceptance criterion. New D8 ("Projection owns strings") is a
  naming boundary, not the seam contract. A correction must shrink the corrected mechanics, not
  the neighbors (capture-fidelity Law 3). → Critical C1.
- **The spec itself is still one level too high** — the owner's root-cause analysis said so
  explicitly. R1's outcome is right, but the declaration-ID representation, the identity API,
  and the prohibition on name-based lookup inside elaboration exist only in this design. R3
  still says "exact-QN comparison"; the design corrects it in an implementation note but the
  spec file is unamended. Without a requirement-level anchor, a future design revision can
  degrade again exactly as D5-v1 did. → Major M3.
- Otherwise compliant: R2/R4 by construction (one node per source occurrence, occurrence
  identity from usage IDs); R6 dual-run preserved; R7 acknowledged (29-cell matrix untouched
  as authority); provenance grades carried faithfully — the owner's 2026-08-08 ruling is
  graded `[OWNER]` (paraphrase), not verbatim, which is correct.

### 2. Pattern Consistency
**Assessment:** Concerns (minor)

- The repo already has a typed-identifier convention: `core/identifier_types.py` (NewType over
  str: `SysMLQN`, `EQN`, `PQN`, `CanonicalChannel`, `ScopedKey`; plus `ScopedAliasKey =
  NewType(..., tuple[str, str])` — the accepted precedent for a *structured* NewType kept
  unjoined so components cannot collide) and frozen-dataclass wrappers where the ID carries
  derivation behavior (`output_registry.py`). D1 says "wrap the UUID in a project type" without
  picking a convention. → Minor m2.
- `element_id` appears nowhere in either repo's `src/` today — greenfield, no conflicting
  precedent. The adapter (`syside_adapter.py`) exposes live elements at exactly the
  evidence-capture point (`resolved_target_fact` already holds the live element), so D1's
  capture seam is sound — but the adapter has **no such accessor today**; D1 creates new
  `agentic-mbse` surface on the unmerged `elaborate-first-salvage` branch. → folded into M2.

### 3. Abstraction Quality
**Assessment:** Pass

DeclarationId / FeatureSlotId / OccurrenceId / NodeId / OutputPortId each earn their
existence: every one closes a confirmed defect class (leaf-name capture, slot splitting,
rendered-path parsing, sanitized-key overwrite, output-name identity). The bridge as a
transient index with one contextual resolver is the right shape — one authority, discarded
after elaboration. "Names are derived metadata" is stated at every layer.

### 4. Duplication Avoidance
**Assessment:** Pass (with the M2 compatibility caveat)

The design refactors the *existing* occurrence walker rather than growing a parallel one, and
explicitly forbids a second persistent identity manifest — both direct answers to the Item-4
postmortem. The evidence types **replace** the QN/name identity contract rather than riding
beside it ("no ID rider while the string resolver stays authoritative").

### 5. Data Structure Clarity
**Assessment:** Pass

Typed, structured, opaque IDs; provenance kept but demoted to non-authority; neutral
expression IR bound to consumer-port IDs. The one confirmed hazard — the generic snapshot
serializer silently emits `null` for a raw `uuid.UUID` (`serializer.py:257-258`, verified) —
is already named in Implementation Notes. Keep it; it is real.

### 6. Route Safety
**Assessment:** Pass

Fail-closed throughout (D10): zero candidates and multi-candidates are named diagnostics,
plural expansion is caller-explicit, alias cycles / dangling edges / duplicate identities fail
before projection, strict-vs-lenient can change halt-vs-report but never identity (invariant
10), and a graph with blocking findings is not projectable. This closes the audit's
alias-cycle-fallback and invocation-becomes-UNBOUND family at the design level.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

Two live probes were run for this review (scripts in the session scratchpad; fixture
`spec_chain_twolevel`, licensed loads):

- **B2 is TRUE — with a pin the design must absorb.** SysIDE **does** materialize implicit
  parameter redefinitions as real Redefinition edges: the usage-side `in drive_power =` param
  carries `owned_redefinitions` n=1 with `redefined_feature → MeierCost::drive_power` and
  `is_implied=True`; authored `:>>` is the same shape with `is_implied=False`
  (`is_implied_included` is True for **both** — it does not discriminate). Def-side parameters
  have zero redefinition edges (they are the slot roots). As written, D2's "explicit
  redefinition edges" reads as authored-only — under that reading the ordinary calc-usage
  parameter binding splits into two slots and the mission invariant fails for the most common
  idiom in the corpus. One sentence fixes it. → Critical C2.
- **B1 is TRUE for the supported boundary — and its falsification record is incomplete.**
  Probe: 33/33 named elements byte-stable across two independent loads, across a relocated
  fixture directory, across source-offset shifts, and across model composition changes;
  `referent.element_id` equals the declaration's ID (the bridge key works). But: stable IDs
  are **UUIDv5 of the qualified name** — cross-load, DeclarationId is a QN hash, so the scheme
  transitively leans on the same `qualified_name` nullability Research Finding 2 uses to
  disqualify QNs. Null-QN elements — name-collision victims, anonymous usages, and **every**
  expression/relationship node including Redefinition edge objects themselves — get a random
  v4 UUID per load. And the stub says `element_id` "may be deprecated in a future release …
  no use outside of serialization", which the design does not record (lens design-F3).
  Consequences the design must state: key slot edges by *endpoint* IDs (never the edge
  object's own ID); name the null-QN forms that fail closed; carry the deprecation in B1's
  if-false path; and persist the probe evidence as a research artifact + pinned tests — the
  current text cites probes with no artifact, which is the exact overclaim pattern
  ("spike-proven") this reopen exists to kill. → Major M1.
- **B3** (resolved graph suffices for projection) is unchanged from the spike's real-generation
  evidence; acceptable.
- Hidden bets surfaced and now discharged by probe: "implied redefinitions are materialized"
  (true, pin it); "referent is populated post-sema for supported forms" (true for all sampled
  FREs; the `| None` typings route to D10 fail-closed).

### 8. Reader Comprehension
**Assessment:** Pass

The three-identity model is stated plainly before mechanism; the ASCII flow anchors it; each
decision names its rejected alternatives. A tired engineer gets the model in one pass.

---

## Issues by Severity

### Critical
- **C1 — Restore the dropped spec-required sections** (projection contract with EP
  classification and parameter-group derivation, diagnostics-code catalog, deletion ledger).
  The reopened revision fixed identity and silently regressed R5/R8 coverage. — Spec
  Compliance (lens design-F1).
- **C2 — Pin D2 to implied edges.** Feature slots must follow Redefinition edges *including*
  SysIDE-materialized implicit ones (`owned_redefinitions`, `is_implied=True`); discriminator
  facts from the probe (no `source`/`target` on Redefinition; use
  `redefined_feature`/`redefining_feature`; `is_implied_included` does not discriminate)
  belong in the design. — Bets Integrity (lens design-F2 + probe).

### Major
- **M1 — Complete B1's falsification record and persist the evidence.** UUIDv5-of-QN fact,
  null-QN v4 instability (collision victims, anonymous elements, all expression/relationship
  nodes), edge-objects-unstable → key by endpoints, `element_id` deprecation risk, probe
  artifact + pinned adversarial tests as the identity-foundation kill probe (not end-stage
  acceptance). — Bets Integrity (lens design-F3 + probe).
- **M2 — State the legacy-compatibility constraint on the D3 refactor and the cross-repo
  landing.** `PartInstanceIndex`/`PathStep`/`instance_path` feed ~8 legacy production modules
  plus the v5 snapshot schema, and three sites parse the rendered path back into structure
  (`constraint_lowering.occurrence_scope`, constraint namespace derivation at
  `constraint_lowering.py:1364-1374`, `output_registry_builder.py:198`). The legacy front end
  must stay authoritative and byte-identical until Item 7, so the refactor must keep the
  rendered surface and snapshot bytes unchanged (or give the elaborator a typed view) — say
  which. D1's adapter accessor is new `agentic-mbse` surface on the unmerged salvage branch;
  name the coordinated-landing requirement. — Duplication/Patterns.
- **M3 — Amend the spec, don't just out-design it.** Add a requirement forcing the
  declaration-ID representation, the identity API, and the no-name-lookup prohibition
  (invariants 7–8), and correct R3's exact-QN wording to declaration-ID. Owner's call on
  wording; without it the requirement-level gap from the postmortem persists. — Spec
  Compliance.

### Minor
- **m1 —** Research Finding 1's citation pairs `FeatureReferenceExpression.referent` with
  `.pyi:5875-5905`, which is `Element.element_id`; `referent` is at ~7823 (inside the
  7798-7835 range already cited). Cosmetic.
- **m2 —** Pin D1's wrapper convention against repo precedent: NewType (per
  `identifier_types.py`, with `ScopedAliasKey` as the structured-NewType precedent) vs frozen
  dataclass where the ID carries derivation. Also note `identifier_types.__all__` already
  omits `ScopedAliasKey` — pre-existing inconsistency, don't inherit it.
- **m3 —** The breadth product-lens ledger stays **BLOCKED** (audit-F1/F2/F3) until landed
  code plus an observed public-boundary mutation clears it; this design being approved does
  not resolve those entries. Record that expectation in the plan so nobody closes them by
  citation.

---

## Recommendations

1. Restore C1's three sections into the reopened design (merge, not append — the identity
   revision governs where they conflict, e.g. EP classification now reads value sites through
   typed IDs).
2. Add the C2 sentence to D2 and the probe facts to Research Findings; re-grade B2 from bet to
   probe-confirmed fact with the `is_implied` pin.
3. Fold M1 into B1 + Risks + Validation (kill-probe placement), and write the probe results
   into a `.project/research/` artifact the design cites.
4. Add M2's compatibility constraint to D3/Integration Strategy explicitly.
5. Ask the owner whether to amend the spec per M3 now or carry it as a recorded gap.

---

## Resolutions

- **C1 — Resolved in design.** Restored the full projection contract in D7-D8: module and entry-
  point projection, value-site classification, parameter groups, producer-edge ordering,
  `entry_point_groups`, output aliases, constraint catalog, registry return contract,
  `fallback_entry_points` retirement, and V11 coverage. Restored a fixed diagnostics catalog in
  D10 and the deletion ledger as its own section.
- **C2 — Resolved in design.** Research Finding 8, B2, D2, live-construction step 3, the handoff,
  and adversarial case 5 now include every SysIDE-materialized `Redefinition` edge, authored and
  implied. Slot families use `redefined_feature` / `redefining_feature` endpoint IDs and never the
  relationship-object ID; `is_implied_included` is explicitly not a filter.
- **M1 — Resolved in design and research record.** B1 now states the proven named-element boundary,
  UUIDv5/QN derivation, null-QN UUIDv4 instability, deprecation risk, endpoint-ID rule, and exact
  fail-closed boundary. The probe results are persisted at
  `.project/research/20260808-103243_syside-identity-and-redefinition-probe-record.md`. Validation
  makes the kept identity tests the first kill probe, before consumer breadth.
- **M2 — Resolved by owner decision 2026-08-08.** The design no longer refactors the legacy
  `PartInstanceIndex` or creates a compatibility view. The new front end owns a clean exact-ID
  occurrence walker. The complete legacy front end stays frozen and byte-identical as the shipped
  route and black-box comparator until atomic cutover, when the old walker and its consumers are
  deleted. No graph mixes the two routes. The new `agentic-mbse` accessor and its first codegen
  consumer are one coordinated cross-repository landing.
- **M3 — Resolved by owner decision 2026-08-08.** The owner selected Option A. Spec R3 now states
  self-binding as exact semantic-declaration equality, and ratified R9 requires exact parser
  declaration IDs, structured occurrence IDs, typed graph targets, the parser identity boundary,
  and the semantic name-lookup prohibition.
- **m1 — Resolved in design.** Research Finding 1 now cites `element_id`, referent/chaining, and
  redefinition endpoints at their correct separate stub ranges.
- **m2 — Resolved in design.** D1 chooses frozen dataclasses for semantic identity because runtime
  namespace distinction, UUID validation, and canonical serialization are required. It records why
  the existing string-oriented `NewType` precedent is insufficient here.
- **m3 — Resolved in design.** Validation states that breadth findings `audit-F1` through
  `audit-F3` remain blocked until landed code plus an observed public mutation clears them. Design
  approval cannot clear the ledger.

### Objective verification — 2026-08-08

**[AGENT]** The correction pass checked the revised text directly:

- C1's projection facts, diagnostics catalog, and deletion ledger are all present.
- C2's implied/authored inclusion rule and endpoint-only identity rule are present in the finding,
  assumption, decision, construction flow, handoff, and adversarial tests.
- M1's probe artifact exists and is cited; the kill probe precedes breadth validation.
- M2's new-walker/frozen-route/atomic-deletion rule is consistent across D3, components,
  integration, validation, and the deletion ledger.
- `git diff --check` is clean.

This is an objective correction check, not a new independent review verdict. M3 was subsequently
resolved by the owner and applied to the spec. Neither event clears the breadth audit ledger.

---

**Overall:** Revise
**Resolution status:** All findings are incorporated. The rewritten Item-5 plan is at
`../elaborator-breadth/plan.md`; its phase strategy is owner-approved and awaits implementation
approval.
