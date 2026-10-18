# Spike S1: in-process raise elision (B2) and corpus run time (B3)

**Date:** 2026-10-18. **Trees:** sysml-codegen `subset-conformance` at `07fd2374` (clean apart from this folder); agentic-mbse sibling `subset-conformance` at `882edc6a`. SysIDE 0.8.4, Python 3.12.3, licensed. **Serves:** [design.md](../../design.md) B2, B3, D5 and "De-risk first". Nothing here is committed, and no product code was changed.

## Summary of Findings

**B2 is confirmed for the mechanism and only partly confirmed for the rule D5 states.** A test helper can disable one site in-process at every code shape the design names. It cannot do so by eliding `raise` statements alone, and a flip is not always visible in codes.

- **The mechanism works everywhere it was tried.** The helper recompiles the outer function with the site's statement replaced and assigns the new code object into the existing function object (`fn.__code__ = new`). The function object keeps its identity, so every by-name import sees the change and no re-binding is needed. It worked for a module function imported by name elsewhere, a private module function, a `_ExactElaborator` staticmethod and method, a nested function (through its outer function), an agentic-mbse `reference_use` function and two `calc_compat_renderer` stub sites. Restoring the old code returned all cases to baseline.
- **"Elide one `raise`" reaches only 15 of the 42 public sites that are linked to a rule or matrix row.** The other 27 record a finding instead of raising: `self._diagnose(...)`, `self._record_readiness(...)`, `diagnostics.append(_diagnostic(...))` or `return [_diagnostic(...)]`. If the rule widens to "neutralize the statement that emits the site" (a call statement becomes `pass`, `return [finding]` becomes `return []`), 38 of 42 are reached, and 478 of all 502 scanned sites. The 4 linked sites still left need a hand patch. Three are in agentic-mbse `executable_profile._evaluate_usage_against_definition`. The fourth is codegen's `_indexed_refusal`, a factory whose caller does the raising.
- **8 of 10 behavioral elisions flipped their witness, and none changed any other case.** The other 2 were shadowed: a later check raised the same observable outcome. Eliding `build_containment_address` (the ES-002 site) let the case reach `_resolve_semantic_reference`, which refused with the same code, `SI_OCCURRENCE_MISSING`. Eliding the `_render` unsupported-node raise fell through to the "Unknown IR node type" raise, and the calc stayed `MANUAL_REQUIRED`. In both runs the elided site really stopped firing, and only the message changed. **So a mutation test that compares codes and compilability will report false survivors.** It needs the per-site reason from D8, and the D9 stub cause for stubs, with distinct values for sites that can shadow each other.
- **Mutating a shared agentic-mbse site moves both halves.** Eliding `_require_supported_invocation` changed the generator's code and also the screen's verdict. The same happened for an `executable_profile` site. Mutation still detects drift, because both stored answers mismatch. But for these sites it is not evidence that is independent of the screen.

**B3 is confirmed with room to spare.** In-process, a small case takes about 9 ms for the generator half and about 4 ms for the screen half. Ten cases take about 0.22 s warm. Both halves over all 152 fixture directories take 22.5 s, and two fixtures account for 14 s of that. The extrapolated corpus costs about 30 to 40 s in total. The current licensed suite takes 113 s, so the corpus would add about a third (see Log 7). Item 1's 70 s for 73 models came from the subprocess-and-export method, so it does not predict the in-process cost.

**What this means for the design.**

- D5 should say "neutralize the statement that emits the site, chosen by site ID". Its fallback list starts with the 4 named hand patches.
- D5's mismatch should be judged on stored reasons and stub causes, not codes alone. That makes D8's reasons a dependency of group B and E mutations: a site's mutation test can only pass once its reason exists.
- The group B and E mutation estimates do not rise for hand patches. They do depend on D8 reasons landing first, and on choosing distinct reasons for sites that shadow each other, such as ES-002 and ES-009.

## Question / Goal

