# Move C — Delete What Defends Nothing

Checklist for REPO-CLEANUP Move C (`.project/backlog/epic_repo_cleanup.md`). Written 2026-08-23
at owner request, before execution. No spec/design/audit; this checklist, the commits, and a
green licensed suite are the record.

**Inventory**: `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md`
§5 (dead `src/` by `file:line`), §6 (deletable weight outside `src/`), §7 (test composition,
false defenders, gating). That document is the coverage inventory; no second one is written.

**Owner rulings already in hand** `[OWNER, 2026-08-23]`: `verification/` retires; the legacy
extraction lane is deleted. Both recorded in the epic.

## Safety rails (checked before every deletion commit)

- **Deletion lock (F2)**: a test named as Authority/Evidence by any `.project/product/*` entry
  is never deleted or weakened without an owner ruling recorded in the citing entry. Cited
  today: `test_usage_owned_reference_anchoring.py`, `test_elaboration_public_mutation.py`
  (`0002`); `test_definition_owned_reference_positions.py`, `test_occurrence_domain_derivation.py`
  (`0003`).
- **Entanglement is not deadness** `[OWNER, 2026-08-21]`: a product test that raises on the
  missing release-evidence manifest is disentangled, never deleted for the raise. Deleting one
  because its *subject* is deleted (e.g. the legacy lane) is allowed `[AGENT] (ratified by
  owner, 2026-08-25)` — check the deletion lock first and say so in the commit.
- **Byte identity**: generated output byte-identical to pre-item for every fixture, licensed.
  Run the timestamp-only diff check first — a full re-capture rewrites every `captured_at`
  (memory: byte-identity captured_at churn).
- Every dead-lane commit demonstrates unreachability from `run_codegen` on both routes
  (importer grep + `vulture`) in the commit message, and deletes the pinning tests in the
  same commit, naming what the test was believed to defend and why that belief was wrong.
- Licensed suite green after each batch; pass/fail counts unchanged except deliberate removals.

## Batches, in commit order

### C1 — Trivially dead trees

- [ ] `scripts/archive/` (8,274 lines; imports modules the cutover deleted, cannot execute)
- [ ] The twelve retired reference docs (3,633 lines): `docs/architecture/reference/`
      03, 04, 05, 07, 10, 11, 12, 13, 17, 24, 25, 28. Doc 09 is mixed — cut its retired half,
      keep the live half. Update `CLAUDE.md`'s "Retired" section to match what remains.

### C2 — `verification/` retirement (owner-ruled)

- [ ] Delete `verification/` (~3,858 lines) and its dedicated test files (~4,900 lines):
      `test_probe_fixture_lock.py`, `test_evidence_artifact_topology.py`,
      `test_artifact_sources.py`, `tests/helpers/artifact_sources.py`, and the
      manifest-bound portions of others found by
      `grep -rlE "from verification|import verification|helpers(\.| import )artifact_sources" tests/`
      (the string-level grep over-matches docstring mentions, including a deletion-locked test)
- [ ] **Split, don't delete, `test_stop_parser_documentation_contract.py`** — it is mixed: its
      manifest-bound legs retire with `verification/`, but it carries the only mechanical guard
      on the owner-verbatim `0003`/`0004` quotes and the register conventions (48 tests passed
      license-free at Move A). Keep those in a renamed register-contract test file.
- [ ] Disentangle the four manifest-raising **product** tests so they run from an ordinary
      checkout — cut the `helpers.artifact_sources` import seam in all four:
      `test_self_binding_guidance_contract.py` (agentic root from the installed
      `agentic_mbse` package), `test_exact_route_fingerprint_stability.py` (history root =
      this repo), and a same-shape cut in `test_hierarchy_resolver.py` (conformance) and
      `test_ast_dispatch_invariant.py` so they stay importable through C2. Their
      subject-driven work is C3's: the hierarchy file was classified 2026-08-25 as
      legacy-subject throughout (all 43 tests) and retires whole in C3 under the ratified
      ruling (epic, Owner Rulings); the dispatch file is mixed and is split in C3.
