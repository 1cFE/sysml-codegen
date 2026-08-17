# Brief — stage `design_review`

Fresh session, deliberately. You did not write this design and you are not here to ratify it.

## Subject

`.project/active/self-binding-replacement/design.md`

## Context to read

1. `.project/active/self-binding-replacement/spec.md` (rev 3, amended 2026-08-15 after measurement)
2. `.project/active/self-binding-replacement/spike/findings.md` — **the measured authority** for
   what each binding shape does on the shipped route
3. `.project/active/self-binding-replacement/briefs/03-spike-dispositions.md` — four findings
   already dispositioned `[AGENT]` by the orchestrator
4. `.project/active/self-binding-replacement/briefs/00-align.md` — the owner checkpoint
5. `.project/active/self-binding-replacement/briefs/04-design.md` — what design was told

## Where to push hardest

The orchestrator's own read of the risk, offered so you spend effort well — not to steer your
verdict. Disagree freely.

1. **Does the design actually serve the intent, or just the checklist?** The intent is that the
   situational rule is known, documented where humans and agents read it, applied, and the wrong
   form confirmed refused. The spine is the mutation check — an off-default mutation reaching
   **every and only** its bound consumers. A design that generates cleanly and teaches nothing an
   agent will read has failed while ticking boxes.

2. **The one-authoritative-copy call rests on a claimed inventory.** Design says the
   agent-instruction surface is a single file across 5 agents, 15 commands and 10 skills, measured
   through a hardlinked install rather than the companion checkouts (which were unreadable from its
   sandbox). If that inventory is wrong or partial, the rollout decision is wrong. Probe the method,
   not just the conclusion — and note that `.claude/` and `claude/` diverge (23 vs 37 files) and
   codegen's symlinks resolve into the main agentic checkout.

3. **Fixture-provenance validation instead of a parser.** The spec's `[INFERRED]` requirement is
   that guidance examples are parser-validated before publication, precisely because the published
   guidance today teaches four examples the shipped route refuses. Does provenance-by-fixture
   genuinely discharge that, or does it let a doc example drift from its fixture later? If it can
   drift, say what closes the gap.

4. **F-3's containment claim.** Design says the fix is a re-raise at `elaborate.py:631` plus naming
   cycle participants, no graph restructuring. If that is optimistic, the disposition says file it
   instead of growing the item. Test the claim.

5. **The R-2 / `hif_driver_instance` reasoning.** Design leaves the pin alone on the argument that
   the pin's subject is the codegen fixture, which still declares the instance and is untouched.
   That is a clean argument if true. Check that the migration really does not disturb what the pin
   measures.

6. **The undersized site list.** Design surfaced that D-5 renames the formal too, so three
   `models/library/analyses/` files join the three design files. Confirm the corrected list is
   complete, and that the bounded-diff check would actually catch an arithmetic or physical-value
   change hiding among renames.

## Bounds

- Review only. Change no code, no model, no guidance.
- Do not relitigate the four dispositions in brief 03 or the ratified D-4..D-7 semantics. If you
  think a disposition is *wrong on evidence*, say so as a finding with the evidence — that is
  allowed and wanted — but do not simply re-argue it.
- Grade findings must-fix / should-fix / observation. Be specific enough to act on: file and line.

## Output

A review artifact with a clear verdict per `/_my_design_review`. End with `ARTIFACT: <path>`.
