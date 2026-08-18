# Brief — Phase 4 implement: close public routes and registry authority

You are executing **Phase 4 only** of plan **Revision 4** for
`.project/active/stop-reinventing-the-parser/`. Phases 1-3 are complete, audited, and closed —
do not reopen them. Phase 3 closed at `stop-parser-impl-r2` **`1451615`** with verdict Pass
with findings and all findings closed (see plan.md's Phase 3 completion section for the full
arc). Phase 4 proves the full natural-route matrix, removes caller-supplied registry authority,
reconciles outputs and documentation, and establishes the production-ready candidate. Read in
order:

1. `.project/active/stop-reinventing-the-parser/plan.md` — **Revision 4**, your contract:
   "Phase 4: Close public routes and registry authority" (checklist + validation + the
   rewritten A5a/A5b ledger-row item) and the Global Execution Contract.
2. `design.md` — **Revision 8** — sections the phase links:
   `#d9-b9-fails-before-output-mutation`, `#evidence-and-public-boundary-matrix` (now carries
   the strict/lenient arms and the required compound-unit coverage),
   `#public-every-and-only-mutation-proofs`, `#static-removal-checks`, the Codegen-gate
   manifest subsection, `#transition-ledger-seed`, and
   `#documentation-and-backlog-obligations`.
3. `run-records/phase3-audit.md` — the audit + re-audit. Its methods are your quality bar:
   per-consumer proofs must be real (M2's lesson), and the closing audit will rerun deletion
   and escape experiments against your work.
4. `run-records/entry-status.md` — run scaffolding and checkout-integrity rules.

Provenance: plan rev 4 and design rev 8 are binding; owner rulings are encoded there with
their grades. On any conflict, surface it in your final message — never resolve it silently.

## Where you work

- **Codegen worktree:** `/tmp/stop-parser-rev2/worktrees/sysml-codegen`, branch
  `stop-parser-impl-r2` at `1451615` — verify clean before starting. ALL implementation
  commits go here, including the repo documentation sweep (the `docs/` and `verification/`
  files live in this repo).
- **Agentic worktree:** `/tmp/stop-parser-rev2/worktrees/agentic-mbse` at `3f8bd58` —
  **read-only**. If any Phase 4 documentation obligation appears to require writing that tree,
  surface it and continue with everything else; do not write there.
- **Docs checkout:** `/home/reid/1cfe/sysml-codegen` (branch `stop-reinventing-the-parser`) —
  the `.project/` updates the checklist names (current work, epic status, backlog row) plus
  the plan.md "Phase 4 completion" section, committed as your final act.
- Touch NOTHING else — no user checkouts, no `/tmp/stop-parser.QVJIIP/*` (read-forbidden), no
  stash/reset/switch anywhere.

## The work (plan rev 4 Phase 4 is the contract; highlights and hard edges)

1. **Tests first — registry.** Extend
   `tests/conformance/test_generation_exit_type_preflight.py`,
   `tests/conformance/test_module_kind_faildloud.py:264`, and
   `tests/unit/test_registry_generation.py` for no-root, one, repeated, multiple, and
   unsupported root types through the CLI, the direct generator, and **every exported alias**.
   Assert byte-identical output preservation on failure and the absence of any caller
   type-set parameter.
2. **Graph-derived registry.** Replace the untyped failure at
   `src/sysml_codegen/generation/registry.py:48`; remove the fifth parameter at
   `registry.py:245` and the caller account at `cli/__init__.py:734`. Every exported
   generation seam derives and validates its wrapper set from the immutable graph before any
   output mutation.
3. **Full natural-route matrix.** Complete
   `tests/conformance/test_expression_evidence_integrity.py` for calculation-definition
   dependencies, calculation/constraint bindings, aliases, computed attributes, predicates,
   and deep overrides — exact positive, indexed, operand/depth, and missing-target cases,
   through live and admitted/capture arms, strict and lenient where offered. This turns the
   deferred Phase-1 red node `test_every_consumer_cell_names_a_proof` green. Public refusals
   carry the exact-field contract throughout (code, authored reference, root-relative
   `file:line`, cause chain, one rendered token, no graph/snapshot/output mutation).
4. **Dual-layer index proof per consumer.** For each expression consumer: the public test
   proving inventory-before-consumer refusal AND the internal test bypassing only inventory to
   prove the consumer backstop. These must route through the real consumer adapters — a shared
   library call with a role label is the exact defect Phase 3's audit killed (M2); the closing
   audit will delete backstops and count failures.
5. **Preservation and transitions.** Rerun the full occurrence/producer matrix and
   `tests/execution/test_occurrence_derivation_mutation_teax.py` through live and snapshot
   generation; reconcile every changed graph, diagnostic, package byte, and execution result
   against `verification/expected-transitions.md`. Any unlisted difference fails the phase.
6. **Ledger rows A5a and A5b** in the same landing unit as the tests that prove them, per plan
   rev 4's rewritten item: A5b carries **both measured starting arms** (strict refusal under
   the wrong name; lenient graph carrying the diagnostics) so the reconciliation gate expects
   the transition — including the lenient graph's disappearance — rather than flagging
   unlisted drift.
