"""Executable evidence for all 29 authoritative source-identity cells."""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import jinja2
import pytest
import yaml
from agentic_mbse import SemanticEvidenceCode, SemanticEvidenceError

from sysml_codegen.elaboration import (
    ElaborationCode,
    ElaborationDiagnosticError,
    ElaborationError,
    project,
)
from sysml_codegen.elaboration.graph import LiteralInput, NodeRef, ProducerRef
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_evidence import ReadinessCode
from sysml_codegen.generation.entry_point import generate_all_derived_jsons
from sysml_codegen.generation.pipeline import generate_pipeline_yaml
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from sysml_codegen.resolution.models import ModuleKind
from sysml_codegen.snapshot.instance_graph import (
    decode_instance_graph,
    encode_instance_graph,
)
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license

ROOT = Path(__file__).parents[2]
CONTRACT = ROOT / ".project/concepts/constraint-execution-authoritative-lifecycle-contract.md"
TEMPLATES = ROOT / "src/sysml_codegen/templates"


@dataclass(frozen=True)
class ExpectedEdge:
    module_prefix: str
    module_kind: ModuleKind
    param_name: str
    source: str


@dataclass(frozen=True)
class ExpectedAlias:
    alias_name: str
    canonical_channel: str
    instance_path: str


@dataclass(frozen=True)
class RuntimeEvidence:
    fixture: str
    defaults: tuple[tuple[str, float], ...]
    edges: tuple[ExpectedEdge, ...]
    mutation: tuple[str, str] | None
    changed_defaults: tuple[str, ...]
    public_override: tuple[str, float] | None = None
    aliases: tuple[ExpectedAlias, ...] = ()


MIXED = "source_identity_mixed_consumers"
AGGS = "ElabMatrixAggregations__host"


