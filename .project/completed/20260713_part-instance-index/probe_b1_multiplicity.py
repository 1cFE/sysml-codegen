"""Orchestrator probe for Item 4 design Bet B1/B2.

Question: does the live SysIDE multiplicity surface expose enough to positively
identify a single fixed literal count and to distinguish it from range, unbounded,
parameterized, and ordered/nonunique shapes — without new extracted facts?
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import syside

MODEL = """
package MultProbe {
    part def Leaf;
    part def Owner {
        attribute n : ScalarValues::Integer = 4;
        part fixed3 : Leaf[3];
        part unbounded_many : Leaf[*];
        part range05 : Leaf[0..5];
        part range33 : Leaf[3..3];
        part ordered3 : Leaf[3] ordered;
        part nonunique3 : Leaf[3] nonunique;
        part param_n : Leaf[n];
        part singleton : Leaf;
    }
}
"""


def describe(usage: syside.PartUsage) -> None:
    print(f"\n=== {usage.declared_name} ===")
    mult = usage.multiplicity
    print(f"  usage.multiplicity: {type(mult).__name__ if mult is not None else None}")
    # Usage-level ordering markers
    for attr in ("is_ordered", "is_nonunique", "is_unique", "ordered", "nonunique"):
        if hasattr(usage, attr):
            try:
                print(f"  usage.{attr} = {getattr(usage, attr)}")
            except Exception as e:  # noqa: BLE001
                print(f"  usage.{attr} -> raises {type(e).__name__}: {e}")
    if mult is None:
        return
    # Multiplicity-node surface
    interesting = [a for a in dir(mult) if not a.startswith("_")]
    print(f"  mult dir (non-private): {interesting}")
    for attr in (
        "cached_lower_bound",
        "cached_upper_bound",
        "lower_bound",
        "upper_bound",
        "bound",
        "range",
    ):
        if hasattr(mult, attr):
            try:
                val = getattr(mult, attr)
            except Exception as e:  # noqa: BLE001
                print(f"  mult.{attr} -> raises {type(e).__name__}: {e}")
                continue
            print(f"  mult.{attr} = {val!r} ({type(val).__name__})")
            for sub in ("referent", "value", "declared_name", "literal"):
                if val is not None and hasattr(val, sub):
                    try:
                        sv = getattr(val, sub)
                        print(f"      .{sub} = {sv!r} ({type(sv).__name__})")
                        if sub == "referent" and sv is not None:
                            print(
                                f"          referent type={type(sv).__name__}, "
                                f"name={getattr(sv, 'declared_name', None)}"
                            )
                    except Exception as e:  # noqa: BLE001
                        print(f"      .{sub} -> raises {type(e).__name__}: {e}")


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "mult_probe.sysml"
        p.write_text(MODEL)
        model, diagnostics = syside.try_load_model([str(p)])
        print(f"diagnostics: {diagnostics}")
        for usage in model.elements(syside.PartUsage, include_subtypes=True):
            owner_name = getattr(getattr(usage, "owner", None), "declared_name", None)
            if owner_name == "Owner":
                describe(usage)


if __name__ == "__main__":
    main()
