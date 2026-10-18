"""Spike S1: for the two non-flipping witnesses, show which raise site actually fires (baseline
and under elision), by recording the raising frame of every exception constructed."""
import sys, traceback
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness as h
import elide as e
from sysml_codegen.extraction.expression_compiler import CompilationError
from sysml_codegen.elaboration.occurrence import OccurrenceResolutionError

def trace_inits(cls, log):
    orig = cls.__init__
    def init(self, *a, **k):
        f = sys._getframe(1)
        log.append(f"{cls.__name__} at {f.f_code.co_filename.rsplit('/src/',1)[-1]}:{f.f_lineno} {f.f_code.co_qualname}: {str(a[-1] if a else k)[:90]}")
        orig(self, *a, **k)
    cls.__init__ = init
    return lambda: setattr(cls, "__init__", orig)

for site, cid in [
    ("sysml_codegen/elaboration/occurrence.py::build_containment_address::coded::SI_OCCURRENCE_MISSING::1",
     "candidate-es-002__constraint_binds_calc_input__binding_value"),
    ("sysml_codegen/extraction/calc_compat_renderer.py::_render_operator::free-text::CompilationError::1",
     "calc_stub_operator"),
]:
    case = next(c for c in h.CASES if c.case_id == cid)
    for label in ("baseline", "elided"):
        log = []
        undo = [trace_inits(CompilationError, log), trace_inits(OccurrenceResolutionError, log)]
        el = e.elide(site) if label == "elided" else None
        try:
            g = h.run_generator(case)
        finally:
            if el: el.restore()
            for u in undo: u()
        print(f"{cid} [{label}] ok={g.ok} codes={g.codes} stubs={g.stubs}")
        print("   error:", g.first_error[:180])
        for line in log: print("   raised:", line)
