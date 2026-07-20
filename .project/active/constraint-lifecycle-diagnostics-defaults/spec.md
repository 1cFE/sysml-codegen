# Spec: Lifecycle Remediation Item 4 — Diagnostic Severity and Modeled-Default Fidelity

**Status:** Implemented — candidate `16dbaa7` (codegen) / `4c18d61` (agentic-mbse), awaiting `/_my_audit`
**Owner:** Reid W
**Created:** 2026-07-19
**Complexity:** HIGH
**Branch:** `constraint-exec-epic`
**Epic:** CONSTRAINT-LIFECYCLE-REMEDIATION — Item 4, register row 4
**RED predecessor (codegen):** `3fbec63a9fc5f81e74b9794885b05219d5812e58`
**RED predecessor (agentic-mbse):** `515e08bbcd70aa9d23212765161bd02b3e3d8f23` (Item 0 pin — **this item moves it**)
**Open predecessor rows:** none. Rows 0–3 are closed (Item 3 audit Pass with notes, `008b5be`).

---

## Problem

Three things the lifecycle contract treats as load-bearing are not, and one referred gap from
Item 2 blocks convergence on real data.

**Extraction diagnostics do not reach anyone.** `ExtractionDiagnosticFact`
(`agentic-mbse/src/agentic_mbse/sysml/constraint_facts.py:170-178`) is the only diagnostic that
crosses the wire. It carries `kind: str` and `message: str` — no severity, and `kind` is a bare
string with no closed vocabulary. It has exactly one producer (`constraint_extraction.py:365-372`,
`kind="non_finite_literal"`) and **zero consumers**: nothing in agentic-mbse validation and nothing
in sysml-codegen reads `facts.diagnostics`. The codegen snapshot loader validates the section's
shape (`snapshot/loader.py:637`) and then the content is dropped. A diagnostic that no code reads
cannot block anything, so today there is no difference between "trust-affecting" and "advisory" —
both are silence.

The profile's own diagnostic is closer but still not classified. `EligibilityDiagnostic`
(`executable_profile.py:109-118`) has `reason: str` plus `force: Literal["error",
"non_numerical"]`. `REASON_CODES` (`:62-96`) lists 27 codes but is **never enforced in
production** — it is a frozenset asserted only by tests, and `reason` is typed `str`. A typo or a
newly added unclassified reason flows through and lands in the L6 message text. `force` defaults to
`"error"`, which is a fail-closed default, but it is a *decision* input to eligibility, not a
transport severity, and it never crosses a codec.

**Warning rendering can replace the halt it is supposed to precede.** Codegen emits every
NON_NUMERICAL warning before the BLOCK halt (`analysis/constraint_lowering.py:692-693`), which is
the right order. But `_report_non_numerical_warnings` resolves each warning's location eagerly
through `projected_location` → `_project_excluded_location` → `map_live_source_referent`
(`:519-525`), and that path raises `"raw source ... does not match any supplied model root"`
(`analysis/source_referent.py:52`). A referent-mapping failure on the *first* warned usage aborts
the whole pre-pass: no warnings are emitted, and the actionable BLOCK diagnostic — constraint name,
reason, repair text — never runs. The failure is unpinned; no test drives the referent failure
through the pre-pass. Item 1 deliberately preserved these bytes for this item.

**Modeled defaults that the model explicitly carries are silently dropped.** `_literal_float`
(`constraint_lowering.py:1300-1310`) returns a value only for a bare `LiteralNode`. `:= -0.1`
parses as an `OperatorNode` over a literal — the exact shape the profile's unary-sign support
exists for — and `= 40.0 [MW]` parses as a `UnitAnnotationNode`. Both return `None`. The
MODELED_DEFAULT formal then mints a LIBRARY_DEFAULT entry point with `default_value=None`
(`:1420-1425`), and the generated JSON simply omits the key (`generation/entry_point.py:270-273`).
A value the model states becomes a value the user must re-supply, with no diagnostic anywhere. The
capability exists elsewhere in the same repo — `generation/predicate_compiler.py:191-197` and
`extraction/calc_compat_renderer.py:71-72` both unwrap unit annotations structurally — so this is
drift, not a missing feature. The behavior is essentially unpinned: no test calls `_literal_float`,
`tests/conformance/test_entry_point_classifier.py:274-288` passes vacuously when the value is
`None`, and `-0.1` appears nowhere in `tests/`.

**Default parsing is duplicated six ways.** One IR-typed lane (`_literal_float`) and five
string-typed lanes: `analysis/parameter_groups.py:820-829`, `:504-522`, `:207-235`,
`resolution/producer_resolution.py:521-527`, and `extraction/extractor.py:504-529`. Only the IR
lane is reached for constraint MODELED_DEFAULT inputs, and it is the one that loses signed and
unit-annotated values.

