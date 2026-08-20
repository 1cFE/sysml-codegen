# Phase 1 Audit — Stop Reinventing the Parser

**Verdict:** Pass with findings — **all four Majors confirmed closed 2026-08-17**
at Codegen `d257ef1` / Agentic `8d27fb3` (see the confirmation addendum at the end).
Minors 5-11 and Informational 12/14 remain open and carry to Phases 2-4; Informational 13 is closed.
**Audited:** 2026-08-17
**Auditor:** independent stage agent, dedicated fresh run
**Codegen:** `stop-parser-impl-r2` @ `e4e26932729a49e4497c89842adf2d79b92deecb`, base `C_base` `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`
**Agentic:** `stop-parser-evidence-r2` @ `85c77588e0006d826bab2d5c15a136582df8e3e5`, base `A_base` `2171016d3e3e0805525aa4cf787c55c6293dd00c`
**Independent extraction:** `/tmp/stop-parser-rev2/audit-extraction/` (left in place; built by this audit from
`git archive` / `git bundle --all` of the two audited commits — no implementer-built artifact was reused)

---

## Summary

Phase 1's contract holds. The two commits contain nothing but tests, fixtures and ledger rows; every
production byte is untouched and `occurrence.py` is the *same Git blob* at both commits. All three lock
legs reproduce independently. Both red cases are red for exactly their stated reasons, verified by
running them and by an independent trace of the elaborator, not by reading the failure count. D1-D4 shows
zero regressions and `deep_cross_scope_probe` is still a typed refusal with no captured snapshot. The
completion record is accurate on essentially every checkable number.

The findings are not about whether Phase 1 measured the right thing. They are about whether the kept tests
will still *demand* the right thing when Phases 2-4 turn them green. Four of them matter: the two indexed
red tests never assert the authored reference or the root-relative location, and I can demonstrate a
weak implementation that satisfies them; one Agentic test cannot go green under the design's own Phase-2
deletion list; one recorded red is unrelated to this item and forces an unplanned production change; and
the red set covers the live arm only where the design requires live plus admitted/capture.

Phase 1 is fit for Phase 2. Findings 1, 2 and 4 should be fixed in the same landing unit as the Phase-2/3
work that turns those tests green, and finding 3 needs a ruling before Phase 3 closure.

---

## Reproduction results

Everything below was run by this audit. Codegen commands ran from the independent extraction with
`STOP_PARSER_ARTIFACT_SOURCE_INPUTS` naming this audit's own manifest; Agentic from its own extraction.
License loaded from the environment; never emitted.

### Obligation 1 — diff-level scope

| Check | Command | Result |
|---|---|---|
| Codegen changed paths | `git diff --stat 78a9beb9 e4e2693` | 7 files, 889 insertions: 3 test modules, 3 fixtures, `verification/expected-transitions.md` |
| Codegen production source | `git diff --stat 78a9beb9 e4e2693 -- src/` | **empty** |
| `occurrence.py` byte identity | `git rev-parse {78a9beb9,e4e2693}:src/sysml_codegen/elaboration/occurrence.py` | both `af721562512d5684ce3dd1c96624fbe3355a536d` — the same blob, stronger than an empty diff |
| Agentic changed paths | `git diff --stat 2171016d 85c7758` | 2 files, 210 insertions: the two new test modules |
| Agentic production source | `git diff --stat 2171016d 85c7758 -- src/` | **empty** |
| Parentage | `git rev-parse e4e2693^`, `85c7758^` | exactly `C_base` and `A_base`; one commit per branch |

No Critical finding. Scope is clean in both repositories.

### Obligation 2 — the three lock legs, reproduced independently

**Leg 1** — my own script, reading `probe_fixture_commit` from the lock and recomputing against that tree
from a bundle I built:

```
schema: stop-parser-probe-lock/v1
probe_fixture_commit: 20f9e60a19b30bc1ec9a27aacb08380f4bc45602
probe_fixture_parent: 7b29d8b636e284364a4fdce9079f153c51c867ea
row count: 118 | rows read: 118 | mismatches: 0
```

Ancestry independently confirmed: `20f9e60a^` = `7b29d8b6`, `43edf9bd^` = `20f9e60a`, both ancestors of
`C_base`; `43edf9bd`'s entire diff is `verification/probe-fixture-lock.json`, one file, one insertion.

**Leg 2** — through the committed validators, not a reimplementation:

