# Minimal reproducer — `SI_OCCURRENCE_MISSING` on a unit-annotated attribute

Gate 4C part 6, ruling 2 investigation. **Evidence, not a fixture**: it is deliberately not
under `tests/fixtures/`, because a fixture that asserts known-broken behaviour needs its own
disposition, and that is the orchestrator's call.

Two models, identical but for one thing: `unit_annotated.sysml` writes
`attribute thickness : Real = 0.5 [m];` and `unit_removed.sysml` writes
`attribute thickness : Real = 0.5;`.

```bash
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
python - <<'PY'
from pathlib import Path
from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
for name in ("unit_annotated", "unit_removed"):
    for route, fn in (("exact", build_elaborated_pipeline), ("legacy", build_pipeline_context)):
        try:
            fn([Path(f".project/active/cutover-recovery/evidence/catf-occurrence-probe/{name}")])
            print(name, route, "ACCEPTED")
        except Exception as error:
            print(name, route, "REFUSED", type(error).__name__)
PY
```

Measured:

| model | exact route | legacy route |
|---|---|---|
| `unit_annotated.sysml` | **REFUSED** `SI_OCCURRENCE_MISSING … leaf declaration 146016c8-… has no feature slot` | ACCEPTED |
| `unit_removed.sysml` | ACCEPTED | ACCEPTED |

`146016c8-c0f8-5b9b-882d-33c75906e6ee` is `SI::metre`. It is the same declaration id that
produces 113 of `catf_mfe_d5`'s 152 diagnostics.

Each `.sysml` here must be placed in its own directory to run; they are kept flat so the two
can be diffed with one command.
