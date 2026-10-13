"""fusion-tea's compatibility surface exists on the moved modules, with its signatures (SC6).

fusion-tea's consumers use 32 names on the study modules, listed in its
``CONSUMER_ATTRIBUTES.md`` at ``b06585709``. Two are the supported route API
(``identity.build_sealed`` and ``common.write_document``); the other 30 are the compatibility
surface (design Appendix C). Each must exist on the moved module with the shape it had.

``data/compat_surface.json`` records that shape, captured once from the staged ``b06585709``
modules by WRAP-SPLIT Item 3's capture script (in git at ``4dfe275``,
``.project/active/study-layer-to-codegen/evidence/compat/capture_compat_surface.py``)
with :func:`describe` below: each name's kind and its parameters, bases, value or module,
without annotations. Behaviour is SC12's and, at adoption, fusion-tea's own suite's.
"""

from __future__ import annotations

import importlib
import inspect
import json
import types
from typing import Any

import pytest

from tests.study.conftest import DATA_DIR

TABLE = DATA_DIR / "compat_surface.json"

#: Every name fusion-tea's consumers use, by module, from ``CONSUMER_ATTRIBUTES.md`` at
#: ``b06585709``. ``integrate`` was ``scripts/integrate.py``; the rest were ``scripts/study/``.
SURFACE: dict[str, tuple[str, ...]] = {
    "common": (
        "ToolError", "assert_tree_clean", "manifest_mod", "read_json", "relative_deviation",
        "write_document",
    ),
    "identity": ("build_sealed",),
    "indicators": ("build_graph", "predicate_operands", "read_model_contract", "read_pipelines"),
    "integrate": ("rederived_census",),
    "manifest": (
        "MANIFEST_SCHEMA_VERSION", "ManifestError", "assert_package_identity",
        "assert_pin_matches", "indicator_input_fingerprint", "indicator_input_read_set", "load",
        "read_executable_fingerprint", "read_package_name", "read_semantic_fingerprint",
        "repo_relative_posix", "validate",
    ),
    "verify": (
        "TOLERANCE", "VerifyError", "check_case", "derive_verdict", "feature_refs",
        "manifest_mod", "objective_channels", "package_input_values",
    ),
}
NAMES = sorted(f"{module}.{name}" for module, names in SURFACE.items() for name in names)

#: Where each staged module lives now.
MOVED = {"scripts.study.": "sysml_codegen.study.", "scripts.integrate": "sysml_codegen.study.integrate"}


def describe(value: object) -> dict[str, Any]:
    """A name's kind, and its parameters, bases, value or module, without annotations."""
    if isinstance(value, types.ModuleType):
        return {"kind": "module", "module": value.__name__}
    if isinstance(value, type):
        return {
            "kind": "class",
            "bases": [f"{base.__module__}.{base.__qualname__}" for base in value.__bases__],
        }
    if callable(value):
        return {
            "kind": "function",
            "parameters": [
                _parameter(parameter)
                for parameter in inspect.signature(value).parameters.values()
            ],
        }
    return {"kind": "value", "value": value}


def _parameter(parameter: inspect.Parameter) -> dict[str, str]:
    entry = {"name": parameter.name, "kind": parameter.kind.name}
    if parameter.default is not inspect.Parameter.empty:
        entry["default"] = repr(parameter.default)
    return entry


def moved_name(staged: str) -> str:
    """A staged dotted name, rewritten to the module it moved to."""
    for old, new in MOVED.items():
        if staged.startswith(old):
            return new + staged.removeprefix(old)
    return staged


def _as_moved(description: dict[str, Any]) -> dict[str, Any]:
    if description["kind"] == "module":
        return {**description, "module": moved_name(description["module"])}
    if description["kind"] == "class":
        return {**description, "bases": [moved_name(base) for base in description["bases"]]}
    return description


def _recorded() -> dict[str, dict[str, Any]]:
    names: dict[str, dict[str, Any]] = json.loads(TABLE.read_text())["names"]
    return names


def test_the_table_records_exactly_the_consumer_names() -> None:
    assert sorted(_recorded()) == NAMES
    assert len(NAMES) == 32


@pytest.mark.parametrize("name", NAMES)
def test_a_consumer_name_exists_with_its_pre_move_shape(name: str) -> None:
    module_name, attribute = name.split(".")
    module = importlib.import_module(f"sysml_codegen.study.{module_name}")
    assert hasattr(module, attribute), f"sysml_codegen.study.{name} is missing"
    assert describe(getattr(module, attribute)) == _as_moved(_recorded()[name])
