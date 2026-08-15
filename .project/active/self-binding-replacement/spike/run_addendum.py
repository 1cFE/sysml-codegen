"""SPIKE THROWAWAY — addendum driver: run the shipped CLI over the usage-qualified fixtures.

Run from the repo root with the license loaded:
    set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
    uv run python .project/active/self-binding-replacement/spike/run_addendum.py [fixture ...]
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SPIKE = Path(".project/active/self-binding-replacement/spike")
FIXTURES = SPIKE / "fixtures"
OUT = SPIKE / "out"

def _load_license() -> str:
    """Read SYSIDE_LICENSE_KEY from the env, else from the companion checkout's .env."""
    key = os.environ.get("SYSIDE_LICENSE_KEY")
    if key:
        return key
    env = Path("/home/reid/1cfe/agentic-mbse/.env")
    for line in env.read_text().splitlines():
        name, _, value = line.strip().partition("=")
        if name == "SYSIDE_LICENSE_KEY":
            os.environ["SYSIDE_LICENSE_KEY"] = value.strip().strip("'\"")
            return os.environ["SYSIDE_LICENSE_KEY"]
    return ""


key = _load_license()
if not key:
    sys.exit("FATAL: SYSIDE_LICENSE_KEY not set")
print(f"license key loaded (len {len(key)})")

names = sys.argv[1:] or sorted(p.name for p in FIXTURES.iterdir() if p.name.startswith("u"))

for name in names:
    out = OUT / name
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    log = OUT / f"{name}.log"
    proc = subprocess.run(
        [
            "sysml-codegen", "generate",
            "--models", str(FIXTURES / name),
            "--output", str(out),
            "--package-name", "spike_pkg",
            "--overwrite",
        ],
        capture_output=True,
        text=True,
    )
    log.write_text(proc.stdout + proc.stderr)
    print(f"=========== {name}  exit={proc.returncode}")
    for line in (proc.stdout + proc.stderr).splitlines():
        if "ERROR" in line or "Built computation" in line or "error (" in line:
            print("   ", line.strip()[:200])
    for jf in sorted((out / "inputs").glob("*.json")):
        print("    inputs:", json.dumps(json.loads(jf.read_text())))
    contract = out / "contracts" / "model_contract.json"
    if contract.exists():
        data = json.loads(contract.read_text())
        for p in data["parameters"]:
            print(f"    param: {p['qualified_name']} = {p['default_value']} ({p['entry_type']})")
        for o in data["outputs"]:
            print(f"    output: {o['channel_name']}")
    yaml = out / "pipelines" / "pipeline.yaml"
    if yaml.exists():
        for line in yaml.read_text().splitlines():
            s = line.strip()
            if s.startswith(("in ", "length", "width", "length_in", "unit_cost", "availability")):
                print("    wiring:", s)
