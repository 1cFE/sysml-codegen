"""Witnesses and the stored effect of every mutation (Item 2a design D5, D7, § B).

A witness is a case that fires a site. Codegen sites are named in the stored generator answer
(``generator.witnesses``); agentic-mbse sites in the packaged case (``agentic_site_witnesses``).

``tests/expectations/subset_profile/mutations.json`` (``subset-mutations/2``) holds, by hand:

- ``generator``: for each mutated site, the cases whose generator answer changes when the site
  is neutralized. A site's own witnesses are among them; any others are recorded, not
  forbidden (design § Implementation Notes);
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
SCHEMA = "subset-mutations/2"
#: The renderer whose ``CompilationError`` raises are the stub family's sites (design D9).
STUB_RENDERER = "sysml_codegen/extraction/calc_compat_renderer.py"


class MutationRecordError(ValueError):
    """The stored mutation record is malformed."""


@dataclass(frozen=True)
class MutationRecord:
    generator: dict[str, frozenset[str]]
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
    if data.get("schema") != SCHEMA or set(data) != {"schema", "generator", "unwitnessed"}:
        raise MutationRecordError(f"{path}: expected schema, generator and unwitnessed")
    unwitnessed = data["unwitnessed"]
    if not all(isinstance(v, str) and v.strip() for v in unwitnessed.values()):
        raise MutationRecordError("unwitnessed: each site says why no case fires it")
    return MutationRecord(
        generator={k: _case_set(v, f"generator.{k}") for k, v in data["generator"].items()},
        unwitnessed=dict(unwitnessed),
    )


def shared_rule_sites() -> tuple[str, ...]:
    """The codegen account rows a shared rule links to."""
    return tuple(sorted(r.site_id for r in site_scan.load_account().rows if r.rules))


def stub_cause_sites() -> tuple[str, ...]:
    """The codegen account rows whose site raises a stub cause (``calc_compat_renderer.py``)."""
    return tuple(
        sorted(
            r.site_id
            for r in site_scan.load_account().rows
            if r.file == STUB_RENDERER and r.reason is not None
        )
    )


def r3_row_sites() -> tuple[str, ...]:
    """The codegen account rows with a reason that an R3 row names and no shared rule links to.

    These are the reproduced gaps (``evidence/r3-closure.md``): the generator refuses there,
    the contract has no rule for the shape, and the reason tells the refusing site apart.
    """
    return tuple(
        sorted(
            r.site_id
            for r in site_scan.load_account().rows
            if r.matrix_rows and not r.rules and r.reason is not None
        )
    )


def tail_sites() -> tuple[str, ...]:
    """The public codegen account rows with a reason that no rule or R3 row names (plan P6).

    The group E tail: valid models reach these sites, the contract is silent on the shape,
    and the reason tells the refusing site apart.
    """
    return tuple(
        sorted(
            r.site_id
            for r in site_scan.load_account().rows
            if r.role is site_scan.Role.PUBLIC_CAPABILITY
            and r.reason is not None
            and not r.rules
            and not r.matrix_rows
            and r.file != STUB_RENDERER
        )
    )


def mutated_sites() -> tuple[str, ...]:
    """Every site the generator mutation test neutralizes: codegen's, then the shared ones."""
    return (
        *shared_rule_sites(),
        *stub_cause_sites(),
        *r3_row_sites(),
        *tail_sites(),
        *sorted(mutate.SHARED),
    )


#: Roles that say no case reaches the site: no live model can (an internal invariant, a guard
#: the pinned SysIDE makes unreachable, a check only a hand-edited snapshot meets), or none
#: was found that does (``unknown``, whose E4 note lists the attempts). A case is a live model,
#: so a site any case fires may keep none of them.
UNREACHED_ROLES = frozenset(
    {
        site_scan.Role.INTERNAL_INVARIANT,
        site_scan.Role.ENVIRONMENT,
        site_scan.Role.SNAPSHOT_INTEGRITY,
        site_scan.Role.UNKNOWN,
    }
)


def recorded_unreached_sites() -> tuple[str, ...]:
    """The codegen account rows whose role says no case reaches them.

    A module-level site runs when its module is imported, before any case runs, so a case
    cannot reach it and it is left out.
    """
    return tuple(
        sorted(
            r.site_id
            for r in site_scan.load_account().rows
            if r.role in UNREACHED_ROLES and "::<module>::" not in r.site_id
        )
    )


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
    """Each case's generator half, run once with every mutated, witnessed or unreached site
    recorded.

    Licensed.
    """
    recorded = sorted(
        set(mutated_sites()) | set(codegen_witnesses()) | set(recorded_unreached_sites())
    )
    fired = {}
    for answer in cases.all_answers():
        with mutate.recording_sites(recorded) as seen:
            observe.generator_half(cases.model_root(answer)).run()
        fired[answer.case_id] = frozenset(seen)
    return fired


def answer_changed(answer: StoredAnswer) -> bool:
    """Whether a live generator run now ends differently from the stored answer.

    Judged by outcome, site reasons and stub causes, not codes (design D5): a shadowing site can
    produce the same code, and a stub site changes no outcome at all.
    """
    observation = observe.generator_half(cases.model_root(answer))
    run = observation.run()
    stored = answer.generator
    return (run.outcome, run.reasons, observation.stubs()) != (
        stored.run.outcome,
        stored.run.reasons,
        stored.stubs,
    )


def fired_in_generator(site_id: str) -> tuple[str, ...]:
    """The cases whose generator half fires ``site_id``. Licensed."""
    return tuple(sorted(c for c, fired in generator_firing().items() if site_id in fired))
