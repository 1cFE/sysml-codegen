# Product-Lens Ledger: Exact-Identity Completion

## spec — 2026-08-09 — rev `.project/active/elaborator-identity-completion/spec.md`

Epic: ELABORATE-FIRST

Point (re-derived): Codegen must carry SysIDE's exact declaration identity through concrete
occurrence identity into one runtime source for every and only its bound consumers; names and
ordering never recover or select identity. [source: `.project/active/elaborator-design/design.md`
“The Point” and `.project/backlog/epic_elaborate_first_architecture.md` Mission invariant, grade:
owner]

Falsifier: An off-default public mutation fails to reach every intended calculation, constraint,
or aggregation consumer, reaches an independent source, or changes attachment after a rename,
same-name collision, or enumeration reorder while the resolved UUID is unchanged.

Findings:
- spec-F1 [DO] Success Criteria require the existing 29-cell suite to “remain green” but never
  require Item 6's still-owed public off-default mutation proof for every runtime-source cell; the
  spec can pass while exact identity remains unproven at the product boundary. —
  `.project/backlog/epic_elaborate_first_architecture.md` Mission invariant and
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` invariant 57 /
  Appendix C route-and-mutation obligations (owner) — disposition: BLOCK

Smells: none.

Gate: BLOCKED (spec-F1)

## spec — 2026-08-09 — rev `.project/active/elaborator-identity-completion/spec.md`

Epic: ELABORATE-FIRST

Point (re-derived): Codegen must carry SysIDE's exact declaration identity through concrete
occurrence identity into one runtime source for every and only its bound consumers; names and
ordering never recover or select identity. [source: `.project/active/elaborator-design/design.md`
“The Point” and `.project/backlog/epic_elaborate_first_architecture.md` Mission invariant, grade:
owner]

Falsifier: An off-default public mutation misses an intended consumer, changes an independent
source, or attachment changes after an identity-preserving rename, collision, or enumeration
reorder.

Findings: none.

Smells: none.

Resolves:
- spec-F1: FIXED — authority: owner — basis: Success Criteria now require off-default mutation for
  every runtime-source matrix cell through the exact route at the public generation boundary,
  reaching every and only its bound consumers.

Gate: CLEAR

## audit — 2026-08-09 — rev `phases 1-2 uncommitted @ codegen b9c22c0`

Epic: ELABORATE-FIRST

Point (re-derived): SysIDE has already resolved which declaration a reference denotes; codegen
carries that exact identity through payload, occurrence, and graph so one semantic source occurrence
becomes exactly one runtime source, and an unsupported form fails loudly before generation. Names,
QNs, and enumeration order describe after resolution; they never select. The shipped legacy route is
frozen while this happens. [source: `.project/backlog/epic_elaborate_first_architecture.md` Mission
invariant + Item 6 [OWNER] authority; `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
invariants 55/59/60 (and 48/50 for the published catalog), grade: owner for the mission invariant,
agent/ratified-INHERITED for the contract invariants]

Falsifier: Perturb display metadata (name, QN, member order) while holding resolved UUIDs fixed and
the selected executable payload moves or defaults; or a required payload is absent and generation
proceeds instead of naming a diagnostic; or the frozen legacy route's accepted-model set changes.

