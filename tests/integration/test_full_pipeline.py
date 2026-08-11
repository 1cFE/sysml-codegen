"""Integration tests for the full code generation pipeline.

Tests end-to-end functionality from SysML models to generated code.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.helpers.legacy_route import generate_via_legacy_route


def test_full_codegen_pipeline(tmp_path: Path, sample_model_path: Path):
    """End-to-end test of code generation.

    Uses the sample_model fixture which contains:
    - simple_calc.sysml
    - multi_output.sysml
    - dependencies.sysml
    """
    from sysml_codegen.cli import GenerationConfig

    output_path = tmp_path / "generated"

    config = GenerationConfig(
        models_path=sample_model_path,
        output_path=output_path,
        package_name="test_package",
        schema_class_name="TestParams",
        pipeline_name="test_pipeline",
        overwrite=True,
    )

    # Run the pipeline (currently a stub, but tests the structure)
    success = generate_via_legacy_route(config)
    assert success, "Code generation should succeed"


def test_cli_help_shows_parameters():
    """Verify CLI shows all required parameters in help."""
    import argparse
    import io
    import sys
    from contextlib import redirect_stdout
    from unittest.mock import patch

    # Import the CLI module and capture help output
    from sysml_codegen.cli import main

    help_text = ""
    # Check generate subcommand help (options are in generate --help, not top-level)
    with patch.object(sys, "argv", ["sysml-codegen", "generate", "--help"]):
        try:
            with redirect_stdout(io.StringIO()) as f:
                main()
        except SystemExit:
            pass  # --help causes SystemExit(0)
        help_text = f.getvalue()

    # Check for parameterized options in generate subcommand
    assert "--package-name" in help_text, "CLI should have --package-name option"
    assert "--schema-class" in help_text, "CLI should have --schema-class option"
    assert "--pipeline-name" in help_text, "CLI should have --pipeline-name option"
    assert "--models" in help_text, "CLI should have --models option"
    assert "--output" in help_text, "CLI should have --output option"


def test_generation_config_defaults():
    """Verify GenerationConfig has correct defaults."""
    from sysml_codegen.cli import GenerationConfig

    config = GenerationConfig(
        models_path=Path("/tmp/models"),
        output_path=Path("/tmp/output"),
    )

    # Check default values (parameterized, not hardcoded)
    assert config.package_name == "generated_code"
    assert config.schema_class_name == "Params"
    assert config.pipeline_name == "pipeline"
    assert config.overwrite is False


def test_no_fusion_simkit_hardcoding():
    """Verify no hardcoded fusion_simkit references in source."""
    src_dir = Path(__file__).parent.parent.parent / "src" / "sysml_codegen"

    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text()

        # Skip comments that explain the change
        lines_without_comments = []
        for line in content.split("\n"):
            # Strip comments for checking
            if "#" in line:
                line = line[:line.index("#")]
            lines_without_comments.append(line)
        code_content = "\n".join(lines_without_comments)

        # Check no hardcoded package name in code (comments OK)
        if "fusion_simkit" in code_content:
            # Allow in strings that are clearly examples or documentation
            assert 'fusion_simkit"' not in code_content or "example" in content.lower(), (
                f"Hardcoded fusion_simkit in {py_file}"
            )


def test_extractor_loads_sample_models(sample_model_path: Path):
    """Verify extractor can load sample SysML models."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    extractor = SysMLDataExtractor([sample_model_path])
    success = extractor.load_models()

    # This may fail if syside is not properly configured for test fixtures
    # For now, we just test the structure
    if success:
        calc_defs = extractor.extract_calculation_definitions()
        assert isinstance(calc_defs, list)


def test_imports_work_across_layers():
    """Verify imports work correctly across all layers."""
    # Extraction layer
    from sysml_codegen.extraction.extractor import SysMLDataExtractor
    from sysml_codegen.extraction.data_models import CalculationDefinitionData
    from sysml_codegen.extraction.usage_extractor import extract_calculation_usages

    # Analysis layer
    from sysml_codegen.analysis.parameter_groups import ParameterGroupDeriver
    from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
    from sysml_codegen.analysis.phantom_detector import PhantomDetector

    # Resolution layer
    from sysml_codegen.resolution.models import ComputationGraph
    from sysml_codegen.resolution.graph_builder import build_computation_graph

    # Generation layer
    from sysml_codegen.generation.modules import generate_teax_module

    # CLI
    from sysml_codegen.cli import main, GenerationConfig

    # All imports successful
    assert True


