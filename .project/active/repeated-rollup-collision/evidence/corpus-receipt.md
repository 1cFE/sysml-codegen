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
