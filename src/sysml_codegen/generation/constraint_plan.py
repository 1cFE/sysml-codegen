"""Read-only constraint generation plan built before output-tree mutation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import jinja2

    from sysml_codegen.orchestration.pipeline_context import PipelineContext


@dataclass(frozen=True)
class ConstraintGenerationPlan:
    """Fully compiled and rendered constraint artifacts ready for emission."""

    compiled_predicates: Mapping[str, tuple[str, str, list[str]]]
    predicates_code: str | None
    rendered_modules: Mapping[str, str]


def build_constraint_generation_plan(
    ctx: PipelineContext,
    template_env: jinja2.Environment,
    package_name: str,
) -> ConstraintGenerationPlan:
    """Validate, compile, and render all constraint artifacts without filesystem writes."""
    from sysml_codegen.generation.modules import (
        compile_shared_predicates,
        render_constraint_module,
        render_constraint_predicates_module,
        render_report_aggregator,
    )
    from sysml_codegen.resolution.models import ModuleKind

    catalog = ctx.computation_graph.constraint_catalog
    if catalog is None:
        return ConstraintGenerationPlan(MappingProxyType({}), None, MappingProxyType({}))

    compiled = compile_shared_predicates(catalog)
    predicates_code = render_constraint_predicates_module(compiled, template_env)
    rendered: dict[str, str] = {}
    for module in ctx.computation_graph.modules:
        if module.module_kind is ModuleKind.CONSTRAINT:
            rendered[module.name] = render_constraint_module(
                module, catalog, compiled, template_env, package_name
            )
        elif module.module_kind is ModuleKind.REPORT_AGGREGATOR:
            rendered[module.name] = render_report_aggregator(
                module, catalog, template_env, package_name
            )
    return ConstraintGenerationPlan(
        MappingProxyType(dict(compiled)),
        predicates_code,
        MappingProxyType(rendered),
    )
