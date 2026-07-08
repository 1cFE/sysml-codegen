# Audit: TRUTH-DEBT Item 6 — D3 Hygiene Tail

**Verdict:** PASS-with-findings
**Audited:** 2026-07-08
**Branch:** truth-debt-epic
**Commits:** c1e010d, a2bc4d7, 295598d, b951c3c, 53653a7, 8a6697e

---

## Summary

Three of the four sites (loader load-bearing fields, aggregation-compile `.replace()` collision,
registry `type_map` "Any" skip) are hardened correctly: each new choke/fix was traced against the
actual code, each test's expected value was hand-verified against the real logic (not just read
as claimed), and every fires-on-shape test pairs with a silent-on-clean sibling with an
independently-anchored expectation. Site 4 was reclassified with real, well-evidenced corpus data
(fires on 5/15 real fixtures) and a named BACKLOG filing — the right engineering call, but the R4
process label "RECLASSIFIED" is a stretch of what R4/spec.md define reclassification to mean (a
**non-reproducing** finding), which the verdict document itself half-acknowledges. Docs and the
verification matrix match code behavior exactly, and the recount (259 = 258 PASS + 1 UNTESTED,
index MF 9/9 / REG 9/9 / SNAP 20/20) is independently reproducible from the file as committed. No
blocking defects found.

## Findings

### Plan completion

All phases verified complete against the actual diff, not just the plan's checkboxes:

- **Phase 0** — `probes/verdict.md` present with per-site reproduce/scan/disposition, matches
  Phase-0-completion notes in `plan.md`. Verified.
- **Phase 1 (Site 1)** — `snapshot/loader.py:53-96` adds `_require`/`_require_binding_type`;
  routed at `:315` (`python_type`), `_require_binding_type` call for `binding_type`, `:372`
  (`parent_part_path`), `:373` (`qualified_name`, raise), `:375` (`owning_part_def_qn`), `:390`
  (design-attribute `qualified_name`, raise). Matches plan claim exactly.
- **Phase 2 (Site 3)** — `generation/registry.py:57-65`, `else` branch on `_collect_exit_point_
  primitive_types`'s `if wrapper:`. Matches.
- **Phase 3 (Site 4)** — no code change, reclassification recorded in `BACKLOG.md`. Matches
  "Not implemented" plan claim.
- **Phase 4 (Site 2)** — `resolution/graph_builder.py:1553` (`re.sub(rf"\b{re.escape(ref)}\b", ...)`
  in place of `.replace()`). Matches. The plan's noted deviation (lambda → plain re.sub to dodge a
  mypy "Cannot infer type of lambda" finding) is consistent with the code as committed — no lambda
  present.
- **Phase 5 (docs)** — REQ-MF-09 / REQ-REG-09 / REQ-SNAP-20 rows present in their reference docs
  and in `verification-matrix.md`, worded consistently with the actual code behavior (see Design
  conformance below).

### Spec conformance

- **SC1** (each site fires-or-reclassifies with fires-on-shape test): met for sites 1/2/3; site 4
  reclassified — see the R4-labeling finding below.
- **SC2** (silent-on-clean sibling per new diagnostic): met. `test_clean_attr_dict_no_warn`,
  `test_clean_usage_dict_no_warn`, `test_clean_design_attribute_no_warn` (site 1);
  `test_float_exit_point_no_warn` (site 3); `test_disjoint_ref_names_unchanged` (site 2, a
  no-regression sibling rather than a no-warn sibling, correct since site 2 is a fix not a
  diagnostic).
- **SC3** (INV-6 preserved): per Phase-0 corpus scans (0 hits sites 1-3, `probes/verdict.md`) and
  the orchestrator-verified baseline run (16 passed, byte-identical) at 8a6697e. Site 4's
  reclassification is precisely what keeps INV-6 intact (a mechanical WARN there would have fired
  on 5/15 fixtures).
- **SC4** (suite green / ruff / mypy not worse): orchestrator-verified at 8a6697e — 2107 passed / 4
  skipped / 0 xfailed, ruff 17, mypy 97, cited per task instructions as already re-run live.
