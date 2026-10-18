"""Witnesses and the stored effect of every mutation (Item 2a design D5, D7, § B).

A witness is a case that fires a site. Codegen sites are named in the stored generator answer
(``generator.witnesses``); agentic-mbse sites in the packaged case (``agentic_site_witnesses``).

``tests/expectations/subset_profile/mutations.json`` (``subset-mutations/1``) holds, by hand:

- ``generator``: for each mutated site, the cases whose generator answer changes when the site
  is neutralized. A site's own witnesses are among them; any others are recorded, not
  forbidden (design § Implementation Notes);
- ``screen``: for each (rule, shape) with a refused context, the cases whose generator answer
  the screen stops agreeing with when the shape's recognizer is disabled;
- ``unwitnessed``: the mutated sites no case fires in the generator half, each with why.
"""

from __future__ import annotations

import functools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.conformance_case import load_packaged_case

from tests.helpers.subset_profile import cases, mutate, observe, site_scan
from tests.helpers.subset_profile.cases import StoredAnswer

MUTATIONS_PATH = cases.EXPECTATIONS_DIR / "mutations.json"
SCHEMA = "subset-mutations/1"


class MutationRecordError(ValueError):
    """The stored mutation record is malformed."""


@dataclass(frozen=True)
class MutationRecord:
    generator: dict[str, frozenset[str]]
    screen: dict[tuple[str, str], frozenset[str]]
    unwitnessed: dict[str, str]


def _case_set(value: Any, where: str) -> frozenset[str]:
    if not isinstance(value, list) or value != sorted(set(value)) or not value:
        raise MutationRecordError(f"{where}: expected a sorted, non-empty list of case IDs")
    unknown = set(value) - cases.answer_ids()
    if unknown:
        raise MutationRecordError(f"{where}: no stored answer for {sorted(unknown)}")
    return frozenset(value)


def read_mutations(path: Path = MUTATIONS_PATH) -> MutationRecord:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA or set(data) != {
        "schema",
        "generator",
        "screen",
        "unwitnessed",
    }:
        raise MutationRecordError(f"{path}: expected schema, generator, screen and unwitnessed")
    screen = {}
    for key, value in data["screen"].items():
        rule, sep, shape = key.partition("/")
        if not sep:
            raise MutationRecordError(f"screen.{key}: expected <rule>/<shape>")
        screen[(rule, shape)] = _case_set(value, f"screen.{key}")
    unwitnessed = data["unwitnessed"]
    if not all(isinstance(v, str) and v.strip() for v in unwitnessed.values()):
        raise MutationRecordError("unwitnessed: each site says why no case fires it")
    return MutationRecord(
        generator={k: _case_set(v, f"generator.{k}") for k, v in data["generator"].items()},
        screen=screen,
        unwitnessed=dict(unwitnessed),
    )


def shared_rule_sites() -> tuple[str, ...]:
    """The codegen account rows a shared rule links to."""
    return tuple(sorted(r.site_id for r in site_scan.load_account().rows if r.rules))


def mutated_sites() -> tuple[str, ...]:
    """Every site the generator mutation test neutralizes: codegen's, then the shared ones."""
    return (*shared_rule_sites(), *sorted(mutate.SHARED))


def codegen_witnesses() -> dict[str, frozenset[str]]:
    found: dict[str, set[str]] = {}
    for answer in cases.all_answers():
        for site_id in answer.generator.witnesses:
            found.setdefault(site_id, set()).add(answer.case_id)
    return {k: frozenset(v) for k, v in found.items()}


def agentic_witnesses() -> dict[str, frozenset[str]]:
    found: dict[str, set[str]] = {}
    for case_id in cases.packaged_ids():
        for site_id in load_packaged_case(case_id).agentic_site_witnesses:
            found.setdefault(site_id, set()).add(case_id)
    return {k: frozenset(v) for k, v in found.items()}


def witnesses_of(site_id: str) -> frozenset[str]:
    """The cases that name ``site_id`` as a witness, in whichever store its repo reads."""
    store = agentic_witnesses() if site_id.startswith("agentic_mbse/") else codegen_witnesses()
    return store.get(site_id, frozenset())


@functools.cache
def generator_firing() -> dict[str, frozenset[str]]:
    """Each case's generator half, run once with every mutated or witnessed site recorded.

    Licensed.
    """
    recorded = sorted(set(mutated_sites()) | set(codegen_witnesses()))
    fired = {}
    for answer in cases.all_answers():
        with mutate.recording_sites(recorded) as seen:
            observe.generator_half(cases.model_root(answer)).run()
        fired[answer.case_id] = frozenset(seen)
    return fired


def answer_changed(answer: StoredAnswer) -> bool:
    """Whether a live generator run now ends differently from the stored answer.

    Judged by outcome and site reasons, not codes (design D5): a shadowing site can produce the
    same code. Stub causes join the judgment once the harness observes them (P4).
    """
    run = observe.generator_half(cases.model_root(answer)).run()
    stored = answer.generator.run
    return (run.outcome, run.reasons) != (stored.outcome, stored.reasons)


def fired_in_generator(site_id: str) -> tuple[str, ...]:
    """The cases whose generator half fires ``site_id``. Licensed."""
    return tuple(sorted(c for c, fired in generator_firing().items() if site_id in fired))
