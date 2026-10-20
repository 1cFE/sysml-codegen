Second-round design review for EXEC-SUBSET-CONTRACT Item 2b, live half. Read `design.md` (revised), your round-1 `design-review.md` (its Resolutions section is filled in), `briefs/design_fix_r1.md` (orchestrator rulings), `product-lens.md`.

The readiness rule D8 is parked with the owner (RG-2 and the epic's omission/exclusion decision); do not review its substance. Do check that it is truly isolated: whichever way the owner rules (READY with omission counts; or "builds, not ready" for the unbound String-default case using a fact from the prepared graph; or a generator change under RG-2 that removes the case), nothing outside `readiness(report)`, its tests and the readiness line has to change.

Confirm whether each round-1 must-fix and should-fix point is resolved. Pay particular attention to minor point m1, which was applied in a stronger form: the writers' repeated constraint-name checks and parameter-field check are dropped because `prepare` runs them first. Confirm that this cannot change what `generate` accepts or refuses (RG-1) — for example, that no path reaches `emit_package` without a `Prepared` from `prepare`, including tests and the snapshot route.

Flag anything new only if it would make the plan build the wrong thing. Append a "Round 2" section to `design-review.md` with the verdict.
