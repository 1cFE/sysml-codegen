# Whole-corpus byte check (design review S1)

What it is: every model root `fixture_classes.model_roots()` classes as generating, plus the two expected flips (`unresolvable_attr_probe`, `elab_native_plural_scope`), generated through the public route (`prepare` then `emit_package`) by `evidence/corpus.py`, once on `main` (`e6c20bca`, run from a worktree) and once on this branch, then compared with `diff -rq` over the whole output trees.

## Phase 2 (registry change in, writers not yet changed)

- `main`: 165 roots generated; `unresolvable_attr_probe` and `elab_native_plural_scope` refused (`REGISTRY_CLASS_NAME_COLLISION`).
- Branch: 167 generated, none refused.
- `diff -rq`: the only differences are the two flipped roots (refused tree on `main`, full package on the branch). The other 165 package trees are byte-identical, every file.

## Phase 3 (writers and duplicate-path check iterate class owners)

- Branch: 167 generated, none refused.
- `diff -rq` against `main`: still only the two flipped roots. The other 165 trees are byte-identical.
- Against the phase 2 run, only `elab_native_plural_scope` changed: its second rollup copy's files (`modules/.../plant/shadow/total.py` and its stencil) are no longer written, since `selected` and `shadow` share one class at `plant/selected/total.py`, and the package and generation manifests change with the file list. `unresolvable_attr_probe` is unchanged between phases, because formula classes already had one definition path.

## Audit follow-up (stencil path and `first_copy`)

After `generation/stencils.py` moved to `module_python_path` and projection and `class_owners` moved to the shared `first_copy`, I re-ran `evidence/corpus.py` on the branch and compared it with a run made just before those changes. That run covers 178 roots: the 167 above plus the 11 generating `repeated_rollup` fixtures (including `specialized_renamed`). `diff -rq`: no differences. The public package oracle (22 snapshots) passes unchanged in the full default run.

## Sibling-override leak fix (D9)

Same method, both runs from the tree at `e34d1402` (so both use the same fixture list, which now includes the new leak fixtures and classes the three flipped cases as generating): once as is, once with `src/sysml_codegen/elaboration/occurrence.py` restored from `b4ba01fc` (the commit before the fix). 186 roots each. Before the fix 183 generated and 3 refused; after, 186 generated.

`diff -rq` differences:

- **The three expected flips** (`candidate-es-008__nested_named_subset__part_usage`, `..._single_rack`, `candidate-es-008__sibling_subsets_redefine__part_usage`): refused before, full package after.
- **The five new leak fixtures** (`repeated_rollup/leak_rollup`, `sibling_override_leak/{nested_specdef,specialized_top,deep_chain,new_members}`): each leaked before the fix and gives per-copy values after (see `test_sibling_override_leak.py`).
- **Two more cases the investigation did not predict**, both already generating and both carrying the leak: `candidate-es-008__one_subset_redefines__part_usage` and `candidate-es-008__outer_redefinition__part_usage`. Only `inputs/fx_params.json`, `schemas/fx_params.py` and the two contracts change, and only in PSU efficiency defaults. Before the fix the one 0.95 override reached PSUs it does not own: 11 of 12 in `one_subset_redefines` (only `rack_1.server_1` sets it) and 8 of 11 in `outer_redefinition` (only `rack_1`'s `part :>> servers` sets it). After the fix those PSUs read the definition default 0.9 and the owners keep 0.95. This is the leak's removal, not a new change; the report's "nothing that builds today changes" was based on the 22-snapshot byte-identity tests, which do not include these cases. Their stored answers hold only the outcome (`generated`), so no test saw the change. Native SysIDE was not run on these two models.

Every other root's tree is byte-identical.