1. **B2.** Can a test helper elide one `raise`, chosen by scanner site ID, in-process? The shapes to try: a module function, an `_ExactElaborator` method, a nested function, an agentic-mbse `reference_use` site and a `calc_compat_renderer` stub site, including functions that other modules import by name. Does each elision flip its own case's outcome and no other case's? *Confirmed if* every shape elides and flips only its witness. *Disproved if* some shape cannot be reached in-process, or an elision fails to flip its witness or flips another case.
2. **B3.** What is the end-to-end time for ten cases (a live generator run with the screen made to raise, plus the screen evaluation)? What does that extrapolate to for about 200 cases, 150 fixtures and 120 mutation runs? *Confirmed if* the extrapolated total fits beside the current licensed suite without dominating it.

## Log

All commands run from the sysml-codegen worktree root after `set -a; source ../agentic-mbse/.env; set +a`. Below, `S=.project/active/subset-profile-conformance/spikes/s1` and `PY=.venv/bin/python`. Output files sit beside the scripts.

### 1. Site IDs resolve on the live trees

Item 1's scanner (agentic-mbse `scripts/subset_profile/scan_sites.py`) has a `scan_sources(codegen_src, agentic_src)` function that works on any source directory. Run on the two installed package trees, it produced 502 sites. Its IDs equal the 502 rows of agentic-mbse `tests/fixtures/subset_profile/inventory/site_account.csv` exactly: 0 scanned sites without a row, and 0 rows without a site. So site IDs from the account resolve to a live file and line without a git export. The scan takes about 1.5 s.

A scanner "site" is the code-carrying *call*, for example `ReadinessFinding(...)`, `self._diagnose(ElaborationCode...)` or `_diagnostic(...)`. It is not always a `raise`. That matters in step 4.

### 2. The helper (`elide.py`)

- Looks up the site row, imports the module and parses its source.
- Finds the innermost statement whose lines contain the site's line.
- Strict mode requires that statement to be a `raise`. Generalized mode also accepts a bare call statement and `return [ ... ]`.
- Replaces the statement in the AST of the outermost function that owns it. That is a module function or a method directly in a class body; a nested function is handled through its outer function.
- Compiles that one function with the module's `from __future__ import annotations` flag and decorators stripped. It wraps the function in a dummy class if the original has a `__class__` cell.
- Assigns the new code into the original function object's `__code__`. Staticmethods and classmethods are unwrapped to the function first.
- `restore()` assigns the original code back.

The test cases are in `harness.py`:

- 8 Item 1 probes, used in place from agentic-mbse `tests/fixtures/subset_profile/probes/`.
- 3 spike models under `models/`: `recursive_containment`, `calc_stub_operator` (`a % b`) and `calc_stub_gt` (`a > b` in a Real calc def).
- The generator half calls `run_codegen` under a tripwire that makes `extract_subset_facts`, `evaluate_subset_profile` and `extract_occurrence_structure` raise wherever they are bound. It reads codes from the ERROR log records with the regex `SI_[A-Z0-9_]+:`, and reads `CalcNode.compilability` from a spy on `elaborated_pipeline.elaborate_model_paths`.
- The screen half runs `SysideAdapter.load_model`, then `extract_subset_facts`, then `evaluate_subset_profile`.

`$PY $S/baseline.py` shows every case with its Item 1 outcome. `calc_stub_operator` and `calc_stub_gt` generate with `fx::Rem` at `manual_required`. The tripwire was never hit, so the generator half does not call the screen today.

### 3. Strict elision, one site per shape (`$PY $S/matrix.py` → `matrix.out`)

Every case was run under each mutation and compared with the unmutated baseline on (generated, codes, stubs) and on the screen's (verdict, findings).

