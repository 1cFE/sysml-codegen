"""Customer-visible one-source fan-out on live and rebuilt exact graphs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import jinja2
import yaml

from sysml_codegen.elaboration import elaborate, project
from sysml_codegen.elaboration.graph import NodeRef
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.generation.entry_point import generate_all_derived_jsons
from sysml_codegen.generation.pipeline import generate_pipeline_yaml
from sysml_codegen.resolution.models import ModuleKind
from sysml_codegen.snapshot.instance_graph import (
    decode_instance_graph,
    encode_instance_graph,
)
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

TEMPLATES = Path(__file__).parents[2] / "src/sysml_codegen/templates"
SOURCE_QN = "source_identity_mixed_consumers__station__rig__gain_setting"
EXPECTED_CONSUMERS = {
    ("source_identity_mixed_consumers__station__chain_calc", ModuleKind.CALCULATION),
    ("source_identity_mixed_consumers__station__chain_guard", ModuleKind.CONSTRAINT),
    ("source_identity_mixed_consumers__station__station_total", ModuleKind.FORMULA),
}
SHADOWED_OUTER_QN = "ShadowedReference__the_outer__scale"
SHADOWED_CALC = "shadowedreference__the_outer__inner__shadowed_calc"


def _load_graph(model_path: Path):
    extractor = SysMLDataExtractor([model_path])
    assert extractor.load_models()
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )


def _source_consumers(graph) -> set[tuple[str, ModuleKind]]:
    return {
        (
            module.name.rsplit("__", 1)[0]
            if module.module_kind is ModuleKind.CONSTRAINT
            else module.name,
            module.module_kind,
        )
        for module in graph.modules
        for input_ in module.inputs
        if input_.source.qualified_name == SOURCE_QN
    }


def _typed_source_consumers(graph, source_path: str) -> set[tuple[object, object]]:
    source_id = graph.attr_by_display_path(source_path).node_id
    return {
        (consumer.node_id, port)
        for consumer in (*graph.calcs.values(), *graph.constraints.values())
        for port, edge in consumer.inputs.items()
        if isinstance(edge, NodeRef) and edge.target == source_id
    }


def _typed_consumer_surface(
    graph, consumers: set[tuple[object, object]]
) -> set[tuple[str, ModuleKind]]:
    calculation_ids = set(graph.calcs)
    constraint_ids = set(graph.constraints)
    result = set()
    for consumer_id, _port in consumers:
        if consumer_id in calculation_ids:
            calculation = graph.calcs[consumer_id]
            if calculation.is_computed:
                kind = (
                    ModuleKind.AGGREGATION
                    if calculation.aggregation_reference_ordinals
                    else ModuleKind.FORMULA
                )
            else:
                kind = ModuleKind.CALCULATION
            result.add((calculation.display_path.lower(), kind))
        elif consumer_id in constraint_ids:
            result.add((graph.constraints[consumer_id].display_path.lower(), ModuleKind.CONSTRAINT))
        else:
            raise AssertionError(f"unknown typed consumer {consumer_id!r}")
    return result


def _generated_source_consumers(graph, source_qn: str) -> set[tuple[str, ModuleKind]]:
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES))
    document = yaml.safe_load(generate_pipeline_yaml(graph, "mutation", environment))
    module_by_name = {module.name: module for module in graph.modules}
    consumers = set()
    for module_name, module_data in document["modules"].items():
        if not any(
            str(binding).split()[-1].endswith(f".{source_qn}")
            for binding in module_data.get("inputs", {}).values()
        ):
            continue
        module = module_by_name[module_name]
        public_name = (
            module.name.rsplit("__", 1)[0]
            if module.module_kind is ModuleKind.CONSTRAINT
            else module.name
        )
        consumers.add((public_name, module.module_kind))
    return consumers


def _source_default(graph) -> float | None:
    matches = [
        parameter.default_value
        for group in graph.entry_point_groups
        for parameter in group.parameters
        if parameter.qualified_name == SOURCE_QN
    ]
    assert len(matches) == 1
    return matches[0]


def _defaults(graph) -> dict[str, float | None]:
    return {
        parameter.qualified_name: parameter.default_value
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }


def _projected_routes(baseline_path: Path, changed_path: Path):
    baseline_internal = _load_graph(baseline_path)
    changed_internal = _load_graph(changed_path)
    return (
        (baseline_internal, changed_internal),
        (project(baseline_internal), project(changed_internal)),
        (
            project(decode_instance_graph(encode_instance_graph(baseline_internal))),
            project(decode_instance_graph(encode_instance_graph(changed_internal))),
        ),
    )


def test_public_mutation_reaches_exactly_one_source_fanout(tmp_path: Path) -> None:
    baseline_path = FIXTURES_DIR / "source_identity_mixed_consumers"
    changed_path = tmp_path / "source_identity_mixed_consumers"
    shutil.copytree(baseline_path, changed_path)
    model_path = changed_path / "model.sysml"
    model_path.write_text(
        model_path.read_text().replace(":>> gain_setting = 42.0;", ":>> gain_setting = 47.0;", 1)
    )

    internal, *routes = _projected_routes(baseline_path, changed_path)
    baseline_internal, changed_internal = internal
    typed_consumers = _typed_source_consumers(baseline_internal, SOURCE_QN)
    assert len(typed_consumers) == len(EXPECTED_CONSUMERS)
    assert _typed_consumer_surface(baseline_internal, typed_consumers) == EXPECTED_CONSUMERS
    assert _typed_source_consumers(changed_internal, SOURCE_QN) == typed_consumers

    for baseline, changed in routes:
        assert _source_consumers(baseline) == EXPECTED_CONSUMERS
        assert _source_consumers(changed) == EXPECTED_CONSUMERS
        assert _source_default(baseline) == 42.0
        assert _source_default(changed) == 47.0

        baseline_defaults = _defaults(baseline)
        changed_defaults = _defaults(changed)
        assert {
            name for name in baseline_defaults if baseline_defaults[name] != changed_defaults[name]
        } == {SOURCE_QN}

    assert _generated_source_consumers(routes[0][1], SOURCE_QN) == EXPECTED_CONSUMERS

    generated = generate_all_derived_jsons(routes[0][1].entry_point_groups, tmp_path / "public")
    public_payload = {
        key: value for output in generated for key, value in json.loads(output.read_text()).items()
    }
    assert public_payload[SOURCE_QN] == 47.0
    assert list(public_payload).count(SOURCE_QN) == 1


def test_public_shadow_mutation_keeps_the_resolved_outer_referent(tmp_path: Path) -> None:
    baseline_path = FIXTURES_DIR / "shadowed_reference"
    changed_path = tmp_path / "shadowed_reference"
    shutil.copytree(baseline_path, changed_path)
    model_path = changed_path / "model.sysml"
    model_path.write_text(
        model_path.read_text().replace(
            "attribute scale : Real = 2.0;", "attribute scale : Real = 3.0;", 1
        )
    )

    internal, *routes = _projected_routes(baseline_path, changed_path)
    baseline_internal, changed_internal = internal
    typed_consumers = _typed_source_consumers(baseline_internal, SHADOWED_OUTER_QN)
    assert len(typed_consumers) == 1
    assert _typed_consumer_surface(baseline_internal, typed_consumers) == {
        (SHADOWED_CALC, ModuleKind.CALCULATION)
    }
    assert _typed_source_consumers(changed_internal, SHADOWED_OUTER_QN) == typed_consumers
    for baseline, changed in routes:
        for graph in (baseline, changed):
            calculation = next(module for module in graph.modules if module.name == SHADOWED_CALC)
            (factor,) = calculation.inputs
            assert factor.source.qualified_name == SHADOWED_OUTER_QN

        baseline_defaults = _defaults(baseline)
        changed_defaults = _defaults(changed)
        assert baseline_defaults[SHADOWED_OUTER_QN] == 2.0
        assert changed_defaults[SHADOWED_OUTER_QN] == 3.0
        assert {
            name for name in baseline_defaults if baseline_defaults[name] != changed_defaults[name]
        } == {SHADOWED_OUTER_QN}

    generated = generate_all_derived_jsons(routes[0][1].entry_point_groups, tmp_path / "shadow")
    public_payload = {
        key: value for output in generated for key, value in json.loads(output.read_text()).items()
    }
    assert public_payload[SHADOWED_OUTER_QN] == 3.0
    assert list(public_payload) == [SHADOWED_OUTER_QN]
    assert _generated_source_consumers(routes[0][1], SHADOWED_OUTER_QN) == {
        (SHADOWED_CALC, ModuleKind.CALCULATION)
    }
