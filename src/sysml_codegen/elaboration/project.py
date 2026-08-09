"""Project a resolved exact-ID graph onto the existing generation seam.

Semantic choices are complete before this module runs.  Projection only
renders public identifiers, classifies already-resolved sources, and orders
the resulting modules.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import NoReturn

from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    InvocationNode,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
    UnsupportedNode,
    parse_expression,
)

from sysml_codegen.analysis.constraint_lowering import mint_constraint_id
from sysml_codegen.core.identifier_types import derive_module_type
from sysml_codegen.core.qualified_names import (
    get_channel_name,
    sanitize_name,
    sanitize_qualified_name,
)
from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.elaboration.graph import (
    CalcNode,
    ConstraintNode,
    Diagnostic,
    GraphValidationError,
    InputPortId,
    InputRef,
    InstanceGraph,
    LiteralInput,
    NodeRef,
    PortMetadata,
    ProducerRef,
)
from sysml_codegen.elaboration.identity import (
    ConsumerPortId,
    ExpressionPortId,
    NodeId,
    OutputPortId,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConstraintCatalog,
    ConstraintCatalogEntry,
    ConstraintCatalogExcludedRecord,
    ConstraintCatalogSourceRecord,
    ConstraintCatalogUsageRecord,
    ConstraintExclusion,
    ConstraintFormalIdentity,
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    OutputAlias,
    ParameterGroup,
    PipelineModule,
)

__all__ = ["ProjectionError", "project"]

_CONSTRAINT_LOGGER = logging.getLogger("sysml_codegen.analysis.constraint_lowering")


class ProjectionError(ValueError):
    """A valid semantic graph cannot be rendered without losing identity."""

    def __init__(self, diagnostics: list[Diagnostic] | tuple[Diagnostic, ...]) -> None:
        self.diagnostics = tuple(diagnostics)
        super().__init__("; ".join(f"{item.code.value}: {item.detail}" for item in diagnostics))


def _diagnostic(
    code: ElaborationCode,
    detail: str,
    *,
    consumer: NodeId | None = None,
    consumer_display: str = "<projection>",
    param_name: str | None = None,
) -> Diagnostic:
    return Diagnostic(code, consumer, consumer_display, param_name, detail)


def _fail(
    code: ElaborationCode,
    detail: str,
    *,
    consumer: NodeId | None = None,
    consumer_display: str = "<projection>",
    param_name: str | None = None,
) -> NoReturn:
    raise ProjectionError(
        [
            _diagnostic(
                code,
                detail,
                consumer=consumer,
                consumer_display=consumer_display,
                param_name=param_name,
            )
        ]
    )


def _port_key(port: InputPortId) -> tuple:
    if isinstance(port, ConsumerPortId):
        return ("consumer", port.formal.to_wire())
    return (
        "expression",
        port.reference_ordinal,
        port.edge_ordinal,
        port.referenced_declaration.to_wire(),
        port.target_occurrence.to_wire() if port.target_occurrence is not None else "",
    )


def _metadata(node: CalcNode | ConstraintNode, port: InputPortId) -> PortMetadata:
    return node.input_metadata.get(port, PortMetadata())


def _float_default(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    _fail(
        ElaborationCode.SI_RENDERING_COLLISION,
        f"the public EntryPoint seam cannot carry non-numeric default {value!r}",
    )


def _group_identity(source_file: str, qualified_name: str) -> tuple[str, str, Path]:
    path = Path(source_file)
    base = path.parent.name if path.stem.lower() == "model" else path.stem
    if not base or base == ".":
        base = qualified_name.split("__", 1)[0] or "system_design"
    base_name = sanitize_name(base).lower()
    if base_name.endswith("_params"):
        base_name = base_name[: -len("_params")]
    name = f"{base_name}_params"
    class_name = "".join(part.capitalize() for part in base_name.split("_") if part)
    return name, f"{class_name or 'SystemDesign'}Params", path


class _Projection:
    def __init__(self, graph: InstanceGraph) -> None:
        self.graph = graph
        self.modules: list[PipelineModule] = []
        self.entry_points: dict[str, EntryPoint] = {}
        self.entry_sources: dict[str, tuple[str, str, Path]] = {}
        self.entry_semantics: dict[str, object] = {}
        self.output_channels: dict[OutputPortId, str] = {}
        self.public_module_names: dict[str, NodeId | str] = {}
        self.public_channels: dict[str, OutputPortId | str] = {}

    def run(self) -> ComputationGraph:
        try:
            self.graph.require_projectable()
        except GraphValidationError as error:
            raise ProjectionError(list(error.diagnostics)) from error

        self._index_output_channels()
        self._build_calculation_modules()
        self._build_constraint_modules()
        aliases = self._build_output_aliases()
        groups = self._build_groups()
        modules = self._topological_modules()
        catalog = self._build_constraint_catalog()
        return ComputationGraph(
            modules=modules,
            entry_point_groups=groups,
            execution_order=[module.name for module in modules],
            fallback_entry_points=set(),
            output_aliases=aliases,
            constraint_catalog=catalog,
        )

    def _claim_module(self, name: str, semantic: NodeId | str) -> None:
        prior = self.public_module_names.get(name)
        if prior is not None and prior != semantic:
            _fail(
                ElaborationCode.SI_RENDERING_COLLISION,
                f"distinct semantic modules render as public name {name!r}",
            )
        self.public_module_names[name] = semantic

    def _claim_channel(self, channel: str, semantic: OutputPortId | str) -> None:
        prior = self.public_channels.get(channel)
        if prior is not None and prior != semantic:
            _fail(
                ElaborationCode.SI_RENDERING_COLLISION,
                f"distinct semantic outputs render as public channel {channel!r}",
            )
        self.public_channels[channel] = semantic

    def _index_output_channels(self) -> None:
        for node in sorted(self.graph.calcs.values(), key=lambda item: item.node_id.to_wire()):
            for declaration, port in sorted(
                node.outputs.items(), key=lambda item: item[0].to_wire()
            ):
                channel = get_channel_name(
                    node.display_path,
                    node.output_names.get(declaration, "result"),
                )
                self._claim_channel(channel, port)
                self.output_channels[port] = channel

    def _entry_source(
        self,
        *,
        qualified_name: str,
        simple_name: str,
        entry_type: EntryPointType,
        default_value: object,
        source_calc_usage: str | None,
        metadata: PortMetadata,
        source_file: str,
        semantic: object,
    ) -> InputSource:
        group_name, class_name, group_path = _group_identity(source_file, qualified_name)
        prior = self.entry_semantics.get(qualified_name)
        if prior is not None and prior != semantic:
            _fail(
                ElaborationCode.SI_RENDERING_COLLISION,
                f"distinct semantic sources render as entry point {qualified_name!r}",
            )
        existing = self.entry_points.get(qualified_name)
        candidate = EntryPoint(
            qualified_name=qualified_name,
            simple_name=simple_name,
            entry_type=entry_type,
            default_value=_float_default(default_value),
            source_calc_usage=source_calc_usage,
            param_group=group_name,
            python_type=metadata.python_type,
            unit_text=metadata.unit,
            unresolved_default_kind=metadata.unresolved_default_kind,
        )
        if existing is not None and existing != candidate:
            _fail(
                ElaborationCode.SI_RENDERING_COLLISION,
                f"entry point {qualified_name!r} has conflicting projected metadata",
            )
        self.entry_semantics[qualified_name] = semantic
        self.entry_points[qualified_name] = candidate
        prior_group = self.entry_sources.get(qualified_name)
        group = (group_name, class_name, group_path)
        if prior_group is not None and prior_group != group:
            _fail(
                ElaborationCode.SI_RENDERING_COLLISION,
                f"entry point {qualified_name!r} renders into two parameter groups",
            )
        self.entry_sources[qualified_name] = group
        return InputSource(
            source_type="entry_point",
            param_group=group_name,
            qualified_name=qualified_name,
        )

    def _source_for_edge(
        self,
        edge: InputRef,
        *,
        consumer: CalcNode | ConstraintNode,
        port: InputPortId,
        param_name: str,
    ) -> InputSource:
        metadata = _metadata(consumer, port)
        if isinstance(edge, ProducerRef):
            channel = self.output_channels.get(edge.target)
            if channel is None:
                _fail(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"producer port for {consumer.display_path}.{param_name} has no output",
                    consumer=consumer.node_id,
                    consumer_display=consumer.display_path,
                    param_name=param_name,
                )
            return InputSource(source_type="module_output", producer_channel=channel)
        if isinstance(edge, NodeRef):
            attr = self.graph.attrs.get(edge.target)
            if attr is None:
                _fail(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"attribute source for {consumer.display_path}.{param_name} is absent",
                    consumer=consumer.node_id,
                    consumer_display=consumer.display_path,
                    param_name=param_name,
                )
            if attr.is_alias:
                _fail(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"unfollowed alias {attr.display_path!r} reached projection",
                    consumer=consumer.node_id,
                    consumer_display=consumer.display_path,
                    param_name=param_name,
                )
            return self._entry_source(
                qualified_name=attr.display_path,
                simple_name=attr.display_name,
                entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                default_value=attr.value,
                source_calc_usage=None,
                metadata=metadata,
                source_file=attr.source_file,
                semantic=attr.node_id,
            )
        if isinstance(edge, LiteralInput):
            qualified_name = f"{consumer.display_path}__{param_name}"
            return self._entry_source(
                qualified_name=qualified_name,
                simple_name=param_name,
                entry_type=EntryPointType.USAGE_LITERAL,
                default_value=edge.value,
                source_calc_usage=consumer.display_path,
                metadata=metadata,
                source_file=consumer.source_file,
                semantic=(consumer.node_id, port),
            )
        raise AssertionError(f"unknown resolved edge {edge!r}")

    def _unbound_source(
        self,
        *,
        consumer: CalcNode | ConstraintNode,
        port: ConsumerPortId,
        param_name: str,
    ) -> InputSource:
        metadata = _metadata(consumer, port)
        qualified_name = f"{consumer.display_path}__{param_name}"
        return self._entry_source(
            qualified_name=qualified_name,
            simple_name=param_name,
            entry_type=EntryPointType.LIBRARY_DEFAULT,
            default_value=metadata.default_value,
            source_calc_usage=consumer.display_path,
            metadata=metadata,
            source_file=consumer.source_file,
            semantic=(consumer.node_id, port),
        )

    def _regular_inputs(self, node: CalcNode | ConstraintNode) -> list[ModuleInput]:
        result: list[ModuleInput] = []
        for port in sorted(node.input_names, key=_port_key):
            param_name = sanitize_name(node.input_names[port])
            edge = node.inputs.get(port)
            if edge is not None:
                source = self._source_for_edge(
                    edge,
                    consumer=node,
                    port=port,
                    param_name=param_name,
                )
            elif isinstance(port, ConsumerPortId) and port.formal in node.unbound_formals:
                source = self._unbound_source(consumer=node, port=port, param_name=param_name)
            else:
                _fail(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"input {node.display_path}.{param_name} has neither edge nor default",
                    consumer=node.node_id,
                    consumer_display=node.display_path,
                    param_name=param_name,
                )
            metadata = _metadata(node, port)
            result.append(
                ModuleInput(
                    param_name=param_name,
                    python_type=metadata.python_type,
                    source=source,
                    description=metadata.description,
                    default_value=metadata.default_value,
                )
            )
        self._require_unique_params(node, result)
        return result

    @staticmethod
    def _require_unique_params(node: CalcNode | ConstraintNode, inputs: list[ModuleInput]) -> None:
        names = [item.param_name for item in inputs]
        if len(names) != len(set(names)):
            _fail(
                ElaborationCode.SI_RENDERING_COLLISION,
                f"distinct inputs on {node.display_path!r} render to one parameter name",
                consumer=node.node_id,
                consumer_display=node.display_path,
            )

    def _computed_inputs(
        self, node: CalcNode
    ) -> tuple[list[ModuleInput], dict[ExpressionPortId, str]]:
        by_reference: dict[int, list[ExpressionPortId]] = defaultdict(list)
        for port in node.input_names:
            if not isinstance(port, ExpressionPortId):
                _fail(
                    ElaborationCode.SI_SNAPSHOT_INVALID,
                    f"computed node {node.display_path!r} has a non-expression input port",
                )
            by_reference[port.reference_ordinal].append(port)

        result: list[ModuleInput] = []
        param_by_port: dict[ExpressionPortId, str] = {}
        source_by_name: dict[str, InputRef] = {}
        for reference_ordinal in sorted(by_reference):
            ports = sorted(by_reference[reference_ordinal], key=lambda item: item.edge_ordinal)
            plural = reference_ordinal in node.aggregation_reference_ordinals
            if not plural and len(ports) != 1:
                _fail(
                    ElaborationCode.SI_SNAPSHOT_INVALID,
                    f"scalar expression reference {reference_ordinal} on "
                    f"{node.display_path!r} has {len(ports)} edges",
                )
            for port in ports:
                edge = node.inputs.get(port)
                if edge is None:
                    _fail(
                        ElaborationCode.SI_EDGE_DANGLING,
                        f"computed input port on {node.display_path!r} has no edge",
                    )
                base = sanitize_name(node.input_names[port])
                param_name = f"{base}_{port.edge_ordinal}" if plural else base
                prior = source_by_name.get(param_name)
                if prior is not None and prior != edge:
                    _fail(
                        ElaborationCode.SI_RENDERING_COLLISION,
                        f"distinct expression sources on {node.display_path!r} render as "
                        f"parameter {param_name!r}",
                        consumer=node.node_id,
                        consumer_display=node.display_path,
                        param_name=param_name,
                    )
                param_by_port[port] = param_name
                if prior is not None:
                    continue
                source_by_name[param_name] = edge
                metadata = _metadata(node, port)
                result.append(
                    ModuleInput(
                        param_name=param_name,
                        python_type=metadata.python_type,
                        source=self._source_for_edge(
                            edge,
                            consumer=node,
                            port=port,
                            param_name=param_name,
                        ),
                        description=metadata.description,
                        default_value=metadata.default_value,
                    )
                )
        return result, param_by_port

    def _compile_computed_expression(
        self, node: CalcNode, param_by_port: dict[ExpressionPortId, str]
    ) -> str:
        if node.expression_ir is None:
            _fail(
                ElaborationCode.SI_SNAPSHOT_INVALID,
                f"computed node {node.display_path!r} has no expression IR",
            )
        ir = parse_expression(node.expression_ir)
        by_reference: dict[int, list[ExpressionPortId]] = defaultdict(list)
        for port in param_by_port:
            by_reference[port.reference_ordinal].append(port)
        reference_ordinal = 0

        def render(expression: object) -> str:
            nonlocal reference_ordinal
            if isinstance(expression, LiteralNode):
                return repr(expression.literal.value)
            if isinstance(expression, FeatureReferenceNode):
                current = reference_ordinal
                reference_ordinal += 1
                ports = sorted(by_reference.get(current, ()), key=lambda item: item.edge_ordinal)
                if not ports:
                    _fail(
                        ElaborationCode.SI_SNAPSHOT_INVALID,
                        f"expression reference {current} on {node.display_path!r} has no edge",
                    )
                values = [f"inputs.{param_by_port[port]}" for port in ports]
                if current in node.aggregation_reference_ordinals:
                    return f"({' + '.join(values)})"
                if len(values) != 1:
                    _fail(
                        ElaborationCode.SI_SNAPSHOT_INVALID,
                        f"scalar expression reference {current} has multiple edges",
                    )
                return values[0]
            if isinstance(expression, UnitAnnotationNode):
                return render(expression.value)
            if isinstance(expression, OperatorNode):
                parts = [render(operand) for operand in expression.operands]
                operator = "**" if expression.operator == "^" else expression.operator
                if len(parts) == 1 and operator in ("+", "-", "not"):
                    spacer = " " if operator == "not" else ""
                    return f"({operator}{spacer}{parts[0]})"
                if len(parts) < 2:
                    _fail(
                        ElaborationCode.SI_SNAPSHOT_INVALID,
                        f"operator {operator!r} on {node.display_path!r} has too few operands",
                    )
                return f"({f' {operator} '.join(parts)})"
            if isinstance(expression, InvocationNode):
                if expression.function_qn != ["NumericalFunctions", "sum"]:
                    _fail(
                        ElaborationCode.SI_SNAPSHOT_INVALID,
                        f"unsupported invocation survived on {node.display_path!r}",
                    )
                if len(expression.arguments) != 1:
                    _fail(
                        ElaborationCode.SI_SNAPSHOT_INVALID,
                        f"sum on {node.display_path!r} must have one argument",
                    )
                return render(expression.arguments[0])
            if isinstance(expression, UnsupportedNode):
                _fail(
                    ElaborationCode.SI_SNAPSHOT_INVALID,
                    f"unsupported expression IR survived on {node.display_path!r}",
                )
            _fail(
                ElaborationCode.SI_SNAPSHOT_INVALID,
                f"unknown expression IR node on {node.display_path!r}",
            )

        compiled = render(ir)
        if reference_ordinal != len(by_reference):
            _fail(
                ElaborationCode.SI_SNAPSHOT_INVALID,
                f"{node.display_path!r} has expression edges not represented in its IR",
            )
        return compiled

    def _outputs(self, node: CalcNode) -> list[ModuleOutput]:
        result: list[ModuleOutput] = []
        single = len(node.outputs) == 1
        for declaration, port in sorted(node.outputs.items(), key=lambda item: item[0].to_wire()):
            metadata = node.output_metadata.get(declaration, PortMetadata())
            result.append(
                ModuleOutput(
                    field_name="root" if single else node.output_names[declaration],
                    python_type=metadata.python_type,
                    channel_name=self.output_channels[port],
                    description=metadata.description,
                    default_value=metadata.default_value,
                    unit=metadata.unit,
                )
            )
        return result

    def _build_calculation_modules(self) -> None:
        for node in sorted(self.graph.calcs.values(), key=lambda item: item.node_id.to_wire()):
            name = node.display_path.lower()
            self._claim_module(name, node.node_id)
            auto_impl_context: dict | None
            if node.is_computed:
                inputs, param_by_port = self._computed_inputs(node)
                compiled = self._compile_computed_expression(node, param_by_port)
                kind = (
                    ModuleKind.AGGREGATION
                    if node.aggregation_reference_ordinals
                    else ModuleKind.FORMULA
                )
                module_qn = (
                    f"{node.calc_def_qualified_name}::{node.calc_def_name}"
                    if node.calc_def_qualified_name
                    else node.calc_def_name
                )
                outputs = self._outputs(node)
                output_name = next(iter(node.output_names.values()), node.display_name)
                auto_impl_context = {
                    "execution_steps": [],
                    "output_expressions": [{"name": output_name, "expression": compiled}],
                    "output_count": 1,
                    "single_output_expression": compiled,
                }
                compilability = Compilability.FULLY_COMPILABLE
            else:
                inputs = self._regular_inputs(node)
                compiled = None
                kind = ModuleKind.CALCULATION
                module_qn = node.calc_def_qualified_name
                outputs = self._outputs(node)
                auto_impl_context = node.auto_impl_context
                compilability = node.compilability
            if not module_qn:
                _fail(
                    ElaborationCode.SI_SNAPSHOT_INVALID,
                    f"module {node.display_path!r} has no definition qualified name",
                )
            self.modules.append(
                PipelineModule(
                    name=name,
                    module_type=derive_module_type(module_qn),
                    inputs=inputs,
                    outputs=outputs,
                    execution_order=0,
                    compilability=compilability,
                    compiled_expression=compiled,
                    module_kind=kind,
                    auto_impl_context=auto_impl_context,
                    calc_def_name=node.calc_def_name,
                    calc_def_qualified_name=node.calc_def_qualified_name,
                    doc_comment=node.doc_comment,
                    calc_expressions=list(node.calc_expressions) or None,
                    source_file=node.source_file,
                    source_line=node.source_line,
                )
            )

    @staticmethod
    def _predicate_identities(node: ConstraintNode) -> dict[str, ConstraintFormalIdentity]:
        if node.predicate_ir is None:
            return {}
        identities: dict[str, ConstraintFormalIdentity] = {}

        def visit(expression: object) -> None:
            if isinstance(expression, FeatureReferenceNode):
                name = expression.reference.source_name
                if name:
                    target = expression.reference.target
                    identity = ConstraintFormalIdentity(
                        raw_name=name,
                        qualified_name=(target.qualified_name if target is not None else None),
                    )
                    prior = identities.get(name)
                    if prior is not None and prior != identity:
                        _fail(
                            ElaborationCode.SI_RENDERING_COLLISION,
                            f"constraint {node.display_path!r} has two predicate identities "
                            f"rendered as {name!r}",
                        )
                    identities[name] = identity
                return
            if isinstance(expression, OperatorNode):
                for operand in expression.operands:
                    visit(operand)
            elif isinstance(expression, UnitAnnotationNode):
                visit(expression.value)
            elif isinstance(expression, InvocationNode):
                for argument in expression.arguments:
                    visit(argument)

        visit(parse_expression(node.predicate_ir))
        return identities

    @staticmethod
    def _constraint_identity(node: ConstraintNode) -> tuple[str, str, str]:
        owner_instance_path = node.display_path.rsplit("__", 1)[0]
        if node.eligibility == "non_numerical":
            owner_instance_path = sanitize_qualified_name(node.usage_qualified_name)
            constraint_id = mint_constraint_id(
                instance_path=owner_instance_path,
                source_local=node.display_name,
                tuple_=(node.usage_qualified_name, node.owner_kind, node.source_form),
            )
            return constraint_id, owner_instance_path, f"{constraint_id}__evaluation"
        constraint_id = mint_constraint_id(
            instance_path=owner_instance_path,
            source_local=node.display_name,
            tuple_=(
                node.usage_qualified_name,
                owner_instance_path,
                node.membership_kind,
                node.is_negated,
            ),
        )
        return constraint_id, owner_instance_path, f"{constraint_id}__evaluation"

    @staticmethod
    def _constraint_module_type(
        constraint_id: str, owner_instance_path: str, source_local: str
    ) -> str:
        local_path = "__".join(owner_instance_path.split("__")[1:]) or owner_instance_path
        local_path = local_path.replace("[", "_").replace("]", "")
        base = "".join(
            part.capitalize() for part in f"{local_path}_{source_local}".split("_") if part
        )
        namespace = owner_instance_path.split("__", 1)[0].lower()
        if not base:
            base = sanitize_name(constraint_id).capitalize()
        return f"{namespace}.{base}ConstraintModule"

    def _build_constraint_modules(self) -> None:
        constraint_outputs: list[tuple[str, str]] = []
        for node in sorted(
            self.graph.constraints.values(), key=lambda item: item.node_id.to_wire()
        ):
            if node.eligibility == "non_numerical":
                reasons = ", ".join(node.exclusion_reasons)
                _CONSTRAINT_LOGGER.warning(
                    "Constraint %s at %s is not numerical and will not execute: %s",
                    node.usage_qualified_name,
                    node.exclusion_location or "<unknown>",
                    reasons,
                )
                continue
            if node.predicate_ir is None:
                _fail(
                    ElaborationCode.SI_SNAPSHOT_INVALID,
                    f"constraint {node.display_path!r} has no effective predicate IR",
                    consumer=node.node_id,
                    consumer_display=node.display_path,
                )
            constraint_id, owner_path, channel = self._constraint_identity(node)
            name = constraint_id.lower()
            self._claim_module(name, node.node_id)
            self._claim_channel(channel, f"constraint:{node.node_id.to_wire()}")
            identities = self._predicate_identities(node)
            inputs = self._regular_inputs(node)
            inputs = [
                item.model_copy(
                    update={
                        "formal_identity": identities.get(
                            item.param_name,
                            ConstraintFormalIdentity(
                                raw_name=item.param_name,
                                qualified_name=None,
                            ),
                        )
                    }
                )
                for item in inputs
            ]
            self.modules.append(
                PipelineModule(
                    name=name,
                    module_type=self._constraint_module_type(
                        constraint_id, owner_path, node.display_name
                    ),
                    inputs=inputs,
                    outputs=[
                        ModuleOutput(
                            field_name="evaluation",
                            python_type="ConstraintEvaluation",
                            channel_name=channel,
                        )
                    ],
                    execution_order=0,
                    module_kind=ModuleKind.CONSTRAINT,
                )
            )
            constraint_outputs.append((constraint_id, channel))

        if not constraint_outputs:
            return
        aggregator_name = "constraint_report_aggregator"
        self._claim_module(aggregator_name, "constraint-report-aggregator")
        self._claim_channel("constraint_report", "constraint-report")
        self.modules.append(
            PipelineModule(
                name=aggregator_name,
                module_type="constraints.ConstraintReportAggregatorModule",
                inputs=[
                    ModuleInput(
                        param_name=sanitize_name(constraint_id),
                        python_type="ConstraintEvaluation",
                        source=InputSource(source_type="module_output", producer_channel=channel),
                    )
                    for constraint_id, channel in constraint_outputs
                ],
                outputs=[
                    ModuleOutput(
                        field_name="constraint_report",
                        python_type="ConstraintReport",
                        channel_name="constraint_report",
                    )
                ],
                execution_order=0,
                module_kind=ModuleKind.REPORT_AGGREGATOR,
            )
        )

    def _build_output_aliases(self) -> list[OutputAlias]:
        aliases: list[OutputAlias] = []
        rendered: dict[tuple[str, str], OutputPortId] = {}
        for node in sorted(self.graph.attrs.values(), key=lambda item: item.node_id.to_wire()):
            if not node.is_alias:
                continue
            if not isinstance(node.alias_target, ProducerRef):
                continue
            channel = self.output_channels.get(node.alias_target.target)
            if channel is None:
                _fail(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"output alias {node.display_path!r} targets an absent producer",
                )
            instance_path = node.display_path.rsplit("__", 1)[0].split("__", 1)[-1]
            key = (instance_path, node.display_name)
            prior = rendered.get(key)
            if prior is not None and prior != node.alias_target.target:
                _fail(
                    ElaborationCode.SI_RENDERING_COLLISION,
                    f"distinct aliases render as {instance_path!r}/{node.display_name!r}",
                )
            rendered[key] = node.alias_target.target
            aliases.append(
                OutputAlias(
                    alias_name=node.display_name,
                    canonical_channel=channel,
                    instance_path=instance_path,
                    shape=("part_usage" if node.alias_shape == "part_usage" else "part_def"),
                )
            )
        return sorted(aliases, key=lambda item: (item.instance_path, item.alias_name))

    def _build_groups(self) -> list[ParameterGroup]:
        by_group: dict[str, tuple[str, Path, list[EntryPoint]]] = {}
        for qualified_name, entry in sorted(self.entry_points.items()):
            name, class_name, source_file = self.entry_sources[qualified_name]
            prior = by_group.get(name)
            if prior is not None and prior[:2] != (class_name, source_file):
                _fail(
                    ElaborationCode.SI_RENDERING_COLLISION,
                    f"distinct source files render as parameter group {name!r}",
                )
            if prior is None:
                by_group[name] = (class_name, source_file, [entry])
            else:
                prior[2].append(entry)
        return [
            ParameterGroup(
                name=name,
                class_name=class_name,
                source_file=source_file,
                parameters=sorted(parameters, key=lambda item: item.qualified_name),
            )
            for name, (class_name, source_file, parameters) in sorted(by_group.items())
        ]

    def _topological_modules(self) -> list[PipelineModule]:
        by_name = {module.name: module for module in self.modules}
        producer = {
            output.channel_name: module.name for module in self.modules for output in module.outputs
        }
        dependencies: dict[str, set[str]] = {name: set() for name in by_name}
        successors: dict[str, set[str]] = {name: set() for name in by_name}
        for module in self.modules:
            for input_ in module.inputs:
                if input_.source.source_type != "module_output":
                    continue
                channel = input_.source.producer_channel
                dependency = producer.get(channel or "")
                if dependency is None:
                    _fail(
                        ElaborationCode.SI_EDGE_DANGLING,
                        f"module {module.name!r} references absent channel {channel!r}",
                    )
                if dependency == module.name:
                    _fail(
                        ElaborationCode.SI_EDGE_DANGLING,
                        f"module {module.name!r} has a self dependency",
                    )
                dependencies[module.name].add(dependency)
                successors[dependency].add(module.name)

        ready = sorted(name for name, values in dependencies.items() if not values)
        ordered: list[str] = []
        while ready:
            current = ready.pop(0)
            ordered.append(current)
            for successor in sorted(successors[current]):
                dependencies[successor].discard(current)
                if (
                    not dependencies[successor]
                    and successor not in ordered
                    and successor not in ready
                ):
                    ready.append(successor)
                    ready.sort()
        if len(ordered) != len(by_name):
            cycle = sorted(set(by_name) - set(ordered))
            _fail(
                ElaborationCode.SI_EDGE_DANGLING,
                f"projected module dependency cycle: {cycle}",
            )
        result = []
        for execution_order, name in enumerate(ordered):
            result.append(by_name[name].model_copy(update={"execution_order": execution_order}))
        return result

    def _build_constraint_catalog(self) -> ConstraintCatalog | None:
        if not self.graph.constraints:
            return None
        entries: list[ConstraintCatalogEntry] = []
        excluded_records: list[ConstraintCatalogExcludedRecord] = []
        source_formals: dict[str, set[str]] = defaultdict(set)
        usage_records: dict[tuple[str, str], ConstraintCatalogUsageRecord] = {}
        for node in sorted(
            self.graph.constraints.values(), key=lambda item: item.node_id.to_wire()
        ):
            constraint_id, owner_path, channel = self._constraint_identity(node)
            if node.eligibility == "non_numerical":
                excluded_records.append(
                    ConstraintCatalogExcludedRecord(
                        constraint_id=constraint_id,
                        usage_qualified_name=node.usage_qualified_name,
                        source_form=node.source_form,
                        membership_kind=node.membership_kind,
                        exclusion=ConstraintExclusion(
                            kind="non_numerical",
                            reasons=list(node.exclusion_reasons),
                            location=node.exclusion_location or "<unknown>",
                        ),
                    )
                )
                continue
            if node.predicate_ir is None:
                _fail(
                    ElaborationCode.SI_SNAPSHOT_INVALID,
                    f"constraint {node.display_path!r} has no predicate IR",
                )
            definition_qn = node.definition_qualified_name or None
            if definition_qn is not None:
                source_formals[definition_qn].update(self._predicate_identities(node))
            entry = ConstraintCatalogEntry(
                constraint_id=constraint_id,
                usage_qualified_name=node.usage_qualified_name,
                source_local_identity=node.display_name,
                source_form=node.source_form,
                owner_qualified_name=node.owner_qualified_name,
                definition_qualified_name=definition_qn,
                owner_instance_path=owner_path,
                membership_kind=node.membership_kind,
                predicate_source_key=node.predicate_source_key,
                is_negated=node.is_negated,
                expected_value=not node.is_negated,
                predicate_ir=node.predicate_ir,
                evaluation_channel=channel,
            )
            entries.append(entry)
            usage_key = (node.usage_qualified_name, node.display_name)
            usage_records.setdefault(
                usage_key,
                ConstraintCatalogUsageRecord(
                    usage_qualified_name=node.usage_qualified_name,
                    source_local_identity=node.display_name,
                    source_form=node.source_form,
                    owner_kind=node.owner_kind,
                    owner_qualified_name=node.owner_qualified_name,
                    definition_qualified_name=definition_qn,
                    membership_kind=node.membership_kind,
                    is_negated=node.is_negated,
                    expected_value=not node.is_negated,
                ),
            )
        source_records = [
            ConstraintCatalogSourceRecord(
                definition_qualified_name=definition_qn,
                formal_names=sorted(formals),
            )
            for definition_qn, formals in sorted(source_formals.items())
        ]
        usages = [usage_records[key] for key in sorted(usage_records)]
        payload = {
            "source_records": [item.model_dump(mode="json") for item in source_records],
            "usage_records": [item.model_dump(mode="json") for item in usages],
            "concrete_entries": [item.model_dump(mode="json") for item in entries],
            "excluded_records": [item.model_dump(mode="json") for item in excluded_records],
        }
        fingerprint = hashlib.sha256(
            json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode()
        ).hexdigest()
        return ConstraintCatalog(
            source_records=source_records,
            usage_records=usages,
            concrete_entries=entries,
            excluded_records=excluded_records,
            fingerprint=fingerprint,
        )


def project(graph: InstanceGraph) -> ComputationGraph:
    """Render one complete resolved graph as a generation ``ComputationGraph``."""
    return _Projection(graph).run()