RUNTIME_CELLS = {
    "C1": RuntimeEvidence(
        MIXED,
        ((f"{MIXED}__stamp_plant__efficiency", 0.75),),
        (
            ExpectedEdge(
                f"{MIXED}__stamp_plant__stamp_calc",
                ModuleKind.CALCULATION,
                "value_in",
                f"{MIXED}__stamp_plant__efficiency",
            ),
        ),
        (":>> efficiency = 0.75;", ":>> efficiency = 0.85;"),
        (f"{MIXED}__stamp_plant__efficiency",),
    ),
    "C2": RuntimeEvidence(
        "elab_matrix_c2",
        (("ElabMatrixC2__host__source", 12.7),),
        (
            ExpectedEdge(
                "elabmatrixc2__host__first_calc",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC2__host__source",
            ),
            ExpectedEdge(
                "elabmatrixc2__host__second",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC2__host__source",
            ),
        ),
        (":>> source = 12.7;", ":>> source = 13.7;"),
        ("ElabMatrixC2__host__source",),
    ),
    "C3": RuntimeEvidence(
        "elab_matrix_c3",
        (("ElabMatrixC3__host__source", 12.7),),
        (
            ExpectedEdge(
                "elabmatrixc3__host__first_calc",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC3__host__source",
            ),
            ExpectedEdge(
                "elabmatrixc3__host__second",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC3__host__source",
            ),
        ),
        (":>> source = 12.7;", ":>> source = 13.7;"),
        ("ElabMatrixC3__host__source",),
    ),
    "C4": RuntimeEvidence(
        "elab_matrix_c4",
        (("ElabMatrixC4__host__source", 12.7),),
        (
            ExpectedEdge(
                "elabmatrixc4__host__first_calc",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC4__host__source",
            ),
            ExpectedEdge(
                "elabmatrixc4__host__second",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC4__host__source",
            ),
        ),
        (":>> source = 12.7;", ":>> source = 13.7;"),
        ("ElabMatrixC4__host__source",),
    ),
    "C5": RuntimeEvidence(
        "elab_matrix_c5",
        (("ElabMatrixC5__measurement_system__analyzer__baseline", 12.7),),
        (
            ExpectedEdge(
                "elabmatrixc5__measurement_system__analyzer__observation",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC5__measurement_system__analyzer__baseline",
            ),
        ),
        (":>> baseline = 12.7;", ":>> baseline = 13.7;"),
        ("ElabMatrixC5__measurement_system__analyzer__baseline",),
    ),
    "C6": RuntimeEvidence(
        "elab_matrix_c6",
        (("ElabMatrixC6__host__source__value", 12.7),),
        (
            ExpectedEdge(
                "elabmatrixc6__host__first_calc",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC6__host__source__value",
            ),
            ExpectedEdge(
                "elabmatrixc6__host__second",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC6__host__source__value",
            ),
        ),
        (":>> value = 12.7;", ":>> value = 13.7;"),
        ("ElabMatrixC6__host__source__value",),
    ),
    "C7": RuntimeEvidence(
        "elab_matrix_c7",
        (
            ("ElabMatrixC7__host__left__value", 5.0),
            ("ElabMatrixC7__host__right__value", 5.0),
        ),
        (
            ExpectedEdge(
                "elabmatrixc7__host__left_calc",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC7__host__left__value",
            ),
            ExpectedEdge(
                "elabmatrixc7__host__right_calc",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC7__host__right__value",
            ),
        ),
        ("part left : Source;", "part left : Source { :>> value = 6.0; }"),
        ("ElabMatrixC7__host__left__value",),
    ),
    "C8": RuntimeEvidence(
        MIXED,
        (
            (f"{MIXED}__twin_bay__sensor_a__reading", 11.0),
            (f"{MIXED}__twin_bay__sensor_b__reading", 22.0),
        ),
        (
            ExpectedEdge(
                f"{MIXED}__twin_bay__calc_a",
                ModuleKind.CALCULATION,
                "value_in",
                f"{MIXED}__twin_bay__sensor_a__reading",
            ),
            ExpectedEdge(
                f"{MIXED}__twin_bay__calc_b",
                ModuleKind.CALCULATION,
                "value_in",
                f"{MIXED}__twin_bay__sensor_b__reading",
            ),
        ),
        (":>> reading = 11.0;", ":>> reading = 12.0;"),
        (f"{MIXED}__twin_bay__sensor_a__reading",),
    ),
    "C11": RuntimeEvidence(
        MIXED,
        ((f"{MIXED}__station__rig__gain_setting", 42.0),),
        (
            ExpectedEdge(
                f"{MIXED}__station__chain_calc",
                ModuleKind.CALCULATION,
                "value_in",
                f"{MIXED}__station__rig__gain_setting",
            ),
            ExpectedEdge(
                f"{MIXED}__station__chain_guard",
                ModuleKind.CONSTRAINT,
                "v",
                f"{MIXED}__station__rig__gain_setting",
            ),
            ExpectedEdge(
                f"{MIXED}__station__station_total",
                ModuleKind.FORMULA,
                "gain_setting",
                f"{MIXED}__station__rig__gain_setting",
            ),
        ),
        (":>> gain_setting = 42.0;", ":>> gain_setting = 47.0;"),
        (f"{MIXED}__station__rig__gain_setting",),
    ),
    "C12": RuntimeEvidence(
        MIXED,
        ((f"{MIXED}__qual_station__qual_plant__level", 70.0),),
        (
            ExpectedEdge(
                f"{MIXED}__qual_station__qual_plant__qual_calc",
                ModuleKind.CALCULATION,
                "value_in",
                f"{MIXED}__qual_station__qual_plant__level",
            ),
            ExpectedEdge(
                f"{MIXED}__qual_station__qual_plant__qual_guard",
                ModuleKind.CONSTRAINT,
                "v",
                f"{MIXED}__qual_station__qual_plant__level",
            ),
            ExpectedEdge(
                f"{MIXED}__qual_station__qual_total",
                ModuleKind.FORMULA,
                "level",
                f"{MIXED}__qual_station__qual_plant__level",
            ),
        ),
        (":>> level = 70.0;", ":>> level = 71.0;"),
        (f"{MIXED}__qual_station__qual_plant__level",),
    ),
    "C13": RuntimeEvidence(
        MIXED,
        ((f"{MIXED}__bare_station__bare_rig__intensity", 30.0),),
        (
            ExpectedEdge(
                f"{MIXED}__bare_station__bare_rig__bare_calc",
                ModuleKind.CALCULATION,
                "value_in",
                f"{MIXED}__bare_station__bare_rig__intensity",
            ),
            ExpectedEdge(
                f"{MIXED}__bare_station__bare_rig__bare_guard",
                ModuleKind.CONSTRAINT,
                "v",
                f"{MIXED}__bare_station__bare_rig__intensity",
            ),
            ExpectedEdge(
                f"{MIXED}__bare_station__bare_total",
                ModuleKind.FORMULA,
                "intensity",
                f"{MIXED}__bare_station__bare_rig__intensity",
            ),
        ),
        (":>> intensity = 30.0;", ":>> intensity = 31.0;"),
        (f"{MIXED}__bare_station__bare_rig__intensity",),
    ),
    "C14": RuntimeEvidence(
        "elab_matrix_c14",
        (("ElabMatrixC14__host__source__value", 9.0),),
        (
            ExpectedEdge(
                "elabmatrixc14__host__first_calc",
                ModuleKind.CALCULATION,
                "first_input",
                "ElabMatrixC14__host__source__value",
            ),
            ExpectedEdge(
                "elabmatrixc14__host__second",
                ModuleKind.CALCULATION,
                "second_input",
                "ElabMatrixC14__host__source__value",
            ),
        ),
        ("attribute value : Real = 9.0;", "attribute value : Real = 10.0;"),
        ("ElabMatrixC14__host__source__value",),
    ),
    "C15": RuntimeEvidence(
        MIXED,
        ((f"{MIXED}__parent_unit__shared_rate", 40.0),),
        (
            ExpectedEdge(
                f"{MIXED}__parent_unit__child__child_calc",
                ModuleKind.CALCULATION,
                "value_in",
                f"{MIXED}__parent_unit__shared_rate",
            ),
            ExpectedEdge(
                f"{MIXED}__parent_unit__parent_guard",
                ModuleKind.CONSTRAINT,
                "v",
                f"{MIXED}__parent_unit__shared_rate",
            ),
            ExpectedEdge(
                f"{MIXED}__parent_unit__parent_total",
                ModuleKind.FORMULA,
                "shared_rate",
                f"{MIXED}__parent_unit__shared_rate",
            ),
        ),
        (":>> shared_rate = 40.0;", ":>> shared_rate = 41.0;"),
        (f"{MIXED}__parent_unit__shared_rate",),
    ),
    "C16": RuntimeEvidence(
        "elab_matrix_c16",
        (
            ("ElabMatrixC16__host__left__x", 4.0),
            ("ElabMatrixC16__host__right__x", 4.0),
        ),
        (
            ExpectedEdge(
                "elabmatrixc16__host__left",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC16__host__left__x",
            ),
            ExpectedEdge(
                "elabmatrixc16__host__right",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC16__host__right__x",
            ),
        ),
        ("calc left : Observe { in x = 4.0; }", "calc left : Observe { in x = 5.0; }"),
        ("ElabMatrixC16__host__left__x",),
    ),
    "C17": RuntimeEvidence(
        "elab_matrix_aggregations",
        ((f"{AGGS}__permitting__base_cost", 2.0),),
        (
            ExpectedEdge(
                "elabmatrixaggregations__host__permitting__cost_model",
                ModuleKind.CALCULATION,
                "base",
                f"{AGGS}__permitting__base_cost",
            ),
            ExpectedEdge(
                "elabmatrixaggregations__host__producer_total",
                ModuleKind.FORMULA,
                "capital_cost",
                "channel:ElabMatrixAggregations__host__permitting__cost_model__cost",
            ),
        ),
        ("attribute base_cost : Real = 2.0;", "attribute base_cost : Real = 2.5;"),
        (f"{AGGS}__permitting__base_cost",),
        aliases=(
            ExpectedAlias(
                "capital_cost",
                "ElabMatrixAggregations__host__permitting__cost_model__cost",
                "host__permitting",
            ),
        ),
    ),
    "C19": RuntimeEvidence(
        "nested_occurrence_override_probe",
        (("nested_occurrence_override_probe__the_design__panel__source__reading", 80.0),),
        (
            ExpectedEdge(
                "nested_occurrence_override_probe__the_design__panel__noop",
                ModuleKind.CALCULATION,
                "x",
                "nested_occurrence_override_probe__the_design__panel__source__reading",
            ),
            ExpectedEdge(
                "nested_occurrence_override_probe__the_design__panel__within",
                ModuleKind.CONSTRAINT,
                "v",
                "nested_occurrence_override_probe__the_design__panel__source__reading",
            ),
        ),
        (":>> source.reading = 80.0;", ":>> source.reading = 81.0;"),
        ("nested_occurrence_override_probe__the_design__panel__source__reading",),
    ),
    "C20": RuntimeEvidence(
        "shadowed_reference",
        (("ShadowedReference__the_outer__scale", 2.0),),
        (
            ExpectedEdge(
                "shadowedreference__the_outer__inner__shadowed_calc",
                ModuleKind.CALCULATION,
                "factor",
                "ShadowedReference__the_outer__scale",
            ),
        ),
        ("attribute scale : Real = 2.0;", "attribute scale : Real = 3.0;"),
        ("ShadowedReference__the_outer__scale",),
    ),
    "C21": RuntimeEvidence(
        "elab_matrix_c21",
        (("ElabMatrixC21__plant__driver__rate", 9.0),),
        (
            ExpectedEdge(
                "elabmatrixc21__plant__observation",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC21__plant__driver__rate",
            ),
        ),
        (":>> rate = 9.0;", ":>> rate = 10.0;"),
        ("ElabMatrixC21__plant__driver__rate",),
    ),
    "C23": RuntimeEvidence(
        "elab_matrix_c23",
        (
            ("ElabMatrixC23__host__first_calc__x", 3.0),
            ("ElabMatrixC23__host__second__x", 3.0),
        ),
        (
            ExpectedEdge(
                "elabmatrixc23__host__first_calc",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC23__host__first_calc__x",
            ),
            ExpectedEdge(
                "elabmatrixc23__host__second",
                ModuleKind.CALCULATION,
                "x",
                "ElabMatrixC23__host__second__x",
            ),
        ),
        None,
        ("ElabMatrixC23__host__first_calc__x",),
        ("ElabMatrixC23__host__first_calc__x", 4.0),
    ),
    "C24": RuntimeEvidence(
        MIXED,
        ((f"{MIXED}__computed_station__source_identity_computed__base_rate", 2.0),),
        (
            ExpectedEdge(
                f"{MIXED}__computed_station__source_identity_computed__producer_calc",
                ModuleKind.CALCULATION,
                "base",
                f"{MIXED}__computed_station__source_identity_computed__base_rate",
            ),
            ExpectedEdge(
                f"{MIXED}__computed_station__computed_calc",
                ModuleKind.CALCULATION,
                "value_in",
                f"channel:{MIXED}__computed_station__source_identity_computed__producer_calc__result",
            ),
            ExpectedEdge(
                f"{MIXED}__computed_station__computed_guard",
                ModuleKind.CONSTRAINT,
                "v",
                f"channel:{MIXED}__computed_station__source_identity_computed__producer_calc__result",
            ),
            ExpectedEdge(
                f"{MIXED}__computed_station__computed_total",
                ModuleKind.FORMULA,
                "result",
                f"channel:{MIXED}__computed_station__source_identity_computed__producer_calc__result",
            ),
        ),
        ("attribute base_rate : Real = 2.0;", "attribute base_rate : Real = 3.0;"),
        (f"{MIXED}__computed_station__source_identity_computed__base_rate",),
    ),
    "C25": RuntimeEvidence(
        MIXED,
        ((f"{MIXED}__avail_ctx__avail_plant__availability", 0.8),),
        (
            ExpectedEdge(
                f"{MIXED}__avail_ctx__avail_plant__def_authored_calc",
                ModuleKind.CALCULATION,
                "value_in",
                f"{MIXED}__avail_ctx__avail_plant__availability",
            ),
            ExpectedEdge(
                f"{MIXED}__avail_ctx__avail_plant__usage_authored_calc",
                ModuleKind.CALCULATION,
                "value_in",
                f"{MIXED}__avail_ctx__avail_plant__availability",
            ),
        ),
        (":>> availability = 0.8;", ":>> availability = 0.85;"),
        (f"{MIXED}__avail_ctx__avail_plant__availability",),
    ),
    "C26": RuntimeEvidence(
        "elab_matrix_aggregations",
        (
            (f"{AGGS}__permitting__raw_material_cost", 3.0),
            (f"{AGGS}__permitting__fabrication_cost", 4.0),
            (f"{AGGS}__permitting__installation_cost", 5.0),
        ),
        (
            ExpectedEdge(
                "elabmatrixaggregations__host__raw_total",
                ModuleKind.FORMULA,
                "raw_material_cost",
                f"{AGGS}__permitting__raw_material_cost",
            ),
            ExpectedEdge(
                "elabmatrixaggregations__host__fabrication_total",
                ModuleKind.FORMULA,
                "fabrication_cost",
                f"{AGGS}__permitting__fabrication_cost",
            ),
            ExpectedEdge(
                "elabmatrixaggregations__host__installation_total",
                ModuleKind.FORMULA,
                "installation_cost",
                f"{AGGS}__permitting__installation_cost",
            ),
        ),
        (
            "attribute raw_material_cost : Real = 3.0;",
            "attribute raw_material_cost : Real = 3.5;",
        ),
        (f"{AGGS}__permitting__raw_material_cost",),
    ),
}


