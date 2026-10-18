"""G2 probe (Item 2a P1.1, plan PD10): does a usage-level override of a definition-owned
referenced multiplicity bound change the occurrence count?

`small : Site` is the control (definition bound, n = 2). `tuned : Site` overrides n to 3.
Runs the spike S1 harness's generator half (run_codegen, screen tripwired) and counts
the `racks` occurrences under each top-level part from the spied instance graph.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "s1"))

import harness  # noqa: E402
from sysml_codegen.orchestration import elaborated_pipeline  # noqa: E402

graphs = []
real = elaborated_pipeline.elaborate_model_paths


def spy(*a, **k):
    g = real(*a, **k)
    graphs.append(g)
    return g


elaborated_pipeline.elaborate_model_paths = spy
try:
    obs = harness.run_generator(harness.Case("g2", HERE / "model.sysml"))
finally:
    elaborated_pipeline.elaborate_model_paths = real

print(f"generated={obs.ok} codes={list(obs.codes)} stubs={list(obs.stubs)}")
graph = graphs[0]
by_id = graph.occurrences
counts: Counter[str] = Counter()
indices: dict[str, list[int | None]] = {}
for rec in by_id.values():
    if rec.display_segment.split("[")[0] != "racks" or rec.parent_id is None:
        continue
    parent = by_id[rec.parent_id].display_segment
    counts[parent] += 1
    indices.setdefault(parent, []).append(rec.occurrence_index)
for parent in sorted(counts):
    print(f"{parent}: racks occurrences={counts[parent]} indices={sorted(i for i in indices[parent] if i is not None)}")
