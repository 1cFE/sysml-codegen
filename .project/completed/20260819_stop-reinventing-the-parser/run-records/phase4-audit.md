# Phase 4 audit: close public routes and registry authority

**Verdict:** Needs Work — bounded. **`audit-phase4-F1` re-audited and FIXED at `571ed39`**
(see "Targeted re-audit of audit-phase4-F1" at the end of this record). The second finding —
the universality claim, including `audit-phase4-F2` — was not re-audited in that pass. Every Phase-4 behavior obligation verifies and reproduces; two
evidence-record obligations do not.
**Audited:** 2026-08-18
**Scope:** Phase 4 only. Item-level spec conformance and Phase 5 were not assessed.
**Audited candidate:** codegen `e5f73e6cff653f5b6a0c3861c0d3d5cd5b2544da` (branch
`stop-parser-impl-r2`, worktree `/tmp/stop-parser-rev2/worktrees/sysml-codegen`, clean);
Agentic input `3f8bd587af40f05b929dd56645901dada7daea37` (read-only); planning artifacts at
`a5ff0a2` on `stop-reinventing-the-parser`.

---

## The Point

The product parses a SysML v2 model with a real parser, walks the parser's resolved semantic tree to
reconstruct the modeled math, and emits that math as executable TEAx Python. Every decision on the
way reads the parser's own resolved evidence. An authored form the toolchain cannot honor has two
honest outcomes and no third: resolve it through the parser, or refuse by name before a graph,
snapshot, package, or output byte exists. Phase 4 is where that rule stops being true only on the
routes a test happened to pick: it must hold on every public expression consumer, through live,
admitted, and capture entry points, and generation must stop taking a caller's word for a fact the
sealed graph already owns.

The certification record carries the same obligation. A gate that no longer measures what it claims
to measure is not evidence, even when it is green.

## Summary

The behavioral work is real and reproduces independently. The registry no longer accepts any
caller-supplied account of exit-point types; the natural-route matrix covers every expression
consumer across five arms on real parsed models; A5a and A5b are in the ledger with correct measured
old states and live proving tests; the deep probe still refuses by name. Every number in the
implementation record reproduced in a fresh run from the recorded extraction.

Two things fail. First, the phase deleted the only committed check that compares a fixture's current
bytes to its locked bytes, in the commit that answered its own documentation-only fixture edit, and
the ledger row that owns the change does not name the coverage that was dropped. Second, the plan's
validation bullet claims every public refusal row asserts six things; six rows assert fewer, and the
consumer closure table asserts public-arm coverage that two deep-override cells do not have.

Neither is a product-behavior defect. Both are evidence-record defects in the phase whose job is to
establish a production-ready candidate, immediately before the phase that seals artifacts around it.

## Product Judgment

**This is the right piece of work, and the closure it claims for behavior is genuine.** The
product-lens gate for this run is **DISPOSED (audit-phase4-F1, audit-phase4-F2)**; no owner or
`[HARD]` contradiction was found in Phase 4. Three older blocks are discharged by this run:
`audit-phase3-F4` is **FIXED** against its own recorded falsifier by independent code reading and a
licensed run — which also clears the `PENDING INDEPENDENT RE-AUDIT` gate the remediation block left
open — and `audit-phase3-F1` and `-F3` are FIXED. `audit-phase3-F2` remains disposed-but-undelivered
and is scheduled nowhere; it is agent-grade and does not block, but it must not be read as closed.

**Structural smell 1 — two representations manually kept synchronized — fired, and this judgment does
not resolve it.** One instance was removed (the caller's exit-point type list beside the graph's own
root outputs). One was created: the frozen fixture inventory and the on-disk fixtures now have no
committed check that their contents agree. That is the substance of `audit-phase4-F1`, and it is the
reason this phase reads Needs Work rather than Certify.

