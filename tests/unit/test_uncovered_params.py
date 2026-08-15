"""Params-coverage collector + V11 strict boundary (Item 7 / REQ-GA-08, D4).

What is left here after retirement step 1 is the collector pair as pure functions:
  - ``collect_uncovered_params`` (wired half → V11) — INV-3, INV-4.
  - ``collect_unwired_fallthrough`` (unwired half → reconciliation summary).

The fixture-driven half of this file — nine nodes that built a ``ComputationGraph`` from a
committed v5 extraction snapshot, plus the V11 generation-boundary nodes that ran through
``tests/helpers/legacy_route.py`` — read the v5 route and retired with it. **The V11
boundary itself is not untested by that:** the raise lives on the exact route
(``cli/__init__.py:277-287``) and is pinned by ``tests/conformance/test_gate_b_generation_gate.py``,
which drives a real generation to the ``CodeGenerationError`` whose message carries V11.

The surviving node covers the partition no committed fixture ever exercised — a
fell-through, valueless, *unwired* entry point, which belongs to the summary list and not
to V11 — on a constructed ``ComputationGraph`` of real Pydantic model objects (R1: real
model objects, no mocks).
"""

from __future__ import annotations

from pathlib import Path

from sysml_codegen.resolution.uncovered_params import (
    collect_uncovered_params,
    collect_unwired_fallthrough,
)
from sysml_codegen.resolution.models import (
    ComputationGraph,
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleKind,
    ParameterGroup,
    PipelineModule,
)


# ---------------------------------------------------------------------------
# Unwired-summary partition (M1). No committed fixture exercises it (every corpus
# V11 case is wired), so build a minimal real ComputationGraph directly.
# ---------------------------------------------------------------------------
def test_unwired_fallthrough_partition():
    """A fell-through, valueless, UNWIRED entry point → summary list, not V11."""
    dangling_qn = "Lib__plant__orphan_calc__p"

    # One module whose sole input is wired to a DIFFERENT (covered) EP, so the
    # dangling EP is genuinely unwired.
    module = PipelineModule(
        name="lib__plant__orphan_calc",
        module_type="OrphanCalcModule",
        inputs=[
            ModuleInput(
                param_name="q",
                python_type="float",
                source=InputSource(
                    source_type="entry_point",
                    param_group="design_params",
                    qualified_name="Lib__plant__orphan_calc__q",
                ),
            )
        ],
        outputs=[],
        execution_order=0,
        module_kind=ModuleKind.CALCULATION,
    )
    group = ParameterGroup(
        name="design_params",
        class_name="DesignParams",
        source_file=Path("design.sysml"),
        parameters=[
            EntryPoint(
                qualified_name="Lib__plant__orphan_calc__q",
                simple_name="q",
                entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                default_value=1.0,
            ),
            EntryPoint(
                qualified_name=dangling_qn,
                simple_name="p",
                entry_type=EntryPointType.USAGE_LITERAL,
                default_value=None,  # valueless
            ),
        ],
    )
    graph = ComputationGraph(
        modules=[module],
        entry_point_groups=[group],
        execution_order=["lib__plant__orphan_calc"],
        fallback_entry_points={dangling_qn},  # fell through
    )

    # Unwired + valueless → summary partition.
    assert collect_unwired_fallthrough(graph) == [dangling_qn]
    # Not wired → NOT a V11 violation.
    assert collect_uncovered_params(graph) == []
