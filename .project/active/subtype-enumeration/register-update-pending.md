# Register & Design-R4 Update — PENDING (apply at Phase 3+)

**Why deferred:** the discovery register (`.project/research/20260706_pipeline-truth-discovery.md`)
and the design's R4 table both live in **sysml-codegen**, where Item 1's implement session is
concurrently committing. Two committers in one tree is forbidden. Phase 0 records the live results
here; a Phase-3+ session (owning sysml-codegen commits) applies them to §D4 and to
`design.md`'s R4 table.

Produced by the Item-4 Phase-0 implement session, 2026-07-06. All results are from **live runs**
in this session (codegen: `uv run python _probe.py` + `/tmp/probe_b1.py`; agentic-mbse:
`.venv/bin/python /tmp/probe_ambse.py`). Companion branch: `pipeline-truth-item4` off `7f77510`
in `/home/reid/1cfe/agentic-mbse`.

---

## R4 Table — verdicts to write into design.md (rows 1–5: "Live run deferred" → CONFIRMED-live)

| # | Finding | Live probe result | Verdict |
|---|---------|-------------------|---------|
| 1 | codegen `extractor.py` report queries exact-type `ConstraintUsage`; the WARN/INFO gate on a non-empty list → totally silent when the only constraint is an `assert`. | wi014_toy: exact `ConstraintUsage` = **0**; swept (`include_subtypes=True`) = **1** = `AssertConstraintUsage` name `affordable`; `is_instance(assert,"ConstraintUsage")` = **True**; `report_dropped_constraints()` emitted **0** log records. | **CONFIRMED (live)** |
| 2 | codegen `constraint_extractor.py` `extract_all_constraints` same exact-type query; docstring claims assert support; zero callers. | `extract_all_constraints(wi014_model)` total = **0**. Zero-caller grep: only self-reference is the `__all__` export at `constraint_extractor.py:260`. `_deserialize_constraint_info`: **zero** references anywhere (dead). | **CONFIRMED (live)** |
| 3 | agentic-mbse `level3_dataflow.py:48` queries abstract `Import` → matches nothing → dep graph always `{}` → circular check structurally always passes. Secondary: `imported_namespace` guard skips MembershipImports. | On `circular_import.sysml` (genuinely circular, two `::*` imports): exact `Import` = **0**; swept = **2** (both `NamespaceImport`); `build_dependency_graph(model)` = **`{}`**; `detect_cycles({})` = **`[]`** → PASSES on a circular model. Secondary confirmed by API: `MembershipImport` exposes `imported_membership`, **not** `imported_namespace`, so the `:58` guard skips MembershipImports once the type is fixed. | **CONFIRMED (live)** |
| 4 | agentic-mbse `level4_constraints.py:113` exact-type `ConstraintUsage` → undercounts asserts. | Assert-bearing model: exact `ConstraintUsage` = **0**; swept = **1** (`AssertConstraintUsage`). Same adapter mechanism as row 1. | **CONFIRMED (live)** |
| 5 | agentic-mbse `level6_architecture.py:602` exact-type `ConstraintUsage` → non-executable WARN never fires on asserts; **`:603-604 except Exception: constraints = []` swallow** collapses any error to "zero constraints". | Same swept vs exact result as row 4. Swallow present verbatim: `constraints = list(...ConstraintUsage...)` / `except Exception:` / `constraints = []` at `level6_architecture.py:602-604`. | **CONFIRMED (live)** |

---

## Line-number re-verification (register said approximate — corrected)

