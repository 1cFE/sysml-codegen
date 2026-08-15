# Product-lens ledger — unit-lane-port-metadata

Append-only. Verdict blocks land verbatim; resolutions cite stable finding IDs.

## spec — 2026-08-13 — rev `.project/active/unit-lane-port-metadata/spec.md`
Epic: CONSTRAINT-SEMANTICS

Point (re-derived): One modeled design attribute remains one public entry source across calculation, constraint-formal, and computed-attribute consumers; its exact unit metadata is established before projection and travels identically through live and snapshot routes, while genuine metadata disagreement still refuses. [source: `.project/backlog/epic_constraint_semantics_contract.md` Item 8; `docs/architecture/modeling-assumptions.md` §§2–3; `docs/architecture/overview.md`; `docs/architecture/reference/27-snapshot-generation.md`, grade: agent/ratified]
Falsifier: A shared attribute projects with `unit=None` on one supported consumer lane, mints different units by route, splits into duplicate entry points, or admits genuinely unequal unit metadata.

Findings: none. The spec preserves the standalone delivery boundary, exact-unit behavior, fail-closed disagreement, three-route parity, conditional single recapture, and Item 6 evidence gate without narrowing the ruled A5/A6/A9 follow-on.

Gate: CLEAR

Parent-epic finding references:
- `.project/active/constraint-semantics-contract/product-lens.md` `spec-F1` — source grade: agent/ratified, INHERITED
- `.project/active/constraint-semantics-contract/product-lens.md` `spec-F2` — source grade: agent/ratified
- `.project/active/constraint-semantics-contract/product-lens.md` `spec-F3` — source grade: agent/ratified
- `.project/active/constraint-semantics-contract/product-lens.md` `spec-F4` — source grades: owner-verbatim; agent/ratified
- `.project/active/constraint-semantics-contract/product-lens.md` `spec-F5` — source grade: agent/ratified
- `.project/active/constraint-semantics-contract/product-lens.md` `spec-F6` — source grade: agent/ratified
- `.project/active/constraint-semantics-contract/product-lens.md` `spec-F7` — source grade: INHERITED
- `.project/active/constraint-semantics-contract/product-lens.md` `spec-F8` — source grade: agent/ratified

## spec — 2026-08-13 — rev final provenance pass
Epic: CONSTRAINT-SEMANTICS

Point (re-derived): One modeled design attribute remains one public entry source across calculation, constraint-formal, and computed-attribute consumers; exact unit metadata travels identically through live and snapshot routes, while genuine disagreement refuses. [source: `.project/backlog/epic_constraint_semantics_contract.md` Item 8, grade: agent/ratified]
Falsifier: A supported consumer loses its unit, routes disagree, one source splits into duplicate entries, or unequal metadata is admitted.

Findings: none.
Prior verdict: PRESERVED — the provenance pass does not change or narrow the prior CLEAR judgment.
Gate: CLEAR

## spec — 2026-08-13 — rev post-review product-design gate
Epic: CONSTRAINT-SEMANTICS

Point (re-derived): Model authors keep the documented mental model: one modeled design attribute is one public entry source, authored units are documentation metadata rather than conversion behavior, and live and snapshot generation expose the same decided graph. This defect repair changes a valid model from an accidental metadata-collision refusal to admission without adding a user choice, workflow, command, API surface, or new unit semantics. [source: `docs/architecture/modeling-assumptions.md` §§2–3; `docs/architecture/overview.md`; `docs/architecture/reference/27-snapshot-generation.md`; `.project/backlog/epic_constraint_semantics_contract.md` Item 8, grade: agent/ratified]
Falsifier: The spec requires model authors to learn a new spelling or workflow, changes CLI/API behavior, introduces unit conversion or inference, changes the meaning of a shared entry point, or leaves a user-visible behavior choice for product design.

Findings: none. The revised recapture, verification-baseline, and Item 6 handoff rules are internal engineering and delivery controls. The only user-observable change restores the existing authored-unit and one-entry-source promises; no experience, mental-model, interaction-flow, UX, or API decision is hidden in the technical-design deferrals.

Product-design verdict: PROCEED — product design is unnecessary for this compiler metadata defect.
Gate: CLEAR

## spec — 2026-08-13 — rev complete-set Item 6 handoff
Epic: CONSTRAINT-SEMANTICS

Point (re-derived): One modeled design attribute remains one public entry source; authored units remain exact documentation metadata, and live and snapshot generation consume the same decided instance graph. Snapshot migrations must preserve that semantic authority rather than letting a subset stand for the retained corpus. [source: `docs/architecture/modeling-assumptions.md` §§2–3; `docs/architecture/overview.md`; `docs/architecture/reference/27-snapshot-generation.md`; `.project/backlog/epic_constraint_semantics_contract.md` Item 8, grade: agent/ratified]
Falsifier: The spec changes model syntax, unit meaning, CLI/API behavior, or interaction flow; merges Item 8's conditional v3 recapture into Item 6's future graph-v4 migration; or allows a count/subset gate to claim complete retained-snapshot coverage.

