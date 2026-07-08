# Audit: Matrix Sweep Residue (TRUTH-DEBT Item 5)

**Verdict:** PASS-with-findings
**Audited:** 2026-07-08
**Branch:** truth-debt-epic
**Commit:** `ae69786` (range audited: `4039b47..ae69786`, 12 commits)

Every claim below was traced directly against source/tests/fixtures at HEAD with Read/Grep
(no delegated verification). File:line citations are lines I read myself.

---

## Summary

The item does what it claims. The two headline gates (REQ-EC-04, REQ-AS-06) are mutation-proven
with concrete, non-vague records; the PGD-03 reclassification is a real finding traced to source,
not a defect laundered as an over-claim; the Phase 5 sweep-residue filing is honest about its own
incompleteness with arithmetic that reconciles exactly; the REQ-OR-03 two-level warning reading
matches `src/` precisely; the reframes match their cited tests; and the recount (259 = 258 PASS +
1 UNTESTED, 66 distinct test files) reproduces exactly. Two of the five spot-checked "strengthened"
tests (REQ-REG-06, REQ-OR-02) oversell what they actually pin — not vacuous, but narrower than
their claimed R1 independence / coverage. Neither hides a production defect; both are advisory. One
pre-existing stale count in the matrix footer (untouched by this item) is also flagged.

Gates at `ae69786`, orchestrator-verified live: suite **2120 passed / 4 skipped / 0 xfailed**;
`ruff check src/` **17**; `mypy src/` **97** — matching the item's own recorded numbers.

## Findings

### Plan completion

Phase checkboxes are honestly differentiated: Phases 1–4 and 6 are `[x]`; Phase 5's steps 5.0–5.3
are correctly left `[ ]` (`plan.md:341-390`), matching the admission that only 2 of 32 residue rows
were individually deep-read. Checkboxes reflect actual state, not aspiration. No placeholder code or
TODOs in the touched test/doc files.

**REQ-EC-04 / REQ-AS-06 mutation records (`plan.md:479-513`).** Not re-executed by this audit (live
mutate+revert is out of audit scope), but the record is concrete, not vague: exact file:line
(`expression_compiler.py:217-223`), exact mutation (`raise` → `pass`), exact failure (`DID NOT RAISE
CompilationError`), plus a second AS-06 mutation forcing index-0 `alias_lookup` to `None` with the
real resulting assertion message and alias name. Meets the "record, not vague" bar — no live-probe
request needed.

### Spec conformance

Verified against `spec.md` Success Criteria and disposition table §A/B/C.

- **High-value pair strengthened + mutation-proven** — met (concrete record above).
- **17-strengthen list fully judged** — met; PGD-03 correctly reclassified (below), not force-fixed.
- **11 reframes byte-safe batch** — met. Directly spot-checked 4/12 (CA-01, SNAP-18, DM-04, AS-02):
  all MATCH their cited tests (detail below). Commit `860e4de` scoped to `verification-matrix.md`
  only.
- **5 citation fixes** — REQ-OR-03's citation confirmed incidentally (below); the other 4 not
  spot-checked to the same depth (advisory — plan's per-row Phase 4 notes are specific, no contrary
  evidence).
