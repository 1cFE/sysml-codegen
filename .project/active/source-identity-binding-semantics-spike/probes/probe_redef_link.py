#!/usr/bin/env python3
"""Micro-probe (SOURCE-IDENTITY Item 1): does SysIDE expose the redefinition link
on a shorthand ``:>> R = 12.7`` feature, and under what attribute name?

Loads form_chain.sysml, finds ``Design Ctx::plant::R`` (the redefining
ReferenceUsage), dumps its dir() surface filtered to plausible relationship
accessors, and tries each, printing what it yields. Raw evidence for the
occurrence-evidence-sufficiency question handed to Item 2.

Usage:
    set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
    uv run python .project/active/source-identity-binding-semantics-spike/probes/probe_redef_link.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

SPIKE_DIR = Path(__file__).resolve().parent
MODEL = SPIKE_DIR / "models" / "form_chain.sysml"


def main() -> int:
    model, diagnostics = SysideAdapter.load_model([MODEL])
    assert not diagnostics.contains_errors(), list(diagnostics.errors)

    target = None
    for ru in SysideAdapter.elements_of_type(model, "ReferenceUsage"):
        owner = getattr(ru, "owner", None)
        if (
            getattr(ru, "name", None) == "R"
            and owner is not None
            and getattr(owner, "name", None) == "plant"
        ):
            target = ru
            break
    assert target is not None, "redefining :>> R not found"

    print(f"Element: {type(target).__name__} name={target.name!r}")
    surface = [a for a in dir(target) if not a.startswith("_")]
    keywords = ("redef", "subset", "special", "relation", "inherit", "feature")
    candidates = [a for a in surface if any(k in a.lower() for k in keywords)]
    print(f"\nFull public surface ({len(surface)} attrs):\n{surface}")
    print(f"\nCandidate relationship accessors: {candidates}")

    for attr in candidates:
        try:
            val: Any = getattr(target, attr)
        except Exception as exc:  # noqa: BLE001
            print(f"\n{attr}: <raised {exc}>")
            continue
        if callable(val):
            print(f"\n{attr}: <method>")
            continue
        print(f"\n{attr}: type={type(val).__name__}")
        try:
            items = list(val) if not isinstance(val, str) else [val]
        except TypeError:
            items = [val]
        for it in items[:5]:
            qn = getattr(it, "qualified_name", None)
            print(
                f"  -> {type(it).__name__} name={getattr(it, 'name', None)!r} qn={qn!r}"
            )
            # One level deeper for relationship nodes.
            for sub in ("redefined_feature", "redefining_feature", "general", "specific"):
                subval = getattr(it, sub, None)
                if subval is not None:
                    print(
                        f"     .{sub} = {type(subval).__name__} "
                        f"qn={getattr(subval, 'qualified_name', None)!r}"
                    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
