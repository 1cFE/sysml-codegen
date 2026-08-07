"""Probe 2: C19 (nested occurrence override, 80.0) + fusion_tea self-binding diagnostic."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from elab_prototype import ElaborationError, elaborate  # noqa: E402

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures"

failures: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {label}{(' — ' + detail) if detail else ''}")
    if not cond:
        failures.append(label)


# --- C19: the fixture the string pipeline cannot fix -------------------------
P = "nested_occurrence_override_probe"
g = elaborate(FIXTURES / P)
target = f"{P}__the_design__panel__source__reading"

node = g.attrs.get(target)
check(
    "C19 deep-path :>> 80.0 lands on the occurrence node",
    node is not None and node.value == 80.0 and node.value_site == "occurrence_override",
    repr(None if node is None else (node.value, node.value_site)),
)

calc = g.calcs.get(f"{P}__the_design__panel__noop")
calc_ref = None if calc is None else calc.inputs.get("x")
check("C19 CALC consumer reads that node", calc_ref == ("node", target), repr(calc_ref))

guard = g.calcs.get(f"{P}__the_design__panel__within")
guard_ref = None if guard is None else guard.inputs.get("v")
check("C19 CONSTRAINT consumer reads that node", guard_ref == ("node", target), repr(guard_ref))

check("C19 no diagnostics", not g.diagnostics, repr(g.diagnostics))

# --- fusion_tea: in gain = gain must fail loudly, never reinterpret ----------
try:
    elaborate(FIXTURES / "fusion_tea")
    check("fusion_tea self-binding raises SI_SELF_BINDING", False, "no error raised")
except ElaborationError as err:
    msg = str(err)
    check(
        "fusion_tea self-binding raises SI_SELF_BINDING",
        msg.startswith("SI_SELF_BINDING") and "gain" in msg,
        msg[:140],
    )

if failures:
    print(f"\nFAILURES: {failures}")
    sys.exit(1)
print("\nALL CHECKS PASS")
