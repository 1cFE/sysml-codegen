import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
p="sysml-codegen/src/sysml_codegen/elaboration/occurrence.py"
open(p,"a").write('\n\nclass _AuditRefusal(Exception):\n    pass\n\n\ndef _audit_check(x):\n    if not x:\n        raise _AuditRefusal("audit")\n    return x\n')
print("appended new exception class and raise")
