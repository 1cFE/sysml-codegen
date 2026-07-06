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
- [ ] **Create the agentic-mbse companion branch:** `git -C /home/reid/1cfe/agentic-mbse checkout -b pipeline-truth-item4 7f77510` (from `upstream-findings-sync` HEAD, clean tree). Confirm the two unrelated untracked docs are untouched.
- [ ] **Re-verify all agentic-mbse line numbers live** (design R4 note; spec §agentic-mbse landing): adapter method (register said `:214`; orchestrator says classmethod at `syside_adapter.py:196` — **re-confirm**), `TYPE_MAP` (`~:244–246`), `level3_dataflow.py:48`, `level4_constraints.py:113`, `level6_architecture.py:602` + swallow `~:601`. Record the actual lines; the register line numbers are approximate.
- [ ] **Re-read the adapter shape** (design §Potential Risks): decorator on `elements_of_type`/`is_instance` (staticmethod vs classmethod — must serve both `SysideAdapter.x(...)` and `self.adapter.x(...)`), that `nodes` accepts `include_subtypes`, the exact `TYPE_MAP` dict shape, and confirm the three names (`AssertConstraintUsage`, `RequirementUsage`, `SatisfyRequirementUsage`) are **absent** (B2).
- [ ] **Run `_probe.py` live** (codegen, license-gated) — confirm rows 1–2: exact `ConstraintUsage` count = 0, `is_instance(assert, "ConstraintUsage")` = True, `report_dropped_constraints()` emits **0** records, `extract_all_constraints()` total = 0.
- [ ] **Run the agentic-mbse probes** for rows 3/5/6/7 (level3 abstract-`Import` → empty graph → circular check always passes; level4/level6 exact-type `ConstraintUsage` undercounts asserts; level6 `:601` swallow collapses errors to `[]`). Seed the minimal fixtures needed to fire each (these become the Phase 2 test fixtures).
- [ ] **Re-run the zero-caller grep** for `extract_all_constraints` and `_deserialize_constraint_info` (D4) — confirm still zero real consumers before Phase 3 deletes them.
- [ ] **Update the design R4 table** (rows 1–5) from "Live run deferred" to CONFIRMED-live (or RECLASSIFIED with evidence if any does not reproduce). **Update register §D4 in place** with the live results.

### Validation
- [ ] `_probe.py` output pasted into the R4 table update; every row is CONFIRMED (or reclassified with evidence, per R4 — a finding that does not reproduce is reclassified, not fixed).
- [ ] Companion branch exists, clean except the (empty) new branch; dirty-workstream files untouched.
- [ ] Both suites green (baseline — no code changed yet).

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

- [ ] `syside_adapter.py` — `elements_of_type` gains keyword-only `include_subtypes: bool = False` (pass-through to `nodes`) and `exclude: Collection[str] = ()` (drops any element `is_instance` of a named type). Preserve the current decorator (confirmed Phase 0).
- [ ] `syside_adapter.py` — **D6:** `TYPE_MAP` gains `AssertConstraintUsage`, `RequirementUsage`, `SatisfyRequirementUsage` (exact syside classes). Both `elements_of_type` and `is_instance` **hard-error (`ValueError` + valid-names list) on an unknown name**. The `is_instance` hard error is gated on **"name not in `TYPE_MAP`" checked BEFORE the documented mock string-match fallback**, so the mock path survives (D6).
- [ ] `syside_adapter.py` — new module-level `EXCLUDED_CONSTRAINT_TYPES = ("RequirementUsage",)` and `is_droppable_constraint(elem)` (built on `is_instance`). This is the **single production location** of the string `"RequirementUsage"` (INV-D).
- [ ] `syside_adapter.py` docstring — teach the decision table + point at the (Phase 6) published table (D4 docs home is the adapter).

### Validation
- [ ] Fires-on-unknown-name pin passes (both methods).
- [ ] `include_subtypes=True` sweep includes the assert; default (False) unchanged.
- [ ] `exclude=EXCLUDED_CONSTRAINT_TYPES` drops requirements but keeps asserts/plain.
- [ ] Every pre-existing adapter call site behaves identically (INV-A regression sweep — run the full agentic-mbse suite).
- [ ] agentic-mbse suite green. Commit on `pipeline-truth-item4` ("adapter: subtype-aware enumeration + hard-error on unknown type name (D1/D6)").

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

- [ ] `level3_dataflow.py` — row 5: `elements_of_type("Import", include_subtypes=True)` (Import already in TYPE_MAP; no new name needed) **and** fix the `imported_namespace` guard that skips `MembershipImport`s once the type is fixed.
- [ ] `level4_constraints.py` — row 6: `include_subtypes=True, exclude=EXCLUDED_CONSTRAINT_TYPES` (mirror row 1). Import the policy from the adapter.
- [ ] `level6_architecture.py` — row 7: same `include_subtypes=True, exclude=...`; **D7:** narrow/remove the `:601 except Exception: constraints = []` swallow so failure is loud, not `[]`.
- [ ] Fixtures (from Phase 0 seeds): seeded circular-import, acyclic import, assert-bearing (level4/level6 fire), clean (silent), error-injection (level6 loud), enum-bearing (row 8 keep-exact-type pin).
- [ ] Row 8 pin: assert the 4 `AttributeUsage` enum sites stay exact-type (opt-OUT, mirror row 3) on the enum fixture.

