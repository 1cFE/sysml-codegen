# Audit: Lifecycle Item 4 — Diagnostic Severity and Modeled-Default Fidelity

**Verdict:** Needs Work
**Audited:** 2026-07-20
**Branch:** `constraint-exec-epic` (both repos)
**Commit:** sysml-codegen `16dbaa7` (evidence `6d3d3c5`, brief `b104659`), agentic-mbse `4c18d61`

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
