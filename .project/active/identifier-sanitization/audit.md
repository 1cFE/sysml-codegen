# Audit: Identifier Sanitization (SC-4 + SC-11 riders) — Item 5

**Verdict:** PASS / Certify
**Audited:** 2026-07-05
**Branch:** upstream-findings-epic
**Commit:** 4b19e4d (18 files)

---

## Summary

Item 5 delivers exactly what the spec and design contract for. Every emitted Python
identifier — class name, module path, FORMULA module_eqn/channel — is now a sanitized
function of the raw SysML QN through one new derivation-layer helper, and the SC-4 leak
(`'margin calc'.py`, `class 'Margin Calc'Module`, registry importing an undeclared class)
is dead. The two recorded deviations are sound and improve on imprecise design prose rather
than cutting scope. Both handoff obligations (Item 7 lockstep, fusion-tea retirement) and
the SC-11 closure are recorded where their consumers will find them.

The one verification limit is the same one that has capped every Item in this epic: the
test suite could not be run in this session (harness-blocked from `uv run`). The
1880/21/109 gate rests on the recorded plan/close-out evidence plus direct code and fixture
inspection, which I did do. No production changes were made; no commits.

## Findings

### Plan completion — all 5 phases verified

- **Phase 0 (static de-risk scans).** `tests/conformance/test_sanitize_invariance.py`
  present with 3 scans: the identifier-safe-segment no-op guard
  (`:145`), the quoted-name corollary (`:169`), and the SC-11 grandparent gate (`:186`).
  The gate scan replicates the parent-segment alias scheme (`_residual_grandparent_collisions`,
  mirroring `registry.py:98-116`) and asserts CLEAN — the recorded decision (hard fail-fast)
  follows from it. REQ IDs confirmed free and assigned (NC-08/09, REG-08).
- **Phase 1 (FORMULA wire).** Helper added (`qualified_names.py:108-121`); the three
  consumer sites in `graph_builder.py` (`:745` resolution_map, `:789` module identity,
  `:818` part_eqn) and the producer (`output_registry_builder.py:124`) all build the
  module_eqn owner via the helper and the leaf from `ca.python_name` (M1). D3 EXPOSE_PURE
  collapse done (`:273-276` → helper call). Fixture + committed snapshot present.
- **Phase 2 (CalcUsage derivation).** Both `from_sysml` methods sanitize per segment
  inline, sanitize-then-lower (`identifier_types.py:113-114, 153-154`). Class name preserves
  case; path/namespace lowercase after sanitize.
- **Phase 3 (fail-fasts).** `_check_duplicate_output_paths` (`cli/__init__.py:175`) wired as
  Step 1.5 before `_clear_output_directory` (`:771`). SC-11 post-alias re-check added to
  `_resolve_class_name_collisions` (`registry.py:129-142`), hard `raise` per the CLEAN gate.
- **Phase 4 (docs + close-out).** Doc 15 REQ-NC-08/09, doc 20 REQ-REG-08, verification
  matrix, and both coordination notes all present.

### Spec conformance — all 6 success criteria met

1. **SC-4 leak dead (importable package).** `test_alias_agg_probe_generation.py` drives the
   committed snapshot through real `run_codegen` (no mocks), then asserts every generated
   `.py` `ast.parse`s **and** every class the registry imports is declared by its module
   file (`_module_class_imports` / `_classes_declared_in`). This is a genuine
   import-consistency check, not a no-crash check — it re-derives the registry imports from
   the generated `__init__.py` and cross-checks declarations. ✅
2. **FORMULA channel sanitized, proven by a real fixture.** `test_formula_quoted_owner.py`
   asserts the *path resolved*: the consumer module's resolved input channel
   (`inp.source.producer_channel`, gated on `source_type == "module_output"`) equals the
   registry's registered canonical channel (`scoped_lookup(key_f)`), and that channel is the
   fully-sanitized `QuotedOwnerFormulaDesign__Margin_Part__net_margin__net_margin`. Fixture
   snapshot confirmed to carry 2 `classification: "formula"` computed attributes on quoted
   owner `'Margin Part'` (→ `Margin_Part`), attr `'net margin'` (→ `net_margin`),
   live-captured. This is INV-5 proven end-to-end, not string-equality. ✅
