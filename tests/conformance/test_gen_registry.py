"""Conformance tests for Module Registry Generator (C24).

Requirements: REQ-REG-01 through REQ-REG-07
Design intent: 20-module-registry-generation.md

Tests verify generate_registry_function() behavior with real ComputationGraph data:
- REQ-REG-01: Aggregation import paths use design-scoped EQN (module_eqn)
- REQ-REG-02: Import paths match actual filesystem paths (PythonModulePath.from_sysml)
- REQ-REG-03: Globally unique class names in module_type_override
- REQ-REG-04: Aliased imports when names collide
- REQ-REG-05: All module types use SysMLQualifiedName derivation pipeline
- REQ-REG-06: CUSTOM_SCHEMA_TYPES includes exit point primitive types
- REQ-REG-07: Collision detection and reporting before rendering

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
import logging
import re
from pathlib import Path

import jinja2
import pytest

from sysml_codegen.generation.registry import (
    _collect_exit_point_primitive_types,
    generate_registry,
)
from sysml_codegen.core.identifier_types import (
    PythonModulePath,
    SysMLQualifiedName,
)
from sysml_codegen.resolution.models import ComputationGraph

from sysml_codegen.snapshot import (
    build_classifier_inputs_from_snapshot,
    build_full_graph_from_snapshot,
)
from tests.conftest import snapshot_fixture


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"
SRC_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen"

# Models with all 3 module types (CalcUsage + FORMULA + aggregation)
ALL_TYPE_MODELS = [
    "solar_battery_model",
]

# Models for parametrized tests
PARAMETRIZED_MODELS = [
    "solar_battery_model",
    "catf_mfe_model",
    "chain_spike_model",
    "attr_expr_probe",
]

MODEL_IDS = {
    "solar_battery_model": "solar_battery",
    "catf_mfe_model": "catf_mfe",
    "chain_spike_model": "chain_spike",
    "attr_expr_probe": "attr_expr_probe",
}

# Models with no expected collisions
NO_COLLISION_MODELS = [
    "catf_mfe_model",
    "chain_spike_model",
]

NO_COLLISION_IDS = {
    "catf_mfe_model": "catf_mfe",
    "chain_spike_model": "chain_spike",
}


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def template_env():
    """Jinja2 template environment for registry generation."""
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture(scope="session")
def all_graph_data() -> dict[str, tuple[ComputationGraph, dict]]:
    """Build ComputationGraphs + inputs for all models (once per session)."""
    data = {}
    for model_name in PARAMETRIZED_MODELS:
        graph, inputs = build_full_graph_from_snapshot(snapshot_fixture(model_name))
        data[model_name] = (graph, inputs)
    return data


@pytest.fixture(scope="session")
def all_registry_codes(all_graph_data, template_env) -> dict[str, str]:
    """Generate registry code for all models (once per session)."""
    codes = {}
    for model_name, (graph, inputs) in all_graph_data.items():
        package_name = MODEL_IDS[model_name]

        exit_types = _collect_exit_point_primitive_types(graph.modules)

        code = generate_registry(
            graph=graph,
            package_name=package_name,
            template_env=template_env,
            output_path=Path("/tmp/test_registry.py"),
            exit_point_primitive_types=exit_types,
        )
        codes[model_name] = code
    return codes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_import_lines(code: str) -> list[str]:
    """Extract all 'from ... import ...' lines from generated code."""
    return [
        line.strip() for line in code.splitlines()
        if line.strip().startswith("from ")
    ]


def _extract_module_import_lines(code: str, package_name: str) -> list[str]:
    """Extract module import lines (from package.modules.*)."""
    return [
        line for line in _extract_import_lines(code)
        if f"from {package_name}.modules." in line
    ]


def _extract_class_names_from_module_type_override(code: str) -> list[str]:
    """Extract class names used as keys in module_type_override dict.

    Parses the generated code AST to find dictionary keys in the
    module_type_override keyword argument.
    """
    tree = ast.parse(code)
    class_names = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        # Look for create_registry() calls
        func = node.func
        if isinstance(func, ast.Name) and func.id == "create_registry":
            for keyword in node.keywords:
                if keyword.arg == "module_type_override":
                    # Dict node: keys are Name nodes (class names)
                    if isinstance(keyword.value, ast.Dict):
                        for key in keyword.value.keys:
                            if isinstance(key, ast.Name):
                                class_names.append(key.id)
    return class_names


def _extract_module_list_from_create_registry(code: str) -> list[str]:
    """Extract class names from the list argument to create_registry()."""
    tree = ast.parse(code)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "create_registry":
            if node.args:
                list_arg = node.args[0]
                if isinstance(list_arg, ast.List):
                    return [
                        elt.id for elt in list_arg.elts
                        if isinstance(elt, ast.Name)
                    ]
    return []


def _extract_aliased_imports(code: str) -> list[tuple[str, str]]:
    """Extract 'import X as Y' pairs from the code.

    Returns list of (original_name, alias) tuples.
    """
    tree = ast.parse(code)
    aliases = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.asname and alias.asname != alias.name:
                    aliases.append((alias.name, alias.asname))
    return aliases


# ---------------------------------------------------------------------------
# REQ-REG-01: Aggregation import paths use design-scoped EQN
# ---------------------------------------------------------------------------

class TestAggregationPathsDesignScoped:
    """REQ-REG-01: Aggregation module import paths SHALL use design-scoped EQN,
    not library QN."""

    @pytest.mark.req("REQ-REG-01")
    def test_req_reg_01_aggregation_paths_use_design_scoped_eqn(
        self, all_registry_codes, all_graph_data,
    ):
        """For solar_battery, all aggregation import paths start with
        'solarbatterydesign.solar_battery_plant.' (design scope), not
        'solarbatterylibrary' (library scope). Verify 20 aggregation imports."""
        code = all_registry_codes["solar_battery_model"]
        graph, inputs = all_graph_data["solar_battery_model"]
        snap = inputs["snap"]

        # Identify aggregation class names from fixture data
        agg_attr_names = {
            agg.expression.attribute_name
            for agg in snap["aggregation_expressions"]
        }
        assert len(agg_attr_names) > 0, "No aggregation expressions in solar_battery"

        # Find import lines whose imported class name matches an aggregation attr
        all_module_imports = _extract_module_import_lines(code, "solar_battery")
        agg_imports = []
        for line in all_module_imports:
            # Extract class name from "from X import ClassName" or "from X import C as D"
            match = re.search(r"import\s+(\w+)", line)
            if match:
                class_name = match.group(1)
                # Aggregation class names are like "capital_costModule"
                # Strip "Module" suffix and check against agg attr names
                base = class_name.replace("Module", "")
                if base in agg_attr_names:
                    agg_imports.append(line)

        assert len(agg_imports) == 20, (
            f"Expected 20 aggregation imports, got {len(agg_imports)}:\n"
            + "\n".join(agg_imports)
        )

        library_violations = [
            line for line in agg_imports
            if "solarbatterylibrary" in line
        ]
        assert not library_violations, (
            "Aggregation imports using library-scoped path (should be design-scoped):\n"
            + "\n".join(library_violations)
        )

        design_scoped = [
            line for line in agg_imports
            if "solarbatterydesign.solar_battery_plant." in line
        ]
        assert len(design_scoped) == 20, (
            f"Expected all 20 aggregation imports to be design-scoped, "
            f"got {len(design_scoped)}"
        )


# ---------------------------------------------------------------------------
# REQ-REG-02: Import paths match filesystem paths
# ---------------------------------------------------------------------------

class TestImportPathsMatchFilesystem:
    """REQ-REG-02: Import paths in registry SHALL match actual filesystem paths
    generated by CLI (i.e., match PythonModulePath.from_sysml())."""

    @pytest.mark.req("REQ-REG-02")
    @pytest.mark.parametrize("model_name", ["solar_battery_model", "catf_mfe_model"],
                             ids=["solar_battery", "catf_mfe"])
    def test_req_reg_02_import_paths_match_filesystem(self, model_name, tmp_path):
        """Every registry module import points at a file a real generation wrote to disk.

        Re-anchored from a weak "each dotted segment is alphanumeric" syntactic check
        (which never touched the filesystem) to on-disk truth: generate the model from
        its committed snapshot -- license-free -- and assert each
        ``from pkg.modules.A.B.C import Name`` has a matching ``output/modules/A/B/C.py``.

        provenance: the on-disk files ARE the anchor -- produced by run_codegen from the
        committed extraction snapshot (the from-snapshot generation harness, cf.
        tests/integration/test_full_pipeline.py generation tests).
        """
        from sysml_codegen.cli import GenerationConfig, run_codegen

        package_name = MODEL_IDS[model_name]
        output = tmp_path / "out"
        generated = run_codegen(GenerationConfig(
            output_path=output,
            from_snapshot=snapshot_fixture(model_name),
            package_name=package_name,
            overwrite=True,
        ))
        assert generated is True, f"generation failed for {model_name}"

        code = (output / "__init__.py").read_text()
        module_imports = _extract_module_import_lines(code, package_name)
        assert len(module_imports) > 0, f"No module imports in {model_name}"

        missing = []
        for line in module_imports:
            # "from pkg.modules.A.B.C import Name" -> modules/A/B/C.py must exist.
            match = re.match(
                rf"from {re.escape(package_name)}\.modules\.(\S+) import \S+",
                line,
            )
            if not match:
                continue
            rel = match.group(1).replace(".", "/") + ".py"
            if not (output / "modules" / rel).exists():
                missing.append(f"  {line.strip()} -> modules/{rel} (no file on disk)")

        assert not missing, (
            f"Registry imports with no file on disk in {model_name}:\n"
            + "\n".join(missing)
        )

    @pytest.mark.req("REQ-REG-02")
    @pytest.mark.parametrize("model_name", ["solar_battery_model", "catf_mfe_model"],
                             ids=["solar_battery", "catf_mfe"])
    def test_module_count_matches_inputs(
        self, model_name, all_registry_codes, all_graph_data,
    ):
        """Number of modules in registry matches the number of distinct
        classes from graph modules: unique CalcUsage calc_defs + FORMULA + aggregations.
        (Registry registers classes, not pipeline instances.)"""
        code = all_registry_codes[model_name]
        graph, _inputs = all_graph_data[model_name]

        module_list = _extract_module_list_from_create_registry(code)

        # Count expected from graph: unique calc_def_names per module type
        unique_calcusage = {
            m.calc_def_name for m in graph.modules
            if not m.is_computed_attribute and not m.is_aggregation
        }
        formula_count = sum(1 for m in graph.modules if m.is_computed_attribute)
        agg_count = sum(1 for m in graph.modules if m.is_aggregation)

        expected = len(unique_calcusage) + formula_count + agg_count
        assert len(module_list) == expected, (
            f"Registry has {len(module_list)} modules but expected {expected} "
            f"(calc_defs={len(unique_calcusage)}, FORMULA={formula_count}, "
            f"agg={agg_count}) in {model_name}"
        )


# ---------------------------------------------------------------------------
# REQ-REG-03: Globally unique class names
# ---------------------------------------------------------------------------

class TestGloballyUniqueClassNames:
    """REQ-REG-03: Class names in module_type_override dict SHALL be
    globally unique."""

    @pytest.mark.req("REQ-REG-03")
    @pytest.mark.parametrize("model_name", ["solar_battery_model", "catf_mfe_model"],
                             ids=["solar_battery", "catf_mfe"])
    def test_req_reg_03_globally_unique_class_names(
        self, model_name, all_registry_codes,
    ):
        """Parse generated code, extract all class names from module_type_override
        dict. Assert len(unique_names) == len(all_names) -- no duplicate keys."""
        code = all_registry_codes[model_name]

        all_names = _extract_class_names_from_module_type_override(code)
        unique_names = set(all_names)

        assert len(unique_names) == len(all_names), (
            f"Duplicate class names in module_type_override for {model_name}: "
            f"{len(all_names)} total, {len(unique_names)} unique. "
            f"Duplicates: {[n for n in all_names if all_names.count(n) > 1]}"
        )

    @pytest.mark.req("REQ-REG-03")
    @pytest.mark.parametrize("model_name", NO_COLLISION_MODELS,
                             ids=[NO_COLLISION_IDS[m] for m in NO_COLLISION_MODELS])
    def test_no_collisions_model(self, model_name, all_registry_codes):
        """Models with no collisions should have zero aliased imports."""
        code = all_registry_codes[model_name]
        package_name = MODEL_IDS[model_name]

        aliased = _extract_aliased_imports(code)
        # Filter to module imports only (not schema re-exports like "X as X")
        real_aliases = [
            (orig, alias) for orig, alias in aliased
            if orig != alias
        ]

        assert len(real_aliases) == 0, (
            f"Unexpected aliased imports in {model_name} (no collisions expected): "
            + str(real_aliases)
        )


# ---------------------------------------------------------------------------
# REQ-REG-04: Aliased imports for collisions
# ---------------------------------------------------------------------------

class TestAliasedImportsForCollisions:
    """REQ-REG-04: When class names collide, registry SHALL use aliased
    imports (import X as Assembly_X)."""

    @pytest.mark.req("REQ-REG-04")
    def test_req_reg_04_aliased_imports_for_collisions(
        self, all_registry_codes, all_graph_data,
    ):
        """For solar_battery, verify aggregation modules with colliding element
        names get aliased imports. Check that 'import X as Alias' appears for
        each collision. Verify the alias includes the assembly name prefix."""
        code = all_registry_codes["solar_battery_model"]
        _, inputs = all_graph_data["solar_battery_model"]
        snap = inputs["snap"]

        aliased = _extract_aliased_imports(code)
        # Filter out schema re-exports (X as X)
        real_aliases = [
            (orig, alias) for orig, alias in aliased
            if orig != alias
        ]

        # 5 element names x 4 assemblies = 20 aggregation modules, all collide
        # Each needs an alias since there are 4 modules per element name
        assert len(real_aliases) >= 20, (
            f"Expected at least 20 aliased imports for solar_battery aggregation "
            f"collisions, got {len(real_aliases)}: {real_aliases}"
        )

        # Get actual assembly names from fixture data (parent segments of module_eqn)
        assembly_segments = set()
        for agg in snap["aggregation_expressions"]:
            # module_eqn: "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost"
            # parent segment is segments[-2] (the assembly name)
            eqn_segments = agg.module_eqn.split("__")
            if len(eqn_segments) >= 2:
                assembly_segments.add(eqn_segments[-2])

        assert len(assembly_segments) > 0, "No assembly segments found"

        for orig, alias in real_aliases:
            # Check that the alias contains some assembly identifier (PascalCased)
            alias_lower = alias.lower()
            has_assembly = any(
                asm.replace("_", "") in alias_lower.replace("_", "")
                for asm in assembly_segments
            )
            assert has_assembly, (
                f"Alias '{alias}' for '{orig}' does not contain an assembly name "
                f"prefix from {sorted(assembly_segments)}"
            )


# ---------------------------------------------------------------------------
# REQ-REG-05: All module types use SysMLQualifiedName derivation pipeline
# ---------------------------------------------------------------------------

class TestAllTypesUseSQNDerivation:
    """REQ-REG-05: CalcUsage, computed attribute, and aggregation modules
    SHALL all derive paths from the same QN derivation pipeline."""

    @pytest.mark.req("REQ-REG-05")
    @pytest.mark.parametrize("model_name", ["solar_battery_model", "attr_expr_probe"],
                             ids=["solar_battery", "attr_expr_probe"])
    def test_req_reg_05_all_types_use_sqn_derivation(
        self, model_name, all_registry_codes, all_graph_data,
    ):
        """For each module import, verify import path is derivable from
        SysMLQualifiedName -> PythonModulePath.from_sysml(). No ad-hoc
        path construction."""
        code = all_registry_codes[model_name]
        package_name = MODEL_IDS[model_name]
        graph, inputs = all_graph_data[model_name]
        snap = inputs["snap"]

        module_imports = _extract_module_import_lines(code, package_name)
        assert len(module_imports) > 0, f"No module imports found in {model_name}"

        # Build expected import paths for all three module types
        expected_paths = set()

        # CalcUsage: derive from calc_def.qualified_name
        for cd in snap["calc_defs"]:
            sqn = SysMLQualifiedName(cd.qualified_name)
            python_path = PythonModulePath.from_sysml(sqn)
            expected_paths.add(python_path.import_path)

        # FORMULA: derive from owning_part_qualified_name::name
        from sysml_codegen.extraction.data_models import ComputedAttributeClassification
        from sysml_codegen.extraction.expression_compiler import Compilability
        for ca in snap["computed_attributes"]:
            if (
                ca.classification == ComputedAttributeClassification.FORMULA
                and ca.compilability == Compilability.FULLY_COMPILABLE
            ):
                sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
                sqn = SysMLQualifiedName(sysml_qn)
                python_path = PythonModulePath.from_sysml(sqn)
                expected_paths.add(python_path.import_path)

        # Aggregation: derive from module_eqn (design-scoped)
        for agg in snap["aggregation_expressions"]:
            sysml_qn = agg.module_eqn.replace("__", "::")
            sqn = SysMLQualifiedName(sysml_qn)
            python_path = PythonModulePath.from_sysml(sqn)
            expected_paths.add(python_path.import_path)

        # Verify each import references a known path
        failures = []
        for line in module_imports:
            match = re.match(
                rf"from {re.escape(package_name)}\.modules\.(\S+) import",
                line,
            )
            if not match:
                continue
            actual_path = match.group(1)
            if actual_path not in expected_paths:
                failures.append(
                    f"  Import path '{actual_path}' not in expected SQN-derived paths"
                )

        assert not failures, (
            f"Non-SQN-derived import paths in {model_name}:\n"
            + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-REG-06: CUSTOM_SCHEMA_TYPES includes exit point primitive types
# ---------------------------------------------------------------------------

class TestCustomSchemaTypesIncludesExitPrimitives:
    """REQ-REG-06: CUSTOM_SCHEMA_TYPES SHALL include all exit point primitive
    types used by any module."""

    @pytest.mark.req("REQ-REG-06")
    @pytest.mark.parametrize("model_name", ["solar_battery_model", "catf_mfe_model"],
                             ids=["solar_battery", "catf_mfe"])
    def test_req_reg_06_custom_schema_types_includes_exit_primitives(
        self, model_name, all_registry_codes, all_graph_data,
    ):
        """Verify CUSTOM_SCHEMA_TYPES includes Float (used by single-output
        modules) and any other primitive types."""
        code = all_registry_codes[model_name]
        graph, _ = all_graph_data[model_name]

        # Get expected exit point types from graph
        exit_types = _collect_exit_point_primitive_types(graph.modules)

        # Parse CUSTOM_SCHEMA_TYPES from generated code
        tree = ast.parse(code)
        custom_types = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "CUSTOM_SCHEMA_TYPES":
                        if isinstance(node.value, ast.List):
                            custom_types = [
                                elt.id for elt in node.value.elts
                                if isinstance(elt, ast.Name)
                            ]

        for et in exit_types:
            assert et in custom_types, (
                f"Exit point type '{et}' not in CUSTOM_SCHEMA_TYPES for {model_name}. "
                f"CUSTOM_SCHEMA_TYPES={custom_types}"
            )

    @pytest.mark.req("REQ-REG-06")
    @pytest.mark.parametrize("model_name", ["solar_battery_model", "catf_mfe_model"],
                             ids=["solar_battery", "catf_mfe"])
    def test_schema_imports_match_entry_point_groups(
        self, model_name, all_registry_codes, all_graph_data,
    ):
        """Number of schema imports matches len(graph.entry_point_groups)."""
        code = all_registry_codes[model_name]
        graph, _ = all_graph_data[model_name]
        package_name = MODEL_IDS[model_name]

        schema_imports = [
            line for line in _extract_import_lines(code)
            if f"from {package_name}.schemas." in line
        ]

        assert len(schema_imports) == len(graph.entry_point_groups), (
            f"Schema imports ({len(schema_imports)}) != entry_point_groups "
            f"({len(graph.entry_point_groups)}) in {model_name}"
        )


# ---------------------------------------------------------------------------
# REQ-REG-07: Collision detection before rendering
# ---------------------------------------------------------------------------

class TestCollisionDetectionBeforeRendering:
    """REQ-REG-07: Registry generation SHALL detect and report name
    collisions before rendering."""

    @pytest.mark.req("REQ-REG-07")
    def test_req_reg_07_collision_detection_before_rendering(
        self, all_graph_data, template_env,
    ):
        """Call the registry generator for solar_battery, verify it detects
        the 5 colliding class names and reports them (via warning or return
        value) before template rendering."""
        graph, inputs = all_graph_data["solar_battery_model"]
        snap = inputs["snap"]

        exit_types = _collect_exit_point_primitive_types(graph.modules)

        # Capture log records from the registry module
        logger = logging.getLogger("sysml_codegen.generation.registry")
        records: list[logging.LogRecord] = []
        handler = logging.Handler()
        handler.emit = lambda record: records.append(record)
        logger.addHandler(handler)
        old_level = logger.level
        logger.setLevel(logging.DEBUG)

        try:
            code = generate_registry(
                graph=graph,
                package_name="solar_battery",
                template_env=template_env,
                output_path=Path("/tmp/test_registry.py"),
                exit_point_primitive_types=exit_types,
            )
        finally:
            logger.removeHandler(handler)
            logger.setLevel(old_level)

        # Check that collision warning was emitted
        collision_warnings = [
            r for r in records
            if r.levelno >= logging.WARNING
            and ("collision" in r.getMessage().lower()
                 or "duplicate" in r.getMessage().lower()
                 or "alias" in r.getMessage().lower())
        ]
        assert len(collision_warnings) > 0, (
            "No collision warning emitted for solar_battery (expected 5 colliding names). "
            f"Log records: {[r.getMessage() for r in records]}"
        )


# ---------------------------------------------------------------------------
# Structural: Generated code is valid Python
# ---------------------------------------------------------------------------

class TestGeneratedCodeValidPython:
    """Every generated registry passes ast.parse()."""

    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_generated_code_valid_python(self, model_name, all_registry_codes):
        """Parse generated code with ast.parse()."""
        code = all_registry_codes[model_name]
        try:
            ast.parse(code)
        except SyntaxError as e:
            pytest.fail(
                f"Generated registry for {model_name} is not valid Python: {e}\n"
                f"Code:\n{code}"
            )


# ---------------------------------------------------------------------------
# Cross-reference: graph_builder module_type mismatch documented
# ---------------------------------------------------------------------------

class TestGraphBuilderModuleTypeConsistency:
    """Static analysis: verify graph_builder.py uses module_eqn (design-scoped)
    for aggregation module_type, consistent with registry.py (Bug 8a fix)."""

    @pytest.mark.req("REQ-REG-01")
    def test_graph_builder_uses_module_eqn_for_aggregation_module_type(self):
        """graph_builder.py uses agg.module_eqn.replace('__', '::') for
        aggregation module_type derivation — matching registry.py's
        design-scoped derivation (Bug 8a remainder fix, 7.5a)."""
        graph_builder_path = SRC_DIR / "resolution" / "graph_builder.py"
        source = graph_builder_path.read_text()

        # owning_part_qn must NOT appear in derive_module_type() context
        assert 'agg.expression.owning_part_qn' not in source or \
            'derive_module_type' not in source[
                max(0, source.find('agg.expression.owning_part_qn') - 200):
                source.find('agg.expression.owning_part_qn') + 100
            ] if 'agg.expression.owning_part_qn' in source else True, (
            "graph_builder.py still uses owning_part_qn near derive_module_type()"
        )

        # module_eqn.replace MUST appear in derive_module_type() context
        assert 'module_eqn.replace("__", "::")' in source, (
            "graph_builder.py should use module_eqn.replace('__', '::') "
            "for aggregation module_type derivation"
        )
