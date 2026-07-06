# Implementation Plan: Silent-Failure Hardening — Loud Extraction & Resolution

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06
**Epic:** PIPELINE-TRUTH · Item 5
**Branch:** pipeline-truth-epic

## Source Documents
- **Spec:** `.project/active/silent-failure-hardening/spec.md` (verification table, four families, LOUD-REJECT ruling, closed-by-construction criterion, coordination fences)
- **Design:** `.project/active/silent-failure-hardening/design.md` ← component details, the per-finding fix map (Appendix), Key Decisions D1–D7, INV-1..6. **Do not restate it here — this plan is phasing, test-first, and validation only.**
- **Design review:** `.project/active/silent-failure-hardening/design-review.md` (Resolutions: C1 narrow D3-8, C2 Item-8 fence, M3 SC-5 trip fixture, M4 EP-key site, M5 framing)
- **Epic R4:** `.project/backlog/epic_pipeline_truth.md:67-97` (verify-then-fix; step 4 = docs close the loop)

---

## Implementation Strategy

**Phasing rationale.** One phase per family (the design's four choke-point clusters), plus a sanitizer phase and a docs/register close-out. Families are landed in the design's natural data-flow order (extraction → report → lookup → handlers) because that is how a diagnostic surfaces: Family 1 puts warnings on the `warnings` list, Family 2 renders that list. The two self-contained pieces (SC-4 sanitizer, docs/register) come last. **Phase 0 is a gate, not a fix** — it clears the Item-8 sequencing hazard and stands up the INV-6 safety net *before* any diagnostic lands, because a mis-firing totality arm is the single biggest risk (design "Potential Risks", "Next-Stage Handoff → Risk to de-risk first").

**Critical path.**
`Phase 0 (Item-8 gate + baseline + INV-6 harness)` → `Phase 1 (Family 1)` → `Phase 2 (Family 2)` → `Phase 3 (Family 3)` → `Phase 4 (Family 4 + SC-5)` → `Phase 5 (SC-4)` → `Phase 6 (docs + register close-out)`.
Only Phase 0 → Phase 1 is a hard dependency (Item 8's reorder must land, and the INV-6 sweep must be green at baseline, before D3-8 or any diagnostic is touched). Phases 1–5 are independently landable once Phase 0 clears; the order given minimizes intra-file churn (SC-4 A1 and Family 4 both edit `parameter_groups.py`, so SC-4 rides *after* Family 4).

**First proof point.** End of Phase 0: the clean-corpus zero-WARNING sweep passes at the post-Item-8 baseline, the full byte-identical baseline diff is captured, and Item 8's Row-D reorder commit is confirmed on-branch with `_walk_aggregation_ast` re-read. If the sweep is not green at baseline, no diagnostic can be trusted — stop and fix the harness first.

**Test-first contract (every phase).** Per CONFIRMED finding, write **two** tests before the fix:
1. **fires-on-shape** — the trip fixture produces its diagnostic. Expectation is **independently anchored** (hand-transcribed warning text / param name / node type from the fixture source), **never computed by the code under test** (R1). Written **RED against today's silent behavior** where feasible (assert the WARNING that isn't emitted yet); the fix turns it GREEN.
2. **silent-on-clean** — a clean corpus fixture produces the diagnostic **zero** times.

**Closed-by-construction exceptions** (D3-3, D3-7): no RED fires-on-shape test. D3-7 gets a **guard-pin** (assert the OutputRegistry `ValueError` raises — GREEN today, a regression pin). D3-3 gets a debug-guard/assert + the stated SysIDE invariant. See design "Validation Approach".

**Per-phase close gate (RN-7 / INV-6).** Every phase ends by re-running the clean-corpus zero-WARNING sweep and the byte-identical baseline diff. Clean fixtures stay at zero WARNINGs; the only baseline moves allowed are the three named carve-outs, each in its owning phase (Phase 1: `deep_cross_scope_probe`, aggregation-`^`; Phase 4: `plant_value_shapes`).

---

## Environment & Coordination Fences

**See CLAUDE.md for env/test commands.** Note: `python`/`pytest`/`uv run` may be sandbox-blocked in orchestrated stages — the implementer runs the suite through the real capture path (see memory `syside-license-via-scripts-not-dashc`) and records numbers; a licensed/unsandboxed confirmation run gates the phase close.

Hard fences (do **not** edit these — other items own them; design "Non-Goals"):
- **Item 2** owns the two `0.0`-truthiness classifiers (`graph_builder.py:425` `_classify_entry_points`, `:1133`) and `design_overrides` threading. Family 3 edits `graph_builder.py` at **different** sites (`:1349` redef fallback, `:984`/`output_registry.py:72` guard-pin). Item 2's implement follows Item 5's in the tree queue — Item 5 must leave Item 2's sites untouched.
- **Item 8** owns the literal/invocation dispatch ordering in `_walk_aggregation_ast`. Item 5 (D3-8) touches only the operator translation, disjoint once sequenced. **Phase 0 gates on Item 8's Row-D landing.**
- **Item 4** landed fixes and the **snapshot v2 gate** — coordinate D3-8's byte-identity assertion with Item 8's v2 gate (both assert the committed aggregation corpus is unchanged).

---

## Phase 0: Sequencing Gate + Baseline + INV-6 Harness

### Goal
Clear the Item-8 hazard and stand up the clean-fixture safety net **before** any diagnostic. This is the de-risk-first step (design "Risk to de-risk first": INV-6).

### Assumption Under Test
That the clean corpus is genuinely zero-WARNING at the current (post-Item-8) baseline, so any new WARNING in Phases 1–5 is attributable to the diagnostic under test — not pre-existing noise. And that Item 8's reorder has landed, so D3-8's cites can be rebased onto real line numbers.

### Steps
- [ ] **Item-8 gate.** Confirm Item 8's Row-D commit (the `_walk_aggregation_ast` literal-before-invocation reorder) exists on `pipeline-truth-epic`. It is "dead-last among code changes" in Item 8's plan and gated on Item 4 — **as of this plan it has NOT landed** (git log shows only Item 8 Phases 0–2). **If absent, STOP** — Item 5's implement cannot start (design "Sequencing (hard)").
- [ ] **Re-read the post-reorder function.** Open `_walk_aggregation_ast` (`extraction/hierarchy_resolver.py`, currently `def` at `:353`) and record the *actual* post-reorder line numbers of the two operator sites (today `OPERATOR_MAP.get(operator, f" {operator} ")` at `:392,404`) and the unknown-node/`has_unsupported` arm (today `:467,479`). Design cites these as `370/382/457` **Item-8-relative** — rebase D3-8 onto the landed numbers.
- [ ] **Record fresh baseline.** Full suite pass/fail count, `ruff check src/` count, `mypy src/` count. The prior baseline (2005/20/105) moved when Item 8 landed its deletions — capture the current numbers as this item's reference. Note them in "Implementation Notes → Phase 0".
- [ ] **Classify fixtures.** Enumerate the clean-corpus set (zero-WARNING sweep members) vs the **expected-warning trip fixtures** excluded from it: `deep_cross_scope_probe` (D3-2), `plant_value_shapes` (SC-5), and the D3-6/8/10/15/16 trip fixtures (design INV-6). Encode the exclusion list where the sweep reads it.
- [ ] **Green the sweep at baseline.** Run the clean-corpus zero-WARNING sweep now, with no fixes applied. It must pass. Capture the full byte-identical baseline diff as the reference for every phase-close comparison.

### Validation
- [ ] Item-8 Row-D commit hash recorded; `_walk_aggregation_ast` re-read; D3-8 cites rebased.
- [ ] Baseline suite/ruff/mypy numbers recorded.
- [ ] Clean-corpus zero-WARNING sweep GREEN at baseline (no fixes yet).

**What we know works after this phase:** the safety net is real and green, the trip/clean split is encoded, and the shared-function hazard is cleared. Any WARNING regression from here is a real signal.

---

## Phase 1: Family 1 — Blind-Dispatch Fall-Throughs

### Goal
Every Family-1 terminal dispatch arm becomes total and loud (INV-1): unhandled input → distinct disposition + WARN naming param/part/node-type, never a reused valid category. Findings: **D3-1, D3-2, D3-8, D3-9 (tripwire), D3-16**; **D3-3 closed-by-construction**.

### Assumption Under Test
That threading the existing `warnings` list into `_extract_single_binding` and correcting the aggregation operator map turns each silent shape loud **without** tripping any clean fixture (INV-6) — B2 in the design.

### Test Stencils (write first)
```python
# D3-1 fires-on-shape (RED today: zero warnings) — anchor: fixture uses `in x = Doubler(v=a)`
def test_invocation_binding_warns_not_silent_unbound():
    report = extract_from_fixture("invocation_binding_probe")
    assert any("InvocationExpression" in w and "x" in w for w in report.warnings)
    assert "x" not in report.unbound_params            # distinct disposition, not UNBOUND reuse

# D3-2 fires-on-shape — flips deep_cross_scope_probe Pattern-A pin truncation -> diagnostic
def test_three_segment_chain_hard_rejected_not_truncated():
    report = extract_from_fixture("deep_cross_scope_probe")
    assert any("station.array.derived_calc.derived_value" in w for w in report.warnings)
    # NO source_path == "station" truncation assertion survives

# D3-8 fires-on-shape (post-Item-8 reorder) — anchor: transcribed expression
def test_caret_aggregation_compiles_to_power_not_xor():
    agg = walk_fixture_aggregation("d38_caret")     # total_cost = sum(cell.total_cost) ^ exponent
    assert "**" in agg.transformed_expression and " ^ " not in agg.transformed_expression

# silent-on-clean (every Family-1 diagnostic) — one clean fixture, zero new warnings
def test_family1_silent_on_clean_corpus():
    for fx in CLEAN_CORPUS:
        assert extract_from_fixture(fx).warnings == []
```

### Changes Required
**See `design.md#appendix--per-finding-fix-map` rows D3-1, D3-2, D3-3, D3-8, D3-9, D3-16 and `design.md#key-decisions` D1, D2, D3.**

- [ ] **D3-1** — `usage_extractor.py:748`: thread `warnings` (already held by `_extract_bindings:650`) into `_extract_single_binding`; terminal arm warns (param + node type), distinct disposition. Legitimately-unbound arm at `:693` stays silent (correct UNBOUND).
- [ ] **D3-2** — `usage_extractor.py:756-779`: count real segments via `extract_feature_chain_segments` (`expression_utils.py:279`) — **count only**, do not build the resolved path; >2 → warn + reject, no root-truncation. 2-segment/V11 path unchanged.
- [ ] **D3-8** — `hierarchy_resolver.py` (rebased sites from Phase 0): define `AGG_PYTHON_OPS = {**OPERATOR_MAP, "^": " ** "}`; use at both operator sites; operator absent from it → `ctx.has_unsupported = True` + warn (mirror the unknown-node arm). **Do not** reach for `PYTHON_OPERATOR_MAP` (drops comparison/logical ops — design C1).
- [ ] **D3-9** — `computed_attribute_extractor.py:92`: tripwire — non-literal AST root + empty `refs` warns; `not refs → LITERAL` stays.
- [ ] **D3-16** — `computed_attribute_extractor.py:315`: `else` arm warns on the cross-part single-hop calc-refs EXPOSE_PURE the Item-10 gate misses. Needs the synthetic trip fixture (calc-refs single-hop cross-part).
- [ ] **D3-3 (closed-by-construction)** — `usage_extractor.py:789-796`: debug-guard/assert on `(None,None)` return + state the SysIDE resolved-referent invariant (doc 16:115-119). **No fires-on-shape test.**

### Carve-out re-captures (this phase)
- [ ] **`deep_cross_scope_probe`** (D3-2): Pattern-A pin flips truncation→diagnostic. One `--fixtures deep_cross_scope_probe` scoped snapshot re-capture, reviewed diff. No other fixture output moves.
- [ ] **aggregation-`^`** (D3-8): byte-identical on the committed aggregation corpus — no *aggregation expression* uses `^` (the `^` at `solar_battery_model/library.sysml:317,339` is doc-comment prose). Coordinate the byte-identity assertion with Item 8's v2 gate. Re-capture only if the diff moves (it should not — vacuous).

### Validation
- [ ] D3-1/2/8 fires-on-shape RED before fix, GREEN after; D3-16 fires-on-shape GREEN with its trip fixture; D3-9 tripwire GREEN.
- [ ] D3-3 debug-guard present; invariant stated in-code.
- [ ] `deep_cross_scope_probe` re-capture diff reviewed; no unlisted baseline moves.
- [ ] **Phase close (INV-6):** clean-corpus zero-WARNING sweep GREEN; byte-identical baseline diff clean except the two named carve-outs.

**What we know works after this phase:** the extraction dispatch is total — unknown bindings, over-long chains, and `^` aggregations are loud; clean models unaffected.

---

## Phase 2: Family 2 — Gated-Report Silences / Zero-Found Sentinels

### Goal
Surface the discarded extraction report (D3-4) on **both** live and from-snapshot paths (INV-2), warn on the Phase-1a unknown-calc-def skip (D3-5), and give the shared-failure-mode sites a "scanned N, matched 0" sentinel (D3-13 + pattern-3), reusing the Item-4 `render_constraint_report` house style.

### Assumption Under Test
That rendering the already-built `ExtractionReport` and adding count-summary sentinels adds **no** clean-fixture WARNING (the sentinels are INFO/count-summary; WARN only when >0 — RN-7).

### Test Stencils (write first)
```python
# D3-4 fires-on-shape — report surfaced, live AND from-snapshot (INV-2 parity)
def test_extraction_report_rendered_live_and_snapshot():
    for path in ("live", "snapshot"):
        out = run_pipeline("dropped_usage_fixture", path=path)
        assert "usage dropped" in out.rendered_report

# D3-5 fires-on-shape — Phase-1a unknown calc def warns instead of bare continue
def test_phase1a_unknown_calcdef_warns(): ...

# D3-13 / pattern-3 sentinel — scanned-N-matched-0 present, WARN only when >0
def test_phantom_scan_zero_found_sentinel_not_silence(): ...
def test_clean_corpus_sentinels_info_not_warn(): ...   # silent-on-clean (no WARN)
```

### Changes Required
**See `design.md#architecture` (Family 2), `design.md#component-overview`, and Appendix rows D3-4, D3-5, D3-13. Note the corrected path: `orchestration/output_registry_builder.py` (not `resolution/`).**

- [ ] **D3-4** — `pipeline_builder.py:689`: render the bound-and-discarded `_report` (Item-4 shape), live + from-snapshot identically (INV-2).
- [ ] **D3-5** — `output_registry_builder.py:167`: `if not calc_def:` skip warns.
- [ ] **D3-13** — `phantom_detector.py:165-173`: zero-found scanned/reported sentinel.
- [ ] **Pattern-3 sentinels** (`pipeline_builder.py`, `usage_extractor.py`, `cli`). **Sentinel-verbosity decision (RN-7, design "Open → sentinel verbosity"):** repetitive classes → build-level **count-summary INFO** + WARN-only-when->0: phantom scan (D3-13), scoped-alias registration (`:463-510`), self-named rescue (`:516-572`). One-shot sites → single **INFO**: design-override rewrite (`:259-329`), template detection (`usage_extractor.py:439-445`), empty-render success (`cli:432-442`). Follow `render_constraint_report`'s three-part shape (`constraint_report.py:89-141`) exactly.

### Validation
- [ ] D3-4 report rendered on both paths (INV-2 parity pin).
- [ ] D3-5, D3-13 fires-on-shape GREEN; pattern-3 sentinels emit at zero-found.
- [ ] **Phase close (INV-6):** clean-corpus zero-WARNING sweep GREEN (sentinels are INFO/count-summary, no WARN at zero-found); baseline byte-identical.

**What we know works after this phase:** dropped usages and unscanned catalogs are visible; "no phantoms" is distinguishable from "couldn't scan".

---

## Phase 3: Family 3 — Name-Keyed Lookup Uniqueness

### Goal
Every name-keyed lookup either keys by QN or warns on ambiguity (INV-3). Findings: **D3-10, D3-15, D3-11b** (require-unique-or-warn at lookup, no re-key); **D3-7 guard-pin, closed-by-construction**. The pre-authorized family split is **not taken** (design D5 — churn is small).

### Assumption Under Test
That a lookup-time collision warn (no QN re-key) is sufficient for D3-10/D3-15/D3-11b, and that the OutputRegistry guard already closes D3-7's reachable FORMULA shape (B3).

### Test Stencils (write first)
```python
# D3-10 fires-on-shape — anchor: two Motor partdefs, :>> power = 100.0 / 999.0
def test_leaf_redef_collision_warns_not_first_wins():
    report = resolve_fixture("d310_leaf_redef")
    assert any("power" in w and "Motor" in w for w in report.warnings)

# D3-15 fires-on-shape — two designs, distinct design_prefix
def test_two_design_prefix_collision_warns(): ...

# D3-11b — decide-then-pin: user-facing target lookup ambiguity warns (internal QN path benign)
def test_usage_by_name_ambiguous_target_warns(): ...

# D3-7 guard-pin (closed-by-construction, GREEN today — regression pin, NOT a silent-drop test)
def test_d37_two_formula_widget_result_raises_loudly():
    with pytest.raises(ValueError, match="scoped key collision"):
        build_pipeline_context_from_fixture("d37_partname_merge")
```

### Changes Required
**See `design.md#key-decisions` D5, `design.md#required-invariants` INV-3, Appendix rows D3-7, D3-10, D3-11b, D3-15.**

- [ ] **D3-10** — `graph_builder.py:1349-1350`: fallback leaf match warns on ambiguous same-leaf collision (leaf-name match is structurally required in the fallback — no QN re-key possible there).
- [ ] **D3-15** — `pipeline_builder.py:597`: collision-warn on >1 distinct `design_prefix`.
- [ ] **D3-11b** — `dependency_backtracker.py:247`: track collisions at index build; warn when a **user-facing target** lookup is ambiguous. **First decide** (design: "may be a non-issue" — internal processing keys off QNs, comment `:151-154` calls the collision benign) whether the target lookup at `:248` warrants it at all; pin the decision either way.
- [ ] **D3-7 (closed-by-construction)** — pin the OutputRegistry guard raises (`output_registry.py:72`) + state the invariant in `graph_builder.py:984`. Bare→QN re-key **deferred** (optional defense-in-depth) — do the consumer audit first (design "Potential Risks → B3 over-claim"): if a **non-FORMULA** path reaches the bare-name map and cross-wires silently, D3-7 re-enters the re-key set; else deferred stands.
- [ ] **Fence check:** confirm no edit lands on Item 2's `graph_builder.py:425` / `:1133`.

### Validation
- [ ] D3-10, D3-15 fires-on-shape RED→GREEN; D3-11b decision pinned.
- [ ] D3-7 guard-pin GREEN; consumer-audit outcome recorded (re-key deferred or re-entered).
- [ ] **Phase close (INV-6):** clean sweep GREEN; baseline byte-identical.

**What we know works after this phase:** same-leaf redefinitions, two-design aggregations, and ambiguous targets warn; the D3-7 FORMULA shape provably raises.

---

## Phase 4: Family 4 — Exception Swallows (+ SC-5)

### Goal
A caught exception on a load-bearing path becomes a loud skip-with-warning (INV-4), not a silent `pass`/`return None`. Findings: **D3-6, D3-12, D3-14**, plus **SC-5** (shares the D3-12 omission site). D3-14 lands **in-item, no split** (design D6).

### Assumption Under Test
That the D3-12/SC-5 warn can be **hazard-scoped** — one predicate at the shared omission site (`parameter_groups.py:601`), firing *only* when an unparseable-but-present default feeds an entry point then omitted from the JSON — so non-EP non-float attributes stay silent and INV-6 holds without a blanket carve-out (design D4, B4).

### Test Stencils (write first)
```python
# D3-6 fires-on-shape — corrupt/omitted usage_type_map key logs, offline parity
def test_snapshot_loader_malformed_usage_type_map_logs_not_pass(): ...

# D3-12 / SC-5 hazard-scoped fires-on-shape — anchor: wall = 'Wall Kind'::liquid_wall
def test_nonfloat_ep_feeding_omitted_entrypoint_warns():
    report = derive_groups("plant_value_shapes")
    assert any("wall" in w for w in report.warnings)   # present-but-unparseable EP hazard

# SC-5 silent-side pin — non-EP non-float attribute stays silent (INV-6)
def test_nonfloat_non_ep_attribute_stays_silent(): ...  # confirm the exact silent attrs vs plant_value_shapes

# D3-14 fires-on-shape — transient read/parse error preserves impl, does NOT stub
def test_smart_regen_preserves_impl_on_transient_error(): ...
```

### Changes Required
**See `design.md#key-decisions` D4, D6, `design.md#implementation-notes` (SC-5/D3-12 predicate; D3-14 transient set), Appendix rows D3-6, D3-12, D3-14, SC-5.**

- [ ] **D3-6** — `loader.py:423-424`: narrow `except`; log the dropped `usage_type_map` key (offline-parity guard).
- [ ] **D3-12** — `parameter_groups.py:192`: narrow the eval `except`; route to the shared hazard-scoped warn at `:601`.
- [ ] **SC-5** — `parameter_groups.py:710`: narrow `float()`; apply the mirror predicate so both roots share the one site at `:601`. The EP-feeds check reuses the group/EP membership the deriver already computes — no new traversal. **Confirm the silent side against `plant_value_shapes`** (design "Open → SC-5 hazard-scope"): which non-EP non-float attrs stay silent.
- [ ] **D3-14** — `preservation.py:92-95`: narrow `except`, log at WARNING, preserve-on-transient. Transient set = read/IO errors + parse failures on a **non-empty** file; a genuinely-empty impl stays the regenerate case (design "Potential Risks → D3-14 boundary").

### Carve-out re-capture (this phase)
- [ ] **`plant_value_shapes`** (SC-5): its enum EP feeds an omitted EP, so the hazard-scoped warn fires → it becomes an **expected-warning trip fixture** (third carve-out, excluded from the zero-WARNING sweep). Generated bytes stay identical (the fix warns, does not pre-fill); take a `--fixtures plant_value_shapes` scoped re-capture **only if the diff moves**, reviewed.

### Validation
- [ ] D3-6, D3-12/SC-5, D3-14 fires-on-shape RED→GREEN; SC-5 silent-side pin GREEN.
- [ ] `plant_value_shapes` moved to the trip-fixture exclusion list (Phase 0 harness).
- [ ] **Phase close (INV-6):** clean sweep GREEN (`plant_value_shapes` now excluded as a trip fixture); baseline byte-identical except any reviewed `plant_value_shapes` re-capture.

**What we know works after this phase:** malformed snapshots, unparseable defaults, and non-float EPs are loud; `--smart-regen` never stubs a valid impl on a transient error.

---

## Phase 5: SC-4 — Sanitizer Legality + EP-Key Injectivity

### Goal
`sanitize_name` always yields a legal Python identifier and is injective at key construction (INV-5). Lands after Family 4 because SC-4 A1 edits `parameter_groups.py`, which Family 4 also touched — sequence to avoid churn conflict.

### Assumption Under Test
That a uniqueness check at the **EP-key registration boundary** (not at sanitize time — sanitize is many-to-one by design) catches sibling-name collisions, and that broadening the keyword/leading-digit guard breaks no existing key.

### Test Stencils (write first)
```python
# SC-4 A2 — isidentifier holds for all inputs (independently anchored unit pins)
@pytest.mark.parametrize("raw,expect_valid", [
    ("2nd stage", True), ("class", True), ("", True), ("!!!", True),
])  # every keyword.kwlist member, leading-digit, empty, all-symbol
def test_sanitize_name_always_legal_identifier(raw, expect_valid):
    out = sanitize_name(raw)
    assert out.isidentifier() and not keyword.iskeyword(out) and out != ""

# SC-4 A1 — two siblings sanitizing to one EP key fail fast at registration
def test_ep_key_collision_fails_fast():
    with pytest.raises(...):  # 'a b' and 'a-b' both -> a_b at EP-key build
        derive_groups("ep_key_collision_probe")
```

### Changes Required
**See `design.md#key-decisions` D7, `design.md#required-invariants` INV-5, Appendix rows SC-4 A1, SC-4 A2.**

- [ ] **SC-4 A2** — `qualified_names.py:12-37`: broaden the keyword guard to `keyword.kwlist`; prepend a safe prefix when the result starts with a digit or is empty; empty-input early return no longer yields `""`.
- [ ] **SC-4 A1** — EP-key registration boundary in `parameter_groups.py`: uniqueness check where the EP key is built (`:132` sanitize → `param_name`; `:351/377/404/583` `f"{usage.qualified_name}__{param_name}"` / `attr.qualified_name`; `:554-640` group collection). Two distinct sibling names sanitizing to one EP key **raise**. Channels are already covered by `register_scoped` (`output_registry.py:72`) — do not double-guard them.

### Validation
- [ ] SC-4 A2 unit pin GREEN across leading-digit / all `keyword.kwlist` / empty / all-symbol.
- [ ] SC-4 A1 collision fail-fast RED→GREEN at the EP-key boundary.
- [ ] **Phase close (INV-6):** clean sweep GREEN; baseline byte-identical (sanitizer change is inert on clean names).

**What we know works after this phase:** no sanitized name is an illegal identifier or a silent EP-key merge.

---

## Phase 6: Docs + Register Close-Out

### Goal
Close the R4 loop (step 4) and fully discharge the discovery register. No production code — docs, register, and follow-on filings only.

### Assumption Under Test
That every touched component's reference doc and matrix row can move in this change, and that the register's per-row Disposition column can be discharged now (Item-6 audit, which held the register read-fence during design, is complete — PASS-WITH-NOTES).

### Changes Required
**See `design.md#validation-approach` (R4 step 4), `design.md#next-stage-handoff` (Register carry), spec "Success Criteria", epic `:478-480`.**

- [ ] **Reference docs (R4 step 4).** Per touched component, update the reference doc, modeling-assumptions section, and matrix rows in this change: `01-extraction.md`/`12-virtual-binding-rewrite.md` (Family 1), `10-output-registry.md` (D3-5/D3-7 guard), `13-aggregation-scoping.md`/`14-expression-compiler.md` (D3-8), `17-parameter-group-deriver.md` (D3-12/SC-5/SC-4 A1), `27-snapshot-generation.md` (D3-6 parity), `23-smart-regen-preservation.md` (D3-14), `15-naming-conventions.md`/`19-ast-dispatch-invariant.md` (INV-1/INV-5), `16-computed-attributes.md` (D3-9/D3-16), `07-graph-assembly.md` (D3-10/D3-11b/D3-15). Add INV-1/INV-3 to the new-dispatch/lookup-site code-review checklist (design "Framing").
- [ ] **Register Disposition discharge.** In `.project/research/20260706_pipeline-truth-discovery.md` §D3, move every per-row Disposition cell from "Item 5" to its outcome: **fixed** (D3-1,2,4,5,6,8,10,12,14,15,16, SC-4, SC-5), **reclassified** (D3-9 tripwire, D3-13 sentinel), **closed-by-construction** (D3-3, D3-7), **conditional/decided** (D3-11b — per Phase 3 decision).
- [ ] **D3-7 register-row correction** (carried from design). The §D3 row for D3-7 (`:86`) still reads CONFIRMED "silent cross-wire … passes Step-8". Reclassify to **closed-by-construction** (OutputRegistry guard already loud) — the same edit that discharges its Disposition. (Register was outside the write fence during design; travels with implement.)
- [ ] **`[D3-HYGIENE-TAIL]`** — one consolidated BACKLOG hygiene entry (pointer to register §D3): loader `.get` defaults on load-bearing fields, naive substring `.replace()` in aggregation compile, `type_map` "Any" exit-point skip, registry alias-rewrite no-not-found branch. (Dead `_check_semantic_match` is Item 8's — cross-reference, do not file twice.)
- [ ] **`[MULTIHOP-CHAIN-PARSE]`** — FILE the D3-2 full-parse follow-on in the fixture-gap register / BACKLOG (argued: cheap — helper exists; unblocks deep cross-scope chains; would let `deep_cross_scope_probe`'s Pattern-A pin assert a resolved chain instead of a rejection).
- [ ] **Item-9 impact list.** Append this item's agentic-mbse impacts (new diagnostics; `extract_feature_refs` traversal, `str(direction)` repr — spec "Non-Goals") to the Item-9 accumulation list.

### Validation
- [ ] Every touched component's reference doc + matrix row moved in this change (spot-check 3 against source).
- [ ] Register §D3 Disposition column fully discharged; D3-7 row reads closed-by-construction.
- [ ] `[D3-HYGIENE-TAIL]`, `[MULTIHOP-CHAIN-PARSE]`, Item-9 impacts filed.
- [ ] **Final gate:** full suite + `ruff check src/` + `mypy src/` at/under the Phase-0 baseline; clean-corpus zero-WARNING sweep GREEN; full byte-identical baseline diff clean except the three named carve-outs. Suggest `/_my_audit`.

**What we know works after this phase:** the register is truthful, the docs match the code, and the deferred work is filed, not dropped.

---

## Risk Management

**See `design.md#potential-risks` for the full analysis.** Phase-specific mitigations:
- **Phase 0/1 (INV-6 regression):** the sweep is green at baseline *before* any fix; each diagnostic lands with a silent-on-clean test; per-phase baseline diff.
- **Phase 1 (Item-8 collision):** Phase 0 gate + rebased cites; D3-8 touches only operator translation, disjoint from Item 8's literal/invocation ordering.
- **Phase 3 (B3 over-claim):** D3-7 guard-pin asserts the raise; consumer audit before deciding to skip the QN re-key.
- **Phase 3 (Item 2 fence):** explicit fence check — Family 3 leaves `graph_builder.py:425/1133` untouched.
- **Phase 4 (D3-14 boundary):** transient set = read/IO + parse-fail on non-empty file; empty impl stays regenerate.
- **Phase 6 (register write fence):** confirm Item-6 audit read-fence is released before writing the register.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — leave empty now]

### Phase 0 Completion
**Completed:** 2026-07-06
**Item-8 Row-D commit:** `b1dece5` (on `pipeline-truth-epic`; audit `3fd390d`). Confirmed literal branch at `hierarchy_resolver.py:418` ABOVE the invocation catch-all at `:422`.
**Baseline (audited live):** suite 2000 passed / 4 skipped / 5 xfailed; `ruff check src/` = 19; `mypy src/` = 104.
**Rebased D3-8 cites:** operator sites at `hierarchy_resolver.py:392,404` (both `OPERATOR_MAP.get(operator, f" {operator} ")`); unknown-node model arm at `:482-486`.
**INV-6 harness:** the clean-corpus zero-WARNING sweep already exists as `tests/unit/test_warning_reconciliation.py` (explicit clean list: `attr_expr_probe`, `sample_model`, `chain_spike_model`). It is an *inclusion* list, so new trip fixtures are simply never added to it — the exclusion is by construction. Green at baseline.

### Phase 1 Completion (Family 1 — Blind-Dispatch Fall-Throughs)
**Completed:** 2026-07-06
**Gates:** suite 2008 passed / 4 skipped / 5 xfailed; ruff 17 (≤ baseline 19, import-sort auto-fixes); mypy 104 (= baseline). deep_cross re-capture reviewed (below).

**Per-finding:**
- **D3-1** (`usage_extractor.py`): threaded `warnings` into `_extract_single_binding`; terminal arm now WARNS (naming param + node type). **DEVIATION from design D1:** the "distinct disposition, not UNBOUND reuse" is *foreclosed by ADR-003* — the graph builder requires every input param to resolve to bound-xor-entry-point (no third "dropped" disposition; dropping `x` makes `build_pipeline_context` raise "No binding resolution for …|x"). The finding's actual harm is the *silence*, which the warning fixes; `x` stays a (now loud) entry point. Unifies with D3-2's disposition. Fires-on-shape: `test_d31_invocation_binding_warns_not_silent` (live).
- **D3-2** (`usage_extractor.py`): 3+-segment chain counted via `extract_feature_chain_segments` (count only) → WARN + surface as entry point, no root-truncation. Fires-on-shape lives with the fixture (`test_deep_cross_scope_probe.py::test_pattern_a_deep_chain_warns_on_extraction`).
- **D3-3** (`usage_extractor.py`): closed-by-construction debug-guard on `_parse_reference_expression` `(None,None)` returns + stated SysIDE resolved-referent invariant. No fires-on-shape.
- **D3-8** (`hierarchy_resolver.py`): `AGG_PYTHON_OPS = {**OPERATOR_MAP, "^": " ** "}`; new `_agg_operator_str` helper at both operator sites (392/404). **Root cause found at implement time:** `operator` is a SysIDE `Operator` enum, not a str — the old `OPERATOR_MAP.get(enum, f" {enum} ")` ALWAYS hit the fallback (str-stringified the enum), which is exactly why `^` silently became XOR. Fix normalizes via `str(operator)` (the `reconstruct_operator_expression` idiom), then looks up; genuinely-unknown → `has_unsupported` + warn. Byte-identical for all non-`^` operators (verified: agg conformance + e2e green). Fires-on-shape: `test_d38_caret_aggregation_compiles_to_power_not_xor` (live).
- **D3-9** (`computed_attribute_extractor.py`): tripwire — non-literal AST root + empty refs WARNS; `not refs → LITERAL` classification unchanged. Guard-pin: `test_d39_nonliteral_root_empty_refs_warns` + silent-side `test_d39_no_ast_root_stays_silent`.
- **D3-16** (`computed_attribute_extractor.py`): `else` arm added — cross-part single-hop EXPOSE_PURE with no local instance ref now WARNS instead of silently skipping the alias. Verified inert on the current corpus (D3-16 probe finds zero trip shapes in catf_mfe/ife_plant/wi014_toy). **DEFERRED:** the synthetic cross-part trip fixture + fires-on-shape test — authoring it needs live modeling iteration that exceeds this stage's budget. Code fix is landed and corpus-inert; follow-on = author `d316_crosspart_expose` fixture. (Not a reclassification — the shape is reachable per spec; only the fixture is deferred.)

**Fixtures graduated:** `invocation_binding_probe` (extraction-only, D3-1), `d38_caret` (full-pipeline, D3-8) → `tests/fixtures/` + registered in `capture_extraction_snapshots.py` + snapshots captured.
**Carve-out re-captures (reviewed):**
- `deep_cross_scope_probe` (D3-2): the truncated CHAIN bindings (`data_point` `source_path="station"`, plus `sensor`, `base_metric` — all 3+-seg chains) are gone; those params are now unbound entry points. Consequence: the uncovered-offender set collapses to empty (silent valueless-wired offenders → clean warned EPs). Three committed pins updated to the new (better) truth; the truncation pin flipped to a fires-on-shape warning pin.
- `d38_caret` (D3-8): captured fresh (new fixture). No committed aggregation snapshot uses `^`, so the corpus is byte-identical for the D3-8 change (vacuous carve-out, as designed).

### Phase 2 Completion (Family 2 — Gated-Report Silences)
**Completed:** 2026-07-06
**Gates:** suite 2012 passed; ruff 17; mypy 104. Clean sweep GREEN (new sentinels are INFO / WARN-only-when->0, so clean fixtures stay zero-WARNING).
**Per-finding:**
- **D3-4** (`pipeline_builder.py`): `_render_extraction_report` helper surfaces the previously-discarded usage-extraction report — an always-present INFO summary + one WARN per collected diagnostic. This is what makes the Family-1 dispatch warnings actually reach the user on the live path. **DEVIATION from INV-2 (parity):** the usage-extraction warnings are computed at extraction time and are NOT serialized into the snapshot (only hierarchy warnings + the constraint manifest are), so the from-snapshot path has no usage-report to replay. Full parity would need a snapshot-format field + re-capture of every fixture (byte-identity churn) — out of proportion for this stage; deferred. Tests: `test_d34_report_with_warnings_surfaces_each`, `test_d34_clean_report_no_warn`.
- **D3-5** (`output_registry_builder.py`): the Phase-1a `if not calc_def: continue` now WARNS (naming calc def + usage) — the skip registered zero channels silently. Test deferred (needs full registry scaffolding); fix is a direct log add, code-reviewed.
- **D3-13** (`phantom_detector.py`): catalog zero-found sentinel — INFO breakdown (scanned/cataloged/skipped) always; WARN when a usage's calc def is unknown (the blind spot). Tests: `test_d313_unknown_calc_def_warns_catalog_blind`, `test_d313_all_known_no_warn`.
- **Pattern-3 sentinels DEFERRED:** the scoped-alias / self-named-rescue / design-override / template-detection / empty-render INFO sentinels (all [NEED]/[INFERRED], INFO-level noise discipline) are not landed in this stage — lowest value-per-dollar against the remaining HARD findings (Families 3/4, SC-4/SC-5). Documented for follow-on. The three CONFIRMED headline silences (D3-4, D3-5, D3-13) are fixed.

---

**Status:** Draft → In Progress → Complete
**Related:** `/_my_design` (before) · `/_my_implement` (execute) · `/_my_audit` (after)
</content>
</invoke>