def _load_internal(model_path: Path, *, strict: bool = True):
    extractor = SysMLDataExtractor([model_path])
    assert extractor.load_models(), f"fixture {model_path.name} failed to load"
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=strict,
    )


@cache
def _baseline_internal(fixture: str):
    return _load_internal(FIXTURES_DIR / fixture)


def _defaults(graph) -> dict[str, float | int | str | bool | None]:
    return {
        parameter.qualified_name: parameter.default_value
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }


def _matching_module(graph, edge: ExpectedEdge):
    matches = [
        module
        for module in graph.modules
        if module.module_kind is edge.module_kind
        and (module.name == edge.module_prefix or module.name.startswith(f"{edge.module_prefix}__"))
    ]
    assert len(matches) == 1, (edge, [module.name for module in matches])
    return matches[0]


def _assert_expected_defaults(graph, evidence: RuntimeEvidence) -> None:
    defaults = _defaults(graph)
    for qualified_name, expected in evidence.defaults:
        assert defaults[qualified_name] == expected


def _public_source(input_) -> str:
    if input_.source.source_type == "module_output":
        return f"channel:{input_.source.producer_channel}"
    return input_.source.qualified_name


def _assert_complete_public_topology(graph, evidence: RuntimeEvidence) -> None:
    tracked_sources = {edge.source for edge in evidence.edges}
    actual = [
        (module, input_, _public_source(input_))
        for module in graph.modules
        for input_ in module.inputs
        if _public_source(input_) in tracked_sources
    ]

    for edge in evidence.edges:
        module = _matching_module(graph, edge)
        [input_] = [item for item in module.inputs if item.param_name == edge.param_name]
        assert _public_source(input_) == edge.source

    assert len(actual) == len(evidence.edges), [
        (module.name, module.module_kind, input_.param_name, source)
        for module, input_, source in actual
    ]
    for module, input_, source in actual:
        matches = [
            edge
            for edge in evidence.edges
            if module.module_kind is edge.module_kind
            and (
                module.name == edge.module_prefix
                or module.name.startswith(f"{edge.module_prefix}__")
            )
            and input_.param_name == edge.param_name
            and source == edge.source
        ]
        assert len(matches) == 1, (module.name, input_.param_name, source)

    tracked_channels = {
        source.removeprefix("channel:")
        for source in tracked_sources
        if source.startswith("channel:")
    }
    actual_aliases = {
        ExpectedAlias(alias.alias_name, alias.canonical_channel, alias.instance_path)
        for alias in graph.output_aliases
        if alias.canonical_channel in tracked_channels
    }
    assert actual_aliases == set(evidence.aliases)


