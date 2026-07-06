# Audit: Expression Reconstruction Fidelity (SC-6) — UPSTREAM-FINDINGS Item 6

**Verdict:** CONDITIONAL — substance certified; clears to PASS on one item (re-run the
test-suite gate in a Python-enabled environment; the auditor was harness-blocked from `uv run`).
**Audited:** 2026-07-05
**Branch:** upstream-findings-epic
**Commits:** `346cf47` (feat, HEAD) + `77fc46c` (chore, stale-fixture refresh)

---

## Summary

The two display-path fixes are implemented exactly as designed: literal/null branches
dispatch before the invocation catch-all via `is_instance`, and operator expressions
parenthesize precedence-aware per the pinned KerML table. The five design hand-traces
match the code's output one-for-one, and the helper honors the single C2 polarity
convention with C3 unary wrapping. The regen is clean: zero `Literal*Evaluation` remain
in the committed corpus, the three snapshot-verifiable paren-restorers are present, and
**no executable field changed across either commit** — the byte-identity gate holds by
direct diff, not just by test-green. All four recorded deviations are present and sound.

The one open item is environmental, not a code defect: `uv run` requires interactive
approval in this orchestrated session, so the recorded suite gate (1894 passed / 21 ruff
/ 109 mypy) could not be re-executed here. This is the same block that left Items 1 and 2
CONDITIONAL. Everything statically checkable passed.

## Findings

### Plan completion

All four phases verified against the tree.

- **Phase 1 (fixes + offline hand-traces).** `expression_utils.py` carries the reorder
  (`:60-80` literal/null branches above the catch-all at `:82`), `RANK`/`UNARY_RANK`/
  `RIGHT_ASSOC` tables (`:98-120`), `binary_op_of` + `needs_parens` (`:123-161`), and the
  parenthesizing `reconstruct_operator_expression` (`:164-224`). `is_literal_expression`
  gained `LiteralInfinity` + `NullExpression` (`:295-296`). Unit test file present with
  the residual stub check + five hand-traces + C2/C3 cases (`test_expression_paren_helper.py`).
- **Phase 2 (live real-AST test).** `test_expression_reconstruction_fidelity.py` parses
  `tests/fixtures/expr_paren_probe/` live (no mocks), asserts all seven shapes exactly and
  no `Evaluation()`. License marker factored into `tests/conftest.py`
  (`_license_available` + `requires_license` + `REPO_ROOT`); `test_snapshot_generation.py`
  imports it and dropped its local copy (no second `load_models()` probe).
- **Phase 3 (regen).** Executed as the recorded two-commit split. Snapshots + 3 pipeline
  baselines regenerated; `test_literal_totality.py` guard present.
- **Phase 4 (docs).** Doc 19, matrix, BACKLOG, PUSH-DOWN, design erratum all landed (see
  Design conformance).

### Spec conformance

- **SC — repro renders faithfully (real AST, no mocks):** MET. `expr_paren_probe` fixture +
  the license-gated real-AST test assert `capacity * rate + capacity * (rate / 2.0) * 3.0`
  and all four branch shapes exactly. In the regenerated `catf_mfe` baseline the same fix
  shows live: `refrigeration_power = thermal_load * (300.0 / operating_temp) / carnot_efficiency`,
  `area = 2.0 * 3.14159265359 * ...`, `a = (r_inner + r_outer) / 2.0 - r_major` — parens and
  literal values both restored.
- **SC — zero `Literal*Evaluation` in the corpus:** MET. Grep of
  `tests/fixtures/**/extraction_snapshot.json` + `baseline_outputs/**/*.json` → 0 matches.
  The offline totality guard pins it.
- **SC — executable content byte-identical after regen:** MET (checked, not assumed). Diff of
  the three `computation_graph.json` baselines across `346cf47~1..346cf47` shows changed lines
  live **only** inside `calc_expressions` arrays (literal→value, parens). No changed line
  touches `compiled_expression`, `compilation_results`, `auto_impl_context`, `compilability`,
  or channel names. INV-1 holds by direct diff.
