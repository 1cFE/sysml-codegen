"""Owner-ratified Phase 5 remediation at the public projection boundary."""

from __future__ import annotations

from collections import Counter

from sysml_codegen.elaboration import NodeRef, ProducerRef, elaborate, project
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_evidence import ReadinessCode
from sysml_codegen.resolution.models import EntryPointType, ModuleKind
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def _exact(name: str):
    extractor = SysMLDataExtractor([FIXTURES_DIR / name])
    assert extractor.load_models()
    return project(
        elaborate(
            extractor.model,
            extractor.extract_calculation_definitions(),
            validation_diagnostics=extractor.diagnostics.validation,
        )
    )


def _internal(name: str, *, strict: bool = True):
    extractor = SysMLDataExtractor([FIXTURES_DIR / name])
    assert extractor.load_models()
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=strict,
    )


def _constraint_modules(graph):
    return [module for module in graph.modules if module.module_kind is ModuleKind.CONSTRAINT]


def _parameters(graph):
    return {
        parameter.qualified_name: parameter
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }


def test_return_styles_reaches_the_three_authored_self_bindings() -> None:
    graph = _internal("return_styles", strict=False)

    assert Counter(item.code for item in graph.diagnostics) == {
        ReadinessCode.SI_SELF_BINDING: 3
    }


def test_inline_constraint_references_a_real_modeled_input() -> None:
    graph = _exact("constraint_inline")
    [constraint] = _constraint_modules(graph)

    [value] = constraint.inputs
    assert value.param_name == "value"
    assert value.source.qualified_name == "constraint_inline__the_host__value"
    assert _parameters(graph)[value.source.qualified_name].default_value == 5.0


def test_defaulted_constraint_formals_remain_public_and_overridable() -> None:
    graph = _exact("modeled_default_fidelity")
    constraints = {module.name.split("__")[-2]: module for module in _constraint_modules(graph)}

    defaults = {
        input_.param_name: _parameters(graph)[input_.source.qualified_name]
        for module in constraints.values()
        for input_ in module.inputs
        if input_.param_name in {"drift", "rated_power", "limit"}
    }
    assert defaults["drift"].default_value == -0.1
    assert defaults["rated_power"].default_value == 40.0
    assert defaults["rated_power"].unit_text == "W"
    assert defaults["limit"].default_value is None
    assert defaults["limit"].unresolved_default_kind == "operator"


def test_non_numerical_constraint_is_cataloged_but_not_executed() -> None:
    graph = _exact("constraint_non_numerical")

    [constraint] = _constraint_modules(graph)
    assert "positive_value" in constraint.name
    assert graph.constraint_catalog is not None
    [excluded] = graph.constraint_catalog.excluded_records
    assert excluded.usage_qualified_name.endswith("status_annotation")
    assert excluded.exclusion.kind == "non_numerical"
    assert excluded.exclusion.reasons == ["warn_non_numerical_equality"]


def test_redefined_calculation_instantiates_only_the_most_specific_writer() -> None:
    graph = _exact("retype_model")
    shared = [module for module in graph.modules if module.name.endswith("__shared_calc")]

    assert len(shared) == 2
    assert len({module.name for module in shared}) == 2


def test_valid_deep_cross_scope_redefinitions_resolve_every_reference() -> None:
    graph = _internal("deep_cross_scope_probe")
    chain = graph.calc_by_display_path(
        "DeepCrossScopeDesign__measurement_system__analyzer__chain_analysis"
    )
    ref = graph.calc_by_display_path(
        "DeepCrossScopeDesign__measurement_system__analyzer__ref_analysis"
    )
    qualified = graph.calc_by_display_path(
        "DeepCrossScopeDesign__measurement_system__analyzer__self_ref_analysis"
    )
    expected = "DeepCrossScopeDesign__measurement_system__analyzer__baseline_value"

    for edge in (
        chain.input_by_name("baseline"),
        ref.input_by_name("baseline"),
        qualified.input_by_name("data_point"),
    ):
        assert isinstance(edge, NodeRef)
        assert graph.attrs[edge.target].display_path == expected

    deep_path = ref.input_by_name("data_point")
    assert isinstance(deep_path, ProducerRef)
    assert (
        graph.calcs[deep_path.target.calculation].display_path
        == "DeepCrossScopeDesign__measurement_system__station__array__sensor__core"
    )
    [reading] = [
        node
        for node in graph.attrs.values()
        if node.display_path.endswith("__station__array__sensor__reading")
    ]
    assert reading.value == 10.0

    public = project(graph)
    ref_module = next(module for module in public.modules if module.name.endswith("__ref_analysis"))
    data_point = next(input_ for input_ in ref_module.inputs if input_.param_name == "data_point")
    assert data_point.source.source_type == "module_output"
    assert (
        data_point.source.producer_channel
        == "DeepCrossScopeDesign__measurement_system__station__array__sensor__core__metric_value"
    )


