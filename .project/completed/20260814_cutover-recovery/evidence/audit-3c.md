# Audit: Slice 3C — Coordinated compiler and constraint authority

**Verdict:** CERTIFY (4 findings — 1 Medium, 2 Low, 1 Informational; none blocking)
**Audited:** 2026-08-11
**Auditor:** independent (did not implement this slice)
**Branches:** `item7-rebuild`, both repositories
**Commits:** sysml-codegen `7af5dc9` (+ OID record `5daa8ed`), agentic-mbse `8b63393`

---

## The Point

sysml-codegen turns a SysML v2 model into Python a simulation framework can actually run. The
recovery plan is rebuilding the Item 7 cutover as vertical slices after the original attempt was
lost, and Phase 4 wants to delete the legacy 1,650-line lowering module. Slice 3C is the
coordinated step where both repositories move together: it takes the exact route's constraint
authority off that legacy module, gives agentic-mbse an exact gate beside its neutral one, and —
the part a customer would notice — fixes a rendered calculation implementation that produced
Python which could not run.

## Summary

The slice does what its notes claim, and the notes are unusually honest about what it does not do.
I reproduced both rendered-implementation failure shapes at `38c2e15`, confirmed both are fixed,
and confirmed the fix changes nothing else across the whole fixture corpus. The decoupling is real
at AST and runtime level. Every gate number in the completion notes reproduced exactly. The one
real defect I found is a narrow robustness regression introduced by quality hunk 3, plus a
regression guard that is weaker than the notes claim it is.

## Environment

Import paths re-asserted before any measurement (the F2 trap in `evidence/baseline.json`):

| package | resolved to |
|---|---|
| `agentic_mbse` | `/home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py` |
| `sysml_codegen` | `/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py` |

License loaded from `/home/reid/1cfe/agentic-mbse/.env`; `grep -c "no live syside license"` = **0**
on both full suites.

**A trap worth recording for later slices.** My first attempt to measure the new tests against
`38c2e15` ran from a detached worktree without forcing `PYTHONPATH`. The editable install silently
resolved `sysml_codegen` to the *rebuild worktree at HEAD*, so three genuinely-red tests reported
green. Every old-commit measurement below sets `PYTHONPATH=<worktree>/src` and asserts
`sysml_codegen.__file__` before trusting a number. This is the same class as F2 and it bites
old-commit comparisons, not just venv rebuilds.

---

## Product Judgment

**Is this the right piece of work? Yes, and one of its three parts is a genuine product fix.**

Proof #2 is not a refactor. At `38c2e15`, a calculation with an undeclared intermediate rendered a
stencil that raises `NameError` on the first call and declares `tuple[float, float]` while
returning three values. I executed both stencils:

- `38c2e15` → `NameError: name 'scaled' is not defined`
- `7af5dc9` → `(4.0, 8.0)`, matching the fixture's hand arithmetic (`total=8 → scaled=16 → half=4
  → doubled_half=8`) and the module's `['half', 'doubled_half']` schema

Generated code that cannot run is the sharpest possible contradiction of why this product exists,
so fixing it is squarely on-point. Proofs #1 and #3 are structural enablers for the Phase 4
deletion, which is what the plan asked this slice for.

**Product-lens gate: CLEAR.** Per the audit command I would normally spawn the product-lens
subagent; this session's operating rules forbid launching agents, so I ran the lens myself against
`CLAUDE.md`, the ADR set, and the plan. No owner/`[HARD]` contradiction found.

**One structural smell fired, and is disposed rather than ignored.** The eight retained duals are
"two representations that must be manually kept synchronized" — the classic drift smell. It fires
by construction here. It is disposed, not waved off, because: the duals are enumerated in the plan
with a named Phase 4 owner; keeping both is the only option that does not rename onto a shipped
name; and the measured cost of renaming is on the record in the forensic tree, where 11 agentic
test modules grew fake-UUID `SimpleNamespace` shims and stopped exercising production. I confirmed
none of those shims came across. This is a time-boxed debt with a ledger, which is what the plan's
Rule 6 asks for. **It must close in Phase 4** — while duals exist, the "green because each
assertion picks a different route" failure mode is live, and only the route-parity tests stand
against it.

The notes also volunteer that the slice is thinner on the agentic side than the brief implied (4
source files of renames plus 3 cleanup hunks, no new decision behavior). I verified that against
the parts bin: `ed5b8b02` touches 15 files, 4 source and 11 test. The notes are accurate and did
not dress the slice up.

---

## Findings

### F1 — Medium. `load_manifest`'s narrowed except lets a real failure escape, and its guard test does not cover the gap.
`agentic-mbse:src/agentic_mbse/validation/level6_architecture.py:63-66`

Quality hunk 3 narrows `except Exception` to `except (OSError, yaml.YAMLError)`. A `manifest.yaml`
that is not valid UTF-8 raises `UnicodeDecodeError` — a `ValueError` subclass, neither `OSError`
nor `yaml.YAMLError` — from inside `yaml.safe_load`. Measured on both sides:

```
5088b41 (old):  Warning: Could not load manifest: 'utf-8' codec can't decode byte 0xff...
                load_manifest -> None
