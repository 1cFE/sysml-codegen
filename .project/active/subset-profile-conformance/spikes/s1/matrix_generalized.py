"""Spike S1: the generalized elision (finding-recording statements too) on three non-raise sites."""
import sys, time
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness as h
import elide as e
h.CASES.append(h.probe("constraint-predicate__blocked_predicate__owner_instantiated"))
MUTATIONS = [
    ("codegen readiness recorder (coded-returned)",
     "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._collect_bound_members::coded-returned::SI_SELF_BINDING|SI_INDEXED_SOURCE_UNSUPPORTED|SI_EXPRESSION_SOURCE_UNSUPPORTED::1",
     "binding-source__expression_source__owner_instantiated"),
    ("codegen diagnostic recorder",
     "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._build_constraint_nodes::coded::SI_CONSTRAINT_BLOCKED::1",
     "constraint-predicate__blocked_predicate__owner_instantiated"),
    ("agentic-mbse executable_profile append",
     "agentic_mbse/sysml/executable_profile.py::_walk_proposition::shared-profile::warn_non_numerical_predicate::1",
     "constraint-predicate__blocked_predicate__owner_instantiated"),
    ("factory return (expected: refused)",
     "sysml_codegen/elaboration/expression_evidence.py::_indexed_refusal::coded::INDEXED_REFERENCE_UNSUPPORTED::1",
     "indexed-reference__indexed_reference__attribute_value"),
]
def observe():
    return {c.case_id: (h.run_generator(c), h.run_screen(c)) for c in h.CASES}
base = observe()
for kind, site, witness in MUTATIONS:
    print(f"\n### {kind}\n  site {site}")
    try:
        el = e.elide(site, generalized=True)
    except e.ElisionError as err:
        print(f"  ELISION REFUSED: {err}"); continue
    print(f"  elided `{el.statement[:110]}`")
    t0 = time.perf_counter()
    try: obs = observe()
    finally: el.restore()
    for cid, (g, s) in obs.items():
        bg, bs = base[cid]
        gflip, sflip = g.key() != bg.key(), (s.verdict, s.findings) != (bs.verdict, bs.findings)
        if gflip or sflip or cid == witness:
            print(f"  {'WITNESS' if cid == witness else 'OTHER  '} {cid}: gen {'FLIP' if gflip else 'same'} {bg.key()} -> {g.key()}")
            if gflip and g.first_error: print(f"          now: {g.first_error[:170]}")
            if sflip: print(f"          screen FLIP {bs.verdict}{bs.findings} -> {s.verdict}{s.findings}")
    print(f"  {len(obs)} cases under mutation: {time.perf_counter()-t0:.2f}s")
after = observe()
print("\nrestore check:", all(after[c][0].key() == base[c][0].key() and after[c][1].findings == base[c][1].findings for c in base))
