# Spec: Dead Code & Cleanup Debt (PIPELINE-TRUTH Item 8)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** MEDIUM
**Branch:** pipeline-truth-epic

---

## Problem

The prior epic and the docs-scrub pass left a pile of small, verified cleanup debt
that never got cleared, plus discovery (D1/D2) turned up residue that was "filed" only
inside plan/audit files and never reached BACKLOG. It is all low-risk on its own, but
it is scattered and un-tracked, so it rots: dead templates and dead functions still
carry weight, DEPRECATED dual-write machinery still runs, four docstrings lie about the
code they document, and one real bug hides in an executable path behind a "no fixture
triggers it" note.

Two things make this worth doing as one reviewed pass now:

- **One item is a real bug, not hygiene.** `_walk_aggregation_ast` dispatches the
  invocation catch-all before the literal branch, so a literal operand inside an
  aggregation expression is mis-classified as unsupported and its literal branch is
  dead code (`hierarchy_resolver.py:433-454`). It is inert only because no fixture has
  a literal-bearing aggregation. It touches the executable aggregation path
  (`transformed_expression` → `compiled_expression` → `auto_impl_context`), so it needs
  a byte-identity gate, which is why it was filed for its own item (doc-19 records it as
  a known deviation from REQ-AST-03).

- **Sequencing.** This item modifies the same `extraction/` and `resolution/` surfaces
  PUSH-DOWN would move, so the epic scheduled PUSH-DOWN to start only after Item 5 and
  Item 8 land. Clearing the debt here unblocks that.

The goal is one reviewed pass that either clears each item or files it properly — with
re-verified zero-callers evidence for every deletion — so nothing is left silently
half-done.

## Success Criteria

- [ ] **Zero grep hits** for every deleted symbol across `src/` and `tests/`; the full
  suite is green; ruff/mypy counts are not worse than the 21/109 baseline (SC-G).
