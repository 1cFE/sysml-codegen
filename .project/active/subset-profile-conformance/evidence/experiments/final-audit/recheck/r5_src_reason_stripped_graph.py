import sys; sys.path.insert(0,'/tmp/audit2a-recheck/perturb'); from edit import edit
edit("sysml-codegen/src/sysml_codegen/elaboration/graph.py", "                            reason=SiteReason.GRAPH_ROOT_OCCURRENCE_PACKAGE_MISSING,\n", "")
