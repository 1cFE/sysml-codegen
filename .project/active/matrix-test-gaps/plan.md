# Implementation Plan: Matrix Test-Gap Authoring (REQ-DM-08, REQ-RES-05, REQ-RES-08)

**Status:** Draft
**Created:** 2026-07-07
**Last Updated:** 2026-07-07
**Epic:** TRUTH-DEBT, Item 3 (SC-C) — `.project/backlog/epic_truth_debt.md:272`

## Source Documents
- **Spec:** `.project/active/matrix-test-gaps/spec.md` ← the mechanism decisions live here (Route A, the canonical enforced surface, the RES-08 reframe, the Item-2 climb re-check). This item has **no design stage** (epic deliverables are `{spec,plan}.md`).
- **Spec review:** `.project/active/matrix-test-gaps/spec-review.md` — Revise verdict; all four findings resolved into the spec (DM-08 mechanism = AST, RES-08 reframe committed, enforced surface pinned canonical, Item-2 climb made concrete).
- **Epic:** `.project/backlog/epic_truth_debt.md` — Item 3 + R1–R4 (`:114-146`).

---

## Implementation Strategy

**What this item is.** Three verification-matrix rows are `UNTESTED` with an argument, not a test. Author one independently-anchored pinning test per row, flip the three rows `UNTESTED → PASS`, and land the two INV-B text reframes (DM-08, RES-08) plus the `[DM08-MODEL-FIELD-TYPING]` backlog filing **in the same change** (R1). It is test-authoring plus a matrix/text/doc reframe — **zero `src/` changes expected**. If a test exposes a real bug, file it, don't fix it (Non-Goals).

**Phasing Rationale.** One phase per test, ordered by risk and by mechanism reuse, then a final coordinated truth-move + gates:

- **Phase 1 (DM-08)** first — it is independent, lowest-risk, and it stands up the **AST-scan mechanism** (`inspect.getsource` + `ast`, the sibling pattern at `test_orchestrator.py:97-117`) that Phase 2 reuses. Proving the AST mechanism early de-risks the two source-scan tests.
- **Phase 2 (RES-05)** next — independent, and it reuses the exact sibling helper `_get_call_lines_in_function` (`test_orchestrator.py:97`). The documented-milestone → real-call-name map is resolved below so the anchor set is unambiguous.
- **Phase 3 (RES-08)** last — the highest-risk row: cross-cutting, three divergent per-path mechanisms, real cross-part fixtures, and the landed Item-2 ancestor-climb leg to confirm and pin. Do it once the two cheaper tests are green.
- **Phase 4 (coordinated truth-move + gates)** — flip the three rows, land both reframes, file the backlog entry, reconcile the matrix counts, run the gates. This is the "R1: row/text/doc/backlog move together" phase; it lands atomically with Phases 1–3 (one commit for the whole item).

**Critical Path.** Phase 1 proves the AST mechanism → Phase 2 reuses it → Phase 3 (independent of 1/2 but riskiest) → Phase 4 flips + reconciles + gates. Phases 1–3 can be authored in any order; the ordering above is by de-risking, not hard dependency.

**First Proof Point.** Phase 1's DM-08 AST scan goes **red** under the named mutation (`_scoped` re-annotated to `dict[str, str]`) and **green** on revert. That single red→green transition proves the whole item's mechanism is honest — it is the exact thing a `get_type_hints` test would get wrong (spec [HARD], `spec.md:154-161`).

**Overall Validation Approach.**
- Each phase authors its test, then runs a **mutation spot-check**: deliberate production mutation → RED → revert → GREEN, recorded in Implementation Notes below (SC, `spec.md:137`).
- **R1 anti-vacuity:** every expected value is hand-authored (the enumerated NewType set, the documented sequence, a hand-transcribed `segments[1:-1]` scope) — never computed from the code under test.
- **Do NOT run the full suite** while authoring (a parallel implement is running). Run only the new test files node-scoped (`pytest tests/conformance/test_x.py -k ...`). The full-suite green gate is Phase 4, run once at the end.

---

## Phase 1: REQ-DM-08 — AST-scan the enforced surface

### Goal
Pin the **enforced surface** (the one canonical definition, `spec.md:77-89`) with a source/AST-scan static test, so REQ-DM-08 can flip to PASS honestly. First because it is independent and stands up the AST mechanism Phase 2 reuses.

