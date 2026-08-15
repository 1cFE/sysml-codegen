# Audit v3: Exact-Identity Elaborator Breadth (ELABORATE-FIRST Item 5, post audit-v2 remediation)

**Verdict:** Certify — after the same-date targeted re-verification of the audit-v3 remediation
(see the addendum at the end of this file). The original v3 verdict below (Needs Work, BLOCKED on
audit-F28) is preserved as the round's record.
**Audited:** 2026-08-09
**Branch:** `source-identity-epic` (codegen) + `elaborate-first-salvage` @ `65a35d7` (agentic-mbse), coordinated dirty trees
**Commit:** `6bed968` (base; work uncommitted)

This is the independent re-audit the plan requested after the audit-v2 remediation. `audit.md`
(Phase-5 checkpoint) and `audit_v2.md` are the prior rounds' records; findings are referenced by
their stable IDs from `product-lens.md`.

---

## The Point

SysIDE has already resolved which declaration each semantic reference denotes. Codegen must
preserve that exact declaration identity, interpret it in one exact concrete occurrence, and store
the resulting node or output-port edge — never reduce the referent to a name and later guess which
same-named object was intended. One semantic source occurrence becomes exactly one runtime source
across calculation, constraint, FORMULA, alias, and aggregation consumers; a `:>>` override applies
at its featuring instance (innermost wins); unsupported or unstable identity produces a named
blocking outcome; strings enter only after semantic identity is settled. Item 5 builds and proves
that complete new front end while the legacy front end stays the unchanged shipped authority;
Item 6 owns the cutover. (Sources: contract invariants 54–60 + referent table + the `:>>`
definition, epic owner rulings, spec R1–R9.)

## Summary

The two audit-v2 blockers were genuinely worked: the string-matching resolver is gone and replaced
by a clean identity-only mechanism that fails closed (audit-F20 — fixed, verified by direct read
and by the lens independently), and the F21 ruling was actually obtained, recorded with honest
provenance in the contract, and implemented consistently across code, ledger, and tests. F22–F25
and F27 were executed, F26 is deferred with a durable record. Every recorded gate reproduces
exactly.

But re-inspecting the ruling's subject exposed a defect underneath it. The witness fixture
re-declares nested usages by name without `:>>`, which SysML v2 makes an **invalid model** (a
name-distinguishability violation — see the semantics note), and the toolchain admits it silently:
the occurrence tree forks into duplicates (two `array`, three `sensor`), the authored
`:>> reading = 10.0` lands on one of three same-named copies with no warning, and the damage
surfaces only as an ambiguity diagnostic on a downstream consumer that names neither the conflict
nor its site. The ratified ruling then recorded that outcome as a parser occurrence-identity
limitation on a supported form. The product-lens gate is BLOCKED (audit-F28); Certify is
forbidden.

## Product Judgment

**Is this the right piece of work? The remediation itself, yes — but the item cannot certify,
because the contract's witness fixture exposes a real identity defect that was recorded to the
owner as an external parser limitation.** The product-lens ledger gate is **BLOCKED (audit-F28)**,
with audit-F29 DISPOSE-and-surface (owner must re-rule with correct evidence), audit-F30/F31
DISPOSED, audit-F19/F26 deferred to Item 6.

- **audit-F28 (owner/[HARD], BLOCK)** — reproduced independently by this audit before accepting
  the lens verdict, then re-diagnosed against the spec. `deep_cross_scope_probe`'s design
  re-declares `array` and `sensor` by name inside the usage body (no explicit `:>>` on the parts,
  only on the leaf `reading`). Live lenient elaboration yields three `…__sensor__reading`
  AttrNodes with one identical display path — two `value=None` on the inherited declaration, one
  `10.0` on the design's redefining declaration — plus three `…__sensor__core` and two
  `…__derived_calc` CalcNodes: inherited `array` + declared `array`, the declared one holding
  inherited + declared `sensor`. Per SysML v2 this shape is not implicit redefinition — it is an
  **invalid model** (semantics note below), and the duplication is the literal parse of that
  invalid model. The defect is the toolchain's silent admission: SysIDE materializes no
  redefinition edge (faithfully), `build_feature_slot_index` (`occurrence.py:110-140`) unifies
  slots only through materialized `owned_redefinitions`, and nothing anywhere reports the
  name-distinguishability violation — so an authored `:>>` override silently applies to one of
  three same-named copies, and the only symptom is `SI_OCCURRENCE_AMBIGUOUS` on a downstream
  consumer, mis-attributing the defect. Invariant 59 requires invalid/unsupported forms to fail
  loudly at their own boundary with a diagnostic that names the condition; the `:>>` definition
  and invariant 56 are the user-visible casualties (an override the modeler believes applies
  reaches one ghost copy). DCS is the only corpus fixture authoring this shape — the working
  one-level probe (`nested_occurrence_override_probe`) uses an explicit `:>> source.reading`
  chain — which is why 37 green corpus rows never surfaced it.
