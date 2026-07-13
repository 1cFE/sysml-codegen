"""Implementation stencil generator with SysML traceability.

Generates handwritten implementation function stubs that preserve SysML
calc expressions and source file:line references for traceability.

Provides unified dispatch between auto-implementation (for FULLY_COMPILABLE
modules) and NotImplementedError stub templates.

Usage:
    from sysml_codegen.generation.stencils import generate_implementation

    code = generate_implementation(module, template_env, output_path)
"""

from pathlib import Path

import jinja2

from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName


def _output_attr_name(out) -> str:
    """Get original output attribute name from ModuleOutput.

    For multi-output modules, field_name IS the attribute name.
    For single-output modules, field_name is "root" -- extract from channel_name.
    Channel name format: {usage_eqn}__{attr_name} (PQN format).
    """
    if out.field_name != "root":
        return out.field_name
    return out.channel_name.split("__")[-1]


def _get_module_sysml_qn(module) -> str:
    """Get the full SysML qualified name for path/import derivation.

    Module types store calc_def_qualified_name differently:
    - CalcUsage: full calc def QN (e.g., "Package::CalcDef")
    - FORMULA: owning part QN only → append "::calc_def_name"
    - Aggregation: owning part QN with __ separator → use module.name with :: separator
    """
    from sysml_codegen.generation.errors import unrenderable_module_kind_error
    from sysml_codegen.resolution.models import ModuleKind

    if module.module_kind == ModuleKind.FORMULA:
        return f"{module.calc_def_qualified_name}::{module.calc_def_name}"
    elif module.module_kind == ModuleKind.AGGREGATION:
        return module.name.replace("__", "::")
    elif module.module_kind == ModuleKind.CALCULATION:
        return module.calc_def_qualified_name
    else:
        raise unrenderable_module_kind_error(module, "stencil")


def _build_stub_docstring_from_graph(module) -> str:
    """Build stub docstring from PipelineModule fields."""
    lines = []

    # Derive output info from module outputs
    output_names = []
    for out in module.outputs:
        output_names.append(_output_attr_name(out))

    lines.append(f"Execute {module.calc_def_name} calculation.")

    if module.doc_comment:
        lines.append("")
        lines.append(module.doc_comment.strip())

    lines.append("")
    lines.append(f"SysML Source: {module.source_file}:{module.source_line}")

    if module.calc_expressions:
        lines.append("")
        lines.append("SysML Expressions:")
        for expr in module.calc_expressions:
            lines.append(f"    {expr}")

    lines.append("")
    lines.append("Args:")
    lines.append(
        f"    inputs: Input parameters validated against {module.calc_def_name}Input schema"
    )

    if len(module.outputs) == 1:
        out = module.outputs[0]
        out_name = _output_attr_name(out)
        desc = out.description or out_name
        lines.append("")
        lines.append("Returns:")
        lines.append(f"    float: {desc}")
    elif len(module.outputs) > 1:
        names = ", ".join(output_names)
        lines.append("")
        lines.append("Returns:")
        lines.append(f"    tuple[float, ...]: ({names})")

    lines.append("")
    lines.append("Example:")
    lines.append(f"    >>> inputs = {module.calc_def_name}Input(...)")
    func_name = f"run_{module.calc_def_name.lower()}"
    if len(module.outputs) > 1:
        output_vars = ", ".join(output_names)
        lines.append(f"    >>> {output_vars} = {func_name}(inputs)")
    else:
        lines.append(f"    >>> result = {func_name}(inputs)")

    return "\n".join(lines)


