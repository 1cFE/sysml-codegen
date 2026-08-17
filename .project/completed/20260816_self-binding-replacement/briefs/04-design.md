# Brief — stage `design`

Sent by the orchestrator. Everything the orchestrator states here is `[AGENT]` grade unless it
carries an explicit owner stamp. Do not read the orchestrator's operationalization as owner intent.

## Read first, in this order

1. `.project/active/self-binding-replacement/spec.md` — **rev 3 as amended today**. The
   `SI_OCCURRENCE_AMBIGUOUS` `[HARD]` row and the three-shapes section changed after measurement.
2. `.project/active/self-binding-replacement/spike/findings.md` — the measured behavior. **This, not
   specification text and not the reverted patches, is the authority for what each shape does.**
3. `.project/active/self-binding-replacement/briefs/03-spike-dispositions.md` — the four findings
   already dispositioned by the orchestrator. Design them; do not relitigate them.
4. `.project/active/self-binding-replacement/briefs/00-align.md` — the owner checkpoint.
5. `.project/research/20260815-103905_item8-bounded-stocktake.md` — scope context.

## The intent to hold

The deliverable is **not** "fusion-tea generates." It is: the situational rule is known, documented
where humans *and agents* read it, applied to the models, and the wrong form confirmed refused
before generation. The spine is the mutation check — an off-default mutation of a migrated design
attribute reaches **every and only** its bound consumers (`P-001`). Generation and seal are
necessary evidence, not the goal.

## What the design must cover

1. **The guidance rewrite.** Organized *by situation*, teaching D-5 / D-7 / D-6 with the measured
   rule, including F-4's sideways reach. Every example parser-validated before publication — this is
   `[INFERRED]` in the spec and non-negotiable in practice, because the currently published guidance
   teaches four examples the shipped route refuses. Fix those four in
   `agentic-mbse/docs/patterns/plant-idiom.md`, including the EXPOSE example at line 200. Do not
   cite SysML v2 Part 1 §7.17.2 as authority for a shadowing rule; it is an action-parameter
   example and says no such thing.
2. **Agent-surface rollout — the spec's open question, and yours to settle.** Which tracked surfaces
   carry the rule directly and which point to one authoritative copy, given the divergent
   `agentic-mbse/claude/` (37 files, 10 skills) and `agentic-mbse/.claude/` (23 files, 4 skills)
   trees, where `skills/sysml-conventions/SKILL.md` exists only in `claude/`. The Item-7 residual
   A-1 two-copies trap is live: codegen's `.claude/` symlinks resolve into the main agentic
   checkout. The success criterion fixes the outcome — every live surface that can instruct an agent
   about calculation bindings either carries the rule or reaches one authoritative copy, **with no
   contradictory guidance left behind**. Choose the mechanism and record why.
3. **The fusion-tea migration.** 15 sites, D-5, in `/home/reid/1cfe/fusion-tea`
   (`designs/generic_ife/ife_plant.sysml` ×10, `designs/hif_ife/hif_driver.sysml` ×2,
   `designs/hif_ife/hif_plant.sysml` ×3). `scripts/make_d5_variant.py` mechanizes the recipe and its
   proof is a strip check, so a stray reformat cannot hide. Base branch: `item8-fusion-embedded-catalog`
   (6 ahead / 0 behind main, dirty tree — clean or stash first). Design the **mechanical check that
   establishes the bounded diff**: referent changes, arithmetic and physical values do not.
   Account for F-3's collision risk across all 15 renames before running them.
4. **The two repairs** dispositioned in brief 03 — F-2 (agentic-mbse identity comparison) and F-3
   (named diagnostic in place of the traceback). Size F-3 honestly; if it is not contained at the
   boundary, file it with name/owner/vehicle instead and say so.
5. **Verification design.** The spine mutation check; generate + seal + snapshot with zero readiness
   diagnostics; and confirmation that both validation paths refuse the self-named form. Note the
   known `hif_driver_instance` / R-2 question: the certified Slice-3D evidence pins 11 channels
   including two from a workaround the customer repo has deleted, so a workaround-free regeneration
   is expected to differ. **You decide and record** whether this item re-anchors that pin or leaves
   it — the owner reserved no gate. Prefer the smaller call that does not contradict R-2.
6. **Stellarator triage.** One pipeline run at `/home/reid/1cfe/fusion-tea-stellarator-mbse-demo`
   (branch `feat/stellarator-mbse-demo`), record what breaks, file any follow-on. **Fix nothing.**
   The July owner hold is not reversed. Its 114 self-bindings are 15 copied-in fusion-tea files plus
   99 of its own.
7. **ADR-010.** The spec lists this as an owner call with no disposition; the owner reserved **no**
   gates at Align, so it is yours. Decide whether the lasting modelling rule is promoted to an ADR
   (a numbered section of `docs/architecture/modeling-assumptions.md` — there is no `docs/adr/`) and
   record the reasoning either way. Next free id is ADR-010.

## Boundaries

- **No `git push`, no PR.** Local commits only, in every repo.
- Three trees are in play — codegen (here), `agentic-mbse` and `fusion-tea` (both outside this
  sandbox). Name explicitly which change lands in which repo.
- Do not reopen D-4 through D-7. Do not expand into the Item-8 Non-Goals (the July IFE impact audit,
  certification repair, the composed proof thread, the doc-repair list).
- Codegen fixtures that exist to pin the refused shape keep carrying it — they are not migration
  targets.
- If evidence contradicts a premise, **surface it and park the dependent conclusions**. Do not
  resolve it silently.

## Output

`.project/active/self-binding-replacement/design.md` per `/_my_design`. End with `ARTIFACT: <path>`.
