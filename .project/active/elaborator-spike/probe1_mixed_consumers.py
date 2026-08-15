"""Probe 1: product-behavior checks on source_identity_mixed_consumers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from elab_prototype import elaborate  # noqa: E402

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
PKG = "source_identity_mixed_consumers"

g = elaborate(FIXTURES / PKG)
P = PKG  # path prefix

failures: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {label}{(' — ' + detail) if detail else ''}")
    if not cond:
        failures.append(label)


def inp(calc_id: str, param: str):
    calc = g.calcs.get(calc_id)
    return None if calc is None else calc.inputs.get(param)


# --- C25: the customer shape — two consumers, ONE node -----------------------
avail_node = f"{P}__avail_ctx__avail_plant__availability"
d = inp(f"{P}__avail_ctx__avail_plant__def_authored_calc", "value_in")
u = inp(f"{P}__avail_ctx__avail_plant__usage_authored_calc", "value_in")
check("C25 def-authored resolves to the occurrence node", d == ("node", avail_node), repr(d))
check("C25 usage-authored resolves to the SAME node", u == ("node", avail_node), repr(u))
check(
    "C25 node value is the occurrence override 0.8",
    g.attrs[avail_node].value == 0.8 and g.attrs[avail_node].value_site == "occurrence_override",
    repr((g.attrs[avail_node].value, g.attrs[avail_node].value_site)),
)

# --- C8: twins stay distinct -------------------------------------------------
a = inp(f"{P}__twin_bay__calc_a", "value_in")
b = inp(f"{P}__twin_bay__calc_b", "value_in")
check("C8 calc_a -> sensor_a.reading", a == ("node", f"{P}__twin_bay__sensor_a__reading"), repr(a))
check("C8 calc_b -> sensor_b.reading", b == ("node", f"{P}__twin_bay__sensor_b__reading"), repr(b))
check(
    "C8 distinct values 11.0 / 22.0",
    g.attrs[f"{P}__twin_bay__sensor_a__reading"].value == 11.0
    and g.attrs[f"{P}__twin_bay__sensor_b__reading"].value == 22.0,
)

# --- C24: chain to a computed value -> producer edge, never an input ---------
c = inp(f"{P}__computed_station__computed_calc", "value_in")
check(
    "C24 computed_calc -> producer output edge",
    c == ("output", f"{P}__computed_station__source_identity_computed__producer_calc", "result"),
    repr(c),
)

# --- C12 qualified / C13 bare / C15 cross-owner ------------------------------
q = inp(f"{P}__qual_station__qual_plant__qual_calc", "value_in")
check("C12 qualified -> occurrence node", q == ("node", f"{P}__qual_station__qual_plant__level"), repr(q))
check("C12 value is override 70.0", g.attrs[f"{P}__qual_station__qual_plant__level"].value == 70.0)

bare = inp(f"{P}__bare_station__bare_rig__bare_calc", "value_in")
check("C13 bare -> occurrence node", bare == ("node", f"{P}__bare_station__bare_rig__intensity"), repr(bare))
check("C13 value is override 30.0", g.attrs[f"{P}__bare_station__bare_rig__intensity"].value == 30.0)

ch = inp(f"{P}__parent_unit__child__child_calc", "value_in")
check("C15 cross-owner -> parent node", ch == ("node", f"{P}__parent_unit__shared_rate"), repr(ch))
check("C15 value is root override 40.0", g.attrs[f"{P}__parent_unit__shared_rate"].value == 40.0)

# --- stamp route: reference-derived vs authored literal ----------------------
s = inp(f"{P}__stamp_plant__stamp_calc", "value_in")
check("stamp_calc -> efficiency node (not a literal)", s == ("node", f"{P}__stamp_plant__efficiency"), repr(s))
check("efficiency value is override 0.75", g.attrs[f"{P}__stamp_plant__efficiency"].value == 0.75)
lit = inp(f"{P}__stamp_plant__lit_calc", "value_in")
check("authored literal stays a literal", lit == ("literal", 9.5), repr(lit))

# --- C11 chain calc + deep-path override -------------------------------------
cc = inp(f"{P}__station__chain_calc", "value_in")
check("C11 chain -> rig node", cc == ("node", f"{P}__station__rig__gain_setting"), repr(cc))
check("C11 value 42.0", g.attrs[f"{P}__station__rig__gain_setting"].value == 42.0)
deep = g.attrs.get(f"{P}__deep_design__panel_two__deep_rig__gain_setting")
check(
    "deep-path :>> lands on the nested occurrence node (43.0)",
    deep is not None and deep.value == 43.0 and deep.value_site == "occurrence_override",
    repr(None if deep is None else (deep.value, deep.value_site)),
)

# --- Bank: multiplicity [3] attr nodes ---------------------------------------
cells = [g.attrs.get(f"{P}__bank__cell[{i}]__cell_cost") for i in range(3)]
check(
    "Bank: three cell_cost occurrence nodes at 6.0",
    all(n is not None and n.value == 6.0 for n in cells),
    repr([None if n is None else n.value for n in cells]),
)

# --- constraint consumers (mixed_consumers has chain_guard etc.) -------------
guard = inp(f"{P}__station__chain_guard", "v")
check(
    "C11 constraint chain_guard -> SAME rig node as chain_calc",
    guard == ("node", f"{P}__station__rig__gain_setting"),
    repr(guard),
)

# --- one public input per node: count consumers of avail node ----------------
consumers = [
    (cid, param)
    for cid, calc in g.calcs.items()
    for param, ref in calc.inputs.items()
    if ref == ("node", avail_node)
]
check("C25 both consumers share ONE node (2 edges, 1 node)", len(consumers) == 2, repr(consumers))

print()
print(f"diagnostics: {g.diagnostics}")
print(f"attr nodes: {len(g.attrs)}  calc/constraint nodes: {len(g.calcs)}")
if failures:
    print(f"\nFAILURES: {failures}")
    sys.exit(1)
print("\nALL CHECKS PASS")
