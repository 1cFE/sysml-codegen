"""Conformance tests for Pipeline YAML Generator (C20).

Requirements: REQ-PY-01 through REQ-PY-07
Design intent: 21-pipeline-yaml-generation.md

Tests verify generate_pipeline_yaml() behavior with real ComputationGraph data:
- REQ-PY-01: All entry point sources include param_group prefix
- REQ-PY-02: No InputSource.param_group is None for entry points
- REQ-PY-03: All numeric types are "float" (including multiplicity)
- REQ-PY-04: Single-output MODULE_OUTPUT sources append .root
- REQ-PY-05: channel_field_map covers every ModuleOutput
- REQ-PY-06: Exit point type is RootModel[T] for root, else T
- REQ-PY-07: One JSON file per ParameterGroup in entry_fusion
- Gold standard: pipeline.py imports only from resolution/models.py
- Structural: Generated YAML is valid with expected structure

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
import inspect
import re
import textwrap
from pathlib import Path

import pytest
import yaml

from sysml_codegen.generation.pipeline import generate_pipeline_yaml
from sysml_codegen.resolution.models import ComputationGraph

import jinja2

# Reuse the graph builder from C17
from sysml_codegen.snapshot import (
    build_full_graph_from_snapshot,
)
from tests.conftest import snapshot_fixture


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"
BASELINE_DIR = Path(__file__).parent.parent / "fixtures" / "baseline_yaml"


# Models that exercise all pipeline YAML features
PARAMETRIZED_MODELS = [
    "solar_battery_model",
    "catf_mfe_model",
    "chain_spike_model",
    "attr_expr_probe",
]

# Short IDs for parametrization
MODEL_IDS = {
    "solar_battery_model": "solar_battery",
    "catf_mfe_model": "catf_mfe",
    "chain_spike_model": "chain_spike",
    "attr_expr_probe": "attr_expr_probe",
}


@pytest.fixture(scope="session")
def template_env():
    """Jinja2 template environment for pipeline YAML generation."""
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture(scope="session")
def all_graphs() -> dict[str, ComputationGraph]:
    """Build ComputationGraphs for all parametrized models (once per session)."""
    graphs = {}
    for model_name in PARAMETRIZED_MODELS:
        graph, _ = build_full_graph_from_snapshot(snapshot_fixture(model_name))
        graphs[model_name] = graph
    return graphs


@pytest.fixture(scope="session")
def all_yamls(all_graphs, template_env) -> dict[str, str]:
    """Generate pipeline YAML for all models (once per session)."""
    yamls = {}
    for model_name, graph in all_graphs.items():
        package_name = MODEL_IDS[model_name]
        yamls[model_name] = generate_pipeline_yaml(
            graph=graph,
            package_name=package_name,
            template_env=template_env,
        )
    return yamls


@pytest.fixture(scope="session")
def all_parsed_yamls(all_yamls) -> dict[str, dict]:
    """Parse generated YAML for all models (once per session)."""
    return {
        model_name: yaml.safe_load(yaml_str)
        for model_name, yaml_str in all_yamls.items()
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_module_input_lines(yaml_str: str) -> list[str]:
    """Extract all input lines from generated YAML (excluding entry_fusion).

    Returns lines like "param_name: float source_value".
    """
    lines = []
    in_inputs = False
    in_entry_fusion = False
    for line in yaml_str.splitlines():
        stripped = line.strip()
        # Track if we're inside entry_fusion
        if stripped == "entry_fusion:":
            in_entry_fusion = True
            continue
        # A new module definition starts (not indented under entry_fusion)
        if re.match(r"^  \w", line) and ":" in stripped and not stripped.startswith("#"):
            in_entry_fusion = False
            in_inputs = False
        if stripped == "inputs:":
            in_inputs = True
            continue
        if stripped in ("outputs:", "") or stripped.startswith("#"):
            in_inputs = False
            continue
        if in_inputs and not in_entry_fusion and stripped:
            lines.append(stripped)
    return lines


def _get_entry_point_input_lines(yaml_str: str) -> list[str]:
    """Extract entry_point input lines from module inputs sections.

    Entry point inputs are those whose source does NOT contain a module channel
    (i.e., source has a dot-prefix like 'design_params.QN' or 'library_params.QN').
    We identify them by checking if the source portion starts with a known param
    group prefix followed by a dot.
    """
    lines = []
    for line in _get_module_input_lines(yaml_str):
        # Format: "param_name: type source"
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        param_with_colon, type_str, source = parts
        # Entry point sources have a param_group prefix with dot separator
        # Module output sources are bare channel names (no prefix dot pattern)
        # Entry point pattern: word.QualifiedName (e.g., design_params.QN)
        if re.match(r"^[a-z_]+\.[A-Z]", source):
            lines.append(line)
    return lines


def _get_all_input_sources(graph: ComputationGraph) -> list:
    """Get all InputSource objects from all module inputs."""
    sources = []
    for module in graph.modules:
        for inp in module.inputs:
            sources.append(inp.source)
    return sources


# ---------------------------------------------------------------------------
# REQ-PY-01: Entry point sources include param_group prefix
# ---------------------------------------------------------------------------

class TestParamGroupPrefix:
    """REQ-PY-01: ALL entry point sources in pipeline YAML SHALL include a
    param_group.qualified_name format -- no bare qualified names."""

    @pytest.mark.req("REQ-PY-01")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_param_group_prefix_all_entry_points(
        self, model_name, all_graphs, all_yamls,
    ):
        """Every entry_point source in YAML has {group}.{qn} format."""
        graph = all_graphs[model_name]
        yaml_str = all_yamls[model_name]

        # Find all entry_point InputSources in the graph
        ep_qns = set()
        for module in graph.modules:
            for inp in module.inputs:
                if inp.source.source_type == "entry_point":
                    ep_qns.add(inp.source.qualified_name)

        if not ep_qns:
            pytest.skip(f"No entry points in {model_name}")

        # Check YAML: no entry point QN appears without a prefix
        for line in _get_module_input_lines(yaml_str):
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            param_with_colon, type_str, source = parts
            # If the source matches a known EP qualified name, it must have a prefix
            for qn in ep_qns:
                if source == qn:
                    pytest.fail(
                        f"Entry point {qn} has no param_group prefix in YAML line: {line}"
                    )
                if source.endswith(f".{qn}"):
                    # Correctly prefixed -- good
                    pass


# ---------------------------------------------------------------------------
# REQ-PY-02: No None param_group on entry point InputSources
# ---------------------------------------------------------------------------

class TestParamGroupNotNone:
    """REQ-PY-02: InputSource.param_group SHALL NOT be None for any entry point
    in the ComputationGraph."""

    @pytest.mark.req("REQ-PY-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_param_group_not_none_in_graph(self, model_name, all_graphs):
        """No entry_point InputSource in ComputationGraph has param_group=None."""
        graph = all_graphs[model_name]
        violations = []
        for module in graph.modules:
            for inp in module.inputs:
                if inp.source.source_type == "entry_point":
                    if inp.source.param_group is None:
                        violations.append(
                            f"  {module.name}.{inp.param_name}: "
                            f"qn={inp.source.qualified_name}"
                        )
        assert not violations, (
            f"Entry points with param_group=None in {model_name}:\n"
            + "\n".join(violations)
        )


# ---------------------------------------------------------------------------
# REQ-PY-03: All numeric types are "float"
# ---------------------------------------------------------------------------

class TestAllNumericTypesFloat:
    """REQ-PY-03: ALL numeric pipeline input types SHALL be 'float'."""

    @pytest.mark.req("REQ-PY-03")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_all_numeric_types_float(self, model_name, all_yamls):
        """No 'int' type string in any YAML inputs line."""
        yaml_str = all_yamls[model_name]
        violations = []
        for line in _get_module_input_lines(yaml_str):
            parts = line.split(None, 2)
            if len(parts) >= 2:
                param_with_colon, type_str = parts[0], parts[1]
                if type_str == "int":
                    violations.append(line)
        assert not violations, (
            f"Input lines with 'int' type in {model_name}:\n"
            + "\n".join(f"  {v}" for v in violations)
        )


# ---------------------------------------------------------------------------
# REQ-PY-04: .root suffix on single-output MODULE_OUTPUT sources
# ---------------------------------------------------------------------------

class TestRootSuffix:
    """REQ-PY-04: MODULE_OUTPUT sources with field_name='root' SHALL append .root."""

    @pytest.mark.req("REQ-PY-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:2],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:2]])
    def test_root_suffix_on_single_output(self, model_name, all_graphs, all_yamls):
        """Every MODULE_OUTPUT source referencing a single-output module
        (field_name='root') appends .root in the YAML."""
        graph = all_graphs[model_name]
        yaml_str = all_yamls[model_name]

        # Build channel_field_map (same logic as pipeline.py)
        channel_field_map = {
            out.channel_name: out.field_name
            for module in graph.modules
            for out in module.outputs
        }

        # Find channels that have field_name="root" (single-output)
        root_channels = {
            ch for ch, field in channel_field_map.items() if field == "root"
        }

        if not root_channels:
            pytest.skip(f"No single-output modules in {model_name}")

        # Check YAML: every reference to a root channel must end with .root
        for line in _get_module_input_lines(yaml_str):
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            source = parts[2]
            # Check if source references a root channel
            for ch in root_channels:
                if source == ch:
                    pytest.fail(
                        f"Root channel {ch} missing .root suffix in: {line}"
                    )
                if source == f"{ch}.root":
                    # Correct
                    pass


# ---------------------------------------------------------------------------
# REQ-PY-05: channel_field_map complete
# ---------------------------------------------------------------------------

class TestChannelFieldMapComplete:
    """REQ-PY-05: channel_field_map SHALL contain an entry for every ModuleOutput."""

    @pytest.mark.req("REQ-PY-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:2],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:2]])
    def test_channel_field_map_complete(self, model_name, all_graphs):
        """len(channel_field_map) == sum(len(m.outputs) for m in graph.modules)."""
        graph = all_graphs[model_name]

        channel_field_map = {
            out.channel_name: out.field_name
            for module in graph.modules
            for out in module.outputs
        }
        total_outputs = sum(len(m.outputs) for m in graph.modules)
        assert len(channel_field_map) == total_outputs, (
            f"channel_field_map has {len(channel_field_map)} entries "
            f"but {total_outputs} module outputs exist in {model_name}"
        )


# ---------------------------------------------------------------------------
# REQ-PY-06: Exit point type rules
# ---------------------------------------------------------------------------

class TestExitPointTypeRules:
    """REQ-PY-06: Exit point type SHALL be RootModel[T] when field_name='root',
    else T for named fields."""

    @pytest.mark.req("REQ-PY-06")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:2],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:2]])
    def test_exit_point_type_rules(self, model_name, all_graphs, all_parsed_yamls):
        """Exit point types match upstream module output types."""
        graph = all_graphs[model_name]
        parsed = all_parsed_yamls[model_name]

        # Build expected exit point types from graph
        expected = {}
        for module in graph.modules:
            for out in module.outputs:
                if out.field_name == "root":
                    expected[out.channel_name] = f"RootModel[{out.python_type}]"
                else:
                    expected[out.channel_name] = out.python_type

        # Parse exit_point outputs from YAML
        exit_outputs = parsed["modules"]["exit_point"]["outputs"]
        for channel_name, value_str in exit_outputs.items():
            # value_str is like "RootModel[float] channel.json" or "float channel.json"
            # Split to get the type
            parts = str(value_str).rsplit(" ", 1)
            actual_type = parts[0] if len(parts) > 1 else str(value_str)
            assert channel_name in expected, (
                f"Exit point {channel_name} not found in graph outputs"
            )
            assert actual_type == expected[channel_name], (
                f"Exit point {channel_name}: expected type {expected[channel_name]}, "
                f"got {actual_type}"
            )


# ---------------------------------------------------------------------------
# REQ-PY-07: Entry fusion JSON count
# ---------------------------------------------------------------------------

class TestEntryFusionJsonCount:
    """REQ-PY-07: Entry point module inputs SHALL list one JSON file per
    ParameterGroup."""

    @pytest.mark.req("REQ-PY-07")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:2],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:2]])
    def test_entry_fusion_json_count(self, model_name, all_graphs, all_parsed_yamls):
        """len(entry_fusion_inputs) == len(graph.entry_point_groups)."""
        graph = all_graphs[model_name]
        parsed = all_parsed_yamls[model_name]

        entry_fusion = parsed["modules"]["entry_fusion"]
        entry_inputs = entry_fusion["inputs"]
        assert len(entry_inputs) == len(graph.entry_point_groups), (
            f"entry_fusion has {len(entry_inputs)} inputs "
            f"but graph has {len(graph.entry_point_groups)} parameter groups "
            f"in {model_name}"
        )


# ---------------------------------------------------------------------------
# Gold standard: generator imports only resolution models
# ---------------------------------------------------------------------------

class TestGoldStandard:
    """pipeline.py imports NOTHING from extraction/, analysis/, or
    generation/initialization.py."""

    @pytest.mark.req("REQ-PY-01")
    def test_generator_imports_only_resolution_models(self):
        """Static analysis: pipeline.py has no forbidden imports."""
        pipeline_path = (
            Path(__file__).parent.parent.parent
            / "src" / "sysml_codegen" / "generation" / "pipeline.py"
        )
        source = pipeline_path.read_text()
        tree = ast.parse(source)

        forbidden_prefixes = [
            "sysml_codegen.extraction",
            "sysml_codegen.analysis",
            "sysml_codegen.generation.initialization",
        ]

        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for prefix in forbidden_prefixes:
                    if node.module.startswith(prefix):
                        violations.append(f"  line {node.lineno}: from {node.module}")

        assert not violations, (
            "pipeline.py has forbidden imports:\n" + "\n".join(violations)
        )


# ---------------------------------------------------------------------------
# Structural: YAML parseable
# ---------------------------------------------------------------------------

class TestYamlParseable:
    """Generated YAML is valid YAML with expected top-level keys."""

    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:2],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:2]])
    def test_yaml_parseable(self, model_name, all_parsed_yamls):
        """Generated YAML parses with expected top-level keys: metadata, modules."""
        parsed = all_parsed_yamls[model_name]
        assert "metadata" in parsed, f"Missing 'metadata' key in {model_name} YAML"
        assert "modules" in parsed, f"Missing 'modules' key in {model_name} YAML"
        assert "entry_fusion" in parsed["modules"], (
            f"Missing 'entry_fusion' in modules for {model_name}"
        )
        assert "exit_point" in parsed["modules"], (
            f"Missing 'exit_point' in modules for {model_name}"
        )


# ---------------------------------------------------------------------------
# Structural: Module comment format
# ---------------------------------------------------------------------------

class TestModuleCommentFormat:
    """CalcUsage modules have '# module_type' comment; FORMULA have
    '# source: computed_attribute'; Aggregation have '# source: aggregation'."""

    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_module_comment_format(self, model_name, all_graphs, all_yamls):
        """Module comment lines match module origin type."""
        graph = all_graphs[model_name]
        yaml_str = all_yamls[model_name]

        # Build lookup: module_name -> module
        module_lookup = {m.name: m for m in graph.modules}

        # Extract comment lines before each module definition
        lines = yaml_str.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("# ") and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # Check if next line is a module instance name
                if ":" in next_line and not next_line.startswith("#"):
                    module_name = next_line.split(":")[0].strip()
                    if module_name in module_lookup:
                        module = module_lookup[module_name]
                        comment = stripped[2:]  # Strip "# "
                        if module.is_aggregation:
                            assert comment.startswith("source: aggregation"), (
                                f"Aggregation module {module_name} has wrong comment: {stripped}"
                            )
                        elif module.is_computed_attribute:
                            assert comment.startswith("source: computed_attribute"), (
                                f"FORMULA module {module_name} has wrong comment: {stripped}"
                            )
                        else:
                            # CalcUsage: comment is the module_type
                            assert comment == module.module_type, (
                                f"CalcUsage module {module_name}: comment '{comment}' "
                                f"!= module_type '{module.module_type}'"
                            )


# ---------------------------------------------------------------------------
# Baseline comparison
# ---------------------------------------------------------------------------

BASELINE_MODELS = [
    "solar_battery_model",
    "chain_spike_model",
    "attr_expr_probe",
]
BASELINE_IDS = {
    "solar_battery_model": "solar_battery",
    "chain_spike_model": "chain_spike",
    "attr_expr_probe": "attr_expr_probe",
}


class TestYamlBaselineComparison:
    """Generated YAML from snapshot matches updated baseline."""

    @pytest.mark.baseline
    @pytest.mark.parametrize("model_name", BASELINE_MODELS,
                             ids=[BASELINE_IDS[m] for m in BASELINE_MODELS])
    def test_yaml_baseline_comparison(self, model_name, all_yamls):
        """Generated YAML from snapshot matches baseline file."""
        short_name = BASELINE_IDS[model_name]
        baseline_path = BASELINE_DIR / f"{short_name}.yaml"
        assert baseline_path.exists(), f"Baseline file not found: {baseline_path}"

        baseline = baseline_path.read_text()
        generated = all_yamls[model_name]

        assert generated == baseline, (
            f"YAML diff for {short_name}: generated output differs from baseline.\n"
            f"If this is expected after Bug 9/10 fixes, update the baseline."
        )

    @pytest.mark.baseline
    def test_yaml_baseline_comparison_wi014_toy(self, template_env) -> None:
        """Item 11 shape A (REQ-PY-08): wi014_toy's committed YAML baseline matches
        the generated output, including the ``total_cost`` exit-point filename
        rename (``…cost_calc__cost`` line → ``demo_plant__total_cost.json``).

        Standalone (not in the shared parametrized fixtures) — a single
        shape-A fixture with a committed YAML, kept off the broad feature-matrix
        tests that target the multi-feature models.
        """
        graph, _ = build_full_graph_from_snapshot(snapshot_fixture("wi014_toy"))
        generated = generate_pipeline_yaml(graph, "wi014_toy", template_env)
        baseline = (BASELINE_DIR / "wi014_toy.yaml").read_text()
        assert generated == baseline, (
            "YAML diff for wi014_toy: generated output differs from committed "
            "baseline. Regenerate via scripts/capture_baseline_yaml.py if intended."
        )
