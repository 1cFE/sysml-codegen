# Stage brief: design — CONSTRAINT-SEMANTICS Item 2 (Canonical Usage Domain and Catalog Totality)

Work in `/home/reid/1cfe/sysml-codegen-item7-rebuild` (branch `item7-rebuild`; companion worktree
`/home/reid/1cfe/agentic-mbse-item7-rebuild`).

**Deliverable:** `.project/active/constraint-catalog-totality/design.md`

**Primary input — the reviewed spec:**
`.project/active/constraint-catalog-totality/spec.md` (verdict Revise → all 11 findings resolved;
resolutions in `spec-review.md`). The spec carries the requirements, provenance grades, non-goals,
and the eight open questions deferred to you. Read it first, then the code it cites:
`elaboration/elaborate.py` (`_scopes_for_owner`, `_build_constraint_nodes`,
`_constraint_metadata`), `elaboration/graph.py` (`ConstraintNode`), `elaboration/project.py`,
`snapshot/instance_graph.py` (codec, fingerprints, version constant), `extraction/extractor.py`
(`collect_constraint_manifest`), the four generation preflights, and the catalog generation path.

## The eight decisions you own (from the spec's Open Questions)

1. **Domain representation** — new usage-tier record kind in the instance graph vs a usage-level
   record beside the per-occurrence `ConstraintNode`s. Name the single owning representation and
   the join to per-occurrence entries. The one-authority rule (D-3, invariants 40/48) is
   inherited: no parallel inventory.
2. **Vacuous-inapplicability mechanism** — model annotation vs reviewed catalog-level acceptance.
   The spec states the properties it must have (explicit, single-authority, fingerprinted, cannot
   silently change coverage role).
3. **Completeness gate home** — extraction-time vs generation-preflight; composition with the four
   existing preflights and ledger checks.
4. **Snapshot version rule** — whether `instance-graph/v2` bumps and the fail-closed rule for
   in-between shapes.
5. **Disposition-kind and reason token spellings** — contract vocabulary governs (`eligible`, not
   the epic's `executable` variant). Item 3 will consume these tokens: record them in a form Item 3
   can cite (a named section of your design), and prefer spellings that won't force a second schema
   change when Item 3 adds coverage accounting.
6. **REQ-EXT-09 internal row conflict** — row rewrite vs domain-boundary change. Either way the
   headline 65 cannot move.
7. **Manifest sweep fate + independent totality oracle — decided together.** Retire or demote to
   test-side oracle with no `src/` caller; name what enumerates the authored population
   independently of the domain under test.
8. **Recapture scope** — the spec requires covering every snapshot-bearing fixture (21 at HEAD),
   counted at execution. Whether the 16 snapshot-less corpus fixtures gain snapshots is yours to
   decide explicitly. Orchestrator steer (execution-tier, record your own reasoning): minting new
   snapshots for fixtures that never had them looks like scope growth beyond the Item 7 register's
   "one reviewed recapture at its final schema"; decide against unless the schema change itself
   forces it, and record the call either way.

## Quality bar and constraints

- One authority, no shims: prefer deletion over compatibility layers (standing owner direction —
  simplicity is qualitative, judged at review). If the manifest sweep retires, delete it; don't
  strand dead code.
- Design the amendment/edit set for the two Item 1 forward pointers
  (`docs/architecture/modeling-assumptions.md:476-477`, `:489-496`) and the REQ-EXT-09/REQ-CL-04
  rows — documentation is corrected before confirmation tests run (owner-directed sequence).
- The severity rule keys on form AND cause together; `catf_mfe_d5` (all 56 invisible usages are
  bare `constraint`) must still generate afterward, with 65 carriers.
- Keep provenance grades when citing spec requirements; your design decisions are agent-grade by
  construction.
- If a probe of the code contradicts a spec premise (e.g. the classifier doesn't behave as cited),
  surface it in the design and park dependent conclusions; don't resolve silently.
- Include a test design: the independent totality tests (fail if a pre-expansion usage vanishes),
  the mutation tests (remove/duplicate/misjoin a disposition), severity-by-cause fixtures
  (asserted-unattachable halts; asserted-vacuous warns; plain-with-BLOCKing-predicate generates),
  and three-route parity (live / in-place snapshot / relocated snapshot).

## Environment notes

- Licensed runs: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; verify zero
  license-skip lines. Test command: `uv run --extra dev pytest tests/`.
- Generated baselines/fixtures are format-exempt. Recapture review = timestamp-only diff check,
  then revert untouched fixtures.

Finish with `ARTIFACT: <path>` as the last line of your final message.
