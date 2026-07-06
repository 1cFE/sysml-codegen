"""SC #1 lock: quoted CalcUsage names generate an importable package (Item 5),
now driven end-to-end after Item 9 pre-fills the plain-usage literal.

``alias_agg_probe`` owns quoted calc defs (``'Margin Calc'``, ``'Report Calc'``,
``'Unit Cost Calc'``). It has ``computed_attributes: []`` and had never flowed
through registry + module generation, so the CalcUsage class-name / module-path
leak (``ModuleType.from_sysml`` / ``PythonModulePath.from_sysml`` building
identifiers straight from the raw quoted QN) was only code-inferred until now.

Item 7 made this fixture abort at the V11 params-coverage boundary (its
``cost_model.base_cost`` bound the dropped ``:>> widget.base_cost = 50.0``, leaving
a wired-valueless entry point). Item 9 captures that plain-usage literal and
rewrites the binding to LITERAL 50.0, so generation completes again — restoring the
REQ-NC-08 file-parse coverage Item 5 deferred.

``issue22_model`` is the same shape (``:>> widget.base_cost = 100.0``); it rides the
shared body as a second parametrization (D4), giving it the equivalent clean-E2E
assertion the spec calls for.

This drives the committed snapshot through full generation (license-free) and asserts:
  1. generation completes (``run_codegen`` returns True — no V11 abort),
  2. every generated ``.py`` file parses (no ``'margin calc'.py`` / ``class
     'Margin Calc'Module`` garbage reaches a file), and
  3. every derived module identifier is quote/space-free (REQ-NC-08 at the graph level).

Requirements: REQ-NC-08, REQ-GA-08, REQ-HR-08.
"""

from __future__ import annotations

import ast

import pytest

from tests.conftest import snapshot_fixture


def _generate(tmp_path, fixture: str, package_name: str):
    """Run full snapshot-driven generation; assert it completes (no V11 abort)."""
    from sysml_codegen.cli import GenerationConfig, run_codegen

    out = tmp_path / "out"
    config = GenerationConfig(
        output_path=out,
        from_snapshot=snapshot_fixture(fixture),
        package_name=package_name,
        overwrite=True,
    )
    assert run_codegen(config) is True, f"{fixture} must generate cleanly (no V11 abort)"
    return out


# (fixture snapshot name, package name)
CLEAN_GEN_CASES = [
    ("alias_agg_probe", "aap"),
    ("issue22_model", "issue22"),
]


@pytest.mark.req("REQ-NC-08")
@pytest.mark.req("REQ-GA-08")
@pytest.mark.req("REQ-HR-08")
@pytest.mark.parametrize("fixture,package_name", CLEAN_GEN_CASES, ids=[c[0] for c in CLEAN_GEN_CASES])
def test_plain_usage_literal_fixture_generates_clean(tmp_path, fixture, package_name) -> None:
    """Item 9: the plain-usage-literal fixtures generate a clean, parseable package.

    Property 1 (generation completes) is asserted inside ``_generate``; here we add
    the file-parse coverage (2) and the derived-identifier cleanliness (3).
    """
    from sysml_codegen.cli import _get_python_path
    from sysml_codegen.snapshot import build_full_graph_from_snapshot

    out = _generate(tmp_path, fixture, package_name)

    # (2) Every generated .py file parses — no quoted/spaced identifier reached a file.
    py_files = [p for p in out.rglob("*.py") if p.is_file()]
    assert py_files, "generation produced no Python files"
    for path in py_files:
        try:
            ast.parse(path.read_text())
        except SyntaxError as exc:  # pragma: no cover - failure path
            pytest.fail(f"generated file {path} does not parse: {exc}")

    # (3) REQ-NC-08: every derived module identifier is quote/space-free.
    graph, _inputs = build_full_graph_from_snapshot(snapshot_fixture(fixture))
    for module in graph.modules:
        assert all(seg.isidentifier() for seg in module.module_type.split(".")), (
            f"module_type {module.module_type!r} leaks a quoted/spaced identifier"
        )
        mod_path = _get_python_path(module).full_path
        stem = mod_path.rsplit("/", 1)[-1].removesuffix(".py")
        assert stem.isidentifier(), (
            f"module path stem {stem!r} (from {mod_path!r}) leaks a quoted identifier"
        )
