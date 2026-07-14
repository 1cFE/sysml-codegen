# Brief: Item 14 design review — Migration, Docs, and IFE Acceptance

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not write this design; review it skeptically. This item closes the epic — its acceptance IS the epic's Critical Success Factor.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- An Item 13 implement session may be committing — write ONLY design-review.md; touch no code.
- Artifact: `design-review.md` in `.project/active/constraint-migration-acceptance/`.

## Review target
`.project/active/constraint-migration-acceptance/design.md` (spec, briefs, and `.project/reference/fusion-tea-ife-sweep/FACTS.md` beside it).

## What to probe hardest
1. **The surfaced premise conflict (D1).** The concept's Migration invariant says "every constraint in today's drop manifest maps to exactly one SOURCE RECORD... and every source record expands to one or more concrete entries." The design reinterprets to per-usage concrete/unassessed records. Read the actual catalog code (generation/constraint_catalog.py, resolution/models.py): is the design's reading of what source records CAN carry correct (per-definition only, can't carry inline)? Check Item 7's landed catalog: does it have per-USAGE source records (the concept's `[AGENT]` note in "Neutral Constraint Facts" said source records are per asserted/applied USAGE)? If the catalog already has per-usage source records, the design's reinterpretation may be unnecessary — adjudicate with code evidence. This decides whether the epic's migration invariant is met as written or as amended.
2. **D2 gain fix.** The instance-self-redefinition tier: walk supplied_values.py's three tiers and the hif_plant model — is the miss diagnosis right, is the fix demand-scoped (R2's exactly-two-snapshots claim), and does it interact with Item 8's occurrence transcripts?
3. **D3 no-version-bump**: removing manifest fields from snapshots without a bump — verify the loader genuinely tolerates absence (which loader path reads manifest fields?) and that this doesn't violate Item 8's three-key gate discipline.
4. **D4/D5 acceptance**: replay-both-then-delete — is the comparison run through the REAL study layer (teax CLI/API over the sealed package) as the epic demands, not a shortcut harness? The boundary-row handling (B3): surfaced as data, decision rule stated?
5. **Workstream sequencing/repo split**: any hidden cross-repo ordering hazard (docs referencing behavior that lands later; the grandfather re-landing vs manifest retirement order)?

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code — do not take the design's word.