- **~46 unswept rows decided** — met via the spec's own "completed OR re-filed with a named count"
  clause. I re-derived the arithmetic myself:
  - `grep -c '^| REQ-'` → **259** total rows.
  - `grep '^| REQ-' … | grep -icE 'SHALL|ALL|every|never|exactly|warn|fire|count'` → **232**
    qualifying — exact match to the claimed D7 figure.
  - 232 − 167 (Item-7-swept, cited `BACKLOG.md:396-397`) − 33 (this item's Phases 1-4) = **32**.
  - `[ITEM5-SWEEP-RESIDUE-OVERFLOW]` (`BACKLOG.md:617`) names 21 rows by REQ id (count-correct) + 11
    unenumerated = 32, and states only REQ-GA-04/LVP-04 were individually read ("2 of 32," not
    oversold). No "sweep complete" / "all rows read" language anywhere in plan.md/spec.md; Phase 5's
    heading is "Deviation from plan, named" and the close-out calls it "the one place this item did
    not fully discharge its charter — named loudly, not silently" (`plan.md:668-669`).
  - **Advisory (cosmetic):** the BACKLOG entry's parenthetical gloss "(EPC 8 + GA 8 + LVP 9, minus
    REQ-EPC-05/07 … = 21)" subtracts only 2 from 25 (nets 23, not 21) — it omits that GA-04/LVP-04
    are also excluded. The final enumerated 21-row list is itself correct; only the inline arithmetic
    is imprecise.
- **Matrix recounted from rows; INV-B holds** — reproduced exactly: `grep '^| REQ-' … | grep -c
  'PASS |'` → **258**; `UNTESTED |` → **1** (REQ-PGD-06, `:398`); `DEFERRED |` → **0**. 258+1=259,
  no discrepancy. Summary block (`:6-13`) states 259/258/1/0 and "Distinct test files cited **66**" —
  matching, not stale. The 66 checks out: a loose `test_*.py` scan gives 67 (one prose mention
  overcounts), the backtick-cited convention gives 66; `test_formula_quoted_owner.py` appears exactly
  once (`:340`) and entered the matrix for the first time in Phase 4 (commit `d252752`), so the
  claimed 65→66 bump is real.
- **Suite green; baselines byte-identical** — orchestrator-verified at `ae69786` (2120/4/0), matching
  the item's own final numbers. Byte-identity trusted from `git status` records per phase; not re-run
  (out of audit scope), no contrary evidence.

**PGD-03 reclassification — traced to source, CONFIRMED real.** In `analysis/parameter_groups.py`:
`_derive_from_design_attributes()` (`:667`) groups by `file_path.stem` (`:672`) and `continue`s past
any attribute whose default fails to parse (`:676-688`) — a file whose attributes are *all*
non-literal-default contributes **zero** groups. Separately, `derive_groups()` merges unbound-param
groups into existing groups **by name**, not one-per-file (`:511-522`). I confirmed the
`chain_spike_model/library.sysml` fixture has only no-default `in` attributes and expression-default
`out` attributes (`area = length * width`, etc.) — all non-literal, so that file yields zero groups
while `design.sysml` yields one: 2 files → 1 group, exactly as the disposition claims. The reframed
matrix row (`:395`) states the `>=` floor with its exceptions and does not re-introduce "exactly one
group per file." The test still asserts `>= 1` (chain_spike, `test_parameter_group_deriver.py:219`)
and `>= 10` (catf_mfe, `:245`) — a force-committed `==` would have *failed* on chain_spike's
1-group-from-2-files reality, so reclassify-not-force-fix was the correct R4 call. This is a genuine
over-claim retirement, not a defect hidden behind a relaxed assertion. (The exact "12 groups" figure
for catf_mfe could not be re-executed — syside/pytest unavailable in-session — but the mechanism and
the chain_spike reproduction are solid enough to trust the disposition.)

**REQ-OR-03 two-level fix — traced to source, CONFIRMED.** `output_registry_builder.py:380-384`:
comment "Item 7 / D5: one WARNING count-summary…", then `if registry.alias_collision_count:
logger.warning(...)` — the builder emits one count-summary WARNING. `output_registry.py:129-130`:
on a genuine collision, `register_alias()` appends to `_alias_collisions` and calls `logger.debug(…)`
— DEBUG per collision, not WARNING. (Line 118's `logger.warning` is a *different* path — target
channel not yet registered — correctly not conflated.) Both tests are tagged REQ-OR-03 and pin the
right level at the right call site: `test_alias_duplicate_warns_first_wins` uses
`caplog.at_level(logging.DEBUG)` on a direct `register_alias()` call (`:272-297`);
`test_alias_collision_emits_one_warning_count_summary` uses `caplog.at_level(WARNING,
logger="…output_registry_builder")` on `build_output_registry()` (`:300-328`). The session's reading
is exactly right.

