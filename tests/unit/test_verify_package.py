"""Phase 2: stdlib-only verifier + verification semantics (offline).

Proves SC-1 (tamper), SC-2 (missing + extra), SC-3 (env-compat advisory/strict) over a
hand-sealed fixture directory, plus the INV-8 half that doesn't need Step 9 — the verifier
imports nothing from sysml-codegen.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sysml_codegen.contracts.seal import DEFAULT_COVERAGE_POLICY, seal_package
from sysml_codegen.contracts.serialize import write_contract_json
from sysml_codegen.contracts.verify import (
    ARTIFACT_UNREADABLE,
    EXTRA,
    GENERATOR_MISMATCH,
    INVALID_PATH,
    MISSING,
    NAME_MISMATCH,
    RUNTIME_MISMATCH,
    SEAL_MALFORMED,
    SEAL_MISSING,
    SEAL_UNREADABLE,
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


def _mutate_seal(package_dir: Path, mutate) -> None:
    seal_path = package_dir / "contracts" / "package_contract.json"
    seal = json.loads(seal_path.read_text())
    mutate(seal)
    seal_path.write_text(json.dumps(seal))


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


def test_missing_seal_returns_diagnostic(tmp_path):
    package_dir = tmp_path / "pkg"
    package_dir.mkdir()
    result = verify_package(package_dir, "pkg")
    assert result.ok is False
    assert [diagnostic.kind for diagnostic in result.diagnostics] == [SEAL_MISSING]


def test_unreadable_seal_returns_diagnostic(tmp_path, monkeypatch):
    d = _sealed(tmp_path / "pkg")
    original_read_text = Path.read_text

    def _deny_seal(path, *args, **kwargs):
        if path.name == "package_contract.json":
            raise PermissionError("permission denied")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", _deny_seal)
    result = verify_package(d, "pkg")
    assert result.ok is False
    assert [diagnostic.kind for diagnostic in result.diagnostics] == [SEAL_UNREADABLE]
    assert "permission denied" in result.diagnostics[0].message


def test_invalid_json_seal_returns_malformed_diagnostic(tmp_path):
    d = _sealed(tmp_path / "pkg")
    (d / "contracts" / "package_contract.json").write_text("{not json")
    result = verify_package(d, "pkg")
    assert result.ok is False
    assert [diagnostic.kind for diagnostic in result.diagnostics] == [SEAL_MALFORMED]


def test_non_object_seal_returns_malformed_diagnostic(tmp_path):
    d = _sealed(tmp_path / "pkg")
    (d / "contracts" / "package_contract.json").write_text("[]")
    result = verify_package(d, "pkg")
    assert result.ok is False
    assert [diagnostic.kind for diagnostic in result.diagnostics] == [SEAL_MALFORMED]


def test_missing_or_wrong_typed_seal_keys_return_malformed_diagnostic(tmp_path):
    for mutate in (
        lambda seal: seal.pop("artifact_hashes"),
        lambda seal: seal.__setitem__("coverage_policy", []),
    ):
        d = _sealed(tmp_path / f"pkg-{len(list(tmp_path.iterdir()))}")
        seal_path = d / "contracts" / "package_contract.json"
        seal = json.loads(seal_path.read_text())
        mutate(seal)
        seal_path.write_text(json.dumps(seal))
        result = verify_package(d, "pkg")
        assert result.ok is False
        assert [diagnostic.kind for diagnostic in result.diagnostics] == [SEAL_MALFORMED]


def test_digest_and_executable_fingerprint_syntax_are_validated(tmp_path):
    for field in ("artifact", "fingerprint"):
        d = _sealed(tmp_path / field)
        if field == "artifact":
            _mutate_seal(
                d, lambda seal: seal["artifact_hashes"].__setitem__("modules/calc.py", "x")
            )
        else:
            _mutate_seal(d, lambda seal: seal.__setitem__("executable_fingerprint", "x"))
        result = verify_package(d, "pkg")
        assert result.ok is False
        assert [diagnostic.kind for diagnostic in result.diagnostics] == [SEAL_MALFORMED]


def test_executable_fingerprint_is_recomputed(tmp_path):
    d = _sealed(tmp_path / "pkg")
    _mutate_seal(
        d,
        lambda seal: seal.__setitem__(
            "executable_fingerprint", hashlib.sha256(b"wrong").hexdigest()
        ),
    )
    result = verify_package(d, "pkg")
    assert result.ok is False
    assert [diagnostic.kind for diagnostic in result.diagnostics] == [TAMPER]
    assert "executable_fingerprint" in result.diagnostics[0].message


@pytest.mark.parametrize(
    "hostile_path", ["../outside", "/tmp/outside", "modules/../modules/calc.py", "modules//calc.py"]
)
def test_noncanonical_or_escaping_artifact_paths_are_rejected(tmp_path, hostile_path):
    d = _sealed(tmp_path / "pkg")
    _mutate_seal(
        d,
        lambda seal: seal["artifact_hashes"].__setitem__(
            hostile_path, hashlib.sha256(b"outside").hexdigest()
        ),
    )
    result = verify_package(d, "pkg")
    assert result.ok is False
    assert [diagnostic.kind for diagnostic in result.diagnostics] == [SEAL_MALFORMED]


def test_recorded_symlink_cannot_escape_package(tmp_path):
    outside = tmp_path / "outside"
    outside.write_text("outside")
    d = _sealed(tmp_path / "pkg")
    (d / "escape").symlink_to(outside)
    _mutate_seal(
        d,
        lambda seal: seal["artifact_hashes"].__setitem__(
            "escape", hashlib.sha256(b"outside").hexdigest()
        ),
    )
    result = verify_package(d, "pkg")
    assert result.ok is False
    assert any(
        diagnostic.kind == INVALID_PATH and diagnostic.path == "escape"
        for diagnostic in result.diagnostics
    )


def test_recorded_artifact_read_failure_returns_diagnostic(tmp_path, monkeypatch):
    d = _sealed(tmp_path / "pkg")
    original_read_bytes = Path.read_bytes

    def _deny_artifact(path):
        if path.name == "calc.py":
            raise PermissionError("artifact denied")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", _deny_artifact)
    result = verify_package(d, "pkg")
    assert result.ok is False
    assert any(
        diagnostic.kind == ARTIFACT_UNREADABLE
        and diagnostic.path == "modules/calc.py"
        and "artifact denied" in diagnostic.message
        for diagnostic in result.diagnostics
    )


def test_package_walk_failure_returns_diagnostic(tmp_path, monkeypatch):
    d = _sealed(tmp_path / "pkg")
    original_rglob = Path.rglob

    def _deny_walk(path, pattern):
        if path == d:
            raise PermissionError("walk denied")
        return original_rglob(path, pattern)

    monkeypatch.setattr(Path, "rglob", _deny_walk)
    result = verify_package(d, "pkg")
    assert result.ok is False
    assert any(
        diagnostic.kind == ARTIFACT_UNREADABLE
        and diagnostic.path is None
        and "walk denied" in diagnostic.message
        for diagnostic in result.diagnostics
    )


def test_env_compat_advisory_then_strict(tmp_path):
    """SC-3: a runtime mismatch is advisory by default, fatal under strict."""
    d = _sealed(tmp_path / "pkg")

    advisory = verify_package(d, "pkg", runtime_version="99.0")
    assert advisory.ok is True
    assert any(x.kind == RUNTIME_MISMATCH for x in advisory.diagnostics)

    strict = verify_package(d, "pkg", runtime_version="99.0", strict=True)
    assert strict.ok is False


def test_strict_runtime_mismatch_uses_kind_value_not_string_identity(tmp_path, monkeypatch):
    from sysml_codegen.contracts import verify as verify_module

    d = _sealed(tmp_path / "pkg")
    diagnostic_type = verify_module.Diagnostic

    def _fresh_kind_diagnostic(*, kind, path, message):
        fresh_kind = kind.encode().decode()
        assert fresh_kind == kind
        return diagnostic_type(kind=fresh_kind, path=path, message=message)

    monkeypatch.setattr(verify_module, "Diagnostic", _fresh_kind_diagnostic)
    result = verify_module.verify_package(d, "pkg", runtime_version="99.0", strict=True)
    assert result.ok is False


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
