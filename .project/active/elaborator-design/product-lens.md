# Product-Lens Ledger — ELABORATE-FIRST Item 4 (Elaborator + Projection Design)

Append-only. Never edit a prior block; a changed gate is a new dated block.
Gate consumers scan **every** block: any `BLOCK` not later resolved by citation is still blocking.

---

## design-review — 2026-08-08 — rev `.project/active/elaborator-design/design.md` (working tree, base `6bed968`)

Point (re-derived): Every consumed modeled value resolves to exactly one runtime source per semantic source occurrence (declaration identity + concrete occurrence identity), and that identity is taken from what KerML/SysIDE already resolved while the model was loaded — reconstruction from owner/name/string fields is not an accepted authority; exactly one identity authority and one occurrence→definition bridge exist; unsupported authored forms fail loudly pre-generation.   [source: `.project/backlog/epic_elaborate_first_architecture.md:31-34,63-70,78-81` (mission invariant + owner rulings), `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:334-368` (invariants 54-60), `.project/concepts/constraint-execution-lifecycle-requirements.md:456-480,516` (LC-SI-02 [HARD], LC-SI-08/09/22), grade: owner/HARD]

Falsifier: The design would show identity produced, matched, keyed, or re-derived from a name string anywhere between "model is loaded" and "graph is built" (name-keyed declaration lookup, leaf-string chain-root search, name-reconstructed expansion, or a second identity map beside the bridge); or would let names re-enter before projection without saying what enforces the boundary; or would resolve a form whose referent depends on binding-owner context with one context-blind rule.

Assessment of the reopened design against that oracle: **it clears the falsifier.** Declaration identity is the SysIDE-resolved element UUID (D1); the chain resolver contextualizes the exact resolved root and is forbidden from searching by leaf (D5 + "Exact contextualization rules"); aggregation enumerates exact occurrence IDs and resolves an exact slot per occurrence rather than concatenating names; Required Invariants 7-9 and Appendix A cases 2/3/7 state the adversarial observables; Appendix A case 10 puts a mechanical guard (no `sanitize_name`, leaf extraction, rendered-path parsing, prefix matching, first-match) on the identity package. The referent table (LC-SI-02 [HARD]) stops being a rule codegen re-implements and becomes an upstream fact the design carries — the strongest thing in the document. The design's own research findings check out: `element_id` appears nowhere in either src tree today, and `ResolvedTargetFact` (`../agentic-mbse/src/agentic_mbse/sysml/data_models.py:53-69`) stores QNs while its docstring claims it "records the resolved element itself". The mechanisms behind the breadth audit's `audit-F1` and `audit-F2` are correctly identified and designed out.

