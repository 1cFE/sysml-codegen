# Move B — Purge `.project`

Checklist for REPO-CLEANUP Move B (`.project/backlog/epic_repo_cleanup.md`). Owner ruling
`[OWNER, 2026-08-23]`: `completed/` leaves HEAD wholesale; git history is the recoverable copy
(pre-purge SHA recorded in the deletion commit).

- [x] `.gitignore` the log family (`.project/**/*.log`, `*.console`, `*.err`, `*full-suite.txt`)
- [x] F1 pre-check: every path cited by `.project/product/*` and `.project/adr/*` into doomed
      dirs is re-pointed (git-history citation) or the wholesale ruling is recorded in the
      citing entry; line-number citations converted to anchor text
- [x] Delete `.project/completed/` wholesale (pre-purge SHA in commit message)
- [x] Delete closed `active/` dirs and stray top-level exhaust; move
      `decision-harvest/{execution-history.md,spine/}` to `research/`; keep
      `elaborator-downstream`, `move-a-entries`, `project-purge`
- [x] Delete `reports/`, `diagrams/`, `specs/`, `logs/` (only research/ cited them; research is historical) unless cited by a register (grep first)
- [x] Fix every `.project` citation from `src/`, `tests/`, `docs/` (missing 27 + all
      completed/-targets): re-point to surviving paths or git-history form, or drop
- [x] Record close = registers + delete-from-active as the standing rule in `.project/README.md`
- [x] Post-purge gates: zero broken `.project` citations (sweep); zero committed logs; zero
      byte-exact duplicates >2KB (hash sweep); `.project/` under 100k lines;
      `ledger-4a.json` loads through its consumers — all verified 2026-08-23: 0 logs, 0 dups >2KB, 62,282 tracked lines, ledger loads (4 top-level keys), all register citations resolve
- [x] Licensed runnable suite: 2,342 passed, 9 policy skips, 94 execution-marker deselected — identical to the Move A gate; the 1 failure and omitted files are the accepted `STOP_PARSER_ARTIFACT_SOURCE_INPUTS` missing-manifest limitation

## Accepted residue (recorded, not broken)

Dead-path strings that survive on purpose — each lives in bytes that must stay frozen or in
data that is itself the record:

- Fixture `.sysml` doc-comments (costed_cart_d5, expr_compile_d5, solar_battery_*,
  constraint_name_collision_*): model bytes are hash-guarded (P_seed / current-source guard);
  a comment edit is a fixture transition. Left as historical references.
- `tests/unit/data/item8-snapshot-inventory-{pre,final}.json`,
  `tests/expectations/gated_manifest/catf_mfe_gated.json`: data values; the item8 pair is
  replaced by digests in Move C.
- `tests/conformance/test_probe_fixture_lock.py` NON_FIXTURE_ROWS: lock row paths, data pinned
  by the lock; the five probe files are kept at `.project/active/stop-reinventing-the-parser/probes/`
  until Move C's `verification/` retirement takes the lock suite with them.
- `.project/active/type-indexing/probe/` is kept: `tests/unit/test_type_indexing_helpers.py`
  loads its model to exercise the legacy `most_specific` lane, and that lane plus its pinning
  tests retire together in Move C (owner ruling). `scripts/capture_v6_batch.py` re-pointed to
  the relocated corpus ledger.
- `tests/conformance/test_stop_parser_documentation_contract.py:314` asserts CURRENT_WORK.md
  still names the archived stop-parser folder; CURRENT_WORK keeps the historical string.
- `tests/unit/test_check_ledger_4a.py:626/641`: `.project/research/whatever.md` is synthetic
  test data, not a citation.

## Relocations

- `diff-ledger.md` → `.project/reference/elaborator-breadth-diff-ledger.md` (read at runtime by
  two tests); spike models → `tests/fixtures/source_identity_binding_forms/` (read by the
  elaboration contract matrix, cell src-03).
- Harvest record → `.project/research/decision-harvest/{execution-history.md,spine/}`.