7. **`deep_cross_scope_probe` stays refused** (`SI_OCCURRENCE_MISSING`, authored reference
   preserved, no captured snapshot) under its named A2 row. Any result returning it to a
   captured graph is the **global stop condition** — halt immediately.
8. **Static closure, green together:** both ownership manifests (Codegen's collision-aware
   24-row manifest with receiver-keyed rows, Agentic's), five evasion mutations plus the
   adapter-free evader failing the equality gate, deleted-symbol absence, transitive off-route
   reachability, no dead extraction cluster, no caller-supplied registry authority.
9. **Documentation and filing:**
   - the architecture overview, reference documents 00/01/19, registry reference 20,
     verification matrix, diagnostic reference, P-003 application status, reconciliation
     ledger seed, current work, and epic status, exactly as
     `design.md#documentation-and-backlog-obligations` specifies — verify the indexed-element
     and output-alias follow-ups remain separately owned rather than duplicating them;
   - file **`[DEEP-QUALIFIED-OUTPUT-WIRING]`** as a separate agent-grade backlog row naming
     the authored shape in `tests/fixtures/deep_cross_scope_probe/design.sysml`, the current
     `SI_OCCURRENCE_MISSING` contract, and the A2 transition record;
   - fix the stale fixture comment at
     `tests/fixtures/deep_cross_scope_probe/design.sysml:75` to state the current contract and
     point at `[DEEP-QUALIFIED-OUTPUT-WIRING]` — documentation-only: the authored reference,
     its refusal, the fixture's locked-hash class, and its ledger ownership are untouched;
   - no documentation may claim Phase-5 artifact evidence before those artifacts exist.

## Validation (plan rev 4 has the complete battery — all binding)

- Complete focused natural-route and registry suites with the SysIDE license; no required
  licensed test or route may skip.
- Full Codegen default suite from a fresh declared extraction under `/tmp/stop-parser-rev2/`
  (expected: zero failures once the deferred consumer-cell node goes green), scoped strict
  zero, repo-wide mypy baseline comparison, Ruff.
- Occurrence matrix and the public every-and-only TEAx mutation suite through live and
  snapshot generation; live/snapshot parity; D1-D4 behavior;
  `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py` still empty.
- Baseline/transition reconciliation: all maintained outputs outside named transitions
  byte-identical.
- Exact static-set equality and symbol-absence checks; `git diff --check` clean.
- Manual reviews per the plan: both indexed bare-chain results against the product-lens
  falsifier; registry failure through the real public command with the output directory's
  complete relative-path-to-bytes map unchanged.
- License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; never copy a secret.
  **[OWNER-VERBATIM]** "do not rerun the PDF suite anymore" — the Agentic slow PDF/HTML corpus
  and 15 paid/network cases stay unrun.
- No compatibility wrapper, alias, exemption, or optional path for anything removed (the
  registry's fifth parameter included). A consumer that cannot work without caller-supplied
  registry authority is a design conflict: **STOP and report**.

## Deliverables

1. Commits on `stop-parser-impl-r2` on top of `1451615`, in reviewable units, tests first.
2. Every Phase 4 validation box executed with commands and results recorded; every suite
   figure recomputable from a recorded command (untraceable numbers were audit findings twice
   in this item — do not create a third).
3. plan.md "Phase 4 completion" section filled (completed date, commit SHAs, red-to-green
   account for the deferred node, reconciliation results, issues/deviations, rollback point)
   plus the named `.project/` updates, committed in the docs checkout.
4. Final message: prose summary — registry closure, the matrix account, A5a/A5b
   reconciliation, static closure, documentation sweep, deviations — ending with
   `ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`. If any stop rule trips,
   say so plainly at the top and stop.

**Rollback/stop rule (plan rev 4):** any production change after this phase invalidates the
production candidate and restarts its affected Phase-4 gates before artifact sealing. Phase 4
is the end of your scope — do not begin Phase 5 (artifact chain, production identities,
Fusion landing) in any form, and do not self-certify: a dedicated independent audit follows.
