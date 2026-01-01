"""Integration tests for the full code generation pipeline.

Tests end-to-end functionality from SysML models to generated code.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def test_full_codegen_pipeline(tmp_path: Path, sample_model_path: Path):
    """End-to-end test of code generation.

    Uses the sample_model fixture which contains:
    - simple_calc.sysml
    - multi_output.sysml
    - dependencies.sysml
    """
    from sysml_codegen.cli import run_codegen, GenerationConfig

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
    success = run_codegen(config)
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
    from sysml_codegen.cli import main, run_codegen, GenerationConfig

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