8b63393 (new):  RAISED: UnicodeDecodeError
```

The sole production caller is `_check_manifests` at `level6_architecture.py:124`, which loops over
every `designs/*/manifest.yaml` and relies on the `None` return to skip a bad one. One non-UTF-8
manifest now aborts the entire Level 6 architecture check instead of warning and continuing.

Three things make this a finding rather than a nitpick: it is a behavior regression *introduced by
this slice*; it contradicts the function's own docstring, rewritten in the same hunk to promise
"None if not found, **unreadable**, malformed, or not a mapping"; and the guard test the notes cite
as covering the narrowing (`test_manifest_read_failure_is_reported_not_raised`, quality-checks
`:1005`) uses `chmod(0o000)`, which raises `OSError` — a case that *is* caught. The test passes
identically before and after and therefore constrains nothing about the narrowing.

**Resolution:** add `UnicodeDecodeError` to the except tuple (or catch `(OSError, ValueError,
yaml.YAMLError)`), and add a test writing non-UTF-8 bytes to `manifest.yaml` that asserts `None`.

### F2 — Medium. The AST pin protecting the slice's headline decoupling can be walked through by the idiomatic import form.
`tests/conformance/test_exact_constraint_route.py:99-111`

The decoupling itself is real — I verified it three independent ways (my own AST walk over both
files; a full-text grep; and a fresh-interpreter import of only the two exact modules, after which
no `constraint_lowering` entry appears in `sys.modules`). The problem is the guard, which the notes
lean on: "Pinned by an AST import check over both files."

The check collects `node.module` for `ast.ImportFrom` and compares against the full dotted string
`"sysml_codegen.analysis.constraint_lowering"`. Two forms evade it:

```
from sysml_codegen.analysis.constraint_lowering import mint_constraint_id  -> caught
from ..analysis.constraint_lowering import mint_constraint_id              -> NOT caught (module="analysis.constraint_lowering")
from sysml_codegen.analysis import constraint_lowering                     -> NOT caught (module="sysml_codegen.analysis")
```

The third is the ordinary way to import a module object, and it is used at line 116 of this very
test file. The second is live too: `src/sysml_codegen/` already contains 8 relative imports
(`extraction/calc_compat_renderer.py:33` and others), so relative style is not hypothetical here.
A routine refactor could restore the exact route's dependency on the module Phase 4 is meant to
delete, and this pin would stay green.

**Resolution:** resolve each `ImportFrom` to an absolute dotted name (account for `node.level`) and
fail if any resolved name equals *or is a proper prefix path of* the legacy module — so that
`from sysml_codegen.analysis import constraint_lowering` is caught via its `names` aliases too. A
cheaper equivalent: import each module in a subprocess and assert `constraint_lowering` is absent
from `sys.modules`, which is the property actually wanted and cannot be spelled around.

### F3 — Low. The ambiguous-QN test asserts the neutral payload is ambiguous but never shows the neutral gate failing on it.
`agentic-mbse:tests/test_sysml/test_executable_profile.py:698-700`

`test_exact_gate_partitions_every_outcome_and_follows_the_uuid_association` establishes ambiguity
structurally — `len({d.identity.qualified_name for d in facts.definitions}) == 1` — then exercises
only the exact gate. The claim under test ("the neutral payload cannot tell the twins apart") is
therefore argued, not measured.

I measured it. Running neutral `preflight` on the same twin pair, varying only the order of the
`definitions` list:

```
definitions=[admitting, blocking] -> ok=False, blocking=['typed']
definitions=[blocking, admitting] -> ok=True,  blocking=[]
```

The neutral gate silently flips its verdict on list order. The exact gate does not — I varied both
list order and UUID association across four combinations and it followed the UUID every time. That
is a stronger result than the shipped test records, and it is the concrete evidence for proof #3.

**Resolution:** add the two-order `preflight` call to the same test and assert the verdicts differ
(or simply that the neutral gate cannot be relied on), so the contrast is a measured fact in the
suite rather than a docstring claim.

### F4 — Informational, not a 3C regression. A logger names the module Phase 4 will delete.
`src/sysml_codegen/elaboration/project.py:83`

`_CONSTRAINT_LOGGER = logging.getLogger("sysml_codegen.analysis.constraint_lowering")` is the only
textual reference to the legacy module left in either exact file. It creates no import and does not
weaken the decoupling. `git log -S` places it at `b9c22c0` (Item 5), so it predates this slice and
is not a finding against it. Flagging it because Phase 4 should retire the string with the module;
left alone it becomes a logger named after code that no longer exists.

---

## Verification performed

### 1. Decoupling is real, not cosmetic — CONFIRMED

- AST walk over `elaboration/elaborate.py` and `elaboration/project.py`: no `ImportFrom`/`Import`
  node referencing `constraint_lowering`. Full-text grep finds only the F4 logger string.
- Fresh interpreter importing *only* those two modules: no `constraint_lowering` in `sys.modules`,
  so the decoupling holds transitively, not just at the top of the file.
- Moved bodies diffed against their `38c2e15` definitions: `ModeledDefault` and
  `resolve_modeled_default` **byte-identical**; `mint_constraint_id` differs **only in its
  docstring** (a cross-reference and a two-line rationale). Code identical.
- Legacy re-import genuine: `constraint_lowering.mint_constraint_id is
  core.identifier_types.mint_constraint_id` → True, same for `resolve_modeled_default` and
  `ModeledDefault`; `mint_constraint_id` still in `constraint_lowering.__all__`. The module's three
  internal call sites are bare-name calls resolving through the module global, so
  `monkeypatch.setattr(constraint_lowering, "mint_constraint_id", ...)` still intercepts them.
- Legacy monkeypatch test run: `test_constraint_lowering.py:679-685` (patches the old path) passes.

### 2. Rendered-implementation fix — CONFIRMED as a real bug fix, corpus-safe

Reproduced at `38c2e15` against the same fixture, with import paths forced to the old worktree:

| | `38c2e15` | `7af5dc9` |
|---|---|---|
| `execution_steps` | `[]` | `scaled`, `half` |
| `output_expressions` | `scaled`, `half`, `doubled_half` | `half`, `doubled_half` |
| `output_count` vs projected schema (`['half','doubled_half']`) | **3 vs 2** | 2 vs 2 |
| generated stencil executed | **`NameError: 'scaled'`** | `(4.0, 8.0)` |

Both failure shapes are present at `38c2e15` and gone at `7af5dc9`. The old stencil's return
statement references `scaled` and `half`, neither of which the function assigns.

**No previously-correct output changed.** I rendered `auto_impl_context` for every module across
the entire fixture corpus at both commits and diffed: **78 fixtures scanned, 36 elaborated
successfully, 110 modules with a rendered context, and exactly one fixture differs —
`exact_calc_ordering`.** The 42 fixtures that raise produce byte-identical error classes on both
sides.

I also checked the fix's load-bearing ordering assumption, which the docstring asserts but no test
states: returns are sorted with `sorted(compilation.declared_output_ids)` (raw `UUID`, ordered by
128-bit int) while projection sorts on `DeclarationId.to_wire()` (the canonical hex string,
`identity.py:58`). These agree because canonical UUID text is fixed-width lowercase hex, where
lexicographic and numeric order coincide — 0 disagreements over 200,000 random pairs. The
assumption is safe.

One edge I probed and cleared: `_calculation_auto_impl_context` skips members whose
`python_expression is None`, which would silently drop a needed assignment step. Under the
`FULLY_COMPILABLE` guard this is unreachable — `classify_compilability`
(`expression_compiler.py:139-143`) requires *every* result to be `FULLY_COMPILABLE`, and every such
result is constructed with a non-`None` expression (`:554`). Defensive, not a silent-failure path.

### 3. `preflight_identified` — CONFIRMED, and it is a genuine second gate

- It never calls `evaluate_profile`. It takes an already-decided `IdentifiedProfileResult` and
  partitions it; `preflight` takes neutral facts and evaluates them first. The only shared code is
  `_partition_decisions`, which is the four-bucket split — the trivially common part. Different
  input type, different association semantics. Not a wrapper.
- Disagreement where identity is ambiguous, and agreement where it is not: measured, see F3. The
  exact gate followed the UUID in all four order/association combinations; the neutral gate flipped
  on list order.
- Both shipped tests pass.

### 4. Retained duals honest — CONFIRMED

All 8 pairs callable at the paired heads, each half a **distinct object** (no silent aliasing):

| repo | exact | legacy | both present, distinct |
|---|---|---|---|
| codegen | `compile_calc_def_exact` | `compile_calc_def` | ✓ |
| codegen | `ExactCompilationResult` | `CompilationResult` | ✓ |
| codegen | `ExactCalcDefCompilationResult` | `CalcDefCompilationResult` | ✓ |
| codegen | `CalculationDefinitionData.*_by_id`, `all_member_ids` | `.output_expression_asts`, `.member_expressions`, `.all_member_names` | ✓ (all 7 fields present) |
| agentic | `extract_identified_constraint_facts` | `extract_constraint_facts` | ✓ |
| agentic | `evaluate_identified_profile` | `evaluate_profile` | ✓ |
| agentic | `IdentifiedProfileResult` | `ProfileResult` | ✓ |
| agentic | `preflight_identified` | `preflight` | ✓ |

**No rename hunk leaked.** The strongest available evidence: every dual-bearing source file is
**byte-untouched** by the slice — `extraction/expression_compiler.py`, `extraction/data_models.py`,
`extraction/extractor.py`, and agentic `sysml/constraint_extraction.py` all show an empty diff
across the slice range. The one touched file carrying duals, `sysml/executable_profile.py`, I read
in full: its only changes are the `__all__` addition, the `Sequence` import, the duplicate-helper
removal, and the `preflight` refactor. No rename.

**The 11 forensic test shims did not come across.** The forensic shape (parts bin
`ed5b8b02:tests/test_sysml/test_executable_profile_v3.py:38-48`) is a module-local `def
evaluate_profile` fabricating `UUID(int=10_000 + index)` and returning a `SimpleNamespace`. No such
shim exists anywhere in agentic `tests/` at `8b63393` — the only `SimpleNamespace` uses are in
`test_aggregation.py`, pre-existing and mocking parser nodes. Only 1 of the 11 forensic test files
changed in this slice (`test_executable_profile.py`, additively);
`test_public_api_exports.py`, which the forensic patch stripped assertions from, is untouched.

### 5. Quality-cleanup hunks — each verified separately

- **Hunk 1 (shadowed duplicate) — CONFIRMED.** At `5088b417`,
  `_promote_non_numerical_diagnostic` is defined twice, at lines **950 and 968**, and the two source
  segments are **byte-identical**. Python binds the last, so the first was the unreachable one; the
  hunk removes the second and the survivor is byte-identical to both. Zero behavior change.
  (The notes say "the second shadows the first and nothing can reach it" — the unreachable copy is
  the first, not the second. Byte-identity makes the distinction moot; noting only for precision.)
- **Hunk 2 (import fallback) — CONFIRMED dead.** The module imports `agentic_mbse.sysml.*`
  absolutely at `:12`, so the package must be installed either way. Executed as a script from `/tmp`
  at both commits: both print the `--help` banner with rc=0. The old `from common import` fallback
  worked only because direct execution puts the script's own directory on `sys.path`; it was never
  the sole working path. The new absolute import is strictly more robust.
- **Hunk 3 (`load_manifest`) — red→green confirmed, narrowing NOT fully covered.**
  `test_manifest_valid_yaml_that_is_not_a_mapping` is genuinely red at `5088b41`
  (`AssertionError: assert ['alpha', 'beta'] is None` — the notes' quoted evidence verbatim) and
  green at `8b63393`. Callers searched: one production caller
  (`level6_architecture.py:124`); the `load_manifest` at
  `tests/corpus/pipelines/track1_cropped_extraction.py:217` is an unrelated local function of the
  same name. See **F1** for the case the narrowing now lets escape.

### 6. Item 6 pins unmoved — CONFIRMED

`test_elaboration_payload_identity.py` run explicitly: **13 passed**.
`test_profile_block_halts_exact_route_before_projection` (`:236-266`) covers all three routes in
one test — strict raises `ElaborationDiagnosticError`, lenient carries exactly one
`SI_CONSTRAINT_BLOCKED` diagnostic, and the encode/decode round trip preserves it such that
projecting the rebuilt graph raises `ProjectionError`. The fail-closed boundary guards
(`missing`/`formal`/`output`, conflicting identity, and the
`missing`/`duplicate`/`unrecognized` decision-inventory cases) all pass.

### 7. Gates re-run in both repositories — ALL CONFIRMED

| gate | claimed | measured by me |
|---|---|---|
| codegen full licensed suite | 3528 / 47 / 18 | **3528 passed, 47 skipped, 18 deselected**, exit 0, license lines **0** |
| codegen collection delta vs `38c2e15` | +8, zero removed | node-ID set diff: **8 added, 0 removed** — exactly the 5 compiler-core + 3 constraint-route tests |
| agentic full suite | 1824 / 1 / 5 | **1824 passed, 1 skipped, 5 deselected**, exit 0 |
| agentic collection delta vs `5088b41` | +5, zero removed | node-ID set diff: **5 added, 0 removed** |
| execution lane | 18 | **18 passed** |
| 3A/3B surface (8 modules) | 70 | **70 passed** |
| codegen `ruff check src` | byte-identical | **identical**, 16 findings both sides; new test modules `All checks passed!` |
| agentic `ruff check src` | identical, 1 finding | **1 finding** both sides |
| agentic `mypy src` | 118→108, zero new, ten fixed, all from cleanup hunks | **118 → 108**; set diff: **0 new, exactly 10 fixed** — 1 `no-redef` (hunk 1), 8 `import-not-found`/`no-redef` at `level4_constraints.py:31` (hunk 2), 1 `no-any-return` (hunk 3). **All ten attributable.** |
| `git diff --check` | clean | clean, both repos |
| changed paths ⊆ declared | equal | codegen **17 paths = declared set exactly** (incl. all five `build_constraint_generation_plan` call sites and the 2 mid-slice deviations); agentic **5 = declared set exactly**. No docs, spikes, probes, snapshots, or baselines touched. |
| legacy CLI smoke | 48 files, 3 params JSONs, 0.35 | **48 files**, `inputs/{hif_driver,hif_plant,ife_plant}_params.json` all present, `hif_driver__HIF_Driver__efficiency: 0.35` |

**Red-then-green claims verified by running the new tests against the old commits** (with import
paths forced, per the trap noted above):

- codegen at `38c2e15`: **5 failed, 3 passed** — matching the claim exactly. The three ordering
  cases fail with the notes' quoted output (`['scaled','half','doubled_half']` vs
  `['half','doubled_half']`; `execution_steps` empty), the legacy-import check fails on
  `elaborate.py`, and the shared-helper check fails with `ImportError: cannot import name
  'mint_constraint_id'`.
- agentic at `5088b41`: the 2 `preflight_identified` tests **fail by collection** (module import
  error), `test_manifest_valid_yaml_that_is_not_a_mapping` **fails by assertion**, and the 2
  cleanup guards pass. Exactly the claimed 1 + 2 + 2 split.

Small imprecision, not a finding: the notes name the collision and cycle cases as the green-before
guards (2), but 3 codegen tests are green before —
`test_identified_facts_gate_and_projected_constraints_agree_by_usage_id` is also a guard.

### 8. Test quality — meets the established bar

- **The script-execution test really executes the file as a script.**
  `test_direct_file_execution_resolves_its_shared_helpers` (quality-checks `:591`) runs
  `subprocess.run([sys.executable, level4_constraints.__file__, "--help"])` — a real interpreter on
  a real path, not an import with a patched `__name__` — and asserts rc 0, the banner in stdout, and
  no `ImportError` in stderr.
- **The preflight tests derive expectations from the model, not the implementation.**
  `test_exact_gate_partitions_every_outcome_and_follows_the_uuid_association` builds two twins with
  hand-written opposite predicates and asserts the *specific* diagnostic reason
  (`block_integer_equality_unpreservable`) plus a partition-totality check
  (`len(blocking)+len(admitted)+len(non_numerical)+len(unassessed) == len(usages)`). The agreement
  test compares two independently produced gates on shared input rather than either against itself.
  See F3 for the one place the derivation stops short.
- **No self-comparison in the codegen tests.**
  `test_identified_facts_gate_and_projected_constraints_agree_by_usage_id:66-72` derives the live
  usage-UUID set from the model via `SysideAdapter` and requires the decision map to equal it, then
  walks each UUID through the elaborated graph and the projected modules.
  `test_returned_values_line_up_with_the_projected_output_schema` checks the rendered return list
  against `ordering_module.outputs` — two independently produced structures, which is exactly the
  cross-check the ordering fix needs.
- **No production code is monkeypatched away.** The one `monkeypatch` in the new modules
  (`test_exact_compiler_core.py:105`) replaces `extract_feature_refs` to hand-build a dependency
  cycle no fixture can express — constructing an input, not stubbing the subject.
- The synthetic `UUID(int=201)` values in the agentic tests are test data for real production
  calls, not the forensic fake-UUID shim pattern, which replaced production functions.

### Code integrity

`build_constraint_generation_plan` narrowing from `PipelineContext` to `ComputationGraph`
(`generation/constraint_plan.py:25`) is a real improvement, not churn: the function read exactly one
attribute off the context, and two test call sites had been fabricating a `SimpleNamespace` context
to satisfy the wider signature. Those fabrications are gone. No god function, no mode flag, no
policy in a utility.

The `_calculation_auto_impl_context` rewrite is one rule with no sentinel parameter — the notes
record that the forensic version branched on an `output_crossrefs` flag and duplicated both loops
under it, and rejecting that was the right call. No new findings here.

---

## Certification

**CERTIFY.** All three claimed proofs hold under independent measurement, every gate number in the
completion notes reproduced exactly, no Item 6 pin moved, no test was removed or silenced in either
repository, and changed paths equal the declared sets. The product-lens gate is CLEAR; the one
structural smell that fired (retained duals) is disposed with a named Phase 4 owner.

The four findings are non-blocking. **F1 should be fixed before Slice 3D** — it is a regression this
slice introduced, and it is a two-line change plus a test. **F2 should be fixed whenever the pin is
next touched**; the property it guards is currently true, but the guard would not notice it becoming
false. F3 strengthens an existing test. F4 is a Phase 4 cleanup note.

**Not checked:**

- **Real TEAx execution.** Slice 3C declares `N/A` for it and I did not run it. The generated
  stencil correctness above is a direct execution of the rendered function in isolation, not a
  SimKit run. Slice 3D owns the real-TEAx proof.
- **The Fusion Tea customer vertical** beyond the legacy CLI smoke (48 files, params JSONs, the
  0.35 value). I did not compare full package bytes against a stored baseline, and I did not run the
  37-path corpus comparison — both are 3D scope.
- **The exact route's behavior under `--from-snapshot`** for the new ordering fix. The corpus
  comparison drove the live `elaborate → project` path only; I did not re-capture snapshots and
  re-render from them.
- **The 42 fixtures that raise during elaboration.** I confirmed their error classes are identical
  across the two commits but did not audit whether any of those failures is itself a defect — they
  are pre-existing on both sides and out of this slice's scope.
- **agentic-mbse `mypy` findings that remain** (108). I verified zero are new and ten were fixed; I
  did not assess the pre-existing 108.
- **Phase 4 deletion readiness.** Whether the eight duals can actually be collapsed, and whether the
  54 forensic `delete` rows are valid, is Gate 4A's job and I made no judgment on it.
- **Performance and scale.** No timing or memory measurement; the corpus run was correctness-only.
