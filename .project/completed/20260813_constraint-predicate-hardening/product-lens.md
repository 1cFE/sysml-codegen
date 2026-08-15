# Product-lens ledger — constraint-predicate-hardening (CONSTRAINT-SEMANTICS Item 4)

Append-only. Verdict blocks land verbatim; dispositions are recorded in the spec/design they amend.

---

## spec — 2026-08-13 — rev e4bbb2a (+ untracked `.project/active/constraint-predicate-hardening/spec.md`)
Epic: constraint-semantics-contract (CONSTRAINT-SEMANTICS, Item 4 — Predicate Defect Hardening)

**Runner note:** `/home/reid/.claude/scripts/product-lens.md` and its pack source
(`claude-pack/scripts/product-lens.md`) are outside this session's sandbox and were refused, so the
lens was run from its stated purpose — an independent two-direction check (does the WORK
contradict/narrow the product point; does it omit an obligation the point requires) — in the ledger
format used by the sibling ledgers `.project/active/constraint-coverage-policy/product-lens.md` and
`.project/active/constraint-semantics-contract/product-lens.md`. The companion checkout
`/home/reid/1cfe/agentic-mbse-item7-rebuild` was **not** read (same restriction the spec surfaces),
so no companion-side claim below is first-hand; every codegen and docs line cited was opened this
session.

**Existing epic finding carried forward (grade preserved, not restated):**
`constraint-semantics-contract/product-lens.md` **spec-F6 [DO]** — the Q4 predicate restriction had
to be stated as *predicate-body-only*, with binding-position chains and inline asserted forms still
admitted — **(agent/ratified)**; disposed into the umbrella spec's Q4 requirement (`spec.md:139-143`).
Item 4 sits directly on top of that disposition.

**Point** (re-derived from SOURCES; the WORK was opened only after the sources were read):

1. Constraints exist to make design search viable — a search must be able to tell a candidate that
   passed its physics gates from one nobody checked. [source: `rulings-20260812.md:13-15`
   **[OWNER-VERBATIM]**; grade: owner]
2. Narrow bands of viability make exploration hard, so the product must instruct *when* an equality
   should be used at all, not only how the pipeline treats one; equality intent is authored as a
   tolerance band, and no equality executes. [source: `rulings-20260812.md:16-18`
   **[OWNER-VERBATIM]** + contract "Equality intent and authoring policy":512-541 and invariant
   11:159-160; grade: owner for the instruction obligation, agent/ratified for the block]
3. Enforcement is assert-only; the gate shape is bindings-only over formals, chains in the predicate
   body stay blocked and chain admission is a *filed future capability*, not a closed door. [source:
   Q4; umbrella `spec.md:134-143`; grade: agent/ratified]
4. Every authored usage stays visible with exactly one disposition, and no report or label claims
   more coverage than was assessed. [source: contract invariants 1/28/32/33; ADR-009
   (`docs/architecture/modeling-assumptions.md` §9); grade: agent/ratified]
