"""SPIKE THROWAWAY — F-7: where does the occurrence information go missing?

Answers, by measurement, whether `comp_a::length` and `comp_b::length` resolve to two
distinct elements or to one shared element AT THE SYSIDE LAYER, before our elaborator
runs; then follows the same references into our own pipeline (evidence record ->
DeclarationId -> FeatureSlotId) and reports where the distinction survives or dies.
Contrasts the `.` feature-chain spelling for the same two values.

This is an INTERNALS probe by design — it reads the SysIDE AST and our own extraction
helpers directly, not the shipped CLI.

Run from the repo root:
    uv run python .project/active/self-binding-replacement/spike/probe_referent_identity.py
"""

import os
import sys
from pathlib import Path

SPIKE = Path(".project/active/self-binding-replacement/spike")
FIXTURES = SPIKE / "fixtures"


def _load_license() -> str:
    key = os.environ.get("SYSIDE_LICENSE_KEY")
    if key:
        return key
    env = Path("/home/reid/1cfe/agentic-mbse/.env")
    for line in env.read_text().splitlines():
        name, _, value = line.strip().partition("=")
        if name == "SYSIDE_LICENSE_KEY":
            os.environ["SYSIDE_LICENSE_KEY"] = value.strip().strip("'\"")
            return os.environ["SYSIDE_LICENSE_KEY"]
    return ""


key = _load_license()
if not key:
    sys.exit("FATAL: SYSIDE_LICENSE_KEY not set")
print(f"license key loaded (len {len(key)})")

from agentic_mbse.sysml.syside_adapter import SysideAdapter  # noqa: E402

from sysml_codegen.elaboration.identity import declaration_id_for  # noqa: E402
from sysml_codegen.elaboration.occurrence import build_feature_slot_index  # noqa: E402
from sysml_codegen.extraction import binding_evidence  # noqa: E402


def load(fixture: str):
    adapter = SysideAdapter()
    loaded = adapter.load_model([FIXTURES / fixture])
    return loaded[0] if isinstance(loaded, tuple) else loaded


def describe(elem, label: str, slots=None) -> dict:
    """Identity of one AST element, plus what our pipeline turns it into."""
    if elem is None:
        print(f"    {label}: <None>")
        return {}
    eid = SysideAdapter.element_id(elem)
    qn = getattr(elem, "qualified_name", None)
    owner = getattr(elem, "owning_namespace", None) or getattr(elem, "owner", None)
    owner_qn = getattr(owner, "qualified_name", None) if owner is not None else None
    print(f"    {label}:")
    print(f"        python id      = {id(elem)}")
    print(f"        metatype       = {type(elem).__name__}")
    print(f"        element_id     = {eid}")
    print(f"        qualified_name = {qn}")
    print(f"        owner          = {owner_qn}")
    redefs = []
    for r in getattr(elem, "owned_redefinitions", None) or []:
        rf = getattr(r, "redefined_feature", None)
        if rf is not None:
            redefs.append((str(getattr(rf, "qualified_name", None)), SysideAdapter.element_id(rf)))
    print(f"        owned_redefinitions -> {redefs if redefs else '(none)'}")
    out = {"element_id": eid, "qn": str(qn), "obj": elem}
    try:
        did = declaration_id_for(elem)
        out["declaration_id"] = did
        print(f"        OUR DeclarationId = {did.to_wire()}")
        if slots is not None:
            try:
                slot = slots.slot_of(did)
                out["slot"] = slot
                print(f"        OUR FeatureSlotId = {slot.root_declaration.to_wire()}")
            except KeyError as exc:
                print(f"        OUR FeatureSlotId = <KeyError: {exc}>")
    except Exception as exc:  # noqa: BLE001
        print(f"        OUR DeclarationId = <{type(exc).__name__}: {exc}>")
    return out


def bindings_of(model, calc_name: str):
    """(param_name, member, value expression) for one calc usage, by simple name."""
    for cu in SysideAdapter.elements_of_type(model, "CalculationUsage"):
        if str(getattr(cu, "name", "")) != calc_name:
            continue
        for member in getattr(cu, "owned_members", None) or []:
            name = getattr(member, "name", None)
            expr = getattr(member, "feature_value_expression", None)
            if name and expr is not None:
                yield str(name), member, expr


# ---------------------------------------------------------------- part 1 + 2
print()
print("=" * 78)
print("PART 1/2 — u7_both_spellings: SysIDE referents for :: and . , and what our")
print("           extraction/elaboration layers turn them into")
print("=" * 78)

model = load("u7_both_spellings")
slots = build_feature_slot_index(model)

