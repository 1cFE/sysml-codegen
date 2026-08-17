"""The exact graph reaches the existing YAML and registry templates."""

from __future__ import annotations

from pathlib import Path

import jinja2

from sysml_codegen.elaboration import project
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.generation.pipeline import generate_pipeline_yaml
from sysml_codegen.generation.registry import generate_registry
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license

TEMPLATES = Path(__file__).parents[2] / "src/sysml_codegen/templates"


def test_exact_projection_renders_real_pipeline_and_registry(tmp_path: Path) -> None:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "source_identity_mixed_consumers"])
    assert extractor.load_models()
    graph = project(
        elaborate(
            extractor.model,
            extractor.extract_calculation_definitions(),
            validation_diagnostics=extractor.diagnostics.validation,
        )
    )
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES))

    pipeline = generate_pipeline_yaml(graph, "exact_probe", environment)
    registry = generate_registry(graph, "exact_probe", environment, tmp_path / "__init__.py")

    assert "source_identity_mixed_consumers__station__chain_calc" in pipeline
    assert "constraint_report_aggregator" in pipeline
    assert "create_exact_probe_registry" in registry
    assert "ConstraintReportAggregatorModule" in registry
