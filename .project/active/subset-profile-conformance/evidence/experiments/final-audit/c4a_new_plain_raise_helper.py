import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
p="sysml-codegen/src/sysml_codegen/elaboration/elaborate.py"
open(p,"a").write('\n\ndef _audit_require_owner(owner):\n    if owner is None:\n        raise ValueError("audit: owner missing")\n    return owner\n')
print("appended helper with plain raise")