### Validation
- [ ] Level 3: seeded circular FAILS + non-empty graph; acyclic PASSES + non-empty graph, no false cycle.
- [ ] Level 4 / Level 6: assert fixture fires; clean fixture silent; level6 error-injection **fails loud, not `[]`** (D7).
- [ ] Row 8 enum pin passes.
- [ ] agentic-mbse suite green. Commit on `pipeline-truth-item4` ("validators: subtype-aware sweeps + remove level6 swallow (rows 5/6/7, D7)"). **Record D7 as absorbing one D3-family site — note for Item 5's ledger so level6 is not double-counted** (carried to Phase 7).

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

- [ ] **`extraction/constraint_report.py` (NEW, pure — no syside import):** `ConstraintKind` (`ASSERT`/`PLAIN`/`REQUIREMENT`/`SATISFY`) + `OwnerKind` (`CALC_DEF`/`PART_DEF`/`PART_USAGE`/`ELEMENT`/`MODEL`) enums (serialize by stable token, D8); `ConstraintManifestEntry` frozen dataclass (`owner_kind, owner_name, owner_qualified_name, constraint_name, constraint_kind, source_line`, D2); `render_constraint_report(manifest, logger)` — always-emitted zero-found sentinel INFO, then M per-droppable INFO, then WARN only if M>0. **Both paths pass the `sysml_codegen.extraction.extractor` logger** (design Implementation Notes — do not let render default to its own module logger).
- [ ] **`extractor.py` — `collect_constraint_manifest(*, include_subtypes=True, excluded_types=EXCLUDED_CONSTRAINT_TYPES)` (NEW):** live sweep (`include_subtypes=True`) + ordered is_instance kind-ladder (assert → satisfy → requirement → plain; satisfy before requirement because `SatisfyRequirementUsage ⊂ RequirementUsage`) → `list[ConstraintManifestEntry]`, **stable-sorted by `(owner_qualified_name, constraint_name)` (INV-G)**. Keeps the **full swept subtree** including excluded requirement/satisfy tagged by kind (INV-C). Ladder-droppable ≡ `is_droppable_constraint` (INV-D pin).
- [ ] **`extractor.py:92` — `report_dropped_constraints`** refactored in place: `manifest = self.collect_constraint_manifest(); render_constraint_report(manifest, logger)`. Same name, same call site (`orchestration/pipeline_builder.py:685`).
- [ ] **Delete `extract_all_constraints`** (`constraint_extractor.py:39/50`, row 2/D4) and **`_deserialize_constraint_info`** (`loader.py:275`, dead) — after re-running the zero-caller grep (Phase 0). Coordinate with Item 8 so each dies once.
- [ ] **`tests/conformance/test_extractor.py:888-922` REQ-EXT-09 re-anchor:** (a) replace the self-referential `expected` (`:895-899`) with a **literal** transcribed from a fixture-source grep (comment the grep); (b) add the **part-usage-owner** leg — confirm catf_mfe carries a part-usage-owned constraint, **else add a minimal Item-4-owned fixture** (owned work, design §Potential Risks — not a quiet drop); (c) wi014 assert pin (1 droppable assert `affordable`); (d) executable mutation check (MF5); (e) the from-snapshot INV-B leg is authored here but its committed-snapshot assertion lands in Phase 5 (see note).

### Validation
- [ ] Live: wi014 assert reported; mutation check MISSES it (discriminates); REQ-EXT-09 fires across calc-def/part-def/part-usage owners with an independent anchor; silent-on-clean holds; sentinel emits scanned/reported/excluded on N=0 and N>0,M=0.
- [ ] `require constraint` certified reported + pinned (plain `ConstraintUsage`, already visible).
- [ ] Deletions: zero-caller grep clean; suite green after removal (B4).
- [ ] codegen suite green. Commit on `pipeline-truth-epic` ("report: collect/render split + subtype-aware manifest, REQ-EXT-09 re-anchored (D3/D4/D8)").

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

- [ ] **`serializer.py`** — write one top-level `dropped_constraints` array (typed records, stable tokens D8, order preserved INV-G).
- [ ] **`loader.py`** — read `dropped_constraints` into `snap["constraint_manifest"]`; **M8:** align the version-mismatch error message to the real re-capture tooling `scripts/capture_extraction_snapshots.py` (not `sysml-codegen snapshot`).
- [ ] **`orchestration/pipeline_context.py:60` `PipelineContext`** — add `constraint_manifest` field.
- [ ] **`orchestration/pipeline_builder.py` step ~685 / `build_pipeline_context`** — set `ctx.constraint_manifest = manifest` when it renders the live report (single-path, MF4).
- [ ] **`orchestration/snapshot_context.py:24` `build_pipeline_context_from_snapshot`** — one added `render_constraint_report(snap["constraint_manifest"], logger)` call (the replay).
- [ ] **INV-B parity test authored** (its committed-snapshot leg activates in Phase 5): compares from-snapshot render output against the **live** render output for the same model + pins a **golden serialized manifest fragment**.

### Validation
- [ ] In-memory round-trip: serialize → deserialize → equal; render byte-identical across a live manifest and its deserialized twin.
- [ ] Existing v1 snapshots still load (additive field; version unchanged) — full suite green.
- [ ] codegen suite green. Commit on `pipeline-truth-epic` ("snapshot: serialize + replay constraint manifest, from-snapshot report parity (D2/MF4)").

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
### Phase 1 Completion
### Phase 2 Completion
### Phase 3 Completion
### Phase 4 Completion
### Phase 5 Completion
### Phase 6 Completion
### Phase 7 Completion

---

**Status:** Draft → In Progress → Complete

ARTIFACT: .project/active/subtype-enumeration/plan.md
