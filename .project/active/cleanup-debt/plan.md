# Implementation Plan: Dead Code & Cleanup Debt (PIPELINE-TRUTH Item 8)

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06
**Branch:** pipeline-truth-epic

## Source Documents
- **Spec:** `.project/active/cleanup-debt/spec.md` ← the catalog A–H **is** the requirements; each row carries its own delete/verify/doc obligations. No design stage (deliverables are `{spec,plan}.md`).
- **Spec review:** `.project/active/cleanup-debt/spec-review.md` (Revise → all 7 must-fixes + 3 minors folded into spec)
- **Epic:** `.project/backlog/epic_pipeline_truth.md` (R1 docs-move-with-code, R3 baseline discipline, R4 verify-then-fix, SC-G suite-green gate)

There is no `design.md`. Where this plan would normally link `design.md#section`, it links the spec row instead (`spec.md` §A…§H).

---

## Implementation Strategy

**This is a deletion catalog, not a feature.** Nine of the ten catalog rows remove dead code, fix a lying docstring, or file a residue finding. Exactly one row (D) changes behavior in an executable path, and it is fenced by a byte-identity gate. So the phase order is: **prove the suite is green and the sequencing gate is clear (Phase 0) → land the unconditional deletions (Phase 1) → land the two verify-then-delete forks with their doc obligations (Phase 2) → fix the four lying docstrings and pin the two hedged doc edges (Phase 3) → disposition the D1 residue and record the SC-11 verdict (Phase 4) → make the one behavior change last, under the byte-identity gate (Phase 5) → close out with the SC-G gate and the auditable count story (Phase 6).**

**Phasing rationale:**
- **Deletions before behavior work.** Every deletion is independently reversible and cannot change a baseline; batching them first gets the surface-shrink done while the tree is quiet, and keeps the risky row (D) isolated at the end.
- **Row D is dead-last among code changes** because it needs a fresh live capture, and that capture is gated on Item 4 (see the [HARD] sequencing requirement). It is the only row that touches `transformed_expression → compiled_expression → auto_impl_context`.
- **Unconditional deletions (Phase 1) before fork deletions (Phase 2)** because the forks (`get_default_value`, `generate_derived_group_json`) carry doc-17 / matrix / BACKLOG obligations and a verify-then-delete decision; keeping them separate keeps each phase's boundary clean and its "suite green" attributable.
- **Doc/backlog obligations travel inside their phase, never batched at the end (R1).** Each phase's checklist includes the docstring, reference-doc, matrix-breadcrumb, and BACKLOG edits that its code change forces. Phase 6 is *consolidation and audit*, not the first time docs get touched.

**Critical path:**
Phase 0 sequencing gate (Item 4 Phase-5 re-capture committed) → Phases 1–4 in any internal order but each ending suite-green → Phase 5 (fixture author → capture at v2 → **reproduce** with failing probe → hoist branch → byte-identity gate) → Phase 6 close-out.

**First proof point:**
Phase 5's *failing* probe on the new literal-bearing aggregation fixture — it demonstrates the mis-dispatch **before** the fix (R4 step 2). That is the one place in this item where a test proves a defect is real rather than proving a deletion is safe.

**Sequencing note (implement queue):** This item's implement is **third** for the tree — Item 4 finishing → Item 6 implement → **this**. The plan is written to execute standalone in a later session. Phase 0's first checkbox re-establishes the world state (Item 4's v1→v2 re-capture landed) so no phase assumes in-session context.

**Overall validation approach:**
- Every deletion re-greps for zero callers **at implement time** ([HARD]) — the spec's greps are the spec-time first pass; line numbers and export sites drift (already observed: BACKLOG's aggregation entry moved off `:185`; the dual-write sites shifted).
- Suite is green at every phase boundary; ruff/mypy never worse than the **21/109** baseline (SC-G).
- Phase 5's baseline gate is **byte-identity against the v2 corpus** (post-Item-4), verified via `git status` after a scripted re-capture (R3 — no hand-edited baselines).

---

## Environment & Baselines

**See CLAUDE.md for commands.** Key ones for this item:

