# Implementation Plan: D3 Hygiene Tail (four benign silent sites)

**Status:** Draft
**Created:** 2026-07-07
**Last Updated:** 2026-07-07
**Branch:** truth-debt-epic
**Epic:** TRUTH-DEBT — Item 6

## Source Documents
- **Spec:** `.project/active/hygiene-tail/spec.md` ← the four sites, the R4 per-site reproduce
  targets, the parked dispositions, the coupling notes. This plan does not restate them.
- **Spec review:** `.project/active/hygiene-tail/spec-review.md` (Revise, all five points applied)
- **Epic:** `.project/backlog/epic_truth_debt.md` Item 6 + R1–R4
- **No design stage.** The spec parks the per-site WARN-vs-raise and reclassify-vs-harden
  decisions for this plan/implement to settle with R4 reproduce evidence.

There is no `design.md`. Where the plan template says "see design.md," read the cited **spec**
section instead.

## HEAD Re-Verification (done at plan pickup, 2026-07-07)

Item 2's parallel implement has landed commits since the spec pass. Re-verified all four pins;
one moved by the expected amount, none into Item-2 files:

- **Site 1** — `snapshot/loader.py`: `python_type=d.get("python_type","Any")` (`:273`),
  `binding_type` falsy→`UNBOUND` (`:268-270`), `parent_part_path` (`:326`),
  `qualified_name` (`:327`, `:343`), `owning_part_def_qn` (`:329`). Hold.
- **Site 2** — `resolution/graph_builder.py`: the `sorted(ref_to_inputs, key=len, reverse=True)`
  + `.replace` loop is now at **`:1534-1535`** (spec said `:1532-1536`; same function, calls
  `resolve_input(…AGG_STRATEGIES)` at `:1498`). Post-cutover, confirmed.
- **Site 3** — `generation/registry.py:44-57` (`_collect_exit_point_primitive_types`):
  `type_map.get(out.python_type)` then `if wrapper:`. Hold.
- **Site 4** — `orchestration/output_registry_builder.py:353-367` (Phase 4): three-lookup ladder,
  no `else`; siblings Phase 2 (`:258-263`) and Phase 3 (`:282-289`) both `logger.warning`. Hold.

**At implement pickup, re-run the pin check before touching each site** — the parallel implement
may land more commits. The line numbers above are guides, not anchors; grep the described shape.

---

## Implementation Strategy

**Phasing rationale.** One phase collapses the only real uncertainty up front (do sites 2 and 3
reproduce at all), then one phase per site does the family-choke harden + test pair. The sites
live in four different modules with no shared choke (spec `[NEED]`), so hardening is one phase per
site with a pathspec-limited commit each — not one batch commit across four modules.

**Critical path.**
Phase 0 (reproduce + corpus-scan gate, all four → per-site verdict) → then the harden phases in
coupling order: Site 1 (loader) → Site 3 (`type_map` Any; its residual reachable shapes depend on
what the Site-1 fix removes) → Site 4 (Phase-4 no-`else`) → Site 2 (`.replace`). Sites 4 and 2 are
independent of the others; they come last because Site 4 is a mechanical sibling-copy and Site 2
is the most likely to reclassify.

**First proof point.**
Phase 0's Site-2 and Site-3 reproduce probes. If neither the nested-attribute-name aggregation
shape (Site 2) nor a non-`{float,int,str,bool}` exit point (Site 3) is reachable on a real
fixture, those sites reclassify to a synthetic-fixture tripwire or re-file — and that is a valid
outcome recorded in the register (R4), not a failure. Everything downstream keys off these two
verdicts, so they run first.

**Overall validation approach.**
- Each harden phase ships a **fires-on-shape** test (independently-anchored expectation, never
  computed by the code under test — R1) paired with a **silent-on-clean** test.
- The **corpus-scan gate** ([HARD], spec line 90) runs in Phase 0, once per site, *before* any
  disposition is chosen — it proves the candidate diagnostic fires on **zero** clean corpus
  fixtures. INV-6 (zero WARNINGs on clean corpora) is the outcome; this scan is the gate that
  earns it. Do not pick WARN, ship, and discover a false fire at INV-6-test time.