**Item 2's referred convergence.** `SharedProducer::the_rig::gain` is read by both a calc input and
a constraint actual and yields two entry points, not one
(`tests/fixtures/shared_producer/PROVENANCE.md`). Item 2 could not close it because the
calculation consumer was believed unable to supply the reference as written. **That premise is
false — see the surfaced conflict below.**

## Surfaced premise conflict — the written reference is already on disk

**Trigger:** genuine surprise producing evidence against a premise this item's scope rests on
(capture-fidelity rule 4). Recorded rather than resolved silently, in either direction.

`tests/fixtures/shared_producer/PROVENANCE.md` states that the occurrence-materialized key form is
"structurally unreachable from the calculation consumer" because extraction discards the written
name. Item 2's evidence PC-4, the epic's Item 2 out-of-scope note, this item's stage brief
("the written-reference carry likely needs a snapshot format bump"), and the docstring at
`resolution/producer_resolution.py:101-104` all rest on that premise.

Measured at HEAD, across all 34 committed fixture snapshots:

```
34 snapshots, 292 bindings, 168 reference bindings, 168 with source_attribute_name populated
fixtures with unnamed reference bindings: []
```

`snapshot/serializer.py:250-251` already writes `source_attribute_name` — the referent's simple
name — into every serialized `BindingInfo`, and `shared_producer`'s committed v3 snapshot contains
`"source_attribute_name": "gain"`. The **loader** discards it:
`snapshot/loader.py:1022-1035` reconstructs `BindingInfo` field by field and never reads that key.
Live, the same value is available as the AST-backed property `BindingInfo.source_attribute_name`
(`extraction/usage_extractor.py:96-100`).

Two consequences, both narrowing:

1. **The carry needs no snapshot format bump of its own and no agentic-mbse change.** It is loader
   plumbing plus one call-site change. The brief's stated reason for a bump does not hold.
2. **The two sides already agree on what "the written reference" means.** The constraint side's
   `FeatureReferenceFact.source_name` is populated by `reconstruct_expression`
   (`constraint_extraction.py:353`), which for a `FeatureReferenceExpression` returns
   `referent.name` (`expression.py:551-554`) — the referent's simple name, not raw source text.
   `source_attribute_name` is the same notion from the same kind of node. Parity is exact, and no
   name is inferred from a formal.

**Dependent conclusion parked, not resolved:** whether a format bump happens at all is decided by
the *severity* work (DD-R06), not by the carry. If design finds the severity field can land
without a fact-schema bump, then no re-capture occurs and the carry must still work on unmodified
v3 snapshots.

A second, smaller conflict: PROVENANCE.md's "Do not" section asserts "a test asserts it" of the
two-entry-point state. **No such test exists at HEAD.** `shared_producer` appears only in
`tests/conformance/conftest.py:62` as a registered session snapshot; nothing asserts either entry
point QN. Item 4 must build the acceptance surface rather than flip an existing one, and must
correct that claim.

## Success Criteria

These four outcomes are the epic's row-4 criteria, absorbed unchanged. They are `[INHERITED]` —
their authority is the epic register and the ratified contract, not an owner statement about this
item.

- [x] **[INHERITED: epic Item 4]** Severity/code round-trip and both consumer sinks pass with
      fail-closed skew.
- [x] **[INHERITED: epic Item 4]** Warning preparation cannot replace the actionable `BLOCK`
      diagnostic.
- [x] **[INHERITED: epic Item 4]** Signed/unit defaults survive; unsupported default IR fails or
      remains explicitly unresolved.
- [x] **[INHERITED: epic Item 4]** Diagnostic/default parsing is consolidated without a second
      representation or compatibility shim.

Two more, from sources outside the epic row:

- [x] **[INHERITED: referral decision 2026-07-20, recorded in epic Item 2 out-of-scope]** SR-A02
      convergence completes on real data with no name inference: the shared attribute yields one
      QN-keyed typed entry point, one modeled default, one group assignment.
- [x] **[OWNER]** Simplicity is judged qualitatively — duplicated diagnostic/default parsing is
      consolidated and what the typed path obsoletes is deleted, not shimmed. No LOC gate, baseline,
      cap, or counting obligation exists for this item. Source: owner amendment 2026-07-19,
      epic "Simplification and Deletion Mandate".

## Known Requirements

### A. Scope, authority, and the coordinated pair

