"""Probe 1d (I1-CRITICAL): does a plain `out attribute` calc def (no return
clause — the shape every existing fixture uses) carry an OWNED
ReturnParameterMembership member? If yes with empty declared_name, V8 would
wrongly fire on existing fixtures and break byte-identity. Must be NO.
"""
import tempfile
from pathlib import Path

from sysml_codegen.core.qualified_names import sanitize_name
from sysml_codegen.extraction.extractor import SysMLDataExtractor

STYLE_A = """package StyleAProbe {
    private import ScalarValues::Real;
    calc def StyleA {
        in x : Real;
        out attribute y : Real = x * 2;
    }
}
"""


def would_v8_fire(cd):
    hits = []
    for m in cd.owned_members:
        om = type(getattr(m, "owning_membership", None)).__name__
        if om == "ReturnParameterMembership" and not sanitize_name(
            getattr(m, "declared_name", None)
        ):
            hits.append((getattr(m, "name", None), om))
    return hits


with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "a.sysml"
    p.write_text(STYLE_A)
    ex = SysMLDataExtractor([p])
    assert ex.load_models()
    for cd in ex.adapter.elements_of_type(ex.model, "CalculationDefinition"):
        members = [
            (getattr(m, "name", None),
             type(getattr(m, "owning_membership", None)).__name__,
             getattr(m, "declared_name", None))
            for m in cd.owned_members
        ]
        print(f"calc def {cd.name}: members={members}")
        print(f"  V8 would fire on: {would_v8_fire(cd)}  (MUST be [])")
