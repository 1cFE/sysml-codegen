"""A writer failure logs the record the base commit logged for it (Item 2b design D18).

``emit_package`` owns the writers' failure handling, moved from ``_generate_package_from_graph``
and ``run_codegen``. One writer is patched to raise each failure class in turn on a case that
builds, and the single refusal record must equal the one Phase 0 recorded at the base commit
(``tests/expectations/subset_profile/refusal_records.json``, ``writer_failure:*``), which
``scripts/refusal_records.py`` took with the same three exceptions. The screen report is still
printed after the failure, and names the writing step as the refusal.

Licensed.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.core.errors import CodeGenerationError, GenerationCode
from tests.conftest import requires_license
from tests.helpers import refusal_records
from tests.helpers.subset_profile import cases

pytestmark = requires_license

#: The case ``scripts/refusal_records.py`` patched; it builds at the base commit.
BUILDS_CASE = "anonymous-declaration__attribute_usage"

FAILURES = {
    "CodeGenerationError": CodeGenerationError(
        "probe: the pipeline writer refused", code=GenerationCode.MODULE_KIND_UNRENDERABLE
    ),
    "OSError": OSError("probe: the disk refused the write"),
    "RuntimeError": RuntimeError("probe: an unclassified writer failure"),
}


@pytest.mark.parametrize("name", sorted(FAILURES))
def test_writer_failure_logs_the_base_record(name, tmp_path: Path, monkeypatch, caplog):
    def raising(*_args, **_kwargs):
        raise FAILURES[name]

    monkeypatch.setattr("sysml_codegen.cli.emit._generate_pipeline", raising)
    output = tmp_path / "pkg"
    config = GenerationConfig(
        output_path=output, models_path=cases.model_root(cases.load_answer(BUILDS_CASE))
    )
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    with refusal_records.capture_refusals(output) as records:
        assert run_codegen(config) is False
    assert records == refusal_records.load()[f"writer_failure:{name}"]
    assert len(records) == 1
    infos = [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]
    assert any(m.startswith("Screen ") for m in infos), infos
    assert infos[-2:] == ["Readiness: refused", "  - the generator refuses at step emit"]
