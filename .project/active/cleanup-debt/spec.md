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

- [x] **Zero grep hits** for every deleted symbol across `src/` and `tests/`; the full
  suite is green; ruff/mypy counts are not worse than the 21/109 baseline (SC-G).
- [x] **Suite green with the count story told, not assumed.** The net test count
  **decreases** (self-tests of deleted dead symbols go with them); the close-out names
  each deleted test and the symbol it solely pinned, and confirms no non-self-test lost
  coverage — so "green" is auditable, not achieved by silently dropping an orphan (the
  test-deletion rule below).
- [x] **Aggregation-literal fix reproduced then fixed** (R4): a failing probe on a new
  literal-bearing aggregation fixture demonstrates the mis-dispatch *before* the fix;
  after the fix that fixture shows the corrected dispatch; **all existing corpora stay
  byte-identical** against the baseline set fixed by the Item-4 sequencing requirement
  (v1 if this lands before Item 4's bump, v2 if after — see the [HARD] sequencing req).
- [x] **The fixed dispatch has a REQ home.** A new/extended REQ-AST row governs
  literal-before-invocation ordering in `_walk_aggregation_ast`, verified-by the new
  fixture; its matrix row is added in this item (R1: rows move with code).
- [x] **doc-19 known-deviation note retired**, its BACKLOG entry (`BACKLOG.md:185`)
  closed, and the dotted-leaf alias edge pinned by a unit test, retiring doc-25's "no
  current model triggers this" hedge.
- [x] **Every D1 finding (D1-F1…D1-F5) ends dispositioned** — deleted, fixed, filed with
  a real BACKLOG entry, or handed off to its owning item — with the disposition recorded
  here. Nothing left "filed" only in a plan file.
- [x] **The 4 vacuous skipif guards removed**; their tests run unconditionally.
- [x] Every touched component's docstring/reference doc updated in the same change (R1) —
  including doc-17 when `get_default_value` is deleted.

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
  its own def, the module-docstring bullet (`type_mapping.py:9` — `- map_sysml_type_to_rootmodel_wrapper(): ...`),
  the `__all__` entry (`:81`), and one conformance test
  (`test_type_mapping_consolidation.py`, incl. a `hasattr` assertion at `:242`). **No
  production caller** — `modules.py` imports the sibling `map_sysml_type_to_python`, not
  this. DELETE the function, the docstring bullet, the `__all__` entry, and the test
  assertions that pin it (drop the dedicated test cases; keep the sibling-function tests).

- **`get_default_value`** (`analysis/parameter_groups.py:533`) — callers: its own def
  and `test_parameter_group_deriver.py` only; documented at doc-17 rows `:26` (REQ-PGD-06)
  and `:28` (REQ-PGD-08 prose) + method prose `:143`; matrix PASS row at
  `verification-matrix.md:379` (verified-by those very tests). **Verify-then-delete with
  a recorded fork:** at implement, confirm the lookup it performs is duplicated by live
  production code (i.e. the method only wraps `_attr_index` for the test).
  - **If dead → DELETE** method + its tests. **In the same change, per R1/R4 step 4,
    this item updates doc-17** (retire/rewrite rows `:26`/`:28` prose and method prose
    `:143` so no doc-line names a deleted symbol) **and leaves a visible breadcrumb on
    `verification-matrix.md:379`** (e.g. `PASS → PENDING-ITEM7`, pointing at the BACKLOG
    entry) so the transient "PASS pins a deleted test" gap is not silent. **Only the
    matrix PASS-row re-frame itself is handed to Item 7** — recorded durably in BACKLOG
    (`[ITEM7-PGD06]`, conditional on this deletion), because `matrix-truth/` (Item 7) is
    still an empty directory and would never see an in-spec note.
  - **If the method is the sole implementation of a live requirement → keep it** and file
    the observation. `[ITEM7-PGD06]` becomes a no-op Item 7 retires.
  - Record which fork was taken in the close-out.

- **`generate_derived_group_json`** (`generation/entry_point.py:188`) — callers: its own
  def, `__all__` (`:326`), and the `generation/__init__.py` re-export (`:20,67`). **No
  functional caller.** The live path is `generate_all_derived_jsons` (omits null-default
  keys — the shape Item 7-of-the-prior-epic corrected); this dead twin still emits
  null-default keys. DELETE the function + both export sites. Verify no external
  (fusion-tea) import at implement.

- **`binding_to_entry_point`** dual-write (DEPRECATED) — the `BacktrackingResult` field
  (`dependency_backtracker.py:81`) and its `_binding_to_entry_point` backing dict, kept
  in lockstep at ~7 init/reset/write/construct sites (register cited 62/80/176/304/372/
  404/439; spot-grep at HEAD shows the machinery at 62/81/177/218/304/373/405/421/440,
  plus the naming comment at `:179` — `# Unified binding resolutions (replaces
  _binding_to_entry_point)` — which references the deleted dict; **re-grep at implement**).
  **No consumer reads `.binding_to_entry_point`** (grep: only the field def, the writes,
  and `test_data_models.py:361` which asserts the field name exists). DELETE the field,
  the backing dict, all dual-write/init/reset/construct sites, the `:179` comment, and
  the `test_data_models.py` field-name assertion.

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
  literal-bearing aggregation, so the reorder changes nothing for them) — judged against
  the baseline set fixed by the [HARD] Item-4 sequencing requirement (v1 before Item 4's
  bump, v2 after); the new fixture shows corrected dispatch.
