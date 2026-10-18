"""Spike S1: which CompilationError line fires for calc_stub_operator with _render::2 elided."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness as h, elide as e
from sysml_codegen.extraction.expression_compiler import CompilationError
log, orig = [], CompilationError.__init__
def init(self, *a, **k):
    f = sys._getframe(1); log.append(f"{f.f_code.co_filename.rsplit('/',1)[-1]}:{f.f_lineno} {a[0][:80]}"); orig(self, *a, **k)
CompilationError.__init__ = init
with e.elided("sysml_codegen/extraction/calc_compat_renderer.py::_render::free-text::CompilationError::2"):
    g = h.run_generator(h.local("calc_stub_operator"))
CompilationError.__init__ = orig
print(g.key(), log)
