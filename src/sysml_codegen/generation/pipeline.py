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
from sysml_codegen.core.qualified_names import params_field_name
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    OutputAlias,
    ParameterGroup,
    PipelineModule,
)


def generate_pipeline_yaml(
    graph: ComputationGraph,
    package_name: str,
    template_env: Environment,
    *,
    selected_channels: set[str] | None = None,
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
        selected_channels: Test-only exit-membership narrowing (Item 7 / D1),
            forwarded to ``_build_exit_points``. ``None`` (production default)
            reproduces today's capture-everything exit list byte-for-byte.

    Returns:
        Generated YAML as string
    """
    from sysml_codegen.generation.errors import validate_constraint_graph_or_raise

    validate_constraint_graph_or_raise(graph)

    # Build channel -> field_name map from module outputs (single source of truth)
    channel_field_map = {
        out.channel_name: out.field_name for module in graph.modules for out in module.outputs
    }

    # Item 11 (REQ-PY-08): an aliased channel's exit line renders the modeler's
    # name as its output filename. The map is policy (which filename wins per
    # channel); _build_exit_points just applies it.
    alias_filenames = _build_alias_filename_map(graph.output_aliases)

    # Build template context
    context = {
        "package_name": package_name,
        "entry_points": _build_entry_points(graph.entry_point_groups),
        "modules": _build_module_contexts(graph.modules, channel_field_map),
        "exit_points": _build_exit_points(
            graph.modules, alias_filenames, selected_channels=selected_channels
        ),
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
    from sysml_codegen.resolution.models import ModuleKind

    return {
        "name": (
            f"source: aggregation ({module.module_type})"
            if module.module_kind == ModuleKind.AGGREGATION
            else f"source: computed_attribute ({module.module_type})"
            if module.module_kind == ModuleKind.FORMULA
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
        # Entry point — "group.<schema field>". The runtime resolves the part
        # after the dot with ``getattr`` on the loaded params model, so it must
        # be the *field* name, which differs from the params key exactly when a
        # modelled multiplicity indexed it. The JSON key itself is unchanged and
        # stays the field's alias.
        field = params_field_name(inp.source.qualified_name)
        if inp.source.param_group:
            source = f"{inp.source.param_group}.{field}"
        else:
            # Fallback if no group (shouldn't happen in practice)
            source = field

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


def _build_alias_filename_map(output_aliases: list[OutputAlias]) -> dict[str, str]:
    """Map each aliased canonical channel to its exit-point output filename.

    First-wins over the INV-5-sorted ``output_aliases``, so a channel carrying
    two names renders the first by ``(instance_path, alias_name)`` deterministically
    (M4). Every alias still appears in ``output_aliases`` for programmatic
    consumers; only the rendered filename is single-valued per channel.
    """
    filenames: dict[str, str] = {}
    for alias in output_aliases:
        filenames.setdefault(alias.canonical_channel, alias.output_filename)
    return filenames


def _build_exit_points(
    modules: list[PipelineModule],
    alias_filenames: dict[str, str],
    *,
    selected_channels: set[str] | None = None,
    pin_report_channels: bool = True,
) -> list[dict]:
    """Build exit point context for template.

    Exit points capture all module outputs for pipeline results.
    Each unique output channel becomes an exit point.

    Type rules:
    - Single-output modules (field_name="root"): channel contains RootModel[T]
    - Multi-output modules (field_name=attr_name): channel contains T (unwrapped)

    Filename rule (Item 11 / D3): an aliased channel uses the modeler's
    instance-qualified name as its output filename; every other channel keeps
    today's ``{channel}.json``. The exit **key** stays the canonical channel
    either way (simkit requires it — REQ-PY-06 unchanged).

    Membership rule (Item 7 / D1): production defaults (``selected_channels=None``,
    ``pin_report_channels=True``) reproduce today's capture-everything output
    byte-for-byte (INV-7) — every channel passes the ``selected_channels is None``
    clause, so the pin is a no-op. The two keyword parameters exist only so a test
    can drive a *narrowed* ``selected_channels`` and prove the ``REPORT_AGGREGATOR``
    channel's membership is structural (INV-5), not incidental capture-everything:
    a channel is included iff it is in ``selected_channels`` (or nothing was
    supplied), or it is a pinned report channel and ``pin_report_channels`` is
    ``True``. There is no production exit-narrowing feature — narrowing is
    exercised only by the kept test's seam (Non-Goals).

    Args:
        modules: List of PipelineModule from ComputationGraph
        alias_filenames: Canonical-channel → alias filename overrides
            (``_build_alias_filename_map``); empty when no channel is aliased.
        selected_channels: Test-only membership narrowing; ``None`` (production
            default) keeps every channel.
        pin_report_channels: Whether ``REPORT_AGGREGATOR`` outputs are always
            kept regardless of ``selected_channels`` (INV-5). Defaults ``True``.

    Returns:
        List of dicts with name, type, filename for exit point outputs
    """
    pinned = {
        out.channel_name
        for module in modules
        if module.module_kind is ModuleKind.REPORT_AGGREGATOR
        for out in module.outputs
    }
    exit_points = []
    for module in modules:
        for out in module.outputs:
            channel = out.channel_name
            included = (selected_channels is None or channel in selected_channels) or (
                pin_report_channels and channel in pinned
            )
            if not included:
                continue
            # Single-output: channel stores RootModel[T]
            # Multi-output: channel stores T (unwrapped primitive)
            if out.field_name == "root":
                output_type = f"RootModel[{out.python_type}]"
            else:
                output_type = out.python_type
            exit_points.append(
                {
                    "name": channel,
                    "type": output_type,
                    "filename": alias_filenames.get(channel, f"{channel}.json"),
                }
            )
    return exit_points


__all__ = [
    "generate_pipeline_yaml",
]