- **DD-R01 [INHERITED: contract invariant 15 / LC-B08]** Every extraction diagnostic that can affect
  trust carries a stable code and a severity. A blocking diagnostic halts before lowering; an
  advisory diagnostic stays visible through authoring and codegen output; a diagnostic whose code
  or severity is unrecognized **fails closed** rather than defaulting to advisory.
- **DD-R02 [INHERITED: epic Item 4, coordinated-pair constraint]** This item changes both
  repositories and **moves the Item 0 agentic-mbse pin** from `515e08bb`. The evidence record names
  the exact new agentic-mbse commit, the codegen commit, and the resolved lock, and states that the
  candidate chain since `515e08bb` (Items 1–3) is additive-certified.
- **DD-R03 [INHERITED: epic delivery order]** Delivery stays in the existing PR wave: agentic-mbse
  PR #11 first, sysml-codegen PR #9 second. No replacement upstream PR is opened.
- **DD-R04 [INFERRED]** Item 4 does not reopen the certified seams of Items 1–3. It extends them:
  the Item 1 warning/BLOCK ordering bytes, the Item 2 shared resolver and its key-form table, and
  the Item 3 generation-gate V11 caller are extension points, not rework targets.

### B. Diagnostic severity and stable codes (agentic-mbse first)

- **DD-R05 [INFERRED]** `EligibilityDiagnostic.reason` is constrained to a closed vocabulary in
  production, not by test convention. Constructing a diagnostic with a reason outside that
  vocabulary is an error at construction, not a string that survives into a user-facing message.
  Today `REASON_CODES` (`executable_profile.py:62-96`) is enforced only by
  `tests/test_sysml/test_executable_profile_matrix.py:72-74`.
- **DD-R06 [INHERITED: LC-B08]** `ExtractionDiagnosticFact` gains a severity classification and a
  closed `kind` vocabulary, which is a fact-schema change: `CONSTRAINT_FACTS_SCHEMA_VERSION`
  advances from `"constraint-facts/v1"`. A sink alone is insufficient — the contract states this
  explicitly and this spec does not challenge it. See DD-B1 for the alternative that was considered
  and why it loses.
- **DD-R07 [INFERRED]** Severity travels **with the data**, not in a reader-side lookup table, so
  two readers at different versions cannot disagree about whether a diagnostic blocks. This is the
  reason DD-R06 is a schema change rather than a classification map.
- **DD-R08 [INHERITED: contract invariant 15]** At least one production consumer reads the
  serialized diagnostics on each side: agentic-mbse authoring validation and sysml-codegen
  lowering/preflight. A field with no code consumer does not satisfy DD-R01 (contract invariant 13).
- **DD-R09 [INFERRED]** The codegen sink is load-bearing: a blocking extraction diagnostic stops
  generation before lowering, with the diagnostic's code, severity, message, and location in the
  failure text. An advisory diagnostic is rendered at a level a build log shows and does not stop
  generation.
- **DD-R10 [INFERRED]** The L6 authoring sink stops collapsing the profile's 27 reason codes into
  two `ValidationCode` members with the real discriminator surviving only as interpolated message
  text (`validation/level6_architecture.py:618-650`). The code survives as a field a consumer can
  branch on. L4's count-only rendering (`level4_constraints.py:42-76`, `success=True` hardcoded at
  `:135`) is informational and stays that way.

### C. Version skew, both directions, fail closed

- **DD-R11 [INHERITED: contract invariant 14 / epic row 4]** Both schema-skew directions fail
  closed: a reader older than the writer and a reader newer than the writer both refuse before any
  semantic use. The current codecs already do this by exact string equality
  (`constraint_facts.py:324-334`, `expression_ir.py:235-245`, `snapshot/loader.py:719-730`); the
  requirement is that the version advance **preserves** that property and proves it with tests in
  both directions, not that a new mechanism is built.
- **DD-R12 [INFERRED]** If the fact-schema version advances, the codegen snapshot envelope advances
  with it (`SNAPSHOT_FORMAT_VERSION` 3 → 4). Leaving the envelope at 3 while its embedded facts
  change meaning would let a v3 snapshot describe two different payloads. The envelope guard is
  already exact-equality (`loader.py:727`), so v3 snapshots are rejected with the existing
  recapture message; no migration or grandfathering path is added.
- **DD-R13 [INFERRED]** All 34 committed fixture snapshots are re-captured at the new version in the
  same change, matching the v2→v3 precedent recorded at `snapshot/__init__.py:11-18`. Re-capture
  requires the SysIDE license and rewrites every `captured_at` timestamp, so the byte-identity gate
  is run as a timestamp-only diff check with the timestamp churn reverted, and only genuine payload
  movement is reviewed.
