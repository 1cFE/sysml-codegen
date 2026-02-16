"""Unit tests for CLI generation helpers (Bug 7)."""

import pytest
from pathlib import Path


class TestEnsurePackageInitFiles:
    """Bug 7: Intermediate __init__.py creation."""

    def test_creates_init_files_in_all_intermediate_dirs(self, tmp_path):
        from sysml_codegen.cli import _ensure_package_init_files

        (tmp_path / "a" / "b" / "c").mkdir(parents=True)
        _ensure_package_init_files(tmp_path, "a/b/c")
        assert (tmp_path / "a" / "__init__.py").exists()
        assert (tmp_path / "a" / "b" / "__init__.py").exists()
        assert (tmp_path / "a" / "b" / "c" / "__init__.py").exists()

    def test_does_not_overwrite_existing_init(self, tmp_path):
        from sysml_codegen.cli import _ensure_package_init_files

        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "__init__.py").write_text("# custom\n")
        _ensure_package_init_files(tmp_path, "a")
        assert (tmp_path / "a" / "__init__.py").read_text() == "# custom\n"

    def test_uses_custom_docstring(self, tmp_path):
        from sysml_codegen.cli import _ensure_package_init_files

        (tmp_path / "x").mkdir()
        _ensure_package_init_files(tmp_path, "x", '"""Custom."""\n')
        assert (tmp_path / "x" / "__init__.py").read_text() == '"""Custom."""\n'

    def test_single_dir(self, tmp_path):
        from sysml_codegen.cli import _ensure_package_init_files

        (tmp_path / "pkg").mkdir()
        _ensure_package_init_files(tmp_path, "pkg")
        assert (tmp_path / "pkg" / "__init__.py").exists()


class TestSetupOutputDirectories:
    """Bug 7 broader scope: top-level subdirectory __init__.py creation."""

    def test_creates_init_py_in_all_subdirectories(self, tmp_path):
        from sysml_codegen.cli import _setup_output_directories, GenerationConfig

        output = tmp_path / "pkg"
        config = GenerationConfig(
            models_path=tmp_path / "models",
            output_path=output,
            package_name="pkg",
        )
        _setup_output_directories(config)

        expected_subdirs = ["schemas", "modules", "handwritten", "pipelines", "inputs", "tests"]
        for subdir in expected_subdirs:
            init_file = output / subdir / "__init__.py"
            assert init_file.exists(), f"Missing __init__.py in {subdir}/"
            assert init_file.read_text() == '"""Generated package."""\n'

    def test_does_not_create_init_py_in_output_path(self, tmp_path):
        from sysml_codegen.cli import _setup_output_directories, GenerationConfig

        output = tmp_path / "pkg"
        config = GenerationConfig(
            models_path=tmp_path / "models",
            output_path=output,
            package_name="pkg",
        )
        _setup_output_directories(config)

        assert not (output / "__init__.py").exists()

    def test_does_not_overwrite_existing_init_py(self, tmp_path):
        from sysml_codegen.cli import _setup_output_directories, GenerationConfig

        output = tmp_path / "pkg"
        (output / "schemas").mkdir(parents=True)
        (output / "schemas" / "__init__.py").write_text("# custom content\n")

        config = GenerationConfig(
            models_path=tmp_path / "models",
            output_path=output,
            package_name="pkg",
        )
        _setup_output_directories(config)

        assert (output / "schemas" / "__init__.py").read_text() == "# custom content\n"