The decisive point is symmetry with the item's own promise. This item exists to stop the generator
accepting a weaker substitute for evidence it should derive exactly. A phase inside it answered a
documentation-only fixture edit by retiring the current-bytes comparison for all 43 fixture roots and
recorded the change as satisfying the lock rather than as narrowing it. Six `ADDED_ROOTS` —
including `indexed_expression_source`, which the phase's own indexed-BINDING matrix cell reads with a
hard-coded line number — now have no byte pin on any leg. The loss is narrow (a semantic fixture edit
still surfaces as output drift through leg 2; a comment-level or added-root edit does not), and the
fix is small. It should land as Phase-4 work, because fixing verification code after certification is
a production change that restarts these gates anyway under the phase's own rollback rule.

## Findings

### Plan completion

Verified complete, independently:

- **Graph-derived registry.** `required_exit_point_wrapper_types(graph)` is the first statement of
  the generation operation (`generation/registry.py:264`), before constraint validation and before
  any rendering. The fifth parameter is gone (`registry.py:238-244`), the CLI collector is gone
  (`cli/__init__.py:711-730`), and a grep over `src tests docs verification scripts` for
  `exit_point_primitive_types` / `_collect_exit_point_wrapper_types` returns zero hits. The three
  exported names are aliases of one object (`registry.py:399-400`), so there is one path, not three.
  Unsupported roots raise typed `EXIT_POINT_TYPE_UNSUPPORTED` (`generation/errors.py:58-73`) with
  module, field/channel, python_type, and `file:line`. Refusal precedes output clearing
  (`cli/__init__.py:1244` preflight vs `:1290` clear), and a nested sentinel tree is asserted
  byte-identical after a refused run. This closes the prior audit's CI-5 structurally, not by test.
- **Full natural-route matrix.** 132 collected nodes in
  `tests/conformance/test_expression_evidence_integrity.py`. The arms are real: live via
  `elaborate_model_paths`, admitted via the real `admit_sources`, capture via
  `capture_instance_graph_snapshot` (`:848`). Exact positive for five roles × 5 arms (`:743`), deep
  override separately (`:800`), indexed refusal 5 × 5 (`:913`), operand/depth and missing-target
  `tuple(ExpressionSiteRole)` × 2 codes × 5 arms (`:1012`), deep-override missing target (`:1055`).
  Capture appears once per row because that route is fixed strict by design (`:38`) — stated, not
  silently dropped.
- **Dual-layer index proof.** The internal layer (`tests/unit/test_expression_evidence_boundary.py`)
  bypasses only the inventory: `_consumer_with_inventory:234` builds the elaborator via
  `object.__new__`, seeds an `IndexedReferenceUse`, and calls the real adapter method, so the
  assertion is about the adapter's own `require_exact` call. Read them as four call sites of one
  backstop (`expression_evidence.py:188-211`), which is the production shape, not four independent
  defenses.
- **A5a / A5b.** `verification/expected-transitions.md:23-24` carry both rows with the required
  measured old states and required new results; the old/new hash columns recompute from the row text.
  A5a's proof (`:1105`) uses `cells : Cell[1]` with authored `cells#(2).mass` out of range; A5b's
  (`:1134`) uses `Cell[3]`, refuses in both strict and lenient arms, and spies
  `OccurrenceIndex.resolve_address` to prove occurrence resolution never ran. A5b's two starting
  states are pinned documentarily (docstring `:1141-1149` plus the hashed ledger text) — unavoidable,
  since old behavior cannot be asserted at new code. The reconciliation gate expects both
  (`test_stop_parser_documentation_contract.py:19-20`) and still reports exactly the two named record
  transitions.
- **`deep_cross_scope_probe` stays refused.** `SI_OCCURRENCE_MISSING`, authored reference
  `measurement_system::station::array::sensor::core::metric_value`, `root-0/design.sysml:77`, one
  rendered code token, through the public route
  (`tests/conformance/test_occurrence_calc_domain_derivation.py:167-204`). The A2 batch record and
  refusal hash are unchanged. The fixture edit is one comment line, no line-number shift.
- **Static closure.** The ownership manifests, five evasion mutations, deleted-symbol absence,
  off-route reachability exclusions, and the no-dynamic-`getattr` rule are kept tests
  (`tests/conformance/test_expression_evidence_ownership.py:1030-1119`,
  `test_gated_manifest_identity.py`) and are inside the default suite, which is green.
