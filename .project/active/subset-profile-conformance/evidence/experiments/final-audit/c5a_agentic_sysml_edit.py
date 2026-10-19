import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
edit("agentic-mbse/src/agentic_mbse/sysml/subset_facts.py", 'class BindingKind(StrEnum):', '# audit: harmless-looking edit\nclass BindingKind(StrEnum):')
