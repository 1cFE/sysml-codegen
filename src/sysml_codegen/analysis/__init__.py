"""Analysis layer for SysML code generation.

This layer provides analysis capabilities for extracted SysML data:
- Parameter group derivation for entry point organization
- Phantom entry point detection for binding validation
- Dependency backtracking for pipeline ordering
- Qualified name utilities for identifier handling
- Signature extraction for implementation preservation
"""

from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    CircularDependencyError,
    DependencyBacktracker,
    TargetNotFoundError,
)
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    ParameterGroupDeriver,
)
from sysml_codegen.analysis.phantom_detector import (
    DomainKeywords,
    PhantomCandidate,
    PhantomDetectionReport,
    PhantomDetector,
)
# Re-export from core for backward compatibility
from sysml_codegen.core.qualified_names import (
    sanitize_name,
    sysml_to_python_qualified_name,
)
from sysml_codegen.analysis.signature_extractor import (
    FunctionSignature,
    extract_signature_from_impl,
    generate_expected_signature,
)

__all__ = [
    # dependency_backtracker
    "BacktrackingResult",
    "CircularDependencyError",
    "DependencyBacktracker",
    "TargetNotFoundError",
    # parameter_groups
    "DesignAttributeData",
    "ParameterGroupDeriver",
    # phantom_detector
    "DomainKeywords",
    "PhantomCandidate",
    "PhantomDetectionReport",
    "PhantomDetector",
    # qualified_names
    "sanitize_name",
    "sysml_to_python_qualified_name",
    # signature_extractor
    "FunctionSignature",
    "extract_signature_from_impl",
    "generate_expected_signature",
]
