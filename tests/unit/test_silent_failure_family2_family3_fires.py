"""Fires-on-shape pins for D3-5, D3-6, D3-15 (audit cure 1, R1 [HARD]).

Each landed diagnostic proves it fires on the claimed shape, with an expectation
anchored to constructed inputs — never computed by the code under test.
"""

from __future__ import annotations

import logging
from pathlib import Path

from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    HierarchyExtractionResult,
)
from sysml_codegen.extraction.usage_extractor import CalcUsageData


def _warns(caplog):
    return [r.message for r in caplog.records if r.levelno >= logging.WARNING]


# --- D3-5: registry Phase-1a unknown calc def warns ------------------------------


def test_d35_unknown_calc_def_phase1a_warns(caplog):
    """A usage whose calc def is absent registers ZERO channels; the bare
    `continue` was silent — it must WARN naming the calc def + usage."""
    from sysml_codegen.orchestration.output_registry_builder import build_output_registry

    usage = CalcUsageData(
        instance_name="widget",
        calc_def_name="MissingDef",
        calc_def_qualified_name="MissingDef",
        module_type="MissingDefModule",
        qualified_name="Design__widget",
    )
    with caplog.at_level(logging.WARNING):
        build_output_registry([usage], [], [], [], [], {})
    warns = _warns(caplog)
    assert any("MissingDef" in w and "widget" in w for w in warns), warns


# --- D3-6: snapshot loader malformed usage_type_map key warns --------------------


def test_d36_malformed_usage_type_map_key_warns(caplog):
    """A malformed usage_type_map key (not JSON) is dropped; the fix logs the
    drop instead of a bare pass so the offline-only mis-wire is visible."""
    from sysml_codegen.snapshot.loader import _deserialize_hierarchy_result

    d = {
        "redefinitions": [],
        "design_overrides": [],
        "multiplicities": [],
        "aggregation_expressions": [],
        "warnings": [],
        "usage_type_map": {"not-valid-json-{{{": "SomeType"},
        "part_usage_names": {},
    }
    with caplog.at_level(logging.WARNING):
        result = _deserialize_hierarchy_result(d)
    # The malformed key is dropped (not present) ...
    assert result.usage_type_map == {}
    # ... and the drop is loud, naming the offending key.
    warns = _warns(caplog)
    assert any("usage_type_map" in w and "not-valid-json" in w for w in warns), warns


# --- D3-15: two design prefixes warn --------------------------------------------


def _agg() -> AggregationExpressionData:
    return AggregationExpressionData(
        owning_part_qn="Lib__Assembly",
        owning_part_name="Assembly",
        attribute_name="total",
        raw_expression_text="sum(x)",
        transformed_expression="(n * x)",
        sum_terms=[],
        singleton_terms=[],
        local_terms=[],
        input_channels=[],
        entry_points=[],
    )


def _usage(qn: str) -> CalcUsageData:
    return CalcUsageData(
        instance_name=qn.split("__")[-1],
        calc_def_name="C",
        calc_def_qualified_name="C",
        module_type="CModule",
        qualified_name=qn,
        owning_part_def_qn="Lib__Assembly",
        is_template=False,
    )


def test_d315_two_design_prefixes_warn(caplog):
    """Two virtual usages with distinct segment[0] prefixes (`DesignA__...`,
    `DesignB__...`) — aggregation scoping keys off the first, mis-keying the
    second design's aggregations; it must WARN naming both prefixes."""
    from sysml_codegen.orchestration.pipeline_builder import _scope_aggregation_expressions

    hierarchy = HierarchyExtractionResult(
        redefinitions=[], design_overrides=[], multiplicities=[],
        aggregation_expressions=[_agg()], warnings=[],
    )
    usages = [_usage("DesignA__plant__agg"), _usage("DesignB__plant__agg")]
    with caplog.at_level(logging.WARNING):
        _scope_aggregation_expressions(hierarchy, usages)
    warns = _warns(caplog)
    assert any(
        "D3-15" in w or ("design prefix" in w and "DesignA" in w and "DesignB" in w)
        for w in warns
    ), warns
