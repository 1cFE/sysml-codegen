"""A1 reproduction: does removing a non-reaching catalog row fail generation?

Run with the licence sourced:
    /home/reid/1cfe/item7-rebuild-venv/bin/python \
        .project/active/constraint-catalog-totality/probes/a1_repro.py
"""

import tempfile
from pathlib import Path

from sysml_codegen.cli import GenerationConfig, _generate_package_from_graph
from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline

for name in ("constraint_domain_detached_owner", "catf_mfe_d5"):
    for want_reaching in (False, True):
        graph = build_elaborated_pipeline([Path("tests/fixtures") / name])
        rows = graph.constraint_catalog.usage_records
        victim = next(r for r in rows if (r.occurrence_count > 0) == want_reaching)
        rows.remove(victim)
        with tempfile.TemporaryDirectory() as td:
            ok = _generate_package_from_graph(
                graph,
                GenerationConfig(
                    output_path=Path(td) / "gen",
                    models_path=Path("tests/fixtures") / name,
                    package_name="probe",
                    overwrite=True,
                ),
            )
        print(f"{name:34s} removed occ={victim.occurrence_count} -> generation={ok}")
