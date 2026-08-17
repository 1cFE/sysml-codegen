"""Native effective declarations and permitted plural occurrence scope."""

from __future__ import annotations

from sysml_codegen.elaboration import NodeRef
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license


def test_plural_formula_edges_stay_inside_the_consumer_occurrence() -> None:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "elab_native_plural_scope"])
    assert extractor.load_models()
    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )

    totals = {
        node.display_path: node
        for node in graph.calcs.values()
        if node.is_computed
        and node.display_name in {"total", "fleet_total", "observed_total"}
    }
    assert set(totals) == {
        "ElabNativePluralScope__plant__selected__total",
        "ElabNativePluralScope__plant__shadow__total",
        "ElabNativePluralScope__fleet_total",
        "ElabNativePluralScope__dashboard__observed_total",
    }

    for display_path, node in totals.items():
        if display_path in {
            "ElabNativePluralScope__fleet_total",
            "ElabNativePluralScope__dashboard__observed_total",
        }:
            targets = {
                graph.attrs[edge.target].display_path
                for edge in node.inputs.values()
                if isinstance(edge, NodeRef)
            }
            assert targets == {
                "ElabNativePluralScope__plant__selected__leaf[0]__value",
                "ElabNativePluralScope__plant__selected__leaf[1]__value",
            }
            continue
        container_path = display_path.rsplit("__", 1)[0]
        targets = {
            graph.attrs[edge.target].display_path
            for edge in node.inputs.values()
            if isinstance(edge, NodeRef)
        }
        assert targets == {
            f"{container_path}__leaf[0]__value",
            f"{container_path}__leaf[1]__value",
        }


def test_native_child_order_does_not_change_occurrence_identity(monkeypatch) -> None:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "elab_native_plural_scope"])
    assert extractor.load_models()
    baseline = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )

    from agentic_mbse.sysml.syside_adapter import SysideAdapter

    original = SysideAdapter.elements_of_type

    def reversed_elements(
        cls,
        model,
        type_name,
        *,
        include_subtypes=False,
        exclude=(),
    ):
        return tuple(
            reversed(
                tuple(
                    original(
                        model,
                        type_name,
                        include_subtypes=include_subtypes,
                        exclude=exclude,
                    )
                )
            )
        )

    monkeypatch.setattr(SysideAdapter, "elements_of_type", classmethod(reversed_elements))
    reordered = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )

    assert set(reordered.attrs) == set(baseline.attrs)
    assert set(reordered.calcs) == set(baseline.calcs)
    assert {
        node.node_id: node.inputs for node in reordered.calcs.values()
    } == {node.node_id: node.inputs for node in baseline.calcs.values()}