```
uv run --extra dev python -m verification.capture_baseline \
  --check --check-current-batch --check-output-transitions      # EXIT=0
{"captured": 14, "refused": 23,
 "current_sha256": "7f9269781a8938308715229c5be00855490e82b7e54f9cb90939195e3aeefa40",
 "frozen_sha256":  "bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288",
 "frozen_p_seed":  "52a03cd2d0a9fdd340b60b16cea79a5b72234b08"}
{"metadata_only_snapshots": 23, "maintained_current_snapshots": 22,
 "batch_record_transitions": ["deep_cross_scope_probe", "plant_value_shapes"],
 "golden_rows": [2 rows]}
```

Every figure matches the completion record exactly.

**Leg 3** — current-byte pinning of the locked non-fixture rows. Five probe scripts byte-identical to
lock-time; `verification/capture_baseline.py` differs, lock-time `6aef97af…`, current `c8a7de07…` — the
one known difference, with both hashes and both owning commits present in the new ledger section.
`git log 20f9e60a..e4e2693 -- verification/capture_baseline.py` returns exactly `46694e2` and `da4aa78`,
so the ledger row's citation is complete.

**The new kept check** (`tests/conformance/test_probe_fixture_lock.py`): **12 passed**. Audited against the
design's five bullets — it reads `probe_fixture_commit` from the file and then asserts it (`PROBE_FIXTURE_COMMIT`
is a comparison constant, never the lookup key); it reads historical bytes only through `git show` against
the declared history root; it asserts `read == len(rows) == 118`; it pins leg 3 separately with a
ledger-ownership requirement; and nothing in the module writes the lock.

**Anti-vacuity, proved by mutation** — I mutated a copy of the lock, ran the module, and restored it
(restored SHA-256 `39e42e35…` verified against `e4e2693:verification/probe-fixture-lock.json`):

| Mutation | Outcome |
|---|---|
| truncate `files` to 2 rows | FAILS (`test_locked_verification_code_is_pinned_at_current_bytes[capture_baseline.py]`) |
| corrupt one row's `sha256` | FAILS (`test_every_locked_hash_recomputes_against_the_named_historical_tree`) |
| set `probe_fixture_commit` to `43edf9bd` | FAILS (same test, on the field assertion) |

A truncated lock file and an unread row both kill the check. The anti-vacuity assertions are real.

### Obligation 3 — red-set quality

Full Codegen suite from the extraction: **9 failed, 2336 passed, 34 skipped** — identical to the record.
(My first run showed 18 failed because my bundle carried only the branch; nine of those were history
lookups for commits off that branch. With `--all` in the bundle, `test_check_ledger_4a.py` and
`test_exact_route_fingerprint_stability.py` are green — 76 passed alongside the lock module.)

All 9 recorded Codegen node IDs reproduce, with these exact failure reasons:

| Node | Observed reason |
|---|---|
| `…singular_slot_refuses_before_consumers[True]` / `[False]` | `Failed: DID NOT RAISE ElaborationDiagnosticError` |
| `…singular_slot_writes_no_snapshot` | `Failed: DID NOT RAISE` |
| `…plural_slot_refuses_before_occurrence_resolution[True]` | got `[SI_OCCURRENCE_AMBIGUOUS, SI_OCCURRENCE_MISSING]`, expected `[SI_INDEXED_SOURCE_UNSUPPORTED]` |
| `…plural_slot_refuses_before_occurrence_resolution[False]` | `Failed: DID NOT RAISE` (see finding 9) |
| `test_every_consumer_cell_names_a_proof` | lists 20 uncovered cells |
| `test_discovered_raw_selectors_equal_the_reviewed_manifest` | ~26 unowned reads |
| `test_no_dynamic_getattr_survives_in_production` | one read, in `resolution/models.py` (see finding 3) |
| `test_deleted_symbols_are_absent` | exactly the five weak identifiers in `extraction/` |

**Independent trace, not the test's word.** I ran the elaborator directly on all three fixtures:

- **Case 1** (`indexed_bare_chain_singular`, `cells : Cell[1]`, `picked = cells#(2).mass` at line 15):
  returns an `InstanceGraph` with `diagnostics == []`, in **both** strict and lenient modes, containing an
  attribute node whose occurrence step is `occurrence_index=0` under the `cells` slot. The authored `#(2)`
  is silently bound to occurrence zero on a slot that has one occurrence. This is the escape, unarguably.
- **Case 1 capture arm:** `capture_instance_graph_snapshot` **succeeds** and seals a 6036-byte snapshot
  from that collapsed graph. The record's claim that the capture arm seals the escape is true and material.