### Assumption Under Test
The enforced surface — the NewType wrappers, the four `OutputRegistry` registry-dict annotations, and the two `make_*` return annotations — is pinnable by AST scan and goes red under the named registry-annotation mutation (where `get_type_hints` would stay green). The spec asserts this ([HARD], `spec.md:154-161`); Phase 1 proves it.

### Test Stencil (Write This First)
```python
# tests/conformance/test_dm08_enforced_surface.py  (NEW)
import ast, inspect, textwrap
from sysml_codegen.core import identifier_types, output_registry

@pytest.mark.req("REQ-DM-08")
def test_wrappers_are_newtype_over_base():
    # (a) runtime: each wrapper is a genuine NewType over its base
    assert identifier_types.SysMLQN.__supertype__ is str
    assert identifier_types.CanonicalChannel.__supertype__ is str
    assert identifier_types.ScopedKey.__supertype__ is str
    # ScopedAliasKey is NewType over tuple[str, str]
    assert identifier_types.ScopedAliasKey.__supertype__ == tuple[str, str]

@pytest.mark.req("REQ-DM-08")
def test_registry_dict_annotations_name_newtypes():
    # (b) AST-scan OutputRegistry.__init__ — the four PEP-526 self.x: dict[...] assigns.
    # Hand-authored expectation: dict-annotation -> (key NewType, value NewType).
    expected = {
        "_scoped": ("ScopedKey", "CanonicalChannel"),
        "_sysml_qn": ("SysMLQN", "CanonicalChannel"),
        "_alias": ("ScopedKey", "CanonicalChannel"),
        "_scoped_alias": ("ScopedAliasKey", "CanonicalChannel"),
    }
    src = textwrap.dedent(inspect.getsource(output_registry.OutputRegistry.__init__))
    # walk AnnAssign nodes; for each self.<name>: dict[K, V], assert K/V ids match expected
    ...

@pytest.mark.req("REQ-DM-08")
def test_make_constructor_return_annotations_name_newtypes():
    # (c) AST-scan make_scoped_key / make_canonical_channel return annotations
    for fn, ret in [("make_scoped_key", "ScopedKey"),
                    ("make_canonical_channel", "CanonicalChannel")]:
        ...  # assert the FunctionDef.returns id == ret
```

### Changes Required

**Mechanism ([HARD], `spec.md:154-161`):** AST, not `get_type_hints`. The registry annotations are PEP-526 `self._scoped: …` assignments inside `__init__` (`output_registry.py:48-55`) — they never reach any `__annotations__`, so a runtime-introspection test stays green under the named mutation. Use `inspect.getsource` + `ast`, the sibling pattern at `test_orchestrator.py:97-117`.

**Enforced surface (canonical, `spec.md:83-89`) — exactly three parts:**
- (a) wrappers are `NewType` over base: `identifier_types.py:24-39` (`SysMLQN/EQN/PQN/CanonicalChannel/ScopedKey` over `str`; `ScopedAliasKey` over `tuple[str, str]`).
- (b) four registry dict annotations in `OutputRegistry.__init__`: `_scoped`, `_sysml_qn`, `_alias`, `_scoped_alias` (`output_registry.py:48-55`).
- (c) return annotations of `make_scoped_key` / `make_canonical_channel` (`identifier_types.py:46,66`).

**Boundary — exclude `register_alias` ([HARD], `spec.md:196-201`; review L3-4).** `register_alias` takes `ScopedKey | str` / `CanonicalChannel | str` by design (`output_registry.py:102-104`). The canonical surface is keys/values + constructors, **not** method params — so a scan scoped to (a)/(b)/(c) excludes it by construction. Do **not** broaden the target set to registration-method params.

