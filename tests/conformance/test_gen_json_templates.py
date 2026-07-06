"""Conformance tests for JSON Template + Parameter Schema Generator (C25).

Requirements: REQ-GEN-05, REQ-PY-07
Design intent: 08-generation.md, 21-pipeline-yaml-generation.md

Tests verify JSON template and Pydantic schema generation from
ComputationGraph.entry_point_groups with real extraction snapshots:
- REQ-GEN-05: Each ParameterGroup produces one JSON template + one Pydantic schema
- REQ-PY-07: Number of JSON files matches number of ParameterGroups

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import jinja2
import pytest

from sysml_codegen.generation.entry_point import (
    generate_all_derived_jsons_from_graph,
    generate_all_derived_schemas_from_graph,
)
from sysml_codegen.resolution.models import ComputationGraph

from sysml_codegen.snapshot import (
    build_full_graph_from_snapshot,
)
from tests.conftest import snapshot_fixture


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"

PARAMETRIZED_MODELS = [
    "solar_battery_model",
    "catf_mfe_model",
]

MODEL_IDS = {
    "solar_battery_model": "solar_battery",
    "catf_mfe_model": "catf_mfe",
}


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def template_env():
    """Jinja2 template environment for schema generation."""
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
def all_jsons(all_graphs, tmp_path_factory) -> dict[str, list[Path]]:
    """Generate JSON template files for all models (once per session)."""
    result = {}
    for model_name in PARAMETRIZED_MODELS:
        graph = all_graphs[model_name]
        output_dir = tmp_path_factory.mktemp(f"json_{MODEL_IDS[model_name]}")
        files = generate_all_derived_jsons_from_graph(
            graph.entry_point_groups, output_dir,
        )
        result[model_name] = files
    return result


@pytest.fixture(scope="session")
def all_schemas(all_graphs, template_env, tmp_path_factory) -> dict[str, list[Path]]:
    """Generate Pydantic schema files for all models (once per session)."""
    result = {}
    for model_name in PARAMETRIZED_MODELS:
        graph = all_graphs[model_name]
        output_dir = tmp_path_factory.mktemp(f"schema_{MODEL_IDS[model_name]}")
        files = generate_all_derived_schemas_from_graph(
            graph.entry_point_groups, template_env, output_dir,
        )
        result[model_name] = files
    return result


# ---------------------------------------------------------------------------
# REQ-GEN-05: One JSON per ParameterGroup
# ---------------------------------------------------------------------------

class TestOneJsonPerGroup:
    """generate_all_derived_jsons_from_graph() produces exactly
    len(graph.entry_point_groups) JSON files."""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_one_json_per_group(self, model_name, all_graphs, all_jsons):
        graph = all_graphs[model_name]
        json_files = all_jsons[model_name]
        assert len(json_files) == len(graph.entry_point_groups), (
            f"{model_name}: expected {len(graph.entry_point_groups)} JSON files, "
            f"got {len(json_files)}"
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: One schema per ParameterGroup
# ---------------------------------------------------------------------------

class TestOneSchemaPerGroup:
    """generate_all_derived_schemas_from_graph() produces exactly
    len(graph.entry_point_groups) schema files."""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_one_schema_per_group(self, model_name, all_graphs, all_schemas):
        graph = all_graphs[model_name]
        schema_files = all_schemas[model_name]
        assert len(schema_files) == len(graph.entry_point_groups), (
            f"{model_name}: expected {len(graph.entry_point_groups)} schema files, "
            f"got {len(schema_files)}"
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: JSON filenames match group names
# ---------------------------------------------------------------------------

class TestJsonFilenamesMatchGroups:
    """Each generated JSON filename matches {group.name}.json."""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_json_filenames_match_groups(
        self, model_name, all_graphs, all_jsons,
    ):
        graph = all_graphs[model_name]
        json_files = all_jsons[model_name]

        expected_names = {f"{g.name}.json" for g in graph.entry_point_groups}
        actual_names = {Path(f).name for f in json_files}

        assert actual_names == expected_names, (
            f"{model_name}: filename mismatch.\n"
            f"  Expected: {sorted(expected_names)}\n"
            f"  Actual:   {sorted(actual_names)}"
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: Schema filenames match group names
# ---------------------------------------------------------------------------

class TestSchemaFilenamesMatchGroups:
    """Each generated schema filename matches {group.name}.py."""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_schema_filenames_match_groups(
        self, model_name, all_graphs, all_schemas,
    ):
        graph = all_graphs[model_name]
        schema_files = all_schemas[model_name]

        expected_names = {f"{g.name}.py" for g in graph.entry_point_groups}
        actual_names = {f.name for f in schema_files}

        assert actual_names == expected_names, (
            f"{model_name}: filename mismatch.\n"
            f"  Expected: {sorted(expected_names)}\n"
            f"  Actual:   {sorted(actual_names)}"
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: JSON values match EP defaults
# ---------------------------------------------------------------------------

class TestJsonValuesMatchDefaults:
    """For each group, JSON keys/values match {ep.qualified_name: ep.default_value}
    for all EPs with non-None defaults."""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_json_values_match_defaults(
        self, model_name, all_graphs, all_jsons,
    ):
        graph = all_graphs[model_name]
        json_files = all_jsons[model_name]

        # Build lookup: filename -> Path
        file_lookup = {Path(f).name: Path(f) for f in json_files}

        mismatches = []
        for group in graph.entry_point_groups:
            json_path = file_lookup[f"{group.name}.json"]
            data = json.loads(json_path.read_text())

            expected = {
                ep.qualified_name: ep.default_value
                for ep in group.parameters
                if ep.default_value is not None
            }

            if data != expected:
                mismatches.append(
                    f"  {group.name}: expected {len(expected)} entries, got {len(data)}"
                )

        assert not mismatches, (
            f"JSON value mismatches in {model_name}:\n" + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: JSON excludes None defaults
# ---------------------------------------------------------------------------

class TestJsonExcludesNoneDefaults:
    """EPs with default_value=None are absent from JSON templates."""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_json_excludes_none_defaults(
        self, model_name, all_graphs, all_jsons,
    ):
        graph = all_graphs[model_name]
        json_files = all_jsons[model_name]
        file_lookup = {Path(f).name: Path(f) for f in json_files}

        violations = []
        for group in graph.entry_point_groups:
            none_eps = [ep for ep in group.parameters if ep.default_value is None]

            if not none_eps:
                continue

            json_path = file_lookup[f"{group.name}.json"]
            data = json.loads(json_path.read_text())

            for ep in none_eps:
                if ep.qualified_name in data:
                    violations.append(
                        f"  {group.name}: {ep.qualified_name} has None default "
                        f"but appears in JSON with value={data[ep.qualified_name]}"
                    )

        # Non-vacuity note: pre-Item-10 catf_mfe carried a None-default EP
        # (magnets_params.magnet_volume) that this test used to prove the exclusion
        # path actually runs. Item 10 stage (a) WIRED that gap, so catf no longer has
        # a None-default EP — the guard is dropped rather than asserted-false. The
        # ``not violations`` check below still fires on every None EP the corpus has;
        # it is vacuously true only when a model has none (which is now the healthy
        # state for both parametrized models).
        assert not violations, (
            f"None-default violations in {model_name}:\n" + "\n".join(violations)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: JSON keys are sorted
# ---------------------------------------------------------------------------

class TestJsonKeysSorted:
    """JSON output has keys in sorted order (deterministic output)."""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_json_keys_sorted(self, model_name, all_jsons):
        json_files = all_jsons[model_name]

        unsorted = []
        for json_path in json_files:
            path = Path(json_path)
            raw = path.read_text()
            # Parse preserving key order
            data = json.loads(raw)
            keys = list(data.keys())
            if keys != sorted(keys):
                unsorted.append(
                    f"  {path.name}: keys not sorted"
                )

        assert not unsorted, (
            f"Unsorted JSON keys in {model_name}:\n" + "\n".join(unsorted)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: Schema class name matches group.class_name
# ---------------------------------------------------------------------------

class TestSchemaClassNameMatches:
    """Generated schema contains class {group.class_name}(BaseModel):"""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_schema_class_name_matches(
        self, model_name, all_graphs, all_schemas,
    ):
        graph = all_graphs[model_name]
        schema_files = all_schemas[model_name]
        file_lookup = {f.name: f for f in schema_files}

        mismatches = []
        for group in graph.entry_point_groups:
            schema_path = file_lookup[f"{group.name}.py"]
            source = schema_path.read_text()

            expected_class = f"class {group.class_name}(BaseModel):"
            if expected_class not in source:
                mismatches.append(
                    f"  {group.name}: expected '{expected_class}' not found"
                )

        assert not mismatches, (
            f"Schema class name mismatches in {model_name}:\n"
            + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: Schema has one field per EP
# ---------------------------------------------------------------------------

class TestSchemaFieldsMatchEPs:
    """Schema has one field per EP in the group, using ep.qualified_name."""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_schema_fields_match_eps(
        self, model_name, all_graphs, all_schemas,
    ):
        graph = all_graphs[model_name]
        schema_files = all_schemas[model_name]
        file_lookup = {f.name: f for f in schema_files}

        mismatches = []
        for group in graph.entry_point_groups:
            schema_path = file_lookup[f"{group.name}.py"]
            source = schema_path.read_text()
            tree = ast.parse(source)

            # Extract field names from the class
            generated_fields = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            generated_fields.add(item.target.id)
                    break

            expected_fields = {ep.qualified_name for ep in group.parameters}

            if generated_fields != expected_fields:
                missing = expected_fields - generated_fields
                extra = generated_fields - expected_fields
                detail = []
                if missing:
                    detail.append(f"missing={sorted(missing)}")
                if extra:
                    detail.append(f"extra={sorted(extra)}")
                mismatches.append(f"  {group.name}: {', '.join(detail)}")

        assert not mismatches, (
            f"Schema field mismatches in {model_name}:\n" + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: Schema field types are float
# ---------------------------------------------------------------------------

class TestSchemaFieldTypesFloat:
    """Schema field types are float (matching ep.python_type for all real data)."""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_schema_field_types_float(
        self, model_name, all_graphs, all_schemas,
    ):
        graph = all_graphs[model_name]
        schema_files = all_schemas[model_name]
        file_lookup = {f.name: f for f in schema_files}

        non_float = []
        for group in graph.entry_point_groups:
            schema_path = file_lookup[f"{group.name}.py"]
            source = schema_path.read_text()
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if not isinstance(item, ast.AnnAssign):
                            continue
                        if not isinstance(item.target, ast.Name):
                            continue
                        type_str = ast.unparse(item.annotation)
                        if type_str != "float":
                            non_float.append(
                                f"  {group.name}.{item.target.id}: type={type_str}"
                            )
                    break

        assert not non_float, (
            f"Non-float field types in {model_name}:\n" + "\n".join(non_float)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: Schema parses as valid Python
# ---------------------------------------------------------------------------

class TestSchemaValidPython:
    """ast.parse() succeeds on every generated schema file."""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_schema_parses_as_valid_python(
        self, model_name, all_schemas,
    ):
        schema_files = all_schemas[model_name]

        failures = []
        for schema_path in schema_files:
            source = schema_path.read_text()
            try:
                ast.parse(source)
            except SyntaxError as e:
                failures.append(f"  {schema_path.name}: {e}")

        assert not failures, (
            f"Invalid Python in {model_name} schemas:\n" + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: Schema default matches EP default
# ---------------------------------------------------------------------------

class TestSchemaDefaultMatchesEP:
    """Schema fields with defaults render Field(default={ep.default_value}, ...)."""

    @pytest.mark.req("REQ-GEN-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_05_schema_default_matches_ep(
        self, model_name, all_graphs, all_schemas,
    ):
        graph = all_graphs[model_name]
        schema_files = all_schemas[model_name]
        file_lookup = {f.name: f for f in schema_files}

        mismatches = []
        for group in graph.entry_point_groups:
            schema_path = file_lookup[f"{group.name}.py"]
            source = schema_path.read_text()
            tree = ast.parse(source)

            # Build expected defaults from EP data
            ep_defaults = {
                ep.qualified_name: ep.default_value
                for ep in group.parameters
            }

            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                for item in node.body:
                    if not isinstance(item, ast.AnnAssign):
                        continue
                    if not isinstance(item.target, ast.Name):
                        continue

                    field_name = item.target.id
                    if field_name not in ep_defaults:
                        continue

                    expected_default = ep_defaults[field_name]

                    # Extract default= from Field() call
                    actual_default = None
                    has_default_kwarg = False
                    if isinstance(item.value, ast.Call):
                        for keyword in item.value.keywords:
                            if keyword.arg == "default":
                                has_default_kwarg = True
                                actual_default = ast.literal_eval(keyword.value)

                    if expected_default is not None:
                        if not has_default_kwarg:
                            mismatches.append(
                                f"  {group.name}.{field_name}: expected default="
                                f"{expected_default}, but no default= in Field()"
                            )
                        elif actual_default != expected_default:
                            mismatches.append(
                                f"  {group.name}.{field_name}: expected default="
                                f"{expected_default}, got {actual_default}"
                            )
                    else:
                        if has_default_kwarg:
                            mismatches.append(
                                f"  {group.name}.{field_name}: expected no default, "
                                f"but found default={actual_default}"
                            )
                break

        assert not mismatches, (
            f"Schema default mismatches in {model_name}:\n" + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# REQ-PY-07: JSON file count matches ParameterGroups (cross-check)
# ---------------------------------------------------------------------------

class TestJsonFileCountMatchesYamlEntry:
    """Number of generated JSON files equals number of ParameterGroups."""

    @pytest.mark.req("REQ-PY-07")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_py_07_json_file_count_matches_entry_point_groups(
        self, model_name, all_graphs, all_jsons,
    ):
        graph = all_graphs[model_name]
        json_files = all_jsons[model_name]

        assert len(json_files) == len(graph.entry_point_groups), (
            f"{model_name}: {len(json_files)} JSON files != "
            f"{len(graph.entry_point_groups)} ParameterGroups"
        )


# ---------------------------------------------------------------------------
# REQ-GEN-05: Group count assertions for specific models
# ---------------------------------------------------------------------------

class TestGroupCounts:
    """Model-specific group count assertions."""

    @pytest.mark.req("REQ-GEN-05")
    def test_group_count_solar_battery(self, all_graphs):
        graph = all_graphs["solar_battery_model"]
        assert len(graph.entry_point_groups) == 3, (
            f"solar_battery: expected 3 groups, got {len(graph.entry_point_groups)}"
        )

    @pytest.mark.req("REQ-GEN-05")
    def test_group_count_catf_mfe(self, all_graphs):
        graph = all_graphs["catf_mfe_model"]
        assert len(graph.entry_point_groups) == 8, (
            f"catf_mfe: expected 8 groups, got {len(graph.entry_point_groups)}"
        )
