# Brief — Phase 3 implement: make Codegen accept only closed evidence

You are executing **Phase 3 only** of an approved implementation plan. Phases 1-2 are complete,
audited, and closed — do not reopen them. Phase 2 sealed the Agentic evidence contract
(`semantic-evidence/v2`, Agentic `0.1.3`) on branch `stop-parser-evidence-r2` at **`68bca37`**;
its audit confirmed no carried findings. Read in order:

1. `.project/active/stop-reinventing-the-parser/plan.md` — **Revision 3**, your contract. Execute
   "Phase 3: Make Codegen accept only closed evidence" exactly, including the Global Execution
   Contract. The Phase 1 completion section records the 15 Codegen red nodes; the Phase 2
   completion section records what Agentic now provides.
2. `design.md` — **Revision 7** — sections the phase links, especially
   `#d7-one-codegen-conversion-boundary`,
   `#binding-and-deep-path-values-are-valid-by-construction`, `#scoped-strict-type-boundary`,
   `#checked-consumer-and-ownership-manifests`, `#d8-diagnostic-ownership`,
   `#codegen-pin-and-dependency-contract`.
3. `run-records/phase1-audit.md` — Minors 6, 7, 8 and Informational 12 are **assigned to this
   phase** (details below).
4. `run-records/phase2-audit.md` — the contract you consume, as independently verified; note its
   m2 residual (import-keyed scope) and i8/i11 context.
5. `run-records/entry-status.md` — run scaffolding.

Provenance: plan rev 3 and design rev 7 are the binding contracts. This brief's operational notes
are orchestrator [AGENT] material; on conflict the plan/design win — surface the conflict, never
resolve it silently.

## The intent you serve

A reference the toolchain cannot honor must be refused by name before a graph, snapshot, package,
or output mutation escapes — never silently rewritten. Phase 3 makes weak evidence
unrepresentable at Codegen's boundary: one pre-graph inventory feeds every consumer, closed
binding variants replace the optional semantic path, one total relationship-path factory replaces
the filtering deep path, and the raw walks are deleted. D1-D4 stay byte-identical.

**The green contract is exact.** The Phase-1 red tests (15 nodes at `d257ef1`, listed in
plan.md) assert exact fields: `code == "SI_INDEXED_SOURCE_UNSUPPORTED"`,
`reference == "cells#(2).mass"`, `source_file == "root-0/model.sysml"`, `source_line == 15`,
refusal before consumers/occurrence resolution, no graph, no snapshot bytes, and no absolute or
staged path in the rendered message — across all three public arms (live/admitted/capture),
strict and lenient. The current `SI_INDEXED_SOURCE_UNSUPPORTED` shape (`reference=None`, absolute
path in `detail`) is deliberately rejected by those tests. Turn them green by satisfying them,
never by editing them. Known and intended: the plural case's lenient arm delivers a
diagnostics-carrying graph today (surfaced item 3 / audit Minor 9); a design amendment before
Phase 4 records that row — your tests already pin both arms, do not re-litigate.

## Where you work [AGENT]

- Codegen worktree: `/tmp/stop-parser-rev2/worktrees/sysml-codegen` (branch `stop-parser-impl-r2`
  at `d257ef1`, verified clean). ALL implementation commits go here.
- Agentic worktree `/tmp/stop-parser-rev2/worktrees/agentic-mbse` at `68bca37`: **read-only** —
  this is your upstream. Build the Agentic `0.1.3` wheel/archive from that commit into a
  directory under `/tmp/stop-parser-rev2/` if the dependency contract needs an installable
  artifact; commit nothing there. How the pin is expressed (`_upstream_pins.py`, `pyproject.toml`,
  `uv.lock`) follows `design.md#codegen-pin-and-dependency-contract` — if the design's mechanism
  cannot be satisfied from a local build, surface it rather than inventing a substitute.
- Docs checkout: `/home/reid/1cfe/sysml-codegen`. Only the plan.md "Phase 3 completion" section
  update is committed here, as your final act. Never run implementation commands from it.
- Touch NOTHING else — no user checkout, no `/tmp/stop-parser.QVJIIP/*` (read-forbidden), no
  stash/reset/switch anywhere. Re-verify the worktree is clean at `d257ef1` before starting.

## Hard constraints (from plan rev 3 — binding)

- **Tests first.** Turn the Phase-1 consumer and ownership tables into focused tests; add
  constructor/exhaustiveness, inventory-missing/duplicate, per-consumer inventory-bypass, and
  deep-path totality tests before production edits.
- **`occurrence.py` untouched:** `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py`
  must be empty at phase end; rerun the focused D1-D4 tests.