- [ ] **Aggregation-literal fix reproduced then fixed** (R4): a failing probe on a new
  literal-bearing aggregation fixture demonstrates the mis-dispatch *before* the fix;
  after the fix that fixture shows the corrected dispatch; **all existing corpora stay
  byte-identical** (the fix is inert on today's fixtures).
- [ ] **doc-19 known-deviation note retired** and the dotted-leaf alias edge pinned by
  a unit test, retiring doc-25's "no current model triggers this" hedge.
- [ ] **Every D1 finding (F1–F5) ends dispositioned** — deleted, fixed, filed with a
  real BACKLOG entry, or handed off to its owning item — with the disposition recorded
  here. Nothing left "filed" only in a plan file.
- [ ] **The 4 vacuous skipif guards removed**; their tests run unconditionally.
- [ ] Every touched component's docstring/reference doc updated in the same change (R1).

## Scope: the cleanup catalog

Each row carries its spec-time grep evidence and its disposition. Line numbers drift
(the register warned of this); every deletion **re-greps at implement time** before
cutting — the greps below are the spec-time verification, not the implement-time one.

### A. Dead templates (DOCS-SCRUB-F1a) — DELETE

Only 9 `get_template(...)` sites exist across `generation/`; neither template is among
them (grep: `get_template` in `generation/` → schemas/stencils/registry/entry_point/
test_gen/modules/pipeline only).

- `templates/pydantic_schema.py.jinja2` — 0 render sites. DELETE.
- `templates/entry_point_schema.py.jinja2` — 0 render sites (only
  `parameter_group_schema.py.jinja2` is rendered by `generation/entry_point.py`). DELETE.

### B. Verify-then-delete dead functions (DOCS-SCRUB-F1b)

- **`map_sysml_type_to_rootmodel_wrapper`** (`generation/type_mapping.py:60`) — callers:
  its own def, the `__all__` entry (`:81`), and one conformance test
  (`test_type_mapping_consolidation.py`, incl. a `hasattr` assertion at `:242`). **No
  production caller** — `modules.py` imports the sibling `map_sysml_type_to_python`, not
  this. DELETE the function, the `__all__` entry, and the test assertions that pin it
  (drop the dedicated test cases; keep the sibling-function tests).

- **`get_default_value`** (`analysis/parameter_groups.py:533`) — callers: its own def
  and `test_parameter_group_deriver.py` only; pins REQ-PGD-06. **Verify-then-delete with
  a recorded fork:** at implement, confirm the lookup it performs is duplicated by live
  production code (i.e. the method only wraps `_attr_index` for the test). If yes →
  DELETE method + its tests, and **hand the REQ-PGD-06 re-frame to Item 7** (matrix
  owner; runs after this item). If the method is the sole implementation of a live
  requirement → keep it and file the observation instead. Record which fork was taken.

- **`generate_derived_group_json`** (`generation/entry_point.py:188`) — callers: its own
  def, `__all__` (`:326`), and the `generation/__init__.py` re-export (`:20,67`). **No
  functional caller.** The live path is `generate_all_derived_jsons` (omits null-default
  keys — the shape Item 7-of-the-prior-epic corrected); this dead twin still emits
  null-default keys. DELETE the function + both export sites. Verify no external
  (fusion-tea) import at implement.

- **`binding_to_entry_point`** dual-write (DEPRECATED) — the `BacktrackingResult` field
  (`dependency_backtracker.py:81`) and its `_binding_to_entry_point` backing dict, kept
  in lockstep at ~7 init/reset/write/construct sites (register cited 62/80/176/304/372/
  404/439; spot-grep at HEAD shows the machinery at 62/81/177/218/304/373/405/421/440 —
  **re-grep at implement**). **No consumer reads `.binding_to_entry_point`** (grep: only
  the field def, the writes, and `test_data_models.py:361` which asserts the field name
  exists). DELETE the field, the backing dict, all dual-write/init/reset/construct sites,
  and the `test_data_models.py` field-name assertion.

### C. Stale docstrings (DOCS-SCRUB-F3) — one-line fixes, verify against body

- `_resolve_binding_via_registry` (`analysis/dependency_backtracker.py`): lists a
  REFERENCE "Step 1b: Normalize :: to dotted → scoped_lookup" that doesn't exist in
  `_resolve_reference_dispatch`; CHAIN summary omits Step 1c.
- `OutputRegistry` class docstring (`core/output_registry.py`): says "Three typed
  registries" (there are four); phase list omits Phase 3b; `__repr__` omits the
  `_scoped_alias` count.
- `build_pipeline_context` (`orchestration/pipeline_builder.py`): stale 7-step summary
  with the group deriver ahead of the registry (it runs at Step 5.7, after).
- `tests/conformance/test_graph_assembly.py`: section header / class docstring still say
  "exactly 3 fields" (body pins 5).

### D. Aggregation-literal dispatch bug (executable path — R4 applies)

- **Intent check (R4 step 1) — done.** doc-19 (`19-ast-dispatch-invariant.md:64-70`)
  records this as a known deviation from REQ-AST-03: the intended canonical ordering
  puts literal/null branches *before* the invocation catch-all. So the legal outcome is
  **fix code to doc**, not the reverse.
- **Site.** `_walk_aggregation_ast` (`extraction/hierarchy_resolver.py`): the invocation
  catch-all `if hasattr(node, "function") and hasattr(node.function, "name")` (~`:392`)
  precedes the `is_literal_expression` branch (~`:452`). Every SysIDE node carries a
  derived KerML `.function`, so a literal operand hits the catch-all, gets
  `has_unsupported=True`, and the literal branch (its `reconstruct_expression`
  delegation) is dead — the exact twin Item 6 fixed in `reconstruct_expression`.
- **Reproduce (R4 step 2).** Author a **literal-bearing aggregation fixture row** (an
  aggregation `:>>` whose RHS mixes a `sum(...)`/FCE term with a numeric literal, e.g.
  `sum(module.cost) + 5.0`). A failing probe shows the literal mis-dispatched
  (`has_unsupported` set / garbage render) before any fix.
- **Fix (R4 step 3).** Hoist the `is_literal_expression` branch above the invocation
  catch-all, matching REQ-AST-03/-08 canonical ordering (mirror the Item-6 fix). Root
  fix, house style — the dispatch-ordering family.
- **Gate.** Existing corpora **byte-identical** (no committed fixture has a
  literal-bearing aggregation, so the reorder changes nothing for them); the new fixture
  shows corrected dispatch.
- **Docs (R4 step 4).** Retire the doc-19 "Known deviation — `_walk_aggregation_ast`"
  note and reconcile REQ-AST-03/-05 verified-by; **coordinate the doc-19 retirement with
  Item 10** (which sweeps retired caveats at epic close).

### E. Dotted-leaf alias unit pin (retires doc-25 hedge)

doc-25 (`25-hierarchy-resolver.md:243-248`) hedges "No current model triggers this" for
the `.`-suffix CHAIN-alias branch, which matches any dotted `source_path` whose leaf
equals the aggregation `attribute_name` regardless of which part it references. Add a
cheap unit pin that exercises the edge directly (a dotted CHAIN redef whose leaf matches
an aggregation attr but references a different part) and asserts the current behavior,
then rewrite the hedge to point at the pin. This is a pin + doc edit, not a behavior
change.

### F. D1 unfiled residue (F1–F5 + two dead helpers)

- **F-2 — two-sanitizer consolidation.** `core.sanitize_name`
  (`core/qualified_names.py:13`) vs `expression_compiler._sanitize_name`
  (`extraction/expression_compiler.py:167`). The divergence is **load-bearing**: the
  compiler deliberately drops the reserved-word suffix that `core.sanitize_name`
  applies, and the identifier-sanitization item built the FORMULA wire to match *by
  construction* on that difference. RECOMMENDATION: **assess, then FILE as P3 BACKLOG**
  rather than force-consolidate in a cleanup pass — a naive merge risks the FORMULA
  REFERENCE match. Implement only if a safe shared core falls out with the byte-identity
  gate green. Record the decision.
- **F-3 — catf fallback-EP chore** (`pumping_speed_total`). Per
  `cross-part-wiring/plan.md:819-823`: catf's remaining fallback EP is a
  `USAGE_LITERAL 200.0` — fell-through but **valued**, so the collector correctly skips
  it; it is a benign pre-existing catf gap, **not a bug**. Assess whether it is still
  present; disposition = file-or-no-op (do not "fix" a non-bug). Record.
- **F-4 — snapshot/graph `param_groups` type-ignore.** The four-line `# type: ignore`
  cluster is in `resolution/graph_builder.py:408-412` (the `param_groups` loop:
  `[assignment]` + `[attr-defined]`), per `snapshot-generation/audit.md:186`. Annotate
  or rename `param_groups` at its root so the cluster deletes cleanly; mypy count must
  not rise.
- **F-5 — dead `out = subprocess.run` var + unflipped plan checkboxes.** Spot-grep found
  **zero** `subprocess` occurrences in `src/` or `scripts/` — the var appears already
  removed. VERIFY at implement (against `snapshot-generation/audit.md:120-123`); if gone,
  mark done; either way flip the unflipped plan checkboxes the finding names.
- **`_check_semantic_match`** (`analysis/phantom_detector.py:263`) — grep: def only, zero
  callers. DELETE.
- **`_deserialize_constraint_info`** (`snapshot/loader.py:275`) — grep: def only, zero
  callers. **HANDOFF — OUT OF SCOPE here.** Item 4's approved constraint-serialization
  design deletes it (it will either wire a real deserializer or remove the stub). Left
  in place so it dies once, in Item 4. Recorded so it is not orphaned.

### G. SC-11 AST-based import rewrite (D1-F1) — assess/implement/file

`identifier-sanitization/close-out.md:31` claims the AST-based import rewrite (substring,
first-match) is a "filed follow-up" — but it is filed **nowhere**. Assess it against the
registry alias-rewrite no-not-found branch (a D3 hygiene site). Implement if small; else
**file it properly** as a P3 BACKLOG entry (closing the false close-out claim). Record
the decision.

### H. The 4 vacuous typed-API skipifs — SIMPLIFY

`test_output_registry.py` carries 4 `skipif` guards (`:114, :119, :141, :146`) gating on
typed-API availability. The API exists at HEAD, so they never fire (D2 confirmed).
Remove the guards; the tests run unconditionally.

## Known Requirements

- **[HARD]** Every deletion lands only with **re-verified zero-callers grep evidence at
  implement time** — the spec-time greps above are the first pass, not the last (line
  numbers and export sites drift).
- **[HARD]** The aggregation-literal fix keeps **all existing corpora byte-identical**;
  all baseline/snapshot regeneration goes through `scripts/capture_*.py` with reviewed
  diffs (R3). No hand-edited baselines.
- **[HARD]** R4 verify-then-fix on the aggregation bug: intent checked against doc-19
  (done — fix code to doc), then reproduced with a failing probe on the new fixture
  *before* the fix.
- **[HARD]** **Sequencing vs Item 4.** Item 4 bumps the snapshot format (v1→v2) and
  re-captures every snapshot. This item's new aggregation fixture capture and its
  byte-identity gate must run **either entirely before Item 4's bump** (v1 baselines;
  Item 4 re-captures the new fixture with the rest) **or entirely after Item 4's
  re-capture** (byte-identity judged against the v2 baselines) — never interleaved.
  State only; the orchestrator slots it.
