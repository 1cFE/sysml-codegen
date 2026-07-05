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

- [ ] `alias_agg_probe` generates a full registry + module package that `ast.parse`
      accepts, and every name the registry imports matches a class the corresponding
      module file declares. The research reproduction (quoted-name leak) is gone.
- [ ] The FORMULA channel/module_eqn path produces sanitized identifiers for a
      quoted-named owner (latent second leak closed).
- [ ] All 4 pipeline baselines and all 10 extraction snapshots are **byte-identical** —
      no baseline/snapshot has a quoted calc def, so a per-segment sanitize is a no-op on
      them.
- [ ] Two names that sanitize to the same output file path fail fast with a clear
      message naming both source names and the collided path — never a silent overwrite.
- [ ] SC-11 is formally closed as "confirmed intended, documented, tested," recorded in
      the Item 5 close-out.
- [ ] agentic-mbse impact recorded, including the fusion-tea `sanitize_names.py`
      retirement coordination note.

## Known Requirements

### The sanitization fix — derivation layer, not source

- **[HARD]** Identifier derivation SHALL sanitize each qualified-name segment before it
  becomes a Python class name, module file path, or FORMULA module_eqn/channel.
  Concretely: `ModuleType.from_sysml` and `PythonModulePath.from_sysml`
  (`identifier_types.py`) sanitize the element name and package segments; the FORMULA
  name-derivation sites sanitize per-segment. **Candidate REQ-NC-08** (doc 15).

- **[HARD]** The fix goes in the **derivation layer**, not at the extraction source.
  This reverses the epic's stated *primary* preference (source-sanitize
  `extractor.py` qualified-name capture + `owning_part_qualified_name` producers) and
  lands on its documented **spec-time fallback** — because the code evidence shows
  source-sanitization hits a raw-QN comparison. See *The source-vs-derivation decision*
  below for the evidence. Non-negotiable given that evidence; if design overturns it, the
  registry-key breakage below must be solved first.

- **[HARD]** The FORMULA `module_eqn` path MUST be covered (epic scope item 1). The
  name-derivation uses of `sysml_to_python_qualified_name` are:
  `output_registry_builder.py:124`, `graph_builder.py:745/789/818`,
  `pipeline_builder.py:70`. These get the per-segment-sanitizing treatment.

- **[HARD]** Item 5 MUST NOT change any QN-**matching** site. The two matching uses of
  `sysml_to_python_qualified_name` — `parameter_groups.py:439` and
  `dependency_backtracker.py:660` (the REFERENCE→DesignAttribute compare the epic flagged
  as "line 663") — belong to Item 7 (SC-8). Changing them is behavioral resolution
  change and is out of scope here. This keeps Item 5 a pure name-derivation change with
  zero resolution behavior change.

- **[INFERRED]** The mechanism is a new shared helper, `sanitize_qualified_name(qn)` =
  split on `::`, `sanitize_name` each segment, join with `__`. Applied only at the
  name-derivation sites above. `sysml_to_python_qualified_name` itself is **left
  unchanged** so the matching sites keep their current (raw) behavior until Item 7 owns
  them. This same helper is the "shared sanitized-QN matching helper" Item 7 depends on
  (epic dependency graph: Item 7 → Item 5) — Item 7 reuses it at the matching sites.
  Final helper name/location firms at design.

- **[INFERRED]** The `graph_builder.py:267-275` ad-hoc EXPOSE_PURE normalization (split
  `::`, sanitize each, join `__`) becomes redundant once the helper exists — collapse it
  to a call of the helper, or leave it and note the duplication for a follow-up. Design
  call.

### Fail-fast duplicate-output-path check

- **[HARD]** When two generated modules derive the same output file path (two distinct
  SysML names sanitizing to one lowercased filename), generation SHALL raise a clear,
  actionable error instead of silently overwriting. Today `cli/__init__.py:214`
  (`output_path.write_text(code)`) overwrites with no check. The message names both
  source qualified names and the collided path. Precedent: the SC-2 zero-output
  fail-fast and `_validate_channel_references`. **Candidate REQ-NC-09** (doc 15) or a
  generation-layer REQ; firm at design. Diagnostic numbering: if this is expressed as a
  model-validation "V" rule, it is **V11** (V8 landed with Item 3; V9/V10 reserved by
  Item 4) — but it is more naturally a generation-time invariant than an extraction V-rule.

### Conformance test

- **[HARD]** A conformance test drives `alias_agg_probe` through **full registry +
  module generation** (the path the fixture has never taken) and asserts: (1) every
  generated file `ast.parse`s; (2) each class name the registry imports is declared by
  the module file it imports from. Real fixture, no mocks (R1). This is the regression
  lock for the whole item.

### SC-11 riders (scope call — see Open Questions)

