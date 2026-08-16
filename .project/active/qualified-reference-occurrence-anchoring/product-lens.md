# Product Lens — qualified-reference-occurrence-anchoring

Append-only ledger. One block per run, per `/home/reid/.codex/scripts/product-lens.md` §3. Gate
consumers scan every block; a finding remains live until a later block resolves it by stable ID.

---

## spec — 2026-08-15 — rev `.project/active/qualified-reference-occurrence-anchoring/spec.md`
Epic: ELABORATE-FIRST

Point (re-derived): A design search must use the resolved semantic referent available at model load
so each concrete source occurrence becomes exactly one runtime source reaching every and only its
bound consumers. For owner-qualified references, usage qualifiers resolve occurrence-level
features; definition qualifiers remain definition-level and bridge only through a unique occurrence
context. [sources: `.project/product/P-001-design-search-free-variation.md` (owner-verbatim);
`.project/backlog/epic_elaborate_first_architecture.md:31-33,67-68,84-86` (owner);
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:618-623`
(agent/ratified)]

Falsifier: From inside `comp_b`, bind a consumer to `comp_a::length`; the obligation is violated if
the edge targets `comp_b.length`, silently chooses any candidate, or an off-default mutation of
`comp_a.length` fails to reach every and only its bound consumers on live and snapshot routes.

Findings:

- spec-F1 [DON'T] The spec marks five code-derived mechanism statements `[HARD]`, including D-6's
  ambiguity/no-guess behavior. D-6 remains `[AGENT] (ratified by owner)`; ratification and current
  code do not upgrade it to `[HARD]`. The exact-owner availability, slot normalization,
  resolver-call surface, and snapshot-shape statements are inherited facts or inferences, not
  external constraints. —
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:584-588,618-623`
  (agent/ratified) — disposition: DISPOSE — preserve the required behavior, but regrade D-6's rule
  as `[INHERITED]`, the owner-selected outcome as `[NEED]`, and code/design facts as `[INHERITED]`
  or `[INFERRED]` before design.

Smells: none.

Gate: DISPOSED (spec-F1)

---

## spec — 2026-08-15 — rev `.project/active/qualified-reference-occurrence-anchoring/spec.md`
Epic: ELABORATE-FIRST (separate bounded child of Item 8; `[INFERRED]`)

Point (re-derived): A design search must use the semantic referent resolved at model load so each
concrete source occurrence becomes exactly one runtime source reaching every and only its bound
consumers. Owner-qualified usage references resolve occurrence-level features; definition-qualified
references remain definition-level and bridge only through a unique occurrence context. [sources:
`.project/product/P-001-design-search-free-variation.md` (owner-verbatim);
`.project/backlog/epic_elaborate_first_architecture.md:31-33,67-68,84-86` (owner);
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:618-623`
(agent/ratified)]

Falsifier: From inside `comp_b`, bind a consumer to `comp_a::length`; the obligation is violated if
the edge targets `comp_b.length`, silently selects another candidate, or an off-default mutation of
`comp_a.length` fails to reach every and only its bound consumers on live and snapshot routes.

Findings:

- None.

Resolves:

- spec-F1: FIXED — authority: agent/ratified — basis: D-6 is now `[INHERITED]`, the owner-selected
  broader outcome is `[NEED]`, and the code/design-derived mechanism statements are `[INHERITED]`
  or `[INFERRED]` with citations; none retains manufactured `[HARD]` authority.

Smells: none.

Gate: CLEAR

---

## spec — 2026-08-15 — rev `.project/active/qualified-reference-occurrence-anchoring/spec.md`
Epic: ELABORATE-FIRST

Point (re-derived): A design search must preserve the semantic referent resolved at model load and
anchor it to the exact concrete occurrence, so one source occurrence reaches every and only its
bound consumers. Usage-owned bare and qualified references retain that occurrence identity;
definition-qualified references bridge only through a unique occurrence context. [sources:
`.project/product/P-001-design-search-free-variation.md` (owner-verbatim);
`.project/backlog/epic_elaborate_first_architecture.md:31-33,67-68,84-86` (owner);
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:394-409,613-626`
(agent/ratified)]

Falsifier: In a discriminating `comp_a`/`comp_b` topology, a direct reference whose resolved leaf
belongs to `comp_a` targets `comp_b`, guesses among occurrences, or an off-default `comp_a`
mutation fails to reach every and only its calculation, alias/computed, constraint, and aggregation
consumers on live and snapshot routes.

Findings:

- None.

Smells: none.

Gate: CLEAR

---

## design_review — 2026-08-15 — rev `.project/active/qualified-reference-occurrence-anchoring/design.md`
Epic: ELABORATE-FIRST

Point (re-derived): One semantic source occurrence must become exactly one runtime source across
every calculation, constraint, alias/computed, and aggregation consumer — that source being the
referent SysIDE resolved while the model was loaded, never one reconstructed from the consumer's
position — and an unsupported form must fail loudly before generation rather than pick a candidate.
[sources: `.project/product/P-001-design-search-free-variation.md:11-18` (owner-verbatim);
`.project/backlog/epic_elaborate_first_architecture.md:31-33,67-68,84-86` (owner);
supplement — coverage truth, `P-001…:57-64` + ADR-009 `docs/architecture/modeling-assumptions.md:588`
(agent/ratified); `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:618-626`
D-6 (agent/ratified)]

Falsifier (design-level observable): the design would show a one-segment reference whose exact
resolved leaf is owned by occurrence A yielding an edge to occurrence B — or a silent/fallback
candidate — with no loud failure; or it would claim the repaired behavior holds on a lane where the
only evidence offered cannot distinguish "checked and passed" from "not checked."

Note (D10 / SC8 deferral, assessed both directions): the deferral HONORS the point. The owner
graded the broad invariant itself (`spec.md:44` `[OWNER]`) and the design implements it (B1, D2,
Core Concept) — it defers the *evidence*, not the behavior, after a targeted probe falsified the
named fixture topology, refuses to substitute a mock while calling it authored evidence (Risks
row 1), and parks production edits behind the owner's choice (Next-Stage Handoff). Capture-fidelity
law 4 done correctly.

Findings:

- design-F1 [DO] The deep-literal-override lane may ship with "a reproducible census proving the
  affected fact shape is not authorable" in place of a regression (`design.md:196-198,357,409`) —
  absence-of-evidence recorded as acceptance evidence; a census shows no instance was found, not
  that none is authorable. — `P-001…:57-64` / ADR-009 (agent/ratified) — falsifier: the validation
  table's Deep override row passes with a census and no named, standing coverage gap. disposition:
  DISPOSE — reword the census option as a declared coverage gap in the same register as D10
  (named, dated, reproducible, visible at close), not as an alternative form of proof.

- design-F2 [DON'T] Smell 2 fires. The producer contract (`ResolvedTargetFact.owner_element_id` +
  `owner_is_definition`, `../agentic-mbse/src/agentic_mbse/sysml/data_models.py:55-89`) exists to
  let downstream distinguish definition- from occurrence-level referents; D2 finds it too coarse,
  freezes it ("schema and extraction behavior do not change", `design.md:306-308`), and compensates
  in the consumer with a live metatype lookup — two representations of one fact kept in agreement
  by test discipline (the design's own risk row admits they can disagree). Reviewer assessment
  tempering the finding: the branch DECISION uses one authority only (live leaf → live owner →
  live metatype); the frozen owner fields corroborate, they do not decide. — producer contract
  ([INHERITED]) + derivation ([INFERRED]) — falsifier: extraction changes owner metatype semantics
  and the resolver branch activates on a declaration the frozen evidence does not agree with, with
  no failure. disposition: DISPOSE — record in the design why the split-source cost is accepted
  for this item and name the extraction/conformance pinning test as the standing guard, or file
  extending the fact with owner metatype as the follow-up that retires the split.

- design-F3 [DO] D10 route 2 would prove the resolver predicate on a constructed fact while
  leaving unproven that any legal authored model reaches the discriminating case; the design does
  not require that outcome to carry a standing "authored bare discrimination is unproven" record,
  so a later reader sees SC8 satisfied. — `P-001…:57-64` / ADR-009 (agent/ratified) — falsifier:
  SC8 marked met under route 2 with no standing record that the authored end is untested.
  disposition: DISPOSE — make the named coverage gap a required output of route 2, carried to
  close.

Smells: smell 2 fired (see design-F2; escalated into the stage judgment, disposed there, verdict
Revise). Smell 7 checked, did not fire: the shift of occurrence authority from consumer lexical
position to the leaf's declared owner is stated explicitly (Core Concept, Branch behavior, B1,
D2), and the snapshot route's reliance on recapture discipline is stated (invariant 13, D9).

Gate: DISPOSED (design-F1, design-F2, design-F3)

---

## independent-audit — 2026-08-16 — rev `8bea4b8`

Point (re-derived): Every supported one-segment reference whose exact leaf is owned by a real
`PartUsage` must preserve that owner's concrete source occurrence, so varying one source changes
every and only its consumers. Aggregation over an arrayed child remains one term per occurrence.
[sources: `.project/product/P-001-design-search-free-variation.md:11-17` (owner-verbatim);
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:394-410,661-668`
(agent/ratified); `docs/architecture/modeling-assumptions.md:409-418` (INHERITED)]

Falsifier: In a model with `comp_a : Component[2]`, `sum(comp_a::length)` produces anything other
than two edges to `comp_a[0].length` and `comp_a[1].length`, or it reads/refuses based on the
enclosing `comp_b` occurrence while the equivalent `sum(comp_a.length)` enumerates both members.

Findings:

- independent-audit-F1 [DO] The direct-reference repair discards the aggregation caller's
  `plural=True` at `elaborate.py:2320-2331`, so an arrayed exact owner is refused instead of
  enumerated. A licensed customer-shaped probe at HEAD produced `SI_OCCURRENCE_AMBIGUOUS` and zero
  inputs for `sum(comp_a::length)`, while changing only `::` to `.` produced two exact-owner inputs
  and no diagnostic. The retained sum test uses a scalar owner and therefore freezes the special
  case without exercising the product's array-enumeration meaning (`test_usage_owned_reference_anchoring.py:288-299`).
  — `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:405-410,661-668`
  (agent/ratified); `docs/architecture/modeling-assumptions.md:409-418` (INHERITED) — falsifier:
  the paired arrayed-owner probe above — disposition: DISPOSE — carry this as a named close
  residual and repair it in a bounded follow-up with a paired kept test proving both spellings
  enumerate the exact owner's two occurrences and never bind the sibling.

Smells: **Smell 3 — special category exempts unchanged user-visible meaning** and **Smell 6 — test
passes only because it selects one interpretation** fire in independent-audit-F1 and escalate the
gate. The one-segment branch treats an arrayed sum differently from the equivalent feature-chain
sum, and the retained sum test passes because its chosen owner has one occurrence. Smell 1 remains
mechanically present but is already disposed by design-F2 and verified here: the live leaf-owner
metatype is the only deciding authority, the frozen owner fields only corroborate it, and the
executing extraction guard pins agreement. Smells 4 and 5 did not fire.

Gate: DISPOSED (independent-audit-F1)

---

## remediation-audit — 2026-08-16 — rev `c2fa657`

Point (re-derived): A resolved one-segment leaf must either preserve its exact occurrence owner or
refuse before codegen can silently substitute another source. Verification must not turn missing
evidence into agreement. [sources: `.project/product/P-001-design-search-free-variation.md`,
`.project/product/P-002-exact-owner-anchoring.md`, and
`docs/architecture/modeling-assumptions.md:588` (ADR-009); grades: owner-verbatim and
agent/ratified]

Falsifier: an absent leaf falls through to consumer-position resolution, or verification accepts a
missing identity block as unchanged.

Findings:

- None at the product boundary for remediation findings 1, 5, and 6. The comparator now rejects a
  missing identity block, the absent-leaf route refuses instead of guessing, and both diagnostic
  branches have discriminating kept tests. The audit separately found an incomplete census claim;
  that is an evidence-integrity gap, not a contradiction in the shipped product behavior.

Smells: smells 1, 3, 4, 5, and 6 do not fire within this bounded remediation. The earlier
`independent-audit-F1` arrayed-aggregation disposition remains untouched.

Gate: CLEAR
