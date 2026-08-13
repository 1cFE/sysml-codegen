import sys
from pathlib import Path
REPO = Path("/home/reid/1cfe/sysml-codegen-item7-rebuild")
sys.path.insert(0, str(REPO))
from tests.execution.real_teax import package_loader
from simkit.evaluation.evaluator import PreparedEvaluator
from simkit.study.bridge import CandidateBridge
PACKAGE = Path("/tmp/item5acc/d5_snap"); NAME="d5"
root = Path("/tmp/item5acc/teax_d5"); root.mkdir(parents=True, exist_ok=True)
loader = package_loader(PACKAGE, NAME, root/"link")
ev = PreparedEvaluator(loader, PACKAGE/"pipelines"/"pipeline.yaml", expects_constraint_report=True)
e = ev.evaluate(CandidateBridge(ev.entry_models).build({}))
print("d5 responses:", dict(sorted(e.responses.items())))
for k, v in sorted(e.outputs.items()):
    if any(t in k for t in ("cooling_power","p_electric_gross","p_net","parasitic")):
        print(f"  {k} = {v}")