- [ ] Delete the five kept probe files at `.project/active/stop-reinventing-the-parser/probes/`
      (they existed only for the lock suite's leg 3) and the now-empty item folder
- [ ] `test_v6_snapshot_inventory.py` / `test_check_ledger_4a.py` / `test_check_proof_integrity.py`
      import repo scripts that import `verification` — re-point or retire those scripts'
      manifest dependency (`assess_v6_snapshot_churn.py`, `check_ledger_4a.py` must keep
      loading `ledger-4a.json` without a manifest); the accepted-limitation omit list should be
      empty after this batch

### C3 — Legacy extraction lane (owner-ruled)

- [ ] Delete `hierarchy_resolver.py` + `usage_extractor.py` (941 lines, unreachable from the
      CLI) with their pinning tests (`tests/unit/test_hierarchy_resolver.py`,
      `tests/unit/test_type_indexing_helpers.py`, others by importer grep) in one commit
- [ ] The commit message records the semantic difference: legacy `most_specific` **warns**
      on an ambiguous definition match where the live `_most_specific_definition` **raises** —
      the old leniency the cutover removed, not a lost capability
- [ ] Delete `tests/conformance/test_hierarchy_resolver.py` in the lane-deletion commit,
      citing the ratified ruling (epic, Owner Rulings, 2026-08-25)
- [ ] Split `tests/conformance/test_ast_dispatch_invariant.py`: retire the legs whose sites
      are `usage_extractor._extract_single_binding`,
      `hierarchy_resolver._walk_aggregation_ast`, and agentic-mbse's
      `_decompose_node`/`classify_redefinition` (no live importer); keep the live-subject
      legs — the src-wide dispatch guardrail (REQ-AST-04, totals recounted post-deletion)
      and the `expression_utils.reconstruct_expression` legs if that module is
      live-reachable, else those retire with the lane too
- [ ] Surgery on `tests/helpers/live_extraction.py` (shared by four other conformance
      files): keep `calc_defs` (live `SysMLDataExtractor`), drop `hierarchy_data` and
      `calc_usages`; sweep `conftest.py`, `test_extractor.py`,
      `test_expression_compiler.py`, `test_elaboration_payload_identity.py` for legs
      reading the dropped keys — legacy-subject legs retire, live legs stay
- [ ] Delete `.project/active/type-indexing/probe/` (kept through Move B only for these tests)

### C4 — Dead `src/` lanes (research §5, each lane + pinning tests per commit)

- [ ] V11 preflight code (85 lines; doc corrections are `[V11-DEAD-GATE-DOCS]`, not here)
- [ ] Deriver-era generators (123)
- [ ] `ConcreteConstraint` (105)
- [ ] Dead extractor and model classes (126)
- [ ] `compile_predicate` / `load_predicate` pair (54)
- [ ] Error-subclass boilerplate (~50)
- [ ] Mechanical duplicates (~390)

### C5 — Committed test data

- [ ] Replace the item8 `unit_map` arrays (~47,000 lines,
      `tests/unit/data/item8-snapshot-inventory-{pre,final}.json`) with digests, preserving
      every live assertion (also clears their accepted-residue dead-path strings from Move B)
- [ ] Delete zero-reader fixture sets: `golden/calc_def_compilation_golden.json` (3,254),
      `baseline_yaml/` (844), plus whatever a reader sweep finds
- [ ] **`baseline_outputs/` (13,923 lines)**: restore a genuinely regenerating comparison or
      delete it with its reader. Either way the emit-step gap gets a `BACKLOG.md` id (F4) —
      the epic must not close with it named in a report and owned by nobody
- [ ] Collapse the `catf_mfe_d5` fork (5,718-line copy, four-line diff) to generated variants,
      keeping each `instance_graph_snapshot.json` (license-bound to regenerate; they keep
      repointed tests license-free). ~20 of `test_d5_variants.py`'s 31 tests test the
      generator's CLI, not the product — retire those with the fork
- [ ] Fix overstating docstrings on tests that stay, as they are passed

### C6 — Process tests of closed items

- [ ] Retire process tests whose items closed months ago (research §7 grading); each commit
      names the item and what the test was believed to defend

### C7 — Final gates

- [ ] Byte-identity gate: generated output byte-identical for every fixture, licensed
- [ ] `vulture` + lane-level sweep report a materially smaller dead surface than the
      2,370-line baseline
- [ ] `tests/` committed data down ≥60,000 lines; test *function* count drops far less than
      line count; zero fixture files with no reader (sweep)
- [ ] Every gap named along the way exits as a filed `BACKLOG.md` item with an id
- [ ] Full licensed suite green — with C2 done, no omit list and no accepted-limitation caveat
- [ ] Update `CURRENT_WORK.md`; archive the three move folders per the standing close rule

## Filed, not done here

- Snapshot codec consolidation (~550 lines): costs an `instance-graph/v4` schema bump and 22
  licensed fixture re-captures — backlog item, not this move
- New tests for coverage gaps — filed to `BACKLOG.md` with ids, not built
- `scripts/spike_attribute_expressions.py` writes into a deleted `active/` path if ever run —
  dev tooling; disposition it in C6 (likely retire)
