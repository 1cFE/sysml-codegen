"""usage: run_pkg.py <package dir> <name> <scratch root>"""
import sys, json, glob
from pathlib import Path
from tests.execution.real_teax import execute_sealed_package
pkg, name, root = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
root.mkdir(parents=True, exist_ok=True)
r = execute_sealed_package(pkg, name, root)
for f in sorted(glob.glob(str(root / "run" / "**" / "*.json"), recursive=True)):
    if "params" in f: continue
    print(Path(f).name, open(f).read().strip()[:200])
