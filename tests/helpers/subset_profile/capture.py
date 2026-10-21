"""Write stored generator answers from live runs, for a reviewer to read (Item 2a design D3).

    uv run --extra dev python -m tests.helpers.subset_profile.capture CASE_ID ... | --all

For each case it runs the generator half (``observe.generator_half``) and writes the run's
outcome, codes and site reasons into ``tests/expectations/subset_profile/cases/<id>.json``.
Everything else in the answer (construct, witnesses, stubs, seams, loss) is hand-written and
kept as it is, so a case's answer must exist before its first capture.

It prints every change. Running it is a manual step; no test calls it, and its output is
reviewed as a diff.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from tests.helpers.subset_profile import cases, observe
from tests.helpers.subset_profile.cases import GeneratorRun


def _run_json(run: GeneratorRun) -> dict[str, Any]:
    return {
        "outcome": run.outcome.value,
        "codes": list(run.codes),
        "reasons": [reason.value for reason in run.reasons],
    }


def capture(case_id: str) -> str:
    """Capture one case's run; return a one-line description of the change."""
    path = cases.ANSWERS_DIR / f"{case_id}.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    previous = cases.load_stored_answer(path)
    run = observe.generator_half(cases.model_root(previous)).run()
    before = previous.generator.run
    if before == run:
        return f"{case_id}: unchanged"
    document["generator"] = {**document["generator"], **_run_json(run)}
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return f"{case_id}: {before} -> {run}"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("case_ids", nargs="*", default=[])
    target.add_argument("--all", action="store_true", help="every case")
    args = parser.parse_args(argv)
    ids = sorted(cases.answer_ids()) if args.all else args.case_ids
    for case_id in ids:
        print(capture(case_id))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
