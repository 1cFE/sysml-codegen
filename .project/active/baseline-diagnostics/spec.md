# Spec: Baseline Repair & Silent-Failure Diagnostics

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** LOW (hardening; ~0.5–1 day)
**Branch:** upstream-findings-epic
**Epic:** UPSTREAM-FINDINGS — Item 1

---

## Problem

Two things are wrong on `main`, and this item fixes both without changing what valid models generate.

**One test is red.** The `solar_battery` pipeline-YAML baseline comparison
(`tests/conformance/test_gen_pipeline_yaml.py:541`) fails. The generated output and the
committed baseline differ by a two-line ordering swap in the `entry_fusion` inputs — content
is identical, execution semantics are identical. The swap comes from the entry-point group
list being emitted in model-discovery order (`generation/pipeline.py:66` iterates the groups
as-derived), so a filesystem/discovery-order shift between capture machines reddens the suite.
The baseline comparison is a byte-exact string match, so any such shift fails it. A red test on
`main` muddies the signal for every change in this epic.

**Three failures are silent or opaque — the three worst in the register.** Each one lets a
real modeling gap pass without a clear signal:

- **Constraints vanish silently (SC-1).** `_extract_part_definition`
  (`extraction/extractor.py:106-107`) stubs `constraints = []`. Constraint usages in a model —
  `catf_mfe` has dozens of inline ones — are dropped with no warning. `modeling-assumptions.md`
  never even states that constraints are not executable, so this is also a contract-documentation
  gap. Nothing on the live path looks at constraints.

- **EXPOSE_PURE derived-attribute names are dropped (SC-7).** When an EXPOSE alias resolves,
  the modeler's chosen name (e.g. `total_cost`) does not surface into generated output — the
  value flows only through the canonical channel. The two existing warnings that fire on the
  EXPOSE_PURE resolution path (`resolution/graph_builder.py:672-687` and the Phase-3 registration
  site `orchestration/output_registry_builder.py:182-186`) report a bare "not in registry" and
  never explain that the *name* was dropped or where the value went.

- **Zero-output calc defs crash inside a Jinja template (SC-2).** A calc def that extracts with
  zero outputs reaches `templates/teax_module.py.jinja2:118`, which indexes
  `output_attributes[0]` and raises an opaque `IndexError` deep in template rendering. Legal
  SysML shapes (return-style outputs, bare `in` params — extracted in Item 3) currently produce
  zero outputs, so today they crash instead of failing with a diagnostic. The crash site is the
  actual bug regardless of which shapes become legal later.

This item is a 0.5–1 day hardening pass: repair the one baseline (recurrence-proof) and turn the
three failures into diagnostics that follow the V1–V6 pattern in `modeling-assumptions.md`
("Validation Rules") — clear, actionable, naming the fix.

## Success Criteria

- [ ] Full test suite passes on `main` — `solar_battery` YAML baseline re-captured via
      `scripts/capture_baseline_yaml.py` and committed.
- [x] The baseline stays green across a filesystem/model-discovery-order shift: the
      `entry_point_groups` list is sorted deterministically at ComputationGraph construction, so
      the graph itself — not just its rendered YAML — is order-independent (see the ordering
      decision below). *(Audit 2026-07-05: verified in code `graph_builder.py:362-366` + I1 test.)*
- [x] Generating a real constraint-bearing fixture (`catf_mfe_model`, which has dozens of inline
      constraints) emits a single summary WARN of the count plus per-constraint INFO lines —
      not per-item WARN noise, not silence. `catf_mfe` is the in-repo stand-in for the epic's
      "WI-014 toy + IFE models" diagnostic-emission evidence: those models live in fusion-tea and
      are out of this repo; the WI-014 toy arrives as a committed fixture in Item 8.
- [ ] The `_resolve_expose_pure` "key not found in registry" name-drop warning and the Phase-3
      registration warning state plainly that the derived-attribute *name* is dropped from
      generated output and name the canonical channel carrying the value. A minimal shape-A
      (part-def EXPOSE_PURE) fixture is committed and its generation emits the reworded message.
- [x] A calc def that extracts with zero outputs produces a hard, actionable extraction
      diagnostic (V-rule style) that names the likely cause and fix — the run never reaches the
      Jinja template. Verified against a real fixture with a zero-output calc def. *(Audit: `extractor.py:264-276` + `zero_output_calc` fixture + REQ-EXT-08 test.)*
