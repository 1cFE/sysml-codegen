"""Round-2 design review: does `p_fusion` surface as a mutable key in the generated inputs JSON?

D6 mutates `p_fusion` in `inputs/*.json`. Nothing in the design measured that it is there.
License-free: reads `catf_mfe_d5`'s committed v6 snapshot. Throwaway.
"""

import json
from pathlib import Path

from sysml_codegen.cli import GenerationConfig, run_codegen

REPO = Path(__file__).resolve().parents[4]
out = REPO / ".tmp_review_r2_pkg"
snap = REPO / "tests/fixtures/catf_mfe_d5/instance_graph_snapshot.json"

print("snapshot exists:", snap.exists())
ok = run_codegen(
    GenerationConfig(
        output_path=out, from_snapshot=snap, package_name="catf", overwrite=True
    )
)
print("generated:", ok)
for p in sorted((out / "inputs").glob("*.json")):
    d = json.loads(p.read_text())
    hits = [k for k in d if "fusion" in k.lower()]
    if hits:
        print(p.name, "->", {k: d[k] for k in hits})
