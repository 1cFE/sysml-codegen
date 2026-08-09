"""Elaborate-then-project front end (ELABORATE-FIRST epic).

``elaborate()`` turns a loaded SysIDE model into an :class:`InstanceGraph` —
one attribute node per modeled value occurrence, consumers holding typed node
references. Projection onto the existing ``ComputationGraph`` seam remains an
internal Item-5 route; until the Item-6 cutover it never becomes a shipped flag.
"""

from sysml_codegen.elaboration.elaborate import (
    ElaborationDiagnosticError,
    ElaborationError,
    elaborate,
)
from sysml_codegen.elaboration.graph import (
    AttrNode,
    CalcNode,
    ConstraintNode,
    Diagnostic,
    ElaborationCode,
    GraphValidationError,
    InputRef,
    InstanceGraph,
    LiteralInput,
    NodeRef,
    PortMetadata,
    ProducerRef,
    ValueSite,
)
from sysml_codegen.elaboration.identity import (
    ConsumerPortId,
    DeclarationId,
    ExpressionPortId,
    FeatureSlotId,
    NodeId,
    NodeKind,
    OccurrenceId,
    OccurrenceStep,
    OutputPortId,
    PackageScopeId,
    ResolvedSemanticReference,
    ScopeId,
)
from sysml_codegen.elaboration.project import ProjectionError, project

__all__ = [
    "AttrNode",
    "CalcNode",
    "ConstraintNode",
    "ConsumerPortId",
    "DeclarationId",
    "Diagnostic",
    "ElaborationCode",
    "ElaborationDiagnosticError",
    "ElaborationError",
    "ExpressionPortId",
    "FeatureSlotId",
    "GraphValidationError",
    "InputRef",
    "InstanceGraph",
    "LiteralInput",
    "NodeRef",
    "NodeId",
    "NodeKind",
    "OccurrenceId",
    "OccurrenceStep",
    "OutputPortId",
    "PackageScopeId",
    "PortMetadata",
    "ProducerRef",
    "ProjectionError",
    "ResolvedSemanticReference",
    "ScopeId",
    "ValueSite",
    "elaborate",
    "project",
]