- **No compatibility surface:** no wrapper, deprecated alias, manifest exemption, optional
  semantic path, or second resolution mode for any deleted weak surface. A production consumer
  that still needs a raw expression is a **design conflict: STOP** and report.
- **Scoped strict gate:** `uv run --extra dev mypy --strict
  src/sysml_codegen/extraction/binding_source.py
  src/sysml_codegen/elaboration/expression_evidence.py` must return zero.
- **Dependency contract:** pin Agentic `0.1.3` / `semantic-evidence/v2`; bump Codegen to `0.1.1`;
  update `_upstream_pins.py`, `pyproject.toml`, version tests, `uv.lock` per the design.
- **`deep_cross_scope_probe` never restores its captured graph** — global stop condition.
- **[OWNER-VERBATIM, 2026-08-17]** "do not rerun the PDF suite anymore" — the Agentic slow
  PDF/HTML corpus and 15 paid/network cases stay unrun.
- Baseline discipline: repo-wide mypy is a comparison against `C_base` (30 errors in 8 files);
  targeted Ruff on every changed file; no item-caused diagnostic; never call a nonzero baseline
  green.
- Validation includes: exact resolver rejects an indexed use, legacy fact, IR node, and
  duck-typed lookalike at runtime; strict and lenient live/admitted produce the same public
  refusal with no graph/snapshot for the focused failure set; the sealed from-snapshot route
  cannot import or call the raw site enumerator or reference inspector.

## Audit findings assigned to this phase (close them; cite closure in the phase record)

- **Phase-1 Minor 6:** all four `REVIEWED_ROWS` in
  `tests/conformance/test_expression_evidence_ownership.py` name closure-proof tests that did not
  exist. Your work creates those tests; when they land, make
  `test_every_reviewed_row_names_a_closure_proof` resolve each named proof to a real test (the
  sibling consumer-table check at `test_every_named_proof_in_the_consumer_table_resolves` is the
  model), not just non-empty strings.
- **Phase-1 Minor 7:** off-route reachability is proved by direct imports only (`_imports_of`
  parses one file). Make it transitive from the public roots — required before Phase 4's closure
  gate, and the ownership file is yours this phase.
- **Phase-1 Minor 8:** `tests/conformance/test_probe_fixture_lock.py:140-158` leg-3
  ledger-ownership check substring-matches the whole ledger file. Parse the row for the path and
  check both hashes within that row.
- **Phase-1 Informational 12:** the lock's row classifier counts
  `verification/fixture-manifest.json` as a fixture input via the
  `or path.startswith("verification/")` clause, which would absorb a future verification-code row
  into the wrong class. Tighten the classification so fixture inputs and verification-code rows
  are decided structurally, without changing what the lock covers.

## Environment notes [AGENT]

- SysIDE license: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` before licensed
  tests. Never copy `.env`, its value, or any secret anywhere.
- Codegen commands: `uv run --extra dev …` from the worktree.
- **The default Codegen suite only fully runs from a declared extraction** (pre-existing at
  `C_base`): from a plain worktree, 6 modules fail collection and 10 further tests fail with
  `ArtifactSourceInputError`. For authoritative full-suite numbers, build a fresh extraction
  under `/tmp/stop-parser-rev2/` (`git archive` + `git bundle`, with the artifact-source
  manifest) the way Phases 1-2 did — see plan.md Phase 1 deviations 1-2. Focused suites run fine
  from the worktree.
- `verification/capture_baseline.py` imports its artifact-source manifest — leg-2 style
  validation also runs from the extraction, not the worktree.
- Do not install or update unrelated dependencies.

## Deliverables

1. Commits on `stop-parser-impl-r2`: tests-first commit(s), then implementation, in reviewable
   units.
2. Every Phase 3 validation box executed with commands and results recorded — including which of
   the 15 Phase-1 red nodes are green (all representation/selector nodes must be; any node whose
   green is deferred to Phase 4 must be named with the plan text that defers it), the runtime
   rejection proofs, the sealed-route import proof, D1-D4 rerun, and the extraction-based full
   suite.
3. plan.md "Phase 3 completion" section filled (completed date, commit SHAs, actual changes and
   test results, issues/deviations, rollback point) and committed in the docs checkout.
4. Final message: prose summary — boundary built, red-to-green account, deletions, gates,
   deviations — ending with
   `ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`. If any stop rule tripped, say
   so plainly at the top and stop.

Phase 3 is the end of your scope. Do not begin Phase 4 work (registry, full route matrix,
ledger rows A5a/A5b, documentation sweep) of any kind.
