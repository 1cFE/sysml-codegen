# Close-stage brief — Item 7 (constraint-docs-agent-sync)

**From:** orchestrating session, 2026-08-14.

## The work item

Close epic Item 7. Audit verdict: **CERTIFY-WITH-RESIDUALS**
(`.project/active/constraint-docs-agent-sync/audit.md`) — two named residuals remain, both
owner calls with no work left undone: A-1 (codegen `.claude/` symlink target goes stale until
the owner merges the agentic-mbse worktree branch) and A-2 (`[CONSTRAINT-GATES-UNTAGGED]`
backlog entry, no REQ tags minted).

## Boundaries (owner-grade)

- **[OWNER 2026-08-14]** Close the ITEM only. The **epic stays open**: no epic close, no
  Lessons Learned authoring, no `pre_pr`, nothing pushed, no `main` touched anywhere. The
  umbrella folder `.project/active/constraint-semantics-contract/` stays active until epic
  close.
- Archived records under `.project/completed/` are cited, never edited.

## Close mechanics (the Item 6/8 pattern — archival breaks readers)

1. Archive `.project/active/constraint-docs-agent-sync/` →
   `.project/completed/20260814_constraint-docs-agent-sync/` via `git mv`.
2. Before finalizing, ensure the product-lens ledger carries its close-stage block (D-1's
   citation point 3 — recording that the trail was wired; the durable citations live in
   `.project/product/INDEX.md` and the epic's product-lens block, both outside the archived
   folder — verify both still resolve after the move).
3. **After the `git mv`, prove nothing reads the old path:** `grep -rn
   "active/constraint-docs-agent-sync" tests/ src/ docs/ .project/backlog/ .project/product/
   CLAUDE.md .claude/` and repoint every live hit to the completed/ path (citations both
   directions). Item 8's close broke 7 suite tests exactly this way.
4. Run the collect check: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/
   --collect-only -q | tail -3` (never `uv run`) — collect count must match the
   verification.md baseline.
5. Epic bookkeeping in `.project/backlog/epic_constraint_semantics_contract.md`: Item 7 status
   → CLOSED with archive path, verdict, the two named residuals, and the SC tick state
   (SC1/SC3/SC4/SC6 ticked; SC2/SC5 carrying named residuals). Follow the epic's existing
   per-item close conventions (look at how Items 8/9 closes were recorded, including any
   CHANGELOG convention those closes used).
6. Update `.project/CURRENT_WORK.md`: Item 7 closed; epic tail state = all items closed, epic
   close + Lessons Learned + pre_pr with the owner; the two residuals named.
7. `git diff --check`, then commit (subject leads with the close decision).

End with the archive path, the collect-check result, and `ARTIFACT:` paths.
