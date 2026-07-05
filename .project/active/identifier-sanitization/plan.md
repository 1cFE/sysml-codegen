# Implementation Plan: Identifier Sanitization (SC-4 + SC-11 riders)

**Status:** Complete (implementation; awaiting audit)
**Created:** 2026-07-05
**Last Updated:** 2026-07-05
**Epic:** UPSTREAM-FINDINGS — Item 5 (1-day item)
**Branch:** upstream-findings-epic

## Source Documents
- **Spec:** `.project/active/identifier-sanitization/spec.md`
- **Design (authoritative; two review rounds applied):** `.project/active/identifier-sanitization/design.md` ← component details, bets, invariants, site-by-site appendix
- **Design review + resolutions:** `.project/active/identifier-sanitization/design-review.md`
- **Epic (R1/R3):** `.project/backlog/epic_upstream_findings.md` — Item 5

---

## Anchor re-verification (done at plan time, 2026-07-05, HEAD `93579e0`)

Items 3 and 4 landed since the design's first draft, so every line anchor was re-checked.
Result: **`cli/__init__.py` anchors have drifted materially — use the current numbers below,
and re-verify once more at implement time** (this file changes often).

| Site | Design says | **Current (verified HEAD `93579e0`)** |
|---|---|---|
| `sanitize_name` | `qualified_names.py:13` | **:13** ✓ |
| `sysml_to_python_qualified_name` | `qualified_names.py:103` | **:103** ✓ (helper lands beside it; `__all__` at **:124**) |
| `ModuleType.from_sysml` | `identifier_types.py:104-108` | **:104-108** ✓ (namespace `.lower()` **:106**, class_name **:107**) |
| `PythonModulePath.from_sysml` | `identifier_types.py:140-143` | **:140-143** ✓ (directory **:142**, filename `.lower()` **:143**) |
| FORMULA producer (channel value) | `output_registry_builder.py:124` | **:124-125** ✓ (`module_eqn = f"{part_qn_python}__{ca.python_name}"`) |
| FORMULA raw registration key (DO NOT TOUCH) | `output_registry_builder.py:130` | **:130** ✓; `key_f` ScopedKey **:136-137** |
| FORMULA consumer — resolution_map | `graph_builder.py:745` | **:744-746** ✓ (`sysml_qn = f"{owner}::{ca.name}"`; `module_eqn` **:745**) |
| FORMULA consumer — module identity | `graph_builder.py:789` | **:788-789** ✓ |
| `derive_module_type` (module_type) | `graph_builder.py:791` | **:791** ✓ |
| `part_eqn` | `graph_builder.py:818` | **:818** ✓ |
| EXPOSE_PURE ad-hoc (D3 collapse) | `graph_builder.py:271-275` | **:273-276** (join at **:275**) |
| FORMULA `PipelineModule(...)` (m3 raw-name provenance) | `graph_builder.py:~890-892` | **:879-892** ✓ (`calc_def_name=ca.name` **:891**, `calc_def_qualified_name=ca.owning_part_qualified_name` **:892**) |
| Schema write (`calc_def_name.lower()`) | `cli/__init__.py:185` | **:177** ⚠ drifted |
| Module write (`full_path`) | `cli/__init__.py:223` | **:215** ⚠ drifted |
| Stencil writes (`{filename}_impl.py`) | `cli/__init__.py:271/285/299` | **:258 / :260** ⚠ drifted |
| `_clear_output_directory` call | `cli/__init__.py:709` | **:712** (inside `if config.overwrite:` at **:710**); pre-pass inserts at **~:708**, after the graph-built log line **:707** |
| `_get_python_path` | — | **:149** |
| `_resolve_class_name_collisions` | `registry.py:60-129` | **:60-129** ✓ (group-by-name **:77-80**, parent segment **:103-108**, alias **:115-116**) |

