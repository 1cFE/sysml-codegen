# Product Lens — qualified-reference-occurrence-anchoring

Append-only ledger. One block per run, per `/home/reid/.codex/scripts/product-lens.md` §3. Gate
consumers scan every block; a finding remains live until a later block resolves it by stable ID.

---

## spec — 2026-08-15 — rev `.project/completed/20260816_qualified-reference-occurrence-anchoring/spec.md`
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

## spec — 2026-08-15 — rev `.project/completed/20260816_qualified-reference-occurrence-anchoring/spec.md`
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

## spec — 2026-08-15 — rev `.project/completed/20260816_qualified-reference-occurrence-anchoring/spec.md`
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

## design_review — 2026-08-15 — rev `.project/completed/20260816_qualified-reference-occurrence-anchoring/design.md`
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

---

## phase7-reverification — 2026-08-16 — rev `d61ac58`

Point (re-derived): Evidence for exact occurrence ownership must distinguish observed-and-passed
from unmeasured population, while an unavailable exact leaf refuses instead of falling back to a
positional source. [sources: `.project/product/P-002-exact-owner-anchoring.md` and
`docs/architecture/modeling-assumptions.md:704-741` (agent/ratified); serves
`.project/product/P-001-design-search-free-variation.md:11-18` (owner-verbatim)]

Falsifier: a root observes a one-segment leaf and later refuses, but the retained census reports
zero or complete coverage; or any retained claim says every corpus leaf was measured while the
census names residual unmeasured roots.

Findings:

