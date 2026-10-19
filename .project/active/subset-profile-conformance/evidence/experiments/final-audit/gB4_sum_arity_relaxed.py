import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
edit("sysml-codegen/src/sysml_codegen/elaboration/project.py", "if len(expression.arguments) != 1:", "if len(expression.arguments) > 1:")
