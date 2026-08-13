"""A1 (a): does the sealed public route name a usage a projection defect dropped?

Simulates the defect the preflight's seal check cannot see — a projection that renders
fewer usage rows than the domain holds, and seals that shorter list coherently. The
receipt re-projects from the sealed instance bytes, so it still has the domain to compare
against.
"""

from pathlib import Path

from sysml_codegen.orchestration import exact_pipeline_context as ctx_module
from sysml_codegen.orchestration.exact_pipeline_context import build_exact_pipeline_context

FIXTURE = Path("tests/fixtures/catf_mfe_d5")
_real_project = ctx_module._project_or_fail


def _dropping_project(graph, targets):
    """Render the catalog, then drop one NON-REACHING row and re-seal it coherently.

    Patched BEFORE the context is built, so the seal and every later read both go through
    the same defective projection. That is what a real projection defect looks like: the
    receipt's own digest agrees with itself, and the catalog is internally consistent. Only
    a check that still holds the domain can see it.
    """
    projected = _real_project(graph, targets)
    catalog = projected.constraint_catalog
    if catalog is not None:
        victim = next(r for r in catalog.usage_records if r.occurrence_count == 0)
        catalog.usage_records.remove(victim)
        object.__setattr__(catalog, "fingerprint", catalog.recomputed_fingerprint())
    return projected


ctx_module._project_or_fail = _dropping_project
try:
    context = build_exact_pipeline_context([FIXTURE])
    context.computation_graph
    print("RESULT: no refusal — the receipt did not notice")
except Exception as error:  # noqa: BLE001 - a probe reports whatever it gets
    print(f"RESULT: refused -> {error}")
finally:
    ctx_module._project_or_fail = _real_project
