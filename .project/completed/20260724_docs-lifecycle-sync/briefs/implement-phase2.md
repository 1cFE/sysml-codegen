# Brief — implement: docs-lifecycle-sync, Phase 2 ONLY (Resolver-Architecture Reconciliation)

**Work item:** `.project/active/docs-lifecycle-sync/`. Read in order: `spec.md` (R6, R7),
`plan.md` (Phase 2), `inventory.md` (sweeps C and D rows + the surfaced module_kind note —
Phase 1 deferred those rows to you deliberately). Phase 1 is committed (`b2e0fc3`).

**Scope guard:** Phase 2 only. Stop after its commit; do not start Phase 3.

**Baseline:** merged main `936315c`, branch `docs-lifecycle-sync`. Docs + `.project/` only.

**Ground truth for the new content, in priority order:**
1. The merged code itself: `src/sysml_codegen/resolution/producer_resolution.py` (KEY_FORMS
   table `:527`, `resolve_producer:616`, Tier/TerminalPolicy), `producer_completeness.py`,
   and the three consumer call sites (`constraint_lowering.py:174`,
   `dependency_backtracker.py:596`, `graph_builder.py:1403,1640,1663`).
2. Item 2's archived design/evidence:
   `.project/completed/20260720_constraint-lifecycle-shared-resolution/{design,evidence}.md`.
   If these contradict merged code anywhere, the code wins — and you must surface the
   contradiction loudly in the register, not silently harmonize (capture-fidelity rule 4).

**Deliverables (owner-approved defaults from spec R6):**
1. Replace `docs/architecture/reference/04-input-resolver.md` with a producer-resolution
   reference doc, keeping the `04-` slot (rename to e.g.
   `04-producer-resolution.md` and fix inbound links, or retitle in place — your call,
   recorded). Cover: the ordered KEY_FORMS ladder, `resolve_producer` as the single entry
   point, the Tier/TerminalPolicy strict-vs-lenient split, the three consumer paths, and the
   `producer_completeness` check. Cite merged-main lines throughout.
2. Amend `24-dual-resolution-architecture.md` to the unified-ladder narrative. Its
   pre-unification story may survive only as clearly-marked dated history.
3. Fix in-place resolver references in docs 03, 05, `overview.md`, and the
   verification-matrix rows the register lists (sweep D rows).
4. The module_kind sweep (register rows C1–C9): doc 05's bool-flag claims,
   `22-output-schema-rules.md:179`, matrix REQ-MF-03 text — in this same commit so doc 05
   and the matrix don't split.
5. Reconcile doc 19's prose dispatch table to `DUAL_CHECK_SITES`
   (`tests/conformance/test_ast_dispatch_invariant.py`) — R7 second half.
6. Update `inventory.md`: set the fix-disposition on every C/D row you close; run and record
   the Phase 2 exit greps:
   `grep -rn 'input_resolver\|resolve_input\|AGG_STRATEGIES\|DesignAttributeLookup' docs/architecture/`
   and `grep -rn 'is_computed_attribute\|is_aggregation' docs/architecture/` — both must
   return zero LIVE claims (clearly-marked dated history is acceptable).
7. Tick plan.md Phase 2 boxes + Implementation Notes. One commit:
   `docs-lifecycle-sync Phase 2: resolver-architecture docs reconciled to producer_resolution`
   (+ `Co-Authored-By: Claude <noreply@anthropic.com>`).

**Quality bar:** a tired engineer must be able to read the new doc 04 once and answer "what
resolves an input, in what order, and what happens on a miss in strict vs lenient mode."
Corrections shrink/amend; no "used to say X" prose outside marked dated-history blocks; no
release claims.

Finish with `ARTIFACT: docs/architecture/reference/<the new/renamed doc 04>`.
