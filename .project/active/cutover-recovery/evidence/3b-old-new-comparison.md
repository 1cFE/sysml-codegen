# Slice 3B — old/new recovery comparison: parameter-group identity

**Comparator, not authority.** The legacy route detects change; it does not define
correctness. Correctness here is the model: a group is named after the file that declares
it, or — when that file is `model.sysml` and so carries no identity of its own — after the
package that declares the owning root occurrence.

Measured on every fixture under `tests/fixtures/`, one subprocess each, licensed.
`before` is `a7c13a6`; `after` is this slice. Group *identity* below means the
`(name, class_name)` pair; the group's recorded `source_file` label changed everywhere by
design (full path -> bare stem or package), and is compared separately in the route tests.

## 1. Exact-route group identity that changed in this slice

| fixture | before | after | why |
|---|---|---|---|
| `elab_constraint_formal_identity` | `[('elab_constraint_formal_identity_params', 'ElabConstraintFormalIdentityParams')]` | `[('constraint_formal_identity_params', 'ConstraintFormalIdentityParams')]` | `model.sysml` fallback moved from the parent directory to the declaring package |

**1 fixture(s) changed identity.** Every other projecting fixture keeps the exact name
and class it had at `a7c13a6`, including every stem-named one.

## 2. Exact vs legacy, stem-named fixtures (no `model.sysml`)

The ruling requires these to match the legacy route exactly, since the stem rule is
untouched. `moved by 3B` says whether this slice changed the exact side's identity.

| fixture | exact | legacy | verdict | moved by 3B |
|---|---|---|---|---|
| `attr_expr_probe` | `[('design_params', 'DesignParams')]` | `[('design_params', 'DesignParams')]` | match | no |
| `d316_crosspart_expose` | `[('design_params', 'DesignParams')]` | `[('design_params', 'DesignParams')]` | match | no |
| `d38_caret` | `[('library_params', 'LibraryParams')]` | `[('design_params', 'DesignParams')]` | **MISMATCH** | no |
| `deep_cross_scope_probe` | `[('design_params', 'DesignParams'), ('library_params', 'LibraryParams')]` | `[('design_params', 'DesignParams'), ('library_params', 'LibraryParams'), ('system_design', 'SystemDesign')]` | match (legacy also emits the hierarchy group) | no |
| `expr_paren_probe` | `[]` | `[]` | match | no |
| `quoted_owner_formula` | `[('design_params', 'DesignParams')]` | `[('design_params', 'DesignParams')]` | match | no |
| `retype_model` | `[('library_params', 'LibraryParams')]` | `[('library_params', 'LibraryParams')]` | match | no |
| `sample_model` | `[]` | `[]` | match | no |
| `unresolvable_attr_probe` | `[('design_params', 'DesignParams')]` | `[('system_design', 'SystemDesign')]` | legacy emits only the hierarchy group | no |
| `wi014_toy` | `[('toy_plant_params', 'ToyPlantParams')]` | `[('toy_plant_params', 'ToyPlantParams')]` | match | no |

### The one mismatch, named

`d38_caret` is the single stem-named fixture where the exact and legacy routes disagree:
exact says `library_params`, legacy says `design_params`. **This slice did not cause it and
does not touch it** — the fixture has no `model.sysml`, so the changed fallback never runs,
and the measured identity is byte-identical before and after (`moved by 3B = no`).

It is a pre-existing property of *which file each route thinks declares an entry point*: the
elaborator records a node's declaration site, which for this fixture is `library.sysml`, while
the legacy deriver attributes it to `design.sysml`. That is a declaration-site question, not a
naming-rule question, so no group-naming rule can reconcile it.

Surfaced rather than absorbed. It is pinned by
`tests/conformance/test_exact_group_identity.py::test_the_known_exact_versus_legacy_declaration_site_divergence`
so it cannot move unnoticed, and it needs a disposition before the public authority switch in
Slice 3E, where it would change a shipped input filename for a model of this shape.

## 3. Exact vs legacy, `model.sysml` fixtures

Legacy names all of these `model_params`, after the filename. That meaningless name is
what the ruling replaces, so a difference here is the fix landing, not a regression.

| fixture | exact | legacy |
|---|---|---|
| `constraint_def_owned_redefining` | `[('constraint_def_owned_redefining_params', 'ConstraintDefOwnedRedefiningParams')]` | `[('model_params', 'ModelParams')]` |
| `constraint_inline` | `[('constraint_inline_params', 'ConstraintInlineParams')]` | `[('model_params', 'ModelParams')]` |
| `constraint_multi_instance` | `[('constraint_multi_instance_params', 'ConstraintMultiInstanceParams')]` | `[('model_params', 'ModelParams')]` |
| `constraint_non_numerical` | `[('constraint_non_numerical_params', 'ConstraintNonNumericalParams')]` | `[('model_params', 'ModelParams')]` |
| `constraint_shared_polarity` | `[('constraint_shared_polarity_params', 'ConstraintSharedPolarityParams')]` | `[('model_params', 'ModelParams')]` |
| `elab_matrix_aggregations` | `[('elab_matrix_aggregations_params', 'ElabMatrixAggregationsParams')]` | `[('model_params', 'ModelParams')]` |
| `elab_matrix_c14` | `[('elab_matrix_c14_params', 'ElabMatrixC14Params')]` | `[('model_params', 'ModelParams')]` |
| `elab_matrix_c16` | `[('elab_matrix_c16_params', 'ElabMatrixC16Params')]` | `[('model_params', 'ModelParams')]` |
| `elab_matrix_c2` | `[('elab_matrix_c2_params', 'ElabMatrixC2Params')]` | `[('system_design', 'SystemDesign')]` |
| `elab_matrix_c21` | `[('elab_matrix_c21_params', 'ElabMatrixC21Params')]` | `[('model_params', 'ModelParams')]` |
| `elab_matrix_c23` | `[('elab_matrix_c23_params', 'ElabMatrixC23Params')]` | `[('model_params', 'ModelParams')]` |
| `elab_matrix_c3` | `[('elab_matrix_c3_params', 'ElabMatrixC3Params')]` | `[('system_design', 'SystemDesign')]` |
| `elab_matrix_c4` | `[('elab_matrix_c4_params', 'ElabMatrixC4Params')]` | `[('system_design', 'SystemDesign')]` |
| `elab_matrix_c5` | `[('elab_matrix_c5_params', 'ElabMatrixC5Params')]` | `[('system_design', 'SystemDesign')]` |
| `elab_matrix_c6` | `[('elab_matrix_c6_params', 'ElabMatrixC6Params')]` | `[('model_params', 'ModelParams')]` |
| `elab_matrix_c7` | `[('elab_matrix_c7_params', 'ElabMatrixC7Params')]` | `[('model_params', 'ModelParams')]` |
| `elab_native_plural_scope` | `[('elab_native_plural_scope_params', 'ElabNativePluralScopeParams')]` | `[('model_params', 'ModelParams')]` |
| `elab_shadowing_probe` | `[('elab_shadowing_probe_params', 'ElabShadowingProbeParams')]` | `[('system_design', 'SystemDesign')]` |
| `modeled_default_fidelity` | `[('modeled_default_fidelity_params', 'ModeledDefaultFidelityParams')]` | `[('model_params', 'ModelParams'), ('system_design', 'SystemDesign')]` |
| `shadowed_reference` | `[('shadowed_reference_params', 'ShadowedReferenceParams')]` | `[('model_params', 'ModelParams')]` |
