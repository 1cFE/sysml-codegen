# Spec: Resolution Matcher Fixes & Warning Reconciliation (SC-8)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** HIGH
**Branch:** upstream-findings-epic
**Epic Item:** UPSTREAM-FINDINGS Item 7

---

## Problem

The codegen pipeline emits "Registry unresolved" WARNING lines on clean fixture
models, and the same warning text hides a real runtime failure. Today a reader
cannot tell benign noise from a genuine break — the warnings are worthless as a
signal.

Three things are actually wrong, and they compound:

1. **Two matcher bugs cause benign first-pass misses.** Bindings that *should*
   resolve don't, so they fall through to a warning-and-fallback path and get
   misclassified.
   - The REFERENCE path converts a SysML qualified name with a bare
     `::`→`__` swap (`sysml_to_python_qualified_name`, `qualified_names.py:103`)
     — no per-segment sanitize. A quoted-segment QN
     (`Lib::'Magnet Part'::attr`) becomes `Lib__'Magnet Part'__attr`, which
     never matches the sanitized design-attribute QN (`Lib__Magnet_Part__attr`).
     The matching FORMULA registry key is registered *raw* too
     (`output_registry_builder.py:130`) — a deliberate temporary state that
     Item 5 handed to this item to flip in lockstep.
   - Design attributes owned by a part **def** extract with `parent_part=''`
     (`get_parent_part_name` returns empty for def owners), while the binding
     carries the part **usage** name. The dotted-path match requires
     `attr.parent_part == parent_part` (`dependency_backtracker.py:650`), so a
     def-owned design attribute never matches its binding.

2. **The fallback that papers over the misses is lossy.** When the matchers
   miss, the binding drops to a Step-4 fallback entry point. This
   misclassifies the ADR-001 kind (`USAGE_LITERAL` instead of
   `DESIGN_ATTRIBUTE`, wrong metadata) and defeats Step-3 dedup: two calcs that
   read one design attribute mint two JSON keys instead of sharing one.

3. **The same warning text masks a real dangling input.** In the committed
   catf_mfe fixture, `cryo_load.magnet_volume` binds to
   `catf_radial_build.magnet_volume_total`, which is itself
   `= tf_coil.volume` — a nested-part EXPOSE the pipeline cannot yet wire
   (cross-part; Items 9–11). The input falls to a Step-4 fallback entry point
   whose synthetic key is never minted in `magnets_params.json`. The generated
   pipeline references a params key that does not exist — a runtime failure,
   wearing the same "Registry unresolved" text as the benign cases. Blanket
   demotion of the warnings would bury it.

Net effect: warnings that fire on healthy models and go quiet on a broken one.
This item makes warnings mean something — benign misses resolve at the right
stage, and a genuinely uncovered input fails loudly and precisely.

## Success Criteria

- [ ] Clean fixture models (solar_battery, chain_spike, attr_expr_probe, and a
      corrected catf_mfe path) generate with **zero WARNING lines**.
- [ ] The two matcher fixes resolve the benign first-pass misses: bindings that
      should resolve do resolve, at the correct stage, with the correct ADR-001
      classification (`DESIGN_ATTRIBUTE`, not `USAGE_LITERAL`).
- [ ] All six lockstep sites flip to per-segment sanitize in one change; the
      implement-time grep for leftover bare-QN swaps / raw `sysml_qn_lookup`
      keys comes back clean.
- [ ] Step-3 dedup returns: two calcs reading one design attribute share a
      single entry-point key.
- [ ] Any module input referencing a `*_params.X` key with **no matching key in
      any parameter group** is a hard, precise error (new V11 diagnostic) — and
      it catches the catf_mfe `magnet_volume` dangling input specifically.
- [ ] A **seeded unresolved-binding fixture** proves the coverage check fires
      independently of catf_mfe.
- [ ] Per-binding Step-4 fallback lines are DEBUG, not WARNING; a single
      post-assembly reconciliation summary reports entry points that fell
      through **and still lack a value**.
