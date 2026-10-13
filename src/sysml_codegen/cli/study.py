"""``sysml-codegen study <tool> [args]``: run one installed study tool with its own arguments.

The dispatcher constructs nothing. It hands the arguments after the tool name, unchanged, to
that tool's ``main``, so ``sysml-codegen study indicators …`` and
``python -m sysml_codegen.study.indicators …`` are the same run with the same exit code.
"""

from __future__ import annotations

import argparse

STUDY_TOOLS = ("indicators", "preflight", "verify", "integrate")


def cmd_study(args: argparse.Namespace) -> int:
    """Run the study tool ``args.tool`` on ``args.args`` and return its exit code."""
    # Imported here so the CLI starts without the study tools, and imported statically so
    # every reachability check over the CLI still sees them.
    from sysml_codegen.study import indicators, integrate, preflight, verify

    mains = {
        "indicators": indicators.main,
        "preflight": preflight.main,
        "verify": verify.main,
        "integrate": integrate.main,
    }
    return mains[args.tool](args.args)