- **Backlog filing.** All three rows exist and are agent-graded, none settled:
  `[INDEXED-ELEMENT-EXPRESSION-SUPPORT]`, `[OUTPUT-ALIAS-DUPLICATE-SOURCE-SILENCE]`, and
  `[DEEP-QUALIFIED-OUTPUT-WIRING]` (`.project/backlog/BACKLOG.md:30-48`).
- **Documentation sweep.** Overview, reference 00, 20 (REQ-REG-09), 30, and the verification matrix
  changed in `1ce8638`; reference 01 and 19 already carry the current contract and needed no edit.
  P-003's application status, the Agentic plant idiom (indexed documented as valid-but-unimplemented),
  `CURRENT_WORK.md`, and the epic status are current and honest about audit-pending state.

Not complete:

1. **The fixture-byte lock was narrowed, and the ledger row does not say so**
   (`verification/capture_baseline.py:191-215`, comparison deleted in `8919232`;
   `verification/expected-transitions.md:116`). See `audit-phase4-F1`. The plan's own wording for
   this work was that "the fixture's locked hash class and ledger ownership must be respected"
   (`plan.md`, Phase 4, last changes-required bullet). Ownership was respected; the hash class was
   narrowed. What should change: restore a current-vs-locked byte comparison across all 43 roots with
   any deliberate difference owned by a named row, or state the loss in the ledger and name what
   covers the six `ADDED_ROOTS`.
2. **The validation bullet claims universality the rows do not have.** The plan requires every row to
   assert code, authored reference, root-relative `file:line`, cause chain, one rendered code token,
   and no graph/snapshot/output mutation. The parameterized rows meet it through
   `_assert_named_indexed_refusal:867`, `_assert_site_failure:958`, and
   `_assert_capture_output_preserved:830`. These assert fewer:
   `test_constraint_definition_index_refuses_at_pregraph_inventory:436` (no cause chain, no token
   count, no output assertion); `test_valid_indexed_source_refuses_before_graph_with_exact_capability_diagnostic:523`
   (no cause chain, no output); `test_public_source_arms_preserve_the_same_evidence_refusal:228`
   (codes and token count only); `test_operator_wrapped_indexed_source_still_refuses_correctly:1164`
   (no output); A5a/A5b `:1105`, `:1134` (capture arm asserts `not output.exists()` without
   pre-seeded bytes); `test_occurrence_calc_domain_derivation.py:189-204` (no cause chain, no
   output). What should change: route them through the two helpers, or amend the plan bullet to name
   the exempt rows and why. Do not leave the bullet claiming universality.

### Spec conformance

Not assessed. This is a phase audit; lane rows A1–A6 / B1–B10, the L-01–L-14 / U-1–U-2 census
ledger, and the item's success criteria belong to the item-level audit after Phase 5. No spec
checkbox was marked by this pass. Phase 4's own contribution to criterion 7 (distinct
unsupported-capability diagnostic that does not blame the model) is verified on every expression
consumer; criterion 8 (both follow-ups separately owned) is verified.

### Design conformance

- **D9 — fail before output mutation:** holds, on both `--models` and `--from-snapshot`, which
  converge on the same preflight ordering inside `run_codegen`.
- **Evidence-and-public-boundary matrix:** holds for the five real expression consumers across five
  arms. The deep-literal-override row is the exception — see `audit-phase4-F2`. The gap is caused by
  the product working correctly (SysIDE refuses `:>> rig.cells#(2).mass = 7.0;` at parse, so there is
  no authorable public route), but the closure table asserts equal public-arm force for that row.
- **Static-removal checks:** hold; exact-set equality and symbol absence are kept tests.
- **Three-leg fixture lock:** leg 1 (historical) and leg 3 (verification code at current bytes) hold.
  The current-bytes leg for fixture inputs no longer exists — `audit-phase4-F1`.

### Code integrity

- `cli/__init__.py:323` calls `required_exit_point_wrapper_types(graph)` and discards the result for
  its exception, then `generate_registry` recomputes it. Harmless duplication; the preflight's only
  remaining value is ordering. Worth collapsing when the CLI is next touched.