5. When the profile refuses a predicate, it **names the construct** so the modeler can act.
   [source: `constraint-execution-and-design-space-studies.md:195` (ratified concept);
   `docs/architecture/modeling-assumptions.md:538` "the generation error names the exact construct
   to fix"; grade: agent/ratified]

**Falsifier:** a landing in which the item's own fixtures elaborate but the model still refuses to
generate (so no gate is ever assessed); or the cured lane produces a usage with no catalog carrier
or an unassessed gate under a satisfied-looking label; or the diagnostic names the offending
reference but directs the modeler onto a route that itself refuses; or the item's demonstrated
authoring shape teaches an equality the ratified policy says never to write.

### Findings

- **item4-F1 [DO] — the item's own reproduction shape cannot execute under the landed contract, and
  Success Criterion 1 pins the absence of one error code rather than a working gate.** The Problem
  states the reproduction as `assert constraint { bioshield.outer_radius == 8.55 [m] }`
  (`spec.md:18`) and concludes "A modeler who writes the *supported* form today is stopped by a bug
  (A)" (`:46-47`). That predicate is unsupported on two independent, already-published counts.
  First, `bioshield.outer_radius` is a feature chain **in the predicate body** — the exact
  construct Defect B's block exists to refuse (Q4, umbrella `spec.md:134-143`, carried there by
  this ledger's epic-level **spec-F6 (agent/ratified)**). Second, it is a bare equality on a
  quantity-typed operand: contract invariant 11 says "No equality or `!=` executes… numerical
  equality blocks until a separate exactness/tolerance contract exists" (`:159-160`), and the
  landed block list names it `block_real_equality_requires_tolerance`
  (`docs/architecture/modeling-assumptions.md:480-487`). So Success Criterion 1 — "elaborates
  without `SI_OCCURRENCE_MISSING`" (`spec.md:51-54`) — is satisfiable by a fixture whose model
  still refuses generation on a *different* named block, one line later. The criterion would go
  green while the lane the item exists to open stays shut. This also runs against the owner's
  equality statement in the direction the owner argued: hardening `==`-with-a-unit as the pinned,
  test-blessed demonstration makes the zero-measure form the worked example, while the ratified
  taxonomy says to write a band (contract `:526-541`; owner-verbatim `rulings:16-18`), and Item 5
  is about to copy an authoring shape 65 times. — source: contract invariant 11 (agent/ratified),
  Q4 (agent/ratified), owner-verbatim equality statement (owner) — **disposition:** restate the
  reproduction in a Q4-supported shape — a band inequality over a formal or local name carrying the
  unit-annotated literal — and strengthen SC-1 from "no `SI_OCCURRENCE_MISSING`" to "the model
  elaborates *and* generates, and the annotated gate is assessed", so no other block can stand in
  for the cured one. Keep the chain/equality reproduction if it is wanted, but label it as the
  defect's discovery shape, not as "the supported form".

- **item4-F2 [DO] — the rewrite the new diagnostic will advertise runs through the one lane the
  item leaves optional.** Defect B's criterion is that the message "states the supported rewrite
  (bind the chain to a formal in the usage; use the formal in the predicate body)" (`spec.md:57-58`).
  The item's own Open Questions record that a unit-annotated literal *in binding position* —
  `in tol = 0.05 [m];` — is refused today as `SI_EXPRESSION_SOURCE_UNSUPPORTED`
  (`spec.md:148-156`; the classification path is `_binding_evidence`,
  `elaborate.py:1838-1846`, which falls through to `expression_evidence` for anything that is not a
  chain, a reference, or a literal node), and leaves curing it to design's pricing. Under Q4 the
  blessed way to express the equality intent in the moved-out predicate is a **tolerance band with a
  modeled tolerance** — that is, exactly `in tol = <value> [unit]`. So a modeler who follows the
  new, legible diagnostic can land on a second refusal, and the instrument Item 5's migration is
  performed with points into it. — source: Q4 band idiom + owner-stated "tolerances are modeled
  values" (`contract:522-525`, owner-stated); concept `:195` "names the construct and blocks
  generation" (agent/ratified) — **disposition:** make it a criterion, not an open question: either
  the binding lane is cured in this item, or the advertised rewrite is written so its own path is
  reachable today (and the known refusal is named in the advice). Design may still choose which,
  but the spec should not let the diagnostic promise a route the spec knows is broken.

- **item4-F3 [DO, low] — the cured predicate's end state is never named, so the item stops one step
  short of the point it serves.** All of Defect A's criteria and requirements stop at elaboration
  (`spec.md:51-54`, `:74-93`). Nothing states what the newly-elaborating usage must be at the end:
  one catalog carrier with one disposition (contract invariants 1/28, landed as
  `ConstraintUsageRecord` per authored usage, `elaborate.py:1130-1185`), counted in the feasibility
  denominator, and assessed rather than silently unassessed under Item 3's coverage accounting. The
  item is opening a lane straight into the machinery Items 2–3 just landed, and its evidence
  contract does not cross that seam in either direction. — source: contract invariants 1/28/32/33;
  ADR-009 (`modeling-assumptions.md` §9) (agent/ratified) — **disposition:** one added criterion:
  the cured fixture's usage appears in the catalog with the expected disposition and the report's
  coverage counts it as an assessed gate. This is the same end-to-end bar Item 3 wrote for itself.

- **item4-F4 [DO, low] — the published promise Defect B discharges is not cited, and it is the bar
  to match.** Two durable statements already say what the diagnostic must do: the ratified concept,
  "the executable profile **names the construct** and blocks generation"
  (`constraint-execution-and-design-space-studies.md:195`), and the landed modeling policy, "If the
  profile BLOCKs an asserted constraint, the generation error names the exact construct to fix"
  (`docs/architecture/modeling-assumptions.md:538`). The spec cites neither; it reaches for a
  codegen-internal analogue instead (`SourceReferenceEvidence.written_text`, `spec.md:99-103`).
  That matters twice: the docs sentence is **false today** — it is exactly what
  `feature_chain: block_feature_chain` fails to do — so it is both the referent for B's criteria and
  a line a reader is currently misled by. — source: concept `:195`; modeling policy `:538`
  (agent/ratified) — **disposition:** cite both as the promise the item discharges, and record that
  `:538` becomes true (or state the wording change) with the fix. No behavior change implied.

### Smells

- **A test that passes only because it selects one interpretation: FIRES**, on item4-F1. A
  code-absence criterion ("without `SI_OCCURRENCE_MISSING`") over a fixture that a second, unrelated
  rule also refuses is the textbook shape — it is the same signature the epic ledger recorded at
  **spec-F7 (agent/ratified)** for REQ-EXT-09. It escalates into this stage's judgment rather than
  sitting in a rubric.
- **Two representations kept in sync: does not fire.** Defect A's cure extends one existing rule
  with one owner (`extraction/unit_annotation.py`) to a third lane; the spec forbids a second rule
  or special case explicitly (`spec.md:76-78`), which is the right posture.

**Not findings (checked, clean):**
- **No owner-graded statement is contradicted.** D-1/D-2/D-3 are untouched — this item adds no
  post-build seam, no adapter, and no second authority. The owner-stated "tolerances are modeled
  values, the pipeline never invents one" is respected (the item invents nothing; item4-F2 is about
  reachability, not invention). The owner-verbatim equality statement is not contradicted either —
  item4-F1's equality point is about which shape gets demonstrated, not about a rule the spec
  denies.
