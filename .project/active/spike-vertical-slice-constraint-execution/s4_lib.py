"""S4 shared test-only lowering + generation library. Throwaway spike code.

Implements the S4 vertical slice on wi014_toy:

- capture_constraint_facts(): live SysIDE -> JSON-safe constraint facts sidecar
  (S1 shapes, S2 ExpressionIR via the reused s2_ir module, S3's owner-instance
  index captured from part structure, never from calc templates).
- lower_constraints(): strict actual resolution against the OutputRegistry +
  design attributes. Unresolved => LoweringError. Never synthesizes an entry
  point, never falls back.
- build_s4_package(): targeted backtracking with the resolved constraint input
  channels joined as roots BEFORE pruning; graph extension with one constraint
  module per concrete assertion + the exact-schema report aggregator; production
  generators for the ordinary artifacts; test-only emitters for the constraint
  schema/modules/registry; test-only ModelContract + PackageContract seal.

Deviations from production paths are deliberate probe seams and are recorded in
findings.md.
"""

from __future__ import annotations

import hashlib
import json
import sys
import types
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SPIKE_DIR = Path(__file__).resolve().parent
S2_DIR = SPIKE_DIR.parent / "spike-expression-tree-parity"
REPO = SPIKE_DIR.parents[2]
FIXTURE = REPO / "tests" / "fixtures" / "wi014_toy"
PACKAGE_NAME = "wi014_s4"
SIDECAR_NAME = "constraint_facts.s4.json"
SIDECAR_FORMAT = "s4-constraint-facts-test-only-v1"

