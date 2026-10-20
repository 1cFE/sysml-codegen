"""The name-based call closure follows each form it claims to, and no further (Item 2b D14).

Each case is a small synthetic ``sysml_codegen`` tree. The closure is over-approximate by
design, so these pin what it must reach; the cases that must stay unreached are the scoping
rules that keep it from reaching everything: a nested function is visible only from its
enclosing function, a method only through an attribute, and an annotation is not a call.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from tests.helpers.subset_profile import site_scan


def _tree(tmp_path: Path, modules: dict[str, str]) -> Path:
    for name, source in modules.items():
        path = tmp_path / "sysml_codegen" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(source))
    return tmp_path


def _reach(tmp_path: Path, modules: dict[str, str], root: str) -> set[str]:
    src = _tree(tmp_path, modules)
    file, function = root.split("::")
    reached = site_scan.call_closure([(f"sysml_codegen/{file}", function)], codegen_src=src)
    return {f"{Path(f).name}::{fn}" for f, fn in reached}


def test_a_call_across_modules_and_through_an_import_alias(tmp_path):
    reached = _reach(
        tmp_path,
        {
            "a.py": """
                from sysml_codegen.b import helper as renamed
                def root():
                    renamed()
            """,
            "b.py": "def helper():\n    deeper()\ndef deeper():\n    pass\n"
            "def unused():\n    pass\n",
        },
        "a.py::root",
    )
    assert reached == {"a.py::root", "b.py::helper", "b.py::deeper"}


def test_a_module_level_alias_is_followed_from_another_module(tmp_path):
    reached = _reach(
        tmp_path,
        {
            "a.py": "from sysml_codegen.b import public\ndef root():\n    public()\n",
            "b.py": "def real():\n    pass\npublic = real\n",
        },
        "a.py::root",
    )
    assert "b.py::real" in reached


def test_a_function_passed_by_name_is_reached(tmp_path):
    reached = _reach(
        tmp_path,
        {"a.py": "def root(xs):\n    return sorted(xs, key=keyfn)\ndef keyfn(x):\n    return x\n"},
        "a.py::root",
    )
    assert "a.py::keyfn" in reached


def test_construction_reaches_init_and_the_base_init(tmp_path):
    reached = _reach(
        tmp_path,
        {
            "a.py": """
                class Base:
                    def __init__(self):
                        self.checked()
                    def checked(self):
                        pass
                    def other(self):
                        pass
                class Child(Base):
                    def __init__(self):
                        super().__init__()
                def root():
                    Child()
            """,
        },
        "a.py::root",
    )
    assert {"a.py::Child.__init__", "a.py::Base.__init__", "a.py::Base.checked"} <= reached
    assert "a.py::Base.other" not in reached


def test_a_property_is_reached_by_attribute_load(tmp_path):
    reached = _reach(
        tmp_path,
        {
            "a.py": """
                class C:
                    @property
                    def graph(self):
                        return build()
                def build():
                    pass
                def root(c):
                    return c.graph
            """,
        },
        "a.py::root",
    )
    assert {"a.py::C.graph", "a.py::build"} <= reached


@pytest.mark.parametrize(
    ("source", "unreached"),
    [
        # A nested function is visible only inside its enclosing function.
        (
            "def other():\n    def render():\n        pass\n    render()\n"
            "def root(t):\n    t.render()\n",
            "a.py::other.render",
        ),
        # A method is not reached by a bare call of its name.
        (
            "class C:\n    def helper(self):\n        pass\ndef root():\n    helper()\n",
            "a.py::C.helper",
        ),
        # An annotation names a type; it runs nothing.
        (
            "class Graph:\n    def __init__(self):\n        pass\n"
            "def root(g: Graph) -> Graph:\n    return g\n",
            "a.py::Graph.__init__",
        ),
        # A plain attribute load is not a call unless it names a property.
        (
            "class C:\n    def size(self):\n        pass\ndef root(c):\n    return c.size\n",
            "a.py::C.size",
        ),
    ],
    ids=["nested-scope", "method-by-bare-name", "annotation", "attribute-load"],
)
def test_scoping_keeps_the_closure_from_reaching(tmp_path, source, unreached):
    assert unreached not in _reach(tmp_path, {"a.py": source}, "a.py::root")


def test_an_unknown_root_fails_loudly(tmp_path):
    with pytest.raises(KeyError, match="no such function"):
        _reach(tmp_path, {"a.py": "def root():\n    pass\n"}, "a.py::absent")
