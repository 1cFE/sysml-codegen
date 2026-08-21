from pathlib import Path

import pytest

from tests.helpers.teax_discovery import discover_teax_simkit


def _simkit_root(path: Path) -> Path:
    package = path / "simkit"
    package.mkdir(parents=True)
    (package / "__init__.py").touch()
    return path


def test_explicit_teax_path_must_equal_the_manifest_root(tmp_path: Path) -> None:
    expected = _simkit_root(tmp_path / "expected")

    assert (
        discover_teax_simkit(
            {"TEAX_SIMKIT_PATH": str(expected)}, expected_root=expected
        )
        == expected.resolve()
    )


def test_missing_explicit_path_is_refused(tmp_path: Path) -> None:
    expected = _simkit_root(tmp_path / "expected")

    with pytest.raises(RuntimeError, match="TEAX_SIMKIT_PATH.*required"):
        discover_teax_simkit({}, expected_root=expected)


def test_different_valid_path_is_refused(tmp_path: Path) -> None:
    expected = _simkit_root(tmp_path / "expected")
    different = _simkit_root(tmp_path / "different")

    with pytest.raises(RuntimeError, match="does not equal the provenance root"):
        discover_teax_simkit(
            {"TEAX_SIMKIT_PATH": str(different)}, expected_root=expected
        )


def test_invalid_explicit_path_is_refused(tmp_path: Path) -> None:
    expected = _simkit_root(tmp_path / "expected")

    with pytest.raises(RuntimeError, match="simkit/__init__.py"):
        discover_teax_simkit(
            {"TEAX_SIMKIT_PATH": str(tmp_path / "invalid")},
            expected_root=expected,
        )


def test_symlink_loop_is_reported(tmp_path: Path) -> None:
    expected = _simkit_root(tmp_path / "expected")
    loop = tmp_path / "loop"
    loop.symlink_to(loop)

    with pytest.raises(RuntimeError, match="TEAX_SIMKIT_PATH"):
        discover_teax_simkit(
            {"TEAX_SIMKIT_PATH": str(loop)}, expected_root=expected
        )
