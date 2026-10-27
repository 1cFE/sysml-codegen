"""Print the occurrence index paths for a models dir. usage: occ.py <models dir> [grep]"""
import sys, re, collections
from pathlib import Path
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.elaboration.occurrence import build_feature_slot_index, build_occurrence_index
paths = sorted(Path(sys.argv[1]).rglob("*.sysml"))
ex = SysMLDataExtractor(paths); assert ex.load_models()
slots = build_feature_slot_index(ex.model)
idx = build_occurrence_index(ex.model, slots)
pat = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
names = sorted(o.display_path for o in idx.occurrences())
print("total occurrences:", len(names))
for n in names:
    if pat is None or pat.search(n): print(n)
