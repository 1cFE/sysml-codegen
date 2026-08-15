"""Shared fixtures and helpers for unit tests."""

from __future__ import annotations

import importlib
import itertools
import sys
from pathlib import Path

import jinja2
import pytest

TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "src/sysml_codegen/templates"

_RENDER_COUNT = itertools.count()


# ---------------------------------------------------------------------------
# Generated constraint-report code (Item 3)
#
# D6's precedence and CoverageAccount's validators live in Jinja templates, so they are
# tested by rendering the templates, importing the result, and running the emitted `run`. A
# test that re-implemented the five precedence arms would prove only that the test agrees
# with itself — which is the failure mode the retired `all_satisfied` headline shipped under.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def _report_template_env() -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture(scope="session")
def generated_constraint_types(_report_template_env, tmp_path_factory):
    """The rendered `schemas/constraint_types` module: `CoverageAccount`, `ConstraintReport`."""
    root = tmp_path_factory.mktemp("constraint_types")
    (root / "constraint_types.py").write_text(
        _report_template_env.get_template("constraint_types.py.jinja2").render()
    )
    sys.path.insert(0, str(root))
    try:
        yield importlib.import_module("constraint_types")
    finally:
        sys.path.remove(str(root))


@pytest.fixture(scope="session")
def coverage_account_model(generated_constraint_types):
    return generated_constraint_types.CoverageAccount


@pytest.fixture(scope="session")
def constraint_report_model(generated_constraint_types):
    return generated_constraint_types.ConstraintReport


@pytest.fixture
def rendered_aggregator(_report_template_env, tmp_path_factory):
    """Render a real aggregator for one shape and run it; return its `ConstraintReport`.

    A fresh package per call, because the input model, `EXPECTED_IDS`, and the baked
    `COVERAGE` are all generation-time constants — reaching into an already-imported module
    to swap them would test something no package ships.
    """

    def run(statuses, account):
        index = next(_RENDER_COUNT)
        package_name = f"aggregator_probe_{index}"
        root = tmp_path_factory.mktemp(package_name)
        package = root / package_name
        (package / "schemas").mkdir(parents=True)
        (package / "modules").mkdir(parents=True)
        for path in (package, package / "schemas", package / "modules"):
            (path / "__init__.py").write_text("")

        (package / "schemas" / "constraint_types.py").write_text(
            _report_template_env.get_template("constraint_types.py.jinja2").render()
        )
        ids = [f"c{position}" for position in range(len(statuses))]
        (package / "modules" / "aggregator.py").write_text(
            _report_template_env.get_template("report_aggregator.py.jinja2").render(
                package_name=package_name,
                expected_ids=repr(tuple(ids)),
                constraint_ids=ids,
                class_name="ProbeAggregator",
                module_name="probe_aggregator",
                catalog_fingerprint="0" * 64,
                coverage=repr(account.as_mapping()),
            )
        )

        sys.path.insert(0, str(root))
        try:
            types = importlib.import_module(f"{package_name}.schemas.constraint_types")
            module = importlib.import_module(f"{package_name}.modules.aggregator")
            evaluations = {
                cid: types.ConstraintEvaluation(
                    constraint_id=cid, status=status, observed={}
                )
                for cid, status in zip(ids, statuses, strict=True)
            }
            result = module.ProbeAggregator().run(**evaluations)
        finally:
            sys.path.remove(str(root))
        return result.data.constraint_report

    return run
