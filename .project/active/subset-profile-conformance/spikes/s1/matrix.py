"""Spike S1: elide each chosen site, run every case's two halves, report which outcomes flip."""
import sys, time
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness as h
import elide as e

MUTATIONS = [
    # (kind, site id, witness case)
    ("module function, imported by name into elaborate.py",
     "sysml_codegen/elaboration/occurrence.py::build_containment_address::coded::SI_OCCURRENCE_MISSING::1",
     "candidate-es-002__constraint_binds_calc_input__binding_value"),
    ("module function (private)",
     "sysml_codegen/elaboration/occurrence.py::_multiplicity_indices::coded::SI_MULTIPLICITY_UNSUPPORTED::3",
     "part-multiplicity__range__expanded_part_usage"),
    ("_ExactElaborator staticmethod",
     "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._require_one_writer::coded::SI_REDEFINITION_INVALID::1",
     "candidate-es-008__nested_named_subset__part_usage"),
    ("_ExactElaborator method",
     "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._resolve_semantic_reference::coded::SI_OCCURRENCE_MISSING::4",
     "candidate-es-009__composition_by_subsetting__part_usage"),
    ("nested function (build_occurrence_index.add_usage)",
     "sysml_codegen/elaboration/occurrence.py::build_occurrence_index.add_usage::coded-fixed::SI_CONTAINMENT_RECURSIVE::1",
     "recursive_containment"),
    ("agentic-mbse reference_use site",
     "agentic_mbse/sysml/reference_use.py::_require_supported_invocation::shared-evidence::EXPRESSION_KIND_UNSUPPORTED::1",
     "invocation-callable__unsupported_callable__attribute_value"),
    ("calc_compat_renderer stub site",
     "sysml_codegen/extraction/calc_compat_renderer.py::_render_operator::free-text::CompilationError::1",
     "calc_stub_gt"),
    ("calc_compat_renderer stub site (UnsupportedNode)",
     "sysml_codegen/extraction/calc_compat_renderer.py::_render::free-text::CompilationError::2",
     "calc_stub_operator"),
    ("non-raise site: coded-returned",
     "sysml_codegen/elaboration/elaborate.py::_ExactElaborator._collect_bound_members::coded-returned::SI_SELF_BINDING|SI_INDEXED_SOURCE_UNSUPPORTED|SI_EXPRESSION_SOURCE_UNSUPPORTED::1",
     "binding-source__expression_source__owner_instantiated"),
    ("non-raise site: codegen indexed refusal",
     "sysml_codegen/elaboration/expression_evidence.py::_indexed_refusal::coded::INDEXED_REFERENCE_UNSUPPORTED::1",
     "indexed-reference__indexed_reference__attribute_value"),
]

def observe():
    return {c.case_id: (h.run_generator(c), h.run_screen(c)) for c in h.CASES}

base = observe()
for kind, site, witness in MUTATIONS:
    print(f"\n### {kind}\n  site {site}")
    try:
        el = e.elide(site)
    except e.ElisionError as err:
        print(f"  ELISION REFUSED: {err}")
        continue
    print(f"  elided `{el.statement}` in {el.target.__module__}.{el.target.__qualname__}")
    t0 = time.perf_counter()
    try:
        obs = observe()
    finally:
        el.restore()
    dt = time.perf_counter() - t0
    for cid, (g, s) in obs.items():
        bg, bs = base[cid]
        gflip, sflip = g.key() != bg.key(), (s.verdict, s.findings) != (bs.verdict, bs.findings)
        if gflip or sflip or cid == witness:
            tag = "WITNESS" if cid == witness else "OTHER  "
            print(f"  {tag} {cid}: gen {'FLIP' if gflip else 'same'} {bg.key()} -> {g.key()}")
            if gflip: print(f"          now: {g.first_error[:170]}")
            if sflip: print(f"          screen FLIP {bs.verdict}{bs.findings} -> {s.verdict}{s.findings}")
    print(f"  all cases under mutation: {dt:.2f}s")

after = observe()
same = all(after[c][0].key() == base[c][0].key() and after[c][1].findings == base[c][1].findings for c in base)
print(f"\nrestore check: all all cases back to baseline = {same}")
