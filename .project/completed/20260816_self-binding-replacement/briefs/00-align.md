# Align record — orchestrated run of self-binding-replacement

**Date:** 2026-08-15
**Orchestrator:** Claude (`/_my_orchestrate`), input `.project/active/self-binding-replacement/spec.md` (rev 3)

## What was asked and answered `[OWNER 2026-08-15]`

1. **Spec approved.** Entry: bounded Item-8 stocktake research + a measurement spike to
   re-establish the pending `[HARD]` rows, then `design` → `design_review` → `plan` →
   `implement` → `audit`. Run as a single item, not an epic.
2. **Reserved gates: none.** The owner reserved no decisions. Every call below the spec is the
   orchestrator's to make and record — including editing the customer fusion-tea model, whether
   the modelling rule is promoted to ADR-010, and branch/PR sequencing.
3. **Detection scope: confirm what ships already refuses.** The success criterion is discharged by
   evidence that the shipped codegen route and the agentic-mbse validation path both refuse the
   self-named form. No new detector, lint, or authoring-time check is built. This closes the spec's
   "shipped codegen and agentic-mbse validation paths are confirmed to refuse it" criterion as a
   *confirmation* obligation.

## Orchestrator-declared boundary (not owner-stated)

`[AGENT] 2026-08-15` **No `git push` and no PR is opened by any stage in this run.** Commits land
locally in each affected repo. Pushing is outward-facing and reversible only awkwardly; the owner
reserved no gate, so this is the orchestrator's own conservatism, recorded so a later reader knows
it was a choice and not an oversight. `close` and the post-close `pre_pr` branch gate are left to
the human per `/_my_orchestrate`.

## Intent the orchestrator is steering every stage toward

The deliverable is **not** "fusion-tea generates." It is: the situational binding rule is *known*
(measured on the shipped route, not asserted from spec text or the reverted branches), *documented*
where both humans and agents read it, *applied* to the models, and the wrong form is *confirmed
refused* before generation. Generation and seal are necessary evidence, not the goal. The spine is
the mutation check — an off-default mutation of a migrated design attribute reaches every and only
its bound consumers (`P-001`, epic `[OWNER]` mission invariant).

## Provenance the stages must respect

- The spec's `[NEED]` rows are owner-originated; the 2026-08-15 restatement is owner-verbatim.
- D-5/D-6/D-7 are `[AGENT] (ratified by owner, 2026-08-05)` — challengeable on evidence by
  re-deriving against their recorded reasoning, not reopened casually.
- The `SI_OCCURRENCE_AMBIGUOUS` `[HARD]` row is marked *measurement pending re-establishment*. It is
  not a fact until the spike reproduces it. Design must not build on it beforehand.
- The `[INFERRED]` "file, don't fix, a newly discovered silent form" row is agent-grade. If evidence
  warrants a different call, surface it — do not silently expand into generator work.
- Anything this orchestrator decides is `[AGENT]`, and stages are told so explicitly. None of it is
  owner intent.
