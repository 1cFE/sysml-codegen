"""Falsifiable exit-pin tests (Item 7 / D1).

`_build_exit_points` gets two keyword-only parameters whose production defaults reproduce
today's capture-everything output byte-for-byte (INV-7). The control/mechanism pair below is
the load-bearing proof: under a narrowed `selected_channels` that excludes the report channel,
`pin_report_channels=False` drops it and `pin_report_channels=True` keeps it — so the report's
exit membership is structural (INV-5), not merely riding capture-everything.
"""

from __future__ import annotations

from sysml_codegen.generation.pipeline import _build_exit_points
from sysml_codegen.resolution.models import ModuleKind, ModuleOutput, PipelineModule


def _calc_module(name: str) -> PipelineModule:
    return PipelineModule(
        name=name,
        module_type="M",
        inputs=[],
        outputs=[ModuleOutput(field_name="root", python_type="float", channel_name=name)],
        execution_order=0,
        module_kind=ModuleKind.CALCULATION,
    )


def _report_aggregator(channel: str) -> PipelineModule:
    return PipelineModule(
        name="constraint_report_aggregator",
        module_type="constraints.ConstraintReportAggregatorModule",
        inputs=[],
        outputs=[
            ModuleOutput(
                field_name="constraint_report", python_type="ConstraintReport", channel_name=channel
            )
        ],
        execution_order=1,
        module_kind=ModuleKind.REPORT_AGGREGATOR,
    )


def test_pin_keeps_report_under_narrowed_exit():
    mods = [_calc_module("area"), _report_aggregator("constraint_report")]
    narrowed = {"area"}  # excludes the report channel

    control = _build_exit_points(
        mods, {}, selected_channels=narrowed, pin_report_channels=False
    )
    mechanism = _build_exit_points(
        mods, {}, selected_channels=narrowed, pin_report_channels=True
    )

    names = lambda xs: {x["name"] for x in xs}  # noqa: E731
    assert "constraint_report" not in names(control)  # control leg DROPS it
    assert "constraint_report" in names(mechanism)  # mechanism leg KEEPS it
    assert "area" in names(control) and "area" in names(mechanism)


def test_production_defaults_capture_everything():
    """At production defaults every channel passes — the pin is a no-op (INV-7)."""
    mods = [_calc_module("area"), _calc_module("cost"), _report_aggregator("constraint_report")]
    exits = _build_exit_points(mods, {})
    names = {x["name"] for x in exits}
    assert names == {"area", "cost", "constraint_report"}
    assert len(exits) == 3


def test_narrowing_without_pin_omits_unselected_non_report_channels_too():
    """Control leg narrows uniformly — the pin, not narrowing itself, is what's under test."""
    mods = [_calc_module("area"), _calc_module("cost"), _report_aggregator("constraint_report")]
    exits = _build_exit_points(
        mods, {}, selected_channels={"area"}, pin_report_channels=False
    )
    assert {x["name"] for x in exits} == {"area"}