- [ ] The repetitive alias-collision warnings (25 of catf_mfe's 29 lines)
      collapse to one count-summary line.
- [ ] Reclassification and dedup churn is reviewed against the procedure below
      and captured in regenerated baselines and this item's release notes, with
      a written enumeration of which entry points moved, which keys collapsed,
      **and which default values changed** (reclassification switches the
      default-value source, so keys can survive with different values).

## Known Requirements

### Matcher fixes (behavioral)

- **[HARD]** The REFERENCE-path QN conversion in `_resolve_to_design_attribute`
  (`dependency_backtracker.py:660`) must sanitize per segment (reuse Item 5's
  `sanitize_qualified_name`, `core/qualified_names.py:108`), not swap
  separators. Forced by the naming contract (REQ-NC-06/08): the comparison
  target is already per-segment sanitized.
- **[HARD]** The FORMULA sysml-QN lockstep flip — **six sites, one atomic
  change.** Item 5 left the FORMULA sysml-QN key registered **raw**, and every
  consumer and twin still uses raw keys / bare separator swaps. All six flip to
  per-segment sanitize (`sanitize_qualified_name`) together — raw→raw becomes
  sanitized→sanitized atomically — or the FORMULA REFERENCE match breaks
  partway. The set:
  1. `output_registry_builder.py:130` — registration
     (`f"{owning_part_qualified_name}::{ca.name}"`, raw).
  2. `dependency_backtracker.py:595` — `sysml_qn_lookup(SysMLQN(source_path))`,
     raw key (primary REFERENCE consumer).
  3. `dependency_backtracker.py:660` — `_resolve_to_design_attribute`
     `sysml_to_python_qualified_name` bare swap (also Item 5's REFERENCE-path
     bug above; same flip).
  4. `pipeline_builder.py:70` — `_remove_formula_from_design_attrs`
     FORMULA-twin match set, bare swap.
  5. `input_resolver.py:120` — `sysml_qn_lookup(SysMLQN(ref))`, the **second**
     raw-key consumer of the same registry (missing from Item 5's close-out
     list; would silently break if not flipped).
  6. `parameter_groups.py:439` — `_find_source_file` bare-swap twin.
- **[HARD]** Grep-based completeness check at implement time. After the flip,
  a scan for any remaining bare-QN separator swap (`sysml_to_python_qualified_name`
  on a QN destined for comparison) or any raw `sysml_qn_lookup(SysMLQN(...))` key
  is a **stop** — a leftover raw site silently re-breaks the FORMULA REFERENCE
  match on quoted owners. (Item 5 close-out §"Item 7 lockstep obligation"
  enumerated four of these six; this item found the other two.)
- **[HARD]** Design attributes owned by a part **def** (empty `parent_part`)
  must match their bindings. The binding carries the part-usage name; the design
  attribute carries a full sanitized QN and no `parent_part`. Matching must be
  usage-name-aware or QN-suffix-based (exact mechanism deferred to design).
- **[INFERRED]** Both matcher fixes are behavioral: entry points reclassify
  (`USAGE_LITERAL` → `DESIGN_ATTRIBUTE`) and Step-3 dedup collapses shared keys.
  Baselines and params-JSON key sets will churn. This churn is *intended output*
  and must be reviewed as such, not suppressed.

### Warning reconciliation

- **[HARD]** The per-binding Step-4 fallback line
  (`dependency_backtracker.py:554`, "Registry unresolved: ...") demotes to
  DEBUG. It fires per binding and is the primary source of benign noise.
- **[HARD]** After assembly, a single reconciliation summary reports the entry
  points that fell through to the Step-4 fallback **and still lack a value** —
  the count and the specific offenders in one place, not scattered per-binding
  lines. It logs at **WARNING** when non-empty. The epic requires the cross-part
  unresolved cases to stay loud until Items 9–10 land: V11 covers *uncovered
  params keys* (hard error), the summary covers *fell-through-and-valueless*
  entries (loud warning) — both are loud, neither is demoted to INFO. Only the
  benign per-binding Step-4 line demotes to DEBUG.
- **[NEED]** The repetitive alias-collision warnings (`OutputRegistry alias
  collision`, `output_registry.py:112`, first-wins during Phase 1a) are
  aggregated into a single count-summary line rather than one line per colliding
  key.

### Params-coverage check — two-layer (collector + strict enforcement)

- **[HARD]** The check is **two layers**, so the same logic can both enumerate
  violations for a test and hard-fail generation:
  1. **Collector** — a pure function that returns the precise violation list:
     each `(module input → missing params key)` where a module input's entry
     point references a parameter-group key that no parameter group provides.
     Returns the list (possibly empty); raises nothing. Modeled on the
     traversal in `_validate_channel_references` (`graph_builder.py:612`), which
     does the analogous check for `module_output` producer channels.
  2. **Strict enforcement** — raises the V11 diagnostic on any non-empty
     violation list. The error names the module, the input, and the missing key.
- **[HARD]** The CLI / generation boundary is **always strict** — it calls the
  collector and raises V11 on any violation. There is **no escape-hatch flag** on
  the CLI surface (no `--allow-uncovered` or equivalent). A genuinely uncovered
  input fails generation, period.
- **[INFERRED]** Enforcement lives at the **generation boundary** (once, where
  the graph and derived parameter groups both exist), not inside
  `build_computation_graph`. It is a cross-artifact invariant (graph entry
  points vs generated param JSONs), semantically distinct from
  `_validate_channel_references`' graph-internal producer-channel invariant.
  Conformance tests that only build the graph call the **collector** and assert
  on the returned list — they never trip strict enforcement. This is what keeps
  catf_mfe's coverage green (see below).

### catf_mfe dangling input — decision: **xfail, do not alter the fixture**

- **[HARD]** The check must fire on the catf_mfe `magnet_volume` input (research
  §SC-8 fact 3). That input is `magnet_volume_total = tf_coil.volume`, a
  nested-part EXPOSE the fixture author explicitly intended as value propagation
  ("valid EXPOSE patterns", `radial_build.sysml:581`). Item 7 does not wire
  cross-part references — that is Items 9–11.
- **Decision:** pin the gap with the **collector**, narrow-xfail only the
  end-to-end expectation. **Do not** change the fixture model. Prove the check
  works with a separate seeded minimal fixture.
  - catf_mfe conformance tests call the **collector** and assert the violation
    list is **exactly `[cryo_load.magnet_volume]`** — this keeps all 42-module
    coverage green while precisely pinning the known gap. If the list grows or
    shrinks unexpectedly, those tests fail loudly.
  - Only the single "catf_mfe generates cleanly end-to-end" expectation gets the
    narrow treatment — an `xfail` (or an inverted assertion that generation
    raises V11 on exactly this input), with a precise reason tracked to
    Items 9–11.
  - Items 9–11 flip that one end-to-end expectation back to passing when they
    wire the `tf_coil.volume` cross-part shape; the collector assertion then
    updates from `[cryo_load.magnet_volume]` to `[]`.
- **Rationale:**
  - Rewriting `= tf_coil.volume` to a literal would falsify a real modeling
    shape and delete a test case Items 9–11 exist to satisfy.
  - The check firing on catf_mfe is the point — it proves the check catches a
    real dangling input (research's own argument for why SC-8 must not be fixed
    by demotion). Pinning the exact violation list states the truth: known
    cross-part gap, correctly flagged, tracked — and it stays a *green*
    assertion, not a suppressed test.
  - Enforcement at the generation boundary (above) means only the E2E generate
    path trips strict V11; the `computation_graph.json` baseline comparison and
    every collector-based test stay green.

### Behavioral-review procedure (required by R1/R2/R3)

Because this item's baseline churn is *behavioral* (unlike Items 1–6's
ordering/display churn), the diff review is a first-class deliverable, not a
rubber stamp. The implement/audit stages must produce, and the release notes
must contain, a written enumeration of:

