"""S2 probe 7: which scope makes the two-step resolve cross-part actuals?

plant_values' `viability` predicate returned (None, 1 diagnostic) with
scope=the assert usage (owned by the part def). The fixture supplies operand
values through usage-level mechanisms (retype / overrides), so the def-owned
scope may be too abstract. Try: the assert usage, the part def, the concrete
part usage, and evaluate_feature on the usage.

Run: uv run python .project/active/spike-expression-tree-parity/probe7_oracle_scope.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

REPO = Path(__file__).resolve().parents[3]
syside = get_syside()
compiler = syside.Compiler()

model, _ = SysideAdapter.load_model([REPO / "tests" / "fixtures" / "plant_values"])
usage = next(u for u in SysideAdapter.elements_of_type(model, "AssertConstraintUsage")
             if getattr(u, "name", None) == "viability")
predicate = usage.predicate.result_expression

part_def = usage.owner
print(f"assert usage owner: {type(part_def).__name__} name={getattr(part_def, 'name', None)!r}")

part_usages = list(SysideAdapter.elements_of_type(model, "PartUsage"))
print(f"part usages: {[getattr(p, 'name', None) for p in part_usages]}")

def try_scope(label, scope):
    try:
        v, report = compiler.evaluate(predicate, scope=scope)
        diags = [str(d) for d in list(getattr(report, "diagnostics", []) or [])]
        print(f"  scope={label}: value={v!r} diags={diags[:2]}")
    except Exception as e:
        print(f"  scope={label}: raised {e}")

print("\n--- evaluate(def predicate, scope=X) ---")
try_scope("assert usage", usage)
try_scope("part def", part_def)
for p in part_usages:
    try_scope(f"part usage {getattr(p, 'name', None)!r}", p)

# nested: viability lives on the plant part def; the concrete plant part usage
# may own a projected copy of the assert usage — check members
print("\n--- evaluate_feature(assert usage, scope=part usage) ---")
for p in part_usages:
    try:
        v, report = compiler.evaluate_feature(usage, p)
        diags = [str(d) for d in list(getattr(report, "diagnostics", []) or [])]
        print(f"  {getattr(p, 'name', None)!r}: value={v!r} diags={diags[:2]}")
    except Exception as e:
        print(f"  {getattr(p, 'name', None)!r}: raised {e}")
