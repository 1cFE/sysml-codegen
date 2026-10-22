"""Write the stop-parser-execution-provenance/v1 manifest for one lane folder (args: L, codegen sha)."""
import hashlib, json, sys
from pathlib import Path
L = Path(sys.argv[1]); CG = sys.argv[2]
A = L / "artifacts"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
codegen_tar = A / f"codegen-{CG[:8]}.tar"
teax_tar = A / "teax-8d877460.tar"
wheel = A / "agentic_mbse-0.1.3-py3-none-any.whl"
TX = "8d877460ac4f6f264561d916e40c1708adb13397"
AG = "e268357fa8a5b23bac7fb17ff972a5a812801b3b"
m = {
  "schema_version": "stop-parser-execution-provenance/v1",
  "artifact_root": str(A),
  "python": {"executable": str(L / "venv/bin/python"), "version": "3.12.3"},
  "roots": {
    "codegen_source": {"path": str(L / "codegen/src"), "commit": CG, "artifact_path": str(codegen_tar), "archive_sha256": sha(codegen_tar)},
    "agentic_install": {"path": str(L / "venv/lib/python3.12/site-packages"), "commit": AG, "artifact_path": str(wheel), "wheel_sha256": sha(wheel)},
    "teax_source": {"path": str(L / "teax-clone"), "commit": TX, "artifact_path": str(teax_tar), "archive_sha256": sha(teax_tar)},
    "teax_simkit": {"path": str(L / "teax-clone/packages/teax-simkit"), "commit": TX, "artifact_path": str(teax_tar), "archive_sha256": sha(teax_tar)},
  },
}
(L / "provenance.json").write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
