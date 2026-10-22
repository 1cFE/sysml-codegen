"""No writer changes the graph it is given (Item 2b design D14, Round 2's guard).

The writers dropped their own re-checks because ``emit_package`` only receives a graph that
``prepare`` already checked. That argument holds only if writing does not change the graph,
so the graph is dumped before and after ``emit_package`` on models that exercise every
writer, constraint machinery included.

Licensed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig
from sysml_codegen.cli.emit import emit_package
from sysml_codegen.cli.prepare import LiveModels, Prepared, load_source, prepare
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


@pytest.mark.parametrize("fixture", ["d38_caret", "constraint_multi_instance"])
def test_emit_package_leaves_the_prepared_graph_unchanged(fixture, tmp_path: Path):
    prepared = prepare(load_source(LiveModels((FIXTURES_DIR / fixture,))), "graph_probe")
    assert isinstance(prepared, Prepared)
    before = prepared.graph.model_dump()
    config = GenerationConfig(output_path=tmp_path / "pkg", package_name="graph_probe")
    assert emit_package(prepared, config) is None
    assert prepared.graph.model_dump() == before
