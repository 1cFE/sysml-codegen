---
date: 2026-07-18T19:20:48-07:00
researcher: Claude (5 parallel review subagents; every High/Medium finding reproduced or traced)
topic: "Code review of the open PR wave: sysml-codegen #9 (constraint-exec-epic @ 512786c) and agentic-mbse #11 (@ 54a95d2)"
tags: [research, code-review, constraint-exec, gap-close, pr-wave]
status: complete
last_updated: 2026-07-18
---

# Research: Open-PR Code Review — CONSTRAINT-EXEC Wave (#9, #11)

**Research Question:** general code bugs, gaps, and software-quality issues on the open PR branches,
beyond the already-filed findings (F1–F10 gap review, `[CONSTRAINT-ARCH-UNIFY]`,
`[ANON-ELIGIBLE-KEY]`, `[EXIT-PIN-SEAM]`, mypy baseline).

**Scope reviewed:** PR #9 src diff (42 files, ~4.9k insertions: analysis, generation + templates,
resolution/contracts/snapshot, CLI/orchestration/extraction) plus a test-quality sample of the
largest new test files; PR #11 src diff (11 files, ~2.7k insertions) at the pushed ref `54a95d2`.
Five reviewers, each instructed to verify findings concretely before reporting; "reproduced" below
means an executed reproduction, "traced" means a concrete code-path trace without execution.

## Summary

- **Four High findings, all in territory no prior review wave covered.** Two are wrong-verdict
  defects in the v3 executable profile (ordering comparisons admit non-numeric operands; negated
  asserts silently invert), one is a silent-evidence family in generated code (model formal names
  shadowing generated locals), one crashes from-snapshot rebuild on a valid snapshot (nullable-QN
  ADMIT filter).
