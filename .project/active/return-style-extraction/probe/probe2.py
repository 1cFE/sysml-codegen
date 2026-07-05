"""Probe 1c: find the property that distinguishes an ANONYMOUS return
(`return : Real = e`, name synthesized to `result`) from a NAMED return
(`return y : Real = e`, user name `y`). Both are ReferenceUsage(Out) with
owning_membership=ReturnParameterMembership, so V8 must key off the
declared-vs-synthesized name distinction, not membership alone.
"""
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import SysideAdapter
from sysml_codegen.extraction.extractor import SysMLDataExtractor

HERE = Path(__file__).parent

CANDIDATE_ATTRS = [
    "name", "declared_name", "declaredName", "short_name", "declared_short_name",
    "declaredShortName", "shortName", "effective_name", "is_implied",
]


def dump(path, label):
    ex = SysMLDataExtractor([path])
    assert ex.load_models(), f"load failed {path}"
    print(f"\n=== {label} ===")
    for cd in ex.adapter.elements_of_type(ex.model, "CalculationDefinition"):
        for m in cd.owned_members:
            om = type(getattr(m, "owning_membership", None)).__name__
            if om != "ReturnParameterMembership":
                continue
            vals = {}
            for a in CANDIDATE_ATTRS:
                try:
                    vals[a] = getattr(m, a, "<MISSING>")
                except Exception as e:  # noqa: BLE001
                    vals[a] = f"<ERR {type(e).__name__}>"
            print(f"  {cd.name} result member:")
            for a, v in vals.items():
                print(f"    {a} = {v!r}")


dump(HERE / "anon.sysml", "ANON return (expect declared name empty/None)")
dump(HERE / "named.sysml", "NAMED return (expect declared name 'y')")
dump(HERE / "styled" / "library.sysml", "STYLE D return attribute")
