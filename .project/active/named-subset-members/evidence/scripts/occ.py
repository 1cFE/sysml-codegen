"""Print occurrence display paths for a models dir."""
import sys, re
from pathlib import Path
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.elaboration.occurrence import build_feature_slot_index, build_occurrence_index
paths = sorted(Path(sys.argv[1]).rglob("*.sysml"))
ex = SysMLDataExtractor(paths); assert ex.load_models()
slots = build_feature_slot_index(ex.model)
try:
    idx = build_occurrence_index(ex.model, slots)
except Exception as e:
    print("REFUSED", type(e).__name__, getattr(e, "code", None), getattr(e, "reason", None), getattr(e, "detail", e)); sys.exit()
pat = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
names = sorted(o.display_path for o in idx.occurrences())
print("total:", len(names))
for n in names:
    if pat is None or pat.search(n): print(" ", n)