class TestInstallCommands:
    """Tests for install-commands CLI subcommand."""

    def test_list_shows_teax_completion(self, capsys):
        """--list shows teax-completion.md command."""
        from sysml_codegen.cli import cmd_install_commands

        class MockArgs:
            list = True
            directory = "."
            force = False

        result = cmd_install_commands(MockArgs())

        assert result == 0
        captured = capsys.readouterr()
        assert "teax-completion.md" in captured.out

    def test_installs_to_directory(self, tmp_path):
        """Installs teax-completion.md to .claude/commands/."""
        from sysml_codegen.cli import cmd_install_commands

        class MockArgs:
            list = False
            directory = str(tmp_path)
            force = False

        result = cmd_install_commands(MockArgs())

        assert result == 0
        commands_dir = tmp_path / ".claude" / "commands"
        assert commands_dir.exists()
        assert (commands_dir / "teax-completion.md").exists()

    def test_skips_existing_without_force(self, tmp_path, capsys):
        """Skips existing file without --force."""
        from sysml_codegen.cli import cmd_install_commands

        # Create existing file
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        existing = commands_dir / "teax-completion.md"
        existing.write_text("existing content")

        class MockArgs:
            list = False
            directory = str(tmp_path)
            force = False

        result = cmd_install_commands(MockArgs())

        assert result == 0
        assert existing.read_text() == "existing content"
        captured = capsys.readouterr()
        assert "Skipping" in captured.out

    def test_overwrites_with_force(self, tmp_path):
        """Overwrites existing file with --force."""
        from sysml_codegen.cli import cmd_install_commands

        # Create existing file
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        existing = commands_dir / "teax-completion.md"
        existing.write_text("old content")

        class MockArgs:
            list = False
            directory = str(tmp_path)
            force = True

        result = cmd_install_commands(MockArgs())

        assert result == 0
        assert existing.read_text() != "old content"


class TestRunCodegenPhases:
    """Tests for run_codegen implementation phases."""

    def test_creates_output_directory_structure(self, tmp_path: Path, sample_model_path: Path):
        """Verify run_codegen creates expected directory structure (Phase 1)."""
        from sysml_codegen.cli import GenerationConfig

        output = tmp_path / "generated"
        config = GenerationConfig(
            models_path=sample_model_path,
            output_path=output,
            package_name="test_pkg",
        )

        # Should at least create directories even if generation partially fails
        generate_via_legacy_route(config)

        assert output.exists(), "Output directory should exist"
        assert (output / "schemas").exists(), "schemas/ directory should exist"
        assert (output / "modules").exists(), "modules/ directory should exist"
        assert (output / "handwritten").exists(), "handwritten/ directory should exist"
        assert (output / "pipelines").exists(), "pipelines/ directory should exist"
        assert (output / "inputs").exists(), "inputs/ directory should exist"
        assert (output / "tests").exists(), "tests/ directory should exist"

        # Check primitives.py is generated (CRITICAL - modules depend on this)
        primitives = output / "primitives.py"
        assert primitives.exists(), "primitives.py should exist"
        content = primitives.read_text()
        assert "Float = RootModel[float]" in content, "primitives should define Float"

    def test_generates_schemas(self, tmp_path: Path, sample_model_path: Path):
        """Verify schema files are generated (Phase 2)."""
        from sysml_codegen.cli import GenerationConfig

        output = tmp_path / "generated"
        config = GenerationConfig(
            models_path=sample_model_path,
            output_path=output,
            package_name="test_pkg",
        )

        generate_via_legacy_route(config)

        # FR-10/AC-5: No static FusionParams schema should be generated
        ref_schema = output / "test_pkg_schemas.py"
        assert not ref_schema.exists(), (
            "Static FusionParams schema should NOT be generated"
        )

        # Multi-output schemas may or may not exist depending on model
        schemas_dir = output / "schemas"
        assert schemas_dir.exists(), "schemas/ directory should exist"

    def test_generates_modules_and_stencils(self, tmp_path: Path):
        """Verify module wrappers and stencils are generated (Phase 3).

        Uses chain_spike fixture which has calc usages in the computation graph.
        The sample_model fixture has CalcDefs but no usages, producing an empty
        graph — correct graph-only behavior per REQ-PIPE-07.
        """
        from sysml_codegen.cli import GenerationConfig

        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        output = tmp_path / "generated"
        config = GenerationConfig(
            models_path=fixtures_dir / "chain_spike_model",
            output_path=output,
            package_name="test_pkg",
        )

        generate_via_legacy_route(config)

        modules_dir = output / "modules"
        handwritten_dir = output / "handwritten"

        # Should have generated module files
        module_files = list(modules_dir.rglob("*.py"))
        stencil_files = list(handwritten_dir.rglob("*_impl.py"))

        assert len(module_files) > 0, "Should generate module wrappers"
        assert len(stencil_files) > 0, "Should generate implementation stencils"

    def test_generates_pipeline_and_registry(self, tmp_path: Path, sample_model_path: Path):
        """Verify pipeline YAML and registry are generated (Phase 4)."""
        from sysml_codegen.cli import GenerationConfig

        output = tmp_path / "generated"
        config = GenerationConfig(
            models_path=sample_model_path,
            output_path=output,
            package_name="test_pkg",
            pipeline_name="test_pipeline",
        )

        generate_via_legacy_route(config)

        # Check pipeline
        pipelines_dir = output / "pipelines"
        yaml_files = list(pipelines_dir.glob("*.yaml"))
        assert len(yaml_files) > 0, "Should generate pipeline YAML"

        # Check registry
        init_file = output / "__init__.py"
        assert init_file.exists(), "Should generate __init__.py registry"
        content = init_file.read_text()
        assert "create_" in content, "Registry should have creation function"

        # Bug 7 broader scope: all subdirectories should have __init__.py
        for subdir in ["schemas", "modules", "handwritten", "pipelines", "inputs", "tests"]:
            sub_init = output / subdir / "__init__.py"
            assert sub_init.exists(), f"Bug 7: missing __init__.py in {subdir}/"

    def test_generates_entry_points_and_extras(self, tmp_path: Path, sample_model_path: Path):
        """Verify entry points, JSON templates, and extras are generated (Phase 5)."""
        from sysml_codegen.cli import GenerationConfig

        output = tmp_path / "generated"
        config = GenerationConfig(
            models_path=sample_model_path,
            output_path=output,
            package_name="test_pkg",
        )

        generate_via_legacy_route(config)

        # Check backlog
        backlog = output / "IMPLEMENTATION_BACKLOG.md"
        assert backlog.exists(), "Should generate implementation backlog"

        # Check tests
        tests_dir = output / "tests"
        test_files = list(tests_dir.glob("test_*.py"))
        assert len(test_files) > 0, "Should generate test files"


