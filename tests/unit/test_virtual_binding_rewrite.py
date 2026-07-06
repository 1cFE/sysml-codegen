"""Virtual-binding-rewrite hardening (Item 9 — REQ-VBR-08, REQ-VBR-09).

License-free constructed unit tests on real model objects (no mocks — precedent
``test_unwired_fallthrough_partition`` builds real Pydantic/dataclass objects).
They prove the two rewrite-hardening edits independently of any snapshot:

  - **REQ-VBR-08** (divergent siblings): ``_create_virtual_calc_usage`` must mint
    each instance its own ``BindingInfo`` objects, so the per-instance rewrite of
    one sibling never bleeds into another. Pre-copy, the two instances share one
    object: rewriting instance A to LITERAL makes the rewrite skip instance B
    (already LITERAL), and B reads A's value.
  - **REQ-VBR-09** (bare-name crash-safety): ``_rewrite_virtual_bindings`` must not
    raise on a bare-name ``source_path`` once the override index is non-empty; it
    logs DEBUG and leaves the binding untouched.

The LITERAL-filter predicate (REQ-HR-08, D3) is tested here too — the keep/drop
decision is factored pure so it carries a direct license-free assertion.
"""

from __future__ import annotations

import logging

from agentic_mbse.sysml.types import BindingType

from sysml_codegen.extraction.data_models import (
    HierarchyExtractionResult,
    RedefinitionData,
    RedefinitionType,
)
from sysml_codegen.extraction.usage_extractor import (
    BindingInfo,
    CalcUsageData,
    _create_virtual_calc_usage,
)
from sysml_codegen.orchestration.pipeline_builder import _rewrite_virtual_bindings


# ---------------------------------------------------------------------------
# Builders — real objects, mirroring the alias_agg_probe committed shape
# (base_cost REFERENCE binding, source_path ``Lib::Widget::cost_model::base_cost``).
# ---------------------------------------------------------------------------
def _template_cost_model(param: str, source_path: str) -> CalcUsageData:
    """A template CalcUsage carrying one REFERENCE binding for ``param``."""
    return CalcUsageData(
        instance_name="cost_model",
        calc_def_name="CostModel",
        calc_def_qualified_name="Lib::Widget::CostModel",
        module_type="lib.CostModel",
        bindings=[
            BindingInfo(
                param_name=param,
                source_path=source_path,
                binding_type=BindingType.REFERENCE,
            )
        ],
        is_template=True,
    )


def _deep_literal_override(
    owning_qn: str, target_path: list[str], value: float
) -> RedefinitionData:
    """A deep-path LITERAL design override keyed to ``owning_qn``/``target_path``.

    The rewrite indexes it as ``(f"{owning_qn}__{intermediate}", leaf)`` where
    ``intermediate = "__".join(target_path[:-1])`` and ``leaf = target_path[-1]``.
    """
    return RedefinitionData(
        owning_part_qn=owning_qn,
        attribute_name=target_path[-1],
        redefinition_type=RedefinitionType.LITERAL,
        literal_value=value,
        target_path=target_path,
        is_deep_path=True,
    )


def _hier(overrides: list[RedefinitionData]) -> HierarchyExtractionResult:
    return HierarchyExtractionResult(
        redefinitions=[],
        design_overrides=overrides,
        multiplicities=[],
        aggregation_expressions=[],
        warnings=[],
    )


def _binding(usage: CalcUsageData, param: str) -> BindingInfo:
    return next(b for b in usage.bindings if b.param_name == param)


# ---------------------------------------------------------------------------
# REQ-VBR-08: the rewrite respects the instance boundary for divergent siblings.
# ---------------------------------------------------------------------------
def test_rewrite_respects_instance_boundary_for_divergent_siblings():
    """Two virtual instances of one template, given DIFFERENT override matches,
    produce independent results — not merely distinct objects.

    Instance A (``Design__plant__widgetA``) matches the 50.0 override; instance B
    (``Design__plant__widgetB``) matches the 100.0 override. Pre-copy, A's rewrite
    mutates the shared BindingInfo to LITERAL, B is then skipped as already-LITERAL,
    and B reads 50.0 — the assertion on B fails.
    """
    template = _template_cost_model(
        param="base_cost",
        source_path="Lib::Widget::cost_model::base_cost",
    )
    iA = _create_virtual_calc_usage(template, "Design__plant__widgetA")
    iB = _create_virtual_calc_usage(template, "Design__plant__widgetB")

    hier = _hier(
        [
            _deep_literal_override("Design__plant", ["widgetA", "base_cost"], 50.0),
            _deep_literal_override("Design__plant", ["widgetB", "base_cost"], 100.0),
        ]
    )
    _rewrite_virtual_bindings([iA, iB], hier)

    assert _binding(iA, "base_cost").literal_value == 50.0
    assert _binding(iA, "base_cost").binding_type == BindingType.LITERAL
    assert _binding(iB, "base_cost").literal_value == 100.0
    assert _binding(iB, "base_cost").binding_type == BindingType.LITERAL


# ---------------------------------------------------------------------------
# REQ-VBR-09: a bare-name source_path is skipped with DEBUG, never raises.
# ---------------------------------------------------------------------------
def test_rewrite_skips_bare_name_source_path_without_raising(caplog):
    """With a non-empty override index (the empty-index shield no longer applies),
    a bare-name ``source_path`` binding is skipped with a DEBUG log, not a raise."""
    usage = CalcUsageData(
        instance_name="my_calc",
        calc_def_name="MyCalc",
        calc_def_qualified_name="Lib::MyCalc",
        module_type="lib.MyCalc",
        bindings=[
            BindingInfo(
                param_name="availability",
                source_path="availability",  # bare name: no ``::``, no ``.``
                binding_type=BindingType.REFERENCE,
            )
        ],
        qualified_name="Design__plant__my_calc",
        is_template=False,
    )
    # Non-empty index (an unrelated deep-path override) so the early return on an
    # empty index does not mask the bare-name branch.
    hier = _hier([_deep_literal_override("Design__plant", ["other", "x"], 1.0)])

    with caplog.at_level(logging.DEBUG):
        _rewrite_virtual_bindings([usage], hier)  # must NOT raise (was ValueError)

    assert _binding(usage, "availability").source_path == "availability"  # unchanged
    assert _binding(usage, "availability").binding_type == BindingType.REFERENCE
    assert any("bare-name" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# REQ-HR-08 / D3: the plain-usage override filter keeps only LITERAL RHS.
# ---------------------------------------------------------------------------
def test_plain_usage_override_filter_keeps_only_literal():
    """The pure keep/drop predicate keeps LITERAL, drops CHAIN and EXPRESSION.

    This is what keeps CHAIN/EXPRESSION plain overrides (Item 10's job) out of
    ``design_overrides`` — INV-1.
    """
    from sysml_codegen.extraction.hierarchy_resolver import _keep_plain_usage_override

    def _redef(kind: RedefinitionType) -> RedefinitionData:
        return RedefinitionData(
            owning_part_qn="Design__plant__assembly",
            attribute_name="base_cost",
            redefinition_type=kind,
        )

    assert _keep_plain_usage_override(_redef(RedefinitionType.LITERAL))
    assert not _keep_plain_usage_override(_redef(RedefinitionType.CHAIN))
    assert not _keep_plain_usage_override(_redef(RedefinitionType.EXPRESSION))