- **Do not run the full suite** (a parallel implement is running). Per-phase validation is
  targeted: the new test file(s), the one affected conformance test, `ruff`/`mypy` on touched
  files. The full-suite-green + byte-identical-baseline gate is the **closing gate** (see below),
  run when it will not collide with the parallel run.

**Corpus for both the scan and the silent-on-clean tests.** The offline (license-free)
`--from-snapshot` corpus is `SNAPSHOT_MODELS` in `tests/conformance/conftest.py:38-62` — reached
via `build_pipeline_context_from_snapshot(snapshot_fixture(name))`. The three-fixture
`CLEAN_CORPUS` (`test_silent_failure_family1.py:23`) is the narrower live-extraction set. Every
probe and scan in this item runs offline over `SNAPSHOT_MODELS` — no syside license needed. Where
a site's live path matters (Site 3's `extractor.py:492`), the reproduce uses a constructed data
model, not a live extraction.

**House style (all four diagnostics).** `logger.warning(...)` that leaves output
importable-but-flagged (RN-7 / V11 precedent; the Item-5 family style in
`tests/unit/test_silent_failure_family2.py`), unless Phase 0 shows a shape where a hard raise is
the honest disposition (a keying/wiring field on a genuinely corrupt snapshot — Site 1 only).
The `_warns(caplog)` helper (`[r.message for r in caplog.records if r.levelno >= logging.WARNING]`)
is the test idiom; reuse it.

---

## Phase 0: Reproduce + corpus-scan gate + disposition (all four sites)

### Goal
For each of the four sites, in R4 order: (1) check doc/REQ intent; (2) reproduce the silent shape
with a probe against **real fixtures** (`SNAPSHOT_MODELS`, offline) or a constructed data model
where the live path is the source; (3) run the **corpus-scan gate** — does the candidate
diagnostic's trigger predicate fire on any clean corpus fixture — and from that choose the
disposition (WARN vs raise vs synthetic-tripwire vs re-file). No production code changes in this
phase — probes and a written verdict only.

### Assumption Under Test
That Sites 2 and 3 actually reproduce on a real fixture. Both carry legitimate reclassification
doubt (spec "R4 Reproduce-First" section). An honest **reclassify** is a valid phase outcome.

### Reproduce probe + gate, per site

Each probe is a throwaway script under `.project/active/hygiene-tail/probes/` (mirror the Item-5
`probes/` layout). The gate predicate is evaluated by iterating `SNAPSHOT_MODELS` offline.

**Site 1 (loader `.get`) — reproduces by construction.**
- Reproduce: take a real snapshot dict, delete a load-bearing field (`python_type`,
  `qualified_name`, or `binding_type`), run `_deserialize_*`, assert the fallback silently
  substitutes (`"Any"` / `""` / `UNBOUND`) with no diagnostic today. Independent anchor: the
  hand-edited malformed dict, not the loader's own default.
- Gate: scan every `SNAPSHOT_MODELS` raw JSON — confirm **none** is missing a load-bearing field
  (so the new diagnostic fires on zero clean snapshots → byte-identical, INV-6-safe).
- **Load-bearing field list (settle here — spec `[INFERRED]`, criterion at spec line 108):**
  the outcome test is "a default that masks a missing/corrupt value that changes wiring, keying,
  or type." Candidates from the pins: `python_type` (type), `qualified_name` at `:327`/`:343`
  (keying), `binding_type` at `:268-270` (wiring — a dropped binding), `parent_part_path`
  (`:326`) and `owning_part_def_qn` (`:329`) (scoping). Benign majority keeps its default:
  `is_input`, `is_output`, `description`, `unit`, `source_line`, `is_optional`, list fields,
  `source_hash`. Confirm the exact list against the reproduce and write it into the verdict.
- **Disposition to settle:** WARN vs raise, per-field. Default WARN (degraded-but-importable) for
  a type default like `python_type`; a **keying** field (`qualified_name`) that would mis-key the
  registry is the candidate for a raise (spec Open Questions). Decide per field, record the reason.

