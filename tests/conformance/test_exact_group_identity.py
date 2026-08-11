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
    pins for one fixture, widened to every stem-named fixture both routes can
    project. The legacy route additionally emits a ``system_design`` group built
    from hierarchy data, which the exact route has no equivalent for; it is
    excluded here and carried as a Slice 3E question.
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


def test_the_known_exact_versus_legacy_declaration_site_divergence() -> None:
    """One fixture where the two routes disagree, pinned rather than absorbed.

    ``d38_caret`` has no ``model.sysml``, so Slice 3B's changed fallback never
    runs on it and this divergence predates the slice — it is byte-identical at
    ``a7c13a6``. The routes disagree about *which file declares* the entry point:
    the elaborator records the declaration site (``library.sysml``) while the
    legacy deriver attributes it to ``design.sysml``. No naming rule can
    reconcile that, so it needs a disposition before the Slice 3E authority
    switch, where it would change a shipped input filename.

    Recorded in ``evidence/3b-old-new-comparison.md``.
    """
    path = FIXTURES_DIR / "d38_caret"
    exact = {group.name for group in build_elaborated_pipeline([path]).entry_point_groups}
    legacy = {
        group.name for group in build_pipeline_context([path]).computation_graph.entry_point_groups
    }

    assert exact == {"library_params"}
    assert legacy == {"design_params"}
