import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
edit("sysml-codegen/src/sysml_codegen/elaboration/occurrence.py", 'for kind in ("PartUsage", "PartDefinition", "Package")', 'for kind in ("PartUsage", "PartDefinition", "Package", "ItemUsage", "AttributeUsage", "CalculationUsage")')
