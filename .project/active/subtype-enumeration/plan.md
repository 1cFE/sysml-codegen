# Implementation Plan: Subtype-Aware Enumeration & Constraint-Report Truth

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06
**Epic:** PIPELINE-TRUTH, Item 4 (Track B head)

## Source Documents
- **Spec:** `.project/active/subtype-enumeration/spec.md` (decision table = the contract; 8 rows, success criteria)
- **Design:** `.project/active/subtype-enumeration/design.md` ← D1–D8, invariants INV-A..G, architecture, bets B1–B5
- **Design review:** `.project/active/subtype-enumeration/design-review.md` (MF1–MF6, M7–M9 — all FIXED, resolutions §Resolutions)
- **Discovery register:** `.project/research/20260706_pipeline-truth-discovery.md` §D4 (evidence base; agentic-mbse rows)
- **R4 probe:** `.project/active/subtype-enumeration/_probe.py` (codegen rows 1–2, authored + committed)

---

## Cross-Repo Ground Rules (read before any phase)

Two repos, two branches. Do not co-mingle.

- **sysml-codegen** — commit on **`pipeline-truth-epic`** (current branch). Editable-installed from the agentic-mbse checkout, so it sees agentic-mbse changes live once they land on the checked-out branch.
- **agentic-mbse** — canonical checkout **`/home/reid/1cfe/agentic-mbse`** (the only one; **not** `~/agentic-mbse` — stale). Currently on `upstream-findings-sync` at `7f77510`, clean tree, PR #7 OPEN. **Create the Item-4 companion branch `pipeline-truth-item4` from `7f77510`** and commit all agentic-mbse work there. Two unrelated untracked docs remain in the tree — leave them; never `git stash`, never stage them.
- **Commit discipline (both repos):** each commit message **leads with the decision** (e.g. "adapter: subtype-aware enumeration at one choke point (D1/D6)"), and ends with the `Co-Authored-By` line.
- **Suite green at every phase boundary in BOTH repos** (R2). State which suite(s) a phase touches.

## Sequencing & Item-1 Gate

The design's `[HARD]` order is **Item 1 impl → Item 4 impl → Item 2 impl**, one working tree, one regen at a time (spec §Constraint serialization; design D5 / Implementation Notes).

Only **one phase actually depends on Item 1: Phase 5** (the repo-wide re-capture, which uses Item 1's new `--fixtures` capture filter and re-captures Item 1's new fixtures). **Everything else is Item-1-independent:**

- **Phases 0–2 are agentic-mbse-side + the codegen live probe** — they can start immediately, even while Item 1 is still capturing.
- **Phases 3–4 are codegen-side, live/in-memory only** — they depend on Phase 1 (the adapter policy source), not on Item 1.
- **Phase 5 is the only Item-1-gated phase.** If Item 1 is still capturing when Phases 0–4 finish, **stop at the Phase 5 boundary and wait** for Item 1's implement to complete; do not re-capture early.

Dependency graph: `0 → 1 → {2, (3 → 4)} → 5 → 6 → 7`. Phase 2 (validators) and Phases 3–4 (codegen) both depend only on Phase 1 and are independent of each other — do them in either order or in parallel.

---

## Implementation Strategy

**Phasing rationale — de-risk the sandbox-blocked adapter first, then build outward from the one choke point:**

The whole mechanism rests on two beliefs the design could not confirm by reading agentic-mbse (sandbox-blocked at design time): **B1** (syside `nodes(include_subtypes=True)` returns the subtree; `is_instance` is hierarchy-aware) and **B2** (the three type names resolve in `TYPE_MAP` — *false today*, closed by D6). Phase 0 re-reads the adapter live and runs the probes, collapsing that uncertainty before any edit. Phase 1 lands the adapter foundation (D6 hard-error + params + policy source) — the single dependency of everything downstream. Then the two independent branches: agentic-mbse validators (Phase 2) and the codegen report (Phases 3–4). Phase 5 is the gated re-capture. Phases 6–7 close docs and the Item-9/register accounting.

**Critical path:** Phase 0 (verify) → Phase 1 (adapter) → Phase 3 (codegen report) → Phase 4 (serialization) → Phase 5 (re-capture, Item-1-gated).

**First proof point:** Phase 0 — `_probe.py` runs live and shows `report_dropped_constraints()` emitting **0** records on wi014_toy's assert (rows 1–2 CONFIRMED), and the agentic-mbse probes confirm rows 3/5/6/7. This is the failing-probe-before-fix evidence R4 demands.

**Biggest risk (design §Potential Risks):** the adapter's exact signature / decorator / `nodes` call / `TYPE_MAP` shape is unread. Mitigation: Phase 0 re-reads it first; the change is additive keyword-only params + three map entries + a guarded hard-error.

**Overall validation:** each phase starts with tests; each has a fires-on-shape **and** silent-on-clean pin (R1); mutation check discriminates (MF5); no mocks (R1) — live extractor + committed fixtures.

---

## Phase 0: R4 Verification-Table Completion (OPENER — MANDATORY)

### Goal
Reproduce every CONFIRMED-BLIND site with a live probe **before touching any code**, and re-read the agentic-mbse adapter to collapse the shape uncertainty. Update the design's R4 table and register §D4 in place. This is the R4 "the probe wins" gate.