- The `[HARD]` unit-annotation rule is carried **whole**, with its single owner named and with the
  "must not suppress the unit as a *unit*" half stated (`spec.md:86-90`) — the failure mode a
  narrow cure would have walked into, caught in the spec rather than in design.
- The `[INFERRED]` scope honesty on Defect A is exact: the walk only runs for
  `source_form in ("inline", "requirement_constraint")` (verified at `elaborate.py:1112-1117`), and
  the spec requires the characterization to say which lane it pins and to claim no other.
- The Item 2 disposition/severity contract is carried as a constraint, not a target
  (`spec.md:109-112`), and Non-Goals keep BLOCK-halts-generation semantics untouched — consistent
  with the landed code, where a BLOCK on an eligible usage becomes a graph diagnostic that strict
  elaboration turns into a halt (`elaborate.py:1097-1108`, `:520-521`).
- Chain admission stays a **filed future capability**, matching Q4's "not a closed door" wording;
  the Non-Goal is phrased as a decision record, not as a prohibition addressed at future agents.
- The owner-directed sequence (settle → fix docs/model with expectations captured → then run) is
  honoured in substance: kept characterizations land red **before** the fixes (`spec.md:60-61`,
  `:121-122`), and the byte-reversal-pinned CATF twins are protected (`:130-132`).
- The companion checkout's unreadability is **surfaced, not resolved** (`spec.md:166-174`), with the
  dependent conclusions marked as weaker evidence — capture-fidelity law 4 applied correctly.