- **REQ home (R1: rows move with code).** The fix moves `_walk_aggregation_ast` from
  "documented-as-deviation" to "documented-as-conforming" — but no existing REQ-AST row
  covers it: REQ-AST-03/-08 are scoped to `reconstruct_expression` by their own text,
  and REQ-AST-05 governs this function only for FCE→SingletonTerm classification, not
  literals. So **add a new REQ row** (recommend **REQ-AST-10**: "`_walk_aggregation_ast`
  SHALL dispatch all literal/null branches before the invocation catch-all"),
  verified-by the new literal-bearing fixture. **Add its matrix row in this item** —
  matrix additions are allowed in-item per R1 ("REQ tags + docs + matrix rows move with
  code"); only Item-7's *PASS-row reconciliation* waits. Note the addition in Item 7's
  ledger via BACKLOG so the sweep sees it.
- **Docs (R4 step 4).** Retire the doc-19 "Known deviation — `_walk_aggregation_ast`"
  note (and add REQ-AST-10 to doc-19's requirements table); **close the BACKLOG entry
  that tracks this bug** (`BACKLOG.md:185`, currently tagged "Absorbed into ... Item 8" —
  move it to Completed / strike it on landing). **Coordinate the doc-19 retirement with
  Item 10** (which sweeps retired caveats at epic close).

### E. Dotted-leaf alias unit pin (retires doc-25 hedge)

doc-25 (`25-hierarchy-resolver.md:243-248`) hedges "No current model triggers this" for
the `.`-suffix CHAIN-alias branch, which matches any dotted `source_path` whose leaf
equals the aggregation `attribute_name` regardless of which part it references. Add a
cheap unit pin that exercises the edge directly (a dotted CHAIN redef whose leaf matches
an aggregation attr but references a different part) and asserts the current behavior,
then rewrite the hedge to point at the pin. This is a pin + doc edit, not a behavior
change.

### F. D1 unfiled residue (D1-F1…D1-F5 + two dead helpers)

- **D1-F2 — two-sanitizer consolidation.** `core.sanitize_name`
  (`core/qualified_names.py:13`) vs `expression_compiler._sanitize_name`
  (`extraction/expression_compiler.py:167`). The divergence is **load-bearing**: the
  compiler deliberately drops the reserved-word suffix that `core.sanitize_name`
  applies, and the identifier-sanitization item built the FORMULA wire to match *by
  construction* on that difference. RECOMMENDATION: **assess, then FILE as P3 BACKLOG**
  rather than force-consolidate in a cleanup pass — a naive merge risks the FORMULA
  REFERENCE match. Implement only if a safe shared core falls out with the byte-identity
  gate green. Record the decision.
- **D1-F3 — catf fallback-EP chore** (`pumping_speed_total`). Per
  `cross-part-wiring/plan.md:819-823`: catf's remaining fallback EP is a
  `USAGE_LITERAL 200.0` — fell-through but **valued**, so the collector correctly skips
  it; it is a benign pre-existing catf gap, **not a bug**. Assess whether it is still
  present; disposition = file-or-no-op (do not "fix" a non-bug). Record.
- **D1-F4 — snapshot/graph `param_groups` type-ignore.** The four-line `# type: ignore`
  cluster is in `resolution/graph_builder.py:408-412` (the `param_groups` loop:
  `[assignment]` + `[attr-defined]`), per `snapshot-generation/audit.md:186`. Annotate
  or rename `param_groups` at its root so the cluster deletes cleanly; mypy count must
  not rise.
- **D1-F5 — dead `out = subprocess.run` var + unflipped plan checkboxes.** Spot-grep found
  **zero** `subprocess` occurrences in `src/` or `scripts/` — the var appears already
  removed. VERIFY at implement (against `snapshot-generation/audit.md:120-123`); if gone,
  mark done; either way flip the unflipped plan checkboxes the finding names.
- **`_check_semantic_match`** (`analysis/phantom_detector.py:263`) — grep: def only, zero
  callers. DELETE.
- **`_deserialize_constraint_info`** (`snapshot/loader.py:275`) — grep: def only, zero
  callers. **HANDOFF — OUT OF SCOPE here.** Item 4's approved constraint-serialization
  design deletes it (it will either wire a real deserializer or remove the stub). Left
  in place so it dies once, in Item 4. Recorded so it is not orphaned.

### G. SC-11 AST-based import rewrite (D1-F1) — assess-then-decide, verdict recorded

`identifier-sanitization/close-out.md:31` claims the AST-based import rewrite (substring,
first-match) is a "filed follow-up" — but it is filed **nowhere**. This is a real
assess-then-decide, and **the assessment verdict is a recorded artifact either way** — so
"file" is a reasoned outcome, not the path of least resistance:

- **Assess** the rewrite against the registry alias-rewrite no-not-found branch (a D3
  hygiene site); record what the comparison showed and the size judgment (what "small"
  meant here — roughly, a one-to-two-site local change vs. a cross-module rework).
- **If small → implement**; the commit is the artifact.
- **If not → file** a P3 BACKLOG entry that carries the size argument, and correct the
  false "filed follow-up" claim in `close-out.md:31`.

Either branch leaves the verdict written down; neither can silently skip.

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
- **[HARD]** **Test-deletion rule (this item's, distinct from Item 6's).** Item 6's rule
  is "no test deleted without a replacement." This item is different: a test is deleted
  **only when its sole purpose was pinning a now-deleted dead symbol**, so no live
  behavior loses coverage. Expect a **net test-count decrease**; the close-out names each
  deleted test and the symbol it pinned. "Suite green" (SC-G) is therefore auditable, not
  a cover for silently dropping a failing orphan.
- **[NEED]** Every D1 finding (D1-F1…D1-F5) ends **dispositioned** — done, filed with a
  real BACKLOG entry, or handed off to its owning item — with the disposition recorded in
  the plan close-out. Nothing silently dropped (register discipline).
- **[INFERRED]** A deletion that orphans a conformance test updates or removes that test
  in the same change, and **updates the reference doc it renders stale in the same change**
  (R1/R4 step 4 — e.g. doc-17 when `get_default_value` is deleted). The *matrix PASS-row*
  re-frame that a deletion forces (REQ-PGD-06) is the one piece handed to Item 7 — via a
  durable BACKLOG entry (`[ITEM7-PGD06]`), not an in-spec note — with a visible breadcrumb
  left on the matrix row so the transient gap is not silent.

## Non-Goals

- `resolve_input` excision/cutover — Item 7 owns that decision.
- `_deserialize_constraint_info` deletion and `extract_all_constraints` deletion — both
  are Item 4's (its approved design deletes them as part of constraint serialization).
- Constraint serialization on the from-snapshot path — Item 4.
- Any ComputationGraph rev or new feature work surfaced by a deletion (file it).
- Forcing the two-sanitizer consolidation when the divergence is load-bearing (file it
  instead — see D1-F2).

## Open Questions / Deferred to design

Item 8 has no design phase (deliverables are `{spec,plan}.md`). The two judgment calls
are verify-at-implement, with recorded decision paths already in the catalog:

- Whether `get_default_value` / `generate_derived_group_json` encode a live requirement
  vs. exist only for their own tests — resolved by the implement-time grep + the
  recorded fork (B), not deferred to a human.
- Whether the two-sanitizer consolidation (D1-F2) is safely doable — assessed at
  implement; default disposition is FILE, given the load-bearing divergence.

**Coordination recorded (not open):**
- **generation-boundary item** (BACKLOG: In Progress, BUILD phase, Step 7.6 —
  traceable). It enforces `generation/` consuming only ComputationGraph. This item
  deletes generation-layer symbols (`map_sysml_type_to_rootmodel_wrapper`,
  `generate_derived_group_json` + its `__init__` exports) plus two Jinja templates that
  live one directory up in `src/sysml_codegen/templates/` (a sibling of `generation/`,
  not inside it) — all surface-shrinking, low conflict. Flag the shared files
  (`generation/type_mapping.py`, `generation/entry_point.py`, `generation/__init__.py`,
  and `templates/`) to that owner so a rebase does not resurrect the deleted exports.
- **Item 4** owns `_deserialize_constraint_info` and `extract_all_constraints` (F, above).
- **Item 7** owns the REQ-PGD-06 matrix PASS-row re-frame if `get_default_value` is
  deleted (B) — received via the durable `[ITEM7-PGD06]` BACKLOG entry, not this spec —
  and reconciliation of the new REQ-AST-10 matrix row (D). The reference-doc updates for
  both land in *this* item.
- **Item 10** sweeps the retired doc-19 and doc-25 caveats at epic close (D, E).

**Orchestration mode:** autonomous epic run. Every disposition above is decided and
recorded; there is no blocking human decision. The two forks (B, D1-F2) resolve on
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