- **[HARD]** No ComputationGraph rev. Every change is a deletion, a docstring, a test, a
  unit pin, or the dispatch-order fix. Anything needing a graph rev is out of scope.
- **[NEED]** Every D1 finding (F1–F5) ends **dispositioned** — done, filed with a real
  BACKLOG entry, or handed off to its owning item — with the disposition recorded in the
  plan close-out. Nothing silently dropped (register discipline).
- **[INFERRED]** A deletion that orphans a conformance test updates or removes that test
  in the same change; any REQ/matrix re-frame it forces (REQ-PGD-06) is **handed to
  Item 7**, which owns the matrix and runs after this item.

## Non-Goals

- `resolve_input` excision/cutover — Item 7 owns that decision.
- `_deserialize_constraint_info` deletion and `extract_all_constraints` deletion — both
  are Item 4's (its approved design deletes them as part of constraint serialization).
- Constraint serialization on the from-snapshot path — Item 4.
- Any ComputationGraph rev or new feature work surfaced by a deletion (file it).
- Forcing the two-sanitizer consolidation when the divergence is load-bearing (file it
  instead — see F-2).

## Open Questions / Deferred to design

Item 8 has no design phase (deliverables are `{spec,plan}.md`). The two judgment calls
are verify-at-implement, with recorded decision paths already in the catalog:

