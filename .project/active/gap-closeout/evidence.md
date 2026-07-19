# GAP-CLOSE Item 5 Implementation Evidence

**Status:** Local Scope Certified — Ready for Explicitly Partial Pre-PR
**Recorded:** 2026-07-18
**Codegen source revision:** `6db321225a5c8568db0287b67ed1d04c03079cc2`
**Codegen merge base:** `430404d21bae3a0fb3d94b82584302f037f77bcb`
**Companion source revision:** `4ed2a0728ea49298666415cd389d9a6173a81a3e`
**Companion merge base:** `6a69e13e8697d17919bd689062a9edc42fffda8a`
**Tools:** Python 3.12.3; uv 0.10.0

The source revisions identify the two dirty candidate bases. Item 5 is not committed. The complete
candidate is each revision plus its classified worktree. Licensed commands loaded the existing
companion `.env` without recording any credential value.

## Independent audit cure evidence

The first independent audit found three local gaps. Each received an isolated RED regression before
its attempted cure. The second re-audit certified the warning-byte cure but found that the
documentation and TEAx discovery boundaries were still incomplete at that point:

1. The document test failed on the opening guide's “one of three” wording. The test now requires all
   four v3 outcome tokens and forbids both retired phrases. The rebuilt `0.1.1` wheel ships that
   source at `agentic_mbse_data/docs/patterns/constraints.md`; wheel sha256:
   `b7ddf326342aede2b4de8b7eed03a9e9b182be880c2e19a77e8d17e324b7c20f`. Re-audit found two
   contradictions the token test misses: BLOCK is described as an L6 warning, and a later summary
   omits asserted NON_NUMERICAL outcomes.
2. The route-parity regression initially captured absolute live paths and `root-0` snapshot paths.
   Anonymous warning rendering now uses the same canonical referent mechanism as exclusions. The
   real lowering logger produces these exact bytes in repeated live, relocated live, and snapshot
   replay routes:

   ```text
   Constraint <anonymous> at root-0/model.sysml:10:2 is not numerical and will not execute: warn_non_numerical_equality: equality is a valid non-numerical statement and is not executed
   Constraint <anonymous> at root-0/model.sysml:20:2 is not numerical and will not execute: warn_non_numerical_equality: equality is a valid non-numerical statement and is not executed
   ```

3. The hostile discovery regression initially received a raw `Symlink loop` exception. Resolution
   and stat failures inside the candidate loop are now classified as invalid routes, and the final
   error names `TEAX_SIMKIT_PATH`, the checkout-relative sibling, and the symlink failure. Re-audit
   found that explicit `expanduser()` still ran before this boundary at that time and could leak a
   raw `RuntimeError` for an unknown-user path.

Audit-cure gates: 3 isolated regressions GREEN; companion relevant selection 36 passed; codegen
relevant selection 63 passed / 13 skipped in both normal and optimized mode; licensed route and
snapshot selection 16 passed; real SimKit 9 passed; sibling fallback 9 nodes collected. Touched
Ruff/format checks pass, including the kept companion documentation regression at
`tests/test_constraint_documentation.py`. Targeted mypy retains the same three inherited lowering
findings. Final candidate/worktree diff checks are clean in both repositories. Fixture manifests
remain identical and fixture diffs are empty at 179 codegen and 61 companion files.

## Second re-audit cure evidence

Both reopened local findings received defect-specific RED regressions before correction:

1. The strengthened companion guide test failed at the opening L6 severity assertion. It now pins
   both audited sections: BLOCK produces one named L6 `ERROR` per blocked construct, and asserted
   predicates route to admitted, blocked, or non-numerical. It also rejects the retired
   `WARNING per blocked construct` statement anywhere in the guide.
2. The TEAx regression injects `RuntimeError("injected expanduser failure")` at `Path.expanduser`,
   the exact seam that previously preceded normalization. Before the cure it escaped as raw text.
   Expansion now occurs inside the same specific `OSError`/`RuntimeError` boundary as resolution
   and package validation, so the final error names `TEAX_SIMKIT_PATH`, the checkout-relative
   sibling, and the injected cause.

