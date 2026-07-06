"""SC #1 lock: quoted CalcUsage names generate an importable package (Item 5).

``alias_agg_probe`` owns quoted calc defs (``'Margin Calc'``, ``'Report Calc'``,
``'Unit Cost Calc'``). It has ``computed_attributes: []`` and has never flowed
through registry + module generation, so the CalcUsage class-name / module-path
leak (``ModuleType.from_sysml`` / ``PythonModulePath.from_sysml`` building
identifiers straight from the raw quoted QN) was only code-inferred until now.

This drives the committed snapshot through full generation (license-free) and
asserts the two properties the leak breaks:
  1. every generated ``.py`` file parses (no ``'margin calc'.py`` / ``class
     'Margin Calc'Module`` garbage), and
  2. each class name the registry imports is declared by the module file it
     imports from (the registry never imports a name its module lacks).

Requirement: REQ-NC-08.
"""

from __future__ import annotations

import pytest

from tests.conftest import snapshot_fixture


@pytest.mark.req("REQ-NC-08")
@pytest.mark.req("REQ-GA-08")
def test_alias_agg_probe_aborts_with_v11_but_identifiers_are_clean(tmp_path) -> None:
    """alias_agg_probe generation aborts with V11 (Item 7) — tracked to Item 9.

    ``cost_model.base_cost`` binds the bare-name ``:>> widget.base_cost = 50.0``
    redefinition, whose value never lands as a resolver-reachable design attribute
    — it falls through valueless and stays wired → a guaranteed runtime
    ``KeyError``. Strict generation refuses it. Item 9 (RedefinitionData literals
    → CalcUsage entry-point defaults) is expected to flip this back to clean
    generation. The exact gap is pinned green in
    ``tests/unit/test_uncovered_params.py`` (``[cost_model.base_cost]``).

    REQ-NC-08 (quoted CalcUsage names never leak into identifiers) is preserved
    here at the graph level: generation aborts before writing files, so the leak
    property is asserted on the derived module identifiers directly (a leaked
    ``'Margin Calc'Module`` / ``'margin calc'.py`` is not a valid identifier).
    Item 9 restores the file-parse coverage when generation completes again.
    """
    from sysml_codegen.cli import (
        GenerationConfig,
        _get_python_path,
        _reconcile_params_coverage,
        run_codegen,
    )
    from sysml_codegen.generation import CodeGenerationError
    from sysml_codegen.resolution.graph_builder import collect_uncovered_params
    from sysml_codegen.snapshot import build_full_graph_from_snapshot

    graph, _inputs = build_full_graph_from_snapshot(snapshot_fixture("alias_agg_probe"))

    # V11 gap pinned: exactly the one base_cost dangle.
    violations = collect_uncovered_params(graph)
    assert [(u.input, u.module.split("__")[-1]) for u in violations] == [
        ("base_cost", "cost_model")
    ]
    # Strict boundary raises V11 (explicit raises-assertion — pins the behavior).
    with pytest.raises(CodeGenerationError, match=r"V11"):
        _reconcile_params_coverage(graph)
    # run_codegen observes the abort as False (fail-fast idiom).
    config = GenerationConfig(
        output_path=tmp_path,
        from_snapshot=snapshot_fixture("alias_agg_probe"),
        package_name="aap",
        overwrite=True,
    )
    assert run_codegen(config) is False

    # REQ-NC-08 preserved: every derived module identifier is quote/space-free.
    # module_type may be namespace-qualified (package.Class) — check per segment.
    for module in graph.modules:
        assert all(seg.isidentifier() for seg in module.module_type.split(".")), (
            f"module_type {module.module_type!r} leaks a quoted/spaced identifier"
        )
        path = _get_python_path(module).full_path
        stem = path.rsplit("/", 1)[-1].removesuffix(".py")
        assert stem.isidentifier(), (
            f"module path stem {stem!r} (from {path!r}) leaks a quoted identifier"
        )