- [ ] `tests/conformance/test_dm08_enforced_surface.py` (NEW) — three tests per stencil; all expectations hand-authored.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_dm08_enforced_surface.py` → pass.
- [ ] `uv run ruff check tests/conformance/test_dm08_enforced_surface.py` → clean.

**Mutation spot-check (record in Implementation Notes):**
- [ ] Re-annotate `OutputRegistry._scoped` from `dict[ScopedKey, CanonicalChannel]` to `dict[str, str]` (`output_registry.py:48`) → `test_registry_dict_annotations_name_newtypes` goes **RED** (AST scan finds the annotation no longer names its NewTypes).
- [ ] Revert → **GREEN**. (This is the mutation that a `get_type_hints` test would pass unchanged — that is why the mechanism is AST.)

**What We Know Works After This Phase:** the AST-scan mechanism pins the enforced surface and is mutation-provable against the exact named production mutation.

---

## Phase 2: REQ-RES-05 — source-order pin of the inner five-milestone sequence

### Goal
Pin `build_computation_graph`'s **internal** five-milestone sequence (classify → build modules → rebuild groups → toposort → validate) on the **real** inner function, distinct from the outer `build_pipeline_context` pin (REQ-ORCH-01, `test_orchestrator.py:124`).

### Assumption Under Test
The five milestones are real, distinct, source-ordered calls in `build_computation_graph` and can be pinned by the same source-order helper the outer test uses, reusing `_get_call_lines_in_function` (`test_orchestrator.py:97`).

### Mechanism decision (resolved here — `spec.md:251-256` deferred it)
**Source-order pin**, reusing the sibling `_get_call_lines_in_function`. Rationale: it matches the sibling precedent (`test_orchestrator.py:149`), is robust to fixture variation, and needs no runtime fixture that exercises all five milestones. A call-sequence spy is the alternative but couples to a runtime run; the source-order pin is the cleaner, in-house-idiomatic choice and mirrors Phase 1's AST family. Place the new test **in `test_orchestrator.py`** (new `TestInnerStepOrdering` class) so it reuses the helper directly and sits beside the outer pin it must not duplicate.

### Documented-milestone → real-call-name map (resolved — [HARD], `spec.md:135-140`, `:262-267`)
The doc uses simplified names (`03-resolution-overview.md:203-205`) that do **not** match the code. The anchor set the source-order pin greps for is the **actual** calls, in this order:

| Documented milestone | Real call name(s) | Anchor |
|---|---|---|
| classify | `_classify_entry_points` | `graph_builder.py:222` |
| build modules | `_build_pipeline_module` / `_build_computed_attr_module` / `_build_aggregation_module` | `:247` / `:275` / `:312` |
| rebuild groups | `derive_groups()` (**not** a single `rebuild_groups` call — `derive_groups` + filtering) | `:326` |
| toposort | `_unified_topological_sort` | `:388` |
| validate | `_validate_channel_references` | `:392` |

Assert first-occurrence ordering across these anchors (`classify` before any build call; the last build call before `derive_groups`; `derive_groups` before `_unified_topological_sort`; that before `_validate_channel_references`). Every milestone appears at least once.

### Test Stencil (Write This First)
```python
# tests/conformance/test_orchestrator.py  (ADD — new class, reuses _get_call_lines_in_function)
class TestInnerStepOrdering:
    """REQ-RES-05: build_computation_graph()'s internal milestones in source order."""

    @pytest.mark.req("REQ-RES-05")
    def test_inner_step_ordering_source(self):
        milestones = [
            ["_classify_entry_points"],
            ["_build_pipeline_module", "_build_computed_attr_module", "_build_aggregation_module"],
            ["derive_groups"],
            ["_unified_topological_sort"],
            ["_validate_channel_references"],
        ]
        flat = [c for group in milestones for c in group]
        lines = _get_call_lines_in_function(build_computation_graph, flat)
        for group in milestones:                 # each milestone present
            assert any(lines[c] for c in group), f"missing milestone: {group}"
        firsts = [min(min(lines[c]) for c in group if lines[c]) for group in milestones]
        assert firsts == sorted(firsts), f"milestones out of source order: {firsts}"
```

### Changes Required
- [ ] `tests/conformance/test_orchestrator.py` (MODIFY) — add `TestInnerStepOrdering`; import `build_computation_graph` if not already imported. Must **not** re-pin `build_pipeline_context` (the outer test at `:124` owns REQ-ORCH-01).

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_orchestrator.py -k InnerStepOrdering` → pass.
- [ ] `uv run ruff check tests/conformance/test_orchestrator.py` → clean.

**Mutation spot-check (record in Implementation Notes):**
- [ ] In `build_computation_graph`, move the `_unified_topological_sort` call (`graph_builder.py:388`) **above** the module-build region (`:247`) → source-order assertion goes **RED**.
- [ ] Revert → **GREEN**.

