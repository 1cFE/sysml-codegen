"""Spike S1 (B3): both halves over every tests/fixtures/<dir> that holds .sysml files, timed.
Treats each top-level fixture directory as one model root (fixture classes are not decided
here; this only measures cost)."""
import sys, time
from pathlib import Path
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness as h
root = Path("tests/fixtures")
rows = []
T0 = time.perf_counter()
for d in sorted(p for p in root.iterdir() if p.is_dir()):
    files = sorted(d.rglob("*.sysml"))
    if not files:
        continue
    case = h.Case(d.name, d)
    g = h.run_generator(case)
    from agentic_mbse.sysml.subset_extraction import extract_subset_facts
    from agentic_mbse.sysml.subset_profile import evaluate_subset_profile
    from agentic_mbse.sysml.syside_adapter import SysideAdapter
    t = time.perf_counter()
    try:
        model, _ = SysideAdapter.load_model(files)
        verdict = str(evaluate_subset_profile(extract_subset_facts(model)).verdict)
    except Exception as err:  # noqa: BLE001
        verdict = f"screen-error:{type(err).__name__}"
    st = time.perf_counter() - t
    rows.append((d.name, len(files), g.seconds, st, g.ok, verdict))
total = time.perf_counter() - T0
rows.sort(key=lambda r: -(r[2] + r[3]))
print(f"{len(rows)} fixture dirs with .sysml; total {total:.1f}s; generator sum {sum(r[2] for r in rows):.1f}s; screen sum {sum(r[3] for r in rows):.1f}s")
print("slowest 12 (name, files, gen s, screen s, generated, screen verdict):")
for r in rows[:12]:
    print(f"  {r[0]:45s} {r[1]:3d} {r[2]:6.2f} {r[3]:6.2f} {r[4]!s:5s} {r[5]}")
