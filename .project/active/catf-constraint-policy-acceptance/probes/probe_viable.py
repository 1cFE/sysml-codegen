import sys
from pathlib import Path
REPO = Path("/home/reid/1cfe/sysml-codegen-item7-rebuild")
sys.path.insert(0, str(REPO))
from tests.execution.real_teax import package_loader
from simkit.evaluation.evaluator import PreparedEvaluator
from simkit.study.bridge import CandidateBridge
PACKAGE = Path("/tmp/item5acc/route2_inplace"); NAME="catf_gated"
root = Path("/tmp/item5acc/teax4"); root.mkdir(parents=True, exist_ok=True)
loader = package_loader(PACKAGE, NAME, root/"link")
ev = PreparedEvaluator(loader, PACKAGE/"pipelines"/"pipeline.yaml", expects_constraint_report=True)
b = CandidateBridge(ev.entry_models)
A2 = "CATFMFEPhysics__catf_physics__net_power_viable__d8cad14493e47fbd"
A3 = "CATFMFEPhysics__catf_physics__parasitic_fraction_ok__280b94b2e8d184f5"
KEY = "CATFMFEPhysics__catf_physics__p_fusion"
print(f"{'p_fusion':>10} {'gross':>12} {'A2':>10} {'A3':>10} {'headline':>12}")
for pf in (2600.0, 5000.0, 10000.0, 14000.0, 16000.0, 20000.0, 30000.0, 60000.0):
    e = ev.evaluate(b.build({KEY: pf}))
    gross = e.outputs.get("CATFMFEPhysics__catf_physics__gross_electric__p_electric_gross")
    print(f"{pf:>10} {gross:>12.1f} {e.responses.get(A2):>10} {e.responses.get(A3):>10} {e.responses['headline']:>12}")
