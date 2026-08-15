"""Probe 4: node-ID stability — two independent loads produce identical graphs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from elab_prototype import elaborate  # noqa: E402

FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
PKG = "source_identity_mixed_consumers"

g1 = elaborate(FIXTURES / PKG)
g2 = elaborate(FIXTURES / PKG)

ids1 = sorted(g1.attrs) + sorted(g1.calcs)
ids2 = sorted(g2.attrs) + sorted(g2.calcs)
assert ids1 == ids2, "node ID sets differ across loads"

edges1 = sorted((cid, p, repr(r)) for cid, c in g1.calcs.items() for p, r in c.inputs.items())
edges2 = sorted((cid, p, repr(r)) for cid, c in g2.calcs.items() for p, r in c.inputs.items())
assert edges1 == edges2, "edges differ across loads"

values1 = sorted((n.node_id, repr(n.value), n.value_site) for n in g1.attrs.values())
values2 = sorted((n.node_id, repr(n.value), n.value_site) for n in g2.attrs.values())
assert values1 == values2, "values differ across loads"

print(f"PASS: {len(ids1)} node IDs, {len(edges1)} edges, identical across two loads")