- Whether `get_default_value` / `generate_derived_group_json` encode a live requirement
  vs. exist only for their own tests — resolved by the implement-time grep + the
  recorded fork (B), not deferred to a human.
- Whether the two-sanitizer consolidation (F-2) is safely doable — assessed at
  implement; default disposition is FILE, given the load-bearing divergence.

**Coordination recorded (not open):**
- **generation-boundary item** (BACKLOG: In Progress, BUILD phase, Step 7.6 —
  traceable). It enforces `generation/` consuming only ComputationGraph. This item
  deletes `generation/` symbols (two templates, `map_sysml_type_to_rootmodel_wrapper`,
  `generate_derived_group_json` + its `__init__` exports) — all surface-shrinking, low
  conflict. Flag the shared files (`type_mapping.py`, `entry_point.py`, `templates/`,
  `generation/__init__.py`) to that owner so a rebase does not resurrect the deleted
  exports.
- **Item 4** owns `_deserialize_constraint_info` and `extract_all_constraints` (F, above).
- **Item 7** owns the REQ-PGD-06 re-frame if `get_default_value` is deleted (B), and the
  matrix rows for any REQ this item touches.
- **Item 10** sweeps the retired doc-19 and doc-25 caveats at epic close (D, E).

**Orchestration mode:** autonomous epic run. Every disposition above is decided and
recorded; there is no blocking human decision. The two forks (B, F-2) resolve on
implement-time evidence with the decision paths written down.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 8 + R1/R3/R4 + SC-G)
- **Required Reading:** discovery register §D1/§D2
  (`.project/research/20260706_pipeline-truth-discovery.md`); BACKLOG
  DOCS-SCRUB-F1/F3; `docs/architecture/reference/19-ast-dispatch-invariant.md`
  (the known-deviation note to retire)
- **Research:** `.project/research/20260706_pipeline-truth-discovery.md`
- **Plan:** `.project/active/cleanup-debt/plan.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_plan` (Item 8 has no design phase).
