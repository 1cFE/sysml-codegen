# Audit: Independent conformance corpus and per-site codes (EXEC-SUBSET-CONTRACT Item 2a), Phases 1–2 (mid-run)

**Verdict:** Needs Work (one Blocker, small fix, to land before P3 closes)
**Audited:** 2026-10-18
**Branch:** sysml-codegen `subset-conformance` (base `b5663c07`); agentic-mbse `subset-conformance` (rebased on `main` with Item 4)
**Commit:** sysml-codegen `d553aebb`; agentic-mbse `f360c3f6`

Scope: Phases 1 and 2 only, against `plan.md`, `spec.md` and `design.md` rev 3. Phases 3–7 are not built and are not judged, except where a Phase 1–2 claim depends on them.

---

## The Point

Prove, with evidence independent of the screen, that the shared subset contract in agentic-mbse matches what this generator actually does, and make drift between them fail a test in sysml-codegen. Test volume is not the goal, and neither are tests that check the screen against itself (spec § Problem, [INFERRED], ratified by owner 2026-10-18).

Why: Item 1 checked the contract once, against 80 probe runs of codegen `b5663c07`. Nothing failed when the generator changed. Items 2b, 3 and 5 will tell modelers what will generate on the strength of this contract, so it has to be held to the generator mechanically. Owner gates bound the work: RG-1 (accept/refuse changes), RG-2 (String policy), RG-3 (merges, ADR filing), and P-0003 ("we do NOT create workarounds to accept bad models -- we follow what KerML, SysMLv2 and SysIDE support").

## Summary

The generator side is solid. A relaxed generator detector fails 17 codegen tests, every generator mutation test goes red when its mutation is made a no-op, accept/refuse is unchanged on all 350 model roots (checked independently against the base generator), and both suites match their baselines exactly.

The screen side is not yet held inside sysml-codegen. No codegen test compares the live screen with anything that can fail. With one screen recognizer switched off for the whole run, all 1401 codegen subset-profile tests pass, including the screen mutation test for that very shape. agentic-mbse's own rule tests do catch it, so the regression is not invisible across the pair, but the codegen suite, which is what the pre-merge gate runs, does not.

## Product Judgment

**Is this the right piece of work?** Yes. The corpus, the stored generator answers checked live, the tripwire and the generator mutations are what the point asks for, and nothing in the diff changes what the generator accepts or refuses (P-0003 and RG-1 respected).

The product-lens run (`product-lens.md`, block "audit (mid-run, Item 2a Phases 1-2)", gate DISPOSED) found two linked gaps, and I confirmed both by experiment:
- **audit-p12-F1:** codegen never runs the live screen on the cases and compares it with a stored answer. It trusts the `case.json` copies. That is the "two representations kept in sync by hand" smell, with the sync check living only in agentic-mbse. This is still true in the code.
- **audit-p12-F2:** the screen mutation test passes with its recognizer already dead. Still true; this is Blocker 1 below.

Neither contradicts an owner-grade statement, so the lens disposes rather than blocks. I grade F2 a Blocker on its own terms (a mutation test with a verified false pass, which spec B6 and the brief exist to prevent). F1 is the reason it matters: design D13 says the pre-merge run is what checks an extractor or evaluator change against the generator, and today's codegen tests cannot do that.

No earlier lens block is open.

## Blockers

