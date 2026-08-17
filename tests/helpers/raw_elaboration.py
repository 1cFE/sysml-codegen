"""Private graph-builder access for internal elaboration tests.

Most of these tests predate the loaded-extractor public boundary and exercise a
synthetic model plus synthetic extracted payload.  Keep that internal seam, but
render its invariant failures with the same public error shape so the assertions
remain about graph semantics rather than the orchestration layer.
"""

from collections.abc import Sequence
from typing import Any

from sysml_codegen.elaboration import Diagnostic, ElaborationDiagnosticError, GraphValidationError
from sysml_codegen.elaboration.diagnostics import ElaborationInvariantError
from sysml_codegen.elaboration.elaborate import _build_instance_graph
from sysml_codegen.elaboration.graph import InstanceGraph


def elaborate(
    model: Any,
    calc_defs: Sequence[Any],
    *,
    validation_diagnostics: Sequence[Any] = (),
    strict: bool = True,
) -> InstanceGraph:
    try:
        return _build_instance_graph(
            model,
            calc_defs,
            validation_diagnostics=validation_diagnostics,
            strict=strict,
        )
    except ElaborationInvariantError as error:
        diagnostic = Diagnostic(
            code=error.code,
            consumer=None,
            consumer_display="<model>",
            param_name=None,
            detail=error.detail,
            reference=error.reference,
            source_file=(error.location[0] if error.location is not None else None),
            source_line=(error.location[1] if error.location is not None else None),
        )
        raise ElaborationDiagnosticError((diagnostic,)) from error
    except GraphValidationError as error:
        raise ElaborationDiagnosticError(error.diagnostics) from error

__all__ = ["elaborate"]
