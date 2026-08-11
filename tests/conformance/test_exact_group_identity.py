"""Where an entry-point group's name comes from, and what still disagrees.

A group is named after the file that declares it. When that file is
``model.sysml`` — a filename that carries no identity of its own — the name
comes from the package that declares the owning root occurrence instead.

That fallback is the Slice 3B fix. It used to be the *parent directory* name,
which is the one input a v6 snapshot rewrites: capture stages every source as
``root-N/<filename>``, so a package generated from a snapshot shipped
``inputs/root_0_params.json`` and a ``Root0Params`` schema class.

Every expectation here is read out of the fixture's own SysML — the `package`
declaration and the filenames — never out of the projection under test.
"""

from __future__ import annotations

import pytest

from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def _identity(graph) -> set[tuple[str, str, str]]:
    return {
        (group.name, group.class_name, str(group.source_file))
        for group in graph.entry_point_groups
    }


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        pytest.param(
            "source_identity_mixed_consumers",
            {
                (
                    "source_identity_mixed_consumers_params",
                    "SourceIdentityMixedConsumersParams",
                    "source_identity_mixed_consumers",
                )
            },
            id="model.sysml -> declaring package",
        ),
        pytest.param(
            "elab_matrix_c14",
            {("elab_matrix_c14_params", "ElabMatrixC14Params", "elab_matrix_c14")},
            id="model.sysml -> PascalCase package read as snake_case",
        ),
        pytest.param(
            "wi014_toy",
            {("toy_plant_params", "ToyPlantParams", "toy_plant")},
            id="stem -> toy_plant.sysml",
        ),
        pytest.param(
            "attr_expr_probe",
            {("design_params", "DesignParams", "design")},
            id="stem -> design.sysml, one package across two files",
        ),
    ],
)
def test_group_identity_comes_from_the_declaring_file_or_package(fixture, expected) -> None:
    assert _identity(build_elaborated_pipeline([FIXTURES_DIR / fixture])) == expected


def test_the_package_fallback_is_spelled_the_way_the_model_declares_it() -> None:
    """``package ElabMatrixC14`` must read as ``elab_matrix_c14``, not one word."""
    source = (FIXTURES_DIR / "elab_matrix_c14" / "model.sysml").read_text()
    assert source.lstrip().startswith("package ElabMatrixC14")

    (identity,) = _identity(build_elaborated_pipeline([FIXTURES_DIR / "elab_matrix_c14"]))
    assert identity[0] == "elab_matrix_c14_params"
    assert identity[1] == "ElabMatrixC14Params"


def test_one_package_spanning_two_files_still_gets_one_group_per_file() -> None:
    """The stem rule is per file, so a two-file package keeps two groups."""
    graph = build_elaborated_pipeline([FIXTURES_DIR / "deep_cross_scope_probe"])
    assert {group.name for group in graph.entry_point_groups} == {
        "design_params",
        "library_params",
    }


@pytest.mark.parametrize(
    "fixture",
    ["attr_expr_probe", "d316_crosspart_expose", "quoted_owner_formula", "retype_model",
     "wi014_toy"],
)
def test_a_stem_named_group_keeps_the_name_the_legacy_route_ships(fixture) -> None:
    """The stem rule is untouched, so these must still match the shipped route.

    This is the compatibility guarantee ``test_elaboration_phase5_remediation.py``
    pins for one fixture, widened to every stem-named fixture where both routes
    agree. The legacy route additionally emits a ``system_design`` group built
    from hierarchy data, which the exact route has no equivalent for; it is
    excluded here and carried as a Slice 3E question.

    Two stem-named fixtures are deliberately absent from this list because the
    routes genuinely diverge on them, both for reasons that predate Slice 3B.
    Each has its own by-value pin below: ``d38_caret`` and
    ``unresolvable_attr_probe``.
    """
    path = FIXTURES_DIR / fixture
    exact = {
        (group.name, group.class_name)
        for group in build_elaborated_pipeline([path]).entry_point_groups
    }
    legacy = {
        (group.name, group.class_name)
        for group in build_pipeline_context([path]).computation_graph.entry_point_groups
    }

    assert exact == legacy - {("system_design", "SystemDesign")}


def _parameters(graph) -> set[str]:
    return {
        parameter.qualified_name
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }


