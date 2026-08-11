"""Every generated params schema is importable Python that loads its own JSON.

This is the coverage hole surfacing S3 exposed. Nothing parsed a generated
package's schema files, so a params key carrying an occurrence index
(``…__cell[0]__base_cost``, minted by a modelled finite multiplicity) was written
straight into a class body as a field name and the module was a ``SyntaxError``.
The shipped route produced a broken artifact on a ratified corpus fixture and no
test noticed.

The fix keeps the JSON key exactly as it was and sanitizes only the Python field
name, with the key carried as the field's alias
(``core/qualified_names.params_field_name``). So the assertions here are in
three layers, and the middle one is the one that matters:

  1. every generated ``.py`` file parses;
  2. the schema module **imports** and validates its own emitted JSON, which is
     what proves the alias is wired and not merely written;
  3. the JSON keys are byte-identical to the entry-point qualified names, so the
     sanitization did not leak into the input surface.

``d38_caret`` is the reproducing specimen — corpus row 12, whose
``…__pack__cell[i]__base_cost`` keys are what broke — and it is joined by the
fixtures that mint an index and by two that mint none, so the no-index path is
covered as well.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.orchestration.exact_pipeline_context import build_exact_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

# (fixture, does it mint an indexed key?). Both answers are represented on
# purpose: the sanitizer must be a no-op wherever there is no index.
CASES = [
    ("d38_caret", True),
    ("costed_cart_d5", True),
    ("alias_agg_d5", True),
    ("attr_expr_probe", False),
    ("wi014_toy", False),
]


@pytest.fixture(scope="module")
def packages(tmp_path_factory) -> dict[str, Path]:
    root = tmp_path_factory.mktemp("schema-import")
    built: dict[str, Path] = {}
    for fixture, _indexed in CASES:
        output = root / fixture
        assert run_codegen(
            GenerationConfig(
                models_path=FIXTURES_DIR / fixture,
                output_path=output,
                package_name=fixture,
                pipeline_name="pipeline",
            )
        ), f"the exact route must generate {fixture}"
        built[fixture] = output
    return built


def _load_schema_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


@pytest.mark.parametrize("fixture,indexed", CASES, ids=[case[0] for case in CASES])
def test_every_generated_python_file_parses(
    packages: dict[str, Path], fixture: str, indexed: bool
) -> None:
    package = packages[fixture]
    unparseable = []
    for path in sorted(package.rglob("*.py")):
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as error:
            unparseable.append(f"{path.relative_to(package)}: {error}")
    assert unparseable == []


@pytest.mark.parametrize("fixture,indexed", CASES, ids=[case[0] for case in CASES])
def test_each_params_schema_imports_and_validates_its_own_json(
    packages: dict[str, Path], fixture: str, indexed: bool
) -> None:
    """The claim a parse check cannot make: the emitted JSON actually loads."""
    package = packages[fixture]
    inputs = sorted((package / "inputs").glob("*.json"))
    assert inputs, f"{fixture} emitted no input JSON"

    for payload_path in inputs:
        schema_path = package / "schemas" / f"{payload_path.stem}.py"
        assert schema_path.exists(), f"no schema for {payload_path.name}"
        module = _load_schema_module(schema_path, f"{fixture}_{payload_path.stem}")

        model = next(
            value
            for name, value in vars(module).items()
            if isinstance(value, type) and name.endswith("Params")
        )
        payload = json.loads(payload_path.read_text())
        loaded = model(**payload)

        for key, value in payload.items():
            assert getattr(loaded, key.replace("[", "_").replace("]", "")) == value


@pytest.mark.parametrize("fixture,indexed", CASES, ids=[case[0] for case in CASES])
def test_the_json_keys_are_the_entry_point_names_verbatim(
    packages: dict[str, Path], fixture: str, indexed: bool
) -> None:
    """The input surface did not move: keys are the graph's qualified names."""
    package = packages[fixture]
    graph = build_exact_pipeline_context([FIXTURES_DIR / fixture]).computation_graph
    minted = {
        parameter.qualified_name
        for group in graph.entry_point_groups
        for parameter in group.parameters
        if parameter.default_value is not None
    }
    emitted: set[str] = set()
    for payload_path in (package / "inputs").glob("*.json"):
        emitted.update(json.loads(payload_path.read_text()))
    assert emitted == minted

    has_index = any("[" in key for key in emitted)
    assert has_index is indexed, (
        f"{fixture} was declared indexed={indexed} but emitted "
        f"{'an indexed' if has_index else 'no indexed'} key"
    )


@pytest.mark.parametrize("fixture,indexed", CASES, ids=[case[0] for case in CASES])
def test_only_an_indexed_key_gets_an_alias(
    packages: dict[str, Path], fixture: str, indexed: bool
) -> None:
    """A package with no multiplicity is byte-for-byte what it was before the fix."""
    package = packages[fixture]
    aliased = [
        path.name
        for path in (package / "schemas").glob("*_params.py")
        if "alias=" in path.read_text()
    ]
    if indexed:
        assert aliased, f"{fixture} mints an indexed key but no schema carries an alias"
    else:
        assert aliased == [], f"{fixture} mints no indexed key but {aliased} carry aliases"


def test_the_pipeline_reads_the_field_name_the_schema_declares(
    packages: dict[str, Path],
) -> None:
    """The runtime resolves ``group.<field>`` with ``getattr``, so they must agree.

    Sanitizing the field without moving the pipeline's reference would leave a
    package that parses and then fails at execution with an ``AttributeError`` —
    strictly worse than the ``SyntaxError`` it replaced.
    """
    import yaml

    package = packages["d38_caret"]
    pipeline = yaml.safe_load((package / "pipelines" / "pipeline.yaml").read_text())

    fields: dict[str, set[str]] = {}
    for schema_path in (package / "schemas").glob("*_params.py"):
        module = _load_schema_module(schema_path, f"d38_fields_{schema_path.stem}")
        model = next(
            value
            for name, value in vars(module).items()
            if isinstance(value, type) and name.endswith("Params")
        )
        fields[schema_path.stem] = set(model.model_fields)

    referenced = 0
    for spec in pipeline["modules"].values():
        for source in spec.get("inputs", {}).values():
            text = str(source).split()[-1]
            group, _, field = text.partition(".")
            if group not in fields:
                continue
            referenced += 1
            assert field in fields[group], f"pipeline reads {group}.{field}, which is not a field"
    assert referenced, "no pipeline input read a params group — the check proved nothing"
