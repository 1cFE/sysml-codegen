"""Read-only constraint generation plan built before output-tree mutation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import jinja2

    from sysml_codegen.generation.coverage import CoverageAccountData
    from sysml_codegen.resolution.models import ComputationGraph


@dataclass(frozen=True)
class ConstraintGenerationPlan:
    """Fully compiled and rendered constraint artifacts ready for emission."""

    compiled_predicates: Mapping[str, tuple[str, str, list[str]]]
    predicates_code: str | None
    rendered_modules: Mapping[str, str]
    #: The coverage account this graph's catalog implies, computed once here so the renderer
    #: and the preflight read one value rather than two derivations of one fact. ``None`` iff
    #: the graph carries no catalog.
    coverage: CoverageAccountData | None = None


def build_constraint_generation_plan(
    graph: ComputationGraph,
    template_env: jinja2.Environment,
    package_name: str,
) -> ConstraintGenerationPlan:
    """Validate, compile, and render all constraint artifacts without filesystem writes."""
    from sysml_codegen.generation.coverage import coverage_account
    from sysml_codegen.generation.modules import (
        compile_shared_predicates,
        render_constraint_module,
        render_constraint_predicates_module,
        render_report_aggregator,
    )
    from sysml_codegen.resolution.models import ModuleKind

    catalog = graph.constraint_catalog
    if catalog is None:
        return ConstraintGenerationPlan(MappingProxyType({}), None, MappingProxyType({}))

    # Before anything is compiled or rendered: D9's refusal and the reason-vocabulary pin
    # both raise from here, so an authoring contradiction stops the run at plan build —
    # earlier than the preflight, and long before the output tree is touched either way.
    coverage = coverage_account(catalog)
    compiled = compile_shared_predicates(catalog)
    predicates_code = render_constraint_predicates_module(compiled, template_env)
    rendered: dict[str, str] = {}
    for module in graph.modules:
        if module.module_kind is ModuleKind.CONSTRAINT:
            rendered[module.name] = render_constraint_module(
                module, catalog, compiled, template_env, package_name
            )
        elif module.module_kind is ModuleKind.REPORT_AGGREGATOR:
            rendered[module.name] = render_report_aggregator(
                module, catalog, coverage, template_env, package_name
            )
    return ConstraintGenerationPlan(
        MappingProxyType(dict(compiled)),
        predicates_code,
        MappingProxyType(rendered),
        coverage,
    )