- `generate_registry_from_graph` and `generate_registry_function` (`registry.py:399-400`) have zero
  production callers — re-exports and tests only. Phase 4 rewrote their comment rather than removing
  them. They are in scope for the B9 rule ("every exported seam enforces the same invariant") and do
  enforce it, so this is a cleanup note, not a defect.
- `docs/architecture/reference/08-generation.md:22` still says `generate_registry_function()`
  produces a `MODULE_REGISTRY` dict; the template emits `create_registry`. The sweep updated 20 and
  the matrix and missed this one.
- `tests/unit/test_registry_generation.py:112-175` renders the Jinja template directly with a
  hand-passed `exit_point_types` list. It exercises the template, not the seam, and would pass
  unchanged before and after the phase. The discriminating power sits in the alias-signature and
  alias-refusal tests, which is enough — but do not count this class as registry-authority coverage.
- The CLI refusal route is driven only through `--models`; `--from-snapshot` is never driven through
  a refusal, though both share the same preflight.
- `generate_registry` remains a long function with four near-identical import passes and
  function-scoped lazy imports to avoid cycles. Pre-existing, untouched by this phase.

No TODO, placeholder, broad `except Exception`, or silent invariant fallback was found in the
Phase-4 diff. No `feedback_*` memory conflicts with this work.

## Independent reproduction

Run from the recorded extraction `/tmp/stop-parser-rev2/phase4-extraction-r2` with
`SYSIDE_LICENSE_KEY` loaded and `STOP_PARSER_ARTIFACT_SOURCE_INPUTS` pointing at its manifest.

| Check | Result |
|---|---|
| Extraction identity | All 2,581 tracked files byte-identical to `e5f73e6`; three archive/bundle SHA-256s match `artifact-source-inputs.json` |
| Default suite | **2,492 passed, 34 skipped, 94 deselected**, 0 failed — matches the record |
| Skip audit | All 34 skips are `test_computed_attribute_golden.py:50` ("no computed attributes in the golden"). No `requires_license` skip; no required licensed route skipped |
| Reconciliation gate | 14 captured / 23 refused, current batch `7f9269…`, frozen `bd7bf2…`, 22 maintained / 23 metadata-only snapshots, exactly `deep_cross_scope_probe` and `plant_value_shapes` — matches |
| `mypy src/` | 30 errors in 8 files across 76 sources — the unchanged Phase-3 baseline |
| Ruff, changed files | clean |
| Public TEAx mutation suite | `tests/execution/test_occurrence_derivation_mutation_teax.py -m execution` → **6 passed** |
| Focused route + registry suites | 173 passed (evidence integrity + boundary + calc-domain); 37 passed on the four named registry files and 295 on a widened registry selection; 46 passed (registry + preflight + module-kind + hygiene + doc contract); 30 passed (doc contract + snapshot inventory + probe lock). Zero skips throughout |
| Candidate durability | `e5f73e6` objects are reachable from the main checkout's `.git`; the `/tmp` worktree is a view, not the only copy |

One environment note: the execution suite needs `pandas`, which the pinned venv does not carry — it
was supplied as an ephemeral `uv run --with pandas` overlay rather than by mutating the recorded
environment. The implementation record hit the same gap.

## Certification

**Needs Work, bounded.** Two items, neither touching shipped behavior:

1. `audit-phase4-F1` — restore or replace the current-bytes fixture leg, and state the coverage
   change plainly in `verification/expected-transitions.md:116`, naming what covers the six
   `ADDED_ROOTS`.
2. The universality claim — either raise the six under-asserting rows to the six-element bar, or
   amend the plan's validation bullet to name them as exempt with the reason. `audit-phase4-F2`
   belongs here too: mark the two deep-override cells with their measured unauthorability and make
   `public_arms` a per-cell assertion.

`audit-phase3-F2` is not a Phase-4 obligation but is scheduled nowhere; it should be given an owner
before close.

No plan checkbox was changed by this pass — the implementation claims are accurate as written, and
the two gaps above are recorded here rather than by unchecking work that was done. No spec or epic
checkbox was marked. No fix, merge, push, close, or pre-PR action was performed.