- The determinism requirement is grounded in an existing precedent rather than invented
  (`_record_readiness`'s `(formal, code)` collapse, `spec.md:104-108`), and it is stated as a
  property of the identified reference *set and order*, which is the version that survives contact
  with the profile emitting 13 copies.

**Gate: DISPOSED (item4-F1..item4-F4) — nothing blocks.** No owner-graded statement is contradicted
and no Item 1 ruling is overturned, so no finding reaches BLOCK grade. **item4-F1 is the one to fix
in the spec text**: as written, the item can land fully green with the authoring lane it exists to
open still refused, because its criterion tests for the absence of one error code over a predicate
that two other published rules independently forbid. item4-F2 is the same class one layer out — the
cure's advice pointing at a route the spec itself records as broken. F3 and F4 each cost a sentence.
The shape running through F1, F3, and F4 is a boundary drawn one step too early: the item measures
elaboration where the product's promise is an assessed gate and an actionable message.

---

## design — 2026-08-13 — design-review stage (carried re-check, NOT a fresh lens run)

**Runner note:** the lens script was not re-run at this stage. This session's standing
instruction bars spawning subagents unprompted, and the script itself
(`~/.claude/scripts/product-lens.md`) is outside the sandbox — the same refusal the spec-stage
entry records. What follows is the design-reviewer re-checking the spec-stage findings against
`design.md`, not an independent second derivation of the Point. Graded accordingly: weaker
evidence than the entry above.

**Disposition of the spec-stage findings in the design:**

- **item4-F1 [DO]** — discharged. The demonstration shape is an inequality carrying a compatible
  unit-annotated literal, not `== <literal> [unit]`, and the pinned end state is a working gate
  (catalog carrier, `disposition_kind == "eligible"`, assessed, counted in coverage) rather than
  the absence of one error code. Design "Fixture Plan" + "Test Plan".
- **item4-F2 [DO]** — discharged by **D2**: the fourth lane (`in tol = 0.05 [m]`) is cured in
  this item, so the rewrite the new diagnostic advertises is reachable. Invariant 6 keeps the
  fallback (drop the annotation from the advertised rewrite) if P3 falsifies it.
- **item4-F3 [DO, low]** — discharged. The end state is named as a catalog carrier with an
  assessed disposition counted in the coverage account.
- **item4-F4 [DO, low]** — discharged, and the citation corrected: the promise is
  `docs/architecture/modeling-assumptions.md:535` (the ledger's `:538` was stale; `:535` verified
  at HEAD this session). The residue list required by success criterion 3 is present but
  **incomplete — `block_invocation` is missing** (design-review M3).

**Smells at design stage:**

- **A test that passes only because it selects one interpretation: fires weakly, again.** The
  `predicate_unit_annotation_incompatible` fixture is presented as guarding B2 (that D1 does not
  strip units from the profile), but the profile verdict is computed at `elaborate.py:403` from
  the companion's own extraction, independent of the reference walk D1 touches. The fixture
  therefore passes whether or not the walk drops the unit. It is a regression guard, not a
  discriminator. Escalated into the review's judgment as Advisory A1, not left in a rubric.
  Not BLOCK grade: the invariant it names is true by construction, so the item cannot land the
  failure the fixture was meant to catch.
- **Two representations kept in sync: does not fire** (unchanged from spec stage — one rule, one
  owner, invariant 1 forbids a stray `operator == "["` test elsewhere).
- **Consumer compensating for a producer guarantee: does not fire.** D3 puts the message where
  the block is decided and the location where the source is known.
- **Ownership of an invariant changing hands silently: does not fire.** The profile keeps
  deciding what is admitted; `extraction/unit_annotation.py` keeps owning the unit rule.

**Gate: DISPOSED — nothing blocks.** No owner-graded statement is contradicted; no finding
reaches BLOCK grade. Verdict carried into the design review: **Revise** on seven must-fix items,
none of which moves a seam.