- **DD-R14 [INFERRED]** The duplicated compatibility literals are made to fail loudly rather than
  drift: `constraint_lowering.py:476-480` pins `"executable-profile/v4"` and `loader.py:777, :782`
  pin the two schema strings, each a hand-copied string in the downstream repo. The package floor
  `agentic-mbse>=0.1.2` (`pyproject.toml:24`) does no work, because the editable path override at
  `:65` always takes the working tree. Design chooses between single-sourcing these and making the
  floor real; the requirement is that a schema or profile bump cannot land without the downstream
  guard noticing.
- **DD-R15 [INFERRED]** Interaction with Item 12 is stated, not implemented here. Item 12 owns
  closing the `grandfathered_off` fail-open path. Item 4 must not introduce a second grandfathering
  route, and must not silently pre-empt Item 12's decision by making legacy snapshots loadable.

### D. Warning totality and BLOCK preservation

- **DD-R16 [INHERITED: epic row 4, R-8 family]** Out-of-root warning rendering is **total**. A
  NON_NUMERICAL usage whose file maps to no supplied model root still produces its warning; the
  location degrades to an explicitly rendered fallback rather than raising.
- **DD-R17 [INHERITED: epic row 4]** Warning preparation can never replace the actionable BLOCK
  diagnostic. Every warning is emitted, in source/profile order, and then the BLOCK halt runs with
  its constraint name, reason, and repair text. No failure inside warning preparation may
  substitute itself for that halt.
- **DD-R18 [INFERRED]** DD-R16 does not weaken the strict source-referent contract elsewhere.
  `map_live_source_referent` and `validate_snapshot_source_referent` keep raising for every other
  caller — an excluded-record location, a catalog entry, or a generated byte still fails on an
  unmappable root. The degradation is local to warning text.
- **DD-R19 [INFERRED]** The exact warning bytes Item 1 pinned
  (`tests/conformance/test_constraint_non_numerical.py:16-27`,
  `tests/unit/test_constraint_usage_preparation.py:409-443`,
  `tests/conformance/test_constraint_lowering.py:893-916`) move only where DD-R16/DD-R17 require it.
  Each moved byte sequence is named in evidence with the reason.

### E. Modeled-default fidelity

- **DD-R20 [INHERITED: contract acceptance row "Signed/unit default + unsupported wrapper"]** An
  explicit `-0.1` modeled default and an explicit `40.0 [MW]` modeled default survive extraction,
  lowering, the typed entry point, and the generated JSON input file with their values intact.
- **DD-R21 [INHERITED: same row / LC-B06]** An unsupported default IR never yields an invented
  value. It either fails generation with the node kind and owner named, or remains **explicitly
  unresolved** — an entry point the user can see is unfilled. Silently omitting the key from the
  generated JSON (`generation/entry_point.py:272-273`) is neither, and is the behavior being
  retired.
- **DD-R22 [INFERRED]** "Explicitly unresolved" is observable: an entry point with no resolvable
  modeled default emits a diagnostic at a level a build log shows, naming the entry point QN and
  the default IR's node kind. The existing `_warn_nonfloat_entry_points`
  (`analysis/parameter_groups.py:551+`) does not cover this — it fires only for a non-numeric-typed
  entry point, so a numeric attribute with a `None` default is invisible today.
- **DD-R23 [INFERRED]** Default resolution is one typed representation. The IR lane
  (`_literal_float`) and the five string lanes (`parameter_groups.py:820-829`, `:504-522`,
  `:207-235`; `producer_resolution.py:521-527`; `extractor.py:504-529`) collapse to the smallest set
  that the pipeline's real inputs justify. Where two lanes read the same input for the same purpose,
  one is deleted; where a lane serves a genuinely different input (AST vs IR vs captured string),
  that is stated as a kept boundary with its reason. No compatibility wrapper preserves a deleted
  lane.
- **DD-R24 [INHERITED: LC-D09]** A modeled default stays an overridable typed contract parameter. It
  is not baked into predicate code and does not become an automatic study variable.
- **DD-R25 [INFERRED]** Scope 4 is unwrapping and sign folding over an explicitly modeled default,
  nothing more. General constant folding and unit conversion stay out (see Non-Goals). A
  `UnitAnnotationNode` contributes its numeric value; its unit is carried or refused, never
  converted.

### F. Written-reference carry (absorbed from Item 2, PC-4)

- **DD-R26 [INHERITED: referral decision 2026-07-20]** The calculation consumer supplies the
  reference as written to the shared resolution request, so it reaches the same key form the
  constraint consumer reaches. No name is inferred from a formal, and no structural-equality
  recovery (`referent_qn == {usage_qn}::{param_name}`) is used — that alternative was measured and
  rejected in Item 2 and stays rejected.
