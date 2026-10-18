"""The stored answers of a subset-profile case, read strictly (design Appendix A).

Two documents describe a case:

- the stored generator answer, ``tests/expectations/subset_profile/cases/<case_id>.json``,
  which every case has wherever its model lives;
- the packaged ``case.json`` beside a screen-tested model in agentic-mbse's
  ``sysml/subset_cases/<case_id>/``.

Loading refuses an unknown key, a missing key, a value of the wrong form, and a stored
answer whose ``id`` is not its file name. Comparing answers with observations is not here.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from sysml_codegen.elaboration.diagnostics import SiteReason

PACKAGED_CASE_SCHEMA = "subset-case/1"
_RG1_ID = re.compile(r"RG1-[1-9][0-9]*")


class CaseAnswerError(ValueError):
    """A stored answer or packaged case does not have the Appendix A form."""


class CaseHome(StrEnum):
    #: The model and screen answer are agentic-mbse package data.
    AGENTIC = "agentic"
    #: The model and screen answer live in this repository.
    CODEGEN = "codegen"


class GeneratorOutcome(StrEnum):
    GENERATED = "generated"
    REFUSED = "refused"


class SeamKind(StrEnum):
    GRAPH_ATTR = "graph_attr"
    ENTRY_POINT = "entry_point"
    CATALOG_USAGE = "catalog_usage"
    CALC_COMPILABILITY = "calc_compilability"
    OCCURRENCES = "occurrences"


class LossDisposition(StrEnum):
    ACCEPTED_OMISSION = "accepted_omission"
    CANDIDATE_REFUSAL = "candidate_refusal"


@dataclass(frozen=True)
class StubAnswer:
    output: str
    reason: SiteReason


@dataclass(frozen=True)
class SeamAnswer:
    kind: SeamKind
    declaration: str
    expect: Any


@dataclass(frozen=True)
class GeneratorAnswer:
    outcome: GeneratorOutcome
    #: The sorted multiset of elaboration and generation codes.
    codes: tuple[str, ...]
    reasons: tuple[SiteReason, ...]
    witnesses: tuple[str, ...]
    stubs: tuple[StubAnswer, ...]
    seams: tuple[SeamAnswer, ...]


@dataclass(frozen=True)
class ScreenFinding:
    rule: str
    shape: str
    context: str
    outcome: str
    subject: str


@dataclass(frozen=True)
class ScreenAnswer:
    verdict: str
    #: The complete set the screen reports, so an unrelated rule change also shows as drift.
    findings: tuple[ScreenFinding, ...]


@dataclass(frozen=True)
class LossAnswer:
    family: str
    disposition: LossDisposition
    rg1: str | None


@dataclass(frozen=True)
class StoredAnswer:
    case_id: str
    home: CaseHome
    generator: GeneratorAnswer
    #: Present exactly for codegen-home cases; an agentic-home case's screen answer is packaged.
    screen: ScreenAnswer | None
    loss: LossAnswer | None


@dataclass(frozen=True)
class Construct:
    file: str
    lines: tuple[int, int]


@dataclass(frozen=True)
class Provenance:
    from_probe: str | None
    note: str


@dataclass(frozen=True)
class PackagedCase:
    case_id: str
    construct: Construct
    screen: ScreenAnswer
    agentic_site_witnesses: tuple[str, ...]
    provenance: Provenance


def _fields(
    value: Any,
    where: str,
    *,
    required: frozenset[str],
    optional: frozenset[str] = frozenset(),
) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise CaseAnswerError(f"{where}: expected an object, got {type(value).__name__}")
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing or unknown:
        raise CaseAnswerError(f"{where}: missing {sorted(missing)}, unknown {sorted(unknown)}")
    return value


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise CaseAnswerError(f"{where}: expected a non-empty string, got {value!r}")
    return value


def _texts(value: Any, where: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise CaseAnswerError(f"{where}: expected a list, got {type(value).__name__}")
    return tuple(_text(item, f"{where}[{i}]") for i, item in enumerate(value))


def _member[E: StrEnum](enum: type[E], value: Any, where: str) -> E:
    try:
        return enum(value)
    except ValueError:
        raise CaseAnswerError(f"{where}: {value!r} is not a {enum.__name__}") from None


def _objects(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list):
        raise CaseAnswerError(f"{where}: expected a list, got {type(value).__name__}")
    return value


def _generator(value: Any, where: str) -> GeneratorAnswer:
    data = _fields(
        value,
        where,
        required=frozenset({"outcome", "codes", "reasons"}),
        optional=frozenset({"witnesses", "stubs", "seams"}),
    )
    codes = _texts(data["codes"], f"{where}.codes")
    if list(codes) != sorted(codes):
        raise CaseAnswerError(f"{where}.codes: must be sorted, got {list(codes)}")
    stubs = []
    for i, item in enumerate(_objects(data.get("stubs", []), f"{where}.stubs")):
        stub = _fields(item, f"{where}.stubs[{i}]", required=frozenset({"output", "reason"}))
        stubs.append(
            StubAnswer(
                output=_text(stub["output"], f"{where}.stubs[{i}].output"),
                reason=_member(SiteReason, stub["reason"], f"{where}.stubs[{i}].reason"),
            )
        )
    seams = []
    for i, item in enumerate(_objects(data.get("seams", []), f"{where}.seams")):
        seam = _fields(
            item, f"{where}.seams[{i}]", required=frozenset({"kind", "declaration", "expect"})
        )
        seams.append(
            SeamAnswer(
                kind=_member(SeamKind, seam["kind"], f"{where}.seams[{i}].kind"),
                declaration=_text(seam["declaration"], f"{where}.seams[{i}].declaration"),
                expect=seam["expect"],
            )
        )
    return GeneratorAnswer(
        outcome=_member(GeneratorOutcome, data["outcome"], f"{where}.outcome"),
        codes=codes,
        reasons=tuple(
            _member(SiteReason, reason, f"{where}.reasons[{i}]")
            for i, reason in enumerate(_objects(data["reasons"], f"{where}.reasons"))
        ),
        witnesses=_texts(data.get("witnesses", []), f"{where}.witnesses"),
        stubs=tuple(stubs),
        seams=tuple(seams),
    )


def _screen(value: Any, where: str) -> ScreenAnswer:
    data = _fields(value, where, required=frozenset({"verdict", "findings"}))
    findings = []
    for i, item in enumerate(_objects(data["findings"], f"{where}.findings")):
        finding = _fields(
            item,
            f"{where}.findings[{i}]",
            required=frozenset({"rule", "shape", "context", "outcome", "subject"}),
        )
        findings.append(
            ScreenFinding(
                **{key: _text(finding[key], f"{where}.findings[{i}].{key}") for key in finding}
            )
        )
    return ScreenAnswer(
        verdict=_text(data["verdict"], f"{where}.verdict"), findings=tuple(findings)
    )


def _loss(value: Any, where: str) -> LossAnswer:
    data = _fields(
        value, where, required=frozenset({"family", "disposition"}), optional=frozenset({"rg1"})
    )
    rg1 = data.get("rg1")
    if rg1 is not None and not (isinstance(rg1, str) and _RG1_ID.fullmatch(rg1)):
        raise CaseAnswerError(f"{where}.rg1: expected RG1-<n>, got {rg1!r}")
    disposition = _member(LossDisposition, data["disposition"], f"{where}.disposition")
    if disposition is LossDisposition.CANDIDATE_REFUSAL and rg1 is None:
        raise CaseAnswerError(f"{where}: a candidate refusal names its RG1-<n>")
    return LossAnswer(
        family=_text(data["family"], f"{where}.family"), disposition=disposition, rg1=rg1
    )


def load_stored_answer(path: Path) -> StoredAnswer:
    """Read one stored generator answer, ``<case_id>.json``."""
    where = str(path)
    data = _fields(
        json.loads(path.read_text()),
        where,
        required=frozenset({"id", "home", "generator"}),
        optional=frozenset({"screen", "loss"}),
    )
    case_id = _text(data["id"], f"{where}.id")
    if case_id != path.stem:
        raise CaseAnswerError(f"{where}: id {case_id!r} is not the file name {path.stem!r}")
    home = _member(CaseHome, data["home"], f"{where}.home")
    if ("screen" in data) != (home is CaseHome.CODEGEN):
        raise CaseAnswerError(
            f"{where}: a screen answer is stored here exactly for codegen-home cases"
        )
    return StoredAnswer(
        case_id=case_id,
        home=home,
        generator=_generator(data["generator"], f"{where}.generator"),
        screen=_screen(data["screen"], f"{where}.screen") if "screen" in data else None,
        loss=_loss(data["loss"], f"{where}.loss") if "loss" in data else None,
    )


def load_packaged_case(case_dir: Path) -> PackagedCase:
    """Read the ``case.json`` of one packaged case directory, ``subset_cases/<case_id>/``."""
    path = case_dir / "case.json"
    where = str(path)
    data = _fields(
        json.loads(path.read_text()),
        where,
        required=frozenset(
            {"schema", "construct", "screen", "agentic_site_witnesses", "provenance"}
        ),
    )
    if data["schema"] != PACKAGED_CASE_SCHEMA:
        raise CaseAnswerError(
            f"{where}.schema: expected {PACKAGED_CASE_SCHEMA!r}, got {data['schema']!r}"
        )
    construct = _fields(
        data["construct"], f"{where}.construct", required=frozenset({"file", "lines"})
    )
    lines = construct["lines"]
    if not (
        isinstance(lines, list)
        and len(lines) == 2
        and all(isinstance(n, int) and n >= 1 for n in lines)
        and lines[0] <= lines[1]
    ):
        raise CaseAnswerError(f"{where}.construct.lines: expected [first, last], got {lines!r}")
    provenance = _fields(
        data["provenance"],
        f"{where}.provenance",
        required=frozenset({"note"}),
        optional=frozenset({"from_probe"}),
    )
    from_probe = provenance.get("from_probe")
    return PackagedCase(
        case_id=case_dir.name,
        construct=Construct(
            file=_text(construct["file"], f"{where}.construct.file"), lines=(lines[0], lines[1])
        ),
        screen=_screen(data["screen"], f"{where}.screen"),
        agentic_site_witnesses=_texts(
            data["agentic_site_witnesses"], f"{where}.agentic_site_witnesses"
        ),
        provenance=Provenance(
            from_probe=None
            if from_probe is None
            else _text(from_probe, f"{where}.provenance.from_probe"),
            note=_text(provenance["note"], f"{where}.provenance.note"),
        ),
    )
