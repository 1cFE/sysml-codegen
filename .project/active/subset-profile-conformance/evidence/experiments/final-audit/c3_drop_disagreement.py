import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
import json
p="sysml-codegen/tests/expectations/subset_profile/disagreements.json"
d=json.load(open(p)); gone=[d["entries"].pop(0), d["entries"].pop(-1)]; json.dump(d,open(p,"w"),indent=2); open(p,"a").write("\n")
print("dropped", [g["subject"] for g in gone])
