import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
# Record-only narrowing: the record says admitted where the generator refuses. Evaluator code unchanged.
edit("agentic-mbse/src/agentic_mbse/sysml/subset_profile_rules.toml", '[[rule.shape.admission]]\ncontext = "owner_package"\noutcome = "refused"\nevidence = [\n    "case:binding-source__expression_source__owner_package",', '[[rule.shape.admission]]\ncontext = "owner_package"\noutcome = "admitted"\nevidence = [\n    "case:binding-source__expression_source__owner_package",')
