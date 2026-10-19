import sys; sys.path.insert(0,'/tmp/audit2a-recheck/perturb'); from edit import edit
import json
p="sysml-codegen/tests/expectations/subset_profile/cases/blocked-predicate-unmapped-code__untyped_assert.json"
d=json.load(open(p)); print("was", d["generator"]["reasons"]); d["generator"]["reasons"]=[]; open(p,"w").write(json.dumps(d,indent=2)+"\n")
