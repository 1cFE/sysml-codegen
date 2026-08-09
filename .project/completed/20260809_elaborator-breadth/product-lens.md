## audit — 2026-08-08 — rev 6bed968
Point (re-derived): Preserve the KerML/SysIDE semantic referent and concrete occurrence so one modeled source occurrence becomes exactly one runtime source for every bound calculation, constraint, and aggregation consumer; unsupported self-bindings halt before generation.   [source: `.project/backlog/epic_elaborate_first_architecture.md` (Mission invariant; Owner-originated rulings) and `.project/concepts/constraint-execution-lifecycle-requirements.md` (LC-SI-02/09), grade: owner/HARD]
Falsifier: A public model with a nearer same-named chain root, a retyped/shadowed aggregation child, or mixed consumers projects more than one source, selects the non-referent value, fails to propagate one off-default mutation to every intended consumer, or permits `in R = R` to reach generation.
Findings:
- audit-F1 [DON'T] Feature-chain resolution reduces the resolved root to its leaf and takes the first matching ancestor path (`src/sysml_codegen/elaboration/elaborate.py:1133`), so a nearer same-named part/calc can capture a binding whose KerML referent is elsewhere. Falsifier: nest a local `source` beside a qualified outer `source`, give them different values, and bind through the outer chain from the inner consumer; the edge must target the outer occurrence. — `.project/backlog/epic_elaborate_first_architecture.md` (Owner-originated ruling: use loaded resolved referents) and `.project/concepts/constraint-execution-lifecycle-requirements.md` (LC-SI-02) (owner/HARD) — disposition: BLOCK
- audit-F2 [DON'T] `sum(...)` expansion ignores the term's resolved identity and reconstructs occurrences as `anchor + sanitized part/attribute names` (`src/sysml_codegen/elaboration/elaborate.py:943`), so shadowing, retyping, or a non-local referent can select or miss the wrong source. Falsifier: sum a resolved child feature whose concrete occurrence differs from that concatenated spelling and mutate only the resolved child; only that child's aggregate edge may move. — `.project/backlog/epic_elaborate_first_architecture.md` (Mission invariant; Owner-originated referent ruling) and `.project/concepts/constraint-execution-lifecycle-requirements.md` (LC-SI-02/09/10) (owner/HARD) — disposition: BLOCK
- audit-F3 [DO] The work stops at a private `InstanceGraph`; no production projection feeds `ComputationGraph` or generation (`src/sysml_codegen/elaboration/__init__.py:5`), and several real-fixture checks select `strict=False` to inspect a partial internal graph. Falsifier: run live and relocated-snapshot public generation, mutate one modeled source off default, and observe every and only its generated calculation/constraint/aggregation consumers; this work exposes no route on which to make that observation. — `.project/backlog/epic_elaborate_first_architecture.md` (Mission invariant and public product-behavior gate) (owner) — disposition: BLOCK
Smells: #4 **Correctness depends on downstream knowledge of an internal representation** fired in audit-F1/F2/F3; #6 **A test passes only because it selects one route or interpretation** fired where real-fixture breadth assertions use lenient internal elaboration after strict elaboration correctly halts. Both are unresolved and must escalate into the audit's Product Judgment.
Gate: BLOCKED (audit-F1, audit-F2, audit-F3)

## audit — 2026-08-08 — rev 6bed968-dirty
Point (re-derived): One semantic source occurrence — declaration identity plus concrete occurrence identity — produces exactly one runtime source, and every and only its calculation, constraint, and aggregation consumers resolve to that source; identity is extraction-owned, never reconstructed from owner/name strings; where no unique concrete occurrence exists in the consumer's context the outcome is a **named** diagnostic, never a guess; unsupported authored forms fail loudly before generation.   [source: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` invariants 54–57, 59–60 + `.project/backlog/epic_elaborate_first_architecture.md` "Critical Success Factor"; graded via `.project/concepts/constraint-execution-lifecycle-requirements.md` LC-SI-01 [NEED], LC-SI-09 [NEED], LC-SI-15 [NEED], LC-SI-08/13/14 [INHERITED], grade: **owner / [HARD]**]
Falsifier: a customer-shaped fixture in which (a) two consumers of one modeled value reach different sources or two distinct occurrences collapse to one; (b) a reference that has no unique occurrence in the consumer's context is silently bound anyway, or is reported under a code that does not name ambiguity; or (c) an unsupported authored form reaches graph construction without raising.
Findings:
- audit-F4 [DO] `ElaborationCode.SI_OCCURRENCE_AMBIGUOUS` is declared but never emitted anywhere in `src/`; every non-unique resolution is reported as `SI_OCCURRENCE_MISSING` with free-text detail "did not resolve uniquely" (`src/sysml_codegen/elaboration/elaborate.py:957-972`), and the fixture staged for this outcome (`tests/fixtures/source_identity_occurrence_ambiguity/PROVENANCE.md:21`) is unwired. Invariant 55 requires a *named* ambiguity diagnostic — contract inv 55 / LC-SI-08 ([INHERITED]) — falsifier: load `source_identity_occurrence_ambiguity` lenient and assert a diagnostic whose code is `SI_OCCURRENCE_AMBIGUOUS`; it is `SI_OCCURRENCE_MISSING` today — disposition: DISPOSE — wire the code (or delete it and rename the emitted one) before Phase 3 closes fail-closed
- audit-F5 [DO] No lenient-route test asserts the graph's complete diagnostic set, so unresolved sources are invisible on the two largest shapes. Reproduced at this rev: `fusion_tea` elaborates with **7 `SI_OCCURRENCE_MISSING`** diagnostics (alias `scope` on six occurrences, `wall_type` on one) while its only test (`tests/conformance/test_elaboration_specialization_retypes.py:120-136`) asserts two named edges and never inspects `graph.diagnostics`; the strict=False suites assert only the `SI_SELF_BINDING` subset (`test_elaboration_sibling_channels.py:73`, `test_elaboration_expose_shapes.py:296`). Invariant 56's "every and only its consumers" half is therefore unproven on the real customer composition — contract inv 56/57 / LC-SI-09 ([NEED], **owner grade**) — falsifier: assert an exact expected diagnostic multiset per lenient fixture; `fusion_tea` yields 7 unaccounted rows — disposition: DISPOSE — add the per-fixture diagnostic allowlist assertion; the elaborator's behavior is correct (it diagnoses, it does not guess), the gap is evidence, not semantics
- audit-F6 [DO] Six of nine `ElaborationCode` members are dead (`SI_OCCURRENCE_AMBIGUOUS`, `OVERRIDE_TARGET_MISSING`, `SI_ID_MISSING`, `SI_ID_UNSTABLE`, `SI_REDEFINITION_INVALID`, `SI_RENDERING_COLLISION`); the conditions they name instead raise untyped exceptions — `IdentityBoundaryError` (`identity.py:35`), `InvalidRedefinitionFamilyError` (`occurrence.py:31`), bare `ValueError("SI_EDGE_DANGLING: …")` (`elaborate.py:951,955`). Invariant 59 requires blocking, *named* diagnostics — contract inv 59 / LC-SI-16 ([NEED]) — falsifier: assert a caller can discriminate an identity-boundary failure from a redefinition-family failure by code; it cannot — disposition: DISPOSE — Phase 3 owns fail-closed; collapse to one vocabulary there
- audit-F7 [DO] The elaborator has **zero production call sites** (`grep` over `src/` finds no importer outside `elaboration/`), so the Phase 1–2 completion recorded in the epic body rests entirely on internal graph structure. Invariant 57 states fixed-point equality and key counts are insufficient evidence; the epic's own gate says every item's completion is "an observable public behavior … never artifact-to-artifact fidelity" — contract inv 57 / LC-SI-14 ([INHERITED]) + epic Success Criteria ([AGENT] ratified) — falsifier: an off-default mutation of one modeled value observed changing every intended consumer and no independent source at the public boundary; no such route exists yet — disposition: DISPOSE — deferred to the scheduled Phase 4 projection / Phase 5 mutation proof. **This finding does not resolve audit-F1/F2/F3**, which remain in force uncited
- audit-F8 [DON'T] `_resolve_leaf` (`elaborate.py:769-775`) ends with a model-wide scan that binds to the single occurrence bearing the slot **anywhere in the model** when lineage and descendant search both fail — resolution outside the consumer's context, which is precisely the condition invariant 55 assigns to a named ambiguity diagnostic. It is also the one surviving resolve-by-search path in an otherwise context-anchored front end, and the guard test that bans first-match routes (`tests/unit/test_elaboration_import_boundaries.py`) only greps for `next(iter` and does not catch the list form — contract inv 55 / LC-SI-08 ([INHERITED]) — falsifier: a fixture with one globally-unique attribute occurrence outside the consumer's containment lineage; the binding resolves instead of diagnosing — disposition: DISPOSE — either justify the fallback as a recorded rule or replace it with the ambiguity diagnostic from audit-F4
- audit-F9 [DO] The import-boundary guard bans the token `sanitize_name` in `identity.py`/`occurrence.py`/`elaborate.py`, and this same work introduces `elaboration/display.py` — a 13-line pass-through to `sanitize_name`/`sanitize_qualified_name` — which `occurrence.py:11` and `elaborate.py:18` import while the guard reads green and does not check `display.py`. The dependency is unchanged; only the token moved — my inference from the guard's own stated purpose ([AGENT]/[INFERRED]) — falsifier: the guard passes with the legacy name-sanitizer still on the elaboration path — disposition: DISPOSE — check `display.py` too, or state in the guard that display rendering is an allowed consumer
- audit-F10 [DO] No durable statement of the point exists in the shipped documentation tier. `README.md` and `docs/architecture/` carry only the name-based pipeline description (CLAUDE.md ADR-003 qualified/channel-name conventions); the one-source invariant lives solely in `.project/concepts/` and the epic. A reader working from README/docs alone derives the superseded point — can't-find at the README/docs tier (grade: **none**) — disposition: DISPOSE — write the point down in `docs/architecture/` at the Item-6 cutover, when it becomes shipped behavior

Smells fired (must escalate into the stage judgment, escalation is not resolution):
- **Smell 1 — two representations manually kept synchronized** (audit-F6): the `ElaborationCode` enum and the exception hierarchy each name the same failure set, and neither is derived from the other.
- **Smell 6 — a test passes only because it selects one route** (audit-F5): `test_fusion_tea_driver_edge_wires_end_to_end` asserts the two edges it names and is green while seven references in the same graph did not resolve.

Verified holding at this rev (not findings, recorded so the gate is not misread as a general negative): the owner-grade self-binding prohibition (LC-SI-01/LC-SI-15) is enforced by exact element-ID comparison, never by name (`extraction/source_evidence.py:132-144`), is checked before form classification (`elaborate.py:553-563`), raises `ElaborationError` in the default strict mode, and every `strict=False` suite carries a companion test asserting the strict raise with the named code; `NodeId` contains no name material and the vertical slice proves order-invariance by reversing parser iteration and comparing semantic edges; distinct occurrences under equal inherited defaults stay distinct nodes by construction (one `AttrNode` per `(scope, slot)`); the Phase-1 kill probes pin UUIDv5 reload stability and UUIDv4 instability against the live parser rather than against a fixture.

Gate: DISPOSED (audit-F4, audit-F5, audit-F6, audit-F7, audit-F8, audit-F9, audit-F10) — **subject to the standing BLOCK**: audit-F1/F2/F3 from the prior block are not cited or resolved here and remain in force; `_my_pre_pr`, `_my_close`, and epic-scope audit still fail while they stand.

## Phase-5 public-mutation resolution — 2026-08-08

- **audit-F1 — RESOLVED.** The exact route retains the loaded outer declaration identity through
  projection. The kept public mutation changes `ShadowedReference__the_outer__scale` from 2.0 to
  3.0 while a nearer same-named inner value stays 7.0; live and rebuilt projections both wire the
  calculation only to the outer input, and generated JSON contains that one input
  (`tests/conformance/test_elaboration_public_mutation.py`).
- **audit-F2 — BLOCK remains.** Exact graph construction now records `sum(...)` inputs as direct
  per-occurrence node edges, so the name-reconstruction implementation cited by the original finding
  is gone. Its public falsifier is still unobserved: the contract requires indexed/parameterized
  population shapes C17/C26, while the exact walker blocks symbolic multiplicity before a single
  child can be mutated and projected. Design and graph-shape evidence do not clear this product gate.
- **audit-F3 — RESOLVED.** The exact graph now projects to `ComputationGraph` from both the live model
  and decoded `instance-graph/v1`. Changing one modeled value from 42.0 to 47.0 changes exactly one
  public input and leaves every unrelated input unchanged; its calculation, constraint, and FORMULA
  consumers retain the same direct source on both routes, and generated JSON contains the changed
  input exactly once (`tests/conformance/test_elaboration_public_mutation.py`).

Gate: **BLOCKED on audit-F2**. The Phase-5 matrix and corpus ledger independently retain the same
symbolic-multiplicity blocker; Item 5 and epic-scope audit cannot close until the owner dispositions
in `diff-ledger.md` are applied and revalidated.

## audit — 2026-08-09 — rev 6bed968-dirty (Phase-5 checkpoint)

Point (re-derived): Every supported model-derived consumed value binds at the semantic referent KerML name resolution supplies, fixed by written form and binding-owner context together (referent table); one semantic source occurrence — declaration identity plus concrete occurrence identity — produces exactly one runtime source that every and only its calculation, constraint, and aggregation consumers resolve to; acceptance is established at the public boundary by off-default mutation, never by fixed-point equality or key counts; and the loud-failure boundary covers *unsupported and deferred* forms only — a supported form that fails closed is as much a violation as an unsupported one that passes.   [source: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` invariants 54, 55, 56, 57, 59 + referent table (lines 312-324); `.project/backlog/epic_elaborate_first_architecture.md` Critical Success Factor (line 31) and Non-Goals (line 108); grade: **owner / [HARD]** for invariants 54-57/59 (Item-3 contract, ratified 2026-08-05, carried as "the semantic authority" by the epic at line 48); **agent / ratified** for the epic's product-behavior and Non-Goal lines]

Falsifier: a model whose written form the referent table marks supported produces a typed error, a wrong node, or a phantom module on the exact route; or a cell's acceptance rests on internal `InstanceGraph` structure rather than an off-default mutation observed in generated public output.

Findings:

- audit-F11 [DON'T] Parameterized-but-finite multiplicity is misclassified as non-finite and blocked. `_multiplicity_indices` (`src/sysml_codegen/elaboration/occurrence.py:270-273`) requires the upper bound to be a `LiteralInteger` AST node and otherwise raises `NonFiniteMultiplicityError("non-literal upper multiplicity")`. Both blocked corpus rows are finite populations: `d38_caret/library.sysml:19,21` declares `attribute count : Integer = 4` with `part cell : 'Cell'[count]`, and `solar_battery_model/library.sysml:598,602` declares `module_count : Integer default := 20` with `part pv_module : 'PV Module' [module_count]`. The epic's disposition is "Expand-finite or block-loud" (line 108) — expand-finite is the ratified treatment for a finite population; block-loud governs genuinely unbounded ones. A population of 4 written `[count]` has the same user-visible meaning as one written `[4]`, and the elaborator already computes attribute values for `AttrNode`s, so the value needed to expand is in hand. Blocking omits every real aggregation consumer under those parents, contradicting invariant 56. — contract inv 55/56 + epic Non-Goal line 108 (**owner/[HARD]**) — falsifier: elaborate `d38_caret` and assert four `cell` occurrence nodes with four aggregation term edges; today it raises. — disposition: **BLOCK**

  **Surfacing (capture-fidelity §4): this finding changes what the standing audit-F2 BLOCK means.** `diff-ledger.md:69-71,80-82` presents symbolic multiplicity as a premise conflict and asks the owner to decide whether "C17/C26 and the Item-5 completion contract must be amended." The conflict is not in the contract. C17/C26 are reachable; a literal-token check in the walker is what stops them, and that same check is why audit-F2's public falsifier (mutate one child of an indexed population, observe only that child's aggregate edge move) is unobservable. The owner is being invited to weaken an owner-graded cell to accommodate an implementation defect. audit-F2 stays BLOCKED, and its blocker is now named as audit-F11, not as a contract conflict.

- audit-F12 [DON'T] The 29-cell matrix certifies internal representation as public behavior. Nine of the ten cells `tests/conformance/test_elaboration_contract_matrix.py` marks `state="public"` — C1, C8, C12, C13, C15, C16, C19, C20, C24, C25 — cite tests that assert against the internal `InstanceGraph` (`test_elaboration_spike_parity.py:105-115` reads `mixed.calcs` / `node_ref`; `test_elaboration_shadowing.py:75-98` reads `node_id`, `attr(...).value`, `graph.diagnostics`). Only C11 reaches `ComputationGraph` and generated JSON. Invariant 57 states value equality and entry-key counts are insufficient evidence and that acceptance is established at the public boundary by off-default mutation; the epic's gate says completion is "an observable public behavior … never artifact-to-artifact fidelity" (line 85). The Item-3 spike proved C25 collapse *in real generated YAML* (epic line 207); Item 5 records the same cell against an internal structure, which is a regression in evidence tier. — contract inv 57 (**owner/[HARD]**) + epic Success Criteria (agent/ratified) — falsifier: for each cell marked `public`, mutate the cell's source off default and observe the change in generated output; nine cells expose no such observation. — disposition: **BLOCK**

- audit-F13 [DON'T] Matrix cells are certified by grepping for a function definition line. `test_cell_has_kept_exact_route_evidence` (`test_elaboration_contract_matrix.py:126-136`) asserts only `f"def {test_name}(" in source.read_text()`. It never executes the cited test, never checks its result, and never checks that it asserts the cell's obligation. A cited test emptied of assertions keeps the matrix green. The `EVIDENCE` map and the suite are two representations held in sync by hand. — epic product-behavior gate (agent/ratified), my inference from the file's own stated purpose ([AGENT]/[INFERRED]) — falsifier: delete the body of `test_c25_exactly_two_consumers_share_the_node` and rerun the matrix; it stays green. — disposition: DISPOSE — bind cells to executed outcomes (parametrized reuse or a pytest node-id collection check), not to source text

- audit-F14 [DO] Seven of the twelve `blocked` xfails are unwritten fixtures, not blockers. C2, C3, C4, C6, C7, C14, C23 all carry the location string "no exact … fixture". Only C5, C17, C18, C21, C26 have a reproduced obstruction. Item 5's criterion is "every matrix cell green-or-named-diagnostic on the new path" (epic line 335). Filing missing work in the same category as genuine conflicts understates remaining breadth to the owner at the checkpoint and makes the xfail permanently green. — epic Item-5 Success Criteria (agent/ratified) — falsifier: the owner reads "12 blocked" as 12 external obstructions when 7 are unstarted fixtures. — disposition: DISPOSE — split the state into `unwritten` and `blocked` before the owner checkpoint is presented

- audit-F15 [DON'T] Definition-level template declarations are projected as runtime modules. `unresolvable_attr_probe` yields 10 exact modules against 1 legacy module (`diff-ledger.md:51`). The fixture declares `calc my_calc` inside `part def 'Design Derived'` (`tests/fixtures/unresolvable_attr_probe/design.sysml:16,20`) alongside three concrete `part` usages. A definition-level declaration has no concrete occurrence, so under invariant 55 it cannot own a runtime source; projecting it emits pipeline modules with no runtime instance behind them. This is customer-visible wrong output, not a counting difference. — contract inv 55/56 (**owner/[HARD]**) — falsifier: project `unresolvable_attr_probe` and assert every module maps to a concrete occurrence; nine do not. — disposition: **BLOCK**

- audit-F16 [DON'T] A supported referent-table form fails closed. `deep_cross_scope_probe` emits `SI_OCCURRENCE_MISSING` on the exact route (`diff-ledger.md:28`; matrix C5). That fixture is the contract's own normative witness: the referent table cites `DCS:71,83` for "bare renamed / usage context → occurrence-level feature" and `DCS:92` for "owner-qualified / usage context" (contract lines 313-314, 320-321). Two of the table's five supported rows are verified against a model the exact route cannot resolve. Invariant 59's loud-failure boundary covers unsupported and deferred forms; applying it to a supported form breaks invariant 54's referent fidelity in the opposite direction from the self-binding case. — contract inv 54/59 + referent table (**owner/[HARD]**) — falsifier: elaborate `deep_cross_scope_probe` and assert the usage-context bare-renamed and owner-qualified bindings reach occurrence-level nodes; both diagnose instead. — disposition: **BLOCK**

- audit-F17 [DON'T] A supported specialization has no public graph because two distinct occurrences cannot be named apart. `retype_model` fails with `SI_RENDERING_COLLISION` (`diff-ledger.md:41`; matrix C21). The identity layer is right — invariant 56 and D-13 require distinct concrete occurrences to stay distinct sources — but the ADR-003 name rendering in projection cannot represent them, so a supported form is blocked at the naming layer rather than the semantic one. — contract inv 56 / D-13 (owner) applied through ADR-003 naming (agent/ratified) — falsifier: project `retype_model` and assert two distinct public input names for the two retyped occurrences; projection raises instead. — disposition: DISPOSE — this is a rendering defect with a bounded fix; it must not be recorded as a semantic blocker at the owner checkpoint

- audit-F18 [DON'T] The exact projection admits a constraint the executable profile excludes. `constraint_non_numerical` goes from legacy `2/1/1/0` to exact `3/0/2/0` (`diff-ledger.md:25`), adding an eligible constraint the profile does not cover. Admitting a non-executable predicate into the catalog puts a check into the certifying path that the profile says cannot be certified. — contract constraint-profile family, inv 52/53 (agent/ratified as applied here; I did not re-derive the profile text) — falsifier: project `constraint_non_numerical` and assert the eligible-constraint set equals the profile-admissible set; the exact route has one extra. — disposition: DISPOSE — reproduce against the profile definition and either fix admission or record the profile change as an intended contract change per §2

- audit-F19 [DO] The fail-closed posture on SRC-01 is correct, but the customer composition is now wholly unproven. The self-binding check is exact element-ID comparison against the bound formal and never reads names (`src/sysml_codegen/extraction/source_evidence.py:130-141`), and the owner ruled `in R = R` a modeling bug not to be worked around (epic lines 63-66). So 27/37 typed errors is the intended posture, not over-reach *in that mechanism* — the over-reach is isolated to F11/F16/F17. But `fusion_tea` (15×) and `ife_plant` (21×) are the real customer compositions, and no corrected variant of either is authored. Exact-route breadth therefore rests on ten fixtures, none at customer scale, and the Item-7 obligation to publish "two valid replacement forms with their distinct meanings" (epic line 402) has no fixture showing that either replacement projects. — epic Success Criteria line 95 and Item-5 Objective (agent/ratified) — falsifier: a corrected `fusion_tea` variant that projects and carries an off-default mutation to all consumers; none exists. — disposition: DISPOSE — required before Item 6 closes, not before Item 5; authoring one corrected customer variant would also convert F19 into the missing public evidence for F12

Smells checked (1, 3, 4, 5, 6) — three fired; escalation is not resolution:
- **Smell 3 — a special category exempts a case whose user-visible meaning is unchanged** (audit-F11): "non-finite multiplicity" is a category that exempts `[count]` where `count = 4`, whose meaning is identical to `[4]`. This is the fingerprint the smell exists to catch, and it is the mechanism behind the standing audit-F2 BLOCK.
- **Smell 4 — correctness depends on downstream knowledge of an internal representation** (audit-F12): nine matrix cells are certified by reading `InstanceGraph` node IDs and edge refs, so the acceptance record depends on the shape of the IR rather than on behavior at the boundary.
- **Smell 6 — a test passes only because it selects one route or interpretation** (audit-F12, audit-F13): the matrix is green because it selects the internal route for nine cells and, for all cells, selects source-text presence over executed outcome.
- Smell 1 not re-fired independently at this rev; audit-F6's enum/exception duplication from the prior block is unresolved and audit-F13 adds a second instance of the same pattern (`EVIDENCE` map vs suite).
- Smell 5 not fired: the legacy route remaining authoritative is the Item-5 criterion, not a preserved contradiction.

Gate: **BLOCKED (audit-F11, audit-F12, audit-F15, audit-F16)** — and the standing **audit-F2 BLOCK remains in force**, now re-anchored: its falsifier is unobservable because of audit-F11, an implementation defect in this work, not because of a conflict in the owner-graded contract. audit-F1 and audit-F3 stay RESOLVED per the 2026-08-08 Phase-5 block. audit-F13, audit-F14, audit-F17, audit-F18, audit-F19 are DISPOSED. The owner checkpoint in `diff-ledger.md` should not be presented as written: decision 1 asks the owner to amend C17/C26 for what audit-F11 shows is a fixable walker check, and the "12 blocked cells" count conflates 7 unwritten fixtures with 5 reproduced blockers (audit-F14).

Verified holding at this rev (recorded so the gate is not misread as a general negative): the SRC-01 self-binding prohibition is enforced by exact `element_id` comparison against the bound formal and is provably name-independent (`extraction/source_evidence.py:130-141`); the Phase-5 public-mutation proof is genuine and well-built — `test_elaboration_public_mutation.py` mutates one modeled value 42.0 → 47.0, checks three mixed consumers (CALCULATION, CONSTRAINT, FORMULA) converge on one source, checks every unrelated default is unchanged, and confirms the generated JSON carries the changed input exactly once, on both the live and decoded `instance-graph/v1` routes; the shadowed-referent companion holds the outer 2.0 → 3.0 while the nearer inner 7.0 stays put. That test is the model the other nine "public" cells in audit-F12 should follow.

## Phase-5 remediation resolution — 2026-08-09

These dispositions apply the `[AGENT] (ratified by owner, 2026-08-09)` decisions recorded in
`plan.md`. They report implemented evidence; they do not self-certify the item.

- **audit-F2 / audit-F11 — RESOLVED.** The occurrence walker resolves a modeled finite integer
  bound before expansion. `d38_caret` now creates four child occurrences and aggregation edges.
  The executable C17/C26 cells project producer-backed and literal-backed child aggregations,
  render public pipeline/input artifacts, and mutate one source without changing the independent
  sources.
- **audit-F12 / audit-F13 — RESOLVED.** The matrix contains no source-text function lookup and no
  xfail. Each of 29 cell callables executes its required public or diagnostic outcome. Every
  runtime cell compares live and relocated projections, renders pipeline YAML and input JSON, and
  applies an off-default mutation.
- **audit-F14 — RESOLVED.** C2, C3, C4, C6, C7, C14, and C23 now have focused SysML fixtures and
  executable public evidence. The matrix passes all 29 cells plus its authority-set check.
- **audit-F15 — RESOLVED by the owner-ratified corpus decision.** The nine extra formula modules
  are modeled behavior on three concrete instances, not definition-only templates. A kept public
  test requires all nine names to be scoped under `derived_instance`, `design_derived_instance`,
  or `grandchild_instance`; none is definition-scoped.
- **audit-F16 — RESOLVED.** Usage-qualified contextualization now selects the concrete analyzer
  occurrence. A clean C5 fixture reaches generated public output and mutation. The larger
  `deep_cross_scope_probe` advances to its independent D8 result: three distinct semantic outputs
  collide under one public rendering and are rejected with `SI_RENDERING_COLLISION`.
- **audit-F17 — RESOLVED.** Calculation population selects one most-specific writer per occurrence.
  `retype_model` now projects instead of raising a rendering collision, and the clean C21 fixture
  proves the specialized value through generated public output and mutation.
- **audit-F18 — RESOLVED.** Numerical constraints remain executable. The string equality is an
  excluded catalog record and has no runtime constraint module.
- **audit-F19 — remains assigned to Item 6.** The customer-scale corrected-composition proof is a
  cutover acceptance obligation. It does not block completion of Item 5's independent route.

The fresh 37-fixture ledger has 26 `expected-collapse`, 11 `expected-fix`, zero `needs-review`, and
zero `new-bug` rows. The product-lens gate is **CLEARED for the Phase-5 implementation checkpoint**;
an independent `$my-audit` still owns certification.

## audit — 2026-08-09 — rev 6bed968-dirty (v2 certification)

**Point (re-derived):** Every supported model-derived consumed value binds at the semantic referent KerML name resolution supplies (written form × binding-owner context, per the contract referent table); one semantic source occurrence — declaration identity plus concrete occurrence identity — produces exactly one runtime source that every and only its calculation, constraint, and aggregation consumers resolve to; that identity is extraction-owned and **never reconstructed from owner/name fields**; acceptance is established at the public boundary by off-default mutation; and loud failure is confined to unsupported and deferred forms.  [source: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` invariants 54, 55, 56, 57, 59, 60 + referent table (lines 313–324); `.project/backlog/epic_elaborate_first_architecture.md` Critical Success Factor (line 31) and the owner ruling "resolved referents are available when the model is loaded; the architecture must use them then, not reconstruct them later" (line 67); graded via `constraint-execution-lifecycle-requirements.md` LC-SI-02 [HARD], LC-SI-09 [NEED], LC-SI-08/13/14/22 [INHERITED]. **grade: owner / [HARD]**]

**Falsifier:** a supported written form whose concrete occurrence is selected by matching name/text material rather than by the loaded referent; or a model the contract itself cites as a supported-form witness that produces no public graph; or a "public" cell whose evidence is an internal `InstanceGraph` assertion rather than an off-default mutation observed in generated output.

**Findings:**

- **audit-F20 [DON'T]** The audit-F16 remediation resolves the concrete occurrence by string-matching the written qualifier against rendered display paths. `_resolve_bindings` threads `evidence.written_qualifier` (the CST byte-span text, `extraction/binding_evidence.py:55-104,199`) into `_resolve_leaf`, which sanitizes it (`display_qualified_name` → `sanitize_name`) and selects the producing calc by `node.display_path.endswith(qualifier_path)` plus a `startswith(f"{relative_path}__")` scan over all part usages (`src/sysml_codegen/elaboration/elaborate.py:1268-1302,1559-1562`). Classifying the *form* from the CST is legitimate and the referent table requires it; using the qualifier *text* to pick the occurrence is reconstruction from name material, which invariant 55 states is not an accepted authority and invariant 60 forbids as a second identity authority. It also fails open: when `contextual` is empty the qualifier is silently discarded and resolution proceeds over every producing calc, so an owner-qualified reference can bind to an occurrence its qualifier does not name (invariant 54). This mechanism is the epic's stated defect ("guess identity back out of strings") re-entering the exact route through its own remediation. — contract inv 54/55/60 + epic owner ruling line 67 (**owner/[HARD]**) — falsifier: a fixture with two same-typed producer occurrences whose display paths share a suffix, plus one whose qualifier matches no display path; the first mis-binds, the second resolves unqualified. — **disposition: BLOCK**

- **audit-F21 [DON'T]** The contract's own referent-table witness still produces no public graph, and the label that clears it rests on an unrecorded claim. `deep_cross_scope_probe` is what the contract cites for two of the five supported referent-table rows (DCS:71,83 bare renamed / usage context; DCS:92 owner-qualified / usage context — contract lines 313-314, 320-321). Legacy yields `graph 5/7/0/0`; the exact route yields `error: SI_RENDERING_COLLISION` (`diff-ledger.md:29`), classified **expected-fix** on the basis "D8 then rejects three genuinely distinct outputs with one public rendering." No test, ledger row, or note identifies which three public names collide, and the three consumer calcs (`chain_analysis`, `ref_analysis`, `self_ref_analysis`, `design.sysml:69,81,91`) have distinct display paths, so the claim is not self-evident. The only kept evidence for the cell uses the **internal** graph (`test_elaboration_phase5_remediation.py:85-99` calls `_internal`, not `_exact`), while C5 is certified by a purpose-built synthetic fixture `elab_matrix_c5`. Invariant 59 confines loud failure to unsupported and deferred forms; a supported form blocked at the naming layer is the audit-F17 class, which was fixed rather than labeled. **This explicitly re-opens audit-F16: I do not accept it as RESOLVED.** — contract inv 54/59 + referent table (**owner/[HARD]**) — falsifier: project `deep_cross_scope_probe` and name the colliding public renderings; the route raises and the repo does not record them. — **disposition: BLOCK** — cheap clearance: reproduce and record the exact colliding names; if genuine, it becomes an ADR-003 rendering decision the owner can rule on.

- **audit-F22 [DO]** The corpus ledger — the artifact carried to the owner checkpoint — is not verified against any run. `test_elaboration_corpus_ledger.py:13-26` checks only that all 37 fixture names appear with one of four labels. Nothing compares the recorded outcomes (`graph 2/6/0/0`, `error: SI_SELF_BINDING`, code multisets) to `scripts/run_elaboration_corpus.py`, which states it "does not update snapshots, ledgers". Every count and code in the table is hand-transcribed and would stay green if wrong. — epic Item-5 success criterion, `epic_elaborate_first_architecture.md:337` (agent/ratified) — falsifier: corrupt a row's counts; the suite passes. — disposition: DISPOSE — emit the table from the runner, or add a re-run comparison.

- **audit-F23 [DO]** The source-text-as-evidence pattern the owner ruled out survives one instance. `test_corpus_runner_discovers_the_same_closed_fixture_set` (`test_elaboration_corpus_ledger.py:29-33`) asserts three literal strings exist in the runner's source text. The ratified decision reads "A function-name source-text check is not evidence" (`plan.md:551-554`); it was removed from the matrix and left here. — plan.md Phase-5 decision (agent/ratified) — falsifier: rename the runner's discovery call while preserving behavior, or preserve the strings while breaking discovery; the test's verdict is unchanged either way. — disposition: DISPOSE — call the runner and compare fixture sets.

- **audit-F24 [DO]** The matrix's mutation assertion is one-sided. `_assert_runtime_cell` (`test_elaboration_contract_matrix.py:671-673`) iterates **baseline** keys only, so a mutation that *adds* a public input is invisible; only removals surface (as a `KeyError`). Invariant 57's "and no independent source" includes phantom sources — the audit-F15 failure family the matrix is meant to guard. — contract inv 57 (**owner/[HARD]**), evidentiary not semantic — falsifier: a mutation that mints an extra entry point passes today. — disposition: DISPOSE — assert key-set equality before comparing values.

- **audit-F25 [DO]** Three failure conditions on the elaboration path still raise un-coded exceptions while a parallel code vocabulary exists: `NonFiniteMultiplicityError` (`occurrence.py:331,333,348,350,360,362`), `InvalidRedefinitionFamilyError` (`occurrence.py:81,97,115,255`), `IdentityBoundaryError` (`elaborate.py:560,1054`). `ElaborationCode.SI_REDEFINITION_INVALID` names the same condition and is used elsewhere (`elaborate.py:390`); `OVERRIDE_TARGET_MISSING`, `SI_ID_MISSING`, `SI_ID_UNSTABLE`, `SI_SNAPSHOT_INVALID` are cited by no test. Invariant 59 requires blocking *named* diagnostics; a caller cannot discriminate a multiplicity block from a redefinition-family block by code. audit-F6 is reduced, not closed. — contract inv 59 / LC-SI-16 [NEED] — disposition: DISPOSE — Item 6 owns the single vocabulary.

- **audit-F26 [DO]** Public identity on the new route is pinned by executing the old front end. `test_public_compatibility_keeps_names_but_uses_occurrence_sources` (`test_elaboration_phase5_remediation.py:102-120`) asserts the exact route's `output_aliases` and constraint IDs equal values computed by calling `build_pipeline_context` at test time. The owner's ratified intent was preserving *public names*; pinning to a live legacy computation makes the defective front end the oracle for the new one and creates a synchronization link the epic's One-authority gate says must not outlive the cutover (`epic:87-88`). — epic One-authority gate and Deletion ledger (agent/ratified) — falsifier: delete the legacy route at Item 6 and this test cannot run. — disposition: DISPOSE — freeze the expected names as literals.

- **audit-F27 [DO]** The finite-multiplicity category boundary is still a literal-token check one step out. `_modeled_integer_bound` (`occurrence.py:261-315`) accepts only a `LiteralInteger` `feature_value_expression`, so `[count]` with `count = 2 * 2` still raises `NonFiniteMultiplicityError`; `ordered`/`nonunique` finite populations are rejected under the same non-finite name (`occurrence.py:330-333`). The ruling was "block only a genuinely unresolved or unbounded cardinality" (`plan.md:511-514`). The two corpus cases are covered; the category still misnames a finite-but-computed bound. — plan.md ratified decision (agent/ratified) — disposition: DISPOSE — state the accepted-bound rule and rename the error.

**Smells checked (1, 3, 4, 5, 6) — four fired; escalation is not resolution:**
- **Smell 1 — two representations manually kept synchronized** (audit-F22, audit-F25): the diff ledger vs. the actual corpus run; the `ElaborationCode` enum vs. the surviving exception hierarchy.
- **Smell 3 — a special category exempts a case whose user-visible meaning is unchanged** (audit-F27): "non-finite multiplicity" still names a finite `[2*2]` population. Much reduced from the prior rev, not eliminated.
- **Smell 4 — correctness depends on downstream knowledge of an internal representation** (audit-F20): leaf resolution depends on the projection layer's sanitized display-path rendering.
- **Smell 6 — a test passes only because it selects one route or interpretation** (audit-F21): C5 is green because a synthetic fixture was substituted for the contract's own witness model, whose supported forms are evidenced only on the internal route.
- **Smell 5 not fired as a preserved contradiction**, but audit-F26 carries its mechanism: a compatibility assertion computed by running the front end the epic exists to delete.

**Resolves:**
- audit-F2: **FIXED** — authority: owner (checkpoint ratification 2026-08-09, `plan.md:511-514`) — basis: finite modeled bounds expand; C17/C26 now execute public projection, YAML/JSON generation, and off-default mutation (`test_elaboration_contract_matrix.py:366-385,510-542`).
- audit-F11: **FIXED** — authority: owner — basis: same; verified in `occurrence.py:261-315`. Residue filed as audit-F27.
- audit-F12: **FIXED** — authority: grade owner/[HARD] satisfied — basis: all 21 runtime cells now project live *and* relocated, render pipeline YAML and input JSON, and apply an off-default mutation or public override (`test_elaboration_contract_matrix.py:648-673`). This is a genuine and substantial upgrade in evidence tier.
- audit-F13: **FIXED** — basis: no source-text function lookup remains in the matrix; the cell set is derived by parsing the contract (`:749-758`). One instance survives elsewhere → audit-F23.
- audit-F14: **FIXED** — basis: C2, C3, C4, C6, C7, C14, C23 have fixtures and executable public evidence; no xfails.
- audit-F15: **FIXED** — authority: owner (`plan.md:518-521`) — basis: kept test requires all nine formulas scoped under three concrete instances (`test_elaboration_phase5_remediation.py:142-155`).
- audit-F16: **NOT RESOLVED** — re-derived and re-anchored as audit-F21.
- audit-F17: **FIXED** — basis: `retype_model` projects; most-specific writer selection verified (`elaborate.py:341-394`); C21 proven on a clean fixture through generated output.
- audit-F18: **FIXED** — basis: `test_non_numerical_constraint_is_cataloged_but_not_executed` (`:65-74`).
- audit-F4: **FIXED** — `SI_OCCURRENCE_AMBIGUOUS` is now emitted (`elaborate.py:1096,1105,1110,1327`) and asserted by C9/C10.
- audit-F7: **FIXED** — production projection exists and is exercised end-to-end.
- audit-F8: **FIXED** — the model-wide scan is gone; `_resolve_leaf` is lineage-anchored and raises `SI_OCCURRENCE_AMBIGUOUS` on >1 descendant (`elaborate.py:1311-1338`).
- audit-F19: **DEFERRED** — authority: prior disposition, assigned to Item 6 — basis: unchanged; no corrected customer-scale composition exists (25 of 37 corpus rows still produce no graph).

**Gate: BLOCKED (audit-F20, audit-F21).** audit-F22 through audit-F27 are DISPOSED. audit-F19 remains deferred to Item 6. Two notes for the stage judgment: the remediation is real and much of it is strong — the runtime matrix is now the kind of public evidence invariant 57 asks for — but the fix that cleared audit-F16 introduced string-based occurrence selection into the exact route (audit-F20), which is the defect class the epic exists to delete, and the contract's own supported-form witness still cannot generate (audit-F21). Neither can be cleared by a green suite; both need an owner disposition or a code fix.

**Auditor verification note (v2 audit, same date):** audit-F20's mechanism was independently re-read and confirmed at `elaborate.py:1268-1301` including the fail-open branch. audit-F21's collision was reproduced live: the corpus runner raises `SI_RENDERING_COLLISION: distinct semantic outputs render as public channel 'DeepCrossScopeDesign__measurement_system__station__array__sensor__core__metric_value'` — the collision is genuine and the channel is named at runtime, but the repo records neither the colliding trio nor an owner ruling that a D8 block on the contract's witness fixture is the intended outcome, so the finding stands as written.

## Implementation response to audit v2 — 2026-08-09

This is remediation evidence for the next independent audit, not self-certification.

- **audit-F20 — remediated in code.** Leaf resolution no longer receives qualifier text, reads no
  rendered display path, and uses no prefix/suffix string matching. Exact usage-owned referents such
  as `analyzer::baseline_value` resolve by declaration/occurrence identity. Missing or ambiguous
  occurrence context fails closed by typed identity. An AST boundary test rejects any return of
  display metadata or string-prefix selection to the resolver.
- **audit-F21 — owner ruling applied.** DCS:71,83 and DCS:92 are referent evidence for the
  supported C4/C5 bindings; their focused matrix fixtures own generated public topology and
  mutation acceptance. The corrected owner-ratified ruling supports DCS:82 on the repaired valid
  witness: one concrete core producer projects to the consumer. The former plain same-name part
  shape is invalid and blocks before occurrence expansion.
- **audit-F22/F23 — remediated.** A kept test executes the real runner over all 37 fixtures and
  compares every recorded route outcome with the ledger. Discovery is also called and checked
  directly.
- **audit-F24 — remediated.** Public mutation comparison first requires identical complete input
  key sets, including a negative test for a phantom input. The C23 public JSON override remains the
  intended public action.
- **audit-F25 — corrected and remediated.** Identity and redefinition failures were already coded.
  Multiplicity and recursive-containment failures now use the fixed catalog and cross the strict
  boundary as structured diagnostics.
- **audit-F26 — intentionally retained for Item 6.** The dual-run legacy oracle remains Item-5
  scaffolding and will be replaced when Item 6 deletes that route.
- **audit-F27 — remediated.** Finite constant integer expressions expand. Unresolved, unsupported,
  invalid, and recursive shapes have distinct named outcomes.

Post-ruling validation: 152 exact-elaboration tests pass, including the live 37-fixture ledger
comparison; the full licensed codegen gate passes 3307 / 47 / 18 with no xfails; changed-file
Ruff/format and `git diff --check` pass; mypy remains at its 72-error baseline with no errors in the
new route. The implementation response has no remaining owner-grade disposition; an independent
re-audit owns certification.

## audit — 2026-08-09 — rev 6bed968-dirty (v3 certification)

**Point (re-derived):** Every supported model-derived consumed value binds at the semantic referent KerML name resolution supplies (written form × binding-owner context, per the contract referent table); one semantic source occurrence — declaration identity **plus concrete occurrence identity** — produces exactly one runtime source, and every and only its calculation, constraint, and aggregation consumers resolve to that source; `:>>` applies innermost-wins at each featuring instance; identity is extraction-owned and never reconstructed from name/text material; acceptance is off-default mutation at the public boundary; loud failure is confined to unsupported and deferred forms. [source: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` invariants 54, 55, 56, 57, 59, 60, the referent table (lines 313–324) and the `Redefinition (:>>)` definition (line 307); `.project/backlog/epic_elaborate_first_architecture.md` Critical Success Factor (line 31) and owner ruling line 67; graded via `constraint-execution-lifecycle-requirements.md` LC-SI-02 [HARD], LC-SI-04 [HARD], LC-SI-09 [NEED], LC-SI-08/13/14/22 [INHERITED]. **grade: owner / [HARD]**. The "Deep-cross-scope evidence boundary" paragraph (lines 326–332) is **agent / ratified**, not owner-grade.]

**Falsifier:** one modeled part usage yields more than one concrete occurrence (or one authored `:>>` override lands on an occurrence its consumers do not read); or a supported form's concrete occurrence is selected by name/text material; or a blocking diagnostic is justified by a recorded premise that the loaded model contradicts.

**Findings:**

- **audit-F28 [DON'T]** One modeled part usage is elaborated into parallel occurrence subtrees, and the authored `:>>` override lands on a duplicate its consumers never read. `deep_cross_scope_probe` declares exactly one `station`, one `array`, one `sensor` (design.sysml:53–58, library.sysml `'Monitoring Station'::array`, `'Sensor Array'::sensor`). Elaboration at this rev produces **two `array` occurrences and three `sensor` occurrences**: three `…__station__array__sensor__reading` AttrNodes with identical display paths — two carrying `value=None` on declaration `0d754e49…` (the inherited def-level `reading`) and one carrying `10.0` on declaration `686c8200…` (the design's `:>> reading = 10.0`) — plus three `…__sensor__core` CalcNodes and two `…__derived_calc` CalcNodes. Cause: `build_feature_slot_index` (`src/sysml_codegen/elaboration/occurrence.py:110-140`) builds slot families **only** from parser `owned_redefinitions`, and SysIDE materializes no redefinition edge between `DeepCrossScopeDesign::measurement_system::station::array` and `'Monitoring Station'::array` (verified live: both carry `redef: []`). A design that re-declares a nested usage of its own definition therefore forks the occurrence tree instead of overriding it. Invariant 56 requires one occurrence → one runtime source; the contract's `:>>` definition requires the definition default to apply at each featuring instance **unless that occurrence supplies an override**. Either (a) these are one occurrence and the elaborator splits it — an invariant-56 violation and a failure of the epic's core "apply `:>>` innermost-wins" promise — or (b) SysML genuinely means three sensors, in which case three distinct sources render to one identical public path (the audit-F17 collision class, unfixed, merely unreachable). The repo records neither branch. Only DCS trips this across all 37 corpus fixtures; the one-level case (`nested_occurrence_override_probe`) resolves correctly to a single `reading = 80.0`. — contract inv 55/56 + `:>>` definition (**owner/[HARD]**) — falsifier: elaborate `deep_cross_scope_probe` and assert one `sensor__reading` node carrying 10.0; three exist, two unset. — **disposition: BLOCK**

- **audit-F29 [DON'T]** *(capture-fidelity §4 surfacing — the owner ratified this on a premise the loaded model falsifies.)* The ratified amendment states that DCS:82 "supplies only a leaf declaration and does not identify one of its three concrete producer occurrences" and is "unsupported until **the parser** supplies exact occurrence identity" (contract lines 326–332). Both halves are wrong at this rev. There are not three concrete producer occurrences — the model declares one; the three exist only because of audit-F28. And the parser is not what drops the path: for a `::` reference our own extractor builds `ResolvedSemanticReferenceFact(root=segments=leaf=referent)` and discards every intermediate segment (`src/sysml_codegen/extraction/binding_evidence.py:207-215`), so `_resolve_semantic_reference` sees a one-segment path and falls to `_resolve_leaf` regardless of what the six written segments named. `SI_OCCURRENCE_AMBIGUOUS: consumer context contains 3 calculation nodes` is the elaborator diagnosing its own duplication, then that diagnosis being recorded as an external parser limitation and blessed as `expected-collapse` (`diff-ledger.md:13`). Item 5's stop condition says a shape that raises a semantics question the contract does not answer goes to the owner; this one went to the owner with the wrong question. — amendment is **agent/ratified** (contradicting it disposes, not blocks), but the *dependent conclusion* it clears is owner-grade — falsifier: the amendment says three producer occurrences exist; the model declares one and the graph's two extras carry `value=None`. — disposition: DISPOSE-and-surface — the amendment must be re-put to the owner with audit-F28's evidence before it is treated as settling the C5/DCS witness; dependent conclusions (the DCS ledger row, matrix C5's scoping) are parked meanwhile.

- **audit-F30 [DO]** The AST guard added for audit-F20 protects one function, not the mechanism. `test_leaf_resolution_never_reads_display_or_qualified_name_metadata` (`tests/unit/test_elaboration_import_boundaries.py:38-59`) walks only the `_resolve_leaf` FunctionDef. The sibling selectors that do the same job — `_contextualize_root`, `_select_occurrences`, `_select_calc_nodes` (`elaborate.py:1118-1232`) — are unguarded, and re-introducing display-path selection in any of them keeps the guard green. Clean at this rev; the guard just does not hold the line it was added for. — my inference from the guard's stated purpose ([AGENT]/[INFERRED]) — falsifier: add `node.display_path.endswith(...)` to `_select_calc_nodes`; the suite stays green. — disposition: DISPOSE — extend the AST check to the whole resolution surface.

- **audit-F31 [DO]** Two fail-open branches survive in occurrence selection, mirroring the audit-F8 class. `_select_occurrences` returns **every candidate occurrence in the model** when `plural=True` and neither the consumer's lineage nor any lineage-anchored descendant search matched (`elaborate.py:1166-1167,1191-1192`) — resolution outside the consumer's context, which invariant 55 assigns to a named ambiguity diagnostic. The mirror image also holds: `_contextualize_root` ignores `plural` on the calc-root branch (`:1136-1147`), so a legitimately plural aggregation rooted at a multi-occurrence calc usage fails closed. I did not reproduce either on a corpus fixture, so I state reachability as unproven. — contract inv 55/56 (**owner/[HARD]**), evidence tier weak — falsifier: two independent parents each owning children of one declaration, with an aggregation authored in one parent; assert its terms cover only that parent's children. — disposition: DISPOSE — author the fixture; if reachable, replace the fallback with `SI_OCCURRENCE_AMBIGUOUS`.

**Smells checked (1, 3, 4, 5, 6) — two fired; escalation is not resolution:**
- **Smell 3 — a special category exempts a case whose user-visible meaning is unchanged** (audit-F28/F29): "deep producer-output form, unsupported until the parser supplies exact occurrence identity" is a category invented for one fixture. Its user-visible meaning is an ordinary qualified reference to one producer output — the same meaning as the C5 form the matrix certifies as supported. The category exists because the occurrence tree is wrong, not because the form differs.
- **Smell 6 — a test passes only because it selects one route or interpretation** (audit-F28): `test_supported_usage_context_baselines_resolve_before_the_deep_path_block` (`test_elaboration_phase5_remediation.py:89-117`) runs the **internal** route and asserts `"3 calculation nodes" in deep_path.detail` — the duplication is pinned as the expected outcome, in a free-text detail string. All 49 tests in the five key files pass at this rev with a live license; the green suite is what makes this finding invisible.
- **Smell 1 not fired**: the ledger is now compared against a live 37-fixture run (`test_elaboration_corpus_ledger.py:47-50`), and the enum/exception duplication is collapsed — `IdentityBoundaryError`, `InvalidRedefinitionFamilyError`, `MultiplicityExpansionError`, `RecursiveContainmentError` all carry `ElaborationCode` through `ElaborationInvariantError`.
- **Smell 4 not fired**: leaf resolution no longer reads rendered material; the runtime matrix cells assert generated YAML/JSON, not `InstanceGraph` shape.
- **Smell 5 not fired.**

**Resolves:**
- audit-F20: **FIXED** — authority: contract inv 55/60 (owner/[HARD]) satisfied — basis: I re-read the resolver myself. `_resolve_leaf` (`elaborate.py:1255-1300`) takes only a `DeclarationId` and a `ScopeId`; no qualifier text reaches it (`grep written_qualifier src/` hits only `source_evidence.py`, `binding_evidence.py`, and the legacy `usage_extractor.py`), no `display_path`/`startswith`/`endswith` remains, and the fallback is lineage → lineage-anchored descendants → fail-closed `SI_OCCURRENCE_AMBIGUOUS`. `_select_occurrences`/`_select_calc_nodes` select by occurrence and declaration identity only. The fail-open "empty contextual set → discard the qualifier" branch is gone. Residual guard-scope gap filed as audit-F30; residual fail-open branches as audit-F31.
- audit-F21: **NOT RESOLVED** — authority: none available — basis: the code change is real but the clearing authority is the amendment, and its premise is false (audit-F29). The v2 finding said the repo "does not record which three renderings collide"; the answer is that they are three renderings of **one** modeled sensor (audit-F28). Re-anchored as audit-F28 (the defect) and audit-F29 (the mis-recorded premise). audit-F16 stays unresolved with it.
- audit-F22: **FIXED** — basis: `test_dual_run_ledger_outcomes_match_a_live_corpus_run` executes the real runner over all 37 fixtures and compares counts, codes, and difference sections against the parsed ledger; verified passing with a live license.
- audit-F23: **FIXED** — basis: `test_corpus_runner_discovers_the_same_closed_fixture_set` now calls `discover_fixture_names()` and compares sets; no source-text assertion remains.
- audit-F24: **FIXED** — basis: `_assert_only_expected_public_changes` asserts `changed.keys() == baseline.keys()` before comparing values, with a kept negative test for a phantom input (`test_elaboration_contract_matrix.py:688-696`).
- audit-F25: **FIXED** — basis: every elaboration-path failure now carries an `ElaborationCode` through `ElaborationInvariantError` (`diagnostics.py:28-34`; `identity.py:40-46`; `occurrence.py:36-55`); the enum has no member naming a condition raised uncoded.
- audit-F27: **FIXED** — basis: finite constant integer bounds expand; the remaining rejections carry distinct `SI_MULTIPLICITY_UNRESOLVED` / `_UNSUPPORTED` / `_INVALID` codes rather than one "non-finite" name.
- audit-F26: **DEFERRED** — authority: `[AGENT] (ratified by owner, 2026-08-09)` — basis: legacy-oracle compatibility assertion retained as Item-5 scaffolding, to be deleted with the legacy route at Item 6.
- audit-F19: **DEFERRED** — authority: prior disposition, Item 6 — basis: unchanged; 25 of 37 corpus rows still produce no graph and neither customer-scale composition has a corrected variant.
- audit-F1, F3, F2, F4, F7, F8, F11–F15, F17, F18: unchanged from their prior recorded resolutions.

**Gate: BLOCKED (audit-F28).** audit-F29 is DISPOSE-and-surface and must reach the owner before the DCS/C5 disposition is treated as settled; audit-F30 and audit-F31 are DISPOSED; audit-F19 and audit-F26 remain deferred to Item 6. Recorded so the gate is not misread as a general negative: the audit-F20 remediation is genuine and clean — string-based occurrence selection is gone from the exact route, the runtime matrix now certifies 21 cells through generated YAML/JSON with key-set-exact off-default mutation on both live and relocated routes, the corpus ledger is machine-verified against a live run, and the diagnostic vocabulary is unified. One defect stands between this and a clear gate, and it is on the contract's own witness fixture: one modeled part usage becomes three occurrences, the authored override lands on the wrong one, and that self-inflicted ambiguity was recorded to the owner as a parser limitation.

**Auditor verification note (v3 audit, same date):** audit-F28 was independently reproduced by the auditor before this block was accepted: a live lenient elaboration of `deep_cross_scope_probe` yields exactly the claimed duplicates — three `…__sensor__reading` AttrNodes (two `value=None` on declaration `0d754e49…`, one `10.0` on `686c8200…`), three `…__sensor__core` CalcNodes, two `…__derived_calc` CalcNodes, and the single `SI_OCCURRENCE_AMBIGUOUS` diagnostic on `ref_analysis.data_point` reading "consumer context contains 3 calculation nodes". The fixture declares one `station`, one `array`, one `sensor`. The observed counts match the no-implicit-redefinition fork exactly (inherited `array` + declared `array`; the declared `array` holding inherited + declared `sensor`).

**Auditor semantics addendum (v3 audit, same date):** a clause-cited SysML v2 spec consultation
(Part 1 §7.6.3; KerML §7.3.2.1, `validateNamespaceDistinguishibility`,
`Membership::isDistinguishableFrom`; recorded in the v3 audit session) refines audit-F28's branch:
SysML v2 has **no name-based implicit redefinition** for nested usages, so the DCS shape as written
is an **invalid model** (owned `array`/`sensor` collide with same-named inherited features of a
conforming metaclass; the spec's resolution is an explicit redefinition). The elaborator's 3-way
fork is the literal parse of that invalid model — neither lens branch (a) nor (b) as stated. The
BLOCK stands with the corrected mechanism: the toolchain **silently admits** the invalid shape
(no distinguishability diagnostic anywhere; the authored `:>>` override lands on one of three
same-named copies; the only symptom is a mis-attributed consumer ambiguity), violating invariant
59's loud-failure boundary, and the F21 amendment recorded that outcome as a parser
occurrence-identity limitation (audit-F29 unchanged: re-put to owner with corrected evidence).
Fix shape per `audit_v3.md`: diagnose the conflict loudly at the model shape, repair the witness
fixture with explicit `:>>`, then re-test the deep DCS:82 reference on the valid fixture.

## Implementation response to audit v3 — 2026-08-09

This is remediation evidence for the next independent audit, not self-certification.

- **audit-F28 — remediated.** A red-first kept fixture now authors inherited/owned same-name
  `PartUsage` conflicts and observes SysIDE's existing `namespace-distinguishability` diagnostics
  (`tests/conformance/test_elaboration_model_validation.py`). The exact-route API requires loader
  validation diagnostics. It promotes that upstream code only when its source site is a semantic
  `PartUsage`, emitting `SYSML_NAMESPACE_NOT_DISTINGUISHABLE` before the occurrence walker runs
  (`src/sysml_codegen/elaboration/elaborate.py`). Strict mode raises the named diagnostics; lenient
  mode returns a diagnostic-only graph with no attributes, calculations, or constraints. Other
  namespace warnings in ten corpus fixtures remain outside this narrow part-conflict policy.
- **audit-F29 — corrected and re-ratified.** `deep_cross_scope_probe` now uses explicit `part :>>`
  redefinitions for both `array` and `sensor`. Live SysIDE validation is clean; exact elaboration
  produces one sensor/core occurrence and one `reading = 10.0`; DCS:82 resolves to that core's
  `metric_value` output and projects publicly as a module-output edge
  (`tests/conformance/test_elaboration_phase5_remediation.py`). The owner ratified the corrected
  agent recommendation on 2026-08-09. The existing contract paragraph was amended in place: DCS:82
  is supported on the valid witness, while the former invalid shape blocks before expansion.
- **Ledger correction.** DCS now compares legacy `graph 5/7/0/0` with exact `graph 5/4/0/1`
  across `M/E/O/A` and is an `expected-fix`. The live comparison exposed and fixed the runner's
  dormant `aliases` section-key mismatch. The ledger totals are 26 `expected-collapse`, 11
  `expected-fix`, and zero unresolved rows.
- **Scope held.** audit-F30 and audit-F31 remain separate non-blocking follow-ups. audit-F19 and
  audit-F26 remain deferred to Item 6. No name, qualified name, rendered path, or authored qualifier
  was added to semantic slot, occurrence, or edge selection.

Final remediation gates pass: 154 exact-elaboration tests, including the 31-test matrix and 3/3
live ledger comparison; 3309 codegen tests with 47 skipped and 18 deselected; and 1814 coordinated
agentic-mbse tests with one skipped and 33 deselected. Changed-file Ruff and format are clean. Mypy
remains at the accepted 72-error baseline with zero errors in the exact route.

The implementation evidence supports resolving audit-F28, audit-F29, the re-anchored audit-F21,
and audit-F16. An independent audit owns that verdict. Item 6 has not begun.

## audit targeted re-verification — 2026-08-09 — rev 6bed968-dirty (audit-v3 remediation)

This block records the independent targeted review of the audit-v3 remediation, run by the same
auditor that produced the v3 block. Every claim below was verified against the working tree and
live licensed runs, not the plan's record.

Resolves:
- audit-F28: **FIXED** — authority: owner (corrected checkpoint ratification 2026-08-09,
  `plan.md` audit-v2/v3 decision record) + contract inv 59 satisfied — basis: the invalid
  inherited/owned part-namespace conflict now blocks loudly **before occurrence expansion**.
  `elaborate()` requires `validation_diagnostics` (keyword-only, no default — a missed caller is a
  TypeError), and `_blocking_model_validation_diagnostics` (`elaborate.py:174-206`) promotes
  SysIDE's own `namespace-distinguishability` diagnostics at PartUsage sites to blocking
  `SYSML_NAMESPACE_NOT_DISTINGUISHABLE` with the `:>>` repair hint; strict raises, lenient returns
  an empty graph with only those diagnostics — the duplicate tree is never built
  (`tests/conformance/test_elaboration_model_validation.py`, 2 kept licensed tests over the
  preserved-invalid-shape fixture `elab_namespace_distinguishability_probe`, verified passing).
  The witness fixture is repaired with explicit `:>> array` / `:>> sensor` (the spec's own
  resolution); the kept strict test asserts exactly one `sensor__reading` node carrying 10.0 — the
  v3 falsifier — and wires DCS:82's `ref_analysis.data_point` to the single
  `…__sensor__core__metric_value` producer channel through public projection
  (`test_elaboration_phase5_remediation.py::test_valid_deep_cross_scope_redefinitions_resolve_every_reference`,
  verified passing). Live corpus run confirms the ledger row: exact `graph 5/4/0/1` vs legacy
  `5/7/0/0`, `expected-fix`.
- audit-F29: **FIXED** — authority: owner (corrected recommendation ratified 2026-08-09; contract
  amendment rewritten in place, still honestly `[AGENT] (ratified by owner, 2026-08-09)`) — basis:
  the amendment's premise now matches the verified facts: DCS:82 is a **supported**
  producer-output reference on the valid witness; the former plain same-name declarations were an
  invalid namespace shape, not three legitimate producer occurrences; "No name or authored
  qualifier selects the supported edge" (verified — the resolution path is the F20-clean identity
  mechanism). The dependent conclusions are un-parked: the DCS ledger row is rewritten as
  `expected-fix` and the "3 calculation nodes" test expectation is replaced by the ProducerRef
  assertion. The smell-3 "unsupported deep form" category is dissolved rather than defended.
- audit-F30: **stands DISPOSED, not yet executed** — the AST guard still covers `_resolve_leaf`
  only (`test_elaboration_import_boundaries.py:38-59` unchanged). Non-blocking; the disposition
  (extend to the full resolution surface) remains open work.
- audit-F31: **stands DISPOSED, not yet executed** — the plural fallback branches remain
  (`elaborate.py:1210,1235`); the reachability fixture is unauthored. Non-blocking.

Gates at this verification (all live, zero `no live syside license` lines): focused
validation/remediation/ledger 15 passed; exact-elaboration selection 154 passed (matches the
plan's corrected count); contract matrix 31 passed within that selection; full codegen
3309 / 47 / 18; agentic-mbse 1814 / 1 / 33; mypy 72-error baseline with 0 in new-route files;
`git diff --check` clean; legacy dirs zero diff; no baseline or `extraction_snapshot.json`
modified; live corpus reproduces all 37 ledger rows (kept test) including the rewritten DCS row.

Gate: **DISPOSED (audit-F30, audit-F31)** — no BLOCK remains anywhere in this ledger by
citation-scan: F1–F3, F11–F18, F20–F25, F27 FIXED; F19/F26 DEFERRED to Item 6 by ratified
decision; F28/F29 FIXED above.
