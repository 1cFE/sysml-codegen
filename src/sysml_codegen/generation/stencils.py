"""Implementation stencil generator with SysML traceability.

Generates handwritten implementation function stubs that preserve SysML
calc expressions and source file:line references for traceability.

Provides unified dispatch between auto-implementation (for FULLY_COMPILABLE
CalcDefs) and NotImplementedError stub templates.

Usage:
    from sysml_codegen.generation.stencils import generate_implementation

    code = generate_implementation(calc_def, template_env, output_path,
                                   compilation_result=result)
"""

from pathlib import Path

import jinja2

from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName

# UPDATED: Import from sysml_codegen package
from sysml_codegen.extraction.data_models import (
    CalculationDefinitionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import (
    CalcDefCompilationResult,
    Compilability,
)
from sysml_codegen.generation.type_mapping import map_sysml_type_to_python


def _build_stub_docstring(calc_def: CalculationDefinitionData) -> str:
    """Build comprehensive stub docstring with usage examples.

    Args:
        calc_def: Calculation definition

    Returns:
        Formatted docstring for implementation function
    """
    lines = []
    output_attrs = calc_def.output_attributes

    # Add purpose
    lines.append(f"Execute {calc_def.name} calculation.")

    # Add description
    if calc_def.doc_comment:
        lines.append("")
        lines.append(calc_def.doc_comment.strip())

    # Add source reference
    lines.append("")
    lines.append(f"SysML Source: {calc_def.source_file}:{calc_def.source_line}")

    # Add SysML expressions
    if calc_def.calc_expressions:
        lines.append("")
        lines.append("SysML Expressions:")
        for expr in calc_def.calc_expressions:
            lines.append(f"    {expr}")

    # Add Args section
    lines.append("")
    lines.append("Args:")
    lines.append(
        f"    inputs: Input parameters validated against {calc_def.name}Input schema"
    )

    # Add Returns section
    if len(output_attrs) == 1:
        desc = output_attrs[0].description or output_attrs[0].name
        lines.append("")
        lines.append("Returns:")
        lines.append(f"    float: {desc}")
    elif len(output_attrs) > 1:
        output_names = ", ".join(attr.name for attr in output_attrs)
        lines.append("")
        lines.append("Returns:")
        lines.append(f"    tuple[float, ...]: ({output_names})")

    # Add usage example
    lines.append("")
    lines.append("Example:")
    lines.append(f"    >>> inputs = {calc_def.name}Input(...)")
    func_name = f"run_{calc_def.name.lower()}"
    if len(output_attrs) > 1:
        output_vars = ", ".join(attr.name for attr in output_attrs)
        lines.append(f"    >>> {output_vars} = {func_name}(inputs)")
    else:
        lines.append(f"    >>> result = {func_name}(inputs)")

    return "\n".join(lines)


def _build_stencil_context(
    calc_def: CalculationDefinitionData,
    output_path: Path,
    package_name: str = "generated_code",
) -> dict:
    """Build shared template context for both stub and auto-impl templates.

    Args:
        calc_def: Calculation definition to implement
        output_path: Where to write handwritten/ file (for future use)
        package_name: Package name for imports

    Returns:
        Dict of template variables shared between stub and auto-impl templates.
    """
    output_attrs = calc_def.output_attributes

    # Determine return type
    if len(output_attrs) == 0:
        return_type = "None"
    elif len(output_attrs) == 1:
        return_type = "float"
    else:
        return_types = ", ".join(["float"] * len(output_attrs))
        return_type = f"tuple[{return_types}]"

    # Extract input parameters
    input_params = [
        {"name": attr.name, "type": map_sysml_type_to_python(attr.sysml_type)}
        for attr in calc_def.input_attributes
    ]

    # Extract calc expressions
    calc_expressions = _extract_calc_expressions(calc_def)

    # ADR-003: Derive namespaced import path for module
    sqn = SysMLQualifiedName(calc_def.qualified_name)
    python_path = PythonModulePath.from_sysml(sqn)
    module_import_path = python_path.import_path

    return {
        "function_name": f"run_{calc_def.name.lower()}",
        "calc_name": calc_def.name,
        "sysml_source": f"{calc_def.source_file}:{calc_def.source_line}",
        "sysml_expressions": calc_expressions,
        "input_params": input_params,
        "output_names": [attr.name for attr in output_attrs],
        "return_type": return_type,
        "docstring": _build_stub_docstring(calc_def),
        "input_class_name": f"{calc_def.name}Input",
        "module_name": calc_def.name.lower(),
        "module_import_path": module_import_path,
        "package_name": package_name,
    }


def _build_auto_impl_context(
    compilation_result: CalcDefCompilationResult,
    calc_def: CalculationDefinitionData,
) -> dict:
    """Build auto-implementation specific template context.

    Separates undeclared intermediates (for local variable assignments)
    from declared outputs (for the return statement), preserving
    topological order for intermediates and output_attributes order
    for the return tuple.

    Args:
        compilation_result: Compilation result from Step 6.5
        calc_def: Calculation definition

    Returns:
        Dict with execution_steps, output_expressions, output_count,
        and single_output_expression.
    """
    output_attr_order = [attr.name for attr in calc_def.output_attributes]
    output_attr_set = set(output_attr_order)
    result_map = {r.output_name: r for r in compilation_result.output_results}

    # Detect declared output cross-references: any declared output's
    # intermediate_refs includes another declared output name.
    has_output_crossrefs = any(
        set(result_map[name].intermediate_refs) & output_attr_set
        for name in output_attr_order
        if name in result_map and result_map[name].intermediate_refs
    )

    execution_steps = []
    output_expressions = []

    if has_output_crossrefs:
        # All entries in execution_order become local variable assignments
        # (both undeclared intermediates AND declared outputs, in topo order)
        for name in compilation_result.execution_order:
            r = result_map.get(name)
            if r and r.python_expression:
                execution_steps.append({
                    "name": r.output_name,
                    "expression": r.python_expression,
                })
        # Return tuple references declared outputs by name only
        for name in output_attr_order:
            if name in result_map:
                output_expressions.append({
                    "name": name,
                    "expression": name,
                })
    else:
        # No cross-refs: undeclared intermediates as steps, declared inlined
        for name in compilation_result.execution_order:
            r = result_map.get(name)
            if r and r.python_expression and r.is_undeclared_intermediate:
                execution_steps.append({
                    "name": r.output_name,
                    "expression": r.python_expression,
                })
        for name in output_attr_order:
            r = result_map.get(name)
            if r and r.python_expression:
                output_expressions.append({
                    "name": r.output_name,
                    "expression": r.python_expression,
                })

    return {
        "execution_steps": execution_steps,
        "output_expressions": output_expressions,
        "output_count": len(output_expressions),
        "single_output_expression": (
            output_expressions[0]["expression"]
            if len(output_expressions) == 1
            else None
        ),
    }


def generate_implementation(
    calc_def: CalculationDefinitionData,
    template_env: jinja2.Environment,
    output_path: Path,
    package_name: str = "generated_code",
    compilation_result: CalcDefCompilationResult | None = None,
) -> str:
    """Generate implementation file for a CalcDef.

    Dispatches to auto-implementation template for FULLY_COMPILABLE CalcDefs,
    or to NotImplementedError stub template for all others.

    Args:
        calc_def: Calculation definition to implement
        template_env: Jinja2 environment
        output_path: Where to write handwritten/ file
        package_name: Package name for imports
        compilation_result: Compilation result from Step 6.5, or None

    Returns:
        Generated Python code
    """
    is_auto_impl = (
        compilation_result is not None
        and compilation_result.overall_compilability == Compilability.FULLY_COMPILABLE
    )

    context = _build_stencil_context(calc_def, output_path, package_name)

    if is_auto_impl:
        assert compilation_result is not None  # guaranteed by is_auto_impl check
        context.update(_build_auto_impl_context(compilation_result, calc_def))
        template = template_env.get_template("auto_implementation.py.jinja2")
    else:
        template = template_env.get_template("implementation_stencil.py.jinja2")

    code = template.render(**context)
    if not code.endswith('\n'):
        code += '\n'
    return code


def generate_implementation_stencil(
    calc_def: CalculationDefinitionData,
    template_env: jinja2.Environment,
    output_path: Path,
    package_name: str = "generated_code",
) -> str:
    """Generate implementation stencil for calc def (stub with NotImplementedError).

    Preserved for backward compatibility. Equivalent to calling
    generate_implementation() with compilation_result=None.

    Args:
        calc_def: Calculation definition to implement
        template_env: Jinja2 environment
        output_path: Where to write handwritten/ file (for future use)
        package_name: Package name for imports (parameterized)

    Returns:
        Generated Python code
    """
    context = _build_stencil_context(calc_def, output_path, package_name)

    template = template_env.get_template("implementation_stencil.py.jinja2")
    code = template.render(**context)

    # Ensure final newline (PEP 8 compliance)
    if not code.endswith('\n'):
        code += '\n'

    return code


def _extract_calc_expressions(calc_def: CalculationDefinitionData) -> list[str]:
    """Extract SysML calc expressions from calc def.

    Args:
        calc_def: Calculation definition

    Returns:
        List of expression strings from SysML
    """
    return calc_def.calc_expressions


def generate_backlog_report(
    calc_defs: list[CalculationDefinitionData],
    output_path: Path,
    package_name: str = "generated_code",
    compilation_results: dict[str, CalcDefCompilationResult] | None = None,
    computed_attributes: list[ComputedAttributeData] | None = None,
    aggregation_data: list[ScopedAggregationData] | None = None,
) -> str:
    """Generate markdown report of implementation backlog.

    Auto-implemented CalcDefs (FULLY_COMPILABLE) are excluded from the
    backlog since they don't require manual implementation.
    FORMULA+FULLY_COMPILABLE computed attributes are also excluded
    (auto-implemented) and shown in a summary line.

    Args:
        calc_defs: All calculation definitions
        output_path: Where to write IMPLEMENTATION_BACKLOG.md (for future)
        package_name: Package name (parameterized)
        compilation_results: Compilation results keyed by calc_def.name
        computed_attributes: Computed attributes from Step 4.5

    Returns:
        Generated markdown string with stage-based checklist
    """
    # Build items with proper source paths
    items = []
    for calc_def in calc_defs:
        # Skip auto-implemented CalcDefs
        if compilation_results and calc_def.name in compilation_results:
            cr = compilation_results[calc_def.name]
            if cr.overall_compilability == Compilability.FULLY_COMPILABLE:
                continue

        complexity = _estimate_complexity(calc_def)

        # Get full relative path from project root
        source_file = calc_def.source_file
        if isinstance(source_file, Path):
            try:
                source_str = str(source_file)
                if "models/" in source_str:
                    source_path = "models/" + source_str.split("models/", 1)[1]
                else:
                    source_path = source_file.name
            except Exception:
                source_path = source_file.name
        else:
            source_path = str(source_file)

        items.append(
            {
                "module": calc_def.name,
                "function": f"run_{calc_def.name.lower()}",
                "source": f"{source_path}:{calc_def.source_line}",
                "complexity": complexity,
                "calc_expressions": calc_def.calc_expressions,
            }
        )

    # Generate markdown with stage-based checklist
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

    # Add computed attribute auto-implementation summary
    if computed_attributes:
        auto_count = sum(
            1 for ca in computed_attributes
            if ca.classification == ComputedAttributeClassification.FORMULA
            and ca.compilability == Compilability.FULLY_COMPILABLE
        )
        if auto_count > 0:
            lines.extend([
                "",
                f"**{auto_count} computed attribute module(s) auto-implemented** "
                "(not included in manual count above).",
            ])

    # Add aggregation auto-implementation summary
    if aggregation_data:
        agg_auto_count = sum(
            1 for agg in aggregation_data
            if not agg.expression.has_unsupported_nodes
        )
        if agg_auto_count > 0:
            lines.extend([
                "",
                f"**{agg_auto_count} aggregation module(s) auto-implemented** "
                "(not included in manual count above).",
            ])

    lines.extend(
        [
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
        ]
    )

    markdown = "\n".join(lines)

    # Ensure final newline
    if not markdown.endswith('\n'):
        markdown += '\n'

    return markdown


def _estimate_complexity(calc_def: CalculationDefinitionData) -> str:
    """Estimate implementation complexity.

    Returns:
        'Low', 'Medium', or 'High'
    """
    output_attrs = calc_def.output_attributes
    if not output_attrs:
        return "Low"

    # Count operators in expressions
    total_ops = 0
    for expr in calc_def.calc_expressions:
        ops = (
            expr.count("+")
            + expr.count("*")
            + expr.count("/")
            + expr.count("-")
        )
        total_ops += ops

    if total_ops <= 5:
        return "Low"
    elif total_ops <= 15:
        return "Medium"
    else:
        return "High"


def _output_attr_name(out) -> str:
    """Get original output attribute name from ModuleOutput.

    For multi-output modules, field_name IS the attribute name.
    For single-output modules, field_name is "root" -- extract from channel_name.
    Channel name format: {usage_eqn}__{attr_name} (PQN format).
    """
    if out.field_name != "root":
        return out.field_name
    return out.channel_name.split("__")[-1]


def _build_stub_docstring_from_graph(module) -> str:
    """Build stub docstring from PipelineModule fields.

    Mirrors _build_stub_docstring() but uses PipelineModule metadata.
    """
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

    sqn = SysMLQualifiedName(module.calc_def_qualified_name)
    python_path = PythonModulePath.from_sysml(sqn)
    module_import_path = python_path.import_path

    return {
        "function_name": f"run_{module.calc_def_name.lower()}",
        "calc_name": module.calc_def_name,
        "sysml_source": f"{module.source_file}:{module.source_line}",
        "sysml_expressions": calc_expressions,
        "input_params": input_params,
        "output_names": output_names,
        "return_type": return_type,
        "docstring": _build_stub_docstring_from_graph(module),
        "input_class_name": f"{module.calc_def_name}Input",
        "module_name": module.calc_def_name.lower(),
        "module_import_path": module_import_path,
        "package_name": package_name,
    }


def generate_implementation_from_graph(
    module,
    template_env: jinja2.Environment,
    output_path: Path,
    package_name: str = "generated_code",
) -> str:
    """Generate implementation from PipelineModule (graph-only variant).

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


def generate_backlog_report_from_graph(
    graph,
    output_path: Path,
    package_name: str = "generated_code",
) -> str:
    """Generate backlog report from ComputationGraph (graph-only variant).

    Args:
        graph: ComputationGraph with modules
        output_path: Where to write IMPLEMENTATION_BACKLOG.md
        package_name: Package name

    Returns:
        Generated markdown string
    """
    items = []
    auto_formula_count = 0
    auto_agg_count = 0

    for module in graph.modules:
        if module.is_computed_attribute:
            if module.auto_impl_context is not None:
                auto_formula_count += 1
            continue
        if module.is_aggregation:
            if module.auto_impl_context is not None:
                auto_agg_count += 1
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


__all__ = [
    "generate_backlog_report",
    "generate_backlog_report_from_graph",
    "generate_implementation",
    "generate_implementation_from_graph",
    "generate_implementation_stencil",
]
