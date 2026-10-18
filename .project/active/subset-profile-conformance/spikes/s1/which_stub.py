"""Spike S1: which CompilationError line fires for each calc-stub candidate model."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness as h
from sysml_codegen.extraction.expression_compiler import CompilationError
for name in sys.argv[1:]:
    log = []
    orig = CompilationError.__init__
    def init(self, *a, **k):
        f = sys._getframe(1); log.append(f"{f.f_code.co_filename.rsplit('/',1)[-1]}:{f.f_lineno} {a[0][:80]}")
        orig(self, *a, **k)
    CompilationError.__init__ = init
    try:
        g = h.run_generator(h.local(name))
    finally:
        CompilationError.__init__ = orig
    print(name, g.ok, g.codes, g.stubs, g.first_error[:120], log)
