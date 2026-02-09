"""Pipeline YAML generator from ComputationGraph.

This module generates pipeline YAML configuration from the ComputationGraph,
which is the single source of truth for pipeline structure.

Key Design:
- Takes ComputationGraph (from graph_builder) as input
- Uses Jinja2 template for YAML generation
- Handles entry points (JSON loading), modules, and exit points
"""

from jinja2 import Environment

# UPDATED: Import from sysml_codegen package
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ModuleInput,
    ModuleOutput,
    ParameterGroup,
    PipelineModule,
)


def generate_pipeline_yaml(
    graph: ComputationGraph,
    package_name: str,
    template_env: Environment,
) -> str:
    """Generate pipeline YAML from ComputationGraph.

    This is the primary entry point for pipeline YAML generation.
    The generated YAML includes:
    1. Metadata section
    2. Entry point module (loads JSON files)
    3. All pipeline modules in execution order
    4. Exit point module (captures results)

    Args:
        graph: ComputationGraph from build_computation_graph()
        package_name: Package name for metadata (parameterized)
        template_env: Jinja2 Environment with pipeline template

    Returns:
        Generated YAML as string
    """
    # Build channel -> field_name map from module outputs (single source of truth)
    channel_field_map = {
        out.channel_name: out.field_name
        for module in graph.modules
        for out in module.outputs
    }

    # Build template context
    context = {
        "package_name": package_name,
        "entry_points": _build_entry_points(graph.entry_point_groups),
        "modules": _build_module_contexts(graph.modules, channel_field_map),
        "exit_points": _build_exit_points(graph.modules),
    }

    # Render template
    template = template_env.get_template("pipeline_yaml.jinja2")
    return template.render(**context)


def _build_entry_points(groups: list[ParameterGroup]) -> list[dict]:
    """Build entry point context for template.

    Each entry point group becomes an input to the entry module,
    which loads the corresponding JSON file.

    Args:
        groups: List of ParameterGroup from ComputationGraph

    Returns:
        List of dicts with name, type, source for template
    """
    entry_points = []
    for group in groups:
        entry_points.append(
            {
                "name": group.name,
                "type": group.class_name,
                "source": f"../inputs/{group.name}.json",
            }
        )
    return entry_points


def _build_module_contexts(
    modules: list[PipelineModule],
    channel_field_map: dict[str, str],
) -> list[dict]:
    """Build module context list for template.

    Converts PipelineModule objects to template-friendly dicts.

    Args:
        modules: List of PipelineModule from ComputationGraph
        channel_field_map: Maps channel_name -> field_name for extraction

    Returns:
        List of dicts for template rendering
    """
    return [_module_to_context(m, channel_field_map) for m in modules]


def _module_to_context(
    module: PipelineModule,
    channel_field_map: dict[str, str],
) -> dict:
    """Convert single PipelineModule to template context.

    Args:
        module: PipelineModule to convert
        channel_field_map: Maps channel_name -> field_name for extraction

    Returns:
        Dict with name, instance_name, type, inputs, outputs
    """
    return {
        "name": (
            f"source: computed_attribute ({module.module_type})"
            if module.is_computed_attribute
            else module.module_type
        ),
        "instance_name": module.name,
        "type": module.module_type,
        "inputs": [_input_to_context(inp, channel_field_map) for inp in module.inputs],
        "outputs": [_output_to_context(out) for out in module.outputs],
    }


def _input_to_context(
    inp: ModuleInput,
    channel_field_map: dict[str, str],
) -> dict:
    """Convert ModuleInput to template context.

    Input source formatting:
    - entry_point: "group.qualified_name"
    - module_output: channel_name with field extraction
      - For single-output modules (field="root"): append ".root"
      - For multi-output modules: no extraction needed (fields stored directly)

    Args:
        inp: ModuleInput to convert
        channel_field_map: Maps channel_name -> field_name for extraction

    Returns:
        Dict with name, type, source
    """
    if inp.source.source_type == "module_output":
        # Upstream module output - channel name with optional field extraction
        channel = inp.source.producer_channel
        # Look up field name from the producing module's output
        producer_field = channel_field_map.get(channel, "")
        # For single-output modules, extract .root from RootModel[float]
        if producer_field == "root":
            source = f"{channel}.root"
        else:
            source = channel
    else:
        # Entry point - use "group.qualified_name" format
        if inp.source.param_group:
            source = f"{inp.source.param_group}.{inp.source.qualified_name}"
        else:
            # Fallback if no group (shouldn't happen in practice)
            source = inp.source.qualified_name

    return {
        "name": inp.param_name,
        "type": inp.python_type,
        "source": source,
    }


def _output_to_context(out: ModuleOutput) -> dict:
    """Convert ModuleOutput to template context.

    Args:
        out: ModuleOutput to convert

    Returns:
        Dict with name, type, channel
    """
    # For single-output modules (field_name="root"), use RootModel[type]
    if out.field_name == "root":
        output_type = f"RootModel[{out.python_type}]"
    else:
        output_type = out.python_type

    return {
        "name": out.field_name,
        "type": output_type,
        "channel": out.channel_name,
    }


def _build_exit_points(modules: list[PipelineModule]) -> list[dict]:
    """Build exit point context for template.

    Exit points capture all module outputs for pipeline results.
    Each unique output channel becomes an exit point.

    Type rules:
    - Single-output modules (field_name="root"): channel contains RootModel[T]
    - Multi-output modules (field_name=attr_name): channel contains T (unwrapped)

    Args:
        modules: List of PipelineModule from ComputationGraph

    Returns:
        List of dicts with name, type for exit point outputs
    """
    exit_points = []
    for module in modules:
        for out in module.outputs:
            # Single-output: channel stores RootModel[T]
            # Multi-output: channel stores T (unwrapped primitive)
            if out.field_name == "root":
                output_type = f"RootModel[{out.python_type}]"
            else:
                output_type = out.python_type
            exit_points.append(
                {
                    "name": out.channel_name,
                    "type": output_type,
                }
            )
    return exit_points


__all__ = [
    "generate_pipeline_yaml",
]
