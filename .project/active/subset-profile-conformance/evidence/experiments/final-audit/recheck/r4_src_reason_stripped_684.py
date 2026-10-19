import sys; sys.path.insert(0,'/tmp/audit2a-recheck/perturb'); from edit import edit
edit("sysml-codegen/src/sysml_codegen/elaboration/elaborate.py", "                        reason=SiteReason.ELABORATION_CONSTRAINT_DEFINITION_UNINDEXED,\n", "")
