"""Elaborate-then-project front end (ELABORATE-FIRST epic).

The public source routes own model loading and error conversion. This package
exports the graph vocabulary and projector; its raw graph builder is private.
"""

from sysml_codegen.elaboration.elaborate import (
    ElaborationDiagnosticError,
    ElaborationError,
)
from sysml_codegen.elaboration.graph import (
    ASSERTED_SOURCE_FORMS,
    AttrNode,
    CalcNode,
    ConstraintNode,
    ConstraintUsageRecord,
    Diagnostic,
    ElaborationCode,
    FormalProvenance,
    GraphValidationError,
    Inapplicability,
    InputRef,
    InstanceGraph,
    LiteralInput,
    NodeRef,
    OccurrenceRecord,
    PortMetadata,
    ProducerRef,
    UsageDisposition,
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
    "ASSERTED_SOURCE_FORMS",
    "AttrNode",
    "CalcNode",
    "ConstraintNode",
    "ConstraintUsageRecord",
    "Inapplicability",
    "UsageDisposition",
    "ConsumerPortId",
    "DeclarationId",
    "Diagnostic",
    "ElaborationCode",
    "ElaborationDiagnosticError",
    "ElaborationError",
    "ExpressionPortId",
    "FeatureSlotId",
    "FormalProvenance",
    "GraphValidationError",
    "InputRef",
    "InstanceGraph",
    "LiteralInput",
    "NodeRef",
    "NodeId",
    "NodeKind",
    "OccurrenceId",
    "OccurrenceRecord",
    "OccurrenceStep",
    "OutputPortId",
    "PackageScopeId",
    "PortMetadata",
    "ProducerRef",
    "ProjectionError",
    "ResolvedSemanticReference",
    "ScopeId",
    "ValueSite",
    "project",
]
