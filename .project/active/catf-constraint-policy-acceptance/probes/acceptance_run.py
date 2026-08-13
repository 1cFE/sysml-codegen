"""Item 5 Phase 6. Drive the derivative through the real TEAx lane, twice.

One generated package, two candidates, two runs — the authored `p_fusion = 2600.0` and a
mutation that drops it until `p_electric_net_out` goes negative.

**The mutation is injected at runtime, not written into `inputs/*.json`.** D6 said the
mutation "lives in the generated inputs/*.json". That route is refused by the product: the
package contract covers the on-disk bytes, so editing a sealed input breaks the seal, and
`test_editing_a_sealed_input_and_resealing_is_refused` pins that refusal in code. The
supported route, and the one Item 3's mutation lane already uses, is TEAx's typed entry
injection — `CandidateBridge.build(selected_fields)` fills every entry channel from the
package's own modelled defaults, and `PreparedEvaluator.evaluate` runs the real executor
against that mapping. D6's actual intent is preserved exactly: one package, two input sets,
the mutation a physics input value rather than a model edit or a study-config override. The
seal stays an active check throughout, because the same loader verifies the package the
evaluator runs.

Run with the licensed env sourced; simkit comes from /home/reid/1cfe/teax on
constraint-semantics-item3.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path("/home/reid/1cfe/sysml-codegen-item7-rebuild")
sys.path.insert(0, str(REPO))

from tests.execution.real_teax import package_loader  # noqa: E402

PACKAGE = Path("/tmp/item5acc/route2_inplace")
NAME = "catf_gated"
P_FUSION = "CATFMFEPhysics__catf_physics__p_fusion"

#: A2 and A3's evaluation channels, measured at Phase 1 and unchanged since.
A2 = "CATFMFEPhysics__catf_physics__net_power_viable__d8cad14493e47fbd__evaluation"
A3 = "CATFMFEPhysics__catf_physics__parasitic_fraction_ok__280b94b2e8d184f5__evaluation"
NET_OUT = "CATFMFEPhysics__catf_physics__p_electric_net_out"


def prepare(root: Path):
    from simkit.evaluation.evaluator import PreparedEvaluator
    from simkit.study.bridge import CandidateBridge

    loader = package_loader(PACKAGE, NAME, root / "link")
    evaluator = PreparedEvaluator(
        loader, PACKAGE / "pipelines" / "pipeline.yaml", expects_constraint_report=True
    )
    return evaluator, CandidateBridge(evaluator.entry_models)


def report(label: str, evidence) -> dict:
    net = {
        name: value
        for name, value in evidence.outputs.items()
        if "p_electric_net" in name or "p_net" in name
    }
    print(f"\n=== {label}")
    print(f"  headline:  {evidence.responses.get('headline')}")
    for channel, tag in ((A2, "A2 net_power_viable"), (A3, "A3 parasitic_fraction_ok")):
        print(f"  {tag}: {evidence.responses.get(channel, '<absent>')}")
    for name, value in sorted(net.items()):
        print(f"  {name} = {value}")
    coverage = {
        key: value
        for key, value in evidence.responses.items()
        if "coverage" in key or "total" in key or "count" in key or "assessed" in key
    }
    print(f"  coverage fields: {json.dumps(coverage, sort_keys=True, default=str)}")
    return {"headline": evidence.responses.get("headline"), "net": net, "coverage": coverage}


def main() -> None:
    root = Path("/tmp/item5acc/teax")
    root.mkdir(parents=True, exist_ok=True)
    evaluator, bridge = prepare(root)

    print("entry channels carrying p_fusion:")
    for name in evaluator.entry_models:
        if "p_fusion" in name or "fusion_power" in name:
            print(f"  {name}")

    valid = evaluator.evaluate(bridge.build({}))
    report("VALID CANDIDATE (authored p_fusion = 2600.0)", valid)

    for candidate in (1500.0, 800.0, 400.0, 200.0, 100.0):
        evidence = evaluator.evaluate(bridge.build({P_FUSION: candidate}))
        net = [v for k, v in evidence.outputs.items() if "p_electric_net" in k]
        print(
            f"  probe p_fusion={candidate:>7}: net={net} "
            f"headline={evidence.responses.get('headline')}"
        )
        if net and net[0] < 0:
            report(f"MUTATED CANDIDATE (p_fusion = {candidate})", evidence)
            break
    else:
        print("\nB3 FALSE: no probed p_fusion drove p_electric_net_out negative")


if __name__ == "__main__":
    main()
