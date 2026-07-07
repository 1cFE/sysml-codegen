"""D3-11 probe: _usage_by_name first-wins target index + unvalidated `.output`.

Intended behavior (doc 11-analysis-backtracker):
  find_required_modules(targets) resolves each "instance.output" target to the
  CalcUsage that PRODUCES it. A correct resolver must (a) disambiguate instance
  names that collide across scopes, and (b) validate that the named output
  actually exists on the resolved usage.

Observed defect claim (D3-11): `_usage_by_name` (dependency_backtracker ~155)
  is a first-wins index keyed by bare instance_name; collisions only log at DEBUG.
  Target resolution (~248) looks up by instance_name and NEVER validates the
  `.output` half. So (a) a colliding instance name resolves to whichever usage
  was indexed first, and (b) a bogus output name resolves silently to the usage.

Reproduction: the EXISTING sibling_channel_ambiguity fixture has two calc usages
  both named `power_calc` (chamber_a / chamber_b) — a real instance-name collision.
  This probe shows the first-wins index and drives a nonexistent output target.
"""
from __future__ import annotations

import logging
from pathlib import Path

logging.basicConfig(level=logging.ERROR)

FIX = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "sibling_channel_ambiguity"


def main() -> None:
    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

    ctx = build_pipeline_context([FIX])
    bt = ctx.backtracker

    # (a) first-wins collision
    pc_usages = [u for u in ctx.calc_usages if u.instance_name == "power_calc"]
    print(f"CalcUsages with instance_name 'power_calc': {len(pc_usages)}")
    for u in pc_usages:
        print(f"    qualified_name={u.qualified_name!r} calc_def={u.calc_def_name!r}")
    idx = bt._usage_by_name.get("power_calc")
    print(f"  _usage_by_name['power_calc'] first-wins -> {idx.qualified_name if idx else None!r}")
    print(f"  (# distinct in _usage_by_qualified with leaf power_calc: "
          f"{sum(1 for k in bt._usage_by_qualified if k.split('__')[-1] == 'power_calc')})")

    # (b) unvalidated .output half — bogus output should raise but does not.
    try:
        res = bt.find_required_modules(["power_calc.THIS_OUTPUT_DOES_NOT_EXIST"])
        n = len(res.required_usages)
        print(f"\nfind_required_modules(['power_calc.THIS_OUTPUT_DOES_NOT_EXIST']) "
              f"did NOT raise; traced {n} usage(s).")
        print("VERDICT: CONFIRMED — (a) instance-name collision resolves first-wins; "
              "(b) the `.output` half is never validated (bogus output silently "
              "resolves to the usage).")
    except Exception as e:  # noqa: BLE001
        print(f"\nfind_required_modules raised {type(e).__name__}: {e}")
        print("VERDICT (b): NOT-REPRODUCED — the output half was validated.")


if __name__ == "__main__":
    main()
