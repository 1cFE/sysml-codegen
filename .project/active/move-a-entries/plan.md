# Move A — Write the Entries

Checklist for REPO-CLEANUP Move A (`.project/backlog/epic_repo_cleanup.md`). No spec/design/audit;
this checklist, the commits, and a green licensed suite are the record.

- [x] ADR: H-124 — derive occurrences from exact parser evidence or refuse by name
- [x] ADR: H-108/110/111 — exact-identity elaboration replaces string resolution, no compat
- [x] ADR: H-090 — lifecycle owner rulings (no late-fill; direct literal actuals; catalog authority)
- [x] ADR: H-078 — agentic-mbse owns neutral facts, codegen owns rendering
- [x] ADR: H-125 — cross-repo merges use explicit merge commits
- [x] Re-home ADR-007 (Compute Once) to `.project/adr/`; reduce §7 to a pointer
- [x] Re-home ADR-009 (Coverage Truth) to `.project/adr/`; reduce §9 to a pointer; update
      product `0001`'s two ADR-009 references (destination-only edit, D6 `[OWNER, 2026-08-21]`)
- [x] Promise: H-112/113 — full satisfaction requires full assessment (closes the gap H-112 recorded)
- [x] Promise: H-089 — sealed package identity verifiable on load (checked: not covered by 0001–0004)
- [x] `adr.sh index` and `product.sh index` regenerate cleanly
- [x] `product.sh check` new entries with git ref
- [x] No new entry cites `.project/completed/`, closed `active/`, or `reports/` (grep sweep)
- [x] Register conformance tests green — 48/51; the 3 failures are the pre-existing `STOP_PARSER_ARTIFACT_SOURCE_INPUTS` manifest entanglement (`[ARTIFACT-MANIFEST-TESTS-HARD-FAIL]`), not register content
- [x] Licensed runnable suite: 2,342 passed, 9 policy skips, 94 `execution`-marker deselected (project default), 10 manifest-dependent files omitted; 1 remaining failure (`tests/unit/test_check_proof_integrity.py`) is the same `STOP_PARSER_ARTIFACT_SOURCE_INPUTS` raise inside the test body — the accepted missing-manifest limitation, not Move A breakage. Folder left in `active/`; Move B sweeps it.