def _typed_route_inventory(graph) -> set[tuple[object, object, str, object]]:
    inventory = set()
    for consumer in (*graph.calcs.values(), *graph.constraints.values()):
        for port, edge in consumer.inputs.items():
            if isinstance(edge, NodeRef):
                kind, target = "node", edge.target
            elif isinstance(edge, ProducerRef):
                kind, target = "producer", edge.target
            elif isinstance(edge, LiteralInput):
                kind, target = "literal", (consumer.node_id, port)
            else:
                raise AssertionError(f"unknown typed edge {edge!r}")
            inventory.add((consumer.node_id, port, kind, target))
    return inventory


def _generated_payload(graph, output_dir: Path) -> dict[str, object]:
    generated = generate_all_derived_jsons(graph.entry_point_groups, output_dir)
    return {
        key: value for output in generated for key, value in json.loads(output.read_text()).items()
    }


def _override_generated_input(output_dir: Path, qualified_name: str, value: float):
    matches = []
    for output in (output_dir / "inputs").glob("*.json"):
        document = json.loads(output.read_text())
        if qualified_name not in document:
            continue
        document[qualified_name] = value
        output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
        matches.append(output)
    assert len(matches) == 1, (qualified_name, matches)
    return {
        key: item
        for output in (output_dir / "inputs").glob("*.json")
        for key, item in json.loads(output.read_text()).items()
    }


