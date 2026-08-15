# Stage brief — Phase 4, Gate 4C part 7 final: dual re-check + the last 35 dispositions

**You are completing Gate 4C** of the recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: the part-7 chunk 11–15 records (especially chunk 12's dual finding and probe
method), the runbook's "four things that must be true" list, the checker `groups` output, and
the 35 blocked files' row analyses. Environment/battery discipline as recorded.

## Piece 1 — the eight duals, re-checked by measurement (chunk 12's method)

The Gate 4A note calls all eight retained 3C duals "one behavior under two names, qualifier
drop at retirement." Chunk 12 proved that false for three. For the five unrechecked (the
expression-compiler trio is done; cover the remaining five including the two agentic-mbse
duals L-036/L-037 — run those in the paired worktree):

- Probe each pair the chunk-12 way: rebind the legacy name to the exact implementation exactly
  as the prescribed rename would, run the consumers, measure. Same-shape → the rename premise
  holds, record it verified. Different-shape → write the real two-step migration on the row
  (what the consumers actually need: adapters ruled out — the plan bans shims; consumers
  migrate to the exact shape, with node accounting), and mark the affected retirement step
  entry accordingly.
- Rows whose premise fails get their retirement-runbook entries rewritten from "rename" to the
  measured migration, sized honestly. If any migration is large enough to be its own gate,
  say so with the measurement — do not start it silently.

## Piece 2 — the final 35 dispositions (27 G2′ ∪ 25 v5-family)

Same standard as chunks 1–15: per-file, real subjects, import-localization first, variants only
where a needed refused fixture demands one (D-5 recipe now covers constraint defs), no
thinning. Special attention:
- Files whose subject is genuinely "the v5 format/route itself" (loaders, format tests) may
  carry disposition retire-with-owner with the typed-refusal pins (L-180's four nodes) named
  as the surviving subject — that is not thinning, it is the subject ending.
- The proof-integrity cross-check must stay at 0 over the full deletion order after every
  chunk.

## End state (the real one this time — verify, then claim)

`groups`: every group READY except those blocked solely by the acceptance gate; zero files
without dispositions. `replacements` all green; proof integrity 0; runbook's "four things"
list resolved or explicitly owner-gated; the runbook headline states the exact post-acceptance
sequence with per-step row lists and the dual-migration entries as measured.

## Rules

Batteries per commit as established. Nothing deletes. Rule-10 stops as established. Honest
remainder if budget ends.

## Report back

Dual verdicts (5 rows: premise held / failed with measured migration), disposition accounting
for the 35, end-state checker proof, runbook state, OIDs. `ARTIFACT:` the updated plan.