def _build_stencil_context_from_graph(module, output_path, package_name="generated_code"):
    """Build shared template context from PipelineModule fields."""
    output_names = [_output_attr_name(out) for out in module.outputs]

    if len(module.outputs) == 0:
        return_type = "None"
    elif len(module.outputs) == 1:
        return_type = "float"
    else:
        return_types = ", ".join(["float"] * len(module.outputs))
        return_type = f"tuple[{return_types}]"

    input_params = [
        {"name": inp.param_name, "type": inp.python_type}
        for inp in module.inputs
    ]

    calc_expressions = module.calc_expressions or []

    # Derive path from full SysML QN (module-type-aware)
    sysml_qn = _get_module_sysml_qn(module)
    sqn = SysMLQualifiedName(sysml_qn)
    python_path = PythonModulePath.from_sysml(sqn)
    module_import_path = python_path.import_path

    # Class name from module_type (correct PascalCase for all module types)
    class_name = module.module_type.split(".")[-1]
    base_name = class_name.removesuffix("Module")

    return {
        "function_name": f"run_{module.calc_def_name.lower()}",
        "calc_name": module.calc_def_name,
        "sysml_source": f"{module.source_file}:{module.source_line}",
        "sysml_expressions": calc_expressions,
        "input_params": input_params,
        "output_names": output_names,
        "return_type": return_type,
        "docstring": _build_stub_docstring_from_graph(module),
        "input_class_name": f"{base_name}Input",
        "module_name": module.calc_def_name.lower(),
        "module_import_path": module_import_path,
        "package_name": package_name,
    }


def generate_implementation(
    module,
    template_env: jinja2.Environment,
    output_path: Path,
    package_name: str = "generated_code",
) -> str:
    """Generate implementation from PipelineModule.

    Dispatches to auto-implementation template when module.auto_impl_context
    is populated (FULLY_COMPILABLE), or to stub template otherwise.

    Args:
        module: PipelineModule with metadata fields populated
        template_env: Jinja2 environment
        output_path: Where to write handwritten/ file
        package_name: Package name for imports

    Returns:
        Generated Python code
    """
    context = _build_stencil_context_from_graph(module, output_path, package_name)

    if module.auto_impl_context is not None:
        context.update(module.auto_impl_context)
        template = template_env.get_template("auto_implementation.py.jinja2")
    else:
        template = template_env.get_template("implementation_stencil.py.jinja2")

    code = template.render(**context)
    if not code.endswith('\n'):
        code += '\n'
    return code


# Keep old name as alias for backward compatibility during transition
generate_implementation_from_graph = generate_implementation


