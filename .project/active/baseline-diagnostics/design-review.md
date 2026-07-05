# Design Review: Baseline Repair & Silent-Failure Diagnostics

**Design:** `.project/active/baseline-diagnostics/design.md`
**Spec:** `.project/active/baseline-diagnostics/spec.md`
**Spec review:** `.project/active/baseline-diagnostics/spec-review.md`
**Review File:** `.project/active/baseline-diagnostics/design-review.md`
**Date:** 2026-07-05
**Reviewed against:** HEAD `2601b55` (branch `upstream-findings-epic`)

---

## Fundamental Assessment

**Sound — with one re-capture gap that will redden the suite if shipped as written.**

The four-edit approach is right-sized for a hardening item: no new module, class, or abstraction;
each fix lands at the site that already owns the concern. The two relocations the design makes on
top of the spec — moving the constraint diagnostic to the calc-def path (Finding 1), and moving the
sort into the graph (D1) — are both correct improvements, and I verified the code claims behind them
against HEAD. This is not a rework.

But the review turned up one thing the design's own safety argument misses, and it hits the item's
top success criterion:

- **The sort breaks a byte-exact ComputationGraph comparison test** (`test_factory_purity.py`,
  REQ-MF-01) for `solar_battery`. The design re-captures only `solar_battery.yaml`. It must also
  re-capture `baseline_outputs/solar_battery/computation_graph.json`, or "full suite green" fails.
  See C1.

And one factual error that creates a blind spot in the very failure the item exists to close:

- **Finding 1's "catf_mfe's constraints all live inside calc defs" is false.** Some live in part
  defs, which the calc-def-path detector never sees — so a class of constraint drops stays silent.
  See M1.

Both are fixable inside the current design; neither changes the shape of the four edits. Verdict is
**Revise**.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

The design covers every spec success criterion and correctly carries the four spec-review
resolutions (D1 sort site, D2 calc-def path, sequential REQ numbers, the two-warning rewording).
Two gaps:

- **Re-capture scope is under-specified and will leave a red test (C1).** The spec's #1 SC is "full
  suite green." The design's re-capture plan names only `solar_battery.yaml` via
  `capture_baseline_yaml.py`. But moving the sort into `build_computation_graph` (D1) changes the
  `ComputationGraph` object itself — and `test_factory_purity.py::test_computation_graph_identical`
  (REQ-MF-01), parametrized on `solar_battery_model`
  (`tests/conformance/test_factory_purity.py:125`), does a raw byte-exact compare:
  `graph.model_dump(mode="json") == baseline` (`test_factory_purity.py:507`), with no
  entry_point_groups ordering normalization. When the sort reorders solar_battery's groups, this
  assertion fails. The committed `baseline_outputs/solar_battery/computation_graph.json` must be
  re-captured via `capture_pipeline_baselines.py`. This is the item's headline risk and the design
  does not name it.

- **Part-def constraint blind spot (M1).** SC-1's intent is "nothing dropped silently." The
  calc-def-only detector leaves part-def-owned constraints silent. Detail under Dimension 7.

### 2. Pattern Consistency
**Assessment:** Pass

Verified against HEAD:
- **ValueError for hard fails** is the established convention — `parameter_groups.py:309/348/374/401`,
  `graph_builder.py:622/777/1487/1505/1516` all `raise ValueError`. There is no `ExtractionError`
  class and no error-code scheme. D3's plain `raise ValueError` is correct; a collector/diagnostic
  object would invent a pattern the codebase does not use.
- **`logger.warning`/`logger.info`** via the module-level stdlib logger (`extractor.py:27`) is the
  soft-diagnostic convention. D2/D4 match it.
- Sequential per-family REQ numbering matches the matrix (Dimension 7 / D5 check).

### 3. Abstraction Quality
**Assessment:** Pass

No new abstractions. The one piece of shared state — `self._dropped_constraint_count` — is a
private int reset per run, read once after the loop. That is the minimum needed for a summary WARN
and does not leak. Nothing here is over-built.

### 4. Duplication Avoidance
**Assessment:** Pass

The design routes each fix to its single owning site rather than adding a parallel validation layer,
and deletes genuinely dead code (`constraints.py`, `constraint_validator.py.jinja2`) — verified
unimported at spec-review time. No new duplication.