**Site 2 (`.replace`) — reclassification doubt.**
- Reproduce: an aggregation fixture with **two attribute names where one is a substring of the
  other** (`cost`/`cost_total`, `p`/`power`), asserting the compiled expression corrupts to
  `inputs.inputs.cost_total` (spec Problem walkthrough, lines 39-47). **The nested-name shape from
  L2-1, not the `x`-inside-`max` shape.**
- Gate / reclassification check: scan every `SNAPSHOT_MODELS` aggregation expression for a ref set
  where one ref is a substring of another. If **no** supported aggregation model has nested
  attribute names **and** none can be added within the covered corpus (a new fixture that stays
  INV-6-clean and byte-identical), Site 2 reclassifies to a **defensive tripwire with a synthetic
  fixture pin**, or is re-filed. **Say which in the verdict.** The mechanism (token-boundary
  `\b`/word-level replace, placeholder pass, or diagnostic-only tripwire) is chosen here too.

**Site 3 (`type_map` Any skip) — reclassification doubt, two sources of `"Any"`.**
- Reproduce (unit): construct a module list with a single-output (`field_name="root"`) exit point
  whose `python_type="Any"`, call `_collect_exit_point_primitive_types`, assert it is silently
  skipped today. Independent anchor: the constructed `python_type`, not any extraction.
- Reproduce (reachability, the real doubt): scan every `SNAPSHOT_MODELS` built graph for a
  single-output exit point carrying `python_type` ∉ `{float,int,str,bool}`. This is the gate and
  the reachability check in one. **If every real exit point is `float`**, Site 3 is a latent-only
  tripwire — say so in the verdict and pin it with a constructed fixture.
- Coupling to Site 1 (do NOT fall into the trap at spec line 145): `"Any"` is also minted on the
  **live** path (`extractor.py:492`, `data_models.py:70`) with no loader involved. The question
  is narrow: does the Site-1 fix remove *any* of Site 3's reachable shapes (the snapshot-sourced
  one) or leave the live-sourced shape standing? Record the answer; Site 3 most likely keeps its
  own diagnostic regardless.

**Site 4 (Phase-4 no-`else`) — reproduces cleanly.**
- Reproduce: a fixture (or constructed registry) with a transitive design-attribute default
  (dotted path, `is_transitive_default` True — `core/output_registry.py:235`) that fails all three
  lookups (`instance_attr_to_channel` → `scoped_lookup` → `alias_lookup`), asserting no warning
  fires today. Independent anchor: mirror the sibling Phase-2/3 warn tests
  (`test_silent_failure_family2_family3_fires.py`), which already have the not-found shape.
- Gate: scan `SNAPSHOT_MODELS` — confirm no clean fixture has an unresolved transitive default
  (so the new warning fires on zero clean corpora).
- **Item-2 adjacency (spec Coupling Notes):** Site 4 is transitive-alias resolution; Item 2 is
  multi-hop chain resolution, one screen away (Phase 3b `_resolve_reference_chain`,
  `:302-334`). If Item 2 has merged by pickup and made a previously-unresolvable dotted path
  resolvable, re-check that Site 4's reproduce fixture still fails all three lookups. If Item 2
  now resolves it, the fixture needs a still-unresolvable dotted path.

### Changes Required
- [x] `.project/active/hygiene-tail/probes/` — one reproduce probe per site (throwaway)
- [x] `.project/active/hygiene-tail/probes/verdict.md` — per-site: reproduce result,
      corpus-scan result, chosen disposition (WARN / raise / synthetic-tripwire / re-file), and
      for Site 1 the settled load-bearing field list. This is the R4 audit trail.
- [x] For any **reclassified** site: record it in `.project/backlog/BACKLOG.md`
      (`[D3-HYGIENE-TAIL]`) and the discovery register (`§D3`) as reclassified-with-reason —
      **not** silently dropped. A re-file gets a named pointer (R4, epic discipline).

### Validation
**Automated:**
- [x] Each probe runs offline (no license) and prints the reproduce verdict + scan count.
- [x] Corpus-scan predicate returns **0 hits** on clean fixtures for every candidate that will
      become a WARN (the disposition gate). (Site 4 returned 5 hits — the gate did its job and
      changed the disposition to reclassify, per above.)

