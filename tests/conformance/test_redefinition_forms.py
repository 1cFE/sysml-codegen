"""Both redefinition forms carry a value: `:>> x = …` and `attribute :>> x = …`.

modeling-assumptions.md once said the `attribute :>>` form is dropped at extraction. A probe on
2026-10-24 found all eight combinations below generate the native value (agentic-mbse
`.project/execution/evidence/redef-forms-20261024/`), and the doc now says so. This pins it.

The base declares `x` with `default 1.0`, so a dropped override shows up as a `p__x` input of
1.0. A kept literal shows up as a `p__x` input of 0.95. A kept expression (`y * 3.0`) makes
`x` computed: it is not an input, and its generated implementation returns 15.0 for y = 5.0.

A dotted override (`:>> inner.x = …`) keeps only a literal; an expression is dropped and the
package uses the base value (backlog `[DOTTED-OVERRIDE-EXPRESSION-DROPPED]`). That case is a
strict expected failure, so fixing the generator turns this file red until it is updated.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from types import SimpleNamespace

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

    inputs = _inputs(output)
    if value == "lit":
        assert inputs.get(f"{name}__p__x") == 0.95, inputs
    else:
        assert f"{name}__p__x" not in inputs, inputs
        assert inputs.get(f"{name}__p__y") == 5.0, inputs
        assert _computed_x(output, name, y=5.0) == 15.0


def _inputs(output: Path) -> dict[str, float]:
    inputs: dict[str, float] = {}
    for f in (output / "inputs").glob("*.json"):
        inputs.update(json.loads(f.read_text()))
    return inputs


def _computed_x(output: Path, name: str, y: float) -> float:
    """Call the generated `run_x` with y, without importing the package (it needs simkit)."""
    (impl,) = (output / "handwritten" / name).rglob("x_impl.py")
    source = impl.read_text()
    tree = ast.parse(source)
    tree.body = [node for node in tree.body if not isinstance(node, ast.ImportFrom)]
    namespace: dict[str, object] = {}
    exec(compile(tree, "x_impl.py", "exec"), namespace)
    return namespace["run_x"](SimpleNamespace(y=y))  # type: ignore[operator]


NESTED = """package {name} {{
    private import ScalarValues::*;
    calc def Twice {{ in v : Real; return r : Real = 2.0 * v; }}
    part def Inner {{ attribute x : Real default 1.0; }}
    part def Host {{
        attribute q : Real = 8.0;
        part inner : Inner;
        calc t : Twice {{ in v = inner.x; }}
    }}
    part h : Host {{ :>> inner.x = {value}; }}
}}
"""


def _generate_nested(tmp_path: Path, name: str, value: str) -> dict[str, float]:
    models = tmp_path / "models"
    models.mkdir()
    (models / "model.sysml").write_text(NESTED.format(name=name, value=value))
    output = tmp_path / "pkg"
    assert run_codegen(
        GenerationConfig(models_path=models, output_path=output, package_name=name, overwrite=True)
    )
    return _inputs(output)


def test_dotted_override_literal_reaches_package(tmp_path: Path) -> None:
    inputs = _generate_nested(tmp_path, "nest_lit", "5.0")
    assert inputs.get("nest_lit__h__inner__x") == 5.0, inputs


@pytest.mark.xfail(strict=True, reason="[DOTTED-OVERRIDE-EXPRESSION-DROPPED]")
def test_dotted_override_expression_reaches_package(tmp_path: Path) -> None:
    inputs = _generate_nested(tmp_path, "nest_expr", "q * 2.0")
    assert inputs.get("nest_expr__h__inner__x") != 1.0, inputs