- **audit-F29 (surface-to-owner)** — the contract amendment (lines 326–332) that clears the DCS
  row states the deep reference "does not identify one of its three concrete producer occurrences"
  and is unsupported "until the parser supplies exact occurrence identity." Both attributions are
  wrong: the three producer occurrences are the fork of an **invalid** witness model (audit-F28),
  not a legitimate population a parser failed to discriminate, and the single-segment evidence
  shape is built by our own extractor (`binding_evidence.py:207-215`), not imposed by the parser.
  The ruling blesses an ill-formed fixture's behavior as the expected supported-model boundary.
  It is honestly graded `[AGENT] (ratified by owner, 2026-08-09)` — correct vocabulary, properly
  not marked settled — but per capture-fidelity §4 it must be re-put to the owner with the
  corrected evidence before it can settle the C5/DCS boundary. Its dependent conclusions (the DCS
  `expected-collapse` ledger row, the "3 calculation nodes" expectation pinned in
  `test_elaboration_phase5_remediation.py:110-117`) are parked, not wrong-by-default.

Fired smells, escalated here and not resolved: Smell 3 (a "deep producer-output" category exempts
a case whose user-visible meaning is an ordinary supported qualified reference — the category
exists because the occurrence tree is wrong); Smell 6 (the remediation test pins the duplicated
tree's ambiguity as the expected outcome, so the green suite hides the defect). Both attach to
audit-F28/F29.

An unresolved owner/[HARD] BLOCK forbids Certify regardless of the green rubric below.

### Semantics note (audit-F28 branch, settled by spec consultation this session)

The design authors `part array : 'Sensor Array' { part sensor : 'Sensor' { :>> reading = 10.0; } }`
inside `part station : 'Monitoring Station'`, whose definition already owns `array`. A SysML v2
spec consultation (recorded in this session; SysML v2 Part 1 §7.6.3, KerML §7.3.2.1 +
`validateNamespaceDistinguishibility` / `Membership::isDistinguishableFrom`) settles the branch:

- There is **no name-based implicit redefinition** for nested usages. Every implicit-redefinition
  rule in the spec is positional/role-based (parameters, connector ends, results); none keys on a
  matching name.
- An owned usage sharing a name with an inherited feature of the same metaclass is a
  **name-distinguishability violation** — the model is invalid, and the spec's stated resolution
  is an explicit redefinition ("Name conflicts can be resolved by redefining one or more of the
  otherwise conflicting inherited features", Part 1 §7.6.3).
- A literal parse of the invalid model yields exactly the duplication observed (3 sensors); the
  author's evidently intended model (explicit `:>>` on `array` and `sensor`) yields 1 sensor with
  `reading = 10.0`.

So the elaborator's fork is the literal reading of an ill-formed witness fixture. The defect to
fix is fail-closed admission (detect the conflict, diagnose it loudly at the model shape), and the
fixture itself needs the `:>>` repair before it can serve as the contract's witness. A tool that
silently produces either 3 occurrences (fork) or 1 (name-based unification) without reporting the
violation is out of spec either way.

## Findings

### Plan completion

Phases 1–4: verified in the prior rounds and re-confirmed by gate reproduction; no regression. All
Phase 1–4 checkboxes stand.

Phase 5: complete except the two legs contradicted by audit-F28/F29 (reopened):

- **Reopened:** "Obtain and record the explicit F21 fixture/contract/rendering ruling before
  certification" — a ruling was obtained and recorded with correct provenance, but its premise is
  falsified by the loaded model (audit-F29), so it does not yet settle the boundary it claims to.
- **Reopened:** "Rerun the 37-fixture corpus, rewrite every classification against the ratified
  decisions" — 36 of 37 rows stand; the `deep_cross_scope_probe` row's `expected-collapse` basis
  is parked pending the corrected ruling.
- The audit-v2 remediation legs for F20/F22–F25/F27 are verified executed (below); the F20 leg's
  checkbox stands.
- Gate reproduction — all exact, zero `no live syside license` lines anywhere: contract matrix
  **31 passed**; exact-elaboration selection (`tests/unit/test_elaboration*.py
  tests/conformance/test_elaboration*.py`) **152 passed** (matches the corrected count the plan
  now records); full codegen **3307 / 47 / 18, no xfails**; agentic-mbse **1814 / 1 / 33** (rerun
  live this audit); corpus runner completes over all 37 fixtures and the live ledger-comparison
  test passes — a deliberately corrupted row fails it (verified by experiment); mypy **72 errors,
  0** in elaboration/codec/internal-route/evidence files; ruff clean on the new-route scope;
  `git diff --check` clean; legacy dirs (`generation/`, `cli/`, `resolution/`, `analysis/`,
  `orchestration/pipeline_builder.py`) **zero diff**; no baseline or `extraction_snapshot.json`
  file modified.

### Spec conformance

- **R1–R8 — met**, unchanged from audit-v2's verification; re-spot-checked at the load-bearing
  points this round (typed edges, one resolver, projection seam, dual-run isolation, matrix as
  authority).
- **R9 (exact parser identity) — the audit-F20 gap is closed.** `_resolve_leaf`
  (`elaborate.py:1255-1300`) receives only a `DeclarationId` and consumer `ScopeId`; selection in
  `_contextualize_root`/`_select_occurrences`/`_select_calc_nodes` (`elaborate.py:1118-1232`) uses
  declaration IDs and occurrence lineage only; every no-match/multi-match path raises
  `SI_OCCURRENCE_MISSING`/`SI_OCCURRENCE_AMBIGUOUS`. Qualifier text no longer reaches resolution —
  `written_qualifier` survives only as form-classification metadata (`binding_evidence.py:195-229`).
  **New R9-adjacent gap (audit-F28):** occurrence identity itself is wrong for same-named nested
  re-declarations — slot unification depends solely on parser-materialized redefinition edges, so
  one modeled feature becomes several occurrences. This is an identity-by-construction defect
  (R2/R4 territory), not a string-matching relapse.
- Non-goals respected: no snapshot format change, no legacy removal, no shipped flag; snapshot v5
  bytes untouched.

### Design conformance

- D1–D10 stand as verified in audit-v2, with the audit-v2 deviations 1–2 (the string-matching
  resolver and its guard) now genuinely closed.
- **D2 deviation (part of audit-F28):** "feature slots follow all materialized redefinition edges"
  is implemented literally — but the same-named nested re-declaration carries no materialized edge
  in SysIDE, and the elaborator has no rule for it, so the occurrence tree forks. Phase 1's kill
  probes covered authored and implied *parameter* redefinitions; this part-usage shape was never
  probed.
- **Guard scope (audit-F30):** the new AST guard
  (`test_elaboration_import_boundaries.py:38-59`) covers `_resolve_leaf` only; the sibling
  selectors and `project.py`/`graph.py`/`diff.py` are unscanned. Clean today (verified), but the
  guard does not hold the line it was added for.
- **D8 letter deviation (carried from v2):** `ValueSite` is still computed and serialized but never
  read by projection (`graph.py:106`, `instance_graph.py:266,303`; zero reads in `project.py`).
- **Order-dependent display metadata (carried from v2):** `alternatives[0]` model-order fallback
  (`elaborate.py:589`) and first-enumerated `base_by_slot` candidate remain; edges unaffected.

### Code integrity

- **Fail-closed posture:** the audit-v2 fail-open branch is gone. Two residual fail-open branches
  in plural occurrence selection (`elaborate.py:1166-1167,1191-1192` return all candidates
  model-wide when lineage anchoring misses) — reachability unproven, filed as audit-F31 with a
  fixture assignment.
- **Diagnostic vocabulary (F25 executed):** all elaboration-route failures now carry an
  `ElaborationCode` through `ElaborationInvariantError` and convert to structured diagnostics at
  the strict boundary (`elaborate.py:149-162`). Residue: `SI_ID_MISSING` is unreachable — no raise
  site passes `missing=True` (`identity.py:43-47`; verified by grep), so missing-identity cases
  report as `SI_ID_UNSTABLE`; `OVERRIDE_TARGET_MISSING`, `SI_MULTIPLICITY_UNSUPPORTED`,
  `SI_MULTIPLICITY_INVALID`, `SI_ID_UNSTABLE` are cited by no test; ordered/nonunique/range/negative
  multiplicity shapes have named outcomes but no fixtures.
- **Multiplicity (F27 executed):** `_modeled_integer_bound` evaluates finite constant expressions
  (`occurrence.py:324-333`; `[2 * 2]` expands to four occurrences,
  `test_elaboration_occurrence.py:123-134`); distinct codes for unresolved/unsupported/invalid/
  recursive shapes.
- **Evidence hygiene (F22/F23/F24 executed):** the ledger is machine-compared against a live
  37-fixture dual run (`test_elaboration_corpus_ledger.py:47-50`; corruption experiment fails as
  required); discovery executes; mutation isolation asserts complete key-set equality with a
  phantom-input negative test (`test_elaboration_contract_matrix.py:678-694`). One negative
  source-text isolation check survives (`test_elaboration_dual_run.py:34-38`) — textual, single
  file, would miss an aliased import.
- **Legacy oracle (F26):** retained by ratified decision, recorded in `plan.md` and the ledger;
  dies with the legacy route at Item 6.
- **Carried notes:** silent `except KeyError: continue` dropping slot-less features
  (`elaborate.py:308`); QN-keyed metadata lookups degrade silently (inside R9's metadata
  carve-out); one `split("__")` structure-recovery site remains in projection (`project.py:689`,
  down from three).

---

## Certification

**Not certified.** The product-lens gate is BLOCKED (audit-F28, owner/[HARD]); audit-F29 requires
an owner re-ruling before the DCS/C5 evidence boundary can be treated as settled. Under the audit
contract that forbids Certify regardless of the green rubric.

What this pass checked and marked:

- Verified and left standing: all Phase 1–4 plan checkboxes; the Phase-5 legs for F20 and
  F22–F27; every recorded gate count (reproduced exactly, listed under Plan completion); the
  corpus ledger's mechanical fidelity (live-run-checked); spec R1–R8 and the R9 string-matching
  closure; design D1–D10 load-bearing points; legacy freeze.
- Reopened: the Phase-5 F21-ruling leg and the corpus-classification leg (audit-F28/F29); the
  Phase-5 progress checkbox carries the annotation.
- Epic Item-5 success criteria: left unchecked (correct as found). Criterion 1 ("every matrix cell
  green-or-named-diagnostic") is nearly real — the matrix is genuine public evidence now — but the
  C5/DCS boundary rests on the parked ruling; criteria 2–3 are met mechanically (classified
  ledger, legacy untouched, both suites green) yet the ledger's DCS row basis is parked.
- Product-lens ledger: v3 block appended with resolutions-by-citation (F20 FIXED; F21 NOT
  RESOLVED → re-anchored F28/F29; F22–F25/F27 FIXED; F19/F26 DEFERRED) and an auditor
  verification note recording the independent reproduction.

**What Needs Work, concretely:**

1. **audit-F28:** fail closed on the invalid shape. The same-name inherited/owned conflict
   (`validateNamespaceDistinguishibility`) must produce a loud, named diagnostic at the model
   shape — in the agentic-mbse validation stack, in codegen independently (invariant 59 requires
   codegen to enforce unconditionally), or both — instead of leaking duplicate occurrences into a
   downstream consumer ambiguity. Detection is mechanical: an owned member whose name collides
   with an inherited member of a conforming metaclass and carries no redefinition of it. Then
   repair `deep_cross_scope_probe` with explicit `:>>` on `array` and `sensor` (the spec's own
   resolution and the author's evident intent) and re-elaborate: the repaired fixture should have
   one sensor with `reading = 10.0`, and the deep DCS:82 reference gets its honest test — if it
   then resolves, the "unsupported deep form" category dissolves; if it still cannot, the ruling
   can be re-made on true evidence.
2. **audit-F29:** re-put the DCS:82 ruling to the owner with the corrected evidence: the witness
   fixture is an invalid model whose fork the ruling mistook for three legitimate producer
   occurrences, and the single-segment evidence shape is built by our own extractor
   (`binding_evidence.py:207-215`), not imposed by the parser. The contract amendment, the DCS
   ledger row, and the "3 calculation nodes" test expectation follow from the answer.
3. Non-blocking, at the next natural pass: extend the AST guard across the resolution surface
   (audit-F30); author the plural fail-open fixture (audit-F31); make `SI_ID_MISSING` reachable or
   delete it; cover the untested multiplicity shapes.

**Not checked:** live behavior of individual matrix cells beyond executing the suites (assertions
were read, not mutated); the agentic-mbse side beyond its full-suite gate; generated-package
execution under a real TEAx simkit; snapshot-v5 byte identity beyond confirming no snapshot or
baseline file is modified; performance; Item-6 cutover concerns. `graph.py`, `diff.py`, and
`display.py` were not line-audited in full this round either. The SysML-semantics reading of the
same-named re-declaration shape (no implicit redefinition; distinguishability violation) rests on
a clause-cited spec consultation from the local Part 1/KerML corpus; it was not validated against
a second SysML v2 implementation, and whether SysIDE emits any diagnostic for the violation at
load/validation level was not checked.

---

## Addendum: targeted re-verification of the audit-v3 remediation — 2026-08-09

The owner requested a targeted review after the audit-v3 remediation landed. Every check was run
live against the working tree by the same auditor; nothing below is carried from the plan's record.

**audit-F28 — verified fixed.**

- The invalid inherited/owned part-namespace conflict now blocks loudly before occurrence
  expansion. `elaborate()` takes a required keyword-only `validation_diagnostics` — a caller that
  omits it fails with a TypeError, so the green suites prove call-site coverage —
  and `_blocking_model_validation_diagnostics` (`elaborate.py:174-206`) promotes SysIDE's own
  `namespace-distinguishability` diagnostics at PartUsage sites to blocking
  `SYSML_NAMESPACE_NOT_DISTINGUISHABLE`, with a `:>>` repair hint in the detail. Strict raises;
  lenient returns an empty graph carrying only those diagnostics — the duplicate tree is never
  built. Two kept licensed tests pin both paths over a preserved copy of the invalid shape
  (`tests/fixtures/elab_namespace_distinguishability_probe`,
  `tests/conformance/test_elaboration_model_validation.py`) — verified passing.
- Reusing the parser's own validation rather than reimplementing the check is the right
  authority direction for this epic; the promotion filter is a location join (PartUsage source
  sites), which is diagnostic-boundary logic, not semantic edge selection.
- The witness fixture is repaired with explicit `:>> array` / `:>> sensor` — the spec's own
  conflict resolution. The kept strict test asserts exactly one `sensor__reading` node carrying
  10.0 (this audit's recorded falsifier — the `[reading] =` destructuring fails on duplicates)
  and wires DCS:82's `ref_analysis.data_point` to the single
  `…__sensor__core__metric_value` producer channel through public projection — verified passing.
- Live corpus run reproduces the rewritten ledger row: exact `graph 5/4/0/1` vs legacy `5/7/0/0`,
  `expected-fix`; totals now 26 expected-collapse / 11 expected-fix, zero unresolved.

**audit-F29 — verified resolved.** The contract amendment was rewritten in place with the
corrected premise — DCS:82 is a supported producer-output reference on the valid witness; the
former shape was an invalid SysML namespace shape, not three legitimate producer occurrences; "No
name or authored qualifier selects the supported edge" — and re-ratified by the owner
(2026-08-09), still honestly graded `[AGENT] (ratified by owner)`. The dependent conclusions are
un-parked: the DCS ledger row is `expected-fix` and the "3 calculation nodes" expectation is
replaced by the ProducerRef assertion. The smell-3 "unsupported deep form" category is dissolved.

**audit-F30 / audit-F31 — still open, non-blocking.** The AST guard still covers `_resolve_leaf`
only, and the plural fallback branches remain (`elaborate.py:1210,1235`) with the reachability
fixture unauthored. Both keep their recorded DISPOSE dispositions.

**Gates (all live, zero `no live syside license` lines):** focused
validation/remediation/ledger 15 passed; exact-elaboration selection 154 passed (the plan's
corrected count); full codegen 3309 / 47 / 18; agentic-mbse 1814 / 1 / 33; mypy 72-error baseline
with 0 in new-route files; `git diff --check` clean; legacy dirs zero diff; no baseline or
snapshot fixture modified.

**Certification.** The product-lens ledger now has no unresolved BLOCK by citation-scan (the
targeted re-verification block resolves F28/F29; F19/F26 stay deferred to Item 6 by ratified
decision; F30/F31 stay disposed). The Phase-5 checkboxes stand as re-checked by the remediation;
epic Item-5 success criteria are marked. Item 5 is **certified**. Item 6 has not begun and must
not begin without the owner's go.

**Not checked in this addendum:** everything listed under the original "Not checked" remains
unchecked (TEAx simkit execution, performance, full line-audit of `graph.py`/`diff.py`/
`display.py`); additionally, whether the namespace-conflict promotion covers non-part member
kinds (an inherited/owned *attribute* conflict is not promoted — it would surface later as a
projection rendering collision rather than at the model boundary), and the SysIDE
`validation` diagnostics surface was exercised only through the extractor, not probed directly.
