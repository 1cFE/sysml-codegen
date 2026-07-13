"""Phase 2: stdlib-only verifier + verification semantics (offline).

Proves SC-1 (tamper), SC-2 (missing + extra), SC-3 (env-compat advisory/strict) over a
hand-sealed fixture directory, plus the INV-8 half that doesn't need Step 9 — the verifier
imports nothing from sysml-codegen.
"""

from __future__ import annotations

from pathlib import Path

from sysml_codegen.contracts.seal import DEFAULT_COVERAGE_POLICY, seal_package
from sysml_codegen.contracts.serialize import write_contract_json
from sysml_codegen.contracts.verify import (
    EXTRA,
    GENERATOR_MISMATCH,
    MISSING,
    NAME_MISMATCH,
    RUNTIME_MISMATCH,
    TAMPER,
    verify_package,
    verify_package_or_raise,
)

CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "src" / "sysml_codegen" / "contracts"


def _sealed(package_dir: Path, package_name: str = "pkg") -> Path:
    """Build a tiny package directory and write a real seal (via ``seal_package``)."""
    (package_dir / "modules").mkdir(parents=True)
    (package_dir / "modules" / "calc.py").write_text("def run():\n    return 1\n")
    (package_dir / "pipelines").mkdir()
    (package_dir / "pipelines" / "p.yaml").write_text("modules: []\n")
    (package_dir / "contracts").mkdir()

    seal = seal_package(package_dir, package_name, DEFAULT_COVERAGE_POLICY)
    write_contract_json(package_dir / "contracts" / "package_contract.json", seal)
    return package_dir


def test_tamper_fails(tmp_path):
    """SC-1: a mutated covered file is a fatal TAMPER diagnostic."""
    d = _sealed(tmp_path / "pkg")
    (d / "pipelines" / "p.yaml").write_text("MUTATED")

    result = verify_package(d, "pkg")
    assert not result.ok
    assert any(x.kind == TAMPER and x.path == "pipelines/p.yaml" for x in result.diagnostics)


def test_missing_fails(tmp_path):
    """SC-2: a deleted covered file is a fatal MISSING diagnostic (closes S4's gap)."""
    d = _sealed(tmp_path / "pkg")
    (d / "modules" / "calc.py").unlink()

    result = verify_package(d, "pkg")
    assert not result.ok
    assert any(x.kind == MISSING and x.path == "modules/calc.py" for x in result.diagnostics)


def test_extra_fails(tmp_path):
    """SC-2: an unhashed policy-scoped file is a fatal EXTRA diagnostic."""
    d = _sealed(tmp_path / "pkg")
    (d / "stray.py").write_text("x = 1\n")

    result = verify_package(d, "pkg")
    assert not result.ok
    assert any(x.kind == EXTRA and x.path == "stray.py" for x in result.diagnostics)


def test_untampered_package_verifies_ok(tmp_path):
    d = _sealed(tmp_path / "pkg")
    result = verify_package(d, "pkg")
    assert result.ok
    assert result.diagnostics == []


def test_env_compat_advisory_then_strict(tmp_path):
    """SC-3: a runtime mismatch is advisory by default, fatal under strict."""
    d = _sealed(tmp_path / "pkg")

    advisory = verify_package(d, "pkg", runtime_version="99.0")
    assert advisory.ok is True
    assert any(x.kind == RUNTIME_MISMATCH for x in advisory.diagnostics)

    strict = verify_package(d, "pkg", runtime_version="99.0", strict=True)
    assert strict.ok is False


def test_env_compat_skipped_when_runtime_version_none(tmp_path):
    d = _sealed(tmp_path / "pkg")
    result = verify_package(d, "pkg", runtime_version=None)
    assert result.ok
    assert result.diagnostics == []


def test_name_mismatch_is_a_diagnostic(tmp_path):
    d = _sealed(tmp_path / "pkg", package_name="pkg")
    result = verify_package(d, "other_name")
    assert not result.ok
    assert any(x.kind == NAME_MISMATCH for x in result.diagnostics)


def test_generator_mismatch_is_a_reserved_unproducible_kind(tmp_path):
    """Item 14 W5a: GENERATOR_MISMATCH is a named, reserved diagnostic kind — no
    call path ever produces it (no caller-supplied expected generator version
    exists to compare against, unlike runtime_version), and it no longer
    participates in the `strict` fatal check (that expectation was dead)."""
    d = _sealed(tmp_path / "pkg")
    result = verify_package(d, "pkg", runtime_version=None, strict=True)
    assert result.ok
    assert not any(x.kind == GENERATOR_MISMATCH for x in result.diagnostics)


def test_verify_package_or_raise_raises_on_not_ok(tmp_path):
    d = _sealed(tmp_path / "pkg")
    (d / "modules" / "calc.py").write_text("MUTATED")

    import pytest

    with pytest.raises(RuntimeError):
        verify_package_or_raise(d, "pkg")


def test_verify_package_or_raise_passes_through_on_ok(tmp_path):
    d = _sealed(tmp_path / "pkg")
    result = verify_package_or_raise(d, "pkg")
    assert result.ok


def test_verifier_imports_nothing_from_sysml_codegen():
    """INV-8 (import scan half): verify.py is stdlib-only, no in-repo imports."""
    import ast

    tree = ast.parse((CONTRACTS_DIR / "verify.py").read_text())
    imported_modules = [
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    ] + [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module]

    assert not any(m.startswith("sysml_codegen") for m in imported_modules)
    assert not any(m.startswith("agentic_mbse") for m in imported_modules)