def test_public_compatibility_keeps_names_but_uses_occurrence_sources() -> None:
    """The public names the legacy route shipped, now stated by value.

    The legacy half of this comparison retired with the v5 family (retirement step 2), per
    the per-node disposition on ledger L-130. What it contributed was the *compatibility*
    claim: the exact route ships the legacy route's output aliases and constraint
    catalogue unchanged. Both are written out below, read from the fixture rather than
    from a second route, so the claim survives the comparison.
    """
    graph = _exact("wi014_toy")

    [group] = graph.entry_point_groups
    assert group.name == "toy_plant_params"
    assert {parameter.entry_type for parameter in group.parameters} == {
        EntryPointType.DESIGN_ATTRIBUTE
    }
    assert all("__demo_plant__" in parameter.qualified_name for parameter in group.parameters)

    # `total_cost` is the shape-A EXPOSE_PURE derived attribute on `part def 'Toy Plant'`
    # (tests/fixtures/wi014_toy/toy_plant.sysml); the alias is the modeller's name for the
    # channel, and both routes shipped it.
    assert [(alias.alias_name, alias.instance_path) for alias in graph.output_aliases] == [
        ("total_cost", "demo_plant")
    ]
    # The fixture models one constraint — `assert constraint affordable : 'Cost Within
    # Budget'` on `part demo_plant` (toy_plant.sysml:51) — so the catalogue carries exactly
    # one entry, on the one occurrence. The legacy comparison asserted the id list matched
    # entry for entry; with one route left, the shape and the occurrence it is keyed to are
    # what that claim reduces to. The id's hash suffix is deliberately not spelled out: it
    # is a fingerprint of the canonical tuple, pinned by `test_exact_constraint_route.py`.
    assert graph.constraint_catalog is not None
    (entry,) = graph.constraint_catalog.concrete_entries
    assert entry.constraint_id.startswith("toy_plant__demo_plant__affordable__")
    assert entry.evaluation_channel == f"{entry.constraint_id}__evaluation"


def test_parameter_group_name_drives_the_compatible_json_filename() -> None:
    graph = _exact("attr_expr_probe")
    names = {group.name for group in graph.entry_point_groups}
    assert "design_params" in names


def test_modeled_formula_dropped_by_legacy_remains_public_runtime_behavior() -> None:
    graph = _exact("attr_expr_probe")
    scaled_area = next(
        module
        for module in graph.modules
        if module.name == "attrexprprobedesign__probe_design__scaled_area"
    )

    [result] = scaled_area.inputs
    assert result.source.source_type == "module_output"
    assert result.source.producer_channel == "AttrExprProbeDesign__probe_design__scale_calc__result"


def test_inherited_formulas_are_scoped_to_three_concrete_instances() -> None:
    graph = _exact("unresolvable_attr_probe")
    formulas = [module for module in graph.modules if module.module_kind is ModuleKind.FORMULA]
    concrete_scopes = {
        "unresolvableattrprobedesign__derived_instance",
        "unresolvableattrprobedesign__design_derived_instance",
        "unresolvableattrprobedesign__grandchild_instance",
    }

    assert len(formulas) == 9
    assert all(
        any(module.name.startswith(f"{scope}__") for scope in concrete_scopes)
        for module in formulas
    )


def test_unbound_calculation_defaults_are_per_usage_public_sources() -> None:
    graph = _exact("elab_matrix_c23")
    calculations = [
        module for module in graph.modules if module.module_kind is ModuleKind.CALCULATION
    ]
    sources = {module.name: module.inputs[0].source.qualified_name for module in calculations}

    assert len(set(sources.values())) == 2
    for qualified_name in sources.values():
        parameter = _parameters(graph)[qualified_name]
        assert parameter.entry_type is EntryPointType.LIBRARY_DEFAULT
        assert parameter.default_value == 3.0