captured: dict[str, dict] = {}

for calc_name, spelling in (("pair_calc", "::  qualified name"), ("dot_calc", ".   feature chain")):
    print()
    print(f"--- {calc_name}  [{spelling}]")
    for param, member, expr in bindings_of(model, calc_name):
        print(f"  binding: in {param} = {binding_evidence.written_reference_text(expr)!r}")
        print(f"      expression metatype = {type(expr).__name__}")
        if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
            ev = binding_evidence.chain_evidence(member, expr)
            target = getattr(expr, "target_feature", None)
            captured[f"{calc_name}.{param}"] = describe(target, "chain target_feature", slots)
        else:
            ev = binding_evidence.reference_evidence(member, expr)
            referent = getattr(expr, "referent", None)
            captured[f"{calc_name}.{param}"] = describe(referent, "expr.referent", slots)
        sr = ev.semantic_reference
        print(f"      OUR source_form        = {ev.source_form.value}")
        print(f"      OUR written_qualifier  = {ev.written_qualifier!r}")
        print(f"      OUR written_text       = {ev.written_text!r}")
        if sr is None:
            print("      OUR semantic_reference = None")
        else:
            print(f"      OUR semantic_reference.segments = {len(sr.segments)} segment(s)")
            root = getattr(sr.root, "element_id", None)
            leaf = getattr(sr.leaf, "element_id", None)
            print(f"          root.element_id = {root}")
            print(f"          leaf.element_id = {leaf}")
            print(f"          resolved_member_names = {sr.resolved_member_names}")

print()
print("--- IDENTITY COMPARISON (the F-7 question)")
for pair in (("pair_calc.a_len", "pair_calc.b_len"), ("dot_calc.a_len", "dot_calc.b_len")):
    a, b = captured.get(pair[0], {}), captured.get(pair[1], {})
    if not a or not b:
        print(f"  {pair[0]} vs {pair[1]}: <missing>")
        continue
    same_obj = a.get("obj") is b.get("obj")
    same_eid = a.get("element_id") == b.get("element_id")
    same_did = a.get("declaration_id") == b.get("declaration_id")
    same_slot = a.get("slot") == b.get("slot")
    print(f"  {pair[0]} vs {pair[1]}:")
    print(f"      same python object   = {same_obj}")
    print(f"      same SysIDE elem id  = {same_eid}   <-- DISTINCT or COLLAPSED at SysIDE")
    print(f"      same OUR DeclarationId = {same_did}")
    print(f"      same OUR FeatureSlotId = {same_slot}   <-- where our code normalises")

print()
print("--- the per-usage redefining features, if any (do distinct elements even exist?)")
for pu in SysideAdapter.elements_of_type(model, "PartUsage"):
    nm = str(getattr(pu, "name", ""))
    if nm not in ("comp_a", "comp_b"):
        continue
    print(f"  usage {nm}: qualified_name={getattr(pu, 'qualified_name', None)}")
    for member in getattr(pu, "owned_members", None) or []:
        describe(member, f"owned member of {nm} ({getattr(member, 'name', None)!r})", slots)

# ---------------------------------------------------------------- part 3
print()
print("=" * 78)
print("PART 3 — s3_path_named: what a feature chain gives, in kind")
print("=" * 78)
s3 = load("s3_path_named")
s3slots = build_feature_slot_index(s3)
for param, member, expr in bindings_of(s3, "cost_calc"):
    print(f"  binding: in {param} = {binding_evidence.written_reference_text(expr)!r}")
    print(f"      expression metatype = {type(expr).__name__}")
    ev = binding_evidence.chain_evidence(member, expr)
    sr = ev.semantic_reference
    print(f"      OUR source_form = {ev.source_form.value}")
    print(f"      OUR authored_segments = {ev.authored_segments}")
    if sr is not None:
        print(f"      OUR semantic_reference.segments = {len(sr.segments)} segment(s)")
        print(f"          resolved_member_names = {sr.resolved_member_names}")
        for i, seg in enumerate(sr.segments):
            print(f"          segment[{i}].element_id = {getattr(seg, 'element_id', None)}"
                  f"  qn={getattr(seg, 'qualified_name', None)}")
    describe(getattr(expr, "target_feature", None), "chain target_feature", s3slots)
    for attr in ("operands", "arguments"):
        ops = getattr(expr, attr, None)
        if ops:
            print(f"      expr.{attr}: {[type(o).__name__ for o in ops]}")
            for o in ops:
                describe(getattr(o, "referent", None), f"  operand referent ({attr})", s3slots)

print()
print("done.")