| Shape | Site (function, code) | Witness | Generator result |
|---|---|---|---|
| module function, imported by name into `elaborate.py` | `occurrence.build_containment_address`, `SI_OCCURRENCE_MISSING::1` | `candidate-es-002…` | **same codes**: shadowed (step 5) |
| private module function | `occurrence._multiplicity_indices`, `SI_MULTIPLICITY_UNSUPPORTED::3` | `part-multiplicity__range__expanded_part_usage` | refused → generated |
| `_ExactElaborator` staticmethod | `_require_one_writer`, `SI_REDEFINITION_INVALID::1` | `candidate-es-008…` | refused → generated |
| `_ExactElaborator` method | `_resolve_semantic_reference`, `SI_OCCURRENCE_MISSING::4` | `candidate-es-009…` | `SI_OCCURRENCE_MISSING` → `SI_OCCURRENCE_AMBIGUOUS` |
| nested function | `build_occurrence_index.add_usage`, `SI_CONTAINMENT_RECURSIVE::1` | `recursive_containment` | → `SI_INTERNAL_DEFECT` (RecursionError, 0.9 s) |
| agentic-mbse `reference_use` | `_require_supported_invocation`, `EXPRESSION_KIND_UNSUPPORTED::1` | `invocation-callable__unsupported_callable__attribute_value` | `SI_EXPRESSION_SOURCE_UNSUPPORTED` → `SI_EDGE_DANGLING`; **screen also flipped** `refused_incomplete` → `refused` |
| `calc_compat_renderer` stub | `_render_operator`, `CompilationError::1` (line 115) | `calc_stub_gt` | `manual_required` → fully compilable |
| `calc_compat_renderer` stub | `_render`, `CompilationError::2` (line 78) | `calc_stub_operator` | **same**: shadowed (step 5) |
| non-raise | `_collect_bound_members`, coded-returned | `binding-source__expression_source…` | strict mode refused: the statement is `self._record_readiness(...)` |
| non-raise | `expression_evidence._indexed_refusal` | `indexed-reference…attribute_value` | strict mode refused: the statement is `return SemanticEvidenceError(...)` |

No case other than the witness changed under any mutation, in either half. After all the mutations, every case was back at baseline ("restore check: … True"). Each pass over the 11 cases took 0.21 to 0.34 s, except the recursion one at 0.95 s.

Two side observations:

- My first stub model (`a % b`) reaches `_render` line 78, not `_render_operator`. `%` becomes an `UnsupportedNode` in agentic-mbse's IR. `$PY $S/which_stub.py calc_stub_gt` confirmed that `a > b` reaches line 115.
- Eliding line 115 renders `(inputs.aNoneinputs.b)`, which is valid Python, so the calc "compiles". Replacing a raise with `pass` shows that the detector is gone. It does not make the shape supported.

### 4. Reachability over all sites (`$PY $S/reach_all.py [--generalized]` → `reach_all.out`, `reach_all_generalized.out`)

The script applies the helper to each of the 502 sites and restores it at once, without running a model. It found no compile failures and no free-variable mismatches.

| | strict (raise only) | generalized |
|---|---|---|
| all 502 sites reached | 390 | 478 |
| public sites linked to a rule or matrix row (42) | 15 | 38 |
| public sites not linked (49) | 40 | 49 |

`nonraise_linked.out` lists the 27 linked public sites that strict mode cannot reach. They are codegen `_diagnose` and `_record_readiness` calls, `project._float_default`'s `_fail(...)`, and 22 sites in agentic-mbse `executable_profile.py`. Those 22 are `diagnostics.append(_diagnostic(...))` or `return [_diagnostic(...)]`, all on the `constraint-predicate` rule.

The 4 linked sites that generalized mode still cannot reach:

- `executable_profile._evaluate_usage_against_definition`, three times: `return _non_executable_block(usage, _diagnostic(...))` and `return _missing_body_block(usage, _diagnostic(...))`.
- `expression_evidence._indexed_refusal`: `return SemanticEvidenceError(...)`. The raise is in its caller.

### 5. The two non-flips are shadowing, not failed elision (`$PY $S/diagnose.py`, `$PY $S/which_stub_elided.py`)

The scripts hook the exception class's `__init__` to record which line constructs each refusal.