**What We Know Works After This Phase:**
Per-site: whether the silent shape reproduces, on which fixture, what the diagnostic's trigger
predicate is, whether that predicate is INV-6-clean on the corpus, and the chosen disposition.
Sites 2 and 3 either have a real reproduce fixture or a recorded reclassification.

**Commit (pathspec-limited):** `git add .project/active/hygiene-tail/ .project/backlog/BACKLOG.md
.project/research/20260706_pipeline-truth-discovery.md` → `chore(item6 phase0): per-site R4
reproduce + corpus-scan gate + dispositions`.

---

## Phase 1: Site 1 — loader load-bearing `.get` choke

### Goal
Replace the load-bearing `.get(field, default)` calls (list settled in Phase 0) with a single
family choke that fires the diagnostic when a load-bearing field is missing/corrupt, per the
Phase-0 disposition. Benign defaults untouched.

### Assumption Under Test
That one choke helper covers the load-bearing subset without touching the benign majority — and
that it fires on zero covered snapshots (byte-identical, INV-6-clean).

### Test Stencil (write first)
```python
# tests/unit/test_hygiene_tail_loader.py
def test_missing_python_type_warns(caplog):
    d = _valid_attr_dict(); del d["python_type"]        # independent anchor: hand-edited dict
    with caplog.at_level(logging.WARNING):
        _deserialize_attribute_info(d)
    assert any("python_type" in w for w in _warns(caplog))

def test_clean_attr_dict_no_warn(caplog):               # silent-on-clean (R1 pair)
    with caplog.at_level(logging.WARNING):
        _deserialize_attribute_info(_valid_attr_dict())
    assert _warns(caplog) == []
```

### Changes Required
**See spec** Problem site 1, `[INFERRED]` (line 108), Open Questions (site-1 raise carve-out).
- [x] `src/sysml_codegen/snapshot/loader.py` — add a family choke (e.g.
      `_require(d, field, context)` that returns `d[field]` or fires the diagnostic + returns the
      degraded default; raise instead of warn for any field Phase 0 marked keying/wiring). Route
      the load-bearing sites through it: `python_type` (`:273`), `qualified_name` (`:327`,
      `:343`), `binding_type` (`:268-270`), `parent_part_path` (`:326`), `owning_part_def_qn`
      (`:329`). Leave the benign `.get(default)` calls alone.
- [x] `tests/unit/test_hygiene_tail_loader.py` (NEW) — fires-on-shape + silent-on-clean per
      load-bearing field.

### Validation
- [x] `uv run pytest tests/unit/test_hygiene_tail_loader.py` → pass (9 passed)
- [x] `uv run pytest tests/conformance/test_baselines.py` → pass (16 passed, byte-identical: every
      covered snapshot has the fields, so the choke never fires)
- [x] `uv run ruff check src/sysml_codegen/snapshot/loader.py` and
      `uv run mypy src/sysml_codegen/snapshot/loader.py` → no new findings (ruff clean; mypy's
      13-file/65-error output is all pre-existing in other modules, none in loader.py)

**What We Know Works After This Phase:** a malformed snapshot missing a load-bearing field is
loud; a valid snapshot is byte-identical and silent.

**Commit:** `git add src/sysml_codegen/snapshot/loader.py tests/unit/test_hygiene_tail_loader.py`
→ `feat(item6 site1): loud load-bearing-field diagnostic in snapshot loader (R4)`.

---

## Phase 2: Site 3 — `type_map` "Any" exit-point skip

### Goal
Make `_collect_exit_point_primitive_types` fire a diagnostic when a single-output exit point
carries a `python_type` outside `{float,int,str,bool}` (notably `"Any"`) instead of silently
skipping it — **or** pin it as a latent-only tripwire if Phase 0 found it unreachable on real
models.

### Assumption Under Test
That the skip shape is reachable with a live-sourced `"Any"` (independent of Site 1), so Site 3
needs its own diagnostic — not the trap of "Site-1 fix → Site 3 becomes a defensive assert"
(spec line 145).