1. **The screen mutation test passes when the screen is already broken** (`tests/conformance/subset_profile/test_screen_mutations.py:42-45`).
   - What is wrong: for each case it compares "agreement with the stored screen answer" (before) against "agreement with the live, mutated screen" (after). The "before" never runs the screen. If the live screen has already stopped recognizing the shape, before and after still differ, so the test passes without the mutation doing anything.
   - Evidence: I disabled `part-multiplicity/range` for a whole pytest session (plugin `/tmp/audit2a/scripts/exp_screen_drift.py`) and ran all of `tests/conformance/subset_profile/`: 1401 passed, including `test_screen_mutations.py[part-multiplicity/range]`. The same drift in agentic-mbse fails its `test_subset_profile_rules_instantiation.py` on all seven range cases.
   - Impact: spec criterion B6 ("disabling the screen's recognition makes its cases report a mismatch") is evidenced only on condition that agentic-mbse's suite has also passed. Inside codegen's suite, which is all the pre-merge gate runs (D13), a screen regression is invisible. The P3 agreement test as planned (pure, stored against stored) does not close this either.
   - What should change: compute "before" from an unmutated live screen run, or add a licensed codegen test that the live screen answer equals the stored one for every case (about 4 ms per case, design § Research Findings). The second also closes lens F1, and it lets the mutation test keep its current shape. Restate plan § "What we know works after Phase 2" to match.

## Advisory

Ranked by importance.