### 5. Data Structure Clarity
**Assessment:** Pass

No schema change. The sort reorders the contents of an existing field (`entry_point_groups`); it does
not alter `ComputationGraph`'s shape. Confirmed `CalculationDefinitionData` has no constraints field
(`extractor.py:215-229`), which is why the constraint drop is count-and-log, not capture — correct.

### 6. Route Safety
**Assessment:** Pass (with the probe caveat the design already owns)

D3 fails fast at extraction (Step 2 of `pipeline_builder`, `extract_calculation_definitions()` at
`pipeline_builder.py:482`), which runs long before any generation or file write — so the ValueError
cannot leave partial output on disk. Confirmed. The EXPOSE probe branch (Finding 2) is a genuine
fork in behavior, but the design handles it explicitly with probe-first + a recorded Item-8 fallback,
and refuses to reword the malformed-refs warning to force a green test. That is the safe routing.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- **B1 is fine as a test-funding bet, but Finding 1's prose overstates it and hides a real bet.**
  B1 claims catf_mfe's constraints are reachable as `ConstraintUsage` members of the *calc-def*
  element. That is true for the geometry/power_balance/thermal calc defs — `geometry.sysml:59`
  `constraint PositiveRadii` sits inside `calc def TorusMinorRadius`. So the summary WARN *will* fire
  and REQ-EXT-09's test is funded. **But Finding 1 also asserts "catf_mfe's dozens of constraints
  all live inside calc defs" — and that is false.** `radial_build.sysml:55` `constraint
  RadiusConsistency` sits inside `part def 'Radial Build Layer'` (`radial_build.sysml:11`). The
  hidden bet is: *catf_mfe has no part-def constraints.* It does. See M1 for the consequence.

- **D2's rejection of orchestration-time detection rests on that false premise.** D2 rejects a
  cross-method summary "since all live constraints are calc-def-owned." They are not. And part defs
  *are* iterated on the live path — `pipeline_builder.py:115` walks
  `elements_of_type(model, "PartDefinition")` for design-attribute extraction — so detecting
  part-def constraints there is feasible, not the "cross-method plumbing for no gain" D2 claims. The
  decision may still be right (scope the item to calc-def constraints and defer part-def), but its
  stated reason is wrong and should be restated honestly.

- **B3 (sort is a semantic no-op) holds** — entry-group order is serialization-only; I verified the
  order-independent consumers (`qn_to_group` at `graph_builder.py:343`, YAML renderer at
  `pipeline.py:66`). But the design generalized "the sort is safe" from those two consumers without
  enumerating the rest, and one of the others (`registry.py:185`, an ordered `class_name` list) plus
  the byte-exact graph test are exactly what C1 trips over. The bet is true; the safety argument
  built on it is incomplete.

- **D5 numbering verified, no collisions.** The live matrix tops out at REQ-EXT-07, REQ-CA-08,
  REQ-BASE-04 (`docs/architecture/verification-matrix.md`). The design's EXT-08/09, CA-09,
  BASE-05/06 are the next sequential IDs with no clash. The spec's 30-band was an unexplained gap;
  D5's correction is right.

- **D1/D3/D4 decisions each name the rejected alternative with a real reason.** Good.

### 8. Reader Comprehension
**Assessment:** Pass

The design leads with the point, separates confirmed-as-spec from the two relocations, and states
each bet with an "if false" consequence. A tired engineer can skim it and know what changes and why.
No voice issue blocks the model. The one comprehension cost is the factual error in M1 — a reader who
trusts "all live inside calc defs" builds the wrong mental model of the diagnostic's coverage.

---

## Issues by Severity

### Critical

- **C1 — The sort reddens `test_factory_purity.py` for solar_battery; re-capture plan is
  incomplete.** `test_computation_graph_identical` (REQ-MF-01) does a raw
  `graph.model_dump(mode="json") == baseline` on `solar_battery_model` with no group-ordering
  normalization (`test_factory_purity.py:507`, params at `:125`). Moving the sort into the graph (D1)
  changes solar_battery's `entry_point_groups` order, so this byte-exact assertion fails. The design
  re-captures only `solar_battery.yaml`; it must also re-capture
  `baseline_outputs/solar_battery/computation_graph.json` (and `registry_init.py`) via
  `capture_pipeline_baselines.py`. Without this, the item's #1 success criterion — full suite green —
  is not met. Note: `test_pipeline_e2e.py` and `test_graph_assembly.py` compare the same baseline but
  *normalize* entry_point_groups order (they say so in their docstrings), so they stay green;
  `test_factory_purity` is the one that does not.

### Major

- **M1 — Part-def-owned constraints stay silent; Finding 1's "all live inside calc defs" is false,
  and the summary WARN overclaims.** `radial_build.sysml:55` (`constraint RadiusConsistency` in a
  `part def`) is dropped and never counted by the calc-def-path detector. The summary string "Dropped
  {n} constraint usage(s) across the model" claims model-wide coverage it does not have, and leaves a
  slice of the exact silent-drop failure SC-1 exists to kill still silent. Decide one of: (a) extend
  detection to part-def constraints at the existing `pipeline_builder.py:115` PartDefinition
  iteration; or (b) explicitly scope the diagnostic and the summary wording to *calc-def* constraints,
  document the part-def drop as a known limitation in `modeling-assumptions.md`, and correct
  Finding 1 / D2's rationale. Either is acceptable; the current design silently does (b) while its
  prose claims (a)-level coverage.

### Minor

- **m1 — I4 defines N ambiguously.** "N = constraint count" must mean *calc-def-owned* constraint
  count, not the total `grep -c constraint` over catf_mfe (which includes part-def constraints the
  detector never sees). Pin this in I4 and in the REQ-EXT-09 caplog test, or the test target is
  ambiguous and may be written against the wrong number.

- **m2 — The "consumers iterate order-independently, so the sort is safe" claim is incomplete.**
  Beyond `qn_to_group` and the YAML renderer, `entry_point_groups` is consumed by `registry.py:149`
  and `registry.py:185` (`group_names = [g.class_name for g in graph.entry_point_groups]` — order
  *dependent*), and `entry_point.py:238/293` (per-group schema/JSON files). These are no-ops for the
  three green baselines only because those have ≤1 group; they are not order-independent in general,
  and `registry.py:185` is the reason solar_battery's `registry_init.py` baseline also goes stale.
  Enumerate the real consumer set so the re-capture scope (C1) is grounded.

---

## Recommendations

1. **Fix C1 first — it gates "suite green."** Add `capture_pipeline_baselines.py` to the re-capture
   step and commit solar_battery's re-captured `computation_graph.json` (+ `registry_init.py`)
   alongside the YAML. Confirm attr_expr_probe (the other REQ-MF-01 param) is single-group and thus
   unchanged, so its baseline stays byte-identical. Update I2 to say "solar_battery's YAML *and*
   ComputationGraph baseline are re-captured; the other three models' YAML, graph, and extraction
   snapshots are byte-identical."

2. **Resolve M1 by choosing (a) or (b) explicitly.** If (b) — the pragmatic Item-1 scope — reword the
   summary WARN to say "calc-def constraint usage(s)" (not "across the model"), correct Finding 1 and
   D2's stated reason, and add the part-def blind spot to Non-Goals with an Item pointer. If (a),
   count at `pipeline_builder.py:115` too.

3. **Tighten I4 (m1) and the consumer enumeration (m2)** so the test target and the sort's safety
   claim are both grounded in the real code.

Everything else verified clean: D3's ValueError type and fail-before-write timing, no zero-output
calc def in any committed snapshot (so D3 is a corpus no-op), D4's two-site rewording with
malformed-refs untouched, Finding 2's probe-first sequencing and its simple-name-vs-EQN risk analysis
(`graph_builder.py:666` compares `ref.name` against `calc_usage_names` = `{u.instance_name ...}` at
`:193`), D5's collision-free numbering, and R1 conformance (real fixtures, matrix rows, named
reference-doc updates).

---

## Resolutions

*Filled in during Stage 4 as each issue is resolved. This section is what the design agent reads to
incorporate the review.*

- **[C1]** _(pending)_
- **[M1]** _(pending)_
- **[m1]** _(pending)_
- **[m2]** _(pending)_

---

**Overall:** Revise
**Next Steps:** Resolve C1 and M1 here (they change the re-capture plan and the constraint diagnostic's
stated scope), then re-run `/_my_design` (or return to the design-agent session) and point it at this
review to incorporate. The reviewer does not edit the design.
