from pathlib import Path

import pytest

from tests.helpers.teax_discovery import discover_teax_simkit


def _simkit_root(path: Path) -> Path:
    package = path / "simkit"
    package.mkdir(parents=True)
    (package / "__init__.py").touch()
    return path


def test_explicit_teax_path_takes_precedence(tmp_path: Path) -> None:
    explicit = _simkit_root(tmp_path / "explicit")
    repository = tmp_path / "checkout" / "sysml-codegen"
    _simkit_root(repository.parent / "teax" / "packages" / "teax-simkit")

    assert (
        discover_teax_simkit({"TEAX_SIMKIT_PATH": str(explicit)}, repository_root=repository)
        == explicit.resolve()
    )


def test_checkout_relative_teax_path_is_used_without_environment(tmp_path: Path) -> None:
    repository = tmp_path / "checkout" / "sysml-codegen"
    sibling = _simkit_root(repository.parent / "teax" / "packages" / "teax-simkit")

    assert discover_teax_simkit({}, repository_root=repository) == sibling.resolve()


def test_invalid_teax_candidates_fail_with_actionable_routes(tmp_path: Path) -> None:
    repository = tmp_path / "checkout" / "sysml-codegen"

    with pytest.raises(RuntimeError, match="TEAX_SIMKIT_PATH.*checkout-relative sibling"):
        discover_teax_simkit(
            {"TEAX_SIMKIT_PATH": str(tmp_path / "invalid")}, repository_root=repository
        )


def test_symlink_loop_is_reported_as_an_invalid_candidate(tmp_path: Path) -> None:
    repository = tmp_path / "checkout" / "sysml-codegen"
    loop = tmp_path / "loop"
    loop.symlink_to(loop)

    with pytest.raises(RuntimeError) as error:
        discover_teax_simkit({"TEAX_SIMKIT_PATH": str(loop)}, repository_root=repository)

    message = str(error.value)
    assert "TEAX_SIMKIT_PATH" in message
    assert "checkout-relative sibling" in message
    assert "symlink" in message.lower()


def test_expanduser_failure_is_reported_as_an_invalid_explicit_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = tmp_path / "checkout" / "sysml-codegen"
    original_expanduser = Path.expanduser

    def raise_for_explicit_candidate(candidate: Path) -> Path:
        if str(candidate) == "injected-expansion-failure":
            raise RuntimeError("injected expanduser failure")
        return original_expanduser(candidate)

    monkeypatch.setattr(Path, "expanduser", raise_for_explicit_candidate)

    with pytest.raises(RuntimeError) as error:
        discover_teax_simkit(
            {"TEAX_SIMKIT_PATH": "injected-expansion-failure"},
            repository_root=repository,
        )

    message = str(error.value)
    assert "TEAX_SIMKIT_PATH" in message
    assert "checkout-relative sibling" in message
    assert "injected expanduser failure" in message