Validation results:

- Isolated cures: companion documentation 1 passed; codegen expansion regression 1 passed.
- Focused files: companion documentation 1 passed; codegen TEAx discovery 5 passed normally and
  5 passed under optimized Python.
- Relevant broader companion guide/profile/L6 selection: 119 passed.
- Licensed real SimKit execution through the established companion environment and explicit local
  source roots: 9 passed. An initial codegen-environment attempt stopped on the already documented
  missing license export and `pandas`; it did not exercise or invalidate the cure.
- Touched Ruff and format checks pass in both repositories. The strengthened companion test was
  mechanically formatted and then passed its test, Ruff, and format checks.
- The rebuilt `agentic_mbse-0.1.1-py3-none-any.whl` guide is byte-identical to source. Wheel sha256:
  `160e7eb55eb6bf4bfba3b422166e6e8f4eef50f7a6c09aa2f7ed91a7cd8a8d4f`.
- Final worktree `git diff --check` is clean in both repositories, both fixture diffs are empty,
  and the carried 179 codegen / 61 companion fixture manifests remain unchanged.

## Success-criterion matrix

| Criterion | Evidence | Result |
|---|---|---|
| Companion patch identity and codegen floor | Package tests; final wheel metadata; two isolated resolver legs | PASS |
| Four-outcome companion documentation | Kept regression pins both guide sections, L6 `ERROR` severity, asserted `NON_NUMERICAL`, and retired wording; rebuilt wheel matches source | PASS |
| Catalog documentation | Doc 28 assertions for all outcomes, `excluded_records`, validated payload, and all three fingerprint inputs | PASS |
| Snapshot lockstep documentation | Doc 27 assertions for re-lowering, fact/IR schemas, v3, package floor, and runtime/schema guards | PASS |
| Public exclusion models | `test_catalog_exclusion_models_are_public_and_fingerprint_contract_is_complete` | PASS |
| Catalog docstring and loader pointer | Same model test plus snapshot-contract focused suite | PASS |
| Actionable D5 warnings | Exact logger bytes match across repeated live, relocated live, and snapshot routes | PASS |
| Portable TEAx discovery | Valid explicit/fallback routes plus symlink-loop and injected pre-normalization expansion failures reach one route-aware diagnostic | PASS |
| Literal whitespace | Candidate-range and worktree diff checks; normalized whitespace-only review | PASS with bookkeeping note below |
| Final paired validation | Licensed full suites, execution lane, live/snapshot family, static, fixture, metadata, and diff gates below | PASS with recorded static baseline debt |
| Re-audit and pre-PR | Final focused re-audit certifies local scope; explicitly partial pre-PR remains to run | PARTIAL PASS |
| External F1 remains open | Backlog row verified; status artifacts retain the dependency | PASS |

## Metadata-only pairing proof

The pre-edit negative wheel was built before changing either version surface:

- `agentic_mbse-0.1.0-py3-none-any.whl`
- sha256 `b1126ccc5a9216dd2dd28bc892cda6fbc27bdc297d02cb2273017de08fea5823`
- metadata: `Name: agentic-mbse`, `Version: 0.1.0`

Final wheels:

- `agentic_mbse-0.1.1-py3-none-any.whl`, post-second-re-audit-cure sha256
  `160e7eb55eb6bf4bfba3b422166e6e8f4eef50f7a6c09aa2f7ed91a7cd8a8d4f`
- `sysml_codegen-0.1.0-py3-none-any.whl`, sha256
  `d3b1611ba60cac7fea2aeac65805d1fc4a2a22e37e29be2d1dfb5c1d217e525b`
- codegen `METADATA`: `Version: 0.1.0`, `Requires-Dist: agentic-mbse>=0.1.1`
- companion `METADATA` and packaged `agentic_mbse/__init__.py`: `0.1.1`