**Fixture inventory (verified):** `grep -rl FORMULA tests/fixtures/*/extraction_snapshot.json`
is **empty** — no committed snapshot carries a FORMULA classification, so the new quoted-owner
FORMULA fixture is genuinely additive (SC #2 R1 lock). `alias_agg_probe` has
`computed_attributes: []` (`extraction_snapshot.json:517`) and has never flowed through
generation. There are **12** committed extraction snapshots now (the design's "11" predates
Items 3/4 fixtures — the invariance argument is unchanged; it is corpus-scoped, INV-1/INV-4).
Pipeline baselines live in `tests/fixtures/baseline_outputs` and `tests/fixtures/baseline_yaml`
(confirm exact count at implement). The license-free generation harness is
`tests/conformance/test_snapshot_generation.py` — `run_codegen` +
`build_pipeline_context_from_snapshot(snapshot_fixture(...))`, byte-diff via `_tree_diff` (`:51`).

---

## Implementation Strategy

**Phasing rationale.** Two ideas drive the order: *de-risk the invariance claim and the FORMULA
wire before writing production code*, and *keep the byte-identical suite green at every phase
boundary*. Phase 0 proves the two claims the whole direction rests on (INV-1 no-op; SC-11 gate)
with license-free static scans. Phase 1 proves the FORMULA wire fixture-first (red→green), because
that wire (B2/INV-5) is the design's explicit "de-risk first" item — the producer/consumer channel
coincidence is the single subtle thing. Phase 2 fixes the CalcUsage class-name/module-path leak
(the reproduced SC-4 bug) and locks it with the `alias_agg_probe` conformance test. Phase 3 adds
the two fail-fasts (duplicate-path, SC-11 re-check) — behavior-adjacent guards, safe once the
core fix is proven. Phase 4 is docs/matrix/close-out carry-through.

**Critical path:** Phase 0 (gate + no-op proof) → Phase 1 (helper + FORMULA wire, fixture-first)
→ Phase 2 (`from_sysml` sanitize + alias_agg_probe lock) → Phase 3 (fail-fasts) → Phase 4 (docs).

**First proof point:** Phase 1's red→green — the new same-part quoted-owner FORMULA fixture's
*resolved-channel == registered-canonical-channel* assertion fails on raw code (quoted owner →
producer `Owner__net_margin` vs consumer `Owner__'net margin'`, no resolution) and passes once the
helper + M1 leaf-from-`python_name` land. That single transition proves the wire is real, not
assumed.

**Overall validation:** every phase starts with a test; the invariance gate (full suite +
`_tree_diff` over all committed snapshots and all baselines == empty) runs at the end of Phases 1,
2, and 3; suite is green at every boundary.

**Key invariants to hold throughout** (see `design.md#required-invariants`): INV-1 (corpus-scoped
no-op), INV-2 (helper applied once at `::`→`__`), INV-3 (three match sites + `:130` byte-unchanged),
INV-4 (no existing snapshot/baseline changes), INV-5 (FORMULA produced channel == consumed channel).

---

## Phase 0: Static de-risk scans (no production code)

### Goal
Prove — by scanning committed artifacts, not by regex reasoning — the two claims the direction
rests on, before any code changes. License-free and fast. See `design.md#key-bets` (B1, B4) and
`design.md#required-invariants` (INV-1).

### Assumption Under Test
- **INV-1 / B1:** `sanitize_name` is the **identity** on every segment appearing in every committed
  extraction snapshot (so the per-segment sanitize is a true no-op → INV-4 byte-identity holds).
  Re-run required: Item 4 churned the corpus.
- **B4 / D5:** no committed fixture/baseline hits the SC-11 grandparent-collision case (two
  same-named scopes under different grandparents sharing a parent). This scan **decides the gate**:
  clean → SC-11 re-check lands as fail-fast; any hit → WARN-first (fail-fast deferred to follow-up).

### Test Stencil (Write This First)
```python
# tests/conformance/test_sanitize_invariance.py  (NEW)

def test_sanitize_name_is_identity_on_committed_corpus():
    """INV-1: sanitize_name changes no segment in any committed snapshot."""
    for snap in all_committed_snapshots():          # 12 extraction_snapshot.json
        for qn in every_qualified_name(snap):       # calc_def QNs, owning_part QNs, attr QNs
            for seg in qn.split("::"):
                assert sanitize_name(seg) == seg, f"{seg!r} in {snap} is not identity"

def test_no_committed_model_hits_grandparent_collision():
    """B4/D5 gate: record WARN-vs-FAIL. Emit the decision as a captured constant."""
    collisions = scan_grandparent_collisions(all_committed_models())  # see registry.py:103-108
    assert collisions == [], f"grandparent collision → SC-11 re-check must land WARN-first: {collisions}"
```

### Changes Required
**See `design.md#required-invariants` (INV-1) and `design.md#key-decisions` (D5) for the reasoning.**

- [x] `tests/conformance/test_sanitize_invariance.py` (NEW) — the two scans above. The INV-1 scan
      enumerates **all** QN-bearing fields across every committed snapshot (calc-def `qualified_name`,
      `owning_part_qualified_name`, computed-attr QNs, part-def QNs).
- [ ] The grandparent scan mirrors the alias scheme exactly (`registry.py:103-108` — alias uses only
      the **parent** segment, so two same-parent/different-grandparent scopes still collide).
- [ ] **Record the gate outcome** in this plan's Implementation Notes (WARN vs FAIL) — it selects the
      Phase 3 SC-11 branch.
- [ ] **Re-verify V/REQ numbering** against docs 15/20 at this point (m5): confirm REQ-NC-08,
      the duplicate-path REQ (recommend a generation-layer REQ over V11 — see `design.md#key-decisions`),
      and REQ-REG-08 are still free after Item 4's concurrent doc edits (V9/V10). Record the confirmed IDs.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_sanitize_invariance.py` → both pass
- [ ] `uv run pytest tests/` → no regressions (this phase adds only tests)

**Manual:**
- [ ] Read the grandparent-scan output; record WARN vs FAIL decision in Implementation Notes.
- [ ] Read docs 15/20 REQ tables; record the confirmed free REQ IDs.

**What We Know Works After This Phase:**
INV-1 is corpus-verified (the no-op is real, not assumed) and the SC-11 gate is decided before any
fail-fast is written.

---

## Phase 1: FORMULA wire — helper + M1, fixture-first (de-risk first)

### Goal
Prove the FORMULA produced-channel == consumed-channel wire on a real quoted-owner fixture, then make
it structural. This is `design.md`'s **"De-risk first"** item (B2 / INV-5) and the SC #2 R1 lock.
Introduce the `sanitize_qualified_name` helper here (it is used by both the FORMULA sites and Phase 2).

### Assumption Under Test
- **INV-5 / B2:** for a FORMULA computed attribute the registry-produced channel equals the
  graph-consumed channel. Today the consumer builds the leaf from `sysml_to_python_qualified_name(ca.name)`
  (`graph_builder.py:745/789`) while the producer builds it from `ca.python_name`
  (`output_registry_builder.py:124-125`) — they diverge on a quoted owner (and on keyword names, via
  the two-sanitizer gap — see `design.md#key-bets` B2). M1 makes the consumer build the leaf from
  `ca.python_name` too, so they are identical **by construction**; the residual bet narrows to "no
  derivation site was missed."

### Test Stencil (Write This First — red on raw code)
```python
# tests/conformance/test_formula_quoted_owner.py  (NEW)

def test_formula_quoted_owner_channel_resolves(tmp_path):
    """SC #2 R1 lock: same-part FORMULA→consumer under a quoted owner.
    Assert the PATH resolved, not just string-equality: the consumer module's
    resolved input channel == the registry's registered canonical channel."""
    ctx = build_pipeline_context_from_snapshot(snapshot_fixture("quoted_owner_formula"))
    registered = registered_canonical_channel_for_formula_output(ctx)   # from output_registry
    resolved   = resolved_input_channel_on_consumer(ctx)                # from ComputationGraph
    assert resolved == registered            # the wire actually resolved
    # cross-part REFERENCE variant is Item 7's (raw :130/:595 path) — noted, not tested here
```

### Changes Required
**See `design.md#component-overview`, `design.md#implementation-notes` (M1 block), and the
`design.md` appendix for the exact before/after at each site.**

#### 1. New fixture (topology + QN constraints are load-bearing — M2/M3)
- [ ] `tests/fixtures/quoted_owner_formula/` (NEW) — a **same-part** FORMULA→consumer model: a
      quoted-named part def owning a FORMULA computed attribute consumed by a calc usage **in the same
      part** (resolves via the in-memory `resolution_map` / `ScopedKey` `key_f` at
      `output_registry_builder.py:136-137` — the **Item-7-independent** path). **MUST NOT** use a
      cross-part REFERENCE consumer (that routes through the raw `:130`/`:595` QN path — Item 7's).
- [ ] **M3 QN constraints:** the quoted owner uses segments that sanitize **non-trivially on purpose**
      (e.g. `'Margin Part'` → `Margin_Part`). Its **unquoted** segments (package, consumer, attr)
      MUST avoid accidental-change forms (`value_`, `_x`, `a__b`, Python keywords) or the no-op / B2
      reasoning breaks on the very fixture being added.
- [ ] Live extraction capture → committed `extraction_snapshot.json` (additive; license window open —
      R3). Capture via the snapshot CLI path used by the conformance suite.

#### 2. The helper
- [ ] `core/qualified_names.py` beside `sysml_to_python_qualified_name` (`:103`) — add
      `sanitize_qualified_name(sysml_qname)` per `design.md#implementation-notes` (~2 lines:
      `"__".join(sanitize_name(seg) for seg in sysml_qname.split("::"))`). Export in `__all__` (`:124`).
      **INV-2:** apply once, at the `::` boundary; never on a `__`-joined string.

#### 3. FORMULA sites (leaf from `python_name`, never re-sanitize `ca.name` — M1)
- [ ] `graph_builder.py:745` (resolution_map consumer) → `f"{sanitize_qualified_name(ca.owning_part_qualified_name)}__{ca.python_name}"`.
- [ ] `graph_builder.py:789` (module identity consumer) → same construction.
- [ ] `graph_builder.py:818` (`part_eqn`, no leaf) → straight helper swap: `sanitize_qualified_name(ca.owning_part_qualified_name)`.
- [ ] `output_registry_builder.py:124-125` (producer) → owner via helper; leaf already `ca.python_name`
      (`sanitize_qualified_name(owner)` + `f"__{ca.python_name}"`). Producer == consumer by construction.
- [ ] `graph_builder.py:791` module_type stays via `derive_module_type`→`from_sysml` (sanitized in
      Phase 2) — a *different* identifier, need not equal `python_name`.
- [ ] **D3 collapse:** replace the `graph_builder.py:273-276` EXPOSE_PURE ad-hoc
      (`"__".join(sanitize_name(seg) ...)`) with a `sanitize_qualified_name(...)` call (character-for-
      character the helper body — verified in `design-review.md#pattern-consistency`).

#### 4. Leave raw (INV-3 — DO NOT TOUCH)
- [ ] `output_registry_builder.py:130` (raw `SysMLQN` registration key) — unchanged; Item 7 flips it in
      lockstep. Same for the three match sites (`dependency_backtracker.py:660`, `parameter_groups.py:439`,
      `pipeline_builder.py:70`).

### Validation
**Automated:**
- [ ] New FORMULA test: **red before the code changes, green after** (the red→green is the proof).
- [ ] `uv run pytest tests/` → green.
- [ ] **Invariance gate:** `_tree_diff` over all 12 committed snapshots + all baselines == empty
      (the FORMULA-site change is a no-op on the 3 unquoted FORMULA models — attr_expr_probe,
      solar_battery_model, catf_mfe_model — by INV-1 + non-keyword attr names).
- [ ] `uv run mypy src/` and `uv run ruff check src/` → no new findings.

**Manual:**
- [ ] Inspect the new fixture's generated FORMULA channel name — confirm it is sanitized
      (`QuotedOwnerLib__Margin_Part__net_margin`, no quotes/spaces).

**What We Know Works After This Phase:**
The FORMULA wire resolves under a quoted owner; producer == consumer is structural; the helper exists;
no existing model changed.

---

## Phase 2: CalcUsage derivation sanitize + `alias_agg_probe` conformance

### Goal
Fix the reproduced SC-4 leak — quoted **calc def** names producing `'margin calc'.py`,
`class 'Margin Calc'Input`, and a registry importing a class its module never declares — by
sanitizing inside the two `from_sysml` methods. Lock it with the `alias_agg_probe` full-generation
conformance test (the fixture that reproduces the bug and has never flowed through generation).

### Assumption Under Test
`ModuleType.from_sysml` / `PythonModulePath.from_sysml` are the class-name and module-path emission
points; sanitizing their segments (inline, per `design.md#key-decisions` D4) produces importable,
internally-consistent Python for a quoted CalcUsage — and is a byte-level no-op on every unquoted
model (INV-1).

### Test Stencil (Write This First)
```python
# tests/conformance/test_alias_agg_probe_generation.py  (NEW)

def test_alias_agg_probe_generates_importable_package(tmp_path):
    """SC #1 lock: full registry + module generation from the committed snapshot."""
    config = GenerationConfig(from_snapshot=snapshot_fixture("alias_agg_probe"),
                              output_path=tmp_path, package_name="aap", overwrite=True)
    assert run_codegen(config) is True
    for py in tmp_path.rglob("*.py"):
        ast.parse(py.read_text())                       # (1) every file parses
    for cls, module in registry_imports(tmp_path):
        assert cls in classes_declared_in(module)       # (2) imported name == declared class
```

### Changes Required
**See `design.md#component-overview` and the `design.md#implementation-notes` "Segment-order gotcha".**

#### 1. `from_sysml` inline sanitize (sanitize **then** lower — order is load-bearing)
- [ ] `identifier_types.py:106` (`ModuleType.from_sysml` namespace) →
      `".".join(sanitize_name(s).lower() for s in sqn.package_segments)`.
- [ ] `identifier_types.py:107` (class_name, **preserve case**) → `f"{sanitize_name(sqn.element_name)}Module"`.
- [ ] `identifier_types.py:142` (`PythonModulePath.from_sysml` directory) →
      `"/".join(sanitize_name(s).lower() for s in sqn.package_segments)`.
- [ ] `identifier_types.py:143` (filename) → `sanitize_name(sqn.element_name).lower()`.
- [ ] Import `sanitize_name` into `identifier_types.py` (from `core.qualified_names`) if not already.
- [ ] **Do NOT lower-then-sanitize** — the reserved-word guard must see the pre-lowercased form,
      matching `build_element_qualified_name` (`qualified_names.py:57`). See `design.md#implementation-notes`.

### Validation
**Automated:**
- [ ] `alias_agg_probe` conformance test → passes (ast.parse + import-name match).
- [ ] `uv run pytest tests/` → green.
- [ ] **Invariance gate:** `_tree_diff` over all snapshots + baselines == empty (from_sysml sanitize
      is a no-op on unquoted segments — INV-1).
- [ ] `uv run mypy src/` / `uv run ruff check src/` → clean.

**Manual:**
- [ ] Inspect `alias_agg_probe` output: module filenames, class names, and registry imports are all
      sanitized and mutually consistent (the research reproduction is gone).

**What We Know Works After This Phase:**
Quoted CalcUsage names generate an importable, internally-consistent package; the SC-4 reproduction
is closed; no existing model changed.

---

## Phase 3: Duplicate-path fail-fast + SC-11 post-alias re-check

### Goal
Turn two silent-overwrite hazards into loud, actionable errors: (a) two SysML names sanitizing to one
output path across **three write key spaces**, and (b) the SC-11 residual grandparent collision that
survives aliasing. The SC-11 branch (fail-fast vs WARN) is set by Phase 0's gate.

### Assumption Under Test
- The duplicate-path pre-pass, run **before `_clear_output_directory`**, catches all three write
  collisions and names both raw sources — with no false positive on any committed model (which is why
  it runs after Phases 1–2 prove the happy path stays byte-identical).
- The post-alias re-group in `_resolve_class_name_collisions` detects exactly the grandparent case
  (`design-review.md` "What checks out" — the alias uses only the parent segment).

### Test Stencil (Write This First)
```python
# tests/unit/test_duplicate_path_failfast.py  (NEW) — one test per key space
def test_module_path_collision_fails_fast():      # two usage EQNs → one modules/.../x.py
    with pytest.raises(GenerationError, match="Duplicate output path"):
        _check_duplicate_output_paths(modules_colliding_on_full_path())
    # message names BOTH raw source names + the shared path

def test_schema_key_collision_fails_fast():       # 'Margin Calc' & 'margin calc' → margin_calc_output.py
    ...                                            # separate key space: calc_def_name.lower()

# tests/unit/test_sc11_recheck.py  (NEW)
def test_grandparent_collision_recheck():         # gate-dependent: raises OR warns per Phase 0
    ...
```

### Changes Required
**See `design.md#component-overview`, `design.md#implementation-notes` (fail-fast key spaces,
raw-name provenance), and `design.md#architecture` (pre-pass placement).**

#### 1. Duplicate-path pre-pass (two key spaces, three write paths)
- [ ] `cli/__init__.py` — new `_check_duplicate_output_paths(modules)`; call it at **~:708** (after the
      graph-built log at `:707`, **before `_clear_output_directory`** at `:712`) so a collision never
      wipes existing output first (m2).
- [ ] **Key space A — modules + stencils (one key):** `_get_python_path(module).full_path` (write at
      `:215`). Stencils write `{filename}_impl.py` from the same `_get_python_path` output (`:258/:260`),
      so a module-key collision implies a stencil collision — verify no stencil path is derived elsewhere.
- [ ] **Key space B — schemas:** `module.calc_def_name.lower()` (write at `:177`), only for modules with
      ≥2 outputs (the `:175`-region skip). Catches `Margin_Calc` vs `margin_calc` → one
      `margin_calc_output.py` even when module paths differ — a module-path-only pass misses this.
- [ ] **Raw-name provenance (m3):** recover each colliding module's raw spelling from `PipelineModule`
      — `calc_def_qualified_name` (raw) for calc-usage modules; for FORMULA modules
      `calc_def_qualified_name = ca.owning_part_qualified_name` + `calc_def_name = ca.name` (both raw,
      populated at `graph_builder.py:891-892` — verified). Both non-None for every colliding type.
- [ ] Error text = V-style, names **both** sources + shared path (see `design.md#implementation-notes`).
      Follow the SC-2 zero-output / `_validate_channel_references` precedent.

#### 2. SC-11 post-alias re-check (gate-dependent)
- [ ] Extend `_resolve_class_name_collisions` (`registry.py:60-129`): after aliasing, re-group by the
      **aliased** class name; if any group still has >1 member, **raise if Phase 0 was clean, else WARN**
      (B4/D5). REQ-REG-08.

### Validation
**Automated:**
- [ ] Three fail-fast tests (module, stencil-via-module, schema) — each asserts the error names both
      sources and the shared path.
- [ ] SC-11 re-check test (fail-fast or WARN per Phase 0).
- [ ] `uv run pytest tests/` → green; **invariance gate** still empty (the pre-pass raises on no
      committed model — Phase 0 proved the grandparent case is absent, and no committed model has a
      sanitize-collision).
- [ ] `uv run mypy src/` / `uv run ruff check src/` → clean.

**Manual:**
- [ ] Run generation on a hand-made two-quoted-name model → see the duplicate-path error naming both.

**What We Know Works After This Phase:**
Silent overwrites across all three write key spaces fail fast; the SC-11 residual hole is closed
(fail-fast) or made visible (WARN); INV-3 held (match sites/`:130` untouched).

---

## Phase 4: Docs, verification matrix, close-out carry-through

### Goal
Land the R1 doc/REQ lockstep and the R2 agentic-mbse impact record, including the two coordination
obligations that must survive to their consumers (Item 7 lockstep; fusion-tea retirement).

### Changes Required
**See `design.md#docs--agentic-mbse-carry-through` and `spec.md#agentic-mbse-impact`.**

- [ ] **Doc 15** (`15-naming-conventions.md`): add REQ-NC-08 (derivation sanitize) + the duplicate-path
      REQ to the table; update §8 to note per-segment sanitize now happens at the FORMULA module_eqn
      sites via `sanitize_qualified_name`, not a bare replace. (Use the REQ IDs confirmed in Phase 0.)
- [ ] **Doc 20** (`20-module-registry-generation.md`): add REQ-REG-08 (post-alias uniqueness re-check);
      record SC-11 as "confirmed intended, documented, tested" (REQ-REG-03/04/07 PASS).
- [ ] **Verification matrix:** rows for REQ-NC-08/09 (or the confirmed duplicate-path REQ) and REQ-REG-08.
- [ ] **SC-11 closure record** in the Item 5 close-out.
- [ ] **agentic-mbse impact** (recorded for Item 12, not built): MODELING_GUIDE/sysml-conventions
      "quoted names are fine — identifiers are derived"; a Level-2/6 validation-warning candidate for
      two SysML names sanitizing to one Python identifier.
- [ ] **⚠️ Item 7 lockstep obligation** (must appear in close-out + agentic-mbse coordination note):
      when Item 7 sanitizes `dependency_backtracker.py:595` it MUST flip
      `output_registry_builder.py:130` to sanitized **in the same change** (raw→raw becomes
      sanitized→sanitized atomically), and the `pipeline_builder.py:70` FORMULA-twin match set moves
      with it — or the FORMULA REFERENCE match breaks. See `design.md#next-stage-handoff`.
- [ ] **fusion-tea note** (close-out): `sanitize_names.py` becomes dead once this lands — flag for
      **coordinated, reviewed retirement** (their post-processor's rules may differ subtly from
      `sanitize_name`), not a silent drop.

### Validation
- [ ] `uv run pytest tests/` → full suite green.
- [ ] **Final invariance gate:** `_tree_diff` over all committed snapshots + all baselines == empty.
- [ ] `uv run mypy src/` / `uv run ruff check src/` → no new findings.
- [ ] Docs render; REQ IDs are unique and matrix rows resolve.

**What We Know Works After This Phase:**
Item 5 is complete and auditable: derivation sanitize + three-key-space fail-fast + SC-11 closure,
byte-identical on every existing model, with both handoff obligations recorded.

---

## Environment Setup

**See CLAUDE.md.** Tests: `uv run pytest tests/`. Single: `uv run pytest tests/... -k name`.
Type check: `uv run mypy src/`. Lint: `uv run ruff check src/`. Fixture capture / snapshot-driven
generation is license-free via the `--from-snapshot` path (Item 2) used by
`tests/conformance/test_snapshot_generation.py`; the **new fixture's live extraction capture**
needs the syside license (expires 2026-08-06 — R3; window open now).

---

## Risk Management

**See `design.md#potential-risks`.** Phase-specific mitigations:

- **Phase 0:** INV-1 overclaim (a segment silently changes) → the corpus scan is the hard proof, run
  before any code. SC-11 gate wrong → the grandparent scan sets WARN-vs-FAIL, not a guess.
- **Phase 1:** a **missed FORMULA site** yields a sanitized-but-mismatched wire (now the *only* B2
  failure mode after M1) → the fixture's resolved==registered assertion is the lock; all four sites
  enumerated in the checklist.
- **Phase 2:** `from_sysml` sanitize/lower order changes an unquoted baseline → the invariance gate is
  the hard stop; sanitize-then-lower is pinned to match `build_element_qualified_name`.
- **Phase 3:** duplicate-path pre-pass false-positive on a committed model → runs only after Phases 1–2
  prove byte-identity; SC-11 fail-fast breaks a baseline → gated on Phase 0's scan.
- **Cross-cutting:** line-anchor drift (Items 3/4 churn) → anchors re-verified at plan time (table
  above) and to be re-verified once more at implement time.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**SC-11 gate decision (WARN vs FAIL):** **FAIL (hard fail-fast).** The grandparent-collision
scan (`_residual_grandparent_collisions`, mirroring `registry.py:98-116`) is **CLEAN** on all
12 committed snapshots — zero residual post-alias collisions. So the Phase 3 SC-11 re-check
lands as `raise`, not WARN.
**Confirmed REQ IDs (docs 15/20):** doc 15 stops at REQ-NC-07, doc 20 at REQ-REG-07, V-rules at
V10. Assigned: **REQ-NC-08** (derivation sanitize), **REQ-NC-09** (duplicate-path fail-fast —
generation REQ, **not** V11 per design recommendation), **REQ-REG-08** (SC-11 post-alias re-check).
**Completed:** 2026-07-05.
**Changes Made:**
- Added `tests/conformance/test_sanitize_invariance.py` (NEW) — 3 scans: INV-1 accidental-form
  guard, INV-1 quoted-name corollary, SC-11 grandparent gate. All pass (0.09s, license-free).
**Anchors re-verified at implement (HEAD `0a6383a`):** all plan-table anchors confirmed unchanged
— `qualified_names.py:13/103/124`, `identifier_types.py:104-108/140-143`, `output_registry_builder.py:124-125/130/136-137`,
`graph_builder.py:744-746/788-791/818/273-276/879-897 (calc_def_name :891, calc_def_qualified_name :892)`,
`cli/__init__.py:149/177/215/258-260/710-712`, `registry.py:60-129`.
**Issues:** None.
**Deviations:**
- **INV-1 scan reformulated (probe contradicted the literal stencil).** The plan/design stencil
  asserts `sanitize_name(seg) == seg` for *every* segment. That is literally false on the corpus:
  9 segments change under sanitize, all quoted SysML names (`alias_agg_probe` calc defs
  `'Margin Calc'`/`'Report Calc'`/`'Unit Cost Calc'`; `solar_battery` `'Solar Array'`;
  `unresolvable_attr_probe` `'Derived Component'`/`'Design Derived'`). The invariant that actually
  underpins INV-4 byte-identity is narrower and *does* hold: **no already-identifier-safe segment
  changes** (the dangerous accidental forms — edge underscore, `__` run, keyword — are absent;
  accidental set is empty), and every changed segment is a quoted name that either never reaches
  generation (`alias_agg_probe` — first generated in Phase 2, the intended change) or is
  already-normalized (`solar_battery` `'Solar Array'` is EXPOSE_PURE, sanitized today via the
  `graph_builder.py:273-276` ad-hoc the D3 collapse replaces char-for-char). The test proves this
  faithfully rather than spuriously failing. The end-to-end byte-identity gate (Phases 1-3 tree_diff)
  remains the authoritative proof.
- **Extra byte-identity precheck (recorded, not a code change):** all FORMULA attrs in the 3
  generating FORMULA models (attr_expr_probe, catf_mfe, solar_battery) have **unquoted owners**
  AND `name == python_name`, so the Phase 1 M1 leaf-from-`python_name` change is byte-identical on
  every existing model.

### Phase 1 Completion
**Completed:** 2026-07-05.
**Changes Made:**
- `core/qualified_names.py`: added `sanitize_qualified_name(sysml_qname)` beside
  `sysml_to_python_qualified_name`; exported in `__all__`.
- `orchestration/output_registry_builder.py:124`: producer owner via helper (import swapped
  `sysml_to_python_qualified_name` → `sanitize_qualified_name`; it was the only use).
- `resolution/graph_builder.py`: import swapped to `sanitize_qualified_name`; resolution_map
  consumer (:744-746) and module-identity consumer (:788-791) now build `module_eqn =
  f"{sanitize_qualified_name(owner)}__{ca.python_name}"` (M1 leaf from python_name); `part_eqn`
  (:818) straight helper swap; module-identity keeps raw `sysml_qn` for `derive_module_type` at
  :791 (separate identifier, sanitized in Phase 2). D3 collapse: the EXPOSE_PURE ad-hoc
  `"__".join(sanitize_name(seg) ...)` (:273-276) → `sanitize_qualified_name(...)`.
- **Left raw (INV-3):** `output_registry_builder.py:130` and the three match sites untouched.
- New tests: `tests/conformance/test_formula_quoted_owner.py` (red→green lock); new fixture
  `tests/fixtures/quoted_owner_formula/` (design.sysml + library.sysml + committed
  `extraction_snapshot.json`, live capture).
**Red→green proof:** on raw code the test failed with consumer-resolved
`QuotedOwnerFormulaDesign__'Margin Part'__net margin__net_margin` vs registry-registered
`...__net_margin__net_margin`; after the helper + M1 both are
`QuotedOwnerFormulaDesign__Margin_Part__net_margin__net_margin` — assertion `resolved == registered`
passes.
**Validation:** full suite **1874 passed** / 4 skipped / 5 xfailed (1870 baseline + 4 new tests);
baseline byte-identity conformance (test_baselines / test_pipeline_e2e / test_gen_pipeline_yaml) all
green; ruff 21, mypy 109 (both unchanged).
**Issues:** None after the fixture-topology correction below.
**Deviations:**
- **Fixture consumer is a computed attribute, not a calc usage (design prose corrected; INV-5
  intact).** The design *prose* (design.md:335) said "consumed by a calc usage in the same part."
  A probe proved that path wrong: a calc-usage input binding to a same-part computed attribute
  produces a `::`-qualified REFERENCE source_path, so it routes through
  `dependency_backtracker._resolve_reference_dispatch` — `sysml_qn_lookup` (raw `:130`/`:595` key)
  then a leaf+parent scoped lookup whose leaf is extracted **raw** (`:473`). For a *quoted* owner
  both fail (raw key/leaf `'net margin'` vs registered python_name `net_margin`), and **those are
  Item 7's match sites — untouched by Item 5** — so a calc-usage consumer stays unresolved after
  Phase 1. The design's own **appendix + site list** (graph_builder `:745/:789`, the
  `resolution_map`) actually describe the **computed-attribute consumer** path, which *is* an
  Item-5 site. The design explicitly left "the fixture's concrete SysML" open for the plan
  (design.md:369), and INV-5 (producer channel == consumer channel via `resolution_map`) is proven
  exactly by this fixture. So the consumer is a second same-part FORMULA attribute
  (`total_payout = 'net margin' * 2.0`); a minimal calc def (`ScaleCalc`, no usage) satisfies the
  "model has calc defs" generation precondition without touching the tested wire. This is a
  correction of imprecise design prose, not a change to any invariant.

### Phase 2 Completion
**Completed:** 2026-07-05.
**Changes Made:**
- `core/identifier_types.py`: imported `sanitize_name` from `core.qualified_names` (no circular
  import — `qualified_names` imports only `re`). `ModuleType.from_sysml`: namespace
  `".".join(sanitize_name(s).lower() ...)`, class_name `f"{sanitize_name(element_name)}Module"`
  (case preserved). `PythonModulePath.from_sysml`: directory `"/".join(sanitize_name(s).lower() ...)`,
  filename `sanitize_name(element_name).lower()`. Sanitize-then-lower throughout (order pinned to
  `build_element_qualified_name`).
- New test `tests/conformance/test_alias_agg_probe_generation.py` (red→green).
**Red→green proof:** before the fix, generation emitted
`from aap.modules.aliasaggprobelibrary.'margin calc' import Margin_CalcModule` — a SyntaxError on
`ast.parse` (module path leaked the quoted name while the class name was already sanitized, the
exact registry/module inconsistency). After the fix all files parse and every imported class is
declared by its module.
**Validation:** full suite **1875 passed** / 4 skipped / 5 xfailed; baseline byte-identity holds
(from_sysml sanitize is a no-op on unquoted segments — INV-1); ruff 21, mypy 109 (unchanged).
**Issues:** None. **Deviations:** None.

### Phase 3 Completion
**Completed:** 2026-07-05.
**Changes Made:**
- `cli/__init__.py`: added `_raw_source_name(module)` (raw provenance — FORMULA:
  `owner_qn::ca.name`; calc-usage: `calc_def_qualified_name`) and
  `_check_duplicate_output_paths(modules)` (two key spaces: module/stencil python path, schema
  `calc_def_name.lower()`; only multi-output modules for schemas). Wired as **Step 1.5** in
  `run_codegen`, after the graph-built log, **before `_clear_output_directory`**. Raises
  `CodeGenerationError` naming both raw sources + shared path. Error keyed on raw-source identity,
  so multiple usages of one calc def (same path, same source) do NOT false-positive — only
  distinct raw names colliding do.
- `generation/registry.py`: `_resolve_class_name_collisions` post-alias re-check (REQ-REG-08) —
  re-group by aliased class_name, `raise ValueError("...grandparent collision...")` on any residual
  >1 group. **Hard fail-fast** per the Phase 0 CLEAN gate.
- New tests: `tests/unit/test_duplicate_path_failfast.py` (3: module-path, schema-key,
  same-source-no-collision) and `tests/unit/test_sc11_recheck.py` (2: grandparent raises, distinct
  parents alias cleanly).
**Validation:** full suite **1880 passed** / 4 skipped / 5 xfailed (1870 + 10 new). Invariance gate
holds — the pre-pass raises on **no** committed model and the SC-11 re-check fires on none (Phase 0
proved both absent). ruff 21; mypy **109** (added `PipelineModule` to the TYPE_CHECKING block and
annotated the two new functions to hold the baseline — an interim run hit 112 before annotation).
**Issues:** mypy rose to 112 on first pass (untyped `module`/`modules` params → Any); fixed by
annotating. **Deviations:** the fail-fast raises `CodeGenerationError` (the established zero-output
precedent, `pipeline_context.py:47`), not a literal `GenerationError` — the plan stencil's
`GenerationError` was a loose name; `CodeGenerationError` is the real class. SC-11 re-check raises
`ValueError` (matches the surrounding `registry.py` collision-handling convention).

### Phase 4 Completion
**Completed:** 2026-07-05.
**Changes Made:**
- **Doc 15** (`15-naming-conventions.md`): added REQ-NC-08 (derivation sanitize) + REQ-NC-09
  (duplicate-path fail-fast) to the table; §8 now notes the FORMULA module_eqn sites use
  `sanitize_qualified_name` (not a bare replace) and the leaf comes from `python_name`.
- **Doc 20** (`20-module-registry-generation.md`): added REQ-REG-08 (post-alias re-check) to the
  table; Design-Constraints §now records SC-11 as confirmed/documented/tested with the residual
  grandparent hole closed as a hard fail-fast, AST rewrite deferred.
- **Close-out** (`close-out.md`, NEW): verification matrix, SC-11 closure, ⚠️ Item 7 lockstep
  obligation, fusion-tea retirement note, agentic-mbse impact (Item 12), deviations.
**Validation:** docs render (markdown tables well-formed); REQ IDs unique (NC-08/09, REG-08); full
suite green; ruff 21 / mypy 109 unchanged.
**Issues:** None. **Deviations:** None (carry-through obligations recorded, not executed — Item 12
owns the agentic-mbse edits; the orchestrator commits).

---

**Status:** Complete
</content>
</invoke>
