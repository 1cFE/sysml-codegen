"""Throwaway elaborator prototype (ELABORATE-FIRST Item 3 spike). NOT production code.

elaborate(model) -> InstanceGraph:
  1. occurrence expansion (PartInstanceIndex — the existing walker)
  2. attribute nodes per occurrence, effective value by innermost-wins:
     occurrence :>> (deepest anchor) > specialized-def :>> > definition default
  3. calc/constraint nodes per occurrence (def-context remap — ONE rule, shared
     with override anchoring)
  4. binding resolution: evidence referent -> node ID, by ONE contextualization
     rule per referent class (chain root+members / def-level / usage-level)

Node ID = the occurrence instance_path extended with the member leaf, `__`-joined
(the same rendering PartInstanceIndex already produces).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_mbse.sysml.expression import (
    extract_literal_value,
    feature_chain_facts,
    resolved_target_fact,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.analysis.part_instance_index import build_part_instance_index
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
from sysml_codegen.extraction.source_evidence import screen_source_readiness
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages


class ElaborationError(Exception):
    pass


@dataclass
class AttrNode:
    node_id: str                 # occurrence path + "__" + attr name
    occurrence_path: str
    attr_name: str
    decl_qn: str                 # def-level declaration raw QN
    value: Any = None            # effective literal after tiering (None = no value)
    value_site: str = "none"     # occurrence_override | specialized_def | definition_default | none
    anchor_depth: int = -1       # depth of the winning occurrence override anchor


@dataclass
class CalcNode:
    node_id: str
    calc_def_qn: str
    kind: str                    # "calc" | "constraint"
    inputs: dict[str, Any] = field(default_factory=dict)   # param -> ("node", id) | ("output", calc_id, out) | ("literal", v)
    outputs: list[str] = field(default_factory=list)


@dataclass
class InstanceGraph:
    attrs: dict[str, AttrNode] = field(default_factory=dict)
    calcs: dict[str, CalcNode] = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)

    def attr_at(self, occurrence_path: str, attr_name: str) -> AttrNode | None:
        return self.attrs.get(f"{occurrence_path}__{attr_name}")


def _san(name: str) -> str:
    return name.replace(" ", "_").replace("'", "")


def _raw_leaf(qn: str) -> str:
    return qn.rsplit("::", 1)[-1].strip("'")


class Elaborator:
    def __init__(self, model: Any) -> None:
        self.model = model
        self.index = build_part_instance_index(model)
        self.hier = extract_hierarchy_data(model)
        self.graph = InstanceGraph()

        # Definition universe: sanitized def key -> def element (raw QN, attrs, heritage)
        self.defs: dict[str, Any] = {}
        self.def_raw_to_key: dict[str, str] = {}
        for pd in SysideAdapter.elements_of_type(model, "PartDefinition"):
            raw = str(getattr(pd, "qualified_name", "") or "")
            if not raw:
                continue
            key = _san(raw.replace("::", "__"))
            self.defs[key] = pd
            self.def_raw_to_key[raw] = key

        # Occurrences per def key; occurrence path -> (def key, steps)
        self.occs_by_def: dict[str, list[Any]] = {}
        self.occ_by_path: dict[str, Any] = {}
        for key in self.defs:
            try:
                occs = self.index.occurrences_of(key)
            except KeyError:
                occs = []
            self.occs_by_def[key] = occs
            for occ in occs:
                self.occ_by_path[occ.instance_path] = occ

        # part-usage raw QN -> its occurrences (exact reverse query, salvaged)
        self._usage_occ_cache: dict[str, list[Any]] = {}

    # ---- shared rule: def-context remap -----------------------------------
    def expand_def_context(self, sanitized_path: str) -> list[str]:
        """Longest def-key prefix of a definition-relative path -> one path per
        occurrence of that def. Occurrence-rooted paths pass through unchanged.
        THE rule that fixes C19 (definition-relative capture vs occurrence-
        relative demand) — also used to place def-declared calcs."""
        segments = sanitized_path.split("__")
        for cut in range(len(segments) - 1, 0, -1):
            prefix = "__".join(segments[:cut])
            if prefix in self.occs_by_def:
                tail = segments[cut:]
                occs = self.occs_by_def[prefix]
                return [
                    "__".join([occ.instance_path, *tail]) for occ in occs
                ]
        return [sanitized_path]

    def usage_occurrences(self, usage_raw_qn: str) -> list[Any]:
        if usage_raw_qn not in self._usage_occ_cache:
            self._usage_occ_cache[usage_raw_qn] = self.index.occurrences_of_part_usage(
                usage_raw_qn
            )
        return self._usage_occ_cache[usage_raw_qn]

    # ---- stage 2: attribute nodes -----------------------------------------
    def _def_attributes(self, pd: Any) -> list[tuple[str, str, Any]]:
        """(name, decl raw QN, default literal) for owned + inherited attributes."""
        out: list[tuple[str, str, Any]] = []
        seen: set[str] = set()
        stack = [pd]
        while stack:
            cur = stack.pop()
            for member in getattr(cur, "owned_members", None) or []:
                if type(member).__name__ != "AttributeUsage":
                    continue
                name = str(getattr(member, "name", "") or "")
                if not name or name in seen:
                    continue
                seen.add(name)
                decl = str(getattr(member, "qualified_name", "") or "")
                default = None
                expr = getattr(member, "feature_value_expression", None)
                if expr is not None:
                    try:
                        default = extract_literal_value(expr)
                    except Exception:
                        default = None
                out.append((name, decl, default))
            for heritage in getattr(cur, "heritage", None) or []:
                target = heritage[1] if isinstance(heritage, tuple) else getattr(
                    heritage, "general", None
                )
                if target is not None and type(target).__name__ == "PartDefinition":
                    stack.append(target)
        return out

    def build_attr_nodes(self) -> None:
        for key, occs in self.occs_by_def.items():
            pd = self.defs[key]
            attrs = self._def_attributes(pd)
            for occ in occs:
                for name, decl, default in attrs:
                    node_id = f"{occ.instance_path}__{name}"
                    self.graph.attrs[node_id] = AttrNode(
                        node_id=node_id,
                        occurrence_path=occ.instance_path,
                        attr_name=name,
                        decl_qn=decl,
                        value=default,
                        value_site="definition_default" if default is not None else "none",
                    )

    # ---- stage 2b: apply redefinitions, innermost-wins --------------------
    def apply_overrides(self) -> None:
        # tier 2 first (specialized-def :>> literals), so tier 1 overwrites.
        for rd in self.hier.redefinitions:
            if rd.literal_value is None:
                continue
            for path in self.expand_def_context(rd.owning_part_qn):
                node = self.graph.attrs.get(f"{path}__{rd.attribute_name}")
                if node is not None and node.value_site != "occurrence_override":
                    node.value = rd.literal_value
                    node.value_site = "specialized_def"

        # tier 1: occurrence overrides; deepest anchor wins.
        for ov in self.hier.design_overrides:
            if ov.literal_value is None:
                continue
            anchor_paths = self.expand_def_context(ov.owning_part_qn)
            tail = list(ov.target_path[:-1]) if ov.is_deep_path else []
            leaf = ov.target_path[-1] if ov.is_deep_path else ov.attribute_name
            for anchor in anchor_paths:
                depth = anchor.count("__")
                node_path = "__".join([anchor, *tail]) if tail else anchor
                node = self.graph.attrs.get(f"{node_path}__{leaf}")
                if node is None:
                    self.graph.diagnostics.append(
                        f"OVERRIDE_TARGET_MISSING: {ov.owning_part_qn}:>>{leaf} at {node_path}"
                    )
                    continue
                if node.value_site == "occurrence_override" and node.anchor_depth >= depth:
                    continue
                node.value = ov.literal_value
                node.value_site = "occurrence_override"
                node.anchor_depth = depth

    # ---- stage 3: calc + constraint nodes ---------------------------------
    def build_calc_nodes(self) -> None:
        usages, _report = extract_calculation_usages(self.model)
        findings = screen_source_readiness(usages)
        blocking = [f for f in findings if f.code.value == "SI_SELF_BINDING"]
        if blocking:
            lines = ", ".join(
                f"{f.usage_qualified_name}.{f.param_name}" for f in blocking
            )
            raise ElaborationError(f"SI_SELF_BINDING: {lines}")

        for usage in usages:
            if usage.is_template:
                continue
            for node_path in self.expand_def_context(usage.qualified_name):
                node = CalcNode(
                    node_id=node_path,
                    calc_def_qn=usage.calc_def_name,
                    kind="calc",
                )
                for b in usage.bindings:
                    node.inputs[b.param_name] = self._resolve_binding(node_path, b)
                self.graph.calcs[node_path] = node

        for cu in SysideAdapter.elements_of_type(
            self.model, "ConstraintUsage", include_subtypes=True
        ):
            raw = str(getattr(cu, "qualified_name", "") or "")
            if not raw:
                continue
            sanitized = _san(raw.replace("::", "__"))
            for node_path in self.expand_def_context(sanitized):
                if node_path == sanitized and not any(
                    node_path.startswith(p + "__") or node_path == p
                    for p in self.occ_by_path
                ):
                    continue  # template context with no occurrence
                node = CalcNode(node_id=node_path, calc_def_qn="", kind="constraint")
                for param in getattr(cu, "owned_members", None) or []:
                    expr = getattr(param, "feature_value_expression", None)
                    if expr is None:
                        continue
                    pname = str(getattr(param, "name", "") or "")
                    if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
                        root, _leaf, _qns, members, _idx = feature_chain_facts(expr)
                        node.inputs[pname] = self._resolve_chain(node_path, root, members)
                    elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
                        fact = resolved_target_fact(getattr(expr, "referent", None))
                        node.inputs[pname] = self._resolve_reference(node_path, fact)
                self.graph.calcs[node_path] = node

    # ---- stage 4: binding resolution (the contextualization rules) --------
    def _resolve_binding(self, consumer_path: str, binding: Any):
        ev = binding.reference_evidence
        if ev is None:
            return ("unresolved", "no-evidence", binding.source_path)
        if ev.source_form.value == "authored_literal":
            return ("literal", binding.literal_value)
        if ev.source_form.value == "feature_chain":
            return self._resolve_chain(consumer_path, ev.chain_root, ev.resolved_member_names)
        if ev.referent is not None:
            return self._resolve_reference(consumer_path, ev.referent)
        return ("unresolved", ev.source_form.value, binding.source_path)

    def _ancestors(self, consumer_path: str) -> list[str]:
        """Consumer's enclosing occurrence paths, innermost first."""
        segs = consumer_path.split("__")
        out = []
        for cut in range(len(segs) - 1, 0, -1):
            candidate = "__".join(segs[:cut])
            if candidate in self.occ_by_path:
                out.append(candidate)
        return out

    def _resolve_chain(self, consumer_path: str, root_fact: Any, members: tuple[str, ...]):
        """ONE chain rule: anchor the root usage at the innermost enclosing
        occurrence that contains it, then descend member names."""
        if root_fact is None:
            return ("unresolved", "chain-no-root", members)
        root_feature = root_fact.element_name or _raw_leaf(root_fact.qualified_name)
        for ancestor in self._ancestors(consumer_path):
            candidate = f"{ancestor}__{root_feature}"
            if candidate in self.occ_by_path or any(
                p.startswith(candidate + "[") for p in self.occ_by_path
            ):
                return self._descend(candidate, list(members))
        return ("unresolved", "chain-anchor-missing", root_fact.qualified_name)

    def _descend(self, base_path: str, members: list[str]):
        path = base_path
        for i, member in enumerate(members):
            calc_candidate = f"{path}__{member}"
            if calc_candidate in self.graph.calcs:
                rest = members[i + 1 :]
                if len(rest) == 1:
                    return ("output", calc_candidate, rest[0])
                return ("unresolved", "calc-chain-tail", tuple(rest))
            if i == len(members) - 1:
                node = self.graph.attrs.get(f"{path}__{member}")
                if node is not None:
                    return ("node", node.node_id)
                return ("unresolved", "member-missing", f"{path}__{member}")
            path = f"{path}__{member}"
        return ("unresolved", "empty-chain", base_path)

    def _resolve_reference(self, consumer_path: str, fact: Any):
        leaf = fact.element_name or _raw_leaf(fact.qualified_name)
        if fact.owner_is_definition:
            # def-level referent: innermost enclosing occurrence whose def
            # (incl. supertypes) declares it. Calc-def outputs never arrive here
            # as REFERENCE bindings in the probe corpus.
            owner_key = self.def_raw_to_key.get(fact.owner_qualified_name)
            for ancestor in self._ancestors(consumer_path):
                occ = self.occ_by_path[ancestor]
                if owner_key is not None and self._def_matches(occ, owner_key):
                    node = self.graph.attr_at(ancestor, leaf)
                    if node is not None:
                        return ("node", node.node_id)
            return ("unresolved", "def-referent-context-missing", fact.qualified_name)
        # usage-level referent (occurrence-rooted redefining feature): the owner
        # usage's occurrence on the consumer's ancestor chain, else unique.
        owner_qn = fact.owner_qualified_name
        occs = self.usage_occurrences(owner_qn)
        candidates = [o.instance_path for o in occs]
        on_chain = [
            p for p in candidates
            if consumer_path == p or consumer_path.startswith(p + "__")
        ]
        pick = on_chain or candidates
        if len(pick) == 1:
            node = self.graph.attr_at(pick[0], leaf)
            if node is not None:
                return ("node", node.node_id)
            return ("unresolved", "usage-referent-attr-missing", f"{pick[0]}__{leaf}")
        if not pick:
            return ("unresolved", "usage-referent-no-occurrence", owner_qn)
        return ("ambiguous", tuple(sorted(pick)), leaf)

    def _def_matches(self, occ: Any, owner_key: str) -> bool:
        if occ.part_def_qn == owner_key:
            return True
        pd = self.defs.get(occ.part_def_qn)
        stack = [pd] if pd is not None else []
        while stack:
            cur = stack.pop()
            raw = str(getattr(cur, "qualified_name", "") or "")
            if self.def_raw_to_key.get(raw) == owner_key:
                return True
            for heritage in getattr(cur, "heritage", None) or []:
                target = heritage[1] if isinstance(heritage, tuple) else getattr(
                    heritage, "general", None
                )
                if target is not None and type(target).__name__ == "PartDefinition":
                    stack.append(target)
        return False


def elaborate(fixture_dir) -> InstanceGraph:
    extractor = SysMLDataExtractor([fixture_dir])
    if not extractor.load_models():
        raise ElaborationError(f"load failed: {fixture_dir}")
    e = Elaborator(extractor.model)
    e.build_attr_nodes()
    e.apply_overrides()
    e.build_calc_nodes()
    return e.graph
