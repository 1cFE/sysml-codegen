# [NESTED-OVERRIDE-LEAKS-TO-SIBLING]: root cause

Read-only investigation run by a subagent on 2026-10-26 at branch HEAD `d2be97ce` (same code on base `e6c20bca`). Recorded here by the orchestrator from the subagent's report; the subagent could not write files. Scratch models were under `/tmp/claude-1000/leak-investigation/` (temporary); the patch and scripts are beside this file.

## Native SysIDE agrees the generator is wrong

`Compiler.evaluate_feature(..., scope=top)` on the reproducer plus `c : Sub20`: `a.leaf.capital_cost` = 10.0, `b.leaf.capital_cost` = 20.0, `c.leaf.capital_cost` = 20.0 (`scripts/native.py`).

## Cause

`src/sysml_codegen/elaboration/occurrence.py:503-511`, `OccurrenceIndex.occurrences_for_declaration`, returns every occurrence whose last step has the declaration's redefinition-family slot. `b`'s `part :>> leaf` and `Sub::leaf` share the slot `Sub::leaf`, so it returns `a.leaf[*]` as well as `b.leaf[*]`. Each occurrence already records its effective declaration (`effective_usage_id`, `occurrence.py:946-982`); the function never checks it.

Path of the wrong value: `_attachment` (`elaborate.py:848-853`) gives `b`'s writer scopes in `a.leaf[*]` (`elaborate.py:910-913`); `_build_value_nodes` lists it as a candidate (`:902-969`); `_select_writer` falls back to any usage writer (`:990-991`) and takes it. Trace: `scripts/trace.py`.

## Shapes

Rule: anything owned by a part usage that redefines another part usage leaks into every other copy of the redefined part, anywhere in the model, unless that copy has its own value. Leaks: nested override in a usage or a specializing def, single child, three levels deep, expression values, one-level part redefinition in a specialized definition (crosses into an unrelated root), two package-level roots, sibling with its own valueless `part :>> leaf[3]`, deep chain owned by a redefining usage (`elaborate.py:1227`), new attributes declared inside the redefinition, constraints inside it (`elaborate.py:1408`). Does not leak: plain attribute override in a usage or a specializing def, deep chain on a non-redefining usage, a value inside `Sub`'s own `leaf`, a sibling with its own exact writer.

## Fix

In `occurrences_for_declaration`, keep only occurrences whose effective usage is the declaration or redefines it (`fix.patch`, four lines; make `FeatureSlotIndex._redefines` public in a clean version). With the patch every leaking shape gives the right per-copy value, the non-leaking shapes are unchanged, and the audit's `leak_rollup` gives 30 / 60 / 90 in real TEAx (unpatched 60 / 60 / 120). Callers: four, all through `_attachment` (`elaborate.py:911`, `:1227`, `:1273`, `:1408`).

## What changes

Nothing that builds today changes; the corpus byte-identity tests pass. Three stored refusals flip to building: `candidate-es-008__nested_named_subset__part_usage`, `..._single_rack`, `candidate-es-008__sibling_subsets_redefine__part_usage` (52 test failures, all from those three and the `_require_one_writer` mutation witness).

Those refusals were caused by the leak, and removing them exposes a separate, pre-existing problem: the generator treats a named subset (`server_1 :> servers`) as an extra copy beside the indexed ones, so `rack_1` gets `servers[0]`, `servers[1]`, `server_1`, `server_2` (four servers in a `Server[2]`). A single named subset with one override already builds that way on stock and also leaks 0.95 into all seven PSUs. No backlog row covers the named-subset double counting.

One overcautious refusal remains (a chain of usage writers with no exact one; native gives 20). It is a refusal, not a wrong number.

## Not checked

The full execution lane; dc3 or other external models; a calc usage inside a redefining part; snapshot replay beyond the default suite; preserve-handwritten and smart regen; whether SysML counts `server_1 :> servers` as one of the two `servers`.
