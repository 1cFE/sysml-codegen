import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
# Widen consistently on the screen side: record says refused, stored screen answer says refused.
# Only the generator side (stored generator answer: generated) can catch this.
edit("agentic-mbse/src/agentic_mbse/sysml/subset_profile_rules.toml", '[[rule.shape.admission]]\ncontext = "owner_uninstantiated"\noutcome = "admitted"\nevidence = [\n    "case:binding-source__expression_source__owner_uninstantiated",', '[[rule.shape.admission]]\ncontext = "owner_uninstantiated"\noutcome = "refused"\nevidence = [\n    "case:binding-source__expression_source__owner_uninstantiated",')
p="agentic-mbse/src/agentic_mbse/sysml/subset_cases/binding-source__expression_source__owner_uninstantiated/case.json"
edit(p, '"verdict": "clear"', '"verdict": "refused"')
edit(p, '"outcome": "admitted"', '"outcome": "refused"')