- **SC — doc 19 + matrix rows + REQ tags:** MET (see Design conformance).
- **SC — agentic-mbse impact recorded (none / travels with PUSH-DOWN):** MET. PUSH-DOWN
  sequencing note added to `agentic-mbse-push-down-design.md`; "none" recorded for the Item-12
  accumulated list.

Tagged HARD requirements: literal-before-invocation ordering via `is_instance` — MET
(`expression_utils.py:60-80`). `is_literal_expression` aligned with `LiteralInfinity` +
`NullExpression` — MET (`:295-296`). Regen through capture scripts only, one item at a time,
byte-identity gate a hard stop — MET (two-commit split, exec fields unchanged). `captured_at`
discipline — the chore commit shows deliberate restamps only on the three refreshed files.

Non-goals respected: `_walk_aggregation_ast`'s twin bug is **not** fixed (filed to BACKLOG,
noted in doc 19); no executable/compiled expression or YAML-wiring change; reconstructor not
replaced by `build_expression_ast`.

### Design conformance

- **Five hand-traces match the design table exactly** (`design.md:334-340` ↔
  `test_expression_paren_helper.py:56-83`): `a - (b - c)`, `a / (b * c)`, `-(a + b)`,
  `a ** b ** c` (flat), `(a ** b) ** c` (wrapped). Single RANK-direct polarity convention;
  unary branch runs `needs_parens(UNARY_RANK, ...)` so operands wrap (C3). Implementation
  follows the design.
- **Signature deviation (recorded, sound):** `needs_parens(parent_rank, parent_right_assoc,
  child, side)` instead of the design's `(parent_op, child, side)`. Rationale in the plan:
  binary `-` (rank 5) and unary `-` (rank 2) share an operator string, so parent rank cannot
  be derived from the string alone. All five traces still render exactly. Accepted.
- **Doc 19:** REQ-AST-03 revised in place (FCE<OE<FRE among reference/operator branches;
  literal/null before the catch-all); REQ-AST-08 and -09 added; the canonical-ordering block
  re-numbered (literals branch 4, invocation catch-all LAST) with rationale; the
  `_walk_aggregation_ast` known-deviation note present. Matches D5.
- **Matrix:** REQ-AST-03 row revised; REQ-AST-08/-09 rows added, pointing at the real-AST
  test, the totality guard, and the hand-trace unit tests.
- **BACKLOG:** both follow-ups filed — the aggregation-literal dispatch bug and
  constraint-reconstruction coverage.
- **PUSH-DOWN note** present in the P1 design.

### Code integrity

No slop or failure-honesty issues.

- The literal branches guard `hasattr(expr_node, "value")` and fall through to the catch-all /
  `str(node)` rather than returning a silent wrong default — honest.
- `binary_op_of` returns `None` (atomic, never-wrap) for non-OE, non-2-operand, or
  unranked-operator children; the RANK-membership clause makes FCE (operator `.`) and
  invocations fall through cleanly with no separate guard and no `KeyError`. Contract readable
  from the signature.
- `needs_parens` is a pure precedence predicate — no policy, no fallback defaults.
- **Deviation #3 (OPERATOR_MAP revival via `str(operator)`), reviewed:** byte-identical. On the
  binary path `op_str = OPERATOR_MAP.get(operator, f" {operator} ")` returns e.g. `" + "`; the
  fallback on the same normalized symbol yields the identical string. `"not"` is unary and never
  reaches this lookup. Sound.
- **Deviation #4 (orchestrator-authored totality guard), reviewed to the same bar:**
  `test_literal_totality.py` greps committed extraction snapshots + `baseline_outputs` for
  `Literal\w*Evaluation` (the broad pattern, catches every sibling) and asserts zero; asserts
  the three snapshot-verifiable restorers verbatim; correctly drops the catf_mfe constraint
  restorer per the erratum. Sound. Nit (non-blocking): the offender dict-comprehension reads each
  file twice (`.read_text()` in both the value and the `if`); cosmetic, no correctness impact.

### Deviation review (adjudicated set)

