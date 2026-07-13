import sys, tempfile
from pathlib import Path
sys.path.insert(0, "/home/reid/1cfe/sysml-codegen/.project/active/spike-expression-tree-parity")
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from s2_ir import extract_ir

tmp = Path(tempfile.mkdtemp()) / "m.sysml"
tmp.write_text("""package p {
    private import ScalarValues::*;
    calc def C { in attribute a: Real; in attribute b: Real; in attribute c: Real; in attribute d: Real;
        out attribute q : Real = a * b * c * d; }
}""")
model, _ = SysideAdapter.load_model([tmp])
for cdef in SysideAdapter.elements_of_type(model, "CalculationDefinition"):
    for m in cdef.owned_elements:
        e = getattr(m, "feature_value_expression", None)
        if e is not None:
            def arity(n, d=0):
                ops = list(getattr(n, "operands", []) or [])
                print("  "*d + f"{type(n).__name__} op={getattr(n,'operator',None)} arity={len(ops)}")
                for o in ops: arity(o, d+1)
            arity(e)
            ir = extract_ir(e)
            print("IR json:", ir.to_json()[:300])
