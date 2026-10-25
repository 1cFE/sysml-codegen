# Whole-corpus byte check (design review S1)

What it is: every model root `fixture_classes.model_roots()` classes as generating, plus the two expected flips (`unresolvable_attr_probe`, `elab_native_plural_scope`), generated through the public route (`prepare` then `emit_package`) by `evidence/corpus.py`, once on `main` (`e6c20bca`, run from a worktree) and once on this branch, then compared with `diff -rq` over the whole output trees.

## Phase 2 (registry change in, writers not yet changed)

- `main`: 165 roots generated; `unresolvable_attr_probe` and `elab_native_plural_scope` refused (`REGISTRY_CLASS_NAME_COLLISION`).
- Branch: 167 generated, none refused.
- `diff -rq`: the only differences are the two flipped roots (refused tree on `main`, full package on the branch). The other 165 package trees are byte-identical, every file.