- **[NEED]** SC-11 (`_resolve_class_name_collisions`, `generation/registry.py:60-129`)
  is closed as-is: it is a first-class design decision with rationale (doc 20:29-34),
  REQ-REG-03/04/07 (PASS), direct conformance tests, and a checked-in aliased baseline.
  The close-out records this. **Recommended rider IN scope:** the post-alias uniqueness
  re-check (the alias scheme uses only the parent segment, so two `pump` scopes under
  different grandparents still collide silently) — turn that residual hole into a
  fail-fast, matching this item's duplicate-path theme. **Recommended rider deferred:**
  the AST-based import rewrite (today substring-based, first-match break) — a larger
  change with baseline-churn risk and no failing fixture; record as a follow-up.

## Non-Goals

- **Banning quoted names.** Contradicts fixtures, docs, and REQ-NC-06.
- **Channel-name (PQN) changes.** The PQN path is already per-segment-sanitized —
  verified, not touched.
- **The QN-matching sites** (`parameter_groups.py:439`, `dependency_backtracker.py:660`)
  and the REFERENCE-path resolution behavior — Item 7 (SC-8) owns these.
- **Source-level extraction sanitization** and any resulting extraction-snapshot
  re-capture — avoided by the derivation-layer choice.
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

- **SC-11 post-alias uniqueness re-check: in or deferred?** Recommended IN as a
  fail-fast (cheap, thematic). If design judges it out of the 1-day budget, defer with
  the AST rewrite. Deferral is lossless — it lands in the epic's SC-11 follow-up note.

- **Duplicate-path check granularity.** Detect the collision as a pre-generation pass
  over all derived `full_path`s (fail before writing anything), or at write time (fail on
  the second write). Pre-pass gives a cleaner message listing all collisions; write-time
  is simpler. Design call. Recommendation: pre-pass.

- **REQ ID / doc-section final numbers.** Candidates: REQ-NC-08 (derivation sanitize),
  REQ-NC-09 (duplicate-path), REQ-REG-08 (SC-11 re-check). Firm against docs 15/20 at
  design; REQ-EXT-10..14 are taken by Item 3 — do not reuse.

---

## The source-vs-derivation decision (code evidence)

The epic asked the spec to "decide source vs derivation-layer with code evidence,"
naming `dependency_backtracker.py:663` as the raw-QN comparison to check. The evidence
points to the **derivation layer** — the epic's documented fallback.

**The flagged site (663) is not the deciding one.** That REFERENCE→DesignAttribute
compare consumes `attr.qualified_name` (a `DesignAttributeData` field, already
per-segment sanitized via `build_element_qualified_name`, `parameter_groups.py:141`) and
a raw REFERENCE `source_path`. It does **not** consume `calc_def_qualified_name` or
`owning_part_qualified_name` — the fields source-sanitization would touch. So the flagged
site is untouched by source-sanitizing those fields; it is Item 7's REFERENCE-path bug,
independent of the sanitization-derivation choice.

**The deciding site is the FORMULA SysML-QN registry key.** At
`output_registry_builder.py:130` the FORMULA output registers under
`SysMLQN(f"{ca.owning_part_qualified_name}::{ca.name}")` — a **raw** key. The REFERENCE
lookup at `dependency_backtracker.py:595` queries `sysml_qn_lookup(SysMLQN(source_path))`
with a **raw** referent QN. Both sides raw → they match today (then the *value*, the
channel name, leaks quotes — the FORMULA latent leak).

- **Source-sanitize `owning_part_qualified_name`** → the registration key at line 130
  becomes sanitized while the lookup stays raw → **the FORMULA REFERENCE match breaks**
  for quoted owners. That is source-sanitization hitting a raw-QN comparison — exactly
  the epic's spec-time fallback trigger. It would also force extraction-snapshot
  re-capture and couple Item 5's correctness to Item 7's lookup fix.

- **Derivation-layer sanitize** (new helper at the name-derivation sites; identifier
  `from_sysml` methods) → fixes the CalcUsage class/filename leak **and** the FORMULA
  channel leak (`output_registry_builder.py:124` derives the channel; sanitize it there),
  while leaving the line-130 registration key raw → the raw-to-raw REFERENCE match is
  preserved. No snapshot re-capture. No coupling to Item 7. Baselines byte-identical.

This also satisfies R1 in spirit: identifiers are still derived once at the derivation
layer and looked up thereafter; the raw qualified name remains the extraction-boundary
form (as doc 15 §1 documents it — SysML QN is the `::` form stored on
`CalculationDefinitionData.qualified_name`), and every downstream identifier is a pure
function of it through the (now-sanitizing) derivation layer.

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
- **Code touchpoints:** `core/identifier_types.py` (`ModuleType.from_sysml`,
  `PythonModulePath.from_sysml`); `core/qualified_names.py` (`sanitize_name`, new
  `sanitize_qualified_name`); FORMULA derivation at `output_registry_builder.py:124`,
  `graph_builder.py:745/789/818`, `pipeline_builder.py:70`; duplicate-path guard at
  `cli/__init__.py:214`; SC-11 at `generation/registry.py:60-129`.
- **Design:** `.project/active/identifier-sanitization/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_spec_review` (adversarial audit —
especially the source-vs-derivation reversal), then `/_my_design`.
