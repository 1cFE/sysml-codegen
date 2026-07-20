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

## Phase 1 — cross-part aggregation routing (LANDED, byte-clean) + a blocking finding (STOP)

**The FORMULA→aggregation routing mechanism is built and byte-identity clean.** New Step 4.7
in `pipeline_builder.build_pipeline_context` (`_route_crosspart_formula_aggregations`) routes a
chain-bearing, non-compilable FORMULA computed attribute into the SAME `build_aggregation_expression`
full construction (decompose + neutral render + `has_unsupported` guard) a `:>>` EXPRESSION sum
uses, appending the scoped aggregation to `scoped_agg_data` before Phase-1b registration. The
routing key fires strictly on FORMULA + not-FULLY_COMPILABLE + `singleton_terms` present — provably
disjoint from EXPOSE_PURE/tentative/existing aggregations.

- **Byte-identity sweep clean:** full licensed `tests/unit`+`tests/conformance` = **2953 passed /
  0 failed / 44 (non-license) skipped**. Zero baseline moved; no fixture reclassified (the target
  shape exists in no current fixture, confirmed by the routing map). No over-catch.
- **A7 (chained aggregation) PROVEN on the real stellarator.** Building the canonical stellarator
  graph, `direct_capital`'s aggregation wires `powercore_capital` and `bop_capital` inputs to
  `source_type=module_output` with the exact channel identities
  (`hif_plant_pkg__stellaris__powercore_capital__powercore_capital`, `…__bop_capital__bop_capital`).
  The producer-registration precondition holds by construction (Phase-1b registers all aggregation
  channels before any module build). This is the structural (channel-identity) proof A7 required.

### 🛑 BLOCKING FINDING — cross-part `child.attr` resolution collapses (Phase 3 blocked)

Building the canonical stellarator graph with the routing on, **every cross-part `SingletonTerm`
collapses**: `magnet.capital_cost`, `heating.capital_cost`, … (13 terms across
`powercore_capital`/`bop_capital`/`direct_capital`) all resolve to the SAME def-level design
attribute `mfe_magnet_cost__Magnet_Coil_Cost__capital_cost` via `key_form=leaf_unique` — the
resolver **drops the `magnet.`/`heating.` qualifier and leaf-matches `capital_cost`** to one
producer. The per-child channels exist (e.g. `stellarator_09__stellaris__magnet_cost__capital_cost`),
but the resolver does not follow each child part usage's `:>> capital_cost = X_cost.capital_cost`
redefinition per instance.

- **The design's Decision-1 premise is empirically false.** The routing map and design assumed
  "the aggregation path already resolves cross-part references through resolve_producer to a real
  MODULE_OUTPUT." It does not for the stellarator's child-part-redefinition shape — it resolves them
  by a qualifier-dropping leaf guess. This is WI-015 finding #4 at its root, deeper than scoped.
- **Item 10's producer-completeness property is genuinely VIOLATED by the stellarator at today's
  chain.** The Phase-2 completeness check catches it exactly: **13 `leaf_name_guess` violations**,
  one per collapsed term. Producing the six anchors from this graph would give WRONG numerics (every
  term = the magnet cost) — an anchor-movement STOP if pushed.
- **Per the design STOP protocol** ("if it does not resolve through the ordinary `resolve_producer`
  ladder, surface it; do not add a rollup-specific resolution arm") **and the owner instruction**
  ("any anchor movement or over-catch: STOP and report"), this is surfaced, not worked around.
- **The fix is a resolver enhancement, not a rollup hack:** teach cross-part `child.attr` resolution
  to follow each child part usage's redefinition to its per-instance channel (or reject the
  qualifier-drop), so `X.capital_cost` reaches `X`'s own cost channel. This is a substantial,
  separately-scoped change to `producer_resolution` / the aggregation term builder
  (`_build_agg_input_source`, `graph_builder.py:1403`) that the design under-scoped. It must land —
  and the byte-identity corpus must stay green — before Phase 3 can produce correct anchors.

### Phase-2 completeness check — refined and validated as a precise diagnostic

The check now flags `LEAF_NAME_GUESS` only for a **qualified** reference (a dropped scope qualifier);
a bare unique name match (`agg_localterm_probe`'s `markup`) is exempt — it is the intended producer
resolved by its only handle. Corpus scan: of 36 snapshot fixtures, exactly **one** trips —
`spec_chain_twolevel`'s `driver.maintenance_rate`, its own documented WI-015 gap — plus the
stellarator's 13. Zero false positives. **Not wired as a hard generation gate:** `spec_chain_twolevel`'s
trip is a corpus-accepted incompleteness, so fail-closing would need that genuine gap (and the
stellarator's) resolved first — which is exactly the blocking finding's resolver work. The check
stands as the precise diagnostic that proves the property and localizes the defect.

## Phase 3 — stellarator cutover: BLOCKED

Cannot proceed. The stellarator cannot generate producer-complete, correct-numeric public output
until the cross-part `child.attr` resolution above is fixed. Restoring the canonical formulas and
recapturing would yield collapsed aggregations (wrong anchors) — a STOP. Deferred pending the
resolver enhancement. When unblocked: restore formulas → recapture (v5) → public gen (zero offenders,
completeness-clean) → runner single-pass cutover → six anchors EXACT + five verdicts → delete bridge
+ `run_stellaris` glue-2 + `handshake_1costingfe.py` glue + DEMO NOTE conversions → WI-027 amendment.

- **Phase 0 snapshot capture** — `two_same_leaf_producers` capture also deferred to that pass.
- **Two-level fixture** `crosspart_rollup_twolevel/` — authored; classifies EXPOSE_COMPUTED (its
  plain child attrs don't locally redefine like the stellarator), so A7 was proven on the real
  stellarator instead. Retained as documentation of the shape; a licensed capture + child-redef
  variant is follow-on.

---

## CANDIDATE_REVs

- **sysml-codegen:** _(recorded at commit — see git log on `constraint-exec-epic`)_
- **agentic-mbse:** unchanged `4c18d61` (no coordinated change in Phases 0/2).
- **stellarator:** unchanged at `43a1d405` (Gate B filing commit; Phase 3 not yet started).
