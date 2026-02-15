"""Unit tests for graph builder compilation_results integration.

Tests:
- build_computation_graph sets PipelineModule.compilability from compilation_results
- Backward compatibility: compilation_results=None leaves UNKNOWN
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    _ensure_backtracking_result_rebuilt,
)
from sysml_codegen.analysis.phantom_detector import PhantomDetectionReport
from sysml_codegen.extraction.data_models import AttributeInfo, CalculationDefinitionData
from sysml_codegen.extraction.expression_compiler import (
    CalcDefCompilationResult,
    Compilability,
    CompilationResult,
)
from sysml_codegen.extraction.usage_extractor import CalcUsageData
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.resolution.graph_builder import build_computation_graph


def _make_minimal_graph_inputs():
    """Build minimal valid inputs for build_computation_graph.

    Creates a single CalcDef with one output and no inputs,
    and a matching CalcUsage. No bindings needed since there
    are no inputs to resolve.
    """
    # Pydantic forward-ref rebuild required for BacktrackingResult
    _ensure_backtracking_result_rebuilt()
    calc_def = CalculationDefinitionData(
        name="TestCalc",
        qualified_name="TestCalc",
        doc_comment="",
        calc_expressions=[],
        input_attributes=[],
        output_attributes=[
            AttributeInfo(name="result", sysml_type="Real", python_type="float"),
        ],
        references=[],
        source_file=Path("test.sysml"),
    )

    usage = CalcUsageData(
        instance_name="test_calc",
        calc_def_name="TestCalc",
        calc_def_qualified_name="TestCalc",
        module_type="TestCalcModule",
        qualified_name="test_calc",
    )

    phantom_report = PhantomDetectionReport()

    result = BacktrackingResult(
        required_usages=[usage],
        dependency_graph={},
        entry_points=set(),
        entry_point_sources={},
        phantom_report=phantom_report,
    )

    group_deriver = MagicMock()
    group_deriver.classify.return_value = None
    group_deriver.derive_groups_filtered.return_value = []

    design_attrs: dict[Path, list] = {}

    return result, [calc_def], design_attrs, group_deriver


def test_compilation_results_none_leaves_unknown():
    """Without compilation_results, modules stay UNKNOWN (backward compat)."""
    result, calc_defs, design_attrs, group_deriver = _make_minimal_graph_inputs()

    graph = build_computation_graph(
        result=result,
        calc_defs=calc_defs,
        design_attrs=design_attrs,
        group_deriver=group_deriver,
        output_registry=OutputRegistry(),
    )

    assert len(graph.modules) == 1
    assert graph.modules[0].compilability == Compilability.UNKNOWN


def test_compilation_results_set_module_compilability():
    """build_computation_graph sets compilability from compilation_results."""
    result, calc_defs, design_attrs, group_deriver = _make_minimal_graph_inputs()

    compilation_results = {
        "TestCalc": CalcDefCompilationResult(
            calc_def_name="TestCalc",
            overall_compilability=Compilability.FULLY_COMPILABLE,
            output_results=[
                CompilationResult(
                    output_name="result",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="inputs.x * 2",
                ),
            ],
            execution_order=["result"],
        ),
    }

    graph = build_computation_graph(
        result=result,
        calc_defs=calc_defs,
        design_attrs=design_attrs,
        group_deriver=group_deriver,
        output_registry=OutputRegistry(),
        compilation_results=compilation_results,
    )

    assert len(graph.modules) == 1
    assert graph.modules[0].compilability == Compilability.FULLY_COMPILABLE


def test_compilation_results_manual_required():
    """MANUAL_REQUIRED compilability propagates to module."""
    result, calc_defs, design_attrs, group_deriver = _make_minimal_graph_inputs()

    compilation_results = {
        "TestCalc": CalcDefCompilationResult(
            calc_def_name="TestCalc",
            overall_compilability=Compilability.MANUAL_REQUIRED,
            output_results=[],
            execution_order=[],
        ),
    }

    graph = build_computation_graph(
        result=result,
        calc_defs=calc_defs,
        design_attrs=design_attrs,
        group_deriver=group_deriver,
        output_registry=OutputRegistry(),
        compilation_results=compilation_results,
    )

    assert graph.modules[0].compilability == Compilability.MANUAL_REQUIRED


def test_compilation_results_partially_compilable():
    """PARTIALLY_COMPILABLE compilability propagates to module."""
    result, calc_defs, design_attrs, group_deriver = _make_minimal_graph_inputs()

    compilation_results = {
        "TestCalc": CalcDefCompilationResult(
            calc_def_name="TestCalc",
            overall_compilability=Compilability.PARTIALLY_COMPILABLE,
            output_results=[],
            execution_order=[],
        ),
    }

    graph = build_computation_graph(
        result=result,
        calc_defs=calc_defs,
        design_attrs=design_attrs,
        group_deriver=group_deriver,
        output_registry=OutputRegistry(),
        compilation_results=compilation_results,
    )

    assert graph.modules[0].compilability == Compilability.PARTIALLY_COMPILABLE


def test_compilation_results_missing_key_leaves_unknown():
    """Module stays UNKNOWN when its calc_def_name is not in compilation_results."""
    result, calc_defs, design_attrs, group_deriver = _make_minimal_graph_inputs()

    # compilation_results has an entry, but NOT for "TestCalc"
    compilation_results = {
        "OtherCalc": CalcDefCompilationResult(
            calc_def_name="OtherCalc",
            overall_compilability=Compilability.FULLY_COMPILABLE,
            output_results=[],
            execution_order=[],
        ),
    }

    graph = build_computation_graph(
        result=result,
        calc_defs=calc_defs,
        design_attrs=design_attrs,
        group_deriver=group_deriver,
        output_registry=OutputRegistry(),
        compilation_results=compilation_results,
    )

    assert graph.modules[0].compilability == Compilability.UNKNOWN