def generate_backlog_report(
    graph,
    output_path: Path,
    package_name: str = "generated_code",
) -> str:
    """Generate backlog report from ComputationGraph.

    Args:
        graph: ComputationGraph with modules
        output_path: Where to write IMPLEMENTATION_BACKLOG.md
        package_name: Package name

    Returns:
        Generated markdown string
    """
    from sysml_codegen.resolution.models import ModuleKind

    items = []
    auto_formula_count = 0
    auto_agg_count = 0

    for module in graph.modules:
        if module.module_kind == ModuleKind.FORMULA:
            if module.auto_impl_context is not None:
                auto_formula_count += 1
            continue
        elif module.module_kind == ModuleKind.AGGREGATION:
            if module.auto_impl_context is not None:
                auto_agg_count += 1
            continue
        elif module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
            # D8: fully generated, no handwritten implementation to backlog.
            continue

        # Skip FULLY_COMPILABLE CalcUsage modules
        if module.auto_impl_context is not None:
            continue

        # Estimate complexity from calc_expressions
        total_ops = 0
        for expr in (module.calc_expressions or []):
            total_ops += expr.count("+") + expr.count("*") + expr.count("/") + expr.count("-")
        if total_ops <= 5:
            complexity = "Low"
        elif total_ops <= 15:
            complexity = "Medium"
        else:
            complexity = "High"

        source_file = module.source_file or "unknown"
        source_line = module.source_line or 0
        source_path = str(source_file)
        if "models/" in source_path:
            source_path = "models/" + source_path.split("models/", 1)[1]
        else:
            source_path = Path(source_path).name

        items.append({
            "module": module.calc_def_name,
            "function": f"run_{module.calc_def_name.lower()}",
            "source": f"{source_path}:{source_line}",
            "complexity": complexity,
        })

    lines = [
        "# Implementation Backlog",
        "",
        "This document tracks the implementation of SysML calculation definitions.",
        "Complete all stages in order for a production-ready system.",
        "",
        "---",
        "",
        "## Stage 1: Implement Calculation Functions",
        "",
        "**Objective**: Implement each calculation definition in its handwritten file.",
        "",
        f"**Total**: {len(items)} functions to implement",
        "",
        "**Instructions for each function**:",
        "1. Open the SysML source file at the line number shown below",
        "2. Review the calculation expressions and constraints in SysML",
        f"3. Open the corresponding `*_impl.py` file in `{package_name}/handwritten/`",
        "4. Replace `raise NotImplementedError(...)` with actual calculation logic",
        "5. Ensure the function returns correct type (single float or tuple of floats)",
        f"6. Test: `python -c \"from {package_name}.modules.<module> import <Module>\"`",
        "",
        "**Complexity Guide**:",
        "- **Low**: Simple arithmetic (1-5 operations)",
        "- **Medium**: Multiple terms, some conditional logic (6-15 operations)",
        "- **High**: Complex logic, loops, or external dependencies (15+ operations)",
        "",
        "| Status | Module | Function | SysML Source | Complexity |",
        "|--------|--------|----------|--------------|------------|",
    ]

    for item in items:
        lines.append(
            f"| [ ] | {item['module']} | `{item['function']}` | "
            f"`{item['source']}` | {item['complexity']} |"
        )

    if auto_formula_count > 0:
        lines.extend([
            "",
            f"**{auto_formula_count} computed attribute module(s) auto-implemented** "
            "(not included in manual count above).",
        ])

    if auto_agg_count > 0:
        lines.extend([
            "",
            f"**{auto_agg_count} aggregation module(s) auto-implemented** "
            "(not included in manual count above).",
        ])

    lines.extend([
        "",
        "---",
        "",
        "## Stage 2: Verification",
        "",
        "**Objective**: Verify implementations work correctly.",
        "",
        "**Instructions**:",
        "",
        "### 2.1 Type Checking",
        "Run pyright to catch typing errors:",
        "```bash",
        f"pyright {package_name}/",
        "```",
        "Expected: 0 errors (should stay clean during implementation)",
        "",
        "### 2.2 Implementation Tests",
        "Run verification tests:",
        "```bash",
        "pytest tests/test_implementations_runnable.py -v",
        "```",
        "All tests should pass (or pytest.skip for NotImplementedError stubs)",
        "",
        "**Test Coverage**:",
        f"- {len(items)} implementation functions",
        "- Each function tested for: imports, signature, return type",
        "- Tests tolerate NotImplementedError (pass before implementation)",
        "- Tests verify return types (pass after implementation)",
        "",
        "**Checklist**:",
        "- [ ] Pyright passes (0 errors)",
        "- [ ] Verification tests pass",
        "- [ ] All implementations return correct types",
        "",
        "**Note**: Import validation and ruff linting performed separately by maintainers.",
        "",
        "---",
        "",
        "## Stage 3: Integration Testing",
        "",
        "**Objective**: Verify the full pipeline works end-to-end.",
        "",
        "**Instructions**:",
        f"1. Create a test pipeline configuration in `{package_name}/pipelines/`",
        "2. Run the pipeline with sample inputs",
        "3. Verify outputs match expected values from SysML models",
        "4. Document any discrepancies and resolve",
        "",
        "**Checklist**:",
        "- [ ] Test pipeline created",
        "- [ ] Pipeline runs without errors",
        "- [ ] Outputs validated against SysML models",
        "- [ ] All discrepancies resolved",
        "",
        "---",
        "",
        "## Completion Criteria",
        "",
        "The implementation is complete when:",
        f"- Stage 1: All {len(items)} functions implemented",
        "- Stage 2: All validations pass",
        "- Stage 3: Integration tests pass",
        "",
        "**Next Steps**: Deploy to production environment or integrate with larger system.",
    ])

    markdown = "\n".join(lines)
    if not markdown.endswith('\n'):
        markdown += '\n'
    return markdown


# Keep old name as alias for backward compatibility during transition
generate_backlog_report_from_graph = generate_backlog_report


__all__ = [
    "generate_backlog_report",
    "generate_backlog_report_from_graph",
    "generate_implementation",
    "generate_implementation_from_graph",
]