Findings:
- audit-F1 [DON'T] The exact route publishes a SysIDE parser UUID as the constraint catalog's
  `predicate_source_key` (`src/sysml_codegen/elaboration/elaborate.py` `_constraint_metadata`,
  `definition:{uuid}`), where the shipped route publishes the model-derived QN. Verified live on
  `tests/fixtures/constraint_shared_polarity`: legacy `definition:constraint_shared_polarity::'Within Bound'`
  vs exact `definition:ffff4ad4-27f2-5df0-9b23-b57063eb58b5`. That key is the explicit join TEAx
  consumes and it feeds the catalog fingerprint (`src/sysml_codegen/generation/constraint_catalog.py:141`).
  The design records `element_id` as a SysIDE-internal, possibly-deprecated, QN-derived value, so a
  SysIDE upgrade would rewrite public catalog bytes and stored fingerprints. Exactness is already
  carried internally by `ConstraintNode.effective_definition_id`; the public string should be
  rendered from the exact definition at projection (R5/D8), not minted in the semantic layer. —
  contract invariants 48/50 + spec Non-Goal "changing generated public naming policy"
  (agent/ratified) — disposition: audit.md 2026-08-09 — fix required before Phase 3 proceeds
- audit-F2 [DON'T] Phase 1 changed the *shared* extractor, not a new-route-only path:
  `SysMLDataExtractor._required_declaration_id` (`src/sysml_codegen/extraction/extractor.py`) now
  raises a bare `ValueError` for any calculation definition or member with a null QN or a non-v5
  UUID — namespace-collision victims and anonymous members the legacy name-keyed route previously
  extracted. The 37-fixture bytes are unchanged, but the frozen shipped live route's accepted-model
  set narrowed, with an unnamed exception, inside an item scoped "new route only; shipped authority
  unchanged". The plan's own risk posture said sidecars are "optional at the shared extraction
  dataclass but mandatory at the live exact-route boundary". — epic Item 6 Type line + spec R10
  (agent/ratified) — disposition: audit.md 2026-08-09 — fix or owner-visible scope note required
- audit-F3 [DO] The mechanical gate that would classify the corpus consequences of F1 is dead, not
  merely red: `tests/conformance/test_elaboration_corpus_ledger.py` fails with
  `FileNotFoundError: .project/active/elaborator-breadth/diff-ledger.md` (the ledger moved to
  `.project/completed/20260809_elaborator-breadth/` at Item-5 close; failure predates Phase 1 and is
  the recorded pre-change baseline). The corpus diff signature includes the full catalog dump
  (`src/sysml_codegen/elaboration/diff.py:76-85`), so every definition-typed constraint fixture now
  carries an unclassified catalog diff behind a gate that cannot run. — epic "zero unclassified
  diffs" gate (agent/ratified) — disposition: audit.md 2026-08-09 — repair gate path before Phase 5
  relies on it
- audit-F4 [DO] Constraint consumer input ports keep the fail-open default the phase claims to have
  removed: `_collect_bound_members` still writes `PortMetadata(python_type="float", ...)` when the
  consumer is a `ConstraintNode` (`src/sysml_codegen/elaboration/elaborate.py:1063-1072`), because
  `_calculation_input_attribute` is only consulted for `CalcNode`. Calculation ports are now exact
  and total; constraint ports are not. — spec Success Criterion 2 / R6 (INHERITED) — disposition:
  DEFERRED — plan Phase 4 "Closed executable state" bullet owns removing default `PortMetadata()`
  reads for required ports

Smells (escalated into the audit's Product Judgment):
- Smell 1 (two representations manually kept synchronized) — `CalculationDefinitionData` carries
  paired name-keyed and ID-keyed maps written side by side in one extractor loop, and
  `compile_calc_def_exact` is a ~200-line second dependency walk beside `compile_calc_def`; the
  plan's own mitigation was "share the AST walk internally". Transitional until Item 7 deletion.
- Smell 3 (special category exemption) — `InstanceGraph._validate_calculation_payload` returns
  early for `node.is_computed`, and `_validate_consumer` enforces input totality only
  `if not self.diagnostics`.
- Smell 4 (correctness depends on downstream knowledge of an internal representation) — the F1
  parser UUID crossing into the TEAx-consumed catalog join and fingerprint.
- Smell 6 (a test passes only by selecting one route/interpretation) — the F3 dead gate: phase
  green evidence rests on excluding the one file that compares the two routes' public output.

Gate: DISPOSED (audit-F1, audit-F2, audit-F3, audit-F4)

## audit remediation — 2026-08-09 — rev `working tree`

Resolves:
- audit-F1: FIXED — definition-typed public source keys are rendered from definition display
  metadata at projection; parser UUIDs stay internal.
- audit-F2: FIXED — shared extraction records live identity sidecars opportunistically; exact-route
  enforcement remains `SI_ID_MISSING`.
- audit-F3: FIXED — the gate reads the archived Item-5 ledger and reaches the live comparison. Its
  current `return_styles` outcome mismatch is assigned to the in-flight Phase 3–4 work before
  Phase 5 certification.

Gate: DISPOSED (audit-F4 remains deferred to Phase 4)

## audit — 2026-08-09 — rev `phases 3-4 uncommitted @ codegen b9c22c0`

Epic: ELABORATE-FIRST

Point (re-derived): SysIDE has already resolved which declaration a reference denotes; codegen
carries that exact identity through occurrence context and the graph so one semantic source
occurrence becomes exactly one runtime source for every and only its bound consumers, and an
unsupported authored form fails loudly with its own named diagnostic before generation. Names, QNs,
rendered paths, and enumeration order describe after resolution; they never select, and a missing
required payload never defaults. The shipped legacy route stays frozen.
[source: `.project/backlog/epic_elaborate_first_architecture.md` Critical Success Factor + Item 6
Success Criteria; `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
invariants 19/20/26/55/56/59 and D-1/D-4; grade: owner for the mission invariant and the `in R = R`
hard-diagnostic ruling, agent/ratified-INHERITED for the contract invariants and the Item-6 gates]

Falsifier: Hold resolved UUIDs fixed and perturb display metadata (a name needing sanitization, a
member reorder, a rendered path) and the executable payload attached to a port moves or silently
defaults; or a supported authored form that previously produced its own named diagnostic is instead
rejected by an unrelated invariant error; or a corpus row's exact-route outcome changes with no
classification.

Findings:
- audit-F5 [DON'T] Projection joins constraint formal provenance by rendered name and fabricates
  the payload when the join misses, instead of using the exact formal already on the port.
  `_predicate_identities` keys identities by the IR leaf's raw `source_name`
  (`src/sysml_codegen/elaboration/project.py:650-683`) while `_build_constraint_modules` looks them
  up by the sanitized `param_name` and, on a miss, substitutes
  `ConstraintFormalIdentity(raw_name=param_name, qualified_name=None)`
  (`src/sysml_codegen/elaboration/project.py:754-767`). The two strings diverge for any formal whose
  name is not already a Python identifier. Reproduced live: a constraint definition with
  `in attribute 'max power' : Real` projects `raw_name='max_power', qualified_name=None` for that
  input while its sibling `limit` carries the real QN. The frozen legacy route builds the same field
  structurally from the formal fact (`src/sysml_codegen/analysis/constraint_lowering.py:850-857`),
  so the exact route is the weaker one. Consequence: the wrapper name-safety guard treats only
  `formal_identity is None` as missing provenance (`src/sysml_codegen/generation/modules.py:257`,
  `src/sysml_codegen/generation/constraint_name_safety.py:385`), so a fabricated identity passes,
  and identity keys built from a null QN let two distinct formals with equal raw names collapse to
  one key inside `validate_scope_bindings`. This is the same fail-open class as audit-F4, which
  Phase 4's "Closed executable state" bullet claimed to close. —
  contract invariants 19/20/55 + Item 6 Success Criterion 2 (agent/ratified; it is the guard on an
  owner-grade invariant) — falsifier: author a constraint def formal named `'max power'`, bind it,
  project through the exact route, and assert `formal_identity.qualified_name` equals the formal's
  QN; it is `None` today — disposition: fix before Phase 5 certification; join the IR feature
  reference to its exact `ConsumerPortId`/target declaration, and make an unjoinable formal a named
  D10 diagnostic rather than a synthesized identity
- audit-F6 [DON'T] Phase 3–4 narrowed the exact route's accepted-model set on a supported authored
  form, and it lands as an unclassified corpus diff while both phases are checked complete.
  `tests/conformance/test_elaboration_corpus_ledger.py::test_dual_run_ledger_outcomes_match_a_live_corpus_run`
  fails at the working tree: `return_styles` now yields `error: SI_REDEFINITION_INVALID` where the
  Item-5 ledger records `error: 3× SI_SELF_BINDING`. **[AGENT] 2026-08-09 causal correction:**
  `_build_value_nodes` admitted the unscoped `StyleD::y` return attribute after Phase 3 removed the
  prior scope gate. That slot roots at the library declaration
  `Performances::Evaluation::result`, which is outside the loaded exact `AttributeUsage`
  population, so the model died before binding analysis. The rejected slot is not the supported
  bare-`in` `BareInC::x` ReferenceUsage formal. The three authored self-bindings (`in a = a`,
  `in b = b`, `in d = d`) therefore no longer produced their diagnostic. —
  epic Item 6 Success Criterion 5 ("37 corpus rows remain green-or-named-diagnostic with zero
  unclassified diffs") and contract invariant 59 (the self-binding diagnostic is not suppressed);
  the underlying `in R = R` hard-diagnostic ruling is [OWNER-VERBATIM] D-4, though it is the
  diagnostic's identity and not its existence that regressed (agent/ratified) — falsifier: run the
  corpus ledger gate at the audited tree; `return_styles` diverges from its recorded outcome —
  disposition: restore the scoped-value admission boundary so `SI_SELF_BINDING` fires again, or
  reclassify the row with owner-visible evidence; the corpus gate must be green before Phase 5 can
  certify. Note the Phase 3 and Phase 4 validation checklists never listed this gate, which is why
  both phases read complete over a red one.

Smells (escalated into the audit's Product Judgment):
- Smell 4 (correctness depends on downstream knowledge of an internal representation) — audit-F5:
  the constraint catalog's formal provenance is recovered by matching two independently rendered
  spellings of the same feature, and the downstream name-safety validator's null check is the only
  thing standing between that and a wrong wrapper binding. Related, lower stakes:
  `_constraint_module_type` still re-splits a rendered instance path to mint the module-type
  namespace (`src/sysml_codegen/elaboration/project.py:711-723`) — rendering from rendering, with no
  collision guard on the result.
- Smell 6 (a test passes only by selecting one route or interpretation) — audit-F6: the Phase 3 and
  Phase 4 green evidence is a set of focused runs that excludes the one gate comparing every corpus
  row's exact-route outcome to its classified record, and that gate is red.
- Smell 3 (special category exempts a case whose user-visible meaning is unchanged) — NOT escalated
  this round. `_validate_consumer`'s `if not self.diagnostics` totality relaxation
  (`src/sysml_codegen/elaboration/graph.py:388`) survives, but `require_projectable`
  (`src/sysml_codegen/elaboration/graph.py:631-635`) now rejects any diagnostics-carrying graph
  before projection, so the relaxed path cannot reach generation.

Resolves:
- audit-F4: FIXED — authority: agent/ratified (verified in code) — basis: the constraint-consumer
  port default is gone; `_collect_bound_members` and `_collect_unbound_constraint_formals` now read
  `_feature_python_type`, which resolves exactly one `FeatureTyping` relationship off the exact
  declaration and raises `SI_EDGE_DANGLING` on zero, multiple, or unsupported typings
  (`src/sysml_codegen/elaboration/elaborate.py:1096-1172, 1251-1282`). Verified: the literal
  `python_type="float"` write for constraint ports no longer exists, and `_metadata` in projection
  indexes `input_metadata` directly rather than defaulting (`project.py:136-137`).
- audit-F5: FIX IMPLEMENTED 2026-08-09; independent re-audit pending — exact constraint ports carry
  declaration-bound raw/QN provenance through graph validation and codec v2; projection no longer
  joins or fabricates identity by rendered name. The quoted `'max power'` regression and malformed
  codec regression pass.
- audit-F6: FIX IMPLEMENTED 2026-08-09; independent re-audit pending — restored the scoped-value
  admission boundary. The causal claim was corrected above: `StyleD::y`, rooted at
  `Performances::Evaluation::result`, was rejected, not the bare-`in` formal. The corpus-ledger gate
  is green and `return_styles` again reports exactly `3× SI_SELF_BINDING`.

Gate: DISPOSED (audit-F5, audit-F6)

## audit — 2026-08-09 — rev `phases 1-5 uncommitted @ codegen b9c22c0`

Epic: ELABORATE-FIRST

Point (re-derived): SysIDE has already resolved which declaration a reference denotes; codegen carries that exact identity through payload, occurrence, graph, and projection so one semantic source occurrence becomes exactly one runtime source reaching every and only its bound consumers — and any form the toolchain does not support fails loudly, by name, before generation. Names, QNs, rendered paths, and enumeration order describe after resolution; they never select. Exactly one authority decides semantic identity. [source: `.project/backlog/epic_elaborate_first_architecture.md` Critical Success Factor + Success Criteria (mission invariant); `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` invariants 1/9/11/19/20/26/55/56/59/60, D-1/D-4, and the Simplification constraint; grade: **owner** for the mission invariant, D-4, D-1 and the simplification constraint; agent/ratified for the numbered invariants and the Item-6 gates]

Falsifier: A model the contract refuses to execute reaches a generated module instead of a named halt; or an off-default public mutation misses a bound consumer or moves an independent one; or holding resolved UUIDs fixed and perturbing display metadata changes payload attachment, occurrence selection, or projected wiring.

Findings:
- audit-F7 [DON'T] **The exact route never halts on a profile `BLOCK`; it generates an executable module for a predicate the contract says must not execute.** `elaborate()` stores `decision.eligibility` and moves on (`src/sysml_codegen/elaboration/elaborate.py:1047`); nothing in `elaborate.py`, `graph.validate/require_projectable`, or the exact entry point has an equivalent of the shipped route's `_raise_on_blocking` (`src/sysml_codegen/analysis/constraint_lowering.py:588-590,749`). Projection then treats `BLOCK` as executable: `_build_constraint_modules` skips only `NON_NUMERICAL` and `UNASSESSED` (`project.py:727,736`), so a `BLOCK` constraint falls through into a `ModuleKind.CONSTRAINT` module and a concrete catalog entry with its predicate IR. The item's own new fixture is the live case: `tests/fixtures/elab_payload_identity/model.sysml:12` asserts `observed == limit` on Reals, and `tests/conformance/test_elaboration_payload_identity.py:194` pins it as an accepted graph node with no halt asserted anywhere. The shipped legacy route rejects this model loudly; the exact route, which Item 7 is meant to promote to sole authority, would ship it. — epic mission invariant "unsupported forms fail loudly pre-generation" (**owner**), contract invariants 1/9/11 and the lifecycle's `BLOCK → named model halt` (agent/ratified) — falsifier: `project(elaborate(...))` on `tests/fixtures/elab_payload_identity`; assert it raises a named diagnostic for `blocked_guard`. Today it returns a `ComputationGraph` containing `blocked_guard`'s constraint module — disposition: **BLOCK** — *reproduced live by the audit 2026-08-09: projection emitted `payloadidentitydesign__system__blocked_guard__4ab986ad7a2a345f` as an executable constraint module.*
- audit-F8 [DO] **Item 6 stood up a second constraint extraction + profile authority and recorded no obligation to converge or delete it.** `extract_identified_constraint_facts` re-sweeps and re-sorts the model, then pairs live UUIDs to neutral facts by positional `zip` guarded only by a length check (`agentic-mbse/src/agentic_mbse/sysml/constraint_extraction.py:203-222`), and `evaluate_identified_profile` keys definitions by UUID where `_evaluate_usage` keys them by QN (`executable_profile.py:1042-1068`). The same doubling exists in codegen: `compile_calc_def` beside `compile_calc_def_exact` (`extraction/expression_compiler.py:240,399`) and paired name-keyed/ID-keyed maps on `CalculationDefinitionData` (`extraction/data_models.py:180-205`). Coexistence is authorized for Item 6, but Item 7's deletion ledger (epic §Item 7 scope 2) is a fixed inventory written before Item 6 existed and names none of these. — epic Success Criterion "Deletion ledger … New mechanisms name what they delete" and contract invariant 60 (agent/ratified); guard on the owner-verbatim Simplification constraint — falsifier: grep Item 7's ledger for these four mechanisms; none appear — disposition: DISPOSE — add the four to Item 7's deletion ledger before Item 6 closes, and replace the positional `zip` alignment with an identity-keyed join
- audit-F9 [DO] **The F30 boundary guard does not cover the boundary Success Criterion 5 claims it protects.** `SELECTION_FUNCTIONS` is a hand-maintained allowlist naming 5 of ~35 functions in `project.py` (`tests/unit/test_elaboration_import_boundaries.py:84-90`). Association-building functions are outside it — `_build_output_aliases`, `_constraint_identity`, `_build_constraint_catalog`, `_entry_source`, `_index_output_channels` — and so are the two that still do rendered-path string surgery: `_constraint_module_type` re-splits an instance path it just rendered, to mint the public module-type namespace with no collision guard (`project.py:709-720`), and `_group_identity` derives group names by filename stem/suffix matching. The companion test only asserts the declared names still exist, so a newly added helper is unguarded by default rather than guarded by default. — Item 6 Success Criterion 5 "F30 protects the whole boundary" (agent/ratified) — falsifier: add a `next(n for n in nodes if n.display_path == name)` helper to `project.py`; the guard stays green — disposition: DISPOSE — invert to deny-by-default with a named exemption list, or narrow the criterion's wording to the set actually covered

Smells (escalated into the audit's Product Judgment):
- **Smell 1 (two representations manually kept synchronized)** — fires three times, all in audit-F8/F9: the two constraint sweeps aligned by position; the paired name-keyed and ID-keyed maps written side by side in one extractor loop; the F30 guard's function-name whitelist versus the real module contents.
- **Smell 3 (special category exempts a case whose meaning is unchanged)** — `_validate_consumer`'s `if not self.diagnostics` totality relaxation and `_validate_calculation_payload`'s early return for `is_computed` survive. Judged contained, as in the prior round: `require_projectable` rejects any diagnostics-carrying graph before projection. Recorded, not escalated.
- Note, below finding grade: `test_value_site_controls_entry_point_classification` asserts a discrimination the code cannot make — all four `ValueSite` values map to `DESIGN_ATTRIBUTE` (`project.py:341-346`) — so it passes for any value site. The exhaustive dict is a good totality guard; the test's name overstates what it proves.

Resolves:
- audit-F1: FIXED — authority: agent/ratified (verified in code) — basis: `_predicate_source_key` renders `definition:{definition_qualified_name}` at projection (`project.py:140-149`); the parser UUID never appears in the public key.
- audit-F2: FIXED — authority: agent/ratified (verified in code) — basis: `_stable_declaration_id` returns `None` instead of raising on a null QN or non-v5 UUID (`extraction/extractor.py:532-540`); shared extraction no longer narrows.
- audit-F5: FIXED — authority: agent/ratified (verified in code) — basis: `_predicate_identities` is deleted; `_constraint_formal_identity` reads `input_metadata[port].formal_provenance` and fails closed when provenance is absent or disagrees with the typed port, with graph-level enforcement in `_validate_constraint_formal_provenance`. No fabricated identity path remains.
- audit-F9 supersedes the undispositioned `_constraint_module_type` smell note from the phases 3-4 block.

Gate: BLOCKED (audit-F7); DISPOSED (audit-F8, audit-F9)

## audit recheck — 2026-08-10 — rev `audit_v3 remediation uncommitted @ codegen b9c22c0`

Targeted independent re-verification of audit-F7/F8/F9 (record: `audit_v3.md` re-audit addendum).

Resolves:
- audit-F7: FIXED — authority: agent/ratified (verified live) — basis: every profile `BLOCK`
  records the named `SI_CONSTRAINT_BLOCKED` D10 diagnostic with exact consumer and profile reason
  (`elaborate.py:900-911`, `diagnostics.py:24`); strict elaboration raises
  `ElaborationDiagnosticError`, lenient graphs retain the typed node plus diagnostic, projection
  refuses live and round-tripped graphs with `ProjectionError SI_CONSTRAINT_BLOCKED`. The original
  falsifier was re-run: `project(elaborate(...))` on `tests/fixtures/elab_payload_identity` halts
  at elaboration with `block_real_equality_requires_tolerance`. Pinned at
  `test_elaboration_payload_identity.py:243,251-255,261-265`.
- audit-F8: FIXED — authority: agent/ratified (verified in code) — basis: neutral facts and their
  live elements are captured in one record inside the single sweep; UUIDs come only from
  `SysideAdapter.element_id`; duplicate usage UUIDs raise; the second sweep and positional `zip`
  are deleted. Epic Item 7 scope 2 now names all four transitional duals with convergence actions
  (`[AGENT] (audit_v3 disposition, 2026-08-10)`). Neutral schema/goldens byte-unchanged.
- audit-F9: FIXED — authority: agent/ratified (verified in code) — basis: the guard is
  deny-by-default over every function in all six boundary files; five narrow
  wire-decoding/rendering exemptions each waive one named rule and fail if no longer exercised
  (`test_guard_exemptions_are_narrow_and_exercised`); the unlisted-function falsifier is pinned
  (`test_new_boundary_function_is_guarded_by_default`). SC5 stands as written. The
  `_constraint_module_type` public-spelling collision guard remains an open rendering-policy note,
  below finding grade.

Findings: none.

Smells: none new; smell 1's three instances are resolved by the F8/F9 fixes (identity-keyed
pairing, deny-by-default guard) or ledgered for Item-7 deletion (paired extraction maps).

Gate: CLEAR