### Design conformance

No `design.md` for this item — `spec.md:8-9` states the disposition table IS the contract and design
is skipped. N/A.

### Code integrity

**Two strengthened tests oversell their R1 independence / coverage (advisory, not blocking):**

- **REQ-REG-06** (`tests/conformance/test_gen_registry.py:549-602`). Credited as "de-circularized
  (R1 anti-vacuity — the named offender)." The primary oracle (`:566-577`) does avoid calling the SUT
  helper — it walks `graph.modules` with a test-local `independent_type_map`. But I compared that map
  and walk against the source: `independent_type_map` (`:566-571`) is **byte-identical** to
  `type_map` in `src/sysml_codegen/generation/registry.py:44-49`, and the `field_name == "root"` walk
  is the same. So it's a re-typed copy, not an independent derivation — a bug shared between the copy
  and the original (e.g. a wrong wrapper name, or both dropping a new primitive type) is invisible to
  both. The test is **not vacuous**: `custom_types` is parsed from the *generated code* (`:585-602`),
  so it genuinely catches the most likely REG-06 bug (generation omits a graph-derived exit type).
  But the R1 "independently anchored" claim is stronger than what the test delivers. **What should
  change:** either derive the expected set from a genuinely different signal (e.g. the generated
  primitives module, or field type annotations) rather than a hand-copied `type_map`, or soften the
  row/plan wording from "de-circularized" to "duplicated-but-not-called."

- **REQ-OR-02** (`tests/conformance/test_output_registry.py:183-195`). The plan (`:169`) and spec
  (`spec.md:107`) describe this as "cover the 4th lookup (`scoped_alias_lookup`)." The
  `not hasattr(registry, "resolve")` half (`:195`) is a real negative-existence assertion — good. But
  the `scoped_alias_lookup` "coverage" is only `hasattr` (`:190`) + `callable` (`:194`) — trivially
  true once the method exists, with zero behavioral exercise (no register-then-lookup hit/miss).
  **What should change:** add a behavioral register/lookup case here, or narrow the row/plan wording
  from "covers the 4th lookup" to "asserts the 4th lookup method exists."

**Three byte-identity-flagged rows — spot-checked, all genuinely independent (not pinning the mock):**

- **REQ-CA-07** (`tests/unit/test_computed_attribute_extraction.py:753-810`). Drives the real
  `extract_computed_attributes` (`:799`) with an `x = x + 1` self-reference; the mocks supply only
  AST node shapes and the raw feature-ref set, while the self-exclusion runs in real source
  (`computed_attribute_extractor.py:292-298`, which I read — subtracts the attr's own sanitized name
  from `input_names`). Asserts `compiled_expression is None` + `compilability == MANUAL_REQUIRED` —
  real behavior, hand-authored expectation. INDEPENDENT.
- **REQ-CA-11** (`tests/unit/test_graph_builder_computed_attrs.py:170-249`). Drives the real
  `_build_attribute_resolution_map` twice — registered-leaf-silent (`:171`) vs unregistered-leaf-warns
  (`:210`) — a proper fires-on-shape / silent-on-clean contrast pair (R1). Asserts the warning names
  the real cause (`orphan_cost` + `plant` + "no scoped alias registered", `:239-247`) and the retired
  Item-1 message does not fire (`:249`). Not a tautology. INDEPENDENT.
- **REQ-SR-05** (`tests/unit/test_stencils.py:634-659`). Drives the real `_generate_stencils` against
  `tmp_path`; asserts the file was upgraded (`:649`), exactly one backup exists (`:655`), and the
  backup content equals the *pre-regen* stub (`:656`) — that last assertion genuinely proves
  backup-before-regen ordering (a post-overwrite backup would hold the auto-impl, not the stub).
  INDEPENDENT.

