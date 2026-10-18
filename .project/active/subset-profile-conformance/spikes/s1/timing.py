"""Spike S1 (B3): end-to-end time of the ten base cases in one fresh process.

Reports process-level import time, the first (cold) case, then REPEATS warm passes over the
ten cases, timing the generator half (run_codegen with the screen tripwire) and the screen
half (load + extract + evaluate) separately. One elided-site mutation pass is timed too.
"""
import statistics, sys, time
T0 = time.perf_counter()
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness as h
import elide as e
from sysml_codegen.cli import run_codegen  # noqa: F401
from agentic_mbse.sysml.subset_extraction import extract_subset_facts  # noqa: F401
T_IMPORT = time.perf_counter() - T0
CASES = h.CASES[:10]
REPEATS = 5

t = time.perf_counter(); h.run_generator(CASES[0]); h.run_screen(CASES[0]); T_COLD = time.perf_counter() - t
gen, scr, passes = [], [], []
for _ in range(REPEATS):
    p0 = time.perf_counter()
    for c in CASES:
        g = h.run_generator(c); s = h.run_screen(c)
        gen.append(g.seconds); scr.append(s.seconds_load + s.seconds_extract + s.seconds_eval)
    passes.append(time.perf_counter() - p0)
t = time.perf_counter(); e.site_rows(); T_SCAN = time.perf_counter() - t
site = "sysml_codegen/elaboration/occurrence.py::_multiplicity_indices::coded::SI_MULTIPLICITY_UNSUPPORTED::3"
t = time.perf_counter(); el = e.elide(site); T_ELIDE = time.perf_counter() - t
t = time.perf_counter(); [h.run_generator(c) for c in CASES]; T_MUT = time.perf_counter() - t; el.restore()
print(f"cases: {[c.case_id[:40] for c in CASES]}")
print(f"import {T_IMPORT:.2f}s, first case cold (both halves) {T_COLD:.2f}s, site scan {T_SCAN:.2f}s, one elision {T_ELIDE*1000:.1f}ms")
print(f"warm pass over 10 cases, both halves: median {statistics.median(passes):.3f}s (all: {', '.join(f'{x:.3f}' for x in passes)})")
print(f"per case: generator median {statistics.median(gen)*1000:.1f}ms max {max(gen)*1000:.1f}ms; screen median {statistics.median(scr)*1000:.1f}ms max {max(scr)*1000:.1f}ms")
print(f"10 generator runs under one mutation: {T_MUT:.3f}s")
print(f"process total {time.perf_counter()-T0:.2f}s")
