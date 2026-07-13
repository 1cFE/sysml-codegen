"""Orchestrator probe for Item 5 design bet B1 (per the design review's recipe).

Question: for a [3]-multiplicity part whose instances each own a calc, does the
OutputRegistry hold three distinct owner-scoped producer channels — or one?
And if one: does an occurrence-indexed lookup collapse onto it or miss loudly?
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

MODEL = """
package MultiChan {
    private import ScalarValues::*;

    calc def 'Power Calc' {
        in attribute r : Real;
        out attribute p : Real = r * 2.0;
    }

    part def Cell {
        attribute cell_rating : Real = 10.0;
        calc power_calc : 'Power Calc' {
            in r = cell_rating;
        }
    }
    part def Container {
        part cell : Cell[3];
    }
    part def Design {
        part c : Container;
    }
    part the_design : Design;
}
"""


def main() -> None:
    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "multi_chan.sysml"
        p.write_text(MODEL)
        ctx = build_pipeline_context(model_paths=[p])
        reg = ctx.output_registry

        # 1. canonical channels for the producer
        chans = [c for c in reg.canonical_channels if "power_calc" in c]
        print(f"canonical power_calc channels ({len(chans)}):")
        for c in sorted(chans):
            print(f"  {c}")

        # 2. scoped keys for the same producer
        scoped = getattr(reg, "_scoped", {})
        skeys = [k for k in scoped if "power_calc" in str(k) or "cell" in str(k)]
        print(f"scoped keys mentioning cell/power_calc ({len(skeys)}):")
        for k in sorted(str(k) for k in skeys):
            print(f"  {k}")

        # 3. instance index occurrences
        import syside
        from sysml_codegen.analysis.part_instance_index import build_part_instance_index
        model, _diag = syside.try_load_model([str(p)])
        idx = build_part_instance_index(model)
        occ = idx.occurrences_of("MultiChan__Cell")
        print(f"index occurrences of Cell ({len(occ)}):")
        for o in occ:
            print(f"  {o.instance_path}")

        # 4. collapse-vs-miss: try occurrence-indexed and de-indexed scoped lookups
        for key_form in (
            "c__cell[0]__power_calc__p",
            "c__cell__power_calc__p",
            "MultiChan__Design__c__cell[0]__power_calc__p",
            "MultiChan__Design__c__cell__power_calc__p",
        ):
            try:
                hit = reg.scoped_lookup(key_form) if hasattr(reg, "scoped_lookup") else None
                print(f"scoped_lookup({key_form!r}) -> {hit}")
            except Exception as e:  # noqa: BLE001
                print(f"scoped_lookup({key_form!r}) raises {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
