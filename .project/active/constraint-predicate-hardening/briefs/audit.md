# Brief: audit stage — CONSTRAINT-SEMANTICS Item 4 (Predicate Defect Hardening)

Orchestrated run (owner-invoked `/_my_orchestrate`, check-ins waived). You are a FRESH audit
session — you did not implement this. Work synchronously; never pause for background agents.
Your sandbox likely has NO code execution and cannot read the companion worktree: audit
statically from the codegen tree (readable) and the committed evidence, and put every check
that needs execution or companion reads into a **"Requested live probes"** section (exact
command or file:line mutation + the expected discriminating outcome). The orchestrator runs
them and appends an addendum. Do not mark a criterion verified on author-reported numbers
alone — mark it "author-reported" and, where it matters, request the probe.

## Audit target

Item 4 implementation: codegen commits `f3b3131..89fc38f` on `item7-rebuild`, companion
commit `0a52942` in `/home/reid/1cfe/agentic-mbse-item7-rebuild`.

Authority chain: `plan.md` (executed as written?), `design.md` (decisions D1–D8 + invariants
honored?), `spec.md` (every success criterion discharged with evidence?), all under
`.project/active/constraint-predicate-hardening/`, plus `probes/companion-evidence.md`,
`probes/red-evidence.md`, `verification.md`, and `reason-codes-reconciliation.md`.

## Concurrency warning — do not misattribute

A concurrent OWNER session committed to this tree during the run: `4e5bc71` (files epic
Item 7) and the archival of Items 2/3 to `.project/completed/20260813_*`, plus an uncommitted
`CURRENT_WORK.md` edit that may still be in progress. None of that is Item 4 work. Do not
audit it, do not attribute it, do not touch the uncommitted file — but DO check Item 4's
claims still hold in its presence (e.g. the ledger-path repair in deviation 7 was forced by
the Item 3 archival).

## Press hardest on

1. **Red-first integrity.** `probes/red-evidence.md` claims a marker-stripped run of 20
   failed / 6 passed matching the marked split. Is the capture verbatim and complete, does
   every xfail row appear, and did the fix commits remove exactly those markers (no test
   silently weakened between red and green)? Diff the characterization files across the fix
   commits.
2. **D1's blast radius.** The walk-head unwrap fires for every `_expression_references`
   caller. The design bounded the widening (alias/computed lanes already top-level-unwrapped;
   only nested annotations newly reached; invariant 7 pins the user-model-`[`-operand case;
   M7's `SI_EDGE_DANGLING` escape). Verify each bound against the actual diff, not the
   design's prose.
3. **D2 does not widen beyond the named shapes.** Genuine expression sources
   (`a + b`, invocations, chains) still refuse as before; the newly admitted set is exactly
   the design's named set (literal and reference under one annotation). Check the diff of
   `_collect_bound_members` and its tests.
4. **Deviations 1–7** (listed in the implement result / verification.md): each is either
   design-consistent or should have halted. Especially deviation 1 (both operands annotated —
   does the demonstration still prove the spec's "compatible unit-annotated literal" claim?),
   deviation 2 (asserted multi-chain fixture — is the plain-form lane then pinned anywhere,
   per the Item 2 contract that plain+blocked generates?), and deviation 7 (the pre-existing
   collection repair — was anything else swept in with it?).
5. **The B2-false surfacing** (a binding's unit never reaches the profile's ordering check,
   so a mis-united tolerance band is admitted): is it surfaced per the capture-fidelity rule
   — loud, in the artifact, dependent conclusions parked, nothing silently resolved — and
   filed where Item 5 will actually see it?
6. **Companion gates.** `ruff src` = 1 / `mypy src` = 108 / 10 pre-existing suite failures
   have no baseline stated in the spec. Request probes establishing the pre-change baseline
   (same commands at `bc69f04`) rather than accepting "identical set with the change stashed"
   on the author's word.
7. **Message truth.** The rendered diagnostic (worked example in docs §8): does the advertised
   bindings rewrite avoid pointing at any still-refused form, given P3's finding? And does the
   single-line invariant (design invariant 8) hold for every rendered path?
8. **Frozen twins + TEAx untouched**, `git diff --check`, and the spec's Success Criteria
   checklist one by one.

## Deliverable

`.project/active/constraint-predicate-hardening/audit.md` — verdict in the header
(Certify / Certify-with-residuals / Needs-work), findings with severity, the Requested live
probes section, and a criterion-by-criterion table. End with `ARTIFACT: <path>`.