### Assumption Under Test
B1 (subtype sweep + hierarchy-aware `is_instance`) and B2 (the three type names are absent from `TYPE_MAP` today, so `is_instance` no-ops silently). Both must be confirmed live before the design's mechanism is safe to build.

### Steps
- [x] **Create the agentic-mbse companion branch:** `git -C /home/reid/1cfe/agentic-mbse checkout -b pipeline-truth-item4 7f77510` (from `upstream-findings-sync` HEAD, clean tree). Confirm the two unrelated untracked docs are untouched. → DONE; branch at `7f77510`, the two untracked docs untouched.
- [x] **Re-verify all agentic-mbse line numbers live** — recorded in `register-update-pending.md`. Corrections: adapter `elements_of_type` classmethod `:196` (not `:214`); no module-level `TYPE_MAP` — map is `_get_type_map()` dict literal `:131-156` (register's `:244-246` = the `is_instance` lookup); `level3:48` ✓, `level4:113` ✓, `level6:602` + swallow `:603-604` (design said `:601`).
- [x] **Re-read the adapter shape** — methods are **`@classmethod`** (not staticmethod), serve both call forms. `include_subtypes` **is** a real param on the Python `Model.elements`/`nodes` wrapper (`syside/_loading.py:213`), default `False` → `all_nodes` vs `nodes`. The three names are **ABSENT** from the map (B2 false-today, confirmed live). **Discrepancy:** `elements_of_type` raises `KeyError`, NOT `ValueError` as the design claimed — Phase 1 must switch to ValueError.
- [x] **Run `_probe.py` live** — rows 1–2 CONFIRMED: exact `ConstraintUsage` = 0; swept (include_subtypes) = 1 = `AssertConstraintUsage` `affordable`; `is_instance(assert,"ConstraintUsage")` = True; `report_dropped_constraints()` emitted **0** records; `extract_all_constraints()` total = 0.
- [x] **Run the agentic-mbse probes** for rows 3/5/6/7 — CONFIRMED: `circular_import.sysml` → exact `Import` = 0, swept = 2 NamespaceImports, `build_dependency_graph` = `{}`, `detect_cycles` = `[]` (passes on a circular model); assert model → exact CU = 0, swept = 1; swallow present at `level6:603-604`. `MembershipImport` exposes `imported_membership` not `imported_namespace` (the `:58` guard bug).
- [x] **Re-run the zero-caller grep** — `extract_all_constraints`: only self-ref is `__all__` at `constraint_extractor.py:260`; `_deserialize_constraint_info`: zero references (dead). Safe to delete in Phase 3.
- [x] **Update the design R4 table + register §D4** — written to `register-update-pending.md` (sysml-codegen is read-only this session; Item 1 owns its commits). Rows 1–5 all CONFIRMED (live).

### Validation
- [x] Probe output recorded in `register-update-pending.md`; every row CONFIRMED live (none reclassified).
- [x] Companion branch exists at `7f77510`; dirty-workstream untracked docs untouched.
- [x] agentic-mbse baseline: **1212 passed, 1 skipped, 10 pre-existing infra failures** (5 shell out to a bare `python` binary absent from PATH; 3 need the `agentic-mbse` console script; 2 are pre-existing level2/level3 baseline-metric mismatches on `sample_models`). None caused by Item 4 (zero code changed at this point). This is the phase-boundary bar: no NEW failures beyond these 10.

**What We Know Works After This Phase:** the blindness is reproduced live at every site; the adapter's real shape is known; B2 is confirmed false-today (so D6 is load-bearing, not belt-and-suspenders).

---

## Phase 1: agentic-mbse Adapter Foundation (D6 + params + policy source)

### Goal
Land the one choke point everything depends on: subtype-aware sweep, exclusion capability, the single droppable-policy source, and the D6 hard-error that turns B2's silent no-op into a loud failure. **Commit on `pipeline-truth-item4`.**

### Assumption Under Test
That the adapter change is additive and backward-compatible (INV-A): defaults `include_subtypes=False`, `exclude=()` leave every current call site byte-for-byte unchanged; the only intentional behavior delta is D6 making a previously-silent unknown-name `is_instance` now raise.

### Test Stencil (Write This First — agentic-mbse suite)
```python
def test_is_instance_raises_on_unmapped_name(adapter, some_elem):
    # D6/INV-F: unknown type name is loud, not a silent False
    with pytest.raises(ValueError, match="unknown type name"):
        adapter.is_instance(some_elem, "NotARealType")

def test_elements_of_type_include_subtypes_sweeps_assert(adapter, assert_model):
    exact = list(adapter.elements_of_type(assert_model, "ConstraintUsage"))
    swept = list(adapter.elements_of_type(assert_model, "ConstraintUsage",
                                          include_subtypes=True))
    assert len(exact) == 0 and len(swept) >= 1          # the assert now appears

def test_is_droppable_excludes_requirement(adapter, req_model):
    reqs = [e for e in adapter.elements_of_type(req_model, "RequirementUsage",
                                                include_subtypes=True)]
    assert reqs and all(not adapter.is_droppable_constraint(r) for r in reqs)
```

### Changes Required
**See `design.md` for:** D6 (§Key Decisions), D1 (policy single-sourcing), §Architecture "Boundaries", INV-D/INV-F, Component Overview.

- [x] `syside_adapter.py` — `elements_of_type` gains keyword-only `include_subtypes: bool = False` (pass-through to `model.elements`) and `exclude: Collection[str] = ()` (subtype-aware `is_instance` filter). Preserved `@classmethod` (Phase-0 confirmed, not staticmethod).
- [x] `syside_adapter.py` — **D6:** `_get_type_map()` gains `AssertConstraintUsage`, `RequirementUsage`, `SatisfyRequirementUsage` **plus `InvocationExpression`** (used-but-unmapped, found via the C5 regression). Both methods raise `ValueError` on unknown name; shared `_require_known_type` helper; `elements_of_type` KeyError→ValueError; `is_instance` gate before the mock fallback (and after the `ImportError`/no-syside path).
- [x] `syside_adapter.py` — module-level `EXCLUDED_CONSTRAINT_TYPES = ("RequirementUsage",)` + `is_droppable_constraint(elem)`. Single production location of `"RequirementUsage"` (INV-D).
- [x] `syside_adapter.py` class docstring — teaches the subtype-enumeration decision table + D6.

### Validation
- [x] Fires-on-unknown-name pin passes (both methods) + unknown-exclude-name pin.
- [x] `include_subtypes=True` sweep includes the assert; default (False) sees only the plain constraint.
- [x] `exclude=EXCLUDED_CONSTRAINT_TYPES` drops the requirement, keeps assert+plain; `is_droppable_constraint` == the exclude filter (INV-D cross-check).
- [x] INV-A regression sweep: full suite back to the 10 pre-existing failures (1220 passed, +8 new). One transient regression (`test_c5_function_invocation_warns`) caught + fixed by mapping `InvocationExpression`. ruff clean; mypy delta zero (4 pre-existing `no-any-return` at the syside boundary, unchanged).
- [x] Commit `64a097e` on `pipeline-truth-item4`.

**What We Know Works After This Phase:** the choke point exists, is opt-in, and fails loud on an unmapped name. B2 is closed. Downstream (Phases 2–4) can build on it.

---

## Phase 2: agentic-mbse Validators — rows 5/6/7 + D7 swallow fix

### Goal
Fix the three blind validators using the Phase 1 adapter; remove the level6 swallow (D7) so the row-7 fix can't be masked. Publish nothing yet (docs in Phase 6). **Commit on `pipeline-truth-item4`.** Independent of Item 1 and of Phases 3–4.

### Assumption Under Test
B3 (metamodel hierarchy: `Import` abstract with only `MembershipImport`/`NamespaceImport` concrete; `SatisfyRequirementUsage ⊂ RequirementUsage ⊂ ConstraintUsage`) and B4 (these validators have zero live consumers that would regress).

### Test Stencil (Write This First — agentic-mbse suite)
```python
def test_level3_seeded_circular_import_FAILS(seeded_circular_fixture):
    result = run_level3(seeded_circular_fixture)
    assert result.dependency_graph != {}          # non-empty (fires-on-shape)
    assert result.circular_check_failed            # the first time it CAN fail

def test_level3_acyclic_import_passes(acyclic_fixture):     # silent-on-clean
    r = run_level3(acyclic_fixture)
    assert r.dependency_graph != {} and not r.circular_check_failed

def test_level6_error_injection_fails_loud(broken_model):   # D7
    with pytest.raises(Exception):                 # NOT swallowed to []
        run_level6(broken_model)
```

### Changes Required
**See `design.md` for:** row 5 (§Implementation Notes "agentic-mbse row 5"), D7 (§Key Decisions), rows 6/7 (spec decision table), INV-F.

- [x] `level3_dataflow.py` — row 5: `elements_of_type("Import", include_subtypes=True)`, `imported_membership` guard for MembershipImports, **AND** re-keyed the graph by importing package (`import_owning_namespace`) not doc URL — the design missed that URL-keyed graphs can never match package-name values, so cycles were undetectable even with a non-empty graph. This is the real row-5 fix.
- [x] `level4_constraints.py` — row 6 (`:113`): `include_subtypes=True, exclude=EXCLUDED_CONSTRAINT_TYPES`, policy imported from adapter.
- [x] `level6_architecture.py` — row 7 (`:602`): same; **D7:** removed the `:603-604 except Exception: constraints = []` swallow (fails loud).
- [x] Fixtures: `circular_imports.sysml`, `acyclic_imports.sysml`, `l4_constraints/` + `l4_clean/`, `enum_attr.sysml` (row 8). (constraints.sysml from Phase 1 reused for level6.)
- [x] Row 8 pin: exact-type AttributeUsage excludes EnumerationUsage members; include_subtypes would sweep them.

### Validation
- [x] Level 3: circular FAILS + `{PkgOne:[PkgTwo],PkgTwo:[PkgOne]}`; acyclic PASSES + `{PkgApp:[PkgLib]}`, no false cycle.
- [x] Level 4 / Level 6: assert counted (total 2, req excluded); level6 warns affordable+positive_cost, not widget_budget; clean silent; D7 error-injection raises RuntimeError (not `[]`).
- [x] Row 8 enum pin passes.
- [x] Suite: 1228 passed, 10 pre-existing failures. Commit `cc64b1d`. Two behavior-encoding tests updated to the fixed behavior: `test_l3_circular_import_detected` (was asserting the bug — level3 passes on a circular model), and `level3_baseline.txt` regenerated (was the blind `0 docs/0 cycles/✅` output → now `3 docs/1 cycle/❌`). Verified via `_extract_metrics` that the baseline matches real level3 output (the subprocess baseline test can't run in this sandbox: no `python` binary, `/tmp` noexec). D7-absorbs-one-D3-site noted in the commit for Item 5's ledger (Phase 7).

**What We Know Works After This Phase:** all three agentic-mbse validators can fire on the shapes they claim; the swallow is gone. The agentic-mbse side of the coordinated pair is complete except docs.

---

## Phase 3: Codegen Pure Report Module + collect/render Split

### Goal
Build the license-free pure report module, the injectable-policy collector, refactor `report_dropped_constraints` into collect+render, delete the dead row-2 code, and re-anchor REQ-EXT-09. **Commit on `pipeline-truth-epic`.** Depends on Phase 1 (imports the adapter policy source); independent of Item 1.

### Assumption Under Test
MF5 — the mutation check is executable: `collect_constraint_manifest(*, include_subtypes=True, excluded_types=...)` accepts an injectable policy defaulting to production, so the test can run it with `include_subtypes=False` and watch the assert-pin fail (proving the test discriminates).

### Test Stencil (Write This First — codegen conformance, live)
```python
def test_wi014_assert_is_reported(self):                    # fires-on-shape
    ext = _load_live_extractor("wi014_toy")
    manifest = ext.collect_constraint_manifest()            # production defaults
    asserts = [e for e in manifest if e.constraint_kind is ConstraintKind.ASSERT]
    assert len(asserts) == 1 and asserts[0].constraint_name == "affordable"  # literal

def test_mutation_check_discriminates(self):                # MF5
    ext = _load_live_extractor("wi014_toy")
    blind = ext.collect_constraint_manifest(include_subtypes=False)
    assert not any(e.constraint_kind is ConstraintKind.ASSERT for e in blind)  # MISSED

def test_reqext09_independent_anchor(self, caplog):
    expected = 3   # LITERAL from `grep -c 'constraint' .../types.sysml` (comment the grep)
    ...            # part-usage-owner leg + summary WARN + per-owner INFO
```

### Changes Required
**See `design.md` for:** D3 (collect/render split), D4 (delete row 2), D8 (stable tokens), §Component Overview, §Implementation Notes (sentinel wording + REQ-EXT-09 re-anchor bullets a–e), INV-C/INV-G, house-style (R1).

- [x] **`extraction/constraint_report.py` (NEW, pure — no syside import):** `ConstraintKind` (`ASSERT`/`PLAIN`/`REQUIREMENT`/`SATISFY`) + `OwnerKind` (`CALC_DEF`/`PART_DEF`/`PART_USAGE`/`ELEMENT`/`MODEL`) enums (serialize by stable token, D8); `ConstraintManifestEntry` frozen dataclass (`owner_kind, owner_name, owner_qualified_name, constraint_name, constraint_kind, source_line`, D2); `render_constraint_report(manifest, logger)` — always-emitted zero-found sentinel INFO, then M per-droppable INFO, then WARN only if M>0. **Both paths pass the `sysml_codegen.extraction.extractor` logger** (design Implementation Notes — do not let render default to its own module logger).
- [x] **`extractor.py` — `collect_constraint_manifest(*, include_subtypes=True, excluded_types=EXCLUDED_CONSTRAINT_TYPES)` (NEW):** live sweep (`include_subtypes=True`) + ordered is_instance kind-ladder (assert → satisfy → requirement → plain; satisfy before requirement because `SatisfyRequirementUsage ⊂ RequirementUsage`) → `list[ConstraintManifestEntry]`, **stable-sorted by `(owner_qualified_name, constraint_name)` (INV-G)**. Keeps the **full swept subtree** including excluded requirement/satisfy tagged by kind (INV-C). Ladder-droppable ≡ `is_droppable_constraint` (INV-D pin).
- [x] **`extractor.py:92` — `report_dropped_constraints`** refactored in place: `manifest = self.collect_constraint_manifest(); render_constraint_report(manifest, logger)`. Same name, same call site (`orchestration/pipeline_builder.py:685`).
- [x] **Delete `extract_all_constraints`** (`constraint_extractor.py:39/50`, row 2/D4) and **`_deserialize_constraint_info`** (`loader.py:275`, dead) — after re-running the zero-caller grep (Phase 0). Coordinate with Item 8 so each dies once.
- [x] **`tests/conformance/test_extractor.py:888-922` REQ-EXT-09 re-anchor:** (a) replace the self-referential `expected` (`:895-899`) with a **literal** transcribed from a fixture-source grep (comment the grep); (b) add the **part-usage-owner** leg — confirm catf_mfe carries a part-usage-owned constraint, **else add a minimal Item-4-owned fixture** (owned work, design §Potential Risks — not a quiet drop); (c) wi014 assert pin (1 droppable assert `affordable`); (d) executable mutation check (MF5); (e) the from-snapshot INV-B leg is authored here but its committed-snapshot assertion lands in Phase 5 (see note).

### Validation
- [x] Live: wi014 assert reported; mutation check MISSES it (discriminates); REQ-EXT-09 fires across calc-def/part-def/part-usage owners with an independent anchor; silent-on-clean holds; sentinel emits scanned/reported/excluded on N=0 and N>0,M=0.
- [x] `require constraint` certified reported + pinned (plain `ConstraintUsage`, already visible).
- [x] Deletions: zero-caller grep clean; suite green after removal (B4).
- [x] codegen suite green. Commit on `pipeline-truth-epic` ("report: collect/render split + subtype-aware manifest, REQ-EXT-09 re-anchored (D3/D4/D8)").

**What We Know Works After This Phase:** the live report fires on assert, is independently anchored, discriminates under mutation, and renders from a typed manifest. Render identity across paths is by construction (one `render` fn).

---

## Phase 4: Codegen Serialization Machinery (version-neutral)

### Goal
Thread the manifest through serialize → snapshot → load → replay, so the from-snapshot path gets the report it never had. **Keep `SNAPSHOT_FORMAT_VERSION = 1`** — the bump + hard-gate + re-capture are Phase 5 (see the planning decision below). **Commit on `pipeline-truth-epic`.** Depends on Phase 3; independent of Item 1.

> **Planning decision (design left implicit):** the version bump to 2 makes the loader reject every committed v1 snapshot, so it cannot land before re-capture without leaving the suite red. This phase adds the manifest read/write code and proves round-trip fidelity **in memory / temp** (serialize dict → load dict → render). The version bump, the loader hard-gate, and the committed-snapshot INV-B leg all land together in Phase 5, gated on Item 1. The manifest field is additive at v1 in the interim, so old snapshots still load and the suite stays green.

### Assumption Under Test
MF4 — collect is single-path: `capture_snapshot` already reuses `build_pipeline_context` (`snapshot/capture.py:42`), so the manifest built at step 2.5 rides on the same `ctx` capture serializes. No separate offline collect call is needed.

### Test Stencil (Write This First — codegen, license-free)
```python
def test_manifest_roundtrip_render_identity(caplog):
    manifest = [ConstraintManifestEntry(OwnerKind.PART_DEF, "Plant", "P::Plant",
                                        "affordable", ConstraintKind.ASSERT, 51)]
    blob = serialize_manifest(manifest)            # stable tokens (D8), order (INV-G)
    back = deserialize_manifest(blob)
    assert back == manifest                        # round-trip fidelity
    # render is identical fn both paths -> byte-identical logs
```

### Changes Required
**See `design.md` for:** D2 (carrier), D8 (tokens), MF4/INV-B, M8, §Architecture (OFFLINE path), Component Overview.

- [x] **`serializer.py`** — write one top-level `dropped_constraints` array (typed records, stable tokens D8, order preserved INV-G).
- [x] **`loader.py`** — read `dropped_constraints` into `snap["constraint_manifest"]`; **M8:** align the version-mismatch error message to the real re-capture tooling `scripts/capture_extraction_snapshots.py` (not `sysml-codegen snapshot`).
- [x] **`orchestration/pipeline_context.py:60` `PipelineContext`** — add `constraint_manifest` field.
- [x] **`orchestration/pipeline_builder.py` step ~685 / `build_pipeline_context`** — set `ctx.constraint_manifest = manifest` when it renders the live report (single-path, MF4).
- [x] **`orchestration/snapshot_context.py:24` `build_pipeline_context_from_snapshot`** — one added `render_constraint_report(snap["constraint_manifest"], logger)` call (the replay).
- [x] **INV-B parity test authored** (its committed-snapshot leg activates in Phase 5): compares from-snapshot render output against the **live** render output for the same model + pins a **golden serialized manifest fragment**.

### Validation
- [x] In-memory round-trip: serialize → deserialize → equal; render byte-identical across a live manifest and its deserialized twin.
- [x] Existing v1 snapshots still load (additive field; version unchanged) — full suite green.
- [x] codegen suite green. Commit on `pipeline-truth-epic` ("snapshot: serialize + replay constraint manifest, from-snapshot report parity (D2/MF4)").

**What We Know Works After This Phase:** the from-snapshot path renders the same report as live, guarded by the INV-B round-trip test. All that remains is flipping the version and re-capturing.

---

## Phase 5: Format Bump + Repo-Wide Re-Capture (Item-1-GATED, [HARD])

### Goal
Flip `SNAPSHOT_FORMAT_VERSION` 1 → 2, hard-gate the loader, and re-capture **all** committed snapshots (incl. Item 1's additions) in **one reviewed commit** under the precise reviewed-diff gate. **Commit on `pipeline-truth-epic`.**

> **GATE:** this phase requires **Item 1's implement to be complete** — it re-captures Item 1's new fixtures and uses Item 1's `--fixtures` capture filter (`scripts/capture_filter.py` / `scripts/capture_extraction_snapshots.py`). If Item 1 is still capturing, **stop at this boundary and wait.** One item's regen at a time (R3).

### Assumption Under Test
INV-E — no v1/v2 coexistence: the loader rejects any non-2 version, so every committed snapshot must be v2 or it fails to load. And the reviewed-diff gate holds: the only per-snapshot change is the version field + (for constraint-bearing models) the new manifest.

### Steps
- [ ] **Confirm Item 1 complete** (its fixtures + snapshots at v1 committed; `--fixtures` filter present). Count committed snapshots = **20 + Item-1's additions** (was 20; M7 — do not hardcode 20).
- [ ] **Bump `snapshot/__init__.py:12`** `SNAPSHOT_FORMAT_VERSION = 2`. Loader hard-gate rejects v1 (INV-E) — `loader.py:81-92`.
- [ ] **Re-capture every committed `tests/fixtures/*/extraction_snapshot.json`** via `scripts/capture_extraction_snapshots.py` (Item 1's `--fixtures` filter), license-gated. Capture-script only (R3) — no hand edits.
- [ ] **Reviewed-diff gate ([HARD]):** diff **every** file. Each snapshot must be **byte-identical to before EXCEPT** (a) `snapshot_format_version: 1 → 2`, and (b) for constraint-bearing models, the new `dropped_constraints` array (stable-ordered, INV-G). **Any other semantic diff = an unintended extraction change slipped in — stop and investigate** (design §Potential Risks "Re-capture blast radius").
- [ ] **Activate the deferred snapshot-dependent tests:** INV-B committed-snapshot parity leg (Phase 3 bullet e / Phase 4) + loader-rejects-v1 test (INV-E).

### Validation
- [ ] Reviewed diff = version field + manifest only, per file. Attach the diff summary to the commit.
- [ ] Loader rejects a hand-made v1 snapshot (INV-E pin).
- [ ] From-snapshot report on a constraint-bearing fixture == live report + matches golden fragment (INV-B, now on a real committed snapshot).
- [ ] codegen suite green. **One reviewed commit** on `pipeline-truth-epic` ("snapshot: hard-gate format v2 + repo-wide re-capture, constraint manifests (D5/INV-E)").

**What We Know Works After This Phase:** every snapshot is v2 with a faithful manifest; the from-snapshot report is real and pinned; the blind-vs-empty ambiguity is dead.

---

## Phase 6: Docs (R4 step 4 — same change)

### Goal
Make the docs match reality and publish the decision table at its mandated home. codegen docs commit on `pipeline-truth-epic`; the agentic-mbse adapter-docs commit on `pipeline-truth-item4`.

### Changes Required
**See `spec.md` §Docs and `design.md` §Implementation Notes "Docs".**

- [ ] **`docs/architecture/modeling-assumptions.md` §8 rewrite:** report covers `ConstraintUsage` incl. `assert` (`AssertConstraintUsage`) and `require`/plain predicates, **excludes `RequirementUsage` (and its `satisfy` subtype)** as requirement-side, available on **both** live and from-snapshot paths. (Removes the current "scans the whole model … and reports them" overclaim.)
- [ ] **`docs/architecture/reference/01-extraction.md` REQ-EXT-09 row:** independent anchor + part-usage leg + assert pin; **drop the "counted structurally" anti-pattern text.**
- [ ] **Publish the 8-row decision table in the agentic-mbse adapter docs** (D4 docs home), with a pointer from `01-extraction.md`. Commit on `pipeline-truth-item4`.
- [ ] **Retire BACKLOG `[CONSTRAINT-SILENCE]`** (finding of record until this item closes).

### Validation
- [ ] Each doc claim traces to a landed test or code path (no new overclaim).
- [ ] Both repos' docs commits made on the correct branches.
- [ ] Both suites still green (docs-only).

**What We Know Works After This Phase:** the truth surface is documented and the decision table is discoverable at the adapter.

---

## Phase 7: Item-9 Impact Accumulation + Register Close-Out

### Goal
Record the cross-repo residue so nothing is lost or double-counted, and close the R4 evidence loop.

### Steps
- [ ] **Accumulate the agentic-mbse companion-branch changes into the Item-9 sync impact list** (the coordinated-pair residue: `pipeline-truth-item4` = adapter + level3/4/6 + fixtures + adapter-docs). Record the branch name, base (`7f77510`), and commit list.
- [ ] **Note D7 in Item 5's ledger** — level6 `:601` swallow was absorbed here; Item 5 must not re-count it (design D7 / Phase 2 record).
- [ ] **Update discovery register §D4 to final state:** every Item-4 row marked resolved with the landed-fix pointer; the subtype-blind verdict table reflects the fix.
- [ ] **Update `.project/CURRENT_WORK.md`:** Item 4 status → implement complete (pending epic close); note the Item-1-gated re-capture landed.

### Validation
- [ ] Item-9 impact list names the companion branch + commits.
- [ ] Register §D4 has no open Item-4 row; D7 recorded against Item 5.
- [ ] Both suites green; both branches in a clean, committed state.

**What We Know Works After This Phase:** the coordinated pair is accounted for, the R4 register is closed, and Item 9 knows exactly what to sync.

---

## Environment Setup

**See CLAUDE.md** for install/test/lint/typecheck commands. Key: `uv run pytest tests/` (codegen), agentic-mbse suite in its own checkout; live capture is license-gated (`scripts/capture_extraction_snapshots.py`); `generate --from-snapshot` is license-free.

## Risk Management

**See `design.md#potential-risks`.** Phase-specific mitigations:
- **Phase 0/1:** adapter shape unread → Phase 0 re-reads live before Phase 1 edits; change is additive keyword-only params + 3 map entries + guarded hard-error.
- **Phase 3:** part-usage fixture may be missing → add a minimal **Item-4-owned** fixture (owned work, not a quiet drop).
- **Phase 5:** re-capture blast radius (~20+ regenerations) → the byte-level reviewed-diff gate; any semantic diff beyond version+manifest halts the phase.
- **Cross-repo:** never `git stash`, never stage the agentic-mbse dirty-workstream files; companion branch from `7f77510` only.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**Completed:** 2026-07-06

**Probe verdicts (all live, this session):**
- Row 1 (codegen report silent on assert): CONFIRMED. wi014_toy exact `ConstraintUsage`=0, swept=1 (`AssertConstraintUsage` `affordable`), report emitted 0 records.
- Row 2 (`extract_all_constraints` blind): CONFIRMED. total=0; zero real callers.
- Row 3/5 (level3 abstract-`Import` → empty graph → circular check always passes): CONFIRMED on `circular_import.sysml` — exact `Import`=0, swept=2, graph=`{}`, cycles=`[]`.
- Row 4/6 (level4 exact-type undercount): CONFIRMED — exact CU=0, swept=1 on assert model.
- Row 7 (level6 undercount + `:603-604 except Exception: constraints=[]` swallow): CONFIRMED.
- B1 (subtype sweep + hierarchy-aware `is_instance`): CONFIRMED live. B2 (three names absent): CONFIRMED false-today. B3 (hierarchy): CONFIRMED by stub read.

**Artifacts:** `register-update-pending.md` (full R4 table + register §D4 update + adapter-shape corrections, to be applied at Phase 3+ by the sysml-codegen committer).

**Key discrepancies carried to Phase 1 (design assumed wrong):**
1. `elements_of_type` raises **`KeyError`**, not `ValueError` — Phase 1 changes it to ValueError for D6.
2. Methods are **`@classmethod`**, not staticmethod — preserve classmethod.
3. No module-level `TYPE_MAP`; add the 3 names to the `_get_type_map()` dict literal (`:131-156`).
4. Subtype mechanism = `model.elements(kind, include_subtypes=True)` (real param on the Python wrapper), not a bare `nodes(...)`.

**Issues:** agentic-mbse suite has 10 pre-existing infra failures (bare-`python`/console-script subprocess tests + 2 sample_models baseline mismatches) — unrelated to Item 4. A `python` shim (`/tmp/shimbin/python` → python3) lets the subprocess validation tests run for Phase 2.

### Phase 1 Completion
**Completed:** 2026-07-06 · Commit `64a097e` on `pipeline-truth-item4`.

**Changes:** `syside_adapter.py` (params + D6 hard-error + policy source + docstring),
`tests/test_adapter.py` (8 new tests + KeyError→ValueError flip), new fixture
`tests/fixtures/item4_subtype/constraints.sysml`.

**Deviation from design (recorded in `register-update-pending.md`):** D6 needed a **4th** TYPE_MAP
name, `InvocationExpression` — used by the C5 check via `is_instance` and previously relying on the
silent string-match. The Phase-0 single-line grep missed it (multi-line call). Mapping it is
required by D6's own principle and makes the check hierarchy-aware. No other used-but-unmapped names
(multi-line-aware scan confirms).

**Suite:** 1220 passed, 1 skipped, 10 pre-existing infra/baseline failures. No new failures.

### Phase 2 Completion
**Completed:** 2026-07-06 · Commit `cc64b1d` on `pipeline-truth-item4`.

**Changes:** `level3_dataflow.py` (row 5 + graph re-key), `level4_constraints.py` (row 6),
`level6_architecture.py` (row 7 + D7), new `tests/test_validation/test_item4_subtype.py` (8 tests),
`test_sysml_quality_checks.py` (l3 circular test flipped to detected), regenerated
`level3_baseline.txt`, 5 new fixtures under `tests/fixtures/item4_subtype/`.

**Deviation from design (row 5 was under-specified):** making the circular check able to fail
needed more than `include_subtypes` — the graph was keyed by document URL but valued by package
name, so `detect_cycles` could never match endpoints. Re-keyed the source node to the importing
package (`import_owning_namespace.qualified_name`). Without this, "seeded circular FAILS" is
impossible. Recorded here and in the commit.

**Two behavior-encoding tests flipped to the fixed behavior** (both anticipated by their own
comments/docstrings): the distinctness circular-import test and the sample_models level3 baseline.
Not regressions — they were asserting the blind-validator bug.

**Suite:** 1228 passed, 1 skipped, 10 pre-existing infra failures (unchanged set; the 2
baseline-comparison subprocess tests among them can't run in this sandbox but the level3 baseline
content is verified correct via `_extract_metrics`).

### Pre-Phase-3: Codegen `is_instance` Name Inventory (D6 gate)
**Completed:** 2026-07-06 · Commits `bc24ae3` (agentic-mbse `pipeline-truth-item4`), `9a8721b` (codegen).

Ran the multi-line-aware `is_instance`/`elements_of_type`/`get_type` name scan over
`src/sysml_codegen/`. 21 distinct names used; 4 used-but-unmapped. Map-or-delete decided
per evidence (syside stub `.venv/.../syside/core/__init__.pyi`):

- **`LiteralReal` — DELETED** (3 sites: `expression_compiler.py:398`, `expression_utils.py:62`,
  `:334`). Not a syside class (only `LiteralRational`). These branches silently returned False
  forever pre-D6; post-D6 they would raise on the unmapped name. A float literal `400.0` is a
  `LiteralRational`, handled by the adjacent branch, so deletion is behavior-neutral. The
  `MockLiteralReal` test fixture (same fiction) renamed to `MockLiteralRational`; 4 hierarchy-
  resolver tests that asserted `MockLiteralReal → LITERAL` fixed by the rename.
- **`OwningMembership`, `Subclassification`, `NullExpression` — MAPPED** (agentic-mbse adapter,
  `bc24ae3`). All real syside classes, used by codegen `is_instance`, previously relying on the
  silent string-match. Mapping makes the checks hierarchy-aware (strictly more correct).

Post-inventory re-scan: **zero** used-but-unmapped codegen names. Both suites green
(codegen 2017, agentic-mbse 1238). The LiteralReal breakage is gone.

### Phase 3 Completion
**Completed:** 2026-07-06 · Commit `501968f` on `pipeline-truth-epic`.

**Changes:** new pure `extraction/constraint_report.py` (`ConstraintKind`/`OwnerKind` str-enums,
frozen `ConstraintManifestEntry`, `DROPPABLE_KINDS`, `render_constraint_report`); `extractor.py`
gains `collect_constraint_manifest(*, include_subtypes=True)` (subtype sweep + ordered kind-ladder,
stable-sorted INV-G) and `_classify_constraint_kind`; `report_dropped_constraints` refactored to
collect+render and now **returns the manifest**; `_constraint_owner_kind` returns `OwnerKind`.
Row 2 deleted (`constraint_extractor.py` gone; dead `loader._deserialize_constraint_info` +
`ConstraintInfo` import removed). REQ-EXT-09 re-anchored.

**Live-verified manifest (probe):** wi014_toy → scanned 1 / exact-only 0 / droppable 1 (assert
`affordable`, part_def owner, L51). catf_mfe → scanned 65 / droppable 65, all plain, owners
{calc_def 51, part_def 5, part_usage 9} — so **catf_mfe already covers the part-usage leg** (no new
part-usage fixture needed). Independent anchor: `grep -rhE '^\s*constraint\s+\w+\s*\{' catf_mfe = 65`.

**Deviations from design (recorded):**
1. **No `excluded_types` parameter on `collect_constraint_manifest`.** The design signature listed
   `excluded_types=EXCLUDED_CONSTRAINT_TYPES`, but INV-C requires keeping the full swept subtree, so
   the sweep never pre-filters — the param would be unused in the body (an abstraction-quality red
   flag). Droppability is derived from `constraint_kind` via `DROPPABLE_KINDS`; INV-D is enforced by
   a live cross-check test (`_classify_constraint_kind` droppability == adapter `is_droppable_constraint`,
   element by element on `item4_require`). The single policy source is still the adapter; the pin is
   stronger than threading a constant the collector wouldn't branch on. `include_subtypes` (the
   mutation-check lever, MF5) is the one injectable param.
2. **New Item-4-owned fixture `tests/fixtures/item4_require/` (live-only, no snapshot)** — pins
   `require constraint` as a reported PLAIN predicate and a requirement usage as swept-and-EXCLUDED
   (kind REQUIREMENT). It is the only codegen fixture exercising the exclusion/sentinel path live.
   Kept snapshot-free so it stays out of the Phase-5 re-capture set.

**Concurrency artifact:** the shared working tree carried other stage subagents (Item 2/Item 8).
My `git rm constraint_extractor.py` was swept into a concurrent Item-8 commit (`2446e4b`) before I
committed Phase 3 — the file dies exactly once (D4 "each dies once"), attributed to that commit
rather than `501968f`. Net state correct; noted for the Item-9 ledger.

**Suite:** codegen 2027 passed (+10). ruff 21→20, mypy 109→105 (dead-code deletion; both under bar).

### Phase 4 Completion
**Completed:** 2026-07-06 · Commit `a627f0a` on `pipeline-truth-epic`. **Version-neutral** (still v1).

**Changes:** `constraint_report.py` gains pure `manifest_to_records`/`manifest_from_records` (stable
tokens D8, order preserved INV-G); `PipelineContext.constraint_manifest` field; `pipeline_builder`
step 2.5 captures the returned manifest → ctx (single-path, MF4); `serializer` writes top-level
`dropped_constraints`; `loader` reads it into `snap["constraint_manifest"]` (additive `.get`, old
snapshots → empty) + M8 message alignment to `scripts/capture_extraction_snapshots.py`;
`snapshot_context` replays `render_constraint_report` through the `sysml_codegen.extraction.extractor`
logger (INV-B); `capture.py` passes `ctx.constraint_manifest`.

**Verified end-to-end (license-free):** `build_pipeline_context_from_snapshot` on the committed catf
snapshot replays the sentinel INFO through the extractor logger (manifest empty until Phase-5
re-capture — expected). In-memory INV-B leg pinned: round-trip lossless + render byte-identical
across a manifest and its deserialized twin. Committed-snapshot INV-B leg deferred to Phase 5.

**Suite:** codegen 2029 passed (+2). ruff 20, mypy 105 (under bar). agentic-mbse untouched (green).

### Phase 5 Completion
### Phase 6 Completion
### Phase 7 Completion

---

**Status:** Draft → In Progress → Complete

ARTIFACT: .project/active/subtype-enumeration/plan.md
