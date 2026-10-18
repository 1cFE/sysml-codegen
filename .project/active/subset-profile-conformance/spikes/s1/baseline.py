"""Spike S1: baseline (unmutated) generator and screen halves for the ten cases, timed."""
import sys, time
sys.path.insert(0, __file__.rsplit("/", 1)[0])
t_import = time.perf_counter()
import harness as h
from sysml_codegen.cli import run_codegen  # noqa: F401  (warm import)
from agentic_mbse.sysml.subset_extraction import extract_subset_facts  # noqa: F401
print(f"imports {time.perf_counter()-t_import:.2f}s")
for c in h.CASES:
    g = h.run_generator(c)
    s = h.run_screen(c)
    print(f"{c.case_id}\n  GEN ok={g.ok} codes={g.codes} stubs={g.stubs} {g.seconds:.2f}s\n     {g.first_error[:160]}\n"
          f"  SCREEN {s.verdict} load={s.seconds_load:.2f}s extract={s.seconds_extract:.2f}s eval={s.seconds_eval:.3f}s\n     {s.findings}")