- **DD-R27 [INFERRED]** The carry is loader plumbing plus call-site plumbing, not a new extraction
  field, because the value is already serialized in every committed snapshot (see the surfaced
  conflict). Concretely: `snapshot/loader.py:1022-1035` stops discarding `source_attribute_name`,
  and `analysis/dependency_backtracker.py:574-588` passes the written reference as `reference`,
  the resolved QN as `target_qn`, and the `instance_path` that
  `_occurrence_materialized_qn` (`producer_resolution.py:363-367`) short-circuits without today.
- **DD-R28 [INHERITED: contract invariant 21 / Item 2 SR-A02, SR-R23]** The shared usage-owned
  attribute yields **one** QN-keyed typed entry point across both consumers, with one modeled
  default and one group assignment.
- **DD-R29 [INFERRED]** The measured blast radius is accepted deliberately and named. The same
  resolution newly resolves 22 self-named bindings across six fixtures — `fusion_tea`,
  `solar_battery_model`, `catf_mfe_model`, `chain_spike_model`, `return_styles`,
  `expression_binding_probe` (Item 2 `design.md:141-149`). All 22 are single-consumer, so no wrong
  value is being fixed; the movement is entry-point identity across those six generated surfaces.
  Evidence records, per fixture, that every moved entry point kept its correct modeled default and
  that no numeric result changed.

  > **SUPERSEDED BY MEASUREMENT (implement, ratified 2026-07-19).** The "22 across six fixtures"
  > above was Item 2's *estimate*, carried forward. Gate 3's probe over all 34 fixtures and all five
  > `ProducerRequest` builders measured **24 entry-point movements across seven fixtures** (the six
  > named plus `shared_producer`), from **89** moved resolutions. The accepted table is in
  > `design.md` under "The gates → Gate 1". This is estimate → probe truth, **not a scope change**:
  > the requirement's substance is unchanged and it was met — every moved entry point kept its
  > correct modeled default and no numeric result changed, verified by whole-corpus before/after
  > diff of every fixture's entry points (0 same-key value changes).
  >
  > One clause did not survive contact: *"no wrong value is being fixed."* Two movements are
  > convergences onto a **correctly scoped** attribute carrying the identical value, and the
  > chain-aware carry (see DD-R26 and design B2) exists because the leaf-only form would have
  > selected a **wrong** same-named attribute. The premise held for values, not for anchors.
- **DD-R30 [INFERRED]** Item 2's objection that this "shrinks `fallback_entry_points` membership
  ahead of Item 3's vacuity proof" is **retired**: Item 3 completed, proved vacuity by closed
  enumeration, and deleted extension-time V11 coverage validation (`c5cc1b4`, epic Item 3). V11
  membership movement is no longer load-bearing for a pending proof. Final-generation V11 stays
  strict and unchanged.
- **DD-R31 [INFERRED]** The artifacts asserting the falsified premise are corrected in the same
  change, not left to contradict the code: `tests/fixtures/shared_producer/PROVENANCE.md` (including
  its false "a test asserts it" claim), the in-model header comment at
  `tests/fixtures/shared_producer/model.sysml:11-16`, the docstring at
  `resolution/producer_resolution.py:101-104`, `dependency_backtracker.py:566-571`, and Item 2's
  evidence PC-4 and design I9.

### G. Inherited residuals this item owns

Each was verified at HEAD before being specified.

- **DD-R32 [INHERITED: Item 1 audit residual]** The tier-2 malformed-literal disposition asymmetry
  is closed. **Reproduces at HEAD:** tier 1 sets `saw_non_literal = True` on an unparseable literal
  (`resolution/supplied_values.py:226-232`) and the caller reports it as a loud deferred skip
  (`:582-590`); tier 2 `continue`s past the same input (`:278-285`) and returns
  `saw_non_literal=False` (`:287`), so the caller's `resolved.value is None` branch (`:540-543`)
  drops the target with **no diagnostic at all**. A wholly-malformed tier-2 target must be as
  visible as the tier-1 case. Item 1's `continue` — which correctly stopped a bad literal from
  suppressing a good one below it — stays; only the silence is fixed.
- **DD-R33 [INHERITED: Item 2 PC-2]** SR-R16's stated basis is amended. **Reproduces at HEAD:**
  `.project/active/constraint-lifecycle-shared-resolution/spec.md:158-162` still reads "Basis: owner
  D-1 (no post-build graph/default mutation)". Item 2's design proved the backfill runs strictly
  before the graph exists, so D-1 is not implicated (`design.md:96-101`); the requirement survives on
  cross-source order-dependence (invariant I5). This is a one-line correction to Item 2's spec text,
  with the bet table row at `spec.md:295` corrected to match.