- `candidate-es-002`. Baseline: `OccurrenceResolutionError at occurrence.py:180 … cannot anchor containment`. Elided: the line 180 refusal no longer appears, and the run refuses with `SI_OCCURRENCE_MISSING: … exact owner address has no target for leaf …`. That is the `_resolve_semantic_reference::4` site, which is ES-009's site.
- `calc_stub_operator`. Baseline: `calc_compat_renderer.py:78 Cannot compile unsupported node: a % b`. Elided: `calc_compat_renderer.py:81 Unknown IR node type: UnsupportedNode`. The calc is still `manual_required`.

### 6. Generalized elision on non-raise sites (`$PY $S/matrix_generalized.py` → `matrix_generalized.out`)

This run used 12 cases: the 11 above plus `constraint-predicate__blocked_predicate__owner_instantiated`. `which_profile_site.py` showed that this probe fires `executable_profile.py:749` (`warn_non_numerical_predicate`).

- `_collect_bound_members`, where `self._record_readiness(...)` became `pass`: `SI_EXPRESSION_SOURCE_UNSUPPORTED` → `SI_EDGE_DANGLING ×2`.
- `_build_constraint_nodes`, where `self._diagnose(SI_CONSTRAINT_BLOCKED…)` became `pass`: refused → `PREDICATE_COMPILE_FAILED` at generation. The spike's regex does not capture that code, but the outcome still changed.
- `executable_profile._walk_proposition:749`, where the `append` became `pass`: the generator flipped the same way, and **the screen flipped** `refused` → `clear`.
- `_indexed_refusal`: refused, as expected.

No other case changed, and the restore check passed.

### 7. Timing (B3)

`/usr/bin/time $PY $S/timing.py`, three fresh processes (`timing.out`):

- imports 0.10 s; first case, both halves, cold: 0.35–0.42 s; site scan 1.4–1.5 s; one elision 6–7 ms.
- warm pass over 10 cases, both halves: median 0.21–0.23 s.
- per case: generator median 8.5–9.2 ms (max 57 ms); screen median 3.9–4.6 ms (max 25 ms).
- 10 generator runs under one mutation: 0.20 s. Process wall time 3.3 s, max RSS about 290 MB.

`$PY $S/fixtures_timing.py` (`fixtures_timing.out`) ran both halves on every `tests/fixtures/*` directory that holds `.sysml`, which is 152 directories. Each directory was treated as one root. That measures cost only; it does not decide fixture classes.

- Total 22.5 s: generator 14.0 s, screen 8.3 s.
- `catf_mfe_model` takes 3.7 + 3.5 s and `catf_mfe_gated` takes 3.7 + 3.1 s. Everything else is under 1 s each.

The current licensed suite (`uv run --extra dev pytest tests/ -q`) with `-x` stopped after 64.7 s at 1151 passed and 1 failed. The failure is an unrelated, existing one: `test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees` flags `project_templates/MODELING_PROCESS.md.template`. The full run without `-x` took 113.5 s wall time: 2735 passed, 9 skipped, 10 failed. The other 9 failures are in `tests/unit/test_check_ledger_4a.py`. They fail because `git diff 1672c57 07531e64` exits 128 (those commits are not in this worktree), so they are environment failures and not caused by the spike. The untracked spike folder is outside `tests/`.

**Extrapolation:**

| Part | Basis | Estimate |
|---|---|---|
| ~200 cases, both halves | 22 ms per case, measured | 4–5 s; up to about 10 s if some cases are larger |
| tripwire (generator half again for every case) | 9 ms per case | about 2 s |
| ~150 classified fixtures | the actual 152 directories, measured | about 23 s, 14 s of it from the two `catf_mfe` fixtures |
| ~120 mutation runs, witnesses only | 6 ms elision + about 2 witnesses × 10 ms | about 3 s; about 216 s if each mutation re-ran all 200 cases |
| scanner | 1.5 s per scan | 1.5 s if cached per session |
| **total** | | **about 30–40 s**, against a current licensed suite of 113 s |