1. **Entry points that reclassified** — every EP that moved `USAGE_LITERAL` →
   `DESIGN_ATTRIBUTE` (or otherwise changed ADR-001 kind/metadata), by name.
2. **Keys that collapsed** — every pair/group of params-JSON keys that Step-3
   dedup merged into one shared key, before → after.
3. **Params-JSON shape and values after** — for each affected model, both the
   key set *and the default values*, now vs. the committed baseline.
   Reclassification does not just relayout keys — it switches the
   **default-value source** (a `USAGE_LITERAL` carries the usage-site literal; a
   `DESIGN_ATTRIBUTE` carries the design attribute's default). A key can survive
   with a *different value*. The review and release notes must diff values at the
   key level, before → after, not just the key layout — a silent value change is
   the exact class of regression this behavioral churn could hide.

Each of the three must be reviewed deliberately (the diff is expected to be
non-empty and *correct*), captured in regenerated baselines via the capture
scripts (R3 — never hand-edited), and enumerated in the release notes.

## Non-Goals

- Resolving the cross-part unresolved cases (`tf_coil.volume` and its kind) —
  Items 9–11. The coverage check keeps them loud in the meantime.
- Constraint execution, alias emission, EXPOSE_COMPUTED — unrelated backlog.
- Changing channel-name (PQN) derivation — already sanitized (Item 5).
- Altering the catf_mfe fixture model (decided above).

## Open Questions / Deferred to design

- **Exact def-owned design-attribute match mechanism** — usage-name-aware match
  vs. QN-suffix match vs. a combined rule. The requirement is that def-owned
  design attributes (empty `parent_part`) match their bindings without
  false-matching sibling attributes. Design picks the mechanism and proves it
  doesn't over-match.
- **Coverage-check enforcement site** — the two-layer shape is decided
  (collector + always-strict generation boundary, no CLI escape hatch). Design
  confirms the exact function/site the strict enforcement hangs off, and that
  collector-only conformance tests never trip it.
- **Reconciliation-summary content** — the exact predicate for "fell through
  AND still lacks a value" (level is decided: WARNING when non-empty).
- **Seeded-fixture shape** — the minimal model that produces one uncovered
  `*_params.X` input to exercise V11. Design specifies it; it must be a real
  SysML fixture (R1 — no mocks).
- **Baseline sequencing vs. Item 6** — Item 6 (expression fidelity) regenerates
  a large baseline set concurrently. This item's files
  (`dependency_backtracker`, `output_registry_builder`, `parameter_groups`) do
  not overlap Item 6's (`expression_utils`), but the committed baselines will
  churn under Item 6. Sequence this item's baseline expectations against
  whatever is committed when implement runs — do not assume today's baseline
  bytes.

## Diagnostics & Requirement Numbering

Confirmed free at spec time (verify again at design):

- **Diagnostic V11** — params-coverage hard error (V1–V10 used; V11 free, Item 5
  did not consume it). Follows the V-pattern (modeling-assumptions "Validation
  Rules"): names the module, input, and missing key, and states the fix.
- **REQ families / next free numbers:**
  - `REQ-BT-09`, `REQ-BT-10` — the two matcher fixes (backtracker; doc 11,
    doc 24). Revises/extends REQ-BT-08's dispatch description.
  - `REQ-OR-09` — FORMULA sysml-QN registered sanitized (output registry;
    doc 10).
  - `REQ-PGD-08` — def-owned design-attribute matching (parameter group
    deriver; doc 17) — confirm this is the right owner vs. backtracker at design.
  - `REQ-GA-08` — params-coverage check, two-layer collector + strict
    enforcement (graph assembly / generation boundary; doc 07), sibling to
    REQ-GA-03 (`_validate_channel_references`). (GA-04 is taken.)
  - Reconciliation summary + count-summary: fold into the REQ-BT or a
    diagnostics REQ at design; not a new family.

Docs to update (R1 — docs move with code): 11 (analysis-backtracker), 24
(dual-resolution-architecture), 10 (output-registry), 17
(parameter-group-deriver), 07 (graph-assembly), and modeling-assumptions
"Validation Rules" (V11) + the SC-8 behavioral note. Verification-matrix rows
for each new REQ.

## agentic-mbse Impact

Expected: **minor or none** (recorded for Item 12; not built here).

- The matcher fixes and coverage check are internal resolution behavior — they
  change what codegen *accepts and reconciles*, not what a model should look
  like, so MODELING_GUIDE / sysml-conventions likely need no change.
- Candidate validation check (Level-6): a design-attribute binding whose
  `*_params` key is never covered by a parameter group — the model-side mirror
  of V11. Record as an Item-12 candidate; V11 in codegen is the hard backstop
  meanwhile.
- Confirm at close-out whether the def-owned design-attribute shape (empty
  `parent_part`) is worth a guidance note ("part-def-owned design attributes are
  supported"), or whether it is purely a codegen matcher concern.

Final "agentic-mbse impact" list lands in this item's close-out per R2.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 7 + R1/R2/R3)
- **Required Reading:**
  - `.project/research/20260705_upstream-findings-deep-research.md` (§SC-8 —
    authoritative reframe)
  - `.project/active/identifier-sanitization/close-out.md` (Item 5 — the
    lockstep obligation this item executes)
  - `docs/architecture/modeling-assumptions.md` (V-pattern; supported subset)
  - `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md`
    (findings register)
- **Design:** `.project/active/warning-reconciliation/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`. Design must nail the
def-owned match mechanism, the coverage-check placement, and the seeded-fixture
shape, then hand a plan that sequences baseline regen against Item 6's committed
state.
