# Evidence: Producer Completeness and Stellarator Rollup (Lifecycle Item 10)

**Status:** In progress — Phases 0 and 2 landed and verified; Phases 1 and 3 remain (plan below).
**Codegen candidate:** _(this commit — see CANDIDATE_REVs at bottom)_
**Chain:** codegen HEAD (this branch), agentic-mbse `4c18d61`, stellarator `43a1d405`.

---

## What is done and verified

### Phase 2 — capture sink + producer-completeness check (the novel mechanism; R2-closing)

- **Capture sink** — `src/sysml_codegen/resolution/producer_resolution.py`. A
  context-managed (`capturing_resolutions()`, ContextVar) sink centralized at the single
  public entry of `resolve_producer`. **Design improvement over the reviewed plan, stated
  honestly:** the review's Major 1 called for threading the sink through all five
  `resolve_producer` call sites (there are five, not the three enumerated:
  `constraint_lowering.py:174`, `dependency_backtracker.py:596`, `graph_builder.py:1403`,
  `:1640`, `:1663`). Centralizing capture *inside* `resolve_producer` covers all five (and
  any future site) **by construction** — a call site cannot be missed, which closes the R2
  blind spot more strongly than per-site wiring. The sink is inert unless a
  `capturing_resolutions()` block is active, so generation behavior is unchanged until the
  check is wired (Phase 1).
- **Completeness check** — `src/sysml_codegen/resolution/producer_completeness.py`.
  `check_producer_completeness(captured)` reads the sink's `(request, resolution)` pairs and
  flags: **ambiguous producer** (`ambiguous_candidates` non-empty — a same-leaf tie the
  resolver refused to guess) and **leaf-name guess** (a `DESIGN_ATTRIBUTE` resolved via a
  name-based lenient row `dotted_pair`/`leaf_unique`/`bare_name_unique`). A clean
  `ENTRY_POINT` (no ties, no name-based form) is exempt — a legitimate external declared
  input (invariant 26; D-1). `MODULE_OUTPUT` and exact-QN `DESIGN_ATTRIBUTE` are conformant.
  No re-resolution.
- **Tests:** `tests/unit/test_producer_completeness.py` (9) — check logic + sink capture,
  inactivity, and reset-safe nesting.

### Phase 0 — ambiguous/defaulted producer coordinate (RED-first)

- **License-free acceptance proven** — `tests/conformance/test_producer_completeness_acceptance.py`
  (3). A genuine two-same-leaf tie driven through the **real** `resolve_producer` under
  capture: the resolver refuses to pick (`ENTRY_POINT` carrying both tied QNs), and the
  completeness check names the ambiguity (`AMBIGUOUS_PRODUCER`). The named error is the
  check's, not the resolver's (Minor 6). The exact-QN escape (`target_qn`) resolves cleanly
  with zero violations — the other admissible observation.
- **Snapshot-route fixture authored** — `tests/fixtures/two_same_leaf_producers/`
  (`library.sysml`, `design.sysml`, `README.md`). Its `extraction_snapshot.json` capture is
  **deferred to the licensed pass** (see README) that also recaptures the stellarator, to
  avoid a separate license round-trip. Documented, not silently skipped.

### Regression + quality gates (verified at this candidate)

- `tests/unit` + `tests/conformance`: **2952 passed, 44 skipped (license), 0 failed** (49s).
  The `resolve_producer` wrapper is behavior-preserving (139 resolver/aggregation tests
  green: `test_producer_resolution_table`, `test_graph_builder_aggregation`,
  `test_backtracker_aggregation`, `test_aggregation_generation`, `test_alias_producers`,
  `test_sibling_channel_ambiguity`, `test_shared_producer_convergence`,
  `test_spec_chain_twolevel`, `test_deep_cross_scope_probe`, `test_gate_a_owner_classification`).
- `ruff`: clean on all new/touched files.
- `mypy`: zero errors introduced in the two changed/added `src` files (the 40 reported are
  the pre-existing baseline in unrelated files).

---

## What remains (honest status for audit / the licensed session)

The check is a tested mechanism but is **not yet wired as a hard generation gate**, and the
cross-part aggregation capability is not yet built. Wiring the gate is deliberately paired
with the Phase-1 fixture enumeration, because turning the completeness check on globally is
exactly what could move a frozen anchor or reclassify an existing fixture — the design makes
that enumeration "load-bearing for the frozen anchors." Sequencing:

- **Phase 1 — cross-part aggregation compilation + gate wiring.** Route chain-bearing FORMULA
  computed attributes into `build_aggregation_expression`'s full construction (incl.
  `has_unsupported`); enumerate the ~15+ chain-bearing-computed-attribute fixtures for
  per-fixture byte-identity (over-catch of EXPOSE_PURE/tentative/existing-aggregation is a
  STOP); the two-level chained fixture with a **structural** `module_output` assertion (A7);
  then wire `capturing_resolutions()` around graph build in `pipeline_builder` + snapshot
  rebuild and run the completeness check at finalization (raise on ambiguity). Needs the
  license for the live-route fixtures.
- **Phase 3 — stellarator cutover.** Restore canonical formulas in the twins → recapture
  (snapshot format is now v5, `test_snapshot_v5_gate.py`) → public generation (zero
  offenders) → runner cutover → six anchors + five verdicts EXACT → deletions incl. **both**
  harnesses (`bridge_v11_generate.py`, `run_stellaris.py` glue-2, `handshake_1costingfe.py`
  glue) → WI-027 amendment. Anchor movement is a STOP. Needs the license + teax exec env.
- **Phase 0 snapshot capture** — capture `two_same_leaf_producers` in the same licensed pass.

---

## CANDIDATE_REVs

- **sysml-codegen:** _(recorded at commit — see git log on `constraint-exec-epic`)_
- **agentic-mbse:** unchanged `4c18d61` (no coordinated change in Phases 0/2).
- **stellarator:** unchanged at `43a1d405` (Gate B filing commit; Phase 3 not yet started).
