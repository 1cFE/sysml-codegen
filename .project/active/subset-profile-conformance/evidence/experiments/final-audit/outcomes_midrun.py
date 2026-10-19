import json, sys, tempfile, logging
from pathlib import Path
logging.disable(logging.CRITICAL)
import sysml_codegen
from sysml_codegen.cli import GenerationConfig, run_codegen
from agentic_mbse.sysml.conformance_case import packaged_case_ids, packaged_case_dir
REPO = Path("/home/reid/src/subset-conformance/sysml-codegen")
F = REPO / "tests/fixtures"
roots = {}
fc = json.load(open(REPO / "tests/expectations/subset_profile/fixture_classes.json"))["fixtures"]
for name, v in fc.items():
    if v["class"] in ("generating", "refusing"):
        roots["fixture:" + name] = F / name
batch = json.load(open(F / "v6_recapture_batch/batch.json"))
for name in batch["fixtures"]:
    roots["fixture:" + name] = F / name
for c in packaged_case_ids():
    roots["case:" + c] = packaged_case_dir(c)
for d in sorted((F / "subset_profile_occurrence_seed").iterdir()):
    if d.is_dir():
        roots["seed:" + d.name] = d
out = {"__file__": sysml_codegen.__file__}
for key, root in sorted(roots.items()):
    with tempfile.TemporaryDirectory() as t:
        try:
            out[key] = run_codegen(GenerationConfig(output_path=Path(t) / "pkg", models_path=root))
        except Exception as e:
            out[key] = "EXC " + type(e).__name__
json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True)
print(sysml_codegen.__file__, len(out))
