# Audit: Lifecycle Item 4 — Diagnostic Severity and Modeled-Default Fidelity

**Verdict:** Pass with notes (round 3, `caa149c`) — supersedes round 1 "Needs Work" (`16dbaa7`)
and round 2 (`765e8b8`). All four findings F1–F4 closed; two non-blocking notes (N1 schema
amend-in-place hole, N2 error-path degradation) recorded in the round-3 section below.
**Audited:** 2026-07-20
**Branch:** `constraint-exec-epic` (both repos)
**Latest commit:** sysml-codegen `caa149c`, agentic-mbse `4c18d61`. Round-1 header below records the
original `16dbaa7` pass; read the "Round 2" and "Round 3" sections for current state.

Independent audit; no artifact from the implementing session was taken on trust. Every headline
number was re-measured. `git diff 16dbaa7 b104659 -- src/ tests/` is empty, so the code candidate
is intact under the two documentation commits.

---

## Summary

The engineering is strong and the gates are real. Every measurable claim in evidence.md that I
could re-run matched exactly: 3040 passed with zero license skips, 72 mypy errors, 184 entry
points across 9 graphs, 34+1 snapshots, the pinned FD-1 regeneration set with no extras, and the
two pre-existing `-O` failures. The three exclusions all reproduce at the parent commit. PC-3, the
change the brief flagged as highest-risk, is sound in all three respects.

The problem is not the code — it is three places where a claim outruns its evidence, each of which
would let a real defect ship unnoticed:

1. On the snapshot route the blocking-diagnostic sink runs **after** lowering, not before. PC-4,
   DD-R09, design D2, and the module's own docstring all state otherwise.
