# Stage brief — Phase 4, Gate 4C part 1: The fourteen pending exact-route specimens

**You are executing one bounded piece** of the recovery plan's Gate 4C:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: the approved ledger (`ledger-4a.md` — the sixteen responsibility-module rows and
their PENDING-4C proof nodes; `ledger-4a.json` for the machine rows), the plan's Gate 4C, the
3E responsibility rows in the plan notes, and the G0/G1 completion notes.

## Intent

Fourteen responsibility rows name behaviors whose only current test drives the LEGACY route via
`tests/helpers/legacy_route.py`. Each needs an exact-route specimen — a kept public-behavior
test proving the responsibility on the shipped route — before G2/G3 may delete the legacy
owners. This stage authors those specimens. It deletes nothing and repoints nothing.

The known lost-responsibility list in plan Gate 4C is the checklist these rows descend from:
real constraint verdict execution, customer E2E, full generated-package structure and schemas,
live-vs-snapshot byte identity where still required, Gate-B missing-input reconciliation,
smart-regeneration preservation (already re-proven in G1 — cite, don't reauthor),
shared-producer/D39 behavior, literal-bearing aggregation (discharged in 3B — cite).

## Ground rules for each specimen

1. **Public behavior on the exact route.** Generate/execute through the public surface
   (`run_codegen`, the v6 snapshot route, the real-TEAx lane where the responsibility is
   execution-shaped). No legacy imports, no `legacy_route.py`, no stubs.
2. **The fixture problem is the real work.** Many legacy specimens used models the exact route
   refuses (self-binding). Where the row names a needed fixture shape, author a NEW minimal
   fixture that elaborates on the exact route and carries the responsibility's trigger
   (e.g. a D-5-renamed variant authored fresh, or a purpose-built model). Never modify the 37
   ratified corpus fixtures — new fixtures live beside them and join no ledger. Follow
   sysml-conventions (load the skill if writing SysML).
3. **Independently derived expectations** — hand arithmetic, model-derived values, exact
   vocabularies. The 3A–3E audit bar applies unchanged.
4. **Each specimen closes its row:** update `ledger-4a.json`'s `replacement_proof_node` from
   `PENDING-4C: …` to the real node id; `scripts/check_ledger_4a.py replacements` must go
   14-pending → 0-pending (all green) by the end, or the remainder are listed with exactly why
   (an unsatisfiable one is a rule-10 stop — surface it, don't fake it).
5. If a responsibility turns out to be ALREADY covered by a Phase 3 test, cite that node in the
   row instead of duplicating it — with a one-line justification the auditor can check.

## Requirements

- Declared path set first: new test modules, new fixtures, ledger JSON, plan. Nothing else.
- Battery before commit: full licensed suite (delta = exactly the new specimens, all green,
  every node named); execution lane if any specimen lives there (state the command); corpus
  15/22 unchanged; ruff/mypy measured; `git diff --check`; checker paths 0 problems,
  replacements 0 pending (or the surfaced remainder).
- One commit + OID record; plan Gate 4C notes updated with a row→specimen table.

## Report back

The row→specimen table (14 rows: responsibility, fixture authored or cited, node id, green
proof), any rule-10 surfacing, battery numbers, commit OIDs. `ARTIFACT:` the updated plan.