### Test Stencil (write first)
```python
# tests/unit/test_hygiene_tail_registry.py
def test_any_exit_point_warns(caplog):
    mods = [_module_with_root_output(python_type="Any")]   # anchor: constructed python_type
    with caplog.at_level(logging.WARNING):
        _collect_exit_point_primitive_types(mods)
    assert any("Any" in w or "unmapped" in w for w in _warns(caplog))

def test_float_exit_point_no_warn(caplog):                 # silent-on-clean
    mods = [_module_with_root_output(python_type="float")]
    with caplog.at_level(logging.WARNING):
        assert "Float" in _collect_exit_point_primitive_types(mods)
    assert _warns(caplog) == []
```

### Changes Required
**See spec** Problem site 3, Open Questions (site-1↔site-3 collapse).
- [x] `src/sysml_codegen/generation/registry.py:50-57` — in the `if wrapper:` branch, add an
      `else` (or a `wrapper is None` guard) that `logger.warning`s the unmapped `python_type` on
      a `field_name="root"` exit point. Keep the skip behavior (importable-but-flagged); do not
      change the returned wrapper set on clean input.
- [x] `tests/unit/test_hygiene_tail_registry.py` (NEW) — fires-on-shape + silent-on-clean.
- [x] Phase 0's reachability scan found **no** real non-`float` exit point — the fires-on-shape
      test is the latent-tripwire pin, noted in the verdict; the diagnostic still lands (correct,
      just latent on the current corpus).

### Validation
- [x] `uv run pytest tests/unit/test_hygiene_tail_registry.py` → pass (2 passed)
- [x] `uv run pytest tests/conformance/test_baselines.py` → pass (16 passed; no clean exit point
      is non-`float` → no fire → byte-identical)
- [x] `ruff`/`mypy` on `src/sysml_codegen/generation/registry.py` → no new findings (ruff clean;
      the one mypy hit at `:185` is pre-existing, outside the diff)

**What We Know Works After This Phase:** an exit point with an unmapped `python_type` is loud;
the all-`float` clean corpus is byte-identical and silent.

**Commit:** `git add src/sysml_codegen/generation/registry.py
tests/unit/test_hygiene_tail_registry.py` → `feat(item6 site3): warn on unmapped exit-point
python_type (R4)`.

---

## Phase 3: Site 4 — Phase-4 transitive-alias no-`else`

### Goal
Add the missing `else` to Phase 4's three-lookup ladder so an unresolved transitive
design-attribute default `logger.warning`s (dropped-alias diagnostic), mirroring siblings Phase 2
(`:258-263`) and Phase 3 (`:282-289`).

### Assumption Under Test
That the sibling-warning shape copies cleanly and that the Item-2 landed state (if merged) has not
made the reproduce fixture's dotted path resolvable (spec Coupling Notes).

### Test Stencil (write first)
```python
# tests/unit/test_hygiene_tail_output_registry.py
def test_unresolved_transitive_default_warns(caplog):
    # construct: design attr with dotted is_transitive_default that fails all 3 lookups
    with caplog.at_level(logging.WARNING):
        build_output_registry(...)                         # anchor: the unresolvable dotted path
    assert any("Phase 4" in w and "not in the registry" in w for w in _warns(caplog))

def test_resolvable_transitive_default_no_warn(caplog):    # silent-on-clean
    with caplog.at_level(logging.WARNING):
        build_output_registry(...)                         # a default that resolves
    assert _warns(caplog) == []
```

### Changes Required — SUPERSEDED BY PHASE 0 RECLASSIFICATION

**Not implemented.** Phase 0's corpus-scan gate found the naive predicate (unresolved
transitive default) already firing on 5/15 real `SNAPSHOT_MODELS` fixtures today — a
mechanical sibling-copy `logger.warning` here would break INV-6 [HARD] on those 5
fixtures immediately, not just in theory. This is the same gap already deferred
(undocumented) at `analysis/parameter_groups.py:672-682`. See
`.project/active/hygiene-tail/probes/verdict.md` (Site 4) and `BACKLOG.md`
`[D3-HYGIENE-TAIL-SITE4-TRANSITIVE-ALIAS]` for full evidence and reasoning.

