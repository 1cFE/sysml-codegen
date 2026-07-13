# Design Review: `module_kind` and the Generation-Seam Refactor (Item 6)

**Design:** `.project/active/module-kind-refactor/design.md`
**Spec:** `.project/active/module-kind-refactor/spec.md`
**Review File:** `.project/active/module-kind-refactor/design-review.md`
**Date:** 2026-07-12
**Reviewer posture:** skeptical; every load-bearing claim checked against the code, not the design's word.

---

## Fundamental Assessment

**Sound.** The approach is the right one and it is not over-built. Replacing two accreted
Booleans with one explicit `module_kind` and turning each seam's inference into a lookup is the
minimal change that both (a) preserves byte-identity for the three existing kinds and (b) converts
the S4 silent mis-render into a loud refusal. The design resists the two tempting over-reaches —
it does not build the structured-render path (D5 reading (a)), and it does not invent a central
dispatcher the seams don't want (D3). The `output_schema_type` carrier is the one piece of
forward-provisioning, and it is justified: it folds Item 7's schema churn into this item's
already-planned baseline regen instead of re-opening the model twice.

I verified the design's highest-risk technical claims directly, and they hold:

- **str-Enum serialization / round-trip.** Confirmed against a committed baseline:
  `compilability` renders as `"fully_compilable"` (the `.value`), so a `str`-Enum serializes as
  its value with no config (`wi014_toy/computation_graph.json:43`). D1's rejection of plain-`Enum`
  and `Literal` is well-grounded.
- **`None` fields are serialized.** `compiled_expression` renders as `null`
  (`wi014_toy/computation_graph.json:44`) — the dump is not `exclude_none`/`exclude_defaults`. So
  `output_schema_type: null` **will** appear in every module of every baseline. D5's recorded cost
  is real and stated correctly; the baseline-diff spec is right to include it.
- **Serialization order = declaration order.** In the baseline the keys run
  `execution_order → compilability → compiled_expression → is_computed_attribute → is_aggregation
  → auto_impl_context` (`wi014_toy:42-47`), matching `models.py`. So D2's "localized two-out /
  two-in replace at the same position" is exactly what `model_dump_json` will produce — no
  field-order reshuffle across baselines.
- **`extra='ignore'` (brief Q3).** Confirmed: `PipelineModule` (`models.py:161`) has no
  `model_config`, so Pydantic v2's default `extra='ignore'` applies. Stale test kwargs are
  **dropped**, not raised. The design's backstop reasoning (the INV-4 grep, not construction
  errors, is the completeness check) is correct — including the sharp consequence that
  `module_kind` must be a **required field with no default** so a *missed construction site*
  still fails loud (a removed kwarg is silent, but an absent required field is a Pydantic error).
  D2's "no default" is load-bearing, not stylistic.
- **Migration surface is complete on the src side (B3).** A repo-wide grep finds the flags in
  exactly the 8 src files the design names — no hidden reader (`registry.py`, `graph_builder.py`,
  `pipeline.py`, `modules.py`, `models.py`, `test_gen.py`, `stencils.py`, `cli/__init__.py`).
- **Comparison harnesses read the flag keys.** Confirmed at `test_pipeline_e2e.py:86-90`,
  `test_graph_assembly.py:563-567`, and the ordered field inventory
  `test_data_models.py:584-585`. The lockstep coupling the design insists on is real.

Two must-fixes below are precision gaps in an otherwise executable design — one seam's shape is
mis-described, and the fail-loud test contract (INV-3) is under-specified at exactly the seam that
can silently drop a kind. Neither touches the foundation. Proceed to the dimensional review.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Pass

Every spec requirement maps to a design element: the five-member enum (D1), the one-to-one
flag→kind construction map (Architecture table), the four-seam dispatch (Architecture), the
repo-wide zero-hit gate (INV-4), fail-loud for constraint/report_aggregator (D4/INV-3), the
lockstep baseline+harness move, and the snapshot-decoupling non-goal. The [INHERITED]
structured-output-schema requirement is carried at its minimal float-identical reading (D5),
matching the spec's own recommendation (Open Question (b), reading (a)). Provenance is preserved:
the design cites the spec's [HARD]/[INHERITED] grades where it leans on them (B1 cites spec
L65-70; D5 cites the [INHERITED] requirement), and it does not silently harden a challengeable
item — `output_schema_type` is introduced as inert, exactly the spec's "introduced and proven
float-identical here, exercised in Item 7" force.