for p in (str(S2_DIR), str(REPO / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

import s2_ir  # noqa: E402  (S2's provisional IR: extract/serialize/compile)
from sysml_codegen.analysis.dependency_backtracker import (  # noqa: E402
    DependencyBacktracker,
)
from sysml_codegen.core.identifier_types import ScopedKey  # noqa: E402
from sysml_codegen.core.qualified_names import (  # noqa: E402
    sanitize_name,
    sanitize_qualified_name,
)
from sysml_codegen.resolution.graph_builder import (  # noqa: E402
    _validate_channel_references,
    build_computation_graph,
    collect_uncovered_params,
)
from sysml_codegen.resolution.models import (  # noqa: E402
    ComputationGraph,
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleOutput,
    ParameterGroup,
    PipelineModule,
)


class LoweringError(Exception):
    """Strict resolution failure: an assertion actual could not be resolved."""


class SidecarError(Exception):
    """Constraint-facts sidecar missing or malformed: refuse, never degrade."""


# ---------------------------------------------------------------------------
# Components: the shared substrate both legs (live / snapshot) provide.
# ---------------------------------------------------------------------------


@dataclass
class Components:
    calc_defs: list[Any]
    calc_usages: list[Any]
    design_attrs: dict[Path, list[Any]]
    group_deriver: Any
    registry: Any
    hierarchy_data: Any
    computed_attributes: list[Any]
    aggregation_expressions: list[Any]
    channel_aliases: list[Any]
    compilation_results: dict[str, Any] = field(default_factory=dict)


def components_from_live_ctx(ctx) -> Components:
    """Adapt a live PipelineContext. wi014 has no supplied-value synth attrs
    (asserted), so ctx.design_attributes == the graph-side copy."""
    hd = ctx.hierarchy_data
    assert not (hd and (hd.redefinitions or hd.design_overrides)), (
        "wi014_toy unexpectedly carries redefinitions/overrides; the probe's "
        "design_attrs shortcut would diverge from the graph-side copy"
    )
    return Components(
        calc_defs=ctx.calc_defs,
        calc_usages=ctx.calc_usages,
        design_attrs=ctx.design_attributes,
        group_deriver=ctx.group_deriver,
        registry=ctx.output_registry,
        hierarchy_data=hd,
        computed_attributes=ctx.computed_attributes,
        aggregation_expressions=ctx.aggregation_expressions,
        channel_aliases=ctx.channel_aliases,
        compilation_results=ctx.compilation_results,
    )


def components_from_snapshot(snapshot_path: Path) -> Components:
    """Adapt the production snapshot rebuild inputs (no syside license)."""
    from sysml_codegen.snapshot.graph_rebuild import (
        build_classifier_inputs_from_snapshot,
    )

    inputs = build_classifier_inputs_from_snapshot(snapshot_path)
    snap = inputs["snap"]
    return Components(
        calc_defs=snap["calc_defs"],
        calc_usages=snap["calc_usages"],
        design_attrs=inputs["design_attrs"],
        group_deriver=inputs["group_deriver"],
        registry=inputs["registry"],
        hierarchy_data=snap["hierarchy_data"],
        computed_attributes=snap["computed_attributes"],
        aggregation_expressions=snap["aggregation_expressions"],
        channel_aliases=snap.get("channel_aliases", []),
        compilation_results=snap.get("compilation_results") or {},
    )


# ---------------------------------------------------------------------------
# Stage 1 (live only): capture constraint facts + owner-instance index.
# ---------------------------------------------------------------------------


def capture_constraint_facts(model) -> dict:
    """Live SysIDE -> JSON-safe facts doc (S1 shapes; S3 part-structure index)."""
    from agentic_mbse.sysml.syside_adapter import SysideAdapter

    facts = []
    # S1: sweep the ConstraintUsage base so no source form is missed; wi014 has
    # exactly one AssertConstraintUsage. Classify afterward.
    asserts = list(SysideAdapter.elements_of_type(model, "AssertConstraintUsage"))
    for usage in asserts:
        cdef = usage.predicate
        owner = usage.owner
        owner_qn = str(owner.qualified_name)

        predicate_ir = s2_ir.extract_ir(cdef.result_expression)

        # S1 pinned quirk: ConstraintDefinition.parameters omits the declared
        # inputs in 0.8.4; recover by owner-filtered AttributeUsage enumeration.
        cdef_qn = str(cdef.qualified_name)
        formals = []
        for attr in SysideAdapter.elements_of_type(model, "AttributeUsage"):
            attr_owner = getattr(attr, "owner", None)
            if attr_owner is None or str(getattr(attr_owner, "qualified_name", "")) != cdef_qn:
                continue
            fv = getattr(attr, "feature_value_expression", None)
            formals.append(
                {
                    "name": sanitize_name(attr.name),
                    "has_default": fv is not None,
                    "default_ir": s2_ir.extract_ir(fv).to_json() if fv is not None else None,
                }
            )

        actuals = []
        for member in usage.owned_members:
            if not (
                SysideAdapter.is_instance(member, "AttributeUsage")
                or SysideAdapter.is_instance(member, "ReferenceUsage")
            ):
                continue
            fv = getattr(member, "feature_value_expression", None)
            if fv is None:
                continue
            actuals.append(
                {
                    "formal": sanitize_name(member.name),
                    "ir": s2_ir.extract_ir(fv).to_json(),
                }
            )

        # S3 direction: owner instances from PART STRUCTURE (PartUsage typed by
        # the owner def), never from calc templates. wi014: demo_plant.
        owner_instances = []
        for pu in SysideAdapter.elements_of_type(model, "PartUsage"):
            pu_def = None
            defs = list(getattr(pu, "definitions", []) or [])
            if defs:
                pu_def = defs[0]
            elif hasattr(pu, "definition"):
                pu_def = pu.definition
            if pu_def is None or str(getattr(pu_def, "qualified_name", "")) != owner_qn:
                continue
            instance_eqn = sanitize_qualified_name(str(pu.qualified_name))
            owner_instances.append(
                {
                    "instance_eqn": instance_eqn,
                    # dotted resolution scope: design-prefix-stripped instance path
                    "scope": ".".join(instance_eqn.split("__")[1:]),
                }
            )
        owner_instances.sort(key=lambda i: i["instance_eqn"])

        loc = SysideAdapter.source_location(usage) if hasattr(SysideAdapter, "source_location") else None
        facts.append(
            {
                "usage_name": sanitize_name(usage.name),
                "source_form": "definition_typed",
                "membership_kind": "assert",
                "is_negated": bool(usage.is_negated),
                "owner_kind": "part_def",
                "owner_qn": owner_qn,
                "definition_qn": str(cdef.qualified_name),
                "predicate_ir": predicate_ir.to_json(),
                "formals": sorted(formals, key=lambda f: f["name"]),
                "actuals": actuals,
                "owner_instances": owner_instances,
                "source_location": str(loc) if loc else None,
            }
        )

    facts.sort(key=lambda f: (f["owner_qn"], f["usage_name"]))
    return {"format": SIDECAR_FORMAT, "facts": facts}


def write_sidecar(facts_doc: dict, snapshot_dir: Path) -> Path:
    path = snapshot_dir / SIDECAR_NAME
    path.write_text(json.dumps(facts_doc, indent=2, ensure_ascii=False) + "\n")
    return path


def load_sidecar(snapshot_dir: Path) -> dict:
    """Strict boundary (S3 lesson): a missing/foreign sidecar refuses loudly."""
    path = snapshot_dir / SIDECAR_NAME
    if not path.exists():
        raise SidecarError(
            f"constraint-facts sidecar missing: {path}. The model asserts "
            "constraints; refusing to generate an assertion-free package. "
            "Re-capture with probe_a_live.py."
        )
    doc = json.loads(path.read_text())
    if doc.get("format") != SIDECAR_FORMAT:
        raise SidecarError(
            f"sidecar format {doc.get('format')!r} != {SIDECAR_FORMAT!r}; re-capture."
        )
    return doc


# ---------------------------------------------------------------------------
# Stage 2: strict lowering (facts -> ConcreteConstraint dicts).
# ---------------------------------------------------------------------------


def _design_attr_index(design_attrs: dict[Path, list[Any]]) -> dict[str, Any]:
    idx: dict[str, Any] = {}
    for attrs in design_attrs.values():
        for a in attrs:
            if a.qualified_name:
                idx[a.qualified_name] = a
    return idx


def _resolve_actual_strict(
    actual_ir: s2_ir.IRNode,
    scope: str,
    registry,
    design_attr_by_qn: dict[str, Any],
    what: str,
) -> dict:
    """Strict resolution of one assertion actual. Exactly two legal outcomes:
    a producer channel or a design-attribute entry point. Anything else raises.
    """
    if actual_ir.kind != "feature_ref":
        raise LoweringError(f"{what}: actual is not a feature reference ({actual_ir.kind})")

    if actual_ir.segments:  # feature chain, e.g. cost_calc.cost
        dotted = ".".join(actual_ir.segments)
        key = f"{scope}.{dotted}" if scope else dotted
        channel = registry.scoped_lookup(ScopedKey(key))
        if channel is None:
            raise LoweringError(
                f"{what}: chain '{dotted}' unresolved in scope '{scope}' "
                "(strict mode: no fallback, no entry-point synthesis)"
            )
        return {"resolution": "module_output", "channel": channel, "source_expr": dotted}

    # plain reference: match the referent QN against design attributes exactly
    qn_raw = "::".join(actual_ir.target_qn or []) or (actual_ir.source_name or "")
    qn = sanitize_qualified_name(qn_raw)
    attr = design_attr_by_qn.get(qn)
    if attr is not None:
        default = None
        if attr.default_value is not None:
            try:
                default = float(attr.default_value)
            except (TypeError, ValueError):
                default = None
        return {
            "resolution": "entry_point",
            "qualified_name": qn,
            "default_value": default,
            "source_expr": actual_ir.source_name,
        }

    # owner-scope reference to a sibling calc output (not present in wi014,
    # but keep the rule symmetric): scoped channel by source name.
    if actual_ir.source_name:
        channel = registry.scoped_lookup(ScopedKey(f"{scope}.{actual_ir.source_name}"))
        if channel is not None:
            return {
                "resolution": "module_output",
                "channel": channel,
                "source_expr": actual_ir.source_name,
            }

    raise LoweringError(
        f"{what}: reference '{qn_raw}' resolved to neither a design attribute "
        "nor a producer channel (strict mode: generation error, never synthesized)"
    )


def lower_constraints(facts_doc: dict, components: Components) -> list[dict]:
    """Expand facts per owner instance and strictly resolve every actual."""
    design_attr_by_qn = _design_attr_index(components.design_attrs)
    concrete: list[dict] = []

    for fact in facts_doc["facts"]:
        predicate_ir = s2_ir.IRNode.from_json(fact["predicate_ir"])
        actual_by_formal = {a["formal"]: a for a in fact["actuals"]}

        # Strict formal coverage: every formal needs an actual or a modeled default.
        for formal in fact["formals"]:
            if formal["name"] not in actual_by_formal and not formal["has_default"]:
                raise LoweringError(
                    f"{fact['usage_name']}: formal '{formal['name']}' has no actual "
                    "and no modeled default"
                )

        if not fact["owner_instances"]:
            raise LoweringError(
                f"{fact['usage_name']}: owner '{fact['owner_qn']}' has no concrete "
                "instances — expected instance cannot be formed (validation error)"
            )

        for inst in fact["owner_instances"]:
            cid = f"{inst['instance_eqn']}__{fact['usage_name']}"
            inputs = []
            for formal in fact["formals"]:
                fname = formal["name"]
                if fname in actual_by_formal:
                    ir = s2_ir.IRNode.from_json(actual_by_formal[fname]["ir"])
                    res = _resolve_actual_strict(
                        ir,
                        inst["scope"],
                        components.registry,
                        design_attr_by_qn,
                        what=f"{cid}.{fname}",
                    )
                else:  # modeled default becomes an overridable contract parameter
                    res = {
                        "resolution": "modeled_default",
                        "default_ir": formal["default_ir"],
                    }
                res["formal"] = fname
                inputs.append(res)

            concrete.append(
                {
                    "constraint_id": cid,
                    "usage_name": fact["usage_name"],
                    "definition_qn": fact["definition_qn"],
                    "owner_qn": fact["owner_qn"],
                    "owner_instance_eqn": inst["instance_eqn"],
                    "membership_kind": fact["membership_kind"],
                    "is_negated": fact["is_negated"],
                    "expected_value": (not fact["is_negated"]),
                    "predicate_ir": fact["predicate_ir"],
                    "inputs": inputs,
                }
            )

    concrete.sort(key=lambda c: c["constraint_id"])  # catalog ordering: by ID
    return concrete


# ---------------------------------------------------------------------------
# Stage 3: targeted graph with constraint roots, then graph extension.
# ---------------------------------------------------------------------------


def targeted_graph(
    components: Components,
    targets: list[str],
    extra_root_channels: list[str],
) -> ComputationGraph:
    """Backtrack from targets + constraint-root channels, pruning enabled."""
    bt = DependencyBacktracker(
        components.calc_usages,
        components.calc_defs,
        design_attributes=components.design_attrs,
        output_registry=components.registry,
    )
    root_targets = list(targets)
    for channel in extra_root_channels:
        usage = bt._find_usage_for_channel(channel)
        if usage is None:
            raise LoweringError(f"no producing usage for constraint root channel {channel}")
        out_name = channel.rsplit("__", 1)[1]
        root_targets.append(f"{usage.instance_name}.{out_name}")

    result = bt.find_required_modules(root_targets, include_all=False)
    hd = components.hierarchy_data
    return build_computation_graph(
        result=result,
        calc_defs=components.calc_defs,
        design_attrs=components.design_attrs,
        group_deriver=components.group_deriver,
        output_registry=components.registry,
        compilation_results=components.compilation_results,
        computed_attributes=components.computed_attributes,
        aggregation_data=components.aggregation_expressions,
        hierarchy_redefinitions=hd.redefinitions if hd else None,
        usage_type_map=hd.usage_type_map if hd else None,
        channel_aliases=components.channel_aliases,
        include_all=False,
    )


def _pascal(s: str) -> str:
    return "".join(part.capitalize() for part in s.split("_") if part)


def _constraint_module_identity(c: dict) -> dict:
    """Names/paths for one concrete constraint module (probe convention)."""
    inst_local = "__".join(c["owner_instance_eqn"].split("__")[1:])  # demo_plant
    base = _pascal(f"{inst_local}_{c['usage_name']}")  # DemoPlantAffordable
    namespace = c["owner_instance_eqn"].split("__")[0].lower()  # toy_plant
    file_stem = f"{inst_local}_{c['usage_name']}".lower()
    return {
        "yaml_key": c["constraint_id"].lower(),
        "class_name": f"{base}ConstraintModule",
        "input_class": f"{base}ConstraintInput",
        "output_class": f"{base}ConstraintOutput",
        "module_type": f"{namespace}.{base}ConstraintModule",
        "namespace": namespace,
        "file_stem": file_stem,
        "import_module": f"modules.{namespace}.{file_stem}",
        "evaluation_channel": f"{c['constraint_id']}__evaluation",
    }


AGGREGATOR = {
    "yaml_key": "constraint_report_aggregator",
    "class_name": "ConstraintReportAggregatorModule",
    "module_type": "constraints.ConstraintReportAggregatorModule",
    "namespace": "constraints",
    "file_stem": "constraint_report_aggregator",
    "import_module": "modules.constraints.constraint_report_aggregator",
    "report_channel": "constraint_report",
}


def extend_graph(
    graph: ComputationGraph,
    concrete: list[dict],
    components: Components,
) -> ComputationGraph:
    """Append one constraint module per concrete assertion + the aggregator,
    and mint entry points for entry-point-resolved actuals in their derived
    parameter groups. Then re-run the graph-level validations (channel refs,
    V11 coverage)."""
    modules = [m.model_copy(deep=True) for m in graph.modules]
    groups = [g.model_copy(deep=True) for g in graph.entry_point_groups]

    # --- mint entry points for constraint actuals -------------------------
    derived = components.group_deriver.derive_groups()

    def group_for(qn: str) -> tuple[str, str, str]:
        for dg in derived:
            if any(ps.name == qn for ps in dg.parameters):
                return dg.name, dg.class_name, dg.source_identifier
        return "system_design", "SystemDesign", "hierarchy"

    existing_param_qns = {p.qualified_name for g in groups for p in g.parameters}
    for c in concrete:
        for inp in c["inputs"]:
            if inp["resolution"] != "entry_point":
                continue
            qn = inp["qualified_name"]
            gname, gclass, gsource = group_for(qn)
            inp["param_group"] = gname
            if qn in existing_param_qns:
                continue
            ep = EntryPoint(
                qualified_name=qn,
                simple_name=qn.split("__")[-1],
                entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                default_value=inp["default_value"],
                param_group=gname,
            )
            target = next((g for g in groups if g.name == gname), None)
            if target is None:
                target = ParameterGroup(
                    name=gname, class_name=gclass,
                    source_file=Path(gsource), parameters=[],
                )
                groups.append(target)
            target.parameters.append(ep)
            existing_param_qns.add(qn)

    for g in groups:
        g.parameters.sort(key=lambda p: p.qualified_name)
    groups.sort(key=lambda g: g.name)

    # --- constraint modules ------------------------------------------------
    order = len(modules)
    for c in concrete:
        ident = _constraint_module_identity(c)
        inputs = []
        for inp in c["inputs"]:
            if inp["resolution"] == "module_output":
                src = InputSource(source_type="module_output", producer_channel=inp["channel"])
            elif inp["resolution"] == "entry_point":
                src = InputSource(
                    source_type="entry_point",
                    param_group=inp["param_group"],
                    qualified_name=inp["qualified_name"],
                )
            else:
                raise LoweringError(
                    f"{c['constraint_id']}: modeled-default formals are not exercised "
                    "by this fixture; refusing to guess"
                )
            inputs.append(ModuleInput(param_name=inp["formal"], python_type="float", source=src))

        modules.append(
            PipelineModule(
                name=ident["yaml_key"],
                module_type=ident["module_type"],
                inputs=inputs,
                outputs=[
                    ModuleOutput(
                        field_name="evaluation",
                        python_type="ConstraintEvaluation",
                        channel_name=ident["evaluation_channel"],
                    )
                ],
                execution_order=order,
                calc_def_name=None,
                calc_def_qualified_name=None,
            )
        )
        order += 1

    # --- report aggregator (exact schema: one required field per assertion) --
    agg_inputs = [
        ModuleInput(
            param_name=c["constraint_id"],
            python_type="ConstraintEvaluation",
            source=InputSource(
                source_type="module_output",
                producer_channel=_constraint_module_identity(c)["evaluation_channel"],
            ),
        )
        for c in concrete
    ]
    modules.append(
        PipelineModule(
            name=AGGREGATOR["yaml_key"],
            module_type=AGGREGATOR["module_type"],
            inputs=agg_inputs,
            outputs=[
                ModuleOutput(
                    field_name="constraint_report",
                    python_type="ConstraintReport",
                    channel_name=AGGREGATOR["report_channel"],
                )
            ],
            execution_order=order,
        )
    )

    extended = ComputationGraph(
        modules=modules,
        entry_point_groups=groups,
        execution_order=[m.name for m in modules],
        fallback_entry_points=set(graph.fallback_entry_points),
        output_aliases=graph.output_aliases,
    )
    _validate_channel_references(extended.modules)
    uncovered = collect_uncovered_params(extended)
    if uncovered:
        raise LoweringError(f"V11 coverage violations in extended graph: {uncovered}")
    return extended


# ---------------------------------------------------------------------------
# Stage 4: test-only emitters (constraint schema / modules / registry / contracts)
# ---------------------------------------------------------------------------

CONSTRAINT_TYPES_SRC = '''"""Constraint evidence schemas (S4 test-only shapes)."""

from typing import Literal, Optional

from pydantic import BaseModel


class ConstraintEvaluation(BaseModel):
    """One assertion verdict in one concrete context. Violation is evidence,
    never an exception."""

    constraint_id: str
    actual_value: Optional[bool] = None
    status: Literal["satisfied", "violated", "indeterminate"]
    margin: Optional[float] = None
    observed: dict[str, float]


class ConstraintReport(BaseModel):
    """Assertion evidence and coverage for one design point."""

    catalog_fingerprint: str
    assessed_count: int
    headline: Literal["violation", "indeterminate", "all_satisfied", "not_assessed"]
    results: list[ConstraintEvaluation]
'''


def _emit_constraint_module(c: dict, package_name: str) -> tuple[Path, str]:
    ident = _constraint_module_identity(c)
    ir = s2_ir.IRNode.from_json(c["predicate_ir"])
    pred_src, args = s2_ir.compile_predicate(ir, "_predicate", negated=c["is_negated"])
    observed = ", ".join(f'"{a}": float({a})' for a in args)
    sig = ", ".join(f"{a}: float" for a in args)
    call = ", ".join(f"{a}={a}" for a in args)

    src = f'''"""Constraint module for {c["constraint_id"]} (S4 test-only generation).

Effective predicate: {c["definition_qn"]} in owner instance {c["owner_instance_eqn"]}.
Membership: {c["membership_kind"]}; negated: {c["is_negated"]}.
Three-valued (Kleene) semantics; a verdict against the assertion NEVER raises.
"""

from pydantic import BaseModel
from simkit.config.schema import MultiOutput
from simkit.core.base import ModuleBase, ModuleResult

from {package_name}.schemas.constraint_types import ConstraintEvaluation

{pred_src}

class {ident["input_class"]}(BaseModel):
    """Exact input schema: one field per resolved formal."""
{chr(10).join(f"    {a}: float" for a in args)}


class {ident["output_class"]}(MultiOutput):
    evaluation: ConstraintEvaluation


class {ident["class_name"]}(ModuleBase[{ident["input_class"]}, {ident["output_class"]}]):
    name: str = "{ident["yaml_key"]}"
    version: str = "s4-probe"

    CONSTRAINT_ID = "{c["constraint_id"]}"

    def run(self, {sig}) -> ModuleResult[{ident["output_class"]}]:
        {ident["input_class"]}({call})  # validate inside run()
        verdict = _predicate({call})
        return ModuleResult(
            data={ident["output_class"]}(
                evaluation=ConstraintEvaluation(
                    constraint_id=self.CONSTRAINT_ID,
                    actual_value=verdict["value"],
                    status=verdict["status"],
                    margin=verdict["margin"],
                    observed={{{observed}}},
                )
            )
        )
'''
    return Path("modules") / ident["namespace"] / f"{ident['file_stem']}.py", src


def _emit_aggregator(concrete: list[dict], package_name: str, catalog_fp: str) -> tuple[Path, str]:
    ids = [c["constraint_id"] for c in concrete]
    fields = "\n".join(f"    {cid}: ConstraintEvaluation" for cid in ids) or "    pass"
    src = f'''"""Constraint report aggregator (S4 test-only generation).

Exact input schema: one REQUIRED field per concrete assertion — a missing
result is a schema failure, not a silent gap. Exists even for zero assertions.
"""

from pydantic import BaseModel
from simkit.config.schema import MultiOutput
from simkit.core.base import ModuleBase, ModuleResult

from {package_name}.schemas.constraint_types import ConstraintEvaluation, ConstraintReport

EXPECTED_IDS = {tuple(ids)!r}


class ConstraintReportAggregatorInput(BaseModel):
    model_config = {{"extra": "forbid"}}

{fields}


class ConstraintReportAggregatorOutput(MultiOutput):
    constraint_report: ConstraintReport


class {AGGREGATOR["class_name"]}(
    ModuleBase[ConstraintReportAggregatorInput, ConstraintReportAggregatorOutput]
):
    name: str = "{AGGREGATOR["yaml_key"]}"
    version: str = "s4-probe"

    CATALOG_FINGERPRINT = "{catalog_fp}"

    def run(self, **evaluations) -> ModuleResult[ConstraintReportAggregatorOutput]:
        validated = ConstraintReportAggregatorInput(**evaluations)
        results = [getattr(validated, cid) for cid in EXPECTED_IDS]
        statuses = [r.status for r in results]
        if "violated" in statuses:
            headline = "violation"
        elif "indeterminate" in statuses:
            headline = "indeterminate"
        elif results:
            headline = "all_satisfied"
        else:
            headline = "not_assessed"
        return ModuleResult(
            data=ConstraintReportAggregatorOutput(
                constraint_report=ConstraintReport(
                    catalog_fingerprint=self.CATALOG_FINGERPRINT,
                    assessed_count=len(results),
                    headline=headline,
                    results=results,
                )
            )
        )
'''
    return Path("modules") / AGGREGATOR["namespace"] / f"{AGGREGATOR['file_stem']}.py", src


def _emit_registry(
    graph_ext: ComputationGraph,
    concrete: list[dict],
    package_name: str,
    template_env,
) -> str:
    """Render the production registry template with constraint-aware context.

    Mirrors generation/registry.py for calc-usage modules (wi014 has no FORMULA
    or aggregation modules on this slice), then appends the constraint modules,
    the aggregator, and the constraint schema types. This bypass is itself a
    finding: production registry generation needs module_kind awareness.
    """
    from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName
    from sysml_codegen.generation.registry import (
        _collect_exit_point_primitive_types,
        _generate_schema_imports_from_entry_points,
        _resolve_class_name_collisions,
    )

    constraint_keys = {c["constraint_id"].lower() for c in concrete} | {AGGREGATOR["yaml_key"]}
    ordinary = [m for m in graph_ext.modules if m.name not in constraint_keys]

    schema_imports = _generate_schema_imports_from_entry_points(
        package_name, graph_ext.entry_point_groups
    )
    schema_imports.append(
        f"from {package_name}.schemas.constraint_types "
        "import ConstraintEvaluation as ConstraintEvaluation, "
        "ConstraintReport as ConstraintReport"
    )
    schema_imports.sort()

    group_names = [g.class_name for g in graph_ext.entry_point_groups]
    group_names += ["ConstraintEvaluation", "ConstraintReport"]

    all_modules: list[dict] = []
    imports: list[str] = [
        "from simkit.core.registry_builder import create_registry",
        "from simkit.core.pipeline_registry import PipelineModuleRegistry",
        "",
    ]

    seen: set[str] = set()
    calc_imports: list[str] = []
    for module in ordinary:
        if module.is_computed_attribute or module.is_aggregation:
            raise LoweringError("unexpected module kind on the wi014 S4 slice")
        if module.calc_def_name in seen:
            continue
        class_name = f"{module.calc_def_name}Module"
        all_modules.append({"class_name": class_name, "module_type": module.module_type})
        sqn = SysMLQualifiedName(module.calc_def_qualified_name)
        pp = PythonModulePath.from_sysml(sqn)
        calc_imports.append(f"from {package_name}.modules.{pp.import_path} import {class_name}")
        seen.add(module.calc_def_name)
    calc_imports.sort()
    imports.extend(calc_imports)

    constraint_imports: list[str] = []
    for c in concrete:
        ident = _constraint_module_identity(c)
        all_modules.append(
            {"class_name": ident["class_name"], "module_type": ident["module_type"]}
        )
        constraint_imports.append(
            f"from {package_name}.{ident['import_module'].replace('/', '.')} "
            f"import {ident['class_name']}"
        )
    all_modules.append(
        {"class_name": AGGREGATOR["class_name"], "module_type": AGGREGATOR["module_type"]}
    )
    constraint_imports.append(
        f"from {package_name}.{AGGREGATOR['import_module'].replace('/', '.')} "
        f"import {AGGREGATOR['class_name']}"
    )
    constraint_imports.sort()
    imports.extend(constraint_imports)

    all_modules, imports = _resolve_class_name_collisions(all_modules, imports)
    all_modules.sort(key=lambda m: m["module_type"])

    context = {
        "function_name": f"create_{package_name}_registry",
        "all_modules": all_modules,
        "imports": imports,
        "schema_imports": schema_imports,
        "parameter_groups": group_names,
        "package_name": package_name,
        "exit_point_types": _collect_exit_point_primitive_types(graph_ext.modules),
    }
    code = template_env.get_template("registry_function.py.jinja2").render(**context)
    return code if code.endswith("\n") else code + "\n"


# ---------------------------------------------------------------------------
# Stage 5: catalog + contracts + seal
# ---------------------------------------------------------------------------


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(text_or_bytes) -> str:
    data = text_or_bytes if isinstance(text_or_bytes, bytes) else text_or_bytes.encode()
    return hashlib.sha256(data).hexdigest()


def build_catalog(facts_doc: dict, concrete: list[dict]) -> tuple[dict, str]:
    """Two-level catalog: source records + concrete entries, ordered by ID."""
    source_records = [
        {
            "usage_name": f["usage_name"],
            "source_form": f["source_form"],
            "membership_kind": f["membership_kind"],
            "is_negated": f["is_negated"],
            "owner_qn": f["owner_qn"],
            "definition_qn": f["definition_qn"],
            "predicate_ir": f["predicate_ir"],
            "source_location": f["source_location"],
        }
        for f in facts_doc["facts"]
    ]
    entries = [
        {
            "constraint_id": c["constraint_id"],
            "source_usage": c["usage_name"],
            "owner_instance": c["owner_instance_eqn"],
            "membership_kind": c["membership_kind"],
            "is_negated": c["is_negated"],
            "expected_value": c["expected_value"],
            "eligible": True,
            "inputs": [
                {k: v for k, v in inp.items() if k != "default_ir"} for inp in c["inputs"]
            ],
            "response_metadata": {"margin": "simple_inequality_signed"},
        }
        for c in concrete
    ]
    catalog = {"source_records": source_records, "concrete_entries": entries}
    return catalog, _sha256(_canonical(catalog))


def write_contracts(
    out_dir: Path,
    graph_ext: ComputationGraph,
    catalog: dict,
    catalog_fp: str,
) -> None:
    contracts = out_dir / "contracts"
    contracts.mkdir(parents=True, exist_ok=True)
    (contracts / "constraint_catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    )

    parameters = [
        {
            "id": p.qualified_name,
            "group": g.name,
            "python_type": p.python_type,
            "default_value": p.default_value,
            "entry_type": p.entry_type.value,
        }
        for g in graph_ext.entry_point_groups
        for p in g.parameters
    ]
    outputs = [
        {"channel": o.channel_name, "python_type": o.python_type, "field": o.field_name}
        for m in graph_ext.modules
        for o in m.outputs
    ]
    model_contract = {
        "parameters": parameters,
        "outputs": outputs,
        "constraint_catalog_fingerprint": catalog_fp,
        "evaluation_semantics": "kleene-three-valued-s4",
    }
    model_contract["semantic_fingerprint"] = _sha256(_canonical(model_contract))
    (contracts / "model_contract.json").write_text(
        json.dumps(model_contract, indent=2, ensure_ascii=False) + "\n"
    )


def seal_package(out_dir: Path) -> dict:
    """Content-hash every artifact (excluding the seal itself); write the seal."""
    seal_path = out_dir / "contracts" / "package_contract.json"
    hashes: dict[str, str] = {}
    for path in sorted(out_dir.rglob("*")):
        if not path.is_file() or path == seal_path or "__pycache__" in path.parts:
            continue
        hashes[str(path.relative_to(out_dir))] = _sha256(path.read_bytes())
    seal = {
        "artifact_hashes": hashes,
        "executable_fingerprint": _sha256(
            "\n".join(f"{k}:{v}" for k, v in sorted(hashes.items()))
        ),
        "generator": "s4-probe",
    }
    seal_path.write_text(json.dumps(seal, indent=2, ensure_ascii=False) + "\n")
    return seal


def verify_seal(out_dir: Path) -> None:
    seal_path = out_dir / "contracts" / "package_contract.json"
    seal = json.loads(seal_path.read_text())
    for rel, expected in seal["artifact_hashes"].items():
        actual = _sha256((out_dir / rel).read_bytes())
        if actual != expected:
            raise RuntimeError(f"seal violation: {rel} hash mismatch")
    extras = {
        str(p.relative_to(out_dir))
        for p in out_dir.rglob("*")
        if p.is_file() and p != seal_path and "__pycache__" not in p.parts
    } - set(seal["artifact_hashes"])
    if extras:
        raise RuntimeError(f"seal violation: unhashed files present: {sorted(extras)}")


# ---------------------------------------------------------------------------
# Stage 6: full package generation (production generators + test-only emitters)
# ---------------------------------------------------------------------------


def generate_s4_package(
    components: Components,
    facts_doc: dict,
    out_dir: Path,
) -> dict:
    """Build control + extended graphs, generate all artifacts, seal. Returns a
    JSON-safe summary used by the probes' assertions."""
    from sysml_codegen.cli import (
        GenerationConfig,
        _check_duplicate_output_paths,
        _clear_output_directory,
        _generate_entry_points,
        _generate_modules,
        _generate_pipeline,
        _generate_primitives,
        _generate_schemas,
        _generate_stencils,
        _get_template_env,
        _reconcile_params_coverage,
        _setup_output_directories,
    )

    # Minimal exit selection: the ONLY target is area_calc.area, so cost_calc
    # can survive pruning only via the constraint dependency.
    area_usage = next(
        u for u in components.calc_usages if u.qualified_name.endswith("__area_calc")
    )
    base_targets = [f"{area_usage.instance_name}.area"]

    # Control: pruning without lowering must drop cost_calc.
    control = targeted_graph(components, base_targets, [])

    # Lowering: strict resolution; resolved channels join the roots BEFORE pruning.
    concrete = lower_constraints(facts_doc, components)
    root_channels = [
        inp["channel"]
        for c in concrete
        for inp in c["inputs"]
        if inp["resolution"] == "module_output"
    ]
    ordinary = targeted_graph(components, base_targets, root_channels)
    extended = extend_graph(ordinary, concrete, components)

    catalog, catalog_fp = build_catalog(facts_doc, concrete)

    config = GenerationConfig(
        output_path=out_dir, package_name=PACKAGE_NAME, overwrite=True,
        pipeline_name="pipeline",
    )
    template_env = _get_template_env()

    ctx_ordinary = types.SimpleNamespace(computation_graph=ordinary)
    ctx_extended = types.SimpleNamespace(computation_graph=extended)

    # Production preflight (V11 on the extended graph; duplicate paths on the
    # ordinary modules — constraint modules carry no calc-def path identity yet,
    # a module_kind gap recorded in findings).
    _check_duplicate_output_paths(ordinary.modules)
    _reconcile_params_coverage(extended)

    _clear_output_directory(config)
    _setup_output_directories(config)
    _generate_primitives(config)
    _generate_schemas(ctx_ordinary, config, template_env)
    _generate_modules(ctx_ordinary, config, template_env)
    _generate_stencils(ctx_ordinary, config, template_env)
    _generate_pipeline(ctx_extended, config, template_env)
    _generate_entry_points(ctx_extended, config, template_env)

    # Test-only constraint artifacts.
    (out_dir / "schemas" / "constraint_types.py").write_text(CONSTRAINT_TYPES_SRC)
    for c in concrete:
        rel, src = _emit_constraint_module(c, PACKAGE_NAME)
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        init = path.parent / "__init__.py"
        if not init.exists():
            init.write_text('"""Namespace package for generated modules."""\n')
        path.write_text(src)
    rel, src = _emit_aggregator(concrete, PACKAGE_NAME, catalog_fp)
    path = out_dir / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    init = path.parent / "__init__.py"
    if not init.exists():
        init.write_text('"""Namespace package for generated modules."""\n')
    path.write_text(src)

    (out_dir / "__init__.py").write_text(
        _emit_registry(extended, concrete, PACKAGE_NAME, template_env)
    )

    write_contracts(out_dir, extended, catalog, catalog_fp)
    seal = seal_package(out_dir)

    return {
        "control_modules": sorted(m.name for m in control.modules),
        "extended_modules": [m.name for m in extended.modules],
        "root_channels": root_channels,
        "constraint_ids": [c["constraint_id"] for c in concrete],
        "entry_point_qns": sorted(
            p.qualified_name for g in extended.entry_point_groups for p in g.parameters
        ),
        "entry_groups": sorted(g.name for g in extended.entry_point_groups),
        "catalog_fingerprint": catalog_fp,
        "executable_fingerprint": seal["executable_fingerprint"],
        "n_artifacts": len(seal["artifact_hashes"]),
    }