- The Highs share one systematic shape: **a fact the schema deliberately captures that the decision
  or generation layer never consults** (operand category under ordering; `is_negated`; the generated
  scope's own names; anonymous identity in the demand collector). Guards check validity, not
  collision with the system's own machinery.
- Medium findings cluster at the **portability and diagnostic-fidelity seams**: named excluded
  locations leak absolute machine paths into fingerprints and contracts; recursive part containment
  silently truncates; a constraint demand can overwrite a calc-usage-derived design attribute's
  grouping; seal can produce packages that can never verify; the v3 loader breaks its own
  "never a raw KeyError" promise.
- **Overall quality is high.** Every reviewer independently reported disciplined work: fail-fast over
  fallback, real invariant guards firing before writes, deterministic ordering at every iteration
  point checked, correct Kleene semantics, byte-stable codecs, and an unusually strong test wave
  (hand-written literals, executed predicates, mutation pins). The defects below are the residue at
  seams the discipline didn't reach, not a pattern of sloppiness.

## High findings (recommend fixing before the wave merges)

### R-1 — Ordering comparisons admit non-numeric operand categories (PR #11) — reproduced live
`agentic-mbse src/agentic_mbse/sysml/executable_profile.py:521-525` (`_walk_comparison` ordering
branch); root cause `unit_compatibility` at `:164-195`.
The ordering path (`<`, `<=`, `>`, `>=`) gates only on `unit_compatibility`, which returns `"ok"`
for any pair of non-quantity categories. The category guards exist only in `classify_equality`.
Reproduced end-to-end via live syside extraction: `assert constraint { label1 < label2 }` (String
attrs) and `assert constraint { armed <= ready }` (Boolean attrs) both return **ADMIT with zero
diagnostics** — a string/boolean/enum ordering enters codegen as an executable numerical claim.
The golden matrix pins only two inequality rows (quantity/quantity, integer/real), so no test sees
this. This is an admit-by-fallthrough hole in a default-deny profile — the exact defect class v3
exists to prevent.

### R-2 — `is_negated` is captured but never consulted: negated asserts admit inverted (PR #11) — reproduced live
`agentic-mbse src/agentic_mbse/sysml/executable_profile.py:717-783` (`_evaluate_usage` reads only
form/identity/location/predicate); `ConstraintUsageFact.is_negated` populated at
`constraint_extraction.py:688`.
`assert not constraint { width < 5.0 }` extracts cleanly with `is_negated=True`; the profile ADMITs
with `effective_predicate` = the positive IR and no diagnostics. `effective_predicate` is exactly
what codegen lowers, and `UsageDecision` carries no negation flag, so the generated check asserts
the inverse of the model. Should at minimum be a named BLOCK, or fold the negation into the IR.

### R-3 — Reserved-name shadowing family in generated code (PR #9) — reproduced by executing generated code
`src/sysml_codegen/generation/predicate_compiler.py:260-271` and
`src/sysml_codegen/templates/constraint_module.py.jinja2:32-42`. Guards check model-derived formal
names only for `isidentifier()`/`iskeyword()`, never for colliding with the generated code's own
scope names. Three symptoms, one seam:
- **Formal named `value`** (natural: `in value : Real`): the emitted body rebinds local `value` (the
  verdict) before the margin expression re-reads the leaf → margin evidence silently corrupted,
  including a violated constraint reporting a **positive** margin (sign inversion). Formal named
  `status` → margin silently `None`. Verdict stays correct; only the evidence is wrong — the silent
  kind. (High)
- **Formal named `verdict`**: template rebinds the run parameter, then `float(verdict)` on a
  `_PredicateResult` → generated module raises `TypeError` on every run, violating INV-3 from a
  valid model. (Medium)
- **Formal named `self`**: `def run(self, self: float)` → `SyntaxError`; generation succeeds
  silently, failure surfaces at import. (Medium)
Fix shape: a deny-list-plus-rename at the sanitize or compile seam covers all three.

### R-4 — Nullable-QN ADMIT filter crashes from-snapshot rebuild on a valid snapshot (PR #9) — reproduced
`src/sysml_codegen/analysis/constraint_lowering.py:448-459` (`collect_bare_actual_demand`).
`admit_qns` is a set of `identity.qualified_name`; anonymous usages have `qualified_name=None`, so
one anonymous ADMIT usage inserts `None` and every anonymous **excluded** usage then passes the
`not in admit_qns` filter and gets owner-expanded. Live capture succeeds (the excluded branch never
queries that owner, so the frozen transcript omits it); from-snapshot rebuild then raises
`FrozenOccurrenceIndexCorruptionError` — not in the `except` tuple at `:459` — with a misleading
"recapture the snapshot" message. Live-side, the same mismatch mints spurious synthesized
supplied-value attributes for constraints that never execute. Note: this re-imports the same
nullable-QN identity mistake F5 just fixed elsewhere in the file (`excluded_usage_indices` already
uses positional zip for exactly this reason). Also missing: the owner-kind filter — an ADMIT usage
with an out-of-profile owner falls into `_expand_owner_instances`'s "never reached" package branch.

## Medium findings

### R-5 — Recursive part containment silently truncates the occurrence set (PR #9) — reproduced
`src/sysml_codegen/analysis/part_instance_index.py:158-161`. The `_visited` cycle guard returns `[]`
for a revisited definition, so `part def A { part suba : A; }` + `part a1 : A;` yields only the
non-recursive occurrences — no `NonFiniteCardinalityError`, no diagnostic. Violates the module's
own INV-2 ("no third disposition beyond expand-finite or block-loud") and lower_constraints'
one-record-per-instance INV-3: a part_def-owned assert lowers to one concrete constraint and the
nested instances are silently never checked. Correct behavior per design: loud block, matching the
`[*]` multiplicity path.

### R-6 — Named excluded locations leak absolute machine paths into fingerprints and contracts (PR #9) — reproduced end-to-end
Found independently by two reviewers. `src/sysml_codegen/snapshot/serializer.py:145-159`
canonicalizes `location.file` only for anonymous excluded usages; `constraint_lowering.py:496-508`
(`_exclusion_for`/`_render_location`) keeps the raw parser path for named excluded usages. The raw
path flows into `excluded_records` → `catalog.fingerprint` → `semantic_fingerprint` and
`contracts/model_contract.json`, and is rendered into the generated `report_aggregator.py`.
Reproduced: `generate --from-snapshot tests/fixtures/constraint_non_numerical/extraction_snapshot.json`
emits a contract containing `"location": "///home/reid/1cfe/sysml-codegen/tests/fixtures/..."`.
Consequences: local paths ship inside generated packages; regenerating the same model from another
checkout changes package bytes solely through the fingerprint; live-vs-snapshot parity holds only on
the capture machine. The committed fixture snapshot already carries the `/home/reid` path.

### R-7 — Constraint-actual demand silently overwrites a calc-usage-derived synthesized design attribute (PR #9) — reproduced
`src/sysml_codegen/resolution/supplied_values.py:265-268` appends constraint demand entries after
calc-usage entries with no dedupe, and `collect_bare_actual_demand` collects every ADMIT
feature-reference actual, not only bare ones as its name and the D2 docstring promise. When the same
`(instance_scope, source_path)` resolves via both routes, the later constraint entry overwrites
`synth[target.qn]` (`:299-312`), replacing `source_file` with the constraint's file — so a model
that keeps assertions in a separate `.sysml` file regroups that entry point into the constraint
file's parameter group (different schema/inputs JSON) the moment lowering is enabled. Side effects:
`scanned`/`applied` double-count; the REQ-SVM-03 collision warning can fire twice.

### R-8 — The F4 warning pre-pass can itself halt, masking the BLOCK diagnostic (PR #9) — reproduced
`src/sysml_codegen/analysis/constraint_lowering.py:549-550, :565, :591`
(`_report_non_numerical_warnings` → `_warning_location` → `_canonical_anonymous_location`).
If an anonymous NON_NUMERICAL statement's file maps to no model root (e.g. an imported library
outside `--models`), the pre-pass raises "raw source '...' does not match any supplied model root":
zero warnings are emitted and the actionable BLOCK halt (constraint name, reason, repair text) is
replaced. The F4 warnings-before-halt guarantee is conditional on referent mapping succeeding.
Reachability from live extraction unproven; the failure mode is real. (Found during the GAP-CLOSE
Item 2 independent audit.)