1. **Two-commit regen split** — sound. Chore `77fc46c` carries only module_type sanitization
   (Item 5) + path canonicalization (source_file / document_path / design_attributes re-key) with
   **zero** `calc_expressions` / `expression_text` / `Literal*Evaluation` churn (verified by diff);
   the pre-Item-6 reconstructor produced it. Feat `346cf47` is the display-only regen on top. R3
   one-item isolation honored by commit separation. Rationale is in the chore commit message.
2. **Appendix-A #4 erratum** — sound. Recorded in `design.md` (strikethrough + ERRATUM) and in
   BACKLOG; M1 for catf_mfe rests on the three snapshot-verifiable restorers + catf_mfe's real
   snapshot gains, which the feat diff confirms.
3. **OPERATOR_MAP revival** — byte-identical (above).
4. **Orchestrator-authored guard** — sound (above).

### Scope check

- Feat `346cf47`: code + 2 conformance tests + unit test + conftest + snapshot_generation import
  + doc 19 + matrix + BACKLOG + PUSH-DOWN + design/plan/spec notes + regenerated snapshots/baselines
  + `expr_paren_probe/probe.sysml`. No stray files; no `scripts/` change (correctly, that is the
  chore commit's).
- Chore `77fc46c`: `capture_extraction_snapshots.py` (registers `quoted_owner_formula`) + 3 stale
  snapshots. Scoped and clean.
- No mocks in the fidelity tests. The paren-helper unit test uses named-fallback stubs — unit-level
  per the plan's Component-5 contract; the residual check `test_residual_stub_drives_binary_op_check`
  confirms `binary_op_of` actually sees the stub, so the other traces are not vacuous. Stub-detection
  contract holds.

### Observation (out of scope, not a finding against Item 6)

Committed extraction snapshots embed machine-specific absolute paths
(`/home/reid/1cfe/sysml-codegen/...` in `design_attributes` keys and `document_path`). This is the
**established** canonical form — 13 snapshots including the reference `solar_battery_model` already
carry it, and the chore commit brought `quoted_owner_formula`/`retype_model` into line with it. Not
introduced by Item 6. Flagged only as pre-existing fixture tech-debt (breaks reproducibility off this
machine) for a future item, not a blocker here.

---

## Certification

**Verified statically and by diff:**
- Five hand-traces ↔ design table, one-for-one; helper matches the single-convention / unary-wraps spec.
- Repro fidelity: parens + literal values render in the regenerated snapshots and the real-AST test.
- Executable byte-identity across both regen commits: zero exec-field diffs (`compiled_expression`,
  `compilation_results`, `auto_impl_context`, `compilability`, channel names).
- Zero `Literal*Evaluation` in the committed corpus; three restorers present.
- Doc 19 revision + walker deviation note; REQ-AST-08/-09 matrix rows; both BACKLOG entries; PUSH-DOWN note.
- Both commit scopes clean; no mocks in fidelity tests; stub contract holds.
- All four recorded deviations present and sound.

**Open (the CONDITIONAL item):**
- Re-run the recorded gate in a Python-enabled environment: `uv run pytest tests/` (expect **1894
  passed**, with `test_live_vs_snapshot_byte_identical` green post-regen), `ruff check src/` (**21**),
  `mypy src/` (**109**). The auditor was harness-blocked from `uv run` (interactive approval
  unavailable in this orchestrated session) — identical to the Items 1/2 audits. No code change is
  expected to clear it.

**Checkbox marking:** spec/plan success-criteria boxes left unchecked pending the suite re-run, to
avoid certifying an execution gate the auditor could not run. Flip on green.


---

## Orchestrator close-out (2026-07-05)

Clearing action: the orchestrator ran the full gate at the committed state (the orchestrator
executed the two-step regen itself and gated before committing): **1894 passed / 4 skipped /
5 xfailed; ruff 21; mypy 109** (== baseline), live-vs-snapshot byte-identical test green.
The absolute-path snapshot canonical-form observation is noted as pre-existing fixture
tech-debt (13 snapshots), not Item 6's.

Verdict upgraded: **PASS**. Item 6 complete.
