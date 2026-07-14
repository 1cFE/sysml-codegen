# Implementation Plan: Part-Instance Index

**Status:** Complete
**Created:** 2026-07-12
**Last Updated:** 2026-07-12
**Epic:** CONSTRAINT-EXEC — Item 4
**Branch:** constraint-exec-epic

## Source Documents
- **Spec:** `.project/active/part-instance-index/spec.md`
- **Design:** `.project/active/part-instance-index/design.md` ← component details, bets, decisions, invariants. This plan does not restate them; it links.
- **B1/B2 evidence:** `.project/active/part-instance-index/b1-probe-evidence.md` (live multiplicity truth table; licensed-env reproduction command)
- **S3 fixture:** `.project/active/spike-concrete-expansion-instance-index/model.sysml` (promotable; nine-instance oracle) and `probe_instance_index.py` (the exact oracle path set).

---

## Implementation Strategy

**Phasing Rationale.** The load-bearing, riskiest surface is the cardinality classifier
(`design.md#implementation-notes` — "the risky surface"), and it is a **pure function over
live/mock multiplicity nodes**. It needs no model load and no license. So it goes first, tested
license-free against a mock-node truth table (Validation #6). Everything else — the walker,
closure projection, dedup, ordering — is exercised only through a live model load, which needs
the licensed sibling env, so it follows once the classifier is proven.

**Critical Path:** classifier + truth table → structured walker + closure + `PartInstanceIndex`
query object → promote/extend fixture → live oracle/collision/cartesian/determinism → live
blocking → additive/byte-identity + full-suite/type/lint gates.

**First Proof Point:** Phase 1 — the classifier truth table (8 rows) green in the plain codegen
venv (no license). That collapses the one genuinely uncertain piece before any live work.

**Two environments, stated once (see CLAUDE.md and `b1-probe-evidence.md`):**

- **Plain codegen venv (license-free)** — classifier truth-table tests, additive-guard test,
  full suite, mypy, ruff:
  ```
  uv run pytest tests/unit/test_part_instance_index.py
  uv run pytest tests/            # full suite; live tests below SKIP here (see marker note)
  uv run mypy src/ && uv run ruff check src/ tests/
  ```
- **Licensed sibling env (live model loads)** — every test that loads the fixture. The codegen
  venv has no SysIDE license (memory: "syside license via scripts not -c"; S3 findings §2), so
  these run through the agentic-mbse env with codegen `src/` first on `PYTHONPATH`:
  ```
  env UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache \
      PYTHONPATH=/home/reid/1cfe/sysml-codegen/src \
      uv run --directory /home/reid/1cfe/agentic-mbse \
      python -m pytest -c /home/reid/1cfe/sysml-codegen/pyproject.toml \
      /home/reid/1cfe/sysml-codegen/tests/conformance/test_part_instance_index.py -v
  ```
  The `-c …/pyproject.toml` makes codegen's pytest config and custom markers load under the
  sibling rootdir. The b1/S3 probes confirm this env has the license and `syside`; a sandbox
  restriction blocked pre-verifying that **pytest itself** is installed there. **Phase 2's first
  action confirms collection.** If pytest is absent in that env, the fallback is a standalone
  runner script (mirroring `probe_instance_index.py`'s invocation) that imports and asserts the
  same cases; do not weaken the assertions.

**The `@requires_license` marker (tests/conftest.py:40).** Mark every live test with
`@requires_license`. In the plain venv they **skip** (keeping `uv run pytest tests/` green); they
are proven **green** by the licensed-env command above. Live-test phases are complete only when
that command shows them passing (not skipped).

**Overall validation:** each phase starts by writing its tests. No production module imports the
new one this item (INV-1); the additive guard (Phase 3) enforces it.

---

## Phase 1 — Cardinality classifier + truth table (license-free)

### Goal
Build the fail-closed cardinality gate as a pure function and pin its full truth table against
mock nodes. First because it is the riskiest surface and needs no license.

### Assumption Under Test
The node-type-dispatch gate (`design.md#key-decisions` D3) exactly reproduces the B1 truth table,
including `[3..3]`→Fixed(3) (C2) and an unrecognized `upper_bound` node → block (fail-closed).

### Test Stencil (Write This First)
`tests/unit/test_part_instance_index.py` (NEW — plain venv):
```python
from sysml_codegen.analysis.part_instance_index import classify_cardinality, Fixed, NonFinite

# Mock nodes dispatch by class name via SysideAdapter.is_instance (as
# test_hierarchy_resolver.py:806-839 mocks multiplicity nodes).
def usage(upper, lower=None, is_ordered=False, is_nonunique=False):
    return _MockUsage(_MockRange(upper_bound=upper, lower_bound=lower),
                      is_ordered=is_ordered, is_nonunique=is_nonunique)

def test_bare_fixed():           # [3]
    assert classify_cardinality(usage(LiteralInteger(3)), "O", "f") == Fixed(3)
def test_equal_bounds_admit():   # [3..3]  (C2)
    assert classify_cardinality(usage(LiteralInteger(3), LiteralInteger(3)), "O", "f") == Fixed(3)
def test_range_blocks():         # [0..5]
    assert isinstance(classify_cardinality(usage(LiteralInteger(5), LiteralInteger(0)), "O","f"), NonFinite)
# ... [*]→NonFinite, [n]→NonFinite, ordered→NonFinite, nonunique→NonFinite, unknown-node→NonFinite
```

### Changes Required
**See `design.md` for:** D3 gate (`#key-decisions`), D8 live-node-only source of truth,
B1 table (`#research-findings`), classifier notes (`#implementation-notes`).

#### 1. New module skeleton
**File:** `src/sysml_codegen/analysis/part_instance_index.py` (NEW)
- [x] Frozen dataclasses `PathStep`, `InstanceOccurrence` per the `design.md#implementation-notes`
      sketch (`InstanceOccurrence` filled out in Phase 2). `PathStep(owning_def_qn: str,
      feature_name: str, occurrence_index: int | None)`.
- [x] `NonFiniteCardinalityError(Exception)` (D4) — message names `owning_part_def_qn` and
      `part_usage_name`.
- [x] Classifier result types: `@dataclass(frozen=True) class Fixed: count: int` and
      `@dataclass(frozen=True) class NonFinite: reason: str`.
- [x] `classify_cardinality(usage_node, owning_def_qn, feature_name) -> Fixed | NonFinite`, pure.
      Called only for usages **with** a multiplicity node (singleton is the walker's job, Phase 2).
      Dispatch exactly D3:
      - `usage.is_ordered` or `usage.is_nonunique` → `NonFinite`.
      - `ub = usage.multiplicity.upper_bound`, `lb = usage.multiplicity.lower_bound`.
      - Dispatch on `ub` node **type** via `SysideAdapter.is_instance(ub, "…")` (class-name
        fallback lets the same code match live nodes and mocks — the codebase idiom):
        `"LiteralInfinity"`→NonFinite; `"FeatureReferenceExpression"`→NonFinite;
        `"LiteralInteger"`→ read integer value `u`; `lb is None`→`Fixed(u)`;
        `lb` is `LiteralInteger` `l==u`→`Fixed(u)`; `l!=u`→NonFinite; **any other node type**→
        NonFinite (fail-closed default arm).
      - **Never** read `cached_*` bounds or `MultiplicityData` (B2/D8).

**Confirm the live integer accessor before writing the value read.** The truth table below uses
mocks, so it does not prove the live `LiteralInteger` value attribute. Extend
`probe_b1_multiplicity.py` with one line printing the fixed-3 node's value attribute (candidates
seen in the probe: `.value`), run it via the licensed env, and use the confirmed accessor. Mocks
set that same attribute.

#### 2. Truth-table tests
**File:** `tests/unit/test_part_instance_index.py` (NEW)
- [x] Local mock node classes (mirror `test_hierarchy_resolver.py:806-839`): a range mock with
      `upper_bound`/`lower_bound`, and per-node mocks whose class names are `LiteralInteger`,
      `LiteralInfinity`, `FeatureReferenceExpression`, plus one `UnknownNode`.
- [x] One test per B1 row (Validation #6): `[3]`→Fixed(3), `[3..3]`→Fixed(3), `[0..5]`→NonFinite,
      `[*]`→NonFinite, `[n]`→NonFinite, `[3] ordered`→NonFinite, `[3] nonunique`→NonFinite,
      unrecognized-`upper_bound`→NonFinite.

### Validation
**Automated (plain venv):**
- [x] `uv run pytest tests/unit/test_part_instance_index.py` → all 8 rows pass.
- [x] `uv run mypy src/sysml_codegen/analysis/part_instance_index.py` → clean.
- [x] `uv run ruff check src/sysml_codegen/analysis/part_instance_index.py` → clean.

**What We Know Works After This Phase:** the fail-closed gate reproduces the confirmed live
surface, license-free, including the `[3..3]` admit and the fail-closed default arm.

---

## Phase 2 — Walker, closure, index object, and live positive tests

### Goal
Build the structured-occurrence walker, subtype-closure projection, dedup, deterministic ordering,
and the `PartInstanceIndex` query object; promote+extend the S3 fixture; prove the 9/9 oracle,
collision keying, Cartesian/closure-multiplicity, `[3..3]` admit, and determinism live.

### Assumption Under Test
Subtype-closure projection over the structured walk finds every concrete occurrence with
entry-independent identity (B3/B4), and owning-def+feature keying (INV-5) separates same-named
members under different owners.

### Test Stencil (Write This First — licensed env, `@requires_license`)
`tests/conformance/test_part_instance_index.py` (NEW):
```python
@requires_license
def test_nine_instance_oracle(instance_index_model):     # Validation #1
    idx = build_part_instance_index(instance_index_model)
    paths = {o.instance_path for o in idx.occurrences_of("InstanceIndexProbe__ConstrainedLeaf")}
    assert paths == EXPECTED_NINE   # exactly probe_instance_index.py's EXPECTED_CONCRETE_PATHS

@requires_license
def test_same_name_collision(instance_index_model):      # Validation #2
    # BankA.member[3] vs BankB.member[2] under different owning defs, distinct leaf type.
    occ = idx.occurrences_of("InstanceIndexProbe__CollisionLeaf")
    assert count_by_owner(occ) == {"…BankA": 3, "…BankB": 2}
```

### Changes Required
**See `design.md` for:** walker (D2, `#implementation-notes` "Do not modify
`_find_instantiation_paths`"), closure data flow (`#architecture`), identity/dedup (D5/D7/C3),
ordering (D6), invariants INV-1..INV-5.

#### 1. Structured walker + index (in the new module)
**File:** `src/sysml_codegen/analysis/part_instance_index.py`
- [x] `_structured_paths(target_qn, part_usage_index, qn_to_partdef, _visited=None)` — a **new**
      function mirroring `_find_instantiation_paths` (`usage_extractor.py:313-369`) recursion
      shape, yielding structured occurrences instead of joined strings. **Replicate the
      `_visited` cycle guard** (`usage_extractor.py:335-337`); add a one-line "keep in sync with
      `_find_instantiation_paths`" note at both sites (INV-1: original untouched).
      - Uniform PathStep model: every usage on the chain is a `PathStep`. Recursive step
        (owning_type is a PartDefinition) → `PathStep(owning_def_qn=parent_def_qn,
        feature_name=usage_name, occurrence_index=…)`, recurse on `parent_def_qn`. Terminal step
        (owner is a Package/PartUsage) → base = `build_element_qualified_name(owner)`; the
        terminal usage is the first `PathStep(owning_def_qn=base, feature_name=usage_name, …)`.
      - **Gate every step's multiplicity**, not just the leaf (`design.md#potential-risks`
        "intermediate-container multiplicity"). For a step's usage: `usage.multiplicity is None`
        → one step, `occurrence_index=None`; else `classify_cardinality(...)` → `Fixed(n)` fans
        the step into `n` copies `occurrence_index=0..n-1` (**Cartesian down the path** — every
        upstream fan multiplies); `NonFinite` → raise `NonFiniteCardinalityError(owning_def_qn,
        feature_name)`.
- [x] `InstanceOccurrence.part_def_qn` = `most_specific(owned typings of the leaf usage,
      qn_to_partdef)[0]` — computed **once from the usage**, entry-independent (C3/D5). Never the
      closure-entry type.
- [x] `instance_path` property = `base` then, for each step in order,
      `f"__{s.feature_name}"` plus `f"[{s.occurrence_index}]"` when the index is not `None`.
      Pinned by the oracle set (below) to the probe spelling `…root__bank__member[0]`.
- [x] `build_part_instance_index(model) -> PartInstanceIndex`: builds `_build_part_usage_index`
      and `user_partdef_lookup` once; the query object closes over them (read-only imports only —
      `#architecture` "Boundaries"; do **not** import `MultiplicityData`/generation code).
- [x] `PartInstanceIndex.occurrences_of(part_def_qn) -> list[InstanceOccurrence]`:
      1. **Closure set** `applicable = {qn} ∪ {c : qn ∈ _supertype_closure(c, lookup)}`, sorted.
      2. Union structured occurrences over `applicable`.
      3. **Dedup** by canonical key `(part_def_qn, base, tuple((s.feature_name,
         s.occurrence_index) for s in steps))` — entry-independent, so a double-keyed retyped
         usage collapses to one record (D7/INV-4).
      4. **Sort** by `(tuple(s.feature_name for s in steps), tuple((s.occurrence_index if
         s.occurrence_index is not None else -1) for s in steps))` — integer indices, singleton
         normalized to `-1` sentinel so a future key change cannot reintroduce `None < int`
         (D6 + `#implementation-notes` m1).
- [x] Convenience `all_occurrences()` (used by the determinism test for a full dump) and
      `all_source_owners()`. Keep thin; no new behavior. **Cured post-audit** (`audit.md`
      Certify-with-notes, priority finding): the original catch-and-skip on
      `NonFiniteCardinalityError` was adjudicated a real silent-drop defect — a third disposition
      INV-2 forbids, reachable through a completeness-named public method. Both methods now return
      a small result object (`AllOccurrencesResult` / `SourceOwnersResult`) carrying the dumped
      items plus a `blocked: dict[str, str]` mapping (PartDef QN -> diagnostic message), so a
      caller can never mistake a partial dump for a complete one. `occurrences_of` is unchanged.
      See the cure commit and `audit.md`'s checked cure box for the full record.

#### 2. Promote and extend the fixture
**File:** `tests/fixtures/instance_index_probe/model.sysml` (NEW — promoted from S3 `model.sysml`)
- [x] Copy the S3 model verbatim (package `InstanceIndexProbe`, the nine-instance shape). This
      alone must satisfy the 9/9 oracle unchanged.
- [x] Add extension shapes using **type families disjoint from `ConstrainedLeaf`/`SpecializedLeaf`**
      so the ConstrainedLeaf closure — and thus the 9-oracle — is untouched. Query each shape by
      its own leaf type. Add matching instantiations under `root` (or new root parts) so each
      queried leaf has a live path (a blocked member only raises when its owner is instantiated):
  - **Collision (#2):** `part def BankA { part member : CollisionLeaf[3]; }` and
    `part def BankB { part member : CollisionLeaf[2]; }`; `part bank_a : BankA; part bank_b : BankB;`.
  - **`[3..3]` admit (#7):** `part def Bank33 { part m33 : Leaf33[3..3]; }`; `part b33 : Bank33;`.
  - **Cartesian (#8):** `part def Inner { part leaf : CartLeaf[3]; }`,
    `part def Outer { part c : Inner[2]; }`; `part outer : Outer;` → `occurrences_of(CartLeaf)` = 6.
  - **Closure×multiplicity (#8):** `part def ClosureBase; part def ClosureSub :> ClosureBase;`,
    `part def ClosureHost { part cs : ClosureSub[2]; }`; `part chost : ClosureHost;`
    → `occurrences_of(ClosureBase)` reaches ClosureSub via closure and expands `cs[2]` = 2.
  - **Blocking (#3), load-safe shapes only:** one host, distinct leaf per shape so each query
    reaches exactly one blocked member:
    `part def BlockHost { part n_member : LeafN[n]; part star_member : LeafStar[*];
    part range_member : LeafRange[0..5]; part ordered_member : LeafOrdered[3] ordered; }`
    with `attribute n = 4;` and `part bhost : BlockHost;`.
    **`[3] nonunique` is NOT added to the fixture** — the evidence notes a `nonunique` subsetting
    of a unique feature emits a **load-error** diagnostic (`b1-probe-evidence.md` note 4;
    `design.md#potential-risks`), which would make the whole fixture unloadable. Its blocking is
    proven by the Phase-1 truth table (mock node) instead. Note this at the fixture site.
- [x] `tests/fixtures/instance_index_probe/PROVENANCE.md` (NEW) — one line: promoted from S3
      `spike-concrete-expansion-instance-index/model.sysml`, extended for Item-4 tests; calc-free.

#### 3. Live positive tests
**File:** `tests/conformance/test_part_instance_index.py` (NEW)
- [x] A `@requires_license` fixture that loads `instance_index_probe` via `SysMLDataExtractor`
      and yields `extractor.model` (pattern: `test_extractor.py:855-861`; the raw model is
      `extractor.model` after `load_models()` — `extractor.py:52-64`).
- [x] `EXPECTED_NINE` = `probe_instance_index.py`'s `EXPECTED_CONCRETE_PATHS` (copy the set).
- [x] **#1 9/9 oracle** — `occurrences_of("InstanceIndexProbe__ConstrainedLeaf")` instance_paths
      == `EXPECTED_NINE`, zero missing, zero unexpected (includes the plain subtype).
- [x] **#2 collision** — `CollisionLeaf` occurrences: 3 keyed to BankA, 2 to BankB, keyed by
      `steps` owning-def, never by bare `member` name.
- [x] **#7 `[3..3]`** — `occurrences_of("…Leaf33")` == 3 occurrences.
- [x] **#8 Cartesian** — `occurrences_of("…CartLeaf")` == 6 with per-step indices
      `…outer__c[i]__leaf[j]` for i∈0..1, j∈0..2; **closure×multiplicity** —
      `occurrences_of("…ClosureBase")` == 2.
- [x] **#4 determinism** — load the fixture twice (two extractor instances); assert identical
      ordered `instance_path` lists from `occurrences_of` on ConstrainedLeaf (and from
      `all_occurrences()`).

### Validation
**Automated (licensed env — the command in Implementation Strategy):**
- [x] First: confirm collection — `python -m pytest -c …/pyproject.toml … --collect-only` lists
      the tests (falls back to a standalone runner only if pytest is missing in that env).
- [x] Run `tests/conformance/test_part_instance_index.py` → #1,#2,#4,#7,#8 pass (not skipped).

**Automated (plain venv):**
- [x] `uv run pytest tests/conformance/test_part_instance_index.py` → **deviation:** the plain
      codegen venv turns out to have a live syside license available too (contrary to the plan's
      assumption and the older "no -c license" memory) — all 10 live tests **pass** here, not
      skip. Re-confirmed independently via the licensed sibling env command: same 10/10 pass.
      No collection failures either way.
- [x] `uv run mypy src/` and `uv run ruff check src/ tests/` → mypy clean (77 baseline, unchanged,
      none in new files). Ruff: the new files themselves are clean; `tests/` as a whole has a
      pre-existing baseline of 316 errors confirmed present at the Phase-1 commit tip (before any
      Phase-2 file existed) — out of this item's scope, not a regression.

**What We Know Works After This Phase:** closure projection finds the plain subtype; identity is
entry-independent; same-named members are separated by owning def; Cartesian and closure×
multiplicity expand correctly; results are deterministic across live loads.

---

## Phase 3 — Live blocking, additive/byte-identity, and final gates

### Goal
Prove non-finite shapes block with a named diagnostic, prove the item is inert against the
existing corpus, and pass all final gates.

### Assumption Under Test
Every non-finite multiplicity on a queried path raises `NonFiniteCardinalityError` naming owner
and feature (INV-2, no third arm), and the new code perturbs no existing artifact (INV-1).

### Test Stencil (Write This First)
```python
@requires_license
@pytest.mark.parametrize("leaf,owner,feature", [
    ("…LeafN", "…BlockHost", "n_member"),        # [n] parameterized
    ("…LeafStar", "…BlockHost", "star_member"),  # [*] unbounded
    ("…LeafRange", "…BlockHost", "range_member"),# [0..5] range
    ("…LeafOrdered", "…BlockHost", "ordered_member"),  # [3] ordered
])
def test_blocking_names_owner_and_feature(instance_index_model, leaf, owner, feature):
    with pytest.raises(NonFiniteCardinalityError) as e:
        list(idx.occurrences_of(leaf))
    assert owner in str(e.value) and feature in str(e.value)
```

### Changes Required
**See `design.md` for:** D4 diagnostic, INV-1 additive, `#validation-approach` #3/#5.

- [x] **#3 blocking (live):** implemented in Phase 2's `test_blocking_names_owner_and_feature`
      (parametrized over the four load-safe shapes) — folded into the single conformance test
      file rather than split across phases, since Phase 2 already needed the same fixture and
      `@requires_license` scaffolding. Each query reaches exactly one blocked member (distinct
      leaf types), so the raised diagnostic names that owner+feature unambiguously. (nonunique is
      covered by the Phase-1 mock-node truth table.)
- [x] **#5 additive guard (plain venv, license-free):** `tests/unit/test_part_instance_index_additive.py`
      — AST-scans `src/sysml_codegen/**/*.py` (excluding `part_instance_index.py` itself) for any
      `import`/`from` of the module and asserts none. Passes.
- [x] **Byte-identity of the corpus:** confirmed via `git status --porcelain` — only new files
      under `src/sysml_codegen/analysis/`, `tests/unit/`, `tests/conformance/`, and
      `tests/fixtures/instance_index_probe/`; zero modified existing artifacts/baselines.

### Validation (final gates — all must pass)
**Licensed env:**
- [x] `tests/conformance/test_part_instance_index.py` — all of #1,#2,#3,#4,#7,#8 pass (not
      skipped) — confirmed in Phase 2.

**Plain venv:**
- [x] `uv run pytest tests/` → 2161 passed, 4 skipped (full suite green; no regressions).
- [x] `uv run mypy src/` → 77 errors (baseline unchanged; none in new files).
- [x] `uv run ruff check src/` → clean. `tests/` as a whole carries a pre-existing 316-error
      baseline (confirmed present at the Phase-1 commit tip, before any Item-4 test file existed)
      — out of this item's scope; the new test files themselves are individually clean.
- [x] **Byte-identity:** `git status --porcelain` shows only additions under
      `src/sysml_codegen/analysis/`, `tests/unit/test_part_instance_index.py`,
      `tests/unit/test_part_instance_index_additive.py`, `tests/conformance/test_part_instance_index.py`,
      and `tests/fixtures/instance_index_probe/` — no modified existing file. (Additive [HARD],
      criterion #5.)

**What We Know Works After This Phase:** non-finite shapes block loudly with owner+feature; the
corpus regenerates byte-identically; the item is complete and inert until Item 5 wires it.

---

## Environment Setup
See CLAUDE.md for install/test/type/lint. The two-environment split (plain venv vs licensed
sibling env) is stated once under **Implementation Strategy** above; every live-test phase runs
through the licensed-env command there.

## Risk Management
See `design.md#potential-risks`. Phase-specific:
- **Phase 1:** live `LiteralInteger` value accessor is mock-unproven — confirm via a one-line
  `probe_b1_multiplicity.py` extension in the licensed env before writing the value read.
- **Phase 2:** the walker must mirror `_find_instantiation_paths` without refactoring it (INV-1)
  and must replicate the `_visited` cycle guard; the 9-oracle set is the exact spelling gate.
  Extension shapes must use type families disjoint from ConstrainedLeaf or the 9-oracle breaks.
- **Phase 3:** licensed-env pytest availability is unconfirmed — Phase 2 gates on a collection
  check with a standalone-runner fallback; `nonunique` stays out of the live fixture (load error).

## Implementation Notes
[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-07-12
**Actual Changes:**
- New `src/sysml_codegen/analysis/part_instance_index.py`: `PathStep`, `Fixed`, `NonFinite`,
  `NonFiniteCardinalityError`, `classify_cardinality`. `InstanceOccurrence` deferred to Phase 2
  per plan.
- New `tests/unit/test_part_instance_index.py`: 8 truth-table tests, one per B1 row, mirroring
  the `test_hierarchy_resolver.py` mock-node idiom.
- Extended `probe_b1_multiplicity.py`'s `describe()` already prints `.value` for lower/upper
  bound sub-attributes (no new line needed); ran it live via the licensed sibling env
  (`UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache uv run --directory /home/reid/1cfe/agentic-mbse
  python <abs path to probe_b1_multiplicity.py>`) and confirmed `upper_bound.value == 3` for the
  `fixed3` usage's `LiteralInteger` node — the accessor the classifier reads. Output matches
  `b1-probe-evidence.md` exactly for all 8 shapes.
**Issues:** None.
**Deviations:** None — `.value` was the confirmed accessor, as `expression_utils.py` and
`parameter_groups.py` already use for `LiteralInteger` elsewhere in this codebase.

**Gates:** `uv run pytest tests/unit/test_part_instance_index.py` → 8/8 pass. `uv run mypy src/`
→ 77 errors (baseline unchanged, none in the new file). `uv run ruff check
src/sysml_codegen/analysis/part_instance_index.py tests/unit/test_part_instance_index.py` →
clean.

### Phase 2 Completion
**Completed:** 2026-07-12
**Actual Changes:**
- `part_instance_index.py`: added `_cardinality_indices`, `_structured_paths` (mirrors
  `_find_instantiation_paths`, keeping structured `PathStep`s and gating every step's
  multiplicity, not just the leaf), `InstanceOccurrence` (+ `instance_path`), `_occurrence_sort_key`,
  `PartInstanceIndex` (`occurrences_of`, `all_occurrences`, `all_source_owners`,
  `_leaf_part_def_qn`), and `build_part_instance_index`.
- New `tests/fixtures/instance_index_probe/model.sysml` + `PROVENANCE.md`: the S3 model verbatim,
  plus disjoint-type-family extensions for collision, `[3..3]`, Cartesian, closure×multiplicity,
  and blocking (nonunique excluded — load-error risk, per plan). Confirmed loads with zero
  diagnostics errors via the licensed env before writing the walker.
- New `tests/conformance/test_part_instance_index.py`: 10 live tests covering #1, #2, #4, #7, #8,
  and parametrized #3 (4 blocking shapes).
**Issues:**
- `all_occurrences()` initially raised `NonFiniteCardinalityError` when the determinism test
  called it against the fully-extended fixture (which now also carries the Phase-2 blocking
  shapes) — see the Phase-1-section deviation note above for the fix (catch-and-skip per def,
  since it's a bulk convenience, not the direct per-owner query INV-2 governs).
**Deviations:**
- The plain codegen venv has a live syside license available (see Validation notes) — the plan's
  "live tests skip in the plain venv" assumption doesn't hold here, but the licensed sibling env
  independently confirms the same 10/10 pass, so the phase's live-positive-test intent is met
  either way.
- `all_occurrences()` scoping (see Issues above) — **later adjudicated a real defect by audit and
  cured post-audit**; see the "Cure (post-audit)" entry after Phase 3 Completion below.

**Gates:** `uv run pytest tests/` → 2160 passed, 4 skipped (2142 baseline + 18 new). `uv run mypy
src/` → 77 (baseline, unchanged). `git status --porcelain` → only new/additive paths under
`src/sysml_codegen/analysis/`, `tests/conformance/`, `tests/fixtures/instance_index_probe/`; no
existing file modified.

### Phase 3 Completion
**Completed:** 2026-07-12
**Actual Changes:**
- New `tests/unit/test_part_instance_index_additive.py`: AST-based scan of
  `src/sysml_codegen/**/*.py` asserting no production module imports `part_instance_index`
  (INV-1). Blocking (#3) was already implemented and proven in Phase 2's combined conformance
  file, so no separate test file was added for it here.
**Issues:** None.
**Deviations:** #3 blocking folded into Phase 2's file rather than a distinct Phase 3 file (see
Changes Required above) — same fixture and `@requires_license` scaffolding, no benefit to
splitting.

**Gates (all green):** `uv run pytest tests/` → 2161 passed, 4 skipped. `uv run mypy src/` → 77
(baseline, unchanged). `uv run ruff check src/` → clean; `tests/` pre-existing 316-error baseline
unrelated to this item. `git status --porcelain` → only additive paths.

**Item 4 is complete.** `PartInstanceIndex`/`build_part_instance_index` are built, tested, and
inert — importable and exercised only by this item's own tests; Item 5 wires them in.

### Cure (post-audit): `all_occurrences()` / `all_source_owners()` silent-skip
**Completed:** 2026-07-12 (same day, follow-up commit after audit)
**Source:** `audit.md`, priority finding — Certify-with-notes, one required must-fix.

**What changed:**
- `all_occurrences()` now returns `AllOccurrencesResult(occurrences: list[InstanceOccurrence],
  blocked: dict[str, str])` instead of a bare list. A `NonFiniteCardinalityError` hit while
  enumerating a given PartDef is caught and recorded as `blocked[part_def_qn] = str(error)`
  instead of being silently swallowed.
- `all_source_owners()` now returns `SourceOwnersResult(owners: list[str], blocked: dict[str,
  str])`, carrying the same `blocked` mapping forward (it is a thin wrapper over
  `all_occurrences()`).
- `occurrences_of()` is unchanged — it was already correct per the audit.
- `test_determinism` updated to assert on `.occurrences` and `.blocked` across two fresh loads.
- New test `test_all_occurrences_surfaces_blocked_definitions` asserts a blocked definition
  (`LeafN`) appears in `blocked` (naming its owner and feature), contributes zero entries to
  `occurrences`, and that unrelated occurrences (`CartLeaf`) are still present — proving the dump
  is honest about what it drops rather than either hiding it or aborting wholesale.
- `design.md`'s API section updated to match, marked "cured post-audit."
- `audit.md`'s priority finding now has a checked cure box recording Option 1 was applied.

**Scope:** additive/behavior-preserving-for-callers-who-check — only `part_instance_index.py`,
`tests/conformance/test_part_instance_index.py`, `design.md`, and `audit.md` touched. No existing
file outside Item 4's own artifacts modified. Nothing calls `all_occurrences()` /
`all_source_owners()` outside this item's own tests (INV-1 holds).

**Execution note (unresolved — needs orchestrator/user follow-up):** this session's sandbox
returns "requires approval" for every `uv`, `python3`, and `pytest` invocation, with no
interactive user available to grant it in this pass — the same constraint `audit.md`'s
"Execution note" already documented for the original implementation. **The 10 (now 11)
conformance tests, the full suite, mypy, and ruff were not re-run in this pass** — they are
restated as `audit.md` Probe E for the orchestrator/user to run and append before Item 5 consumes
the surface. The code change itself was verified by hand (types, control flow, and the two
touched call sites), not by execution.

---

**Status:** Draft → In Progress → Complete → Cured (execution gates pending re-run, see Probe E)