Findings: none. The handoff now carries exact sorted path sets as well as dated counts, requires Item 6 to re-derive and prove its own complete then-current graph-v4 path set, and leaves the proof mechanism to the later Item 6 design. Item 8 retains only its conditional v3 recapture duty. These are internal evidence and ownership controls; they neither narrow product intent nor introduce a UX, API, workflow, or product-design choice.

Product-design verdict: PROCEED — no product-design stage is needed.
Gate: CLEAR

## design-review — 2026-08-13 — rev `.project/active/unit-lane-port-metadata/design.md`

Point (re-derived): One modeled source must retain exact unit metadata across calculation, constraint-formal, and computed-expression consumers and through live and snapshot routes; unequal metadata must refuse. [source: `.project/backlog/epic_constraint_semantics_contract.md` Item 8; `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` D-2, grade: agent/ratified]

Falsifier: A supported lane loses or changes its unit, or v6 validation accepts a graph that `project()` rejects for conflicting port metadata.

Findings:
- design-review-F1 [DO] The design certifies projectability only in `capture_instance_graph_snapshot()`, leaving v6 envelope validation able to accept a re-sealed graph whose metadata collides during projection; the sealed graph therefore does not meet the documented projectable-authority guarantee — `docs/architecture/reference/27-snapshot-generation.md` (INHERITED) — disposition: revise D5 so envelope validation owns projection certification, capture consumes that guarantee, and a re-sealed-loader refusal test pins it.

Smells:
- 2 `consumer-compensates-for-producer-guarantee`: **FIRED** — capture compensates for the projectability guarantee claimed by `build_envelope()` and `load_instance_graph_snapshot()`; escalate into the stage judgment.
- 7 `invariant-ownership-changes-silently`: **NOT FIRED** — D5 explicitly names capture as the proposed owner, though design-review-F1 finds that ownership choice inconsistent with the durable snapshot contract.

Gate: DISPOSED (design-review-F1)

Recommendation: DISPOSE-and-proceed only through a design revision; Smell 2 requires the current design-review judgment to be Rework.

## design-review — 2026-08-13 — rev revised independent rerun

Point (re-derived): One modeled source must retain exact authored unit metadata across calculation,
constraint-formal, and computed-expression consumers and through live and snapshot routes; unequal
metadata must refuse, and Item 8 must not take Item 6's calc-provenance ownership. [source:
`.project/backlog/epic_constraint_semantics_contract.md` Item 8;
`.project/active/calcdef-constraint-gate-design/design.md` R5, grade: agent/ratified]

Falsifier: A supported constraint definition's formals never enter the unit selector; a supported
alias loses its referenced-declaration metadata; capture certifies a graph the envelope loader later
rejects; or generated-output evidence changes the graph/unit-only recapture trigger.

Findings:
- design-review-F2 [DO] The revised selector walks `ConstraintDefinition.features`, but the pinned
  SysIDE build exposes current constraint input formals through `ConstraintDefinition.usages`; a
  normal supported definition therefore supplies no candidates to the proposed closed map and
  cannot receive its exact unit metadata — `.project/backlog/epic_constraint_semantics_contract.md`
  Item 8 (agent/ratified) — disposition:
  `.project/active/unit-lane-port-metadata/design-review.md` RDR-1; design rework required.

Smells:
- 2 `consumer-compensates-for-producer-guarantee`: **NOT FIRED** — envelope build and decoded-load
  now own one projectability certifier; capture only consumes `build_envelope()`.
- 7 `invariant-ownership-changes-silently`: **NOT FIRED** — the revision explicitly distinguishes
  effective constraint-port identity, referenced-alias metadata, and Item 6's later calc-input
  `formal_provenance` ownership.

Resolves:
- design-review-F1: FIXED — authority: INHERITED/verified code and revised design — basis: D5 moves
  projection certification to the shared envelope build/load boundary and removes capture-local
  policy.

Gate: DISPOSED (design-review-F2)

## audit — 2026-08-13 — rev `62a07e5c870158672eb100f1cba73adfe4c9df28`
Epic: CONSTRAINT-SEMANTICS

Point (re-derived): One modeled design attribute has one public input identity even when several
consumers read it; authored units remain exact documentation metadata rather than conversion
behavior; and a v6 snapshot carries the already-decided, projectable instance graph without a
source-tree or licensed-parser dependency. [source: `docs/architecture/modeling-assumptions.md`
§2; `docs/architecture/reference/27-snapshot-generation.md` “Why”, “Three routes, one authority”,
grade: INHERITED]

Falsifier: A shared modeled attribute splits into consumer-specific public inputs, a supported
consumer loses or converts its authored unit, unequal unit text is admitted, or live and relocated
snapshot routes project different port metadata.

Findings: none. The frozen implementation makes declaration identity own unit selection, retains
the existing one-key projection/refusal law, and makes envelope build/load certify the same
projectability rule before capture can write. The A9 and radius customer shapes, both repaired
lanes' agreement/disagreement cases, and live/in-place/relocated routes exercise the falsifier.

Smells: none of the audit code/test smells fired. There is one unit-extraction rule, no
consumer-category exemption, snapshot replay consumes graph metadata without reconstructing it,
the known all-marker baseline does not preserve contradictory product behavior, and the tests do
not select among duplicate outputs or route interpretations.

Gate: CLEAR
