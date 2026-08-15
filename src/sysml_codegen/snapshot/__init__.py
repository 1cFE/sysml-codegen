"""The v6 instance-graph snapshot: capture a sealed graph, load it license-free.

Three modules, and nothing is re-exported here — every caller imports from the
one that owns what it needs:

- ``instance_graph`` — the canonical codec for a resolved exact-ID instance
  graph, and the digest over its bytes.
- ``envelope`` — the sealed envelope around those bytes, with the load-time
  version gate that refuses a v5 extraction snapshot by name.
- ``capture`` — ``capture_instance_graph_snapshot``, the only part of this
  package that needs a live syside license.

The v5 extraction snapshot this package used to carry is retired. Its version
constant, its constraint-lowering-mode vocabulary, its two error classes and its
certifiability gate went with the read path that gave them meaning; a v5
envelope is refused at load, typed, by ``envelope.py``.
"""