```bash
uv run pytest tests/                 # full suite — green at every phase boundary
uv run ruff check src/ | tail -1     # must stay ≤ 21
uv run mypy src/ 2>&1 | tail -1      # must stay ≤ 109
```

**Baseline to hold:** suite green, **ruff 21 / mypy 109**. Record the exact pre-work suite count in Phase 0 so the net test-count *decrease* (deleted self-tests) is auditable in Phase 6.

**Re-grep idiom for every deletion (do NOT trust the spec's line numbers):**
```bash
grep -rn "<symbol>" src/ tests/ scripts/ docs/   # expect only the def + doc/__all__/test sites the row names
```

---

## Phase 0: Preflight & Item-4 Sequencing Gate

### Goal
Re-establish world state for a standalone session and prove the tree is green before touching anything. This phase writes no production code.

### Assumption Under Test
That Item 4's v1→v2 snapshot re-capture has already landed on `pipeline-truth-epic`, so Phase 5's fixture captures at **v2** and its byte-identity gate is judged against the **v2** corpus (the [HARD] sequencing requirement: entirely-after, never interleaved).

### Changes Required
- [ ] **Confirm Item 4's Phase-5 re-capture is committed** — `git log --oneline` shows Item 4's snapshot-format-v2 re-capture landed; `snapshot_format_version` in a sample `extraction_snapshot.json` reads the v2 value. If it is **not** landed, STOP: this item's Phase 5 cannot run (Phases 1–4 are safe to run, but do not author/capture the Row-D fixture until Item 4 lands).
- [ ] Record the pre-work state in this plan's Implementation Notes: full suite count (`uv run pytest tests/ -q | tail -1`), ruff count, mypy count.
- [ ] **Flag shared files to the generation-boundary item owner** (BACKLOG: In Progress, Step 7.6) so a rebase does not resurrect deleted exports: `generation/type_mapping.py`, `generation/entry_point.py`, `generation/__init__.py`, and `src/sysml_codegen/templates/` (a **sibling** of `generation/`, not inside it — per spec-review L4-1). Record the flag in Implementation Notes.

### Validation
**Automated:**
- [ ] `uv run pytest tests/` → green; count recorded.
- [ ] ruff = 21, mypy = 109 recorded.

**What We Know Works After This Phase:**
The baseline is captured, the sequencing precondition is confirmed (or the item is correctly blocked on Item 4), and the coordination flag is out.

---

## Phase 1: Unconditional Deletions (§A, §B-map, §B-binding, §F dead helper, §H, §D1-F5)

### Goal
Remove every zero-caller symbol that carries **no** verify-then-delete fork and **no** live-requirement question — the safe surface-shrink. Suite green at the boundary; net test count starts dropping here.

### Assumption Under Test
That the spec's zero-caller enumerations still hold at HEAD (re-grep confirms), so each deletion is inert.

### Test Stencil (write/observe this first — the "test" here is the re-grep gate)
```bash
# Before each cut: prove zero production callers remain.
grep -rn "map_sysml_type_to_rootmodel_wrapper" src/ tests/ scripts/ docs/
#   expect: def @ type_mapping.py:~60, docstring bullet :~9, __all__ :~81,
#           test_type_mapping_consolidation.py dedicated cases (incl. hasattr :242)
grep -rn "_check_semantic_match" src/ tests/          # expect: def only, zero callers
grep -rn "\.binding_to_entry_point\b" src/ tests/     # expect: field def + writes + test_data_models.py:~361 only
```

### Changes Required
**See `spec.md` §A, §B (rows map/binding), §F (dead helpers, D1-F5), §H.**

#### §A — Dead templates (DELETE)
- [ ] `src/sysml_codegen/templates/pydantic_schema.py.jinja2` — re-confirm 0 `get_template(...)` render sites, delete.
- [ ] `src/sysml_codegen/templates/entry_point_schema.py.jinja2` — re-confirm 0 render sites (only `parameter_group_schema.py.jinja2` is rendered by `generation/entry_point.py`), delete.

#### §B — `map_sysml_type_to_rootmodel_wrapper` (DELETE — no fork; `modules.py` imports the sibling `map_sysml_type_to_python`)
- [ ] Delete the function (`generation/type_mapping.py:~60`).
- [ ] Delete the module-docstring bullet (`type_mapping.py:~9` — `- map_sysml_type_to_rootmodel_wrapper(): ...`) **[R1 — spec-review L1-1]**.
- [ ] Delete the `__all__` entry (`:~81`).
- [ ] Delete the dedicated test cases in `test_type_mapping_consolidation.py` (incl. the `hasattr` assertion `:242`); **keep the sibling-function tests** (`map_sysml_type_to_python`). Record deleted test names for Phase 6.

#### §B — `binding_to_entry_point` dual-write (DEPRECATED — DELETE; no consumer reads it)
- [ ] Delete the `BacktrackingResult` field (`dependency_backtracker.py:~81`) and its DEPRECATED docstring line (`:~62`).
- [ ] Delete the `_binding_to_entry_point` backing dict + every init/reset/write/construct site (re-grep — HEAD shows `:177,218,304,373,405,421,440`; line numbers drift).
- [ ] Delete the `:~179` naming comment `# Unified binding resolutions (replaces _binding_to_entry_point)` — it names the deleted dict **[R1 — spec-review L1-1]**.
- [ ] Delete the `test_data_models.py:~361` field-name assertion. Record for Phase 6.

#### §F — dead helper (DELETE)
- [ ] `_check_semantic_match` (`analysis/phantom_detector.py:~263`) — re-grep def-only, delete. (Note: `_deserialize_constraint_info` in `snapshot/loader.py` is **OUT OF SCOPE** — Item 4 deletes it. Do not touch.)

#### §F — D1-F5 (verify + bookkeeping, likely no code)
- [ ] Re-grep `subprocess` across `src/` and `scripts/` (spec-time spot-grep found **zero** — the dead `out = subprocess.run` var appears already removed). If present, delete it. Either way, **flip the unflipped plan checkboxes the finding names** in `snapshot-generation/audit.md:120-123`. Record disposition (done / already-gone) for Phase 6.

#### §H — 4 vacuous skipif guards (SIMPLIFY)
- [ ] `tests/conformance/test_output_registry.py` — remove the 4 `skipif` guards (`:114, :119, :141, :146`; the typed API exists at HEAD, so they never fire). Tests run unconditionally.

### Validation
**Automated:**
- [ ] Re-grep each deleted symbol across `src/ tests/ scripts/ docs/` → **zero hits** (SC-G).
- [ ] `uv run pytest tests/` → green; count **decreased** vs Phase 0 by exactly the deleted self-tests.
- [ ] ruff ≤ 21, mypy ≤ 109.

**What We Know Works After This Phase:**
The un-forked dead surface is gone, the four skipifs run unconditionally, and D1-F5 is dispositioned — all with zero grep residue and a green suite.

---

## Phase 2: Verify-then-Delete Forks (§B — `get_default_value`, `generate_derived_group_json`)

### Goal
Resolve the two rows that carry a **live-requirement question**, then land the delete-fork with its full R1 doc obligations in the same change.

### Assumption Under Test
That each method only wraps existing logic for its own test (dead), not that it is the sole implementation of a live requirement. The implement-time grep + the recorded fork resolves this — no human decision (spec §Open Questions).

### Test Stencil (write/observe this first)
```bash
# get_default_value — confirm the lookup it performs is duplicated by live production code
grep -rn "get_default_value" src/ tests/ docs/        # expect: def + test_parameter_group_deriver.py + doc-17 rows
# Inspect the body: does it only wrap _attr_index for the test? If a live path does the
# same lookup inline → DEAD → delete fork. If it is the sole impl of a live req → KEEP.
grep -rn "generate_derived_group_json" src/ tests/    # expect: def + __all__ :326 + __init__ re-export :20,67
# Live path is generate_all_derived_jsons (omits null-default keys); the twin emits them → dead.
```

### Changes Required
**See `spec.md` §B (get_default_value / generate_derived_group_json rows), §Coordination.**

#### `get_default_value` (`analysis/parameter_groups.py:~533`) — verify-then-delete with recorded fork
- [ ] Confirm the fork (dead vs live). **Record which fork was taken in the close-out** (spec §B).
- [ ] **If DEAD → delete** the method + its dedicated tests in `test_parameter_group_deriver.py`. In the **same change** (R1/R4 step 4):
  - [ ] Update **doc-17** (`reference/17-parameter-group-deriver.md`): retire/rewrite the REQ table row `:26` (REQ-PGD-06), the REQ-PGD-08 prose `:28`, and the method prose `:143` — no doc-line may name the deleted symbol.
  - [ ] Leave a **visible breadcrumb** on `verification-matrix.md:379`: `PASS → PENDING-ITEM7` pointing at the `[ITEM7-PGD06]` BACKLOG entry, so the transient "PASS pins a deleted test" gap is not silent.
  - [ ] **Activate** the existing `[ITEM7-PGD06]` BACKLOG entry (`BACKLOG.md:170`, conditional — "only fires if Item 8 deleted `get_default_value`"): flip its condition to fired, so Item 7's required reading picks up the matrix PASS-row re-frame. Only the matrix PASS-row re-frame is handed to Item 7 — the doc-17 updates land **here**.
  - [ ] Record the deleted test names for Phase 6.
- [ ] **If LIVE → keep** the method and file the observation; `[ITEM7-PGD06]` becomes a no-op Item 7 retires. Record the fork.

#### `generate_derived_group_json` (`generation/entry_point.py:~188`) — DELETE (dead twin emits null-default keys; live path is `generate_all_derived_jsons`)
- [ ] Re-grep: def + `__all__` (`:~326`) + `generation/__init__.py` re-export (`:~20,67`); **verify no external (fusion-tea) import** at implement.
- [ ] Delete the function + both export sites (`__all__` + the `__init__` re-export).
- [ ] Update any docstring/reference doc rendered stale by the delete in the same change (R1).

### Validation
**Automated:**
- [ ] Re-grep both symbols across `src/ tests/ docs/` → zero code hits; doc-17 and matrix:379 no longer name a deleted symbol as live.
- [ ] `uv run pytest tests/` → green; count decreased.
- [ ] ruff ≤ 21, mypy ≤ 109.

**Manual:**
- [ ] Read doc-17 rows `:26/:28/:143` → describe reality (or are retired), not the deleted method.
- [ ] `matrix:379` carries the `PENDING-ITEM7` breadcrumb; `[ITEM7-PGD06]` is activated.

**What We Know Works After This Phase:**
Both forks are resolved on evidence with the decision recorded, the delete-fork's reference doc is truthful in the same change, and the one matrix re-frame that legitimately waits for Item 7 has a durable, breadcrumbed home.

---

## Phase 3: Docstring Truth (§C) + Dotted-Leaf Alias Pin (§E)

### Goal
Fix the four docstrings that lie about their code, and add the cheap unit pin that retires doc-25's "no current model triggers this" hedge. No behavior change.

### Assumption Under Test
That each stale docstring's *body* is correct and only the prose is wrong (verify against body — spec §C), and that the dotted-leaf alias edge behaves as doc-25 describes when exercised directly.

### Test Stencil (write this first — §E)
```python
# tests/unit/test_hierarchy_resolver.py (or nearest home)
def test_dotted_leaf_alias_matches_by_leaf_regardless_of_part():
    # A dotted CHAIN redef whose leaf equals an aggregation attr but references a DIFFERENT part.
    # Pins the current `.`-suffix CHAIN-alias behavior that doc-25:243-248 hedges.
    result = _resolve(...)                 # exercise the dotted-leaf branch directly
    assert result == <current observed behavior>   # assert current behavior, not a fix
```

### Changes Required
**See `spec.md` §C (four rows) and §E.**

#### §C — four docstring fixes (verify each against the body first)
- [ ] `_resolve_binding_via_registry` (`analysis/dependency_backtracker.py`): drop the non-existent "Step 1b: Normalize :: to dotted → scoped_lookup" reference; add the omitted Step 1c to the CHAIN summary — match `_resolve_reference_dispatch` actual steps.
- [ ] `OutputRegistry` class docstring (`core/output_registry.py`): "Three typed registries" → **four**; add the omitted Phase 3b to the phase list; add the `_scoped_alias` count to the `__repr__` description.
- [ ] `build_pipeline_context` (`orchestration/pipeline_builder.py`): fix the stale 7-step summary — the group deriver runs at **Step 5.7, after** the registry, not ahead of it.
- [ ] `tests/conformance/test_graph_assembly.py`: section header / class docstring "exactly 3 fields" → **5** (the body already pins 5).

#### §E — dotted-leaf alias unit pin + doc-25 rewrite
- [ ] Add the unit pin above, exercising the `.`-suffix CHAIN-alias branch directly and asserting current behavior.
- [ ] Rewrite the doc-25 hedge (`25-hierarchy-resolver.md:243-248`) to point at the new pin instead of "No current model triggers this". **Coordinate the doc-25 retirement with Item 10** (epic-close caveat sweep) — note it so Item 10 sees it.

### Validation
**Automated:**
- [ ] `uv run pytest tests/` → green (new pin passes; +1 test).
- [ ] ruff ≤ 21, mypy ≤ 109.

**Manual:**
- [ ] Read each of the four docstrings against its body → they now agree.
- [ ] doc-25:243-248 points at the pin, not the hedge.

**What We Know Works After This Phase:**
No touched docstring lies about its code, and the dotted-leaf edge is pinned by a test rather than a hope.

---

## Phase 4: D1 Residue Dispositions (§F — D1-F2, D1-F3, D1-F4) + SC-11 Verdict (§G)

### Goal
End every remaining D1 finding **dispositioned** — deleted, fixed, filed with a real BACKLOG entry, or handed off — with the disposition recorded here, not "filed only in a plan file" ([NEED]). Record the SC-11 assessment verdict as an artifact either way.

### Assumption Under Test
That the two-sanitizer divergence (D1-F2) is load-bearing (default disposition = FILE), that the catf fallback EP (D1-F3) is a benign valued fall-through (not a bug), and that the SC-11 import rewrite is *not* small (default = FILE) — each confirmed or overturned by implement-time assessment.

### Changes Required
**See `spec.md` §F (D1-F2/F3/F4), §G, §Non-Goals.**

#### §F — D1-F2 two-sanitizer consolidation (assess → default FILE)
- [ ] Assess `core.sanitize_name` (`core/qualified_names.py:13`) vs `expression_compiler._sanitize_name` (`extraction/expression_compiler.py:167`). The divergence is **load-bearing** — the compiler deliberately drops the reserved-word suffix, and the FORMULA wire matches *by construction* on that difference.
- [ ] **Default: file as P3 BACKLOG.** Implement a shared core **only** if it falls out safely with the byte-identity gate green (a naive merge risks the FORMULA REFERENCE match). **Record the decision** in close-out.

#### §F — D1-F3 catf fallback-EP chore (assess → file-or-no-op)
- [ ] Assess whether catf's `pumping_speed_total` fallback EP (a `USAGE_LITERAL 200.0` — valued, so the collector correctly skips it; a benign pre-existing gap, **not a bug**) is still present (per `cross-part-wiring/plan.md:819-823`). Disposition = file-or-no-op. **Do not "fix" a non-bug.** Record.

#### §F — D1-F4 `param_groups` type-ignore cluster (fix)
- [ ] Annotate or rename `param_groups` at its root so the four-line `# type: ignore` cluster in `resolution/graph_builder.py:408-412` (`[assignment]` + `[attr-defined]`) deletes cleanly. **mypy count must not rise** (target: 109 or lower).

#### §G — SC-11 AST-based import rewrite (D1-F1) — assess-then-decide, verdict recorded
- [ ] **Assess** the rewrite (`identifier-sanitization/close-out.md:31`, substring/first-match) against the registry alias-rewrite no-not-found branch (D3 hygiene site). **Record what the comparison showed and the size judgment** ("small" ≈ a 1–2-site local change vs. a cross-module rework).
- [ ] **If small → implement** (the commit is the artifact).
- [ ] **If not → file** a P3 BACKLOG entry carrying the size argument, **and correct the false "filed follow-up" claim** in `close-out.md:31`.
- [ ] Either branch: the verdict is written down (spec §G). This is the **SC-11 assessment verdict artifact** the close-out names.

### Validation
**Automated:**
- [ ] `uv run pytest tests/` → green.
- [ ] mypy ≤ 109 (D1-F4 must not raise the count); ruff ≤ 21.

**Manual:**
- [ ] Each of D1-F1…F5 has a written disposition (this phase covers F1/F2/F3/F4; F5 was Phase 1). Cross-check for Phase 6's residue table.

**What We Know Works After This Phase:**
No D1 finding is left "filed only in a plan file"; the type-ignore cluster is gone without raising mypy; the SC-11 verdict exists as an artifact.

---

## Phase 5: Aggregation-Literal Dispatch Fix (§D — R4 in full, LAST code change)

### Goal
Fix the one real bug: `_walk_aggregation_ast` dispatches the invocation catch-all before the literal branch, so a literal operand in an aggregation expression is mis-classified as unsupported and its `reconstruct_expression` delegation is dead code (`extraction/hierarchy_resolver.py`, catch-all `~:392`, literal branch `~:452`). Fix code to doc (doc-19 records the canonical ordering as literal-before-invocation).

### Assumption Under Test
That the reorder is inert on the committed corpus — **no committed fixture has a literal-bearing aggregation**, so hoisting the literal branch changes nothing for existing baselines (the byte-identity gate) — and that a *new* literal-bearing fixture demonstrably mis-dispatches before the fix and dispatches correctly after.

**[HARD] Sequencing:** this phase runs **entirely after** Item 4's v1→v2 re-capture (confirmed in Phase 0). The new fixture captures at **v2**; the byte-identity gate is judged against the **v2** corpus. Never interleaved with Item 4's bump.

### Test Stencil (write this first — R4 step 2, the FAILING probe)
```python
# tests/conformance/test_agg_literal_dispatch.py  (new)
# Fixture: agg_literal_probe — an aggregation :>> whose RHS mixes a sum(...)/FCE term
# with a numeric literal, e.g.  :>> total = sum(module.cost) + 5.0
def test_literal_operand_mis_dispatched_BEFORE_fix():
    ctx = _walk_and_collect(agg_literal_probe_redef)
    # BEFORE the fix this FAILS the intended contract: the literal hits the invocation
    # catch-all, has_unsupported flips True, and the render is garbage.
    assert ctx.has_unsupported is False          # <-- red before the hoist
    assert "5.0" in transformed_expression        # literal survives, not swallowed
```

### Changes Required
**See `spec.md` §D and the [HARD] R4 + sequencing requirements.**

#### R4 step 1 — intent check (DONE at spec time)
- [ ] Confirm doc-19 (`19-ast-dispatch-invariant.md:64-70`) still records the known deviation from REQ-AST-03 (literal/null branches dispatch **before** the invocation catch-all). Legal outcome = fix code to doc.

#### R4 step 2 — author fixture + reproduce
- [ ] Author the `agg_literal_probe` fixture (`tests/fixtures/agg_literal_probe/` with `library.sysml` + `design.sysml`) — an aggregation `:>>` whose RHS mixes a `sum(...)`/FCE term with a numeric literal.
- [ ] **Register it** in `scripts/capture_extraction_snapshots.py` (`MODELS` dict) so the snapshot is script-reproducible (never hand-authored — R3).
- [ ] **Capture at v2** via `scripts/capture_extraction_snapshots.py --fixtures agg_literal_probe` (+ the pipeline baseline if it builds a graph). License-bearing path — run through the real capture script (per the syside-license memory, the license loads for capture scripts, not a bare `-c` probe).
- [ ] Write the failing probe above; **run it and see it fail** (R4 step 2 — the mis-dispatch is demonstrated before any fix).

#### R4 step 3 — fix (root fix, house style)
- [ ] Hoist the `is_literal_expression` branch (`~:452-454`) **above** the invocation catch-all (`~:392`) in `_walk_aggregation_ast`, matching REQ-AST-03/-08 canonical ordering (mirror the Item-6 `reconstruct_expression` fix). The literal branch is no longer dead.
- [ ] Re-run the probe → now green (corrected dispatch: `has_unsupported` stays False, literal survives).

#### R4 gate — byte-identity
- [ ] Re-capture / re-run baselines and confirm **all existing corpora are byte-identical** against the **v2** set (`git status` shows only the new `agg_literal_probe` files changed). No hand-edited baselines (R3).

#### R1 — REQ home + matrix row (rows move with code)
- [ ] Add **REQ-AST-10** to doc-19's requirements table: "`_walk_aggregation_ast` SHALL dispatch all literal/null branches before the invocation catch-all," **verified-by** the new `agg_literal_probe` fixture.
- [ ] **Add its matrix row in this item** (`verification-matrix.md` — matrix *additions* are allowed in-item per R1; only Item-7's *PASS-row reconciliation* waits). Note the addition in Item 7's ledger via BACKLOG so the sweep sees it.

#### R4 step 4 — docs + BACKLOG closure
- [ ] Retire the doc-19 "Known deviation — `_walk_aggregation_ast`" note (`:64-70`). **Coordinate the doc-19 retirement with Item 10** (epic-close caveat sweep) — note it so Item 10 sees it.
- [ ] **Close the BACKLOG entry that tracks this bug** — currently in "Ideas / Future Considerations", tagged "*→ Absorbed into PIPELINE-TRUTH Item 8*" (spec cited `:185`; it has drifted — re-grep `Absorbed into PIPELINE-TRUTH Item 8`). Move it to Completed / strike it on landing. This is the **BACKLOG:185 closure** the close-out names.

### Validation
**Automated:**
- [ ] Probe **red before** the hoist, **green after** (R4 step 2 → step 3, demonstrated in-order).
- [ ] `git status` after re-capture → only `agg_literal_probe` files new; **every other baseline byte-identical** (v2).
- [ ] `uv run pytest tests/` → green; ruff ≤ 21, mypy ≤ 109.

**Manual:**
- [ ] doc-19 no longer lists the deviation; REQ-AST-10 is in its table; matrix carries the new row verified-by the fixture.
- [ ] The aggregation-literal BACKLOG entry is in Completed / struck.

**What We Know Works After This Phase:**
A literal operand inside an aggregation expression now dispatches to the literal branch (proven by a fixture that failed before the fix), every pre-existing corpus is byte-identical, and the fixed dispatch has a REQ home + matrix row + retired deviation note.

---

## Phase 6: Close-Out (SC-G gate, count story, disposition ledger)

### Goal
Consolidate the auditable close-out the spec's success criteria demand. No new code — this phase proves the item met its own bar.

### Changes Required (all recorded in this plan's Implementation Notes / close-out)
- [ ] **SC-G gate:** final full suite green; **zero grep hits** for every deleted symbol across `src/` and `tests/`; ruff/mypy **not worse than 21/109**. Record the final counts.
- [ ] **The count story (auditable, not assumed):** the net test count **decreased**; list **each deleted test and the dead symbol it solely pinned**, and confirm **no non-self-test lost coverage**. Named-deleted-tests list assembled from Phases 1–2 (map-function dedicated cases incl. `hasattr` :242; `get_default_value` tests if the delete-fork was taken; `test_data_models.py:361` field-name assertion) — this is the **named-deleted-tests list** the close-out requires.
- [ ] **§B fork record:** state which fork `get_default_value` took (dead→deleted, or live→kept), and confirm `generate_derived_group_json` deleted with both export sites.
- [ ] **D1 residue ledger:** every D1-F1…D1-F5 with its final disposition (F1/§G verdict; F2 filed-or-merged; F3 file-or-no-op; F4 fixed; F5 done/already-gone) — nothing "filed only in a plan file" ([NEED]).
- [ ] **SC-11 assessment verdict artifact** (§G): implemented-commit or filed-BACKLOG-entry + corrected `close-out.md:31` — named and linked.
- [ ] **BACKLOG:185 closure** confirmed (§D aggregation entry → Completed / struck) and **doc-19 / doc-25 caveats** noted as handed to Item 10.
- [ ] **`[ITEM7-PGD06]` state** recorded (activated if `get_default_value` deleted; no-op if kept) and the new **REQ-AST-10 matrix row** noted in Item 7's ledger via BACKLOG.
- [ ] Update `.project/CURRENT_WORK.md` Item 8 entry to IMPLEMENTED with the close-out summary; suggest `/_my_audit`.

### Validation
**Automated:**
- [ ] `uv run pytest tests/` → green; final counts recorded.
- [ ] `grep -rn "<each deleted symbol>" src/ tests/` → zero.

**What We Know Works After This Phase:**
Every success criterion has a written, auditable answer; no disposition stops one step short of "nothing left filed in a plan file."

---

## Risk Management

**Phase-specific mitigations:**
- **Phase 1/2 (drift):** the spec's line numbers are stale by design (already observed: dual-write sites shifted, BACKLOG aggregation entry moved off `:185`). Mitigation: **re-grep every symbol at implement** ([HARD]); never cut on a spec line number.
- **Phase 2 (fork misjudged):** deleting a method that is the sole impl of a live requirement. Mitigation: the verify-then-delete gate (grep + body inspection) and the recorded fork; if live, keep and file — the delete is not forced.
- **Phase 4 D1-F2 (FORMULA wire break):** a naive sanitizer merge breaks the by-construction FORMULA REFERENCE match. Mitigation: default disposition is **FILE**; implement only if a safe shared core falls out with the byte-identity gate green.
- **Phase 5 (baseline drift / wrong version):** capturing against v1 when the gate expects v2, or hand-editing a baseline. Mitigation: Phase 0 confirms Item 4's v2 re-capture landed; all capture goes through `scripts/capture_*.py` with `git status` byte-identity review (R3).
- **Phase 5 (false-green probe):** a probe that passes both before and after proves nothing. Mitigation: the probe must be **red before the hoist** (run and observe), green after — R4 step 2 is a demonstrated ordering, not a claim.

---

## Constraints (from spec §Known Requirements — carried, not restated)
- **[HARD]** Every deletion lands with re-verified zero-callers grep evidence at implement time.
- **[HARD]** Aggregation-literal fix keeps all existing corpora byte-identical; all regeneration via `scripts/capture_*.py` with reviewed diffs (R3). No hand-edited baselines.
- **[HARD]** R4 verify-then-fix on Row D: intent checked (done), reproduced with a failing probe *before* the fix.
- **[HARD]** Sequencing vs Item 4: Row D fixture capture + gate run entirely **after** Item 4's v1→v2 re-capture (v2 baselines). Confirmed in Phase 0.
- **[HARD]** No ComputationGraph rev — every change is a deletion, docstring, test, unit pin, or the dispatch-order fix. Anything needing a graph rev is out of scope (file it).
- **[HARD]** Test-deletion rule: delete a test **only** when its sole purpose was pinning a now-deleted dead symbol; expect a net test-count decrease; close-out names each.
- **[NEED]** Every D1 finding ends dispositioned, recorded in the close-out.
- **[INFERRED]** A deletion that orphans a conformance test updates/removes it **and** updates the reference doc it renders stale in the **same change** (R1/R4 step 4). Only the matrix PASS-row re-frame (REQ-PGD-06) is handed to Item 7, via the durable `[ITEM7-PGD06]` BACKLOG entry with a visible matrix breadcrumb.

## Out of Scope (spec §Non-Goals — do not touch)
- `resolve_input` excision/cutover (Item 7).
- `_deserialize_constraint_info` (`snapshot/loader.py`) and `extract_all_constraints` deletion (Item 4).
- Constraint serialization on the from-snapshot path (Item 4).
- Any ComputationGraph rev or new feature work surfaced by a deletion (file it).
- Forcing the two-sanitizer consolidation when the divergence is load-bearing (file it — D1-F2).

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — leave empty now]

### Phase 0 Completion
**Baseline:** suite count = __ ; ruff = __ ; mypy = __ . Item 4 v2 re-capture committed? __ . Coordination flag sent? __

### Phase 1 Completion
### Phase 2 Completion  (fork taken: __ )
### Phase 3 Completion
### Phase 4 Completion  (D1-F2 decision: __ ; SC-11 verdict: __ )
### Phase 5 Completion  (probe red-before/green-after: __ ; byte-identity: __ )
### Phase 6 Completion  (named-deleted-tests: __ ; net count Δ: __ )

---

**Status:** Draft → In Progress → Complete
</content>
</invoke>