- **DD-R34 [INFERRED — scope call, recorded]** `param_group=None` on LocalTerm mints is **closed as
  non-reproducing**, not deferred to Item 10. Verified at HEAD: `build_computation_graph` takes a
  non-optional `ParameterGroupDeriver` (`resolution/graph_builder.py:168`) and
  `_mint_entry_point_once` classifies through it (`:1299`), and the aggregation LocalTerm mint
  passes `param_group=ep.param_group` (`:1662-1666`). The `| None` annotations at `:1278, :1342,
  :1448` are a test affordance, documented as such at `:1465` ("None in tests"). There is no
  production path that mints a LocalTerm entry point without a group. Nothing is carried forward.

### H. Simplification and deletion

- **DD-R35 [OWNER]** No LOC gate, baseline, per-file cap, counting obligation, or growth-deviation
  review applies. Simplicity is judged qualitatively at review. Source: owner amendment 2026-07-19.
- **DD-R36 [OWNER, applied]** Named deletion targets are stated before design and verified absent
  after: superseded default-parsing lanes retired under DD-R23; the discarded-then-recomputed
  written-name path under DD-R27; any raising branch in warning-location preparation superseded by
  DD-R16. Deletion is proved by absence (`rg` returns no match), not by a wrapper that preserves the
  old call shape.
