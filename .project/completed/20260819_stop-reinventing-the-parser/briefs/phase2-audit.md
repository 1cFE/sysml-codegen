# Brief — Phase 2 audit (dedicated, fresh)

You are the independent auditor for **Phase 2 only** (close the Agentic evidence contract). The
implementing agent's claims are recorded in plan.md's "Phase 2 completion" section; your job is to
try to break them, not to summarize them. Reproduce what can be reproduced; verify the rest
against artifacts. Trust nothing that is only asserted.

Read in order:

1. `.project/active/stop-reinventing-the-parser/plan.md` — Revision 3: the Phase 2 contract
   (checklist, validation boxes, Global Execution Contract) and the completion record you are
   auditing. The Phase 1 completion section lists the 10 Agentic red node IDs Phase 2 had to turn
   green.
2. `design.md` Revision 7 — `#d5-public-agentic-evidence-contract`, `#d6-documenttier-owns-b5`,
   `#agentic-semantic-contract`, `#closed-reference-use-values`,
   `#one-total-inspection-operation`, `#delete-the-permissive-production-surface`,
   `#documentation-and-backlog-obligations`.
3. `run-records/phase1-audit.md` — Phase 1's audit. Its Minors 5 and 11 were assigned to Phase 2;
   verify their closure. Phase 1 itself is closed — do not re-audit it.

## Where the work is

- Agentic worktree `/tmp/stop-parser-rev2/worktrees/agentic-mbse`, branch
  `stop-parser-evidence-r2`: audit commits `40dee5c` → `4a3ec46` → `144ae02` against Phase-1 base
  `8d27fb3` (and `A_base` = `2171016d…` beneath it).
- Codegen worktree `/tmp/stop-parser-rev2/worktrees/sysml-codegen` must be **untouched at
  `d257ef1`** — verify, read-only.
- You may run tests and read anything in those worktrees. You must not modify them, commit, or
  touch any other checkout. For isolated runs build your own extraction under
  `/tmp/stop-parser-rev2/` with `agentic-mbse` in the directory name (a baseline test asserts the
  path contains that string).
- License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` (never copy a secret into
  output). Agentic commands: `uv run …`.
- **[OWNER-VERBATIM]** "do not rerun the PDF suite anymore" — the slow PDF/HTML corpus and the 15
  paid/network cases are outside validation; do not invoke or report them.
- Known `A_base` baseline: 18 fast-suite failures (17 `tests/test_web_backend.py`, 1
  `tests/test_equations.py`, optional-dep `ModuleNotFoundError`). Pre-existing, not item-caused —
  but confirm the set is exactly those 18, no more.

## Audit obligations

1. **Diff-level scope check.** The three commits must contain only what the Phase 2 checklist
   places there. Any change outside the Agentic worktree (Codegen worktree, user checkouts —
   compare `run-records/entry-status.md` digests) is Critical.
2. **Red-to-green quality.** Run all 10 recorded red nodes; each must be green. Then diff each
   test against its Phase-1 body (`git diff 8d27fb3 -- tests/`): a test weakened, softened, or
   replaced to reach green — rather than the implementation satisfying the original contract — is
   a Major finding. The plan forbids substituting easier tests.
3. **Deletion closure.** Independently sweep for all seven ordered deletions
   (`extract_feature_refs`, `feature_reference_facts`, `feature_chain_facts`,
   `ResolvedSemanticReferenceFact`, `has_index_segment`, `ExpressionRef`,
   `BindingInfo.references`): absent from production code, `__init__` barrels, lazy aliases, and
   public exports; no wrapper, deprecation path, or re-implementation under a new name. Inspect
   the migrated consumers (the record claims 8, three beyond the plan's measured list) and confirm
   none reconstructs the weak route locally.
4. **Boundary quality.** `src/agentic_mbse/sysml/reference_use.py` against the design: closed
   union, `IndexedReferenceUse` with no `path` attribute, one total inspection operation,
   `IndexExpression` dispatch from the mapped SysIDE metatype (never a class-name string
   comparison), `DocumentTier` as the sole document-authority owner. Rerun the scoped strict gate
   (`uv run mypy --strict src/agentic_mbse/errors.py src/agentic_mbse/sysml/reference_use.py`);
   require zero.
5. **The three flagged deviations** — scrutinize each; the implementer flagged them honestly, but
   honesty is not correctness:
   - *Ownership gate scoped to adapter-importing modules.* Is `executable_profile.py` really
     neutral `ExpressionIR` only? Do the two anti-vacuity tests actually fire (mutate mentally or
     in a throwaway copy)? Could a production module read raw SysIDE selectors while evading the
     gate by not importing the adapter?
   - *Constraint-fact golden re-anchored on 8 `source_name` lines.* Verify against
     `type_units.sysml` that the new values are the authored spellings, and that every other byte
     of the golden is unchanged (`git diff` the file).
   - *`BindingType` moved from `types.py` to `data_models.py`.* Layering fix or shim? Same enum,
     same values, still exported from the same public surface?
6. **Package/artifact contract.** Version `0.1.3`, `semantic-evidence/v2` marker, `uv.lock`
   consistency; reproduce at least the focused suite and scoped strict from a clean extraction or
   the built wheel in a fresh venv, and verify deleted symbols are absent from the installed
   package.
7. **Completion-record accuracy.** Every count, SHA, and claim in the Phase 2 completion section
   (fast suite 18/1883/1, mypy 101→101, Ruff 119→119, wheel markers, manual inspections) must be
   true or the record corrected. An overstated record is a finding even when the work is sound.
8. **Minors 5 and 11.** Verify both closures: the symbol-absence gate now covers all seven
   deletions with a coverage pin, and the aggregation-refusal test uses a constructed instance
   with a narrowed exception and proves refusal precedes term construction.
9. **Vacuity sweep.** Any new or modified test that cannot fail (empty iteration, over-broad
   catch, self-comparison) is a finding regardless of its color today.

## Deliverable

Write `.project/active/stop-reinventing-the-parser/run-records/phase2-audit.md` (do not commit):
verdict `Pass` / `Pass with findings` / `Fail` for Phase 2, findings ranked with severity and
exact locations, your reproduction results (commands + outcomes), and a short "fit for Phase 3?"
judgment. Final message: prose summary ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/run-records/phase2-audit.md`.