**Not checked:**

- **Phase 5 and item-level spec conformance.** Out of scope by instruction.
- **Mutation testing.** The five evasion mutations and the static-closure kill table were verified as
  present and green, not re-executed as fresh mutations. A switch arm no kept mutation names could
  still be unpinned.
- **Agentic.** Verified as the read-only input `3f8bd58`; not re-audited. Its suites were not rerun.
- **The owner-retired Agentic PDF/HTML corpus** was not run, per the standing owner instruction, and
  must not be.
- **Paid/network cases** were not run.
- **Repository-wide Ruff** was compared only on changed files; the 608-error broad baseline was not
  re-measured.
- **Generated-package runtime beyond the six-node mutation suite.** No wider real-simkit execution.
- **`ruff format`** was not run as a gate.
- **The claim that no check anywhere else pins current fixture bytes** rests on reading
  `capture_baseline.py`, `test_probe_fixture_lock.py`, and a grep for the two manifest paths; it was
  not established by mutating a fixture and observing the suite stay green.


---

## Targeted re-audit of `audit-phase4-F1` (2026-08-18)

**Scope:** finding 1 only — the verification-code regression. The universality finding and
`audit-phase4-F2` were **not** re-audited here; the user asked for finding 1.

**Re-audited candidate:** codegen `571ed39b8059860206be57e3509cecc85bfbfac5` on
`stop-parser-impl-r2` (repairs `9da3d84` tests, `f951663` fix, `571ed39` ledger); project records
`3d7a362`; auditor artifacts preserved at `fef3284`.

**Result: FIXED.** Both halves of the finding are answered — the coverage is restored by an
independent mechanism, and the ledger now states plainly what was lost and what restored it.

### The mechanism, read rather than trusted

`validate_current_fixture_sources` (`verification/capture_baseline.py:210`) walks the frozen P_seed
inventory and, for every source, hashes the file **under `repository_root`**. A P_seed rebuild
cannot satisfy it, because the compared byte always comes from the working tree. A difference is
allowed only when `verification/expected-transitions.md` carries **exactly one** row for that path
naming **both** the frozen and the current hash; zero rows, two rows, or a row missing either hash
all raise. It is called unconditionally from `validate_manifest:196`, which `main:710` runs on every
invocation, before the batch and output-transition legs.

Counts: 43 roots (37 canonical + 6 `ADDED_ROOTS`), 110 sources — confirmed against
`verification/fixture-manifest.json` itself, not against the claim.

### Adversarial probes (all run; the falsification my first pass listed as not checked)

Against a scratch copy of the real fixture tree and the real frozen manifest:

| Probe | Result |
|---|---|
| Unmutated baseline | PASSED — 110 checked, 6 added roots, 7 added sources, one transitioned source |
| Comment-only edit, canonical root (`plant_value_shapes/design.sysml`) | REFUSED — unowned transition, 0 ledger rows |
| Comment-only edit, `ADDED_ROOT` `indexed_expression_source/model.sysml` | REFUSED — the exact hole F1 named |
| Extra edit to the ledger-owned deep-probe file | REFUSED — row omits the current hash |
| Duplicate ledger row for the owned path | REFUSED — expected one row, found 2 |
| Ledger row present with a wrong current hash | REFUSED — row omits the frozen or current hash |
| Restore | PASSED — identical report to baseline |

End-to-end through the real gate, in a disposable full copy of the `571ed39` extraction:

- Comment-only edit to `indexed_expression_source/model.sysml` → `sysml-codegen`'s
  `capture_baseline.py --check` **refuses inside `validate_manifest`**, before the batch and output
  legs: `unowned current fixture source transition`.
- New `.sysml` file added to a locked root → refused by the file-set leg
  (`capture_baseline.py:190`, `unlisted or missing source`). Byte changes and set changes are both
  covered; the byte leg alone does not see an added file, and does not need to.