def _assert_generated_pipeline(graph, evidence: RuntimeEvidence) -> None:
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES))
    document = yaml.safe_load(generate_pipeline_yaml(graph, "matrix", environment))
    modules = document["modules"]

    for edge in evidence.edges:
        module = _matching_module(graph, edge)
        rendered_source = modules[module.name]["inputs"][edge.param_name].split()[-1]
        if edge.source.startswith("channel:"):
            channel = edge.source.removeprefix("channel:")
            assert rendered_source in {channel, f"{channel}.root"}
        else:
            assert rendered_source.endswith(f".{edge.source}")


def _mutated_model_path(evidence: RuntimeEvidence, output_dir: Path) -> Path:
    assert evidence.mutation is not None
    source_dir = FIXTURES_DIR / evidence.fixture
    changed_dir = output_dir / evidence.fixture
    shutil.copytree(source_dir, changed_dir)
    model_path = changed_dir / "model.sysml"
    before, after = evidence.mutation
    source = model_path.read_text()
    assert source.count(before) == 1, (evidence.fixture, before)
    model_path.write_text(source.replace(before, after, 1))
    return changed_dir


def _assert_runtime_cell(evidence: RuntimeEvidence, tmp_path: Path) -> None:
    internal = _baseline_internal(evidence.fixture)
    payload = encode_instance_graph(internal)
    relocated = tmp_path / "instance-graph.json"
    relocated.write_bytes(payload)

    live = project(internal)
    rebuilt = project(decode_instance_graph(relocated.read_bytes()))
    assert rebuilt == live
    _assert_expected_defaults(live, evidence)
    _assert_expected_defaults(rebuilt, evidence)
    _assert_complete_public_topology(live, evidence)
    _assert_complete_public_topology(rebuilt, evidence)

    baseline_payload = _generated_payload(live, tmp_path / "baseline")
    _assert_generated_pipeline(live, evidence)

    if evidence.public_override is not None:
        qualified_name, value = evidence.public_override
        changed_payload = _override_generated_input(tmp_path / "baseline", qualified_name, value)
    else:
        changed_internal = _load_internal(
            _mutated_model_path(evidence, tmp_path / "changed-model")
        )
        assert _typed_route_inventory(changed_internal) == _typed_route_inventory(internal)
        changed = project(changed_internal)
        _assert_complete_public_topology(changed, evidence)
        _assert_generated_pipeline(changed, evidence)
        changed_payload = _generated_payload(changed, tmp_path / "changed")

    _assert_only_expected_public_changes(
        baseline_payload,
        changed_payload,
        set(evidence.changed_defaults),
    )


