"""Spike S1: which executable_profile `_diagnostic` call fires for the blocked-predicate probe."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness as h
from agentic_mbse.sysml import executable_profile as ep
log, orig = [], ep._diagnostic
def spy(*a, **k):
    f = sys._getframe(1); log.append((f.f_lineno, f.f_code.co_qualname, a[0])); return orig(*a, **k)
ep._diagnostic = spy
g = h.run_generator(h.probe("constraint-predicate__blocked_predicate__owner_instantiated"))
s = h.run_screen(h.probe("constraint-predicate__blocked_predicate__owner_instantiated"))
ep._diagnostic = orig
print(g.key(), s.verdict, s.findings); print(sorted(set(log)))