Findings:
- design-F1 [DO] The revision states it "replaces the prior D1/D5/D6 mechanics" but the file also silently drops the prior design's projection contract (entry-point classification from value-site, `output_aliases`, execution order, constraint-catalog attachment, `fallback_entry_points` retirement + V11 invariant, ADR-003 name helpers), the diagnostic-code catalog (`SI_SELF_BINDING` / `SI_INDEXED_SOURCE_UNSUPPORTED` / `SI_EXPRESSION_SOURCE_UNSUPPORTED` / `OVERRIDE_TARGET_MISSING`), and the deletion ledger — all present at `git show HEAD:.project/active/elaborator-design/design.md:69-96`. D8 is a naming rule, not the seam contract. This is the artifact that must make the public-boundary obligation schedulable, and it moved backwards on it while telling the next stage to "treat these as fixed". — spec R5/R8 ([NEED]), epic Item 4 scope 2-3 and the "[AGENT] Deletion ledger" success criterion, contract invariant 60 / LC-SI-22 ([INHERITED]) (agent/ratified) — disposition: restore the three dropped sections into this design before design review; a correction shrinks the thing corrected, not its neighbors (capture-fidelity §3).
- design-F2 [DO] D2 unifies a feature slot from "explicit `redefined_feature` edges" only, and never names the SysIDE switch that decides what "explicit" returns — `Relationship.is_implied` / `is_implied_included` (`.venv/.../syside/core/__init__.pyi:1117,6041`). If implied redefinitions are excluded by default, one semantic slot splits into two runtime sources for the ordinary specialize-and-redefine idiom, which is the mission-invariant failure mode this epic exists to kill. B2 states the bet honestly, but its stated fallback — "the unsupported shape must be surfaced rather than joined by name" — would narrow the inherited 29-cell matrix that R7 makes the behavior authority, and would drop a shape Item 5 leg 3 already lands green. — epic mission invariant (owner), LC-SI-04 and R7 ([HARD]), contract invariant 56 (owner/HARD) — disposition: pin implied-relationship query behavior in the identity-foundation slice before B2 is treated as held; if B2 is false, the route is an added SysML semantic rule surfaced to the owner, never a matrix cell going unsupported.
- design-F3 [DO] D1 makes `element_id` the fixed declaration identity, but SysIDE's own contract says more than the design records: the id is "currently only stable for elements with `qualified_name`, and their owning memberships", SysIDE "reserve[s] the option to change non-standard element id generation", and the property "may be deprecated in a future release ... it has no use outside of serialization" (`.venv/.../syside/core/__init__.pyi:5885-5905`). Research finding 6 carries the stability half and omits the deprecation. The exposure is precise: `qualified_name` is null exactly when same-named elements collide in a namespace (finding 2) — the same case Appendix A case 3 asserts as a required pass, and the same case relocated-snapshot identity parity depends on. The design asserts case 3 as an acceptance requirement rather than as the observable that falsifies B1. — contract invariant 58 / LC-SI-13, LC-SI-02 ([HARD] for the referent authority; [INHERITED] for route parity) (agent/ratified) — disposition: record the deprecation sentence in B1's falsification path, name the fallback exact coordinate (stable owning-membership UUID, or an elaboration-minted ID serialized once) and which supported forms fail closed without it; run Appendix A cases 1 and 3 first, as B1's kill probe, not as end-stage acceptance.

Smells: design smells **#2** and **#7** checked, neither fires. #7 does not fire because the design says plainly that it replaces the Item-2 QN/name identity contract in `agentic-mbse` and that the SysIDE version becomes a pinned assumption boundary (Component Overview; Risks) — the ownership move is stated, not smuggled. #2 does not fire; the inverse-shaped risk (codegen relying on a guarantee the platform explicitly declines to make) is carried as design-F3 rather than forced into a smell.

Standing gates from other ledgers (not resolved here): `.project/active/elaborator-breadth/product-lens.md` remains **BLOCKED** on `audit-F1`, `audit-F2`, `audit-F3`. A design that removes the mechanism is not a resolution — those findings are against code at `elaborate.py:943,1133` and `elaboration/__init__.py`, and only a later block in that ledger, citing those IDs against landed code and an observed public-boundary mutation, clears them.

Gate: DISPOSED (design-F1, design-F2, design-F3)

---

## spec-identity-amendment — 2026-08-08 — rev `.project/active/elaborator-design/spec.md`

Epic: `.project/backlog/epic_elaborate_first_architecture.md`

Point (re-derived): Consume resolved referents at load time and preserve each semantic source
occurrence as one runtime source; never reconstruct semantic identity from names. [source:
`.project/backlog/epic_elaborate_first_architecture.md` owner rulings + mission invariant; grade:
owner/HARD]

Falsifier: R3/R9 permits name-based self-binding equality or later name/QN lookup to select a
declaration, occurrence, or consumer edge.

Findings:
- None.

Amendment relation: Narrows the allowed implementation mechanisms, not supported behavior. R3/R9
require exact parser declaration IDs, structured occurrence IDs, and typed edges while preserving
fail-closed behavior. The amendment does not contradict the owner/HARD point.

Gate: CLEAR