**What We Know Works After This Phase:** the inner five-milestone sequence is pinned on the real inner function, distinct from and non-duplicating the outer DAG pin.

---

## Phase 3: REQ-RES-08 — per-path consumer-scope pin over `plant_values` (incl. Item-2 climb)

### Goal
Enumerate the live resolution paths — backtracker (CalcUsage) **base leg + landed ancestor-climb leg**, aggregation, and FORMULA — and assert consumer-scope derivation on each, every expectation written **independently** of the code under test (R1), over the `plant_values` cross-part fixtures. Highest-risk row; last.

### Assumption Under Test
Each of the (now four) enumerated legs applies **the consumer's scope**, and each can be pinned with a hand-authored expectation over a real cross-part fixture — including the Item-2 climb leg, whose "Step CLIMB" block is present at implement HEAD.

### Mechanism decision (resolved here — `spec.md:227-235` deferred it)
**Per-path value assertions with hand-transcribed expectations** (spec family (a): observe the scope string / scoped-key each path constructs; compare to a hand-authored expectation). Chosen over outcome-level (family (b)) because the FORMULA arm derives **no** `consumer_scope` string — a value-level per-path assertion states each arm's real mechanism honestly, where an outcome-level unification would blur the divergence the reframe is committing to name. The three (four-leg) arms:

1. **Backtracker base leg** — `_consumer_scope_dotted(usage)` (`dependency_backtracker.py:450`, `segments[1:-1]` at `:460`). Pick a `plant_values` cross-part CalcUsage; hand-transcribe its expected dotted scope from the usage QN's `segments[1:-1]`; assert equality.
2. **Backtracker climb leg (Item 2, landed)** — the "Step CLIMB" ancestor loop in `_resolve_chain_dispatch` (`dependency_backtracker.py:652-682`; loop `:675`; single-match guard `:681`). For a deep CHAIN whose reference lives in an ancestor scope, the hand-authored expectation is the channel found **at the ancestor scope**. See the concrete re-check below.
3. **Aggregation** — `ResolutionContext.consumer_scope` derived at `graph_builder.py:1383` (`agg_parts[1:-1]`). Hand-transcribe the expected dotted scope for a `plant_values` aggregation; assert the derived `consumer_scope` equals it.
4. **FORMULA** — owning-part-keyed scope: `_build_attribute_resolution_map` keys on `ca.owning_part_name`; `module_eqn` from `ca.owning_part_qualified_name` (`graph_builder.py:923-985`, esp. `:966`). Assert the FORMULA arm scopes by the consumer's **owning-part QN** (for a computed attribute, owner = consumer), **not** a dotted `consumer_scope` string. Asserting a shared mechanism across arms would be a false pin ([NEED], `spec.md:186-195`).