- phase7-reverification-F1 [DON'T] The repaired JSON correctly reserves 15 roots as partial or
  unmeasured, but `tests/unit/test_direct_reference_unknown_leaf.py:15-19` still says the census
  measures every one-segment leaf, `audit.md:155-158` and `verification/README.md:232-243` use the
  census to support corpus-wide no-authored-model/no-regression claims, and `spec.md:6-10` says no
  artifact claims whole-population coverage. Those claims are stronger than the retained
  measurement and contradict one another. — ADR-009,
  `docs/architecture/modeling-assumptions.md:711-730` (agent/ratified) — falsifier: the retained
  totals say `population_claim: observed only` and `residual_unmeasured_roots: 15` while the kept
  test says every leaf was measured — disposition: DISPOSE — narrow all claims to the 770 observed
  resolver calls and preserve the 15-root residual explicitly.

- phase7-reverification-F2 [DON'T] The census documentation defines `measurement: none` as
  “elaboration never started,” but the code assigns `none` after any refusal with zero resolver
  observations; retained rows include in-run elaboration failures such as `item4_require`'s
  `ElaborationInvariantError`. The totals remain honest, but the per-root state meaning is false.
  — ADR-009, `docs/architecture/modeling-assumptions.md:711-730` (agent/ratified) — falsifier: an
  elaborator is constructed and `run()` raises before its first direct-reference call, yet the row
  says `none` under a definition that claims elaboration never started — disposition: DISPOSE —
  define `none` as zero resolver observations before refusal, and split pre-run from in-run refusal
  only if that distinction is needed.

Smells: **Smell 1 — two representations must be manually kept synchronized** fires and escalates
the gate: the coverage statement copied into the JSON vocabulary, test docstring, audit, README,
and spec has already drifted. Smells 3, 4, 5, and 6 did not fire in this bounded repair.

Checks:

- Fresh licensed census output was byte-identical to the retained JSON: 154 roots, 139 complete,
  1 partial, 14 unmeasured, 770 observed leaves, 0 observed absent leaves, 15 residual roots.
- The focused runtime boundary test passed (`1 passed`); it proves fail-closed behavior but does
  not prove whole-population census coverage.
- Ruff check and format check passed for `absent_leaf_census.py`; `d61ac58` changes no `src/` or
  `tests/` file.

Not checked: findings 2, 3, 4, and 7; the full suite was not rerun; snapshot routes, historical
captures, unseen leaves in the 15 residual roots, and unrelated self-binding work in `d61ac58` were
outside this pass.

Gate: DISPOSED (phase7-reverification-F1, phase7-reverification-F2)

---

## phase7-reverification disposition — 2026-08-16

- `phase7-reverification-F1` — **resolved.** The test docstring, verification README, audit, spec,
  plan, and current-work record now state 0 absent among 770 observed resolver calls and preserve
  the 15-root residual. No current artifact claims whole-corpus authored reachability.
- `phase7-reverification-F2` — **resolved.** `measurement: none` now means no resolver-boundary call
  was observed before refusal, including a run that raised before its first direct-reference call.

Disposition: both findings closed. The DISPOSED gate above remains the historical result of the
`d61ac58` lens run.

---

## final-audit — 2026-08-16 — rev `working tree at 00825a1`
Epic: ELABORATE-FIRST

Point (re-derived): One modeled source occurrence must become exactly one runtime source reaching
every and only its bound consumers; when the exact owner cannot select one occurrence, elaboration
must refuse by name rather than substitute a positional value. Evidence for that promise must state
what was observed and preserve what was not measured. [sources:
`.project/product/P-002-exact-owner-anchoring.md` (agent/ratified), serving
`.project/product/P-001-design-search-free-variation.md:11-18` (owner-verbatim);
`.project/backlog/epic_elaborate_first_architecture.md:31-33,84-86` (owner); ADR-009,
`docs/architecture/modeling-assumptions.md:704-741` (agent/ratified)]

Falsifier: mutating one usage-owned source changes a non-bound consumer or misses a bound one; an
unindexed arrayed owner silently chooses a value; or retained evidence reports complete/no-absence
coverage while any measured root remains partial or unmeasured.

Findings:

- final-audit-F1 [DO] The retained before/after ledgers record the codegen revision but not the
  editable `agentic-mbse` companion revision, so their historical dependency provenance remains
  incomplete. The current companion is clean at `1decd9525888265b3eabf2811a8aaabbd1678020`, the
  revision used by the independent re-audit, but that does not retroactively prove the original
  capture's checkout. — evidence-integrity inference (none) — disposition: DISPOSE — preserve this
  as the certification's historical-provenance residual; it does not contradict an owner or
  `[HARD]` product obligation and does not require changing shipped behavior.

Audit finding dispositions:

- **2 — CLOSED for this item by owner disposition.** The deep-override lane remains explicitly
  unevidenced and empirically bounded, not promoted to proof. The owner accepted the gap as-is and
  required no further authoring attempt or follow-up (`plan.md:1040-1044`); P-002 carries the bound
  through archival.
- **3 — DISPOSED to the owner-directed follow-up.** Scalar direct-reference policy and its named
  refusal remain shipped and pinned. The owner accepted that policy for this item and filed
  `[ANCHORING-ARRAYED-DIAGNOSTIC]` (`.project/backlog/BACKLOG.md:425-441`) for the author-facing
  diagnostic split.
- **4 — CLOSED.** The live self-binding spec now says the shipped resolver honors the exact usage
  owner (`../self-binding-replacement/spec.md:54-62`), and its success criteria and `[HARD]` rows
  agree (`:69-81,134-153`). The unchecked SC14 box is tracking lag, not a live contradiction.
- **7 — DISPOSED as `final-audit-F1`.** It remains a traceability limit, not a product block.

Census judgment: no coverage claim remains stronger than the measurement. The retained JSON says
154 roots, 139 complete, 1 partial, 14 unmeasured, 770 observed calls, 0 observed absent leaves, and
15 residual roots; `population_claim` says `observed only`. The promoted population is now frozen in
`verification/promoted_roots.json`, so later fixtures cannot silently change the census. A current
ledger rerun differs from the retained capture only in `s5_sibling_formal`'s refusal text because
later commit `00825a1` replaced a raw graph-validation error with the named
`ElaborationDiagnosticError`; semantic and identity totals are unchanged.

Resolves:

- independent-audit-F1: DEFERRED — authority: owner — basis: scalar arrayed-owner policy accepted
  for this item; author-facing diagnostic reconciliation filed as `[ANCHORING-ARRAYED-DIAGNOSTIC]`.
- phase7-reverification-F1: FIXED — authority: agent/ratified — basis: every current claim is
  bounded to 770 observed calls and preserves the 15-root residual.
- phase7-reverification-F2: FIXED — authority: agent/ratified — basis: `none` now means no
  resolver-boundary call was observed before refusal.

Smells: Smells 3 and 6 remain mechanically present at the arrayed spelling split, but are explicitly
disposed for this item by the owner's accepted scalar policy and named follow-up. The historical
Smell 1 is also explicitly disposed for this gate: the JSON is the canonical measurement, its
machine-readable claim carries the residual, the frozen promoted-root manifest prevents population
drift, and every current prose summary agrees with that bound. The summaries remain duplicated, so
future disagreement reopens the smell; there is no current product contradiction. Smells 4 and 5 do
not fire. The exact-owner fan-out test prevents a passing result assembled from separate routes.

Checks: focused licensed product falsifiers passed, **4 passed**: exact source fan-out, scalar direct
sum, arrayed-owner loud refusal, and unknown-leaf loud refusal. The current companion checkout is
clean at the revision named above.

Gate: DISPOSED (final-audit-F1) — passing gate; no unresolved BLOCK and every fired smell has an
explicit disposition.

Certification: **The item may be certified and closed.** Carry `final-audit-F1` as the stated
historical-provenance residual; do not read it as proof of the original companion checkout.

---

## final-audit tracking disposition — 2026-08-16

The final certification reconciliation checked SC1 and SC14, completed the two remaining Phase 5
tracking items, and updated the spec, design, plan, adjudication, and audit statuses. The tracking
lag named in the final-audit block is resolved. Gate remains **DISPOSED (passing)** with no BLOCK.
