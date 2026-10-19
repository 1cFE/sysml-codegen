"""Run run_codegen on every model root; record outcome, package hash, WARNING+ log records.

usage: PYTHONPATH=<tree>/src python outcomes.py <side> <out.json> [--dc3 <models_root>]
"""
import hashlib, json, logging, shutil, sys, traceback
from pathlib import Path

import sysml_codegen
from sysml_codegen.cli import GenerationConfig, run_codegen
from agentic_mbse.sysml.conformance_case import packaged_case_ids, packaged_case_dir

side, out_path = sys.argv[1], Path(sys.argv[2])
GATE = Path("/tmp/audit2a-gate")
F = GATE / "head/tests/fixtures"  # HEAD fixture paths for both sides
WORK = GATE / f"work-{side}"
KEEP = GATE / f"pkgs-{side}"

roots = {}
if "--dc3" in sys.argv:
    roots["dc3:repaired"] = Path(sys.argv[sys.argv.index("--dc3") + 1])
else:
    fc = json.load(open(GATE / "head/tests/expectations/subset_profile/fixture_classes.json"))["fixtures"]
    for name, v in fc.items():
        if v["class"] in ("generating", "refusing"):
            roots["fixture:" + name] = F / name
    batch = json.load(open(F / "v6_recapture_batch/batch.json"))
    for name in batch["fixtures"]:
        roots["fixture:" + name] = F / name
    for c in packaged_case_ids():
        roots["case:" + c] = packaged_case_dir(c)
    for d in sorted((F / "subset_profile").iterdir()):
        if d.is_dir():
            roots["home:" + d.name] = d
    for d in sorted((F / "subset_profile_occurrence_seed").iterdir()):
        if d.is_dir():
            roots["seed:" + d.name] = d


class Cap(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.recs = []

    def emit(self, r):
        msg = r.getMessage()
        if r.exc_info and r.exc_info[1] is not None:
            msg += " | exc=" + type(r.exc_info[1]).__name__
        self.recs.append([r.name, r.levelname, msg.replace(str(WORK), "<WORK>")])


def tree_hash(p: Path):
    h = hashlib.sha256()
    n = 0
    for f in sorted(x for x in p.rglob("*") if x.is_file() and "__pycache__" not in x.parts):
        h.update(str(f.relative_to(p)).encode() + b"\0" + f.read_bytes() + b"\0")
        n += 1
    return h.hexdigest(), n


cap = Cap()
root_logger = logging.getLogger()
root_logger.addHandler(cap)
root_logger.setLevel(logging.WARNING)

out = {"__file__": sysml_codegen.__file__, "roots": {}}
for key, root in sorted(roots.items()):
    cap.recs = []
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    pkg = WORK / "pkg"
    rec = {"root": str(root)}
    try:
        rec["result"] = run_codegen(GenerationConfig(output_path=pkg, models_path=root, package_name="audit_pkg"))
    except Exception as e:
        rec["result"] = "EXC " + type(e).__name__
        rec["exc"] = str(e).replace(str(WORK), "<WORK>")[:2000]
    if rec["result"] is True and pkg.exists():
        rec["sha"], rec["nfiles"] = tree_hash(pkg)
        dest = KEEP / key.replace(":", "__")
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(pkg, dest)
    rec["logs"] = cap.recs
    out["roots"][key] = rec
shutil.rmtree(WORK, ignore_errors=True)
json.dump(out, open(out_path, "w"), indent=1, sort_keys=True)
print(sysml_codegen.__file__, len(out["roots"]))