**Reframe spot-checks (4/12), all MATCH:**

- **REQ-CA-01** (`:142` → "assign each attr exactly one enum member"). Cited test
  `test_computed_attributes.py`: `test_classification_exclusive` (`:94`) asserts each of 18 attrs has
  exactly one non-None enum member; `test_classification_exhaustive` (`:86`) treats
  `EXPOSE_CHAIN_TENTATIVE` as a *valid* member. So the dropped INV-F over-claim ("transient value
  never survives to a reader") is genuinely unpinned — dropping it is honest. MATCH.
- **REQ-SNAP-18** (`:497`). I independently confirmed both claims: `grep -rn generation_timestamp
  src/sysml_codegen/` → **zero** hits; `find … -iname 'pydantic_schema*.jinja*'` → **nothing** (the
  carrying template is deleted). Row's regression-guard framing is accurate. MATCH.
- **REQ-DM-04** (`:164` → "importable from its documented source file"). Narrowed from a broader
  parent-class claim; cited `test_data_models.py`. MATCH (importability-only framing).
- **REQ-AS-02** (`:76`). Row honestly states "as observed on the disjoint fixture cases exercised (no
  dual-match part-def case exists to show the short-circuit directly)" — matching the spec's rule not
  to manufacture a dual-match fixture. MATCH.

No slop (god functions, deep nesting, silent fallbacks) in the touched test/doc files — the changes
are narrowly scoped test additions and doc-text edits.

**Side finding (out of this item's scope, same document):** `verification-matrix.md:562`
("Related Documents" footer) still states "62 distinct test files cited … 44 in conformance/, 18 in
unit/ + integration/" — stale, inconsistent with the Summary block's correct 66. Phase 6's recount
updated the Summary block but not this footer line. Pre-existing drift, not this item's regression,
but worth a follow-on fix since it sits in the same recounted document.

---

## Certification

**Verified directly by this audit (own Read/Grep at HEAD):**
- Total rows (259), D7 qualifier (232), status recount (258/1/0), UNTESTED = REQ-PGD-06, distinct
  test files (66) with the 65→66 bump traced to a real Phase-4 citation.
- PGD-03 mechanism — read both derivation methods + the merge logic + the chain_spike fixture;
  confirmed the `>=` test assertions; confirmed the reframed row text.
- REQ-OR-03 two-level DEBUG/WARNING split — read both src call sites and both tests.
- 5 of 17 strengthens (CA-07, CA-11, SR-05 independent; REG-06, OR-02 advisory) — read each test and
  the relevant source.
- 4 of 12 reframes (CA-01, SNAP-18, DM-04, AS-02) — read row text + cited tests; independently
  grepped SNAP-18's src/template claims.
- Phase 5 arithmetic + honesty language — re-derived and read the BACKLOG entry.

**Trusted from the item's own record (not re-executed; no contrary evidence):**
- The EC-04/AS-06 live mutation spot-checks (record is concrete, not vague).
- The remaining 12 of 17 strengthens, 8 of 12 reframes, and 4 of 5 citations outside the sample.
- Byte-identity gate results per phase.

**Tracking updated:** `spec.md`'s 7 success criteria and `epic_truth_debt.md` Item 5's 4 success
criteria checked off; the epic Item 5 heading marked ✅. Nothing marked without the verification
above. Not committed (orchestrator commits).

**Verdict: PASS-with-findings.** Two advisory code-integrity findings (REG-06 copied-type-map,
OR-02 existence-only coverage) and one cosmetic arithmetic-gloss note; one pre-existing footer-count
side finding. None blocking — no production defect, no dishonest overclaim, and the one genuine
incompleteness (Phase 5's partial deep-read) is named loudly, not hidden.
