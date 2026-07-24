# Spec Brief — Lifecycle Item 2: Shared Producer Resolution and Gate A

**Stage:** spec
**Epic authority:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` Item 2
(register row 2); ratified contract
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` (D-1/D-2,
invariants 19–26); requirements spec
`.project/active/constraint-execution-lifecycle-contract/spec.md` (LC-A–LC-I).

## Intent (provenance marked)

- [INHERITED: ratified contract] Three drifted resolver ladders (calculation, constraint,
  aggregation) leave too many places for the same meaning to drift. Replace them with ONE typed
  resolution request/result and one ordered positive ladder: real producer channel, then real
  design attribute under exact qualified identity.
- [INHERITED: owner decisions D-1/D-2] Every model-derived consumed value has a real graph
  producer; direct literal design attributes resolve through shared exact-QN machinery — no
  passthrough calculations, no public late fill, no post-build mutation.
- Strict/lenient differences survive ONLY at terminal miss; constraints never use a calculation
  fallback or invented value; lenient calc behavior never becomes ambiguous first-pick or
  leaf-name guess.
- Gate A shape is the driving acceptance: usage-owned attribute on a concrete `PartUsage`,
  self-named actual, public live and relocated routes.
- [OWNER, 2026-07-19] No numeric LOC gates (epic amendment, commit `a1435e1`). The deletion
  mandate is qualitative and binding: the three consumer-specific ladders and their obsolete
  string surgery are deleted, not shimmed.

## Constraints from landed Item 1 (certified at `287afc4`)

Item 2 builds ON the Item 1 seams, it does not rework them: `prepare_constraint_usages` /
`PreparedConstraintBatch` (constraint_lowering.py), `resolve_logical_demand` /
`select_group_source` / `enrich_graph_design_attributes` (supplied_values.py). Item 1's
recorded deviations (evidence §6) are facts on the ground — notably `ResolvedDemand` has four
fields and provenance selection is call-site policy. Item 1's public acceptance file and
fixtures are frozen controls; do not modify them.

## Required reading beyond the epic

- `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md` — the R-findings
  that motivated this item.
- `BACKLOG.md` row `[CONSTRAINT-ARCH-UNIFY]` — absorbed by this item; its scope notes name the
  parallel ladders / triple walker.
- Item 1's `evidence.md` §6 deviations and `audit.md` residual items (the tier-2 disposition
  asymmetry is Item 4 territory — do not absorb it).

## Out of scope (firewall)

Public late fill, placeholder completion, post-build graph/default mutation; general typed-path
or part-index refactors not required to unify the resolver; Item 3's Gate B; Item 4's
diagnostics; Item 5's relocated whole-tree proof (Item 2's relocated Gate A leg uses the
same-checkout replay route as regression only, labeled non-certifying, if full relocation is
not yet available).

## Spec shape

Provenance-graded requirements (LC mapping), mandatory acceptance cases with exact
fixture/owner/route coordinates, RED-first public surface (like Item 1's OD-A11 discipline),
and named deletion targets. Keep it lean — Item 1's spec is the register-row template; do not
exceed its rigor where the contract already settles a question.
