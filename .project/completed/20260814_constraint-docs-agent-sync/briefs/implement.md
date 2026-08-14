# Implement-stage brief — Item 7 (constraint-docs-agent-sync)

**From:** orchestrating session, 2026-08-14.

## The work item

Execute the plan: `.project/active/constraint-docs-agent-sync/plan.md`, phases 1–6 in order.
The spec (`spec.md`, same folder) is the contract; the owner checkpoint
(`owner-checkpoint-20260813.md`) is verbatim payload — the two owner bullets are NEVER reworded,
in any artifact you write. Check plan boxes as you complete them and fill the per-phase
Implementation Notes; a resumed session continues from the last checked box.

## Intent

This item documents the landed constraint-semantics contract so the next authoring session —
human or agent — teaches the new policy instead of the superseded one. The falsifier is in the
plan's "The Point": a reader of any shipped surface in the three repos reproducing the
superseded constraint shape means the item failed. Hold that bar when you write: teaching text
a tired modeler reads once and gets right (working-voice rules), not change-log prose.

## Hard boundaries (owner-grade; violating any of these is a stop-and-report)

- TEAx edits ONLY on branch `constraint-semantics-item3` at `/home/reid/1cfe/teax`. Never
  `main` in any repo. Nothing is pushed anywhere.
- agentic-mbse edits ONLY in the worktree `/home/reid/1cfe/agentic-mbse-item7-rebuild`
  (branch `item7-rebuild`).
- No code, fixture, or schema changes — docs, skills, prompts, and `.project/` records only.
- Archived records under `.project/completed/` are cited, never edited.
- Never `uv run`. The one licensed check uses exactly the plan's Phase 6 terms.

## Execution notes

- Phase 1's sweep is the foundation — record RAW output before any edit; the sizing counts in
  the plan are for comparison, not for copying.
- Commit discipline: make a git commit in the relevant repo at each phase boundary (codegen
  commits for codegen+`.project/` changes; agentic-mbse and TEAx commits in their own repos
  when their files change). Subject line leads with what the phase landed. This trail is how
  the run is audited.
- If a phase surfaces something that contradicts the spec or plan (a fourth item3-F2 site is
  pre-authorized; anything else unexpected), record it in the phase notes and — if it blocks —
  stop cleanly at the phase boundary and ask; do not improvise around a premise conflict.
- If you approach your session limits, stop at a phase boundary with notes filled and say
  which phase is next; the orchestrator will resume you.

End your final message with the phases completed, any deviations, and
`ARTIFACT: .project/active/constraint-docs-agent-sync/plan.md` plus the verification record.
