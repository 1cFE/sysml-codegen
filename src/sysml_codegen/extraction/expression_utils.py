"""Compatibility shim for shared SysML expression utilities.

Note: the authored-name helpers (``extract_feature_chain_name``,
``extract_feature_chain_segments``, ``extract_feature_reference_name``) are gone
upstream. The authored spelling is evidence now and travels on
``ExactReferenceUse``; :func:`authored_chain_segments` reads it from there.

The implementation lives in ``agentic_mbse.sysml.expression``. This module is a
permanent compatibility path for sysml-codegen callers and conformance tests.
"""

from typing import Any

from agentic_mbse.sysml.expression import (
    OPERATOR_MAP,
    RANK,
    RIGHT_ASSOC,
    UNARY_RANK,
    binary_op_of,
    extract_literal_value,
    is_literal_node,
    needs_parens,
    reconstruct_expression,
    reconstruct_operator_expression,
)
from agentic_mbse.sysml.reference_use import ExactReferenceUse, inspect_reference_uses
from agentic_mbse.sysml.syside_adapter import SysideAdapter

is_literal_expression = is_literal_node


def authored_chain_segments(expression: Any) -> list[str]:
    """The authored dotted segments of one feature chain, or ``[]``.

    The authored spelling now travels on the exact reference use itself, so this asks
    the one inspection operation rather than re-walking the chain. An indexed use has
    no segments to report: the index is the reason it has no path.
    """
    uses = inspect_reference_uses(expression)
    if len(uses) != 1 or not isinstance(uses[0], ExactReferenceUse):
        return []
    return list(uses[0].authored_segments)

__all__ = [
    "authored_chain_segments",
    "OPERATOR_MAP",
    "RANK",
    "UNARY_RANK",
    "RIGHT_ASSOC",
    "binary_op_of",
    "needs_parens",
    "reconstruct_expression",
    "reconstruct_operator_expression",
    "is_literal_expression",
    "is_literal_node",
    "extract_literal_value",
    "SysideAdapter",
]