**agentic-mbse `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py`:**
- `elements_of_type` — **classmethod at `:196`** (register said `:214`; orchestrator's `:196` is correct).
- `is_instance` — **classmethod at `:231`**; unknown-name lookup (`type_map.get`) at `:245-246`.
- **No module-level `TYPE_MAP`.** The map is `cls._type_map`, built lazily in `_get_type_map()`;
  the dict literal is **`:131-156`** (register's `:244-246` actually points at the `is_instance`
  lookup, not the map definition).

**agentic-mbse validators:**
- `level3_dataflow.py:48` — `for element in SysideAdapter.elements_of_type(model, "Import"):` ✓ (`imported_namespace` guard at `:58`).
- `level4_constraints.py:113` — `constraints = list(SysideAdapter.elements_of_type(model, "ConstraintUsage"))` ✓.
- `level6_architecture.py:602` — same query ✓; swallow at **`:603-604`** (design said `:601`).

**codegen `src/sysml_codegen/extraction/extractor.py`:** report query at `:107-108`, WARN gate `if constraints:` at `:123` ✓.

---

## Adapter shape — resolved (design §Potential Risks "unread")

These correct assumptions the design/register made without reading the live repo. **Phase 1 must
build against these, not the design's wording:**

1. **B1 CONFIRMED live.** The subtype mechanism is `model.elements(kind, include_subtypes=False)`
   in the Python `Model` wrapper `syside/_loading.py:213` (an alias for `nodes` at `:190`), which
   dispatches to the C++ `Document.all_nodes(kind)` when `include_subtypes=True` and
   `Document.nodes(kind)` (exact) when `False`. So `include_subtypes` **is** a real parameter,
   defaulting `False` — the adapter's `elements_of_type` calls `model.elements(type)` today and
   just needs to pass the flag through. (The core `.pyi` stub's `nodes(self, kind)` has no such
   param; that is the low-level C++ view. The high-level Python `Model` adds it. Do not be misled
   by the stub.)

2. **B2 CONFIRMED false-today.** `_get_type_map()` (`:131-156`) contains **none** of
   `AssertConstraintUsage`, `RequirementUsage`, `SatisfyRequirementUsage`. Live proof: querying
   `AssertConstraintUsage` raises today (see #3 below). D6 is load-bearing, not belt-and-suspenders.

3. **DISCREPANCY — `elements_of_type` raises `KeyError`, NOT `ValueError`.** The design D6 text
   ("`elements_of_type` already raises `ValueError`") is **wrong**. Current code at `:210-213`
   raises `KeyError(f"Unknown type '{type_name}'. Valid types: {...}")`. Live probe output:
   `ERR "Unknown type 'AssertConstraintUsage'. Valid types: [...]"`. **Phase 1 must change this to
   `ValueError`** to satisfy D6/INV-F and align both methods — and check no caller depends on
   `KeyError` (validators wrap in `except Exception`, so they are unaffected).

4. **DISCREPANCY — methods are `@classmethod`, not `@staticmethod`.** The design's "a `@staticmethod`
   serves both; confirm at implement" resolves to: they are **`@classmethod`** and already serve
   both `SysideAdapter.x(...)` and `self.adapter.x(...)`. **Preserve `@classmethod`** — do not
   convert.

5. **`is_instance` mechanism** (`:244-257`): `type_map.get(type_name)` → if a real syside type and
   `elem` has `.isinstance`, call `elem.isinstance(sysml_type)` (hierarchy-aware, confirmed live:
   `assert.isinstance(AssertConstraintUsage)` = True, `is_instance(assert,"ConstraintUsage")` = True);
   otherwise fall through to string-match `type_name in type(elem).__name__` (the mock path). It
   wraps `_get_type_map()` in `except ImportError` for the no-syside/mock path.
   **D6 for `is_instance`:** after the map is available, raise `ValueError` when `type_name` not in
   the map, **before** the string-match fallback — but keep the fallback for *mapped* names on mock
   objects (mock tests use real syside type-name strings, so they stay in the map and survive). When
   syside is unavailable (`_get_type_map()` raises `ImportError`), there is no map to check, so the
   string-match path runs unchanged (no hard error possible without a map — acceptable; D6's target
   is the live path where the map exists but lacks the name).

6. **`Import` hierarchy CONFIRMED** (B3): `AssertConstraintUsage(ConstraintUsage)`,
   `RequirementUsage(ConstraintUsage)`, `SatisfyRequirementUsage(RequirementUsage)`,
   `MembershipImport(Import)`, `NamespaceImport(Import)`, `RequirementConstraintMembership`
   (require-constraint carrier) — all present in the stub. `Import` matches zero exact-type
   (abstract), confirmed live (row 3).

---

## D6 scope correction — `InvocationExpression` also needed (found in Phase 1)

D6 as designed adds **three** names to the map (`AssertConstraintUsage`, `RequirementUsage`,
`SatisfyRequirementUsage`). Phase 1 found a **fourth** required addition: **`InvocationExpression`**.

- The C5 check `check_static_function_invocations` (`agentic-mbse/src/agentic_mbse/validation/adr002.py:190`)
  calls `is_instance(node, "InvocationExpression")` — a name **not** in the map. Before D6,
  `is_instance` silently string-matched the real type name and it worked; under D6's hard-error it
  raised `ValueError`, which the check's `except Exception` swallowed → the WARN vanished →
  `test_c5_function_invocation_warns` regressed.
- **Root cause of the miss:** the Phase-0 name inventory used a single-line grep, which does not
  catch multi-line `is_instance(\n node,\n "Name")` calls. A multi-line-aware scan of *all*
  `is_instance`/`elements_of_type`/`get_type` names finds exactly one used-but-unmapped name:
  `InvocationExpression`. All others were already mapped.
- **Fix:** map `InvocationExpression` (`syside.InvocationExpression`; `OperatorExpression` is a
  subtype). The check is now hierarchy-aware (strictly more correct) and the C5 test passes.
- **Lesson for the codegen side (Phase 3):** codegen's `is_instance` names must be inventoried the
  same multi-line-aware way before relying on D6 — any used-but-unmapped name will raise once the
  codegen path consults the (shared) hardened adapter.

## §D4 register text to mark resolved (apply at Phase 3+)

- Rows 1–5 above: strike "CONFIRMED-BY-REGISTER / Live run deferred", replace with **CONFIRMED (live,
  Item-4 Phase 0, 2026-07-06)**.
- Record the adapter-shape corrections (#1–#5) so no later item re-derives them from the stale
  `nodes(kind, include_subtypes)` framing or the `KeyError`/`staticmethod` assumptions.
- Zero-caller grep for `extract_all_constraints` / `_deserialize_constraint_info` re-run clean —
  safe for Phase 3 to delete.

## What Phase 3+ needs to know (from Phases 0–2, done on `pipeline-truth-item4`)

- **Adapter API landed** (commit `64a097e`): `elements_of_type(model, name, *, include_subtypes=False,
  exclude=())`, both methods raise `ValueError` on an unmapped name, module-level
  `EXCLUDED_CONSTRAINT_TYPES` + `is_droppable_constraint(elem)`. Codegen imports these from
  `agentic_mbse.sysml.syside_adapter`. The editable install means codegen sees them live.
- **Codegen `is_instance` inventory (do before relying on D6):** run the *multi-line-aware* scan (see
  the D6-scope-correction section) over `src/sysml_codegen/` for every `is_instance`/`elements_of_type`
  name. Any used-but-unmapped name will now raise once it hits the shared hardened adapter. Map it, as
  Phase 1 did for `InvocationExpression`.
- **level6 D7 absorbed one D3-family site** — note for Item 5's ledger so it is not double-counted
  (Phase 7 / plan carries this).
- **Row-5 graph re-key (design deviation):** level3's dependency graph is now keyed by the importing
  package's qualified name (`import_owning_namespace`), not the document URL — required for
  `detect_cycles` to work. Nothing in codegen depends on this; recorded for the register close-out.
- **Companion-branch commits:** `64a097e` (adapter), `cc64b1d` (validators) on `pipeline-truth-item4`
  off `7f77510`. For the Item-9 sync impact list (Phase 7).
- **agentic-mbse suite baseline for reference:** 1228 passed, 10 pre-existing infra failures (5 shell
  out to a bare `python` binary absent from PATH; 3 need the `agentic-mbse` console script; 2 are the
  subprocess baseline-comparison tests, which need a working `python`). None are Item-4 regressions.