- **Case 2** (`indexed_bare_chain_plural`, `Cell[3]`): strict refuses with `SI_OCCURRENCE_AMBIGUOUS`
  (`reference='cells#(2).mass'`, `root-0/model.sysml:15`, "exact containment step … has 3 concrete
  occurrences") then `SI_OCCURRENCE_MISSING` on the typed alias. Exactly the recorded starting diagnostic.
- **Operator-wrapped** (`* 1.0`): refuses in both modes with `SI_INDEXED_SOURCE_UNSUPPORTED` — and with
  `reference=None`, `source_file=None`, `source_line=None`, and an **absolute** path in `detail`. This is
  the evidence behind finding 1.

No red is a fixture, license, import or harness failure. All three fixtures parse and load; the licensed
tests ran live; `AUTHORED_INDEXED_LINE = 15` is correct for all three.

Agentic fast suite: **10 recorded red nodes reproduce exactly**, all 10 node IDs matching the record.

### Obligation 4 — D1-D4 preservation

Occurrence/producer matrix (11 modules named by the design, resolved to paths — note
`test_elaboration_containment_address.py` lives under `tests/unit/`, not `tests/conformance/`):
**110 passed, 0 failed.** No occurrence module appears anywhere in the full-suite failure list.

`deep_cross_scope_probe`: batch record is `status: refused`, `codes: ["SI_OCCURRENCE_MISSING"]`, message
"exact output `0b877fee-e8c8-5472-a0b2-24aebac57e50` has no producer in the consumer domain". The fixture
directory holds only `design.sysml` and `library.sysml` — **no captured snapshot**. The never-restore
condition holds.

Retained harness (`test_coverage_probes.py`, `test_baselines.py`, `test_evidence_artifact_topology.py`):
**37 passed** — the record's figure exactly.

### Obligation 5 — completion-record accuracy

Verified true: changed-path set; both empty `src/` diffs; the `occurrence.py` claim (understated, in fact);
the ancestry and parentage claims; `43edf9bd`'s one-file diff; all three lock legs including both
`capture_baseline.py` hashes and both owning commits; the lock check's 12 green tests; the 37 retained-harness
tests; the Codegen 9/2336/34; all 19 red node IDs; the Case 1 and Case 2 traces; the operator fixture's
positive result; `deep_cross_scope_probe`; issues 1, 2, 4, 5 and 6; and every static baseline —
Codegen `ruff check tests/` = **127**, `mypy src/` = **30 errors in 8 files**, Agentic `mypy src/` =
**101 errors in 21 files**, `ruff check` clean on all five added files. Both original user checkouts and
both worktrees are `status --porcelain` empty at audit end.

Two record figures I could not reproduce exactly, neither material:

- **"125 passed" for the D1-D4 matrix** — the record names modules by informal label, not path. My closest
  reconstruction gives 110; plausible variants give 114, 123 or 127. The substantive claim (zero
  regressions) is confirmed; the number is not traceable. See finding 13.
- **Agentic "28 failed, 1846 passed"** — I measured 29/1845. The extra failure is
  `tests/test_cli.py::TestCmdInitDevMode::test_dev_creates_symlinks_for_commands`, which asserts the
  resolved checkout path contains the literal string `agentic-mbse`. Re-run from a directory named
  `agentic-mbse`, it **passes**. The record's figures are correct; my extraction path differed.

### Obligation 6 — the three surfaced items

1. **Artifact-source manifest import constraint — accurate, pre-existing, independently reproduced.**
   I hit it identically: `verification/capture_baseline.py` resolves its history at import through
   `verification/artifact_sources.py`, which requires `STOP_PARSER_ARTIFACT_SOURCE_INPUTS` and a declared
   `extracted/codegen/…` root, and no committed script builds that manifest. Running leg 2 "through the
   committed validators" is impossible from a plain worktree; building a throwaway extraction was the
   correct call, not a shortcut. No owner decision needed before Phase 2. Phase 5 should note that the
   manifest builder is still uncommitted.
2. **Extraction-only default suite at `C_base` — accurate, pre-existing, reproduced exactly.** Without the
   manifest: 6 collection errors, in precisely the six modules named
   (`test_ast_dispatch_invariant`, `test_exact_route_fingerprint_stability`, `test_hierarchy_resolver`,
   `test_stop_parser_documentation_contract`, `test_v6_snapshot_inventory`, `test_check_ledger_4a`), plus
   exactly 10 further failures — 9 in `test_self_binding_guidance_contract.py` and 1 in
   `test_check_proof_integrity.py`. Property of the audited base, not a regression. See finding 10 for the
   one consequence the record does not draw.
3. **Strict/lenient gap for Case 2 — accurate, and I reproduced it.** Under `strict=False` the `Cell[3]`
   fixture returns a graph carrying `[SI_OCCURRENCE_AMBIGUOUS, SI_OCCURRENCE_MISSING]` with all three
   `cells[i]__mass` attributes present and `picked` unresolved; it does not refuse. The design's behavior
   matrix records only "REFUSED — `SI_OCCURRENCE_AMBIGUOUS`", which is the strict arm. Pre-existing design
   silence, not introduced, and correctly surfaced rather than reconciled in the test. It does **not** block
   Phase 2. It **must** be resolved before Phase 4, because ledger row A5b states the transition as
   `SI_OCCURRENCE_AMBIGUOUS → SI_INDEXED_SOURCE_UNSUPPORTED`, and under lenient the true transition is
   "graph-with-diagnostics → pre-graph refusal". The reconciliation gate will otherwise read it as drift.

---

## Findings

### Major

**1. The indexed red-set tests never assert the authored reference or the root-relative location, and a
weak implementation demonstrably satisfies them.**
`tests/conformance/test_expression_evidence_integrity.py:456-533`.

Both red tests assert the diagnostic code and `diagnostic.detail.endswith("tests/fixtures/<name>/model.sysml:15: indexed source '#(...)' is recognized but not implemented")`.
Neither asserts `diagnostic.reference`, `diagnostic.source_file`, or `diagnostic.source_line`.

This is not hypothetical. The existing `SI_INDEXED_SOURCE_UNSUPPORTED` diagnostic at `C_base` — measured
by me on `indexed_bare_chain_operator` — carries `reference=None`, `source_file=None`, `source_line=None`,
and an **absolute** filesystem path inside `detail`. Because `endswith` on a relative tail also matches an
absolute path ending in that tail, the assertion cannot tell `root-0/model.sysml:15` from
`/tmp/…/tests/fixtures/…/model.sysml:15`. A Phase-3 implementation that simply routes the bare chain into
the existing diagnostic shape turns every red test green while delivering neither of the two things the
design requires.

The design is explicit: Case 1 "asserts pre-graph `SI_INDEXED_SOURCE_UNSUPPORTED` with the authored
reference and root-relative `file:line`" (`design.md`, the indexed red set), and ledger row A5a requires a
refusal "naming the authored reference". The plan's own stencil asserts `r.reference == "cells#(2).mass"`.
The delivered tests dropped that assertion.

*What should change:* assert `diagnostic.reference == "cells#(2).mass"` and
`diagnostic.source_file == "root-0/model.sysml"` / `source_line == 15` as separate fields, not as a
suffix of `detail`. The same weakness sits in the pre-existing
`test_valid_indexed_source_refuses_before_graph_with_exact_capability_diagnostic:363-380`, which asserts
`consumer_display == "<model>"` while `reference` is `None`.

**2. `test_the_permissive_boolean_index_marker_is_gone` cannot go green under the design's own Phase-2
deletion list.**
`tests/test_sysml/test_reference_use.py:66-79` (Agentic).

The body reads `data_models.ResolvedSemanticReferenceFact.__annotations__`. Plan Phase 2 orders
`ResolvedSemanticReferenceFact` **deleted** ("Atomic deletion: remove … `ResolvedSemanticReferenceFact`,
`has_index_segment` …"). Once it is gone, the attribute access raises `AttributeError` and the test stays
red — a correct implementation cannot satisfy it. Today it is red for the stated reason (the field exists),
so Phase 1's record is not wrong; the test is.

*What should change:* assert the *class* is absent, or guard with `hasattr(data_models, …)` so that
deletion is the passing condition rather than an error.

**3. The dynamic-`getattr` gate's scope does not match its documented scope, and its recorded red is
unrelated to this item.**
`tests/conformance/test_expression_evidence_ownership.py:230-241` (scanner `visit_Call` else-branch) and
`:268-271` (the test).

The module docstring says the scanner discovers "a non-literal `getattr` **in the raw-SysIDE module set**
(which is rejected outright, because its selector cannot be reviewed)". The implementation records
`<unreviewable>` for *every* non-literal `getattr` anywhere in `src/sysml_codegen`, with no module filter.
The single red it produces is
`resolution/models.py::ConcreteConstraintInput._resolution_field_matches_tag` — a Pydantic validator
looping over a literal tuple of its own field names (`resolution/models.py:318-330`). It reads no SysIDE
selector, it is entirely reviewable, and no design section names it for change.

As written, Phase 3 must either rewrite an unrelated validator or amend the gate to reach closure. Neither
is planned work.

*What should change:* restrict the dynamic-`getattr` rejection to the raw-SysIDE module set the docstring
names, or record `resolution/models.py` as a reviewed exception with its reason.

**4. The red set exercises the live arm only, where the design requires live plus admitted/capture for
both cases.**
`test_expression_evidence_integrity.py:456-533`.

Both red tests call `elaborated_pipeline.elaborate_model_paths` — the live arm. Case 1's capture arm exists
as a separate test (`…_writes_no_snapshot`), but neither case has an **admitted** arm, and Case 2 has
neither admitted nor capture. The design requires "live + admitted/capture" for every consumer row and, for
Case 1 specifically, "through the live, admitted, and capture arms". The file already has a working
admitted-arm pattern (`test_public_source_arms_preserve_the_same_evidence_refusal:185-224`) to copy.

### Minor

**5. The Agentic symbol-absence gate omits four of the seven identifiers the design orders deleted.**
`tests/test_sysml/test_semantic_selector_ownership.py:37-44`. `PERMISSIVE_SYMBOLS` covers
`has_index_segment`, `feature_reference_facts`, `feature_chain_facts` and three chain/reference-name
helpers, but not `extract_feature_refs`, `ResolvedSemanticReferenceFact`, `ExpressionRef`, or
`BindingInfo.references`. I confirmed all four exist at `A_base`
(`sysml/expression.py`, `sysml/data_models.py`, `sysml/types.py`). Close in Phase 2.

**6. The Codegen ownership manifest's `closure_proof` strings are unverified claims.**
`test_expression_evidence_ownership.py:68-119`. All four `REVIEWED_ROWS` name a proving test; all four name
tests that do not exist yet (e.g. `test_deep_override_mapped_index_refuses_at_the_path_factory`).
`test_every_reviewed_row_names_a_closure_proof:261-265` only checks the string is non-empty. The consumer
table in the sibling file has exactly the right check —
`test_every_named_proof_in_the_consumer_table_resolves:650-658` — and the ownership manifest should adopt
it once those tests land.

**7. Off-route reachability is proved by direct imports only.**
`test_expression_evidence_ownership.py:312-325`. `_imports_of` parses one file, so an off-route module
reached two hops from a public arm passes. The design requires exclusions to be "mechanically reachable
from the public roots rather than prose assertions". Must become transitive before Phase 4's closure.

**8. Leg 3's ledger-ownership check substring-matches the whole ledger file.**
`tests/conformance/test_probe_fixture_lock.py:140-158`. It asserts `locked_path in ledger`,
`row["sha256"] in ledger`, `current in ledger` — three independent substring tests against the entire
document. A hash appearing in an unrelated row satisfies it. Parse the row for that path and check the
hashes within it.

**9. Case 2's lenient parameter is red for a reason the design does not record.**
`test_expression_evidence_integrity.py:496-533`, `[False]` case. It fails `DID NOT RAISE`, not
`SI_OCCURRENCE_AMBIGUOUS`. The stated reason reproduces in the strict arm — the arm the design's matrix
describes — so the phase's stop rule did not need to fire, and surfacing rather than reconciling was
correct. But the record's blanket sentence "Each red is red for its stated reason" is true of the strict
arm only. Resolve with the design amendment in surfaced item 3 before Phase 4.

**10. The new committed lock check's leg 1 runs only in the artifact-extraction lane.**
`tests/conformance/test_probe_fixture_lock.py:62-68` (`history_root` fixture). Without
`STOP_PARSER_ARTIFACT_SOURCE_INPUTS`, 2 of the 12 tests ERROR
(`test_recorded_probe_commit_parentage_holds`, `test_every_locked_hash_recomputes_against_the_named_historical_tree`)
while the other 10 pass. The failure is loud, not silent, so the design's "fail loudly rather than skipping"
holds. But the residual gap the design says this check closes is closed only where the manifest exists —
which, per surfaced item 1, no committed script builds.

**11. `pytest.raises(Exception)` and a class where an instance belongs.**
`tests/test_sysml/test_reference_use.py:80-88`. The broad catch is narrowed by the
`caught.value.code is …INDEXED_REFERENCE_UNSUPPORTED` assertion, so it is not vacuous. But it passes
`module.IndexedReferenceUse` — the class — to `build_aggregation_term`, and it does not prove the docstring's
claim that "refusal happens before term construction". Tighten to `pytest.raises(SemanticEvidenceError)`
over a constructed instance in Phase 2.

### Informational

**12. The lock has seven non-fixture rows, not six.** `verification/fixture-manifest.json` is the seventh.
Leg 1 covers it (it recomputes against `20f9e60a`), so every locked byte is still covered by exactly one
leg. But `test_locked_rows_split_into_fixture_inputs_and_verification_code:127-137` classifies it as a
"fixture input" via its `or path.startswith("verification/")` clause, which would silently absorb a future
verification **code** row into the wrong class. The design's "six non-fixture rows" phrasing is imprecise
for the same reason.

**13. The record's "125 passed" D1-D4 figure is not traceable.** It names modules by informal label. Record
the paths.

**14. Retracted concern.** I initially flagged `_spy_on_expression_consumers` (`:417-429`) for spying
`SysMLDataExtractor.extract_calculation_definitions`, which at `C_base` runs unconditionally before
`_build_instance_graph` (`orchestration/elaborated_pipeline.py:149-155`) — apparently making
`assert not consumers.called` unsatisfiable. Design D7 step 2 resolves it: the inventory must "refuse every
`IndexedReferenceUse` **before** calculation-definition extraction". The spy is on the correct seam.

### Vacuity sweep

Every new test was checked for empty iteration, over-broad exception catching, and self-comparison.
Non-vacuous, with anti-vacuity guards that I verified actually fire:
`test_a_clean_module_produces_no_selector_reads`, `test_every_ast_evasion_mutation_is_discovered`
(5 parameters), `test_off_route_modules_are_inventoried_and_present`,
`test_the_scanner_finds_each_reviewed_selector` / `…_ignores_an_unrelated_attribute` (Agentic), the lock
module's row-count and path-uniqueness assertions (mutation-proved above), and
`test_every_named_proof_in_the_consumer_table_resolves`. The two soft spots are finding 11 and
`test_the_lock_file_is_never_rewritten_by_this_check:161-163`, which can only fail if another test in its
own module writes the lock — a guard rather than a measurement, and harmless.

---

## Fit for Phase 2?

Yes. The base is proved, the lock is verified on all three legs by a committed test that I could not make
pass vacuously, and the failure class is reproduced by kept tests that fail for the reasons the design
records — confirmed by running the elaborator myself, not by trusting the tests. D1-D4 is untouched.

Two carry-forwards. Findings 1 and 4 must be fixed **before** the Phase 3 work that turns those tests
green, or Phase 3 will certify against a weaker contract than the design states — and finding 1 is a
demonstrated escape, not a theoretical one. Finding 2 must be fixed in Phase 2 itself, because the
deletion it blocks is Phase 2's own work. Finding 3 needs a ruling before Phase 3 closure. Finding 9 and
surfaced item 3 need a design amendment before Phase 4's reconciliation gate.

**Not checked:** anything downstream of Phase 1. No Phase 2-5 gate, no artifact chain, no execution lane,
no Fusion or TEAx surface, no generated-package byte comparison. Per the owner-verbatim exclusion I did not
invoke the Agentic slow PDF/HTML corpus or the 15 paid/network cases, and I make no claim about them. I did
not run the Agentic scoped-strict command (its targets do not exist until Phases 2-3) or the Codegen
execution lane. I did not audit the correctness of the reviewed-selector manifest's *content* beyond
checking that its four rows name proofs and that the discovered set is non-empty — whether those four are
the right four is a Phase-3 design question. The product-lens ledger was not re-run for this phase; the
`audit3-F1` block remains open by design until Phase 5.

---

# Addendum — Targeted confirmation of the four Major closures

**Dated:** 2026-08-17
**Scope:** the four Major findings only. This is not a re-audit of the phase.
**Codegen:** `d257ef1` (was `e4e2693`) · **Agentic:** `8d27fb3` (was `85c7758`) · plan note `1d8a5c6`
**Independent extraction:** `/tmp/stop-parser-rev2/audit-extraction2/`, built fresh from the new commits
(`git archive` + `git bundle --all`); the original `audit-extraction/` is untouched.

**Result: all four Majors closed.** Each was verified by execution, not by reading the diff. Two bounded
residuals are recorded below as Informational; neither reopens a finding.

## Scope re-check at the new commits

| Check | Result |
|---|---|
| `git diff --stat 78a9beb9 d257ef1 -- src/` | **empty** |
| `occurrence.py` blob at `78a9beb9` and `d257ef1` | both `af721562512d5684ce3dd1c96624fbe3355a536d` |
| `git diff --stat 2171016d 8d27fb3 -- src/` | **empty** |
| `git diff --stat e4e2693 d257ef1` | 2 files: the integrity and ownership test modules only |
| `git diff --stat e4e2693 d257ef1 -- verification/ tests/fixtures/` | **empty** |

No production byte moved. The lock file, the ledger and all three fixtures are byte-identical to the
commit whose three legs I verified in the main audit, so that verification carries forward unchanged;
`test_probe_fixture_lock.py`'s 12 tests are green in the full suite below.

## Major 1 — exact-field assertions: **closed**

The two red tests now route every arm through one helper,
`_assert_named_indexed_refusal` (`tests/conformance/test_expression_evidence_integrity.py:477-499`), which
compares `reference`, `source_file` and `source_line` for **exact equality** and adds two guards against a
path leaking into the rendered message.

**I re-ran my demonstrated escape against that helper** by constructing diagnostics directly and calling it:

| Shape fed to the gate | Outcome |
|---|---|
| Today's weak shape — `reference=None`, `source_file=None`, absolute path in `detail` | **rejected** |
| Right code and reference, still no place, absolute `detail` | **rejected** |
| All three fields right, staged absolute path still leaking into `detail` | **rejected** |
| Full named contract (`cells#(2).mass`, `root-0/model.sysml`, 15, root-relative detail) | passes |

All twelve arm-parameterized red nodes route through this helper; the remaining three Codegen reds
(consumer table, selector manifest, deleted symbols) do not concern the diagnostic shape. **A Phase-3
implementation emitting `reference=None` plus an absolute path cannot go green anywhere in the red set.**

**Spot-verification of the shared-referent claim — measured, and it holds.** The implementer asserts one
`ROOT_RELATIVE_REFERENT` constant is correct for all three arms. I measured it on the plural fixture, which
refuses today in every arm:

```
live    strict=True : source_file='root-0/model.sysml' line=15 ref='cells#(2).mass'
admitted strict=True: source_file='root-0/model.sysml' line=15 ref='cells#(2).mass'
capture             : source_file='root-0/model.sysml' line=15 ref='cells#(2).mass'
rendered message contains '/tmp/' : False, in all three arms
```

The admitted and capture arms do map their private staged copy back through `staged_to_referent`. One
constant is correct for all three; the claim is measured, not assumed.

Also tightened, and I confirm it: `test_operator_wrapped_indexed_source_still_refuses_correctly` now pins
today's shape *exactly* — `reference is None`, `source_file is None`, `source_line is None`, and the literal
`//`-prefixed absolute `detail` — instead of the old `endswith`. That converts the weakness I flagged on
that test into a tripwire: Phase 3 cannot tighten this path silently.

## Major 2 — deletion-safety: **closed**

`test_the_permissive_boolean_index_marker_is_gone` (`tests/test_sysml/test_reference_use.py:66-83`) now
resolves the class by `getattr(data_models, "ResolvedSemanticReferenceFact", None)` and reads absent
annotations as empty. I verified all three states by mutating a copy of
`src/agentic_mbse/sysml/data_models.py` and restoring it (restored SHA-256 `090d79df78afe1d8…` verified
against `8d27fb3`'s blob):

| State | Result |
|---|---|
| Today — class present, marker present | **1 failed** (the recorded red) |
| Class present, `has_index_segment` field removed | **1 passed** |
| Class deleted outright, per Phase 2 | **1 passed** |

The test can now be satisfied by the deletion the design orders, and only today's state fails.

## Major 3 — re-keyed scoping rule: **closed, and the deviation is sound**

My instruction said "restrict the dynamic-`getattr` rejection to the raw-SysIDE module set". Taken
literally — keying on a direct `syside` import — that set would have been **empty**, because Codegen
reaches SysIDE only through `agentic_mbse.sysml.syside_adapter`. The implementer re-keyed on
"imports the adapter **or** reads a reviewed selector" and added
`test_no_production_module_imports_syside_directly` to prove the premise. That is the right call: it
preserves the rule's intent (bound the gate to modules that handle raw parser nodes) where the literal
instruction would have produced a vacuous scope. The deviation is measured and companion-tested.

Verified by executing the module's own scope function:

- computed set size **21**, and `raw_syside_modules() == RAW_SYSIDE_MODULES` is **True** — the recorded set
  is the measured set, not a hand-list;
- **21 of 74** production modules are in scope, so the rule is selective, not "everything";
- `resolution/models.py` is **out** of scope (`adapter_import=False`, no reviewed selector), so the spurious
  red I flagged is gone — `discovered_reads()` now yields **zero** dynamic-`getattr` entries;
- the two modules the brief asked about are in scope for a real reason, and it is the adapter clause doing
  the work rather than a selector read: `extraction/computed_attribute_extractor.py` and
  `extraction/feature_metadata.py` both show `adapter_import=True` with an empty selector set. Keying on
  selectors alone would have missed both. Contrast `usage_extractor.py`
  (`selectors=['operands','referent','target_feature']`) and `hierarchy_resolver.py` (`['operands']`), which
  qualify either way. The 21-module set is right.

The five evasion mutants each now carry `_ADAPTER_IMPORT`, and
`test_every_ast_evasion_mutation_is_discovered` asserts `is_raw_syside_module(source)` before scanning — so
the mutants are tested *inside* the scope the gate was narrowed to, which is exactly the trap a scoped gate
must avoid. All five still die; the whole ownership module is green in the suite below. Both anti-vacuity
guards are present and meaningful: `test_a_clean_module_produces_no_selector_reads` (scope admits nothing
spurious) and `test_a_clean_module_is_not_in_the_raw_syside_set` (scope does not admit everything).

`test_no_dynamic_getattr_survives_in_the_raw_syside_module_set` correctly leaves the red set — it is an
anti-evasion gate, not a red-set member, and its former red was the unrelated Pydantic validator.

## Major 4 — three-arm coverage: **closed**

Both cases are now parameterized `("live", "admitted", "capture") × strict ∈ {True, False}` through
`_elaborate_through_arm` (`:459-473`), which uses the real `admit_sources` context manager for the admitted
arm and the real `capture_instance_graph_snapshot` for capture. Case 1's snapshot assertion is preserved
and strengthened: `assert not output.exists()` now runs in **every** parameter of the main test rather than
in a separate single-arm test, and Case 2 gained the same assertion.

Every arm is red for its stated reason — measured, not assumed:

| Node | Observed failure |
|---|---|
| singular, all 6 (`{True,False}-{live,admitted,capture}`) | `DID NOT RAISE` — the zero-diagnostic graph, and the sealed snapshot in the capture arm |
| plural `True-{live,admitted,capture}` | got `[SI_OCCURRENCE_AMBIGUOUS, SI_OCCURRENCE_MISSING]`, expected `[SI_INDEXED_SOURCE_UNSUPPORTED]` |
| plural `False-{live,admitted}` | `DID NOT RAISE` — the documented lenient-delivery gap (audit Minor 9) |
| plural `False-capture` | `AMBIGUOUS…` — correct: the capture arm seals through the admitted route, which the design fixes at strict, so `strict=False` is a duplicate strict run |

No arm fails for a fixture, license, import or harness reason.

## Spot-check of the updated completion-record figures

Every figure reproduces exactly from my own extraction of the new commits:

| Claim | Measured |
|---|---|
| 25 red nodes — 15 Codegen / 10 Agentic | **confirmed**, node IDs match the recorded list exactly |
| Codegen suite `15 failed, 2340 passed, 34 skipped` | **15 failed, 2340 passed, 34 skipped, 94 deselected** |
| Agentic fast suite `28 failed, 1846 passed` | **28 failed, 1846 passed, 1 skipped** (run from an `agentic-mbse`-named path, per the main audit's note) |
| D1-D4 + retained harness `162 passed`, paths recorded | **162 passed**, running the 15 paths the record now names |

Informational 13 is closed: the module paths are recorded and the figure is now reproducible.

## New informational notes (neither reopens a finding)

**I-15. The rendered-message path guards are literal, and one bounded gap remains.**
`_assert_named_indexed_refusal:498-499` guards with `"/tmp/" not in rendered` and
`not diagnostic.detail.startswith("/")`. I probed the edge: a `detail` embedding a **non-leading**,
**non-`/tmp`** absolute path (e.g. `"… at /scratch/stage9/model.sysml:15 …"`) **passes** the helper, while
the realistic `/var/tmp/` variant is rejected. The three structured fields are still exactly asserted, and
`admit_sources` stages under the system temp directory, so the realistic staged-path leak is caught. Closing
the gap properly would mean asserting the rendered message *contains the root-relative referent and no
absolute segment* rather than blacklisting two prefixes. Worth doing when Phase 3 rewrites the diagnostic.

**I-16. The scope rule's second clause is partly self-referential.**
`is_raw_syside_module` admits a module that reads a reviewed selector, so a module that receives raw parser
nodes as arguments, imports no adapter and uses only dynamic `getattr` would sit outside the dynamic-`getattr`
gate. No such module exists today — I checked all 53 out-of-scope modules and the only dynamic `getattr`
among them is `resolution/models.py`, which reads its own declared field names. `test_the_raw_syside_module_set_is_the_recorded_one`
makes any drift visible at review time, which is the right mitigation for a bounded hole.

**Still open and carried forward:** audit Minors 5-11 and Informational 12 and 14, unchanged and correctly
placed as Phase 2-4 work by the implementer's note. Minor 9 and surfaced item 3 (the lenient arm of Case 2)
still need a design amendment before Phase 4's reconciliation gate.

**Not checked in this addendum:** everything outside the four closures. I did not re-verify the three lock
legs by hand (their inputs are byte-identical to the commit where I did), did not re-run the lock mutation
suite, did not re-examine `deep_cross_scope_probe`, the static baselines, or any Phase 2-5 surface.

**Fit for Phase 2: yes.** The two closures that had to land before Phase 3 (Majors 1 and 4) are in the kept
tests now rather than promised, and Major 2's fix is in the file Phase 2 will edit first.
