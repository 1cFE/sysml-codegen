# Spec-stage brief — Item 7 (constraint-docs-agent-sync)

**From:** orchestrating session, 2026-08-14. Provenance marks below follow
`claude-pack/rules/capture-fidelity.md`: `[OWNER…]` = owner-grade, `[AGENT]` = my
inference/decision as orchestrator — do not upgrade my grades to owner intent.

## The work item

Write the **light spec** for epic CONSTRAINT-SEMANTICS **Item 7: ADR, Product Promise, and
Agent-Facing Documentation Sync**. This is capture, not invention — the requirements are already
enumerated. Authority, in order:

1. `.project/backlog/epic_constraint_semantics_contract.md` → "### Item 7: ADR, Product Promise,
   and Agent-Facing Documentation Sync" — scope (6 numbered areas), success criteria, out-of-scope.
2. `.project/active/constraint-docs-agent-sync/owner-checkpoint-20260813.md` — **read in full.**
   Pre-discharged owner checkpoint: the `[OWNER-VERBATIM]` coverage-truth promise (never reword
   it), the glean-from-concept-docs instruction, filing guidance, and the item3-F2 ruling
   (option (a), `[AGENT] ratified by owner 2026-08-13`).

Item home: `.project/active/constraint-docs-agent-sync/`. Write the spec there.

## Intent (why this item exists)

The epic landed a new constraint-semantics contract (Items 1–6, 8, 9, all closed and archived
under `.project/completed/20260813_*`). Item 7 documents the **final landed state** so the next
authoring session — human or agent — teaches the new policy instead of the superseded one, and
gives the coverage-truth promise its first durable product/ADR home. It is the last item before
epic close.

## Decisions already made (carry into the spec with these grades)

- **[OWNER 2026-08-14]** The item runs through close (archive), but the **epic stays open** —
  epic close, `pre_pr`, and any push are reserved to the owner. Out of scope for this item.
- **[AGENT, orchestrator 2026-08-14]** ADR/product home shape: first `.project/product/INDEX.md`
  ledger entry + a per-repo ADR convention, per the handoff default (the repo has no
  `.project/product/` or `.project/adr/` infrastructure today — deciding the home and minting the
  first capture is this item's work). The spec records this as the default; the design/plan may
  refine the shape but not relocate authority.
- **[OWNER-ratified framing]** The known tension (promise bullet 2 vs the A5/A6/A7 basis rulings)
  is handled exactly per the checkpoint's filing guidance: promise stated as directional intent,
  pointing at `[ACAUSAL-RELATIONS-CAPABILITY]` (BACKLOG, 2026-08-13). Not open for re-resolution;
  the spec must require it be surfaced in the entry, never silently resolved.
- **[AGENT]** item3-F2 amendment execution: the contract clause amends to reaching-gates scope
  with original text preserved per Item 1's amendment conventions, and the umbrella spec's
  parked-conflict record (`.project/active/constraint-semantics-contract/spec.md`, Open
  Questions) flips to RESOLVED-with-citation. Both are requirements of this item.

## Facts the spec should rely on (verified by orchestrator or carried from close records)

- Cross-repo surfaces: codegen (this repo), agentic-mbse worktree
  `/home/reid/1cfe/agentic-mbse-item7-rebuild` (branch `item7-rebuild`; the editable install
  reads it), TEAx `/home/reid/1cfe/teax` (branch `constraint-semantics-item3` — all TEAx edits
  stay on that branch, never `main`).
- The stale agent-prompt example: codegen `.claude/skills/sysml-conventions/SKILL.md:136` —
  inline assert with unit literal, superseded by the bindings-only blessed pattern.
- Item 9 final state to document: three executing gates (A2, A3, A9), identity
  `65 = 56 carriers + 9 named deletions` (`tests/fixtures/catf_mfe_gated/PROVENANCE.md:14`),
  `[CONSTRAINT-FORM-PER-DIMENSION-COST]` filed in BACKLOG.
- B1–B5 marker mechanism (Item 5 close obligation): `@inapplicable:` reaches the domain on
  bindings-form constraints; on inline-predicate form SysIDE silently drops doc comments — open
  defect `[INLINE-PREDICATE-MARKER-DROP]`; until it closes, PROVENANCE carries the disposition.
  Worked case: `catf_mfe_gated` B1–B5 (five markers written, zero carried); loud detector:
  `tests/conformance/test_constraint_population_oracle.py` rule 3.
- Item 8 final state: `modeling-assumptions.md` §8 unit-on-binding account changed — authored
  unit text on constraint-formal and computed-attribute ports, fail-closed
  `SI_RENDERING_COLLISION` on unequal metadata. Evidence:
  `completed/20260813_unit-lane-port-metadata/`.
- Item 2/3 surfaces: disposition vocabulary (`eligible`/`excluded`/`non_reaching`, closed
  reasons, precedence — the Item 3-citable section of
  `completed/20260813_constraint-catalog-totality/design.md`), carriers, totality gate, six
  report states, coverage block, TEAx keep-for-boundary default + feed-strategy opt-in config.
- Also folded in: A-8 matrix reconciliation (one pass, recount discipline per
  `[MATRIX-EPIC-SURFACE-ROWS]`), D9 eligible+inapplicable refusal + companion advisory guidance
  for agentic-mbse `docs/patterns/constraints.md`, and the two Item 3 close residuals re-homed
  here (design-F2's Appendix C cell, D9 advisory guidance).

## Constraints on the spec itself

- Light spec — the smallest auditable capture. Map epic scope areas + checkpoint obligations to
  requirements with correct provenance grades per capture-fidelity: `[OWNER-VERBATIM]` → `[NEED]`
  carrying the quote or path-cite; `[OWNER]` → `[NEED]`; `[AGENT]` → `[INFERRED]`; gleaned
  concept-doc material → `[INHERITED: source]`.
- Out of scope (from the epic section): any code/fixture/schema change; re-litigating the
  contract; the derivative fixture docs (Item 5 owns them).
- Success criteria: adopt the epic section's six checkboxes as the acceptance frame; add the
  doc-check/`git diff --check` gate in every touched repo.
- Do not run `uv run` for anything; if you must verify a test path exists, plain file reads are
  enough at spec stage.

End your final message with `ARTIFACT: <path>` when the spec is written.