- Restored copy, full `--check --check-current-batch --check-output-transitions` → the same
  reconciliation numbers as before the repair (14 captured / 23 refused, batch `7f9269…` vs frozen
  `bd7bf2…`, 22 maintained / 23 metadata-only, exactly `deep_cross_scope_probe` and
  `plant_value_shapes`).

**Evasion route closed:** regenerating the manifest to absorb a mutation does not work. The rebuild
reads P_seed, and `verification/fixture-manifest.json` is itself one of the 118 rows recomputed
against history at `20f9e60` by leg 1, so altered manifest bytes fail that leg.

### Anti-vacuity and honesty

- `test_every_current_fixture_source_is_pinned_or_ledger_owned`
  (`tests/conformance/test_probe_fixture_lock.py`) pins the exact report — 110 / 6 / 7 and exactly
  one transitioned path — so a check that silently stopped covering roots fails.
- `test_an_unowned_current_fixture_edit_fails_the_lock` is a real negative: it mutates bytes and
  requires the `ValueError`.
- The deep-probe row's two hashes match the frozen manifest entry and the file on disk exactly.
- The `capture_baseline.py` leg-3 row now records current hash `442dbf9…`, which matches the file,
  and its reason names the regression in plain words: `8919232` "also dropped the comparison with
  current fixture bytes", and `f951663` "restores that coverage as a separate ledger-gated check over
  all 110 current sources in all 43 roots, including the six `ADDED_ROOTS`". That is the disclosure
  F1 asked for.

### Reproduction

- Extraction identity: all 2,581 tracked files in `/tmp/stop-parser-rev2/phase4-fix-extraction.jyhBwP`
  byte-identical to the worktree at `571ed39`; archive SHA-256 `c5e96f00…` matches its manifest.
- `test_probe_fixture_lock.py` + `test_stop_parser_documentation_contract.py` +
  `test_v6_snapshot_inventory.py` → **32 passed**, matching the remediation record.

**Not checked in this pass:** the second finding (six under-asserting refusal rows) and
`audit-phase4-F2`; the `--from-snapshot` refusal coverage, graph-input registry rendering tests, and
documentation correction claimed in the same remediation; the full default suite at `571ed39`
(claimed 2,496 / 34 / 94); mypy, Ruff, and the TEAx lane at `571ed39`; and `audit-phase3-F2`'s
scheduling. Those remain on the remediation record's word, not this auditor's.

---

## Orchestrator verification — finding 2 and remediation residuals (2026-08-18)

The F1 re-audit above confirmed finding 1 by adversarial execution but explicitly did not
re-verify finding 2 or the non-blocking repairs. Those are record-accuracy and test-existence
claims — objectively checkable — so they were verified by the orchestrator by execution, per the
run's record-the-verification rule for minor, objectively verifiable fixes:

- **Focused Phase 4 selection: 206 passed**, recomputed verbatim from the implementation
  record's recorded 7-file command (the remediation's figure is that selection plus its four
  added nodes; traceability is via the cross-reference, one hop).
- **Finding 2 substance:** the plan's validation bullet now scopes the six-part assertion claim
  to the parameterized public matrix and enumerates each narrower row group's actual assertion
  set (plan.md:1127-1139). The consumer-closure table records public arms per cell, requires a
  reason for exactly the empty-arm cells, and requires every named proof to resolve
  (test_expression_evidence_integrity.py:1363-1404). The two deep-override exception cells now
  carry real proofs, run individually: the licensed parser probe (authors
  `:>> deep_rig.cells#(2).mass = 7.0;`, asserts SysIDE parse rejection), the Feature-only
  structural probe, and the path-factory refusal — 3 passed.
- **Non-blocking repairs:** `--from-snapshot` is a real parametrized source arm of the
  unsupported-exit-type refusal (preflight suite 17 passed); `test_registry_generation.py` now
  drives `generate_registry(graph, …)`; `audit-phase3-F2` is an explicit unchecked Phase 5
  obligation gating `C_prod` (plan.md:1231).
- Full default suite from the retained `571ed39` extraction rerun for the 2,496 figure
  (result recorded in the Phase 4 closure note in plan.md).

Escalation was not needed; nothing contradicted the remediation record.
