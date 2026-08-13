import sys, json
from pathlib import Path
REPO = Path("/home/reid/1cfe/sysml-codegen-item7-rebuild")
sys.path.insert(0, str(REPO))
from tests.execution.real_teax import package_loader
PACKAGE = Path("/tmp/item5acc/route2_inplace"); NAME="catf_gated"
from simkit.evaluation.evaluator import PreparedEvaluator
from simkit.study.bridge import CandidateBridge
root = Path("/tmp/item5acc/teax3"); root.mkdir(parents=True, exist_ok=True)
loader = package_loader(PACKAGE, NAME, root/"link")
ev = PreparedEvaluator(loader, PACKAGE/"pipelines"/"pipeline.yaml", expects_constraint_report=True)
b = CandidateBridge(ev.entry_models)
pf = [f for ch, m in ev.entry_models.items() for f in m.model_fields if "p_fusion" in f]
print("p_fusion fields:", pf)
e = ev.evaluate(b.build({}))
print("\nRESPONSES:")
for k, v in sorted(e.responses.items()): print(f"  {k} = {v!r}")
print("\nOUTPUTS (net/electric/parasitic):")
for k, v in sorted(e.outputs.items()):
    if any(t in k for t in ("net","electric","parasitic","p_fusion")): print(f"  {k} = {v}")
print("\ntotal outputs:", len(e.outputs))