- [ ] No baseline changes beyond the re-captured `solar_battery` YAML — the other three pipeline
      baselines and all extraction snapshots are byte-identical (valid models' output unchanged).
- [x] `modeling-assumptions.md` gains a "constraints are not executable" section; the zero-output
      rule is added to the "Validation Rules" table. *(Audit: §8 + V7 row verified.)*
- [x] Dead constraint code removed: `extraction/constraints.py` and
      `templates/constraint_validator.py.jinja2` (see dead-code decision below). *(Audit: both files deleted, deletion assertions added.)*
- [ ] Every new/changed behavior carries a REQ-* tag, a verification-matrix row, and an update to
      the relevant `docs/architecture/reference/` doc (R1).
- [ ] Each new diagnostic is locked in by a conformance test using a real SysML fixture, never a
      mock (R1).
- [x] agentic-mbse impact recorded — expected: endorse the A-1 constraint-non-executability WARN
      check (see the closing section). *(Audit: recorded in plan Phase 4 + spec §agentic-mbse impact for Item 12.)*

## Known Requirements

Proposed REQ IDs below; design finalizes numbering against the verification matrix.

**Baseline repair**

- **[HARD]** *(REQ-BASE-05)* The `solar_battery` YAML baseline is re-captured only via
  `scripts/capture_baseline_yaml.py` with a reviewed diff (R3) — never hand-edited. The re-capture
  requires a live syside license; the license is valid until 2026-08-06 and live capture now is
  in-window.
- **[NEED]** *(REQ-BASE-06)* The ComputationGraph is deterministic and independent of
  filesystem/model-discovery order, so an order shift between machines cannot redden the baseline
  again. **Decision (delegated to this spec): sort `entry_point_groups` by a stable derived key at
  ComputationGraph construction** (`graph_builder.py:364`), and keep the baseline comparison
  byte-exact. Sorting the graph (not the YAML) makes the deterministic ordering available to every
  consumer, including Item 2's snapshot path. Rationale is in *Decisions Recorded* below.

**SC-1 — constraint drop diagnostic**

- **[NEED]** *(REQ-EXT-30)* When constraint usages are found during extraction/orchestration and
  dropped, the pipeline emits one summary WARN reporting the total count and a per-constraint INFO
  line identifying each. Per-item WARN is explicitly avoided — `catf_mfe`'s dozens of benign inline
  constraints would drown real warnings.
- **[NEED]** *(REQ-DOC)* `modeling-assumptions.md` gains a "constraints are not executable"
  section stating that constraint predicates are dropped, why (no execution path today), and what a
  modeler who needs a viability gate should do instead.

**SC-7 — EXPOSE_PURE name-drop diagnostic wording**

- **[NEED]** *(REQ-CA-30)* Two EXPOSE_PURE warnings are reworded to state plainly that the
  modeler's alias name is dropped from generated output and name the canonical channel the value
  flows through: the "key not found in output registry" warning in `_resolve_expose_pure`
  (`graph_builder.py:683-687`) and the Phase-3 registration warning
  (`output_registry_builder.py:182-186`). The *malformed-refs* warning in `_resolve_expose_pure`
  (`graph_builder.py:672-675`, "could not identify instance/output") is a different failure and is
  left unchanged. Wording follows the V1–V6 pattern. This is a wording change only.

**SC-2 — zero-output fail-fast**

- **[HARD]** *(REQ-EXT-31)* A calc def that extracts with zero output attributes produces a hard
  extraction diagnostic and halts before generation — it can never reach the Jinja template. The
  message follows V-rule style: it names the calc def, states the cause (no output attribute
  extracted), and points at the likely fix (return-style/bare-param support is Item 3; anonymous
  `return` is unsupported). Added as a new row (V7) in the "Validation Rules" table.

**Cross-cutting (R1/R2/R3)**

- **[HARD]** Diagnostics follow the V1–V6 pattern: a dropped/rejected shape gets a clear,
  actionable message naming the fix; nothing is dropped silently.
- **[HARD]** Every new diagnostic lands with a conformance test using a real SysML fixture
  (`catf_mfe_model` for constraints; an EXPOSE_PURE-bearing fixture for the wording; a new minimal
  zero-output fixture for the fail-fast). No mocks.
- **[INFERRED]** A new minimal fixture with a single zero-output calc def is required — no existing
  baseline model has one (the research confirms no baseline uses return-style outputs). It must be
  loadable and trigger the fail-fast without depending on Item 3's extraction changes.
- **[INFERRED]** A new minimal shape-A EXPOSE_PURE fixture is required to fund the REQ-CA-30 test —
  a part def carrying an attribute and calcs, instantiated separately, so the reworded warning has
  a real model to fire against. Keep it to a handful of elements; capture via the standard scripts
  (live license). Fallback (recorded, not the plan): if capture proves disproportionate at
  implementation, defer the SC-7 warning test to Item 8's WI-014 toy with an explicit note.

## Non-Goals

- **Constraint execution.** Compiling `assert constraint` into boolean-output modules is a deferred
  epic. This item only makes the drop loud and documents it.
- **Return-style / bare-`in` extraction (Item 3).** Zero-output calc defs fail fast here; making
  them extract correctly is Item 3. In the interim, a legal return-style calc def hard-errors
  (loud) instead of crashing — strictly better, and no fixture model has this shape, so nothing
  in the corpus breaks.
- **Alias surfacing (Item 11).** Making the EXPOSE alias name appear in generated output, and
  warning on the *silent* shape-B (part-usage) drop, are Item 11. This item only rewords the two
  existing warning sites; shape B stays silent until Item 11.
- **Deleting `constraint_extractor.py`.** See the dead-code decision — it is kept.
- **Any behavioral change to valid models' generated output.** The only baseline that may change
  is the re-captured `solar_battery` YAML.

## Open Questions / Deferred to design

- **Exact placement of the constraint warning** — pure extraction (`_extract_part_definition`,
  and the calc-def path if constraint usages can appear there) versus an orchestration-time
  summary that aggregates across the model. The summary WARN + per-item INFO split suggests
  detection at extraction with the count rolled up at orchestration. Design decides.
- **Zero-output check placement and aggregation** — fail on the first zero-output calc def versus
  collect all and report together. "Fail-fast" argues for the former; design confirms and picks the
  exact extraction site (right after `output_attributes` is populated, `extractor.py:~164`).
- **Exact new REQ numbers and which reference docs get rows** — `01-extraction.md` for the
  zero-output and constraint diagnostics, `16-computed-attributes.md` for the EXPOSE wording,
  the baseline/verification-matrix doc for REQ-BASE-05/06. Design assigns final numbers.

---

## Decisions Recorded

These are the two spec-time calls the epic delegated to this item (orchestrator guidance).

### D1 — Prevent baseline-ordering recurrence at ComputationGraph construction

**Decision:** Sort `entry_point_groups` by a stable derived key (the group name) at ComputationGraph
construction (`graph_builder.py:364`), scoped to that list only, and keep the baseline comparison
byte-exact.

**Why the graph site, scoped to `entry_point_groups`:**

- It fixes the root cause per R1's "compute once / fix at the source" — the ComputationGraph is the
  sole input to generation, so making the graph deterministic makes every consumer deterministic,
  not just the YAML renderer. Item 2's snapshot path reads the same graph and inherits the fix for
  free.
- Non-deterministic output is a latent defect in its own right: spurious diffs across machines and
  CI, and different output handed to fusion-tea for the same model. Ordering the graph removes that
  class of problem, not just this one test failure.
- It keeps the byte-exact baseline comparison strong. Loosening the comparison to be
  order-insensitive would weaken a test that otherwise catches real ordering regressions.

**Scope and no-churn:** the review verified this sort is a no-op for the three currently-green
baselines — the `entry_point_groups`-only scope touches nothing else, and `entry_fusion` input
order does not affect execution. So the hard success criterion "no baseline changes beyond the
re-captured `solar_battery` YAML" stands unqualified: no other baseline is re-captured under this
decision.

### D2 — Delete `constraints.py` and `constraint_validator.py.jinja2`; keep `constraint_extractor.py`

**Decision:** Delete the two dead files the epic names; keep `constraint_extractor.py`.

**Evidence (verified against HEAD):**

- `extraction/constraints.py` (262 lines) is imported by nothing on the live path — it only loads
  the `constraint_validator.py.jinja2` template, and nothing loads it. Cleanly dead.
- `templates/constraint_validator.py.jinja2` (17 lines) is referenced only by
  `constraints.py`. Cleanly dead.
- `extraction/constraint_extractor.py` (261 lines) is imported by nothing either, but it imports
  `expression_utils.reconstruct_expression` — a live module (SC-6's target). The dependency runs
  *from* the dead file *to* live code, so deleting `constraint_extractor.py` would not break
  anything. It is kept anyway because the deferred constraint-execution epic will rewrite (not
  wire in) the extractor, and it is a useful in-repo reference for the inline-constraint shape;
  deleting it is not in this item's named scope. It is unimported, so it is harmless.
- `PartDefinitionData.constraints` / `ConstraintInfo` (`extraction/data_models.py`) stay — the
  field is part of the frozen extraction data model and is asserted by the field-set conformance
  test (`tests/conformance/test_data_models.py:285`). It remains always-empty until the future epic.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 1 + Cross-Cutting R1/R2/R3)
- **Required Reading:**
  - `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md` — findings
    register. *Note: this path is outside the working sandbox and could not be read directly during
    spec'ing; its content is covered by the research report (authoritative on disagreements) and the
    epic's manifestation summaries.*
  - `.project/research/20260705_upstream-findings-deep-research.md` — deep research (SC-1, SC-2,
    SC-6, SC-7 sections; wins over the register on disagreements, verified against HEAD)
  - `docs/architecture/modeling-assumptions.md` — supported-subset contract
- **Design:** `.project/active/baseline-diagnostics/design.md` (to be created)

---

## agentic-mbse impact

- **Endorse A-1 (constraint non-executability WARN check).** sysml-codegen now warns at extraction
  when constraints are dropped; agentic-mbse should carry the matching Level-6 (or equivalent)
  guidance/check that constraints are not executable, with the negative fixture. Recorded here for
  Item 12 (the epic's agentic-mbse sync item); no agentic-mbse code change is made in this item.
- **Documentation pointer.** The new "constraints are not executable" section in
  `modeling-assumptions.md` becomes the canonical reference the agentic-mbse guidance points at.
- Nothing else in this item changes what models should look like, so no MODELING_GUIDE / skill
  stencil change is triggered by Item 1.

---

**Next Steps:** After approval, proceed to `/_my_design`.
