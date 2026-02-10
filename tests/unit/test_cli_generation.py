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