- **DD-R37 [INFERRED]** The two independent profile consumers stay independent (contract LC-C04, and
  the epic's explicit "do not collapse intentional boundaries"). Codegen re-evaluates facts;
  authoring decisions are not passed to codegen as mutable state. Consolidating the *sinks* does not
  mean merging the consumers.

---

## Mandatory Acceptance Cases

Requirements above are the single normative decision home. Each row is an `[INFERRED]` proof
instrument citing the requirements it tests. Every row inherits LC-I09: exact revision/lock set,
fixture ID, both public routes, and open predecessor rows (none). RED-first: each row's public
surface fails at the stated predecessor for its named defect and passes at candidate GREEN with
identical test bytes.

| ID | Governing requirements | Case and required observation |
|---|---|---|
| DD-A01 | DD-R05, DD-R08 | A diagnostic constructed with a reason outside the closed vocabulary is refused at construction. Every one of the 27 existing reasons is accepted unchanged. No reason string reaches a user-facing message as the whole of its own explanation. |
| DD-A02 | DD-R01, DD-R06, DD-R07 | An `ExtractionDiagnosticFact` round-trips code and severity through serialize → parse → serialize byte-identically at one pinned schema pair. A fact whose severity or kind is unrecognized fails closed at parse, before any semantic use. |
| DD-A03 | DD-R08, DD-R09 | Both sinks are load-bearing on one fixture carrying a blocking diagnostic: codegen halts before lowering with code/severity/message/location in the failure text, and agentic-mbse validation reports it as an error. The same fixture with the diagnostic downgraded to advisory generates successfully and the advisory is visible in the build log. |
| DD-A04 | DD-R10 | A blocking and a non-numerical profile outcome each surface their specific reason code as a field a consumer branches on, not only inside interpolated message text. The L6 truncation at five issues does not drop the code from the structured result. |
| DD-A05 | DD-R11, DD-R12 | Reader-older-than-writer and reader-newer-than-writer both fail closed, for the fact schema and for the snapshot envelope, before any field deserialization. Four cells, no shared setup. |
| DD-A06 | DD-R13 | All 34 fixture snapshots load at the new version. A retained v3 snapshot fails with the existing recapture message and produces no partial context. The re-capture diff, with `captured_at` churn reverted, shows only the payload movement DD-R06/DD-R27 predict, each entry named. |
| DD-A07 | DD-R14 | A profile or schema version bumped in agentic-mbse without the corresponding codegen update fails loudly at the downstream guard, in a test that does not depend on a human remembering to edit a string literal. |
| DD-A08 | DD-R16, DD-R17 | Public source with one NON_NUMERICAL usage whose file maps to no supplied model root **and** one BLOCK usage. Every warning is emitted with a rendered fallback location, in order, and the BLOCK halt then runs with its constraint name, reason, and repair text. This is the R-8 cell; it fails at the predecessor with zero warnings and the referent error in place of the halt. |
| DD-A09 | DD-R18 | The same unmappable root, reached through an excluded-record location and through a generated byte, still fails loudly. The DD-R16 degradation does not leak to any other caller. |
| DD-A10 | DD-R19 | Every Item-1-pinned warning byte sequence is either unchanged or changed with its reason named in evidence. No pinned sequence changes silently. |
| DD-A11 | DD-R20, DD-R24 | A fixture with `:= -0.1` and a fixture with `= 40.0 [MW]` as explicit modeled defaults. Both values reach the typed entry point and the generated JSON input file intact. Overriding each in the input file changes the generated execution's verdict; neither is baked into predicate code. Both public routes. |
| DD-A12 | DD-R21, DD-R22 | An unsupported default IR either fails generation naming the node kind and owner, or produces an entry point that is explicitly unresolved and diagnosed by QN and node kind. The generated JSON never silently omits the key, and no value is invented. |
| DD-A13 | DD-R23, DD-R36 | Each retired default-parsing lane is absent from the tree, with no wrapper, alias, flag, or dead fallback preserving its call shape. Each kept lane has a stated distinct input and a test that exercises it. |
| DD-A14 | DD-R26, DD-R27, DD-R28 | `shared_producer` yields **one** entry point, `SharedProducer__the_rig__gain`, for both the calc input and the constraint actual, with one modeled default (40.0) and one group assignment. Both public routes. The RED surface is newly authored — no test pins the current two-entry-point state at HEAD. |
| DD-A15 | DD-R29 | Each of the six named fixtures records its moved entry-point identities, that every moved entry point kept its correct modeled default, and that no numeric result changed. A fixture whose numerics move fails the cell. |
| DD-A16 | DD-R30 | Final-generation V11 remains whole-graph strict and unchanged. The Item 3 generation-gate caller of `collect_uncovered_params` behaves identically before and after the entry-point identity movement. |
| DD-A17 | DD-R32 | A wholly-malformed tier-2 supplied-value target is as visible as the tier-1 case: the value is not applied, and a diagnostic names the target. Item 1's tier fall-through is preserved — a malformed literal on the type def still does not suppress a valid literal on the consuming part def (`test_malformed_type_def_literal_does_not_suppress_part_def_literal` stays green). |
| DD-A18 | DD-R31, DD-R33 | The corrected artifacts contain no surviving assertion of the falsified premise, and no artifact claims a test that does not exist. Verified by grep against the named files. |
| DD-A19 | DD-R02, DD-R03 | Evidence records the exact new agentic-mbse commit, the codegen commit, the resolved lock, and the additive-certified status of the Items 1–3 chain since `515e08bb`. PR #11 precedes PR #9 in the stated merge order. |
| DD-A20 | DD-R15, DD-R37 | Item 4 introduces no second grandfathering route and does not make a `grandfathered_off` snapshot loadable. The two profile consumers remain independent: codegen re-evaluates facts and consumes no authoring decision as state. |

---

## Explicit Agent Bets

Non-normative reviewer index. The requirement IDs above are the single decision home. These remain
challengeable even if design proceeds with them.

| Bet | Requirement | Default and rationale |
|---|---|---|
| **DD-B1** — severity is a fact field, not a reader-side table | DD-R06, DD-R07 | A classification map from `kind` to severity would need no schema bump and no re-capture — materially cheaper. It loses because severity would then be a property of the reader's version, so two readers could disagree about whether the same diagnostic blocks, which is the skew the contract closes. LC-B08 says the same thing and is `[INFERRED]`, so it is challengeable: if design shows the map can be single-sourced and version-gated as strictly as the codec, this bet loses and DD-R12/DD-R13 fall away with it. |
| **DD-B2** — the envelope bumps with the facts | DD-R12 | Bumping `SNAPSHOT_FORMAT_VERSION` 3 → 4 alongside `constraint-facts/v2` follows the v2→v3 precedent and keeps one gate answer per snapshot. The alternative — leaving the envelope at 3 and letting the embedded facts gate do the work — means a v3 snapshot can describe two payloads, which is exactly what the version is for. |
| **DD-B3** — re-capture rather than migrate | DD-R13 | No migration or grandfathering code is written; old snapshots fail with the existing recapture message. This matches Item 12's fail-closed direction and avoids writing a compatibility path Item 12 would then have to delete. Cost: a licensed re-capture and `captured_at` churn across 34 files. |
| **DD-B4** — the carry rides the loader, not a new field | DD-R27 | `source_attribute_name` is already in all 168 reference bindings across all 34 snapshots. Reading the existing key is smaller than adding a field, and it means the carry works on unmodified v3 data if DD-B1 loses and no bump happens. If the two values ever diverge — the property is AST-backed live, the key is captured at serialization — this bet loses and an explicit extraction field is required. |
| **DD-B5** — the six-fixture rename is accepted | DD-R29 | Item 2 deferred it partly to protect Item 3's pending proof; Item 3 is closed, so that reason is gone. The remaining cost is identity movement across six generated surfaces with no value change. If review finds a moved identity that a consumer depends on by name, this bet loses and the carry needs a narrower gate. |
| **DD-B6** — advisory diagnostics are visible, not silent | DD-R09 | An advisory diagnostic logs at a level the build shows. If design finds a diagnostic family so noisy that visibility degrades the log, the answer is to reclassify that family, not to lower the rendering level. |

---

## Non-Goals

- **[INHERITED: epic Item 4 out-of-scope]** General constant folding and unit conversion. DD-R25
  bounds default handling to unwrapping and sign folding over an explicitly modeled default.
- **[INHERITED: epic Item 4 out-of-scope]** A diagnostics framework beyond the versioned contract.
  No new severity taxonomy, routing layer, or diagnostic registry beyond what DD-R01 requires.
- **[INHERITED: stage brief firewall]** Item 5's whole-tree portability, Item 12's grandfathered-
  snapshot closure (DD-R15 states the interaction only), and reworking the certified seams of
  Items 1–3.
- **[INFERRED]** `AggregationDiagnostic` (`agentic-mbse/.../aggregation.py:68-75`) is out of scope.
  Its `diagnostic_id` is positional (`f"AGG-{n:03d}"`) and therefore not a stable code, but it is a
  separate lineage with no consumer in either repository, so it is not trust-affecting today. It
  must not be described anywhere as carrying a stable code.
- **[INFERRED]** Making `agentic-mbse validate`'s L4 rendering load-bearing. It is informational by
  construction (`level4_constraints.py:135`) and DD-R10 leaves it that way.
- **[INFERRED]** Fixing the L6 five-issue / three-warning print truncation
  (`validation/common.py:123-149`). DD-A04 requires the code to survive in the structured result;
  terminal presentation is not this item's.

## Open Questions / Deferred to design

- Where the consolidated default representation lives, and which of the six current lanes survive.
  DD-R23 states the outcome; the boundary between the AST lane, the IR lane, and the captured-string
  lane is a design call with a stated reason per kept lane.
- Whether severity is a new field on `ExtractionDiagnosticFact` or a promotion of the existing
  `EligibilityDiagnostic.force` vocabulary to a shared type. Both satisfy DD-R01/DD-R07; the
  simplification mandate favors one typed representation over two.
- The exact fallback rendering for an unmappable warning location under DD-R16 — a sentinel, the raw
  path, or the referent with a marker. The requirement is that it renders and does not raise.
- Whether DD-R14 is satisfied by single-sourcing the version literals or by making the package floor
  real. Both close the gap; they have different blast radii.
- Whether the unsupported-default disposition under DD-R21 is fail-generation or
  explicitly-unresolved, per node kind. The requirement forbids only the invented value and the
  silent omission.
- Ordering within the change set: DD-R27's carry is independent of DD-R06's schema work and could
  land first, which would isolate the six-fixture identity movement from the re-capture diff and
  make DD-A06's review tractable.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` — Item 4, register row 4
- **Stage brief:** `.project/active/constraint-lifecycle-diagnostics-defaults/briefs/spec.md`
- **Ratified authority:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — invariants 14, 15, 26; proof-matrix row "Signed/unit default + unsupported wrapper"; register row 4
- **Requirements authority:** `.project/active/constraint-execution-lifecycle-contract/spec.md` — LC-B06, LC-B07, LC-B08, LC-C04, LC-D09, LC-I09
- **Referral source:** `.project/active/constraint-lifecycle-shared-resolution/{spec,design,evidence}.md` — SR-A02, SR-R23, design I9, evidence PC-2 and PC-4
- **Fixture provenance:** `tests/fixtures/shared_producer/PROVENANCE.md` — **contains two claims this spec falsifies; corrected under DD-R31**
- **Predecessor residuals:** `.project/active/constraint-lifecycle-occurrence-demand/audit.md:346, :433-440`; `.project/active/constraint-lifecycle-gate-b/decision.md`
- **Defect reproductions:** `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md` — R-8 (`:130-138`), R-9 (`:140-147`)
- **Rigor template:** `.project/active/constraint-lifecycle-occurrence-demand/spec.md`
- **Design:** `.project/active/constraint-lifecycle-diagnostics-defaults/design.md` (to be created)

---

**Next Steps:** independent `/_my_audit` against the candidate. Evidence at
`.project/active/constraint-lifecycle-diagnostics-defaults/evidence.md`.

**Scope note on the SR-A02 criterion:** convergence closes for the unbracketed (`PartUsage`-owned)
shape, which is the shape SR-A02 names and `shared_producer` carries. It is **explicitly not
claimed** for an occurrence-indexed `part_def` owner, where row 16 deliberately misses (evidence
PC-6).