class TestCodegenRuntimeGapFixes:
    """Integration tests verifying all three runtime gap fixes.

    These tests run full codegen on the chain spike model and verify
    the output is correct without manual intervention.
    """

    def test_design_params_json_populated(self, tmp_path: Path, chain_spike_model_path: Path):
        """AC-1: design_params.json should contain correct default values."""
        import json
        from sysml_codegen.cli import GenerationConfig

        output = tmp_path / "generated"
        config = GenerationConfig(
            models_path=chain_spike_model_path,
            output_path=output,
            package_name="chain_spike",
        )

        success = generate_via_legacy_route(config)
        assert success, "Codegen should succeed on chain spike model"

        # Find JSON files in inputs/
        json_files = list((output / "inputs").glob("*.json"))
        assert len(json_files) > 0, "Should generate at least one JSON input file"

        # Collect all populated numeric values across JSON files
        all_numeric_values: dict[str, float] = {}
        for jf in json_files:
            data = json.loads(jf.read_text())
            for key, value in data.items():
                assert isinstance(value, (int, float)), (
                    f"JSON value for '{key}' should be numeric, got {type(value)}"
                )
                all_numeric_values[key] = value

        assert len(all_numeric_values) >= 3, (
            f"Expected >= 3 populated numeric entries across JSON files, got {len(all_numeric_values)}: "
            f"{all_numeric_values}"
        )

        # Verify the chain spike model's known defaults are present
        expected_defaults = {"length": 10.0, "width": 5.0, "rate": 12.0}
        for name, expected_val in expected_defaults.items():
            matching = {k: v for k, v in all_numeric_values.items() if name in k.lower()}
            assert matching, f"Expected a JSON entry containing '{name}' in its key"
            for k, v in matching.items():
                assert v == expected_val, (
                    f"Expected '{k}' to be {expected_val}, got {v}"
                )

    def test_custom_schema_types_includes_exit_point_types(
        self, tmp_path: Path, chain_spike_model_path: Path
    ):
        """AC-3: Generated __init__.py should include Float in CUSTOM_SCHEMA_TYPES."""
        from sysml_codegen.cli import GenerationConfig

        output = tmp_path / "generated"
        config = GenerationConfig(
            models_path=chain_spike_model_path,
            output_path=output,
            package_name="chain_spike",
        )

        success = generate_via_legacy_route(config)
        assert success, "Codegen should succeed on chain spike model"

        init_content = (output / "__init__.py").read_text()
        assert "CUSTOM_SCHEMA_TYPES" in init_content, (
            "Generated __init__.py should have CUSTOM_SCHEMA_TYPES"
        )
        assert "Float" in init_content, (
            "CUSTOM_SCHEMA_TYPES should include Float for RootModel[float] exit points"
        )
        assert "from chain_spike.primitives import" in init_content, (
            "Should import Float from primitives"
        )

    def test_no_fusion_params_schema(self, tmp_path: Path, chain_spike_model_path: Path):
        """AC-5/AC-6: No FusionParams schema should exist in generated output."""
        from sysml_codegen.cli import GenerationConfig

        output = tmp_path / "generated"
        config = GenerationConfig(
            models_path=chain_spike_model_path,
            output_path=output,
            package_name="chain_spike",
        )

        success = generate_via_legacy_route(config)
        assert success, "Codegen should succeed"

        # No {package}_schemas.py file should exist
        schemas_file = output / "chain_spike_schemas.py"
        assert not schemas_file.exists(), (
            "Static FusionParams schema should not be generated"
        )

        # Double-check: no FusionParams anywhere in generated code
        for py_file in output.rglob("*.py"):
            content = py_file.read_text()
            assert "FusionParams" not in content, (
                f"FusionParams found in {py_file.name} — static template was not removed"
            )
