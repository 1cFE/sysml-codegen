"""Throwaway: which types can a SubsetFacts tree hold, and which did the 269 runs exercise?

Walks the resolved type hints from `SubsetFacts` (dataclasses and enums), then compares with the
type tags in `OUT_DIR/*.facts.json`. Usage: uv run --extra dev python type_coverage.py OUT_DIR
"""
import dataclasses, enum, glob, re, sys, typing, types
from agentic_mbse.sysml import constraint_extraction  # noqa: F401  (resolves the TYPE_CHECKING name)
from agentic_mbse.sysml.subset_facts import SubsetFacts
import agentic_mbse.sysml.subset_facts as sf
sf.IdentifiedConstraintFacts = constraint_extraction.IdentifiedConstraintFacts

seen, todo = set(), [SubsetFacts]
def push(t):
    for a in typing.get_args(t) or ():
        push(a)
    o = typing.get_origin(t)
    if o is None and isinstance(t, type) and (dataclasses.is_dataclass(t) or issubclass(t, enum.Enum)):
        if t not in seen:
            seen.add(t); todo.append(t)
while todo:
    t = todo.pop()
    if dataclasses.is_dataclass(t):
        mod = sys.modules[t.__module__]
        hints = typing.get_type_hints(t, vars(mod) | {"IdentifiedConstraintFacts": constraint_extraction.IdentifiedConstraintFacts})
        for h in hints.values():
            push(h)
seen.add(SubsetFacts)
static = {f"{t.__module__}:{t.__qualname__}" for t in seen}
observed = set()
for f in glob.glob(sys.argv[1] + "/*.facts.json"):
    observed |= set(re.findall(r'"\$[de]":"([^"]+)"', open(f).read()))
print("reachable types:", len(static), "observed:", len(static & observed))
print("never exercised:", sorted(static - observed))
print("observed but not reachable by hints:", sorted(observed - static))