2. The written-reference carry **silently re-anchored a `::`-qualified reference onto an
   owner-local shadow**, and FD-1 records that movement as a fix ("convergence onto correct
   scope"). It is a live instance of the exact bug family PC-1 exists to close, masked because
   both attributes hold 3.0.
3. DD-A03 is labelled Partial on the strength of a "unit surface" that does not exist. The sink has
   **zero** test coverage on either route, and the advisory branch is unreachable as shipped.

Findings 1 and 3 share one root cause: nothing tests the sink, so the ordering defect had nothing
to catch it. Finding 2 is independent and is the more serious of the three.

---

## Findings

### Plan completion

No `plan.md` by design — the epic records the phased plan as living in `design.md`
(`epic_constraint_execution_lifecycle_remediation.md:463-464`). Phases 0–6 are all marked complete
in `design.md:812-1040` with implementation notes. Spot-checked Phase 1 (carry + regeneration),
Phase 3 (default fidelity), and Phase 5 (re-capture); each has the artifacts its note claims. No
placeholder code or TODOs found in the diff.

### Spec conformance

**Verified met.** DD-R01, R02, R03, R05, R06, R07, R11, R12, R13, R14, R16, R17, R18, R19, R20,
R21, R22, R24, R25, R26 (as amended), R27, R28, R30, R31, R32, R33, R34.

Highlights re-derived rather than accepted:

- **DD-R07 / I1 — severity never recomputed.** Reproduced the `rg` independently in both repos.
  The codegen grep for the severity table returns exit 1, zero hits; the only codegen consumer
  reads the stored field (`analysis/diagnostic_screen.py:45,57,62`). Confirmed.
- **DD-R11 / I2 — skew fails closed both directions.** Exact equality, not `>=`, at
  `constraint_facts.py:404` and `snapshot/loader.py:731`. Both directions parametrized for the
  fact schema (`v1`/`v3`) and the envelope (`3`/`5`). The fact-schema test also corrupts a field to
  prove the gate precedes field deserialization.
- **DD-R15 / DD-A20 — gate before lowering-mode read.** Verified in the production function, not
  from the test name: envelope gate at `loader.py:723-736`, mode first read at `:743`. Ordering
  genuinely holds.
- **DD-R16 / I3 — warning totality.** The catch is narrow (`except CodeGenerationError`), not a
  swallow. `_degraded_location` (`constraint_lowering.py:540-550`) cannot raise. The memo argument
  is structural: `location_cache[index] = projected` at `:715` runs only after a successful
  projection, so the degraded string never enters the cache and the exclusion path at `:749`
  re-attempts and still raises. This is the cleanest piece of design in the item.
- **DD-R31 — falsified-artifact corrections.** Verified the sharper of the two claims: at the
  predecessor, `shared_producer` appeared in `tests/` only as a registered session snapshot in
  `conftest.py:59-62`. No test asserted the two-entry-point state. The correction is honest and is
  written as a decision record rather than as an instruction to future agents.
- **DD-R32 / DD-A17 — tier-2 visibility.** `test_supplied_values.py:343` diagnoses the wholly
  malformed tier-2 target, and `:381` byte-freezes the tier-1 aggregate so the new diagnostic
  lands as a separate record. Item 1's fall-through test is named and stays green.
- **I9 / I10 — row 16 containment.** `written_reference` is consumed at exactly one site
  (`producer_resolution.py:381`). All three `graph_builder` consumers (`:1369`, `:1606`, `:1629`)
  pass only `instance_path` and neither dedicated field, so C3's `or` expressions preserve their
  prior behaviour. Confirmed by reading all four sites.

**Gaps.**

**F1 — DD-R09 / PC-4: the snapshot-route sink runs after lowering.**
`orchestration/snapshot_context.py:34` calls `build_full_graph_from_snapshot`, which lowers at
`snapshot/graph_rebuild.py:213`. The sink is at `snapshot_context.py:42`, eight lines later.
Proven dynamically, not inferred:

```
SNAPSHOT ROUTE CALL ORDER: ['lower_constraints', 'screen_extraction_diagnostics']
```

The live route is correct (extract `:765` → screen `:767` → prepare `:838` → lower `:885`). So the
two routes are **not** symmetric, contrary to PC-4's explicit rationale, and D2's requirement
("one function, two call sites, both before lowering") is not met on the offline route — the
license-free production path. `diagnostic_screen.py:3` compounds it by still naming
`snapshot/loader` as the second site, which PC-4 moved away from.

Blast radius is bounded and I want to be exact about it: the sink still raises before
`build_pipeline_context_from_snapshot` returns, so no bad package escapes, and a non-finite
operand degrades to `unknown` at `predicate_compiler.py:86-93` rather than crashing. The harm is
that lowering consumes the bad literal first, so a user can get an obscure lowering failure
instead of the actionable diagnostic — which is the failure mode DD-R09 exists to prevent.
*Should change:* move the sink above `build_full_graph_from_snapshot`, and add an ordering test.

**F2 — the carry re-anchored a `::`-qualified reference onto an owner-local shadow, recorded as a
fix.** FD-1's third row credits "convergence onto correct scope: catf_mfe 1 (elongation, 3.0)".
That movement is the opposite of a fix.

- The model writes `in kappa = catf_radial_build::elongation`
  (`tests/fixtures/catf_mfe_model/designs/catf_mfe/radial_build.sysml:105`) — an explicit reference
  to the **outer** scope.
- `plasma_region` declares a local shadow, `attribute elongation : Real = 3.0; // Inherited from
  parent` (`radial_build.sysml:93`).
- Fourteen `volume_calc` modules carry that identical binding text. Thirteen resolve to
  `CATFMFERadialBuild__catf_radial_build__elongation`. After the carry, exactly one —
  `plasma_region` — resolves to `CATFMFERadialBuild__catf_radial_build__plasma_region__elongation`.
- At the parent `3fbec63` it resolved to the outer key like its thirteen siblings, and the key
  `plasma_region__elongation` **did not exist in the baseline at all**. Item 4 created it.

Mechanically this is PC-1's own counterexample in a different clothing. The snapshot records
`binding_type: "reference"`, `source_instance_name: null`, `source_attribute_name: "elongation"`,
so `written_reference` is the bare leaf and row 16 keys it under the occurrence owner — the local
shadow. The chain-aware fix covers `.` chains; `::` qualifiers lose their qualifier exactly as `.`
chains did before PC-1.

Every gate passed because both attributes are 3.0, so Gate 2's "0 same-key value changes" and
FD-1's "numeric result unchanged" are both literally true. That is what makes it serious rather
than cosmetic: a value coincidence is the only thing standing between this and a wrong number, and
the evidence files it as a success. *Should change:* reclassify the FD-1 row as a re-anchor,
record the `::`-qualified gap alongside PC-6's bracketed-owner gap as known partial coverage, and
decide whether the plasma_region binding is now wrong.

Scope: 84 `::`-qualified bindings across two fixtures; one moved, because only `plasma_region`
declares a shadow. Narrow today, but not self-limiting.

The `fusion_tea` half of that same FD-1 row (`in eta = driver.efficiency`, `ife_plant.sysml:145`)
is a genuine `.` chain and **is** correctly labelled. Only the catf_mfe entry is inverted.

**F3 — DD-A03 is Fail, not Partial.** The "Partial" label rests on the codegen halt and advisory
logging being "proven by unit surface". There is no such surface. Zero occurrences of
`diagnostic_screen`, `screen_extraction_diagnostics`, `DiagnosticSeverity`, or the halt string
anywhere under `tests/`, confirmed by grep and by coverage over the full 3040-test run:

```
src/sysml_codegen/analysis/diagnostic_screen.py  19  7  63%  Missing: 38-44, 66, 71-74
```

`71-74` is the `CodeGenerationError` raise, `66` is the advisory `logger.warning`, `38-44` is the
entire `_render` formatter. None executes under any test. The behaviour is correct — both sinks
were verified by direct execution, producing code, severity, message, and location — but it is
entirely unpinned and would regress silently. DD-R08 and DD-R09 are marked Met on unexercised code.

Two aggravating facts:

- **The advisory leg is unreachable, not merely untested.** `EXTRACTION_DIAGNOSTIC_SEVERITY`
  (`agentic-mbse .../constraint_facts.py:80-82`) has one entry, `non_finite_literal: BLOCKING`,
  and parse refuses any document whose stored severity disagrees with the table. No `ConstraintFacts`
  can carry an ADVISORY diagnostic today, so `diagnostic_screen.py:65-66` has no possible input.
  DD-R09's "ADVISORY logs at WARNING" is unfalsifiable as shipped.
- **The end-to-end fixture is cheap, contrary to the Open-items framing.** A ~20-line model with a
  literal that overflows to `inf` (e.g. `1.0e400`) triggers `non_finite_literal` at
  `constraint_extraction.py:363-372` on the first attempt, with a real location and no license
  obstacle. "Requires a non-finite literal in a model" is true but materially overstates the cost.
  Recording this as a finding, per the brief — the fixture belongs to the implementer.

**F4 — DD-R23's retention justification is falsified by this item's own fixture.** The 531/0/0
measurement reproduces exactly (669 present, 531 float-parsing, 138 non-parsing, 0 signed, 0
unit-bracketed across the 34). But `parameter_groups.py:216-222` justifies keeping
`_parse_default_value` because it reads "a captured string for which no expression IR exists", and
the new fixture breaks that: `ModeledDefaultFidelity__Derived_Bound__limit` captures `'5.0'`
because the AST lane folded `2.0 + 3.0`, while an IR **does** exist for it — the operator node the
IR lane deliberately refuses under DD-R25. The two lanes hold contradictory answers for the same
modeled default: `5.0` versus explicitly unresolved. Not observable today (the design-attribute
route does not mint that entry point), but the kept-lane boundary is not "different input" — it is
the same input under two disagreeing policies, which is what success criterion 4 forbids. The
docstring's "zero carry a sign" also went stale in the same commit that measured it: the 35-snapshot
corpus now has one (`drift`, `-0.1`).

**Non-goals respected.** No routing layer or diagnostic registry was built —
`diagnostic_screen.py:14-19` explicitly refuses to become one and states why. No constant folding
in the IR lane (`2.0 + 3.0` stays unresolved, verified). Items 1–3 seams untouched: all six primary
acceptance files are byte-identical across `3fbec63..16dbaa7`, the two Item-1 support files are
purely additive (zero deletions), and the Item 1–3 set passes 76/76 at the candidate.

### Design conformance

**PC-3 (the brief's priority 1) is sound in all three respects.** This was the highest-risk change
and it holds up:

- *Property genuinely unchanged.* Diffed the old and new test bodies: from `reviewed_seal = _seal(...)`
  through the final `!=` on executable fingerprints, the assertion block is byte-identical. Only
  the setup changed (whole-revision `git archive` → working tree with one file overwritten), plus
  the added guard.
- *Impossibility argument holds.* `verify.py` has exactly two commits in the window: `512786c`
  (18 Jul, the pinned old policy) and `e217119` (19 Jul 14:27). `e217119` is an ancestor of the
  carry `7430aba` (19 Jul 23:38), confirmed by `git merge-base --is-ancestor`. So every revision
  with the old policy also predates the carry and therefore has the old entry-point keys, and no
  third revision exists. `REVIEWED_VERIFY_SHA256` matches `512786c`'s bytes exactly.
- *The loud guard fires.* Reproduced by repointing `REVIEWED_REVISION` at a post-`e217119`
  revision in a throwaway copy. It failed at `:129`, before generating anything, with the intended
  message. The probe file was removed; the tree is clean.

One observation, not a finding: the old form was structurally self-guarding (a no-op was
impossible), the new form depends on an explicit assertion. That assertion is present and fires,
and `assert reviewed_verifier_hash == REVIEWED_VERIFY_SHA256` independently proves the source
override took effect, so the rewrite is a stricter test of the same claim, as argued.

**PC-1** is correctly implemented as designed — `written_reference` composes
`{source_instance_name}.{source_attribute_name}` for chains (`usage_extractor.py:102-116`), and
the cryo_pumps counterexample is real: the competing key
`CATFMFEVacuum__catf_vacuum_pumping__n_pumps` = 48.0 genuinely exists in the same baseline and is
legitimately consumed elsewhere, so the leaf-only carry really would have served 48.0 where the
model means 32.0. The design bet is right. F2 is a gap in its reach, not a defect in its logic.

**PC-6** verified by direct probe: row 16 misses (`_MISS`) for the bracketed owner rather than
hitting a wrong key. The evidence's self-correction — that the miss comes from def-scoping rather
than bracket mismatch alone — is accurate.

**PC-4 is the one deviation that does not hold.** See F1. The rationale for moving the sink off
`snapshot/loader` is sound; the placement it moved to is past lowering, which the rationale claims
it is not.

### Code integrity

No god functions, no back-compat shims without callers, no broad `except Exception`, `ruff check
src/` clean. `diagnostic_screen.py` is a good small module: one job, no fallbacks, no table lookup,
advisory logged before blocking raises so both surface. Findings beyond F1–F4:

- **`analysis/parameter_groups.py:230-233`** — `design_attribute_float_default` returns `None` on
  `TypeError`/`ValueError` with no logging at all. The predecessor `_parse_default_value` logged at
  DEBUG. This is now the resolver's default lane, and DD-R22 requires unresolved defaults to be
  observable, which the IR lane does and this one no longer does. *Should change:* restore a DEBUG
  record, or state why the string lane is exempt.
- **`resolution/producer_resolution.py:379-381`** — the two `or` fallbacks let one row serve two
  consumers with disjoint field sets, so the row's contract is implicit in which fields each caller
  leaves `None`. Compounded by `constraint_lowering.py:188` passing `written_reference=dotted or ""`,
  whose empty string falls straight back to `req.reference`. This is deliberate (C3, and I10 depends
  on it) and I am not asking for it to be undone — but the precondition should be asserted per
  consumer rather than left to field-absence.
- **`resolution/producer_resolution.py:538`** — function-local import of `analysis.parameter_groups`
  from the resolution layer, reading as cycle avoidance. *Should change:* move the shared parser to
  a neutral module, or record the layering exception.
- **`agentic-mbse .../constraint_facts.py:380-385`** — the stored-vs-table severity disagreement
  branch is live (verified by executing it) but has no test. Cheapest gap in the item to close.
- **`generation/predicate_compiler.py:150,201`** — two user-visible error messages say
  `executable-profile/v3` while the pin is `v4`, with the stale string pinned by
  `test_predicate_compiler.py:384`. **Pre-existing at `3fbec63`**, so not an Item 4 regression and
  outside the "three hand-copied literals" the item did replace — but it is an unowned residual.
- **`analysis/diagnostic_screen.py:3`** — docstring names `snapshot/loader` as the second sink;
  PC-4 moved it to `snapshot_context`. The module contradicts its own call site.

### Evidence honesty

Good overall — the PC ledger is candid, the exclusions are each reproduced at the parent, and PC-5
records a guard catching the implementer's own mistake. Four places the record is looser than it
reads:

- **FD-4 has an unnamed seventh delta class.** Classifying all 842 changed lines: five classes
  match exactly, but `dropped_constraints` measures **582**, not 594. The missing 12 are
  `source_line`/`line` shifts of exactly +2 in `shared_producer`, caused by the Phase-1 header
  correction being net +2 lines. Benign, but folded into another row, so the 594 figure is not
  reproducible as written and "comment-only, no semantic change" understates an edit that moved
  location metadata.
- **DD-A06's "retained v3 snapshot" does not exist as an artifact.** No committed fixture carries
  `"snapshot_format_version": 3`; the test synthesizes v3 in `tmp_path` from the v4 payload
  (`test_snapshot_v4_gate.py:49-52`). The rejection is genuinely proven, by a different mechanism
  than the wording implies.
- **The merge-order failure mode is harsher than described.** With agentic-mbse at the old pin, the
  guard test never runs — collection dies at `analysis/diagnostic_screen.py:26` with `ImportError:
  cannot import name 'DiagnosticSeverity'`. Fails closed, loudly, so DD-R03's conclusion stands and
  PR #11 must land before PR #9. But the operator sees an ImportError, not the guard's message.
- **SR-A02's bracket limitation is in the right file, in the wrong place.** The scope note is at
  `spec.md:466-469` — after the closing "Next Steps" block, as the last four lines of the file —
  while the criterion it qualifies is at `:137-139`, checked with no caveat and no back-reference.
  The epic version (`epic_...remediation.md:457-459`) does state it inline and is the model to
  follow.

Minor, recorded for completeness: `plant_values` also drifts `registry_init.py`, not only
`computation_graph.json`; the single agentic-mbse skip is a missing-CATF-models skip, not the
`slow` marker (which accounts for the 33 deselected); DD-R20 names `40.0 [MW]` where the fixture
uses `[W]`. The `dropped_constraints` exclusion is actually better-supported than argued — zero
producers exist in `src/` or `scripts/` at any of the three revisions, so no re-capture could emit
it.

### Gates

All reproduced at the candidate, all matching evidence:

| gate | evidence | measured |
|---|---|---|
| codegen suite | 3040 passed | **3040 passed, 41 skipped, 17 deselected** |
| license skips | 0 | **0** — verified in `-rs` output, not by count |
| codegen `PYTHONOPTIMIZE=1` | 2 pre-existing failures | **2 failed, 3038 passed**, exactly the two named |
| agentic-mbse suite | 1811 passed | **1811 passed, 1 skipped, 33 deselected** |
| mypy (codegen) | 72, zero added | **72 in 17 files** |
| ruff `src/` (both) | clean | **clean** |
| byte-identity / FD-2 | 9 graphs, 184 EPs, two null keys only | **184 EPs, 0 field changes**; 6 of 9 graphs byte-identical once the two new fields are stripped, the other 3 exactly the FD-1 set |

The `-O` failures are provably pre-existing without running the parent: neither test file appears
in `git diff --stat 3fbec63 16dbaa7 -- 'tests/**/*.py'`, so both are byte-identical at the
predecessor and the failure is purely `assert`-stripping.

Scope note on lint: `ruff check src/ tests/` reports 363 errors, all under `tests/`. `tests/` has
never been in the project's documented lint scope (`CLAUDE.md`), so the evidence's "ruff (both)
clean" — meaning both repos — is not wrong. Flagging it only so a reader does not read it as full
coverage.

**Execution lane not re-run** is a defensible scope call, and I verified its premise: no generated
`.py` module body changed anywhere in the diff. Only the 9 computation graphs and 2 pipeline YAMLs
moved.

---

## Certification

**Verified and marked:**
- Spec success criteria 2, 3, 5, 6 — left checked, each verified above.
- Epic Item 4 success criteria 2, 3, 5 — left checked.

**Unmarked (were checked by the implementing session, not verified here):**
- Spec criterion 1 and epic criterion 1, "Severity/code round-trip and both consumer sinks pass
  with fail-closed skew." Round-trip and fail-closed skew are verified. **Both consumer sinks** are
  not: one has no test at all (F3) and one runs at the wrong point in the pipeline (F1).
- Spec criterion 4 and epic criterion 4, "Diagnostic/default parsing is consolidated without a
  second representation." F4 shows two lanes holding disagreeing answers for the same modeled
  default.

No ✅ appended to the epic item heading. `CURRENT_WORK.md` updated to "needs work".

**To clear this audit** (all three are the implementer's, not fixes I drafted): move the snapshot
sink above `build_full_graph_from_snapshot` and pin the ordering with a test; reclassify FD-1's
catf_mfe elongation row and rule on the `::`-qualified gap; give
`screen_extraction_diagnostics` a test covering the raise, and either add the cheap end-to-end
fixture or restate DD-A03 as Fail. F4 needs a re-stated boundary; the remaining items are notes.

**Not checked:**
- The whole-corpus resolution-level probe behind FD-1 (89 of 303 calls across 34 fixtures, five
  request builders) was not re-run. Corroborated only where committed baselines exist — 12 of 34
  fixtures, and 4 of the 7 moving fixtures have no committed graph. That claim still rests on the
  implementing session's probe.
- No live-extraction re-capture of the 35 snapshots was performed; FD-4 was audited as a diff, not
  by regenerating.
- The execution lane was not run, in either repo — I verified only that no generated module body
  changed, which is the premise of the scope call, not a substitute for the lane.
- TEAx (`d545701f`) was not exercised at all.
- agentic-mbse code integrity was reviewed only where it touches the severity contract; the rest of
  `4c18d61` was not read line by line.
- Whether the `plasma_region` kappa binding is now *wrong* in the modeller's intent (F2) is a
  modelling question I did not resolve — I established only that it diverged from thirteen
  identical siblings and from its own parent-commit resolution.
- The 363 `tests/` ruff findings were not triaged.
- Performance, security, and the generated packages' runtime behaviour were out of scope.

---

# Round 2 — remediation re-verification

**Verdict:** Needs Work (narrowly — one finding)
**Audited:** 2026-07-20
**Commit:** sysml-codegen `765e8b8`; agentic-mbse `4c18d61` unchanged

Scope: my four round-1 findings only, plus the gates and evidence corrections. Nothing else
re-audited.

## Summary

Three of four findings are closed, and the remediation's evidence discipline is notably good — it
discloses a discarded first fix and a second cut that broke a certified seam before it was scoped,
rather than presenting only the final answer.

**F2 is not closed.** The catf_mfe symptom is fixed, but the guard is scoped by *"does the resolved
QN happen to be indexed"* rather than *"was the reference scope-qualified as written"*, and that
mis-scoping silently reverted a second, unrelated binding. It reproduces the exact pattern F2 was
raised about: a real regression, masked by a value coincidence, in a fixture with no committed
baseline.

## F1 — sink ordering: **CLOSED**

Re-ran my own call-order probe at `765e8b8`:

```
SNAPSHOT ROUTE CALL ORDER: ['screen_extraction_diagnostics', 'lower_constraints']
```

The sink moved above `build_full_graph_from_snapshot` (`snapshot_context.py:35-49`). The pinning
test `test_snapshot_route_screens_before_lowering` (`test_diagnostic_screen.py:158`) records actual
call order with monkeypatched spies — the same technique I used — rather than inferring it from
source position, and its second assertion (`"lower_constraints" in order`) stops it passing
vacuously on a snapshot that never lowers. `diagnostic_screen.py:3` now names `snapshot_context`.

*Note, not a finding:* the fix costs a second `load_extraction_snapshot` of the same file, which
reverses PC-4's original "there is no second load". The code comment discloses this and argues the
graph build dominates it. Honest and proportionate.

## F3 — sink coverage: **CLOSED**

Coverage over the full suite moved from `19 7 63% Missing: 38-44, 66, 71-74` to **`19 0 100%`**.
The raise, the advisory branch, and the whole `_render` formatter now execute. 8 tests in
`test_diagnostic_screen.py`, both routes, plus the end-to-end `non_finite_literal` fixture I said
was cheap — it is, and it exists.

Both stated structural limits are accurate, and both were verified as facts rather than accepted as
excuses:

- **The serializer genuinely refuses non-finite floats.** Reproduced by attempting a real capture:
  `ValueError: Out of range float values are not JSON compliant: inf` at `expression_ir.py:180`
  (`allow_nan=False`). A blocking `non_finite_literal` cannot reach a snapshot by construction, so
  the snapshot leg's synthesized payload is a necessity, not a shortcut.
- **The advisory branch is unreachable** — `EXTRACTION_DIAGNOSTIC_SEVERITY` still has one entry.

The synthesized-snapshot injection is honest: it splices a well-formed diagnostic into a real v4
payload and passes through the production parse, where `_diagnostic_from_dict` re-derives severity
and would raise on disagreement. It bypasses no guard. The advisory test's `object.__setattr__` is a
genuine bypass, confined to the one branch with provably no reachable input and labelled as such.

## F4 — lane disagreement: **CLOSED as Met-with-exception**

The false "no expression IR exists" claim is deleted, not softened; the docstring now leads with
"**the kept-lane boundary is NOT 'different input', and saying so was wrong**" and states the honest
boundary (same input, two policies, one unconsumed). The disagreement is pinned by
`test_default_lane_disagreement.py` — both the contradiction (`"5.0"` vs `unresolved_node_kind ==
"operator"`) and *why* it is unobservable. The root cause is named with its blast radius
(constraint-definition formals captured as design attributes, four-fixture reach) and recorded as an
unowned open item rather than smuggled into a remediation commit; the diff confirms nothing extra
landed. The stale "zero carry a sign" measurement is corrected.

Criterion 4 correctly stays unchecked — the disagreement persists by design until the
double-ownership item lands.

*Minor, same class as the defect being corrected:* the docstring and evidence say "the 35-snapshot
corpus"; `shadowed_reference` made it 36, and the figures moved 669/531 → 677/539.

## F2 — the `::` re-anchor: **NOT CLOSED**

What did land, verified:

- **plasma_region is fixed.** All fourteen `volume_calc` kappa bindings now share one key,
  `CATFMFERadialBuild__catf_radial_build__elongation`; `plasma_region__elongation` occurs zero times
  in the baseline, matching the parent.
- **The certified Item-2 seam is intact.** `test_precedence_occurrence_qn_beats_target_qn_design_attribute`
  is byte-unchanged since `3fbec63` and passes, and its scenario is still discriminating: it sets
  `target_qn`, so the guard is inert, and both candidate keys are indexed.
- **The 7.0 → 2.0 flip is real.** Independently reproduced by deleting the guard in a `/tmp` copy
  and generating: `..._inner__scale` (7.0) without it, `..._the_outer__scale` (2.0) with it.
- **SR-A02 convergence survives** — `test_shared_producer_convergence` passes, so the fix did not
  repeat the discarded first attempt's failure.

**F2b — the guard silently reverted fusion_tea to a definition-scoped key.** The guard fires on
`sanitize_qualified_name(req.reference) in ctx.design_attr_by_qn` — resolution, not written form. It
therefore also captures the bare-leaf shape row 16 exists to serve. Reproduced directly at all three
revisions:

| revision | `hif_plant_pkg__hif_plant__driver__meier_cost.driver_efficiency` |
|---|---|
| `16dbaa7` | `hif_plant_pkg__hif_plant__driver__efficiency` (instance-scoped) |
| `765e8b8` | `hif_driver__HIF_Driver__efficiency` (**definition-scoped**) |

That binding is a bare leaf (`source_attribute_name: "efficiency"`, `source_instance_name: null`) —
neither `::`-qualified nor a `.` chain. The `::` in its `source_path` is only the resolved QN, which
is precisely the ambiguity the *discarded* first fix was rejected for; it re-enters through the
guard's index test. The consequence is the SR-A02 defect Item 4 exists to close: this consumer now
collapses onto the same definition-scoped key as `hif_driver__hif_driver_instance__meier_cost`, so
two instances share one parameter.

Both keys hold 0.35 and fusion_tea has no committed baseline, so no gate sees it. This is the same
masking that hid the original F2 for a full audit cycle.

*Should change:* scope the guard by the written form rather than by whether the resolved QN happens
to be indexed, and re-check the whole corpus for guard-induced movement rather than only the fixture
that motivated it.

**F2c — the discriminating fixture asserts nothing.** `tests/fixtures/shadowed_reference/` was
authored so a re-anchor moves a value visibly (2.0 / 7.0), answering my round-1 point that the
3.0/3.0 coincidence was the only thing hiding the bug. No test references it. The three parametrized
conformance tests that glob it all SKIP; there is no `baseline_outputs/shadowed_reference/`. The
behaviour is correct — I probed it — but unpinned. This is structurally the same criticism round 1
made of `shared_producer` under DD-R31, reproduced in the fixture written to close it. Evidence
calls it a "Discriminating regression test, as required"; it is a fixture, not a test.

**F2d — FD-1's corrected table is still wrong.** Its rows sum to 24 (18 + 5 + 1), not the stated 23;
the fixture set is seven, not six (removing the catf_mfe *elongation* entry does not remove catf_mfe
from the pure-rename row); and the surviving "convergence onto correct scope: 1 — `fusion_tea` only"
is false at `765e8b8`, because F2b reverted it. It is also mislabelled "a genuine `.` chain" — the
moved binding is a bare leaf; the `.` chain in that fixture is a different, unaffected consumer.

## Gates at `765e8b8`

| gate | claimed | measured |
|---|---|---|
| codegen suite | 3050 passed, 0 failed | **3050 passed, 44 skipped, 17 deselected** |
| license skips | 0 | **0** — verified in `-rs` output |
| mypy `src/` | 72, zero added | **72 in 17 files** |
| ruff `src/` | clean | **All checks passed!** |
| agentic-mbse | 1811 passed | **1811 passed, 1 skipped, 33 deselected** |
| Items 1–3 acceptance | untouched | **confirmed** — the test diff touches three files, all Item-4's |

## Evidence corrections

All five I raised are made, and stated accurately rather than gestured at — including the two I only
mentioned in passing (`plant_values` also drifting `registry_init.py`, and the SR-A02 scope note
moving inline). Two residuals:

- **DD-A06's correction is by appendix, not amendment.** `evidence.md:175` still reads "retained v3
  fails with the existing recapture message"; the correction sits 390 lines later. A reader hitting
  the ledger row first still gets the false impression. Amend in place.
- **The commit table (`evidence.md:38-44`) and the "Final gate results" block still end at
  `16dbaa7`/3040.** A separate remediated-gates table carries 3050, so this reads as before/after
  rather than a false claim, but `765e8b8` is not identified as the candidate anywhere in the table.

## Certification

**Marked this round:**
- Spec criterion 1 and epic criterion 1 → **checked**. F1 and F3 are both closed and independently
  verified. My round-1 annotation on that criterion had gone false at `765e8b8` and is replaced.

**Left unchecked:**
- Spec criterion 4 and epic criterion 4 — correct as they stand. DD-R23 is Met-with-exception and
  the box should stay open until the double-ownership item lands.

**Left checked, with a pointer added:**
- Criterion 5 (SR-A02). The criterion names `shared_producer`, which still converges. F2b regresses
  instance-scoping for a different binding in a different fixture, so it is noted at the criterion
  rather than treated as falsifying it.

No ✅ on the epic item heading.

**To clear:** F2b (re-scope the guard by written form, re-check the corpus for guard-induced
movement), F2c (attach a test to `shadowed_reference`), F2d (correct FD-1's arithmetic, fixture
count, and the now-false fusion_tea row), and amend DD-A06 in place.

**Not checked this round:**
- Anything outside my four findings and the gates — no re-audit of PC-1, PC-3, PC-6, the skew
  machinery, or the re-capture, all of which round 1 covered at `16dbaa7` and which the diff does
  not touch.
- The whole-corpus resolution probe behind FD-1, still not re-run at either candidate.
- The `-O` gate was not re-run at `765e8b8`.
- FD-4's line classification was not re-derived by the implementer's own method.
- The "8 constraint-def formals across 4 fixtures" figure could not be reproduced exactly; a looser
  probe suggests it may understate, which is the safe direction for an open item.
- Execution lane, TEAx, and the 363 `tests/` ruff findings — untouched, as in round 1.
- Round-1's `design_attribute_float_default` silent-`None` note (DD-R22 observability) was out of
  this round's scope and remains open at `parameter_groups.py:248`.

---

# Round 3 — F2 remediation re-verification

**Verdict:** Pass with notes
**Audited:** 2026-07-20
**Commit:** sysml-codegen `caa149c`; agentic-mbse `4c18d61` unchanged

Scope: F2 closure only, plus the schema-amend argument and the gates. F1/F3/F4 were closed at
round 2 (`765e8b8`) and their code is untouched in this window.

## Summary

**F2 is closed.** The fix moved the discrimination to where the information actually lives: a new
`BindingInfo.stored_source_written_qualifier` captures the scope qualifier from the FeatureReference
CST byte span at extraction (`usage_extractor.py:913-970`), `written_reference` returns `None` when
a qualifier is present, and row 16's two earlier resolution-based guards are both deleted
(`producer_resolution.py`). This is the correct source of truth — resolution destroys the written
form, and reading it from the CST is the one place it survives.

All three sentinel shapes resolve correctly, verified by my own probes and pinned by a new test:

| shape | resolves to | correct? |
|---|---|---|
| `fusion_tea` `meier_cost.driver_efficiency` (bare leaf) | `hif_plant_pkg__hif_plant__driver__efficiency` (instance-scoped) | ✓ — F2b closed |
| `catf_mfe` `kappa = catf_radial_build::elongation` (qualified) | `..._catf_radial_build__elongation` (outer key) | ✓ |
| `shadowed_reference` `factor = the_outer::scale` (qualified, 2.0 vs shadow 7.0) | `..._the_outer__scale` (2.0) | ✓ |

**F2c closed.** `test_written_qualifier_anchoring.py` (6 tests, none skipped) pins all three on both
routes, asserts the 7.0 shadow is absent, asserts the qualifier survives the snapshot, and
`test_three_sentinel_bindings` pins the three shapes together with the note that they are
byte-identical except the written qualifier. Independently confirmed discriminating: nulling the
stored qualifier flips `factor` from 2.0 to the 7.0 shadow. A committed
`baseline_outputs/shadowed_reference/` now exists.

**F2d closed in substance, stale in place.** The authoritative table (`evidence.md:659-672`) sums
correctly (18 + 5 = 23 across seven fixtures), removes the false fusion_tea "convergence onto
correct scope" row, and retracts the `.`-chain mislabel. Note: the earlier round-1-remediation table
at `evidence.md:504-513` still literally carries `convergence onto correct scope | 1 | fusion_tea
only — a genuine .` chain` and "23 across six fixtures," cured only by the later supersede note — the
same correction-by-appendix pattern round 2 flagged for DD-A06.

Gates all reproduce: **3056 passed / 0 license skips**, mypy 72 (zero added), ruff clean, `-O`
identical except the two pre-existing assert-stripped tests. Scope is disciplined — the five source
changes all trace to F2, the Item-2 precedence seam test is byte-unchanged, no Items-1-3 acceptance
file moved. The `test_snapshot_v3_gate.py` the brief asked about is a stale docstring comment in
`test_grandfather_carveout.py:13` naming a file that was renamed to `test_snapshot_envelope_gate.py`
— one occurrence, harmless, no live resurrection.

## Notes (not blocking; the owner should weigh the first)

**N1 — amending v4 in place has a reproduced silent-degradation hole.** The fix added
`source_written_qualifier` to the snapshot payload without bumping `SNAPSHOT_FORMAT_VERSION` (still
4). The ratified argument — v4 is on no remote, every committed snapshot was re-captured, so no
field-less v4 exists anywhere a gate must catch — has verified premises: v3 rejection and both skew
directions are RED-tested, and my staleness scan found every committed v4 snapshot with reference
bindings carries the field. **But the failure is real and I reproduced it:** strip the field from a
committed v4 snapshot, leave the version at 4, and it loads with no error and resolves
`shadowed_reference.factor` to the 7.0 shadow — F2 silently back. This is exactly the "one version,
two payloads" case DD-R12 bumped 3→4 to prevent, and `test_every_committed_snapshot_loads_at_v4`
checks the version but not the field's presence. Field-less v4 snapshots exist today only at this
branch's own prior commits (`765e8b8`, `16dbaa7`), so real-world risk is low while the branch stays
unmerged — but nothing structural holds the premise after merge. A one-line test asserting every
committed v4 snapshot with reference bindings carries the field would close the residual cheaply.

**N2 — the written-form recovery degrades toward the bug on every error path.**
`_written_reference_text` (`usage_extractor.py:913-957`) returns `None` on a missing `cst_node`,
an invalid byte span, `get_source_file` raising, an unreadable file, an out-of-range span, or a
`UnicodeDecodeError`. A `None` qualifier is treated as a bare leaf, which for a `::`-qualified
reference re-anchors it — F2. So the fix's correctness silently depends on the CST byte span always
being recoverable; any failure fails toward the defect rather than surfacing. The `except Exception`
at `:938` (noqa "a missing location is an absence") is wider than its justification — a real adapter
bug also lands there and becomes "bare leaf." Unobservable on the current corpus, but the direction
is unsafe. `_SOURCE_BYTES_CACHE` keys on path only, not path+mtime — benign for the single-run CLI,
a stale-content risk only for a long-lived process that rewrites a fixture in place.

## Certification

**Marked this round:**
- Spec criterion 5 and epic criterion 5 (SR-A02) already checked; the scope note is now broadened —
  the qualified-reference case is handled correctly by written form, not deliberately missed. Left
  checked; the "not claimed for `::`" caveat is superseded and should be trimmed to the
  bracketed-owner case only (minor doc cleanup, not a gate).

**Item verdict: certifiable at the code level.** All four original findings (F1, F2, F3, F4) are
closed and independently reproduced across rounds. I am recording Pass-with-notes rather than a
clean Certify solely because of N1: an item whose own thesis is fail-closed schema skew left a v4
payload that validates two shapes, with no test guarding the difference. That is a design call the
owner ratified with verified premises, so it does not block — but it is the one thing worth an
explicit decision before merge, and the merge-order discipline (PR #11 before PR #9) is the moment
the "v4 never shipped" premise stops being free.

**Not checked this round:**
- The whole-corpus resolution probe behind FD-1's 23-across-seven — only the 3 fixtures with
  committed baselines corroborate the diff; the other 4 have no committed graph (standing exclusion).
- No re-audit of F1/F3/F4 code (untouched since `765e8b8`), nor of PC-1/PC-3/PC-6 (round 1).
- Live re-capture of the 36 snapshots; FD-4 line classification by the implementer's method.
- Execution lane, TEAx, the 363 `tests/` ruff findings, and round-1's
  `design_attribute_float_default` silent-`None` note (DD-R22) — all still open, out of scope here.