- **`[HARD]` fires-on-shape independently anchored**: verified by hand-tracing, not just reading
  the docstring claims —
  - Site 1: expected values (`"Any"`, `UNBOUND`, `""`, `None`) are the function's own documented
    defaults, hand-typed into `_valid_attr()`/`_valid_usage()`/`_valid_design_attribute()` literal
    dicts with one key deleted — independent of the code under test.
  - Site 2: hand-traced the regex substitution logic myself: refs sorted by length so
    `cost_total` substitutes first (`"cost + inputs.cost_total"`), then `\bcost\b` cannot match
    inside `cost_total` because `_` is a `\w` character (no word boundary before the embedded
    `cost`) — so the standalone `cost` token is the only remaining match. Result:
    `"inputs.cost + inputs.cost_total"`, exactly the test's hand-written expected string. Confirmed
    correct by direct trace, not just trusting the test.
  - Site 3: `_module_with_root_output(python_type="Any")` is a constructed `PipelineModule`, whose
    fields I verified against `resolution/models.py` (`PipelineModule`, `ModuleOutput`,
    `Compilability`) — the test's field names and types are valid, and the test would fail
    collection/construction if they weren't.
- **`[HARD]` corpus-scan-before-disposition gate**: `probes/verdict.md` documents the scan for
  each site (0/0/0/5 hits) run before the disposition was chosen, per Phase 0 (pre-hardening).
  Order is correct (probes precede the harden commits in the git log).
- **`[HARD]` R4 verify-then-fix**: sites 1-3 followed doc-intent → reproduce → fix → docs.
  Site 4 followed doc-intent → reproduce → **reclassify**, with the reclassification filed in
  `BACKLOG.md` with the actual evidence (fixture names, `default_value`s, root cause). See the
  labeling finding below — the substance is sound, the R4 vocabulary is stretched.
- **`[HARD]` baseline discipline (R3)**: no `scripts/capture_*.py` re-run mentioned or needed —
  all three hardened sites are latent-only or fix-without-behavior-change on the covered corpus;
  consistent with 0-corpus-hit scan results.
- Non-goals respected: `[SANITIZER-MERGE]`, `[SC11-IMPORT-REWRITE]`, `[DOTTED-LEAF-PART-BLIND]`
  untouched; `str(expr)` fallbacks in `expression_utils.py` untouched (out of scope per spec);
  no baseline changed wiring (0 corpus hits on sites 1-3, Site 4 not shipped).

### Design conformance

No `design.md` — spec explicitly parks these decisions for plan/implement with R4 evidence
(spec.md:14-18). The plan's Phase-0 dispositions substitute for a design stage and are internally
consistent with the spec's Open Questions:

- Site 1 field list and WARN/RAISE split matches spec `[INFERRED]` criterion exactly (a field
  "whose default masks a missing/corrupt value that changes wiring, keying, or type" → WARN;
  `qualified_name` as the sole keying field → RAISE). Confirmed principled, not arbitrary — I
  read the remaining `.get(default)` calls in `loader.py` (`_deserialize_compilation_result`,
  `_deserialize_calc_def`, `_deserialize_binding_info`, `_deserialize_redefinition_data`, and the
  benign fields on `AttributeInfo`/`CalcUsageData`/`DesignAttributeData`) and confirmed none of
  them affect wiring, keying, or type — they're metadata (`description`, `unit`, `source_line`,
  list fields) or fields that already raise via direct `d[...]` indexing (`output_name`,
  `compilability`, `calc_def_name`, `execution_order`) rather than defaulting.
- Site 2's mechanism (word-boundary `re.sub`, not a placeholder pass or diagnostic-only tripwire)
  matches the Phase-0 verdict's chosen mechanism and the spec's Open-Questions menu.
- Site 3's "latent-only tripwire, own diagnostic regardless of Site 1" matches spec's explicit
  warning against the "Site-1 fix removes Site-3's shape" trap (spec.md:141-148) — verified: the
  new `else` branch fires independent of any loader-sourced value, since the test constructs the
  `PipelineModule` directly, bypassing the loader entirely.
