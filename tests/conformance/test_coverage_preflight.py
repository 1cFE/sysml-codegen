"""The coverage account cannot ship disagreeing with the catalog it summarizes.

Four refusals, each named, each fail-before-mutate. The tree assertion is not decoration: a
refusal that fires *after* `_clear_output_directory` leaves a half-written package where a
working one used to be, which is worse than the disagreement it caught.

The perturbations act on the **graph and the plan**, not on snapshot bytes — a snapshot with a
row removed fails the document fingerprint long before any gate runs, so mutating bytes would
prove the fingerprint works rather than that this gate does.
"""

from __future__ import annotations

import dataclasses
import logging
from pathlib import Path

import pytest

from sysml_codegen.cli import (
    GenerationConfig,
    _generate_package_from_graph,
    _preflight_coverage_account,
)
from sysml_codegen.core.errors import CodeGenerationError
from sysml_codegen.elaboration import project
from sysml_codegen.generation.constraint_plan import build_constraint_generation_plan
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from sysml_codegen.resolution.models import ModuleKind
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "constraint_domain_detached_owner"
D9_FIXTURE = FIXTURES_DIR / "constraint_coverage_eligible_inapplicable"


def _graph_and_plan(fixture: Path = FIXTURE):
    from sysml_codegen.cli import _get_template_env

    graph = project(elaborate_model_paths([fixture]))
    return graph, build_constraint_generation_plan(graph, _get_template_env(), "probe")


def _config(tmp_path: Path, fixture: Path = FIXTURE) -> GenerationConfig:
    return GenerationConfig(
        output_path=tmp_path / "generated",
        models_path=fixture,
        package_name="coverage_preflight_probe",
        overwrite=True,
    )


def _nothing_was_written(config: GenerationConfig) -> bool:
    output = config.output_path
    return not output.exists() or not any(output.iterdir())


def _refused(graph, config, caplog) -> str:
    """Generate, require refusal, and return the logged message.

    ``_generate_package_from_graph`` reports a refusal by logging it and returning False —
    that is its contract with the CLI — so the assertion is on the return value and the
    message, not on an escaping exception.
    """
    with caplog.at_level(logging.ERROR):
        assert _generate_package_from_graph(graph, config) is False
    return "\n".join(record.getMessage() for record in caplog.records)


# ---------------------------------------------------------------------------
# 1. The account disagrees with its catalog
# ---------------------------------------------------------------------------


def _perturbed(plan):
    """An account that is internally CONSISTENT but wrong about this catalog.

    Perturbing a count into an arithmetic contradiction would be caught by
    ``CoverageAccountData``'s own identities before the preflight ever compared anything, and
    would prove the wrong guard. `authored_usage_total` is outside those identities, so a
    wrong value here can only be caught by comparing against the catalog.
    """
    return dataclasses.replace(
        plan, coverage=dataclasses.replace(plan.coverage, authored_usage_total=99)
    )


def test_a_perturbed_plan_account_refuses_and_names_both_sides():
    graph, plan = _graph_and_plan()
    with pytest.raises(
        CodeGenerationError, match="COVERAGE_ACCOUNT_INVALID"
    ) as raised:
        _preflight_coverage_account(graph, _perturbed(plan))
    assert "authored_usage_total=99" in str(raised.value)
    assert "authored_usage_total=2" in str(raised.value)


def test_a_perturbed_account_refuses_before_any_write(tmp_path, monkeypatch, caplog):
    """Fail-before-mutate, through the real generation route rather than the check alone."""
    real = build_constraint_generation_plan

    def _corrupt(graph, template_env, package_name):
        return _perturbed(real(graph, template_env, package_name))

    monkeypatch.setattr(
        "sysml_codegen.generation.constraint_plan.build_constraint_generation_plan", _corrupt
    )
    config = _config(tmp_path)
    message = _refused(project(elaborate_model_paths([FIXTURE])), config, caplog)
    assert "COVERAGE_ACCOUNT_INVALID: the account disagrees with its catalog" in message
    assert _nothing_was_written(config)


# ---------------------------------------------------------------------------
# 2. The aggregator disagrees with the usage rows, in both directions
# ---------------------------------------------------------------------------


def test_usage_rows_without_an_aggregator_refuse():
    graph, plan = _graph_and_plan()
    stripped = graph.model_copy(
        update={
            "modules": [
                module
                for module in graph.modules
                if module.module_kind is not ModuleKind.REPORT_AGGREGATOR
            ]
        }
    )
    with pytest.raises(
        CodeGenerationError, match="disagrees with the report-required rule"
    ) as raised:
        _preflight_coverage_account(stripped, plan)
    assert "requires a REPORT_AGGREGATOR module" in str(raised.value)


def test_an_aggregator_without_a_catalog_refuses():
    graph, plan = _graph_and_plan()
    orphaned = graph.model_copy(update={"constraint_catalog": None})
    with pytest.raises(CodeGenerationError, match="no constraint catalog"):
        _preflight_coverage_account(orphaned, plan)


# ---------------------------------------------------------------------------
# 3. An untaught reason token
# ---------------------------------------------------------------------------


def test_a_reason_item_two_adds_later_refuses_with_the_ruling_instruction(monkeypatch):
    """The pin compares the vocabularies, not only the tokens records happen to carry.

    A reason nobody wrote a coverage ruling for still refuses, because the question it raises
    — inside or outside the feasibility denominator — has no default answer.
    """
    from sysml_codegen.elaboration import graph as graph_module

    monkeypatch.setitem(
        graph_module.DISPOSITION_REASONS, "excluded", frozenset({"newly_invented"})
    )
    graph = project(elaborate_model_paths([FIXTURE]))
    from sysml_codegen.cli import _get_template_env

    # Raises at plan build, which is earlier than the preflight and earlier still than any
    # write. The preflight recomputes through the same function, so it is total over this
    # refusal too; there is simply no way to reach it with an untaught token in the tree.
    with pytest.raises(CodeGenerationError, match="has not been taught reason"):
        build_constraint_generation_plan(graph, _get_template_env(), "probe")


# ---------------------------------------------------------------------------
# 4. D9's contradiction
# ---------------------------------------------------------------------------


def test_the_d9_fixture_refuses_generation_by_name(tmp_path, caplog):
    """An inapplicability marker on a gate that ran stops the run, before any output."""
    config = _config(tmp_path, D9_FIXTURE)
    message = _refused(project(elaborate_model_paths([D9_FIXTURE])), config, caplog)
    assert "marked inapplicable but produced" in message
    assert _nothing_was_written(config)


def test_the_d9_refusal_names_the_usage_and_says_what_to_do():
    with pytest.raises(CodeGenerationError) as raised:
        _graph_and_plan(D9_FIXTURE)
    message = str(raised.value)
    assert "constraint_coverage_eligible_inapplicable::Live::live_but_marked" in message
    assert "produced 1 executable entries" in message
    assert "Remove the marker, or stop asserting the gate" in message
