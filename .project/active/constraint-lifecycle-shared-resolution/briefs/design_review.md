# Design Review Brief — Lifecycle Item 2: Shared Producer Resolution and Gate A

**Stage:** design_review (fresh session, independent of the authoring stage)
**Under review:** `.project/active/constraint-lifecycle-shared-resolution/design.md`
against `spec.md` in the same directory. Authority chain per `briefs/spec.md`.

## Orchestrator rulings already made (review the mechanism, not the permission)

- **PC-1 ruling:** adding a NEW `part_usage` owner branch to `prepare_constraint_usages`
  (reading `usage.owner.owner`) is an extension of the Item 1 certified seam, not a rework —
  CONDITIONAL on existing branches remaining unchanged and Item 1's full acceptance + unit
  suites staying green untouched. Your job: verify the design's mechanism actually satisfies
  that condition, and that the claimed adapter shape (`owner.owner` carries the usage) is real.
- **PC-2 ruling:** the reframing is accepted — the entry-point backfill is pre-build, the
  spec's D-1 basis is wrong, and the requirement stands on iteration-order dependence. The spec
  will be amended; confirm the design's replacement basis is itself correct.

## Review priorities

1. **PC-1 mechanism:** is the owner-classification analysis right at the adapter level
   (verify against agentic-mbse's actual fact shapes, not the design's description)? Does the
   proposed branch preserve every Item 1 certified behavior? Is the permission-blocked live
   confirmation properly fenced by a Phase 0 stop condition?
2. **Tier vs key-form separation:** the design's organizing idea — invariant 19's two tiers
   constrain producer class, not key count; each guessing key form has an exact-identity twin
   in another ladder, so guesses get deleted without losing coverage. Attack this: find a
   currently-resolving model shape that would STOP resolving under the unified exact-key set,
   or confirm none exists.
3. **Strict/lenient at terminal miss only:** verify the design doesn't thread mode flags
   through rungs or reintroduce first-pick/leaf-guess under a new name.
4. **The five spec-bet verdicts:** each confirmed/challenged verdict must carry real code
   evidence; spot-check them at the cited locations.
5. **Fixture traps:** the design flags that inline-form constraints never reach
   `resolve_actual` — verify the Gate A fixture spec (def-typed form, explicit self-named
   actual, usage-owned attribute on concrete PartUsage) actually exercises the fixed path.
6. **Folded-in plan:** phases ordered so PC-1 resolves before any deletion; per-phase
   validation commands runnable; stop conditions concrete.
7. **Deletion inventory:** complete per the spec's six targets; no shim/alias/adapter survives
   in the design; no intentional boundary collapsed.

Verdict: Approve / Approve-with-revisions / Needs-rework, findings with evidence. Max-two-round
discipline: only must-fix findings return to the author.
