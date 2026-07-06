# Audit: Return-Style & Bare-Parameter Extraction (SC-2)

**Verdict:** PASS (Certify)
**Audited:** 2026-07-05
**Branch:** upstream-findings-epic
**Commit:** 559a0bb
**Companion:** agentic-mbse A-2 stencil fix — commit 6dbdf1b on branch upstream-findings-sync (see caveat)

---

## Summary

The item delivers exactly what the spec and design specify. The fix is one honest
predicate replacing a proxy (`is_instance(AttributeUsage)` → `_is_parameter_member`)
at both filter passes, a raw-member V8 pre-scan for the anonymous return, and a V7
reword. All four parameter styles extract with correct I/O in the committed snapshot;
style B compiles, style D is absent (degraded, as designed). Docs and REQ tags move in
lockstep. The one adjudicated deviation (V8 keys off `ReturnParameterMembership` +
empty `declared_name`, the authorized B4 fallback) is recorded, probe-evidenced, and
sound.

Two verification limits, neither blocking: the harness could not run `uv run pytest`
(sandbox approval), so test-green rests on recorded evidence plus direct snapshot/code
inspection; and the agentic-mbse repo is outside this session's working directory, so
the A-2 fix was checked against recorded plan evidence, not read directly. Item 12
re-verifies A-2 as an explicit gate.

## Findings

### Plan completion

All four phases verified complete.

- **Phase 0 (probes)** — recorded in `plan.md` Phase 0 Completion. The B4 refutation
  is real and correctly reasoned: syside synthesizes `name='result'` for an anonymous
  return, so the design's primary "direction-Out + empty `sanitize_name`" rule would
  have both failed to fire *and* admitted a garbage `result` output. The adopted key
  (`ReturnParameterMembership` owned member with empty `declared_name`) is the design's
  named fallback, tightened so a named `return y` is not also rejected. Probe scripts
  committed under `probe/`.
- **Phase 1 (code)** — predicate at both sites, V8 pre-scan, V7 reword. Verified in the
  diff (below).
- **Phase 2 (capture + I1)** — snapshot committed; I1 verified timestamp-only and
  reverted. `git show --stat 559a0bb` confirms only `return_styles` +
  `anonymous_return` fixtures added; no existing snapshot or `baseline_outputs/**` file
  touched.
- **Phase 3 (docs + A-2)** — REQ rows, V7/V8 rows, BACKLOG note all present (below).

### Spec conformance

Each success criterion, traced to committed evidence:

- **Named `return y` extracts with output `y` + expression AST** — met.
  `extractor.py:204/242` now admit the ReferenceUsage(Out); the AST-capture block runs
  in the same loop. Snapshot: `NamedReturnB` OUT `[y]`, `compilation_results["NamedReturnB"]`
  present with `python_expression "(inputs.b * 3)"`, `fully_compilable`. Live test
  `test_named_return_autoimpls` asserts non-empty `output_expression_asts["y"]`.
- **Bare `in x` extracts as input** — met. Snapshot `BareInC` IN includes `x`; live
  `test_bare_in_extracted`.
- **`return attribute y` + body-assignment: single output, no double-ingestion** — met.
  Snapshot `StyleD` OUT `[y]` (count 1), `member_expressions` null, `calc_expressions`
  empty; direction-None body ref excluded by the predicate. Live
  `test_body_assignment_single_output_no_phantom` pins `y` once, `y not in
  member_expressions`, and no auto-impl.
- **`out attribute` control unchanged** — met. `ControlA` IN `[a]` OUT `[y]`, compiles;
  `test_control_style_unchanged`.
- **Anonymous `return` raises specific V8, before V7** — met. `extractor.py:267-284`
  pre-scan raises the name-the-result message before the `:290` V7 guard.
  `test_anonymous_return_raises_v8` asserts the V8 text and the absence of "zero output
  attributes". I3 (fires regardless of sibling outputs) holds — the scan is unconditional
  on the raw member.
- **New fixture + snapshot + conformance tests** — met. `return_styles` (4 styles +
  `rs_design` binding every input, full-pipeline) and `anonymous_return` (live-only);
  `test_return_style_extraction.py` (live + offline layers).
- **Existing snapshots + 4 baselines byte-identical** — met in substance. Recorded I1
  diff was `captured_at`-only (Item-2 provenance field) and reverted. Commit stat shows
  no existing snapshot/baseline in the changeset. B4 probe 1d confirms plain
  `out attribute` calc defs carry no `ReturnParameterMembership` member, so the V8 scan
  is negative on every existing fixture.
- **doc 01 canonical example now true** — met. `01-extraction.md:32-35` teaches
  `in capacity : Real; in unit_cost : Real; return total_cost : Real = capacity *
  unit_cost;` — bare-`in` + named-`return`, precisely the forms the filter relaxation
  now extracts. Correctly resolved by making the code match the doc (no example edit),
  as the design directed.
- **V7 no longer claims "not yet extracted (Item 3)"** — met. Reworded in both
  `extractor.py:290-296` and `modeling-assumptions.md:350`; the doc adds a V8 row.
  Grep for "not yet extracted" across `src/` and `docs/` → zero hits. (Two residual
  "Item 3" strings in `src/` are an unrelated COST-PATTERN reference, not this epic.)