### 2. Pattern Consistency
**Assessment:** Pass

`ModuleKind(str, Enum)` sits beside the codebase's existing `str`-Enums (`EntryPointType`
at `models.py:24`, `Compilability` at `expression_compiler.py:25`) — same base, same serialized
form. The fail-loud raise reuses `CodeGenerationError`, already the generation layer's fail-fast
type (`cli/__init__.py:203,217`; caught at the CLI boundary `cli/__init__.py:876`). No new
mechanism. One imprecision worth a doc-line: `CodeGenerationError` is *defined* in
`orchestration/pipeline_context.py:48` and only **re-exported** through `generation/__init__.py`.
The design's "colocated with `CodeGenerationError` in `generation/`" (Component Overview) will
send an implementer looking for the class definition where it isn't. (Nice-to-have below.)

### 3. Abstraction Quality
**Assessment:** Pass

One enum, one shared error constructor, six local dispatches. The design correctly refuses a
central dispatcher (D3): the seams genuinely don't share a return shape, so one function would fit
none. The `unrenderable_module_kind_error(module, seam_name)` helper earns its place — it gives
the refusal uniform identity across six call sites without forcing the return shapes together.

### 4. Duplication Avoidance
**Assessment:** Pass

The per-seam dispatch is deliberately local because the QN derivations differ per seam; that is
not duplication, it is genuinely different logic. The one shared thing (the error) is shared.

### 5. Data Structure Clarity
**Assessment:** Pass

`module_kind` replaces two ambiguous Booleans with one named value — a strict clarity gain. The
design closes the two-flag space's fourth (both-true) cell honestly: it is unreachable because no
construction site sets both, so three members cover every constructible module (B1, matching spec
L65-70). `output_schema_type: str | None` is a plain, typed field.

### 6. Route Safety
**Assessment:** Concerns — see must-fix 2

The whole point of the item is route safety: no constraint kind may take a calc path or be
skipped. The design's dispatch-plus-raise achieves this **at the seams it rewrites**, but one
seam has a filter shape that fails *open*, and the design's verification contract (INV-3) is
specified at a level that would not catch a regression there. Detail in must-fix 2.

### 7. Bets & Decisions Integrity
**Assessment:** Pass

B1–B3 are genuine claims about reality, each with an "if false → what fails," and I verified all
three against the code (construction sites `graph_builder.py:1183,1586`, neither-flag site 1783;
the 8-file src reader set; the 9 flag-carrying baselines). The decisions each name a rejected
alternative with a reason (Literal/plain-Enum, append-at-end, central dispatcher,
NotImplementedError, field-validator, build-the-render-path-now). **Hidden-bet hunt:** the one
unstated bet I can find is *"every seam iterates all modules, so a constraint module actually
reaches the raise."* That is true today but it is the belief must-fix 2 is about — the registry
seam's partition can drop an unknown kind before any raise, so this bet is not free; it has to be
protected by the guard-pass **and** by a seam-entry-level test. Surfacing it is the point of
must-fix 2.

### 8. Reader Comprehension
**Assessment:** Pass

The design leads with the concept (kind is computed at every seam today; make it an explicit
property, set once, looked up everywhere), then the mechanism. The per-seam before/after table,
the baseline-diff spec, and the migration-order list are exactly what a mechanical implement
session needs. A tired engineer can skim it once and know the work and the gate.

---

## Issues by Severity

### Critical
None.

### Major (must-fix before implementation)

