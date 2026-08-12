"""REQ-DM-08: the typed-registry enforced surface uses NewType wrappers.

The enforced surface is exactly three parts (the canonical definition,
matrix-test-gaps spec):

  (a) the wrappers in ``core/identifier_types.py`` are genuine ``NewType``s
      over their documented bases;
  (b) the four ``OutputRegistry.__init__`` registry-dict annotations carry
      NewType keys and values;
  (c) the ``make_scoped_key`` / ``make_canonical_channel`` constructors are
      annotated to return their NewType.

Mechanism note (load-bearing): (b) and (c) are **AST scans** of the source,
not ``get_type_hints``. The registry annotations are PEP-526 ``self._x: …``
assignments inside ``__init__`` — they never reach any ``__annotations__``,
so a runtime-introspection test would stay green if a registry dict were
re-annotated to ``dict[str, str]``. The AST scan goes red under exactly that
mutation. Sibling pattern: ``test_orchestrator._get_call_lines_in_function``.

Deliberately OUT of the surface: ``register_alias``'s ``ScopedKey | str`` /
``CanonicalChannel | str`` params (a designed union, not drift), and the
``resolution/models.py`` field annotations — those are documented as bare
``str`` with the deferral filed under ``[DM08-MODEL-FIELD-TYPING]``
(see 09-data-models.md "REQ-DM-08 is open" note).
"""

import ast
import inspect
import textwrap

import pytest

from sysml_codegen.core import identifier_types

# Hand-authored expectation: wrapper name -> base type it must wrap.
# (Enumerated from ADR/27-typed-registry-refactor.md, not read off the code.)
EXPECTED_WRAPPERS_OVER_STR = ["SysMLQN", "EQN", "PQN", "CanonicalChannel", "ScopedKey"]

# Hand-authored expectation: registry dict attribute -> (key NewType, value NewType).
EXPECTED_REGISTRY_ANNOTATIONS = {
    "_scoped": ("ScopedKey", "CanonicalChannel"),
    "_sysml_qn": ("SysMLQN", "CanonicalChannel"),
    "_alias": ("ScopedKey", "CanonicalChannel"),
    "_scoped_alias": ("ScopedAliasKey", "CanonicalChannel"),
}

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

    # (b) — the AST scan asserting the four ``OutputRegistry.__init__`` dicts are
    # annotated ``dict[NewType, NewType]`` — retired with the v5 family (retirement
    # step 2) together with ``core/output_registry.py`` (L-007), per the per-node
    # disposition on ledger L-125. (a) and (c), the NewType wrappers themselves in the
    # retained ``core/identifier_types.py``, are unaffected.
    def _retired_registry_dict_annotations(self):
        from sysml_codegen.core.output_registry import OutputRegistry

        src = textwrap.dedent(inspect.getsource(OutputRegistry.__init__))
        tree = ast.parse(src)

        found: dict[str, list[str]] = {}
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Attribute)
                and isinstance(node.target.value, ast.Name)
                and node.target.value.id == "self"
            ):
                found[node.target.attr] = _annotation_ids(node.annotation)

        for attr, (key_t, val_t) in EXPECTED_REGISTRY_ANNOTATIONS.items():
            assert attr in found, f"OutputRegistry.__init__ has no annotation for self.{attr}"
            ids = found[attr]
            assert ids[0] == "dict", f"self.{attr} is not annotated as a dict: {ids}"
            assert key_t in ids and val_t in ids, (
                f"self.{attr} annotation {ids} does not carry the NewTypes "
                f"({key_t}, {val_t}) — the typed-registry surface has drifted"
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
