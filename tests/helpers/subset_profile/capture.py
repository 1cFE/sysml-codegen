"""Write stored generator answers from live runs, for a reviewer to read (Item 2a design D3).

    uv run --extra dev python -m tests.helpers.subset_profile.capture CASE_ID ... | --packaged

For each case it runs the generator half (``observe.generator_half``) and writes the run's
outcome, codes and site reasons into ``tests/expectations/subset_profile/cases/<id>.json``.
Everything else in an existing answer (witnesses, stubs, seams, loss, a codegen-home case's
construct and screen answer) is hand-written and kept as it is. A packaged case with no answer
yet gets a new one; a codegen-home case's answer must exist first, because its construct and
screen answer are written by hand.

It refuses to write a run that disagrees with the case's stored screen answer unless the
disagreement record already lists that exact disagreement: the record is edited by hand
first, so a capture can never make a disagreement pass on its own. It prints every change.
Running it is a manual step; no test calls it, and its output is reviewed as a diff.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.conformance_case import (
    ScreenAnswer,
    load_packaged_case,
    packaged_case_dir,
)

from tests.helpers.subset_profile import cases, observe
from tests.helpers.subset_profile.cases import CaseHome, GeneratorRun, StoredAnswer


class CaptureRefusedError(RuntimeError):
    """The live run disagrees with the case's screen answer and the record does not list it."""


def _run_json(run: GeneratorRun) -> dict[str, Any]:
    return {
        "outcome": run.outcome.value,
        "codes": list(run.codes),
        "reasons": [reason.value for reason in run.reasons],
    }


def _document(case_id: str) -> tuple[dict[str, Any], StoredAnswer | None]:
    path = cases.ANSWERS_DIR / f"{case_id}.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8")), cases.load_stored_answer(path)
    if case_id not in cases.packaged_ids():
        raise CaptureRefusedError(
            f"{case_id}: a codegen-home case's answer is written by hand before its first capture"
        )
    return {"id": case_id, "home": CaseHome.AGENTIC.value, "generator": {}}, None


def _model_and_screen(case_id: str, previous: StoredAnswer | None) -> tuple[Path, ScreenAnswer]:
    if previous is None:  # a new answer is only ever a packaged case's (``_document``)
        return packaged_case_dir(case_id), load_packaged_case(case_id).screen
    return cases.model_root(previous), cases.screen_of(previous)


def capture(case_id: str) -> str:
    """Capture one case's run; return a one-line description of the change."""
    document, previous = _document(case_id)
    root, screen = _model_and_screen(case_id, previous)
    run = observe.generator_half(root).run()
    found = cases.disagreement(f"case:{case_id}", run, screen)
    if found is not None and not cases.recorded(found, cases.read_disagreements()):
        raise CaptureRefusedError(
            f"{case_id}: the run disagrees with the stored screen answer ({found}), and the "
            "disagreement record does not list it. Record it by hand first, or fix the case."
        )
    before = None if previous is None else previous.generator.run
    if before == run:
        return f"{case_id}: unchanged"
    document["generator"] = {**document["generator"], **_run_json(run)}
    path = cases.ANSWERS_DIR / f"{case_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return f"{case_id}: {before} -> {run}"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("case_ids", nargs="*", default=[])
    target.add_argument("--packaged", action="store_true", help="every packaged case")
    args = parser.parse_args(argv)
    ids = sorted(cases.packaged_ids()) if args.packaged else args.case_ids
    for case_id in ids:
        print(capture(case_id))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