- **M1 — Seam 1's `_raw_source_name` is a *two-arm* function, not three; the design describes it
  as three-arm and its blanket mechanical rule mis-maps it.** The design says "Seam 1 — … The
  three `if/elif/else` arms keep their exact QN-derivation bodies, rekeyed to `module_kind`."
  That is true for `_get_python_path` (`cli/__init__.py:150-161`, a real
  computed/agg/else chain) but **false for `_raw_source_name`** (`cli/__init__.py:164-174`):

  ```python
  if module.is_computed_attribute:
      return f"{module.calc_def_qualified_name}::{module.calc_def_name}"
  return module.calc_def_qualified_name or module.name
  ```

  There is no `is_aggregation` branch — **aggregation shares the calc `else`**. The design's
  stated mechanical rule ("`is_aggregation` branch → `AGGREGATION` arm") has nothing to map to
  here. An implementer applying the three-arm template verbatim could give `AGGREGATION` its own
  arm or route it to the raise; either breaks every aggregation module, because
  `_raw_source_name` is called for **all** modules in `_check_duplicate_output_paths`
  (`cli/__init__.py:200,214`), not only colliding ones. The correct migration groups
  `AGGREGATION` **with** `CALCULATION` in the `return calc_def_qualified_name or name` arm;
  only `CONSTRAINT`/`REPORT_AGGREGATOR` raise.

  *Why it matters:* the byte-identity gate would catch a divergence here as a hard abort (not a
  silent diff), so it is not a silent-gate-defeat. But the design's core promise is that each
  seam's shape is "spelled out so a sonnet implement session executes it without judgment calls,"
  and this seam's spelled-out shape is wrong. Fix: give `_raw_source_name` its own two-arm
  before/after in the Seam 1 entry (FORMULA arm; AGGREGATION+CALCULATION share the QN-or-name arm;
  CONSTRAINT/REPORT_AGGREGATOR raise), separate from `_get_python_path`'s three-arm shape.

- **M2 — INV-3's fail-loud contract must be tested at the *seam entry point*, not the inner
  helper, because the registry seam fails *open* if the guard-pass is dropped.** The registry seam
  partitions by membership:

  ```python
  calcusage_modules   = [m for m in graph.modules if not m.is_computed_attribute and not m.is_aggregation]
  formula_modules     = [m for m in graph.modules if m.is_computed_attribute]
  aggregation_modules = [m for m in graph.modules if m.is_aggregation]
  ```
  (`registry.py:221-226`).

  The design correctly rewrites this to partition by `module_kind ==` and **adds a guard pass**
  that raises for `CONSTRAINT`/`REPORT_AGGREGATOR` before the split. Good — but the guard is the
  *only* thing standing between a constraint module and silent disappearance: a
  partition-by-equality simply **omits** any kind that matches no list. If the guard is forgotten,
  or is added but later regressed, a constraint module is dropped with **no raise and no diff** —
  the exact silent outcome the item exists to kill. The design's INV-3 says "construct a
  `PipelineModule(module_kind=CONSTRAINT, …)` and assert each of the six sites raises." If a test
  calls the *inner helper* (e.g. `_get_module_sysml_qn`) it passes even when the seam that drives
  it silently filters the module out. Pin INV-3 to call the **seam entry point** — the function
  that iterates `graph.modules` (`generate_registry`, `_check_duplicate_output_paths`,
  `_generate_modules`, `_generate_stencils`, the pipeline-YAML builder, the test-gen builder) with
  a graph containing a constraint module — and assert *that* raises. The registry seam is the one
  that can't be covered by a helper-level test; call it out explicitly.

  *Why it matters:* directly answers the brief's Q4 ("no seam where the kind is silently filtered
  before dispatch"). The registry seam *is* a filter-before-dispatch shape; the design mitigates
  it, but the mitigation is only as strong as a test that exercises the seam end-to-end.

### Minor (nice-to-have)

- **m1 — `CodeGenerationError` home.** It is defined in `orchestration/pipeline_context.py:48`,
  re-exported via `generation/__init__.py:24,69`. The design's "colocated with
  `CodeGenerationError`" (Component Overview / Core Concept) is imprecise. State that the new
  helper lives in `generation/` and *imports* `CodeGenerationError` (definition is in
  orchestration), so the implementer doesn't hunt for a class that isn't defined there.

- **m2 — Baseline count is 10 dirs, 9 with flags.** There are 10 `baseline_outputs/*`
  directories; `sample_model/computation_graph.json` has **zero modules** (`"modules": []`), so it
  carries no flag keys and regenerates byte-identically. The design/spec "9 baselines" is correct
  for flag-carrying files. Add a one-line note so the implementer isn't alarmed that the diff
  touches 9 of 10 baseline JSONs and treats `sample_model` as unchanged (not missed).

