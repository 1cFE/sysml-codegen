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
untouched. Ten fixtures, eight matching; the two that do not are analysed below. `moved by 3B` says whether this slice changed the exact side's identity.

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

### The two mismatches, named

**Neither is caused or touched by this slice.** Both fixtures lack a `model.sysml`, so the changed
fallback never runs on either, and both measure byte-identical before and after (`moved by 3B =
no`). Both are pinned by value in `tests/conformance/test_exact_group_identity.py` so they cannot
move unnoticed, and both need a disposition before the Slice 3E authority switch, where each would
change a shipped input filename **and** what that file contains.

Corrected 2026-08-11 after the 3B audit (F3, F5): an earlier version of this section named only
`d38_caret`, and described it as a declaration-site difference alone. Measured, both fixtures also
disagree on the entry-point *set*, which is the larger half of each.

**`d38_caret`** — exact `library_params`, legacy `design_params`.

| | parameters |
|---|---|
| exact | `noop__x`, `pack__exponent`, `pack__cell[0..3]__base_cost` (6) |
| legacy | `noop__x` (1) |

The one shared parameter is a declaration-site difference: the elaborator records the node's
declaration site (`library.sysml`), the legacy deriver attributes it to `design.sysml`, and the
group name follows from that. The other five are a content difference — the exact route resolves
the four modelled `cell` occurrences and the exponent that the legacy route drops.

**`unresolvable_attr_probe`** — exact `design_params`, legacy `system_design`. **The two routes
share no entry point at all.**

| | parameters |
|---|---|
| exact | nine `design_attribute` entries: `{derived_instance, design_derived_instance, grandchild_instance}` × their attributes |
| legacy | one `usage_literal`: `design_derived_instance__my_calc__x` |

This one is not a naming difference in any part. The exact route resolves the inherited design
attributes onto three concrete instances — behavior the Item 6 suite already pins as correct in
`test_elaboration_phase5_remediation.py::test_inherited_formulas_are_scoped_to_three_concrete_instances`.
The legacy deriver drops all nine and emits one literal instead, attributed to its synthetic
`hierarchy` source; *that* attribution is what names the group `system_design`. So the group name is
downstream of a **legacy fallback-attribution difference**: change the naming rule however you like
and these two routes still ship different files with different contents.

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
