# Audit Brief — Lifecycle Item 2: Shared Producer Resolution and Gate A

**Stage:** audit (independent; fresh session — the implementing session does not self-certify)
**Candidate:** sysml-codegen `039d66e` (companion pins unchanged: agentic-mbse `515e08bb`,
TEAx `d545701f`).
**Artifacts:** `.project/active/constraint-lifecycle-shared-resolution/{spec,design,design-review,evidence}.md`
(phased plan folded into design; no plan.md by design).

## Ratified context (do not re-litigate the permission, audit the mechanism)

Orchestrator/owner rulings on record: no LOC gates (owner, epic mandate); PC-1 part_usage
branch = extension (design review confirmed); PC-2 order-dependence basis; PC-3/I10 V11 stays
calculation-only (widening is Item 3's); SR-A02 referred to Item 4 (epic commit c685a0a) with
`shared_producer` as the known-incomplete pin; D2-falsified disposition (constraint order,
measured latent exposure); param_group LocalTerm residual out of scope.

## Priorities — the implementer itself flagged 1–3 for your eye

1. **Retired `test_dual_resolution.py` parity classes.** Six classes comparing two
   now-identical code paths were replaced by a single property pin. Tautology is real, but
   verify the replacement pin actually covers the protected property and nothing else those
   classes incidentally guarded is now uncovered. The full-suite count moved 3037 → 3003
   across 5b+6; account for the whole delta — every retired/migrated test named, nothing
   silently dropped.
2. **D2 falsification.** Verify the measurement (44/249 single-conflicting-row exposure, none
   dual) by rerunning it, and that the chosen constraint order cannot change a currently
   resolving binding's outcome (byte identity + EP manifest are the claimed controls — check
   the manifest tool itself is sound: 34 fixtures, 273 EPs, 484 module inputs, 0 diffs).
3. **SR-A02 honesty:** referral recorded in spec/design/evidence/epic consistently; the
   `shared_producer` PROVENANCE pins the exact two-entry-point state; I9 annotated falsified.
4. **Deletion reality:** input_resolver.py gone; four calc ladder methods, AGG_STRATEGIES,
   strategy functions at 0 occurrences; no wrapper/alias/re-export; family3 migration as
   declared; docstrings clean of removed mechanisms.
5. **Gate A end-to-end:** part_usage classification fix; live fixtures for both owner
   branches; satisfied/violated verdicts through real simkit; RED stash-verification claims.
6. **Invariants:** I10 one-writer check; all constraint lookups exact (no guess reachable from
   strict); lenient terminal fork only; forced-difference table complete (five entries, no
   corpus population) — attempt to falsify "no corpus population" by searching for a fixture
   shape that hits one.
7. **Item 1 non-regression:** its acceptance file byte-identical and green; Item 1's certified
   seams extended, not reworked.
8. **Evidence honesty:** claims match outputs; open items (V11 widening → Item 3,
   written-reference carry → Item 4, param_group residual) stated; no unsupported checkbox.

Environment: license via `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; TEAx lane
per Item 1 evidence §3; never format fixtures/baselines; `.claude/projects/` untouchable.

Verdict: Certify / Pass-with-notes / Needs-work with reproduced evidence.
