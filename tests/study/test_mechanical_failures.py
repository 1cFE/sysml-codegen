"""The fail-closed half of the indicators tool, end to end.

Moved from fusion-tea ``tests/study/test_mechanical_failures.py`` at ``b06585709`` and re-pointed
at the neutral station fixture. Each case is a refusal the tool's module docstring documents:
the pedantic reader's "every unrecognized construct raises with a location. Every failure
there is mechanical, exits non-zero, and writes nothing" (``sysml_codegen/study/indicators.py:
6-11``).

Every case asserts three things, not one: a non-zero exit, a message that locates the fault,
and that no output file exists and stdout is empty. A broken analysis must never look like an
empty one.

All mutation runs on a copy of the station package. Because the fingerprint gate runs before
the parse, each copy is re-pinned by default, or the test would fail at the gate instead of at
the failure it means to exercise. The fingerprint-mismatch case is the same helper with
re-pinning off.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.study.conftest import PackageCopy

PIPELINE = "pipelines/pipeline.yaml"
P = "PumpStation__station__"
ABSENT_KEY = P + "no_such_axis_key"
COMPUTED_QUANTITY = P + "demand__required_flow"
UNCLASSIFIED_KEY = P + "not_in_the_contract"
AREA_INPUT = "area: float station_params.PumpStation__station__basin_area"


def _declare(copy: PackageCopy, key: str, axis: str = "basin_area") -> None:
    def mutate(data: dict[str, Any]) -> None:
        group = next(g for g in data["groups"] if g["axis"] == axis)
        group["keys"].append({"key": key, "provenance": "fan_out"})

    copy.edit_axes(mutate)


def missing_declared_key(copy: PackageCopy) -> None:
    _declare(copy, ABSENT_KEY)


def key_names_produced_channel(copy: PackageCopy) -> None:
    """A real channel from the trace: a model output, not an axis."""
    _declare(copy, COMPUTED_QUANTITY)


def unclassifiable_key(copy: PackageCopy) -> None:
    """Present in inputs/ but absent from the contract parameters, so its entry type
    cannot be classified."""
    path = copy.path / "inputs" / "station_params.json"
    data = json.loads(path.read_text())
    assert UNCLASSIFIED_KEY not in data, "fixture key already exists in the package"
    data[UNCLASSIFIED_KEY] = 1.0
    path.write_text(json.dumps(data, indent=2) + "\n")
    _declare(copy, UNCLASSIFIED_KEY)


def fingerprint_mismatch(copy: PackageCopy) -> None:
    copy.edit(PIPELINE, "run_description:", "run_description:  ")


def unparseable_reference(copy: PackageCopy) -> None:
    copy.edit(
        PIPELINE,
        "demand_flow: float PumpStation__station__demand__required_flow.root",
        "demand_flow: float PumpStation__station__demand__required_flow.value.deep",
    )


def corrupt_pipeline_line(copy: PackageCopy) -> None:
    path = copy.path / PIPELINE
    text = path.read_text()
    document = yaml.compose(text)
    modules = next(value for key, value in document.value if key.value == "modules")
    demand = next(
        value for key, value in modules.value if key.value == "pumpstation__station__demand"
    )
    inputs = next(value for key, value in demand.value if key.value == "inputs")
    value = next(value for key, value in inputs.value if key.value == "area")
    assert value.value == "float station_params.PumpStation__station__basin_area"
    path.write_text(
        text[: value.start_mark.index] + "floatonly_one_token" + text[value.end_mark.index :]
    )


def ghost_objective_channel(copy: PackageCopy) -> None:
    copy.edit_manifest(
        lambda data: data["objective_catalog"][0].update(channel="PumpStation__no_such_channel")
    )


def wrong_manifest_for_package(copy: PackageCopy) -> None:
    copy.edit_manifest(lambda data: data["package"].update(name="some_other_package"))


def malformed_manifest_baseline(copy: PackageCopy) -> None:
    copy.edit_manifest(lambda data: data["baseline"]["headline"].update(value="two dollars"))


CASES: list[tuple[str, Callable[[PackageCopy], None], str, bool]] = [
    ("missing_declared_key", missing_declared_key, ABSENT_KEY, True),
    ("key_names_produced_channel", key_names_produced_channel, "computed quantity", True),
    ("unclassifiable_key", unclassifiable_key, "not in contract parameters", True),
    ("fingerprint_mismatch", fingerprint_mismatch, "indicator-input fingerprint", False),
    ("unparseable_reference", unparseable_reference, "required_flow.value.deep", True),
    ("corrupt_pipeline_line", corrupt_pipeline_line, "pipeline.yaml:", True),
    ("ghost_objective_channel", ghost_objective_channel, "produced by no module", True),
    ("wrong_manifest_for_package", wrong_manifest_for_package, "package_name", True),
    ("malformed_manifest_baseline", malformed_manifest_baseline, "baseline", True),
]


@pytest.mark.parametrize("name,mutate,expect,repin", CASES, ids=[case[0] for case in CASES])
def test_fails_closed(
    station_copy: PackageCopy,
    name: str,
    mutate: Callable[[PackageCopy], None],
    expect: str,
    repin: bool,
    tmp_path: Path,
) -> None:
    mutate(station_copy)
    out_path = tmp_path / "indicators.json"
    rc, out, err = station_copy.run(repin=repin, out=out_path)
    assert rc != 0, f"{name} exited 0"
    assert expect in err, f"{name}: message does not locate the fault:\n{err}"
    assert out == ""
    assert not out_path.exists()


def test_the_absent_key_and_the_computed_quantity_say_different_things(
    station_copy: PackageCopy, tmp_path: Path
) -> None:
    """An author told 'your key is missing' when they picked a model output goes looking
    in the wrong place."""
    missing_declared_key(station_copy)
    _, _, absent = station_copy.run(out=tmp_path / "a.json")
    assert "absent from the package inputs" in absent
    assert "computed quantity" not in absent


def test_the_computed_quantity_message_names_the_producing_module(
    station_copy: PackageCopy, tmp_path: Path
) -> None:
    key_names_produced_channel(station_copy)
    _, _, err = station_copy.run(out=tmp_path / "b.json")
    assert COMPUTED_QUANTITY in err
    assert "computed quantity" in err
    assert "channel produced by module" in err


def test_the_corrupt_line_carries_file_line_and_key_path(
    station_copy: PackageCopy, tmp_path: Path
) -> None:
    corrupt_pipeline_line(station_copy)
    _, _, err = station_copy.run(out=tmp_path / "c.json")
    fault_line = next(
        i for i, line in enumerate((station_copy.path / PIPELINE).read_text().splitlines(), 1)
        if "area: floatonly_one_token" in line
    )
    assert f"pipeline.yaml:{fault_line}" in err
    assert "key path modules.pumpstation__station__demand.inputs.area" in err
    assert "floatonly_one_token" in err


def test_the_fingerprint_mismatch_names_the_live_digests(
    station_copy: PackageCopy, tmp_path: Path
) -> None:
    fingerprint_mismatch(station_copy)
    _, _, err = station_copy.run(repin=False, out=tmp_path / "d.json")
    assert "manifest pins" in err
    assert "live per-file digests" in err
    assert "pipelines/pipeline.yaml" in err
    assert "--print-fingerprint" in err


def test_the_ghost_objective_names_the_channel(station_copy: PackageCopy, tmp_path: Path) -> None:
    ghost_objective_channel(station_copy)
    _, _, err = station_copy.run(out=tmp_path / "e.json")
    assert "PumpStation__no_such_channel" in err


def test_a_nonstandard_node_tag_inside_modules_is_a_failure(
    station_copy: PackageCopy, tmp_path: Path
) -> None:
    """Compose preserves node tags, so a tagged value must be refused rather than read.
    Nothing executes either way: compose does not construct."""
    station_copy.edit(PIPELINE, AREA_INPUT, "area: !!python/object/apply:os.system ['echo pwned']")
    rc, out, err = station_copy.run(out=tmp_path / "f.json")
    assert rc != 0
    assert "node tag" in err
    assert out == ""


def test_an_unknown_key_inside_a_module_is_a_failure(
    station_copy: PackageCopy, tmp_path: Path
) -> None:
    station_copy.edit(
        PIPELINE,
        "  pumpstation__station__demand:\n    module_type:",
        "  pumpstation__station__demand:\n    surprise: true\n    module_type:",
    )
    rc, _, err = station_copy.run(out=tmp_path / "g.json")
    assert rc != 0
    assert "unknown key(s)" in err and "surprise" in err


def test_a_duplicate_axis_in_the_declaration_is_a_failure(
    station_copy: PackageCopy, tmp_path: Path
) -> None:
    station_copy.edit_axes(lambda data: data["groups"].append(dict(data["groups"][0])))
    rc, _, err = station_copy.run(out=tmp_path / "h.json")
    assert rc != 0
    assert "duplicate axis name" in err


def test_an_unknown_provenance_is_a_failure(station_copy: PackageCopy, tmp_path: Path) -> None:
    station_copy.edit_axes(
        lambda data: data["groups"][0]["keys"][0].update(provenance="because_i_said_so")
    )
    rc, _, err = station_copy.run(out=tmp_path / "i.json")
    assert rc != 0
    assert "'fan_out' or 'tie'" in err


def test_an_unknown_group_named_by_the_group_flag_is_a_failure(
    station_copy: PackageCopy, tmp_path: Path
) -> None:
    rc, out, err = station_copy.run(out=tmp_path / "j.json", group=("no_such_axis",))
    assert rc != 0
    assert "no_such_axis" in err
    assert out == ""
    assert not (tmp_path / "j.json").exists()
