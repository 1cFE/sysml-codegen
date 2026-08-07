"""Elaborate-then-project front end (ELABORATE-FIRST epic).

``elaborate()`` turns a loaded SysIDE model into an :class:`InstanceGraph` —
one attribute node per modeled value occurrence, consumers holding typed node
references. Projection onto the existing ``ComputationGraph`` seam follows in
a later item phase; until the Item-6 cutover this front end runs only behind
internal dual-run entry points, never a shipped flag.
"""

from sysml_codegen.elaboration.elaborate import ElaborationError, elaborate
from sysml_codegen.elaboration.graph import (
    AttrNode,
    CalcNode,
    ConstraintNode,
    Diagnostic,
    ElaborationCode,
    InputRef,
    InstanceGraph,
    LiteralInput,
    NodeRef,
    ProducerRef,
    ValueSite,
)

__all__ = [
    "AttrNode",
    "CalcNode",
    "ConstraintNode",
    "Diagnostic",
    "ElaborationCode",
    "ElaborationError",
    "InputRef",
    "InstanceGraph",
    "LiteralInput",
    "NodeRef",
    "ProducerRef",
    "ValueSite",
    "elaborate",
]
