# Spec: Identifier Sanitization (SC-4, + SC-11 riders)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** MEDIUM
**Branch:** upstream-findings-epic
**Epic:** UPSTREAM-FINDINGS — Item 5

---

## Problem

A quoted SysML name (`calc def 'Margin Calc'`) is legal and supported — the naming
contract mandates it (REQ-NC-06), `sanitize_name`'s docstring anticipates it, and the
fixture corpus uses quoted names pervasively (`'Fusion Power Plant'`, `'Racking &
Mounting'` — the `&` is only expressible quoted). But quoted **calc def** names produce
non-importable Python today. The gap is real and reproduced at HEAD on
`tests/fixtures/alias_agg_probe/`: `'margin calc'.py` filenames, `class 'Margin
Calc'Input`, and a registry importing a sanitized class name the module file never
declares.

The root cause is a split at extraction that the derivation layer never closes:

- `name` is sanitized at capture (`extractor.py:133` / `:212`), but `qualified_name`
  is stored raw.
- The ADR-003 derivation layer is pure string transforms with **no** sanitize:
  `ModuleType.from_sysml` and `PythonModulePath.from_sysml`
  (`identifier_types.py:104-108, 140-143`) build the registry class name and the module
  file path straight from the raw qualified name.
- A latent second leak on the FORMULA path: the computed-attribute `module_eqn`/channel
  is derived via `sysml_to_python_qualified_name` (`qualified_names.py:103-105`), a bare
  `::`→`__` replace with no per-segment sanitize. A FORMULA attribute on a quoted-named
  owner leaks quotes into module and channel names.

Channel names (PQN) are already clean — they are built per-segment-sanitized — so the
defect is confined to the class-name / module-path / FORMULA-channel derivation.

This survived 1,500+ conformance tests because **no baseline model has a quoted calc
def** — the quoted fixtures only feed hierarchy/backtracker unit tests and never flow
through registry/module generation. fusion-tea papers over the whole class of defect
with a downstream `sanitize_names.py` post-processor.

## Success Criteria

- [x] `alias_agg_probe` generates a full registry + module package that `ast.parse`
      accepts, and every name the registry imports matches a class the corresponding
      module file declares. The research reproduction (quoted-name CalcUsage leak) is gone.
- [x] The FORMULA channel/module_eqn path produces sanitized identifiers for a
      quoted-named owner, **proven by a real fixture** — a minimal quoted-owner FORMULA
      computed-attribute fixture (new fixture + committed extraction snapshot, live
      capture) whose generated FORMULA channel is *produced and consumed under the
      identical name* (the wire resolves, not merely `ast.parse`s). R1: no new behavior
      without a real fixture; the leak was only code-inferred until now.
- [x] **No EXISTING snapshot or baseline changes.** All 4 pipeline baselines and all 11
      committed extraction snapshots are byte-identical — a per-segment sanitize is a
      no-op on every model without a quoted calc def, which is all of them.
      `alias_agg_probe`'s own committed snapshot holds raw quoted QNs and stays
      byte-identical under the derivation-layer choice — that is load-bearing evidence for
      the direction, not a footnote. The new FORMULA fixture is **additive** and does not
      touch the invariance claim.
- [x] Silent output-file overwrites fail fast across **all three write key spaces** —
      modules, stencils, and schemas — each with a clear message naming the colliding
      source names and the shared path. See the duplicate-path requirement for why one
      check per key space is required. (Modules + stencils share one path key; schemas a
      separate `calc_def_name.lower()` key — two checks, three write paths.)
- [x] SC-11 is formally closed as "confirmed intended, documented, tested," recorded in
      the Item 5 close-out.
- [x] agentic-mbse impact recorded, including the fusion-tea `sanitize_names.py`
      retirement coordination note and the Item 7 registration-key lockstep obligation.

## Known Requirements

### The sanitization fix — derivation layer, not source

- **[HARD]** Identifier derivation SHALL sanitize each qualified-name segment before it
  becomes a Python class name, module file path, or FORMULA module_eqn/channel.
  Concretely: `ModuleType.from_sysml` and `PythonModulePath.from_sysml`
  (`identifier_types.py`) sanitize the element name and package segments; the FORMULA
  name-derivation sites sanitize per-segment. **Candidate REQ-NC-08** (doc 15).

