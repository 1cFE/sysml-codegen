"""The shipped study tools name no consumer (spec SC5 (a), design I10).

A study tool that names one consumer's packages, paths, requirement numbers or machine is
that consumer's tool. The identifier classes and closed lists below are the spec's, committed
as literals with their provenance so a reader can check them. Vocabulary is not checked:
domain words stay legal; identifiers do not, even inside an example.

Covered so far: every study module the root split edits, plus ``identity``, ``roots`` and
``census``. ``integrate`` and ``declarations`` join with integrate's port, and the installed
skill text joins when it ships.

The last five tests are fusion-tea's ``tests/study/test_generic.py`` agnostic checks at
``b06585709``, moved and re-pointed at the installed package.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from sysml_codegen.study import roots
from tests.study.conftest import SCHEMAS, SYNTHETIC_MANIFEST

STUDY = roots.TOOL_HOME / "sysml_codegen" / "study"
COVERED_MODULES = (
    "census", "common", "identity", "indicators", "manifest",
    "preflight", "read_coverage", "roots", "verify",
)

#: fusion-tea paths (spec SC5 (a)).
FUSION_PATHS = (
    "exploration/", ".project/", "tests/models", "docs/integration_seam",
    "scripts/study", "scripts/integrate",
)
#: The nine ``exploration/`` package directories in fusion-tea's ``CONSUMER_SURFACE.md`` at
#: ``b06585709`` (spec SC5 (a)).
EXPLORATION_DIRECTORIES = (
    "aries_integrated", "component_alternatives", "costed_loop_brayton",
    "exchanger_architecture", "ife_e2e", "magnet_materials", "stellarator_e2e",
    "stellarator_materials", "whole_plant_conversion",
)
#: The 17 generated package names in live ``package_contract.json`` files, from fusion-tea's
#: ``CONSUMER_ATTRIBUTES.md`` at ``b06585709``.
PACKAGE_NAMES = (
    "stellarator_tea", "ife_tea", "aries_integrated", "inventory_tea", "heat_tea", "fuel_tea",
    "brayton_tea", "budget_tea", "combinations_tea", "component_alternatives_tea",
    "costed_loop_brayton_tea", "exchanger_architecture_thermal_tea", "magnet_materials_tea",
    "stellarator_materials_nb3sn_tea", "stellarator_materials_rebco_tea",
    "stellarator_materials_reference_tea", "whole_plant_conversion_tea",
)
#: The 20 root key prefixes of live package inputs, from fusion-tea's ``CONSUMER_ATTRIBUTES.md``
#: at ``b06585709``. They cover the spec's two known prefixes, ``stellarator_09__stellaris__``
#: and ``hif_plant_pkg__hif_plant__``.
KEY_PREFIXES = (
    "SolarBatteryDesign__", "aries_constituent_inventory__", "aries_cs_plasma_integration__",
    "aries_dual_blanket_heat__", "aries_fuel_reuse__", "aries_integrated_plant__",
    "aries_nominal_brayton__", "aries_source_budget__", "combinations_circulator_purchase__",
    "combinations_loop_brayton__", "combinations_lumped_fit__", "combinations_plasma_chain__",
    "component_alternatives__", "costed_loop_brayton__", "exp_toy__", "hif_plant_pkg__",
    "magnet_subsystem__", "stellarator_09__", "stellarator_09_materials__",
    "whole_plant_conversion__",
)
#: Machine paths, environment variables and adapters (spec SC5 (a)).
MACHINE_IDENTIFIERS = ("/home/", "~/1cfe", "STOP_PARSER_", "era_adapter")
#: Requirement, decision and work-item numbers; process pointers (spec SC5 (a)).
NUMBERED = re.compile(r"\b(?:MR|PR|WI|ADR|SC)-\d|\bR-[A-Z]\d")
POINTERS = re.compile(r"\(Item \d+\)|\b20\d{6}-[a-z]|\b[LT]-\d{3}\b")


def _identifier_hits(text: str) -> list[str]:
    hits = [needle for needle in (*FUSION_PATHS, *KEY_PREFIXES, *MACHINE_IDENTIFIERS)
            if needle in text]
    hits += [name for name in (*EXPLORATION_DIRECTORIES, *PACKAGE_NAMES)
             if re.search(rf"\b{re.escape(name)}\b", text)]
    hits += [match.group() for match in NUMBERED.finditer(text)]
    hits += [match.group() for match in POINTERS.finditer(text)]
    return hits


def _module(name: str) -> Path:
    return STUDY / f"{name}.py"


@pytest.mark.parametrize("name", COVERED_MODULES)
def test_a_study_module_carries_no_consumer_identifier(name: str) -> None:
    assert _identifier_hits(_module(name).read_text()) == []


@pytest.mark.parametrize(
    "text",
    [
        "see exploration/stellarator_e2e/studies", "stellarator_09__stellaris__R",
        "per MR-7", "decided in ADR-009", "rule R-B1", "(Item 3)", "20260905-stored-energy-basis",
        "lesson L-012", "STOP_PARSER_TEAX_ROOT", "/home/someone", "the heat_tea package",
    ],
)
def test_the_identifier_check_sees_each_class(text: str) -> None:
    """A grep that matches nothing proves nothing: each class must actually fire."""
    assert _identifier_hits(text) != []


def test_domain_vocabulary_is_not_an_identifier() -> None:
    assert _identifier_hits("a stellarator's levelized cost, heat and fuel budgets") == []


# --------------------------------------------- moved from fusion-tea's test_generic.py


@pytest.mark.parametrize(
    "needle", ["stellarator_tea", "stellarator_09__stellaris__", "era_adapter"]
)
@pytest.mark.parametrize("name", COVERED_MODULES)
def test_tool_modules_are_generic(needle: str, name: str) -> None:
    assert needle not in _module(name).read_text()


@pytest.mark.parametrize("name", COVERED_MODULES)
def test_tool_modules_name_no_pipeline_or_objective_channel(name: str) -> None:
    """The objective catalog is manifest-owned; no channel is hard-coded in the tool."""
    text = _module(name).read_text()
    for needle in ("mfe_stellarator", "lcoe_calc", "verify_stellaris", "stellaris"):
        assert needle not in text


@pytest.mark.parametrize("name", COVERED_MODULES)
def test_tool_modules_import_no_package_code(name: str) -> None:
    text = _module(name).read_text()
    assert "exploration" not in text
    assert "stellarator" not in text


@pytest.mark.parametrize("needle", ["import ", "lambda", "eval(", "exec(", "$ref", "!!"])
def test_the_manifest_holds_no_executable_content(needle: str) -> None:
    """The manifest is data only: no import hooks, no computed defaults."""
    assert SYNTHETIC_MANIFEST.suffix == ".json"
    json.loads(SYNTHETIC_MANIFEST.read_text())
    assert needle not in SYNTHETIC_MANIFEST.read_text()


def test_the_schema_files_are_the_committed_contract() -> None:
    found = {resource.name for resource in SCHEMAS.iterdir()}
    assert {
        "axis_declaration.v1.schema.json",
        "indicators.v1.schema.json",
        "study_package_manifest.v1.schema.json",
    } <= found
