"""Conformance tests for Type Mapping Consolidation (X01).

Requirements: REQ-GEN-06
Design intent: 08-generation.md

Tests verify that SysML-to-Python type mapping is consistent across all
generators, using a single shared function from type_mapping.py.

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import jinja2
import pytest

from sysml_codegen.generation.type_mapping import (
    map_sysml_type_to_python,
)

from sysml_codegen.snapshot import (
    build_full_graph_from_snapshot,
)
from tests.conftest import snapshot_fixture


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SRC_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen"
TEMPLATE_DIR = SRC_DIR / "templates"

PARAMETRIZED_MODELS = [
    "solar_battery_model",
    "catf_mfe_model",
]

MODEL_IDS = {
    "solar_battery_model": "solar_battery",
    "catf_mfe_model": "catf_mfe",
}

# Generator source files that should NOT have their own type mapping copies
GENERATOR_FILES_TO_CHECK = {
    "modules": "generation/modules.py",
    "entry_point": "generation/entry_point.py",
    "schemas": "generation/schemas.py",
    "stencils": "generation/stencils.py",
    "registry": "generation/registry.py",
}


# ===========================================================================
# REQ-GEN-06: Primitive type mapping (Real, Integer, Boolean, String)
# ===========================================================================
class TestPrimitiveMapping:
    """REQ-GEN-06: SysML-to-Python type mapping for primitive types."""

    @pytest.mark.req("REQ-GEN-06")
    def test_map_real_to_float(self):
        """Real (both forms) maps to float."""
        assert map_sysml_type_to_python("Real") == "float"
        assert map_sysml_type_to_python("ScalarValues::Real") == "float"

    @pytest.mark.req("REQ-GEN-06")
    def test_map_integer_to_int(self):
        """Integer (both forms) maps to int."""
        assert map_sysml_type_to_python("Integer") == "int"
        assert map_sysml_type_to_python("ScalarValues::Integer") == "int"

    @pytest.mark.req("REQ-GEN-06")
    def test_map_boolean_to_bool(self):
        """Boolean (both forms) maps to bool."""
        assert map_sysml_type_to_python("Boolean") == "bool"
        assert map_sysml_type_to_python("ScalarValues::Boolean") == "bool"

    @pytest.mark.req("REQ-GEN-06")
    def test_map_string_to_str(self):
        """String (both forms) maps to str."""
        assert map_sysml_type_to_python("String") == "str"
        assert map_sysml_type_to_python("ScalarValues::String") == "str"

    @pytest.mark.req("REQ-GEN-06")
    def test_unknown_type_passthrough(self):
        """Unknown types pass through unchanged."""
        assert map_sysml_type_to_python("PlasmaParams") == "PlasmaParams"
        assert map_sysml_type_to_python("MyCustomType") == "MyCustomType"


# ===========================================================================
# REQ-GEN-06: No divergent copies across generators
# ===========================================================================
class TestNoDivergentCopies:
    """REQ-GEN-06: Generators must not define their own type mapping functions."""

    @pytest.mark.req("REQ-GEN-06")
    @pytest.mark.parametrize(
        "module_id,rel_path,forbidden_functions",
        [
            ("modules", "generation/modules.py", ["_map_input_type"]),
            ("entry_point", "generation/entry_point.py", ["_map_input_type"]),
            ("schemas", "generation/schemas.py", ["_map_input_type", "_map_output_type"]),
            ("stencils", "generation/stencils.py", ["_map_input_type"]),
            ("registry", "generation/registry.py", ["_map_output_type"]),
        ],
        ids=["modules", "entry_point", "schemas", "stencils", "registry"],
    )
    def test_no_divergent_copies(self, module_id, rel_path, forbidden_functions):
        """Generator file does NOT define its own type mapping function."""
        source_path = SRC_DIR / rel_path
        source = source_path.read_text()
        tree = ast.parse(source)

        # Find all function definitions in the file
        defined_functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defined_functions.add(node.name)

        for func_name in forbidden_functions:
            assert func_name not in defined_functions, (
                f"{rel_path} still defines {func_name}(). "
                f"Should use shared function from generation/type_mapping.py instead."
            )


# ===========================================================================
# REQ-GEN-06: Cross-generator consistency with real fixture data
# ===========================================================================
class TestCrossGeneratorConsistency:
    """REQ-GEN-06: All generators produce consistent types for the same SysML type."""

    @pytest.mark.req("REQ-GEN-06")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS, ids=lambda m: MODEL_IDS[m])
    def test_all_generators_use_shared_function(self, model_name, extraction_snapshots):
        """For each CalcUsage module, all type annotations are consistent
        with map_sysml_type_to_python() output for the same SysML type."""
        # NOTE (Item 6, L4): this is a weak, partly self-referential check --
        # expected = map_sysml_type_to_python(attr.sysml_type) recomputes the graph's own
        # value. Its residual value is real but narrow: it proves every generator routes
        # through the shared mapping (a divergent hardcode would fail). The actual type-map
        # CONTENT is pinned independently by the literal siblings
        # test_gen_schemas.py:359-381 and test_gen_module_wrappers.py (map literal table).
        # Kept as a consistency guard, not deleted; sibling-pinned for content.
        graph, inputs = build_full_graph_from_snapshot(snapshot_fixture(model_name))
        snap = inputs["snap"]
        calc_defs = snap["calc_defs"]

        # Build lookup: calc_def name -> calc_def
        calc_def_by_name = {cd.name: cd for cd in calc_defs}

        # For each module, verify input types are consistent with shared mapping
        for module in graph.modules:
            # Find matching calc_def (CalcUsage modules match by name)
            calc_def = calc_def_by_name.get(module.name)
            if calc_def is None:
                # FORMULA or aggregation module -- skip (no calc_def)
                continue

            # Verify input types match shared mapping
            for mod_input in module.inputs:
                # Find matching attribute in calc_def
                matching_attrs = [
                    a for a in calc_def.input_attributes
                    if a.name == mod_input.name
                ]
                if not matching_attrs:
                    continue

                attr = matching_attrs[0]
                expected_python_type = map_sysml_type_to_python(attr.sysml_type)
                assert mod_input.python_type == expected_python_type, (
                    f"Module {module.name} input {mod_input.name}: "
                    f"python_type={mod_input.python_type!r} != "
                    f"map_sysml_type_to_python({attr.sysml_type!r})={expected_python_type!r}"
                )

            # Verify output types match shared mapping
            for mod_output in module.outputs:
                matching_out_attrs = [
                    a for a in calc_def.output_attributes
                    if a.name == mod_output.name or mod_output.field_name == "root"
                ]
                if not matching_out_attrs:
                    continue

                attr = matching_out_attrs[0]
                expected_python_type = map_sysml_type_to_python(attr.sysml_type)
                assert mod_output.python_type == expected_python_type, (
                    f"Module {module.name} output {mod_output.name}: "
                    f"python_type={mod_output.python_type!r} != "
                    f"map_sysml_type_to_python({attr.sysml_type!r})={expected_python_type!r}"
                )


# ===========================================================================
# REQ-GEN-06: Shared module exists and has correct API
# ===========================================================================
class TestSharedModuleAPI:
    """REQ-GEN-06: type_mapping.py provides the expected public API."""

    @pytest.mark.req("REQ-GEN-06")
    def test_type_mapping_module_exists(self):
        """type_mapping.py module exists and is importable."""
        from sysml_codegen.generation import type_mapping
        assert hasattr(type_mapping, "map_sysml_type_to_python")

    @pytest.mark.req("REQ-GEN-06")
    def test_sysml_to_python_dict_has_8_entries(self):
        """SYSML_TO_PYTHON dict covers all 4 types × 2 forms."""
        from sysml_codegen.generation.type_mapping import SYSML_TO_PYTHON
        assert len(SYSML_TO_PYTHON) == 8
