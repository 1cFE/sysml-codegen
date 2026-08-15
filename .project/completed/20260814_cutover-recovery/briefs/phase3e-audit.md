# Stage brief — Independent audit of Slice 3E (public authority switch)

Fresh, independent auditor; you did not implement this. Audit codegen commit `430e26a`
(+ OID record `885c2b1`) on `item7-rebuild` at `/home/reid/1cfe/sysml-codegen-item7-rebuild`
(agentic-mbse claimed unchanged at `cc6c7a7` — verify). Contract: plan Slice 3E + per-slice
validation + rules, the five orchestrator rulings recorded in the plan's 3E notes, and
`evidence/audit-3{a,b,c,d}.md`. This is the last Phase 3 audit; Phase 4 deletion planning
consumes what you certify. Run everything yourself; full permissions.

Environment: venv `/home/reid/1cfe/item7-rebuild-venv` (re-assert all three import paths — F2);
old-commit comparisons force PYTHONPATH + assert `__file__`; license `set -a; source
/home/reid/1cfe/agentic-mbse/.env; set +a`, proof = zero license-skip lines. Scratch
`/tmp/claude-audit3e/`. Write only `.project/active/cutover-recovery/evidence/audit-3e.md`;
no commits.

## Verify (minimum; add your own judgment)

1. **Single authority, by behavior.** Re-run the discriminating cases yourself: `d38_caret` CLI
   package is the exact one; `chain_spike_model` refused publicly (typed) while the legacy
   internals still generate it; a v5 snapshot gets the typed v6 refusal (not a stack trace, not
   silent fallback); `--design-path-filter` refuses rather than no-ops. Then hunt for an escape
   hatch the pins missed: env vars, config fields, entry points, subcommands, or import-time
   side channels that could still reach legacy construction from a public surface. The pinned
   transitive-closure residual (v5 re-exports via `snapshot/__init__`) is accepted — anything
   beyond it is a finding.
2. **The 116-node reclassification is honest.** Zero deleted/silenced/deselected/xfailed —
   verify by node-id diff against `0a812af`, not by trusting counts. Spot-check 10+ repointed
   modules: each has a responsibility row; the row names a real Gate 4C owner; the repointed
   test still exercises the behavior it claims (not reduced to a smoke call). Verify the Gate 4B
   blocking language landed in the plan (no legacy deletion while a row lacks its replacement).
3. **Package-diff classification.** Re-run the 14-fixture tree diff; confirm zero unexplained
   differences and that the five mechanisms genuinely cover every hunk (sample adversarially —
   pick the diffs the notes discuss least). Confirm fusion_tea: module/schema names equal, no
   group renamed, hand values unchanged, and the per-consumer-mint collapse is exactly the
   ratified single-source semantics (one key per modelled attribute, both consumers wired to
   it) — check C25/C2 wiring in the emitted YAML, not just the JSON keys.
4. **The new fixture and specimens.** The committed v6 fusion_tea snapshot: verify it loads,
   relocates, and drives the oracle at the hand values; README marks it not-the-accepted-batch.
   The two fail-before-mutate specimens: confirm they reach the guard on the exact route
   through public generate (break the guard experimentally — the tests must fail), and that the
   forged-identity retirement is a measurement, not an argument.
5. **After-battery re-run:** corpus (15/22, zero rows moved, exact multisets); full licensed
   suite 3557/47/38 with delta = exactly the 18 new nodes (node-id diff); execution lane 38
   incl. real TEAx at the anchor values through the switched surface; ruff byte-identical; mypy
   71/17 measured; `git diff --check`; declared paths; agentic untouched.
6. **`unresolvable_attr_probe` ledger row 36:** reproduce the collision-guard refusal;
   confirm the corpus row genuinely didn't move and the recorded classification is accurate.
7. **Checklist reconciliation:** spot-check the 3A–3D evidence pointers, including the honest
   non-tick for 3D's mypy gate.

## Verdict

CERTIFY / FINDINGS (numbered, severity, file:line, resolution) / BLOCK. Phase 4 planning starts
from your record — state explicitly what you did not verify.
`ARTIFACT: .project/active/cutover-recovery/evidence/audit-3e.md`
