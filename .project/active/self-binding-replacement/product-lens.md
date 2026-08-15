# Product Lens — self-binding-replacement

Append-only ledger. One block per run, per `~/.claude/scripts/product-lens.md` §3. Never edit a
prior block; a changed gate is a new dated block. Gate consumers scan **every** block — any `BLOCK`
finding not later resolved by citation is still blocking.

---

## spec — 2026-08-15 — rev `9ce5548` / `.project/active/self-binding-replacement/spec.md`
Epic: ELABORATE-FIRST

Point (re-derived), three strands, all owner-grade:
1. **Publish the guidance, with two distinct-meaning replacements.** "publish the
   allowable-modeling-pattern guidance in `agentic-mbse` docs, including the `in R = R` diagnostic
   and its **two valid replacement forms with their distinct meanings**"
   [source: `.project/backlog/epic_elaborate_first_architecture.md:497-499` (`[OWNER-VERBATIM
   obligation]`), rooted in the 2026-08-05 `[OWNER-VERBATIM]` quote at `:71-72`; grade: **owner**]
2. **Mission invariant / Critical Success Factor.** "every consumed modeled value resolves to
   exactly one runtime source across all bound consumers; an unsupported authored form fails loudly
   before generation" [source: same file `:31-33` (inherited, owner grade) and Success Criteria
   `:78-80` (`[OWNER]` mission invariant): "public mutation reaches every and only the bound
   consumers"; grade: **owner**]
3. **Never reinterpret a self-binding as an outer reference; the replacement follows D-5/D-6/D-7
   referent semantics for the model's intended topology** [source:
   `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` D-4
   (`[OWNER-VERBATIM]`, 2026-08-05); grade: **owner**]
Serving promise: `P-001` (`[OWNER-VERBATIM, 2026-08-13]`) — parameters vary freely and viability is
assessed. A self-binding is the direct negation of it: the varied design parameter never reaches the
calculation and the viability number is confidently wrong. This item is squarely in service of
`P-001`; the findings below are about whether its criteria prove the service, not about direction.

Falsifier (described observable, non-code work): the guidance ships naming fewer than two
replacement forms, or names two without stating referents that differ; **or** the item completes with
the customer model generating clean while no evidence exists that a mutated design attribute now
reaches every bound consumer — i.e. the loud failure was removed without the value arriving.

