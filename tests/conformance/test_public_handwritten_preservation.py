"""Typing changes retain real package generation and handwritten implementations."""
from __future__ import annotations

import ast
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.orchestration.exact_pipeline_context import (
    build_exact_pipeline_context_from_snapshot,
)
from sysml_codegen.resolution.models import ModuleKind
from tests.conftest import FIXTURES_DIR

SNAPSHOT = FIXTURES_DIR / "fusion_tea" / "instance_graph_snapshot.json"


@pytest.mark.parametrize("smart_regen", [False, True])
def test_real_handwritten_body_survives_public_package_regeneration(
    smart_regen: bool, tmp_path: Path,
) -> None:
    output = tmp_path / "preserved_package"
    config = GenerationConfig(from_snapshot=SNAPSHOT, output_path=output,
                              package_name="preserved_package", overwrite=True)
    assert run_codegen(config)
    graph = build_exact_pipeline_context_from_snapshot(SNAPSHOT).computation_graph
    assert {ModuleKind.CALCULATION, ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR} <= {
        m.module_kind for m in graph.modules
    }
    paths = list(output.rglob("recirculating_power_fraction_impl.py"))
    assert len(paths) == 1
    impl = paths[0]
    source = impl.read_text()
    tree = ast.parse(source)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
    # Replace the implementation itself, retaining its genuine generated interface.
    header = "\n".join(source.splitlines()[:function.lineno])
    handwritten = (header + '\n    """Owner implementation using a modeled field."""\n'
                   '    return inputs.eta + 7.125\n').encode()
    impl.write_bytes(handwritten)
    config.preserve_handwritten = True
    config.smart_regen = smart_regen
    assert run_codegen(config)
    assert impl.read_bytes() == handwritten
    assert not (output / "handwritten" / "backup").exists()
    assert len(list(output.rglob("*constraint*.py"))) >= 2
    assert (output / "pipelines" / "pipeline.yaml").is_file()
    assert (output / "contracts" / "model_contract.json").is_file()


@pytest.mark.parametrize("missing", ["calc_def_name", "calc_def_qualified_name",
                                      "producer_channel", "qualified_name"])
@pytest.mark.parametrize("existing", [False, True])
def test_missing_renderer_metadata_refuses_publicly_before_output_mutation(
    missing: str, existing: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    from sysml_codegen.orchestration import exact_pipeline_context

    context = build_exact_pipeline_context_from_snapshot(SNAPSHOT)
    graph = context.computation_graph
    if missing.startswith("calc_def"):
        module = next(m for m in graph.modules if m.module_kind is ModuleKind.CALCULATION)
        setattr(module, missing, None)
    else:
        source_kind = "module_output" if missing == "producer_channel" else "entry_point"
        source = next(i.source for m in graph.modules for i in m.inputs
                      if i.source.source_type == source_kind)
        setattr(source, missing, None)
    monkeypatch.setattr(exact_pipeline_context, "build_exact_pipeline_context_from_snapshot",
                        lambda path: SimpleNamespace(computation_graph=graph))
    output = tmp_path / "existing_package"
    if existing:
        output.mkdir()
        (output / "owner.bin").write_bytes(b"owner implementation\x00")
    before = {p.name: p.read_bytes() for p in output.glob("*")}
    with caplog.at_level(logging.ERROR):
        assert not run_codegen(GenerationConfig(from_snapshot=SNAPSHOT, output_path=output,
                                                package_name="existing_package", overwrite=True))
    assert "GENERATION_METADATA_MISSING" in caplog.text
    assert f"lacks {missing}" in caplog.text
    assert {p.name: p.read_bytes() for p in output.glob("*")} == before
    assert output.exists() == existing