def test_the_known_exact_versus_legacy_divergence_on_d38_caret() -> None:
    """One fixture where the two routes disagree, pinned rather than absorbed.

    ``d38_caret`` has no ``model.sysml``, so Slice 3B's changed fallback never
    runs on it and this divergence predates the slice — it is byte-identical at
    ``a7c13a6``.

    Two things differ, and the whole measured divergence is asserted here rather
    than the group name alone. The routes disagree on the *declaration site* of
    the one entry point they share (the elaborator records ``library.sysml``, the
    legacy deriver attributes it to ``design.sysml``), and they disagree on the
    *entry-point set*: the exact route additionally resolves the four modelled
    ``cell`` occurrences and the exponent that the legacy route drops entirely.
    The group name follows from the first; the second is why no naming rule can
    reconcile the two routes here.

    **Disposition made at Slice 3E: this is the expected state, not a defect.**
    The orchestrator classified it expected-fix at the authority switch, on the
    epic's ratified premise that string-era attribution is the defect home and
    declaration-site semantics are the right answer. The exact column below is
    now what the product ships. Diff-ledger row 12 carries the measured
    before/after package cells; both are flagged to the Phase 5 owner packet.
    """
    path = FIXTURES_DIR / "d38_caret"
    exact = build_elaborated_pipeline([path])
    legacy = build_pipeline_context([path]).computation_graph

    assert {group.name for group in exact.entry_point_groups} == {"library_params"}
    assert {group.name for group in legacy.entry_point_groups} == {"design_params"}

    shared = "D38Design__plant__noop__x"
    assert _parameters(legacy) == {shared}
    assert _parameters(exact) == {
        shared,
        "D38Design__plant__pack__exponent",
        *(f"D38Design__plant__pack__cell[{index}]__base_cost" for index in range(4)),
    }


def test_the_known_exact_versus_legacy_divergence_on_unresolvable_attr_probe() -> None:
    """The second measured divergence, and it is not a naming difference at all.

    The two routes here share **no** entry point. The exact route resolves the
    inherited design attributes onto three concrete instances — nine
    ``design_attribute`` entries, which
    ``test_elaboration_phase5_remediation.py::test_inherited_formulas_are_scoped_to_three_concrete_instances``
    already pins as correct exact behavior. The legacy deriver drops all nine and
    emits one ``usage_literal`` instead, attributed to its synthetic ``hierarchy``
    source, which is what names the group ``system_design``.

    So the group name is downstream of a legacy fallback-attribution difference,
    not of any naming rule: change the naming rule however you like and these two
    still ship different files with different contents. Like ``d38_caret``, it
    predates Slice 3B — the fixture has no ``model.sysml``, so the changed
    fallback never runs on it — and it needs a disposition before Slice 3E.

    **Disposition made at Slice 3E: this is the expected state, not a defect.**
    Classified expected-fix at the authority switch — the exact route's
    three-concrete-instances scoping is already pinned as correct by
    ``test_elaboration_phase5_remediation.py``. Measured at the switch, the
    exact route now reaches generation and the generator's module-class
    collision guard refuses the package, because two of the nine newly resolved
    formulas alias to one class name. Diff-ledger row 36 carries both cells; the
    fixture is a graph-level probe no test generates a package from, and both
    halves are flagged to the Phase 5 owner packet.
    """
    path = FIXTURES_DIR / "unresolvable_attr_probe"
    exact = build_elaborated_pipeline([path])
    legacy = build_pipeline_context([path]).computation_graph

    assert {(group.name, group.class_name) for group in exact.entry_point_groups} == {
        ("design_params", "DesignParams")
    }
    assert {(group.name, group.class_name) for group in legacy.entry_point_groups} == {
        ("system_design", "SystemDesign")
    }

    assert _parameters(legacy) == {
        "UnresolvableAttrProbeDesign__design_derived_instance__my_calc__x"
    }
    assert _parameters(exact) == {
        f"UnresolvableAttrProbeDesign__{instance}__{attribute}"
        for instance, attributes in (
            ("derived_instance", ("base_factor", "base_rate", "local_multiplier")),
            ("design_derived_instance", ("base_factor", "base_rate", "local_val")),
            ("grandchild_instance", ("base_factor", "base_rate", "local_multiplier")),
        )
        for attribute in attributes
    }
    assert not _parameters(exact) & _parameters(legacy), "the routes share no entry point at all"