1. **The reach test cannot tell the `ExpressionInventoryError` converter from the catch-all** (`tests/conformance/subset_profile/test_site_reason_reaches_harness.py:146-149, :170`). The patched raise carries `INTERNAL_FAILURE_UNCLASSIFIED`, the same reason the `except Exception` branch assigns. With that converter removed (its exception name rebound so the branch never matches, plugin `exp_inventory_branch.py`), all 10 reach tests still pass. Impact: losing that converter would turn `SI_EVIDENCE_INCOMPLETE` into `SI_INTERNAL_DEFECT` and nothing would notice. Fix: give the patched raise a reason the catch-all never uses, or assert the code too. Every other converter branch is covered and each witness is distinct.
2. **The String omission is not yet observed at its seam** (`tests/expectations/subset_profile/cases/string-value-omission__*`). The seams assert "attribute node present, no entry point", which is also true of an unconsumed `Real` attribute (the P2.2 premise conflict, surfaced and parked to P4). So spec B7 is not met for `string-value-omission` yet. It was surfaced properly; P4 must close it or record the limit.
3. **Occurrence parity has a known break that no case shows.** P2.4 found that an anonymous `assert positive;` makes agentic-mbse's occurrence port abort while codegen's index builds, so ADR 0001 invariant 6 does not hold on that input. The case was left unpackaged pending the orchestrator call (commit `d553aebb`: P3 fixes agentic-mbse's copy). Until it lands, the parity test is green because the counterexample is not in the corpus. P3 should package the case together with the fix.
4. **agentic-mbse alone no longer pins its occurrence summaries.** The 34 `expected.json` captures were deleted (by design D6). The occurrence extractor is now checked against stored behavior only by codegen's parity test, plus four root tests and the screen replay in agentic-mbse. That is the intended design; it means an agentic-mbse change to `occurrence_extraction.py` relies on the pre-merge gate actually being run.
5. **The disagreement record's `owner` field names a work item, not a person** (`tests/expectations/subset_profile/disagreements.json`, every entry "EXEC-SUBSET-CONTRACT Item 2a P…"). The spec defines a recorded disagreement as having an owner. When P3 decides each row, give it a real owner.
6. **The screen mutation test counts any change in disagreement as "breaking agreement"** (`test_screen_mutations.py:44-47`), including a disagreement turning into agreement. No current subject can do that (every recorded disagreement has no refused screen finding), but the rule is looser than D5's "fails agreement". Fold into Blocker 1's fix.
7. **`test_tripwire.py` adds little.** `observe.generator_half` always applies the tripwire, so `test_generator_half.py` already runs every case tripwired and checks more (codes and reasons, not only outcome). The two self-tests of the tripwire are useful; the per-case loop is a weaker copy. Keep it if 2b needs the name, but say so.
8. **Stale text.** `evidence/versioning.md` § Not checked says the `v1` → `v2` bump lands later; it landed in P2.1. agentic-mbse `tests/test_subset_case_citations.py` `test_a_reproduction_is_refused_by_no_rule` docstring lists "an anonymous assertion by reference", which is not packaged. `plan.md` status line still says "(Phase 1)".

## Findings Detail

### Plan completion

Phases 1 and 2: every step's items exist in the code as the plan and its deviation notes describe. No TODOs, placeholders or stub bodies in the diff (searched). The recorded deviations (20-member `GenerationCode` with a required `code`, the projection refusal carrying its diagnostics, `scan_sites/2`, `case.json` `kind`/`description`/`line`, `[[rule.shape.unobservable]]`, four unwitnessed linked sites, `sys.monitoring` tracer, dc3 shapes mapped to the existing `candidate-es-*` models) are each justified in the notes.

- Step 2.4's screen mutation item is not certified: Blocker 1.
- Phase gate, re-run here: snapshots and oracle/batch files byte-identical to `b5663c07` (not only `d73a4fc5`); codegen licensed suite 4182 passed, 9 failed, 9 skipped, failures exactly the baseline's 9 IDs (the tenth baseline failure now passes, from Item 4); agentic-mbse all-extras suite 3875 passed, 5 failed, 8 skipped, 1 xfailed, failures exactly the 5 baseline IDs; codegen mypy clean, ruff 94; agentic-mbse mypy 88, ruff 118. All equal the recorded baselines.

### Spec conformance

Group A:
- A1 pin and test: met (`_upstream_pins.py`, `tests/conformance/test_upstream_pins.py`; the adapter refuses import on a mismatch, `subset_profile_adapter.py:29-34`).
- A2 version requirement: met in design D12's form (no package version identifies the contract; `evidence/versioning.md`). The package index was not checked, as the evidence says.
- A3–A5 mapping, `NO_REFUSAL`, keys test: met. `REASON_MAPPING` is hand-written, 14 entries (16 less the two retired shapes), not derived from the records at runtime.
- A6 every (reason, code) pair witnessed: met (`test_reason_mapping.py::test_every_mapping_pair_has_a_witnessing_case`), over stored answers that `test_generator_half.py` holds to the live generator.
- A7 renderer, off the generate route: met (unit test per reason; AST import-boundary test).
- A8 occurrence parity: met for every existing case, seed and corpus root, with a working mutation test and fail-by-name on missing inputs. See Advisory 3 for the known counterexample outside the corpus.
- A9, A10 staged ADR 0012, ADR 0001 (and P-0001, ADR 0016, fact-placement) amendments: met; each ends "Filing: owner, at merge (RG-3)" and the 0012 text names `test_occurrence_parity.py`.

Group B:
- B1 tripwire: met. Every generator-half observation runs with the three screen entry points rebound to raise, and a swallowed call still fails the observation. The generator imports no screen module (grep of `src/`).
- B2 refusing case per refused pair, B3 non-refused case or SA-1 per refused shape, B8 unconfirmed pairs, B9 retired shapes: met (`test_record_coverage.py`, agentic-mbse records and citation tests).
- B4 case families and dc3 shapes: met, with the dc3 deviation recorded (the scratch models are in no dc3 revision; `candidate-es-002/008/009` carry the provenance).
- B5 fixture classification: classification met; "screen reports zero refused on every generating fixture" is P3's licensed test and not done yet.
- B6 mutations: generator half met and verified (no-op neutralizer turns all 13 site tests red; a relaxed range site turns 17 tests red). Screen half not met: Blocker 1.
- B7 omitted/excluded observed at a seam: met for the three site rules' `other_expression_site` (calc usage outputs only `r`) and the NON_NUMERICAL catalog dispositions; not met for String (Advisory 2).

Groups C–F: not in scope.

### Design conformance

The implementation follows D1–D9, D12, D14 and D15 as placed. Invariants 1, 2, 4, 5, 7, 8, 9 and 10 hold in the code (9 and 10 verified independently, below). Invariant 6 holds for generator mutations; for screen mutations the comparison is against the stored generator answer as required, but the baseline flaw in Blocker 1 lets it pass for the wrong reason. Invariant 3 is P3's.

D13's statement that the pre-merge run is what checks an extractor or evaluator change against the generator is not delivered by the codegen tests that exist; see Product Judgment.

**Accept/refuse unchanged, checked independently.** I exported `src/` at `b5663c07` and ran `run_codegen` from it and from HEAD, with the same installed agentic-mbse, on 350 model roots (every generating or refusing fixture, the 37 batch fixtures, all 124 packaged cases, the 34-model seed). The generated/refused result is identical on all 350 (137 generated, 213 refused). Script: `/tmp/audit2a/scripts/outcomes.py`.

### Code integrity

- `GenerationCode` and the mandatory `code`: clean. Each of the 20 members names one family, the message text is unchanged, mypy enforces the keyword, and the E1 scan checks it. `_generation_error` in `generation/constraint_catalog.py` and `generation/modules.py` are pre-existing twins that both gained a `code` parameter; not new duplication.
- `cli/refusal.py`: small, typed, one function per carrier. `_project_or_fail` now splits the graph-refusal branch (carrying diagnostics) from the `TypeError`/`ValueError` branch; it still raises in both.
- The converters in `orchestration/elaborated_pipeline.py` now use `dataclasses.replace`, which removes the field-by-field copies that would drop a new field.
- Failure honesty: no new broad excepts or silent fallbacks in `src/`. The harness turns a coded-less refusal into a test failure rather than an answer (`observe.py` `GeneratorObservation.run`).
- Mutation tooling (`mutate.py`): the four unwitnessed sites' guards are real. I called `_multiplicity_indices` with a nonunique usage under `recording_sites` and the tracer recorded the site; the `reference_use.py:702` claim (only `decompose_aggregation_expression` calls it, and nothing calls that) holds by grep of both `src/` trees.
- Product-drift smells: "two representations kept in sync by hand" (live screen against stored `case.json`, Blocker 1 and lens F1) and "a test passes only because it selects one interpretation" (`test_screen_mutations.py`) both fired and are carried into the verdict.

---

## Certification

Checked:
- Both full suites licensed (`SYSIDE_LICENSE_KEY` from `.env`), compared by test ID with `evidence/baseline.md`; static checks in both repos.
- Snapshot byte identity and oracle/batch files against `b5663c07`; independent 350-root accept/refuse comparison against the base generator.
- Mutation strength by experiment: no-op generator neutralizer (13 of 13 site tests red), no-op recognizer disable (11 of 11 red), whole-run generator relaxation of the range site (17 red), whole-run screen regression of the range shape (0 codegen red, agentic-mbse red), reach-test converter removal (0 red), an unwitnessed site reached directly (tracer fires).
- Reach test against every converter branch of `elaborate_loaded_extractor`.
- Non-circularity: the mapping is hand-written; stored generator answers are captured by a manual helper that refuses a screen-disagreeing write without a hand-made record entry; no tool writes `disagreements.json`; the generator half never runs the screen.
- agentic-mbse still tests the screen on real models (both rule tests replay all 124 packaged cases; the citation test checks every cited case).

Marked: spec criteria A1–A10 and B1–B4, B8, B9 checked off. B5, B6 and B7 left open (reasons above). Plan checkboxes were already ticked by the implementer; I left them, and step 2.4's screen-mutation item is not certified by this audit. `CURRENT_WORK.md` updated to "needs work".

**Not checked:** groups C–F; the content of each of the 124 stored answers and 124 `case.json` screen answers beyond their tests (I reviewed the record, the mapping, the mutation record and a sample of answers, not every answer diff); whether each `generator.witnesses` list is complete; the 154 internal-invariant guards (spec Non-Goal); E2 scanner-mutation snippets beyond their passing tests; agentic-mbse script changes (`codegen_suite.py`, `isolated_tree.py`) beyond their tests; the staged amendment texts' wording; the agentic-mbse wheel contents (`uv build` not run).