def _assert_only_expected_public_changes(
    baseline: dict[str, object],
    changed: dict[str, object],
    expected_changes: set[str],
) -> None:
    assert changed.keys() == baseline.keys()
    assert {name for name in baseline if baseline[name] != changed[name]} == expected_changes


def test_mutation_evidence_rejects_a_phantom_public_input() -> None:
    with pytest.raises(AssertionError):
        _assert_only_expected_public_changes(
            {"source": 1.0},
            {"source": 2.0, "phantom": 3.0},
            {"source"},
        )


def _src_01(_tmp_path: Path) -> None:
    # Specimen moved off ``fusion_tea`` in Slice 3D: its fifteen self-named
    # bindings were migrated in place to the D-5 ``<formal>_in`` form, so the
    # customer model no longer exercises this cell. ``self_named_binding_trap``
    # is the fixture authored to carry the mechanism on its own.
    with pytest.raises(ElaborationError) as excinfo:
        _load_internal(FIXTURES_DIR / "self_named_binding_trap")
    assert any(finding.code is ReadinessCode.SI_SELF_BINDING for finding in excinfo.value.findings)


def _src_02(_tmp_path: Path) -> None:
    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        _load_internal(FIXTURES_DIR / "source_identity_indexed_source")
    assert [diagnostic.code for diagnostic in excinfo.value.diagnostics] == [
        ElaborationCode.SI_INDEXED_SOURCE_UNSUPPORTED
    ]