3. **No existing snapshot/baseline changes.** INV-1 reformulated corpus-honestly (see
   Deviation 1). The invariance scans prove the load-bearing property (no identifier-safe
   segment changes; every changed segment is a genuinely-quoted name off the byte-identity
   path). Byte-identity gate (`_tree_diff` over all snapshots + baselines) recorded empty at
   Phases 1/2/3. ✅ (rests on recorded gate — suite not re-run here.)
4. **Duplicate-path fail-fast across the write key spaces.** `_check_duplicate_output_paths`
   covers the two key spaces the collision spans: module/stencil python path (one key —
   stencils are `{filename}_impl.py` off the same `_get_python_path`) and schema
   `calc_def_name.lower()` (separate key). The schema pass guard (`len(outputs) < 2`) and key
   (`{calc_def_name.lower()}_output.py`) match the actual `_generate_schemas` loop
   (`cli/__init__.py:236-238`) byte-for-byte — I verified this directly, since it is the
   crux of the "schemas key space actually covered" question. Three tests
   (`test_duplicate_path_failfast.py`): module-path collision, schema-key collision (distinct
   packages, same schema file), and same-source-no-false-positive. Each error names both raw
   sources and the shared path. ✅
5. **SC-11 formally closed.** Recorded in close-out §"SC-11 closure" as intended/documented/
   tested; residual grandparent hole now a hard fail-fast; AST rewrite deferred. ✅
6. **agentic-mbse impact + coordination notes.** Item 7 lockstep, fusion-tea
   `sanitize_names.py` retirement, and MODELING_GUIDE guidance all recorded in close-out. ✅

**Non-goals respected.** Match sites and the `:130` registration key untouched (verified
below); no source-level extraction sanitization; no existing snapshot re-captured (the one
new fixture is additive); AST rewrite not built; fusion-tea not modified.

### Design conformance — implementation follows design

- **INV-2 (helper applied once).** `sanitize_qualified_name` splits on `::`, sanitizes each
  segment, joins with `__` — never applied to a `__`-joined string. Docstring pins the
  re-entrancy hazard. ✅
- **INV-3 (match sites + `:130` byte-unchanged).** Verified directly: commit 4b19e4d touches
  **none** of `dependency_backtracker.py`, `pipeline_builder.py`, `parameter_groups.py`. In
  the touched `output_registry_builder.py`, the `:130` registration key still reads
  `SysMLQN(f"{ca.owning_part_qualified_name}::{ca.name}")` (raw) — only the `:124` channel
  *value* was sanitized. Raw match sites confirmed present: `dependency_backtracker.py:595/660`,
  `pipeline_builder.py:70-71/81`. ✅
- **M1 (leaf from `python_name`).** Both `graph_builder.py:745` and `:789` build
  `f"{sanitize_qualified_name(owner)}__{ca.python_name}"`, never re-sanitizing `ca.name` —
  the keyword-edge divergence (B2) is structural. `derive_module_type` at `:794` correctly
  keeps the raw `sysml_qn` (a different identifier, sanitized inside `from_sysml`). ✅
- **Fail-fast placement.** Before `_clear_output_directory`, so a collision never wipes
  output. ✅
- **sanitize-then-lower order.** Both `from_sysml` methods sanitize before `.lower()`,
  matching `build_element_qualified_name`. ✅

### Code integrity — no issues

- `_check_duplicate_output_paths` and `_raw_source_name` are two focused, readable
  functions; no god-function, no mode sentinel. The collision keys on raw-source identity, so
  multiple usages of one calc def do not false-positive (tested).
- Fail-fasts raise loudly (`CodeGenerationError`, `ValueError`) — no silent fallback on an
  invariant violation, no broad `except`. The SC-11 re-check raises rather than papering the
  collision.
- No mocks, TODOs, FIXMEs, or placeholders in the new tests or `cli/__init__.py`.

### Recorded deviations — both sound

