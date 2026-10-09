"""Public nonfinite refusal and finite inputs through actual source authorities."""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import FIXTURES_DIR, requires_license

SNAPSHOT = FIXTURES_DIR / "solar_battery_d5" / "instance_graph_snapshot.json"


def _tree(output: Path) -> dict[str, bytes]:
    return {
        p.relative_to(output).as_posix(): p.read_bytes()
        for p in output.rglob("*") if p.is_file()
    }


def _output(tmp_path: Path, existing: bool) -> Path:
    output = tmp_path / "package"
    if existing:
        (output / "nested").mkdir(parents=True)
        (output / "nested" / "owner.bin").write_bytes(b"handwritten\x00\n")
    return output


@requires_license
@pytest.mark.parametrize("literal", ["1.0e400", "-1.0e400"])
@pytest.mark.parametrize("existing", [False, True])
def test_real_model_overflow_refuses_before_mutating_output(
    literal: str, existing: bool, tmp_path: Path, caplog: pytest.LogCaptureFixture,
) -> None:
    model = tmp_path / "model.sysml"
    model.write_text("""package FiniteBoundary {
    private import ScalarValues::*;
    calc def Scale {
        in attribute factor : Real;
        out attribute scaled : Real = factor * 2.0;
    }
    part def Rig {
        attribute reading : Real = LITERAL;
        calc scale : Scale { in factor = reading; }
    }
    part rig : Rig;
}
""".replace("LITERAL", literal))
    output = _output(tmp_path, existing)
    before = _tree(output)
    with caplog.at_level(logging.ERROR):
        assert not run_codegen(GenerationConfig(models_path=model, output_path=output,
                                                package_name="finite_boundary", overwrite=True))
    assert "SI_SNAPSHOT_INVALID" in caplog.text
    assert "Out of range float values are not JSON compliant" in caplog.text
    assert _tree(output) == before
    assert output.exists() == existing


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("existing", [False, True])
def test_resealed_nonfinite_snapshot_refuses_before_mutating_output(
    value: float, existing: bool, tmp_path: Path, caplog: pytest.LogCaptureFixture,
) -> None:
    document = json.loads(SNAPSHOT.read_bytes())
    attributes = document["instance_graph"]["graph"]["attrs"]
    attribute = next(row for row in attributes if isinstance(row["value"], float))
    attribute["value"] = value
    # An untrusted producer can seal permissive JSON. Neither checksum authorizes
    # nonfinite values; the public loader must refuse before touching output.
    def permissive(payload: object) -> bytes:
        return json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
    instance = document["instance_graph"]
    instance["fingerprint"] = hashlib.sha256(permissive({
        "schema_version": instance["schema_version"], "graph": instance["graph"],
    })).hexdigest()
    unsigned = {k: v for k, v in document.items() if k != "integrity"}
    document["integrity"]["digest"] = hashlib.sha256(permissive(unsigned)).hexdigest()
    snapshot = tmp_path / "nonfinite.json"
    snapshot.write_bytes(permissive(document))
    output = _output(tmp_path, existing)
    before = _tree(output)
    with caplog.at_level(logging.ERROR):
        assert not run_codegen(GenerationConfig(from_snapshot=snapshot, output_path=output,
                                                package_name="finite_boundary", overwrite=True))
    assert "SI_INTERNAL_DEFECT" in caplog.text
    assert "Out of range float values are not JSON compliant" in caplog.text
    assert _tree(output) == before
    assert output.exists() == existing


def test_generated_input_json_is_strict_finite_json(tmp_path: Path) -> None:
    output = tmp_path / "finite_package"
    assert run_codegen(GenerationConfig(from_snapshot=SNAPSHOT, output_path=output,
                                        package_name="finite_package", overwrite=True))
    inputs = list((output / "inputs").glob("*.json"))
    assert inputs
    def refuse(token: str) -> None:
        raise AssertionError(f"nonfinite JSON token {token}")
    for path in inputs:
        assert isinstance(json.loads(path.read_text(), parse_constant=refuse), dict)


@pytest.mark.parametrize("value", [1.25, 1.0e20, 1.7976931348623157e308, 5.0e-324, -0.0])
def test_input_writer_preserves_finite_bytes(value: float, tmp_path: Path) -> None:
    from sysml_codegen.generation.entry_point import generate_all_derived_jsons
    from sysml_codegen.resolution.models import EntryPoint, EntryPointType, ParameterGroup

    group = ParameterGroup(
        name="finite_params", class_name="FiniteParams", source_file="model.sysml",
                           parameters=[EntryPoint(qualified_name="Pkg__value", simple_name="value",
                                                  entry_type=EntryPointType.LIBRARY_DEFAULT,
                                                  default_value=value, python_type="float")])
    paths = generate_all_derived_jsons([group], tmp_path)
    assert len(paths) == 1
    expected = json.dumps({"Pkg__value": value}, indent=2, sort_keys=True) + "\n"
    assert paths[0].read_text() == expected
