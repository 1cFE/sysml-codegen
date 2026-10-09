"""REQ-DM-08: surviving name wrappers and constructors retain their NewType surface."""

import ast
import inspect
import textwrap

import pytest

from sysml_codegen.core import identifier_types

# Hand-authored expectation: wrapper name -> base type it must wrap.
# (Enumerated from ADR/27-typed-registry-refactor.md, not read off the code.)
EXPECTED_WRAPPERS_OVER_STR = ["SysMLQN", "EQN", "PQN", "CanonicalChannel", "ScopedKey"]

# Hand-authored expectation: constructor -> return-annotation NewType name.
EXPECTED_CONSTRUCTOR_RETURNS = {
    "make_scoped_key": "ScopedKey",
    "make_canonical_channel": "CanonicalChannel",
}


def _annotation_ids(node: ast.expr) -> list[str]:
    """Flatten an annotation expression into its Name identifiers, in order.

    ``dict[ScopedKey, CanonicalChannel]`` -> ["dict", "ScopedKey", "CanonicalChannel"].
    """
    return [n.id for n in ast.walk(node) if isinstance(n, ast.Name)]


class TestDM08EnforcedSurface:
    """REQ-DM-08: NewType wrappers exist and the enforced surface carries them."""

    @pytest.mark.req("REQ-DM-08")
    def test_wrappers_are_newtype_over_base(self):
        """(a) Each wrapper is a genuine NewType over its documented base."""
        for name in EXPECTED_WRAPPERS_OVER_STR:
            wrapper = getattr(identifier_types, name)
            assert getattr(wrapper, "__supertype__", None) is str, (
                f"{name} is not a NewType over str"
            )
        alias_key = identifier_types.ScopedAliasKey
        assert getattr(alias_key, "__supertype__", None) == tuple[str, str], (
            "ScopedAliasKey is not a NewType over tuple[str, str]"
        )

    @pytest.mark.req("REQ-DM-08")
    def test_make_constructor_return_annotations_name_newtypes(self):
        """(c) The make_* constructors are annotated to return their NewType."""
        src = textwrap.dedent(inspect.getsource(identifier_types))
        tree = ast.parse(src)

        returns: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in EXPECTED_CONSTRUCTOR_RETURNS:
                assert node.returns is not None, f"{node.name} has no return annotation"
                ids = _annotation_ids(node.returns)
                assert len(ids) == 1, f"{node.name} return annotation unexpectedly complex: {ids}"
                returns[node.name] = ids[0]

        for fn, expected_ret in EXPECTED_CONSTRUCTOR_RETURNS.items():
            assert returns.get(fn) == expected_ret, (
                f"{fn} return annotation is {returns.get(fn)!r}, expected {expected_ret!r}"
            )