Both resolver legs used the same final codegen wheel and fresh virtual environments. Supplying
only companion `0.1.0` exited 1 with an unsatisfiable `agentic-mbse>=0.1.1` diagnostic. Supplying
companion `0.1.1` resolved and installed 28 packages from the local candidate wheels plus registry
dependencies. The accepted environment reported:

```text
agentic-dist 0.1.1
agentic-runtime 0.1.1
agentic-root /tmp/gap-closeout.0RaoeN/final-new-env/lib/python3.12/site-packages/agentic_mbse/__init__.py
codegen-dist 0.1.0
codegen-root /tmp/gap-closeout.0RaoeN/final-new-env/lib/python3.12/site-packages/sysml_codegen/__init__.py
requirement agentic-mbse>=0.1.1
```

No editable source participated in either resolver result. Both `uv.lock` files were refreshed so
their root package records agree with `0.1.1`; the profile remains `executable-profile/v3`, and the
constraint-facts and expression-IR schemas remain v1.

## Focused and licensed test evidence

| Gate | Result |
|---|---|
| Companion package/profile/codec focused, normal | 169 passed |
| Companion package/profile/codec focused, `python -O` | 169 passed |
| Codegen metadata/model/warning/lowering/catalog/snapshot/discovery focused, normal | 120 passed |
| Same codegen focused selection, `python -O` | 120 passed |
| Licensed companion full default suite | 1,525 passed, 1 skipped, 33 deselected |
| Licensed codegen full default suite | 2,516 passed, 26 skipped, 9 deselected |
| Licensed real-SimKit execution through explicit `TEAX_SIMKIT_PATH` | 9 passed |
| Sibling-fallback execution collection | 9 tests collected |
| Licensed live/snapshot byte/fingerprint/warning parity family | 11 passed |
| Audit-cure companion selection | 36 passed |
| Audit-cure codegen selection, normal and `python -O` | 63 passed, 13 skipped in each mode |
| Audit-cure licensed route/snapshot selection | 16 passed |
| Second-cure companion documentation focused | 1 passed |
| Second-cure TEAx discovery focused, normal and `python -O` | 5 passed in each mode |
| Second-cure companion guide/profile/L6 broader selection | 119 passed |
| Second-cure licensed real-SimKit execution | 9 passed |

The 11-test live/snapshot gate covered the parameterized complete-tree comparisons, the symlinked
route, fingerprint parity, and non-numerical warning/catalog parity. It produced no Item 5 generated
artifact difference. Running the execution lane once from codegen's smaller environment failed on
the known missing TEAx transitive dependency `pandas`; rerunning through the documented licensed
companion environment passed all 9 tests. This is environment evidence, not an implementation
failure or fallback in discovery.

## Documentation assertions

Positive assertions find all four exact outcome tokens, the Boolean/string/enumeration versus
integer/real/quantity equality split, binary `xor`/`implies` containment, malformed-arity default
denial, the exclusion payload, all three fingerprint collections, snapshot re-lowering, the package
floor, and runtime/schema pins. The kept document test rejects “one of three” and “three-outcome,”
pins one named L6 `ERROR` per blocked construct in both audited guide sections, requires asserted
`NON_NUMERICAL` routing in the later summary, and rejects `WARNING per blocked construct` globally.
Inspection of the rebuilt wheel proves the corrected shipped copy is byte-identical to source. The
codegen docs retain none of the retired claims.

## Static and hygiene evidence

- Touched-file Ruff and `ruff format --check` passed in both repositories.
- Codegen `ruff check src/` passed. Its whole-source format baseline still identifies 24 existing
  files outside the Item 5 formatting scope. Project-wide mypy reproduced 76 errors in 17 files;
  this matches the recorded codegen baseline. The changed lowering file has three inherited
  `no-any-return` findings when imports are followed; the Item 5 warning hunk adds none.