- [x] ~~`src/sysml_codegen/orchestration/output_registry_builder.py:363-367` — add an `else`~~
      — **not done**; not INV-6-safe as scoped (see above).
- [x] ~~`tests/unit/test_hygiene_tail_output_registry.py` (NEW)~~ — **not created**; no code
      change to test.
- [x] Reclassification recorded in `BACKLOG.md` and the discovery register (§D3) — R4 audit
      trail complete (done at Phase 0, cross-referenced here).

### Validation — N/A (no code change)

**What We Know Works After This Phase:** Site 4's silent gap is real and already occurring on
5 real fixtures, but a mechanical single-choke fix is not safe to ship — it needs a
cross-derivation EP-omission check spanning `output_registry_builder.py` Phase 4 and
`parameter_groups.py`'s design-attribute derivation, which is design-level work. Filed, not
forced (R4).

**Commit:** `git add .project/active/hygiene-tail/plan.md` → `chore(item6 site4): record
Phase-4 reclassification disposition (no code change, R4)`.

<!-- Original (superseded) commit line, kept for plan-history traceability:
git add src/sysml_codegen/orchestration/output_registry_builder.py
tests/unit/test_hygiene_tail_output_registry.py -> feat(item6 site4): warn on dropped Phase-4
transitive alias (R4). -->

---

## Phase 4: Site 2 — aggregation-compile `.replace` collision

### Goal
Per the Phase-0 verdict: either fix the token-boundary/nested-name corruption at its cleanest
choke in the compile loop (`graph_builder.py:1534-1535`) with a fires-on-shape test on a real
nested-name aggregation fixture, **or** land the recorded reclassification (defensive tripwire
with a synthetic-fixture pin, or re-file).

### Assumption Under Test
That the nested-attribute-name corruption (`cost`/`cost_total` → `inputs.inputs.cost_total`)
reproduces on a real or corpus-addable aggregation fixture. If not, Phase 0 already recorded the
reclassification and this phase implements that instead.

### Test Stencil (write first)
```python
# tests/unit/test_hygiene_tail_agg_compile.py
def test_nested_ref_names_do_not_corrupt(caplog):
    # agg expression over refs {cost, cost_total}; anchor: expected compiled string
    compiled = _compile_agg(expr="cost + cost_total", refs=["cost", "cost_total"])
    assert compiled == "inputs.cost + inputs.cost_total"   # NOT inputs.inputs.cost_total
    # or, if disposition is tripwire-only: assert the diagnostic fires

def test_disjoint_ref_names_unchanged(caplog):             # silent-on-clean / no-regression
    compiled = _compile_agg(expr="a + b", refs=["a", "b"])
    assert compiled == "inputs.a + inputs.b"
    assert _warns(caplog) == []
```

### Changes Required
**See spec** Problem site 2 (corruption walkthrough), Open Questions (site-2 mitigation form),
"R4 Reproduce-First" site 2.
- [x] `src/sysml_codegen/resolution/graph_builder.py:~1547-1558` — applied the word-boundary
      mechanism: `re.sub(rf"\b{re.escape(ref)}\b", ref_to_inputs[ref], compiled)` in place of
      the plain `.replace()`. Does not change the compiled output for disjoint ref sets
      (byte-identical baselines).
- [x] `tests/unit/test_hygiene_tail_agg_compile.py` (NEW) — fires/corrupts-on-nested-name +
      unchanged-on-disjoint. Independent anchor: the hand-written expected compiled string.
- [x] Not reclassified (Phase 0 verdict: FIX, real reproduce, 0 corpus hits) — n/a.

### Validation
- [x] `uv run pytest tests/unit/test_hygiene_tail_agg_compile.py` → pass (2 passed)
- [x] `uv run pytest tests/conformance/test_baselines.py` → pass (16 passed; disjoint-ref
      aggregations — the whole covered corpus — compile byte-identically)
- [x] `uv run pytest tests/unit/test_graph_builder_aggregation.py` → pass (39 passed, no
      regression)
