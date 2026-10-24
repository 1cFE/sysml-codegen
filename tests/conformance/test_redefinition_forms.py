"""Both redefinition forms carry a value: `:>> x = …` and `attribute :>> x = …`.

modeling-assumptions.md once said the `attribute :>>` form is dropped at extraction. A probe on
2026-10-24 found all eight combinations below generate the native value (agentic-mbse
`.project/execution/evidence/redef-forms-20261024/`), and the doc now says so. This pins it.

The base declares `x` with `default 1.0`, so a dropped override shows up as a `p__x` input of
1.0. A kept literal shows up as a `p__x` input of 0.95. A kept expression (`y * 3.0`) makes
`x` computed, so it is not an input at all.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import requires_license

pytestmark = requires_license

BASE = """package {name} {{
    private import ScalarValues::*;
    calc def Twice {{ in v : Real; return r : Real = 2.0 * v; }}
    part def Base {{
        attribute y : Real = 5.0;
        attribute x : Real default 1.0;
        calc t : Twice {{ in v = x; }}
    }}
{body}
}}
"""

FORMS = {"attr": "attribute :>> x", "bare": ":>> x"}
VALUES = {"lit": "0.95", "expr": "y * 3.0"}


def _body(place: str, form: str, value: str) -> str:
    member = f"{FORMS[form]} = {VALUES[value]};"
    if place == "use":
        return f"    part p : Base {{ {member} }}"
    return f"    part def Sub :> Base {{ {member} }}\n    part p : Sub;"


@pytest.mark.parametrize("value", VALUES)
@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("place", ["use", "def"])
def test_redefinition_value_reaches_package(
    tmp_path: Path, place: str, form: str, value: str
) -> None:
    name = f"{place}_{form}_{value}"
    models = tmp_path / "models"
    models.mkdir()
    (models / "model.sysml").write_text(BASE.format(name=name, body=_body(place, form, value)))
    output = tmp_path / "pkg"
    assert run_codegen(
        GenerationConfig(models_path=models, output_path=output, package_name=name, overwrite=True)
    )

    inputs: dict[str, float] = {}
    for f in (output / "inputs").glob("*.json"):
        inputs.update(json.loads(f.read_text()))

    if value == "lit":
        assert inputs.get(f"{name}__p__x") == 0.95, inputs
    else:
        assert f"{name}__p__x" not in inputs, inputs
        assert inputs.get(f"{name}__p__y") == 5.0, inputs