### R-9 — `_literal_float` silently loses signed and unit-annotated modeled defaults (PR #9) — reproduced at unit level
`src/sysml_codegen/analysis/constraint_lowering.py:1114-1124`; consequence
`generation/entry_point.py:272-273`. Only a bare `LiteralNode` yields a value: `:= -0.1`
(unary-minus OperatorNode — the shape the profile's unary-sign support exists for) and `= 40.0 [MW]`
(UnitAnnotationNode) return `None`, so the MODELED_DEFAULT formal mints a LIBRARY_DEFAULT entry
point with `default_value=None` and the generated JSON input omits the key — a default the model
explicitly carries becomes a value the user must re-supply.

### R-10 — Seal/verify symlink gaps: seal produces unverifiable packages; dangling symlinks pass verify (PR #9) — reproduced
Found independently by two reviewers.
- `src/sysml_codegen/contracts/seal.py:67-73` has no symlink policy: sealing a tree containing an
  escaping file symlink records and hashes it; a directory symlink is silently skipped. Both produce
  a "successfully sealed" package that immediately fails its own verification (`INVALID_PATH`) —
  the failure surfaces at first load, far from the cause, with no diagnostic at seal time
  (`cli/__init__.py:610-640` Step 9 completes without error).
- `src/sysml_codegen/contracts/verify.py:277-307`: a dangling symlink is neither dir-symlink nor
  file, so the extras walk skips it with no diagnostic — `ok=True`. It is uncovered mutable content
  (live the moment its target exists), the same threat class F9 closed.

### R-11 — v3 loader violates its own "never a raw KeyError" gate on malformed section shapes (PR #9) — reproduced
`src/sysml_codegen/snapshot/loader.py:154-199` gates only presence and `schema_version`.
`part_occurrences` as a list → raw `AttributeError` (via `part_instance_index.py:425-447`); an
occurrence missing `steps` → bare `KeyError: 'steps'`; `constraint_facts.usages = 42` → bare
`TypeError`. None carry the re-capture instruction the loader's comment (`:154-156`) promises for
every v3 section.

### R-12 — Explicitly-set but invalid `TEAX_SIMKIT_PATH` silently falls through to the sibling (PR #9, test infra) — reproduced
`tests/helpers/teax_discovery.py:12-38`. An operator pinning a specific simkit build who typos the
path (or whose checkout moves) silently validates against `../teax/packages/teax-simkit` instead —
green results against the wrong dependency. The dangerous cell (invalid explicit + valid sibling) is
exactly the one `tests/unit/test_teax_discovery.py` doesn't test. An explicitly-set-but-invalid path
should be an error or a loud warning. Ironic note: this helper is itself the GAP-CLOSE hygiene fix.

## Low / latent / informational

**PR #9 production:**
- `orchestration/pipeline_builder.py:1004-1009` — load-bearing comment claims
  `assemble_constraint_catalog` "returns None when every concrete record is unassessed"; it never
  returns None (found independently by two reviewers). Same drift in the
  `extend_graph_with_constraints` docstring (`constraint_lowering.py:1153-1155`, "when at least one
  assertion is eligible" vs unconditional D11 emission).
- `orchestration/pipeline_builder.py:912-930` — P2 constraint-root injection round-trips the resolved
  channel through `"{instance_name}.{output}"`; downstream resolves by bare instance name first-wins,
  so with `include_all=False` and duplicate instance names the root can anchor to the wrong usage.
  Inert on the CLI path (`include_all=True`).
- `generation/registry.py:~293-300` — mixes `/` and `.` separators; any future 3-segment
  `module_type` emits a SyntaxError import. Unreachable today.
- `constraint_lowering.py:972-974` — duplicate actual names last-wins on the inline path where the
  definition-typed twin raises (plausible-only; shape may not survive extraction).
- `constraint_lowering.py:371-380` vs `analysis/parameter_groups.py:358-367` — opposite duplicate-QN
  precedence (last-wins vs first-wins) between the two design-attribute indexes; resolution and
  minted `default_value` can come from different records (plausible-only).
- `generation/modules.py` `compile_shared_predicates` — `is_negated` read from the first entry with
  no cross-entry agreement check; mutation-only (one usage per key under the profile), but it is the
  one field the INV-2 guard family doesn't cover.
- `generation/predicate_compiler.py:130-135` — n-ary `**` left-folds (wrong associativity);
  unreachable through v3 preflight, but `compile_predicate` is a public API with no arity guard of
  its own.
- Same-location anonymous siblings still hard-collide (deterministic 128-bit suffix, zero
  per-sibling entropy) — the F5 symptom reproduces if extraction ever yields two facts at one
  file/line/column (`constraint_lowering.py:907-919`).
- Lowering: excluded-branch mint aside, `_TransactionalAssignmentModel` latents — `Field(exclude=True)`
  on a required field would fail every assignment ("complete candidate" uses `model_dump`); an
  after-validator that assigns would recurse; in-place container mutation bypasses the guard
  (out of scope by spec) (`resolution/models.py:34-39`).
- `snapshot_context.py:60-76` — from-snapshot ctx reports `constraint_lowering_mode="grandfathered_off"`
  / `constraint_facts=None` even for an "applied" capture; harmless today, dishonest to a future consumer.
- `cli/__init__.py:726` — `cmd_seal` re-seals with `DEFAULT_COVERAGE_POLICY` unconditionally rather
  than the package's recorded policy; inert while one policy exists.

**PR #9 tests:**
- `tests/unit/test_expression_compiler.py:475-491` — exact-name-match isinstance mock can't represent
  FeatureChainExpression <: OperatorExpression, so the Edge-5 dispatch-order test passes regardless
  of ordering; the real risk now lives in agentic-mbse's `_expression_ir` dispatch, unprotected here.
- `tests/unit/test_verify_package.py:346-359` — the INV-8 import scan ignores relative imports
  (`node.level > 0` unchecked); a relative in-repo import in `verify.py` would pass silently.
- `tests/unit/test_predicate_compiler.py:135-140,167` — asserts glibc's exact errno-34 OverflowError
  text; fails on macOS despite correct behavior.
- Minor: docstring-content assertion in `test_concrete_constraint_model.py:19-26`; stray
  `monkeypatch=None` param at `test_constraint_emission.py:148`.

**PR #11:**
- `constraint_extraction.py:59-61` — `_BOOLEAN_CONNECTIVE_OPERATORS` omits `xor`, so live-parsed xor
  nodes carry an `operand_type` in violation of the `expression_ir.py:71-76` wire invariant
  (canonical-bytes inconsistency; no admission impact).
- `executable_profile.py:198-227` — `classify_equality` docstring promises same-enumeration /
  same-category checks the code doesn't perform; `boolean == string` passes as a valid non-numerical
  statement (never ADMIT, so not an admit hole; cross-category severity is a design judgment).
- `validation/level6_architecture.py` — UNASSESSED decisions now emit no per-constraint L6 issue;
  pre-PR every dropped ConstraintUsage drew a WARNING. Per-constraint visibility loss, likely
  intended scope — worth confirming against the Item-3 spec.
- Extractor dedupes duplicate-QN definitions first-wins (`constraint_extraction.py:146`); the
  profile's lookup is last-wins (`executable_profile.py:792-796`). Unreachable from own extraction
  output.
- Cosmetic (from the Item 4 audit): the contradictory-fact block reuses
  `block_derived_unit_unsupported`, which names a different condition.

## Verified clean (checked, no defect)

Kleene truth tables and eager-evaluation soundness; full parenthesization (no precedence hole);
`inf`/`nan` unreachable (`allow_nan=False`); aggregator precedence/exactness/determinism;
compile-once + same-IR + unique-id + unique-function-name + duplicate-path guards all fire before
writes; codec byte-stable round-trip on a maximal ConstraintFacts aggregate; F8 ordering propagated
consistently; L6 ERROR-on-BLOCK fails the level; seal/verify glob parity, fingerprint
self-exclusion, recorded-symlink containment, hostile-path diagnostics; live/offline lowering-gate
parity including the frozen-transcript query set; transactional-assignment F6 fix holds on every
route probed; `source_referent` round-trip fail-closed; `classify_cardinality` fail-closed;
determinism at every iteration point sampled in both repos. Test wave quality: no self-referential
assertions, no pass-or-skip, no overbroad raises in the sampled files; strong precedence-under-conflict
and executed-Kleene coverage.

## Recommendations

1. **Fix before merge (wave is already held on F1):** R-1, R-2 (profile, one spec'd fix wave in
   agentic-mbse — both are wrong-verdict class, same severity tier as the findings that gated this
   wave); R-3 (one deny-list seam in codegen); R-4 (positional/index-based identity + owner-kind
   filter + widen the except tuple). R-1/R-2 also need golden-matrix rows (ordering × non-numeric
   categories; negation rows).
2. **Ride the next fix wave or file:** R-5 (make the cycle guard loud), R-6 (canonicalize named
   excluded locations — note the committed `constraint_non_numerical` snapshot then needs a
   justified re-capture), R-7 (dedupe demand by target QN, or make the collector match its "bare"
   contract), R-8 (wrap the pre-pass location render, fall back to raw location in the warning
   rather than halting), R-9 (fold unary sign + unit annotation into `_literal_float`), R-10 (symlink
   policy at seal + diagnose dangling links at verify), R-11 (shape-gate v3 sections), R-12 (error on
   invalid explicit path + the missing test cell).
3. **File as hygiene:** the Low/latent list (comment corrections are one-line fixes; the two wrong
   comments were independently flagged by multiple reviewers and will actively mislead).
4. The four Highs share the "captured-but-unconsulted fact" shape. When specing the fixes, add a
   completeness check per decision seam: for every field the facts schema carries, name the consumer
   or the reason it is decision-irrelevant. That converts this defect class from review-luck to a
   checkable contract.

## Open Questions

- R-1/R-2 fix semantics need an owner call: BLOCK vs extend the admitted matrix (ordering on
  non-numeric categories should almost certainly BLOCK under v3's default-deny; negation could
  either BLOCK or be folded into the IR — folding changes the admitted surface and may warrant the
  v4 discussion the epic deferred).
- Is the L6 UNASSESSED silence (PR #11) intended scope or a visibility regression? Check the
  CONSTRAINT-EXEC Item-3 spec before filing.
- R-6's fix churns the committed `constraint_non_numerical` snapshot and every fingerprint-bearing
  baseline containing a named excluded record — needs the per-fixture recapture discipline.