- [x] `ruff`/`mypy` on `src/sysml_codegen/resolution/graph_builder.py` → no new findings (first
      lambda-based attempt introduced a new mypy `Cannot infer type of lambda` finding; replaced
      with a plain `re.sub` string replacement — `ref_to_inputs` values are always
      `"inputs.{identifier}"`, never containing backslash-escape sequences, so no lambda is
      needed to guard against `re.sub` backreference interpretation)

**What We Know Works After This Phase:** a nested-attribute-name aggregation no longer silently
corrupts (or trips a loud tripwire); disjoint-name aggregations are byte-identical.

**Commit:** `git add src/sysml_codegen/resolution/graph_builder.py
tests/unit/test_hygiene_tail_agg_compile.py` → `feat(item6 site2): close aggregation-compile
substring collision (R4)`.

---

## Closing Gate (run when it will not collide with the parallel implement)

Per-phase validation above is targeted (do **not** run the full suite while the parallel implement
is running). The closing gate, run once at the end:

- [ ] **Suite green:** `uv run pytest tests/` (coordinate timing with the parallel run).
- [ ] **INV-6 final check:** the clean corpora still generate with **zero WARNINGs** — the
      silent-on-clean tests plus the corpus-level assertion (`report.warnings == []` idiom,
      `test_silent_failure_family1.py:133`). No new diagnostic fires on any clean fixture.
- [ ] **Baselines byte-identical:** `uv run pytest tests/conformance/test_baselines.py`. No
      covered model changed wiring or output. If a baseline moved, the shape was not benign —
      **file it, do not force it** (spec Non-Goals); it leaves this item's scope.
- [ ] **ruff ≤ 17, mypy ≤ 97:** `uv run ruff check src/` and `uv run mypy src/` — not worse than
      the current baseline counts.
- [ ] **R2 (agentic-mbse lockstep):** record the new-diagnostic surface for each site (likely
      "no change needed" — these are in-repo loader/resolution/generation diagnostics), per the
      epic R2 note.
- [ ] **Docs loop (R4 step 4):** update the reference doc + modeling-assumptions/matrix rows for
      each touched component in the same change — loader (`27-snapshot-generation.md`),
      output registry (`10-output-registry.md`), and any matrix rows for the four sites.

---

## Environment Setup

See CLAUDE.md. Offline reproduce/scan needs no license (`--from-snapshot` over `SNAPSHOT_MODELS`).
Live extraction (not needed here) requires the syside license and loads only via capture
scripts / full pytest, not a bare `-c` probe (memory: `syside-license-via-scripts-not-dashc`).

---

## Risk Management

- **Site 2 or 3 does not reproduce (fixing a non-bug).** Mitigation: Phase 0 reproduce-first with
  an explicit reclassify path recorded in BACKLOG/register (R4). Reclassification is a valid
  outcome, not a failure.
- **A new diagnostic false-fires on a clean corpus (breaks INV-6).** Mitigation: the corpus-scan
  gate in Phase 0 proves zero clean-fixture fires *before* the disposition is chosen — not
  discovered at INV-6-test time.
- **A harden moves a baseline (out-of-scope behavior change).** Mitigation: byte-identity check in
  every harden phase and the closing gate; a moved baseline means the shape is not benign → file
  it, do not force it (spec Non-Goals).
- **Item 2 lands more commits under the four sites during this work.** Mitigation: re-grep each
  pin at phase pickup (the HEAD line numbers are guides). The only semantic adjacency is Site 4 ↔
  Item 2's multi-hop resolution — re-check Site 4's reproduce fixture against Item 2's landed
  state (Phase 3).
- **Byte-identity gate churns on `captured_at` if a snapshot is re-captured.** This item expects
  **no** re-capture (byte-identical). If one becomes necessary, use the timestamp-only diff check
  + revert (memory: `byte-identity-captured-at-churn`).

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**Completed:** 2026-07-07. Probes in `probes/probe_site{1,2,3,4}_*.py`, full verdict in
`probes/verdict.md`.

