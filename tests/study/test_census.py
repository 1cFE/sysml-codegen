"""The entry-point census groups a package's parameters by entry type (design DD9, B11)."""

from __future__ import annotations

import json
from pathlib import Path

from sysml_codegen.study import census, integrate
from tests.study.conftest import STATION_PACKAGE


def _package(root: Path, parameters: list[dict[str, str]]) -> Path:
    (root / "contracts").mkdir(parents=True)
    (root / "contracts" / "model_contract.json").write_text(
        json.dumps({"parameters": parameters})
    )
    return root


def test_parameters_group_by_entry_type(tmp_path: Path) -> None:
    package = _package(
        tmp_path,
        [
            {"entry_type": "design_attribute", "qualified_name": "P__a"},
            {"entry_type": "library_default", "qualified_name": "P__calc__x"},
            {"entry_type": "design_attribute", "qualified_name": "P__b"},
            {"entry_type": "usage_literal", "qualified_name": "P__calc__y"},
        ],
    )
    assert census.by_entry_type(package) == {
        "design_attribute": {"P__a", "P__b"},
        "library_default": {"P__calc__x"},
        "usage_literal": {"P__calc__y"},
    }


def test_a_package_with_no_parameters_has_an_empty_census(tmp_path: Path) -> None:
    assert census.by_entry_type(_package(tmp_path, [])) == {}


def test_the_station_census_is_six_design_attributes() -> None:
    station = "PumpStation__station__"
    assert census.by_entry_type(STATION_PACKAGE) == {
        "design_attribute": {
            station + name
            for name in (
                "allowed_rise_rate", "basin_area", "design_inflow",
                "energy_price", "installed_capacity", "pump_head",
            )
        }
    }


def test_integrate_rederives_its_census_through_the_shipped_helper() -> None:
    assert integrate.rederived_census(STATION_PACKAGE) == {
        "entry_points": 6,
        "by_entry_type": {
            key: sorted(value) for key, value in census.by_entry_type(STATION_PACKAGE).items()
        },
    }
