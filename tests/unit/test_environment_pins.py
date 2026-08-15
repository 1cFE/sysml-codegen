"""The execution lane's environment pin must still be able to fail.

This pin once asserted paths inside the ``item7-rebuild`` worktrees; when those were
deleted (2026-08-15) it went from checking the tree to erroring 12 nodes at setup — and
the repair risk is the opposite failure, a pin that goes green for any resolution. These
tests run in the default suite and feed the predicate wrong resolutions, so the pin's
ability to reject them is proved on every run, not once in a review.
"""

from __future__ import annotations

from tests.execution.environment_pins import (
    CODEGEN_SRC,
    COMPANION_SRC,
    environment_pin_problems,
)


def _pinned_resolution() -> dict[str, str]:
    return {
        "python": "/anywhere/bin/python",
        "simkit": "/home/x/teax/packages/teax-simkit/src/simkit/__init__.py",
        "sysml_codegen": str(CODEGEN_SRC / "sysml_codegen" / "__init__.py"),
        "agentic_mbse": str(COMPANION_SRC / "agentic_mbse" / "__init__.py"),
    }


def test_the_pinned_resolution_passes() -> None:
    assert environment_pin_problems(_pinned_resolution()) == []


def test_the_pinned_roots_are_the_main_checkouts() -> None:
    """Anchor-derived, and pointing where the content actually lives now."""
    repo_root = CODEGEN_SRC.parent
    assert CODEGEN_SRC == repo_root / "src"
    assert COMPANION_SRC == repo_root.parent / "agentic-mbse" / "src"
    assert CODEGEN_SRC.is_dir()
    assert COMPANION_SRC.is_dir()


def test_simkit_outside_the_teax_checkout_is_rejected() -> None:
    resolved = _pinned_resolution() | {
        "simkit": "/home/x/.venv/lib/python3.12/site-packages/simkit/__init__.py"
    }
    problems = environment_pin_problems(resolved)
    assert len(problems) == 1
    assert "simkit resolved outside the pinned TEAx checkout" in problems[0]


def test_sysml_codegen_from_site_packages_is_rejected() -> None:
    """A copy under this repo's own ``.venv`` is a stale tree, not ``src``."""
    repo_root = CODEGEN_SRC.parent
    resolved = _pinned_resolution() | {
        "sysml_codegen": str(
            repo_root / ".venv/lib/python3.12/site-packages/sysml_codegen/__init__.py"
        )
    }
    problems = environment_pin_problems(resolved)
    assert len(problems) == 1
    assert problems[0].startswith("sysml_codegen resolved outside")


def test_agentic_mbse_from_a_dead_worktree_is_rejected() -> None:
    """The exact 2026-08-15 shape: a sibling directory that is not the main checkout."""
    repo_root = CODEGEN_SRC.parent
    resolved = _pinned_resolution() | {
        "agentic_mbse": str(
            repo_root.parent
            / "agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py"
        )
    }
    problems = environment_pin_problems(resolved)
    assert len(problems) == 1
    assert problems[0].startswith("agentic_mbse resolved outside")
