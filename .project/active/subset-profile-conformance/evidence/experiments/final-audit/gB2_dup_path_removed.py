import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
edit("sysml-codegen/src/sysml_codegen/cli/__init__.py", "if prior is not None and prior != raw:\n            raise CodeGenerationError(\n                f\"DUPLICATE_OUTPUT_PATH", "if False:\n            raise CodeGenerationError(\n                f\"DUPLICATE_OUTPUT_PATH")