- Companion touched-file Ruff and format checks passed. Its source-wide Ruff baseline contains one
  existing N806 finding in `extraction/index.py`; the broader tests tree also contains existing
  lint debt. The full current mypy command reports 104 errors in 22 files, all outside the Item 5
  version files. This is broader than the earlier Item 4 note of 21 errors in 8 files; the
  discrepancy is retained for audit rather than rewritten as a green baseline. The changed
  `agentic_mbse/__init__.py` passes with `--follow-imports=skip`.
- Placeholder/debug scan was clean on every Item 5 Python file. No secret value was printed or
  added.
- The loader comment now points to the profile guard symbol. The public exports and catalog
  docstring are pinned by tests. Warning tests pin reason plus message order.
- Audit-cure touched files pass Ruff and format checks. This explicitly includes companion
  `tests/test_constraint_documentation.py`, whose kept four-outcome/retired-wording regression is
  formatted. The new warning-location code adds no mypy finding; the lowering file retains its
  same three inherited `no-any-return` findings.
- Second-cure touched files pass Ruff and format checks. Companion
  `tests/test_constraint_documentation.py` was mechanically formatted after strengthening and then
  passed its focused test, Ruff, and format checks. The TEAx helper remains test-only production
  support and adds no project mypy baseline claim.

## Diff, whitespace, fixture, and artifact evidence

Before cleanup, the committed branch ranges identified trailing whitespace in five codegen
project artifacts and a final blank line in one companion artifact. Cleanup changed horizontal
trailing whitespace or final blank lines only. Review with whitespace-normalized content found no
substantive difference.

Because commits are forbidden in this stage, the historical `merge-base..HEAD` objects themselves
cannot change. The final proposed candidate checks therefore use `git diff --check <merge-base>`,
which includes HEAD plus the Item 5 worktree cleanup, and plain worktree `git diff --check`; both
are clean in both repositories. A later commit will make the equivalent `merge-base..HEAD` check
clean. This distinction is recorded instead of claiming that an immutable HEAD range changed.

Fixture evidence:

- Codegen: 179-file pre/post manifest identical; aggregate manifest sha256
  `01de9728bd7e86ec18ecd3a0c38917b14e4b20362deec5a567a7a4563b6c3284`.
- Companion: 61-file pre/post manifest identical; aggregate manifest sha256
  `2a47247d8ae80ca4bdd011b82878d2783816a53430a5cf4c0a643c22aae74263`.
- Both fixture diffs are empty. The licensed capture-filter test temporarily changed the
  `sample_model` capture timestamp and final newline because sandboxing prevented its Git cleanup;
  the exact recorded pre-run bytes were restored and the full 179-file manifest then passed.
- No fixture or generated byte change is accepted for Item 5. The 11-test live/snapshot gate found
  no generated-tree difference, so the justified Item 5 byte-change table is empty.

## Worktree classification and handoff

The final statuses retain every recorded Item 1–4 path. Item 5 adds only:

- packaging: both `pyproject.toml` files, both `uv.lock` files, companion `__init__.py`, and two
  package metadata tests;
- durable docs: companion constraints guide and codegen docs 27/28;
- hygiene: public exports/docstring, loader comment, D5 warning rendering and assertions, portable
  TEAx helper/tests/conftest including hostile symlink handling, exact anonymous warning route
  parity, and six whitespace-only historical paths;
- workflow artifacts: this directory and synchronized current-work/spec status.

All other modified/untracked entries are inherited Item 1–4 or unrelated pre-existing work and
remain unabsorbed. No commit, push, PR comment, or close action occurred.

`[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains open. Item 1 completed codegen exception propagation;
evaluator-level normalization and failed constraint-module identity remain external. GAP-CLOSE and
F1 are not complete. Merge order remains load-bearing: agentic-mbse PR #11 before sysml-codegen
PR #9. Next stages are an independent GAP-CLOSE epic audit and `my-pre-pr`.