### Item-2 climb re-check (concrete — `spec.md:237-249`; review L3-2)
This is a **confirmation, not a fork** (the climb landed at `91e073f`). At implement HEAD, before authoring leg 2:
- [ ] Grep `_resolve_chain_dispatch` for the **"Step CLIMB"** block (`dependency_backtracker.py:652-682`): the ancestor loop `for i in range(len(scope_segments), -1, -1)` (`:675`) and the ambiguity guard `if len(climbed) == 1` (`:681`). Confirm both present (line numbers may have shifted as Item 2 closed out — re-grep, don't trust the number).
- [ ] **Fixture check for the climb leg (real risk).** Confirm `plant_values` (or `plant_value_shapes`) actually contains a deep CHAIN whose reference resolves via the ancestor climb. If **neither** exercises CLIMB: the climb leg's substrate is the fixture that does — prefer a registered cross-part CHAIN fixture (`chain_override_probe` is session-registered, `conftest.py`), else read the deep-chain graph directly as `test_deep_cross_scope_probe.py` does (note `deep_cross_scope_probe` is deliberately **not** session-registered — `conftest.py:56-62`). Record which fixture backs leg 2. Never mock (R1, [HARD] `spec.md:179-181`).
- [ ] If a later Item-2 phase reverted/reshaped the climb, adjust the climb-leg expectation to match HEAD (or, if fully reverted, drop leg 2 and note it). Do not assert a climb the code no longer does.

### Test Stencil (Write This First)
```python
# tests/conformance/test_res08_consumer_scope_paths.py  (NEW)
# Real fixtures only (R1). plant_values cross-part substrate; a genuine consumer≠producer scope gap.

@pytest.mark.req("REQ-RES-08")
def test_backtracker_base_leg_scopes_to_consumer(plant_values_snapshot):
    bt = ...  # drive the real backtracker over plant_values
    usage = ...  # a known cross-part CalcUsage
    expected = ".".join(usage.qualified_name.split("__")[1:-1])  # hand-transcribed, not from _consumer_scope_dotted
    assert bt._consumer_scope_dotted(usage) == expected

@pytest.mark.req("REQ-RES-08")
def test_backtracker_climb_leg_finds_ancestor_channel(...):
    # deep CHAIN: expected = channel at the ancestor scope (hand-authored)
    ...

@pytest.mark.req("REQ-RES-08")
def test_aggregation_leg_carries_consumer_scope(plant_values_snapshot):
    # expected dotted scope hand-transcribed from agg module_eqn segments[1:-1]
    ...

@pytest.mark.req("REQ-RES-08")
def test_formula_leg_scopes_by_owning_part_qn(plant_values_snapshot):
    # FORMULA scopes by owning-part QN, NOT a dotted consumer_scope string
    ...
```

### Changes Required
- [ ] `tests/conformance/test_res08_consumer_scope_paths.py` (NEW) — four legs (base, climb, aggregation, FORMULA), each with an independently hand-authored expectation over real `plant_values` (+ climb fixture per re-check). Reuse the fixture-loading pattern from `tests/conformance/conftest.py` (`extraction_snapshots`, `snapshot_fixture`) and the scope-derivation precedent in `test_dual_resolution.py`.
- [ ] **If any leg EXPOSES a real bug** (e.g. a path that does not in fact scope to the consumer): file it explicitly with a matrix pointer, do **not** fix inline (Non-Goals, `spec.md:213-216`). A leg that reveals a bug does not flip its row to PASS — surface it in the close-out.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_res08_consumer_scope_paths.py` → pass.
- [ ] `uv run ruff check tests/conformance/test_res08_consumer_scope_paths.py` → clean.

**Mutation spot-check (record in Implementation Notes) — one per class of leg:**
- [ ] Hardcode `_consumer_scope_dotted` to return `""` (`dependency_backtracker.py:450`) → base-leg assertion **RED**; revert → GREEN.
- [ ] Disable the climb (short-circuit the ancestor loop) or remove the `len(climbed) == 1` guard (`dependency_backtracker.py:675,681`) → climb-leg assertion **RED**; revert → GREEN.
- [ ] (Optional, if cheap) hardcode aggregation `consumer_scope=""` (`graph_builder.py:1383`) → aggregation-leg **RED**; revert → GREEN.

**What We Know Works After This Phase:** each enumerated resolution path applies the consumer's scope, pinned independently over real fixtures, with the landed Item-2 climb leg included.

---

## Phase 4: Coordinated truth-move + gates (R1 — row/text/doc/backlog together)

### Goal
Land the matrix flips, both INV-B reframes, and the backlog filing **in the same change** as the three tests (R1, [HARD] `spec.md:202-205`), then run the final gates. This is one atomic item (one commit); Phases 1–3 do not land separately.

### Changes Required

**1. Flip the three matrix rows `UNTESTED → PASS` with new citations** (`docs/architecture/verification-matrix.md`):
- [ ] REQ-DM-08 (`:165`) → PASS, cite `test_dm08_enforced_surface.py`; **reframe the row text** to the enforced-surface claim (the typed-registry surface uses NewType wrappers), citing `09-data-models.md:104` as the pre-existing admission that the model fields are not yet typed (`spec.md:68-75`).
- [ ] REQ-RES-05 (`:464`) → PASS, cite `test_orchestrator.py` (`TestInnerStepOrdering`). **No text reframe** — RES-05's text is accurate as written (Non-Goals, `spec.md:222`).
- [ ] REQ-RES-08 (`:467`) → PASS, cite `test_res08_consumer_scope_paths.py`; **reframe the row text** to the honest three-mechanism per-path claim — drop the false "via `ResolutionContext.consumer_scope`" universal; use the reframe target verbatim from `spec.md:114-120` (base leg + climb leg + aggregation + FORMULA owning-part; "per-path scope application over the enumerated paths, not an exhaustiveness proof").

**2. Update the "Untested Requirements" summary block** (`verification-matrix.md:544-547`):
- [ ] Remove the DM-08, RES-05, RES-08 bullets (they are now PASS). **REQ-PGD-06 stays** (`:545`) — it is not this item's row (Non-Goals, `spec.md:217-219`).

**3. Reconcile the index counts (recount FROM the rows — memory `verification-matrix-drift-modes`)** (`verification-matrix.md:9-11`):
- [ ] UNTESTED `4 → 1` (only REQ-PGD-06 remains); PASS `249 → 252`; Total `253` unchanged. **Recount by grepping the row table**, not by editing the summary block to match an assumption. Verify: `grep -c "| UNTESTED |"` over the row table == 1; PASS count + UNTESTED + any other == 253.

**4. Doc consistency (R1 close-the-loop):**
- [ ] `09-data-models.md` — ensure the DM-08 reframe is consistent with the existing open-status admission at `:104` (no contradiction; the model fields remain documented as bare `str` with the deferral pointer).
- [ ] `03-resolution-overview.md:70` — apply the RES-08 row-text reframe here too (the matrix row and this doc row must agree). Check `:185-206` (the RES-05 documented sequence) needs **no** change.

**5. File `[DM08-MODEL-FIELD-TYPING]` in BACKLOG** (`.project/backlog/BACKLOG.md`):
- [ ] New P3 entry, placed near the other typed-surface / graph_builder P3 filings (e.g. after `[GB-PARAMGROUPS-TYPING]` `:387`). Content: the still-open model-field typing (`EntryPoint.qualified_name`, `InputSource.qualified_name` / `producer_channel`, `ModuleOutput.channel_name` in `resolution/models.py`), with the doc's own pointer (`09-data-models.md:104`), noting Route A deferred it out of the test-authoring item (`spec.md:74-75`).

### Validation (Final Gates — run ONCE, at the end)
**Automated:**
- [ ] `uv run pytest tests/` → **full suite green** (only now — a parallel implement runs during authoring; do not run the full suite before this phase).
- [ ] `uv run ruff check src/ tests/` → **≤ 17** findings.
- [ ] `uv run mypy src/` → **≤ 97** findings.
- [ ] **Baselines byte-identical** — no baseline touch expected (test-only item). Confirm `git status` shows **zero** changes under `tests/fixtures/baseline_outputs/` and no snapshot churn. If any baseline moved, stop — a `src/` change leaked in (this item expects zero `src/` changes).

**Manual:**
- [ ] `git diff --stat` over `src/` → **empty** (zero production changes; mutations all reverted).
- [ ] Recount reconciles: matrix summary counts == counts derived from the rows.

**What We Know Works After This Phase:** three rows pin their text honestly and PASS; both reframes and the backlog filing landed with the tests; the matrix is internally consistent; the suite is green and baselines are untouched.

---

## Environment Setup
**See CLAUDE.md.** Node-scope test runs during authoring (`uv run pytest tests/conformance/test_x.py -k ...`); full suite only at Phase 4. `plant_values` snapshot is license-free (captured fixture at `tests/fixtures/plant_values/extraction_snapshot.json`), loaded via `snapshot_fixture` (`tests/conftest.py:45`) / the `extraction_snapshots` session fixture (`tests/conformance/conftest.py`).

---

## Risk Management

**Phase-Specific Mitigations:**
- **Phase 1 (DM-08):** the trap is reaching for `get_type_hints` (the obvious "static test"), which passes unchanged under the named mutation. Mechanism is **AST** — the mutation spot-check is the guard: if the `_scoped → dict[str,str]` mutation does not go red, the mechanism is wrong.
- **Phase 2 (RES-05):** do not re-pin `build_pipeline_context` (owned by the outer test). Use the milestone→call-name map — `rebuild groups` is `derive_groups()`, not a `rebuild_groups` call.
- **Phase 3 (RES-08):** two live risks — (a) **false uniform pin**: the four legs do not share one derivation; assert each independently, never "they call one shared function" ([NEED], `spec.md:186-195`); (b) **climb-leg fixture**: `plant_values` may not exercise CLIMB — the re-check names the fallback fixture. If a leg exposes a real bug, file don't fix.
- **Phase 4:** recount **from the rows**, not by trusting the summary block (memory `verification-matrix-drift-modes`: index counts and missing families are the real drift). Byte-identity gate catches any leaked `src/` change (memory `byte-identity-captured-at-churn`).

**Cross-cutting:** R1 anti-vacuity — every expected value hand-authored. Non-Goals — zero behavior/code changes; a test that exposes a bug is filed, not fixed.

## Implementation Notes

**Execution mode:** implemented directly by the orchestrator (the account's weekly
usage limit killed delegated headless sessions mid-epic). Same plan, same gates.

### Phase 1 Completion (DM-08)
**Completed:** 2026-07-07 — `tests/conformance/test_dm08_enforced_surface.py` (3 tests).
**Mutation spot-check (red→green):** `_scoped` re-annotated `dict[str, str]` →
`test_registry_dict_annotations_name_newtypes` RED; revert → 3/3 GREEN. (Exactly the
mutation `get_type_hints` would miss — PEP 526.)
**Deviations:** none.

### Phase 2 Completion (RES-05)
**Completed:** 2026-07-07 — `TestInnerStepOrdering` in `test_orchestrator.py`.
**Mutation spot-check (red→green):** swapped `_validate_channel_references` above
`_unified_topological_sort` → RED; revert → GREEN.
**Deviations:** strengthened beyond the stencil — ALL three factory calls must sit inside
the classify..derive_groups window (a single `min()` would let one drift).

### Phase 3 Completion (RES-08)
**Completed:** 2026-07-07 — `tests/conformance/test_res08_consumer_scope_paths.py` (4 legs).
**Item-2 climb re-check:** Step CLIMB present (`dependency_backtracker.py:672-682`); neither
plant fixture exercises it, so leg 2 loads `deep_cross_scope_probe` directly (the
`chain_analysis` deep chain — resolves only at the ancestor scope; the test also asserts
the consumer's own scope key MISSES, proving the climb is load-bearing).
**Mutation spot-checks (red→green):** (1) `_consumer_scope_dotted` hardcoded `""` →
base-leg RED; (2) climb gate short-circuited → climb-leg RED; both revert → 4/4 GREEN.
**Deviations / substrate:** per-leg fixtures instead of plant_values-only (plant_values has
one CalcUsage, zero aggregations, zero FORMULA attrs): base = plant_values + catf_mfe,
climb = deep_cross_scope_probe, aggregation = solar_battery (whole-plant `capital_cost`;
the test proves the unscoped key misses while the consumer-scoped key wires), FORMULA =
attr_expr_probe. Aggregation leg is outcome-level (the wired channel) because the ctx is
factory-local — the consumer-scope prefix is still the thing proven. Hand-derivation
correction recorded: a child-aggregation channel repeats the attribute segment
(`{instance_path}__{attr}__{attr}`) because the module EQN is `{instance_path}__{attr}`.
No bug exposed; nothing filed from test authoring.

### Phase 4 Completion (truth-move + gates)
**Completed:** 2026-07-07.
**Matrix recount (from rows):** 256 rows = 255 PASS + 1 UNTESTED (REQ-PGD-06). This also
resolved the 256-vs-255 summary discrepancy Item 5 flagged: the old block said 251 PASS + 4
UNTESTED = 255 ≠ 256 — the PASS count was undercounted by one; totals were right. Distinct
test files cited: 62 (44 conformance, 18 unit+integration) — summary + Related Documents
updated. Reframes: DM-08 (enforced surface) + RES-08 (per-path mechanisms incl. climb leg)
in matrix + docs 09/03; RES-05 text unchanged (accurate), its doc row now cites the pin.
`[DM08-MODEL-FIELD-TYPING]` filed. Bonus truth-fix: the stale conformance/conftest.py
comment still describing the retired Pattern-A truncation (Item-2 residue) rewritten.
**Gate results:** suite **2094 passed / 4 skipped / 0 xfailed** (+8 = 3 DM-08 + 1 RES-05 +
4 RES-08); ruff src **17** (≤17); mypy **97** (≤97); new test files lint-clean;
byte-identity clean (`git status` empty over `tests/fixtures/` and `src/`).

---

**Status:** Complete (all 4 phases, 2026-07-07)