1. **INV-1 scan reformulated.** The literal design/plan stencil (`sanitize_name(seg) == seg`
   for every segment) is false on the corpus by construction — quoted names exist there by
   design (9 segments change). The reformulation asserts the property that actually underpins
   byte-identity: **no already-identifier-safe segment changes** (the dangerous accidental
   forms — edge underscore, `__` run, keyword — are absent), and every changed segment carries
   a non-`[A-Za-z0-9_]` character (a genuinely-quoted name off the byte-identity path). The
   two scans (`:145`, `:169`) prove this faithfully; the end-to-end `_tree_diff` remains the
   authoritative byte-identity proof. Sound — the reformulation is more honest than the
   stencil, not weaker.
2. **FORMULA fixture consumer is a computed attribute, not a calc usage.** The probe reasoning
   holds: a calc-usage consumer of a same-part FORMULA attribute produces a `::`-qualified
   REFERENCE `source_path` that routes through `dependency_backtracker._resolve_reference_dispatch`
   (`sysml_qn_lookup` at `:595`, then a raw leaf lookup at `:473`) — Item 7's match sites,
   untouched by Item 5, so a quoted owner stays unresolved there. The design's own appendix
   and site list (`graph_builder.py:745/:789`, the `resolution_map`) describe the
   computed-attribute path, which **is** an Item-5 site; the design explicitly left the
   concrete fixture SysML to the plan (design.md:369). Using a second same-part FORMULA attr
   (`total_payout = 'net margin' * 2.0`) as consumer proves INV-5 on exactly the Item-5 wire.
   Sound — a correction of imprecise design prose, not an invariant change. The close-out
   correctly re-files the calc-usage-under-quoted-owner case as Item 7's.
3. **Exception types** (`CodeGenerationError` / `ValueError` vs the plan stencil's loose
   `GenerationError`). Matches established precedents (`pipeline_context.py` zero-output;
   registry collision convention). Cosmetic; sound.

---

## Observations (non-blocking, no action required)

- **Stencil key space is covered transitively, not by an independent test.** The design (D2)
  establishes that stencils share the module python path (`{filename}_impl.py` off the same
  `_get_python_path`), so the module-path check covers them. This is correct and
  design-sanctioned, but no test asserts a stencil path cannot escape the module key — it
  rests on the design's "verify no stencil path is derived elsewhere," which is true today.
  If a future change ever derived a stencil path independently, the transitive coverage would
  silently lapse. Worth a one-line note in any Item 7 handoff, not a fix here.
- **Schema check adds `or not module.calc_def_name`** beyond `_generate_schemas`' guard. This
  is strictly more conservative (skips an empty-name multi-output module the generator would
  still write as `_output.py`). Not realistic in practice; harmless.

## Certification

Checked and verified: all 5 plan phases; all 6 spec success criteria; INV-1..INV-5; the three
match sites + `:130` untouched (diff-scope confirmed); M1 producer/consumer coincidence;
the schema key-space check against the real schema-gen condition; both `from_sysml` methods;
the fail-fast placement; the SC-11 CLEAN gate → hard fail-fast; docs 15/20 rows; both
coordination notes and the SC-11 closure in close-out; commit scope (18 files, matches);
no mocks/TODOs.

**Marked:** all spec success criteria (`- [x]`), all plan phase checkboxes, and the Item 5
heading/checkboxes in the epic. CURRENT_WORK.md updated to certified.

**Open (verification limit, not a defect):** the 1880/21/109 gate was not re-run — this
session is harness-blocked from `uv run pytest`. Certification rests on the recorded gate
plus the direct code/fixture inspection above. To fully close, re-run
`uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/` on 4b19e4d and confirm
1880 passed / ruff 21 / mypy 109. This is the same harness limit noted on Items 1–4.


---

## Orchestrator close-out (2026-07-05)

Verification limit covered: orchestrator ran the full gate at the committed code state
immediately before commit 4b19e4d: 1880 passed / 4 skipped / 5 xfailed; ruff 21; mypy 109
(== baseline). Verdict stands: **PASS**. Item 5 complete.