## What it means for D5 and the estimate

- **The helper design.** Use code-object replacement, not module re-binding. It makes the "every module that imported the same function object by name" step in D5 unnecessary.
- **The rule.** Change "elides one `raise` statement" to "neutralizes the one statement that emits the site: `raise` → `pass`, a recorder call → `pass`, `return [finding]` → `return []`". Name the fallback hand patches now: the 3 `_evaluate_usage_against_definition` returns and `_indexed_refusal`, which is patched at its caller's raise. For `constraint-predicate`, design D5 already keeps the shared tables out of scope. Which of the 22 `executable_profile` sites count as "shared tables", and which as "context and ownership logic", is still a plan decision.
- **The mismatch.** Compare on stored reasons and stub causes, not codes or compilability alone. Otherwise shadowed sites like ES-002 → ES-009 and `_render` 78 → 81 look like surviving mutants. This puts D8's `SiteReason` on the path of every generator mutation test. D8 must give shadowing sites distinct reasons. If both sites share a reason, a different observable is needed: an untested option is to replace the statement with a call to a recorder, so the test can tell "the site was reached" apart from "the outcome changed".
- **Independence.** A mutation of an agentic-mbse site (ES-005, ES-006, indexed reference, `executable_profile`) also changes the screen half. The design's independence argument should count those mutations as drift detection, not as evidence that is independent of the screen.
- **The estimate.** No hand-patch blow-up: about 4 patches, not about 110. Group B and E mutation cost is about what the design assumed. The new cost is ordering: a site's mutation test can only pass once its reason exists. B3 needs no mitigation beyond running witnesses only. Caching screen facts is optional at this scale.

## Reproduction

```bash
cd /home/reid/src/subset-conformance/sysml-codegen
set -a; source ../agentic-mbse/.env; set +a
S=.project/active/subset-profile-conformance/spikes/s1; PY=.venv/bin/python
$PY $S/baseline.py            # unmutated halves, 11 cases
$PY $S/matrix.py              # strict elision matrix (expected: the step 3 table)
$PY $S/diagnose.py            # which site fires, for the two shadowed witnesses
$PY $S/which_stub_elided.py   # _render::2 elided -> line 81 fires
$PY $S/matrix_generalized.py  # generalized elision on non-raise sites
$PY $S/reach_all.py; $PY $S/reach_all.py --generalized   # 390 / 478 of 502
$PY $S/nonraise_linked.py     # the 27 linked non-raise sites
$PY $S/timing.py; $PY $S/fixtures_timing.py
uv run --extra dev pytest tests/ -q -p no:cacheprovider   # current suite time
```

The scripts import agentic-mbse's `scripts/subset_profile/scan_sites.py` by absolute path. They expect the sibling worktree at `/home/reid/src/subset-conformance/agentic-mbse`.


## Open Questions / Follow-ups

- **Not tested:** functions behind `functools.lru_cache` or other caching wrappers. A swapped `__code__` would not clear cached results. None of the 10 behavioral sites had one, and I did not survey the tree.
- **Not tested:** a function with a `__class__` cell (zero-argument `super()`). The helper handles it, but no exercised site needed it.
- Stripping decorators moves `co_firstlineno` to the `def` line, so tracebacks inside an elided decorated function are off by the decorator lines. Behavior is unaffected.
- `__code__` replacement changes the whole process. It is safe under pytest-xdist, which runs separate processes. It is not safe if tests run in threads.
- "Only its own case flipped" was checked over 11 to 12 cases that were mostly unrelated. The real corpus will have many cases that share sites, so the "only" claim gets its real test in P1/P2.
- The spike regex reads only `SI_*` codes. `CodeGenerationError` prefixes such as `PREDICATE_COMPILE_FAILED:` need the D2 `extra={"refusal": …}` observation.
- Fixture timing treated every top-level directory as one model root. Container directories with several roots may cost a little more or less once they are classified.
