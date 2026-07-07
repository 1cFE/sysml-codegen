"""R4 verification probes for Item 4 (codegen side). License-gated (live).

Reproduces the CONFIRMED-BLIND sites for rows 1 and 2 against the real
wi014_toy fixture, which carries an `assert constraint` at toy_plant.sysml:51.
"""
import logging
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import SysideAdapter
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.constraint_extractor import extract_all_constraints

FIX = Path("tests/fixtures/wi014_toy")
paths = [FIX]

ext = SysMLDataExtractor(paths)
ok = ext.load_models()
print("loaded:", ok, "errors:", ext.diagnostics.contains_errors())

model = ext.model
ad = ext.adapter

# --- Metamodel facts ---
exact_cu = list(ad.elements_of_type(model, "ConstraintUsage"))
try:
    exact_acu = list(ad.elements_of_type(model, "AssertConstraintUsage"))
except Exception as e:
    exact_acu = f"ERR {e}"
print("exact ConstraintUsage count:", len(exact_cu))
print("exact AssertConstraintUsage count:",
      len(exact_acu) if isinstance(exact_acu, list) else exact_acu)

# is_instance is hierarchy-aware: an AssertConstraintUsage IS a ConstraintUsage
if isinstance(exact_acu, list) and exact_acu:
    a = exact_acu[0]
    print("assert.name:", getattr(a, "name", None))
    print("is_instance(assert, ConstraintUsage):",
          ad.is_instance(a, "ConstraintUsage"))
    print("is_instance(assert, RequirementUsage):",
          ad.is_instance(a, "RequirementUsage"))

# Does include_subtypes exist on the adapter today?
import inspect
sig = inspect.signature(SysideAdapter.elements_of_type)
print("elements_of_type signature:", sig)
print("is staticmethod:",
      isinstance(inspect.getattr_static(SysideAdapter, "elements_of_type"), staticmethod))

# --- PROBE 1 (row 1): report_dropped_constraints is SILENT on the assert ---
logger = logging.getLogger("sysml_codegen.extraction.extractor")
records = []
h = logging.Handler()
h.emit = lambda r: records.append((r.levelno, r.getMessage()))
logger.addHandler(h)
logger.setLevel(logging.INFO)
ext.report_dropped_constraints()
logger.removeHandler(h)
print("PROBE1 report emitted", len(records), "log records (expected >=1 if assert seen)")
for lv, m in records:
    print("   ", logging.getLevelName(lv), m[:70])

# --- PROBE 2 (row 2): extract_all_constraints blind to the assert ---
by_owner = extract_all_constraints(model)
total = sum(len(v) for v in by_owner.values())
print("PROBE2 extract_all_constraints total constraints:", total,
      "(expected 0 today; docstring claims assert support)")