Findings:
- spec-F1 [DON'T] Success criterion "the migration provably changes only the binding form: no
  arithmetic, no physical value, and **no semantic referent is altered**" (`spec.md:60-62`)
  contradicts D-4 on the literal reading: the self-binding's referent *is* the calculation's own
  formal (context-invariant, inert), so the replacement necessarily lands on a different feature —
  changing the referent is the fix, not a defect. Only a no-op migration satisfies the criterion as
  written, and a mechanical check built against it checks the wrong invariant. The intended reading
  ("the modelled value the author meant is unchanged") is a different claim and must be the one
  written down — `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` D-4
  (**owner-verbatim**) — disposition: **BLOCK** (clears on pinning the criterion's wording to the
  intended invariant, owner-visible because it restates an owner-verbatim ruling)
- spec-F2 [DO] The spec quotes the "two valid replacement forms with their distinct meanings"
  obligation (`spec.md:37-40`, `:74-76`) and claims sub-item 4 is covered **in full**
  (`spec.md:150-151`), but no success criterion carries the count or the distinctness: "states the
  supported replacement forms, what each one *means*" (`spec.md:53-55`) is satisfied by guidance
  documenting a single form. Separately, the obligation says **two** while D-4's migration note
  routes the replacement through **three** dispositions (D-5 bare-renamed, D-6 owner-qualified, D-7
  occurrence-rooted chain), which the spec lists at `:77-83` without reconciling the count. Under
  capture-fidelity law 4 that premise mismatch is surfaced, never smoothed into an unnumbered
  plural — epic `:497-499` (**owner-verbatim**) + contract D-4/D-5/D-6/D-7 — disposition: **BLOCK**
  (clears on a criterion that requires at least two supported forms whose referents provably differ,
  plus one line reconciling two-vs-three, owner-visible)
- spec-F3 [DO] Nothing obliges a newly measured form that resolves *not* as intended to fail loudly.
  Criterion 1 (`spec.md:48-52`) is record-only ("it is known and recorded whether it resolves as
  intended"), and the Non-Goal "Changing which forms are supported" (`spec.md:111-112`) can be read
  to foreclose adding a diagnostic. The epic exists because exactly such a form was legal, silent
  and inert; discovering a second one and only writing it in a doc repeats the defect the CSF
  forbids. Recording in guidance is not "fails loudly before generation" — epic `:31-33`
  (**owner**, inherited) — disposition: **BLOCK** (clears on a criterion routing any measured
  silently-mis-resolving form to a readiness diagnostic or a filed, owned gap)
- spec-F4 [DO] No criterion proves the migration delivers the point. The fusion-tea gate is
  "generates, seals, and captures a snapshot ... with zero readiness diagnostics"
  (`spec.md:58-59`) — an absence-of-diagnostic gate, i.e. proof the loud refusal is gone, not proof
  the modelled value now arrives. The `[OWNER]` mission invariant asks for "public mutation reaches
  every and only the bound consumers", and the epic's own gate rule (`:84-86`) requires an
  observable public behaviour, "never artifact-to-artifact fidelity". Criterion 1's
  reaches-every-consumer language is scoped to the per-form probe table, not to the migrated
  customer model — epic `:78-80` (**owner** mission invariant), `:84-86` (`[AGENT]` ratified) —
  disposition: **BLOCK** (clears on a mutation-propagation gate on the migrated model; pairs with
  spec-F1, which is the same missing model of what the migration does, seen from the other side)
- spec-F5 [DON'T] The parked keep-versus-revert decision (`spec.md:120-127`) is **acceptable as
  parking** — it is surfaced in daylight, the decision is named as the owner's, nothing is pushed or
  merged, and capture-fidelity law 4 asks for exactly that rather than a silent resolution. It is
  **not neutral**, though, and the spec's claim that "the outcomes above are the same either way"
  overstates: the executed `fusion-tea` branch is `self-binding-migration-qualified-refs`, i.e. it
  has already committed to the D-6 owner-qualified form — which is the form the spec's own `[HARD]`
  row (`:87-89`) says is refused with `SI_OCCURRENCE_AMBIGUOUS` under repeated subsystems — while
  "which replacement form should be the recommended default" is still listed as open
  (`spec.md:132-134`). Keeping the work therefore pre-decides a deferred mechanism choice. Also
  note the spec's `[HARD]` rows are measurements taken by that same unreviewed work — evidence
  survives a revert, but it must be reviewed as evidence, not inherited as settled —
  `claude-pack/rules/workflow-accountability.md` + capture-fidelity law 4 (**owner**-authored
  process rules) — disposition: **DISPOSE** — record that keeping the work reopens the default-form
  question for explicit design ruling, and that criteria 2 and 4 gate on review, never on the
  branches' own assertion. No BLOCK: the process fact already occurred and the spec discloses it.
- spec-F6 [DO] The Item-8 split leaves part of sub-item 1 unowned. The spec claims "the
  model-migration half of sub-item 1" (`spec.md:150-151`), but sub-item 1 as written
  (epic `:488-491`) is regeneration: packages/contracts regenerated, duplicate-field workarounds
  removed, "new study lineage where identity changed", TEAx compatibility through stock APIs. Its
  Non-Goals carve out sub-items 2, 3 and 5 only — the remaining half of sub-item 1 is attributed to
  a "regeneration item" (`spec.md:135-138`) with no path, while Item 8's declared home
  `.project/active/elaborator-downstream/` does not exist. The concrete orphan is the acceptance pin
  re-anchoring (9 channels published against a certified pin expecting 11), parked as open. Nothing
  currently owns "the identity changed, so the study lineage changes" — epic `:488-491`, `:502-506`
  (`[AGENT]` ratified epic scope) — disposition: **DISPOSE** — name the owning item (create it, or
  state in the spec that the remainder stays with Item 8 at its declared home) before design.

Smells: none of the seven fire — this is a spec, and the two design smells (2, 7) have no mechanism
to bite yet. Flagging forward for `_my_design_review`: smell 7 (ownership of an invariant moving
without saying so) is the live risk in spec-F3 — if the design settles on "the guidance teaches it"
for a form the route cannot resolve, the loud-failure invariant has silently moved from the
generator to the reader.

Gate: **BLOCKED** (spec-F1, spec-F2, spec-F3, spec-F4) · DISPOSED (spec-F5, spec-F6)

## spec — 2026-08-15 — rev 3 / .project/active/self-binding-replacement/spec.md
Epic: ELABORATE-FIRST
Point (re-derived): Establish and document the right binding pattern for each situation, migrate affected models, detect `in R = R`, and never reinterpret its self-referent as an outer value. [source: `.project/backlog/epic_elaborate_first_architecture.md` Item 8 and owner ruling; `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` D-4; grade: owner]
Falsifier: Guidance leaves a situation without a correct positive pattern, or a migrated model generates without an off-default mutation reaching every and only the intended consumers.
Findings:
- None. DON'T: rev 3 preserves D-4 referent semantics and does not retain the false replacement-form count. DO: its situational guidance, dual-path detection, measured-form disposition, bounded migration, and fusion-tea mutation spine carry the owner obligation.
Resolves:
- spec-F1: FIXED — authority: owner — basis: the migration criterion now explicitly changes the referent from the self-input to the intended modeled value while preserving model meaning.
- spec-F2: FIXED — authority: owner — basis: the epic records the owner's 2026-08-15 provenance correction; no fixed form count governs, and the spec distinguishes D-5, D-6, and D-7 by situation.
- spec-F3: FIXED — authority: owner — basis: any newly measured silently wrong form must receive a contained repair or a named, owned follow-on; documentation alone cannot dispose it.
- spec-F4: FIXED — authority: owner — basis: the leading criterion requires off-default mutation on migrated fusion-tea data to reach every and only its bound consumers.
- spec-F5: FIXED — authority: owner — basis: the owner ordered `REVERT ALL`; the branches were deleted and their measurements are explicitly non-settled evidence pending re-establishment.
- spec-F6: FIXED — authority: agent/ratified — basis: the spec names the regeneration remainder, its contents, and its owner/home under ELABORATE-FIRST Item 8.
Gate: CLEAR

## design — 2026-08-15 — `.project/active/self-binding-replacement/design.md`
Epic: ELABORATE-FIRST

**Process caveat, surfaced not smoothed.** The lens run could not read
`~/.claude/scripts/product-lens.md` — the session sandbox denies both `Read` and `Bash` outside
`/home/reid/1cfe/sysml-codegen`. It reconstructed the §3 ledger format and the §4 seven-smell set
from the ~20 prior ledger blocks in `.project/`, recovering the set as: 1 two-representations,
2 consumer-compensates-for-producer, 3 special-category-exempts, 4 downstream-knows-internal-
representation, 5 baseline-preserves-contradiction, 6 test-selects-one-route, 7 invariant-ownership-
moves-silently. If §4's wording differs, the smell judgments below need a re-read, not the findings.
*Reviewer note:* `/_my_design_review` Stage 0 step 5 independently names the two design-level smells
as "a consumer compensating for a producer or platform guarantee" and "a solution that changes who
owns an invariant without saying so" — smells 2 and 7 as reconstructed. The reconstruction is
corroborated on the part that carries the gate.

Point (re-derived), four clauses, owner grade: know which authoring pattern is right **for each
situation**, document those patterns in `agentic-mbse` docs, fix the models to use them, and detect
`in R = R` as the wrong pattern [source: `.project/backlog/epic_elaborate_first_architecture.md`
`[OWNER-VERBATIM 2026-08-15]`, superseding the 2026-08-05 wording and carrying **no** form count;
grade: **owner**]. Bounded by the inherited Critical Success Factor: every consumed modelled value
resolves to exactly one runtime source across all bound consumers, and an unsupported authored form
fails loudly before generation [`:31-33`, inherited owner grade], with the `[OWNER]` mission
invariant adding the observable — public mutation reaches **every and only** the bound consumers
[`:84-86`]. Referent semantics fixed by D-4 `[OWNER-VERBATIM]` with D-5/D-6/D-7 `[AGENT] (ratified
by owner, 2026-08-05)` [`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:604-627`].
*Reviewer note on citations:* the lens cited `epic:59-66`, `:499-505`, `:78-80`; the reviewer
verified the same statements at `:31-33`, `:71-78`, `:84-86`. Same statements, drifted ranges — the
Item-8 stocktake already named epic line-range drift as a recurring failure mode
(`.project/research/20260815-103905_item8-bounded-stocktake.md:313-315`).

Serving promise: `P-001` `[OWNER-VERBATIM, 2026-08-13]` — parameters vary freely, viability is
assessed. A self-binding is its direct negation. The design is squarely on this point; every finding
is about whether its evidence proves the service, not about direction.

Falsifier (observable): the item completes with fusion-tea generating clean while no evidence exists
that a mutated design attribute reaches its bound consumers for the formals the spine does not
touch; **or** the published guidance leaves a situation without a correct positive pattern; **or** a
taught shape's stated behavior is not the behavior of the shipped route at the landing commit.

Findings:

- design-F1 [DO] **The spine proves arrival for 1 of 11 renamed formals and 1 of 3 migrated design
  files.** The mutation check is `gain` in `designs/generic_ife/ife_plant.sysml` (Validation
  Approach; "The spine mutation check"). The migration renames 11 distinct formals across 15 sites
  in three design files (Appendix A). For the other ten — including everything in
  `designs/hif_ife/hif_plant.sysml` and `hif_driver.sysml` — the only evidence is "generates, seals,
  snapshots with zero readiness diagnostics", which the design itself correctly labels "necessary
  evidence, not sufficient". That is the absence-of-diagnostic gate the epic's product-behavior rule
  forbids (`epic:84-86`, "never artifact-to-artifact fidelity") and that this ledger's own `spec-F4`
  blocked once at spec scope. It reappears one level down: closed for `gain`, open for the rest. The
  residual silent failure mode is real — a renamed formal whose bare right-hand side resolves to a
  same-named attribute in an *enclosing* scope produces no diagnostic and a wrong value, and D5's
  precheck inspects the **declaring def** for member collisions, not the usage-side resolved
  referent. Cheap to close: one regeneration, then assert all 11 supplying attributes appear as
  entry points keyed on the supplying attribute's display path (B5's rule), plus one off-default
  mutation outside `ife_plant.sysml` — `epic:84-86` (**owner** mission invariant) — disposition:
  **BLOCK** (clears on an arrival check enumerating all 11 renamed formals plus one mutation in a
  second design file)
- design-F2 [DO] **D1 dissolves duplicate teaching but not the duplicate pointer, in the exact pair
  it cites as drifting.** One authoritative copy removes the teaching from both `claude/` and
  `.claude/`, but the pointer plus D2's one-paragraph inline summary must now be planted in both,
  and Component Overview treats `.claude/` as "the same treatment for whatever it finds". The
  mechanism that produced Item 7's A-1 residual is left in place at reduced size, and no decision
  says which agent tree is authoritative or whether one is generated from the other. **Smell 1**,
  escalated. The design's own inventory could not reach `.claude/`, so the size of the duplication
  is unknown as well as unowned — disposition: **DISPOSE** — the plan states, after the `.claude/`
  inventory, which tree is authoritative and whether the pointer is duplicated deliberately or
  generated
- design-F3 [DO] **What CI holds for F-4 is not what the design says it holds.** Potential Risks
  answers the forward-flagged smell 7 with "the sideways shape gets a tracked fixture and a
  conformance assertion, so the sentence in the guidance describes something CI holds". A fixture
  pins that `'Unit'::cost` **resolves** into a sibling subtree. It cannot pin that the author meant
  the sibling. The gap between resolution and intent stays with the reader — the honest position,
  and it should be stated as such. The upstream "characterised, not a defect" call is `[AGENT]`
  (`spike/findings.md:171-177`) and rests on "it is the only occurrence in the model", a property of
  the probed fixture, not of the rule. The design does **not** smuggle this — it names the risk in
  daylight, which is why smell 7 does not fire — disposition: **DISPOSE** — state plainly what the
  fixture asserts (resolution) and what the reader still owns (intent), and record why spec
  criterion 3 does not bind F-4 (D-6 is a *supported* form per contract)
- design-F4 [DO] **A Non-Goal hardens an agent-grade ratified choice into do-not-relitigate.**
  "Reopening D-4 through D-7, or the choice of D-5 for the fusion-tea sites." D-4 is
  `[OWNER-VERBATIM]` and correctly settled. D-5/D-6/D-7 and the D-5-for-fusion-tea recommendation
  are `[AGENT] (ratified by owner, 2026-08-05)`, which capture-fidelity §1 makes challengeable by
  re-deriving against recorded reasoning — and the reasoning **did** change: the `[HARD]` row was
  re-measured and corrected on 2026-08-15. The choice of D-5 still looks right on its merits, so
  this is wording, not direction. As written it is the "WE MUST NOT ⟨suggestion⟩" shape
  capture-fidelity §3 names — disposition: **DISPOSE** — split the Non-Goal: D-4 settled (owner),
  D-5-for-these-sites recorded as a decision with its reasoning, challengeable on evidence
- design-F5 [DO] **The third `gain` consumer is a constraint, and the wording invites a check that
  drops it.** `tests/fixtures/fusion_tea/designs/generic_ife/ife_plant.sysml:168` is inside
  `assert constraint viability : 'Viability Threshold'`; `:122` is `lcoe_calc` and `:146` is
  `recirc_calc`. The mechanism holds — `ConstraintNode` runs the same `_regular_inputs` /
  `_source_for_edge` path as a `CalcNode` (`elaboration/project.py:503-539`) and
  `_build_constraint_modules` (`:845`) emits it as a module. But "three consumer modules" written
  flat is easy to implement as "the three calc modules", dropping the one consumer class where
  "every and only" has historically been hardest; the constraint consumer additionally carries
  `formal_identity` (`project.py:543`) that the calc consumers do not — disposition: **DISPOSE** —
  name the constraint consumer explicitly in the spine check
- design-F6 [DO] **Required Invariant 7 asserts an agreement no mechanism in this repo can fail
  on.** D7 fixes agentic-mbse's `level2_structure.py:350` by mirroring codegen's identity
  comparison, with "one test per direction" — in agentic-mbse. Nothing in sysml-codegen fails if
  `extraction/source_evidence.py` later drifts from that mirror. Two independent implementations of
  one owner-verbatim rule (D-4) across two repos, agreement asserted as an invariant, neither side
  deriving from the other. **Smell 1**, second instance, escalated. Merging them is out of scope and
  should stay out; the fix is naming the invariant's owner — disposition: **DISPOSE** — state which
  repo owns the rule, which mirrors it, and where drift would be caught
- design-F7 [DON'T] **Verified holdings, recorded so the gate is not misread as a general
  negative.** F-3's diagnosis is exact and D6's scope is exactly right, not too narrow:
  `elaborate.py:631` is the *only* unguarded `validate()`/`require_projectable()` call site — the
  others all convert `GraphValidationError` into a CLI-caught class
  (`orchestration/exact_pipeline_context.py:248-253`, `elaboration/project.py:218-221`,
  `snapshot/envelope.py:307-313`, `snapshot/instance_graph.py:1015-1021`, `:1106-1110`). Opened as a
  suspected hole in Required Invariant 6; it closed. `GraphValidationError` carries `.diagnostics`
  (`graph.py:82-87`), so the Implementation Notes re-raise compiles as written. `_graph_failure`'s
  nameless payload is at `graph.py:945-952` as described. D8 is correct —
  `designs/hif_ife/hif_driver.sysml:100` still declares `part hif_driver_instance`, so R-2's subject
  is untouched. Appendix A/B check out against the migrated fixture. B5 is confirmed. D3's three
  promoted D-6 fixtures are not gold-plating: the in-repo corpus uses the D-6 form 85 times, and
  teaching its position rule while leaving it unpinned would reproduce the defect the item exists to
  end — disposition: **no action**

Smells (§4, all seven checked):

- **Smell 2 — consumer compensates for a producer/platform guarantee: DOES NOT FIRE.** Checked, not
  assumed. D7 moves compensation the correct direction: the name-based check that produced the F-2
  false positive is replaced in the *producer*, rather than by codegen tolerating a wrong flag.
  `make_d5_variant.py --root` widens addressing, not compensation.
- **Smell 7 — ownership of an invariant moves without saying so: DOES NOT FIRE.** The prior spec
  block flagged it forward on F-4's sideways reach. The design meets it head-on in a named "Where
  smell 7 could bite" subsection. The smell's hinge is *without saying so*, and this is said. The
  answer it gives is weaker than its own summary claims — that is design-F3 at DISPOSE, not a fired
  smell. Separately checked: confirm-only detection scope is **not** an ownership move, because it
  is `[OWNER 2026-08-15]` (`briefs/00-align.md:13-18`).
- **Smell 1 — two representations manually kept synchronized: FIRES twice, escalated.** design-F2
  (the `claude/` ↔ `.claude/` pointer pair) and design-F6 (codegen ↔ agentic-mbse self-named checks).
  Both disposed, neither blocking.
- **Smells 3, 4, 5, 6 — do not fire.** No special category exempts a case whose meaning is
  unchanged; the spine reads public generated artifacts rather than `InstanceGraph` internals;
  nothing preserves a contradicting baseline (byte-identity-after-strip against the originals is the
  opposite pattern); checks assert by diagnostic name and entry-point value, not by route selection.

Gate: **BLOCKED** (design-F1) · DISPOSED (design-F2, design-F3, design-F4, design-F5, design-F6) · DON'T (design-F7)

---

## spec — 2026-08-15 — rev 4 / `.project/active/self-binding-replacement/spec.md`
Epic: ELABORATE-FIRST

Point (re-derived): A freely varied design parameter must reach its intended semantic source
occurrence so viability evidence remains trustworthy; this item must establish, document, and
migrate the right patterns, detect `in R = R`, and never reinterpret its self-referent as an outer
value. [source: `.project/product/P-001-design-search-free-variation.md`;
`.project/backlog/epic_elaborate_first_architecture.md` Item 8;
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` D-4; grade: owner;
D-5–D-7 replacement semantics: agent/ratified]

Falsifier: Guidance presents positional slot search as D-6 language semantics, or a taught
replacement resolves to a competing occurrence or misses the exact usage owner, so an off-default
mutation fails to reach every and only the intended consumers.

Findings:

- None. Rev 4 removes the positional implementation defect from the modeling rule, preserves D-5
  and D-7 guidance, and requires any D-6 teaching to follow SysIDE's resolved owner after the
  separately owned exact-owner repair.

Smells: none.

Gate: CLEAR