- **m3 — Ordered field-inventory insert position.** `test_data_models.py:578-591` asserts the
  field list **in order**. When swapping the two flags for `module_kind` + `output_schema_type`,
  they must land at the flags' position (after `compiled_expression`, before `auto_impl_context`)
  to match declaration/serialization order. The design's D2/Architecture already places them
  there; just make the ordered-list constraint explicit in the test-migration note so it isn't
  appended at the end of the inventory.

- **m4 — The blanket "reproduce verbatim" rule doesn't literally fit three of the six sites.**
  The pipeline-YAML label is a **ternary** (`pipeline.py:127-134`), the stencils auto-impl counter
  is a pair of **guard-`continue`s** (`stencils.py:208-220`), and test-gen is a single **`or`
  guard** (`test_gen.py:47`) — none is an `if/elif/else` chain, and a ternary cannot raise inline.
  The design's *per-site* notes handle each correctly (ternary "rekeys," the loop guards become
  `if/elif`, the `or` becomes `in`), so this is not a correctness gap — but the blanket rule
  ("`is_computed` branch → FORMULA arm … `else` → CALCULATION arm") in the Dispatch preamble reads
  as if all six are the same shape. Caveat the blanket rule, or lean on the per-site notes as the
  authority.

---

## Answers to the brief's five probes

1. **Byte-identity / serialization (Q1):** Verified correct. str-Enum → `.value`, `None` →
   `null`, order = declaration order; the per-module diff is exactly two-out (`is_computed_attribute`,
   `is_aggregation`) / two-in (`module_kind`, `output_schema_type: null`) at the same position.
   D5's cost claim holds. No key-ordering surprise.
2. **Generated-package gate / four seams (Q2):** Existing-kind branches are behaviorally identical
   for Seams 2, 3, 4 and for `_get_python_path` in Seam 1. **Exception:** Seam 1's
   `_raw_source_name` is mis-described (M1) — its AGGREGATION path must join CALCULATION, not get
   its own arm.
3. **`extra='ignore'` (Q3):** Verified — no `model_config` on `PipelineModule`. Stale kwargs drop
   silently; the required-field-no-default choice is what makes a missed *construction* site loud.
   Design's reasoning is correct.
4. **Fail-loud reachability (Q4):** `CodeGenerationError` is the right family (generation
   fail-fast, caught at the CLI boundary). All six sites can raise, **but** the registry seam
   fails open if its guard-pass is missing, and INV-3 as written may test below the seam entry —
   see M2.
5. **Migration order (Q5):** The tree **cannot** pass the suite at each stage boundary, and the
   design says so plainly: red between steps 1 and 4, green only at the end, with step 4 (baseline
   + harness + test edits) as **one atomic move**. That is correct — after step 1 the required
   `module_kind` field with no default makes every un-migrated construction site raise, and
   un-migrated src reads hit `AttributeError`. The lockstep step 4 is genuinely atomic (regenerated
   `module_kind` JSON and the harnesses that read it must change together). No change needed;
   the design's answer to this probe is right.

---

## Recommendations

1. **M1** — Rewrite the Seam 1 entry to give `_raw_source_name` its own two-arm before/after
   (AGGREGATION shares the calc QN-or-name arm), separate from `_get_python_path`'s three-arm shape.
2. **M2** — Pin INV-3 to call each seam's **entry point** (the module-iterating function) with a
   constraint-bearing graph, and call out the registry partition as the seam that fails open
   without its guard-pass. This is what makes the fail-loud contract real rather than helper-local.
3. Fold in the four nice-to-haves (helper home, 10-vs-9 baselines, ordered field-inventory
   position, blanket-rule caveat) as doc precision so the implement session stays mechanical.

---

## Resolutions

*(To be filled in as the owner engages. Keyed by finding ID.)*

---

**Overall:** Approved-with-must-fixes

**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to fold in M1, M2, and the nice-to-haves. The reviewer does
not edit the design. Both must-fixes are localized doc/test-spec sharpenings — no rework of the
approach, which is sound and code-verified.