- **[HARD]** The fix goes in the **derivation layer**, not at the extraction source —
  and the reason is **item-boundary discipline, not permanent superiority.** Sanitizing
  the source is the same *direction*, not a worse one: completing it means flipping both
  sides of the FORMULA registry key (registration at `output_registry_builder.py:130`
  *and* the lookups at `dependency_backtracker.py:595/:660` and `parameter_groups.py:439`)
  from raw to sanitized together. Those lookups are exactly the matching sites Item 7
  (SC-8) owns. So Item 5 does the **name-derivation slice now**, and the both-sides key
  sanitization is **deferred to Item 7**, not rejected. See *The source-vs-derivation
  decision* below. The snapshot-re-capture savings are a genuine but *secondary* benefit —
  Item 2 made capture cheap, so it is not load-bearing.

- **[HARD]** The FORMULA `module_eqn` path MUST be covered (epic scope item 1). The
  **name-derivation** uses of `sysml_to_python_qualified_name` — the ones Item 5
  sanitizes — are: `output_registry_builder.py:124` (channel value),
  `graph_builder.py:745/789/818` (module_eqn). These get the per-segment-sanitizing
  treatment via the new helper.

- **[HARD]** Item 5 MUST NOT change any QN-**matching** site. Three uses of
  `sysml_to_python_qualified_name` build a set/value that is later *matched* rather than
  emitted, and all three stay untouched:
  - `dependency_backtracker.py:660` — REFERENCE→DesignAttribute compare (the epic's "line
    663").
  - `parameter_groups.py:439` — source-path match.
  - `pipeline_builder.py:70` — builds `formula_qns` and uses it as a *match set* at
    `:81` (`a.qualified_name not in formula_qns`) to strip a FORMULA attribute's
    design-attribute twin. `a.qualified_name` is per-segment sanitized; the set is
    raw-replaced, so for a quoted FORMULA owner they mismatch and the twin is *not*
    removed (a latent false entry point). Sanitizing `:70` would fix that — a real
    behavioral change for quoted FORMULA owners — so it is **Item 7's**, not Item 5's.

  The precise invariance claim is therefore: **no change on existing (unquoted) models;
  a latent correctness fix for quoted FORMULA owners at the match sites is deferred to
  Item 7.** (Not "zero resolution behavior change" — that overclaims.)

- **[HARD · Item 7 handoff]** `output_registry_builder.py:130` staying raw is a
  **temporary state, not an invariant.** When Item 7 sanitizes the REFERENCE lookup at
  `:595` (reusing this item's helper), it MUST flip the `:130` registration to sanitized
  **in lockstep** — raw-to-raw becomes sanitized-to-sanitized atomically — or the FORMULA
  REFERENCE match breaks (sanitized lookup vs. raw key). This obligation is recorded here
  and in the agentic-mbse/coordination section so Item 7's spec author finds it before
  implementation, not mid-flight.

- **[INFERRED]** The mechanism is a new shared helper, `sanitize_qualified_name(qn)` =
  split on `::`, `sanitize_name` each segment, join with `__`. Applied only at the four
  name-derivation sites above. `sysml_to_python_qualified_name` itself is **left
  unchanged** so the matching sites keep their current (raw) behavior until Item 7 owns
  them. This same helper is the "shared sanitized-QN matching helper" Item 7 depends on
  (epic dependency graph: Item 7 → Item 5) — Item 7 reuses it at the matching sites *and*
  at `:130`. Final helper name/location firms at design.

- **[INFERRED]** The `graph_builder.py:267-275` ad-hoc EXPOSE_PURE normalization (split
  `::`, sanitize each, join `__`) becomes redundant once the helper exists — collapse it
  to a call of the helper, or leave it and note the duplication for a follow-up. Design
  call.

### Fail-fast duplicate-output-path check

- **[HARD]** When two distinct SysML names sanitize to one output file, generation SHALL
  raise a clear, actionable error naming both source names and the shared path — never a
  silent overwrite. The overwrite hazard spans **three write paths in two key spaces**,
  and the check MUST cover all three (one collision check per key space):
  - **Modules** — `modules_dir / python_path.full_path`, write at `cli/__init__.py:223`.
    Keyed by the usage EQN's lowercased element name (`python_path.filename`).
  - **Stencils** — `{python_path.filename}_impl.py`, writes at `:271` / `:285` / `:299`.
    **Same filename key as modules** — a module collision implies a stencil collision, so
    the module-key check covers both; verify at design that no stencil path escapes it.
  - **Schemas** — `schemas_dir / f"{module.calc_def_name.lower()}_output.py"`, write at
    `:185`. **A different key space** — keyed by `calc_def_name`, not the usage EQN. Two
    calc defs whose names sanitize to one lowercased name (`'Margin Calc'` and
    `'margin calc'`) collide on `margin_calc_output.py` *even if their module paths
    differ*. A module-path-only pass would miss this entirely.

  A single pre-generation pass over module `full_path`s (the earlier draft's proposal)
  is insufficient — it must also detect the `calc_def_name.lower()` schema collision.
  Precedent: the SC-2 zero-output fail-fast and `_validate_channel_references`.
  **Candidate REQ-NC-09** (doc 15) or a generation-layer REQ; firm at design. If
  expressed as a model-validation "V" rule, it is **V11** (V8 landed with Item 3;
  V9/V10 reserved by Item 4) — but it is more naturally a generation-time invariant than
  an extraction V-rule.

### Fixtures & conformance tests

- **[HARD]** `alias_agg_probe` conformance test: drive it through **full registry +
  module generation** (the path the fixture has never taken) and assert (1) every
  generated file `ast.parse`s; (2) each class name the registry imports is declared by
  the module file it imports from. This locks the CalcUsage class-name / module-path leak
  (`ModuleType.from_sysml` / `PythonModulePath.from_sysml`). Real fixture, no mocks (R1).

- **[HARD]** New quoted-owner FORMULA fixture: a minimal model with a FORMULA
  computed-attribute on a quoted-named part (no existing fixture carries a FORMULA
  classification on a quoted owner — `grep -l FORMULA tests/fixtures/*/extraction_snapshot.json`
  is empty, and `alias_agg_probe` has `computed_attributes: []`). Live extraction capture
  produces a **new committed snapshot** (additive — license window is open, Item 2 made
  capture cheap). Its conformance test asserts the generated FORMULA channel is
  **produced and consumed under the identical name** — the wire resolves. This matters
  because the channel is derived two ways that only coincide when the helper is applied
  consistently: `output_registry_builder.py:124-126` builds `module_eqn` from
  `ca.python_name`, while `graph_builder.py:745` builds it from raw `ca.name` through
  `sysml_to_python_qualified_name`. A missed derivation site yields a
  "sanitized-but-mismatched" wire that `ast.parse` + import-name checks alone would not
  catch. This fixture is the R1 lock for SC #2.

### SC-11 riders (scope call — see Open Questions)

- **[NEED]** SC-11 (`_resolve_class_name_collisions`, `generation/registry.py:60-129`)
  is closed as-is: it is a first-class design decision with rationale (doc 20:29-34),
  REQ-REG-03/04/07 (PASS), direct conformance tests, and a checked-in aliased baseline.
  The close-out records this. **Recommended rider IN scope:** the post-alias uniqueness
  re-check — the alias scheme uses only the parent segment (`registry.py:103-108, 115`),
  so two `pump` scopes under different grandparents still collide silently. Turn that
  residual hole into a fail-fast, matching this item's duplicate-path theme. **Candidate
  REQ-REG-08** (doc 20).

  - **[HARD] Precondition (plan-phase task):** before making it a fail-fast, statically
    verify that **no committed fixture/baseline hits the grandparent-collision case**
    (two same-named scopes under different grandparents). If one does, a hard fail-fast
    would turn a currently-generating model into an error and break the "no existing
    baseline changes" criterion. In that case the re-check lands as **WARN first** and the
    fail-fast defers to a follow-up. Record this static check as an explicit plan phase.

  **Recommended rider deferred:** the AST-based import rewrite (today substring-based,
  first-match break) — a larger change with baseline-churn risk and no failing fixture;
  record as a follow-up.

## Non-Goals

- **Banning quoted names.** Contradicts fixtures, docs, and REQ-NC-06.
- **Channel-name (PQN) changes.** The PQN path is already per-segment-sanitized —
  verified, not touched.
- **The QN-matching sites** (`dependency_backtracker.py:660`, `parameter_groups.py:439`,
  `pipeline_builder.py:70`) and the REFERENCE-path / FORMULA-twin-stripping resolution
  behavior — Item 7 (SC-8) owns these, including the lockstep flip of
  `output_registry_builder.py:130`.
- **Source-level extraction sanitization** and any **re-capture of existing snapshots** —
  avoided by the derivation-layer choice. (One *new* FORMULA fixture is captured live and
  committed additively — that is a fixture addition, not a re-capture of the 11 existing
  snapshots.)
- **The SC-11 AST import rewrite** (recorded as a follow-up, not built here).
- **Fixing fusion-tea's `sanitize_names.py`** — flagged for their coordinated
  retirement, not changed by us.

## Open Questions / Deferred to design

- **Helper vs in-place edit of `sysml_to_python_qualified_name`.** The spec recommends a
  *new* `sanitize_qualified_name` helper applied only at name-derivation sites, leaving
  `sysml_to_python_qualified_name` untouched for Item 7. The alternative — fix
  `sysml_to_python_qualified_name` in place (per-segment sanitize, covering all uses) —
  is baseline-safe (no baseline has quoted names) and would advance Item 7's REFERENCE
  fix for free, but it silently does Item 7's behavioral work at
  `dependency_backtracker.py:660` and blurs the item boundary. Recommendation: the helper.
  Confirm at design.

- **SC-11 post-alias uniqueness re-check** (resolved to IN, conditionally): lands as a
  fail-fast *if* the plan-phase static check confirms no committed baseline hits the
  grandparent-collision case; otherwise WARN-first with the fail-fast deferred. Open only
  in the sense that the precondition check decides WARN vs. FAIL — see the SC-11
  requirement.

- **Duplicate-path check: pre-pass vs write-time** (scope resolved: all three key spaces
  per the requirement). Remaining design call is only the *mechanism*: a pre-generation
  pass over all derived paths in both key spaces (module `full_path` + schema
  `calc_def_name.lower()`), or a write-time guard per site. Pre-pass gives a cleaner
  message listing all collisions up front; write-time is simpler but fails on the second
  write. Recommendation: pre-pass covering both key spaces.

- **REQ ID / doc-section final numbers.** Candidates: REQ-NC-08 (derivation sanitize),
  REQ-NC-09 (duplicate-path), REQ-REG-08 (SC-11 re-check). Firm against docs 15/20 at
  design; REQ-EXT-10..14 are taken by Item 3 — do not reuse.

---

## The source-vs-derivation decision (code evidence)

**Conclusion first:** Item 5 does the **name-derivation slice** — sanitize where
identifiers are *emitted*. The complete both-sides key sanitization (registration *and*
lookup) is **Item 7's**, deferred not rejected, because Item 7 owns the QN-matching
sites. This is item-boundary discipline. Source-sanitization is not a worse *direction* —
it is the same direction done all at once, which necessarily reaches into Item 7's
matching work. The three line numbers below are the mechanism behind that call.

The epic asked the spec to "decide source vs derivation-layer with code evidence,"
naming `dependency_backtracker.py:663` as the raw-QN comparison to check.

**The flagged site (663) is not the deciding one.** That REFERENCE→DesignAttribute
compare consumes `attr.qualified_name` (a `DesignAttributeData` field, already
per-segment sanitized via `build_element_qualified_name`, `parameter_groups.py:141`) and
a raw REFERENCE `source_path`. It does **not** consume `calc_def_qualified_name` or
`owning_part_qualified_name` — the fields source-sanitization would touch. So the flagged
site is untouched by source-sanitizing those fields; it is Item 7's REFERENCE-path bug,
independent of this choice.

**The deciding site is the FORMULA SysML-QN registry key.** At
`output_registry_builder.py:130` the FORMULA output registers under
`SysMLQN(f"{ca.owning_part_qualified_name}::{ca.name}")` — a **raw** key. The REFERENCE
lookup at `dependency_backtracker.py:595` queries `sysml_qn_lookup(SysMLQN(source_path))`
with a **raw** referent QN. Both sides raw → they match today (the *value*, the channel
name, still leaks quotes — the FORMULA latent leak Item 5 fixes at the derivation site).

- **Source-sanitize `owning_part_qualified_name` (do it "completely")** → the
  registration key at `:130` becomes sanitized. To keep the match, the lookup at `:595`
  (and the `:660` / `parameter_groups.py:439` matching sites) must be sanitized *in the
  same change*. Those are exactly the sites Item 7 owns. So "complete source
  sanitization" = Item 5 + Item 7 collapsed into one change. Splitting them the other way
  — sanitize `:130` but not `:595` — breaks the FORMULA REFERENCE match for quoted owners.
  Either way, source-sanitization forces the matching-site work into Item 5's boundary.

- **Derivation-layer sanitize (Item 5's slice)** → a new helper at the name-*emission*
  sites: identifier `from_sysml` methods, plus the FORMULA channel/module_eqn derivation
  (`output_registry_builder.py:124`, `graph_builder.py:745/789/818`). Leaves the `:130`
  registration key and every matching site raw → raw-to-raw match preserved, no coupling
  to Item 7, existing snapshots and baselines byte-identical. Item 7 later flips `:130`
  and the lookups to sanitized **atomically** (see the Item 7 handoff requirement).

This satisfies R1 in spirit: identifiers are derived once at the derivation layer and
looked up thereafter; the raw qualified name remains the extraction-boundary form (doc 15
§1 — SysML QN is the `::` form stored on `CalculationDefinitionData.qualified_name`), and
every emitted identifier is a pure function of it through the now-sanitizing derivation
layer.

---

## agentic-mbse impact

Recorded for Item 12 execution (R2); nothing urgent enough to implement inline.

- **Guidance (MODELING_GUIDE / sysml-conventions):** add "quoted names are fine —
  identifiers are derived." Modelers may use `'Fusion Power Plant'` freely; the generator
  sanitizes at derivation. No modeling change is required or requested.

- **Validation warning candidate:** two distinct SysML names that sanitize to the **same**
  Python identifier (e.g., `'margin calc'` and `'Margin Calc'`) — a Level-2/Level-6
  check candidate that warns before generation fails on the duplicate-path error. Filed
  as a candidate, not built here.

- **Item 7 coordination note (in-repo, must appear in the close-out):** Item 7 inherits
  an obligation from this item. When it sanitizes the REFERENCE lookup at
  `dependency_backtracker.py:595` (reusing this item's `sanitize_qualified_name` helper),
  it MUST flip the FORMULA registration key at `output_registry_builder.py:130` to
  sanitized **in the same change** — raw-to-raw becomes sanitized-to-sanitized atomically,
  or the FORMULA REFERENCE match breaks. The `:70` FORMULA-twin match set moves with it.
  This is the price of Item 5 taking only the derivation slice; record it so Item 7's
  spec author sees it before implementation.

- **fusion-tea coordination note (must appear in the close-out):** once this lands,
  `sanitize_names.py` in fusion-tea becomes dead code — flag it for **coordinated
  retirement**. Their post-processor's rules may differ subtly from `sanitize_name`, so
  retiring it can shift some downstream names; treat it as a one-time, reviewed name
  migration on their side, not a silent drop-in.

- **SC-11 close-out:** record SC-11 as "confirmed intended, documented, tested"
  (REQ-REG-03/04/07 PASS, conformance-tested, aliased baseline parseable). If the
  post-alias uniqueness re-check lands, note the residual grandparent-collision hole is
  now a fail-fast; the AST import-rewrite gap is filed as a follow-up.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` — Item 5; R1/R2/R3.
- **Required Reading (from the epic):**
  - `.project/research/20260705_upstream-findings-deep-research.md` — SC-4 (§137-147),
    SC-11 (§236-240), the name-form-mismatch family (§57-63), fixture blind spot (§67).
  - `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md` —
    findings register (SC-4, SC-11, `sanitize_names.py` workaround).
  - `docs/architecture/modeling-assumptions.md` — supported-subset contract, "compute
    once, look up thereafter" (§7).
- **Naming contract:** `docs/architecture/reference/15-naming-conventions.md`
  (REQ-NC-06); `docs/architecture/reference/20-module-registry-generation.md` (SC-11
  machinery, REQ-REG-03/04/07). Both get updated by this item.
- **Code touchpoints:**
  - **Change (name-emission):** `core/identifier_types.py` (`ModuleType.from_sysml`,
    `PythonModulePath.from_sysml`); `core/qualified_names.py` (`sanitize_name`, new
    `sanitize_qualified_name`); FORMULA channel/module_eqn derivation at
    `orchestration/output_registry_builder.py:124` and
    `resolution/graph_builder.py:745/789/818`.
  - **Do NOT change (match sites — Item 7):** `orchestration/output_registry_builder.py:130`
    (the FORMULA registration *key*, left raw — the same file's `:124` value gets
    sanitized while `:130` stays raw, and that pairing is deliberate; Item 7 flips `:130`
    in lockstep with `analysis/dependency_backtracker.py:595/:660`);
    `analysis/parameter_groups.py:439`; `orchestration/pipeline_builder.py:70`.
  - **Duplicate-path guard:** `cli/__init__.py` — modules `:223`, stencils `:271/:285/:299`,
    schemas `:185`.
  - **SC-11:** `generation/registry.py:60-129` (alias parent-segment scheme at
    `:103-108, 115`).
- **New fixture:** `tests/fixtures/{quoted-owner FORMULA}/` + committed
  `extraction_snapshot.json` (live capture).
- **Design:** `.project/active/identifier-sanitization/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_spec_review` (adversarial audit —
especially the source-vs-derivation reversal), then `/_my_design`.