- Site 4's reclassification is evidenced (5 named fixtures, root-caused to short-vs-full-EQN
  dotted-path key mismatch, cross-referenced to the pre-existing deferred gap in
  `parameter_groups.py:672-682`) — this is a genuinely new discovery beyond what spec.md
  anticipated ("reproduces cleanly," spec.md:185), and Phase 0 caught it via the corpus-scan gate
  working as designed.

**Finding (advisory) — R4 reclassification label stretched.** `file: .project/backlog/BACKLOG.md:590`,
`.project/active/hygiene-tail/probes/verdict.md:132-140`. R4 (epic_truth_debt.md:142-150) and
spec.md's own Success Criterion ("R4: a site that does not reproduce is not fixed") define
"reclassify" as the disposition for a **non-reproducing** finding. Site 4 reproduces robustly — on
5 of 15 real corpus fixtures, confirmed independently against the live `OutputRegistry`
(`registry.scoped_lookup`/`alias_lookup` both return `None`), not a synthetic edge case. What
actually happened is R4 step (3), "fix at the root... not site-by-site" — the root fix needs a
cross-derivation check spanning two modules, which is design-level work out of a 1-day hygiene
item's scope, so it was correctly deferred rather than shipped as an INV-6-breaking mechanical
patch. The *engineering call* is right and the evidence is honest and complete (the verdict
document itself flags the tension by loosely paraphrasing R4 rather than quoting it). But calling
this "RECLASSIFIED" conflates two different R4 outcomes — "doesn't reproduce, so not a real bug"
vs. "reproduces, but the safe fix is out of scope, so deferred" — under one label. A future reader
skimming BACKLOG.md could misread Site 4 as *not a real bug*, when the evidence says the opposite:
it is a live, confirmed, 5-fixture-wide gap that happens to have no observable output effect
today. **Recommendation:** no code change needed; a one-line amendment to the BACKLOG entry's
opening sentence (e.g. "reproduces on 5/15 real fixtures; deferred as design-level work, not
reclassified as a non-bug") would remove the ambiguity for future readers. Advisory, not blocking
— the underlying decision and evidence are sound.

**Finding (advisory) — R2 agentic-mbse note lands in one doc, not all three.** `file:
docs/architecture/reference/05-module-factory.md`, `docs/architecture/reference/
20-module-registry-generation.md`. The plan's closing-gate R2 bullet (`plan.md:457-464`) reasons
about all three hardened sites' agentic-mbse impact ("zero... lockstep obligations") but the
explicit "agentic-mbse impact" section only appears in `27-snapshot-generation.md` (Site 1); grep
confirms neither `05-module-factory.md` nor `20-module-registry-generation.md` mentions
agentic-mbse at all. R2's intent (record the disposition, even "no change needed") is satisfied at
the plan level, which is a durable, epic-linked artifact — so this isn't a compliance gap, just an
inconsistency in *where* the R2 note lives across the three touched docs. Advisory, no action
required.

### Code integrity

No slop or failure-honesty issues found:

- `_require`/`_require_binding_type` (`loader.py:53-96`) are small, single-purpose, well-documented
  chokes. `_require`'s `raise_on_missing` flag is used at exactly 2 of 6 call sites for a
  well-justified reason (keying vs. non-keying); not parameter sprawl.
- `_require_binding_type` is a separate function rather than forcing `binding_type`'s falsy-check
  predicate into `_require`'s `field in d` predicate — correct call, since the two fields have
  different "missing" semantics (explicit key absence vs. falsy value).
- Site 3's `else` branch and Site 2's `re.sub` swap are minimal, localized diffs with no new
  abstraction, consistent with "harden at the cleanest choke, no cross-site abstraction" (spec
  `[NEED]`).
- No new silent fallbacks, no broad `except Exception`, no new `Optional`-papering-over-missing-data
  parameters introduced by this item.

---

## Requested live probes

I could not execute `pytest`/`ruff`/`mypy` directly in this session (sandbox denies `uv run
pytest ...`), so the below are hand-traced but not machine-executed. All expected-to-fail mutations
are RED→GREEN sanity checks the orchestrator should run to confirm the tests are not vacuous.

1. **Site 1, `qualified_name` raise removed.**
   File: `src/sysml_codegen/snapshot/loader.py:373`.
   Edit: change `_require(d, "qualified_name", "", context, raise_on_missing=True)` to
   `_require(d, "qualified_name", "", context)` (drop the kwarg).
   Expected failing test: `tests/unit/test_hygiene_tail_loader.py::test_missing_usage_qualified_name_raises`
   (no `SnapshotFormatError` raised; the `pytest.raises` block would fail to catch anything).

2. **Site 2, `.replace()` regression.**
   File: `src/sysml_codegen/resolution/graph_builder.py:1553`.
   Edit: change `compiled = re.sub(rf"\b{re.escape(ref)}\b", ref_to_inputs[ref], compiled)` to
   `compiled = compiled.replace(ref, ref_to_inputs[ref])`.
   Expected failing test: `tests/unit/test_hygiene_tail_agg_compile.py::test_nested_ref_names_do_not_corrupt`
   (compiled would become `"inputs.cost + inputs.inputs.cost_total"`, not the expected string).

3. **Site 3, warning suppressed.**
   File: `src/sysml_codegen/generation/registry.py:57-65`.
   Edit: replace the `else: logger.warning(...)` block body with `pass`.
   Expected failing test: `tests/unit/test_hygiene_tail_registry.py::test_any_exit_point_warns`
   (`_warns(caplog)` would be empty, failing the `any(...)` assertion).

4. **Site 1, silent-on-clean false positive.**
   File: `src/sysml_codegen/snapshot/loader.py:64`.
   Edit: change `if field in d:` to `if False:` (forces the warn/degrade path unconditionally).
   Expected failing test: `tests/unit/test_hygiene_tail_loader.py::test_clean_attr_dict_no_warn`
   (and the other two `_no_warn` tests) — `_warns(caplog)` would be non-empty on clean input.

---

## Certification

Checked and marking complete in `plan.md`/`spec.md`:
- Plan Phases 0-5: all verified complete against the diff (not just checkboxes) — marking `[x]`
  already present, no change needed (plan already shows Complete).
- Spec Success Criteria: all four boxes verified met (site 4 via reclassification, per spec's own
  allowed outcome) — spec.md checkboxes are currently unchecked (`- [ ]`); this audit verifies
  they are in fact satisfied. Marking `[x]` in spec.md.
- Epic `epic_truth_debt.md` Item 6: success criteria verified met; adding ✅ to the Item 6 heading
  and marking its success-criteria checkboxes `[x]`.

Gates (suite/ruff/mypy/baselines) are cited as orchestrator-verified at commit 8a6697e per the
task's instructions, not independently re-run by this audit (sandbox blocks `uv run`/`pytest`
directly). The four numbered mutations above are the residual live-probe verification this audit
could not perform itself.

**Verdict: PASS-with-findings.** Both findings are advisory (documentation/labeling precision);
neither blocks certification. No blocking findings.

ARTIFACT: .project/active/hygiene-tail/audit.md

---

## Orchestrator addendum: live probe results (2026-07-08, at 8a6697e)

All four requested mutations run live by the orchestrator; each applied, run, and reverted
(`git checkout` restored the file; final confirmation run green).

1. Site 1 `qualified_name` raise removed (loader.py:373, dropped `raise_on_missing=True`) →
   `test_missing_usage_qualified_name_raises` **FAILED** (RED). Reverted → green.
2. Site 2 regressed to substring `.replace` (graph_builder.py:1561) →
   `test_nested_ref_names_do_not_corrupt` **FAILED** (RED). Reverted → green.
3. Site 3 warning suppressed (registry.py else-branch → `pass`) →
   `test_any_exit_point_warns` **FAILED** (RED). Reverted → green.
4. Site 1 forced degrade path (loader.py:64 `if field in d:` → `if False:`) → all three
   `*_no_warn` tests **FAILED** (RED). Reverted → green.

Post-revert: all 13 hygiene-tail tests pass. None of the test pairs is vacuous.
