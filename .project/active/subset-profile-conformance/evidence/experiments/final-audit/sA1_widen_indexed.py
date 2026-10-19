import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
edit("agentic-mbse/src/agentic_mbse/sysml/subset_profile.py", '        BindingKind.SELF_BINDING: "self_reference_source",\n    }', '        BindingKind.SELF_BINDING: "self_reference_source",\n        BindingKind.INDEXED: "expression_source",\n    }')
