"""Compatibility shim for shared SysML expression utilities.

The implementation lives in ``agentic_mbse.sysml.expression``. This module is a
permanent compatibility path for sysml-codegen callers and conformance tests.
"""

from agentic_mbse.sysml.expression import (
    OPERATOR_MAP,
    RANK,
    RIGHT_ASSOC,
    UNARY_RANK,
    binary_op_of,
    extract_feature_chain_name,
    extract_feature_chain_segments,
    extract_feature_reference_name,
    extract_literal_value,
    is_literal_node,
    needs_parens,
    reconstruct_expression,
    reconstruct_operator_expression,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

is_literal_expression = is_literal_node

__all__ = [
    "OPERATOR_MAP",
    "RANK",
    "UNARY_RANK",
    "RIGHT_ASSOC",
    "binary_op_of",
    "needs_parens",
    "reconstruct_expression",
    "reconstruct_operator_expression",
    "extract_feature_reference_name",
    "extract_feature_chain_name",
    "extract_feature_chain_segments",
    "is_literal_expression",
    "is_literal_node",
    "extract_literal_value",
    "SysideAdapter",
]