- **Six IFE calc defs work in original return form** — satisfied by design, per the
  spec's spec-review evidence (all six were inline `return`, fusion-tea `8852afcf`); the
  four-styles fixture covers the same inline-return shape. Live IFE re-run was correctly
  demoted to opportunistic (D6).
- **agentic-mbse impact recorded** — met. A-2 specified and applied (see caveat);
  Level-6 output-style check recorded for Item 12 in `spec.md`.

Non-goals respected: no body-assignment expression capture (deferred to BACKLOG),
no multi-output return, no constraint/alias/type-index work.

### Design conformance

Implementation follows the design.

- **D1** one shared `_is_parameter_member` at both sites — verified `extractor.py:316-332`,
  called at `:204` and `:242`. I4 holds (identical predicate both passes).
- **D2** V8 as a standalone raw-member pre-scan before V7 — verified `:267-284`,
  independent of the relaxed predicate, over `elem.owned_members`.
- **D3** full-pipeline fixture — `rs_design` binds every input; snapshot carries
  `calc_usages` and `design_attributes`.
- **D4/M2** `compilation_results` pins auto-impl offline — snapshot keys are
  `ControlA/NamedReturnB/BareInC`, `StyleD` absent. `test_style_b_compiled_style_d_absent`
  asserts presence/absence (format-stable, not "carries no compilation data").
- **D5** REQ-EXT-10/11/12 — all three rows real in `01-extraction.md` and
  `verification-matrix.md`, each pointing at `test_return_style_extraction.py`.
- Invariants I1–I5 each map to a committed assertion or the reverted-diff evidence.

The predicate is exactly two sites; nothing else in extraction changed semantics.
`_get_direction`'s harmless `"Return"` substring branch was left as designed.

### Code integrity

No slop, no failure-dishonesty. The change reads as native.

- `_is_parameter_member` is a clean predicate extraction, one job, docstring states the
  contract and the I2 rationale. No mode flags, no sprawl.
- V8 pre-scan raises loudly with an actionable message — no silent fallback. It keys on
  `type(owning_membership).__name__ == "ReturnParameterMembership"` (a string type-name
  check) rather than `adapter.is_instance`; reasonable, since the target is a membership
  edge, not a Usage, and the adapter's `is_instance` covers usages. `sanitize_name(None)`
  returns `""` (verified `qualified_names.py:23-24`), so the empty-`declared_name` guard
  fires correctly on the anonymous case and skips named returns.
- New tests use real SysML fixtures through the live extractor and the committed
  snapshot — no mocks (R1 mock-ban respected).
- `_is_parameter_member(self, member: Any)` is annotated to hold mypy at the 109
  baseline; recorded and sound.

## Certification

Checked and marked:

- Read spec, design, plan, epic Item 3 + R1/R2/R3.
- Verified the extractor diff is exactly: predicate at `:204`/`:242`, V8 pre-scan, V7
  reword, one new helper — nothing else.
- Read the committed `return_styles` snapshot directly: four styles, correct I/O, style B
  compilation present / style D absent.
- Verified V8/V7 wording in `extractor.py` and `modeling-assumptions.md`; V8 row added;
  REQ-EXT-10/11/12 rows real in doc 01 and the verification matrix; doc 01 canonical
  example is now true; BACKLOG follow-up present.
- Confirmed no mocks in the new tests; confirmed no "not yet extracted" residue.
- Scope of 559a0bb (22 files) is all in-scope: extractor, fixtures, tests, docs, capture
  script registration, probe scripts, plan, CURRENT_WORK.

Marked complete: spec success criteria (all met on committed evidence), plan phases 0–3
(already `[x]`, re-verified). Epic Item 3 heading may be flagged ✅ — but see the two
open verification limits below; the epic-level mark should note them.

### Open verification limits (non-blocking)

1. **Tests not executed.** `uv run pytest` / mypy / ruff require an approval this
   non-interactive session cannot grant. Green rests on the recorded gate (1857 passed /
   4 skipped / 5 xfailed; mypy 109, ruff 21) plus direct inspection of the snapshot and
   the code paths the tests assert on. No contradicting evidence found.
2. **A-2 not read directly.** `~/1cfe/agentic-mbse` is outside this session's working
   directory; git and file reads against it are sandbox-blocked. The A-2 fix (inline
   `return result : Real = <expr>` replacing the body-assignment stencil at
   `stencils.md:39-41`, commit 6dbdf1b) is verified only against `plan.md` Phase 3 and
   the commit message. The "grep the skill dir — nothing else teaches the broken pattern"
   task could not be run. **Item 12 re-verifies A-2 as an explicit success criterion**,
   so this is backstopped; flagged here so it is not assumed done.


---

## Orchestrator close-out (2026-07-05)

Both verification limits were independently covered by the orchestrator:
1. Gate re-run before commit 559a0bb at the exact committed state: 1857 passed / 4 skipped /
   5 xfailed; ruff 21; mypy 109 (== baseline).
2. A-2 diff reviewed directly before committing agentic-mbse 6dbdf1b: body-assignment form
   replaced with inline return in stencils.md:39-41, exactly the spec'd wrong→right change.
   Item 12 still re-verifies as its own gate.

Item 3 complete: **PASS**.