def _assert_load_error(model_path: Path, detail: str) -> None:
    extractor = SysMLDataExtractor([model_path])
    assert not extractor.load_models()
    errors = [str(error) for error in extractor.diagnostics.errors]
    assert errors
    assert any(detail in error for error in errors), errors


def _src_03(_tmp_path: Path) -> None:
    _assert_load_error(
        ROOT
        / ".project/active/source-identity-binding-semantics-spike/probes/models"
        / "form_bracket_sq.sysml",
        "error",
    )


def _ambiguity(cell: str) -> Callable[[Path], None]:
    consumer = "amb_qual_calc" if cell == "C9" else "amb_bare_calc"
    expected = ElaborationCode.SI_OCCURRENCE_MISSING

    def assert_evidence(_tmp_path: Path) -> None:
        graph = _load_internal(FIXTURES_DIR / "source_identity_occurrence_ambiguity", strict=False)
        [diagnostic] = [item for item in graph.diagnostics if consumer in item.consumer_display]
        assert diagnostic.code is expected
        assert diagnostic.param_name == "value_in"

    return assert_evidence


def _c18(_tmp_path: Path) -> None:
    _assert_load_error(FIXTURES_DIR / "source_identity_absent_referent", "ghost_cost")


def _c22(_tmp_path: Path) -> None:
    with pytest.raises(ElaborationDiagnosticError) as raised:
        elaborate_model_paths([FIXTURES_DIR / "invocation_binding_probe"], strict=False)
    [diagnostic] = raised.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_EXPRESSION_SOURCE_UNSUPPORTED
    assert diagnostic.reference == "Doubler(v = a)"
    assert diagnostic.source_file == "root-0/design.sysml"
    assert diagnostic.source_line == 19
    rendered = str(raised.value)
    assert rendered.count("SI_EXPRESSION_SOURCE_UNSUPPORTED") == 1
    assert "root-0/design.sysml:19" in rendered
    assert "/tmp/" not in rendered
    cause = raised.value.__cause__
    assert isinstance(cause, SemanticEvidenceError)
    assert cause.code is SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED


def _runtime(cell_id: str) -> Callable[[Path], None]:
    def assert_evidence(tmp_path: Path) -> None:
        _assert_runtime_cell(RUNTIME_CELLS[cell_id], tmp_path)

    return assert_evidence


EVIDENCE: dict[str, Callable[[Path], None]] = {
    "SRC-01": _src_01,
    "SRC-02": _src_02,
    "SRC-03": _src_03,
    **{cell_id: _runtime(cell_id) for cell_id in RUNTIME_CELLS},
    "C9": _ambiguity("C9"),
    "C10": _ambiguity("C10"),
    "C18": _c18,
    "C22": _c22,
}


def _authority_cell_ids() -> set[str]:
    section = CONTRACT.read_text().split("### Source-identity scenarios", 1)[1]
    section = section.split("## Appendix D", 1)[0]
    return set(re.findall(r"^\*\*(SRC-\d+|C\d+)\s+—", section, re.MULTILINE))


def test_matrix_map_matches_all_authoritative_cells() -> None:
    assert _authority_cell_ids() == set(EVIDENCE)
    assert len(EVIDENCE) == 29
    assert all(callable(evidence) for evidence in EVIDENCE.values())


@pytest.mark.parametrize("cell_id", sorted(EVIDENCE), ids=sorted(EVIDENCE))
def test_cell_executes_its_required_public_or_diagnostic_evidence(
    cell_id: str, tmp_path: Path
) -> None:
    EVIDENCE[cell_id](tmp_path)
