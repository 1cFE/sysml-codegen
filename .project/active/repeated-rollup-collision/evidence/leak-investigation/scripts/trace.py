import sys
from sysml_codegen.elaboration import elaborate as E
from sysml_codegen.elaboration.occurrence import semantic_owner
orig_create = E._ExactElaborator._create_value_node
def create(self, scope, slot, base, writer):
    if str(getattr(base, "name", "")) in ("capital_cost", "x"):
        expr = getattr(writer, "feature_value_expression", None)
        try:
            from sysml_codegen.extraction.literal import extract_literal_value  # may not exist
        except Exception:
            pass
        lit = None
        try:
            lit = E.extract_literal_value(expr) if expr is not None else None
        except Exception:
            lit = "<expr>"
        owner = semantic_owner(writer)
        print(f"TRACE {self._display_path(scope, base.name)} <- writer owned by {getattr(owner,'qualified_name',None)} value={lit if lit is not None else ('<expr>' if expr is not None else None)}", file=sys.stderr)
    return orig_create(self, scope, slot, base, writer)
E._ExactElaborator._create_value_node = create
orig_deep = E._ExactElaborator._apply_deep_literal_redefinitions
def deep(self):
    r = orig_deep(self)
    for n in self._graph.attrs.values():
        if n.value_site == E.ValueSite.OCCURRENCE_OVERRIDE:
            print(f"TRACE-DEEP {n.display_path} = {n.value}", file=sys.stderr)
    return r
E._ExactElaborator._apply_deep_literal_redefinitions = deep
from sysml_codegen.cli import main
sys.argv = ["sysml-codegen"] + sys.argv[1:]
main()