**Per-site verdict (reproduce / scan / disposition):**
- **Site 1 (loader):** reproduces by construction; corpus scan 0 hits on all 5 candidate
  fields. Disposition: WARN for `python_type`, `binding_type`, `parent_part_path`,
  `owning_part_def_qn`; **RAISE** for `qualified_name` (both the calc_usage `:327` and
  design_attribute `:343` sites — a keying field that would mis-key the registry).
- **Site 2 (`.replace`):** reproduces on a real nested-name shape (`cost`/`cost_total` →
  `inputs.inputs.cost_total`), confirming the spec-review L2-1 correction. Corpus scan 0
  hits (no covered aggregation has nested names yet). Disposition: **FIX** the compile
  choke with a word-boundary substitution — not a diagnostic, a correctness fix that is
  byte-identical on the covered corpus.
- **Site 3 (`type_map` Any):** reproduces at the unit level; reachability scan finds 0
  non-primitive exit points in the corpus → latent-only today. Confirmed independent of
  Site 1 (live `extractor.py:492` source) per spec L1-1. Disposition: WARN, pinned with a
  constructed fixture (no real fixture exercises the shape yet).
- **Site 4 (Phase-4 no-`else`):** **RECLASSIFIED.** Corpus scan found the identical
  unresolved-lookup shape already firing on 5/15 real `SNAPSHOT_MODELS` fixtures today
  (short-form vs. full-EQN key mismatch on transitive design-attribute defaults). A
  mechanical sibling-copy WARN would break INV-6 on those 5 fixtures. This is the same
  gap already deferred, undocumented in BACKLOG, at `parameter_groups.py:672-682`
  (SC-5/D3-12 hazard-scoped-WARN note). Filed as
  `[D3-HYGIENE-TAIL-SITE4-TRANSITIVE-ALIAS]` — a correct fix needs a cross-derivation
  EP-omission check spanning two modules, which is design-level work, not a
  single-choke mechanical hygiene fix. No code change to `output_registry_builder.py`
  in this item; Phase 3 below records the reclassification only.

**Reclassifications recorded:** Site 4 → `BACKLOG.md` `[D3-HYGIENE-TAIL-SITE4-TRANSITIVE-ALIAS]`
(new entry, TRUTH-DEBT Item 6 Phase 0 filings section).

### Phase 1 Completion (Site 1)
**Completed:** 2026-07-07. Added `_require`/`_require_binding_type` chokes in
`snapshot/loader.py`; routed `python_type`/`binding_type` (WARN) in
`_deserialize_attribute_info`, `parent_part_path`/`owning_part_def_qn` (WARN) and
`qualified_name` (RAISE) in `_deserialize_calc_usage`, and `qualified_name` (RAISE) in
`_deserialize_design_attribute`. 9 new tests (5 fires-on-shape/raise, 3 silent-on-clean,
1 clean-design-attribute). No deviations from plan.
### Phase 2 Completion (Site 3)
**Completed:** 2026-07-07. Added an `else` branch to `_collect_exit_point_primitive_types`
warning on an unmapped `python_type` for a `field_name="root"` exit point. 2 new tests
(fires-on-shape with a constructed `"Any"` module — latent-tripwire pin per Phase 0's
reachability scan; silent-on-clean with `"float"`). No deviations.
### Phase 3 Completion (Site 4)
**Completed:** 2026-07-07. **Reclassified, no code change** — see Phase 0 verdict and
`BACKLOG.md` `[D3-HYGIENE-TAIL-SITE4-TRANSITIVE-ALIAS]`. No production or test file touched
in this phase; only the plan itself records the disposition.
### Phase 4 Completion (Site 2)
**Completed:** 2026-07-07. Replaced the `.replace()` loop in `_build_aggregation_module`'s
compile step with a word-boundary `re.sub`. 2 new tests (nested-name no-corrupt,
disjoint-name unchanged); full existing aggregation suite (39 tests) and baselines (16 tests)
still pass. One deviation: initial fix used a lambda-with-default-arg replacement to dodge
`re.sub`'s backslash-escape handling in the replacement string; mypy flagged
`Cannot infer type of lambda`, so switched to a plain string replacement (safe here since
substitution values are always sanitized `inputs.{identifier}` strings).

---

**Status:** Draft → In Progress → Complete
