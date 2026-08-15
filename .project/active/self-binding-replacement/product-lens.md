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
